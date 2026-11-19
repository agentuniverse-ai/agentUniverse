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
        ("round 135: the quick brown fox jumps over the lazy dog", 4),
        ["round", "135:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", 8),
        ["round", "135: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", 12),
        ["round 135:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", 16),
        ["round 135: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", 24),
        ["round 135: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 135: the quick brown fox jumps over the lazy dog", 32),
        ["round 135: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", 4),
        ["round", "135:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", 8),
        ["round", "135:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", 12),
        ["round 135:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", 16),
        ["round 135:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", 24),
        ["round 135: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 135: agentuniverse is a framework for multi agents", 32),
        ["round 135: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", 4),
        ["round", "135:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", 8),
        ["round", "135:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", 12),
        ["round 135:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", 16),
        ["round 135:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", 24),
        ["round 135: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 135: knowledge stored as vectors enables retrieval", 32),
        ["round 135: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 135: the processor reads the record then stops", 4),
        ["round", "135:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 135: the processor reads the record then stops", 8),
        ["round", "135: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 135: the processor reads the record then stops", 12),
        ["round 135:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 135: the processor reads the record then stops", 16),
        ["round 135: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 135: the processor reads the record then stops", 24),
        ["round 135: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 135: the processor reads the record then stops", 32),
        ["round 135: the processor reads", "the record then stops"],
    ),
    (
        ("round 135: a worker pulls the next task from the queue", 4),
        ["round", "135:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 135: a worker pulls the next task from the queue", 8),
        ["round", "135: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 135: a worker pulls the next task from the queue", 12),
        ["round 135: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 135: a worker pulls the next task from the queue", 16),
        ["round 135: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 135: a worker pulls the next task from the queue", 24),
        ["round 135: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 135: a worker pulls the next task from the queue", 32),
        ["round 135: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 135: signals travel through the network layer", 4),
        ["round", "135:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 135: signals travel through the network layer", 8),
        ["round", "135:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 135: signals travel through the network layer", 12),
        ["round 135:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 135: signals travel through the network layer", 16),
        ["round 135:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 135: signals travel through the network layer", 24),
        ["round 135: signals", "travel through the", "network layer"],
    ),
    (
        ("round 135: signals travel through the network layer", 32),
        ["round 135: signals travel", "through the network layer"],
    ),
    (
        ("round 135: the gateway routes each request by policy", 4),
        ["round", "135:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 135: the gateway routes each request by policy", 8),
        ["round", "135: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 135: the gateway routes each request by policy", 12),
        ["round 135:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 135: the gateway routes each request by policy", 16),
        ["round 135: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 135: the gateway routes each request by policy", 24),
        ["round 135: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 135: the gateway routes each request by policy", 32),
        ["round 135: the gateway routes", "each request by policy"],
    ),
    (
        ("round 135: memory grows until the buffer is full", 4),
        ["round", "135:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 135: memory grows until the buffer is full", 8),
        ["round", "135:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 135: memory grows until the buffer is full", 12),
        ["round 135:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 135: memory grows until the buffer is full", 16),
        ["round 135:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 135: memory grows until the buffer is full", 24), ["round 135: memory grows", "until the buffer is full"]),
    (("round 135: memory grows until the buffer is full", 32), ["round 135: memory grows until", "the buffer is full"]),
    (
        ("round 135: the cluster mirrors every packet twice", 4),
        ["round", "135:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 135: the cluster mirrors every packet twice", 8),
        ["round", "135: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 135: the cluster mirrors every packet twice", 12),
        ["round 135:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 135: the cluster mirrors every packet twice", 16),
        ["round 135: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 135: the cluster mirrors every packet twice", 24),
        ["round 135: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 135: the cluster mirrors every packet twice", 32),
        ["round 135: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", 4),
        ["round", "135:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", 8),
        ["round", "135:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", 12),
        ["round 135:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", 16),
        ["round 135:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", 24),
        ["round 135: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 135: ranking uses tokens learned from the corpus", 32),
        ["round 135: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 135: a long session ends when the candle dies", 4),
        ["round", "135:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 135: a long session ends when the candle dies", 8),
        ["round", "135: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 135: a long session ends when the candle dies", 12),
        ["round 135: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 135: a long session ends when the candle dies", 16),
        ["round 135: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 135: a long session ends when the candle dies", 24),
        ["round 135: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 135: a long session ends when the candle dies", 32),
        ["round 135: a long session ends", "when the candle dies"],
    ),
    (
        ("round 135: encode the prompt then map the result", 4),
        ["round", "135:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 135: encode the prompt then map the result", 8),
        ["round", "135:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 135: encode the prompt then map the result", 12),
        ["round 135:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 135: encode the prompt then map the result", 16),
        ["round 135:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 135: encode the prompt then map the result", 24),
        ["round 135: encode the", "prompt then map the", "result"],
    ),
    (("round 135: encode the prompt then map the result", 32), ["round 135: encode the prompt", "then map the result"]),
    (
        ("round 135: the kernel wakes the worker at dawn", 4),
        ["round", "135:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 135: the kernel wakes the worker at dawn", 8),
        ["round", "135: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 135: the kernel wakes the worker at dawn", 12),
        ["round 135:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 135: the kernel wakes the worker at dawn", 16), ["round 135: the", "kernel wakes the", "worker at dawn"]),
    (("round 135: the kernel wakes the worker at dawn", 24), ["round 135: the kernel", "wakes the worker at dawn"]),
    (("round 135: the kernel wakes the worker at dawn", 32), ["round 135: the kernel wakes the", "worker at dawn"]),
    (
        ("round 135: service latency drops after the patch", 4),
        ["round", "135:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 135: service latency drops after the patch", 8),
        ["round", "135:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 135: service latency drops after the patch", 12),
        ["round 135:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 135: service latency drops after the patch", 16),
        ["round 135:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 135: service latency drops after the patch", 24),
        ["round 135: service", "latency drops after the", "patch"],
    ),
    (("round 135: service latency drops after the patch", 32), ["round 135: service latency drops", "after the patch"]),
    (
        ("round 135: the library caches every vector it sees", 4),
        ["round", "135:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 135: the library caches every vector it sees", 8),
        ["round", "135: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 135: the library caches every vector it sees", 12),
        ["round 135:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 135: the library caches every vector it sees", 16),
        ["round 135: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 135: the library caches every vector it sees", 24),
        ["round 135: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 135: the library caches every vector it sees", 32),
        ["round 135: the library caches", "every vector it sees"],
    ),
    (
        ("round 135: agents argue then the debate resolves", 4),
        ["round", "135:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 135: agents argue then the debate resolves", 8),
        ["round", "135:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 135: agents argue then the debate resolves", 12),
        ["round 135:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 135: agents argue then the debate resolves", 16),
        ["round 135:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 135: agents argue then the debate resolves", 24), ["round 135: agents argue", "then the debate resolves"]),
    (("round 135: agents argue then the debate resolves", 32), ["round 135: agents argue then the", "debate resolves"]),
    (
        ("round 135: the filter keeps only strong matches", 4),
        ["round", "135:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 135: the filter keeps only strong matches", 8),
        ["round", "135: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 135: the filter keeps only strong matches", 12),
        ["round 135:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 135: the filter keeps only strong matches", 16),
        ["round 135: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 135: the filter keeps only strong matches", 24),
        ["round 135: the filter", "keeps only strong", "matches"],
    ),
    (("round 135: the filter keeps only strong matches", 32), ["round 135: the filter keeps only", "strong matches"]),
    (
        ("round 135: the model answers with a short reply", 4),
        ["round", "135:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 135: the model answers with a short reply", 8),
        ["round", "135: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 135: the model answers with a short reply", 12),
        ["round 135:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 135: the model answers with a short reply", 16),
        ["round 135: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 135: the model answers with a short reply", 24),
        ["round 135: the model", "answers with a short", "reply"],
    ),
    (("round 135: the model answers with a short reply", 32), ["round 135: the model answers", "with a short reply"]),
    (
        ("round 135: the recorder stores the reasoning trace", 4),
        ["round", "135:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 135: the recorder stores the reasoning trace", 8),
        ["round", "135: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 135: the recorder stores the reasoning trace", 12),
        ["round 135:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 135: the recorder stores the reasoning trace", 16),
        ["round 135: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 135: the recorder stores the reasoning trace", 24),
        ["round 135: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 135: the recorder stores the reasoning trace", 32),
        ["round 135: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 135: the angel watches the processor run", 4),
        ["round", "135:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 135: the angel watches the processor run", 8),
        ["round", "135: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 135: the angel watches the processor run", 12),
        ["round 135:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 135: the angel watches the processor run", 16),
        ["round 135: the", "angel watches", "the processor", "run"],
    ),
    (("round 135: the angel watches the processor run", 24), ["round 135: the angel", "watches the processor", "run"]),
    (("round 135: the angel watches the processor run", 32), ["round 135: the angel watches the", "processor run"]),
    (
        ("round 135: angle of the vector decides the match", 4),
        ["round", "135:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 135: angle of the vector decides the match", 8),
        ["round", "135:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 135: angle of the vector decides the match", 12),
        ["round 135:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 135: angle of the vector decides the match", 16),
        ["round 135: angle", "of the vector", "decides the", "match"],
    ),
    (("round 135: angle of the vector decides the match", 24), ["round 135: angle of the", "vector decides the match"]),
    (("round 135: angle of the vector decides the match", 32), ["round 135: angle of the vector", "decides the match"]),
    (
        ("round 135: the candle burns twice as long at night", 4),
        ["round", "135:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 135: the candle burns twice as long at night", 8),
        ["round", "135: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 135: the candle burns twice as long at night", 12),
        ["round 135:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 135: the candle burns twice as long at night", 16),
        ["round 135: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 135: the candle burns twice as long at night", 24),
        ["round 135: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 135: the candle burns twice as long at night", 32),
        ["round 135: the candle burns", "twice as long at night"],
    ),
    (
        ("round 135: a mirror of the universe in one line", 4),
        ["round", "135:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 135: a mirror of the universe in one line", 8),
        ["round", "135: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 135: a mirror of the universe in one line", 12),
        ["round 135: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 135: a mirror of the universe in one line", 16),
        ["round 135: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 135: a mirror of the universe in one line", 24), ["round 135: a mirror of", "the universe in one line"]),
    (("round 135: a mirror of the universe in one line", 32), ["round 135: a mirror of the", "universe in one line"]),
    (
        ("round 135: the queue drains before the storm", 4),
        ["round", "135:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 135: the queue drains before the storm", 8),
        ["round", "135: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 135: the queue drains before the storm", 12),
        ["round 135:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 135: the queue drains before the storm", 16), ["round 135: the", "queue drains", "before the storm"]),
    (("round 135: the queue drains before the storm", 24), ["round 135: the queue", "drains before the storm"]),
    (("round 135: the queue drains before the storm", 32), ["round 135: the queue drains", "before the storm"]),
    (
        ("kitten135 sitting135 agent135 angle135 universe135 memory135", 6),
        ["kitten135", "sitting135", "agent135", "angle135", "universe135", "memory135"],
    ),
    (
        ("kitten135 sitting135 agent135 angle135 universe135 memory135", 10),
        ["kitten135", "sitting135", "agent135", "angle135", "universe135", "memory135"],
    ),
    (
        ("kitten135 sitting135 agent135 angle135 universe135 memory135", 18),
        ["kitten135", "sitting135", "agent135 angle135", "universe135", "memory135"],
    ),
    (
        ("kitten135 sitting135 agent135 angle135 universe135 memory135", 28),
        ["kitten135 sitting135", "agent135 angle135", "universe135 memory135"],
    ),
    (
        ("sitting135 agent135 angle135 universe135 memory135 stream135", 6),
        ["sitting135", "agent135", "angle135", "universe135", "memory135", "stream135"],
    ),
    (
        ("sitting135 agent135 angle135 universe135 memory135 stream135", 10),
        ["sitting135", "agent135", "angle135", "universe135", "memory135", "stream135"],
    ),
    (
        ("sitting135 agent135 angle135 universe135 memory135 stream135", 18),
        ["sitting135", "agent135 angle135", "universe135", "memory135", "stream135"],
    ),
    (
        ("sitting135 agent135 angle135 universe135 memory135 stream135", 28),
        ["sitting135 agent135 angle135", "universe135 memory135", "stream135"],
    ),
    (
        ("agent135 angle135 universe135 memory135 stream135 context135", 6),
        ["agent135", "angle135", "universe135", "memory135", "stream135", "context135"],
    ),
    (
        ("agent135 angle135 universe135 memory135 stream135 context135", 10),
        ["agent135", "angle135", "universe135", "memory135", "stream135", "context135"],
    ),
    (
        ("agent135 angle135 universe135 memory135 stream135 context135", 18),
        ["agent135 angle135", "universe135", "memory135", "stream135", "context135"],
    ),
    (
        ("agent135 angle135 universe135 memory135 stream135 context135", 28),
        ["agent135 angle135", "universe135 memory135", "stream135 context135"],
    ),
    (
        ("angle135 universe135 memory135 stream135 context135 knowledge135", 6),
        ["angle135", "universe135", "memory135", "stream135", "context135", "knowledge135"],
    ),
    (
        ("angle135 universe135 memory135 stream135 context135 knowledge135", 10),
        ["angle135", "universe135", "memory135", "stream135", "context135", "knowledge135"],
    ),
    (
        ("angle135 universe135 memory135 stream135 context135 knowledge135", 18),
        ["angle135", "universe135", "memory135", "stream135", "context135", "knowledge135"],
    ),
    (
        ("angle135 universe135 memory135 stream135 context135 knowledge135", 28),
        ["angle135 universe135", "memory135 stream135", "context135 knowledge135"],
    ),
    (
        ("universe135 memory135 stream135 context135 knowledge135 vector135", 6),
        ["universe135", "memory135", "stream135", "context135", "knowledge135", "vector135"],
    ),
    (
        ("universe135 memory135 stream135 context135 knowledge135 vector135", 10),
        ["universe135", "memory135", "stream135", "context135", "knowledge135", "vector135"],
    ),
    (
        ("universe135 memory135 stream135 context135 knowledge135 vector135", 18),
        ["universe135", "memory135", "stream135", "context135", "knowledge135", "vector135"],
    ),
    (
        ("universe135 memory135 stream135 context135 knowledge135 vector135", 28),
        ["universe135 memory135", "stream135 context135", "knowledge135 vector135"],
    ),
    (
        ("memory135 stream135 context135 knowledge135 vector135 processor135", 6),
        ["memory135", "stream135", "context135", "knowledge135", "vector135", "processor135"],
    ),
    (
        ("memory135 stream135 context135 knowledge135 vector135 processor135", 10),
        ["memory135", "stream135", "context135", "knowledge135", "vector135", "processor135"],
    ),
    (
        ("memory135 stream135 context135 knowledge135 vector135 processor135", 18),
        ["memory135", "stream135", "context135", "knowledge135", "vector135", "processor135"],
    ),
    (
        ("memory135 stream135 context135 knowledge135 vector135 processor135", 28),
        ["memory135 stream135", "context135 knowledge135", "vector135 processor135"],
    ),
    (
        ("stream135 context135 knowledge135 vector135 processor135 reasoning135", 6),
        ["stream135", "context135", "knowledge135", "vector135", "processor135", "reasoning135"],
    ),
    (
        ("stream135 context135 knowledge135 vector135 processor135 reasoning135", 10),
        ["stream135", "context135", "knowledge135", "vector135", "processor135", "reasoning135"],
    ),
    (
        ("stream135 context135 knowledge135 vector135 processor135 reasoning135", 18),
        ["stream135", "context135", "knowledge135", "vector135", "processor135", "reasoning135"],
    ),
    (
        ("stream135 context135 knowledge135 vector135 processor135 reasoning135", 28),
        ["stream135 context135", "knowledge135 vector135", "processor135 reasoning135"],
    ),
    (
        ("context135 knowledge135 vector135 processor135 reasoning135 machine135", 6),
        ["context135", "knowledge135", "vector135", "processor135", "reasoning135", "machine135"],
    ),
    (
        ("context135 knowledge135 vector135 processor135 reasoning135 machine135", 10),
        ["context135", "knowledge135", "vector135", "processor135", "reasoning135", "machine135"],
    ),
    (
        ("context135 knowledge135 vector135 processor135 reasoning135 machine135", 18),
        ["context135", "knowledge135", "vector135", "processor135", "reasoning135", "machine135"],
    ),
    (
        ("context135 knowledge135 vector135 processor135 reasoning135 machine135", 28),
        ["context135 knowledge135", "vector135 processor135", "reasoning135 machine135"],
    ),
    (
        ("knowledge135 vector135 processor135 reasoning135 machine135 learning135", 6),
        ["knowledge135", "vector135", "processor135", "reasoning135", "machine135", "learning135"],
    ),
    (
        ("knowledge135 vector135 processor135 reasoning135 machine135 learning135", 10),
        ["knowledge135", "vector135", "processor135", "reasoning135", "machine135", "learning135"],
    ),
    (
        ("knowledge135 vector135 processor135 reasoning135 machine135 learning135", 18),
        ["knowledge135", "vector135", "processor135", "reasoning135", "machine135", "learning135"],
    ),
    (
        ("knowledge135 vector135 processor135 reasoning135 machine135 learning135", 28),
        ["knowledge135 vector135", "processor135 reasoning135", "machine135 learning135"],
    ),
    (
        ("vector135 processor135 reasoning135 machine135 learning135 model135", 6),
        ["vector135", "processor135", "reasoning135", "machine135", "learning135", "model135"],
    ),
    (
        ("vector135 processor135 reasoning135 machine135 learning135 model135", 10),
        ["vector135", "processor135", "reasoning135", "machine135", "learning135", "model135"],
    ),
    (
        ("vector135 processor135 reasoning135 machine135 learning135 model135", 18),
        ["vector135", "processor135", "reasoning135", "machine135", "learning135", "model135"],
    ),
    (
        ("vector135 processor135 reasoning135 machine135 learning135 model135", 28),
        ["vector135 processor135", "reasoning135 machine135", "learning135 model135"],
    ),
    (
        ("processor135 reasoning135 machine135 learning135 model135 token135", 6),
        ["processor135", "reasoning135", "machine135", "learning135", "model135", "token135"],
    ),
    (
        ("processor135 reasoning135 machine135 learning135 model135 token135", 10),
        ["processor135", "reasoning135", "machine135", "learning135", "model135", "token135"],
    ),
    (
        ("processor135 reasoning135 machine135 learning135 model135 token135", 18),
        ["processor135", "reasoning135", "machine135", "learning135", "model135 token135"],
    ),
    (
        ("processor135 reasoning135 machine135 learning135 model135 token135", 28),
        ["processor135 reasoning135", "machine135 learning135", "model135 token135"],
    ),
    (
        ("reasoning135 machine135 learning135 model135 token135 prompt135", 6),
        ["reasoning135", "machine135", "learning135", "model135", "token135", "prompt135"],
    ),
    (
        ("reasoning135 machine135 learning135 model135 token135 prompt135", 10),
        ["reasoning135", "machine135", "learning135", "model135", "token135", "prompt135"],
    ),
    (
        ("reasoning135 machine135 learning135 model135 token135 prompt135", 18),
        ["reasoning135", "machine135", "learning135", "model135 token135", "prompt135"],
    ),
    (
        ("reasoning135 machine135 learning135 model135 token135 prompt135", 28),
        ["reasoning135 machine135", "learning135 model135", "token135 prompt135"],
    ),
    (
        ("machine135 learning135 model135 token135 prompt135 session135", 6),
        ["machine135", "learning135", "model135", "token135", "prompt135", "session135"],
    ),
    (
        ("machine135 learning135 model135 token135 prompt135 session135", 10),
        ["machine135", "learning135", "model135", "token135", "prompt135", "session135"],
    ),
    (
        ("machine135 learning135 model135 token135 prompt135 session135", 18),
        ["machine135", "learning135", "model135 token135", "prompt135", "session135"],
    ),
    (
        ("machine135 learning135 model135 token135 prompt135 session135", 28),
        ["machine135 learning135", "model135 token135 prompt135", "session135"],
    ),
    (
        ("learning135 model135 token135 prompt135 session135 library135", 6),
        ["learning135", "model135", "token135", "prompt135", "session135", "library135"],
    ),
    (
        ("learning135 model135 token135 prompt135 session135 library135", 10),
        ["learning135", "model135", "token135", "prompt135", "session135", "library135"],
    ),
    (
        ("learning135 model135 token135 prompt135 session135 library135", 18),
        ["learning135", "model135 token135", "prompt135", "session135", "library135"],
    ),
    (
        ("learning135 model135 token135 prompt135 session135 library135", 28),
        ["learning135 model135", "token135 prompt135", "session135 library135"],
    ),
    (
        ("model135 token135 prompt135 session135 library135 service135", 6),
        ["model135", "token135", "prompt135", "session135", "library135", "service135"],
    ),
    (
        ("model135 token135 prompt135 session135 library135 service135", 10),
        ["model135", "token135", "prompt135", "session135", "library135", "service135"],
    ),
    (
        ("model135 token135 prompt135 session135 library135 service135", 18),
        ["model135 token135", "prompt135", "session135", "library135", "service135"],
    ),
    (
        ("model135 token135 prompt135 session135 library135 service135", 28),
        ["model135 token135 prompt135", "session135 library135", "service135"],
    ),
    (
        ("token135 prompt135 session135 library135 service135 gateway135", 6),
        ["token135", "prompt135", "session135", "library135", "service135", "gateway135"],
    ),
    (
        ("token135 prompt135 session135 library135 service135 gateway135", 10),
        ["token135", "prompt135", "session135", "library135", "service135", "gateway135"],
    ),
    (
        ("token135 prompt135 session135 library135 service135 gateway135", 18),
        ["token135 prompt135", "session135", "library135", "service135", "gateway135"],
    ),
    (
        ("token135 prompt135 session135 library135 service135 gateway135", 28),
        ["token135 prompt135", "session135 library135", "service135 gateway135"],
    ),
    (
        ("prompt135 session135 library135 service135 gateway135 storage135", 6),
        ["prompt135", "session135", "library135", "service135", "gateway135", "storage135"],
    ),
    (
        ("prompt135 session135 library135 service135 gateway135 storage135", 10),
        ["prompt135", "session135", "library135", "service135", "gateway135", "storage135"],
    ),
    (
        ("prompt135 session135 library135 service135 gateway135 storage135", 18),
        ["prompt135", "session135", "library135", "service135", "gateway135", "storage135"],
    ),
    (
        ("prompt135 session135 library135 service135 gateway135 storage135", 28),
        ["prompt135 session135", "library135 service135", "gateway135 storage135"],
    ),
    (
        ("session135 library135 service135 gateway135 storage135 network135", 6),
        ["session135", "library135", "service135", "gateway135", "storage135", "network135"],
    ),
    (
        ("session135 library135 service135 gateway135 storage135 network135", 10),
        ["session135", "library135", "service135", "gateway135", "storage135", "network135"],
    ),
    (
        ("session135 library135 service135 gateway135 storage135 network135", 18),
        ["session135", "library135", "service135", "gateway135", "storage135", "network135"],
    ),
    (
        ("session135 library135 service135 gateway135 storage135 network135", 28),
        ["session135 library135", "service135 gateway135", "storage135 network135"],
    ),
    (
        ("library135 service135 gateway135 storage135 network135 latency135", 6),
        ["library135", "service135", "gateway135", "storage135", "network135", "latency135"],
    ),
    (
        ("library135 service135 gateway135 storage135 network135 latency135", 10),
        ["library135", "service135", "gateway135", "storage135", "network135", "latency135"],
    ),
    (
        ("library135 service135 gateway135 storage135 network135 latency135", 18),
        ["library135", "service135", "gateway135", "storage135", "network135", "latency135"],
    ),
    (
        ("library135 service135 gateway135 storage135 network135 latency135", 28),
        ["library135 service135", "gateway135 storage135", "network135 latency135"],
    ),
    (
        ("service135 gateway135 storage135 network135 latency135 buffer135", 6),
        ["service135", "gateway135", "storage135", "network135", "latency135", "buffer135"],
    ),
    (
        ("service135 gateway135 storage135 network135 latency135 buffer135", 10),
        ["service135", "gateway135", "storage135", "network135", "latency135", "buffer135"],
    ),
    (
        ("service135 gateway135 storage135 network135 latency135 buffer135", 18),
        ["service135", "gateway135", "storage135", "network135", "latency135", "buffer135"],
    ),
    (
        ("service135 gateway135 storage135 network135 latency135 buffer135", 28),
        ["service135 gateway135", "storage135 network135", "latency135 buffer135"],
    ),
    (
        ("gateway135 storage135 network135 latency135 buffer135 queue135", 6),
        ["gateway135", "storage135", "network135", "latency135", "buffer135", "queue135"],
    ),
    (
        ("gateway135 storage135 network135 latency135 buffer135 queue135", 10),
        ["gateway135", "storage135", "network135", "latency135", "buffer135", "queue135"],
    ),
    (
        ("gateway135 storage135 network135 latency135 buffer135 queue135", 18),
        ["gateway135", "storage135", "network135", "latency135", "buffer135 queue135"],
    ),
    (
        ("gateway135 storage135 network135 latency135 buffer135 queue135", 28),
        ["gateway135 storage135", "network135 latency135", "buffer135 queue135"],
    ),
    (
        ("storage135 network135 latency135 buffer135 queue135 worker135", 6),
        ["storage135", "network135", "latency135", "buffer135", "queue135", "worker135"],
    ),
    (
        ("storage135 network135 latency135 buffer135 queue135 worker135", 10),
        ["storage135", "network135", "latency135", "buffer135", "queue135", "worker135"],
    ),
    (
        ("storage135 network135 latency135 buffer135 queue135 worker135", 18),
        ["storage135", "network135", "latency135", "buffer135 queue135", "worker135"],
    ),
    (
        ("storage135 network135 latency135 buffer135 queue135 worker135", 28),
        ["storage135 network135", "latency135 buffer135", "queue135 worker135"],
    ),
    (
        ("network135 latency135 buffer135 queue135 worker135 kernel135", 6),
        ["network135", "latency135", "buffer135", "queue135", "worker135", "kernel135"],
    ),
    (
        ("network135 latency135 buffer135 queue135 worker135 kernel135", 10),
        ["network135", "latency135", "buffer135", "queue135", "worker135", "kernel135"],
    ),
    (
        ("network135 latency135 buffer135 queue135 worker135 kernel135", 18),
        ["network135", "latency135", "buffer135 queue135", "worker135", "kernel135"],
    ),
    (
        ("network135 latency135 buffer135 queue135 worker135 kernel135", 28),
        ["network135 latency135", "buffer135 queue135 worker135", "kernel135"],
    ),
    (
        ("latency135 buffer135 queue135 worker135 kernel135 signal135", 6),
        ["latency135", "buffer135", "queue135", "worker135", "kernel135", "signal135"],
    ),
    (
        ("latency135 buffer135 queue135 worker135 kernel135 signal135", 10),
        ["latency135", "buffer135", "queue135", "worker135", "kernel135", "signal135"],
    ),
    (
        ("latency135 buffer135 queue135 worker135 kernel135 signal135", 18),
        ["latency135", "buffer135 queue135", "worker135", "kernel135", "signal135"],
    ),
    (
        ("latency135 buffer135 queue135 worker135 kernel135 signal135", 28),
        ["latency135 buffer135", "queue135 worker135 kernel135", "signal135"],
    ),
    (
        ("buffer135 queue135 worker135 kernel135 signal135 packet135", 6),
        ["buffer135", "queue135", "worker135", "kernel135", "signal135", "packet135"],
    ),
    (
        ("buffer135 queue135 worker135 kernel135 signal135 packet135", 10),
        ["buffer135", "queue135", "worker135", "kernel135", "signal135", "packet135"],
    ),
    (
        ("buffer135 queue135 worker135 kernel135 signal135 packet135", 18),
        ["buffer135 queue135", "worker135", "kernel135", "signal135", "packet135"],
    ),
    (
        ("buffer135 queue135 worker135 kernel135 signal135 packet135", 28),
        ["buffer135 queue135 worker135", "kernel135 signal135", "packet135"],
    ),
    (
        ("queue135 worker135 kernel135 signal135 packet135 router135", 6),
        ["queue135", "worker135", "kernel135", "signal135", "packet135", "router135"],
    ),
    (
        ("queue135 worker135 kernel135 signal135 packet135 router135", 10),
        ["queue135", "worker135", "kernel135", "signal135", "packet135", "router135"],
    ),
    (
        ("queue135 worker135 kernel135 signal135 packet135 router135", 18),
        ["queue135 worker135", "kernel135", "signal135", "packet135", "router135"],
    ),
    (
        ("queue135 worker135 kernel135 signal135 packet135 router135", 28),
        ["queue135 worker135 kernel135", "signal135 packet135", "router135"],
    ),
    (
        ("worker135 kernel135 signal135 packet135 router135 cluster135", 6),
        ["worker135", "kernel135", "signal135", "packet135", "router135", "cluster135"],
    ),
    (
        ("worker135 kernel135 signal135 packet135 router135 cluster135", 10),
        ["worker135", "kernel135", "signal135", "packet135", "router135", "cluster135"],
    ),
    (
        ("worker135 kernel135 signal135 packet135 router135 cluster135", 18),
        ["worker135", "kernel135", "signal135", "packet135", "router135", "cluster135"],
    ),
    (
        ("worker135 kernel135 signal135 packet135 router135 cluster135", 28),
        ["worker135 kernel135", "signal135 packet135", "router135 cluster135"],
    ),
    (
        ("kernel135 signal135 packet135 router135 cluster135 mirror135", 6),
        ["kernel135", "signal135", "packet135", "router135", "cluster135", "mirror135"],
    ),
    (
        ("kernel135 signal135 packet135 router135 cluster135 mirror135", 10),
        ["kernel135", "signal135", "packet135", "router135", "cluster135", "mirror135"],
    ),
    (
        ("kernel135 signal135 packet135 router135 cluster135 mirror135", 18),
        ["kernel135", "signal135", "packet135", "router135", "cluster135", "mirror135"],
    ),
    (
        ("kernel135 signal135 packet135 router135 cluster135 mirror135", 28),
        ["kernel135 signal135", "packet135 router135", "cluster135 mirror135"],
    ),
    (
        ("signal135 packet135 router135 cluster135 mirror135 filter135", 6),
        ["signal135", "packet135", "router135", "cluster135", "mirror135", "filter135"],
    ),
    (
        ("signal135 packet135 router135 cluster135 mirror135 filter135", 10),
        ["signal135", "packet135", "router135", "cluster135", "mirror135", "filter135"],
    ),
    (
        ("signal135 packet135 router135 cluster135 mirror135 filter135", 18),
        ["signal135", "packet135", "router135", "cluster135", "mirror135", "filter135"],
    ),
    (
        ("signal135 packet135 router135 cluster135 mirror135 filter135", 28),
        ["signal135 packet135", "router135 cluster135", "mirror135 filter135"],
    ),
    (
        ("packet135 router135 cluster135 mirror135 filter135 ranking135", 6),
        ["packet135", "router135", "cluster135", "mirror135", "filter135", "ranking135"],
    ),
    (
        ("packet135 router135 cluster135 mirror135 filter135 ranking135", 10),
        ["packet135", "router135", "cluster135", "mirror135", "filter135", "ranking135"],
    ),
    (
        ("packet135 router135 cluster135 mirror135 filter135 ranking135", 18),
        ["packet135", "router135", "cluster135", "mirror135", "filter135", "ranking135"],
    ),
    (
        ("packet135 router135 cluster135 mirror135 filter135 ranking135", 28),
        ["packet135 router135", "cluster135 mirror135", "filter135 ranking135"],
    ),
    (
        ("router135 cluster135 mirror135 filter135 ranking135 encoding135", 6),
        ["router135", "cluster135", "mirror135", "filter135", "ranking135", "encoding135"],
    ),
    (
        ("router135 cluster135 mirror135 filter135 ranking135 encoding135", 10),
        ["router135", "cluster135", "mirror135", "filter135", "ranking135", "encoding135"],
    ),
    (
        ("router135 cluster135 mirror135 filter135 ranking135 encoding135", 18),
        ["router135", "cluster135", "mirror135", "filter135", "ranking135", "encoding135"],
    ),
    (
        ("router135 cluster135 mirror135 filter135 ranking135 encoding135", 28),
        ["router135 cluster135", "mirror135 filter135", "ranking135 encoding135"],
    ),
    (
        ("cluster135 mirror135 filter135 ranking135 encoding135 mapping135", 6),
        ["cluster135", "mirror135", "filter135", "ranking135", "encoding135", "mapping135"],
    ),
    (
        ("cluster135 mirror135 filter135 ranking135 encoding135 mapping135", 10),
        ["cluster135", "mirror135", "filter135", "ranking135", "encoding135", "mapping135"],
    ),
    (
        ("cluster135 mirror135 filter135 ranking135 encoding135 mapping135", 18),
        ["cluster135", "mirror135", "filter135", "ranking135", "encoding135", "mapping135"],
    ),
    (
        ("cluster135 mirror135 filter135 ranking135 encoding135 mapping135", 28),
        ["cluster135 mirror135", "filter135 ranking135", "encoding135 mapping135"],
    ),
    (
        ("mirror135 filter135 ranking135 encoding135 mapping135 record135", 6),
        ["mirror135", "filter135", "ranking135", "encoding135", "mapping135", "record135"],
    ),
    (
        ("mirror135 filter135 ranking135 encoding135 mapping135 record135", 10),
        ["mirror135", "filter135", "ranking135", "encoding135", "mapping135", "record135"],
    ),
    (
        ("mirror135 filter135 ranking135 encoding135 mapping135 record135", 18),
        ["mirror135", "filter135", "ranking135", "encoding135", "mapping135", "record135"],
    ),
    (
        ("mirror135 filter135 ranking135 encoding135 mapping135 record135", 28),
        ["mirror135 filter135", "ranking135 encoding135", "mapping135 record135"],
    ),
    (
        ("filter135 ranking135 encoding135 mapping135 record135 candle135", 6),
        ["filter135", "ranking135", "encoding135", "mapping135", "record135", "candle135"],
    ),
    (
        ("filter135 ranking135 encoding135 mapping135 record135 candle135", 10),
        ["filter135", "ranking135", "encoding135", "mapping135", "record135", "candle135"],
    ),
    (
        ("filter135 ranking135 encoding135 mapping135 record135 candle135", 18),
        ["filter135", "ranking135", "encoding135", "mapping135", "record135", "candle135"],
    ),
    (
        ("filter135 ranking135 encoding135 mapping135 record135 candle135", 28),
        ["filter135 ranking135", "encoding135 mapping135", "record135 candle135"],
    ),
    (
        ("ranking135 encoding135 mapping135 record135 candle135 thread135", 6),
        ["ranking135", "encoding135", "mapping135", "record135", "candle135", "thread135"],
    ),
    (
        ("ranking135 encoding135 mapping135 record135 candle135 thread135", 10),
        ["ranking135", "encoding135", "mapping135", "record135", "candle135", "thread135"],
    ),
    (
        ("ranking135 encoding135 mapping135 record135 candle135 thread135", 18),
        ["ranking135", "encoding135", "mapping135", "record135", "candle135", "thread135"],
    ),
    (
        ("ranking135 encoding135 mapping135 record135 candle135 thread135", 28),
        ["ranking135 encoding135", "mapping135 record135", "candle135 thread135"],
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
