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
        ("round 732: the quick brown fox jumps over the lazy dog", 4),
        ["round", "732:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", 8),
        ["round", "732: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", 12),
        ["round 732:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", 16),
        ["round 732: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", 24),
        ["round 732: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 732: the quick brown fox jumps over the lazy dog", 32),
        ["round 732: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", 4),
        ["round", "732:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", 8),
        ["round", "732:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", 12),
        ["round 732:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", 16),
        ["round 732:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", 24),
        ["round 732: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 732: agentuniverse is a framework for multi agents", 32),
        ["round 732: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", 4),
        ["round", "732:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", 8),
        ["round", "732:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", 12),
        ["round 732:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", 16),
        ["round 732:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", 24),
        ["round 732: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 732: knowledge stored as vectors enables retrieval", 32),
        ["round 732: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 732: the processor reads the record then stops", 4),
        ["round", "732:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 732: the processor reads the record then stops", 8),
        ["round", "732: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 732: the processor reads the record then stops", 12),
        ["round 732:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 732: the processor reads the record then stops", 16),
        ["round 732: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 732: the processor reads the record then stops", 24),
        ["round 732: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 732: the processor reads the record then stops", 32),
        ["round 732: the processor reads", "the record then stops"],
    ),
    (
        ("round 732: a worker pulls the next task from the queue", 4),
        ["round", "732:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 732: a worker pulls the next task from the queue", 8),
        ["round", "732: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 732: a worker pulls the next task from the queue", 12),
        ["round 732: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 732: a worker pulls the next task from the queue", 16),
        ["round 732: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 732: a worker pulls the next task from the queue", 24),
        ["round 732: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 732: a worker pulls the next task from the queue", 32),
        ["round 732: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 732: signals travel through the network layer", 4),
        ["round", "732:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 732: signals travel through the network layer", 8),
        ["round", "732:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 732: signals travel through the network layer", 12),
        ["round 732:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 732: signals travel through the network layer", 16),
        ["round 732:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 732: signals travel through the network layer", 24),
        ["round 732: signals", "travel through the", "network layer"],
    ),
    (
        ("round 732: signals travel through the network layer", 32),
        ["round 732: signals travel", "through the network layer"],
    ),
    (
        ("round 732: the gateway routes each request by policy", 4),
        ["round", "732:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 732: the gateway routes each request by policy", 8),
        ["round", "732: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 732: the gateway routes each request by policy", 12),
        ["round 732:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 732: the gateway routes each request by policy", 16),
        ["round 732: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 732: the gateway routes each request by policy", 24),
        ["round 732: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 732: the gateway routes each request by policy", 32),
        ["round 732: the gateway routes", "each request by policy"],
    ),
    (
        ("round 732: memory grows until the buffer is full", 4),
        ["round", "732:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 732: memory grows until the buffer is full", 8),
        ["round", "732:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 732: memory grows until the buffer is full", 12),
        ["round 732:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 732: memory grows until the buffer is full", 16),
        ["round 732:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 732: memory grows until the buffer is full", 24), ["round 732: memory grows", "until the buffer is full"]),
    (("round 732: memory grows until the buffer is full", 32), ["round 732: memory grows until", "the buffer is full"]),
    (
        ("round 732: the cluster mirrors every packet twice", 4),
        ["round", "732:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 732: the cluster mirrors every packet twice", 8),
        ["round", "732: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 732: the cluster mirrors every packet twice", 12),
        ["round 732:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 732: the cluster mirrors every packet twice", 16),
        ["round 732: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 732: the cluster mirrors every packet twice", 24),
        ["round 732: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 732: the cluster mirrors every packet twice", 32),
        ["round 732: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", 4),
        ["round", "732:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", 8),
        ["round", "732:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", 12),
        ["round 732:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", 16),
        ["round 732:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", 24),
        ["round 732: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 732: ranking uses tokens learned from the corpus", 32),
        ["round 732: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 732: a long session ends when the candle dies", 4),
        ["round", "732:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 732: a long session ends when the candle dies", 8),
        ["round", "732: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 732: a long session ends when the candle dies", 12),
        ["round 732: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 732: a long session ends when the candle dies", 16),
        ["round 732: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 732: a long session ends when the candle dies", 24),
        ["round 732: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 732: a long session ends when the candle dies", 32),
        ["round 732: a long session ends", "when the candle dies"],
    ),
    (
        ("round 732: encode the prompt then map the result", 4),
        ["round", "732:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 732: encode the prompt then map the result", 8),
        ["round", "732:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 732: encode the prompt then map the result", 12),
        ["round 732:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 732: encode the prompt then map the result", 16),
        ["round 732:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 732: encode the prompt then map the result", 24),
        ["round 732: encode the", "prompt then map the", "result"],
    ),
    (("round 732: encode the prompt then map the result", 32), ["round 732: encode the prompt", "then map the result"]),
    (
        ("round 732: the kernel wakes the worker at dawn", 4),
        ["round", "732:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 732: the kernel wakes the worker at dawn", 8),
        ["round", "732: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 732: the kernel wakes the worker at dawn", 12),
        ["round 732:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 732: the kernel wakes the worker at dawn", 16), ["round 732: the", "kernel wakes the", "worker at dawn"]),
    (("round 732: the kernel wakes the worker at dawn", 24), ["round 732: the kernel", "wakes the worker at dawn"]),
    (("round 732: the kernel wakes the worker at dawn", 32), ["round 732: the kernel wakes the", "worker at dawn"]),
    (
        ("round 732: service latency drops after the patch", 4),
        ["round", "732:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 732: service latency drops after the patch", 8),
        ["round", "732:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 732: service latency drops after the patch", 12),
        ["round 732:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 732: service latency drops after the patch", 16),
        ["round 732:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 732: service latency drops after the patch", 24),
        ["round 732: service", "latency drops after the", "patch"],
    ),
    (("round 732: service latency drops after the patch", 32), ["round 732: service latency drops", "after the patch"]),
    (
        ("round 732: the library caches every vector it sees", 4),
        ["round", "732:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 732: the library caches every vector it sees", 8),
        ["round", "732: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 732: the library caches every vector it sees", 12),
        ["round 732:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 732: the library caches every vector it sees", 16),
        ["round 732: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 732: the library caches every vector it sees", 24),
        ["round 732: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 732: the library caches every vector it sees", 32),
        ["round 732: the library caches", "every vector it sees"],
    ),
    (
        ("round 732: agents argue then the debate resolves", 4),
        ["round", "732:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 732: agents argue then the debate resolves", 8),
        ["round", "732:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 732: agents argue then the debate resolves", 12),
        ["round 732:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 732: agents argue then the debate resolves", 16),
        ["round 732:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 732: agents argue then the debate resolves", 24), ["round 732: agents argue", "then the debate resolves"]),
    (("round 732: agents argue then the debate resolves", 32), ["round 732: agents argue then the", "debate resolves"]),
    (
        ("round 732: the filter keeps only strong matches", 4),
        ["round", "732:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 732: the filter keeps only strong matches", 8),
        ["round", "732: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 732: the filter keeps only strong matches", 12),
        ["round 732:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 732: the filter keeps only strong matches", 16),
        ["round 732: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 732: the filter keeps only strong matches", 24),
        ["round 732: the filter", "keeps only strong", "matches"],
    ),
    (("round 732: the filter keeps only strong matches", 32), ["round 732: the filter keeps only", "strong matches"]),
    (
        ("round 732: the model answers with a short reply", 4),
        ["round", "732:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 732: the model answers with a short reply", 8),
        ["round", "732: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 732: the model answers with a short reply", 12),
        ["round 732:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 732: the model answers with a short reply", 16),
        ["round 732: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 732: the model answers with a short reply", 24),
        ["round 732: the model", "answers with a short", "reply"],
    ),
    (("round 732: the model answers with a short reply", 32), ["round 732: the model answers", "with a short reply"]),
    (
        ("round 732: the recorder stores the reasoning trace", 4),
        ["round", "732:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 732: the recorder stores the reasoning trace", 8),
        ["round", "732: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 732: the recorder stores the reasoning trace", 12),
        ["round 732:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 732: the recorder stores the reasoning trace", 16),
        ["round 732: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 732: the recorder stores the reasoning trace", 24),
        ["round 732: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 732: the recorder stores the reasoning trace", 32),
        ["round 732: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 732: the angel watches the processor run", 4),
        ["round", "732:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 732: the angel watches the processor run", 8),
        ["round", "732: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 732: the angel watches the processor run", 12),
        ["round 732:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 732: the angel watches the processor run", 16),
        ["round 732: the", "angel watches", "the processor", "run"],
    ),
    (("round 732: the angel watches the processor run", 24), ["round 732: the angel", "watches the processor", "run"]),
    (("round 732: the angel watches the processor run", 32), ["round 732: the angel watches the", "processor run"]),
    (
        ("round 732: angle of the vector decides the match", 4),
        ["round", "732:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 732: angle of the vector decides the match", 8),
        ["round", "732:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 732: angle of the vector decides the match", 12),
        ["round 732:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 732: angle of the vector decides the match", 16),
        ["round 732: angle", "of the vector", "decides the", "match"],
    ),
    (("round 732: angle of the vector decides the match", 24), ["round 732: angle of the", "vector decides the match"]),
    (("round 732: angle of the vector decides the match", 32), ["round 732: angle of the vector", "decides the match"]),
    (
        ("round 732: the candle burns twice as long at night", 4),
        ["round", "732:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 732: the candle burns twice as long at night", 8),
        ["round", "732: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 732: the candle burns twice as long at night", 12),
        ["round 732:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 732: the candle burns twice as long at night", 16),
        ["round 732: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 732: the candle burns twice as long at night", 24),
        ["round 732: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 732: the candle burns twice as long at night", 32),
        ["round 732: the candle burns", "twice as long at night"],
    ),
    (
        ("round 732: a mirror of the universe in one line", 4),
        ["round", "732:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 732: a mirror of the universe in one line", 8),
        ["round", "732: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 732: a mirror of the universe in one line", 12),
        ["round 732: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 732: a mirror of the universe in one line", 16),
        ["round 732: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 732: a mirror of the universe in one line", 24), ["round 732: a mirror of", "the universe in one line"]),
    (("round 732: a mirror of the universe in one line", 32), ["round 732: a mirror of the", "universe in one line"]),
    (
        ("round 732: the queue drains before the storm", 4),
        ["round", "732:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 732: the queue drains before the storm", 8),
        ["round", "732: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 732: the queue drains before the storm", 12),
        ["round 732:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 732: the queue drains before the storm", 16), ["round 732: the", "queue drains", "before the storm"]),
    (("round 732: the queue drains before the storm", 24), ["round 732: the queue", "drains before the storm"]),
    (("round 732: the queue drains before the storm", 32), ["round 732: the queue drains", "before the storm"]),
    (
        ("kitten732 sitting732 agent732 angle732 universe732 memory732", 6),
        ["kitten732", "sitting732", "agent732", "angle732", "universe732", "memory732"],
    ),
    (
        ("kitten732 sitting732 agent732 angle732 universe732 memory732", 10),
        ["kitten732", "sitting732", "agent732", "angle732", "universe732", "memory732"],
    ),
    (
        ("kitten732 sitting732 agent732 angle732 universe732 memory732", 18),
        ["kitten732", "sitting732", "agent732 angle732", "universe732", "memory732"],
    ),
    (
        ("kitten732 sitting732 agent732 angle732 universe732 memory732", 28),
        ["kitten732 sitting732", "agent732 angle732", "universe732 memory732"],
    ),
    (
        ("sitting732 agent732 angle732 universe732 memory732 stream732", 6),
        ["sitting732", "agent732", "angle732", "universe732", "memory732", "stream732"],
    ),
    (
        ("sitting732 agent732 angle732 universe732 memory732 stream732", 10),
        ["sitting732", "agent732", "angle732", "universe732", "memory732", "stream732"],
    ),
    (
        ("sitting732 agent732 angle732 universe732 memory732 stream732", 18),
        ["sitting732", "agent732 angle732", "universe732", "memory732", "stream732"],
    ),
    (
        ("sitting732 agent732 angle732 universe732 memory732 stream732", 28),
        ["sitting732 agent732 angle732", "universe732 memory732", "stream732"],
    ),
    (
        ("agent732 angle732 universe732 memory732 stream732 context732", 6),
        ["agent732", "angle732", "universe732", "memory732", "stream732", "context732"],
    ),
    (
        ("agent732 angle732 universe732 memory732 stream732 context732", 10),
        ["agent732", "angle732", "universe732", "memory732", "stream732", "context732"],
    ),
    (
        ("agent732 angle732 universe732 memory732 stream732 context732", 18),
        ["agent732 angle732", "universe732", "memory732", "stream732", "context732"],
    ),
    (
        ("agent732 angle732 universe732 memory732 stream732 context732", 28),
        ["agent732 angle732", "universe732 memory732", "stream732 context732"],
    ),
    (
        ("angle732 universe732 memory732 stream732 context732 knowledge732", 6),
        ["angle732", "universe732", "memory732", "stream732", "context732", "knowledge732"],
    ),
    (
        ("angle732 universe732 memory732 stream732 context732 knowledge732", 10),
        ["angle732", "universe732", "memory732", "stream732", "context732", "knowledge732"],
    ),
    (
        ("angle732 universe732 memory732 stream732 context732 knowledge732", 18),
        ["angle732", "universe732", "memory732", "stream732", "context732", "knowledge732"],
    ),
    (
        ("angle732 universe732 memory732 stream732 context732 knowledge732", 28),
        ["angle732 universe732", "memory732 stream732", "context732 knowledge732"],
    ),
    (
        ("universe732 memory732 stream732 context732 knowledge732 vector732", 6),
        ["universe732", "memory732", "stream732", "context732", "knowledge732", "vector732"],
    ),
    (
        ("universe732 memory732 stream732 context732 knowledge732 vector732", 10),
        ["universe732", "memory732", "stream732", "context732", "knowledge732", "vector732"],
    ),
    (
        ("universe732 memory732 stream732 context732 knowledge732 vector732", 18),
        ["universe732", "memory732", "stream732", "context732", "knowledge732", "vector732"],
    ),
    (
        ("universe732 memory732 stream732 context732 knowledge732 vector732", 28),
        ["universe732 memory732", "stream732 context732", "knowledge732 vector732"],
    ),
    (
        ("memory732 stream732 context732 knowledge732 vector732 processor732", 6),
        ["memory732", "stream732", "context732", "knowledge732", "vector732", "processor732"],
    ),
    (
        ("memory732 stream732 context732 knowledge732 vector732 processor732", 10),
        ["memory732", "stream732", "context732", "knowledge732", "vector732", "processor732"],
    ),
    (
        ("memory732 stream732 context732 knowledge732 vector732 processor732", 18),
        ["memory732", "stream732", "context732", "knowledge732", "vector732", "processor732"],
    ),
    (
        ("memory732 stream732 context732 knowledge732 vector732 processor732", 28),
        ["memory732 stream732", "context732 knowledge732", "vector732 processor732"],
    ),
    (
        ("stream732 context732 knowledge732 vector732 processor732 reasoning732", 6),
        ["stream732", "context732", "knowledge732", "vector732", "processor732", "reasoning732"],
    ),
    (
        ("stream732 context732 knowledge732 vector732 processor732 reasoning732", 10),
        ["stream732", "context732", "knowledge732", "vector732", "processor732", "reasoning732"],
    ),
    (
        ("stream732 context732 knowledge732 vector732 processor732 reasoning732", 18),
        ["stream732", "context732", "knowledge732", "vector732", "processor732", "reasoning732"],
    ),
    (
        ("stream732 context732 knowledge732 vector732 processor732 reasoning732", 28),
        ["stream732 context732", "knowledge732 vector732", "processor732 reasoning732"],
    ),
    (
        ("context732 knowledge732 vector732 processor732 reasoning732 machine732", 6),
        ["context732", "knowledge732", "vector732", "processor732", "reasoning732", "machine732"],
    ),
    (
        ("context732 knowledge732 vector732 processor732 reasoning732 machine732", 10),
        ["context732", "knowledge732", "vector732", "processor732", "reasoning732", "machine732"],
    ),
    (
        ("context732 knowledge732 vector732 processor732 reasoning732 machine732", 18),
        ["context732", "knowledge732", "vector732", "processor732", "reasoning732", "machine732"],
    ),
    (
        ("context732 knowledge732 vector732 processor732 reasoning732 machine732", 28),
        ["context732 knowledge732", "vector732 processor732", "reasoning732 machine732"],
    ),
    (
        ("knowledge732 vector732 processor732 reasoning732 machine732 learning732", 6),
        ["knowledge732", "vector732", "processor732", "reasoning732", "machine732", "learning732"],
    ),
    (
        ("knowledge732 vector732 processor732 reasoning732 machine732 learning732", 10),
        ["knowledge732", "vector732", "processor732", "reasoning732", "machine732", "learning732"],
    ),
    (
        ("knowledge732 vector732 processor732 reasoning732 machine732 learning732", 18),
        ["knowledge732", "vector732", "processor732", "reasoning732", "machine732", "learning732"],
    ),
    (
        ("knowledge732 vector732 processor732 reasoning732 machine732 learning732", 28),
        ["knowledge732 vector732", "processor732 reasoning732", "machine732 learning732"],
    ),
    (
        ("vector732 processor732 reasoning732 machine732 learning732 model732", 6),
        ["vector732", "processor732", "reasoning732", "machine732", "learning732", "model732"],
    ),
    (
        ("vector732 processor732 reasoning732 machine732 learning732 model732", 10),
        ["vector732", "processor732", "reasoning732", "machine732", "learning732", "model732"],
    ),
    (
        ("vector732 processor732 reasoning732 machine732 learning732 model732", 18),
        ["vector732", "processor732", "reasoning732", "machine732", "learning732", "model732"],
    ),
    (
        ("vector732 processor732 reasoning732 machine732 learning732 model732", 28),
        ["vector732 processor732", "reasoning732 machine732", "learning732 model732"],
    ),
    (
        ("processor732 reasoning732 machine732 learning732 model732 token732", 6),
        ["processor732", "reasoning732", "machine732", "learning732", "model732", "token732"],
    ),
    (
        ("processor732 reasoning732 machine732 learning732 model732 token732", 10),
        ["processor732", "reasoning732", "machine732", "learning732", "model732", "token732"],
    ),
    (
        ("processor732 reasoning732 machine732 learning732 model732 token732", 18),
        ["processor732", "reasoning732", "machine732", "learning732", "model732 token732"],
    ),
    (
        ("processor732 reasoning732 machine732 learning732 model732 token732", 28),
        ["processor732 reasoning732", "machine732 learning732", "model732 token732"],
    ),
    (
        ("reasoning732 machine732 learning732 model732 token732 prompt732", 6),
        ["reasoning732", "machine732", "learning732", "model732", "token732", "prompt732"],
    ),
    (
        ("reasoning732 machine732 learning732 model732 token732 prompt732", 10),
        ["reasoning732", "machine732", "learning732", "model732", "token732", "prompt732"],
    ),
    (
        ("reasoning732 machine732 learning732 model732 token732 prompt732", 18),
        ["reasoning732", "machine732", "learning732", "model732 token732", "prompt732"],
    ),
    (
        ("reasoning732 machine732 learning732 model732 token732 prompt732", 28),
        ["reasoning732 machine732", "learning732 model732", "token732 prompt732"],
    ),
    (
        ("machine732 learning732 model732 token732 prompt732 session732", 6),
        ["machine732", "learning732", "model732", "token732", "prompt732", "session732"],
    ),
    (
        ("machine732 learning732 model732 token732 prompt732 session732", 10),
        ["machine732", "learning732", "model732", "token732", "prompt732", "session732"],
    ),
    (
        ("machine732 learning732 model732 token732 prompt732 session732", 18),
        ["machine732", "learning732", "model732 token732", "prompt732", "session732"],
    ),
    (
        ("machine732 learning732 model732 token732 prompt732 session732", 28),
        ["machine732 learning732", "model732 token732 prompt732", "session732"],
    ),
    (
        ("learning732 model732 token732 prompt732 session732 library732", 6),
        ["learning732", "model732", "token732", "prompt732", "session732", "library732"],
    ),
    (
        ("learning732 model732 token732 prompt732 session732 library732", 10),
        ["learning732", "model732", "token732", "prompt732", "session732", "library732"],
    ),
    (
        ("learning732 model732 token732 prompt732 session732 library732", 18),
        ["learning732", "model732 token732", "prompt732", "session732", "library732"],
    ),
    (
        ("learning732 model732 token732 prompt732 session732 library732", 28),
        ["learning732 model732", "token732 prompt732", "session732 library732"],
    ),
    (
        ("model732 token732 prompt732 session732 library732 service732", 6),
        ["model732", "token732", "prompt732", "session732", "library732", "service732"],
    ),
    (
        ("model732 token732 prompt732 session732 library732 service732", 10),
        ["model732", "token732", "prompt732", "session732", "library732", "service732"],
    ),
    (
        ("model732 token732 prompt732 session732 library732 service732", 18),
        ["model732 token732", "prompt732", "session732", "library732", "service732"],
    ),
    (
        ("model732 token732 prompt732 session732 library732 service732", 28),
        ["model732 token732 prompt732", "session732 library732", "service732"],
    ),
    (
        ("token732 prompt732 session732 library732 service732 gateway732", 6),
        ["token732", "prompt732", "session732", "library732", "service732", "gateway732"],
    ),
    (
        ("token732 prompt732 session732 library732 service732 gateway732", 10),
        ["token732", "prompt732", "session732", "library732", "service732", "gateway732"],
    ),
    (
        ("token732 prompt732 session732 library732 service732 gateway732", 18),
        ["token732 prompt732", "session732", "library732", "service732", "gateway732"],
    ),
    (
        ("token732 prompt732 session732 library732 service732 gateway732", 28),
        ["token732 prompt732", "session732 library732", "service732 gateway732"],
    ),
    (
        ("prompt732 session732 library732 service732 gateway732 storage732", 6),
        ["prompt732", "session732", "library732", "service732", "gateway732", "storage732"],
    ),
    (
        ("prompt732 session732 library732 service732 gateway732 storage732", 10),
        ["prompt732", "session732", "library732", "service732", "gateway732", "storage732"],
    ),
    (
        ("prompt732 session732 library732 service732 gateway732 storage732", 18),
        ["prompt732", "session732", "library732", "service732", "gateway732", "storage732"],
    ),
    (
        ("prompt732 session732 library732 service732 gateway732 storage732", 28),
        ["prompt732 session732", "library732 service732", "gateway732 storage732"],
    ),
    (
        ("session732 library732 service732 gateway732 storage732 network732", 6),
        ["session732", "library732", "service732", "gateway732", "storage732", "network732"],
    ),
    (
        ("session732 library732 service732 gateway732 storage732 network732", 10),
        ["session732", "library732", "service732", "gateway732", "storage732", "network732"],
    ),
    (
        ("session732 library732 service732 gateway732 storage732 network732", 18),
        ["session732", "library732", "service732", "gateway732", "storage732", "network732"],
    ),
    (
        ("session732 library732 service732 gateway732 storage732 network732", 28),
        ["session732 library732", "service732 gateway732", "storage732 network732"],
    ),
    (
        ("library732 service732 gateway732 storage732 network732 latency732", 6),
        ["library732", "service732", "gateway732", "storage732", "network732", "latency732"],
    ),
    (
        ("library732 service732 gateway732 storage732 network732 latency732", 10),
        ["library732", "service732", "gateway732", "storage732", "network732", "latency732"],
    ),
    (
        ("library732 service732 gateway732 storage732 network732 latency732", 18),
        ["library732", "service732", "gateway732", "storage732", "network732", "latency732"],
    ),
    (
        ("library732 service732 gateway732 storage732 network732 latency732", 28),
        ["library732 service732", "gateway732 storage732", "network732 latency732"],
    ),
    (
        ("service732 gateway732 storage732 network732 latency732 buffer732", 6),
        ["service732", "gateway732", "storage732", "network732", "latency732", "buffer732"],
    ),
    (
        ("service732 gateway732 storage732 network732 latency732 buffer732", 10),
        ["service732", "gateway732", "storage732", "network732", "latency732", "buffer732"],
    ),
    (
        ("service732 gateway732 storage732 network732 latency732 buffer732", 18),
        ["service732", "gateway732", "storage732", "network732", "latency732", "buffer732"],
    ),
    (
        ("service732 gateway732 storage732 network732 latency732 buffer732", 28),
        ["service732 gateway732", "storage732 network732", "latency732 buffer732"],
    ),
    (
        ("gateway732 storage732 network732 latency732 buffer732 queue732", 6),
        ["gateway732", "storage732", "network732", "latency732", "buffer732", "queue732"],
    ),
    (
        ("gateway732 storage732 network732 latency732 buffer732 queue732", 10),
        ["gateway732", "storage732", "network732", "latency732", "buffer732", "queue732"],
    ),
    (
        ("gateway732 storage732 network732 latency732 buffer732 queue732", 18),
        ["gateway732", "storage732", "network732", "latency732", "buffer732 queue732"],
    ),
    (
        ("gateway732 storage732 network732 latency732 buffer732 queue732", 28),
        ["gateway732 storage732", "network732 latency732", "buffer732 queue732"],
    ),
    (
        ("storage732 network732 latency732 buffer732 queue732 worker732", 6),
        ["storage732", "network732", "latency732", "buffer732", "queue732", "worker732"],
    ),
    (
        ("storage732 network732 latency732 buffer732 queue732 worker732", 10),
        ["storage732", "network732", "latency732", "buffer732", "queue732", "worker732"],
    ),
    (
        ("storage732 network732 latency732 buffer732 queue732 worker732", 18),
        ["storage732", "network732", "latency732", "buffer732 queue732", "worker732"],
    ),
    (
        ("storage732 network732 latency732 buffer732 queue732 worker732", 28),
        ["storage732 network732", "latency732 buffer732", "queue732 worker732"],
    ),
    (
        ("network732 latency732 buffer732 queue732 worker732 kernel732", 6),
        ["network732", "latency732", "buffer732", "queue732", "worker732", "kernel732"],
    ),
    (
        ("network732 latency732 buffer732 queue732 worker732 kernel732", 10),
        ["network732", "latency732", "buffer732", "queue732", "worker732", "kernel732"],
    ),
    (
        ("network732 latency732 buffer732 queue732 worker732 kernel732", 18),
        ["network732", "latency732", "buffer732 queue732", "worker732", "kernel732"],
    ),
    (
        ("network732 latency732 buffer732 queue732 worker732 kernel732", 28),
        ["network732 latency732", "buffer732 queue732 worker732", "kernel732"],
    ),
    (
        ("latency732 buffer732 queue732 worker732 kernel732 signal732", 6),
        ["latency732", "buffer732", "queue732", "worker732", "kernel732", "signal732"],
    ),
    (
        ("latency732 buffer732 queue732 worker732 kernel732 signal732", 10),
        ["latency732", "buffer732", "queue732", "worker732", "kernel732", "signal732"],
    ),
    (
        ("latency732 buffer732 queue732 worker732 kernel732 signal732", 18),
        ["latency732", "buffer732 queue732", "worker732", "kernel732", "signal732"],
    ),
    (
        ("latency732 buffer732 queue732 worker732 kernel732 signal732", 28),
        ["latency732 buffer732", "queue732 worker732 kernel732", "signal732"],
    ),
    (
        ("buffer732 queue732 worker732 kernel732 signal732 packet732", 6),
        ["buffer732", "queue732", "worker732", "kernel732", "signal732", "packet732"],
    ),
    (
        ("buffer732 queue732 worker732 kernel732 signal732 packet732", 10),
        ["buffer732", "queue732", "worker732", "kernel732", "signal732", "packet732"],
    ),
    (
        ("buffer732 queue732 worker732 kernel732 signal732 packet732", 18),
        ["buffer732 queue732", "worker732", "kernel732", "signal732", "packet732"],
    ),
    (
        ("buffer732 queue732 worker732 kernel732 signal732 packet732", 28),
        ["buffer732 queue732 worker732", "kernel732 signal732", "packet732"],
    ),
    (
        ("queue732 worker732 kernel732 signal732 packet732 router732", 6),
        ["queue732", "worker732", "kernel732", "signal732", "packet732", "router732"],
    ),
    (
        ("queue732 worker732 kernel732 signal732 packet732 router732", 10),
        ["queue732", "worker732", "kernel732", "signal732", "packet732", "router732"],
    ),
    (
        ("queue732 worker732 kernel732 signal732 packet732 router732", 18),
        ["queue732 worker732", "kernel732", "signal732", "packet732", "router732"],
    ),
    (
        ("queue732 worker732 kernel732 signal732 packet732 router732", 28),
        ["queue732 worker732 kernel732", "signal732 packet732", "router732"],
    ),
    (
        ("worker732 kernel732 signal732 packet732 router732 cluster732", 6),
        ["worker732", "kernel732", "signal732", "packet732", "router732", "cluster732"],
    ),
    (
        ("worker732 kernel732 signal732 packet732 router732 cluster732", 10),
        ["worker732", "kernel732", "signal732", "packet732", "router732", "cluster732"],
    ),
    (
        ("worker732 kernel732 signal732 packet732 router732 cluster732", 18),
        ["worker732", "kernel732", "signal732", "packet732", "router732", "cluster732"],
    ),
    (
        ("worker732 kernel732 signal732 packet732 router732 cluster732", 28),
        ["worker732 kernel732", "signal732 packet732", "router732 cluster732"],
    ),
    (
        ("kernel732 signal732 packet732 router732 cluster732 mirror732", 6),
        ["kernel732", "signal732", "packet732", "router732", "cluster732", "mirror732"],
    ),
    (
        ("kernel732 signal732 packet732 router732 cluster732 mirror732", 10),
        ["kernel732", "signal732", "packet732", "router732", "cluster732", "mirror732"],
    ),
    (
        ("kernel732 signal732 packet732 router732 cluster732 mirror732", 18),
        ["kernel732", "signal732", "packet732", "router732", "cluster732", "mirror732"],
    ),
    (
        ("kernel732 signal732 packet732 router732 cluster732 mirror732", 28),
        ["kernel732 signal732", "packet732 router732", "cluster732 mirror732"],
    ),
    (
        ("signal732 packet732 router732 cluster732 mirror732 filter732", 6),
        ["signal732", "packet732", "router732", "cluster732", "mirror732", "filter732"],
    ),
    (
        ("signal732 packet732 router732 cluster732 mirror732 filter732", 10),
        ["signal732", "packet732", "router732", "cluster732", "mirror732", "filter732"],
    ),
    (
        ("signal732 packet732 router732 cluster732 mirror732 filter732", 18),
        ["signal732", "packet732", "router732", "cluster732", "mirror732", "filter732"],
    ),
    (
        ("signal732 packet732 router732 cluster732 mirror732 filter732", 28),
        ["signal732 packet732", "router732 cluster732", "mirror732 filter732"],
    ),
    (
        ("packet732 router732 cluster732 mirror732 filter732 ranking732", 6),
        ["packet732", "router732", "cluster732", "mirror732", "filter732", "ranking732"],
    ),
    (
        ("packet732 router732 cluster732 mirror732 filter732 ranking732", 10),
        ["packet732", "router732", "cluster732", "mirror732", "filter732", "ranking732"],
    ),
    (
        ("packet732 router732 cluster732 mirror732 filter732 ranking732", 18),
        ["packet732", "router732", "cluster732", "mirror732", "filter732", "ranking732"],
    ),
    (
        ("packet732 router732 cluster732 mirror732 filter732 ranking732", 28),
        ["packet732 router732", "cluster732 mirror732", "filter732 ranking732"],
    ),
    (
        ("router732 cluster732 mirror732 filter732 ranking732 encoding732", 6),
        ["router732", "cluster732", "mirror732", "filter732", "ranking732", "encoding732"],
    ),
    (
        ("router732 cluster732 mirror732 filter732 ranking732 encoding732", 10),
        ["router732", "cluster732", "mirror732", "filter732", "ranking732", "encoding732"],
    ),
    (
        ("router732 cluster732 mirror732 filter732 ranking732 encoding732", 18),
        ["router732", "cluster732", "mirror732", "filter732", "ranking732", "encoding732"],
    ),
    (
        ("router732 cluster732 mirror732 filter732 ranking732 encoding732", 28),
        ["router732 cluster732", "mirror732 filter732", "ranking732 encoding732"],
    ),
    (
        ("cluster732 mirror732 filter732 ranking732 encoding732 mapping732", 6),
        ["cluster732", "mirror732", "filter732", "ranking732", "encoding732", "mapping732"],
    ),
    (
        ("cluster732 mirror732 filter732 ranking732 encoding732 mapping732", 10),
        ["cluster732", "mirror732", "filter732", "ranking732", "encoding732", "mapping732"],
    ),
    (
        ("cluster732 mirror732 filter732 ranking732 encoding732 mapping732", 18),
        ["cluster732", "mirror732", "filter732", "ranking732", "encoding732", "mapping732"],
    ),
    (
        ("cluster732 mirror732 filter732 ranking732 encoding732 mapping732", 28),
        ["cluster732 mirror732", "filter732 ranking732", "encoding732 mapping732"],
    ),
    (
        ("mirror732 filter732 ranking732 encoding732 mapping732 record732", 6),
        ["mirror732", "filter732", "ranking732", "encoding732", "mapping732", "record732"],
    ),
    (
        ("mirror732 filter732 ranking732 encoding732 mapping732 record732", 10),
        ["mirror732", "filter732", "ranking732", "encoding732", "mapping732", "record732"],
    ),
    (
        ("mirror732 filter732 ranking732 encoding732 mapping732 record732", 18),
        ["mirror732", "filter732", "ranking732", "encoding732", "mapping732", "record732"],
    ),
    (
        ("mirror732 filter732 ranking732 encoding732 mapping732 record732", 28),
        ["mirror732 filter732", "ranking732 encoding732", "mapping732 record732"],
    ),
    (
        ("filter732 ranking732 encoding732 mapping732 record732 candle732", 6),
        ["filter732", "ranking732", "encoding732", "mapping732", "record732", "candle732"],
    ),
    (
        ("filter732 ranking732 encoding732 mapping732 record732 candle732", 10),
        ["filter732", "ranking732", "encoding732", "mapping732", "record732", "candle732"],
    ),
    (
        ("filter732 ranking732 encoding732 mapping732 record732 candle732", 18),
        ["filter732", "ranking732", "encoding732", "mapping732", "record732", "candle732"],
    ),
    (
        ("filter732 ranking732 encoding732 mapping732 record732 candle732", 28),
        ["filter732 ranking732", "encoding732 mapping732", "record732 candle732"],
    ),
    (
        ("ranking732 encoding732 mapping732 record732 candle732 thread732", 6),
        ["ranking732", "encoding732", "mapping732", "record732", "candle732", "thread732"],
    ),
    (
        ("ranking732 encoding732 mapping732 record732 candle732 thread732", 10),
        ["ranking732", "encoding732", "mapping732", "record732", "candle732", "thread732"],
    ),
    (
        ("ranking732 encoding732 mapping732 record732 candle732 thread732", 18),
        ["ranking732", "encoding732", "mapping732", "record732", "candle732", "thread732"],
    ),
    (
        ("ranking732 encoding732 mapping732 record732 candle732 thread732", 28),
        ["ranking732 encoding732", "mapping732 record732", "candle732 thread732"],
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
