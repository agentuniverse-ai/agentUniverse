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
        ("round 15: the quick brown fox jumps over the lazy dog", 4),
        ["round", "15:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 15: the quick brown fox jumps over the lazy dog", 8),
        ["round", "15: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 15: the quick brown fox jumps over the lazy dog", 12),
        ["round 15:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 15: the quick brown fox jumps over the lazy dog", 16),
        ["round 15: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 15: the quick brown fox jumps over the lazy dog", 24),
        ["round 15: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 15: the quick brown fox jumps over the lazy dog", 32),
        ["round 15: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 15: agentuniverse is a framework for multi agents", 4),
        ["round", "15:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 15: agentuniverse is a framework for multi agents", 8),
        ["round", "15:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 15: agentuniverse is a framework for multi agents", 12),
        ["round 15:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 15: agentuniverse is a framework for multi agents", 16),
        ["round 15:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 15: agentuniverse is a framework for multi agents", 24),
        ["round 15: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 15: agentuniverse is a framework for multi agents", 32),
        ["round 15: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 15: knowledge stored as vectors enables retrieval", 4),
        ["round", "15:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 15: knowledge stored as vectors enables retrieval", 8),
        ["round", "15:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 15: knowledge stored as vectors enables retrieval", 12),
        ["round 15:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 15: knowledge stored as vectors enables retrieval", 16),
        ["round 15:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 15: knowledge stored as vectors enables retrieval", 24),
        ["round 15: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 15: knowledge stored as vectors enables retrieval", 32),
        ["round 15: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 15: the processor reads the record then stops", 4),
        ["round", "15:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 15: the processor reads the record then stops", 8),
        ["round", "15: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 15: the processor reads the record then stops", 12),
        ["round 15:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 15: the processor reads the record then stops", 16),
        ["round 15: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 15: the processor reads the record then stops", 24),
        ["round 15: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 15: the processor reads the record then stops", 32),
        ["round 15: the processor reads", "the record then stops"],
    ),
    (
        ("round 15: a worker pulls the next task from the queue", 4),
        ["round", "15:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 15: a worker pulls the next task from the queue", 8),
        ["round", "15: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 15: a worker pulls the next task from the queue", 12),
        ["round 15: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 15: a worker pulls the next task from the queue", 16),
        ["round 15: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 15: a worker pulls the next task from the queue", 24),
        ["round 15: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 15: a worker pulls the next task from the queue", 32),
        ["round 15: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 15: signals travel through the network layer", 4),
        ["round", "15:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 15: signals travel through the network layer", 8),
        ["round", "15:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 15: signals travel through the network layer", 12),
        ["round 15:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 15: signals travel through the network layer", 16),
        ["round 15:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 15: signals travel through the network layer", 24),
        ["round 15: signals travel", "through the network", "layer"],
    ),
    (
        ("round 15: signals travel through the network layer", 32),
        ["round 15: signals travel through", "the network layer"],
    ),
    (
        ("round 15: the gateway routes each request by policy", 4),
        ["round", "15:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 15: the gateway routes each request by policy", 8),
        ["round", "15: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 15: the gateway routes each request by policy", 12),
        ["round 15:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 15: the gateway routes each request by policy", 16),
        ["round 15: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 15: the gateway routes each request by policy", 24),
        ["round 15: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 15: the gateway routes each request by policy", 32),
        ["round 15: the gateway routes", "each request by policy"],
    ),
    (
        ("round 15: memory grows until the buffer is full", 4),
        ["round", "15:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 15: memory grows until the buffer is full", 8),
        ["round", "15:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 15: memory grows until the buffer is full", 12),
        ["round 15:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 15: memory grows until the buffer is full", 16),
        ["round 15: memory", "grows until the", "buffer is full"],
    ),
    (("round 15: memory grows until the buffer is full", 24), ["round 15: memory grows", "until the buffer is full"]),
    (("round 15: memory grows until the buffer is full", 32), ["round 15: memory grows until the", "buffer is full"]),
    (
        ("round 15: the cluster mirrors every packet twice", 4),
        ["round", "15:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 15: the cluster mirrors every packet twice", 8),
        ["round", "15: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 15: the cluster mirrors every packet twice", 12),
        ["round 15:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 15: the cluster mirrors every packet twice", 16),
        ["round 15: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 15: the cluster mirrors every packet twice", 24),
        ["round 15: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 15: the cluster mirrors every packet twice", 32), ["round 15: the cluster mirrors", "every packet twice"]),
    (
        ("round 15: ranking uses tokens learned from the corpus", 4),
        ["round", "15:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 15: ranking uses tokens learned from the corpus", 8),
        ["round", "15:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 15: ranking uses tokens learned from the corpus", 12),
        ["round 15:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 15: ranking uses tokens learned from the corpus", 16),
        ["round 15:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 15: ranking uses tokens learned from the corpus", 24),
        ["round 15: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 15: ranking uses tokens learned from the corpus", 32),
        ["round 15: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 15: a long session ends when the candle dies", 4),
        ["round", "15:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 15: a long session ends when the candle dies", 8),
        ["round", "15: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 15: a long session ends when the candle dies", 12),
        ["round 15: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 15: a long session ends when the candle dies", 16),
        ["round 15: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 15: a long session ends when the candle dies", 24),
        ["round 15: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 15: a long session ends when the candle dies", 32),
        ["round 15: a long session ends", "when the candle dies"],
    ),
    (
        ("round 15: encode the prompt then map the result", 4),
        ["round", "15:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 15: encode the prompt then map the result", 8),
        ["round", "15:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 15: encode the prompt then map the result", 12),
        ["round 15:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 15: encode the prompt then map the result", 16),
        ["round 15: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 15: encode the prompt then map the result", 24),
        ["round 15: encode the", "prompt then map the", "result"],
    ),
    (("round 15: encode the prompt then map the result", 32), ["round 15: encode the prompt then", "map the result"]),
    (
        ("round 15: the kernel wakes the worker at dawn", 4),
        ["round", "15:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 15: the kernel wakes the worker at dawn", 8),
        ["round", "15: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 15: the kernel wakes the worker at dawn", 12),
        ["round 15:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 15: the kernel wakes the worker at dawn", 16), ["round 15: the", "kernel wakes the", "worker at dawn"]),
    (("round 15: the kernel wakes the worker at dawn", 24), ["round 15: the kernel", "wakes the worker at dawn"]),
    (("round 15: the kernel wakes the worker at dawn", 32), ["round 15: the kernel wakes the", "worker at dawn"]),
    (
        ("round 15: service latency drops after the patch", 4),
        ["round", "15:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 15: service latency drops after the patch", 8),
        ["round", "15:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 15: service latency drops after the patch", 12),
        ["round 15:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 15: service latency drops after the patch", 16),
        ["round 15:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 15: service latency drops after the patch", 24),
        ["round 15: service", "latency drops after the", "patch"],
    ),
    (("round 15: service latency drops after the patch", 32), ["round 15: service latency drops", "after the patch"]),
    (
        ("round 15: the library caches every vector it sees", 4),
        ["round", "15:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 15: the library caches every vector it sees", 8),
        ["round", "15: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 15: the library caches every vector it sees", 12),
        ["round 15:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 15: the library caches every vector it sees", 16),
        ["round 15: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 15: the library caches every vector it sees", 24),
        ["round 15: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 15: the library caches every vector it sees", 32),
        ["round 15: the library caches", "every vector it sees"],
    ),
    (
        ("round 15: agents argue then the debate resolves", 4),
        ["round", "15:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 15: agents argue then the debate resolves", 8),
        ["round", "15:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 15: agents argue then the debate resolves", 12),
        ["round 15:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 15: agents argue then the debate resolves", 16),
        ["round 15: agents", "argue then the", "debate resolves"],
    ),
    (("round 15: agents argue then the debate resolves", 24), ["round 15: agents argue", "then the debate resolves"]),
    (("round 15: agents argue then the debate resolves", 32), ["round 15: agents argue then the", "debate resolves"]),
    (
        ("round 15: the filter keeps only strong matches", 4),
        ["round", "15:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 15: the filter keeps only strong matches", 8),
        ["round", "15: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 15: the filter keeps only strong matches", 12),
        ["round 15:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 15: the filter keeps only strong matches", 16),
        ["round 15: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 15: the filter keeps only strong matches", 24), ["round 15: the filter", "keeps only strong", "matches"]),
    (("round 15: the filter keeps only strong matches", 32), ["round 15: the filter keeps only", "strong matches"]),
    (
        ("round 15: the model answers with a short reply", 4),
        ["round", "15:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 15: the model answers with a short reply", 8),
        ["round", "15: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 15: the model answers with a short reply", 12),
        ["round 15:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 15: the model answers with a short reply", 16),
        ["round 15: the", "model answers", "with a short", "reply"],
    ),
    (("round 15: the model answers with a short reply", 24), ["round 15: the model", "answers with a short", "reply"]),
    (("round 15: the model answers with a short reply", 32), ["round 15: the model answers with", "a short reply"]),
    (
        ("round 15: the recorder stores the reasoning trace", 4),
        ["round", "15:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 15: the recorder stores the reasoning trace", 8),
        ["round", "15: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 15: the recorder stores the reasoning trace", 12),
        ["round 15:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 15: the recorder stores the reasoning trace", 16),
        ["round 15: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 15: the recorder stores the reasoning trace", 24),
        ["round 15: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 15: the recorder stores the reasoning trace", 32),
        ["round 15: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 15: the angel watches the processor run", 4),
        ["round", "15:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 15: the angel watches the processor run", 8),
        ["round", "15: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 15: the angel watches the processor run", 12),
        ["round 15:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 15: the angel watches the processor run", 16), ["round 15: the", "angel watches", "the processor", "run"]),
    (("round 15: the angel watches the processor run", 24), ["round 15: the angel", "watches the processor", "run"]),
    (("round 15: the angel watches the processor run", 32), ["round 15: the angel watches the", "processor run"]),
    (
        ("round 15: angle of the vector decides the match", 4),
        ["round", "15:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 15: angle of the vector decides the match", 8),
        ["round", "15:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 15: angle of the vector decides the match", 12),
        ["round 15:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 15: angle of the vector decides the match", 16),
        ["round 15: angle", "of the vector", "decides the", "match"],
    ),
    (("round 15: angle of the vector decides the match", 24), ["round 15: angle of the", "vector decides the match"]),
    (("round 15: angle of the vector decides the match", 32), ["round 15: angle of the vector", "decides the match"]),
    (
        ("round 15: the candle burns twice as long at night", 4),
        ["round", "15:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 15: the candle burns twice as long at night", 8),
        ["round", "15: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 15: the candle burns twice as long at night", 12),
        ["round 15:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 15: the candle burns twice as long at night", 16),
        ["round 15: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 15: the candle burns twice as long at night", 24),
        ["round 15: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 15: the candle burns twice as long at night", 32),
        ["round 15: the candle burns twice", "as long at night"],
    ),
    (
        ("round 15: a mirror of the universe in one line", 4),
        ["round", "15:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 15: a mirror of the universe in one line", 8),
        ["round", "15: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 15: a mirror of the universe in one line", 12),
        ["round 15: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 15: a mirror of the universe in one line", 16),
        ["round 15: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 15: a mirror of the universe in one line", 24), ["round 15: a mirror of", "the universe in one line"]),
    (("round 15: a mirror of the universe in one line", 32), ["round 15: a mirror of the", "universe in one line"]),
    (
        ("round 15: the queue drains before the storm", 4),
        ["round", "15:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 15: the queue drains before the storm", 8),
        ["round", "15: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 15: the queue drains before the storm", 12), ["round 15:", "the queue", "drains", "before the", "storm"]),
    (("round 15: the queue drains before the storm", 16), ["round 15: the", "queue drains", "before the storm"]),
    (("round 15: the queue drains before the storm", 24), ["round 15: the queue", "drains before the storm"]),
    (("round 15: the queue drains before the storm", 32), ["round 15: the queue drains", "before the storm"]),
    (
        ("kitten15 sitting15 agent15 angle15 universe15 memory15", 6),
        ["kitten15", "sitting15", "agent15", "angle15", "universe15", "memory15"],
    ),
    (
        ("kitten15 sitting15 agent15 angle15 universe15 memory15", 10),
        ["kitten15", "sitting15", "agent15", "angle15", "universe15", "memory15"],
    ),
    (
        ("kitten15 sitting15 agent15 angle15 universe15 memory15", 18),
        ["kitten15 sitting15", "agent15 angle15", "universe15", "memory15"],
    ),
    (
        ("kitten15 sitting15 agent15 angle15 universe15 memory15", 28),
        ["kitten15 sitting15 agent15", "angle15 universe15 memory15"],
    ),
    (
        ("sitting15 agent15 angle15 universe15 memory15 stream15", 6),
        ["sitting15", "agent15", "angle15", "universe15", "memory15", "stream15"],
    ),
    (
        ("sitting15 agent15 angle15 universe15 memory15 stream15", 10),
        ["sitting15", "agent15", "angle15", "universe15", "memory15", "stream15"],
    ),
    (
        ("sitting15 agent15 angle15 universe15 memory15 stream15", 18),
        ["sitting15 agent15", "angle15 universe15", "memory15 stream15"],
    ),
    (
        ("sitting15 agent15 angle15 universe15 memory15 stream15", 28),
        ["sitting15 agent15 angle15", "universe15 memory15 stream15"],
    ),
    (
        ("agent15 angle15 universe15 memory15 stream15 context15", 6),
        ["agent15", "angle15", "universe15", "memory15", "stream15", "context15"],
    ),
    (
        ("agent15 angle15 universe15 memory15 stream15 context15", 10),
        ["agent15", "angle15", "universe15", "memory15", "stream15", "context15"],
    ),
    (
        ("agent15 angle15 universe15 memory15 stream15 context15", 18),
        ["agent15 angle15", "universe15", "memory15 stream15", "context15"],
    ),
    (
        ("agent15 angle15 universe15 memory15 stream15 context15", 28),
        ["agent15 angle15 universe15", "memory15 stream15 context15"],
    ),
    (
        ("angle15 universe15 memory15 stream15 context15 knowledge15", 6),
        ["angle15", "universe15", "memory15", "stream15", "context15", "knowledge15"],
    ),
    (
        ("angle15 universe15 memory15 stream15 context15 knowledge15", 10),
        ["angle15", "universe15", "memory15", "stream15", "context15", "knowledge15"],
    ),
    (
        ("angle15 universe15 memory15 stream15 context15 knowledge15", 18),
        ["angle15 universe15", "memory15 stream15", "context15", "knowledge15"],
    ),
    (
        ("angle15 universe15 memory15 stream15 context15 knowledge15", 28),
        ["angle15 universe15 memory15", "stream15 context15", "knowledge15"],
    ),
    (
        ("universe15 memory15 stream15 context15 knowledge15 vector15", 6),
        ["universe15", "memory15", "stream15", "context15", "knowledge15", "vector15"],
    ),
    (
        ("universe15 memory15 stream15 context15 knowledge15 vector15", 10),
        ["universe15", "memory15", "stream15", "context15", "knowledge15", "vector15"],
    ),
    (
        ("universe15 memory15 stream15 context15 knowledge15 vector15", 18),
        ["universe15", "memory15 stream15", "context15", "knowledge15", "vector15"],
    ),
    (
        ("universe15 memory15 stream15 context15 knowledge15 vector15", 28),
        ["universe15 memory15 stream15", "context15 knowledge15", "vector15"],
    ),
    (
        ("memory15 stream15 context15 knowledge15 vector15 processor15", 6),
        ["memory15", "stream15", "context15", "knowledge15", "vector15", "processor15"],
    ),
    (
        ("memory15 stream15 context15 knowledge15 vector15 processor15", 10),
        ["memory15", "stream15", "context15", "knowledge15", "vector15", "processor15"],
    ),
    (
        ("memory15 stream15 context15 knowledge15 vector15 processor15", 18),
        ["memory15 stream15", "context15", "knowledge15", "vector15", "processor15"],
    ),
    (
        ("memory15 stream15 context15 knowledge15 vector15 processor15", 28),
        ["memory15 stream15 context15", "knowledge15 vector15", "processor15"],
    ),
    (
        ("stream15 context15 knowledge15 vector15 processor15 reasoning15", 6),
        ["stream15", "context15", "knowledge15", "vector15", "processor15", "reasoning15"],
    ),
    (
        ("stream15 context15 knowledge15 vector15 processor15 reasoning15", 10),
        ["stream15", "context15", "knowledge15", "vector15", "processor15", "reasoning15"],
    ),
    (
        ("stream15 context15 knowledge15 vector15 processor15 reasoning15", 18),
        ["stream15 context15", "knowledge15", "vector15", "processor15", "reasoning15"],
    ),
    (
        ("stream15 context15 knowledge15 vector15 processor15 reasoning15", 28),
        ["stream15 context15", "knowledge15 vector15", "processor15 reasoning15"],
    ),
    (
        ("context15 knowledge15 vector15 processor15 reasoning15 machine15", 6),
        ["context15", "knowledge15", "vector15", "processor15", "reasoning15", "machine15"],
    ),
    (
        ("context15 knowledge15 vector15 processor15 reasoning15 machine15", 10),
        ["context15", "knowledge15", "vector15", "processor15", "reasoning15", "machine15"],
    ),
    (
        ("context15 knowledge15 vector15 processor15 reasoning15 machine15", 18),
        ["context15", "knowledge15", "vector15", "processor15", "reasoning15", "machine15"],
    ),
    (
        ("context15 knowledge15 vector15 processor15 reasoning15 machine15", 28),
        ["context15 knowledge15", "vector15 processor15", "reasoning15 machine15"],
    ),
    (
        ("knowledge15 vector15 processor15 reasoning15 machine15 learning15", 6),
        ["knowledge15", "vector15", "processor15", "reasoning15", "machine15", "learning15"],
    ),
    (
        ("knowledge15 vector15 processor15 reasoning15 machine15 learning15", 10),
        ["knowledge15", "vector15", "processor15", "reasoning15", "machine15", "learning15"],
    ),
    (
        ("knowledge15 vector15 processor15 reasoning15 machine15 learning15", 18),
        ["knowledge15", "vector15", "processor15", "reasoning15", "machine15", "learning15"],
    ),
    (
        ("knowledge15 vector15 processor15 reasoning15 machine15 learning15", 28),
        ["knowledge15 vector15", "processor15 reasoning15", "machine15 learning15"],
    ),
    (
        ("vector15 processor15 reasoning15 machine15 learning15 model15", 6),
        ["vector15", "processor15", "reasoning15", "machine15", "learning15", "model15"],
    ),
    (
        ("vector15 processor15 reasoning15 machine15 learning15 model15", 10),
        ["vector15", "processor15", "reasoning15", "machine15", "learning15", "model15"],
    ),
    (
        ("vector15 processor15 reasoning15 machine15 learning15 model15", 18),
        ["vector15", "processor15", "reasoning15", "machine15", "learning15 model15"],
    ),
    (
        ("vector15 processor15 reasoning15 machine15 learning15 model15", 28),
        ["vector15 processor15", "reasoning15 machine15", "learning15 model15"],
    ),
    (
        ("processor15 reasoning15 machine15 learning15 model15 token15", 6),
        ["processor15", "reasoning15", "machine15", "learning15", "model15", "token15"],
    ),
    (
        ("processor15 reasoning15 machine15 learning15 model15 token15", 10),
        ["processor15", "reasoning15", "machine15", "learning15", "model15", "token15"],
    ),
    (
        ("processor15 reasoning15 machine15 learning15 model15 token15", 18),
        ["processor15", "reasoning15", "machine15", "learning15 model15", "token15"],
    ),
    (
        ("processor15 reasoning15 machine15 learning15 model15 token15", 28),
        ["processor15 reasoning15", "machine15 learning15 model15", "token15"],
    ),
    (
        ("reasoning15 machine15 learning15 model15 token15 prompt15", 6),
        ["reasoning15", "machine15", "learning15", "model15", "token15", "prompt15"],
    ),
    (
        ("reasoning15 machine15 learning15 model15 token15 prompt15", 10),
        ["reasoning15", "machine15", "learning15", "model15", "token15", "prompt15"],
    ),
    (
        ("reasoning15 machine15 learning15 model15 token15 prompt15", 18),
        ["reasoning15", "machine15", "learning15 model15", "token15 prompt15"],
    ),
    (
        ("reasoning15 machine15 learning15 model15 token15 prompt15", 28),
        ["reasoning15 machine15", "learning15 model15 token15", "prompt15"],
    ),
    (
        ("machine15 learning15 model15 token15 prompt15 session15", 6),
        ["machine15", "learning15", "model15", "token15", "prompt15", "session15"],
    ),
    (
        ("machine15 learning15 model15 token15 prompt15 session15", 10),
        ["machine15", "learning15", "model15", "token15", "prompt15", "session15"],
    ),
    (
        ("machine15 learning15 model15 token15 prompt15 session15", 18),
        ["machine15", "learning15 model15", "token15 prompt15", "session15"],
    ),
    (
        ("machine15 learning15 model15 token15 prompt15 session15", 28),
        ["machine15 learning15 model15", "token15 prompt15 session15"],
    ),
    (
        ("learning15 model15 token15 prompt15 session15 library15", 6),
        ["learning15", "model15", "token15", "prompt15", "session15", "library15"],
    ),
    (
        ("learning15 model15 token15 prompt15 session15 library15", 10),
        ["learning15", "model15", "token15", "prompt15", "session15", "library15"],
    ),
    (
        ("learning15 model15 token15 prompt15 session15 library15", 18),
        ["learning15 model15", "token15 prompt15", "session15", "library15"],
    ),
    (
        ("learning15 model15 token15 prompt15 session15 library15", 28),
        ["learning15 model15 token15", "prompt15 session15 library15"],
    ),
    (
        ("model15 token15 prompt15 session15 library15 service15", 6),
        ["model15", "token15", "prompt15", "session15", "library15", "service15"],
    ),
    (
        ("model15 token15 prompt15 session15 library15 service15", 10),
        ["model15", "token15", "prompt15", "session15", "library15", "service15"],
    ),
    (
        ("model15 token15 prompt15 session15 library15 service15", 18),
        ["model15 token15", "prompt15 session15", "library15", "service15"],
    ),
    (
        ("model15 token15 prompt15 session15 library15 service15", 28),
        ["model15 token15 prompt15", "session15 library15", "service15"],
    ),
    (
        ("token15 prompt15 session15 library15 service15 gateway15", 6),
        ["token15", "prompt15", "session15", "library15", "service15", "gateway15"],
    ),
    (
        ("token15 prompt15 session15 library15 service15 gateway15", 10),
        ["token15", "prompt15", "session15", "library15", "service15", "gateway15"],
    ),
    (
        ("token15 prompt15 session15 library15 service15 gateway15", 18),
        ["token15 prompt15", "session15", "library15", "service15", "gateway15"],
    ),
    (
        ("token15 prompt15 session15 library15 service15 gateway15", 28),
        ["token15 prompt15 session15", "library15 service15", "gateway15"],
    ),
    (
        ("prompt15 session15 library15 service15 gateway15 storage15", 6),
        ["prompt15", "session15", "library15", "service15", "gateway15", "storage15"],
    ),
    (
        ("prompt15 session15 library15 service15 gateway15 storage15", 10),
        ["prompt15", "session15", "library15", "service15", "gateway15", "storage15"],
    ),
    (
        ("prompt15 session15 library15 service15 gateway15 storage15", 18),
        ["prompt15 session15", "library15", "service15", "gateway15", "storage15"],
    ),
    (
        ("prompt15 session15 library15 service15 gateway15 storage15", 28),
        ["prompt15 session15 library15", "service15 gateway15", "storage15"],
    ),
    (
        ("session15 library15 service15 gateway15 storage15 network15", 6),
        ["session15", "library15", "service15", "gateway15", "storage15", "network15"],
    ),
    (
        ("session15 library15 service15 gateway15 storage15 network15", 10),
        ["session15", "library15", "service15", "gateway15", "storage15", "network15"],
    ),
    (
        ("session15 library15 service15 gateway15 storage15 network15", 18),
        ["session15", "library15", "service15", "gateway15", "storage15", "network15"],
    ),
    (
        ("session15 library15 service15 gateway15 storage15 network15", 28),
        ["session15 library15", "service15 gateway15", "storage15 network15"],
    ),
    (
        ("library15 service15 gateway15 storage15 network15 latency15", 6),
        ["library15", "service15", "gateway15", "storage15", "network15", "latency15"],
    ),
    (
        ("library15 service15 gateway15 storage15 network15 latency15", 10),
        ["library15", "service15", "gateway15", "storage15", "network15", "latency15"],
    ),
    (
        ("library15 service15 gateway15 storage15 network15 latency15", 18),
        ["library15", "service15", "gateway15", "storage15", "network15", "latency15"],
    ),
    (
        ("library15 service15 gateway15 storage15 network15 latency15", 28),
        ["library15 service15", "gateway15 storage15", "network15 latency15"],
    ),
    (
        ("service15 gateway15 storage15 network15 latency15 buffer15", 6),
        ["service15", "gateway15", "storage15", "network15", "latency15", "buffer15"],
    ),
    (
        ("service15 gateway15 storage15 network15 latency15 buffer15", 10),
        ["service15", "gateway15", "storage15", "network15", "latency15", "buffer15"],
    ),
    (
        ("service15 gateway15 storage15 network15 latency15 buffer15", 18),
        ["service15", "gateway15", "storage15", "network15", "latency15 buffer15"],
    ),
    (
        ("service15 gateway15 storage15 network15 latency15 buffer15", 28),
        ["service15 gateway15", "storage15 network15", "latency15 buffer15"],
    ),
    (
        ("gateway15 storage15 network15 latency15 buffer15 queue15", 6),
        ["gateway15", "storage15", "network15", "latency15", "buffer15", "queue15"],
    ),
    (
        ("gateway15 storage15 network15 latency15 buffer15 queue15", 10),
        ["gateway15", "storage15", "network15", "latency15", "buffer15", "queue15"],
    ),
    (
        ("gateway15 storage15 network15 latency15 buffer15 queue15", 18),
        ["gateway15", "storage15", "network15", "latency15 buffer15", "queue15"],
    ),
    (
        ("gateway15 storage15 network15 latency15 buffer15 queue15", 28),
        ["gateway15 storage15", "network15 latency15 buffer15", "queue15"],
    ),
    (
        ("storage15 network15 latency15 buffer15 queue15 worker15", 6),
        ["storage15", "network15", "latency15", "buffer15", "queue15", "worker15"],
    ),
    (
        ("storage15 network15 latency15 buffer15 queue15 worker15", 10),
        ["storage15", "network15", "latency15", "buffer15", "queue15", "worker15"],
    ),
    (
        ("storage15 network15 latency15 buffer15 queue15 worker15", 18),
        ["storage15", "network15", "latency15 buffer15", "queue15 worker15"],
    ),
    (
        ("storage15 network15 latency15 buffer15 queue15 worker15", 28),
        ["storage15 network15", "latency15 buffer15 queue15", "worker15"],
    ),
    (
        ("network15 latency15 buffer15 queue15 worker15 kernel15", 6),
        ["network15", "latency15", "buffer15", "queue15", "worker15", "kernel15"],
    ),
    (
        ("network15 latency15 buffer15 queue15 worker15 kernel15", 10),
        ["network15", "latency15", "buffer15", "queue15", "worker15", "kernel15"],
    ),
    (
        ("network15 latency15 buffer15 queue15 worker15 kernel15", 18),
        ["network15", "latency15 buffer15", "queue15 worker15", "kernel15"],
    ),
    (
        ("network15 latency15 buffer15 queue15 worker15 kernel15", 28),
        ["network15 latency15 buffer15", "queue15 worker15 kernel15"],
    ),
    (
        ("latency15 buffer15 queue15 worker15 kernel15 signal15", 6),
        ["latency15", "buffer15", "queue15", "worker15", "kernel15", "signal15"],
    ),
    (
        ("latency15 buffer15 queue15 worker15 kernel15 signal15", 10),
        ["latency15", "buffer15", "queue15", "worker15", "kernel15", "signal15"],
    ),
    (
        ("latency15 buffer15 queue15 worker15 kernel15 signal15", 18),
        ["latency15 buffer15", "queue15 worker15", "kernel15 signal15"],
    ),
    (
        ("latency15 buffer15 queue15 worker15 kernel15 signal15", 28),
        ["latency15 buffer15 queue15", "worker15 kernel15 signal15"],
    ),
    (
        ("buffer15 queue15 worker15 kernel15 signal15 packet15", 6),
        ["buffer15", "queue15", "worker15", "kernel15", "signal15", "packet15"],
    ),
    (
        ("buffer15 queue15 worker15 kernel15 signal15 packet15", 10),
        ["buffer15", "queue15", "worker15", "kernel15", "signal15", "packet15"],
    ),
    (
        ("buffer15 queue15 worker15 kernel15 signal15 packet15", 18),
        ["buffer15 queue15", "worker15 kernel15", "signal15 packet15"],
    ),
    (
        ("buffer15 queue15 worker15 kernel15 signal15 packet15", 28),
        ["buffer15 queue15 worker15", "kernel15 signal15 packet15"],
    ),
    (
        ("queue15 worker15 kernel15 signal15 packet15 router15", 6),
        ["queue15", "worker15", "kernel15", "signal15", "packet15", "router15"],
    ),
    (
        ("queue15 worker15 kernel15 signal15 packet15 router15", 10),
        ["queue15", "worker15", "kernel15", "signal15", "packet15", "router15"],
    ),
    (
        ("queue15 worker15 kernel15 signal15 packet15 router15", 18),
        ["queue15 worker15", "kernel15 signal15", "packet15 router15"],
    ),
    (
        ("queue15 worker15 kernel15 signal15 packet15 router15", 28),
        ["queue15 worker15 kernel15", "signal15 packet15 router15"],
    ),
    (
        ("worker15 kernel15 signal15 packet15 router15 cluster15", 6),
        ["worker15", "kernel15", "signal15", "packet15", "router15", "cluster15"],
    ),
    (
        ("worker15 kernel15 signal15 packet15 router15 cluster15", 10),
        ["worker15", "kernel15", "signal15", "packet15", "router15", "cluster15"],
    ),
    (
        ("worker15 kernel15 signal15 packet15 router15 cluster15", 18),
        ["worker15 kernel15", "signal15 packet15", "router15 cluster15"],
    ),
    (
        ("worker15 kernel15 signal15 packet15 router15 cluster15", 28),
        ["worker15 kernel15 signal15", "packet15 router15 cluster15"],
    ),
    (
        ("kernel15 signal15 packet15 router15 cluster15 mirror15", 6),
        ["kernel15", "signal15", "packet15", "router15", "cluster15", "mirror15"],
    ),
    (
        ("kernel15 signal15 packet15 router15 cluster15 mirror15", 10),
        ["kernel15", "signal15", "packet15", "router15", "cluster15", "mirror15"],
    ),
    (
        ("kernel15 signal15 packet15 router15 cluster15 mirror15", 18),
        ["kernel15 signal15", "packet15 router15", "cluster15 mirror15"],
    ),
    (
        ("kernel15 signal15 packet15 router15 cluster15 mirror15", 28),
        ["kernel15 signal15 packet15", "router15 cluster15 mirror15"],
    ),
    (
        ("signal15 packet15 router15 cluster15 mirror15 filter15", 6),
        ["signal15", "packet15", "router15", "cluster15", "mirror15", "filter15"],
    ),
    (
        ("signal15 packet15 router15 cluster15 mirror15 filter15", 10),
        ["signal15", "packet15", "router15", "cluster15", "mirror15", "filter15"],
    ),
    (
        ("signal15 packet15 router15 cluster15 mirror15 filter15", 18),
        ["signal15 packet15", "router15 cluster15", "mirror15 filter15"],
    ),
    (
        ("signal15 packet15 router15 cluster15 mirror15 filter15", 28),
        ["signal15 packet15 router15", "cluster15 mirror15 filter15"],
    ),
    (
        ("packet15 router15 cluster15 mirror15 filter15 ranking15", 6),
        ["packet15", "router15", "cluster15", "mirror15", "filter15", "ranking15"],
    ),
    (
        ("packet15 router15 cluster15 mirror15 filter15 ranking15", 10),
        ["packet15", "router15", "cluster15", "mirror15", "filter15", "ranking15"],
    ),
    (
        ("packet15 router15 cluster15 mirror15 filter15 ranking15", 18),
        ["packet15 router15", "cluster15 mirror15", "filter15 ranking15"],
    ),
    (
        ("packet15 router15 cluster15 mirror15 filter15 ranking15", 28),
        ["packet15 router15 cluster15", "mirror15 filter15 ranking15"],
    ),
    (
        ("router15 cluster15 mirror15 filter15 ranking15 encoding15", 6),
        ["router15", "cluster15", "mirror15", "filter15", "ranking15", "encoding15"],
    ),
    (
        ("router15 cluster15 mirror15 filter15 ranking15 encoding15", 10),
        ["router15", "cluster15", "mirror15", "filter15", "ranking15", "encoding15"],
    ),
    (
        ("router15 cluster15 mirror15 filter15 ranking15 encoding15", 18),
        ["router15 cluster15", "mirror15 filter15", "ranking15", "encoding15"],
    ),
    (
        ("router15 cluster15 mirror15 filter15 ranking15 encoding15", 28),
        ["router15 cluster15 mirror15", "filter15 ranking15", "encoding15"],
    ),
    (
        ("cluster15 mirror15 filter15 ranking15 encoding15 mapping15", 6),
        ["cluster15", "mirror15", "filter15", "ranking15", "encoding15", "mapping15"],
    ),
    (
        ("cluster15 mirror15 filter15 ranking15 encoding15 mapping15", 10),
        ["cluster15", "mirror15", "filter15", "ranking15", "encoding15", "mapping15"],
    ),
    (
        ("cluster15 mirror15 filter15 ranking15 encoding15 mapping15", 18),
        ["cluster15 mirror15", "filter15 ranking15", "encoding15", "mapping15"],
    ),
    (
        ("cluster15 mirror15 filter15 ranking15 encoding15 mapping15", 28),
        ["cluster15 mirror15 filter15", "ranking15 encoding15", "mapping15"],
    ),
    (
        ("mirror15 filter15 ranking15 encoding15 mapping15 record15", 6),
        ["mirror15", "filter15", "ranking15", "encoding15", "mapping15", "record15"],
    ),
    (
        ("mirror15 filter15 ranking15 encoding15 mapping15 record15", 10),
        ["mirror15", "filter15", "ranking15", "encoding15", "mapping15", "record15"],
    ),
    (
        ("mirror15 filter15 ranking15 encoding15 mapping15 record15", 18),
        ["mirror15 filter15", "ranking15", "encoding15", "mapping15 record15"],
    ),
    (
        ("mirror15 filter15 ranking15 encoding15 mapping15 record15", 28),
        ["mirror15 filter15 ranking15", "encoding15 mapping15", "record15"],
    ),
    (
        ("filter15 ranking15 encoding15 mapping15 record15 candle15", 6),
        ["filter15", "ranking15", "encoding15", "mapping15", "record15", "candle15"],
    ),
    (
        ("filter15 ranking15 encoding15 mapping15 record15 candle15", 10),
        ["filter15", "ranking15", "encoding15", "mapping15", "record15", "candle15"],
    ),
    (
        ("filter15 ranking15 encoding15 mapping15 record15 candle15", 18),
        ["filter15 ranking15", "encoding15", "mapping15 record15", "candle15"],
    ),
    (
        ("filter15 ranking15 encoding15 mapping15 record15 candle15", 28),
        ["filter15 ranking15", "encoding15 mapping15", "record15 candle15"],
    ),
    (
        ("ranking15 encoding15 mapping15 record15 candle15 thread15", 6),
        ["ranking15", "encoding15", "mapping15", "record15", "candle15", "thread15"],
    ),
    (
        ("ranking15 encoding15 mapping15 record15 candle15 thread15", 10),
        ["ranking15", "encoding15", "mapping15", "record15", "candle15", "thread15"],
    ),
    (
        ("ranking15 encoding15 mapping15 record15 candle15 thread15", 18),
        ["ranking15", "encoding15", "mapping15 record15", "candle15 thread15"],
    ),
    (
        ("ranking15 encoding15 mapping15 record15 candle15 thread15", 28),
        ["ranking15 encoding15", "mapping15 record15 candle15", "thread15"],
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
