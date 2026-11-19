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
        ("round 149: the quick brown fox jumps over the lazy dog", 4),
        ["round", "149:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", 8),
        ["round", "149: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", 12),
        ["round 149:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", 16),
        ["round 149: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", 24),
        ["round 149: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 149: the quick brown fox jumps over the lazy dog", 32),
        ["round 149: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", 4),
        ["round", "149:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", 8),
        ["round", "149:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", 12),
        ["round 149:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", 16),
        ["round 149:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", 24),
        ["round 149: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 149: agentuniverse is a framework for multi agents", 32),
        ["round 149: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", 4),
        ["round", "149:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", 8),
        ["round", "149:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", 12),
        ["round 149:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", 16),
        ["round 149:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", 24),
        ["round 149: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 149: knowledge stored as vectors enables retrieval", 32),
        ["round 149: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 149: the processor reads the record then stops", 4),
        ["round", "149:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 149: the processor reads the record then stops", 8),
        ["round", "149: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 149: the processor reads the record then stops", 12),
        ["round 149:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 149: the processor reads the record then stops", 16),
        ["round 149: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 149: the processor reads the record then stops", 24),
        ["round 149: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 149: the processor reads the record then stops", 32),
        ["round 149: the processor reads", "the record then stops"],
    ),
    (
        ("round 149: a worker pulls the next task from the queue", 4),
        ["round", "149:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 149: a worker pulls the next task from the queue", 8),
        ["round", "149: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 149: a worker pulls the next task from the queue", 12),
        ["round 149: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 149: a worker pulls the next task from the queue", 16),
        ["round 149: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 149: a worker pulls the next task from the queue", 24),
        ["round 149: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 149: a worker pulls the next task from the queue", 32),
        ["round 149: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 149: signals travel through the network layer", 4),
        ["round", "149:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 149: signals travel through the network layer", 8),
        ["round", "149:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 149: signals travel through the network layer", 12),
        ["round 149:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 149: signals travel through the network layer", 16),
        ["round 149:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 149: signals travel through the network layer", 24),
        ["round 149: signals", "travel through the", "network layer"],
    ),
    (
        ("round 149: signals travel through the network layer", 32),
        ["round 149: signals travel", "through the network layer"],
    ),
    (
        ("round 149: the gateway routes each request by policy", 4),
        ["round", "149:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 149: the gateway routes each request by policy", 8),
        ["round", "149: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 149: the gateway routes each request by policy", 12),
        ["round 149:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 149: the gateway routes each request by policy", 16),
        ["round 149: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 149: the gateway routes each request by policy", 24),
        ["round 149: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 149: the gateway routes each request by policy", 32),
        ["round 149: the gateway routes", "each request by policy"],
    ),
    (
        ("round 149: memory grows until the buffer is full", 4),
        ["round", "149:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 149: memory grows until the buffer is full", 8),
        ["round", "149:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 149: memory grows until the buffer is full", 12),
        ["round 149:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 149: memory grows until the buffer is full", 16),
        ["round 149:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 149: memory grows until the buffer is full", 24), ["round 149: memory grows", "until the buffer is full"]),
    (("round 149: memory grows until the buffer is full", 32), ["round 149: memory grows until", "the buffer is full"]),
    (
        ("round 149: the cluster mirrors every packet twice", 4),
        ["round", "149:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 149: the cluster mirrors every packet twice", 8),
        ["round", "149: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 149: the cluster mirrors every packet twice", 12),
        ["round 149:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 149: the cluster mirrors every packet twice", 16),
        ["round 149: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 149: the cluster mirrors every packet twice", 24),
        ["round 149: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 149: the cluster mirrors every packet twice", 32),
        ["round 149: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", 4),
        ["round", "149:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", 8),
        ["round", "149:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", 12),
        ["round 149:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", 16),
        ["round 149:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", 24),
        ["round 149: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 149: ranking uses tokens learned from the corpus", 32),
        ["round 149: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 149: a long session ends when the candle dies", 4),
        ["round", "149:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 149: a long session ends when the candle dies", 8),
        ["round", "149: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 149: a long session ends when the candle dies", 12),
        ["round 149: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 149: a long session ends when the candle dies", 16),
        ["round 149: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 149: a long session ends when the candle dies", 24),
        ["round 149: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 149: a long session ends when the candle dies", 32),
        ["round 149: a long session ends", "when the candle dies"],
    ),
    (
        ("round 149: encode the prompt then map the result", 4),
        ["round", "149:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 149: encode the prompt then map the result", 8),
        ["round", "149:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 149: encode the prompt then map the result", 12),
        ["round 149:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 149: encode the prompt then map the result", 16),
        ["round 149:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 149: encode the prompt then map the result", 24),
        ["round 149: encode the", "prompt then map the", "result"],
    ),
    (("round 149: encode the prompt then map the result", 32), ["round 149: encode the prompt", "then map the result"]),
    (
        ("round 149: the kernel wakes the worker at dawn", 4),
        ["round", "149:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 149: the kernel wakes the worker at dawn", 8),
        ["round", "149: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 149: the kernel wakes the worker at dawn", 12),
        ["round 149:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 149: the kernel wakes the worker at dawn", 16), ["round 149: the", "kernel wakes the", "worker at dawn"]),
    (("round 149: the kernel wakes the worker at dawn", 24), ["round 149: the kernel", "wakes the worker at dawn"]),
    (("round 149: the kernel wakes the worker at dawn", 32), ["round 149: the kernel wakes the", "worker at dawn"]),
    (
        ("round 149: service latency drops after the patch", 4),
        ["round", "149:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 149: service latency drops after the patch", 8),
        ["round", "149:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 149: service latency drops after the patch", 12),
        ["round 149:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 149: service latency drops after the patch", 16),
        ["round 149:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 149: service latency drops after the patch", 24),
        ["round 149: service", "latency drops after the", "patch"],
    ),
    (("round 149: service latency drops after the patch", 32), ["round 149: service latency drops", "after the patch"]),
    (
        ("round 149: the library caches every vector it sees", 4),
        ["round", "149:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 149: the library caches every vector it sees", 8),
        ["round", "149: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 149: the library caches every vector it sees", 12),
        ["round 149:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 149: the library caches every vector it sees", 16),
        ["round 149: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 149: the library caches every vector it sees", 24),
        ["round 149: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 149: the library caches every vector it sees", 32),
        ["round 149: the library caches", "every vector it sees"],
    ),
    (
        ("round 149: agents argue then the debate resolves", 4),
        ["round", "149:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 149: agents argue then the debate resolves", 8),
        ["round", "149:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 149: agents argue then the debate resolves", 12),
        ["round 149:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 149: agents argue then the debate resolves", 16),
        ["round 149:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 149: agents argue then the debate resolves", 24), ["round 149: agents argue", "then the debate resolves"]),
    (("round 149: agents argue then the debate resolves", 32), ["round 149: agents argue then the", "debate resolves"]),
    (
        ("round 149: the filter keeps only strong matches", 4),
        ["round", "149:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 149: the filter keeps only strong matches", 8),
        ["round", "149: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 149: the filter keeps only strong matches", 12),
        ["round 149:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 149: the filter keeps only strong matches", 16),
        ["round 149: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 149: the filter keeps only strong matches", 24),
        ["round 149: the filter", "keeps only strong", "matches"],
    ),
    (("round 149: the filter keeps only strong matches", 32), ["round 149: the filter keeps only", "strong matches"]),
    (
        ("round 149: the model answers with a short reply", 4),
        ["round", "149:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 149: the model answers with a short reply", 8),
        ["round", "149: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 149: the model answers with a short reply", 12),
        ["round 149:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 149: the model answers with a short reply", 16),
        ["round 149: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 149: the model answers with a short reply", 24),
        ["round 149: the model", "answers with a short", "reply"],
    ),
    (("round 149: the model answers with a short reply", 32), ["round 149: the model answers", "with a short reply"]),
    (
        ("round 149: the recorder stores the reasoning trace", 4),
        ["round", "149:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 149: the recorder stores the reasoning trace", 8),
        ["round", "149: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 149: the recorder stores the reasoning trace", 12),
        ["round 149:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 149: the recorder stores the reasoning trace", 16),
        ["round 149: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 149: the recorder stores the reasoning trace", 24),
        ["round 149: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 149: the recorder stores the reasoning trace", 32),
        ["round 149: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 149: the angel watches the processor run", 4),
        ["round", "149:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 149: the angel watches the processor run", 8),
        ["round", "149: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 149: the angel watches the processor run", 12),
        ["round 149:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 149: the angel watches the processor run", 16),
        ["round 149: the", "angel watches", "the processor", "run"],
    ),
    (("round 149: the angel watches the processor run", 24), ["round 149: the angel", "watches the processor", "run"]),
    (("round 149: the angel watches the processor run", 32), ["round 149: the angel watches the", "processor run"]),
    (
        ("round 149: angle of the vector decides the match", 4),
        ["round", "149:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 149: angle of the vector decides the match", 8),
        ["round", "149:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 149: angle of the vector decides the match", 12),
        ["round 149:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 149: angle of the vector decides the match", 16),
        ["round 149: angle", "of the vector", "decides the", "match"],
    ),
    (("round 149: angle of the vector decides the match", 24), ["round 149: angle of the", "vector decides the match"]),
    (("round 149: angle of the vector decides the match", 32), ["round 149: angle of the vector", "decides the match"]),
    (
        ("round 149: the candle burns twice as long at night", 4),
        ["round", "149:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 149: the candle burns twice as long at night", 8),
        ["round", "149: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 149: the candle burns twice as long at night", 12),
        ["round 149:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 149: the candle burns twice as long at night", 16),
        ["round 149: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 149: the candle burns twice as long at night", 24),
        ["round 149: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 149: the candle burns twice as long at night", 32),
        ["round 149: the candle burns", "twice as long at night"],
    ),
    (
        ("round 149: a mirror of the universe in one line", 4),
        ["round", "149:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 149: a mirror of the universe in one line", 8),
        ["round", "149: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 149: a mirror of the universe in one line", 12),
        ["round 149: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 149: a mirror of the universe in one line", 16),
        ["round 149: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 149: a mirror of the universe in one line", 24), ["round 149: a mirror of", "the universe in one line"]),
    (("round 149: a mirror of the universe in one line", 32), ["round 149: a mirror of the", "universe in one line"]),
    (
        ("round 149: the queue drains before the storm", 4),
        ["round", "149:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 149: the queue drains before the storm", 8),
        ["round", "149: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 149: the queue drains before the storm", 12),
        ["round 149:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 149: the queue drains before the storm", 16), ["round 149: the", "queue drains", "before the storm"]),
    (("round 149: the queue drains before the storm", 24), ["round 149: the queue", "drains before the storm"]),
    (("round 149: the queue drains before the storm", 32), ["round 149: the queue drains", "before the storm"]),
    (
        ("kitten149 sitting149 agent149 angle149 universe149 memory149", 6),
        ["kitten149", "sitting149", "agent149", "angle149", "universe149", "memory149"],
    ),
    (
        ("kitten149 sitting149 agent149 angle149 universe149 memory149", 10),
        ["kitten149", "sitting149", "agent149", "angle149", "universe149", "memory149"],
    ),
    (
        ("kitten149 sitting149 agent149 angle149 universe149 memory149", 18),
        ["kitten149", "sitting149", "agent149 angle149", "universe149", "memory149"],
    ),
    (
        ("kitten149 sitting149 agent149 angle149 universe149 memory149", 28),
        ["kitten149 sitting149", "agent149 angle149", "universe149 memory149"],
    ),
    (
        ("sitting149 agent149 angle149 universe149 memory149 stream149", 6),
        ["sitting149", "agent149", "angle149", "universe149", "memory149", "stream149"],
    ),
    (
        ("sitting149 agent149 angle149 universe149 memory149 stream149", 10),
        ["sitting149", "agent149", "angle149", "universe149", "memory149", "stream149"],
    ),
    (
        ("sitting149 agent149 angle149 universe149 memory149 stream149", 18),
        ["sitting149", "agent149 angle149", "universe149", "memory149", "stream149"],
    ),
    (
        ("sitting149 agent149 angle149 universe149 memory149 stream149", 28),
        ["sitting149 agent149 angle149", "universe149 memory149", "stream149"],
    ),
    (
        ("agent149 angle149 universe149 memory149 stream149 context149", 6),
        ["agent149", "angle149", "universe149", "memory149", "stream149", "context149"],
    ),
    (
        ("agent149 angle149 universe149 memory149 stream149 context149", 10),
        ["agent149", "angle149", "universe149", "memory149", "stream149", "context149"],
    ),
    (
        ("agent149 angle149 universe149 memory149 stream149 context149", 18),
        ["agent149 angle149", "universe149", "memory149", "stream149", "context149"],
    ),
    (
        ("agent149 angle149 universe149 memory149 stream149 context149", 28),
        ["agent149 angle149", "universe149 memory149", "stream149 context149"],
    ),
    (
        ("angle149 universe149 memory149 stream149 context149 knowledge149", 6),
        ["angle149", "universe149", "memory149", "stream149", "context149", "knowledge149"],
    ),
    (
        ("angle149 universe149 memory149 stream149 context149 knowledge149", 10),
        ["angle149", "universe149", "memory149", "stream149", "context149", "knowledge149"],
    ),
    (
        ("angle149 universe149 memory149 stream149 context149 knowledge149", 18),
        ["angle149", "universe149", "memory149", "stream149", "context149", "knowledge149"],
    ),
    (
        ("angle149 universe149 memory149 stream149 context149 knowledge149", 28),
        ["angle149 universe149", "memory149 stream149", "context149 knowledge149"],
    ),
    (
        ("universe149 memory149 stream149 context149 knowledge149 vector149", 6),
        ["universe149", "memory149", "stream149", "context149", "knowledge149", "vector149"],
    ),
    (
        ("universe149 memory149 stream149 context149 knowledge149 vector149", 10),
        ["universe149", "memory149", "stream149", "context149", "knowledge149", "vector149"],
    ),
    (
        ("universe149 memory149 stream149 context149 knowledge149 vector149", 18),
        ["universe149", "memory149", "stream149", "context149", "knowledge149", "vector149"],
    ),
    (
        ("universe149 memory149 stream149 context149 knowledge149 vector149", 28),
        ["universe149 memory149", "stream149 context149", "knowledge149 vector149"],
    ),
    (
        ("memory149 stream149 context149 knowledge149 vector149 processor149", 6),
        ["memory149", "stream149", "context149", "knowledge149", "vector149", "processor149"],
    ),
    (
        ("memory149 stream149 context149 knowledge149 vector149 processor149", 10),
        ["memory149", "stream149", "context149", "knowledge149", "vector149", "processor149"],
    ),
    (
        ("memory149 stream149 context149 knowledge149 vector149 processor149", 18),
        ["memory149", "stream149", "context149", "knowledge149", "vector149", "processor149"],
    ),
    (
        ("memory149 stream149 context149 knowledge149 vector149 processor149", 28),
        ["memory149 stream149", "context149 knowledge149", "vector149 processor149"],
    ),
    (
        ("stream149 context149 knowledge149 vector149 processor149 reasoning149", 6),
        ["stream149", "context149", "knowledge149", "vector149", "processor149", "reasoning149"],
    ),
    (
        ("stream149 context149 knowledge149 vector149 processor149 reasoning149", 10),
        ["stream149", "context149", "knowledge149", "vector149", "processor149", "reasoning149"],
    ),
    (
        ("stream149 context149 knowledge149 vector149 processor149 reasoning149", 18),
        ["stream149", "context149", "knowledge149", "vector149", "processor149", "reasoning149"],
    ),
    (
        ("stream149 context149 knowledge149 vector149 processor149 reasoning149", 28),
        ["stream149 context149", "knowledge149 vector149", "processor149 reasoning149"],
    ),
    (
        ("context149 knowledge149 vector149 processor149 reasoning149 machine149", 6),
        ["context149", "knowledge149", "vector149", "processor149", "reasoning149", "machine149"],
    ),
    (
        ("context149 knowledge149 vector149 processor149 reasoning149 machine149", 10),
        ["context149", "knowledge149", "vector149", "processor149", "reasoning149", "machine149"],
    ),
    (
        ("context149 knowledge149 vector149 processor149 reasoning149 machine149", 18),
        ["context149", "knowledge149", "vector149", "processor149", "reasoning149", "machine149"],
    ),
    (
        ("context149 knowledge149 vector149 processor149 reasoning149 machine149", 28),
        ["context149 knowledge149", "vector149 processor149", "reasoning149 machine149"],
    ),
    (
        ("knowledge149 vector149 processor149 reasoning149 machine149 learning149", 6),
        ["knowledge149", "vector149", "processor149", "reasoning149", "machine149", "learning149"],
    ),
    (
        ("knowledge149 vector149 processor149 reasoning149 machine149 learning149", 10),
        ["knowledge149", "vector149", "processor149", "reasoning149", "machine149", "learning149"],
    ),
    (
        ("knowledge149 vector149 processor149 reasoning149 machine149 learning149", 18),
        ["knowledge149", "vector149", "processor149", "reasoning149", "machine149", "learning149"],
    ),
    (
        ("knowledge149 vector149 processor149 reasoning149 machine149 learning149", 28),
        ["knowledge149 vector149", "processor149 reasoning149", "machine149 learning149"],
    ),
    (
        ("vector149 processor149 reasoning149 machine149 learning149 model149", 6),
        ["vector149", "processor149", "reasoning149", "machine149", "learning149", "model149"],
    ),
    (
        ("vector149 processor149 reasoning149 machine149 learning149 model149", 10),
        ["vector149", "processor149", "reasoning149", "machine149", "learning149", "model149"],
    ),
    (
        ("vector149 processor149 reasoning149 machine149 learning149 model149", 18),
        ["vector149", "processor149", "reasoning149", "machine149", "learning149", "model149"],
    ),
    (
        ("vector149 processor149 reasoning149 machine149 learning149 model149", 28),
        ["vector149 processor149", "reasoning149 machine149", "learning149 model149"],
    ),
    (
        ("processor149 reasoning149 machine149 learning149 model149 token149", 6),
        ["processor149", "reasoning149", "machine149", "learning149", "model149", "token149"],
    ),
    (
        ("processor149 reasoning149 machine149 learning149 model149 token149", 10),
        ["processor149", "reasoning149", "machine149", "learning149", "model149", "token149"],
    ),
    (
        ("processor149 reasoning149 machine149 learning149 model149 token149", 18),
        ["processor149", "reasoning149", "machine149", "learning149", "model149 token149"],
    ),
    (
        ("processor149 reasoning149 machine149 learning149 model149 token149", 28),
        ["processor149 reasoning149", "machine149 learning149", "model149 token149"],
    ),
    (
        ("reasoning149 machine149 learning149 model149 token149 prompt149", 6),
        ["reasoning149", "machine149", "learning149", "model149", "token149", "prompt149"],
    ),
    (
        ("reasoning149 machine149 learning149 model149 token149 prompt149", 10),
        ["reasoning149", "machine149", "learning149", "model149", "token149", "prompt149"],
    ),
    (
        ("reasoning149 machine149 learning149 model149 token149 prompt149", 18),
        ["reasoning149", "machine149", "learning149", "model149 token149", "prompt149"],
    ),
    (
        ("reasoning149 machine149 learning149 model149 token149 prompt149", 28),
        ["reasoning149 machine149", "learning149 model149", "token149 prompt149"],
    ),
    (
        ("machine149 learning149 model149 token149 prompt149 session149", 6),
        ["machine149", "learning149", "model149", "token149", "prompt149", "session149"],
    ),
    (
        ("machine149 learning149 model149 token149 prompt149 session149", 10),
        ["machine149", "learning149", "model149", "token149", "prompt149", "session149"],
    ),
    (
        ("machine149 learning149 model149 token149 prompt149 session149", 18),
        ["machine149", "learning149", "model149 token149", "prompt149", "session149"],
    ),
    (
        ("machine149 learning149 model149 token149 prompt149 session149", 28),
        ["machine149 learning149", "model149 token149 prompt149", "session149"],
    ),
    (
        ("learning149 model149 token149 prompt149 session149 library149", 6),
        ["learning149", "model149", "token149", "prompt149", "session149", "library149"],
    ),
    (
        ("learning149 model149 token149 prompt149 session149 library149", 10),
        ["learning149", "model149", "token149", "prompt149", "session149", "library149"],
    ),
    (
        ("learning149 model149 token149 prompt149 session149 library149", 18),
        ["learning149", "model149 token149", "prompt149", "session149", "library149"],
    ),
    (
        ("learning149 model149 token149 prompt149 session149 library149", 28),
        ["learning149 model149", "token149 prompt149", "session149 library149"],
    ),
    (
        ("model149 token149 prompt149 session149 library149 service149", 6),
        ["model149", "token149", "prompt149", "session149", "library149", "service149"],
    ),
    (
        ("model149 token149 prompt149 session149 library149 service149", 10),
        ["model149", "token149", "prompt149", "session149", "library149", "service149"],
    ),
    (
        ("model149 token149 prompt149 session149 library149 service149", 18),
        ["model149 token149", "prompt149", "session149", "library149", "service149"],
    ),
    (
        ("model149 token149 prompt149 session149 library149 service149", 28),
        ["model149 token149 prompt149", "session149 library149", "service149"],
    ),
    (
        ("token149 prompt149 session149 library149 service149 gateway149", 6),
        ["token149", "prompt149", "session149", "library149", "service149", "gateway149"],
    ),
    (
        ("token149 prompt149 session149 library149 service149 gateway149", 10),
        ["token149", "prompt149", "session149", "library149", "service149", "gateway149"],
    ),
    (
        ("token149 prompt149 session149 library149 service149 gateway149", 18),
        ["token149 prompt149", "session149", "library149", "service149", "gateway149"],
    ),
    (
        ("token149 prompt149 session149 library149 service149 gateway149", 28),
        ["token149 prompt149", "session149 library149", "service149 gateway149"],
    ),
    (
        ("prompt149 session149 library149 service149 gateway149 storage149", 6),
        ["prompt149", "session149", "library149", "service149", "gateway149", "storage149"],
    ),
    (
        ("prompt149 session149 library149 service149 gateway149 storage149", 10),
        ["prompt149", "session149", "library149", "service149", "gateway149", "storage149"],
    ),
    (
        ("prompt149 session149 library149 service149 gateway149 storage149", 18),
        ["prompt149", "session149", "library149", "service149", "gateway149", "storage149"],
    ),
    (
        ("prompt149 session149 library149 service149 gateway149 storage149", 28),
        ["prompt149 session149", "library149 service149", "gateway149 storage149"],
    ),
    (
        ("session149 library149 service149 gateway149 storage149 network149", 6),
        ["session149", "library149", "service149", "gateway149", "storage149", "network149"],
    ),
    (
        ("session149 library149 service149 gateway149 storage149 network149", 10),
        ["session149", "library149", "service149", "gateway149", "storage149", "network149"],
    ),
    (
        ("session149 library149 service149 gateway149 storage149 network149", 18),
        ["session149", "library149", "service149", "gateway149", "storage149", "network149"],
    ),
    (
        ("session149 library149 service149 gateway149 storage149 network149", 28),
        ["session149 library149", "service149 gateway149", "storage149 network149"],
    ),
    (
        ("library149 service149 gateway149 storage149 network149 latency149", 6),
        ["library149", "service149", "gateway149", "storage149", "network149", "latency149"],
    ),
    (
        ("library149 service149 gateway149 storage149 network149 latency149", 10),
        ["library149", "service149", "gateway149", "storage149", "network149", "latency149"],
    ),
    (
        ("library149 service149 gateway149 storage149 network149 latency149", 18),
        ["library149", "service149", "gateway149", "storage149", "network149", "latency149"],
    ),
    (
        ("library149 service149 gateway149 storage149 network149 latency149", 28),
        ["library149 service149", "gateway149 storage149", "network149 latency149"],
    ),
    (
        ("service149 gateway149 storage149 network149 latency149 buffer149", 6),
        ["service149", "gateway149", "storage149", "network149", "latency149", "buffer149"],
    ),
    (
        ("service149 gateway149 storage149 network149 latency149 buffer149", 10),
        ["service149", "gateway149", "storage149", "network149", "latency149", "buffer149"],
    ),
    (
        ("service149 gateway149 storage149 network149 latency149 buffer149", 18),
        ["service149", "gateway149", "storage149", "network149", "latency149", "buffer149"],
    ),
    (
        ("service149 gateway149 storage149 network149 latency149 buffer149", 28),
        ["service149 gateway149", "storage149 network149", "latency149 buffer149"],
    ),
    (
        ("gateway149 storage149 network149 latency149 buffer149 queue149", 6),
        ["gateway149", "storage149", "network149", "latency149", "buffer149", "queue149"],
    ),
    (
        ("gateway149 storage149 network149 latency149 buffer149 queue149", 10),
        ["gateway149", "storage149", "network149", "latency149", "buffer149", "queue149"],
    ),
    (
        ("gateway149 storage149 network149 latency149 buffer149 queue149", 18),
        ["gateway149", "storage149", "network149", "latency149", "buffer149 queue149"],
    ),
    (
        ("gateway149 storage149 network149 latency149 buffer149 queue149", 28),
        ["gateway149 storage149", "network149 latency149", "buffer149 queue149"],
    ),
    (
        ("storage149 network149 latency149 buffer149 queue149 worker149", 6),
        ["storage149", "network149", "latency149", "buffer149", "queue149", "worker149"],
    ),
    (
        ("storage149 network149 latency149 buffer149 queue149 worker149", 10),
        ["storage149", "network149", "latency149", "buffer149", "queue149", "worker149"],
    ),
    (
        ("storage149 network149 latency149 buffer149 queue149 worker149", 18),
        ["storage149", "network149", "latency149", "buffer149 queue149", "worker149"],
    ),
    (
        ("storage149 network149 latency149 buffer149 queue149 worker149", 28),
        ["storage149 network149", "latency149 buffer149", "queue149 worker149"],
    ),
    (
        ("network149 latency149 buffer149 queue149 worker149 kernel149", 6),
        ["network149", "latency149", "buffer149", "queue149", "worker149", "kernel149"],
    ),
    (
        ("network149 latency149 buffer149 queue149 worker149 kernel149", 10),
        ["network149", "latency149", "buffer149", "queue149", "worker149", "kernel149"],
    ),
    (
        ("network149 latency149 buffer149 queue149 worker149 kernel149", 18),
        ["network149", "latency149", "buffer149 queue149", "worker149", "kernel149"],
    ),
    (
        ("network149 latency149 buffer149 queue149 worker149 kernel149", 28),
        ["network149 latency149", "buffer149 queue149 worker149", "kernel149"],
    ),
    (
        ("latency149 buffer149 queue149 worker149 kernel149 signal149", 6),
        ["latency149", "buffer149", "queue149", "worker149", "kernel149", "signal149"],
    ),
    (
        ("latency149 buffer149 queue149 worker149 kernel149 signal149", 10),
        ["latency149", "buffer149", "queue149", "worker149", "kernel149", "signal149"],
    ),
    (
        ("latency149 buffer149 queue149 worker149 kernel149 signal149", 18),
        ["latency149", "buffer149 queue149", "worker149", "kernel149", "signal149"],
    ),
    (
        ("latency149 buffer149 queue149 worker149 kernel149 signal149", 28),
        ["latency149 buffer149", "queue149 worker149 kernel149", "signal149"],
    ),
    (
        ("buffer149 queue149 worker149 kernel149 signal149 packet149", 6),
        ["buffer149", "queue149", "worker149", "kernel149", "signal149", "packet149"],
    ),
    (
        ("buffer149 queue149 worker149 kernel149 signal149 packet149", 10),
        ["buffer149", "queue149", "worker149", "kernel149", "signal149", "packet149"],
    ),
    (
        ("buffer149 queue149 worker149 kernel149 signal149 packet149", 18),
        ["buffer149 queue149", "worker149", "kernel149", "signal149", "packet149"],
    ),
    (
        ("buffer149 queue149 worker149 kernel149 signal149 packet149", 28),
        ["buffer149 queue149 worker149", "kernel149 signal149", "packet149"],
    ),
    (
        ("queue149 worker149 kernel149 signal149 packet149 router149", 6),
        ["queue149", "worker149", "kernel149", "signal149", "packet149", "router149"],
    ),
    (
        ("queue149 worker149 kernel149 signal149 packet149 router149", 10),
        ["queue149", "worker149", "kernel149", "signal149", "packet149", "router149"],
    ),
    (
        ("queue149 worker149 kernel149 signal149 packet149 router149", 18),
        ["queue149 worker149", "kernel149", "signal149", "packet149", "router149"],
    ),
    (
        ("queue149 worker149 kernel149 signal149 packet149 router149", 28),
        ["queue149 worker149 kernel149", "signal149 packet149", "router149"],
    ),
    (
        ("worker149 kernel149 signal149 packet149 router149 cluster149", 6),
        ["worker149", "kernel149", "signal149", "packet149", "router149", "cluster149"],
    ),
    (
        ("worker149 kernel149 signal149 packet149 router149 cluster149", 10),
        ["worker149", "kernel149", "signal149", "packet149", "router149", "cluster149"],
    ),
    (
        ("worker149 kernel149 signal149 packet149 router149 cluster149", 18),
        ["worker149", "kernel149", "signal149", "packet149", "router149", "cluster149"],
    ),
    (
        ("worker149 kernel149 signal149 packet149 router149 cluster149", 28),
        ["worker149 kernel149", "signal149 packet149", "router149 cluster149"],
    ),
    (
        ("kernel149 signal149 packet149 router149 cluster149 mirror149", 6),
        ["kernel149", "signal149", "packet149", "router149", "cluster149", "mirror149"],
    ),
    (
        ("kernel149 signal149 packet149 router149 cluster149 mirror149", 10),
        ["kernel149", "signal149", "packet149", "router149", "cluster149", "mirror149"],
    ),
    (
        ("kernel149 signal149 packet149 router149 cluster149 mirror149", 18),
        ["kernel149", "signal149", "packet149", "router149", "cluster149", "mirror149"],
    ),
    (
        ("kernel149 signal149 packet149 router149 cluster149 mirror149", 28),
        ["kernel149 signal149", "packet149 router149", "cluster149 mirror149"],
    ),
    (
        ("signal149 packet149 router149 cluster149 mirror149 filter149", 6),
        ["signal149", "packet149", "router149", "cluster149", "mirror149", "filter149"],
    ),
    (
        ("signal149 packet149 router149 cluster149 mirror149 filter149", 10),
        ["signal149", "packet149", "router149", "cluster149", "mirror149", "filter149"],
    ),
    (
        ("signal149 packet149 router149 cluster149 mirror149 filter149", 18),
        ["signal149", "packet149", "router149", "cluster149", "mirror149", "filter149"],
    ),
    (
        ("signal149 packet149 router149 cluster149 mirror149 filter149", 28),
        ["signal149 packet149", "router149 cluster149", "mirror149 filter149"],
    ),
    (
        ("packet149 router149 cluster149 mirror149 filter149 ranking149", 6),
        ["packet149", "router149", "cluster149", "mirror149", "filter149", "ranking149"],
    ),
    (
        ("packet149 router149 cluster149 mirror149 filter149 ranking149", 10),
        ["packet149", "router149", "cluster149", "mirror149", "filter149", "ranking149"],
    ),
    (
        ("packet149 router149 cluster149 mirror149 filter149 ranking149", 18),
        ["packet149", "router149", "cluster149", "mirror149", "filter149", "ranking149"],
    ),
    (
        ("packet149 router149 cluster149 mirror149 filter149 ranking149", 28),
        ["packet149 router149", "cluster149 mirror149", "filter149 ranking149"],
    ),
    (
        ("router149 cluster149 mirror149 filter149 ranking149 encoding149", 6),
        ["router149", "cluster149", "mirror149", "filter149", "ranking149", "encoding149"],
    ),
    (
        ("router149 cluster149 mirror149 filter149 ranking149 encoding149", 10),
        ["router149", "cluster149", "mirror149", "filter149", "ranking149", "encoding149"],
    ),
    (
        ("router149 cluster149 mirror149 filter149 ranking149 encoding149", 18),
        ["router149", "cluster149", "mirror149", "filter149", "ranking149", "encoding149"],
    ),
    (
        ("router149 cluster149 mirror149 filter149 ranking149 encoding149", 28),
        ["router149 cluster149", "mirror149 filter149", "ranking149 encoding149"],
    ),
    (
        ("cluster149 mirror149 filter149 ranking149 encoding149 mapping149", 6),
        ["cluster149", "mirror149", "filter149", "ranking149", "encoding149", "mapping149"],
    ),
    (
        ("cluster149 mirror149 filter149 ranking149 encoding149 mapping149", 10),
        ["cluster149", "mirror149", "filter149", "ranking149", "encoding149", "mapping149"],
    ),
    (
        ("cluster149 mirror149 filter149 ranking149 encoding149 mapping149", 18),
        ["cluster149", "mirror149", "filter149", "ranking149", "encoding149", "mapping149"],
    ),
    (
        ("cluster149 mirror149 filter149 ranking149 encoding149 mapping149", 28),
        ["cluster149 mirror149", "filter149 ranking149", "encoding149 mapping149"],
    ),
    (
        ("mirror149 filter149 ranking149 encoding149 mapping149 record149", 6),
        ["mirror149", "filter149", "ranking149", "encoding149", "mapping149", "record149"],
    ),
    (
        ("mirror149 filter149 ranking149 encoding149 mapping149 record149", 10),
        ["mirror149", "filter149", "ranking149", "encoding149", "mapping149", "record149"],
    ),
    (
        ("mirror149 filter149 ranking149 encoding149 mapping149 record149", 18),
        ["mirror149", "filter149", "ranking149", "encoding149", "mapping149", "record149"],
    ),
    (
        ("mirror149 filter149 ranking149 encoding149 mapping149 record149", 28),
        ["mirror149 filter149", "ranking149 encoding149", "mapping149 record149"],
    ),
    (
        ("filter149 ranking149 encoding149 mapping149 record149 candle149", 6),
        ["filter149", "ranking149", "encoding149", "mapping149", "record149", "candle149"],
    ),
    (
        ("filter149 ranking149 encoding149 mapping149 record149 candle149", 10),
        ["filter149", "ranking149", "encoding149", "mapping149", "record149", "candle149"],
    ),
    (
        ("filter149 ranking149 encoding149 mapping149 record149 candle149", 18),
        ["filter149", "ranking149", "encoding149", "mapping149", "record149", "candle149"],
    ),
    (
        ("filter149 ranking149 encoding149 mapping149 record149 candle149", 28),
        ["filter149 ranking149", "encoding149 mapping149", "record149 candle149"],
    ),
    (
        ("ranking149 encoding149 mapping149 record149 candle149 thread149", 6),
        ["ranking149", "encoding149", "mapping149", "record149", "candle149", "thread149"],
    ),
    (
        ("ranking149 encoding149 mapping149 record149 candle149 thread149", 10),
        ["ranking149", "encoding149", "mapping149", "record149", "candle149", "thread149"],
    ),
    (
        ("ranking149 encoding149 mapping149 record149 candle149 thread149", 18),
        ["ranking149", "encoding149", "mapping149", "record149", "candle149", "thread149"],
    ),
    (
        ("ranking149 encoding149 mapping149 record149 candle149 thread149", 28),
        ["ranking149 encoding149", "mapping149 record149", "candle149 thread149"],
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
