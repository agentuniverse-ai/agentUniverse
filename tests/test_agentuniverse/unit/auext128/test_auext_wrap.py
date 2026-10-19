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
        ("round 128: the quick brown fox jumps over the lazy dog", 4),
        ["round", "128:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", 8),
        ["round", "128: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", 12),
        ["round 128:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", 16),
        ["round 128: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", 24),
        ["round 128: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 128: the quick brown fox jumps over the lazy dog", 32),
        ["round 128: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", 4),
        ["round", "128:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", 8),
        ["round", "128:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", 12),
        ["round 128:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", 16),
        ["round 128:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", 24),
        ["round 128: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 128: agentuniverse is a framework for multi agents", 32),
        ["round 128: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", 4),
        ["round", "128:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", 8),
        ["round", "128:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", 12),
        ["round 128:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", 16),
        ["round 128:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", 24),
        ["round 128: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 128: knowledge stored as vectors enables retrieval", 32),
        ["round 128: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 128: the processor reads the record then stops", 4),
        ["round", "128:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 128: the processor reads the record then stops", 8),
        ["round", "128: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 128: the processor reads the record then stops", 12),
        ["round 128:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 128: the processor reads the record then stops", 16),
        ["round 128: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 128: the processor reads the record then stops", 24),
        ["round 128: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 128: the processor reads the record then stops", 32),
        ["round 128: the processor reads", "the record then stops"],
    ),
    (
        ("round 128: a worker pulls the next task from the queue", 4),
        ["round", "128:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 128: a worker pulls the next task from the queue", 8),
        ["round", "128: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 128: a worker pulls the next task from the queue", 12),
        ["round 128: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 128: a worker pulls the next task from the queue", 16),
        ["round 128: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 128: a worker pulls the next task from the queue", 24),
        ["round 128: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 128: a worker pulls the next task from the queue", 32),
        ["round 128: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 128: signals travel through the network layer", 4),
        ["round", "128:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 128: signals travel through the network layer", 8),
        ["round", "128:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 128: signals travel through the network layer", 12),
        ["round 128:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 128: signals travel through the network layer", 16),
        ["round 128:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 128: signals travel through the network layer", 24),
        ["round 128: signals", "travel through the", "network layer"],
    ),
    (
        ("round 128: signals travel through the network layer", 32),
        ["round 128: signals travel", "through the network layer"],
    ),
    (
        ("round 128: the gateway routes each request by policy", 4),
        ["round", "128:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 128: the gateway routes each request by policy", 8),
        ["round", "128: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 128: the gateway routes each request by policy", 12),
        ["round 128:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 128: the gateway routes each request by policy", 16),
        ["round 128: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 128: the gateway routes each request by policy", 24),
        ["round 128: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 128: the gateway routes each request by policy", 32),
        ["round 128: the gateway routes", "each request by policy"],
    ),
    (
        ("round 128: memory grows until the buffer is full", 4),
        ["round", "128:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 128: memory grows until the buffer is full", 8),
        ["round", "128:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 128: memory grows until the buffer is full", 12),
        ["round 128:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 128: memory grows until the buffer is full", 16),
        ["round 128:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 128: memory grows until the buffer is full", 24), ["round 128: memory grows", "until the buffer is full"]),
    (("round 128: memory grows until the buffer is full", 32), ["round 128: memory grows until", "the buffer is full"]),
    (
        ("round 128: the cluster mirrors every packet twice", 4),
        ["round", "128:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 128: the cluster mirrors every packet twice", 8),
        ["round", "128: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 128: the cluster mirrors every packet twice", 12),
        ["round 128:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 128: the cluster mirrors every packet twice", 16),
        ["round 128: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 128: the cluster mirrors every packet twice", 24),
        ["round 128: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 128: the cluster mirrors every packet twice", 32),
        ["round 128: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", 4),
        ["round", "128:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", 8),
        ["round", "128:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", 12),
        ["round 128:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", 16),
        ["round 128:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", 24),
        ["round 128: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 128: ranking uses tokens learned from the corpus", 32),
        ["round 128: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 128: a long session ends when the candle dies", 4),
        ["round", "128:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 128: a long session ends when the candle dies", 8),
        ["round", "128: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 128: a long session ends when the candle dies", 12),
        ["round 128: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 128: a long session ends when the candle dies", 16),
        ["round 128: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 128: a long session ends when the candle dies", 24),
        ["round 128: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 128: a long session ends when the candle dies", 32),
        ["round 128: a long session ends", "when the candle dies"],
    ),
    (
        ("round 128: encode the prompt then map the result", 4),
        ["round", "128:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 128: encode the prompt then map the result", 8),
        ["round", "128:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 128: encode the prompt then map the result", 12),
        ["round 128:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 128: encode the prompt then map the result", 16),
        ["round 128:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 128: encode the prompt then map the result", 24),
        ["round 128: encode the", "prompt then map the", "result"],
    ),
    (("round 128: encode the prompt then map the result", 32), ["round 128: encode the prompt", "then map the result"]),
    (
        ("round 128: the kernel wakes the worker at dawn", 4),
        ["round", "128:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 128: the kernel wakes the worker at dawn", 8),
        ["round", "128: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 128: the kernel wakes the worker at dawn", 12),
        ["round 128:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 128: the kernel wakes the worker at dawn", 16), ["round 128: the", "kernel wakes the", "worker at dawn"]),
    (("round 128: the kernel wakes the worker at dawn", 24), ["round 128: the kernel", "wakes the worker at dawn"]),
    (("round 128: the kernel wakes the worker at dawn", 32), ["round 128: the kernel wakes the", "worker at dawn"]),
    (
        ("round 128: service latency drops after the patch", 4),
        ["round", "128:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 128: service latency drops after the patch", 8),
        ["round", "128:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 128: service latency drops after the patch", 12),
        ["round 128:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 128: service latency drops after the patch", 16),
        ["round 128:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 128: service latency drops after the patch", 24),
        ["round 128: service", "latency drops after the", "patch"],
    ),
    (("round 128: service latency drops after the patch", 32), ["round 128: service latency drops", "after the patch"]),
    (
        ("round 128: the library caches every vector it sees", 4),
        ["round", "128:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 128: the library caches every vector it sees", 8),
        ["round", "128: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 128: the library caches every vector it sees", 12),
        ["round 128:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 128: the library caches every vector it sees", 16),
        ["round 128: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 128: the library caches every vector it sees", 24),
        ["round 128: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 128: the library caches every vector it sees", 32),
        ["round 128: the library caches", "every vector it sees"],
    ),
    (
        ("round 128: agents argue then the debate resolves", 4),
        ["round", "128:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 128: agents argue then the debate resolves", 8),
        ["round", "128:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 128: agents argue then the debate resolves", 12),
        ["round 128:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 128: agents argue then the debate resolves", 16),
        ["round 128:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 128: agents argue then the debate resolves", 24), ["round 128: agents argue", "then the debate resolves"]),
    (("round 128: agents argue then the debate resolves", 32), ["round 128: agents argue then the", "debate resolves"]),
    (
        ("round 128: the filter keeps only strong matches", 4),
        ["round", "128:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 128: the filter keeps only strong matches", 8),
        ["round", "128: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 128: the filter keeps only strong matches", 12),
        ["round 128:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 128: the filter keeps only strong matches", 16),
        ["round 128: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 128: the filter keeps only strong matches", 24),
        ["round 128: the filter", "keeps only strong", "matches"],
    ),
    (("round 128: the filter keeps only strong matches", 32), ["round 128: the filter keeps only", "strong matches"]),
    (
        ("round 128: the model answers with a short reply", 4),
        ["round", "128:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 128: the model answers with a short reply", 8),
        ["round", "128: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 128: the model answers with a short reply", 12),
        ["round 128:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 128: the model answers with a short reply", 16),
        ["round 128: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 128: the model answers with a short reply", 24),
        ["round 128: the model", "answers with a short", "reply"],
    ),
    (("round 128: the model answers with a short reply", 32), ["round 128: the model answers", "with a short reply"]),
    (
        ("round 128: the recorder stores the reasoning trace", 4),
        ["round", "128:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 128: the recorder stores the reasoning trace", 8),
        ["round", "128: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 128: the recorder stores the reasoning trace", 12),
        ["round 128:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 128: the recorder stores the reasoning trace", 16),
        ["round 128: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 128: the recorder stores the reasoning trace", 24),
        ["round 128: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 128: the recorder stores the reasoning trace", 32),
        ["round 128: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 128: the angel watches the processor run", 4),
        ["round", "128:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 128: the angel watches the processor run", 8),
        ["round", "128: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 128: the angel watches the processor run", 12),
        ["round 128:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 128: the angel watches the processor run", 16),
        ["round 128: the", "angel watches", "the processor", "run"],
    ),
    (("round 128: the angel watches the processor run", 24), ["round 128: the angel", "watches the processor", "run"]),
    (("round 128: the angel watches the processor run", 32), ["round 128: the angel watches the", "processor run"]),
    (
        ("round 128: angle of the vector decides the match", 4),
        ["round", "128:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 128: angle of the vector decides the match", 8),
        ["round", "128:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 128: angle of the vector decides the match", 12),
        ["round 128:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 128: angle of the vector decides the match", 16),
        ["round 128: angle", "of the vector", "decides the", "match"],
    ),
    (("round 128: angle of the vector decides the match", 24), ["round 128: angle of the", "vector decides the match"]),
    (("round 128: angle of the vector decides the match", 32), ["round 128: angle of the vector", "decides the match"]),
    (
        ("round 128: the candle burns twice as long at night", 4),
        ["round", "128:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 128: the candle burns twice as long at night", 8),
        ["round", "128: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 128: the candle burns twice as long at night", 12),
        ["round 128:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 128: the candle burns twice as long at night", 16),
        ["round 128: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 128: the candle burns twice as long at night", 24),
        ["round 128: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 128: the candle burns twice as long at night", 32),
        ["round 128: the candle burns", "twice as long at night"],
    ),
    (
        ("round 128: a mirror of the universe in one line", 4),
        ["round", "128:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 128: a mirror of the universe in one line", 8),
        ["round", "128: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 128: a mirror of the universe in one line", 12),
        ["round 128: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 128: a mirror of the universe in one line", 16),
        ["round 128: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 128: a mirror of the universe in one line", 24), ["round 128: a mirror of", "the universe in one line"]),
    (("round 128: a mirror of the universe in one line", 32), ["round 128: a mirror of the", "universe in one line"]),
    (
        ("round 128: the queue drains before the storm", 4),
        ["round", "128:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 128: the queue drains before the storm", 8),
        ["round", "128: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 128: the queue drains before the storm", 12),
        ["round 128:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 128: the queue drains before the storm", 16), ["round 128: the", "queue drains", "before the storm"]),
    (("round 128: the queue drains before the storm", 24), ["round 128: the queue", "drains before the storm"]),
    (("round 128: the queue drains before the storm", 32), ["round 128: the queue drains", "before the storm"]),
    (
        ("kitten128 sitting128 agent128 angle128 universe128 memory128", 6),
        ["kitten128", "sitting128", "agent128", "angle128", "universe128", "memory128"],
    ),
    (
        ("kitten128 sitting128 agent128 angle128 universe128 memory128", 10),
        ["kitten128", "sitting128", "agent128", "angle128", "universe128", "memory128"],
    ),
    (
        ("kitten128 sitting128 agent128 angle128 universe128 memory128", 18),
        ["kitten128", "sitting128", "agent128 angle128", "universe128", "memory128"],
    ),
    (
        ("kitten128 sitting128 agent128 angle128 universe128 memory128", 28),
        ["kitten128 sitting128", "agent128 angle128", "universe128 memory128"],
    ),
    (
        ("sitting128 agent128 angle128 universe128 memory128 stream128", 6),
        ["sitting128", "agent128", "angle128", "universe128", "memory128", "stream128"],
    ),
    (
        ("sitting128 agent128 angle128 universe128 memory128 stream128", 10),
        ["sitting128", "agent128", "angle128", "universe128", "memory128", "stream128"],
    ),
    (
        ("sitting128 agent128 angle128 universe128 memory128 stream128", 18),
        ["sitting128", "agent128 angle128", "universe128", "memory128", "stream128"],
    ),
    (
        ("sitting128 agent128 angle128 universe128 memory128 stream128", 28),
        ["sitting128 agent128 angle128", "universe128 memory128", "stream128"],
    ),
    (
        ("agent128 angle128 universe128 memory128 stream128 context128", 6),
        ["agent128", "angle128", "universe128", "memory128", "stream128", "context128"],
    ),
    (
        ("agent128 angle128 universe128 memory128 stream128 context128", 10),
        ["agent128", "angle128", "universe128", "memory128", "stream128", "context128"],
    ),
    (
        ("agent128 angle128 universe128 memory128 stream128 context128", 18),
        ["agent128 angle128", "universe128", "memory128", "stream128", "context128"],
    ),
    (
        ("agent128 angle128 universe128 memory128 stream128 context128", 28),
        ["agent128 angle128", "universe128 memory128", "stream128 context128"],
    ),
    (
        ("angle128 universe128 memory128 stream128 context128 knowledge128", 6),
        ["angle128", "universe128", "memory128", "stream128", "context128", "knowledge128"],
    ),
    (
        ("angle128 universe128 memory128 stream128 context128 knowledge128", 10),
        ["angle128", "universe128", "memory128", "stream128", "context128", "knowledge128"],
    ),
    (
        ("angle128 universe128 memory128 stream128 context128 knowledge128", 18),
        ["angle128", "universe128", "memory128", "stream128", "context128", "knowledge128"],
    ),
    (
        ("angle128 universe128 memory128 stream128 context128 knowledge128", 28),
        ["angle128 universe128", "memory128 stream128", "context128 knowledge128"],
    ),
    (
        ("universe128 memory128 stream128 context128 knowledge128 vector128", 6),
        ["universe128", "memory128", "stream128", "context128", "knowledge128", "vector128"],
    ),
    (
        ("universe128 memory128 stream128 context128 knowledge128 vector128", 10),
        ["universe128", "memory128", "stream128", "context128", "knowledge128", "vector128"],
    ),
    (
        ("universe128 memory128 stream128 context128 knowledge128 vector128", 18),
        ["universe128", "memory128", "stream128", "context128", "knowledge128", "vector128"],
    ),
    (
        ("universe128 memory128 stream128 context128 knowledge128 vector128", 28),
        ["universe128 memory128", "stream128 context128", "knowledge128 vector128"],
    ),
    (
        ("memory128 stream128 context128 knowledge128 vector128 processor128", 6),
        ["memory128", "stream128", "context128", "knowledge128", "vector128", "processor128"],
    ),
    (
        ("memory128 stream128 context128 knowledge128 vector128 processor128", 10),
        ["memory128", "stream128", "context128", "knowledge128", "vector128", "processor128"],
    ),
    (
        ("memory128 stream128 context128 knowledge128 vector128 processor128", 18),
        ["memory128", "stream128", "context128", "knowledge128", "vector128", "processor128"],
    ),
    (
        ("memory128 stream128 context128 knowledge128 vector128 processor128", 28),
        ["memory128 stream128", "context128 knowledge128", "vector128 processor128"],
    ),
    (
        ("stream128 context128 knowledge128 vector128 processor128 reasoning128", 6),
        ["stream128", "context128", "knowledge128", "vector128", "processor128", "reasoning128"],
    ),
    (
        ("stream128 context128 knowledge128 vector128 processor128 reasoning128", 10),
        ["stream128", "context128", "knowledge128", "vector128", "processor128", "reasoning128"],
    ),
    (
        ("stream128 context128 knowledge128 vector128 processor128 reasoning128", 18),
        ["stream128", "context128", "knowledge128", "vector128", "processor128", "reasoning128"],
    ),
    (
        ("stream128 context128 knowledge128 vector128 processor128 reasoning128", 28),
        ["stream128 context128", "knowledge128 vector128", "processor128 reasoning128"],
    ),
    (
        ("context128 knowledge128 vector128 processor128 reasoning128 machine128", 6),
        ["context128", "knowledge128", "vector128", "processor128", "reasoning128", "machine128"],
    ),
    (
        ("context128 knowledge128 vector128 processor128 reasoning128 machine128", 10),
        ["context128", "knowledge128", "vector128", "processor128", "reasoning128", "machine128"],
    ),
    (
        ("context128 knowledge128 vector128 processor128 reasoning128 machine128", 18),
        ["context128", "knowledge128", "vector128", "processor128", "reasoning128", "machine128"],
    ),
    (
        ("context128 knowledge128 vector128 processor128 reasoning128 machine128", 28),
        ["context128 knowledge128", "vector128 processor128", "reasoning128 machine128"],
    ),
    (
        ("knowledge128 vector128 processor128 reasoning128 machine128 learning128", 6),
        ["knowledge128", "vector128", "processor128", "reasoning128", "machine128", "learning128"],
    ),
    (
        ("knowledge128 vector128 processor128 reasoning128 machine128 learning128", 10),
        ["knowledge128", "vector128", "processor128", "reasoning128", "machine128", "learning128"],
    ),
    (
        ("knowledge128 vector128 processor128 reasoning128 machine128 learning128", 18),
        ["knowledge128", "vector128", "processor128", "reasoning128", "machine128", "learning128"],
    ),
    (
        ("knowledge128 vector128 processor128 reasoning128 machine128 learning128", 28),
        ["knowledge128 vector128", "processor128 reasoning128", "machine128 learning128"],
    ),
    (
        ("vector128 processor128 reasoning128 machine128 learning128 model128", 6),
        ["vector128", "processor128", "reasoning128", "machine128", "learning128", "model128"],
    ),
    (
        ("vector128 processor128 reasoning128 machine128 learning128 model128", 10),
        ["vector128", "processor128", "reasoning128", "machine128", "learning128", "model128"],
    ),
    (
        ("vector128 processor128 reasoning128 machine128 learning128 model128", 18),
        ["vector128", "processor128", "reasoning128", "machine128", "learning128", "model128"],
    ),
    (
        ("vector128 processor128 reasoning128 machine128 learning128 model128", 28),
        ["vector128 processor128", "reasoning128 machine128", "learning128 model128"],
    ),
    (
        ("processor128 reasoning128 machine128 learning128 model128 token128", 6),
        ["processor128", "reasoning128", "machine128", "learning128", "model128", "token128"],
    ),
    (
        ("processor128 reasoning128 machine128 learning128 model128 token128", 10),
        ["processor128", "reasoning128", "machine128", "learning128", "model128", "token128"],
    ),
    (
        ("processor128 reasoning128 machine128 learning128 model128 token128", 18),
        ["processor128", "reasoning128", "machine128", "learning128", "model128 token128"],
    ),
    (
        ("processor128 reasoning128 machine128 learning128 model128 token128", 28),
        ["processor128 reasoning128", "machine128 learning128", "model128 token128"],
    ),
    (
        ("reasoning128 machine128 learning128 model128 token128 prompt128", 6),
        ["reasoning128", "machine128", "learning128", "model128", "token128", "prompt128"],
    ),
    (
        ("reasoning128 machine128 learning128 model128 token128 prompt128", 10),
        ["reasoning128", "machine128", "learning128", "model128", "token128", "prompt128"],
    ),
    (
        ("reasoning128 machine128 learning128 model128 token128 prompt128", 18),
        ["reasoning128", "machine128", "learning128", "model128 token128", "prompt128"],
    ),
    (
        ("reasoning128 machine128 learning128 model128 token128 prompt128", 28),
        ["reasoning128 machine128", "learning128 model128", "token128 prompt128"],
    ),
    (
        ("machine128 learning128 model128 token128 prompt128 session128", 6),
        ["machine128", "learning128", "model128", "token128", "prompt128", "session128"],
    ),
    (
        ("machine128 learning128 model128 token128 prompt128 session128", 10),
        ["machine128", "learning128", "model128", "token128", "prompt128", "session128"],
    ),
    (
        ("machine128 learning128 model128 token128 prompt128 session128", 18),
        ["machine128", "learning128", "model128 token128", "prompt128", "session128"],
    ),
    (
        ("machine128 learning128 model128 token128 prompt128 session128", 28),
        ["machine128 learning128", "model128 token128 prompt128", "session128"],
    ),
    (
        ("learning128 model128 token128 prompt128 session128 library128", 6),
        ["learning128", "model128", "token128", "prompt128", "session128", "library128"],
    ),
    (
        ("learning128 model128 token128 prompt128 session128 library128", 10),
        ["learning128", "model128", "token128", "prompt128", "session128", "library128"],
    ),
    (
        ("learning128 model128 token128 prompt128 session128 library128", 18),
        ["learning128", "model128 token128", "prompt128", "session128", "library128"],
    ),
    (
        ("learning128 model128 token128 prompt128 session128 library128", 28),
        ["learning128 model128", "token128 prompt128", "session128 library128"],
    ),
    (
        ("model128 token128 prompt128 session128 library128 service128", 6),
        ["model128", "token128", "prompt128", "session128", "library128", "service128"],
    ),
    (
        ("model128 token128 prompt128 session128 library128 service128", 10),
        ["model128", "token128", "prompt128", "session128", "library128", "service128"],
    ),
    (
        ("model128 token128 prompt128 session128 library128 service128", 18),
        ["model128 token128", "prompt128", "session128", "library128", "service128"],
    ),
    (
        ("model128 token128 prompt128 session128 library128 service128", 28),
        ["model128 token128 prompt128", "session128 library128", "service128"],
    ),
    (
        ("token128 prompt128 session128 library128 service128 gateway128", 6),
        ["token128", "prompt128", "session128", "library128", "service128", "gateway128"],
    ),
    (
        ("token128 prompt128 session128 library128 service128 gateway128", 10),
        ["token128", "prompt128", "session128", "library128", "service128", "gateway128"],
    ),
    (
        ("token128 prompt128 session128 library128 service128 gateway128", 18),
        ["token128 prompt128", "session128", "library128", "service128", "gateway128"],
    ),
    (
        ("token128 prompt128 session128 library128 service128 gateway128", 28),
        ["token128 prompt128", "session128 library128", "service128 gateway128"],
    ),
    (
        ("prompt128 session128 library128 service128 gateway128 storage128", 6),
        ["prompt128", "session128", "library128", "service128", "gateway128", "storage128"],
    ),
    (
        ("prompt128 session128 library128 service128 gateway128 storage128", 10),
        ["prompt128", "session128", "library128", "service128", "gateway128", "storage128"],
    ),
    (
        ("prompt128 session128 library128 service128 gateway128 storage128", 18),
        ["prompt128", "session128", "library128", "service128", "gateway128", "storage128"],
    ),
    (
        ("prompt128 session128 library128 service128 gateway128 storage128", 28),
        ["prompt128 session128", "library128 service128", "gateway128 storage128"],
    ),
    (
        ("session128 library128 service128 gateway128 storage128 network128", 6),
        ["session128", "library128", "service128", "gateway128", "storage128", "network128"],
    ),
    (
        ("session128 library128 service128 gateway128 storage128 network128", 10),
        ["session128", "library128", "service128", "gateway128", "storage128", "network128"],
    ),
    (
        ("session128 library128 service128 gateway128 storage128 network128", 18),
        ["session128", "library128", "service128", "gateway128", "storage128", "network128"],
    ),
    (
        ("session128 library128 service128 gateway128 storage128 network128", 28),
        ["session128 library128", "service128 gateway128", "storage128 network128"],
    ),
    (
        ("library128 service128 gateway128 storage128 network128 latency128", 6),
        ["library128", "service128", "gateway128", "storage128", "network128", "latency128"],
    ),
    (
        ("library128 service128 gateway128 storage128 network128 latency128", 10),
        ["library128", "service128", "gateway128", "storage128", "network128", "latency128"],
    ),
    (
        ("library128 service128 gateway128 storage128 network128 latency128", 18),
        ["library128", "service128", "gateway128", "storage128", "network128", "latency128"],
    ),
    (
        ("library128 service128 gateway128 storage128 network128 latency128", 28),
        ["library128 service128", "gateway128 storage128", "network128 latency128"],
    ),
    (
        ("service128 gateway128 storage128 network128 latency128 buffer128", 6),
        ["service128", "gateway128", "storage128", "network128", "latency128", "buffer128"],
    ),
    (
        ("service128 gateway128 storage128 network128 latency128 buffer128", 10),
        ["service128", "gateway128", "storage128", "network128", "latency128", "buffer128"],
    ),
    (
        ("service128 gateway128 storage128 network128 latency128 buffer128", 18),
        ["service128", "gateway128", "storage128", "network128", "latency128", "buffer128"],
    ),
    (
        ("service128 gateway128 storage128 network128 latency128 buffer128", 28),
        ["service128 gateway128", "storage128 network128", "latency128 buffer128"],
    ),
    (
        ("gateway128 storage128 network128 latency128 buffer128 queue128", 6),
        ["gateway128", "storage128", "network128", "latency128", "buffer128", "queue128"],
    ),
    (
        ("gateway128 storage128 network128 latency128 buffer128 queue128", 10),
        ["gateway128", "storage128", "network128", "latency128", "buffer128", "queue128"],
    ),
    (
        ("gateway128 storage128 network128 latency128 buffer128 queue128", 18),
        ["gateway128", "storage128", "network128", "latency128", "buffer128 queue128"],
    ),
    (
        ("gateway128 storage128 network128 latency128 buffer128 queue128", 28),
        ["gateway128 storage128", "network128 latency128", "buffer128 queue128"],
    ),
    (
        ("storage128 network128 latency128 buffer128 queue128 worker128", 6),
        ["storage128", "network128", "latency128", "buffer128", "queue128", "worker128"],
    ),
    (
        ("storage128 network128 latency128 buffer128 queue128 worker128", 10),
        ["storage128", "network128", "latency128", "buffer128", "queue128", "worker128"],
    ),
    (
        ("storage128 network128 latency128 buffer128 queue128 worker128", 18),
        ["storage128", "network128", "latency128", "buffer128 queue128", "worker128"],
    ),
    (
        ("storage128 network128 latency128 buffer128 queue128 worker128", 28),
        ["storage128 network128", "latency128 buffer128", "queue128 worker128"],
    ),
    (
        ("network128 latency128 buffer128 queue128 worker128 kernel128", 6),
        ["network128", "latency128", "buffer128", "queue128", "worker128", "kernel128"],
    ),
    (
        ("network128 latency128 buffer128 queue128 worker128 kernel128", 10),
        ["network128", "latency128", "buffer128", "queue128", "worker128", "kernel128"],
    ),
    (
        ("network128 latency128 buffer128 queue128 worker128 kernel128", 18),
        ["network128", "latency128", "buffer128 queue128", "worker128", "kernel128"],
    ),
    (
        ("network128 latency128 buffer128 queue128 worker128 kernel128", 28),
        ["network128 latency128", "buffer128 queue128 worker128", "kernel128"],
    ),
    (
        ("latency128 buffer128 queue128 worker128 kernel128 signal128", 6),
        ["latency128", "buffer128", "queue128", "worker128", "kernel128", "signal128"],
    ),
    (
        ("latency128 buffer128 queue128 worker128 kernel128 signal128", 10),
        ["latency128", "buffer128", "queue128", "worker128", "kernel128", "signal128"],
    ),
    (
        ("latency128 buffer128 queue128 worker128 kernel128 signal128", 18),
        ["latency128", "buffer128 queue128", "worker128", "kernel128", "signal128"],
    ),
    (
        ("latency128 buffer128 queue128 worker128 kernel128 signal128", 28),
        ["latency128 buffer128", "queue128 worker128 kernel128", "signal128"],
    ),
    (
        ("buffer128 queue128 worker128 kernel128 signal128 packet128", 6),
        ["buffer128", "queue128", "worker128", "kernel128", "signal128", "packet128"],
    ),
    (
        ("buffer128 queue128 worker128 kernel128 signal128 packet128", 10),
        ["buffer128", "queue128", "worker128", "kernel128", "signal128", "packet128"],
    ),
    (
        ("buffer128 queue128 worker128 kernel128 signal128 packet128", 18),
        ["buffer128 queue128", "worker128", "kernel128", "signal128", "packet128"],
    ),
    (
        ("buffer128 queue128 worker128 kernel128 signal128 packet128", 28),
        ["buffer128 queue128 worker128", "kernel128 signal128", "packet128"],
    ),
    (
        ("queue128 worker128 kernel128 signal128 packet128 router128", 6),
        ["queue128", "worker128", "kernel128", "signal128", "packet128", "router128"],
    ),
    (
        ("queue128 worker128 kernel128 signal128 packet128 router128", 10),
        ["queue128", "worker128", "kernel128", "signal128", "packet128", "router128"],
    ),
    (
        ("queue128 worker128 kernel128 signal128 packet128 router128", 18),
        ["queue128 worker128", "kernel128", "signal128", "packet128", "router128"],
    ),
    (
        ("queue128 worker128 kernel128 signal128 packet128 router128", 28),
        ["queue128 worker128 kernel128", "signal128 packet128", "router128"],
    ),
    (
        ("worker128 kernel128 signal128 packet128 router128 cluster128", 6),
        ["worker128", "kernel128", "signal128", "packet128", "router128", "cluster128"],
    ),
    (
        ("worker128 kernel128 signal128 packet128 router128 cluster128", 10),
        ["worker128", "kernel128", "signal128", "packet128", "router128", "cluster128"],
    ),
    (
        ("worker128 kernel128 signal128 packet128 router128 cluster128", 18),
        ["worker128", "kernel128", "signal128", "packet128", "router128", "cluster128"],
    ),
    (
        ("worker128 kernel128 signal128 packet128 router128 cluster128", 28),
        ["worker128 kernel128", "signal128 packet128", "router128 cluster128"],
    ),
    (
        ("kernel128 signal128 packet128 router128 cluster128 mirror128", 6),
        ["kernel128", "signal128", "packet128", "router128", "cluster128", "mirror128"],
    ),
    (
        ("kernel128 signal128 packet128 router128 cluster128 mirror128", 10),
        ["kernel128", "signal128", "packet128", "router128", "cluster128", "mirror128"],
    ),
    (
        ("kernel128 signal128 packet128 router128 cluster128 mirror128", 18),
        ["kernel128", "signal128", "packet128", "router128", "cluster128", "mirror128"],
    ),
    (
        ("kernel128 signal128 packet128 router128 cluster128 mirror128", 28),
        ["kernel128 signal128", "packet128 router128", "cluster128 mirror128"],
    ),
    (
        ("signal128 packet128 router128 cluster128 mirror128 filter128", 6),
        ["signal128", "packet128", "router128", "cluster128", "mirror128", "filter128"],
    ),
    (
        ("signal128 packet128 router128 cluster128 mirror128 filter128", 10),
        ["signal128", "packet128", "router128", "cluster128", "mirror128", "filter128"],
    ),
    (
        ("signal128 packet128 router128 cluster128 mirror128 filter128", 18),
        ["signal128", "packet128", "router128", "cluster128", "mirror128", "filter128"],
    ),
    (
        ("signal128 packet128 router128 cluster128 mirror128 filter128", 28),
        ["signal128 packet128", "router128 cluster128", "mirror128 filter128"],
    ),
    (
        ("packet128 router128 cluster128 mirror128 filter128 ranking128", 6),
        ["packet128", "router128", "cluster128", "mirror128", "filter128", "ranking128"],
    ),
    (
        ("packet128 router128 cluster128 mirror128 filter128 ranking128", 10),
        ["packet128", "router128", "cluster128", "mirror128", "filter128", "ranking128"],
    ),
    (
        ("packet128 router128 cluster128 mirror128 filter128 ranking128", 18),
        ["packet128", "router128", "cluster128", "mirror128", "filter128", "ranking128"],
    ),
    (
        ("packet128 router128 cluster128 mirror128 filter128 ranking128", 28),
        ["packet128 router128", "cluster128 mirror128", "filter128 ranking128"],
    ),
    (
        ("router128 cluster128 mirror128 filter128 ranking128 encoding128", 6),
        ["router128", "cluster128", "mirror128", "filter128", "ranking128", "encoding128"],
    ),
    (
        ("router128 cluster128 mirror128 filter128 ranking128 encoding128", 10),
        ["router128", "cluster128", "mirror128", "filter128", "ranking128", "encoding128"],
    ),
    (
        ("router128 cluster128 mirror128 filter128 ranking128 encoding128", 18),
        ["router128", "cluster128", "mirror128", "filter128", "ranking128", "encoding128"],
    ),
    (
        ("router128 cluster128 mirror128 filter128 ranking128 encoding128", 28),
        ["router128 cluster128", "mirror128 filter128", "ranking128 encoding128"],
    ),
    (
        ("cluster128 mirror128 filter128 ranking128 encoding128 mapping128", 6),
        ["cluster128", "mirror128", "filter128", "ranking128", "encoding128", "mapping128"],
    ),
    (
        ("cluster128 mirror128 filter128 ranking128 encoding128 mapping128", 10),
        ["cluster128", "mirror128", "filter128", "ranking128", "encoding128", "mapping128"],
    ),
    (
        ("cluster128 mirror128 filter128 ranking128 encoding128 mapping128", 18),
        ["cluster128", "mirror128", "filter128", "ranking128", "encoding128", "mapping128"],
    ),
    (
        ("cluster128 mirror128 filter128 ranking128 encoding128 mapping128", 28),
        ["cluster128 mirror128", "filter128 ranking128", "encoding128 mapping128"],
    ),
    (
        ("mirror128 filter128 ranking128 encoding128 mapping128 record128", 6),
        ["mirror128", "filter128", "ranking128", "encoding128", "mapping128", "record128"],
    ),
    (
        ("mirror128 filter128 ranking128 encoding128 mapping128 record128", 10),
        ["mirror128", "filter128", "ranking128", "encoding128", "mapping128", "record128"],
    ),
    (
        ("mirror128 filter128 ranking128 encoding128 mapping128 record128", 18),
        ["mirror128", "filter128", "ranking128", "encoding128", "mapping128", "record128"],
    ),
    (
        ("mirror128 filter128 ranking128 encoding128 mapping128 record128", 28),
        ["mirror128 filter128", "ranking128 encoding128", "mapping128 record128"],
    ),
    (
        ("filter128 ranking128 encoding128 mapping128 record128 candle128", 6),
        ["filter128", "ranking128", "encoding128", "mapping128", "record128", "candle128"],
    ),
    (
        ("filter128 ranking128 encoding128 mapping128 record128 candle128", 10),
        ["filter128", "ranking128", "encoding128", "mapping128", "record128", "candle128"],
    ),
    (
        ("filter128 ranking128 encoding128 mapping128 record128 candle128", 18),
        ["filter128", "ranking128", "encoding128", "mapping128", "record128", "candle128"],
    ),
    (
        ("filter128 ranking128 encoding128 mapping128 record128 candle128", 28),
        ["filter128 ranking128", "encoding128 mapping128", "record128 candle128"],
    ),
    (
        ("ranking128 encoding128 mapping128 record128 candle128 thread128", 6),
        ["ranking128", "encoding128", "mapping128", "record128", "candle128", "thread128"],
    ),
    (
        ("ranking128 encoding128 mapping128 record128 candle128 thread128", 10),
        ["ranking128", "encoding128", "mapping128", "record128", "candle128", "thread128"],
    ),
    (
        ("ranking128 encoding128 mapping128 record128 candle128 thread128", 18),
        ["ranking128", "encoding128", "mapping128", "record128", "candle128", "thread128"],
    ),
    (
        ("ranking128 encoding128 mapping128 record128 candle128 thread128", 28),
        ["ranking128 encoding128", "mapping128 record128", "candle128 thread128"],
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
