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
        ("round 81: the quick brown fox jumps over the lazy dog", 4),
        ["round", "81:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 81: the quick brown fox jumps over the lazy dog", 8),
        ["round", "81: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 81: the quick brown fox jumps over the lazy dog", 12),
        ["round 81:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 81: the quick brown fox jumps over the lazy dog", 16),
        ["round 81: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 81: the quick brown fox jumps over the lazy dog", 24),
        ["round 81: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 81: the quick brown fox jumps over the lazy dog", 32),
        ["round 81: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 81: agentuniverse is a framework for multi agents", 4),
        ["round", "81:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 81: agentuniverse is a framework for multi agents", 8),
        ["round", "81:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 81: agentuniverse is a framework for multi agents", 12),
        ["round 81:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 81: agentuniverse is a framework for multi agents", 16),
        ["round 81:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 81: agentuniverse is a framework for multi agents", 24),
        ["round 81: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 81: agentuniverse is a framework for multi agents", 32),
        ["round 81: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 81: knowledge stored as vectors enables retrieval", 4),
        ["round", "81:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 81: knowledge stored as vectors enables retrieval", 8),
        ["round", "81:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 81: knowledge stored as vectors enables retrieval", 12),
        ["round 81:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 81: knowledge stored as vectors enables retrieval", 16),
        ["round 81:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 81: knowledge stored as vectors enables retrieval", 24),
        ["round 81: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 81: knowledge stored as vectors enables retrieval", 32),
        ["round 81: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 81: the processor reads the record then stops", 4),
        ["round", "81:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 81: the processor reads the record then stops", 8),
        ["round", "81: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 81: the processor reads the record then stops", 12),
        ["round 81:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 81: the processor reads the record then stops", 16),
        ["round 81: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 81: the processor reads the record then stops", 24),
        ["round 81: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 81: the processor reads the record then stops", 32),
        ["round 81: the processor reads", "the record then stops"],
    ),
    (
        ("round 81: a worker pulls the next task from the queue", 4),
        ["round", "81:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 81: a worker pulls the next task from the queue", 8),
        ["round", "81: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 81: a worker pulls the next task from the queue", 12),
        ["round 81: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 81: a worker pulls the next task from the queue", 16),
        ["round 81: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 81: a worker pulls the next task from the queue", 24),
        ["round 81: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 81: a worker pulls the next task from the queue", 32),
        ["round 81: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 81: signals travel through the network layer", 4),
        ["round", "81:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 81: signals travel through the network layer", 8),
        ["round", "81:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 81: signals travel through the network layer", 12),
        ["round 81:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 81: signals travel through the network layer", 16),
        ["round 81:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 81: signals travel through the network layer", 24),
        ["round 81: signals travel", "through the network", "layer"],
    ),
    (
        ("round 81: signals travel through the network layer", 32),
        ["round 81: signals travel through", "the network layer"],
    ),
    (
        ("round 81: the gateway routes each request by policy", 4),
        ["round", "81:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 81: the gateway routes each request by policy", 8),
        ["round", "81: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 81: the gateway routes each request by policy", 12),
        ["round 81:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 81: the gateway routes each request by policy", 16),
        ["round 81: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 81: the gateway routes each request by policy", 24),
        ["round 81: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 81: the gateway routes each request by policy", 32),
        ["round 81: the gateway routes", "each request by policy"],
    ),
    (
        ("round 81: memory grows until the buffer is full", 4),
        ["round", "81:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 81: memory grows until the buffer is full", 8),
        ["round", "81:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 81: memory grows until the buffer is full", 12),
        ["round 81:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 81: memory grows until the buffer is full", 16),
        ["round 81: memory", "grows until the", "buffer is full"],
    ),
    (("round 81: memory grows until the buffer is full", 24), ["round 81: memory grows", "until the buffer is full"]),
    (("round 81: memory grows until the buffer is full", 32), ["round 81: memory grows until the", "buffer is full"]),
    (
        ("round 81: the cluster mirrors every packet twice", 4),
        ["round", "81:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 81: the cluster mirrors every packet twice", 8),
        ["round", "81: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 81: the cluster mirrors every packet twice", 12),
        ["round 81:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 81: the cluster mirrors every packet twice", 16),
        ["round 81: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 81: the cluster mirrors every packet twice", 24),
        ["round 81: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 81: the cluster mirrors every packet twice", 32), ["round 81: the cluster mirrors", "every packet twice"]),
    (
        ("round 81: ranking uses tokens learned from the corpus", 4),
        ["round", "81:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 81: ranking uses tokens learned from the corpus", 8),
        ["round", "81:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 81: ranking uses tokens learned from the corpus", 12),
        ["round 81:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 81: ranking uses tokens learned from the corpus", 16),
        ["round 81:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 81: ranking uses tokens learned from the corpus", 24),
        ["round 81: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 81: ranking uses tokens learned from the corpus", 32),
        ["round 81: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 81: a long session ends when the candle dies", 4),
        ["round", "81:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 81: a long session ends when the candle dies", 8),
        ["round", "81: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 81: a long session ends when the candle dies", 12),
        ["round 81: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 81: a long session ends when the candle dies", 16),
        ["round 81: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 81: a long session ends when the candle dies", 24),
        ["round 81: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 81: a long session ends when the candle dies", 32),
        ["round 81: a long session ends", "when the candle dies"],
    ),
    (
        ("round 81: encode the prompt then map the result", 4),
        ["round", "81:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 81: encode the prompt then map the result", 8),
        ["round", "81:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 81: encode the prompt then map the result", 12),
        ["round 81:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 81: encode the prompt then map the result", 16),
        ["round 81: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 81: encode the prompt then map the result", 24),
        ["round 81: encode the", "prompt then map the", "result"],
    ),
    (("round 81: encode the prompt then map the result", 32), ["round 81: encode the prompt then", "map the result"]),
    (
        ("round 81: the kernel wakes the worker at dawn", 4),
        ["round", "81:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 81: the kernel wakes the worker at dawn", 8),
        ["round", "81: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 81: the kernel wakes the worker at dawn", 12),
        ["round 81:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 81: the kernel wakes the worker at dawn", 16), ["round 81: the", "kernel wakes the", "worker at dawn"]),
    (("round 81: the kernel wakes the worker at dawn", 24), ["round 81: the kernel", "wakes the worker at dawn"]),
    (("round 81: the kernel wakes the worker at dawn", 32), ["round 81: the kernel wakes the", "worker at dawn"]),
    (
        ("round 81: service latency drops after the patch", 4),
        ["round", "81:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 81: service latency drops after the patch", 8),
        ["round", "81:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 81: service latency drops after the patch", 12),
        ["round 81:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 81: service latency drops after the patch", 16),
        ["round 81:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 81: service latency drops after the patch", 24),
        ["round 81: service", "latency drops after the", "patch"],
    ),
    (("round 81: service latency drops after the patch", 32), ["round 81: service latency drops", "after the patch"]),
    (
        ("round 81: the library caches every vector it sees", 4),
        ["round", "81:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 81: the library caches every vector it sees", 8),
        ["round", "81: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 81: the library caches every vector it sees", 12),
        ["round 81:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 81: the library caches every vector it sees", 16),
        ["round 81: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 81: the library caches every vector it sees", 24),
        ["round 81: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 81: the library caches every vector it sees", 32),
        ["round 81: the library caches", "every vector it sees"],
    ),
    (
        ("round 81: agents argue then the debate resolves", 4),
        ["round", "81:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 81: agents argue then the debate resolves", 8),
        ["round", "81:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 81: agents argue then the debate resolves", 12),
        ["round 81:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 81: agents argue then the debate resolves", 16),
        ["round 81: agents", "argue then the", "debate resolves"],
    ),
    (("round 81: agents argue then the debate resolves", 24), ["round 81: agents argue", "then the debate resolves"]),
    (("round 81: agents argue then the debate resolves", 32), ["round 81: agents argue then the", "debate resolves"]),
    (
        ("round 81: the filter keeps only strong matches", 4),
        ["round", "81:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 81: the filter keeps only strong matches", 8),
        ["round", "81: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 81: the filter keeps only strong matches", 12),
        ["round 81:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 81: the filter keeps only strong matches", 16),
        ["round 81: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 81: the filter keeps only strong matches", 24), ["round 81: the filter", "keeps only strong", "matches"]),
    (("round 81: the filter keeps only strong matches", 32), ["round 81: the filter keeps only", "strong matches"]),
    (
        ("round 81: the model answers with a short reply", 4),
        ["round", "81:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 81: the model answers with a short reply", 8),
        ["round", "81: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 81: the model answers with a short reply", 12),
        ["round 81:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 81: the model answers with a short reply", 16),
        ["round 81: the", "model answers", "with a short", "reply"],
    ),
    (("round 81: the model answers with a short reply", 24), ["round 81: the model", "answers with a short", "reply"]),
    (("round 81: the model answers with a short reply", 32), ["round 81: the model answers with", "a short reply"]),
    (
        ("round 81: the recorder stores the reasoning trace", 4),
        ["round", "81:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 81: the recorder stores the reasoning trace", 8),
        ["round", "81: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 81: the recorder stores the reasoning trace", 12),
        ["round 81:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 81: the recorder stores the reasoning trace", 16),
        ["round 81: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 81: the recorder stores the reasoning trace", 24),
        ["round 81: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 81: the recorder stores the reasoning trace", 32),
        ["round 81: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 81: the angel watches the processor run", 4),
        ["round", "81:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 81: the angel watches the processor run", 8),
        ["round", "81: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 81: the angel watches the processor run", 12),
        ["round 81:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 81: the angel watches the processor run", 16), ["round 81: the", "angel watches", "the processor", "run"]),
    (("round 81: the angel watches the processor run", 24), ["round 81: the angel", "watches the processor", "run"]),
    (("round 81: the angel watches the processor run", 32), ["round 81: the angel watches the", "processor run"]),
    (
        ("round 81: angle of the vector decides the match", 4),
        ["round", "81:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 81: angle of the vector decides the match", 8),
        ["round", "81:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 81: angle of the vector decides the match", 12),
        ["round 81:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 81: angle of the vector decides the match", 16),
        ["round 81: angle", "of the vector", "decides the", "match"],
    ),
    (("round 81: angle of the vector decides the match", 24), ["round 81: angle of the", "vector decides the match"]),
    (("round 81: angle of the vector decides the match", 32), ["round 81: angle of the vector", "decides the match"]),
    (
        ("round 81: the candle burns twice as long at night", 4),
        ["round", "81:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 81: the candle burns twice as long at night", 8),
        ["round", "81: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 81: the candle burns twice as long at night", 12),
        ["round 81:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 81: the candle burns twice as long at night", 16),
        ["round 81: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 81: the candle burns twice as long at night", 24),
        ["round 81: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 81: the candle burns twice as long at night", 32),
        ["round 81: the candle burns twice", "as long at night"],
    ),
    (
        ("round 81: a mirror of the universe in one line", 4),
        ["round", "81:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 81: a mirror of the universe in one line", 8),
        ["round", "81: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 81: a mirror of the universe in one line", 12),
        ["round 81: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 81: a mirror of the universe in one line", 16),
        ["round 81: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 81: a mirror of the universe in one line", 24), ["round 81: a mirror of", "the universe in one line"]),
    (("round 81: a mirror of the universe in one line", 32), ["round 81: a mirror of the", "universe in one line"]),
    (
        ("round 81: the queue drains before the storm", 4),
        ["round", "81:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 81: the queue drains before the storm", 8),
        ["round", "81: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 81: the queue drains before the storm", 12), ["round 81:", "the queue", "drains", "before the", "storm"]),
    (("round 81: the queue drains before the storm", 16), ["round 81: the", "queue drains", "before the storm"]),
    (("round 81: the queue drains before the storm", 24), ["round 81: the queue", "drains before the storm"]),
    (("round 81: the queue drains before the storm", 32), ["round 81: the queue drains", "before the storm"]),
    (
        ("kitten81 sitting81 agent81 angle81 universe81 memory81", 6),
        ["kitten81", "sitting81", "agent81", "angle81", "universe81", "memory81"],
    ),
    (
        ("kitten81 sitting81 agent81 angle81 universe81 memory81", 10),
        ["kitten81", "sitting81", "agent81", "angle81", "universe81", "memory81"],
    ),
    (
        ("kitten81 sitting81 agent81 angle81 universe81 memory81", 18),
        ["kitten81 sitting81", "agent81 angle81", "universe81", "memory81"],
    ),
    (
        ("kitten81 sitting81 agent81 angle81 universe81 memory81", 28),
        ["kitten81 sitting81 agent81", "angle81 universe81 memory81"],
    ),
    (
        ("sitting81 agent81 angle81 universe81 memory81 stream81", 6),
        ["sitting81", "agent81", "angle81", "universe81", "memory81", "stream81"],
    ),
    (
        ("sitting81 agent81 angle81 universe81 memory81 stream81", 10),
        ["sitting81", "agent81", "angle81", "universe81", "memory81", "stream81"],
    ),
    (
        ("sitting81 agent81 angle81 universe81 memory81 stream81", 18),
        ["sitting81 agent81", "angle81 universe81", "memory81 stream81"],
    ),
    (
        ("sitting81 agent81 angle81 universe81 memory81 stream81", 28),
        ["sitting81 agent81 angle81", "universe81 memory81 stream81"],
    ),
    (
        ("agent81 angle81 universe81 memory81 stream81 context81", 6),
        ["agent81", "angle81", "universe81", "memory81", "stream81", "context81"],
    ),
    (
        ("agent81 angle81 universe81 memory81 stream81 context81", 10),
        ["agent81", "angle81", "universe81", "memory81", "stream81", "context81"],
    ),
    (
        ("agent81 angle81 universe81 memory81 stream81 context81", 18),
        ["agent81 angle81", "universe81", "memory81 stream81", "context81"],
    ),
    (
        ("agent81 angle81 universe81 memory81 stream81 context81", 28),
        ["agent81 angle81 universe81", "memory81 stream81 context81"],
    ),
    (
        ("angle81 universe81 memory81 stream81 context81 knowledge81", 6),
        ["angle81", "universe81", "memory81", "stream81", "context81", "knowledge81"],
    ),
    (
        ("angle81 universe81 memory81 stream81 context81 knowledge81", 10),
        ["angle81", "universe81", "memory81", "stream81", "context81", "knowledge81"],
    ),
    (
        ("angle81 universe81 memory81 stream81 context81 knowledge81", 18),
        ["angle81 universe81", "memory81 stream81", "context81", "knowledge81"],
    ),
    (
        ("angle81 universe81 memory81 stream81 context81 knowledge81", 28),
        ["angle81 universe81 memory81", "stream81 context81", "knowledge81"],
    ),
    (
        ("universe81 memory81 stream81 context81 knowledge81 vector81", 6),
        ["universe81", "memory81", "stream81", "context81", "knowledge81", "vector81"],
    ),
    (
        ("universe81 memory81 stream81 context81 knowledge81 vector81", 10),
        ["universe81", "memory81", "stream81", "context81", "knowledge81", "vector81"],
    ),
    (
        ("universe81 memory81 stream81 context81 knowledge81 vector81", 18),
        ["universe81", "memory81 stream81", "context81", "knowledge81", "vector81"],
    ),
    (
        ("universe81 memory81 stream81 context81 knowledge81 vector81", 28),
        ["universe81 memory81 stream81", "context81 knowledge81", "vector81"],
    ),
    (
        ("memory81 stream81 context81 knowledge81 vector81 processor81", 6),
        ["memory81", "stream81", "context81", "knowledge81", "vector81", "processor81"],
    ),
    (
        ("memory81 stream81 context81 knowledge81 vector81 processor81", 10),
        ["memory81", "stream81", "context81", "knowledge81", "vector81", "processor81"],
    ),
    (
        ("memory81 stream81 context81 knowledge81 vector81 processor81", 18),
        ["memory81 stream81", "context81", "knowledge81", "vector81", "processor81"],
    ),
    (
        ("memory81 stream81 context81 knowledge81 vector81 processor81", 28),
        ["memory81 stream81 context81", "knowledge81 vector81", "processor81"],
    ),
    (
        ("stream81 context81 knowledge81 vector81 processor81 reasoning81", 6),
        ["stream81", "context81", "knowledge81", "vector81", "processor81", "reasoning81"],
    ),
    (
        ("stream81 context81 knowledge81 vector81 processor81 reasoning81", 10),
        ["stream81", "context81", "knowledge81", "vector81", "processor81", "reasoning81"],
    ),
    (
        ("stream81 context81 knowledge81 vector81 processor81 reasoning81", 18),
        ["stream81 context81", "knowledge81", "vector81", "processor81", "reasoning81"],
    ),
    (
        ("stream81 context81 knowledge81 vector81 processor81 reasoning81", 28),
        ["stream81 context81", "knowledge81 vector81", "processor81 reasoning81"],
    ),
    (
        ("context81 knowledge81 vector81 processor81 reasoning81 machine81", 6),
        ["context81", "knowledge81", "vector81", "processor81", "reasoning81", "machine81"],
    ),
    (
        ("context81 knowledge81 vector81 processor81 reasoning81 machine81", 10),
        ["context81", "knowledge81", "vector81", "processor81", "reasoning81", "machine81"],
    ),
    (
        ("context81 knowledge81 vector81 processor81 reasoning81 machine81", 18),
        ["context81", "knowledge81", "vector81", "processor81", "reasoning81", "machine81"],
    ),
    (
        ("context81 knowledge81 vector81 processor81 reasoning81 machine81", 28),
        ["context81 knowledge81", "vector81 processor81", "reasoning81 machine81"],
    ),
    (
        ("knowledge81 vector81 processor81 reasoning81 machine81 learning81", 6),
        ["knowledge81", "vector81", "processor81", "reasoning81", "machine81", "learning81"],
    ),
    (
        ("knowledge81 vector81 processor81 reasoning81 machine81 learning81", 10),
        ["knowledge81", "vector81", "processor81", "reasoning81", "machine81", "learning81"],
    ),
    (
        ("knowledge81 vector81 processor81 reasoning81 machine81 learning81", 18),
        ["knowledge81", "vector81", "processor81", "reasoning81", "machine81", "learning81"],
    ),
    (
        ("knowledge81 vector81 processor81 reasoning81 machine81 learning81", 28),
        ["knowledge81 vector81", "processor81 reasoning81", "machine81 learning81"],
    ),
    (
        ("vector81 processor81 reasoning81 machine81 learning81 model81", 6),
        ["vector81", "processor81", "reasoning81", "machine81", "learning81", "model81"],
    ),
    (
        ("vector81 processor81 reasoning81 machine81 learning81 model81", 10),
        ["vector81", "processor81", "reasoning81", "machine81", "learning81", "model81"],
    ),
    (
        ("vector81 processor81 reasoning81 machine81 learning81 model81", 18),
        ["vector81", "processor81", "reasoning81", "machine81", "learning81 model81"],
    ),
    (
        ("vector81 processor81 reasoning81 machine81 learning81 model81", 28),
        ["vector81 processor81", "reasoning81 machine81", "learning81 model81"],
    ),
    (
        ("processor81 reasoning81 machine81 learning81 model81 token81", 6),
        ["processor81", "reasoning81", "machine81", "learning81", "model81", "token81"],
    ),
    (
        ("processor81 reasoning81 machine81 learning81 model81 token81", 10),
        ["processor81", "reasoning81", "machine81", "learning81", "model81", "token81"],
    ),
    (
        ("processor81 reasoning81 machine81 learning81 model81 token81", 18),
        ["processor81", "reasoning81", "machine81", "learning81 model81", "token81"],
    ),
    (
        ("processor81 reasoning81 machine81 learning81 model81 token81", 28),
        ["processor81 reasoning81", "machine81 learning81 model81", "token81"],
    ),
    (
        ("reasoning81 machine81 learning81 model81 token81 prompt81", 6),
        ["reasoning81", "machine81", "learning81", "model81", "token81", "prompt81"],
    ),
    (
        ("reasoning81 machine81 learning81 model81 token81 prompt81", 10),
        ["reasoning81", "machine81", "learning81", "model81", "token81", "prompt81"],
    ),
    (
        ("reasoning81 machine81 learning81 model81 token81 prompt81", 18),
        ["reasoning81", "machine81", "learning81 model81", "token81 prompt81"],
    ),
    (
        ("reasoning81 machine81 learning81 model81 token81 prompt81", 28),
        ["reasoning81 machine81", "learning81 model81 token81", "prompt81"],
    ),
    (
        ("machine81 learning81 model81 token81 prompt81 session81", 6),
        ["machine81", "learning81", "model81", "token81", "prompt81", "session81"],
    ),
    (
        ("machine81 learning81 model81 token81 prompt81 session81", 10),
        ["machine81", "learning81", "model81", "token81", "prompt81", "session81"],
    ),
    (
        ("machine81 learning81 model81 token81 prompt81 session81", 18),
        ["machine81", "learning81 model81", "token81 prompt81", "session81"],
    ),
    (
        ("machine81 learning81 model81 token81 prompt81 session81", 28),
        ["machine81 learning81 model81", "token81 prompt81 session81"],
    ),
    (
        ("learning81 model81 token81 prompt81 session81 library81", 6),
        ["learning81", "model81", "token81", "prompt81", "session81", "library81"],
    ),
    (
        ("learning81 model81 token81 prompt81 session81 library81", 10),
        ["learning81", "model81", "token81", "prompt81", "session81", "library81"],
    ),
    (
        ("learning81 model81 token81 prompt81 session81 library81", 18),
        ["learning81 model81", "token81 prompt81", "session81", "library81"],
    ),
    (
        ("learning81 model81 token81 prompt81 session81 library81", 28),
        ["learning81 model81 token81", "prompt81 session81 library81"],
    ),
    (
        ("model81 token81 prompt81 session81 library81 service81", 6),
        ["model81", "token81", "prompt81", "session81", "library81", "service81"],
    ),
    (
        ("model81 token81 prompt81 session81 library81 service81", 10),
        ["model81", "token81", "prompt81", "session81", "library81", "service81"],
    ),
    (
        ("model81 token81 prompt81 session81 library81 service81", 18),
        ["model81 token81", "prompt81 session81", "library81", "service81"],
    ),
    (
        ("model81 token81 prompt81 session81 library81 service81", 28),
        ["model81 token81 prompt81", "session81 library81", "service81"],
    ),
    (
        ("token81 prompt81 session81 library81 service81 gateway81", 6),
        ["token81", "prompt81", "session81", "library81", "service81", "gateway81"],
    ),
    (
        ("token81 prompt81 session81 library81 service81 gateway81", 10),
        ["token81", "prompt81", "session81", "library81", "service81", "gateway81"],
    ),
    (
        ("token81 prompt81 session81 library81 service81 gateway81", 18),
        ["token81 prompt81", "session81", "library81", "service81", "gateway81"],
    ),
    (
        ("token81 prompt81 session81 library81 service81 gateway81", 28),
        ["token81 prompt81 session81", "library81 service81", "gateway81"],
    ),
    (
        ("prompt81 session81 library81 service81 gateway81 storage81", 6),
        ["prompt81", "session81", "library81", "service81", "gateway81", "storage81"],
    ),
    (
        ("prompt81 session81 library81 service81 gateway81 storage81", 10),
        ["prompt81", "session81", "library81", "service81", "gateway81", "storage81"],
    ),
    (
        ("prompt81 session81 library81 service81 gateway81 storage81", 18),
        ["prompt81 session81", "library81", "service81", "gateway81", "storage81"],
    ),
    (
        ("prompt81 session81 library81 service81 gateway81 storage81", 28),
        ["prompt81 session81 library81", "service81 gateway81", "storage81"],
    ),
    (
        ("session81 library81 service81 gateway81 storage81 network81", 6),
        ["session81", "library81", "service81", "gateway81", "storage81", "network81"],
    ),
    (
        ("session81 library81 service81 gateway81 storage81 network81", 10),
        ["session81", "library81", "service81", "gateway81", "storage81", "network81"],
    ),
    (
        ("session81 library81 service81 gateway81 storage81 network81", 18),
        ["session81", "library81", "service81", "gateway81", "storage81", "network81"],
    ),
    (
        ("session81 library81 service81 gateway81 storage81 network81", 28),
        ["session81 library81", "service81 gateway81", "storage81 network81"],
    ),
    (
        ("library81 service81 gateway81 storage81 network81 latency81", 6),
        ["library81", "service81", "gateway81", "storage81", "network81", "latency81"],
    ),
    (
        ("library81 service81 gateway81 storage81 network81 latency81", 10),
        ["library81", "service81", "gateway81", "storage81", "network81", "latency81"],
    ),
    (
        ("library81 service81 gateway81 storage81 network81 latency81", 18),
        ["library81", "service81", "gateway81", "storage81", "network81", "latency81"],
    ),
    (
        ("library81 service81 gateway81 storage81 network81 latency81", 28),
        ["library81 service81", "gateway81 storage81", "network81 latency81"],
    ),
    (
        ("service81 gateway81 storage81 network81 latency81 buffer81", 6),
        ["service81", "gateway81", "storage81", "network81", "latency81", "buffer81"],
    ),
    (
        ("service81 gateway81 storage81 network81 latency81 buffer81", 10),
        ["service81", "gateway81", "storage81", "network81", "latency81", "buffer81"],
    ),
    (
        ("service81 gateway81 storage81 network81 latency81 buffer81", 18),
        ["service81", "gateway81", "storage81", "network81", "latency81 buffer81"],
    ),
    (
        ("service81 gateway81 storage81 network81 latency81 buffer81", 28),
        ["service81 gateway81", "storage81 network81", "latency81 buffer81"],
    ),
    (
        ("gateway81 storage81 network81 latency81 buffer81 queue81", 6),
        ["gateway81", "storage81", "network81", "latency81", "buffer81", "queue81"],
    ),
    (
        ("gateway81 storage81 network81 latency81 buffer81 queue81", 10),
        ["gateway81", "storage81", "network81", "latency81", "buffer81", "queue81"],
    ),
    (
        ("gateway81 storage81 network81 latency81 buffer81 queue81", 18),
        ["gateway81", "storage81", "network81", "latency81 buffer81", "queue81"],
    ),
    (
        ("gateway81 storage81 network81 latency81 buffer81 queue81", 28),
        ["gateway81 storage81", "network81 latency81 buffer81", "queue81"],
    ),
    (
        ("storage81 network81 latency81 buffer81 queue81 worker81", 6),
        ["storage81", "network81", "latency81", "buffer81", "queue81", "worker81"],
    ),
    (
        ("storage81 network81 latency81 buffer81 queue81 worker81", 10),
        ["storage81", "network81", "latency81", "buffer81", "queue81", "worker81"],
    ),
    (
        ("storage81 network81 latency81 buffer81 queue81 worker81", 18),
        ["storage81", "network81", "latency81 buffer81", "queue81 worker81"],
    ),
    (
        ("storage81 network81 latency81 buffer81 queue81 worker81", 28),
        ["storage81 network81", "latency81 buffer81 queue81", "worker81"],
    ),
    (
        ("network81 latency81 buffer81 queue81 worker81 kernel81", 6),
        ["network81", "latency81", "buffer81", "queue81", "worker81", "kernel81"],
    ),
    (
        ("network81 latency81 buffer81 queue81 worker81 kernel81", 10),
        ["network81", "latency81", "buffer81", "queue81", "worker81", "kernel81"],
    ),
    (
        ("network81 latency81 buffer81 queue81 worker81 kernel81", 18),
        ["network81", "latency81 buffer81", "queue81 worker81", "kernel81"],
    ),
    (
        ("network81 latency81 buffer81 queue81 worker81 kernel81", 28),
        ["network81 latency81 buffer81", "queue81 worker81 kernel81"],
    ),
    (
        ("latency81 buffer81 queue81 worker81 kernel81 signal81", 6),
        ["latency81", "buffer81", "queue81", "worker81", "kernel81", "signal81"],
    ),
    (
        ("latency81 buffer81 queue81 worker81 kernel81 signal81", 10),
        ["latency81", "buffer81", "queue81", "worker81", "kernel81", "signal81"],
    ),
    (
        ("latency81 buffer81 queue81 worker81 kernel81 signal81", 18),
        ["latency81 buffer81", "queue81 worker81", "kernel81 signal81"],
    ),
    (
        ("latency81 buffer81 queue81 worker81 kernel81 signal81", 28),
        ["latency81 buffer81 queue81", "worker81 kernel81 signal81"],
    ),
    (
        ("buffer81 queue81 worker81 kernel81 signal81 packet81", 6),
        ["buffer81", "queue81", "worker81", "kernel81", "signal81", "packet81"],
    ),
    (
        ("buffer81 queue81 worker81 kernel81 signal81 packet81", 10),
        ["buffer81", "queue81", "worker81", "kernel81", "signal81", "packet81"],
    ),
    (
        ("buffer81 queue81 worker81 kernel81 signal81 packet81", 18),
        ["buffer81 queue81", "worker81 kernel81", "signal81 packet81"],
    ),
    (
        ("buffer81 queue81 worker81 kernel81 signal81 packet81", 28),
        ["buffer81 queue81 worker81", "kernel81 signal81 packet81"],
    ),
    (
        ("queue81 worker81 kernel81 signal81 packet81 router81", 6),
        ["queue81", "worker81", "kernel81", "signal81", "packet81", "router81"],
    ),
    (
        ("queue81 worker81 kernel81 signal81 packet81 router81", 10),
        ["queue81", "worker81", "kernel81", "signal81", "packet81", "router81"],
    ),
    (
        ("queue81 worker81 kernel81 signal81 packet81 router81", 18),
        ["queue81 worker81", "kernel81 signal81", "packet81 router81"],
    ),
    (
        ("queue81 worker81 kernel81 signal81 packet81 router81", 28),
        ["queue81 worker81 kernel81", "signal81 packet81 router81"],
    ),
    (
        ("worker81 kernel81 signal81 packet81 router81 cluster81", 6),
        ["worker81", "kernel81", "signal81", "packet81", "router81", "cluster81"],
    ),
    (
        ("worker81 kernel81 signal81 packet81 router81 cluster81", 10),
        ["worker81", "kernel81", "signal81", "packet81", "router81", "cluster81"],
    ),
    (
        ("worker81 kernel81 signal81 packet81 router81 cluster81", 18),
        ["worker81 kernel81", "signal81 packet81", "router81 cluster81"],
    ),
    (
        ("worker81 kernel81 signal81 packet81 router81 cluster81", 28),
        ["worker81 kernel81 signal81", "packet81 router81 cluster81"],
    ),
    (
        ("kernel81 signal81 packet81 router81 cluster81 mirror81", 6),
        ["kernel81", "signal81", "packet81", "router81", "cluster81", "mirror81"],
    ),
    (
        ("kernel81 signal81 packet81 router81 cluster81 mirror81", 10),
        ["kernel81", "signal81", "packet81", "router81", "cluster81", "mirror81"],
    ),
    (
        ("kernel81 signal81 packet81 router81 cluster81 mirror81", 18),
        ["kernel81 signal81", "packet81 router81", "cluster81 mirror81"],
    ),
    (
        ("kernel81 signal81 packet81 router81 cluster81 mirror81", 28),
        ["kernel81 signal81 packet81", "router81 cluster81 mirror81"],
    ),
    (
        ("signal81 packet81 router81 cluster81 mirror81 filter81", 6),
        ["signal81", "packet81", "router81", "cluster81", "mirror81", "filter81"],
    ),
    (
        ("signal81 packet81 router81 cluster81 mirror81 filter81", 10),
        ["signal81", "packet81", "router81", "cluster81", "mirror81", "filter81"],
    ),
    (
        ("signal81 packet81 router81 cluster81 mirror81 filter81", 18),
        ["signal81 packet81", "router81 cluster81", "mirror81 filter81"],
    ),
    (
        ("signal81 packet81 router81 cluster81 mirror81 filter81", 28),
        ["signal81 packet81 router81", "cluster81 mirror81 filter81"],
    ),
    (
        ("packet81 router81 cluster81 mirror81 filter81 ranking81", 6),
        ["packet81", "router81", "cluster81", "mirror81", "filter81", "ranking81"],
    ),
    (
        ("packet81 router81 cluster81 mirror81 filter81 ranking81", 10),
        ["packet81", "router81", "cluster81", "mirror81", "filter81", "ranking81"],
    ),
    (
        ("packet81 router81 cluster81 mirror81 filter81 ranking81", 18),
        ["packet81 router81", "cluster81 mirror81", "filter81 ranking81"],
    ),
    (
        ("packet81 router81 cluster81 mirror81 filter81 ranking81", 28),
        ["packet81 router81 cluster81", "mirror81 filter81 ranking81"],
    ),
    (
        ("router81 cluster81 mirror81 filter81 ranking81 encoding81", 6),
        ["router81", "cluster81", "mirror81", "filter81", "ranking81", "encoding81"],
    ),
    (
        ("router81 cluster81 mirror81 filter81 ranking81 encoding81", 10),
        ["router81", "cluster81", "mirror81", "filter81", "ranking81", "encoding81"],
    ),
    (
        ("router81 cluster81 mirror81 filter81 ranking81 encoding81", 18),
        ["router81 cluster81", "mirror81 filter81", "ranking81", "encoding81"],
    ),
    (
        ("router81 cluster81 mirror81 filter81 ranking81 encoding81", 28),
        ["router81 cluster81 mirror81", "filter81 ranking81", "encoding81"],
    ),
    (
        ("cluster81 mirror81 filter81 ranking81 encoding81 mapping81", 6),
        ["cluster81", "mirror81", "filter81", "ranking81", "encoding81", "mapping81"],
    ),
    (
        ("cluster81 mirror81 filter81 ranking81 encoding81 mapping81", 10),
        ["cluster81", "mirror81", "filter81", "ranking81", "encoding81", "mapping81"],
    ),
    (
        ("cluster81 mirror81 filter81 ranking81 encoding81 mapping81", 18),
        ["cluster81 mirror81", "filter81 ranking81", "encoding81", "mapping81"],
    ),
    (
        ("cluster81 mirror81 filter81 ranking81 encoding81 mapping81", 28),
        ["cluster81 mirror81 filter81", "ranking81 encoding81", "mapping81"],
    ),
    (
        ("mirror81 filter81 ranking81 encoding81 mapping81 record81", 6),
        ["mirror81", "filter81", "ranking81", "encoding81", "mapping81", "record81"],
    ),
    (
        ("mirror81 filter81 ranking81 encoding81 mapping81 record81", 10),
        ["mirror81", "filter81", "ranking81", "encoding81", "mapping81", "record81"],
    ),
    (
        ("mirror81 filter81 ranking81 encoding81 mapping81 record81", 18),
        ["mirror81 filter81", "ranking81", "encoding81", "mapping81 record81"],
    ),
    (
        ("mirror81 filter81 ranking81 encoding81 mapping81 record81", 28),
        ["mirror81 filter81 ranking81", "encoding81 mapping81", "record81"],
    ),
    (
        ("filter81 ranking81 encoding81 mapping81 record81 candle81", 6),
        ["filter81", "ranking81", "encoding81", "mapping81", "record81", "candle81"],
    ),
    (
        ("filter81 ranking81 encoding81 mapping81 record81 candle81", 10),
        ["filter81", "ranking81", "encoding81", "mapping81", "record81", "candle81"],
    ),
    (
        ("filter81 ranking81 encoding81 mapping81 record81 candle81", 18),
        ["filter81 ranking81", "encoding81", "mapping81 record81", "candle81"],
    ),
    (
        ("filter81 ranking81 encoding81 mapping81 record81 candle81", 28),
        ["filter81 ranking81", "encoding81 mapping81", "record81 candle81"],
    ),
    (
        ("ranking81 encoding81 mapping81 record81 candle81 thread81", 6),
        ["ranking81", "encoding81", "mapping81", "record81", "candle81", "thread81"],
    ),
    (
        ("ranking81 encoding81 mapping81 record81 candle81 thread81", 10),
        ["ranking81", "encoding81", "mapping81", "record81", "candle81", "thread81"],
    ),
    (
        ("ranking81 encoding81 mapping81 record81 candle81 thread81", 18),
        ["ranking81", "encoding81", "mapping81 record81", "candle81 thread81"],
    ),
    (
        ("ranking81 encoding81 mapping81 record81 candle81 thread81", 28),
        ["ranking81 encoding81", "mapping81 record81 candle81", "thread81"],
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
