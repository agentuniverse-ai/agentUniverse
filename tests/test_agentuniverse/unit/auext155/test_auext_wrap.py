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
        ("round 155: the quick brown fox jumps over the lazy dog", 4),
        ["round", "155:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", 8),
        ["round", "155: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", 12),
        ["round 155:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", 16),
        ["round 155: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", 24),
        ["round 155: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 155: the quick brown fox jumps over the lazy dog", 32),
        ["round 155: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", 4),
        ["round", "155:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", 8),
        ["round", "155:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", 12),
        ["round 155:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", 16),
        ["round 155:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", 24),
        ["round 155: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 155: agentuniverse is a framework for multi agents", 32),
        ["round 155: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", 4),
        ["round", "155:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", 8),
        ["round", "155:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", 12),
        ["round 155:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", 16),
        ["round 155:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", 24),
        ["round 155: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 155: knowledge stored as vectors enables retrieval", 32),
        ["round 155: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 155: the processor reads the record then stops", 4),
        ["round", "155:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 155: the processor reads the record then stops", 8),
        ["round", "155: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 155: the processor reads the record then stops", 12),
        ["round 155:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 155: the processor reads the record then stops", 16),
        ["round 155: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 155: the processor reads the record then stops", 24),
        ["round 155: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 155: the processor reads the record then stops", 32),
        ["round 155: the processor reads", "the record then stops"],
    ),
    (
        ("round 155: a worker pulls the next task from the queue", 4),
        ["round", "155:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 155: a worker pulls the next task from the queue", 8),
        ["round", "155: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 155: a worker pulls the next task from the queue", 12),
        ["round 155: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 155: a worker pulls the next task from the queue", 16),
        ["round 155: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 155: a worker pulls the next task from the queue", 24),
        ["round 155: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 155: a worker pulls the next task from the queue", 32),
        ["round 155: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 155: signals travel through the network layer", 4),
        ["round", "155:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 155: signals travel through the network layer", 8),
        ["round", "155:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 155: signals travel through the network layer", 12),
        ["round 155:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 155: signals travel through the network layer", 16),
        ["round 155:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 155: signals travel through the network layer", 24),
        ["round 155: signals", "travel through the", "network layer"],
    ),
    (
        ("round 155: signals travel through the network layer", 32),
        ["round 155: signals travel", "through the network layer"],
    ),
    (
        ("round 155: the gateway routes each request by policy", 4),
        ["round", "155:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 155: the gateway routes each request by policy", 8),
        ["round", "155: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 155: the gateway routes each request by policy", 12),
        ["round 155:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 155: the gateway routes each request by policy", 16),
        ["round 155: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 155: the gateway routes each request by policy", 24),
        ["round 155: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 155: the gateway routes each request by policy", 32),
        ["round 155: the gateway routes", "each request by policy"],
    ),
    (
        ("round 155: memory grows until the buffer is full", 4),
        ["round", "155:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 155: memory grows until the buffer is full", 8),
        ["round", "155:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 155: memory grows until the buffer is full", 12),
        ["round 155:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 155: memory grows until the buffer is full", 16),
        ["round 155:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 155: memory grows until the buffer is full", 24), ["round 155: memory grows", "until the buffer is full"]),
    (("round 155: memory grows until the buffer is full", 32), ["round 155: memory grows until", "the buffer is full"]),
    (
        ("round 155: the cluster mirrors every packet twice", 4),
        ["round", "155:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 155: the cluster mirrors every packet twice", 8),
        ["round", "155: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 155: the cluster mirrors every packet twice", 12),
        ["round 155:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 155: the cluster mirrors every packet twice", 16),
        ["round 155: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 155: the cluster mirrors every packet twice", 24),
        ["round 155: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 155: the cluster mirrors every packet twice", 32),
        ["round 155: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", 4),
        ["round", "155:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", 8),
        ["round", "155:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", 12),
        ["round 155:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", 16),
        ["round 155:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", 24),
        ["round 155: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 155: ranking uses tokens learned from the corpus", 32),
        ["round 155: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 155: a long session ends when the candle dies", 4),
        ["round", "155:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 155: a long session ends when the candle dies", 8),
        ["round", "155: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 155: a long session ends when the candle dies", 12),
        ["round 155: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 155: a long session ends when the candle dies", 16),
        ["round 155: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 155: a long session ends when the candle dies", 24),
        ["round 155: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 155: a long session ends when the candle dies", 32),
        ["round 155: a long session ends", "when the candle dies"],
    ),
    (
        ("round 155: encode the prompt then map the result", 4),
        ["round", "155:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 155: encode the prompt then map the result", 8),
        ["round", "155:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 155: encode the prompt then map the result", 12),
        ["round 155:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 155: encode the prompt then map the result", 16),
        ["round 155:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 155: encode the prompt then map the result", 24),
        ["round 155: encode the", "prompt then map the", "result"],
    ),
    (("round 155: encode the prompt then map the result", 32), ["round 155: encode the prompt", "then map the result"]),
    (
        ("round 155: the kernel wakes the worker at dawn", 4),
        ["round", "155:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 155: the kernel wakes the worker at dawn", 8),
        ["round", "155: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 155: the kernel wakes the worker at dawn", 12),
        ["round 155:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 155: the kernel wakes the worker at dawn", 16), ["round 155: the", "kernel wakes the", "worker at dawn"]),
    (("round 155: the kernel wakes the worker at dawn", 24), ["round 155: the kernel", "wakes the worker at dawn"]),
    (("round 155: the kernel wakes the worker at dawn", 32), ["round 155: the kernel wakes the", "worker at dawn"]),
    (
        ("round 155: service latency drops after the patch", 4),
        ["round", "155:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 155: service latency drops after the patch", 8),
        ["round", "155:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 155: service latency drops after the patch", 12),
        ["round 155:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 155: service latency drops after the patch", 16),
        ["round 155:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 155: service latency drops after the patch", 24),
        ["round 155: service", "latency drops after the", "patch"],
    ),
    (("round 155: service latency drops after the patch", 32), ["round 155: service latency drops", "after the patch"]),
    (
        ("round 155: the library caches every vector it sees", 4),
        ["round", "155:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 155: the library caches every vector it sees", 8),
        ["round", "155: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 155: the library caches every vector it sees", 12),
        ["round 155:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 155: the library caches every vector it sees", 16),
        ["round 155: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 155: the library caches every vector it sees", 24),
        ["round 155: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 155: the library caches every vector it sees", 32),
        ["round 155: the library caches", "every vector it sees"],
    ),
    (
        ("round 155: agents argue then the debate resolves", 4),
        ["round", "155:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 155: agents argue then the debate resolves", 8),
        ["round", "155:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 155: agents argue then the debate resolves", 12),
        ["round 155:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 155: agents argue then the debate resolves", 16),
        ["round 155:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 155: agents argue then the debate resolves", 24), ["round 155: agents argue", "then the debate resolves"]),
    (("round 155: agents argue then the debate resolves", 32), ["round 155: agents argue then the", "debate resolves"]),
    (
        ("round 155: the filter keeps only strong matches", 4),
        ["round", "155:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 155: the filter keeps only strong matches", 8),
        ["round", "155: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 155: the filter keeps only strong matches", 12),
        ["round 155:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 155: the filter keeps only strong matches", 16),
        ["round 155: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 155: the filter keeps only strong matches", 24),
        ["round 155: the filter", "keeps only strong", "matches"],
    ),
    (("round 155: the filter keeps only strong matches", 32), ["round 155: the filter keeps only", "strong matches"]),
    (
        ("round 155: the model answers with a short reply", 4),
        ["round", "155:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 155: the model answers with a short reply", 8),
        ["round", "155: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 155: the model answers with a short reply", 12),
        ["round 155:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 155: the model answers with a short reply", 16),
        ["round 155: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 155: the model answers with a short reply", 24),
        ["round 155: the model", "answers with a short", "reply"],
    ),
    (("round 155: the model answers with a short reply", 32), ["round 155: the model answers", "with a short reply"]),
    (
        ("round 155: the recorder stores the reasoning trace", 4),
        ["round", "155:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 155: the recorder stores the reasoning trace", 8),
        ["round", "155: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 155: the recorder stores the reasoning trace", 12),
        ["round 155:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 155: the recorder stores the reasoning trace", 16),
        ["round 155: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 155: the recorder stores the reasoning trace", 24),
        ["round 155: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 155: the recorder stores the reasoning trace", 32),
        ["round 155: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 155: the angel watches the processor run", 4),
        ["round", "155:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 155: the angel watches the processor run", 8),
        ["round", "155: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 155: the angel watches the processor run", 12),
        ["round 155:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 155: the angel watches the processor run", 16),
        ["round 155: the", "angel watches", "the processor", "run"],
    ),
    (("round 155: the angel watches the processor run", 24), ["round 155: the angel", "watches the processor", "run"]),
    (("round 155: the angel watches the processor run", 32), ["round 155: the angel watches the", "processor run"]),
    (
        ("round 155: angle of the vector decides the match", 4),
        ["round", "155:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 155: angle of the vector decides the match", 8),
        ["round", "155:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 155: angle of the vector decides the match", 12),
        ["round 155:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 155: angle of the vector decides the match", 16),
        ["round 155: angle", "of the vector", "decides the", "match"],
    ),
    (("round 155: angle of the vector decides the match", 24), ["round 155: angle of the", "vector decides the match"]),
    (("round 155: angle of the vector decides the match", 32), ["round 155: angle of the vector", "decides the match"]),
    (
        ("round 155: the candle burns twice as long at night", 4),
        ["round", "155:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 155: the candle burns twice as long at night", 8),
        ["round", "155: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 155: the candle burns twice as long at night", 12),
        ["round 155:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 155: the candle burns twice as long at night", 16),
        ["round 155: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 155: the candle burns twice as long at night", 24),
        ["round 155: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 155: the candle burns twice as long at night", 32),
        ["round 155: the candle burns", "twice as long at night"],
    ),
    (
        ("round 155: a mirror of the universe in one line", 4),
        ["round", "155:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 155: a mirror of the universe in one line", 8),
        ["round", "155: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 155: a mirror of the universe in one line", 12),
        ["round 155: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 155: a mirror of the universe in one line", 16),
        ["round 155: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 155: a mirror of the universe in one line", 24), ["round 155: a mirror of", "the universe in one line"]),
    (("round 155: a mirror of the universe in one line", 32), ["round 155: a mirror of the", "universe in one line"]),
    (
        ("round 155: the queue drains before the storm", 4),
        ["round", "155:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 155: the queue drains before the storm", 8),
        ["round", "155: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 155: the queue drains before the storm", 12),
        ["round 155:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 155: the queue drains before the storm", 16), ["round 155: the", "queue drains", "before the storm"]),
    (("round 155: the queue drains before the storm", 24), ["round 155: the queue", "drains before the storm"]),
    (("round 155: the queue drains before the storm", 32), ["round 155: the queue drains", "before the storm"]),
    (
        ("kitten155 sitting155 agent155 angle155 universe155 memory155", 6),
        ["kitten155", "sitting155", "agent155", "angle155", "universe155", "memory155"],
    ),
    (
        ("kitten155 sitting155 agent155 angle155 universe155 memory155", 10),
        ["kitten155", "sitting155", "agent155", "angle155", "universe155", "memory155"],
    ),
    (
        ("kitten155 sitting155 agent155 angle155 universe155 memory155", 18),
        ["kitten155", "sitting155", "agent155 angle155", "universe155", "memory155"],
    ),
    (
        ("kitten155 sitting155 agent155 angle155 universe155 memory155", 28),
        ["kitten155 sitting155", "agent155 angle155", "universe155 memory155"],
    ),
    (
        ("sitting155 agent155 angle155 universe155 memory155 stream155", 6),
        ["sitting155", "agent155", "angle155", "universe155", "memory155", "stream155"],
    ),
    (
        ("sitting155 agent155 angle155 universe155 memory155 stream155", 10),
        ["sitting155", "agent155", "angle155", "universe155", "memory155", "stream155"],
    ),
    (
        ("sitting155 agent155 angle155 universe155 memory155 stream155", 18),
        ["sitting155", "agent155 angle155", "universe155", "memory155", "stream155"],
    ),
    (
        ("sitting155 agent155 angle155 universe155 memory155 stream155", 28),
        ["sitting155 agent155 angle155", "universe155 memory155", "stream155"],
    ),
    (
        ("agent155 angle155 universe155 memory155 stream155 context155", 6),
        ["agent155", "angle155", "universe155", "memory155", "stream155", "context155"],
    ),
    (
        ("agent155 angle155 universe155 memory155 stream155 context155", 10),
        ["agent155", "angle155", "universe155", "memory155", "stream155", "context155"],
    ),
    (
        ("agent155 angle155 universe155 memory155 stream155 context155", 18),
        ["agent155 angle155", "universe155", "memory155", "stream155", "context155"],
    ),
    (
        ("agent155 angle155 universe155 memory155 stream155 context155", 28),
        ["agent155 angle155", "universe155 memory155", "stream155 context155"],
    ),
    (
        ("angle155 universe155 memory155 stream155 context155 knowledge155", 6),
        ["angle155", "universe155", "memory155", "stream155", "context155", "knowledge155"],
    ),
    (
        ("angle155 universe155 memory155 stream155 context155 knowledge155", 10),
        ["angle155", "universe155", "memory155", "stream155", "context155", "knowledge155"],
    ),
    (
        ("angle155 universe155 memory155 stream155 context155 knowledge155", 18),
        ["angle155", "universe155", "memory155", "stream155", "context155", "knowledge155"],
    ),
    (
        ("angle155 universe155 memory155 stream155 context155 knowledge155", 28),
        ["angle155 universe155", "memory155 stream155", "context155 knowledge155"],
    ),
    (
        ("universe155 memory155 stream155 context155 knowledge155 vector155", 6),
        ["universe155", "memory155", "stream155", "context155", "knowledge155", "vector155"],
    ),
    (
        ("universe155 memory155 stream155 context155 knowledge155 vector155", 10),
        ["universe155", "memory155", "stream155", "context155", "knowledge155", "vector155"],
    ),
    (
        ("universe155 memory155 stream155 context155 knowledge155 vector155", 18),
        ["universe155", "memory155", "stream155", "context155", "knowledge155", "vector155"],
    ),
    (
        ("universe155 memory155 stream155 context155 knowledge155 vector155", 28),
        ["universe155 memory155", "stream155 context155", "knowledge155 vector155"],
    ),
    (
        ("memory155 stream155 context155 knowledge155 vector155 processor155", 6),
        ["memory155", "stream155", "context155", "knowledge155", "vector155", "processor155"],
    ),
    (
        ("memory155 stream155 context155 knowledge155 vector155 processor155", 10),
        ["memory155", "stream155", "context155", "knowledge155", "vector155", "processor155"],
    ),
    (
        ("memory155 stream155 context155 knowledge155 vector155 processor155", 18),
        ["memory155", "stream155", "context155", "knowledge155", "vector155", "processor155"],
    ),
    (
        ("memory155 stream155 context155 knowledge155 vector155 processor155", 28),
        ["memory155 stream155", "context155 knowledge155", "vector155 processor155"],
    ),
    (
        ("stream155 context155 knowledge155 vector155 processor155 reasoning155", 6),
        ["stream155", "context155", "knowledge155", "vector155", "processor155", "reasoning155"],
    ),
    (
        ("stream155 context155 knowledge155 vector155 processor155 reasoning155", 10),
        ["stream155", "context155", "knowledge155", "vector155", "processor155", "reasoning155"],
    ),
    (
        ("stream155 context155 knowledge155 vector155 processor155 reasoning155", 18),
        ["stream155", "context155", "knowledge155", "vector155", "processor155", "reasoning155"],
    ),
    (
        ("stream155 context155 knowledge155 vector155 processor155 reasoning155", 28),
        ["stream155 context155", "knowledge155 vector155", "processor155 reasoning155"],
    ),
    (
        ("context155 knowledge155 vector155 processor155 reasoning155 machine155", 6),
        ["context155", "knowledge155", "vector155", "processor155", "reasoning155", "machine155"],
    ),
    (
        ("context155 knowledge155 vector155 processor155 reasoning155 machine155", 10),
        ["context155", "knowledge155", "vector155", "processor155", "reasoning155", "machine155"],
    ),
    (
        ("context155 knowledge155 vector155 processor155 reasoning155 machine155", 18),
        ["context155", "knowledge155", "vector155", "processor155", "reasoning155", "machine155"],
    ),
    (
        ("context155 knowledge155 vector155 processor155 reasoning155 machine155", 28),
        ["context155 knowledge155", "vector155 processor155", "reasoning155 machine155"],
    ),
    (
        ("knowledge155 vector155 processor155 reasoning155 machine155 learning155", 6),
        ["knowledge155", "vector155", "processor155", "reasoning155", "machine155", "learning155"],
    ),
    (
        ("knowledge155 vector155 processor155 reasoning155 machine155 learning155", 10),
        ["knowledge155", "vector155", "processor155", "reasoning155", "machine155", "learning155"],
    ),
    (
        ("knowledge155 vector155 processor155 reasoning155 machine155 learning155", 18),
        ["knowledge155", "vector155", "processor155", "reasoning155", "machine155", "learning155"],
    ),
    (
        ("knowledge155 vector155 processor155 reasoning155 machine155 learning155", 28),
        ["knowledge155 vector155", "processor155 reasoning155", "machine155 learning155"],
    ),
    (
        ("vector155 processor155 reasoning155 machine155 learning155 model155", 6),
        ["vector155", "processor155", "reasoning155", "machine155", "learning155", "model155"],
    ),
    (
        ("vector155 processor155 reasoning155 machine155 learning155 model155", 10),
        ["vector155", "processor155", "reasoning155", "machine155", "learning155", "model155"],
    ),
    (
        ("vector155 processor155 reasoning155 machine155 learning155 model155", 18),
        ["vector155", "processor155", "reasoning155", "machine155", "learning155", "model155"],
    ),
    (
        ("vector155 processor155 reasoning155 machine155 learning155 model155", 28),
        ["vector155 processor155", "reasoning155 machine155", "learning155 model155"],
    ),
    (
        ("processor155 reasoning155 machine155 learning155 model155 token155", 6),
        ["processor155", "reasoning155", "machine155", "learning155", "model155", "token155"],
    ),
    (
        ("processor155 reasoning155 machine155 learning155 model155 token155", 10),
        ["processor155", "reasoning155", "machine155", "learning155", "model155", "token155"],
    ),
    (
        ("processor155 reasoning155 machine155 learning155 model155 token155", 18),
        ["processor155", "reasoning155", "machine155", "learning155", "model155 token155"],
    ),
    (
        ("processor155 reasoning155 machine155 learning155 model155 token155", 28),
        ["processor155 reasoning155", "machine155 learning155", "model155 token155"],
    ),
    (
        ("reasoning155 machine155 learning155 model155 token155 prompt155", 6),
        ["reasoning155", "machine155", "learning155", "model155", "token155", "prompt155"],
    ),
    (
        ("reasoning155 machine155 learning155 model155 token155 prompt155", 10),
        ["reasoning155", "machine155", "learning155", "model155", "token155", "prompt155"],
    ),
    (
        ("reasoning155 machine155 learning155 model155 token155 prompt155", 18),
        ["reasoning155", "machine155", "learning155", "model155 token155", "prompt155"],
    ),
    (
        ("reasoning155 machine155 learning155 model155 token155 prompt155", 28),
        ["reasoning155 machine155", "learning155 model155", "token155 prompt155"],
    ),
    (
        ("machine155 learning155 model155 token155 prompt155 session155", 6),
        ["machine155", "learning155", "model155", "token155", "prompt155", "session155"],
    ),
    (
        ("machine155 learning155 model155 token155 prompt155 session155", 10),
        ["machine155", "learning155", "model155", "token155", "prompt155", "session155"],
    ),
    (
        ("machine155 learning155 model155 token155 prompt155 session155", 18),
        ["machine155", "learning155", "model155 token155", "prompt155", "session155"],
    ),
    (
        ("machine155 learning155 model155 token155 prompt155 session155", 28),
        ["machine155 learning155", "model155 token155 prompt155", "session155"],
    ),
    (
        ("learning155 model155 token155 prompt155 session155 library155", 6),
        ["learning155", "model155", "token155", "prompt155", "session155", "library155"],
    ),
    (
        ("learning155 model155 token155 prompt155 session155 library155", 10),
        ["learning155", "model155", "token155", "prompt155", "session155", "library155"],
    ),
    (
        ("learning155 model155 token155 prompt155 session155 library155", 18),
        ["learning155", "model155 token155", "prompt155", "session155", "library155"],
    ),
    (
        ("learning155 model155 token155 prompt155 session155 library155", 28),
        ["learning155 model155", "token155 prompt155", "session155 library155"],
    ),
    (
        ("model155 token155 prompt155 session155 library155 service155", 6),
        ["model155", "token155", "prompt155", "session155", "library155", "service155"],
    ),
    (
        ("model155 token155 prompt155 session155 library155 service155", 10),
        ["model155", "token155", "prompt155", "session155", "library155", "service155"],
    ),
    (
        ("model155 token155 prompt155 session155 library155 service155", 18),
        ["model155 token155", "prompt155", "session155", "library155", "service155"],
    ),
    (
        ("model155 token155 prompt155 session155 library155 service155", 28),
        ["model155 token155 prompt155", "session155 library155", "service155"],
    ),
    (
        ("token155 prompt155 session155 library155 service155 gateway155", 6),
        ["token155", "prompt155", "session155", "library155", "service155", "gateway155"],
    ),
    (
        ("token155 prompt155 session155 library155 service155 gateway155", 10),
        ["token155", "prompt155", "session155", "library155", "service155", "gateway155"],
    ),
    (
        ("token155 prompt155 session155 library155 service155 gateway155", 18),
        ["token155 prompt155", "session155", "library155", "service155", "gateway155"],
    ),
    (
        ("token155 prompt155 session155 library155 service155 gateway155", 28),
        ["token155 prompt155", "session155 library155", "service155 gateway155"],
    ),
    (
        ("prompt155 session155 library155 service155 gateway155 storage155", 6),
        ["prompt155", "session155", "library155", "service155", "gateway155", "storage155"],
    ),
    (
        ("prompt155 session155 library155 service155 gateway155 storage155", 10),
        ["prompt155", "session155", "library155", "service155", "gateway155", "storage155"],
    ),
    (
        ("prompt155 session155 library155 service155 gateway155 storage155", 18),
        ["prompt155", "session155", "library155", "service155", "gateway155", "storage155"],
    ),
    (
        ("prompt155 session155 library155 service155 gateway155 storage155", 28),
        ["prompt155 session155", "library155 service155", "gateway155 storage155"],
    ),
    (
        ("session155 library155 service155 gateway155 storage155 network155", 6),
        ["session155", "library155", "service155", "gateway155", "storage155", "network155"],
    ),
    (
        ("session155 library155 service155 gateway155 storage155 network155", 10),
        ["session155", "library155", "service155", "gateway155", "storage155", "network155"],
    ),
    (
        ("session155 library155 service155 gateway155 storage155 network155", 18),
        ["session155", "library155", "service155", "gateway155", "storage155", "network155"],
    ),
    (
        ("session155 library155 service155 gateway155 storage155 network155", 28),
        ["session155 library155", "service155 gateway155", "storage155 network155"],
    ),
    (
        ("library155 service155 gateway155 storage155 network155 latency155", 6),
        ["library155", "service155", "gateway155", "storage155", "network155", "latency155"],
    ),
    (
        ("library155 service155 gateway155 storage155 network155 latency155", 10),
        ["library155", "service155", "gateway155", "storage155", "network155", "latency155"],
    ),
    (
        ("library155 service155 gateway155 storage155 network155 latency155", 18),
        ["library155", "service155", "gateway155", "storage155", "network155", "latency155"],
    ),
    (
        ("library155 service155 gateway155 storage155 network155 latency155", 28),
        ["library155 service155", "gateway155 storage155", "network155 latency155"],
    ),
    (
        ("service155 gateway155 storage155 network155 latency155 buffer155", 6),
        ["service155", "gateway155", "storage155", "network155", "latency155", "buffer155"],
    ),
    (
        ("service155 gateway155 storage155 network155 latency155 buffer155", 10),
        ["service155", "gateway155", "storage155", "network155", "latency155", "buffer155"],
    ),
    (
        ("service155 gateway155 storage155 network155 latency155 buffer155", 18),
        ["service155", "gateway155", "storage155", "network155", "latency155", "buffer155"],
    ),
    (
        ("service155 gateway155 storage155 network155 latency155 buffer155", 28),
        ["service155 gateway155", "storage155 network155", "latency155 buffer155"],
    ),
    (
        ("gateway155 storage155 network155 latency155 buffer155 queue155", 6),
        ["gateway155", "storage155", "network155", "latency155", "buffer155", "queue155"],
    ),
    (
        ("gateway155 storage155 network155 latency155 buffer155 queue155", 10),
        ["gateway155", "storage155", "network155", "latency155", "buffer155", "queue155"],
    ),
    (
        ("gateway155 storage155 network155 latency155 buffer155 queue155", 18),
        ["gateway155", "storage155", "network155", "latency155", "buffer155 queue155"],
    ),
    (
        ("gateway155 storage155 network155 latency155 buffer155 queue155", 28),
        ["gateway155 storage155", "network155 latency155", "buffer155 queue155"],
    ),
    (
        ("storage155 network155 latency155 buffer155 queue155 worker155", 6),
        ["storage155", "network155", "latency155", "buffer155", "queue155", "worker155"],
    ),
    (
        ("storage155 network155 latency155 buffer155 queue155 worker155", 10),
        ["storage155", "network155", "latency155", "buffer155", "queue155", "worker155"],
    ),
    (
        ("storage155 network155 latency155 buffer155 queue155 worker155", 18),
        ["storage155", "network155", "latency155", "buffer155 queue155", "worker155"],
    ),
    (
        ("storage155 network155 latency155 buffer155 queue155 worker155", 28),
        ["storage155 network155", "latency155 buffer155", "queue155 worker155"],
    ),
    (
        ("network155 latency155 buffer155 queue155 worker155 kernel155", 6),
        ["network155", "latency155", "buffer155", "queue155", "worker155", "kernel155"],
    ),
    (
        ("network155 latency155 buffer155 queue155 worker155 kernel155", 10),
        ["network155", "latency155", "buffer155", "queue155", "worker155", "kernel155"],
    ),
    (
        ("network155 latency155 buffer155 queue155 worker155 kernel155", 18),
        ["network155", "latency155", "buffer155 queue155", "worker155", "kernel155"],
    ),
    (
        ("network155 latency155 buffer155 queue155 worker155 kernel155", 28),
        ["network155 latency155", "buffer155 queue155 worker155", "kernel155"],
    ),
    (
        ("latency155 buffer155 queue155 worker155 kernel155 signal155", 6),
        ["latency155", "buffer155", "queue155", "worker155", "kernel155", "signal155"],
    ),
    (
        ("latency155 buffer155 queue155 worker155 kernel155 signal155", 10),
        ["latency155", "buffer155", "queue155", "worker155", "kernel155", "signal155"],
    ),
    (
        ("latency155 buffer155 queue155 worker155 kernel155 signal155", 18),
        ["latency155", "buffer155 queue155", "worker155", "kernel155", "signal155"],
    ),
    (
        ("latency155 buffer155 queue155 worker155 kernel155 signal155", 28),
        ["latency155 buffer155", "queue155 worker155 kernel155", "signal155"],
    ),
    (
        ("buffer155 queue155 worker155 kernel155 signal155 packet155", 6),
        ["buffer155", "queue155", "worker155", "kernel155", "signal155", "packet155"],
    ),
    (
        ("buffer155 queue155 worker155 kernel155 signal155 packet155", 10),
        ["buffer155", "queue155", "worker155", "kernel155", "signal155", "packet155"],
    ),
    (
        ("buffer155 queue155 worker155 kernel155 signal155 packet155", 18),
        ["buffer155 queue155", "worker155", "kernel155", "signal155", "packet155"],
    ),
    (
        ("buffer155 queue155 worker155 kernel155 signal155 packet155", 28),
        ["buffer155 queue155 worker155", "kernel155 signal155", "packet155"],
    ),
    (
        ("queue155 worker155 kernel155 signal155 packet155 router155", 6),
        ["queue155", "worker155", "kernel155", "signal155", "packet155", "router155"],
    ),
    (
        ("queue155 worker155 kernel155 signal155 packet155 router155", 10),
        ["queue155", "worker155", "kernel155", "signal155", "packet155", "router155"],
    ),
    (
        ("queue155 worker155 kernel155 signal155 packet155 router155", 18),
        ["queue155 worker155", "kernel155", "signal155", "packet155", "router155"],
    ),
    (
        ("queue155 worker155 kernel155 signal155 packet155 router155", 28),
        ["queue155 worker155 kernel155", "signal155 packet155", "router155"],
    ),
    (
        ("worker155 kernel155 signal155 packet155 router155 cluster155", 6),
        ["worker155", "kernel155", "signal155", "packet155", "router155", "cluster155"],
    ),
    (
        ("worker155 kernel155 signal155 packet155 router155 cluster155", 10),
        ["worker155", "kernel155", "signal155", "packet155", "router155", "cluster155"],
    ),
    (
        ("worker155 kernel155 signal155 packet155 router155 cluster155", 18),
        ["worker155", "kernel155", "signal155", "packet155", "router155", "cluster155"],
    ),
    (
        ("worker155 kernel155 signal155 packet155 router155 cluster155", 28),
        ["worker155 kernel155", "signal155 packet155", "router155 cluster155"],
    ),
    (
        ("kernel155 signal155 packet155 router155 cluster155 mirror155", 6),
        ["kernel155", "signal155", "packet155", "router155", "cluster155", "mirror155"],
    ),
    (
        ("kernel155 signal155 packet155 router155 cluster155 mirror155", 10),
        ["kernel155", "signal155", "packet155", "router155", "cluster155", "mirror155"],
    ),
    (
        ("kernel155 signal155 packet155 router155 cluster155 mirror155", 18),
        ["kernel155", "signal155", "packet155", "router155", "cluster155", "mirror155"],
    ),
    (
        ("kernel155 signal155 packet155 router155 cluster155 mirror155", 28),
        ["kernel155 signal155", "packet155 router155", "cluster155 mirror155"],
    ),
    (
        ("signal155 packet155 router155 cluster155 mirror155 filter155", 6),
        ["signal155", "packet155", "router155", "cluster155", "mirror155", "filter155"],
    ),
    (
        ("signal155 packet155 router155 cluster155 mirror155 filter155", 10),
        ["signal155", "packet155", "router155", "cluster155", "mirror155", "filter155"],
    ),
    (
        ("signal155 packet155 router155 cluster155 mirror155 filter155", 18),
        ["signal155", "packet155", "router155", "cluster155", "mirror155", "filter155"],
    ),
    (
        ("signal155 packet155 router155 cluster155 mirror155 filter155", 28),
        ["signal155 packet155", "router155 cluster155", "mirror155 filter155"],
    ),
    (
        ("packet155 router155 cluster155 mirror155 filter155 ranking155", 6),
        ["packet155", "router155", "cluster155", "mirror155", "filter155", "ranking155"],
    ),
    (
        ("packet155 router155 cluster155 mirror155 filter155 ranking155", 10),
        ["packet155", "router155", "cluster155", "mirror155", "filter155", "ranking155"],
    ),
    (
        ("packet155 router155 cluster155 mirror155 filter155 ranking155", 18),
        ["packet155", "router155", "cluster155", "mirror155", "filter155", "ranking155"],
    ),
    (
        ("packet155 router155 cluster155 mirror155 filter155 ranking155", 28),
        ["packet155 router155", "cluster155 mirror155", "filter155 ranking155"],
    ),
    (
        ("router155 cluster155 mirror155 filter155 ranking155 encoding155", 6),
        ["router155", "cluster155", "mirror155", "filter155", "ranking155", "encoding155"],
    ),
    (
        ("router155 cluster155 mirror155 filter155 ranking155 encoding155", 10),
        ["router155", "cluster155", "mirror155", "filter155", "ranking155", "encoding155"],
    ),
    (
        ("router155 cluster155 mirror155 filter155 ranking155 encoding155", 18),
        ["router155", "cluster155", "mirror155", "filter155", "ranking155", "encoding155"],
    ),
    (
        ("router155 cluster155 mirror155 filter155 ranking155 encoding155", 28),
        ["router155 cluster155", "mirror155 filter155", "ranking155 encoding155"],
    ),
    (
        ("cluster155 mirror155 filter155 ranking155 encoding155 mapping155", 6),
        ["cluster155", "mirror155", "filter155", "ranking155", "encoding155", "mapping155"],
    ),
    (
        ("cluster155 mirror155 filter155 ranking155 encoding155 mapping155", 10),
        ["cluster155", "mirror155", "filter155", "ranking155", "encoding155", "mapping155"],
    ),
    (
        ("cluster155 mirror155 filter155 ranking155 encoding155 mapping155", 18),
        ["cluster155", "mirror155", "filter155", "ranking155", "encoding155", "mapping155"],
    ),
    (
        ("cluster155 mirror155 filter155 ranking155 encoding155 mapping155", 28),
        ["cluster155 mirror155", "filter155 ranking155", "encoding155 mapping155"],
    ),
    (
        ("mirror155 filter155 ranking155 encoding155 mapping155 record155", 6),
        ["mirror155", "filter155", "ranking155", "encoding155", "mapping155", "record155"],
    ),
    (
        ("mirror155 filter155 ranking155 encoding155 mapping155 record155", 10),
        ["mirror155", "filter155", "ranking155", "encoding155", "mapping155", "record155"],
    ),
    (
        ("mirror155 filter155 ranking155 encoding155 mapping155 record155", 18),
        ["mirror155", "filter155", "ranking155", "encoding155", "mapping155", "record155"],
    ),
    (
        ("mirror155 filter155 ranking155 encoding155 mapping155 record155", 28),
        ["mirror155 filter155", "ranking155 encoding155", "mapping155 record155"],
    ),
    (
        ("filter155 ranking155 encoding155 mapping155 record155 candle155", 6),
        ["filter155", "ranking155", "encoding155", "mapping155", "record155", "candle155"],
    ),
    (
        ("filter155 ranking155 encoding155 mapping155 record155 candle155", 10),
        ["filter155", "ranking155", "encoding155", "mapping155", "record155", "candle155"],
    ),
    (
        ("filter155 ranking155 encoding155 mapping155 record155 candle155", 18),
        ["filter155", "ranking155", "encoding155", "mapping155", "record155", "candle155"],
    ),
    (
        ("filter155 ranking155 encoding155 mapping155 record155 candle155", 28),
        ["filter155 ranking155", "encoding155 mapping155", "record155 candle155"],
    ),
    (
        ("ranking155 encoding155 mapping155 record155 candle155 thread155", 6),
        ["ranking155", "encoding155", "mapping155", "record155", "candle155", "thread155"],
    ),
    (
        ("ranking155 encoding155 mapping155 record155 candle155 thread155", 10),
        ["ranking155", "encoding155", "mapping155", "record155", "candle155", "thread155"],
    ),
    (
        ("ranking155 encoding155 mapping155 record155 candle155 thread155", 18),
        ["ranking155", "encoding155", "mapping155", "record155", "candle155", "thread155"],
    ),
    (
        ("ranking155 encoding155 mapping155 record155 candle155 thread155", 28),
        ["ranking155 encoding155", "mapping155 record155", "candle155 thread155"],
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
