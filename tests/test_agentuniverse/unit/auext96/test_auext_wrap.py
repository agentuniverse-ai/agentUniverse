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
        ("round 96: the quick brown fox jumps over the lazy dog", 4),
        ["round", "96:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 96: the quick brown fox jumps over the lazy dog", 8),
        ["round", "96: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 96: the quick brown fox jumps over the lazy dog", 12),
        ["round 96:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 96: the quick brown fox jumps over the lazy dog", 16),
        ["round 96: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 96: the quick brown fox jumps over the lazy dog", 24),
        ["round 96: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 96: the quick brown fox jumps over the lazy dog", 32),
        ["round 96: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 96: agentuniverse is a framework for multi agents", 4),
        ["round", "96:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 96: agentuniverse is a framework for multi agents", 8),
        ["round", "96:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 96: agentuniverse is a framework for multi agents", 12),
        ["round 96:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 96: agentuniverse is a framework for multi agents", 16),
        ["round 96:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 96: agentuniverse is a framework for multi agents", 24),
        ["round 96: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 96: agentuniverse is a framework for multi agents", 32),
        ["round 96: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 96: knowledge stored as vectors enables retrieval", 4),
        ["round", "96:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 96: knowledge stored as vectors enables retrieval", 8),
        ["round", "96:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 96: knowledge stored as vectors enables retrieval", 12),
        ["round 96:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 96: knowledge stored as vectors enables retrieval", 16),
        ["round 96:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 96: knowledge stored as vectors enables retrieval", 24),
        ["round 96: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 96: knowledge stored as vectors enables retrieval", 32),
        ["round 96: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 96: the processor reads the record then stops", 4),
        ["round", "96:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 96: the processor reads the record then stops", 8),
        ["round", "96: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 96: the processor reads the record then stops", 12),
        ["round 96:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 96: the processor reads the record then stops", 16),
        ["round 96: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 96: the processor reads the record then stops", 24),
        ["round 96: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 96: the processor reads the record then stops", 32),
        ["round 96: the processor reads", "the record then stops"],
    ),
    (
        ("round 96: a worker pulls the next task from the queue", 4),
        ["round", "96:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 96: a worker pulls the next task from the queue", 8),
        ["round", "96: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 96: a worker pulls the next task from the queue", 12),
        ["round 96: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 96: a worker pulls the next task from the queue", 16),
        ["round 96: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 96: a worker pulls the next task from the queue", 24),
        ["round 96: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 96: a worker pulls the next task from the queue", 32),
        ["round 96: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 96: signals travel through the network layer", 4),
        ["round", "96:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 96: signals travel through the network layer", 8),
        ["round", "96:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 96: signals travel through the network layer", 12),
        ["round 96:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 96: signals travel through the network layer", 16),
        ["round 96:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 96: signals travel through the network layer", 24),
        ["round 96: signals travel", "through the network", "layer"],
    ),
    (
        ("round 96: signals travel through the network layer", 32),
        ["round 96: signals travel through", "the network layer"],
    ),
    (
        ("round 96: the gateway routes each request by policy", 4),
        ["round", "96:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 96: the gateway routes each request by policy", 8),
        ["round", "96: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 96: the gateway routes each request by policy", 12),
        ["round 96:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 96: the gateway routes each request by policy", 16),
        ["round 96: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 96: the gateway routes each request by policy", 24),
        ["round 96: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 96: the gateway routes each request by policy", 32),
        ["round 96: the gateway routes", "each request by policy"],
    ),
    (
        ("round 96: memory grows until the buffer is full", 4),
        ["round", "96:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 96: memory grows until the buffer is full", 8),
        ["round", "96:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 96: memory grows until the buffer is full", 12),
        ["round 96:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 96: memory grows until the buffer is full", 16),
        ["round 96: memory", "grows until the", "buffer is full"],
    ),
    (("round 96: memory grows until the buffer is full", 24), ["round 96: memory grows", "until the buffer is full"]),
    (("round 96: memory grows until the buffer is full", 32), ["round 96: memory grows until the", "buffer is full"]),
    (
        ("round 96: the cluster mirrors every packet twice", 4),
        ["round", "96:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 96: the cluster mirrors every packet twice", 8),
        ["round", "96: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 96: the cluster mirrors every packet twice", 12),
        ["round 96:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 96: the cluster mirrors every packet twice", 16),
        ["round 96: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 96: the cluster mirrors every packet twice", 24),
        ["round 96: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 96: the cluster mirrors every packet twice", 32), ["round 96: the cluster mirrors", "every packet twice"]),
    (
        ("round 96: ranking uses tokens learned from the corpus", 4),
        ["round", "96:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 96: ranking uses tokens learned from the corpus", 8),
        ["round", "96:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 96: ranking uses tokens learned from the corpus", 12),
        ["round 96:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 96: ranking uses tokens learned from the corpus", 16),
        ["round 96:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 96: ranking uses tokens learned from the corpus", 24),
        ["round 96: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 96: ranking uses tokens learned from the corpus", 32),
        ["round 96: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 96: a long session ends when the candle dies", 4),
        ["round", "96:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 96: a long session ends when the candle dies", 8),
        ["round", "96: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 96: a long session ends when the candle dies", 12),
        ["round 96: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 96: a long session ends when the candle dies", 16),
        ["round 96: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 96: a long session ends when the candle dies", 24),
        ["round 96: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 96: a long session ends when the candle dies", 32),
        ["round 96: a long session ends", "when the candle dies"],
    ),
    (
        ("round 96: encode the prompt then map the result", 4),
        ["round", "96:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 96: encode the prompt then map the result", 8),
        ["round", "96:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 96: encode the prompt then map the result", 12),
        ["round 96:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 96: encode the prompt then map the result", 16),
        ["round 96: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 96: encode the prompt then map the result", 24),
        ["round 96: encode the", "prompt then map the", "result"],
    ),
    (("round 96: encode the prompt then map the result", 32), ["round 96: encode the prompt then", "map the result"]),
    (
        ("round 96: the kernel wakes the worker at dawn", 4),
        ["round", "96:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 96: the kernel wakes the worker at dawn", 8),
        ["round", "96: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 96: the kernel wakes the worker at dawn", 12),
        ["round 96:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 96: the kernel wakes the worker at dawn", 16), ["round 96: the", "kernel wakes the", "worker at dawn"]),
    (("round 96: the kernel wakes the worker at dawn", 24), ["round 96: the kernel", "wakes the worker at dawn"]),
    (("round 96: the kernel wakes the worker at dawn", 32), ["round 96: the kernel wakes the", "worker at dawn"]),
    (
        ("round 96: service latency drops after the patch", 4),
        ["round", "96:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 96: service latency drops after the patch", 8),
        ["round", "96:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 96: service latency drops after the patch", 12),
        ["round 96:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 96: service latency drops after the patch", 16),
        ["round 96:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 96: service latency drops after the patch", 24),
        ["round 96: service", "latency drops after the", "patch"],
    ),
    (("round 96: service latency drops after the patch", 32), ["round 96: service latency drops", "after the patch"]),
    (
        ("round 96: the library caches every vector it sees", 4),
        ["round", "96:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 96: the library caches every vector it sees", 8),
        ["round", "96: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 96: the library caches every vector it sees", 12),
        ["round 96:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 96: the library caches every vector it sees", 16),
        ["round 96: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 96: the library caches every vector it sees", 24),
        ["round 96: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 96: the library caches every vector it sees", 32),
        ["round 96: the library caches", "every vector it sees"],
    ),
    (
        ("round 96: agents argue then the debate resolves", 4),
        ["round", "96:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 96: agents argue then the debate resolves", 8),
        ["round", "96:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 96: agents argue then the debate resolves", 12),
        ["round 96:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 96: agents argue then the debate resolves", 16),
        ["round 96: agents", "argue then the", "debate resolves"],
    ),
    (("round 96: agents argue then the debate resolves", 24), ["round 96: agents argue", "then the debate resolves"]),
    (("round 96: agents argue then the debate resolves", 32), ["round 96: agents argue then the", "debate resolves"]),
    (
        ("round 96: the filter keeps only strong matches", 4),
        ["round", "96:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 96: the filter keeps only strong matches", 8),
        ["round", "96: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 96: the filter keeps only strong matches", 12),
        ["round 96:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 96: the filter keeps only strong matches", 16),
        ["round 96: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 96: the filter keeps only strong matches", 24), ["round 96: the filter", "keeps only strong", "matches"]),
    (("round 96: the filter keeps only strong matches", 32), ["round 96: the filter keeps only", "strong matches"]),
    (
        ("round 96: the model answers with a short reply", 4),
        ["round", "96:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 96: the model answers with a short reply", 8),
        ["round", "96: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 96: the model answers with a short reply", 12),
        ["round 96:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 96: the model answers with a short reply", 16),
        ["round 96: the", "model answers", "with a short", "reply"],
    ),
    (("round 96: the model answers with a short reply", 24), ["round 96: the model", "answers with a short", "reply"]),
    (("round 96: the model answers with a short reply", 32), ["round 96: the model answers with", "a short reply"]),
    (
        ("round 96: the recorder stores the reasoning trace", 4),
        ["round", "96:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 96: the recorder stores the reasoning trace", 8),
        ["round", "96: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 96: the recorder stores the reasoning trace", 12),
        ["round 96:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 96: the recorder stores the reasoning trace", 16),
        ["round 96: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 96: the recorder stores the reasoning trace", 24),
        ["round 96: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 96: the recorder stores the reasoning trace", 32),
        ["round 96: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 96: the angel watches the processor run", 4),
        ["round", "96:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 96: the angel watches the processor run", 8),
        ["round", "96: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 96: the angel watches the processor run", 12),
        ["round 96:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 96: the angel watches the processor run", 16), ["round 96: the", "angel watches", "the processor", "run"]),
    (("round 96: the angel watches the processor run", 24), ["round 96: the angel", "watches the processor", "run"]),
    (("round 96: the angel watches the processor run", 32), ["round 96: the angel watches the", "processor run"]),
    (
        ("round 96: angle of the vector decides the match", 4),
        ["round", "96:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 96: angle of the vector decides the match", 8),
        ["round", "96:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 96: angle of the vector decides the match", 12),
        ["round 96:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 96: angle of the vector decides the match", 16),
        ["round 96: angle", "of the vector", "decides the", "match"],
    ),
    (("round 96: angle of the vector decides the match", 24), ["round 96: angle of the", "vector decides the match"]),
    (("round 96: angle of the vector decides the match", 32), ["round 96: angle of the vector", "decides the match"]),
    (
        ("round 96: the candle burns twice as long at night", 4),
        ["round", "96:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 96: the candle burns twice as long at night", 8),
        ["round", "96: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 96: the candle burns twice as long at night", 12),
        ["round 96:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 96: the candle burns twice as long at night", 16),
        ["round 96: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 96: the candle burns twice as long at night", 24),
        ["round 96: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 96: the candle burns twice as long at night", 32),
        ["round 96: the candle burns twice", "as long at night"],
    ),
    (
        ("round 96: a mirror of the universe in one line", 4),
        ["round", "96:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 96: a mirror of the universe in one line", 8),
        ["round", "96: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 96: a mirror of the universe in one line", 12),
        ["round 96: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 96: a mirror of the universe in one line", 16),
        ["round 96: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 96: a mirror of the universe in one line", 24), ["round 96: a mirror of", "the universe in one line"]),
    (("round 96: a mirror of the universe in one line", 32), ["round 96: a mirror of the", "universe in one line"]),
    (
        ("round 96: the queue drains before the storm", 4),
        ["round", "96:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 96: the queue drains before the storm", 8),
        ["round", "96: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 96: the queue drains before the storm", 12), ["round 96:", "the queue", "drains", "before the", "storm"]),
    (("round 96: the queue drains before the storm", 16), ["round 96: the", "queue drains", "before the storm"]),
    (("round 96: the queue drains before the storm", 24), ["round 96: the queue", "drains before the storm"]),
    (("round 96: the queue drains before the storm", 32), ["round 96: the queue drains", "before the storm"]),
    (
        ("kitten96 sitting96 agent96 angle96 universe96 memory96", 6),
        ["kitten96", "sitting96", "agent96", "angle96", "universe96", "memory96"],
    ),
    (
        ("kitten96 sitting96 agent96 angle96 universe96 memory96", 10),
        ["kitten96", "sitting96", "agent96", "angle96", "universe96", "memory96"],
    ),
    (
        ("kitten96 sitting96 agent96 angle96 universe96 memory96", 18),
        ["kitten96 sitting96", "agent96 angle96", "universe96", "memory96"],
    ),
    (
        ("kitten96 sitting96 agent96 angle96 universe96 memory96", 28),
        ["kitten96 sitting96 agent96", "angle96 universe96 memory96"],
    ),
    (
        ("sitting96 agent96 angle96 universe96 memory96 stream96", 6),
        ["sitting96", "agent96", "angle96", "universe96", "memory96", "stream96"],
    ),
    (
        ("sitting96 agent96 angle96 universe96 memory96 stream96", 10),
        ["sitting96", "agent96", "angle96", "universe96", "memory96", "stream96"],
    ),
    (
        ("sitting96 agent96 angle96 universe96 memory96 stream96", 18),
        ["sitting96 agent96", "angle96 universe96", "memory96 stream96"],
    ),
    (
        ("sitting96 agent96 angle96 universe96 memory96 stream96", 28),
        ["sitting96 agent96 angle96", "universe96 memory96 stream96"],
    ),
    (
        ("agent96 angle96 universe96 memory96 stream96 context96", 6),
        ["agent96", "angle96", "universe96", "memory96", "stream96", "context96"],
    ),
    (
        ("agent96 angle96 universe96 memory96 stream96 context96", 10),
        ["agent96", "angle96", "universe96", "memory96", "stream96", "context96"],
    ),
    (
        ("agent96 angle96 universe96 memory96 stream96 context96", 18),
        ["agent96 angle96", "universe96", "memory96 stream96", "context96"],
    ),
    (
        ("agent96 angle96 universe96 memory96 stream96 context96", 28),
        ["agent96 angle96 universe96", "memory96 stream96 context96"],
    ),
    (
        ("angle96 universe96 memory96 stream96 context96 knowledge96", 6),
        ["angle96", "universe96", "memory96", "stream96", "context96", "knowledge96"],
    ),
    (
        ("angle96 universe96 memory96 stream96 context96 knowledge96", 10),
        ["angle96", "universe96", "memory96", "stream96", "context96", "knowledge96"],
    ),
    (
        ("angle96 universe96 memory96 stream96 context96 knowledge96", 18),
        ["angle96 universe96", "memory96 stream96", "context96", "knowledge96"],
    ),
    (
        ("angle96 universe96 memory96 stream96 context96 knowledge96", 28),
        ["angle96 universe96 memory96", "stream96 context96", "knowledge96"],
    ),
    (
        ("universe96 memory96 stream96 context96 knowledge96 vector96", 6),
        ["universe96", "memory96", "stream96", "context96", "knowledge96", "vector96"],
    ),
    (
        ("universe96 memory96 stream96 context96 knowledge96 vector96", 10),
        ["universe96", "memory96", "stream96", "context96", "knowledge96", "vector96"],
    ),
    (
        ("universe96 memory96 stream96 context96 knowledge96 vector96", 18),
        ["universe96", "memory96 stream96", "context96", "knowledge96", "vector96"],
    ),
    (
        ("universe96 memory96 stream96 context96 knowledge96 vector96", 28),
        ["universe96 memory96 stream96", "context96 knowledge96", "vector96"],
    ),
    (
        ("memory96 stream96 context96 knowledge96 vector96 processor96", 6),
        ["memory96", "stream96", "context96", "knowledge96", "vector96", "processor96"],
    ),
    (
        ("memory96 stream96 context96 knowledge96 vector96 processor96", 10),
        ["memory96", "stream96", "context96", "knowledge96", "vector96", "processor96"],
    ),
    (
        ("memory96 stream96 context96 knowledge96 vector96 processor96", 18),
        ["memory96 stream96", "context96", "knowledge96", "vector96", "processor96"],
    ),
    (
        ("memory96 stream96 context96 knowledge96 vector96 processor96", 28),
        ["memory96 stream96 context96", "knowledge96 vector96", "processor96"],
    ),
    (
        ("stream96 context96 knowledge96 vector96 processor96 reasoning96", 6),
        ["stream96", "context96", "knowledge96", "vector96", "processor96", "reasoning96"],
    ),
    (
        ("stream96 context96 knowledge96 vector96 processor96 reasoning96", 10),
        ["stream96", "context96", "knowledge96", "vector96", "processor96", "reasoning96"],
    ),
    (
        ("stream96 context96 knowledge96 vector96 processor96 reasoning96", 18),
        ["stream96 context96", "knowledge96", "vector96", "processor96", "reasoning96"],
    ),
    (
        ("stream96 context96 knowledge96 vector96 processor96 reasoning96", 28),
        ["stream96 context96", "knowledge96 vector96", "processor96 reasoning96"],
    ),
    (
        ("context96 knowledge96 vector96 processor96 reasoning96 machine96", 6),
        ["context96", "knowledge96", "vector96", "processor96", "reasoning96", "machine96"],
    ),
    (
        ("context96 knowledge96 vector96 processor96 reasoning96 machine96", 10),
        ["context96", "knowledge96", "vector96", "processor96", "reasoning96", "machine96"],
    ),
    (
        ("context96 knowledge96 vector96 processor96 reasoning96 machine96", 18),
        ["context96", "knowledge96", "vector96", "processor96", "reasoning96", "machine96"],
    ),
    (
        ("context96 knowledge96 vector96 processor96 reasoning96 machine96", 28),
        ["context96 knowledge96", "vector96 processor96", "reasoning96 machine96"],
    ),
    (
        ("knowledge96 vector96 processor96 reasoning96 machine96 learning96", 6),
        ["knowledge96", "vector96", "processor96", "reasoning96", "machine96", "learning96"],
    ),
    (
        ("knowledge96 vector96 processor96 reasoning96 machine96 learning96", 10),
        ["knowledge96", "vector96", "processor96", "reasoning96", "machine96", "learning96"],
    ),
    (
        ("knowledge96 vector96 processor96 reasoning96 machine96 learning96", 18),
        ["knowledge96", "vector96", "processor96", "reasoning96", "machine96", "learning96"],
    ),
    (
        ("knowledge96 vector96 processor96 reasoning96 machine96 learning96", 28),
        ["knowledge96 vector96", "processor96 reasoning96", "machine96 learning96"],
    ),
    (
        ("vector96 processor96 reasoning96 machine96 learning96 model96", 6),
        ["vector96", "processor96", "reasoning96", "machine96", "learning96", "model96"],
    ),
    (
        ("vector96 processor96 reasoning96 machine96 learning96 model96", 10),
        ["vector96", "processor96", "reasoning96", "machine96", "learning96", "model96"],
    ),
    (
        ("vector96 processor96 reasoning96 machine96 learning96 model96", 18),
        ["vector96", "processor96", "reasoning96", "machine96", "learning96 model96"],
    ),
    (
        ("vector96 processor96 reasoning96 machine96 learning96 model96", 28),
        ["vector96 processor96", "reasoning96 machine96", "learning96 model96"],
    ),
    (
        ("processor96 reasoning96 machine96 learning96 model96 token96", 6),
        ["processor96", "reasoning96", "machine96", "learning96", "model96", "token96"],
    ),
    (
        ("processor96 reasoning96 machine96 learning96 model96 token96", 10),
        ["processor96", "reasoning96", "machine96", "learning96", "model96", "token96"],
    ),
    (
        ("processor96 reasoning96 machine96 learning96 model96 token96", 18),
        ["processor96", "reasoning96", "machine96", "learning96 model96", "token96"],
    ),
    (
        ("processor96 reasoning96 machine96 learning96 model96 token96", 28),
        ["processor96 reasoning96", "machine96 learning96 model96", "token96"],
    ),
    (
        ("reasoning96 machine96 learning96 model96 token96 prompt96", 6),
        ["reasoning96", "machine96", "learning96", "model96", "token96", "prompt96"],
    ),
    (
        ("reasoning96 machine96 learning96 model96 token96 prompt96", 10),
        ["reasoning96", "machine96", "learning96", "model96", "token96", "prompt96"],
    ),
    (
        ("reasoning96 machine96 learning96 model96 token96 prompt96", 18),
        ["reasoning96", "machine96", "learning96 model96", "token96 prompt96"],
    ),
    (
        ("reasoning96 machine96 learning96 model96 token96 prompt96", 28),
        ["reasoning96 machine96", "learning96 model96 token96", "prompt96"],
    ),
    (
        ("machine96 learning96 model96 token96 prompt96 session96", 6),
        ["machine96", "learning96", "model96", "token96", "prompt96", "session96"],
    ),
    (
        ("machine96 learning96 model96 token96 prompt96 session96", 10),
        ["machine96", "learning96", "model96", "token96", "prompt96", "session96"],
    ),
    (
        ("machine96 learning96 model96 token96 prompt96 session96", 18),
        ["machine96", "learning96 model96", "token96 prompt96", "session96"],
    ),
    (
        ("machine96 learning96 model96 token96 prompt96 session96", 28),
        ["machine96 learning96 model96", "token96 prompt96 session96"],
    ),
    (
        ("learning96 model96 token96 prompt96 session96 library96", 6),
        ["learning96", "model96", "token96", "prompt96", "session96", "library96"],
    ),
    (
        ("learning96 model96 token96 prompt96 session96 library96", 10),
        ["learning96", "model96", "token96", "prompt96", "session96", "library96"],
    ),
    (
        ("learning96 model96 token96 prompt96 session96 library96", 18),
        ["learning96 model96", "token96 prompt96", "session96", "library96"],
    ),
    (
        ("learning96 model96 token96 prompt96 session96 library96", 28),
        ["learning96 model96 token96", "prompt96 session96 library96"],
    ),
    (
        ("model96 token96 prompt96 session96 library96 service96", 6),
        ["model96", "token96", "prompt96", "session96", "library96", "service96"],
    ),
    (
        ("model96 token96 prompt96 session96 library96 service96", 10),
        ["model96", "token96", "prompt96", "session96", "library96", "service96"],
    ),
    (
        ("model96 token96 prompt96 session96 library96 service96", 18),
        ["model96 token96", "prompt96 session96", "library96", "service96"],
    ),
    (
        ("model96 token96 prompt96 session96 library96 service96", 28),
        ["model96 token96 prompt96", "session96 library96", "service96"],
    ),
    (
        ("token96 prompt96 session96 library96 service96 gateway96", 6),
        ["token96", "prompt96", "session96", "library96", "service96", "gateway96"],
    ),
    (
        ("token96 prompt96 session96 library96 service96 gateway96", 10),
        ["token96", "prompt96", "session96", "library96", "service96", "gateway96"],
    ),
    (
        ("token96 prompt96 session96 library96 service96 gateway96", 18),
        ["token96 prompt96", "session96", "library96", "service96", "gateway96"],
    ),
    (
        ("token96 prompt96 session96 library96 service96 gateway96", 28),
        ["token96 prompt96 session96", "library96 service96", "gateway96"],
    ),
    (
        ("prompt96 session96 library96 service96 gateway96 storage96", 6),
        ["prompt96", "session96", "library96", "service96", "gateway96", "storage96"],
    ),
    (
        ("prompt96 session96 library96 service96 gateway96 storage96", 10),
        ["prompt96", "session96", "library96", "service96", "gateway96", "storage96"],
    ),
    (
        ("prompt96 session96 library96 service96 gateway96 storage96", 18),
        ["prompt96 session96", "library96", "service96", "gateway96", "storage96"],
    ),
    (
        ("prompt96 session96 library96 service96 gateway96 storage96", 28),
        ["prompt96 session96 library96", "service96 gateway96", "storage96"],
    ),
    (
        ("session96 library96 service96 gateway96 storage96 network96", 6),
        ["session96", "library96", "service96", "gateway96", "storage96", "network96"],
    ),
    (
        ("session96 library96 service96 gateway96 storage96 network96", 10),
        ["session96", "library96", "service96", "gateway96", "storage96", "network96"],
    ),
    (
        ("session96 library96 service96 gateway96 storage96 network96", 18),
        ["session96", "library96", "service96", "gateway96", "storage96", "network96"],
    ),
    (
        ("session96 library96 service96 gateway96 storage96 network96", 28),
        ["session96 library96", "service96 gateway96", "storage96 network96"],
    ),
    (
        ("library96 service96 gateway96 storage96 network96 latency96", 6),
        ["library96", "service96", "gateway96", "storage96", "network96", "latency96"],
    ),
    (
        ("library96 service96 gateway96 storage96 network96 latency96", 10),
        ["library96", "service96", "gateway96", "storage96", "network96", "latency96"],
    ),
    (
        ("library96 service96 gateway96 storage96 network96 latency96", 18),
        ["library96", "service96", "gateway96", "storage96", "network96", "latency96"],
    ),
    (
        ("library96 service96 gateway96 storage96 network96 latency96", 28),
        ["library96 service96", "gateway96 storage96", "network96 latency96"],
    ),
    (
        ("service96 gateway96 storage96 network96 latency96 buffer96", 6),
        ["service96", "gateway96", "storage96", "network96", "latency96", "buffer96"],
    ),
    (
        ("service96 gateway96 storage96 network96 latency96 buffer96", 10),
        ["service96", "gateway96", "storage96", "network96", "latency96", "buffer96"],
    ),
    (
        ("service96 gateway96 storage96 network96 latency96 buffer96", 18),
        ["service96", "gateway96", "storage96", "network96", "latency96 buffer96"],
    ),
    (
        ("service96 gateway96 storage96 network96 latency96 buffer96", 28),
        ["service96 gateway96", "storage96 network96", "latency96 buffer96"],
    ),
    (
        ("gateway96 storage96 network96 latency96 buffer96 queue96", 6),
        ["gateway96", "storage96", "network96", "latency96", "buffer96", "queue96"],
    ),
    (
        ("gateway96 storage96 network96 latency96 buffer96 queue96", 10),
        ["gateway96", "storage96", "network96", "latency96", "buffer96", "queue96"],
    ),
    (
        ("gateway96 storage96 network96 latency96 buffer96 queue96", 18),
        ["gateway96", "storage96", "network96", "latency96 buffer96", "queue96"],
    ),
    (
        ("gateway96 storage96 network96 latency96 buffer96 queue96", 28),
        ["gateway96 storage96", "network96 latency96 buffer96", "queue96"],
    ),
    (
        ("storage96 network96 latency96 buffer96 queue96 worker96", 6),
        ["storage96", "network96", "latency96", "buffer96", "queue96", "worker96"],
    ),
    (
        ("storage96 network96 latency96 buffer96 queue96 worker96", 10),
        ["storage96", "network96", "latency96", "buffer96", "queue96", "worker96"],
    ),
    (
        ("storage96 network96 latency96 buffer96 queue96 worker96", 18),
        ["storage96", "network96", "latency96 buffer96", "queue96 worker96"],
    ),
    (
        ("storage96 network96 latency96 buffer96 queue96 worker96", 28),
        ["storage96 network96", "latency96 buffer96 queue96", "worker96"],
    ),
    (
        ("network96 latency96 buffer96 queue96 worker96 kernel96", 6),
        ["network96", "latency96", "buffer96", "queue96", "worker96", "kernel96"],
    ),
    (
        ("network96 latency96 buffer96 queue96 worker96 kernel96", 10),
        ["network96", "latency96", "buffer96", "queue96", "worker96", "kernel96"],
    ),
    (
        ("network96 latency96 buffer96 queue96 worker96 kernel96", 18),
        ["network96", "latency96 buffer96", "queue96 worker96", "kernel96"],
    ),
    (
        ("network96 latency96 buffer96 queue96 worker96 kernel96", 28),
        ["network96 latency96 buffer96", "queue96 worker96 kernel96"],
    ),
    (
        ("latency96 buffer96 queue96 worker96 kernel96 signal96", 6),
        ["latency96", "buffer96", "queue96", "worker96", "kernel96", "signal96"],
    ),
    (
        ("latency96 buffer96 queue96 worker96 kernel96 signal96", 10),
        ["latency96", "buffer96", "queue96", "worker96", "kernel96", "signal96"],
    ),
    (
        ("latency96 buffer96 queue96 worker96 kernel96 signal96", 18),
        ["latency96 buffer96", "queue96 worker96", "kernel96 signal96"],
    ),
    (
        ("latency96 buffer96 queue96 worker96 kernel96 signal96", 28),
        ["latency96 buffer96 queue96", "worker96 kernel96 signal96"],
    ),
    (
        ("buffer96 queue96 worker96 kernel96 signal96 packet96", 6),
        ["buffer96", "queue96", "worker96", "kernel96", "signal96", "packet96"],
    ),
    (
        ("buffer96 queue96 worker96 kernel96 signal96 packet96", 10),
        ["buffer96", "queue96", "worker96", "kernel96", "signal96", "packet96"],
    ),
    (
        ("buffer96 queue96 worker96 kernel96 signal96 packet96", 18),
        ["buffer96 queue96", "worker96 kernel96", "signal96 packet96"],
    ),
    (
        ("buffer96 queue96 worker96 kernel96 signal96 packet96", 28),
        ["buffer96 queue96 worker96", "kernel96 signal96 packet96"],
    ),
    (
        ("queue96 worker96 kernel96 signal96 packet96 router96", 6),
        ["queue96", "worker96", "kernel96", "signal96", "packet96", "router96"],
    ),
    (
        ("queue96 worker96 kernel96 signal96 packet96 router96", 10),
        ["queue96", "worker96", "kernel96", "signal96", "packet96", "router96"],
    ),
    (
        ("queue96 worker96 kernel96 signal96 packet96 router96", 18),
        ["queue96 worker96", "kernel96 signal96", "packet96 router96"],
    ),
    (
        ("queue96 worker96 kernel96 signal96 packet96 router96", 28),
        ["queue96 worker96 kernel96", "signal96 packet96 router96"],
    ),
    (
        ("worker96 kernel96 signal96 packet96 router96 cluster96", 6),
        ["worker96", "kernel96", "signal96", "packet96", "router96", "cluster96"],
    ),
    (
        ("worker96 kernel96 signal96 packet96 router96 cluster96", 10),
        ["worker96", "kernel96", "signal96", "packet96", "router96", "cluster96"],
    ),
    (
        ("worker96 kernel96 signal96 packet96 router96 cluster96", 18),
        ["worker96 kernel96", "signal96 packet96", "router96 cluster96"],
    ),
    (
        ("worker96 kernel96 signal96 packet96 router96 cluster96", 28),
        ["worker96 kernel96 signal96", "packet96 router96 cluster96"],
    ),
    (
        ("kernel96 signal96 packet96 router96 cluster96 mirror96", 6),
        ["kernel96", "signal96", "packet96", "router96", "cluster96", "mirror96"],
    ),
    (
        ("kernel96 signal96 packet96 router96 cluster96 mirror96", 10),
        ["kernel96", "signal96", "packet96", "router96", "cluster96", "mirror96"],
    ),
    (
        ("kernel96 signal96 packet96 router96 cluster96 mirror96", 18),
        ["kernel96 signal96", "packet96 router96", "cluster96 mirror96"],
    ),
    (
        ("kernel96 signal96 packet96 router96 cluster96 mirror96", 28),
        ["kernel96 signal96 packet96", "router96 cluster96 mirror96"],
    ),
    (
        ("signal96 packet96 router96 cluster96 mirror96 filter96", 6),
        ["signal96", "packet96", "router96", "cluster96", "mirror96", "filter96"],
    ),
    (
        ("signal96 packet96 router96 cluster96 mirror96 filter96", 10),
        ["signal96", "packet96", "router96", "cluster96", "mirror96", "filter96"],
    ),
    (
        ("signal96 packet96 router96 cluster96 mirror96 filter96", 18),
        ["signal96 packet96", "router96 cluster96", "mirror96 filter96"],
    ),
    (
        ("signal96 packet96 router96 cluster96 mirror96 filter96", 28),
        ["signal96 packet96 router96", "cluster96 mirror96 filter96"],
    ),
    (
        ("packet96 router96 cluster96 mirror96 filter96 ranking96", 6),
        ["packet96", "router96", "cluster96", "mirror96", "filter96", "ranking96"],
    ),
    (
        ("packet96 router96 cluster96 mirror96 filter96 ranking96", 10),
        ["packet96", "router96", "cluster96", "mirror96", "filter96", "ranking96"],
    ),
    (
        ("packet96 router96 cluster96 mirror96 filter96 ranking96", 18),
        ["packet96 router96", "cluster96 mirror96", "filter96 ranking96"],
    ),
    (
        ("packet96 router96 cluster96 mirror96 filter96 ranking96", 28),
        ["packet96 router96 cluster96", "mirror96 filter96 ranking96"],
    ),
    (
        ("router96 cluster96 mirror96 filter96 ranking96 encoding96", 6),
        ["router96", "cluster96", "mirror96", "filter96", "ranking96", "encoding96"],
    ),
    (
        ("router96 cluster96 mirror96 filter96 ranking96 encoding96", 10),
        ["router96", "cluster96", "mirror96", "filter96", "ranking96", "encoding96"],
    ),
    (
        ("router96 cluster96 mirror96 filter96 ranking96 encoding96", 18),
        ["router96 cluster96", "mirror96 filter96", "ranking96", "encoding96"],
    ),
    (
        ("router96 cluster96 mirror96 filter96 ranking96 encoding96", 28),
        ["router96 cluster96 mirror96", "filter96 ranking96", "encoding96"],
    ),
    (
        ("cluster96 mirror96 filter96 ranking96 encoding96 mapping96", 6),
        ["cluster96", "mirror96", "filter96", "ranking96", "encoding96", "mapping96"],
    ),
    (
        ("cluster96 mirror96 filter96 ranking96 encoding96 mapping96", 10),
        ["cluster96", "mirror96", "filter96", "ranking96", "encoding96", "mapping96"],
    ),
    (
        ("cluster96 mirror96 filter96 ranking96 encoding96 mapping96", 18),
        ["cluster96 mirror96", "filter96 ranking96", "encoding96", "mapping96"],
    ),
    (
        ("cluster96 mirror96 filter96 ranking96 encoding96 mapping96", 28),
        ["cluster96 mirror96 filter96", "ranking96 encoding96", "mapping96"],
    ),
    (
        ("mirror96 filter96 ranking96 encoding96 mapping96 record96", 6),
        ["mirror96", "filter96", "ranking96", "encoding96", "mapping96", "record96"],
    ),
    (
        ("mirror96 filter96 ranking96 encoding96 mapping96 record96", 10),
        ["mirror96", "filter96", "ranking96", "encoding96", "mapping96", "record96"],
    ),
    (
        ("mirror96 filter96 ranking96 encoding96 mapping96 record96", 18),
        ["mirror96 filter96", "ranking96", "encoding96", "mapping96 record96"],
    ),
    (
        ("mirror96 filter96 ranking96 encoding96 mapping96 record96", 28),
        ["mirror96 filter96 ranking96", "encoding96 mapping96", "record96"],
    ),
    (
        ("filter96 ranking96 encoding96 mapping96 record96 candle96", 6),
        ["filter96", "ranking96", "encoding96", "mapping96", "record96", "candle96"],
    ),
    (
        ("filter96 ranking96 encoding96 mapping96 record96 candle96", 10),
        ["filter96", "ranking96", "encoding96", "mapping96", "record96", "candle96"],
    ),
    (
        ("filter96 ranking96 encoding96 mapping96 record96 candle96", 18),
        ["filter96 ranking96", "encoding96", "mapping96 record96", "candle96"],
    ),
    (
        ("filter96 ranking96 encoding96 mapping96 record96 candle96", 28),
        ["filter96 ranking96", "encoding96 mapping96", "record96 candle96"],
    ),
    (
        ("ranking96 encoding96 mapping96 record96 candle96 thread96", 6),
        ["ranking96", "encoding96", "mapping96", "record96", "candle96", "thread96"],
    ),
    (
        ("ranking96 encoding96 mapping96 record96 candle96 thread96", 10),
        ["ranking96", "encoding96", "mapping96", "record96", "candle96", "thread96"],
    ),
    (
        ("ranking96 encoding96 mapping96 record96 candle96 thread96", 18),
        ["ranking96", "encoding96", "mapping96 record96", "candle96 thread96"],
    ),
    (
        ("ranking96 encoding96 mapping96 record96 candle96 thread96", 28),
        ["ranking96 encoding96", "mapping96 record96 candle96", "thread96"],
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
