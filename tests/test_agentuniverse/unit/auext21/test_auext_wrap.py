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
        ("round 21: the quick brown fox jumps over the lazy dog", 4),
        ["round", "21:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 21: the quick brown fox jumps over the lazy dog", 8),
        ["round", "21: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 21: the quick brown fox jumps over the lazy dog", 12),
        ["round 21:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 21: the quick brown fox jumps over the lazy dog", 16),
        ["round 21: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 21: the quick brown fox jumps over the lazy dog", 24),
        ["round 21: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 21: the quick brown fox jumps over the lazy dog", 32),
        ["round 21: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 21: agentuniverse is a framework for multi agents", 4),
        ["round", "21:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 21: agentuniverse is a framework for multi agents", 8),
        ["round", "21:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 21: agentuniverse is a framework for multi agents", 12),
        ["round 21:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 21: agentuniverse is a framework for multi agents", 16),
        ["round 21:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 21: agentuniverse is a framework for multi agents", 24),
        ["round 21: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 21: agentuniverse is a framework for multi agents", 32),
        ["round 21: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 21: knowledge stored as vectors enables retrieval", 4),
        ["round", "21:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 21: knowledge stored as vectors enables retrieval", 8),
        ["round", "21:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 21: knowledge stored as vectors enables retrieval", 12),
        ["round 21:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 21: knowledge stored as vectors enables retrieval", 16),
        ["round 21:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 21: knowledge stored as vectors enables retrieval", 24),
        ["round 21: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 21: knowledge stored as vectors enables retrieval", 32),
        ["round 21: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 21: the processor reads the record then stops", 4),
        ["round", "21:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 21: the processor reads the record then stops", 8),
        ["round", "21: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 21: the processor reads the record then stops", 12),
        ["round 21:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 21: the processor reads the record then stops", 16),
        ["round 21: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 21: the processor reads the record then stops", 24),
        ["round 21: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 21: the processor reads the record then stops", 32),
        ["round 21: the processor reads", "the record then stops"],
    ),
    (
        ("round 21: a worker pulls the next task from the queue", 4),
        ["round", "21:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 21: a worker pulls the next task from the queue", 8),
        ["round", "21: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 21: a worker pulls the next task from the queue", 12),
        ["round 21: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 21: a worker pulls the next task from the queue", 16),
        ["round 21: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 21: a worker pulls the next task from the queue", 24),
        ["round 21: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 21: a worker pulls the next task from the queue", 32),
        ["round 21: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 21: signals travel through the network layer", 4),
        ["round", "21:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 21: signals travel through the network layer", 8),
        ["round", "21:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 21: signals travel through the network layer", 12),
        ["round 21:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 21: signals travel through the network layer", 16),
        ["round 21:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 21: signals travel through the network layer", 24),
        ["round 21: signals travel", "through the network", "layer"],
    ),
    (
        ("round 21: signals travel through the network layer", 32),
        ["round 21: signals travel through", "the network layer"],
    ),
    (
        ("round 21: the gateway routes each request by policy", 4),
        ["round", "21:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 21: the gateway routes each request by policy", 8),
        ["round", "21: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 21: the gateway routes each request by policy", 12),
        ["round 21:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 21: the gateway routes each request by policy", 16),
        ["round 21: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 21: the gateway routes each request by policy", 24),
        ["round 21: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 21: the gateway routes each request by policy", 32),
        ["round 21: the gateway routes", "each request by policy"],
    ),
    (
        ("round 21: memory grows until the buffer is full", 4),
        ["round", "21:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 21: memory grows until the buffer is full", 8),
        ["round", "21:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 21: memory grows until the buffer is full", 12),
        ["round 21:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 21: memory grows until the buffer is full", 16),
        ["round 21: memory", "grows until the", "buffer is full"],
    ),
    (("round 21: memory grows until the buffer is full", 24), ["round 21: memory grows", "until the buffer is full"]),
    (("round 21: memory grows until the buffer is full", 32), ["round 21: memory grows until the", "buffer is full"]),
    (
        ("round 21: the cluster mirrors every packet twice", 4),
        ["round", "21:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 21: the cluster mirrors every packet twice", 8),
        ["round", "21: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 21: the cluster mirrors every packet twice", 12),
        ["round 21:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 21: the cluster mirrors every packet twice", 16),
        ["round 21: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 21: the cluster mirrors every packet twice", 24),
        ["round 21: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 21: the cluster mirrors every packet twice", 32), ["round 21: the cluster mirrors", "every packet twice"]),
    (
        ("round 21: ranking uses tokens learned from the corpus", 4),
        ["round", "21:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 21: ranking uses tokens learned from the corpus", 8),
        ["round", "21:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 21: ranking uses tokens learned from the corpus", 12),
        ["round 21:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 21: ranking uses tokens learned from the corpus", 16),
        ["round 21:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 21: ranking uses tokens learned from the corpus", 24),
        ["round 21: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 21: ranking uses tokens learned from the corpus", 32),
        ["round 21: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 21: a long session ends when the candle dies", 4),
        ["round", "21:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 21: a long session ends when the candle dies", 8),
        ["round", "21: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 21: a long session ends when the candle dies", 12),
        ["round 21: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 21: a long session ends when the candle dies", 16),
        ["round 21: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 21: a long session ends when the candle dies", 24),
        ["round 21: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 21: a long session ends when the candle dies", 32),
        ["round 21: a long session ends", "when the candle dies"],
    ),
    (
        ("round 21: encode the prompt then map the result", 4),
        ["round", "21:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 21: encode the prompt then map the result", 8),
        ["round", "21:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 21: encode the prompt then map the result", 12),
        ["round 21:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 21: encode the prompt then map the result", 16),
        ["round 21: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 21: encode the prompt then map the result", 24),
        ["round 21: encode the", "prompt then map the", "result"],
    ),
    (("round 21: encode the prompt then map the result", 32), ["round 21: encode the prompt then", "map the result"]),
    (
        ("round 21: the kernel wakes the worker at dawn", 4),
        ["round", "21:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 21: the kernel wakes the worker at dawn", 8),
        ["round", "21: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 21: the kernel wakes the worker at dawn", 12),
        ["round 21:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 21: the kernel wakes the worker at dawn", 16), ["round 21: the", "kernel wakes the", "worker at dawn"]),
    (("round 21: the kernel wakes the worker at dawn", 24), ["round 21: the kernel", "wakes the worker at dawn"]),
    (("round 21: the kernel wakes the worker at dawn", 32), ["round 21: the kernel wakes the", "worker at dawn"]),
    (
        ("round 21: service latency drops after the patch", 4),
        ["round", "21:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 21: service latency drops after the patch", 8),
        ["round", "21:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 21: service latency drops after the patch", 12),
        ["round 21:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 21: service latency drops after the patch", 16),
        ["round 21:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 21: service latency drops after the patch", 24),
        ["round 21: service", "latency drops after the", "patch"],
    ),
    (("round 21: service latency drops after the patch", 32), ["round 21: service latency drops", "after the patch"]),
    (
        ("round 21: the library caches every vector it sees", 4),
        ["round", "21:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 21: the library caches every vector it sees", 8),
        ["round", "21: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 21: the library caches every vector it sees", 12),
        ["round 21:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 21: the library caches every vector it sees", 16),
        ["round 21: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 21: the library caches every vector it sees", 24),
        ["round 21: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 21: the library caches every vector it sees", 32),
        ["round 21: the library caches", "every vector it sees"],
    ),
    (
        ("round 21: agents argue then the debate resolves", 4),
        ["round", "21:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 21: agents argue then the debate resolves", 8),
        ["round", "21:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 21: agents argue then the debate resolves", 12),
        ["round 21:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 21: agents argue then the debate resolves", 16),
        ["round 21: agents", "argue then the", "debate resolves"],
    ),
    (("round 21: agents argue then the debate resolves", 24), ["round 21: agents argue", "then the debate resolves"]),
    (("round 21: agents argue then the debate resolves", 32), ["round 21: agents argue then the", "debate resolves"]),
    (
        ("round 21: the filter keeps only strong matches", 4),
        ["round", "21:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 21: the filter keeps only strong matches", 8),
        ["round", "21: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 21: the filter keeps only strong matches", 12),
        ["round 21:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 21: the filter keeps only strong matches", 16),
        ["round 21: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 21: the filter keeps only strong matches", 24), ["round 21: the filter", "keeps only strong", "matches"]),
    (("round 21: the filter keeps only strong matches", 32), ["round 21: the filter keeps only", "strong matches"]),
    (
        ("round 21: the model answers with a short reply", 4),
        ["round", "21:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 21: the model answers with a short reply", 8),
        ["round", "21: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 21: the model answers with a short reply", 12),
        ["round 21:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 21: the model answers with a short reply", 16),
        ["round 21: the", "model answers", "with a short", "reply"],
    ),
    (("round 21: the model answers with a short reply", 24), ["round 21: the model", "answers with a short", "reply"]),
    (("round 21: the model answers with a short reply", 32), ["round 21: the model answers with", "a short reply"]),
    (
        ("round 21: the recorder stores the reasoning trace", 4),
        ["round", "21:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 21: the recorder stores the reasoning trace", 8),
        ["round", "21: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 21: the recorder stores the reasoning trace", 12),
        ["round 21:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 21: the recorder stores the reasoning trace", 16),
        ["round 21: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 21: the recorder stores the reasoning trace", 24),
        ["round 21: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 21: the recorder stores the reasoning trace", 32),
        ["round 21: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 21: the angel watches the processor run", 4),
        ["round", "21:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 21: the angel watches the processor run", 8),
        ["round", "21: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 21: the angel watches the processor run", 12),
        ["round 21:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 21: the angel watches the processor run", 16), ["round 21: the", "angel watches", "the processor", "run"]),
    (("round 21: the angel watches the processor run", 24), ["round 21: the angel", "watches the processor", "run"]),
    (("round 21: the angel watches the processor run", 32), ["round 21: the angel watches the", "processor run"]),
    (
        ("round 21: angle of the vector decides the match", 4),
        ["round", "21:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 21: angle of the vector decides the match", 8),
        ["round", "21:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 21: angle of the vector decides the match", 12),
        ["round 21:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 21: angle of the vector decides the match", 16),
        ["round 21: angle", "of the vector", "decides the", "match"],
    ),
    (("round 21: angle of the vector decides the match", 24), ["round 21: angle of the", "vector decides the match"]),
    (("round 21: angle of the vector decides the match", 32), ["round 21: angle of the vector", "decides the match"]),
    (
        ("round 21: the candle burns twice as long at night", 4),
        ["round", "21:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 21: the candle burns twice as long at night", 8),
        ["round", "21: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 21: the candle burns twice as long at night", 12),
        ["round 21:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 21: the candle burns twice as long at night", 16),
        ["round 21: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 21: the candle burns twice as long at night", 24),
        ["round 21: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 21: the candle burns twice as long at night", 32),
        ["round 21: the candle burns twice", "as long at night"],
    ),
    (
        ("round 21: a mirror of the universe in one line", 4),
        ["round", "21:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 21: a mirror of the universe in one line", 8),
        ["round", "21: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 21: a mirror of the universe in one line", 12),
        ["round 21: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 21: a mirror of the universe in one line", 16),
        ["round 21: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 21: a mirror of the universe in one line", 24), ["round 21: a mirror of", "the universe in one line"]),
    (("round 21: a mirror of the universe in one line", 32), ["round 21: a mirror of the", "universe in one line"]),
    (
        ("round 21: the queue drains before the storm", 4),
        ["round", "21:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 21: the queue drains before the storm", 8),
        ["round", "21: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 21: the queue drains before the storm", 12), ["round 21:", "the queue", "drains", "before the", "storm"]),
    (("round 21: the queue drains before the storm", 16), ["round 21: the", "queue drains", "before the storm"]),
    (("round 21: the queue drains before the storm", 24), ["round 21: the queue", "drains before the storm"]),
    (("round 21: the queue drains before the storm", 32), ["round 21: the queue drains", "before the storm"]),
    (
        ("kitten21 sitting21 agent21 angle21 universe21 memory21", 6),
        ["kitten21", "sitting21", "agent21", "angle21", "universe21", "memory21"],
    ),
    (
        ("kitten21 sitting21 agent21 angle21 universe21 memory21", 10),
        ["kitten21", "sitting21", "agent21", "angle21", "universe21", "memory21"],
    ),
    (
        ("kitten21 sitting21 agent21 angle21 universe21 memory21", 18),
        ["kitten21 sitting21", "agent21 angle21", "universe21", "memory21"],
    ),
    (
        ("kitten21 sitting21 agent21 angle21 universe21 memory21", 28),
        ["kitten21 sitting21 agent21", "angle21 universe21 memory21"],
    ),
    (
        ("sitting21 agent21 angle21 universe21 memory21 stream21", 6),
        ["sitting21", "agent21", "angle21", "universe21", "memory21", "stream21"],
    ),
    (
        ("sitting21 agent21 angle21 universe21 memory21 stream21", 10),
        ["sitting21", "agent21", "angle21", "universe21", "memory21", "stream21"],
    ),
    (
        ("sitting21 agent21 angle21 universe21 memory21 stream21", 18),
        ["sitting21 agent21", "angle21 universe21", "memory21 stream21"],
    ),
    (
        ("sitting21 agent21 angle21 universe21 memory21 stream21", 28),
        ["sitting21 agent21 angle21", "universe21 memory21 stream21"],
    ),
    (
        ("agent21 angle21 universe21 memory21 stream21 context21", 6),
        ["agent21", "angle21", "universe21", "memory21", "stream21", "context21"],
    ),
    (
        ("agent21 angle21 universe21 memory21 stream21 context21", 10),
        ["agent21", "angle21", "universe21", "memory21", "stream21", "context21"],
    ),
    (
        ("agent21 angle21 universe21 memory21 stream21 context21", 18),
        ["agent21 angle21", "universe21", "memory21 stream21", "context21"],
    ),
    (
        ("agent21 angle21 universe21 memory21 stream21 context21", 28),
        ["agent21 angle21 universe21", "memory21 stream21 context21"],
    ),
    (
        ("angle21 universe21 memory21 stream21 context21 knowledge21", 6),
        ["angle21", "universe21", "memory21", "stream21", "context21", "knowledge21"],
    ),
    (
        ("angle21 universe21 memory21 stream21 context21 knowledge21", 10),
        ["angle21", "universe21", "memory21", "stream21", "context21", "knowledge21"],
    ),
    (
        ("angle21 universe21 memory21 stream21 context21 knowledge21", 18),
        ["angle21 universe21", "memory21 stream21", "context21", "knowledge21"],
    ),
    (
        ("angle21 universe21 memory21 stream21 context21 knowledge21", 28),
        ["angle21 universe21 memory21", "stream21 context21", "knowledge21"],
    ),
    (
        ("universe21 memory21 stream21 context21 knowledge21 vector21", 6),
        ["universe21", "memory21", "stream21", "context21", "knowledge21", "vector21"],
    ),
    (
        ("universe21 memory21 stream21 context21 knowledge21 vector21", 10),
        ["universe21", "memory21", "stream21", "context21", "knowledge21", "vector21"],
    ),
    (
        ("universe21 memory21 stream21 context21 knowledge21 vector21", 18),
        ["universe21", "memory21 stream21", "context21", "knowledge21", "vector21"],
    ),
    (
        ("universe21 memory21 stream21 context21 knowledge21 vector21", 28),
        ["universe21 memory21 stream21", "context21 knowledge21", "vector21"],
    ),
    (
        ("memory21 stream21 context21 knowledge21 vector21 processor21", 6),
        ["memory21", "stream21", "context21", "knowledge21", "vector21", "processor21"],
    ),
    (
        ("memory21 stream21 context21 knowledge21 vector21 processor21", 10),
        ["memory21", "stream21", "context21", "knowledge21", "vector21", "processor21"],
    ),
    (
        ("memory21 stream21 context21 knowledge21 vector21 processor21", 18),
        ["memory21 stream21", "context21", "knowledge21", "vector21", "processor21"],
    ),
    (
        ("memory21 stream21 context21 knowledge21 vector21 processor21", 28),
        ["memory21 stream21 context21", "knowledge21 vector21", "processor21"],
    ),
    (
        ("stream21 context21 knowledge21 vector21 processor21 reasoning21", 6),
        ["stream21", "context21", "knowledge21", "vector21", "processor21", "reasoning21"],
    ),
    (
        ("stream21 context21 knowledge21 vector21 processor21 reasoning21", 10),
        ["stream21", "context21", "knowledge21", "vector21", "processor21", "reasoning21"],
    ),
    (
        ("stream21 context21 knowledge21 vector21 processor21 reasoning21", 18),
        ["stream21 context21", "knowledge21", "vector21", "processor21", "reasoning21"],
    ),
    (
        ("stream21 context21 knowledge21 vector21 processor21 reasoning21", 28),
        ["stream21 context21", "knowledge21 vector21", "processor21 reasoning21"],
    ),
    (
        ("context21 knowledge21 vector21 processor21 reasoning21 machine21", 6),
        ["context21", "knowledge21", "vector21", "processor21", "reasoning21", "machine21"],
    ),
    (
        ("context21 knowledge21 vector21 processor21 reasoning21 machine21", 10),
        ["context21", "knowledge21", "vector21", "processor21", "reasoning21", "machine21"],
    ),
    (
        ("context21 knowledge21 vector21 processor21 reasoning21 machine21", 18),
        ["context21", "knowledge21", "vector21", "processor21", "reasoning21", "machine21"],
    ),
    (
        ("context21 knowledge21 vector21 processor21 reasoning21 machine21", 28),
        ["context21 knowledge21", "vector21 processor21", "reasoning21 machine21"],
    ),
    (
        ("knowledge21 vector21 processor21 reasoning21 machine21 learning21", 6),
        ["knowledge21", "vector21", "processor21", "reasoning21", "machine21", "learning21"],
    ),
    (
        ("knowledge21 vector21 processor21 reasoning21 machine21 learning21", 10),
        ["knowledge21", "vector21", "processor21", "reasoning21", "machine21", "learning21"],
    ),
    (
        ("knowledge21 vector21 processor21 reasoning21 machine21 learning21", 18),
        ["knowledge21", "vector21", "processor21", "reasoning21", "machine21", "learning21"],
    ),
    (
        ("knowledge21 vector21 processor21 reasoning21 machine21 learning21", 28),
        ["knowledge21 vector21", "processor21 reasoning21", "machine21 learning21"],
    ),
    (
        ("vector21 processor21 reasoning21 machine21 learning21 model21", 6),
        ["vector21", "processor21", "reasoning21", "machine21", "learning21", "model21"],
    ),
    (
        ("vector21 processor21 reasoning21 machine21 learning21 model21", 10),
        ["vector21", "processor21", "reasoning21", "machine21", "learning21", "model21"],
    ),
    (
        ("vector21 processor21 reasoning21 machine21 learning21 model21", 18),
        ["vector21", "processor21", "reasoning21", "machine21", "learning21 model21"],
    ),
    (
        ("vector21 processor21 reasoning21 machine21 learning21 model21", 28),
        ["vector21 processor21", "reasoning21 machine21", "learning21 model21"],
    ),
    (
        ("processor21 reasoning21 machine21 learning21 model21 token21", 6),
        ["processor21", "reasoning21", "machine21", "learning21", "model21", "token21"],
    ),
    (
        ("processor21 reasoning21 machine21 learning21 model21 token21", 10),
        ["processor21", "reasoning21", "machine21", "learning21", "model21", "token21"],
    ),
    (
        ("processor21 reasoning21 machine21 learning21 model21 token21", 18),
        ["processor21", "reasoning21", "machine21", "learning21 model21", "token21"],
    ),
    (
        ("processor21 reasoning21 machine21 learning21 model21 token21", 28),
        ["processor21 reasoning21", "machine21 learning21 model21", "token21"],
    ),
    (
        ("reasoning21 machine21 learning21 model21 token21 prompt21", 6),
        ["reasoning21", "machine21", "learning21", "model21", "token21", "prompt21"],
    ),
    (
        ("reasoning21 machine21 learning21 model21 token21 prompt21", 10),
        ["reasoning21", "machine21", "learning21", "model21", "token21", "prompt21"],
    ),
    (
        ("reasoning21 machine21 learning21 model21 token21 prompt21", 18),
        ["reasoning21", "machine21", "learning21 model21", "token21 prompt21"],
    ),
    (
        ("reasoning21 machine21 learning21 model21 token21 prompt21", 28),
        ["reasoning21 machine21", "learning21 model21 token21", "prompt21"],
    ),
    (
        ("machine21 learning21 model21 token21 prompt21 session21", 6),
        ["machine21", "learning21", "model21", "token21", "prompt21", "session21"],
    ),
    (
        ("machine21 learning21 model21 token21 prompt21 session21", 10),
        ["machine21", "learning21", "model21", "token21", "prompt21", "session21"],
    ),
    (
        ("machine21 learning21 model21 token21 prompt21 session21", 18),
        ["machine21", "learning21 model21", "token21 prompt21", "session21"],
    ),
    (
        ("machine21 learning21 model21 token21 prompt21 session21", 28),
        ["machine21 learning21 model21", "token21 prompt21 session21"],
    ),
    (
        ("learning21 model21 token21 prompt21 session21 library21", 6),
        ["learning21", "model21", "token21", "prompt21", "session21", "library21"],
    ),
    (
        ("learning21 model21 token21 prompt21 session21 library21", 10),
        ["learning21", "model21", "token21", "prompt21", "session21", "library21"],
    ),
    (
        ("learning21 model21 token21 prompt21 session21 library21", 18),
        ["learning21 model21", "token21 prompt21", "session21", "library21"],
    ),
    (
        ("learning21 model21 token21 prompt21 session21 library21", 28),
        ["learning21 model21 token21", "prompt21 session21 library21"],
    ),
    (
        ("model21 token21 prompt21 session21 library21 service21", 6),
        ["model21", "token21", "prompt21", "session21", "library21", "service21"],
    ),
    (
        ("model21 token21 prompt21 session21 library21 service21", 10),
        ["model21", "token21", "prompt21", "session21", "library21", "service21"],
    ),
    (
        ("model21 token21 prompt21 session21 library21 service21", 18),
        ["model21 token21", "prompt21 session21", "library21", "service21"],
    ),
    (
        ("model21 token21 prompt21 session21 library21 service21", 28),
        ["model21 token21 prompt21", "session21 library21", "service21"],
    ),
    (
        ("token21 prompt21 session21 library21 service21 gateway21", 6),
        ["token21", "prompt21", "session21", "library21", "service21", "gateway21"],
    ),
    (
        ("token21 prompt21 session21 library21 service21 gateway21", 10),
        ["token21", "prompt21", "session21", "library21", "service21", "gateway21"],
    ),
    (
        ("token21 prompt21 session21 library21 service21 gateway21", 18),
        ["token21 prompt21", "session21", "library21", "service21", "gateway21"],
    ),
    (
        ("token21 prompt21 session21 library21 service21 gateway21", 28),
        ["token21 prompt21 session21", "library21 service21", "gateway21"],
    ),
    (
        ("prompt21 session21 library21 service21 gateway21 storage21", 6),
        ["prompt21", "session21", "library21", "service21", "gateway21", "storage21"],
    ),
    (
        ("prompt21 session21 library21 service21 gateway21 storage21", 10),
        ["prompt21", "session21", "library21", "service21", "gateway21", "storage21"],
    ),
    (
        ("prompt21 session21 library21 service21 gateway21 storage21", 18),
        ["prompt21 session21", "library21", "service21", "gateway21", "storage21"],
    ),
    (
        ("prompt21 session21 library21 service21 gateway21 storage21", 28),
        ["prompt21 session21 library21", "service21 gateway21", "storage21"],
    ),
    (
        ("session21 library21 service21 gateway21 storage21 network21", 6),
        ["session21", "library21", "service21", "gateway21", "storage21", "network21"],
    ),
    (
        ("session21 library21 service21 gateway21 storage21 network21", 10),
        ["session21", "library21", "service21", "gateway21", "storage21", "network21"],
    ),
    (
        ("session21 library21 service21 gateway21 storage21 network21", 18),
        ["session21", "library21", "service21", "gateway21", "storage21", "network21"],
    ),
    (
        ("session21 library21 service21 gateway21 storage21 network21", 28),
        ["session21 library21", "service21 gateway21", "storage21 network21"],
    ),
    (
        ("library21 service21 gateway21 storage21 network21 latency21", 6),
        ["library21", "service21", "gateway21", "storage21", "network21", "latency21"],
    ),
    (
        ("library21 service21 gateway21 storage21 network21 latency21", 10),
        ["library21", "service21", "gateway21", "storage21", "network21", "latency21"],
    ),
    (
        ("library21 service21 gateway21 storage21 network21 latency21", 18),
        ["library21", "service21", "gateway21", "storage21", "network21", "latency21"],
    ),
    (
        ("library21 service21 gateway21 storage21 network21 latency21", 28),
        ["library21 service21", "gateway21 storage21", "network21 latency21"],
    ),
    (
        ("service21 gateway21 storage21 network21 latency21 buffer21", 6),
        ["service21", "gateway21", "storage21", "network21", "latency21", "buffer21"],
    ),
    (
        ("service21 gateway21 storage21 network21 latency21 buffer21", 10),
        ["service21", "gateway21", "storage21", "network21", "latency21", "buffer21"],
    ),
    (
        ("service21 gateway21 storage21 network21 latency21 buffer21", 18),
        ["service21", "gateway21", "storage21", "network21", "latency21 buffer21"],
    ),
    (
        ("service21 gateway21 storage21 network21 latency21 buffer21", 28),
        ["service21 gateway21", "storage21 network21", "latency21 buffer21"],
    ),
    (
        ("gateway21 storage21 network21 latency21 buffer21 queue21", 6),
        ["gateway21", "storage21", "network21", "latency21", "buffer21", "queue21"],
    ),
    (
        ("gateway21 storage21 network21 latency21 buffer21 queue21", 10),
        ["gateway21", "storage21", "network21", "latency21", "buffer21", "queue21"],
    ),
    (
        ("gateway21 storage21 network21 latency21 buffer21 queue21", 18),
        ["gateway21", "storage21", "network21", "latency21 buffer21", "queue21"],
    ),
    (
        ("gateway21 storage21 network21 latency21 buffer21 queue21", 28),
        ["gateway21 storage21", "network21 latency21 buffer21", "queue21"],
    ),
    (
        ("storage21 network21 latency21 buffer21 queue21 worker21", 6),
        ["storage21", "network21", "latency21", "buffer21", "queue21", "worker21"],
    ),
    (
        ("storage21 network21 latency21 buffer21 queue21 worker21", 10),
        ["storage21", "network21", "latency21", "buffer21", "queue21", "worker21"],
    ),
    (
        ("storage21 network21 latency21 buffer21 queue21 worker21", 18),
        ["storage21", "network21", "latency21 buffer21", "queue21 worker21"],
    ),
    (
        ("storage21 network21 latency21 buffer21 queue21 worker21", 28),
        ["storage21 network21", "latency21 buffer21 queue21", "worker21"],
    ),
    (
        ("network21 latency21 buffer21 queue21 worker21 kernel21", 6),
        ["network21", "latency21", "buffer21", "queue21", "worker21", "kernel21"],
    ),
    (
        ("network21 latency21 buffer21 queue21 worker21 kernel21", 10),
        ["network21", "latency21", "buffer21", "queue21", "worker21", "kernel21"],
    ),
    (
        ("network21 latency21 buffer21 queue21 worker21 kernel21", 18),
        ["network21", "latency21 buffer21", "queue21 worker21", "kernel21"],
    ),
    (
        ("network21 latency21 buffer21 queue21 worker21 kernel21", 28),
        ["network21 latency21 buffer21", "queue21 worker21 kernel21"],
    ),
    (
        ("latency21 buffer21 queue21 worker21 kernel21 signal21", 6),
        ["latency21", "buffer21", "queue21", "worker21", "kernel21", "signal21"],
    ),
    (
        ("latency21 buffer21 queue21 worker21 kernel21 signal21", 10),
        ["latency21", "buffer21", "queue21", "worker21", "kernel21", "signal21"],
    ),
    (
        ("latency21 buffer21 queue21 worker21 kernel21 signal21", 18),
        ["latency21 buffer21", "queue21 worker21", "kernel21 signal21"],
    ),
    (
        ("latency21 buffer21 queue21 worker21 kernel21 signal21", 28),
        ["latency21 buffer21 queue21", "worker21 kernel21 signal21"],
    ),
    (
        ("buffer21 queue21 worker21 kernel21 signal21 packet21", 6),
        ["buffer21", "queue21", "worker21", "kernel21", "signal21", "packet21"],
    ),
    (
        ("buffer21 queue21 worker21 kernel21 signal21 packet21", 10),
        ["buffer21", "queue21", "worker21", "kernel21", "signal21", "packet21"],
    ),
    (
        ("buffer21 queue21 worker21 kernel21 signal21 packet21", 18),
        ["buffer21 queue21", "worker21 kernel21", "signal21 packet21"],
    ),
    (
        ("buffer21 queue21 worker21 kernel21 signal21 packet21", 28),
        ["buffer21 queue21 worker21", "kernel21 signal21 packet21"],
    ),
    (
        ("queue21 worker21 kernel21 signal21 packet21 router21", 6),
        ["queue21", "worker21", "kernel21", "signal21", "packet21", "router21"],
    ),
    (
        ("queue21 worker21 kernel21 signal21 packet21 router21", 10),
        ["queue21", "worker21", "kernel21", "signal21", "packet21", "router21"],
    ),
    (
        ("queue21 worker21 kernel21 signal21 packet21 router21", 18),
        ["queue21 worker21", "kernel21 signal21", "packet21 router21"],
    ),
    (
        ("queue21 worker21 kernel21 signal21 packet21 router21", 28),
        ["queue21 worker21 kernel21", "signal21 packet21 router21"],
    ),
    (
        ("worker21 kernel21 signal21 packet21 router21 cluster21", 6),
        ["worker21", "kernel21", "signal21", "packet21", "router21", "cluster21"],
    ),
    (
        ("worker21 kernel21 signal21 packet21 router21 cluster21", 10),
        ["worker21", "kernel21", "signal21", "packet21", "router21", "cluster21"],
    ),
    (
        ("worker21 kernel21 signal21 packet21 router21 cluster21", 18),
        ["worker21 kernel21", "signal21 packet21", "router21 cluster21"],
    ),
    (
        ("worker21 kernel21 signal21 packet21 router21 cluster21", 28),
        ["worker21 kernel21 signal21", "packet21 router21 cluster21"],
    ),
    (
        ("kernel21 signal21 packet21 router21 cluster21 mirror21", 6),
        ["kernel21", "signal21", "packet21", "router21", "cluster21", "mirror21"],
    ),
    (
        ("kernel21 signal21 packet21 router21 cluster21 mirror21", 10),
        ["kernel21", "signal21", "packet21", "router21", "cluster21", "mirror21"],
    ),
    (
        ("kernel21 signal21 packet21 router21 cluster21 mirror21", 18),
        ["kernel21 signal21", "packet21 router21", "cluster21 mirror21"],
    ),
    (
        ("kernel21 signal21 packet21 router21 cluster21 mirror21", 28),
        ["kernel21 signal21 packet21", "router21 cluster21 mirror21"],
    ),
    (
        ("signal21 packet21 router21 cluster21 mirror21 filter21", 6),
        ["signal21", "packet21", "router21", "cluster21", "mirror21", "filter21"],
    ),
    (
        ("signal21 packet21 router21 cluster21 mirror21 filter21", 10),
        ["signal21", "packet21", "router21", "cluster21", "mirror21", "filter21"],
    ),
    (
        ("signal21 packet21 router21 cluster21 mirror21 filter21", 18),
        ["signal21 packet21", "router21 cluster21", "mirror21 filter21"],
    ),
    (
        ("signal21 packet21 router21 cluster21 mirror21 filter21", 28),
        ["signal21 packet21 router21", "cluster21 mirror21 filter21"],
    ),
    (
        ("packet21 router21 cluster21 mirror21 filter21 ranking21", 6),
        ["packet21", "router21", "cluster21", "mirror21", "filter21", "ranking21"],
    ),
    (
        ("packet21 router21 cluster21 mirror21 filter21 ranking21", 10),
        ["packet21", "router21", "cluster21", "mirror21", "filter21", "ranking21"],
    ),
    (
        ("packet21 router21 cluster21 mirror21 filter21 ranking21", 18),
        ["packet21 router21", "cluster21 mirror21", "filter21 ranking21"],
    ),
    (
        ("packet21 router21 cluster21 mirror21 filter21 ranking21", 28),
        ["packet21 router21 cluster21", "mirror21 filter21 ranking21"],
    ),
    (
        ("router21 cluster21 mirror21 filter21 ranking21 encoding21", 6),
        ["router21", "cluster21", "mirror21", "filter21", "ranking21", "encoding21"],
    ),
    (
        ("router21 cluster21 mirror21 filter21 ranking21 encoding21", 10),
        ["router21", "cluster21", "mirror21", "filter21", "ranking21", "encoding21"],
    ),
    (
        ("router21 cluster21 mirror21 filter21 ranking21 encoding21", 18),
        ["router21 cluster21", "mirror21 filter21", "ranking21", "encoding21"],
    ),
    (
        ("router21 cluster21 mirror21 filter21 ranking21 encoding21", 28),
        ["router21 cluster21 mirror21", "filter21 ranking21", "encoding21"],
    ),
    (
        ("cluster21 mirror21 filter21 ranking21 encoding21 mapping21", 6),
        ["cluster21", "mirror21", "filter21", "ranking21", "encoding21", "mapping21"],
    ),
    (
        ("cluster21 mirror21 filter21 ranking21 encoding21 mapping21", 10),
        ["cluster21", "mirror21", "filter21", "ranking21", "encoding21", "mapping21"],
    ),
    (
        ("cluster21 mirror21 filter21 ranking21 encoding21 mapping21", 18),
        ["cluster21 mirror21", "filter21 ranking21", "encoding21", "mapping21"],
    ),
    (
        ("cluster21 mirror21 filter21 ranking21 encoding21 mapping21", 28),
        ["cluster21 mirror21 filter21", "ranking21 encoding21", "mapping21"],
    ),
    (
        ("mirror21 filter21 ranking21 encoding21 mapping21 record21", 6),
        ["mirror21", "filter21", "ranking21", "encoding21", "mapping21", "record21"],
    ),
    (
        ("mirror21 filter21 ranking21 encoding21 mapping21 record21", 10),
        ["mirror21", "filter21", "ranking21", "encoding21", "mapping21", "record21"],
    ),
    (
        ("mirror21 filter21 ranking21 encoding21 mapping21 record21", 18),
        ["mirror21 filter21", "ranking21", "encoding21", "mapping21 record21"],
    ),
    (
        ("mirror21 filter21 ranking21 encoding21 mapping21 record21", 28),
        ["mirror21 filter21 ranking21", "encoding21 mapping21", "record21"],
    ),
    (
        ("filter21 ranking21 encoding21 mapping21 record21 candle21", 6),
        ["filter21", "ranking21", "encoding21", "mapping21", "record21", "candle21"],
    ),
    (
        ("filter21 ranking21 encoding21 mapping21 record21 candle21", 10),
        ["filter21", "ranking21", "encoding21", "mapping21", "record21", "candle21"],
    ),
    (
        ("filter21 ranking21 encoding21 mapping21 record21 candle21", 18),
        ["filter21 ranking21", "encoding21", "mapping21 record21", "candle21"],
    ),
    (
        ("filter21 ranking21 encoding21 mapping21 record21 candle21", 28),
        ["filter21 ranking21", "encoding21 mapping21", "record21 candle21"],
    ),
    (
        ("ranking21 encoding21 mapping21 record21 candle21 thread21", 6),
        ["ranking21", "encoding21", "mapping21", "record21", "candle21", "thread21"],
    ),
    (
        ("ranking21 encoding21 mapping21 record21 candle21 thread21", 10),
        ["ranking21", "encoding21", "mapping21", "record21", "candle21", "thread21"],
    ),
    (
        ("ranking21 encoding21 mapping21 record21 candle21 thread21", 18),
        ["ranking21", "encoding21", "mapping21 record21", "candle21 thread21"],
    ),
    (
        ("ranking21 encoding21 mapping21 record21 candle21 thread21", 28),
        ["ranking21 encoding21", "mapping21 record21 candle21", "thread21"],
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
