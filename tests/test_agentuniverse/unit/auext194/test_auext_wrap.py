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
        ("round 194: the quick brown fox jumps over the lazy dog", 4),
        ["round", "194:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", 8),
        ["round", "194: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", 12),
        ["round 194:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", 16),
        ["round 194: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", 24),
        ["round 194: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 194: the quick brown fox jumps over the lazy dog", 32),
        ["round 194: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", 4),
        ["round", "194:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", 8),
        ["round", "194:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", 12),
        ["round 194:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", 16),
        ["round 194:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", 24),
        ["round 194: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 194: agentuniverse is a framework for multi agents", 32),
        ["round 194: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", 4),
        ["round", "194:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", 8),
        ["round", "194:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", 12),
        ["round 194:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", 16),
        ["round 194:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", 24),
        ["round 194: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 194: knowledge stored as vectors enables retrieval", 32),
        ["round 194: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 194: the processor reads the record then stops", 4),
        ["round", "194:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 194: the processor reads the record then stops", 8),
        ["round", "194: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 194: the processor reads the record then stops", 12),
        ["round 194:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 194: the processor reads the record then stops", 16),
        ["round 194: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 194: the processor reads the record then stops", 24),
        ["round 194: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 194: the processor reads the record then stops", 32),
        ["round 194: the processor reads", "the record then stops"],
    ),
    (
        ("round 194: a worker pulls the next task from the queue", 4),
        ["round", "194:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 194: a worker pulls the next task from the queue", 8),
        ["round", "194: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 194: a worker pulls the next task from the queue", 12),
        ["round 194: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 194: a worker pulls the next task from the queue", 16),
        ["round 194: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 194: a worker pulls the next task from the queue", 24),
        ["round 194: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 194: a worker pulls the next task from the queue", 32),
        ["round 194: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 194: signals travel through the network layer", 4),
        ["round", "194:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 194: signals travel through the network layer", 8),
        ["round", "194:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 194: signals travel through the network layer", 12),
        ["round 194:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 194: signals travel through the network layer", 16),
        ["round 194:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 194: signals travel through the network layer", 24),
        ["round 194: signals", "travel through the", "network layer"],
    ),
    (
        ("round 194: signals travel through the network layer", 32),
        ["round 194: signals travel", "through the network layer"],
    ),
    (
        ("round 194: the gateway routes each request by policy", 4),
        ["round", "194:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 194: the gateway routes each request by policy", 8),
        ["round", "194: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 194: the gateway routes each request by policy", 12),
        ["round 194:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 194: the gateway routes each request by policy", 16),
        ["round 194: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 194: the gateway routes each request by policy", 24),
        ["round 194: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 194: the gateway routes each request by policy", 32),
        ["round 194: the gateway routes", "each request by policy"],
    ),
    (
        ("round 194: memory grows until the buffer is full", 4),
        ["round", "194:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 194: memory grows until the buffer is full", 8),
        ["round", "194:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 194: memory grows until the buffer is full", 12),
        ["round 194:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 194: memory grows until the buffer is full", 16),
        ["round 194:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 194: memory grows until the buffer is full", 24), ["round 194: memory grows", "until the buffer is full"]),
    (("round 194: memory grows until the buffer is full", 32), ["round 194: memory grows until", "the buffer is full"]),
    (
        ("round 194: the cluster mirrors every packet twice", 4),
        ["round", "194:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 194: the cluster mirrors every packet twice", 8),
        ["round", "194: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 194: the cluster mirrors every packet twice", 12),
        ["round 194:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 194: the cluster mirrors every packet twice", 16),
        ["round 194: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 194: the cluster mirrors every packet twice", 24),
        ["round 194: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 194: the cluster mirrors every packet twice", 32),
        ["round 194: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", 4),
        ["round", "194:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", 8),
        ["round", "194:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", 12),
        ["round 194:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", 16),
        ["round 194:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", 24),
        ["round 194: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 194: ranking uses tokens learned from the corpus", 32),
        ["round 194: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 194: a long session ends when the candle dies", 4),
        ["round", "194:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 194: a long session ends when the candle dies", 8),
        ["round", "194: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 194: a long session ends when the candle dies", 12),
        ["round 194: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 194: a long session ends when the candle dies", 16),
        ["round 194: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 194: a long session ends when the candle dies", 24),
        ["round 194: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 194: a long session ends when the candle dies", 32),
        ["round 194: a long session ends", "when the candle dies"],
    ),
    (
        ("round 194: encode the prompt then map the result", 4),
        ["round", "194:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 194: encode the prompt then map the result", 8),
        ["round", "194:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 194: encode the prompt then map the result", 12),
        ["round 194:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 194: encode the prompt then map the result", 16),
        ["round 194:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 194: encode the prompt then map the result", 24),
        ["round 194: encode the", "prompt then map the", "result"],
    ),
    (("round 194: encode the prompt then map the result", 32), ["round 194: encode the prompt", "then map the result"]),
    (
        ("round 194: the kernel wakes the worker at dawn", 4),
        ["round", "194:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 194: the kernel wakes the worker at dawn", 8),
        ["round", "194: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 194: the kernel wakes the worker at dawn", 12),
        ["round 194:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 194: the kernel wakes the worker at dawn", 16), ["round 194: the", "kernel wakes the", "worker at dawn"]),
    (("round 194: the kernel wakes the worker at dawn", 24), ["round 194: the kernel", "wakes the worker at dawn"]),
    (("round 194: the kernel wakes the worker at dawn", 32), ["round 194: the kernel wakes the", "worker at dawn"]),
    (
        ("round 194: service latency drops after the patch", 4),
        ["round", "194:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 194: service latency drops after the patch", 8),
        ["round", "194:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 194: service latency drops after the patch", 12),
        ["round 194:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 194: service latency drops after the patch", 16),
        ["round 194:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 194: service latency drops after the patch", 24),
        ["round 194: service", "latency drops after the", "patch"],
    ),
    (("round 194: service latency drops after the patch", 32), ["round 194: service latency drops", "after the patch"]),
    (
        ("round 194: the library caches every vector it sees", 4),
        ["round", "194:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 194: the library caches every vector it sees", 8),
        ["round", "194: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 194: the library caches every vector it sees", 12),
        ["round 194:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 194: the library caches every vector it sees", 16),
        ["round 194: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 194: the library caches every vector it sees", 24),
        ["round 194: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 194: the library caches every vector it sees", 32),
        ["round 194: the library caches", "every vector it sees"],
    ),
    (
        ("round 194: agents argue then the debate resolves", 4),
        ["round", "194:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 194: agents argue then the debate resolves", 8),
        ["round", "194:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 194: agents argue then the debate resolves", 12),
        ["round 194:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 194: agents argue then the debate resolves", 16),
        ["round 194:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 194: agents argue then the debate resolves", 24), ["round 194: agents argue", "then the debate resolves"]),
    (("round 194: agents argue then the debate resolves", 32), ["round 194: agents argue then the", "debate resolves"]),
    (
        ("round 194: the filter keeps only strong matches", 4),
        ["round", "194:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 194: the filter keeps only strong matches", 8),
        ["round", "194: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 194: the filter keeps only strong matches", 12),
        ["round 194:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 194: the filter keeps only strong matches", 16),
        ["round 194: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 194: the filter keeps only strong matches", 24),
        ["round 194: the filter", "keeps only strong", "matches"],
    ),
    (("round 194: the filter keeps only strong matches", 32), ["round 194: the filter keeps only", "strong matches"]),
    (
        ("round 194: the model answers with a short reply", 4),
        ["round", "194:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 194: the model answers with a short reply", 8),
        ["round", "194: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 194: the model answers with a short reply", 12),
        ["round 194:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 194: the model answers with a short reply", 16),
        ["round 194: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 194: the model answers with a short reply", 24),
        ["round 194: the model", "answers with a short", "reply"],
    ),
    (("round 194: the model answers with a short reply", 32), ["round 194: the model answers", "with a short reply"]),
    (
        ("round 194: the recorder stores the reasoning trace", 4),
        ["round", "194:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 194: the recorder stores the reasoning trace", 8),
        ["round", "194: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 194: the recorder stores the reasoning trace", 12),
        ["round 194:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 194: the recorder stores the reasoning trace", 16),
        ["round 194: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 194: the recorder stores the reasoning trace", 24),
        ["round 194: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 194: the recorder stores the reasoning trace", 32),
        ["round 194: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 194: the angel watches the processor run", 4),
        ["round", "194:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 194: the angel watches the processor run", 8),
        ["round", "194: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 194: the angel watches the processor run", 12),
        ["round 194:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 194: the angel watches the processor run", 16),
        ["round 194: the", "angel watches", "the processor", "run"],
    ),
    (("round 194: the angel watches the processor run", 24), ["round 194: the angel", "watches the processor", "run"]),
    (("round 194: the angel watches the processor run", 32), ["round 194: the angel watches the", "processor run"]),
    (
        ("round 194: angle of the vector decides the match", 4),
        ["round", "194:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 194: angle of the vector decides the match", 8),
        ["round", "194:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 194: angle of the vector decides the match", 12),
        ["round 194:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 194: angle of the vector decides the match", 16),
        ["round 194: angle", "of the vector", "decides the", "match"],
    ),
    (("round 194: angle of the vector decides the match", 24), ["round 194: angle of the", "vector decides the match"]),
    (("round 194: angle of the vector decides the match", 32), ["round 194: angle of the vector", "decides the match"]),
    (
        ("round 194: the candle burns twice as long at night", 4),
        ["round", "194:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 194: the candle burns twice as long at night", 8),
        ["round", "194: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 194: the candle burns twice as long at night", 12),
        ["round 194:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 194: the candle burns twice as long at night", 16),
        ["round 194: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 194: the candle burns twice as long at night", 24),
        ["round 194: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 194: the candle burns twice as long at night", 32),
        ["round 194: the candle burns", "twice as long at night"],
    ),
    (
        ("round 194: a mirror of the universe in one line", 4),
        ["round", "194:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 194: a mirror of the universe in one line", 8),
        ["round", "194: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 194: a mirror of the universe in one line", 12),
        ["round 194: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 194: a mirror of the universe in one line", 16),
        ["round 194: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 194: a mirror of the universe in one line", 24), ["round 194: a mirror of", "the universe in one line"]),
    (("round 194: a mirror of the universe in one line", 32), ["round 194: a mirror of the", "universe in one line"]),
    (
        ("round 194: the queue drains before the storm", 4),
        ["round", "194:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 194: the queue drains before the storm", 8),
        ["round", "194: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 194: the queue drains before the storm", 12),
        ["round 194:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 194: the queue drains before the storm", 16), ["round 194: the", "queue drains", "before the storm"]),
    (("round 194: the queue drains before the storm", 24), ["round 194: the queue", "drains before the storm"]),
    (("round 194: the queue drains before the storm", 32), ["round 194: the queue drains", "before the storm"]),
    (
        ("kitten194 sitting194 agent194 angle194 universe194 memory194", 6),
        ["kitten194", "sitting194", "agent194", "angle194", "universe194", "memory194"],
    ),
    (
        ("kitten194 sitting194 agent194 angle194 universe194 memory194", 10),
        ["kitten194", "sitting194", "agent194", "angle194", "universe194", "memory194"],
    ),
    (
        ("kitten194 sitting194 agent194 angle194 universe194 memory194", 18),
        ["kitten194", "sitting194", "agent194 angle194", "universe194", "memory194"],
    ),
    (
        ("kitten194 sitting194 agent194 angle194 universe194 memory194", 28),
        ["kitten194 sitting194", "agent194 angle194", "universe194 memory194"],
    ),
    (
        ("sitting194 agent194 angle194 universe194 memory194 stream194", 6),
        ["sitting194", "agent194", "angle194", "universe194", "memory194", "stream194"],
    ),
    (
        ("sitting194 agent194 angle194 universe194 memory194 stream194", 10),
        ["sitting194", "agent194", "angle194", "universe194", "memory194", "stream194"],
    ),
    (
        ("sitting194 agent194 angle194 universe194 memory194 stream194", 18),
        ["sitting194", "agent194 angle194", "universe194", "memory194", "stream194"],
    ),
    (
        ("sitting194 agent194 angle194 universe194 memory194 stream194", 28),
        ["sitting194 agent194 angle194", "universe194 memory194", "stream194"],
    ),
    (
        ("agent194 angle194 universe194 memory194 stream194 context194", 6),
        ["agent194", "angle194", "universe194", "memory194", "stream194", "context194"],
    ),
    (
        ("agent194 angle194 universe194 memory194 stream194 context194", 10),
        ["agent194", "angle194", "universe194", "memory194", "stream194", "context194"],
    ),
    (
        ("agent194 angle194 universe194 memory194 stream194 context194", 18),
        ["agent194 angle194", "universe194", "memory194", "stream194", "context194"],
    ),
    (
        ("agent194 angle194 universe194 memory194 stream194 context194", 28),
        ["agent194 angle194", "universe194 memory194", "stream194 context194"],
    ),
    (
        ("angle194 universe194 memory194 stream194 context194 knowledge194", 6),
        ["angle194", "universe194", "memory194", "stream194", "context194", "knowledge194"],
    ),
    (
        ("angle194 universe194 memory194 stream194 context194 knowledge194", 10),
        ["angle194", "universe194", "memory194", "stream194", "context194", "knowledge194"],
    ),
    (
        ("angle194 universe194 memory194 stream194 context194 knowledge194", 18),
        ["angle194", "universe194", "memory194", "stream194", "context194", "knowledge194"],
    ),
    (
        ("angle194 universe194 memory194 stream194 context194 knowledge194", 28),
        ["angle194 universe194", "memory194 stream194", "context194 knowledge194"],
    ),
    (
        ("universe194 memory194 stream194 context194 knowledge194 vector194", 6),
        ["universe194", "memory194", "stream194", "context194", "knowledge194", "vector194"],
    ),
    (
        ("universe194 memory194 stream194 context194 knowledge194 vector194", 10),
        ["universe194", "memory194", "stream194", "context194", "knowledge194", "vector194"],
    ),
    (
        ("universe194 memory194 stream194 context194 knowledge194 vector194", 18),
        ["universe194", "memory194", "stream194", "context194", "knowledge194", "vector194"],
    ),
    (
        ("universe194 memory194 stream194 context194 knowledge194 vector194", 28),
        ["universe194 memory194", "stream194 context194", "knowledge194 vector194"],
    ),
    (
        ("memory194 stream194 context194 knowledge194 vector194 processor194", 6),
        ["memory194", "stream194", "context194", "knowledge194", "vector194", "processor194"],
    ),
    (
        ("memory194 stream194 context194 knowledge194 vector194 processor194", 10),
        ["memory194", "stream194", "context194", "knowledge194", "vector194", "processor194"],
    ),
    (
        ("memory194 stream194 context194 knowledge194 vector194 processor194", 18),
        ["memory194", "stream194", "context194", "knowledge194", "vector194", "processor194"],
    ),
    (
        ("memory194 stream194 context194 knowledge194 vector194 processor194", 28),
        ["memory194 stream194", "context194 knowledge194", "vector194 processor194"],
    ),
    (
        ("stream194 context194 knowledge194 vector194 processor194 reasoning194", 6),
        ["stream194", "context194", "knowledge194", "vector194", "processor194", "reasoning194"],
    ),
    (
        ("stream194 context194 knowledge194 vector194 processor194 reasoning194", 10),
        ["stream194", "context194", "knowledge194", "vector194", "processor194", "reasoning194"],
    ),
    (
        ("stream194 context194 knowledge194 vector194 processor194 reasoning194", 18),
        ["stream194", "context194", "knowledge194", "vector194", "processor194", "reasoning194"],
    ),
    (
        ("stream194 context194 knowledge194 vector194 processor194 reasoning194", 28),
        ["stream194 context194", "knowledge194 vector194", "processor194 reasoning194"],
    ),
    (
        ("context194 knowledge194 vector194 processor194 reasoning194 machine194", 6),
        ["context194", "knowledge194", "vector194", "processor194", "reasoning194", "machine194"],
    ),
    (
        ("context194 knowledge194 vector194 processor194 reasoning194 machine194", 10),
        ["context194", "knowledge194", "vector194", "processor194", "reasoning194", "machine194"],
    ),
    (
        ("context194 knowledge194 vector194 processor194 reasoning194 machine194", 18),
        ["context194", "knowledge194", "vector194", "processor194", "reasoning194", "machine194"],
    ),
    (
        ("context194 knowledge194 vector194 processor194 reasoning194 machine194", 28),
        ["context194 knowledge194", "vector194 processor194", "reasoning194 machine194"],
    ),
    (
        ("knowledge194 vector194 processor194 reasoning194 machine194 learning194", 6),
        ["knowledge194", "vector194", "processor194", "reasoning194", "machine194", "learning194"],
    ),
    (
        ("knowledge194 vector194 processor194 reasoning194 machine194 learning194", 10),
        ["knowledge194", "vector194", "processor194", "reasoning194", "machine194", "learning194"],
    ),
    (
        ("knowledge194 vector194 processor194 reasoning194 machine194 learning194", 18),
        ["knowledge194", "vector194", "processor194", "reasoning194", "machine194", "learning194"],
    ),
    (
        ("knowledge194 vector194 processor194 reasoning194 machine194 learning194", 28),
        ["knowledge194 vector194", "processor194 reasoning194", "machine194 learning194"],
    ),
    (
        ("vector194 processor194 reasoning194 machine194 learning194 model194", 6),
        ["vector194", "processor194", "reasoning194", "machine194", "learning194", "model194"],
    ),
    (
        ("vector194 processor194 reasoning194 machine194 learning194 model194", 10),
        ["vector194", "processor194", "reasoning194", "machine194", "learning194", "model194"],
    ),
    (
        ("vector194 processor194 reasoning194 machine194 learning194 model194", 18),
        ["vector194", "processor194", "reasoning194", "machine194", "learning194", "model194"],
    ),
    (
        ("vector194 processor194 reasoning194 machine194 learning194 model194", 28),
        ["vector194 processor194", "reasoning194 machine194", "learning194 model194"],
    ),
    (
        ("processor194 reasoning194 machine194 learning194 model194 token194", 6),
        ["processor194", "reasoning194", "machine194", "learning194", "model194", "token194"],
    ),
    (
        ("processor194 reasoning194 machine194 learning194 model194 token194", 10),
        ["processor194", "reasoning194", "machine194", "learning194", "model194", "token194"],
    ),
    (
        ("processor194 reasoning194 machine194 learning194 model194 token194", 18),
        ["processor194", "reasoning194", "machine194", "learning194", "model194 token194"],
    ),
    (
        ("processor194 reasoning194 machine194 learning194 model194 token194", 28),
        ["processor194 reasoning194", "machine194 learning194", "model194 token194"],
    ),
    (
        ("reasoning194 machine194 learning194 model194 token194 prompt194", 6),
        ["reasoning194", "machine194", "learning194", "model194", "token194", "prompt194"],
    ),
    (
        ("reasoning194 machine194 learning194 model194 token194 prompt194", 10),
        ["reasoning194", "machine194", "learning194", "model194", "token194", "prompt194"],
    ),
    (
        ("reasoning194 machine194 learning194 model194 token194 prompt194", 18),
        ["reasoning194", "machine194", "learning194", "model194 token194", "prompt194"],
    ),
    (
        ("reasoning194 machine194 learning194 model194 token194 prompt194", 28),
        ["reasoning194 machine194", "learning194 model194", "token194 prompt194"],
    ),
    (
        ("machine194 learning194 model194 token194 prompt194 session194", 6),
        ["machine194", "learning194", "model194", "token194", "prompt194", "session194"],
    ),
    (
        ("machine194 learning194 model194 token194 prompt194 session194", 10),
        ["machine194", "learning194", "model194", "token194", "prompt194", "session194"],
    ),
    (
        ("machine194 learning194 model194 token194 prompt194 session194", 18),
        ["machine194", "learning194", "model194 token194", "prompt194", "session194"],
    ),
    (
        ("machine194 learning194 model194 token194 prompt194 session194", 28),
        ["machine194 learning194", "model194 token194 prompt194", "session194"],
    ),
    (
        ("learning194 model194 token194 prompt194 session194 library194", 6),
        ["learning194", "model194", "token194", "prompt194", "session194", "library194"],
    ),
    (
        ("learning194 model194 token194 prompt194 session194 library194", 10),
        ["learning194", "model194", "token194", "prompt194", "session194", "library194"],
    ),
    (
        ("learning194 model194 token194 prompt194 session194 library194", 18),
        ["learning194", "model194 token194", "prompt194", "session194", "library194"],
    ),
    (
        ("learning194 model194 token194 prompt194 session194 library194", 28),
        ["learning194 model194", "token194 prompt194", "session194 library194"],
    ),
    (
        ("model194 token194 prompt194 session194 library194 service194", 6),
        ["model194", "token194", "prompt194", "session194", "library194", "service194"],
    ),
    (
        ("model194 token194 prompt194 session194 library194 service194", 10),
        ["model194", "token194", "prompt194", "session194", "library194", "service194"],
    ),
    (
        ("model194 token194 prompt194 session194 library194 service194", 18),
        ["model194 token194", "prompt194", "session194", "library194", "service194"],
    ),
    (
        ("model194 token194 prompt194 session194 library194 service194", 28),
        ["model194 token194 prompt194", "session194 library194", "service194"],
    ),
    (
        ("token194 prompt194 session194 library194 service194 gateway194", 6),
        ["token194", "prompt194", "session194", "library194", "service194", "gateway194"],
    ),
    (
        ("token194 prompt194 session194 library194 service194 gateway194", 10),
        ["token194", "prompt194", "session194", "library194", "service194", "gateway194"],
    ),
    (
        ("token194 prompt194 session194 library194 service194 gateway194", 18),
        ["token194 prompt194", "session194", "library194", "service194", "gateway194"],
    ),
    (
        ("token194 prompt194 session194 library194 service194 gateway194", 28),
        ["token194 prompt194", "session194 library194", "service194 gateway194"],
    ),
    (
        ("prompt194 session194 library194 service194 gateway194 storage194", 6),
        ["prompt194", "session194", "library194", "service194", "gateway194", "storage194"],
    ),
    (
        ("prompt194 session194 library194 service194 gateway194 storage194", 10),
        ["prompt194", "session194", "library194", "service194", "gateway194", "storage194"],
    ),
    (
        ("prompt194 session194 library194 service194 gateway194 storage194", 18),
        ["prompt194", "session194", "library194", "service194", "gateway194", "storage194"],
    ),
    (
        ("prompt194 session194 library194 service194 gateway194 storage194", 28),
        ["prompt194 session194", "library194 service194", "gateway194 storage194"],
    ),
    (
        ("session194 library194 service194 gateway194 storage194 network194", 6),
        ["session194", "library194", "service194", "gateway194", "storage194", "network194"],
    ),
    (
        ("session194 library194 service194 gateway194 storage194 network194", 10),
        ["session194", "library194", "service194", "gateway194", "storage194", "network194"],
    ),
    (
        ("session194 library194 service194 gateway194 storage194 network194", 18),
        ["session194", "library194", "service194", "gateway194", "storage194", "network194"],
    ),
    (
        ("session194 library194 service194 gateway194 storage194 network194", 28),
        ["session194 library194", "service194 gateway194", "storage194 network194"],
    ),
    (
        ("library194 service194 gateway194 storage194 network194 latency194", 6),
        ["library194", "service194", "gateway194", "storage194", "network194", "latency194"],
    ),
    (
        ("library194 service194 gateway194 storage194 network194 latency194", 10),
        ["library194", "service194", "gateway194", "storage194", "network194", "latency194"],
    ),
    (
        ("library194 service194 gateway194 storage194 network194 latency194", 18),
        ["library194", "service194", "gateway194", "storage194", "network194", "latency194"],
    ),
    (
        ("library194 service194 gateway194 storage194 network194 latency194", 28),
        ["library194 service194", "gateway194 storage194", "network194 latency194"],
    ),
    (
        ("service194 gateway194 storage194 network194 latency194 buffer194", 6),
        ["service194", "gateway194", "storage194", "network194", "latency194", "buffer194"],
    ),
    (
        ("service194 gateway194 storage194 network194 latency194 buffer194", 10),
        ["service194", "gateway194", "storage194", "network194", "latency194", "buffer194"],
    ),
    (
        ("service194 gateway194 storage194 network194 latency194 buffer194", 18),
        ["service194", "gateway194", "storage194", "network194", "latency194", "buffer194"],
    ),
    (
        ("service194 gateway194 storage194 network194 latency194 buffer194", 28),
        ["service194 gateway194", "storage194 network194", "latency194 buffer194"],
    ),
    (
        ("gateway194 storage194 network194 latency194 buffer194 queue194", 6),
        ["gateway194", "storage194", "network194", "latency194", "buffer194", "queue194"],
    ),
    (
        ("gateway194 storage194 network194 latency194 buffer194 queue194", 10),
        ["gateway194", "storage194", "network194", "latency194", "buffer194", "queue194"],
    ),
    (
        ("gateway194 storage194 network194 latency194 buffer194 queue194", 18),
        ["gateway194", "storage194", "network194", "latency194", "buffer194 queue194"],
    ),
    (
        ("gateway194 storage194 network194 latency194 buffer194 queue194", 28),
        ["gateway194 storage194", "network194 latency194", "buffer194 queue194"],
    ),
    (
        ("storage194 network194 latency194 buffer194 queue194 worker194", 6),
        ["storage194", "network194", "latency194", "buffer194", "queue194", "worker194"],
    ),
    (
        ("storage194 network194 latency194 buffer194 queue194 worker194", 10),
        ["storage194", "network194", "latency194", "buffer194", "queue194", "worker194"],
    ),
    (
        ("storage194 network194 latency194 buffer194 queue194 worker194", 18),
        ["storage194", "network194", "latency194", "buffer194 queue194", "worker194"],
    ),
    (
        ("storage194 network194 latency194 buffer194 queue194 worker194", 28),
        ["storage194 network194", "latency194 buffer194", "queue194 worker194"],
    ),
    (
        ("network194 latency194 buffer194 queue194 worker194 kernel194", 6),
        ["network194", "latency194", "buffer194", "queue194", "worker194", "kernel194"],
    ),
    (
        ("network194 latency194 buffer194 queue194 worker194 kernel194", 10),
        ["network194", "latency194", "buffer194", "queue194", "worker194", "kernel194"],
    ),
    (
        ("network194 latency194 buffer194 queue194 worker194 kernel194", 18),
        ["network194", "latency194", "buffer194 queue194", "worker194", "kernel194"],
    ),
    (
        ("network194 latency194 buffer194 queue194 worker194 kernel194", 28),
        ["network194 latency194", "buffer194 queue194 worker194", "kernel194"],
    ),
    (
        ("latency194 buffer194 queue194 worker194 kernel194 signal194", 6),
        ["latency194", "buffer194", "queue194", "worker194", "kernel194", "signal194"],
    ),
    (
        ("latency194 buffer194 queue194 worker194 kernel194 signal194", 10),
        ["latency194", "buffer194", "queue194", "worker194", "kernel194", "signal194"],
    ),
    (
        ("latency194 buffer194 queue194 worker194 kernel194 signal194", 18),
        ["latency194", "buffer194 queue194", "worker194", "kernel194", "signal194"],
    ),
    (
        ("latency194 buffer194 queue194 worker194 kernel194 signal194", 28),
        ["latency194 buffer194", "queue194 worker194 kernel194", "signal194"],
    ),
    (
        ("buffer194 queue194 worker194 kernel194 signal194 packet194", 6),
        ["buffer194", "queue194", "worker194", "kernel194", "signal194", "packet194"],
    ),
    (
        ("buffer194 queue194 worker194 kernel194 signal194 packet194", 10),
        ["buffer194", "queue194", "worker194", "kernel194", "signal194", "packet194"],
    ),
    (
        ("buffer194 queue194 worker194 kernel194 signal194 packet194", 18),
        ["buffer194 queue194", "worker194", "kernel194", "signal194", "packet194"],
    ),
    (
        ("buffer194 queue194 worker194 kernel194 signal194 packet194", 28),
        ["buffer194 queue194 worker194", "kernel194 signal194", "packet194"],
    ),
    (
        ("queue194 worker194 kernel194 signal194 packet194 router194", 6),
        ["queue194", "worker194", "kernel194", "signal194", "packet194", "router194"],
    ),
    (
        ("queue194 worker194 kernel194 signal194 packet194 router194", 10),
        ["queue194", "worker194", "kernel194", "signal194", "packet194", "router194"],
    ),
    (
        ("queue194 worker194 kernel194 signal194 packet194 router194", 18),
        ["queue194 worker194", "kernel194", "signal194", "packet194", "router194"],
    ),
    (
        ("queue194 worker194 kernel194 signal194 packet194 router194", 28),
        ["queue194 worker194 kernel194", "signal194 packet194", "router194"],
    ),
    (
        ("worker194 kernel194 signal194 packet194 router194 cluster194", 6),
        ["worker194", "kernel194", "signal194", "packet194", "router194", "cluster194"],
    ),
    (
        ("worker194 kernel194 signal194 packet194 router194 cluster194", 10),
        ["worker194", "kernel194", "signal194", "packet194", "router194", "cluster194"],
    ),
    (
        ("worker194 kernel194 signal194 packet194 router194 cluster194", 18),
        ["worker194", "kernel194", "signal194", "packet194", "router194", "cluster194"],
    ),
    (
        ("worker194 kernel194 signal194 packet194 router194 cluster194", 28),
        ["worker194 kernel194", "signal194 packet194", "router194 cluster194"],
    ),
    (
        ("kernel194 signal194 packet194 router194 cluster194 mirror194", 6),
        ["kernel194", "signal194", "packet194", "router194", "cluster194", "mirror194"],
    ),
    (
        ("kernel194 signal194 packet194 router194 cluster194 mirror194", 10),
        ["kernel194", "signal194", "packet194", "router194", "cluster194", "mirror194"],
    ),
    (
        ("kernel194 signal194 packet194 router194 cluster194 mirror194", 18),
        ["kernel194", "signal194", "packet194", "router194", "cluster194", "mirror194"],
    ),
    (
        ("kernel194 signal194 packet194 router194 cluster194 mirror194", 28),
        ["kernel194 signal194", "packet194 router194", "cluster194 mirror194"],
    ),
    (
        ("signal194 packet194 router194 cluster194 mirror194 filter194", 6),
        ["signal194", "packet194", "router194", "cluster194", "mirror194", "filter194"],
    ),
    (
        ("signal194 packet194 router194 cluster194 mirror194 filter194", 10),
        ["signal194", "packet194", "router194", "cluster194", "mirror194", "filter194"],
    ),
    (
        ("signal194 packet194 router194 cluster194 mirror194 filter194", 18),
        ["signal194", "packet194", "router194", "cluster194", "mirror194", "filter194"],
    ),
    (
        ("signal194 packet194 router194 cluster194 mirror194 filter194", 28),
        ["signal194 packet194", "router194 cluster194", "mirror194 filter194"],
    ),
    (
        ("packet194 router194 cluster194 mirror194 filter194 ranking194", 6),
        ["packet194", "router194", "cluster194", "mirror194", "filter194", "ranking194"],
    ),
    (
        ("packet194 router194 cluster194 mirror194 filter194 ranking194", 10),
        ["packet194", "router194", "cluster194", "mirror194", "filter194", "ranking194"],
    ),
    (
        ("packet194 router194 cluster194 mirror194 filter194 ranking194", 18),
        ["packet194", "router194", "cluster194", "mirror194", "filter194", "ranking194"],
    ),
    (
        ("packet194 router194 cluster194 mirror194 filter194 ranking194", 28),
        ["packet194 router194", "cluster194 mirror194", "filter194 ranking194"],
    ),
    (
        ("router194 cluster194 mirror194 filter194 ranking194 encoding194", 6),
        ["router194", "cluster194", "mirror194", "filter194", "ranking194", "encoding194"],
    ),
    (
        ("router194 cluster194 mirror194 filter194 ranking194 encoding194", 10),
        ["router194", "cluster194", "mirror194", "filter194", "ranking194", "encoding194"],
    ),
    (
        ("router194 cluster194 mirror194 filter194 ranking194 encoding194", 18),
        ["router194", "cluster194", "mirror194", "filter194", "ranking194", "encoding194"],
    ),
    (
        ("router194 cluster194 mirror194 filter194 ranking194 encoding194", 28),
        ["router194 cluster194", "mirror194 filter194", "ranking194 encoding194"],
    ),
    (
        ("cluster194 mirror194 filter194 ranking194 encoding194 mapping194", 6),
        ["cluster194", "mirror194", "filter194", "ranking194", "encoding194", "mapping194"],
    ),
    (
        ("cluster194 mirror194 filter194 ranking194 encoding194 mapping194", 10),
        ["cluster194", "mirror194", "filter194", "ranking194", "encoding194", "mapping194"],
    ),
    (
        ("cluster194 mirror194 filter194 ranking194 encoding194 mapping194", 18),
        ["cluster194", "mirror194", "filter194", "ranking194", "encoding194", "mapping194"],
    ),
    (
        ("cluster194 mirror194 filter194 ranking194 encoding194 mapping194", 28),
        ["cluster194 mirror194", "filter194 ranking194", "encoding194 mapping194"],
    ),
    (
        ("mirror194 filter194 ranking194 encoding194 mapping194 record194", 6),
        ["mirror194", "filter194", "ranking194", "encoding194", "mapping194", "record194"],
    ),
    (
        ("mirror194 filter194 ranking194 encoding194 mapping194 record194", 10),
        ["mirror194", "filter194", "ranking194", "encoding194", "mapping194", "record194"],
    ),
    (
        ("mirror194 filter194 ranking194 encoding194 mapping194 record194", 18),
        ["mirror194", "filter194", "ranking194", "encoding194", "mapping194", "record194"],
    ),
    (
        ("mirror194 filter194 ranking194 encoding194 mapping194 record194", 28),
        ["mirror194 filter194", "ranking194 encoding194", "mapping194 record194"],
    ),
    (
        ("filter194 ranking194 encoding194 mapping194 record194 candle194", 6),
        ["filter194", "ranking194", "encoding194", "mapping194", "record194", "candle194"],
    ),
    (
        ("filter194 ranking194 encoding194 mapping194 record194 candle194", 10),
        ["filter194", "ranking194", "encoding194", "mapping194", "record194", "candle194"],
    ),
    (
        ("filter194 ranking194 encoding194 mapping194 record194 candle194", 18),
        ["filter194", "ranking194", "encoding194", "mapping194", "record194", "candle194"],
    ),
    (
        ("filter194 ranking194 encoding194 mapping194 record194 candle194", 28),
        ["filter194 ranking194", "encoding194 mapping194", "record194 candle194"],
    ),
    (
        ("ranking194 encoding194 mapping194 record194 candle194 thread194", 6),
        ["ranking194", "encoding194", "mapping194", "record194", "candle194", "thread194"],
    ),
    (
        ("ranking194 encoding194 mapping194 record194 candle194 thread194", 10),
        ["ranking194", "encoding194", "mapping194", "record194", "candle194", "thread194"],
    ),
    (
        ("ranking194 encoding194 mapping194 record194 candle194 thread194", 18),
        ["ranking194", "encoding194", "mapping194", "record194", "candle194", "thread194"],
    ),
    (
        ("ranking194 encoding194 mapping194 record194 candle194 thread194", 28),
        ["ranking194 encoding194", "mapping194 record194", "candle194 thread194"],
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
