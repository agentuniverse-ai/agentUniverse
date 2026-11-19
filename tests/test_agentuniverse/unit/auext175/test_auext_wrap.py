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
        ("round 175: the quick brown fox jumps over the lazy dog", 4),
        ["round", "175:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", 8),
        ["round", "175: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", 12),
        ["round 175:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", 16),
        ["round 175: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", 24),
        ["round 175: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 175: the quick brown fox jumps over the lazy dog", 32),
        ["round 175: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", 4),
        ["round", "175:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", 8),
        ["round", "175:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", 12),
        ["round 175:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", 16),
        ["round 175:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", 24),
        ["round 175: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 175: agentuniverse is a framework for multi agents", 32),
        ["round 175: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", 4),
        ["round", "175:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", 8),
        ["round", "175:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", 12),
        ["round 175:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", 16),
        ["round 175:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", 24),
        ["round 175: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 175: knowledge stored as vectors enables retrieval", 32),
        ["round 175: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 175: the processor reads the record then stops", 4),
        ["round", "175:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 175: the processor reads the record then stops", 8),
        ["round", "175: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 175: the processor reads the record then stops", 12),
        ["round 175:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 175: the processor reads the record then stops", 16),
        ["round 175: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 175: the processor reads the record then stops", 24),
        ["round 175: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 175: the processor reads the record then stops", 32),
        ["round 175: the processor reads", "the record then stops"],
    ),
    (
        ("round 175: a worker pulls the next task from the queue", 4),
        ["round", "175:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 175: a worker pulls the next task from the queue", 8),
        ["round", "175: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 175: a worker pulls the next task from the queue", 12),
        ["round 175: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 175: a worker pulls the next task from the queue", 16),
        ["round 175: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 175: a worker pulls the next task from the queue", 24),
        ["round 175: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 175: a worker pulls the next task from the queue", 32),
        ["round 175: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 175: signals travel through the network layer", 4),
        ["round", "175:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 175: signals travel through the network layer", 8),
        ["round", "175:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 175: signals travel through the network layer", 12),
        ["round 175:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 175: signals travel through the network layer", 16),
        ["round 175:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 175: signals travel through the network layer", 24),
        ["round 175: signals", "travel through the", "network layer"],
    ),
    (
        ("round 175: signals travel through the network layer", 32),
        ["round 175: signals travel", "through the network layer"],
    ),
    (
        ("round 175: the gateway routes each request by policy", 4),
        ["round", "175:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 175: the gateway routes each request by policy", 8),
        ["round", "175: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 175: the gateway routes each request by policy", 12),
        ["round 175:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 175: the gateway routes each request by policy", 16),
        ["round 175: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 175: the gateway routes each request by policy", 24),
        ["round 175: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 175: the gateway routes each request by policy", 32),
        ["round 175: the gateway routes", "each request by policy"],
    ),
    (
        ("round 175: memory grows until the buffer is full", 4),
        ["round", "175:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 175: memory grows until the buffer is full", 8),
        ["round", "175:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 175: memory grows until the buffer is full", 12),
        ["round 175:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 175: memory grows until the buffer is full", 16),
        ["round 175:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 175: memory grows until the buffer is full", 24), ["round 175: memory grows", "until the buffer is full"]),
    (("round 175: memory grows until the buffer is full", 32), ["round 175: memory grows until", "the buffer is full"]),
    (
        ("round 175: the cluster mirrors every packet twice", 4),
        ["round", "175:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 175: the cluster mirrors every packet twice", 8),
        ["round", "175: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 175: the cluster mirrors every packet twice", 12),
        ["round 175:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 175: the cluster mirrors every packet twice", 16),
        ["round 175: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 175: the cluster mirrors every packet twice", 24),
        ["round 175: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 175: the cluster mirrors every packet twice", 32),
        ["round 175: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", 4),
        ["round", "175:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", 8),
        ["round", "175:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", 12),
        ["round 175:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", 16),
        ["round 175:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", 24),
        ["round 175: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 175: ranking uses tokens learned from the corpus", 32),
        ["round 175: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 175: a long session ends when the candle dies", 4),
        ["round", "175:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 175: a long session ends when the candle dies", 8),
        ["round", "175: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 175: a long session ends when the candle dies", 12),
        ["round 175: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 175: a long session ends when the candle dies", 16),
        ["round 175: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 175: a long session ends when the candle dies", 24),
        ["round 175: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 175: a long session ends when the candle dies", 32),
        ["round 175: a long session ends", "when the candle dies"],
    ),
    (
        ("round 175: encode the prompt then map the result", 4),
        ["round", "175:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 175: encode the prompt then map the result", 8),
        ["round", "175:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 175: encode the prompt then map the result", 12),
        ["round 175:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 175: encode the prompt then map the result", 16),
        ["round 175:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 175: encode the prompt then map the result", 24),
        ["round 175: encode the", "prompt then map the", "result"],
    ),
    (("round 175: encode the prompt then map the result", 32), ["round 175: encode the prompt", "then map the result"]),
    (
        ("round 175: the kernel wakes the worker at dawn", 4),
        ["round", "175:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 175: the kernel wakes the worker at dawn", 8),
        ["round", "175: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 175: the kernel wakes the worker at dawn", 12),
        ["round 175:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 175: the kernel wakes the worker at dawn", 16), ["round 175: the", "kernel wakes the", "worker at dawn"]),
    (("round 175: the kernel wakes the worker at dawn", 24), ["round 175: the kernel", "wakes the worker at dawn"]),
    (("round 175: the kernel wakes the worker at dawn", 32), ["round 175: the kernel wakes the", "worker at dawn"]),
    (
        ("round 175: service latency drops after the patch", 4),
        ["round", "175:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 175: service latency drops after the patch", 8),
        ["round", "175:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 175: service latency drops after the patch", 12),
        ["round 175:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 175: service latency drops after the patch", 16),
        ["round 175:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 175: service latency drops after the patch", 24),
        ["round 175: service", "latency drops after the", "patch"],
    ),
    (("round 175: service latency drops after the patch", 32), ["round 175: service latency drops", "after the patch"]),
    (
        ("round 175: the library caches every vector it sees", 4),
        ["round", "175:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 175: the library caches every vector it sees", 8),
        ["round", "175: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 175: the library caches every vector it sees", 12),
        ["round 175:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 175: the library caches every vector it sees", 16),
        ["round 175: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 175: the library caches every vector it sees", 24),
        ["round 175: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 175: the library caches every vector it sees", 32),
        ["round 175: the library caches", "every vector it sees"],
    ),
    (
        ("round 175: agents argue then the debate resolves", 4),
        ["round", "175:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 175: agents argue then the debate resolves", 8),
        ["round", "175:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 175: agents argue then the debate resolves", 12),
        ["round 175:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 175: agents argue then the debate resolves", 16),
        ["round 175:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 175: agents argue then the debate resolves", 24), ["round 175: agents argue", "then the debate resolves"]),
    (("round 175: agents argue then the debate resolves", 32), ["round 175: agents argue then the", "debate resolves"]),
    (
        ("round 175: the filter keeps only strong matches", 4),
        ["round", "175:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 175: the filter keeps only strong matches", 8),
        ["round", "175: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 175: the filter keeps only strong matches", 12),
        ["round 175:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 175: the filter keeps only strong matches", 16),
        ["round 175: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 175: the filter keeps only strong matches", 24),
        ["round 175: the filter", "keeps only strong", "matches"],
    ),
    (("round 175: the filter keeps only strong matches", 32), ["round 175: the filter keeps only", "strong matches"]),
    (
        ("round 175: the model answers with a short reply", 4),
        ["round", "175:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 175: the model answers with a short reply", 8),
        ["round", "175: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 175: the model answers with a short reply", 12),
        ["round 175:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 175: the model answers with a short reply", 16),
        ["round 175: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 175: the model answers with a short reply", 24),
        ["round 175: the model", "answers with a short", "reply"],
    ),
    (("round 175: the model answers with a short reply", 32), ["round 175: the model answers", "with a short reply"]),
    (
        ("round 175: the recorder stores the reasoning trace", 4),
        ["round", "175:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 175: the recorder stores the reasoning trace", 8),
        ["round", "175: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 175: the recorder stores the reasoning trace", 12),
        ["round 175:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 175: the recorder stores the reasoning trace", 16),
        ["round 175: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 175: the recorder stores the reasoning trace", 24),
        ["round 175: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 175: the recorder stores the reasoning trace", 32),
        ["round 175: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 175: the angel watches the processor run", 4),
        ["round", "175:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 175: the angel watches the processor run", 8),
        ["round", "175: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 175: the angel watches the processor run", 12),
        ["round 175:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 175: the angel watches the processor run", 16),
        ["round 175: the", "angel watches", "the processor", "run"],
    ),
    (("round 175: the angel watches the processor run", 24), ["round 175: the angel", "watches the processor", "run"]),
    (("round 175: the angel watches the processor run", 32), ["round 175: the angel watches the", "processor run"]),
    (
        ("round 175: angle of the vector decides the match", 4),
        ["round", "175:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 175: angle of the vector decides the match", 8),
        ["round", "175:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 175: angle of the vector decides the match", 12),
        ["round 175:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 175: angle of the vector decides the match", 16),
        ["round 175: angle", "of the vector", "decides the", "match"],
    ),
    (("round 175: angle of the vector decides the match", 24), ["round 175: angle of the", "vector decides the match"]),
    (("round 175: angle of the vector decides the match", 32), ["round 175: angle of the vector", "decides the match"]),
    (
        ("round 175: the candle burns twice as long at night", 4),
        ["round", "175:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 175: the candle burns twice as long at night", 8),
        ["round", "175: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 175: the candle burns twice as long at night", 12),
        ["round 175:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 175: the candle burns twice as long at night", 16),
        ["round 175: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 175: the candle burns twice as long at night", 24),
        ["round 175: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 175: the candle burns twice as long at night", 32),
        ["round 175: the candle burns", "twice as long at night"],
    ),
    (
        ("round 175: a mirror of the universe in one line", 4),
        ["round", "175:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 175: a mirror of the universe in one line", 8),
        ["round", "175: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 175: a mirror of the universe in one line", 12),
        ["round 175: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 175: a mirror of the universe in one line", 16),
        ["round 175: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 175: a mirror of the universe in one line", 24), ["round 175: a mirror of", "the universe in one line"]),
    (("round 175: a mirror of the universe in one line", 32), ["round 175: a mirror of the", "universe in one line"]),
    (
        ("round 175: the queue drains before the storm", 4),
        ["round", "175:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 175: the queue drains before the storm", 8),
        ["round", "175: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 175: the queue drains before the storm", 12),
        ["round 175:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 175: the queue drains before the storm", 16), ["round 175: the", "queue drains", "before the storm"]),
    (("round 175: the queue drains before the storm", 24), ["round 175: the queue", "drains before the storm"]),
    (("round 175: the queue drains before the storm", 32), ["round 175: the queue drains", "before the storm"]),
    (
        ("kitten175 sitting175 agent175 angle175 universe175 memory175", 6),
        ["kitten175", "sitting175", "agent175", "angle175", "universe175", "memory175"],
    ),
    (
        ("kitten175 sitting175 agent175 angle175 universe175 memory175", 10),
        ["kitten175", "sitting175", "agent175", "angle175", "universe175", "memory175"],
    ),
    (
        ("kitten175 sitting175 agent175 angle175 universe175 memory175", 18),
        ["kitten175", "sitting175", "agent175 angle175", "universe175", "memory175"],
    ),
    (
        ("kitten175 sitting175 agent175 angle175 universe175 memory175", 28),
        ["kitten175 sitting175", "agent175 angle175", "universe175 memory175"],
    ),
    (
        ("sitting175 agent175 angle175 universe175 memory175 stream175", 6),
        ["sitting175", "agent175", "angle175", "universe175", "memory175", "stream175"],
    ),
    (
        ("sitting175 agent175 angle175 universe175 memory175 stream175", 10),
        ["sitting175", "agent175", "angle175", "universe175", "memory175", "stream175"],
    ),
    (
        ("sitting175 agent175 angle175 universe175 memory175 stream175", 18),
        ["sitting175", "agent175 angle175", "universe175", "memory175", "stream175"],
    ),
    (
        ("sitting175 agent175 angle175 universe175 memory175 stream175", 28),
        ["sitting175 agent175 angle175", "universe175 memory175", "stream175"],
    ),
    (
        ("agent175 angle175 universe175 memory175 stream175 context175", 6),
        ["agent175", "angle175", "universe175", "memory175", "stream175", "context175"],
    ),
    (
        ("agent175 angle175 universe175 memory175 stream175 context175", 10),
        ["agent175", "angle175", "universe175", "memory175", "stream175", "context175"],
    ),
    (
        ("agent175 angle175 universe175 memory175 stream175 context175", 18),
        ["agent175 angle175", "universe175", "memory175", "stream175", "context175"],
    ),
    (
        ("agent175 angle175 universe175 memory175 stream175 context175", 28),
        ["agent175 angle175", "universe175 memory175", "stream175 context175"],
    ),
    (
        ("angle175 universe175 memory175 stream175 context175 knowledge175", 6),
        ["angle175", "universe175", "memory175", "stream175", "context175", "knowledge175"],
    ),
    (
        ("angle175 universe175 memory175 stream175 context175 knowledge175", 10),
        ["angle175", "universe175", "memory175", "stream175", "context175", "knowledge175"],
    ),
    (
        ("angle175 universe175 memory175 stream175 context175 knowledge175", 18),
        ["angle175", "universe175", "memory175", "stream175", "context175", "knowledge175"],
    ),
    (
        ("angle175 universe175 memory175 stream175 context175 knowledge175", 28),
        ["angle175 universe175", "memory175 stream175", "context175 knowledge175"],
    ),
    (
        ("universe175 memory175 stream175 context175 knowledge175 vector175", 6),
        ["universe175", "memory175", "stream175", "context175", "knowledge175", "vector175"],
    ),
    (
        ("universe175 memory175 stream175 context175 knowledge175 vector175", 10),
        ["universe175", "memory175", "stream175", "context175", "knowledge175", "vector175"],
    ),
    (
        ("universe175 memory175 stream175 context175 knowledge175 vector175", 18),
        ["universe175", "memory175", "stream175", "context175", "knowledge175", "vector175"],
    ),
    (
        ("universe175 memory175 stream175 context175 knowledge175 vector175", 28),
        ["universe175 memory175", "stream175 context175", "knowledge175 vector175"],
    ),
    (
        ("memory175 stream175 context175 knowledge175 vector175 processor175", 6),
        ["memory175", "stream175", "context175", "knowledge175", "vector175", "processor175"],
    ),
    (
        ("memory175 stream175 context175 knowledge175 vector175 processor175", 10),
        ["memory175", "stream175", "context175", "knowledge175", "vector175", "processor175"],
    ),
    (
        ("memory175 stream175 context175 knowledge175 vector175 processor175", 18),
        ["memory175", "stream175", "context175", "knowledge175", "vector175", "processor175"],
    ),
    (
        ("memory175 stream175 context175 knowledge175 vector175 processor175", 28),
        ["memory175 stream175", "context175 knowledge175", "vector175 processor175"],
    ),
    (
        ("stream175 context175 knowledge175 vector175 processor175 reasoning175", 6),
        ["stream175", "context175", "knowledge175", "vector175", "processor175", "reasoning175"],
    ),
    (
        ("stream175 context175 knowledge175 vector175 processor175 reasoning175", 10),
        ["stream175", "context175", "knowledge175", "vector175", "processor175", "reasoning175"],
    ),
    (
        ("stream175 context175 knowledge175 vector175 processor175 reasoning175", 18),
        ["stream175", "context175", "knowledge175", "vector175", "processor175", "reasoning175"],
    ),
    (
        ("stream175 context175 knowledge175 vector175 processor175 reasoning175", 28),
        ["stream175 context175", "knowledge175 vector175", "processor175 reasoning175"],
    ),
    (
        ("context175 knowledge175 vector175 processor175 reasoning175 machine175", 6),
        ["context175", "knowledge175", "vector175", "processor175", "reasoning175", "machine175"],
    ),
    (
        ("context175 knowledge175 vector175 processor175 reasoning175 machine175", 10),
        ["context175", "knowledge175", "vector175", "processor175", "reasoning175", "machine175"],
    ),
    (
        ("context175 knowledge175 vector175 processor175 reasoning175 machine175", 18),
        ["context175", "knowledge175", "vector175", "processor175", "reasoning175", "machine175"],
    ),
    (
        ("context175 knowledge175 vector175 processor175 reasoning175 machine175", 28),
        ["context175 knowledge175", "vector175 processor175", "reasoning175 machine175"],
    ),
    (
        ("knowledge175 vector175 processor175 reasoning175 machine175 learning175", 6),
        ["knowledge175", "vector175", "processor175", "reasoning175", "machine175", "learning175"],
    ),
    (
        ("knowledge175 vector175 processor175 reasoning175 machine175 learning175", 10),
        ["knowledge175", "vector175", "processor175", "reasoning175", "machine175", "learning175"],
    ),
    (
        ("knowledge175 vector175 processor175 reasoning175 machine175 learning175", 18),
        ["knowledge175", "vector175", "processor175", "reasoning175", "machine175", "learning175"],
    ),
    (
        ("knowledge175 vector175 processor175 reasoning175 machine175 learning175", 28),
        ["knowledge175 vector175", "processor175 reasoning175", "machine175 learning175"],
    ),
    (
        ("vector175 processor175 reasoning175 machine175 learning175 model175", 6),
        ["vector175", "processor175", "reasoning175", "machine175", "learning175", "model175"],
    ),
    (
        ("vector175 processor175 reasoning175 machine175 learning175 model175", 10),
        ["vector175", "processor175", "reasoning175", "machine175", "learning175", "model175"],
    ),
    (
        ("vector175 processor175 reasoning175 machine175 learning175 model175", 18),
        ["vector175", "processor175", "reasoning175", "machine175", "learning175", "model175"],
    ),
    (
        ("vector175 processor175 reasoning175 machine175 learning175 model175", 28),
        ["vector175 processor175", "reasoning175 machine175", "learning175 model175"],
    ),
    (
        ("processor175 reasoning175 machine175 learning175 model175 token175", 6),
        ["processor175", "reasoning175", "machine175", "learning175", "model175", "token175"],
    ),
    (
        ("processor175 reasoning175 machine175 learning175 model175 token175", 10),
        ["processor175", "reasoning175", "machine175", "learning175", "model175", "token175"],
    ),
    (
        ("processor175 reasoning175 machine175 learning175 model175 token175", 18),
        ["processor175", "reasoning175", "machine175", "learning175", "model175 token175"],
    ),
    (
        ("processor175 reasoning175 machine175 learning175 model175 token175", 28),
        ["processor175 reasoning175", "machine175 learning175", "model175 token175"],
    ),
    (
        ("reasoning175 machine175 learning175 model175 token175 prompt175", 6),
        ["reasoning175", "machine175", "learning175", "model175", "token175", "prompt175"],
    ),
    (
        ("reasoning175 machine175 learning175 model175 token175 prompt175", 10),
        ["reasoning175", "machine175", "learning175", "model175", "token175", "prompt175"],
    ),
    (
        ("reasoning175 machine175 learning175 model175 token175 prompt175", 18),
        ["reasoning175", "machine175", "learning175", "model175 token175", "prompt175"],
    ),
    (
        ("reasoning175 machine175 learning175 model175 token175 prompt175", 28),
        ["reasoning175 machine175", "learning175 model175", "token175 prompt175"],
    ),
    (
        ("machine175 learning175 model175 token175 prompt175 session175", 6),
        ["machine175", "learning175", "model175", "token175", "prompt175", "session175"],
    ),
    (
        ("machine175 learning175 model175 token175 prompt175 session175", 10),
        ["machine175", "learning175", "model175", "token175", "prompt175", "session175"],
    ),
    (
        ("machine175 learning175 model175 token175 prompt175 session175", 18),
        ["machine175", "learning175", "model175 token175", "prompt175", "session175"],
    ),
    (
        ("machine175 learning175 model175 token175 prompt175 session175", 28),
        ["machine175 learning175", "model175 token175 prompt175", "session175"],
    ),
    (
        ("learning175 model175 token175 prompt175 session175 library175", 6),
        ["learning175", "model175", "token175", "prompt175", "session175", "library175"],
    ),
    (
        ("learning175 model175 token175 prompt175 session175 library175", 10),
        ["learning175", "model175", "token175", "prompt175", "session175", "library175"],
    ),
    (
        ("learning175 model175 token175 prompt175 session175 library175", 18),
        ["learning175", "model175 token175", "prompt175", "session175", "library175"],
    ),
    (
        ("learning175 model175 token175 prompt175 session175 library175", 28),
        ["learning175 model175", "token175 prompt175", "session175 library175"],
    ),
    (
        ("model175 token175 prompt175 session175 library175 service175", 6),
        ["model175", "token175", "prompt175", "session175", "library175", "service175"],
    ),
    (
        ("model175 token175 prompt175 session175 library175 service175", 10),
        ["model175", "token175", "prompt175", "session175", "library175", "service175"],
    ),
    (
        ("model175 token175 prompt175 session175 library175 service175", 18),
        ["model175 token175", "prompt175", "session175", "library175", "service175"],
    ),
    (
        ("model175 token175 prompt175 session175 library175 service175", 28),
        ["model175 token175 prompt175", "session175 library175", "service175"],
    ),
    (
        ("token175 prompt175 session175 library175 service175 gateway175", 6),
        ["token175", "prompt175", "session175", "library175", "service175", "gateway175"],
    ),
    (
        ("token175 prompt175 session175 library175 service175 gateway175", 10),
        ["token175", "prompt175", "session175", "library175", "service175", "gateway175"],
    ),
    (
        ("token175 prompt175 session175 library175 service175 gateway175", 18),
        ["token175 prompt175", "session175", "library175", "service175", "gateway175"],
    ),
    (
        ("token175 prompt175 session175 library175 service175 gateway175", 28),
        ["token175 prompt175", "session175 library175", "service175 gateway175"],
    ),
    (
        ("prompt175 session175 library175 service175 gateway175 storage175", 6),
        ["prompt175", "session175", "library175", "service175", "gateway175", "storage175"],
    ),
    (
        ("prompt175 session175 library175 service175 gateway175 storage175", 10),
        ["prompt175", "session175", "library175", "service175", "gateway175", "storage175"],
    ),
    (
        ("prompt175 session175 library175 service175 gateway175 storage175", 18),
        ["prompt175", "session175", "library175", "service175", "gateway175", "storage175"],
    ),
    (
        ("prompt175 session175 library175 service175 gateway175 storage175", 28),
        ["prompt175 session175", "library175 service175", "gateway175 storage175"],
    ),
    (
        ("session175 library175 service175 gateway175 storage175 network175", 6),
        ["session175", "library175", "service175", "gateway175", "storage175", "network175"],
    ),
    (
        ("session175 library175 service175 gateway175 storage175 network175", 10),
        ["session175", "library175", "service175", "gateway175", "storage175", "network175"],
    ),
    (
        ("session175 library175 service175 gateway175 storage175 network175", 18),
        ["session175", "library175", "service175", "gateway175", "storage175", "network175"],
    ),
    (
        ("session175 library175 service175 gateway175 storage175 network175", 28),
        ["session175 library175", "service175 gateway175", "storage175 network175"],
    ),
    (
        ("library175 service175 gateway175 storage175 network175 latency175", 6),
        ["library175", "service175", "gateway175", "storage175", "network175", "latency175"],
    ),
    (
        ("library175 service175 gateway175 storage175 network175 latency175", 10),
        ["library175", "service175", "gateway175", "storage175", "network175", "latency175"],
    ),
    (
        ("library175 service175 gateway175 storage175 network175 latency175", 18),
        ["library175", "service175", "gateway175", "storage175", "network175", "latency175"],
    ),
    (
        ("library175 service175 gateway175 storage175 network175 latency175", 28),
        ["library175 service175", "gateway175 storage175", "network175 latency175"],
    ),
    (
        ("service175 gateway175 storage175 network175 latency175 buffer175", 6),
        ["service175", "gateway175", "storage175", "network175", "latency175", "buffer175"],
    ),
    (
        ("service175 gateway175 storage175 network175 latency175 buffer175", 10),
        ["service175", "gateway175", "storage175", "network175", "latency175", "buffer175"],
    ),
    (
        ("service175 gateway175 storage175 network175 latency175 buffer175", 18),
        ["service175", "gateway175", "storage175", "network175", "latency175", "buffer175"],
    ),
    (
        ("service175 gateway175 storage175 network175 latency175 buffer175", 28),
        ["service175 gateway175", "storage175 network175", "latency175 buffer175"],
    ),
    (
        ("gateway175 storage175 network175 latency175 buffer175 queue175", 6),
        ["gateway175", "storage175", "network175", "latency175", "buffer175", "queue175"],
    ),
    (
        ("gateway175 storage175 network175 latency175 buffer175 queue175", 10),
        ["gateway175", "storage175", "network175", "latency175", "buffer175", "queue175"],
    ),
    (
        ("gateway175 storage175 network175 latency175 buffer175 queue175", 18),
        ["gateway175", "storage175", "network175", "latency175", "buffer175 queue175"],
    ),
    (
        ("gateway175 storage175 network175 latency175 buffer175 queue175", 28),
        ["gateway175 storage175", "network175 latency175", "buffer175 queue175"],
    ),
    (
        ("storage175 network175 latency175 buffer175 queue175 worker175", 6),
        ["storage175", "network175", "latency175", "buffer175", "queue175", "worker175"],
    ),
    (
        ("storage175 network175 latency175 buffer175 queue175 worker175", 10),
        ["storage175", "network175", "latency175", "buffer175", "queue175", "worker175"],
    ),
    (
        ("storage175 network175 latency175 buffer175 queue175 worker175", 18),
        ["storage175", "network175", "latency175", "buffer175 queue175", "worker175"],
    ),
    (
        ("storage175 network175 latency175 buffer175 queue175 worker175", 28),
        ["storage175 network175", "latency175 buffer175", "queue175 worker175"],
    ),
    (
        ("network175 latency175 buffer175 queue175 worker175 kernel175", 6),
        ["network175", "latency175", "buffer175", "queue175", "worker175", "kernel175"],
    ),
    (
        ("network175 latency175 buffer175 queue175 worker175 kernel175", 10),
        ["network175", "latency175", "buffer175", "queue175", "worker175", "kernel175"],
    ),
    (
        ("network175 latency175 buffer175 queue175 worker175 kernel175", 18),
        ["network175", "latency175", "buffer175 queue175", "worker175", "kernel175"],
    ),
    (
        ("network175 latency175 buffer175 queue175 worker175 kernel175", 28),
        ["network175 latency175", "buffer175 queue175 worker175", "kernel175"],
    ),
    (
        ("latency175 buffer175 queue175 worker175 kernel175 signal175", 6),
        ["latency175", "buffer175", "queue175", "worker175", "kernel175", "signal175"],
    ),
    (
        ("latency175 buffer175 queue175 worker175 kernel175 signal175", 10),
        ["latency175", "buffer175", "queue175", "worker175", "kernel175", "signal175"],
    ),
    (
        ("latency175 buffer175 queue175 worker175 kernel175 signal175", 18),
        ["latency175", "buffer175 queue175", "worker175", "kernel175", "signal175"],
    ),
    (
        ("latency175 buffer175 queue175 worker175 kernel175 signal175", 28),
        ["latency175 buffer175", "queue175 worker175 kernel175", "signal175"],
    ),
    (
        ("buffer175 queue175 worker175 kernel175 signal175 packet175", 6),
        ["buffer175", "queue175", "worker175", "kernel175", "signal175", "packet175"],
    ),
    (
        ("buffer175 queue175 worker175 kernel175 signal175 packet175", 10),
        ["buffer175", "queue175", "worker175", "kernel175", "signal175", "packet175"],
    ),
    (
        ("buffer175 queue175 worker175 kernel175 signal175 packet175", 18),
        ["buffer175 queue175", "worker175", "kernel175", "signal175", "packet175"],
    ),
    (
        ("buffer175 queue175 worker175 kernel175 signal175 packet175", 28),
        ["buffer175 queue175 worker175", "kernel175 signal175", "packet175"],
    ),
    (
        ("queue175 worker175 kernel175 signal175 packet175 router175", 6),
        ["queue175", "worker175", "kernel175", "signal175", "packet175", "router175"],
    ),
    (
        ("queue175 worker175 kernel175 signal175 packet175 router175", 10),
        ["queue175", "worker175", "kernel175", "signal175", "packet175", "router175"],
    ),
    (
        ("queue175 worker175 kernel175 signal175 packet175 router175", 18),
        ["queue175 worker175", "kernel175", "signal175", "packet175", "router175"],
    ),
    (
        ("queue175 worker175 kernel175 signal175 packet175 router175", 28),
        ["queue175 worker175 kernel175", "signal175 packet175", "router175"],
    ),
    (
        ("worker175 kernel175 signal175 packet175 router175 cluster175", 6),
        ["worker175", "kernel175", "signal175", "packet175", "router175", "cluster175"],
    ),
    (
        ("worker175 kernel175 signal175 packet175 router175 cluster175", 10),
        ["worker175", "kernel175", "signal175", "packet175", "router175", "cluster175"],
    ),
    (
        ("worker175 kernel175 signal175 packet175 router175 cluster175", 18),
        ["worker175", "kernel175", "signal175", "packet175", "router175", "cluster175"],
    ),
    (
        ("worker175 kernel175 signal175 packet175 router175 cluster175", 28),
        ["worker175 kernel175", "signal175 packet175", "router175 cluster175"],
    ),
    (
        ("kernel175 signal175 packet175 router175 cluster175 mirror175", 6),
        ["kernel175", "signal175", "packet175", "router175", "cluster175", "mirror175"],
    ),
    (
        ("kernel175 signal175 packet175 router175 cluster175 mirror175", 10),
        ["kernel175", "signal175", "packet175", "router175", "cluster175", "mirror175"],
    ),
    (
        ("kernel175 signal175 packet175 router175 cluster175 mirror175", 18),
        ["kernel175", "signal175", "packet175", "router175", "cluster175", "mirror175"],
    ),
    (
        ("kernel175 signal175 packet175 router175 cluster175 mirror175", 28),
        ["kernel175 signal175", "packet175 router175", "cluster175 mirror175"],
    ),
    (
        ("signal175 packet175 router175 cluster175 mirror175 filter175", 6),
        ["signal175", "packet175", "router175", "cluster175", "mirror175", "filter175"],
    ),
    (
        ("signal175 packet175 router175 cluster175 mirror175 filter175", 10),
        ["signal175", "packet175", "router175", "cluster175", "mirror175", "filter175"],
    ),
    (
        ("signal175 packet175 router175 cluster175 mirror175 filter175", 18),
        ["signal175", "packet175", "router175", "cluster175", "mirror175", "filter175"],
    ),
    (
        ("signal175 packet175 router175 cluster175 mirror175 filter175", 28),
        ["signal175 packet175", "router175 cluster175", "mirror175 filter175"],
    ),
    (
        ("packet175 router175 cluster175 mirror175 filter175 ranking175", 6),
        ["packet175", "router175", "cluster175", "mirror175", "filter175", "ranking175"],
    ),
    (
        ("packet175 router175 cluster175 mirror175 filter175 ranking175", 10),
        ["packet175", "router175", "cluster175", "mirror175", "filter175", "ranking175"],
    ),
    (
        ("packet175 router175 cluster175 mirror175 filter175 ranking175", 18),
        ["packet175", "router175", "cluster175", "mirror175", "filter175", "ranking175"],
    ),
    (
        ("packet175 router175 cluster175 mirror175 filter175 ranking175", 28),
        ["packet175 router175", "cluster175 mirror175", "filter175 ranking175"],
    ),
    (
        ("router175 cluster175 mirror175 filter175 ranking175 encoding175", 6),
        ["router175", "cluster175", "mirror175", "filter175", "ranking175", "encoding175"],
    ),
    (
        ("router175 cluster175 mirror175 filter175 ranking175 encoding175", 10),
        ["router175", "cluster175", "mirror175", "filter175", "ranking175", "encoding175"],
    ),
    (
        ("router175 cluster175 mirror175 filter175 ranking175 encoding175", 18),
        ["router175", "cluster175", "mirror175", "filter175", "ranking175", "encoding175"],
    ),
    (
        ("router175 cluster175 mirror175 filter175 ranking175 encoding175", 28),
        ["router175 cluster175", "mirror175 filter175", "ranking175 encoding175"],
    ),
    (
        ("cluster175 mirror175 filter175 ranking175 encoding175 mapping175", 6),
        ["cluster175", "mirror175", "filter175", "ranking175", "encoding175", "mapping175"],
    ),
    (
        ("cluster175 mirror175 filter175 ranking175 encoding175 mapping175", 10),
        ["cluster175", "mirror175", "filter175", "ranking175", "encoding175", "mapping175"],
    ),
    (
        ("cluster175 mirror175 filter175 ranking175 encoding175 mapping175", 18),
        ["cluster175", "mirror175", "filter175", "ranking175", "encoding175", "mapping175"],
    ),
    (
        ("cluster175 mirror175 filter175 ranking175 encoding175 mapping175", 28),
        ["cluster175 mirror175", "filter175 ranking175", "encoding175 mapping175"],
    ),
    (
        ("mirror175 filter175 ranking175 encoding175 mapping175 record175", 6),
        ["mirror175", "filter175", "ranking175", "encoding175", "mapping175", "record175"],
    ),
    (
        ("mirror175 filter175 ranking175 encoding175 mapping175 record175", 10),
        ["mirror175", "filter175", "ranking175", "encoding175", "mapping175", "record175"],
    ),
    (
        ("mirror175 filter175 ranking175 encoding175 mapping175 record175", 18),
        ["mirror175", "filter175", "ranking175", "encoding175", "mapping175", "record175"],
    ),
    (
        ("mirror175 filter175 ranking175 encoding175 mapping175 record175", 28),
        ["mirror175 filter175", "ranking175 encoding175", "mapping175 record175"],
    ),
    (
        ("filter175 ranking175 encoding175 mapping175 record175 candle175", 6),
        ["filter175", "ranking175", "encoding175", "mapping175", "record175", "candle175"],
    ),
    (
        ("filter175 ranking175 encoding175 mapping175 record175 candle175", 10),
        ["filter175", "ranking175", "encoding175", "mapping175", "record175", "candle175"],
    ),
    (
        ("filter175 ranking175 encoding175 mapping175 record175 candle175", 18),
        ["filter175", "ranking175", "encoding175", "mapping175", "record175", "candle175"],
    ),
    (
        ("filter175 ranking175 encoding175 mapping175 record175 candle175", 28),
        ["filter175 ranking175", "encoding175 mapping175", "record175 candle175"],
    ),
    (
        ("ranking175 encoding175 mapping175 record175 candle175 thread175", 6),
        ["ranking175", "encoding175", "mapping175", "record175", "candle175", "thread175"],
    ),
    (
        ("ranking175 encoding175 mapping175 record175 candle175 thread175", 10),
        ["ranking175", "encoding175", "mapping175", "record175", "candle175", "thread175"],
    ),
    (
        ("ranking175 encoding175 mapping175 record175 candle175 thread175", 18),
        ["ranking175", "encoding175", "mapping175", "record175", "candle175", "thread175"],
    ),
    (
        ("ranking175 encoding175 mapping175 record175 candle175 thread175", 28),
        ["ranking175 encoding175", "mapping175 record175", "candle175 thread175"],
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
