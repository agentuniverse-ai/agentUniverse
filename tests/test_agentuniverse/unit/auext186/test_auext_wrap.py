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
        ("round 186: the quick brown fox jumps over the lazy dog", 4),
        ["round", "186:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", 8),
        ["round", "186: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", 12),
        ["round 186:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", 16),
        ["round 186: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", 24),
        ["round 186: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 186: the quick brown fox jumps over the lazy dog", 32),
        ["round 186: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", 4),
        ["round", "186:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", 8),
        ["round", "186:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", 12),
        ["round 186:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", 16),
        ["round 186:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", 24),
        ["round 186: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 186: agentuniverse is a framework for multi agents", 32),
        ["round 186: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", 4),
        ["round", "186:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", 8),
        ["round", "186:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", 12),
        ["round 186:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", 16),
        ["round 186:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", 24),
        ["round 186: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 186: knowledge stored as vectors enables retrieval", 32),
        ["round 186: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 186: the processor reads the record then stops", 4),
        ["round", "186:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 186: the processor reads the record then stops", 8),
        ["round", "186: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 186: the processor reads the record then stops", 12),
        ["round 186:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 186: the processor reads the record then stops", 16),
        ["round 186: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 186: the processor reads the record then stops", 24),
        ["round 186: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 186: the processor reads the record then stops", 32),
        ["round 186: the processor reads", "the record then stops"],
    ),
    (
        ("round 186: a worker pulls the next task from the queue", 4),
        ["round", "186:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 186: a worker pulls the next task from the queue", 8),
        ["round", "186: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 186: a worker pulls the next task from the queue", 12),
        ["round 186: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 186: a worker pulls the next task from the queue", 16),
        ["round 186: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 186: a worker pulls the next task from the queue", 24),
        ["round 186: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 186: a worker pulls the next task from the queue", 32),
        ["round 186: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 186: signals travel through the network layer", 4),
        ["round", "186:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 186: signals travel through the network layer", 8),
        ["round", "186:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 186: signals travel through the network layer", 12),
        ["round 186:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 186: signals travel through the network layer", 16),
        ["round 186:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 186: signals travel through the network layer", 24),
        ["round 186: signals", "travel through the", "network layer"],
    ),
    (
        ("round 186: signals travel through the network layer", 32),
        ["round 186: signals travel", "through the network layer"],
    ),
    (
        ("round 186: the gateway routes each request by policy", 4),
        ["round", "186:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 186: the gateway routes each request by policy", 8),
        ["round", "186: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 186: the gateway routes each request by policy", 12),
        ["round 186:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 186: the gateway routes each request by policy", 16),
        ["round 186: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 186: the gateway routes each request by policy", 24),
        ["round 186: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 186: the gateway routes each request by policy", 32),
        ["round 186: the gateway routes", "each request by policy"],
    ),
    (
        ("round 186: memory grows until the buffer is full", 4),
        ["round", "186:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 186: memory grows until the buffer is full", 8),
        ["round", "186:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 186: memory grows until the buffer is full", 12),
        ["round 186:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 186: memory grows until the buffer is full", 16),
        ["round 186:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 186: memory grows until the buffer is full", 24), ["round 186: memory grows", "until the buffer is full"]),
    (("round 186: memory grows until the buffer is full", 32), ["round 186: memory grows until", "the buffer is full"]),
    (
        ("round 186: the cluster mirrors every packet twice", 4),
        ["round", "186:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 186: the cluster mirrors every packet twice", 8),
        ["round", "186: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 186: the cluster mirrors every packet twice", 12),
        ["round 186:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 186: the cluster mirrors every packet twice", 16),
        ["round 186: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 186: the cluster mirrors every packet twice", 24),
        ["round 186: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 186: the cluster mirrors every packet twice", 32),
        ["round 186: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", 4),
        ["round", "186:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", 8),
        ["round", "186:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", 12),
        ["round 186:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", 16),
        ["round 186:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", 24),
        ["round 186: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 186: ranking uses tokens learned from the corpus", 32),
        ["round 186: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 186: a long session ends when the candle dies", 4),
        ["round", "186:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 186: a long session ends when the candle dies", 8),
        ["round", "186: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 186: a long session ends when the candle dies", 12),
        ["round 186: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 186: a long session ends when the candle dies", 16),
        ["round 186: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 186: a long session ends when the candle dies", 24),
        ["round 186: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 186: a long session ends when the candle dies", 32),
        ["round 186: a long session ends", "when the candle dies"],
    ),
    (
        ("round 186: encode the prompt then map the result", 4),
        ["round", "186:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 186: encode the prompt then map the result", 8),
        ["round", "186:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 186: encode the prompt then map the result", 12),
        ["round 186:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 186: encode the prompt then map the result", 16),
        ["round 186:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 186: encode the prompt then map the result", 24),
        ["round 186: encode the", "prompt then map the", "result"],
    ),
    (("round 186: encode the prompt then map the result", 32), ["round 186: encode the prompt", "then map the result"]),
    (
        ("round 186: the kernel wakes the worker at dawn", 4),
        ["round", "186:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 186: the kernel wakes the worker at dawn", 8),
        ["round", "186: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 186: the kernel wakes the worker at dawn", 12),
        ["round 186:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 186: the kernel wakes the worker at dawn", 16), ["round 186: the", "kernel wakes the", "worker at dawn"]),
    (("round 186: the kernel wakes the worker at dawn", 24), ["round 186: the kernel", "wakes the worker at dawn"]),
    (("round 186: the kernel wakes the worker at dawn", 32), ["round 186: the kernel wakes the", "worker at dawn"]),
    (
        ("round 186: service latency drops after the patch", 4),
        ["round", "186:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 186: service latency drops after the patch", 8),
        ["round", "186:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 186: service latency drops after the patch", 12),
        ["round 186:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 186: service latency drops after the patch", 16),
        ["round 186:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 186: service latency drops after the patch", 24),
        ["round 186: service", "latency drops after the", "patch"],
    ),
    (("round 186: service latency drops after the patch", 32), ["round 186: service latency drops", "after the patch"]),
    (
        ("round 186: the library caches every vector it sees", 4),
        ["round", "186:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 186: the library caches every vector it sees", 8),
        ["round", "186: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 186: the library caches every vector it sees", 12),
        ["round 186:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 186: the library caches every vector it sees", 16),
        ["round 186: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 186: the library caches every vector it sees", 24),
        ["round 186: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 186: the library caches every vector it sees", 32),
        ["round 186: the library caches", "every vector it sees"],
    ),
    (
        ("round 186: agents argue then the debate resolves", 4),
        ["round", "186:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 186: agents argue then the debate resolves", 8),
        ["round", "186:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 186: agents argue then the debate resolves", 12),
        ["round 186:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 186: agents argue then the debate resolves", 16),
        ["round 186:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 186: agents argue then the debate resolves", 24), ["round 186: agents argue", "then the debate resolves"]),
    (("round 186: agents argue then the debate resolves", 32), ["round 186: agents argue then the", "debate resolves"]),
    (
        ("round 186: the filter keeps only strong matches", 4),
        ["round", "186:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 186: the filter keeps only strong matches", 8),
        ["round", "186: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 186: the filter keeps only strong matches", 12),
        ["round 186:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 186: the filter keeps only strong matches", 16),
        ["round 186: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 186: the filter keeps only strong matches", 24),
        ["round 186: the filter", "keeps only strong", "matches"],
    ),
    (("round 186: the filter keeps only strong matches", 32), ["round 186: the filter keeps only", "strong matches"]),
    (
        ("round 186: the model answers with a short reply", 4),
        ["round", "186:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 186: the model answers with a short reply", 8),
        ["round", "186: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 186: the model answers with a short reply", 12),
        ["round 186:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 186: the model answers with a short reply", 16),
        ["round 186: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 186: the model answers with a short reply", 24),
        ["round 186: the model", "answers with a short", "reply"],
    ),
    (("round 186: the model answers with a short reply", 32), ["round 186: the model answers", "with a short reply"]),
    (
        ("round 186: the recorder stores the reasoning trace", 4),
        ["round", "186:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 186: the recorder stores the reasoning trace", 8),
        ["round", "186: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 186: the recorder stores the reasoning trace", 12),
        ["round 186:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 186: the recorder stores the reasoning trace", 16),
        ["round 186: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 186: the recorder stores the reasoning trace", 24),
        ["round 186: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 186: the recorder stores the reasoning trace", 32),
        ["round 186: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 186: the angel watches the processor run", 4),
        ["round", "186:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 186: the angel watches the processor run", 8),
        ["round", "186: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 186: the angel watches the processor run", 12),
        ["round 186:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 186: the angel watches the processor run", 16),
        ["round 186: the", "angel watches", "the processor", "run"],
    ),
    (("round 186: the angel watches the processor run", 24), ["round 186: the angel", "watches the processor", "run"]),
    (("round 186: the angel watches the processor run", 32), ["round 186: the angel watches the", "processor run"]),
    (
        ("round 186: angle of the vector decides the match", 4),
        ["round", "186:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 186: angle of the vector decides the match", 8),
        ["round", "186:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 186: angle of the vector decides the match", 12),
        ["round 186:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 186: angle of the vector decides the match", 16),
        ["round 186: angle", "of the vector", "decides the", "match"],
    ),
    (("round 186: angle of the vector decides the match", 24), ["round 186: angle of the", "vector decides the match"]),
    (("round 186: angle of the vector decides the match", 32), ["round 186: angle of the vector", "decides the match"]),
    (
        ("round 186: the candle burns twice as long at night", 4),
        ["round", "186:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 186: the candle burns twice as long at night", 8),
        ["round", "186: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 186: the candle burns twice as long at night", 12),
        ["round 186:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 186: the candle burns twice as long at night", 16),
        ["round 186: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 186: the candle burns twice as long at night", 24),
        ["round 186: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 186: the candle burns twice as long at night", 32),
        ["round 186: the candle burns", "twice as long at night"],
    ),
    (
        ("round 186: a mirror of the universe in one line", 4),
        ["round", "186:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 186: a mirror of the universe in one line", 8),
        ["round", "186: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 186: a mirror of the universe in one line", 12),
        ["round 186: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 186: a mirror of the universe in one line", 16),
        ["round 186: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 186: a mirror of the universe in one line", 24), ["round 186: a mirror of", "the universe in one line"]),
    (("round 186: a mirror of the universe in one line", 32), ["round 186: a mirror of the", "universe in one line"]),
    (
        ("round 186: the queue drains before the storm", 4),
        ["round", "186:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 186: the queue drains before the storm", 8),
        ["round", "186: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 186: the queue drains before the storm", 12),
        ["round 186:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 186: the queue drains before the storm", 16), ["round 186: the", "queue drains", "before the storm"]),
    (("round 186: the queue drains before the storm", 24), ["round 186: the queue", "drains before the storm"]),
    (("round 186: the queue drains before the storm", 32), ["round 186: the queue drains", "before the storm"]),
    (
        ("kitten186 sitting186 agent186 angle186 universe186 memory186", 6),
        ["kitten186", "sitting186", "agent186", "angle186", "universe186", "memory186"],
    ),
    (
        ("kitten186 sitting186 agent186 angle186 universe186 memory186", 10),
        ["kitten186", "sitting186", "agent186", "angle186", "universe186", "memory186"],
    ),
    (
        ("kitten186 sitting186 agent186 angle186 universe186 memory186", 18),
        ["kitten186", "sitting186", "agent186 angle186", "universe186", "memory186"],
    ),
    (
        ("kitten186 sitting186 agent186 angle186 universe186 memory186", 28),
        ["kitten186 sitting186", "agent186 angle186", "universe186 memory186"],
    ),
    (
        ("sitting186 agent186 angle186 universe186 memory186 stream186", 6),
        ["sitting186", "agent186", "angle186", "universe186", "memory186", "stream186"],
    ),
    (
        ("sitting186 agent186 angle186 universe186 memory186 stream186", 10),
        ["sitting186", "agent186", "angle186", "universe186", "memory186", "stream186"],
    ),
    (
        ("sitting186 agent186 angle186 universe186 memory186 stream186", 18),
        ["sitting186", "agent186 angle186", "universe186", "memory186", "stream186"],
    ),
    (
        ("sitting186 agent186 angle186 universe186 memory186 stream186", 28),
        ["sitting186 agent186 angle186", "universe186 memory186", "stream186"],
    ),
    (
        ("agent186 angle186 universe186 memory186 stream186 context186", 6),
        ["agent186", "angle186", "universe186", "memory186", "stream186", "context186"],
    ),
    (
        ("agent186 angle186 universe186 memory186 stream186 context186", 10),
        ["agent186", "angle186", "universe186", "memory186", "stream186", "context186"],
    ),
    (
        ("agent186 angle186 universe186 memory186 stream186 context186", 18),
        ["agent186 angle186", "universe186", "memory186", "stream186", "context186"],
    ),
    (
        ("agent186 angle186 universe186 memory186 stream186 context186", 28),
        ["agent186 angle186", "universe186 memory186", "stream186 context186"],
    ),
    (
        ("angle186 universe186 memory186 stream186 context186 knowledge186", 6),
        ["angle186", "universe186", "memory186", "stream186", "context186", "knowledge186"],
    ),
    (
        ("angle186 universe186 memory186 stream186 context186 knowledge186", 10),
        ["angle186", "universe186", "memory186", "stream186", "context186", "knowledge186"],
    ),
    (
        ("angle186 universe186 memory186 stream186 context186 knowledge186", 18),
        ["angle186", "universe186", "memory186", "stream186", "context186", "knowledge186"],
    ),
    (
        ("angle186 universe186 memory186 stream186 context186 knowledge186", 28),
        ["angle186 universe186", "memory186 stream186", "context186 knowledge186"],
    ),
    (
        ("universe186 memory186 stream186 context186 knowledge186 vector186", 6),
        ["universe186", "memory186", "stream186", "context186", "knowledge186", "vector186"],
    ),
    (
        ("universe186 memory186 stream186 context186 knowledge186 vector186", 10),
        ["universe186", "memory186", "stream186", "context186", "knowledge186", "vector186"],
    ),
    (
        ("universe186 memory186 stream186 context186 knowledge186 vector186", 18),
        ["universe186", "memory186", "stream186", "context186", "knowledge186", "vector186"],
    ),
    (
        ("universe186 memory186 stream186 context186 knowledge186 vector186", 28),
        ["universe186 memory186", "stream186 context186", "knowledge186 vector186"],
    ),
    (
        ("memory186 stream186 context186 knowledge186 vector186 processor186", 6),
        ["memory186", "stream186", "context186", "knowledge186", "vector186", "processor186"],
    ),
    (
        ("memory186 stream186 context186 knowledge186 vector186 processor186", 10),
        ["memory186", "stream186", "context186", "knowledge186", "vector186", "processor186"],
    ),
    (
        ("memory186 stream186 context186 knowledge186 vector186 processor186", 18),
        ["memory186", "stream186", "context186", "knowledge186", "vector186", "processor186"],
    ),
    (
        ("memory186 stream186 context186 knowledge186 vector186 processor186", 28),
        ["memory186 stream186", "context186 knowledge186", "vector186 processor186"],
    ),
    (
        ("stream186 context186 knowledge186 vector186 processor186 reasoning186", 6),
        ["stream186", "context186", "knowledge186", "vector186", "processor186", "reasoning186"],
    ),
    (
        ("stream186 context186 knowledge186 vector186 processor186 reasoning186", 10),
        ["stream186", "context186", "knowledge186", "vector186", "processor186", "reasoning186"],
    ),
    (
        ("stream186 context186 knowledge186 vector186 processor186 reasoning186", 18),
        ["stream186", "context186", "knowledge186", "vector186", "processor186", "reasoning186"],
    ),
    (
        ("stream186 context186 knowledge186 vector186 processor186 reasoning186", 28),
        ["stream186 context186", "knowledge186 vector186", "processor186 reasoning186"],
    ),
    (
        ("context186 knowledge186 vector186 processor186 reasoning186 machine186", 6),
        ["context186", "knowledge186", "vector186", "processor186", "reasoning186", "machine186"],
    ),
    (
        ("context186 knowledge186 vector186 processor186 reasoning186 machine186", 10),
        ["context186", "knowledge186", "vector186", "processor186", "reasoning186", "machine186"],
    ),
    (
        ("context186 knowledge186 vector186 processor186 reasoning186 machine186", 18),
        ["context186", "knowledge186", "vector186", "processor186", "reasoning186", "machine186"],
    ),
    (
        ("context186 knowledge186 vector186 processor186 reasoning186 machine186", 28),
        ["context186 knowledge186", "vector186 processor186", "reasoning186 machine186"],
    ),
    (
        ("knowledge186 vector186 processor186 reasoning186 machine186 learning186", 6),
        ["knowledge186", "vector186", "processor186", "reasoning186", "machine186", "learning186"],
    ),
    (
        ("knowledge186 vector186 processor186 reasoning186 machine186 learning186", 10),
        ["knowledge186", "vector186", "processor186", "reasoning186", "machine186", "learning186"],
    ),
    (
        ("knowledge186 vector186 processor186 reasoning186 machine186 learning186", 18),
        ["knowledge186", "vector186", "processor186", "reasoning186", "machine186", "learning186"],
    ),
    (
        ("knowledge186 vector186 processor186 reasoning186 machine186 learning186", 28),
        ["knowledge186 vector186", "processor186 reasoning186", "machine186 learning186"],
    ),
    (
        ("vector186 processor186 reasoning186 machine186 learning186 model186", 6),
        ["vector186", "processor186", "reasoning186", "machine186", "learning186", "model186"],
    ),
    (
        ("vector186 processor186 reasoning186 machine186 learning186 model186", 10),
        ["vector186", "processor186", "reasoning186", "machine186", "learning186", "model186"],
    ),
    (
        ("vector186 processor186 reasoning186 machine186 learning186 model186", 18),
        ["vector186", "processor186", "reasoning186", "machine186", "learning186", "model186"],
    ),
    (
        ("vector186 processor186 reasoning186 machine186 learning186 model186", 28),
        ["vector186 processor186", "reasoning186 machine186", "learning186 model186"],
    ),
    (
        ("processor186 reasoning186 machine186 learning186 model186 token186", 6),
        ["processor186", "reasoning186", "machine186", "learning186", "model186", "token186"],
    ),
    (
        ("processor186 reasoning186 machine186 learning186 model186 token186", 10),
        ["processor186", "reasoning186", "machine186", "learning186", "model186", "token186"],
    ),
    (
        ("processor186 reasoning186 machine186 learning186 model186 token186", 18),
        ["processor186", "reasoning186", "machine186", "learning186", "model186 token186"],
    ),
    (
        ("processor186 reasoning186 machine186 learning186 model186 token186", 28),
        ["processor186 reasoning186", "machine186 learning186", "model186 token186"],
    ),
    (
        ("reasoning186 machine186 learning186 model186 token186 prompt186", 6),
        ["reasoning186", "machine186", "learning186", "model186", "token186", "prompt186"],
    ),
    (
        ("reasoning186 machine186 learning186 model186 token186 prompt186", 10),
        ["reasoning186", "machine186", "learning186", "model186", "token186", "prompt186"],
    ),
    (
        ("reasoning186 machine186 learning186 model186 token186 prompt186", 18),
        ["reasoning186", "machine186", "learning186", "model186 token186", "prompt186"],
    ),
    (
        ("reasoning186 machine186 learning186 model186 token186 prompt186", 28),
        ["reasoning186 machine186", "learning186 model186", "token186 prompt186"],
    ),
    (
        ("machine186 learning186 model186 token186 prompt186 session186", 6),
        ["machine186", "learning186", "model186", "token186", "prompt186", "session186"],
    ),
    (
        ("machine186 learning186 model186 token186 prompt186 session186", 10),
        ["machine186", "learning186", "model186", "token186", "prompt186", "session186"],
    ),
    (
        ("machine186 learning186 model186 token186 prompt186 session186", 18),
        ["machine186", "learning186", "model186 token186", "prompt186", "session186"],
    ),
    (
        ("machine186 learning186 model186 token186 prompt186 session186", 28),
        ["machine186 learning186", "model186 token186 prompt186", "session186"],
    ),
    (
        ("learning186 model186 token186 prompt186 session186 library186", 6),
        ["learning186", "model186", "token186", "prompt186", "session186", "library186"],
    ),
    (
        ("learning186 model186 token186 prompt186 session186 library186", 10),
        ["learning186", "model186", "token186", "prompt186", "session186", "library186"],
    ),
    (
        ("learning186 model186 token186 prompt186 session186 library186", 18),
        ["learning186", "model186 token186", "prompt186", "session186", "library186"],
    ),
    (
        ("learning186 model186 token186 prompt186 session186 library186", 28),
        ["learning186 model186", "token186 prompt186", "session186 library186"],
    ),
    (
        ("model186 token186 prompt186 session186 library186 service186", 6),
        ["model186", "token186", "prompt186", "session186", "library186", "service186"],
    ),
    (
        ("model186 token186 prompt186 session186 library186 service186", 10),
        ["model186", "token186", "prompt186", "session186", "library186", "service186"],
    ),
    (
        ("model186 token186 prompt186 session186 library186 service186", 18),
        ["model186 token186", "prompt186", "session186", "library186", "service186"],
    ),
    (
        ("model186 token186 prompt186 session186 library186 service186", 28),
        ["model186 token186 prompt186", "session186 library186", "service186"],
    ),
    (
        ("token186 prompt186 session186 library186 service186 gateway186", 6),
        ["token186", "prompt186", "session186", "library186", "service186", "gateway186"],
    ),
    (
        ("token186 prompt186 session186 library186 service186 gateway186", 10),
        ["token186", "prompt186", "session186", "library186", "service186", "gateway186"],
    ),
    (
        ("token186 prompt186 session186 library186 service186 gateway186", 18),
        ["token186 prompt186", "session186", "library186", "service186", "gateway186"],
    ),
    (
        ("token186 prompt186 session186 library186 service186 gateway186", 28),
        ["token186 prompt186", "session186 library186", "service186 gateway186"],
    ),
    (
        ("prompt186 session186 library186 service186 gateway186 storage186", 6),
        ["prompt186", "session186", "library186", "service186", "gateway186", "storage186"],
    ),
    (
        ("prompt186 session186 library186 service186 gateway186 storage186", 10),
        ["prompt186", "session186", "library186", "service186", "gateway186", "storage186"],
    ),
    (
        ("prompt186 session186 library186 service186 gateway186 storage186", 18),
        ["prompt186", "session186", "library186", "service186", "gateway186", "storage186"],
    ),
    (
        ("prompt186 session186 library186 service186 gateway186 storage186", 28),
        ["prompt186 session186", "library186 service186", "gateway186 storage186"],
    ),
    (
        ("session186 library186 service186 gateway186 storage186 network186", 6),
        ["session186", "library186", "service186", "gateway186", "storage186", "network186"],
    ),
    (
        ("session186 library186 service186 gateway186 storage186 network186", 10),
        ["session186", "library186", "service186", "gateway186", "storage186", "network186"],
    ),
    (
        ("session186 library186 service186 gateway186 storage186 network186", 18),
        ["session186", "library186", "service186", "gateway186", "storage186", "network186"],
    ),
    (
        ("session186 library186 service186 gateway186 storage186 network186", 28),
        ["session186 library186", "service186 gateway186", "storage186 network186"],
    ),
    (
        ("library186 service186 gateway186 storage186 network186 latency186", 6),
        ["library186", "service186", "gateway186", "storage186", "network186", "latency186"],
    ),
    (
        ("library186 service186 gateway186 storage186 network186 latency186", 10),
        ["library186", "service186", "gateway186", "storage186", "network186", "latency186"],
    ),
    (
        ("library186 service186 gateway186 storage186 network186 latency186", 18),
        ["library186", "service186", "gateway186", "storage186", "network186", "latency186"],
    ),
    (
        ("library186 service186 gateway186 storage186 network186 latency186", 28),
        ["library186 service186", "gateway186 storage186", "network186 latency186"],
    ),
    (
        ("service186 gateway186 storage186 network186 latency186 buffer186", 6),
        ["service186", "gateway186", "storage186", "network186", "latency186", "buffer186"],
    ),
    (
        ("service186 gateway186 storage186 network186 latency186 buffer186", 10),
        ["service186", "gateway186", "storage186", "network186", "latency186", "buffer186"],
    ),
    (
        ("service186 gateway186 storage186 network186 latency186 buffer186", 18),
        ["service186", "gateway186", "storage186", "network186", "latency186", "buffer186"],
    ),
    (
        ("service186 gateway186 storage186 network186 latency186 buffer186", 28),
        ["service186 gateway186", "storage186 network186", "latency186 buffer186"],
    ),
    (
        ("gateway186 storage186 network186 latency186 buffer186 queue186", 6),
        ["gateway186", "storage186", "network186", "latency186", "buffer186", "queue186"],
    ),
    (
        ("gateway186 storage186 network186 latency186 buffer186 queue186", 10),
        ["gateway186", "storage186", "network186", "latency186", "buffer186", "queue186"],
    ),
    (
        ("gateway186 storage186 network186 latency186 buffer186 queue186", 18),
        ["gateway186", "storage186", "network186", "latency186", "buffer186 queue186"],
    ),
    (
        ("gateway186 storage186 network186 latency186 buffer186 queue186", 28),
        ["gateway186 storage186", "network186 latency186", "buffer186 queue186"],
    ),
    (
        ("storage186 network186 latency186 buffer186 queue186 worker186", 6),
        ["storage186", "network186", "latency186", "buffer186", "queue186", "worker186"],
    ),
    (
        ("storage186 network186 latency186 buffer186 queue186 worker186", 10),
        ["storage186", "network186", "latency186", "buffer186", "queue186", "worker186"],
    ),
    (
        ("storage186 network186 latency186 buffer186 queue186 worker186", 18),
        ["storage186", "network186", "latency186", "buffer186 queue186", "worker186"],
    ),
    (
        ("storage186 network186 latency186 buffer186 queue186 worker186", 28),
        ["storage186 network186", "latency186 buffer186", "queue186 worker186"],
    ),
    (
        ("network186 latency186 buffer186 queue186 worker186 kernel186", 6),
        ["network186", "latency186", "buffer186", "queue186", "worker186", "kernel186"],
    ),
    (
        ("network186 latency186 buffer186 queue186 worker186 kernel186", 10),
        ["network186", "latency186", "buffer186", "queue186", "worker186", "kernel186"],
    ),
    (
        ("network186 latency186 buffer186 queue186 worker186 kernel186", 18),
        ["network186", "latency186", "buffer186 queue186", "worker186", "kernel186"],
    ),
    (
        ("network186 latency186 buffer186 queue186 worker186 kernel186", 28),
        ["network186 latency186", "buffer186 queue186 worker186", "kernel186"],
    ),
    (
        ("latency186 buffer186 queue186 worker186 kernel186 signal186", 6),
        ["latency186", "buffer186", "queue186", "worker186", "kernel186", "signal186"],
    ),
    (
        ("latency186 buffer186 queue186 worker186 kernel186 signal186", 10),
        ["latency186", "buffer186", "queue186", "worker186", "kernel186", "signal186"],
    ),
    (
        ("latency186 buffer186 queue186 worker186 kernel186 signal186", 18),
        ["latency186", "buffer186 queue186", "worker186", "kernel186", "signal186"],
    ),
    (
        ("latency186 buffer186 queue186 worker186 kernel186 signal186", 28),
        ["latency186 buffer186", "queue186 worker186 kernel186", "signal186"],
    ),
    (
        ("buffer186 queue186 worker186 kernel186 signal186 packet186", 6),
        ["buffer186", "queue186", "worker186", "kernel186", "signal186", "packet186"],
    ),
    (
        ("buffer186 queue186 worker186 kernel186 signal186 packet186", 10),
        ["buffer186", "queue186", "worker186", "kernel186", "signal186", "packet186"],
    ),
    (
        ("buffer186 queue186 worker186 kernel186 signal186 packet186", 18),
        ["buffer186 queue186", "worker186", "kernel186", "signal186", "packet186"],
    ),
    (
        ("buffer186 queue186 worker186 kernel186 signal186 packet186", 28),
        ["buffer186 queue186 worker186", "kernel186 signal186", "packet186"],
    ),
    (
        ("queue186 worker186 kernel186 signal186 packet186 router186", 6),
        ["queue186", "worker186", "kernel186", "signal186", "packet186", "router186"],
    ),
    (
        ("queue186 worker186 kernel186 signal186 packet186 router186", 10),
        ["queue186", "worker186", "kernel186", "signal186", "packet186", "router186"],
    ),
    (
        ("queue186 worker186 kernel186 signal186 packet186 router186", 18),
        ["queue186 worker186", "kernel186", "signal186", "packet186", "router186"],
    ),
    (
        ("queue186 worker186 kernel186 signal186 packet186 router186", 28),
        ["queue186 worker186 kernel186", "signal186 packet186", "router186"],
    ),
    (
        ("worker186 kernel186 signal186 packet186 router186 cluster186", 6),
        ["worker186", "kernel186", "signal186", "packet186", "router186", "cluster186"],
    ),
    (
        ("worker186 kernel186 signal186 packet186 router186 cluster186", 10),
        ["worker186", "kernel186", "signal186", "packet186", "router186", "cluster186"],
    ),
    (
        ("worker186 kernel186 signal186 packet186 router186 cluster186", 18),
        ["worker186", "kernel186", "signal186", "packet186", "router186", "cluster186"],
    ),
    (
        ("worker186 kernel186 signal186 packet186 router186 cluster186", 28),
        ["worker186 kernel186", "signal186 packet186", "router186 cluster186"],
    ),
    (
        ("kernel186 signal186 packet186 router186 cluster186 mirror186", 6),
        ["kernel186", "signal186", "packet186", "router186", "cluster186", "mirror186"],
    ),
    (
        ("kernel186 signal186 packet186 router186 cluster186 mirror186", 10),
        ["kernel186", "signal186", "packet186", "router186", "cluster186", "mirror186"],
    ),
    (
        ("kernel186 signal186 packet186 router186 cluster186 mirror186", 18),
        ["kernel186", "signal186", "packet186", "router186", "cluster186", "mirror186"],
    ),
    (
        ("kernel186 signal186 packet186 router186 cluster186 mirror186", 28),
        ["kernel186 signal186", "packet186 router186", "cluster186 mirror186"],
    ),
    (
        ("signal186 packet186 router186 cluster186 mirror186 filter186", 6),
        ["signal186", "packet186", "router186", "cluster186", "mirror186", "filter186"],
    ),
    (
        ("signal186 packet186 router186 cluster186 mirror186 filter186", 10),
        ["signal186", "packet186", "router186", "cluster186", "mirror186", "filter186"],
    ),
    (
        ("signal186 packet186 router186 cluster186 mirror186 filter186", 18),
        ["signal186", "packet186", "router186", "cluster186", "mirror186", "filter186"],
    ),
    (
        ("signal186 packet186 router186 cluster186 mirror186 filter186", 28),
        ["signal186 packet186", "router186 cluster186", "mirror186 filter186"],
    ),
    (
        ("packet186 router186 cluster186 mirror186 filter186 ranking186", 6),
        ["packet186", "router186", "cluster186", "mirror186", "filter186", "ranking186"],
    ),
    (
        ("packet186 router186 cluster186 mirror186 filter186 ranking186", 10),
        ["packet186", "router186", "cluster186", "mirror186", "filter186", "ranking186"],
    ),
    (
        ("packet186 router186 cluster186 mirror186 filter186 ranking186", 18),
        ["packet186", "router186", "cluster186", "mirror186", "filter186", "ranking186"],
    ),
    (
        ("packet186 router186 cluster186 mirror186 filter186 ranking186", 28),
        ["packet186 router186", "cluster186 mirror186", "filter186 ranking186"],
    ),
    (
        ("router186 cluster186 mirror186 filter186 ranking186 encoding186", 6),
        ["router186", "cluster186", "mirror186", "filter186", "ranking186", "encoding186"],
    ),
    (
        ("router186 cluster186 mirror186 filter186 ranking186 encoding186", 10),
        ["router186", "cluster186", "mirror186", "filter186", "ranking186", "encoding186"],
    ),
    (
        ("router186 cluster186 mirror186 filter186 ranking186 encoding186", 18),
        ["router186", "cluster186", "mirror186", "filter186", "ranking186", "encoding186"],
    ),
    (
        ("router186 cluster186 mirror186 filter186 ranking186 encoding186", 28),
        ["router186 cluster186", "mirror186 filter186", "ranking186 encoding186"],
    ),
    (
        ("cluster186 mirror186 filter186 ranking186 encoding186 mapping186", 6),
        ["cluster186", "mirror186", "filter186", "ranking186", "encoding186", "mapping186"],
    ),
    (
        ("cluster186 mirror186 filter186 ranking186 encoding186 mapping186", 10),
        ["cluster186", "mirror186", "filter186", "ranking186", "encoding186", "mapping186"],
    ),
    (
        ("cluster186 mirror186 filter186 ranking186 encoding186 mapping186", 18),
        ["cluster186", "mirror186", "filter186", "ranking186", "encoding186", "mapping186"],
    ),
    (
        ("cluster186 mirror186 filter186 ranking186 encoding186 mapping186", 28),
        ["cluster186 mirror186", "filter186 ranking186", "encoding186 mapping186"],
    ),
    (
        ("mirror186 filter186 ranking186 encoding186 mapping186 record186", 6),
        ["mirror186", "filter186", "ranking186", "encoding186", "mapping186", "record186"],
    ),
    (
        ("mirror186 filter186 ranking186 encoding186 mapping186 record186", 10),
        ["mirror186", "filter186", "ranking186", "encoding186", "mapping186", "record186"],
    ),
    (
        ("mirror186 filter186 ranking186 encoding186 mapping186 record186", 18),
        ["mirror186", "filter186", "ranking186", "encoding186", "mapping186", "record186"],
    ),
    (
        ("mirror186 filter186 ranking186 encoding186 mapping186 record186", 28),
        ["mirror186 filter186", "ranking186 encoding186", "mapping186 record186"],
    ),
    (
        ("filter186 ranking186 encoding186 mapping186 record186 candle186", 6),
        ["filter186", "ranking186", "encoding186", "mapping186", "record186", "candle186"],
    ),
    (
        ("filter186 ranking186 encoding186 mapping186 record186 candle186", 10),
        ["filter186", "ranking186", "encoding186", "mapping186", "record186", "candle186"],
    ),
    (
        ("filter186 ranking186 encoding186 mapping186 record186 candle186", 18),
        ["filter186", "ranking186", "encoding186", "mapping186", "record186", "candle186"],
    ),
    (
        ("filter186 ranking186 encoding186 mapping186 record186 candle186", 28),
        ["filter186 ranking186", "encoding186 mapping186", "record186 candle186"],
    ),
    (
        ("ranking186 encoding186 mapping186 record186 candle186 thread186", 6),
        ["ranking186", "encoding186", "mapping186", "record186", "candle186", "thread186"],
    ),
    (
        ("ranking186 encoding186 mapping186 record186 candle186 thread186", 10),
        ["ranking186", "encoding186", "mapping186", "record186", "candle186", "thread186"],
    ),
    (
        ("ranking186 encoding186 mapping186 record186 candle186 thread186", 18),
        ["ranking186", "encoding186", "mapping186", "record186", "candle186", "thread186"],
    ),
    (
        ("ranking186 encoding186 mapping186 record186 candle186 thread186", 28),
        ["ranking186 encoding186", "mapping186 record186", "candle186 thread186"],
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
