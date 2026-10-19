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
        ("round 109: the quick brown fox jumps over the lazy dog", 4),
        ["round", "109:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", 8),
        ["round", "109: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", 12),
        ["round 109:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", 16),
        ["round 109: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", 24),
        ["round 109: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 109: the quick brown fox jumps over the lazy dog", 32),
        ["round 109: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", 4),
        ["round", "109:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", 8),
        ["round", "109:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", 12),
        ["round 109:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", 16),
        ["round 109:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", 24),
        ["round 109: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 109: agentuniverse is a framework for multi agents", 32),
        ["round 109: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", 4),
        ["round", "109:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", 8),
        ["round", "109:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", 12),
        ["round 109:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", 16),
        ["round 109:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", 24),
        ["round 109: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 109: knowledge stored as vectors enables retrieval", 32),
        ["round 109: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 109: the processor reads the record then stops", 4),
        ["round", "109:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 109: the processor reads the record then stops", 8),
        ["round", "109: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 109: the processor reads the record then stops", 12),
        ["round 109:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 109: the processor reads the record then stops", 16),
        ["round 109: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 109: the processor reads the record then stops", 24),
        ["round 109: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 109: the processor reads the record then stops", 32),
        ["round 109: the processor reads", "the record then stops"],
    ),
    (
        ("round 109: a worker pulls the next task from the queue", 4),
        ["round", "109:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 109: a worker pulls the next task from the queue", 8),
        ["round", "109: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 109: a worker pulls the next task from the queue", 12),
        ["round 109: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 109: a worker pulls the next task from the queue", 16),
        ["round 109: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 109: a worker pulls the next task from the queue", 24),
        ["round 109: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 109: a worker pulls the next task from the queue", 32),
        ["round 109: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 109: signals travel through the network layer", 4),
        ["round", "109:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 109: signals travel through the network layer", 8),
        ["round", "109:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 109: signals travel through the network layer", 12),
        ["round 109:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 109: signals travel through the network layer", 16),
        ["round 109:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 109: signals travel through the network layer", 24),
        ["round 109: signals", "travel through the", "network layer"],
    ),
    (
        ("round 109: signals travel through the network layer", 32),
        ["round 109: signals travel", "through the network layer"],
    ),
    (
        ("round 109: the gateway routes each request by policy", 4),
        ["round", "109:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 109: the gateway routes each request by policy", 8),
        ["round", "109: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 109: the gateway routes each request by policy", 12),
        ["round 109:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 109: the gateway routes each request by policy", 16),
        ["round 109: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 109: the gateway routes each request by policy", 24),
        ["round 109: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 109: the gateway routes each request by policy", 32),
        ["round 109: the gateway routes", "each request by policy"],
    ),
    (
        ("round 109: memory grows until the buffer is full", 4),
        ["round", "109:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 109: memory grows until the buffer is full", 8),
        ["round", "109:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 109: memory grows until the buffer is full", 12),
        ["round 109:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 109: memory grows until the buffer is full", 16),
        ["round 109:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 109: memory grows until the buffer is full", 24), ["round 109: memory grows", "until the buffer is full"]),
    (("round 109: memory grows until the buffer is full", 32), ["round 109: memory grows until", "the buffer is full"]),
    (
        ("round 109: the cluster mirrors every packet twice", 4),
        ["round", "109:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 109: the cluster mirrors every packet twice", 8),
        ["round", "109: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 109: the cluster mirrors every packet twice", 12),
        ["round 109:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 109: the cluster mirrors every packet twice", 16),
        ["round 109: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 109: the cluster mirrors every packet twice", 24),
        ["round 109: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 109: the cluster mirrors every packet twice", 32),
        ["round 109: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", 4),
        ["round", "109:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", 8),
        ["round", "109:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", 12),
        ["round 109:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", 16),
        ["round 109:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", 24),
        ["round 109: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 109: ranking uses tokens learned from the corpus", 32),
        ["round 109: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 109: a long session ends when the candle dies", 4),
        ["round", "109:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 109: a long session ends when the candle dies", 8),
        ["round", "109: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 109: a long session ends when the candle dies", 12),
        ["round 109: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 109: a long session ends when the candle dies", 16),
        ["round 109: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 109: a long session ends when the candle dies", 24),
        ["round 109: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 109: a long session ends when the candle dies", 32),
        ["round 109: a long session ends", "when the candle dies"],
    ),
    (
        ("round 109: encode the prompt then map the result", 4),
        ["round", "109:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 109: encode the prompt then map the result", 8),
        ["round", "109:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 109: encode the prompt then map the result", 12),
        ["round 109:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 109: encode the prompt then map the result", 16),
        ["round 109:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 109: encode the prompt then map the result", 24),
        ["round 109: encode the", "prompt then map the", "result"],
    ),
    (("round 109: encode the prompt then map the result", 32), ["round 109: encode the prompt", "then map the result"]),
    (
        ("round 109: the kernel wakes the worker at dawn", 4),
        ["round", "109:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 109: the kernel wakes the worker at dawn", 8),
        ["round", "109: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 109: the kernel wakes the worker at dawn", 12),
        ["round 109:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 109: the kernel wakes the worker at dawn", 16), ["round 109: the", "kernel wakes the", "worker at dawn"]),
    (("round 109: the kernel wakes the worker at dawn", 24), ["round 109: the kernel", "wakes the worker at dawn"]),
    (("round 109: the kernel wakes the worker at dawn", 32), ["round 109: the kernel wakes the", "worker at dawn"]),
    (
        ("round 109: service latency drops after the patch", 4),
        ["round", "109:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 109: service latency drops after the patch", 8),
        ["round", "109:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 109: service latency drops after the patch", 12),
        ["round 109:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 109: service latency drops after the patch", 16),
        ["round 109:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 109: service latency drops after the patch", 24),
        ["round 109: service", "latency drops after the", "patch"],
    ),
    (("round 109: service latency drops after the patch", 32), ["round 109: service latency drops", "after the patch"]),
    (
        ("round 109: the library caches every vector it sees", 4),
        ["round", "109:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 109: the library caches every vector it sees", 8),
        ["round", "109: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 109: the library caches every vector it sees", 12),
        ["round 109:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 109: the library caches every vector it sees", 16),
        ["round 109: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 109: the library caches every vector it sees", 24),
        ["round 109: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 109: the library caches every vector it sees", 32),
        ["round 109: the library caches", "every vector it sees"],
    ),
    (
        ("round 109: agents argue then the debate resolves", 4),
        ["round", "109:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 109: agents argue then the debate resolves", 8),
        ["round", "109:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 109: agents argue then the debate resolves", 12),
        ["round 109:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 109: agents argue then the debate resolves", 16),
        ["round 109:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 109: agents argue then the debate resolves", 24), ["round 109: agents argue", "then the debate resolves"]),
    (("round 109: agents argue then the debate resolves", 32), ["round 109: agents argue then the", "debate resolves"]),
    (
        ("round 109: the filter keeps only strong matches", 4),
        ["round", "109:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 109: the filter keeps only strong matches", 8),
        ["round", "109: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 109: the filter keeps only strong matches", 12),
        ["round 109:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 109: the filter keeps only strong matches", 16),
        ["round 109: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 109: the filter keeps only strong matches", 24),
        ["round 109: the filter", "keeps only strong", "matches"],
    ),
    (("round 109: the filter keeps only strong matches", 32), ["round 109: the filter keeps only", "strong matches"]),
    (
        ("round 109: the model answers with a short reply", 4),
        ["round", "109:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 109: the model answers with a short reply", 8),
        ["round", "109: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 109: the model answers with a short reply", 12),
        ["round 109:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 109: the model answers with a short reply", 16),
        ["round 109: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 109: the model answers with a short reply", 24),
        ["round 109: the model", "answers with a short", "reply"],
    ),
    (("round 109: the model answers with a short reply", 32), ["round 109: the model answers", "with a short reply"]),
    (
        ("round 109: the recorder stores the reasoning trace", 4),
        ["round", "109:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 109: the recorder stores the reasoning trace", 8),
        ["round", "109: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 109: the recorder stores the reasoning trace", 12),
        ["round 109:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 109: the recorder stores the reasoning trace", 16),
        ["round 109: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 109: the recorder stores the reasoning trace", 24),
        ["round 109: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 109: the recorder stores the reasoning trace", 32),
        ["round 109: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 109: the angel watches the processor run", 4),
        ["round", "109:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 109: the angel watches the processor run", 8),
        ["round", "109: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 109: the angel watches the processor run", 12),
        ["round 109:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 109: the angel watches the processor run", 16),
        ["round 109: the", "angel watches", "the processor", "run"],
    ),
    (("round 109: the angel watches the processor run", 24), ["round 109: the angel", "watches the processor", "run"]),
    (("round 109: the angel watches the processor run", 32), ["round 109: the angel watches the", "processor run"]),
    (
        ("round 109: angle of the vector decides the match", 4),
        ["round", "109:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 109: angle of the vector decides the match", 8),
        ["round", "109:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 109: angle of the vector decides the match", 12),
        ["round 109:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 109: angle of the vector decides the match", 16),
        ["round 109: angle", "of the vector", "decides the", "match"],
    ),
    (("round 109: angle of the vector decides the match", 24), ["round 109: angle of the", "vector decides the match"]),
    (("round 109: angle of the vector decides the match", 32), ["round 109: angle of the vector", "decides the match"]),
    (
        ("round 109: the candle burns twice as long at night", 4),
        ["round", "109:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 109: the candle burns twice as long at night", 8),
        ["round", "109: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 109: the candle burns twice as long at night", 12),
        ["round 109:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 109: the candle burns twice as long at night", 16),
        ["round 109: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 109: the candle burns twice as long at night", 24),
        ["round 109: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 109: the candle burns twice as long at night", 32),
        ["round 109: the candle burns", "twice as long at night"],
    ),
    (
        ("round 109: a mirror of the universe in one line", 4),
        ["round", "109:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 109: a mirror of the universe in one line", 8),
        ["round", "109: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 109: a mirror of the universe in one line", 12),
        ["round 109: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 109: a mirror of the universe in one line", 16),
        ["round 109: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 109: a mirror of the universe in one line", 24), ["round 109: a mirror of", "the universe in one line"]),
    (("round 109: a mirror of the universe in one line", 32), ["round 109: a mirror of the", "universe in one line"]),
    (
        ("round 109: the queue drains before the storm", 4),
        ["round", "109:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 109: the queue drains before the storm", 8),
        ["round", "109: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 109: the queue drains before the storm", 12),
        ["round 109:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 109: the queue drains before the storm", 16), ["round 109: the", "queue drains", "before the storm"]),
    (("round 109: the queue drains before the storm", 24), ["round 109: the queue", "drains before the storm"]),
    (("round 109: the queue drains before the storm", 32), ["round 109: the queue drains", "before the storm"]),
    (
        ("kitten109 sitting109 agent109 angle109 universe109 memory109", 6),
        ["kitten109", "sitting109", "agent109", "angle109", "universe109", "memory109"],
    ),
    (
        ("kitten109 sitting109 agent109 angle109 universe109 memory109", 10),
        ["kitten109", "sitting109", "agent109", "angle109", "universe109", "memory109"],
    ),
    (
        ("kitten109 sitting109 agent109 angle109 universe109 memory109", 18),
        ["kitten109", "sitting109", "agent109 angle109", "universe109", "memory109"],
    ),
    (
        ("kitten109 sitting109 agent109 angle109 universe109 memory109", 28),
        ["kitten109 sitting109", "agent109 angle109", "universe109 memory109"],
    ),
    (
        ("sitting109 agent109 angle109 universe109 memory109 stream109", 6),
        ["sitting109", "agent109", "angle109", "universe109", "memory109", "stream109"],
    ),
    (
        ("sitting109 agent109 angle109 universe109 memory109 stream109", 10),
        ["sitting109", "agent109", "angle109", "universe109", "memory109", "stream109"],
    ),
    (
        ("sitting109 agent109 angle109 universe109 memory109 stream109", 18),
        ["sitting109", "agent109 angle109", "universe109", "memory109", "stream109"],
    ),
    (
        ("sitting109 agent109 angle109 universe109 memory109 stream109", 28),
        ["sitting109 agent109 angle109", "universe109 memory109", "stream109"],
    ),
    (
        ("agent109 angle109 universe109 memory109 stream109 context109", 6),
        ["agent109", "angle109", "universe109", "memory109", "stream109", "context109"],
    ),
    (
        ("agent109 angle109 universe109 memory109 stream109 context109", 10),
        ["agent109", "angle109", "universe109", "memory109", "stream109", "context109"],
    ),
    (
        ("agent109 angle109 universe109 memory109 stream109 context109", 18),
        ["agent109 angle109", "universe109", "memory109", "stream109", "context109"],
    ),
    (
        ("agent109 angle109 universe109 memory109 stream109 context109", 28),
        ["agent109 angle109", "universe109 memory109", "stream109 context109"],
    ),
    (
        ("angle109 universe109 memory109 stream109 context109 knowledge109", 6),
        ["angle109", "universe109", "memory109", "stream109", "context109", "knowledge109"],
    ),
    (
        ("angle109 universe109 memory109 stream109 context109 knowledge109", 10),
        ["angle109", "universe109", "memory109", "stream109", "context109", "knowledge109"],
    ),
    (
        ("angle109 universe109 memory109 stream109 context109 knowledge109", 18),
        ["angle109", "universe109", "memory109", "stream109", "context109", "knowledge109"],
    ),
    (
        ("angle109 universe109 memory109 stream109 context109 knowledge109", 28),
        ["angle109 universe109", "memory109 stream109", "context109 knowledge109"],
    ),
    (
        ("universe109 memory109 stream109 context109 knowledge109 vector109", 6),
        ["universe109", "memory109", "stream109", "context109", "knowledge109", "vector109"],
    ),
    (
        ("universe109 memory109 stream109 context109 knowledge109 vector109", 10),
        ["universe109", "memory109", "stream109", "context109", "knowledge109", "vector109"],
    ),
    (
        ("universe109 memory109 stream109 context109 knowledge109 vector109", 18),
        ["universe109", "memory109", "stream109", "context109", "knowledge109", "vector109"],
    ),
    (
        ("universe109 memory109 stream109 context109 knowledge109 vector109", 28),
        ["universe109 memory109", "stream109 context109", "knowledge109 vector109"],
    ),
    (
        ("memory109 stream109 context109 knowledge109 vector109 processor109", 6),
        ["memory109", "stream109", "context109", "knowledge109", "vector109", "processor109"],
    ),
    (
        ("memory109 stream109 context109 knowledge109 vector109 processor109", 10),
        ["memory109", "stream109", "context109", "knowledge109", "vector109", "processor109"],
    ),
    (
        ("memory109 stream109 context109 knowledge109 vector109 processor109", 18),
        ["memory109", "stream109", "context109", "knowledge109", "vector109", "processor109"],
    ),
    (
        ("memory109 stream109 context109 knowledge109 vector109 processor109", 28),
        ["memory109 stream109", "context109 knowledge109", "vector109 processor109"],
    ),
    (
        ("stream109 context109 knowledge109 vector109 processor109 reasoning109", 6),
        ["stream109", "context109", "knowledge109", "vector109", "processor109", "reasoning109"],
    ),
    (
        ("stream109 context109 knowledge109 vector109 processor109 reasoning109", 10),
        ["stream109", "context109", "knowledge109", "vector109", "processor109", "reasoning109"],
    ),
    (
        ("stream109 context109 knowledge109 vector109 processor109 reasoning109", 18),
        ["stream109", "context109", "knowledge109", "vector109", "processor109", "reasoning109"],
    ),
    (
        ("stream109 context109 knowledge109 vector109 processor109 reasoning109", 28),
        ["stream109 context109", "knowledge109 vector109", "processor109 reasoning109"],
    ),
    (
        ("context109 knowledge109 vector109 processor109 reasoning109 machine109", 6),
        ["context109", "knowledge109", "vector109", "processor109", "reasoning109", "machine109"],
    ),
    (
        ("context109 knowledge109 vector109 processor109 reasoning109 machine109", 10),
        ["context109", "knowledge109", "vector109", "processor109", "reasoning109", "machine109"],
    ),
    (
        ("context109 knowledge109 vector109 processor109 reasoning109 machine109", 18),
        ["context109", "knowledge109", "vector109", "processor109", "reasoning109", "machine109"],
    ),
    (
        ("context109 knowledge109 vector109 processor109 reasoning109 machine109", 28),
        ["context109 knowledge109", "vector109 processor109", "reasoning109 machine109"],
    ),
    (
        ("knowledge109 vector109 processor109 reasoning109 machine109 learning109", 6),
        ["knowledge109", "vector109", "processor109", "reasoning109", "machine109", "learning109"],
    ),
    (
        ("knowledge109 vector109 processor109 reasoning109 machine109 learning109", 10),
        ["knowledge109", "vector109", "processor109", "reasoning109", "machine109", "learning109"],
    ),
    (
        ("knowledge109 vector109 processor109 reasoning109 machine109 learning109", 18),
        ["knowledge109", "vector109", "processor109", "reasoning109", "machine109", "learning109"],
    ),
    (
        ("knowledge109 vector109 processor109 reasoning109 machine109 learning109", 28),
        ["knowledge109 vector109", "processor109 reasoning109", "machine109 learning109"],
    ),
    (
        ("vector109 processor109 reasoning109 machine109 learning109 model109", 6),
        ["vector109", "processor109", "reasoning109", "machine109", "learning109", "model109"],
    ),
    (
        ("vector109 processor109 reasoning109 machine109 learning109 model109", 10),
        ["vector109", "processor109", "reasoning109", "machine109", "learning109", "model109"],
    ),
    (
        ("vector109 processor109 reasoning109 machine109 learning109 model109", 18),
        ["vector109", "processor109", "reasoning109", "machine109", "learning109", "model109"],
    ),
    (
        ("vector109 processor109 reasoning109 machine109 learning109 model109", 28),
        ["vector109 processor109", "reasoning109 machine109", "learning109 model109"],
    ),
    (
        ("processor109 reasoning109 machine109 learning109 model109 token109", 6),
        ["processor109", "reasoning109", "machine109", "learning109", "model109", "token109"],
    ),
    (
        ("processor109 reasoning109 machine109 learning109 model109 token109", 10),
        ["processor109", "reasoning109", "machine109", "learning109", "model109", "token109"],
    ),
    (
        ("processor109 reasoning109 machine109 learning109 model109 token109", 18),
        ["processor109", "reasoning109", "machine109", "learning109", "model109 token109"],
    ),
    (
        ("processor109 reasoning109 machine109 learning109 model109 token109", 28),
        ["processor109 reasoning109", "machine109 learning109", "model109 token109"],
    ),
    (
        ("reasoning109 machine109 learning109 model109 token109 prompt109", 6),
        ["reasoning109", "machine109", "learning109", "model109", "token109", "prompt109"],
    ),
    (
        ("reasoning109 machine109 learning109 model109 token109 prompt109", 10),
        ["reasoning109", "machine109", "learning109", "model109", "token109", "prompt109"],
    ),
    (
        ("reasoning109 machine109 learning109 model109 token109 prompt109", 18),
        ["reasoning109", "machine109", "learning109", "model109 token109", "prompt109"],
    ),
    (
        ("reasoning109 machine109 learning109 model109 token109 prompt109", 28),
        ["reasoning109 machine109", "learning109 model109", "token109 prompt109"],
    ),
    (
        ("machine109 learning109 model109 token109 prompt109 session109", 6),
        ["machine109", "learning109", "model109", "token109", "prompt109", "session109"],
    ),
    (
        ("machine109 learning109 model109 token109 prompt109 session109", 10),
        ["machine109", "learning109", "model109", "token109", "prompt109", "session109"],
    ),
    (
        ("machine109 learning109 model109 token109 prompt109 session109", 18),
        ["machine109", "learning109", "model109 token109", "prompt109", "session109"],
    ),
    (
        ("machine109 learning109 model109 token109 prompt109 session109", 28),
        ["machine109 learning109", "model109 token109 prompt109", "session109"],
    ),
    (
        ("learning109 model109 token109 prompt109 session109 library109", 6),
        ["learning109", "model109", "token109", "prompt109", "session109", "library109"],
    ),
    (
        ("learning109 model109 token109 prompt109 session109 library109", 10),
        ["learning109", "model109", "token109", "prompt109", "session109", "library109"],
    ),
    (
        ("learning109 model109 token109 prompt109 session109 library109", 18),
        ["learning109", "model109 token109", "prompt109", "session109", "library109"],
    ),
    (
        ("learning109 model109 token109 prompt109 session109 library109", 28),
        ["learning109 model109", "token109 prompt109", "session109 library109"],
    ),
    (
        ("model109 token109 prompt109 session109 library109 service109", 6),
        ["model109", "token109", "prompt109", "session109", "library109", "service109"],
    ),
    (
        ("model109 token109 prompt109 session109 library109 service109", 10),
        ["model109", "token109", "prompt109", "session109", "library109", "service109"],
    ),
    (
        ("model109 token109 prompt109 session109 library109 service109", 18),
        ["model109 token109", "prompt109", "session109", "library109", "service109"],
    ),
    (
        ("model109 token109 prompt109 session109 library109 service109", 28),
        ["model109 token109 prompt109", "session109 library109", "service109"],
    ),
    (
        ("token109 prompt109 session109 library109 service109 gateway109", 6),
        ["token109", "prompt109", "session109", "library109", "service109", "gateway109"],
    ),
    (
        ("token109 prompt109 session109 library109 service109 gateway109", 10),
        ["token109", "prompt109", "session109", "library109", "service109", "gateway109"],
    ),
    (
        ("token109 prompt109 session109 library109 service109 gateway109", 18),
        ["token109 prompt109", "session109", "library109", "service109", "gateway109"],
    ),
    (
        ("token109 prompt109 session109 library109 service109 gateway109", 28),
        ["token109 prompt109", "session109 library109", "service109 gateway109"],
    ),
    (
        ("prompt109 session109 library109 service109 gateway109 storage109", 6),
        ["prompt109", "session109", "library109", "service109", "gateway109", "storage109"],
    ),
    (
        ("prompt109 session109 library109 service109 gateway109 storage109", 10),
        ["prompt109", "session109", "library109", "service109", "gateway109", "storage109"],
    ),
    (
        ("prompt109 session109 library109 service109 gateway109 storage109", 18),
        ["prompt109", "session109", "library109", "service109", "gateway109", "storage109"],
    ),
    (
        ("prompt109 session109 library109 service109 gateway109 storage109", 28),
        ["prompt109 session109", "library109 service109", "gateway109 storage109"],
    ),
    (
        ("session109 library109 service109 gateway109 storage109 network109", 6),
        ["session109", "library109", "service109", "gateway109", "storage109", "network109"],
    ),
    (
        ("session109 library109 service109 gateway109 storage109 network109", 10),
        ["session109", "library109", "service109", "gateway109", "storage109", "network109"],
    ),
    (
        ("session109 library109 service109 gateway109 storage109 network109", 18),
        ["session109", "library109", "service109", "gateway109", "storage109", "network109"],
    ),
    (
        ("session109 library109 service109 gateway109 storage109 network109", 28),
        ["session109 library109", "service109 gateway109", "storage109 network109"],
    ),
    (
        ("library109 service109 gateway109 storage109 network109 latency109", 6),
        ["library109", "service109", "gateway109", "storage109", "network109", "latency109"],
    ),
    (
        ("library109 service109 gateway109 storage109 network109 latency109", 10),
        ["library109", "service109", "gateway109", "storage109", "network109", "latency109"],
    ),
    (
        ("library109 service109 gateway109 storage109 network109 latency109", 18),
        ["library109", "service109", "gateway109", "storage109", "network109", "latency109"],
    ),
    (
        ("library109 service109 gateway109 storage109 network109 latency109", 28),
        ["library109 service109", "gateway109 storage109", "network109 latency109"],
    ),
    (
        ("service109 gateway109 storage109 network109 latency109 buffer109", 6),
        ["service109", "gateway109", "storage109", "network109", "latency109", "buffer109"],
    ),
    (
        ("service109 gateway109 storage109 network109 latency109 buffer109", 10),
        ["service109", "gateway109", "storage109", "network109", "latency109", "buffer109"],
    ),
    (
        ("service109 gateway109 storage109 network109 latency109 buffer109", 18),
        ["service109", "gateway109", "storage109", "network109", "latency109", "buffer109"],
    ),
    (
        ("service109 gateway109 storage109 network109 latency109 buffer109", 28),
        ["service109 gateway109", "storage109 network109", "latency109 buffer109"],
    ),
    (
        ("gateway109 storage109 network109 latency109 buffer109 queue109", 6),
        ["gateway109", "storage109", "network109", "latency109", "buffer109", "queue109"],
    ),
    (
        ("gateway109 storage109 network109 latency109 buffer109 queue109", 10),
        ["gateway109", "storage109", "network109", "latency109", "buffer109", "queue109"],
    ),
    (
        ("gateway109 storage109 network109 latency109 buffer109 queue109", 18),
        ["gateway109", "storage109", "network109", "latency109", "buffer109 queue109"],
    ),
    (
        ("gateway109 storage109 network109 latency109 buffer109 queue109", 28),
        ["gateway109 storage109", "network109 latency109", "buffer109 queue109"],
    ),
    (
        ("storage109 network109 latency109 buffer109 queue109 worker109", 6),
        ["storage109", "network109", "latency109", "buffer109", "queue109", "worker109"],
    ),
    (
        ("storage109 network109 latency109 buffer109 queue109 worker109", 10),
        ["storage109", "network109", "latency109", "buffer109", "queue109", "worker109"],
    ),
    (
        ("storage109 network109 latency109 buffer109 queue109 worker109", 18),
        ["storage109", "network109", "latency109", "buffer109 queue109", "worker109"],
    ),
    (
        ("storage109 network109 latency109 buffer109 queue109 worker109", 28),
        ["storage109 network109", "latency109 buffer109", "queue109 worker109"],
    ),
    (
        ("network109 latency109 buffer109 queue109 worker109 kernel109", 6),
        ["network109", "latency109", "buffer109", "queue109", "worker109", "kernel109"],
    ),
    (
        ("network109 latency109 buffer109 queue109 worker109 kernel109", 10),
        ["network109", "latency109", "buffer109", "queue109", "worker109", "kernel109"],
    ),
    (
        ("network109 latency109 buffer109 queue109 worker109 kernel109", 18),
        ["network109", "latency109", "buffer109 queue109", "worker109", "kernel109"],
    ),
    (
        ("network109 latency109 buffer109 queue109 worker109 kernel109", 28),
        ["network109 latency109", "buffer109 queue109 worker109", "kernel109"],
    ),
    (
        ("latency109 buffer109 queue109 worker109 kernel109 signal109", 6),
        ["latency109", "buffer109", "queue109", "worker109", "kernel109", "signal109"],
    ),
    (
        ("latency109 buffer109 queue109 worker109 kernel109 signal109", 10),
        ["latency109", "buffer109", "queue109", "worker109", "kernel109", "signal109"],
    ),
    (
        ("latency109 buffer109 queue109 worker109 kernel109 signal109", 18),
        ["latency109", "buffer109 queue109", "worker109", "kernel109", "signal109"],
    ),
    (
        ("latency109 buffer109 queue109 worker109 kernel109 signal109", 28),
        ["latency109 buffer109", "queue109 worker109 kernel109", "signal109"],
    ),
    (
        ("buffer109 queue109 worker109 kernel109 signal109 packet109", 6),
        ["buffer109", "queue109", "worker109", "kernel109", "signal109", "packet109"],
    ),
    (
        ("buffer109 queue109 worker109 kernel109 signal109 packet109", 10),
        ["buffer109", "queue109", "worker109", "kernel109", "signal109", "packet109"],
    ),
    (
        ("buffer109 queue109 worker109 kernel109 signal109 packet109", 18),
        ["buffer109 queue109", "worker109", "kernel109", "signal109", "packet109"],
    ),
    (
        ("buffer109 queue109 worker109 kernel109 signal109 packet109", 28),
        ["buffer109 queue109 worker109", "kernel109 signal109", "packet109"],
    ),
    (
        ("queue109 worker109 kernel109 signal109 packet109 router109", 6),
        ["queue109", "worker109", "kernel109", "signal109", "packet109", "router109"],
    ),
    (
        ("queue109 worker109 kernel109 signal109 packet109 router109", 10),
        ["queue109", "worker109", "kernel109", "signal109", "packet109", "router109"],
    ),
    (
        ("queue109 worker109 kernel109 signal109 packet109 router109", 18),
        ["queue109 worker109", "kernel109", "signal109", "packet109", "router109"],
    ),
    (
        ("queue109 worker109 kernel109 signal109 packet109 router109", 28),
        ["queue109 worker109 kernel109", "signal109 packet109", "router109"],
    ),
    (
        ("worker109 kernel109 signal109 packet109 router109 cluster109", 6),
        ["worker109", "kernel109", "signal109", "packet109", "router109", "cluster109"],
    ),
    (
        ("worker109 kernel109 signal109 packet109 router109 cluster109", 10),
        ["worker109", "kernel109", "signal109", "packet109", "router109", "cluster109"],
    ),
    (
        ("worker109 kernel109 signal109 packet109 router109 cluster109", 18),
        ["worker109", "kernel109", "signal109", "packet109", "router109", "cluster109"],
    ),
    (
        ("worker109 kernel109 signal109 packet109 router109 cluster109", 28),
        ["worker109 kernel109", "signal109 packet109", "router109 cluster109"],
    ),
    (
        ("kernel109 signal109 packet109 router109 cluster109 mirror109", 6),
        ["kernel109", "signal109", "packet109", "router109", "cluster109", "mirror109"],
    ),
    (
        ("kernel109 signal109 packet109 router109 cluster109 mirror109", 10),
        ["kernel109", "signal109", "packet109", "router109", "cluster109", "mirror109"],
    ),
    (
        ("kernel109 signal109 packet109 router109 cluster109 mirror109", 18),
        ["kernel109", "signal109", "packet109", "router109", "cluster109", "mirror109"],
    ),
    (
        ("kernel109 signal109 packet109 router109 cluster109 mirror109", 28),
        ["kernel109 signal109", "packet109 router109", "cluster109 mirror109"],
    ),
    (
        ("signal109 packet109 router109 cluster109 mirror109 filter109", 6),
        ["signal109", "packet109", "router109", "cluster109", "mirror109", "filter109"],
    ),
    (
        ("signal109 packet109 router109 cluster109 mirror109 filter109", 10),
        ["signal109", "packet109", "router109", "cluster109", "mirror109", "filter109"],
    ),
    (
        ("signal109 packet109 router109 cluster109 mirror109 filter109", 18),
        ["signal109", "packet109", "router109", "cluster109", "mirror109", "filter109"],
    ),
    (
        ("signal109 packet109 router109 cluster109 mirror109 filter109", 28),
        ["signal109 packet109", "router109 cluster109", "mirror109 filter109"],
    ),
    (
        ("packet109 router109 cluster109 mirror109 filter109 ranking109", 6),
        ["packet109", "router109", "cluster109", "mirror109", "filter109", "ranking109"],
    ),
    (
        ("packet109 router109 cluster109 mirror109 filter109 ranking109", 10),
        ["packet109", "router109", "cluster109", "mirror109", "filter109", "ranking109"],
    ),
    (
        ("packet109 router109 cluster109 mirror109 filter109 ranking109", 18),
        ["packet109", "router109", "cluster109", "mirror109", "filter109", "ranking109"],
    ),
    (
        ("packet109 router109 cluster109 mirror109 filter109 ranking109", 28),
        ["packet109 router109", "cluster109 mirror109", "filter109 ranking109"],
    ),
    (
        ("router109 cluster109 mirror109 filter109 ranking109 encoding109", 6),
        ["router109", "cluster109", "mirror109", "filter109", "ranking109", "encoding109"],
    ),
    (
        ("router109 cluster109 mirror109 filter109 ranking109 encoding109", 10),
        ["router109", "cluster109", "mirror109", "filter109", "ranking109", "encoding109"],
    ),
    (
        ("router109 cluster109 mirror109 filter109 ranking109 encoding109", 18),
        ["router109", "cluster109", "mirror109", "filter109", "ranking109", "encoding109"],
    ),
    (
        ("router109 cluster109 mirror109 filter109 ranking109 encoding109", 28),
        ["router109 cluster109", "mirror109 filter109", "ranking109 encoding109"],
    ),
    (
        ("cluster109 mirror109 filter109 ranking109 encoding109 mapping109", 6),
        ["cluster109", "mirror109", "filter109", "ranking109", "encoding109", "mapping109"],
    ),
    (
        ("cluster109 mirror109 filter109 ranking109 encoding109 mapping109", 10),
        ["cluster109", "mirror109", "filter109", "ranking109", "encoding109", "mapping109"],
    ),
    (
        ("cluster109 mirror109 filter109 ranking109 encoding109 mapping109", 18),
        ["cluster109", "mirror109", "filter109", "ranking109", "encoding109", "mapping109"],
    ),
    (
        ("cluster109 mirror109 filter109 ranking109 encoding109 mapping109", 28),
        ["cluster109 mirror109", "filter109 ranking109", "encoding109 mapping109"],
    ),
    (
        ("mirror109 filter109 ranking109 encoding109 mapping109 record109", 6),
        ["mirror109", "filter109", "ranking109", "encoding109", "mapping109", "record109"],
    ),
    (
        ("mirror109 filter109 ranking109 encoding109 mapping109 record109", 10),
        ["mirror109", "filter109", "ranking109", "encoding109", "mapping109", "record109"],
    ),
    (
        ("mirror109 filter109 ranking109 encoding109 mapping109 record109", 18),
        ["mirror109", "filter109", "ranking109", "encoding109", "mapping109", "record109"],
    ),
    (
        ("mirror109 filter109 ranking109 encoding109 mapping109 record109", 28),
        ["mirror109 filter109", "ranking109 encoding109", "mapping109 record109"],
    ),
    (
        ("filter109 ranking109 encoding109 mapping109 record109 candle109", 6),
        ["filter109", "ranking109", "encoding109", "mapping109", "record109", "candle109"],
    ),
    (
        ("filter109 ranking109 encoding109 mapping109 record109 candle109", 10),
        ["filter109", "ranking109", "encoding109", "mapping109", "record109", "candle109"],
    ),
    (
        ("filter109 ranking109 encoding109 mapping109 record109 candle109", 18),
        ["filter109", "ranking109", "encoding109", "mapping109", "record109", "candle109"],
    ),
    (
        ("filter109 ranking109 encoding109 mapping109 record109 candle109", 28),
        ["filter109 ranking109", "encoding109 mapping109", "record109 candle109"],
    ),
    (
        ("ranking109 encoding109 mapping109 record109 candle109 thread109", 6),
        ["ranking109", "encoding109", "mapping109", "record109", "candle109", "thread109"],
    ),
    (
        ("ranking109 encoding109 mapping109 record109 candle109 thread109", 10),
        ["ranking109", "encoding109", "mapping109", "record109", "candle109", "thread109"],
    ),
    (
        ("ranking109 encoding109 mapping109 record109 candle109 thread109", 18),
        ["ranking109", "encoding109", "mapping109", "record109", "candle109", "thread109"],
    ),
    (
        ("ranking109 encoding109 mapping109 record109 candle109 thread109", 28),
        ["ranking109 encoding109", "mapping109 record109", "candle109 thread109"],
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
