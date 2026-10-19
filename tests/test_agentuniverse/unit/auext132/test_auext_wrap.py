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
        ("round 132: the quick brown fox jumps over the lazy dog", 4),
        ["round", "132:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", 8),
        ["round", "132: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", 12),
        ["round 132:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", 16),
        ["round 132: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", 24),
        ["round 132: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 132: the quick brown fox jumps over the lazy dog", 32),
        ["round 132: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", 4),
        ["round", "132:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", 8),
        ["round", "132:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", 12),
        ["round 132:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", 16),
        ["round 132:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", 24),
        ["round 132: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 132: agentuniverse is a framework for multi agents", 32),
        ["round 132: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", 4),
        ["round", "132:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", 8),
        ["round", "132:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", 12),
        ["round 132:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", 16),
        ["round 132:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", 24),
        ["round 132: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 132: knowledge stored as vectors enables retrieval", 32),
        ["round 132: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 132: the processor reads the record then stops", 4),
        ["round", "132:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 132: the processor reads the record then stops", 8),
        ["round", "132: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 132: the processor reads the record then stops", 12),
        ["round 132:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 132: the processor reads the record then stops", 16),
        ["round 132: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 132: the processor reads the record then stops", 24),
        ["round 132: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 132: the processor reads the record then stops", 32),
        ["round 132: the processor reads", "the record then stops"],
    ),
    (
        ("round 132: a worker pulls the next task from the queue", 4),
        ["round", "132:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 132: a worker pulls the next task from the queue", 8),
        ["round", "132: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 132: a worker pulls the next task from the queue", 12),
        ["round 132: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 132: a worker pulls the next task from the queue", 16),
        ["round 132: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 132: a worker pulls the next task from the queue", 24),
        ["round 132: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 132: a worker pulls the next task from the queue", 32),
        ["round 132: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 132: signals travel through the network layer", 4),
        ["round", "132:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 132: signals travel through the network layer", 8),
        ["round", "132:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 132: signals travel through the network layer", 12),
        ["round 132:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 132: signals travel through the network layer", 16),
        ["round 132:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 132: signals travel through the network layer", 24),
        ["round 132: signals", "travel through the", "network layer"],
    ),
    (
        ("round 132: signals travel through the network layer", 32),
        ["round 132: signals travel", "through the network layer"],
    ),
    (
        ("round 132: the gateway routes each request by policy", 4),
        ["round", "132:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 132: the gateway routes each request by policy", 8),
        ["round", "132: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 132: the gateway routes each request by policy", 12),
        ["round 132:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 132: the gateway routes each request by policy", 16),
        ["round 132: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 132: the gateway routes each request by policy", 24),
        ["round 132: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 132: the gateway routes each request by policy", 32),
        ["round 132: the gateway routes", "each request by policy"],
    ),
    (
        ("round 132: memory grows until the buffer is full", 4),
        ["round", "132:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 132: memory grows until the buffer is full", 8),
        ["round", "132:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 132: memory grows until the buffer is full", 12),
        ["round 132:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 132: memory grows until the buffer is full", 16),
        ["round 132:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 132: memory grows until the buffer is full", 24), ["round 132: memory grows", "until the buffer is full"]),
    (("round 132: memory grows until the buffer is full", 32), ["round 132: memory grows until", "the buffer is full"]),
    (
        ("round 132: the cluster mirrors every packet twice", 4),
        ["round", "132:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 132: the cluster mirrors every packet twice", 8),
        ["round", "132: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 132: the cluster mirrors every packet twice", 12),
        ["round 132:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 132: the cluster mirrors every packet twice", 16),
        ["round 132: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 132: the cluster mirrors every packet twice", 24),
        ["round 132: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 132: the cluster mirrors every packet twice", 32),
        ["round 132: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", 4),
        ["round", "132:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", 8),
        ["round", "132:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", 12),
        ["round 132:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", 16),
        ["round 132:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", 24),
        ["round 132: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 132: ranking uses tokens learned from the corpus", 32),
        ["round 132: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 132: a long session ends when the candle dies", 4),
        ["round", "132:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 132: a long session ends when the candle dies", 8),
        ["round", "132: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 132: a long session ends when the candle dies", 12),
        ["round 132: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 132: a long session ends when the candle dies", 16),
        ["round 132: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 132: a long session ends when the candle dies", 24),
        ["round 132: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 132: a long session ends when the candle dies", 32),
        ["round 132: a long session ends", "when the candle dies"],
    ),
    (
        ("round 132: encode the prompt then map the result", 4),
        ["round", "132:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 132: encode the prompt then map the result", 8),
        ["round", "132:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 132: encode the prompt then map the result", 12),
        ["round 132:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 132: encode the prompt then map the result", 16),
        ["round 132:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 132: encode the prompt then map the result", 24),
        ["round 132: encode the", "prompt then map the", "result"],
    ),
    (("round 132: encode the prompt then map the result", 32), ["round 132: encode the prompt", "then map the result"]),
    (
        ("round 132: the kernel wakes the worker at dawn", 4),
        ["round", "132:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 132: the kernel wakes the worker at dawn", 8),
        ["round", "132: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 132: the kernel wakes the worker at dawn", 12),
        ["round 132:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 132: the kernel wakes the worker at dawn", 16), ["round 132: the", "kernel wakes the", "worker at dawn"]),
    (("round 132: the kernel wakes the worker at dawn", 24), ["round 132: the kernel", "wakes the worker at dawn"]),
    (("round 132: the kernel wakes the worker at dawn", 32), ["round 132: the kernel wakes the", "worker at dawn"]),
    (
        ("round 132: service latency drops after the patch", 4),
        ["round", "132:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 132: service latency drops after the patch", 8),
        ["round", "132:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 132: service latency drops after the patch", 12),
        ["round 132:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 132: service latency drops after the patch", 16),
        ["round 132:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 132: service latency drops after the patch", 24),
        ["round 132: service", "latency drops after the", "patch"],
    ),
    (("round 132: service latency drops after the patch", 32), ["round 132: service latency drops", "after the patch"]),
    (
        ("round 132: the library caches every vector it sees", 4),
        ["round", "132:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 132: the library caches every vector it sees", 8),
        ["round", "132: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 132: the library caches every vector it sees", 12),
        ["round 132:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 132: the library caches every vector it sees", 16),
        ["round 132: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 132: the library caches every vector it sees", 24),
        ["round 132: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 132: the library caches every vector it sees", 32),
        ["round 132: the library caches", "every vector it sees"],
    ),
    (
        ("round 132: agents argue then the debate resolves", 4),
        ["round", "132:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 132: agents argue then the debate resolves", 8),
        ["round", "132:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 132: agents argue then the debate resolves", 12),
        ["round 132:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 132: agents argue then the debate resolves", 16),
        ["round 132:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 132: agents argue then the debate resolves", 24), ["round 132: agents argue", "then the debate resolves"]),
    (("round 132: agents argue then the debate resolves", 32), ["round 132: agents argue then the", "debate resolves"]),
    (
        ("round 132: the filter keeps only strong matches", 4),
        ["round", "132:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 132: the filter keeps only strong matches", 8),
        ["round", "132: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 132: the filter keeps only strong matches", 12),
        ["round 132:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 132: the filter keeps only strong matches", 16),
        ["round 132: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 132: the filter keeps only strong matches", 24),
        ["round 132: the filter", "keeps only strong", "matches"],
    ),
    (("round 132: the filter keeps only strong matches", 32), ["round 132: the filter keeps only", "strong matches"]),
    (
        ("round 132: the model answers with a short reply", 4),
        ["round", "132:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 132: the model answers with a short reply", 8),
        ["round", "132: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 132: the model answers with a short reply", 12),
        ["round 132:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 132: the model answers with a short reply", 16),
        ["round 132: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 132: the model answers with a short reply", 24),
        ["round 132: the model", "answers with a short", "reply"],
    ),
    (("round 132: the model answers with a short reply", 32), ["round 132: the model answers", "with a short reply"]),
    (
        ("round 132: the recorder stores the reasoning trace", 4),
        ["round", "132:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 132: the recorder stores the reasoning trace", 8),
        ["round", "132: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 132: the recorder stores the reasoning trace", 12),
        ["round 132:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 132: the recorder stores the reasoning trace", 16),
        ["round 132: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 132: the recorder stores the reasoning trace", 24),
        ["round 132: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 132: the recorder stores the reasoning trace", 32),
        ["round 132: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 132: the angel watches the processor run", 4),
        ["round", "132:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 132: the angel watches the processor run", 8),
        ["round", "132: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 132: the angel watches the processor run", 12),
        ["round 132:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 132: the angel watches the processor run", 16),
        ["round 132: the", "angel watches", "the processor", "run"],
    ),
    (("round 132: the angel watches the processor run", 24), ["round 132: the angel", "watches the processor", "run"]),
    (("round 132: the angel watches the processor run", 32), ["round 132: the angel watches the", "processor run"]),
    (
        ("round 132: angle of the vector decides the match", 4),
        ["round", "132:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 132: angle of the vector decides the match", 8),
        ["round", "132:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 132: angle of the vector decides the match", 12),
        ["round 132:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 132: angle of the vector decides the match", 16),
        ["round 132: angle", "of the vector", "decides the", "match"],
    ),
    (("round 132: angle of the vector decides the match", 24), ["round 132: angle of the", "vector decides the match"]),
    (("round 132: angle of the vector decides the match", 32), ["round 132: angle of the vector", "decides the match"]),
    (
        ("round 132: the candle burns twice as long at night", 4),
        ["round", "132:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 132: the candle burns twice as long at night", 8),
        ["round", "132: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 132: the candle burns twice as long at night", 12),
        ["round 132:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 132: the candle burns twice as long at night", 16),
        ["round 132: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 132: the candle burns twice as long at night", 24),
        ["round 132: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 132: the candle burns twice as long at night", 32),
        ["round 132: the candle burns", "twice as long at night"],
    ),
    (
        ("round 132: a mirror of the universe in one line", 4),
        ["round", "132:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 132: a mirror of the universe in one line", 8),
        ["round", "132: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 132: a mirror of the universe in one line", 12),
        ["round 132: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 132: a mirror of the universe in one line", 16),
        ["round 132: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 132: a mirror of the universe in one line", 24), ["round 132: a mirror of", "the universe in one line"]),
    (("round 132: a mirror of the universe in one line", 32), ["round 132: a mirror of the", "universe in one line"]),
    (
        ("round 132: the queue drains before the storm", 4),
        ["round", "132:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 132: the queue drains before the storm", 8),
        ["round", "132: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 132: the queue drains before the storm", 12),
        ["round 132:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 132: the queue drains before the storm", 16), ["round 132: the", "queue drains", "before the storm"]),
    (("round 132: the queue drains before the storm", 24), ["round 132: the queue", "drains before the storm"]),
    (("round 132: the queue drains before the storm", 32), ["round 132: the queue drains", "before the storm"]),
    (
        ("kitten132 sitting132 agent132 angle132 universe132 memory132", 6),
        ["kitten132", "sitting132", "agent132", "angle132", "universe132", "memory132"],
    ),
    (
        ("kitten132 sitting132 agent132 angle132 universe132 memory132", 10),
        ["kitten132", "sitting132", "agent132", "angle132", "universe132", "memory132"],
    ),
    (
        ("kitten132 sitting132 agent132 angle132 universe132 memory132", 18),
        ["kitten132", "sitting132", "agent132 angle132", "universe132", "memory132"],
    ),
    (
        ("kitten132 sitting132 agent132 angle132 universe132 memory132", 28),
        ["kitten132 sitting132", "agent132 angle132", "universe132 memory132"],
    ),
    (
        ("sitting132 agent132 angle132 universe132 memory132 stream132", 6),
        ["sitting132", "agent132", "angle132", "universe132", "memory132", "stream132"],
    ),
    (
        ("sitting132 agent132 angle132 universe132 memory132 stream132", 10),
        ["sitting132", "agent132", "angle132", "universe132", "memory132", "stream132"],
    ),
    (
        ("sitting132 agent132 angle132 universe132 memory132 stream132", 18),
        ["sitting132", "agent132 angle132", "universe132", "memory132", "stream132"],
    ),
    (
        ("sitting132 agent132 angle132 universe132 memory132 stream132", 28),
        ["sitting132 agent132 angle132", "universe132 memory132", "stream132"],
    ),
    (
        ("agent132 angle132 universe132 memory132 stream132 context132", 6),
        ["agent132", "angle132", "universe132", "memory132", "stream132", "context132"],
    ),
    (
        ("agent132 angle132 universe132 memory132 stream132 context132", 10),
        ["agent132", "angle132", "universe132", "memory132", "stream132", "context132"],
    ),
    (
        ("agent132 angle132 universe132 memory132 stream132 context132", 18),
        ["agent132 angle132", "universe132", "memory132", "stream132", "context132"],
    ),
    (
        ("agent132 angle132 universe132 memory132 stream132 context132", 28),
        ["agent132 angle132", "universe132 memory132", "stream132 context132"],
    ),
    (
        ("angle132 universe132 memory132 stream132 context132 knowledge132", 6),
        ["angle132", "universe132", "memory132", "stream132", "context132", "knowledge132"],
    ),
    (
        ("angle132 universe132 memory132 stream132 context132 knowledge132", 10),
        ["angle132", "universe132", "memory132", "stream132", "context132", "knowledge132"],
    ),
    (
        ("angle132 universe132 memory132 stream132 context132 knowledge132", 18),
        ["angle132", "universe132", "memory132", "stream132", "context132", "knowledge132"],
    ),
    (
        ("angle132 universe132 memory132 stream132 context132 knowledge132", 28),
        ["angle132 universe132", "memory132 stream132", "context132 knowledge132"],
    ),
    (
        ("universe132 memory132 stream132 context132 knowledge132 vector132", 6),
        ["universe132", "memory132", "stream132", "context132", "knowledge132", "vector132"],
    ),
    (
        ("universe132 memory132 stream132 context132 knowledge132 vector132", 10),
        ["universe132", "memory132", "stream132", "context132", "knowledge132", "vector132"],
    ),
    (
        ("universe132 memory132 stream132 context132 knowledge132 vector132", 18),
        ["universe132", "memory132", "stream132", "context132", "knowledge132", "vector132"],
    ),
    (
        ("universe132 memory132 stream132 context132 knowledge132 vector132", 28),
        ["universe132 memory132", "stream132 context132", "knowledge132 vector132"],
    ),
    (
        ("memory132 stream132 context132 knowledge132 vector132 processor132", 6),
        ["memory132", "stream132", "context132", "knowledge132", "vector132", "processor132"],
    ),
    (
        ("memory132 stream132 context132 knowledge132 vector132 processor132", 10),
        ["memory132", "stream132", "context132", "knowledge132", "vector132", "processor132"],
    ),
    (
        ("memory132 stream132 context132 knowledge132 vector132 processor132", 18),
        ["memory132", "stream132", "context132", "knowledge132", "vector132", "processor132"],
    ),
    (
        ("memory132 stream132 context132 knowledge132 vector132 processor132", 28),
        ["memory132 stream132", "context132 knowledge132", "vector132 processor132"],
    ),
    (
        ("stream132 context132 knowledge132 vector132 processor132 reasoning132", 6),
        ["stream132", "context132", "knowledge132", "vector132", "processor132", "reasoning132"],
    ),
    (
        ("stream132 context132 knowledge132 vector132 processor132 reasoning132", 10),
        ["stream132", "context132", "knowledge132", "vector132", "processor132", "reasoning132"],
    ),
    (
        ("stream132 context132 knowledge132 vector132 processor132 reasoning132", 18),
        ["stream132", "context132", "knowledge132", "vector132", "processor132", "reasoning132"],
    ),
    (
        ("stream132 context132 knowledge132 vector132 processor132 reasoning132", 28),
        ["stream132 context132", "knowledge132 vector132", "processor132 reasoning132"],
    ),
    (
        ("context132 knowledge132 vector132 processor132 reasoning132 machine132", 6),
        ["context132", "knowledge132", "vector132", "processor132", "reasoning132", "machine132"],
    ),
    (
        ("context132 knowledge132 vector132 processor132 reasoning132 machine132", 10),
        ["context132", "knowledge132", "vector132", "processor132", "reasoning132", "machine132"],
    ),
    (
        ("context132 knowledge132 vector132 processor132 reasoning132 machine132", 18),
        ["context132", "knowledge132", "vector132", "processor132", "reasoning132", "machine132"],
    ),
    (
        ("context132 knowledge132 vector132 processor132 reasoning132 machine132", 28),
        ["context132 knowledge132", "vector132 processor132", "reasoning132 machine132"],
    ),
    (
        ("knowledge132 vector132 processor132 reasoning132 machine132 learning132", 6),
        ["knowledge132", "vector132", "processor132", "reasoning132", "machine132", "learning132"],
    ),
    (
        ("knowledge132 vector132 processor132 reasoning132 machine132 learning132", 10),
        ["knowledge132", "vector132", "processor132", "reasoning132", "machine132", "learning132"],
    ),
    (
        ("knowledge132 vector132 processor132 reasoning132 machine132 learning132", 18),
        ["knowledge132", "vector132", "processor132", "reasoning132", "machine132", "learning132"],
    ),
    (
        ("knowledge132 vector132 processor132 reasoning132 machine132 learning132", 28),
        ["knowledge132 vector132", "processor132 reasoning132", "machine132 learning132"],
    ),
    (
        ("vector132 processor132 reasoning132 machine132 learning132 model132", 6),
        ["vector132", "processor132", "reasoning132", "machine132", "learning132", "model132"],
    ),
    (
        ("vector132 processor132 reasoning132 machine132 learning132 model132", 10),
        ["vector132", "processor132", "reasoning132", "machine132", "learning132", "model132"],
    ),
    (
        ("vector132 processor132 reasoning132 machine132 learning132 model132", 18),
        ["vector132", "processor132", "reasoning132", "machine132", "learning132", "model132"],
    ),
    (
        ("vector132 processor132 reasoning132 machine132 learning132 model132", 28),
        ["vector132 processor132", "reasoning132 machine132", "learning132 model132"],
    ),
    (
        ("processor132 reasoning132 machine132 learning132 model132 token132", 6),
        ["processor132", "reasoning132", "machine132", "learning132", "model132", "token132"],
    ),
    (
        ("processor132 reasoning132 machine132 learning132 model132 token132", 10),
        ["processor132", "reasoning132", "machine132", "learning132", "model132", "token132"],
    ),
    (
        ("processor132 reasoning132 machine132 learning132 model132 token132", 18),
        ["processor132", "reasoning132", "machine132", "learning132", "model132 token132"],
    ),
    (
        ("processor132 reasoning132 machine132 learning132 model132 token132", 28),
        ["processor132 reasoning132", "machine132 learning132", "model132 token132"],
    ),
    (
        ("reasoning132 machine132 learning132 model132 token132 prompt132", 6),
        ["reasoning132", "machine132", "learning132", "model132", "token132", "prompt132"],
    ),
    (
        ("reasoning132 machine132 learning132 model132 token132 prompt132", 10),
        ["reasoning132", "machine132", "learning132", "model132", "token132", "prompt132"],
    ),
    (
        ("reasoning132 machine132 learning132 model132 token132 prompt132", 18),
        ["reasoning132", "machine132", "learning132", "model132 token132", "prompt132"],
    ),
    (
        ("reasoning132 machine132 learning132 model132 token132 prompt132", 28),
        ["reasoning132 machine132", "learning132 model132", "token132 prompt132"],
    ),
    (
        ("machine132 learning132 model132 token132 prompt132 session132", 6),
        ["machine132", "learning132", "model132", "token132", "prompt132", "session132"],
    ),
    (
        ("machine132 learning132 model132 token132 prompt132 session132", 10),
        ["machine132", "learning132", "model132", "token132", "prompt132", "session132"],
    ),
    (
        ("machine132 learning132 model132 token132 prompt132 session132", 18),
        ["machine132", "learning132", "model132 token132", "prompt132", "session132"],
    ),
    (
        ("machine132 learning132 model132 token132 prompt132 session132", 28),
        ["machine132 learning132", "model132 token132 prompt132", "session132"],
    ),
    (
        ("learning132 model132 token132 prompt132 session132 library132", 6),
        ["learning132", "model132", "token132", "prompt132", "session132", "library132"],
    ),
    (
        ("learning132 model132 token132 prompt132 session132 library132", 10),
        ["learning132", "model132", "token132", "prompt132", "session132", "library132"],
    ),
    (
        ("learning132 model132 token132 prompt132 session132 library132", 18),
        ["learning132", "model132 token132", "prompt132", "session132", "library132"],
    ),
    (
        ("learning132 model132 token132 prompt132 session132 library132", 28),
        ["learning132 model132", "token132 prompt132", "session132 library132"],
    ),
    (
        ("model132 token132 prompt132 session132 library132 service132", 6),
        ["model132", "token132", "prompt132", "session132", "library132", "service132"],
    ),
    (
        ("model132 token132 prompt132 session132 library132 service132", 10),
        ["model132", "token132", "prompt132", "session132", "library132", "service132"],
    ),
    (
        ("model132 token132 prompt132 session132 library132 service132", 18),
        ["model132 token132", "prompt132", "session132", "library132", "service132"],
    ),
    (
        ("model132 token132 prompt132 session132 library132 service132", 28),
        ["model132 token132 prompt132", "session132 library132", "service132"],
    ),
    (
        ("token132 prompt132 session132 library132 service132 gateway132", 6),
        ["token132", "prompt132", "session132", "library132", "service132", "gateway132"],
    ),
    (
        ("token132 prompt132 session132 library132 service132 gateway132", 10),
        ["token132", "prompt132", "session132", "library132", "service132", "gateway132"],
    ),
    (
        ("token132 prompt132 session132 library132 service132 gateway132", 18),
        ["token132 prompt132", "session132", "library132", "service132", "gateway132"],
    ),
    (
        ("token132 prompt132 session132 library132 service132 gateway132", 28),
        ["token132 prompt132", "session132 library132", "service132 gateway132"],
    ),
    (
        ("prompt132 session132 library132 service132 gateway132 storage132", 6),
        ["prompt132", "session132", "library132", "service132", "gateway132", "storage132"],
    ),
    (
        ("prompt132 session132 library132 service132 gateway132 storage132", 10),
        ["prompt132", "session132", "library132", "service132", "gateway132", "storage132"],
    ),
    (
        ("prompt132 session132 library132 service132 gateway132 storage132", 18),
        ["prompt132", "session132", "library132", "service132", "gateway132", "storage132"],
    ),
    (
        ("prompt132 session132 library132 service132 gateway132 storage132", 28),
        ["prompt132 session132", "library132 service132", "gateway132 storage132"],
    ),
    (
        ("session132 library132 service132 gateway132 storage132 network132", 6),
        ["session132", "library132", "service132", "gateway132", "storage132", "network132"],
    ),
    (
        ("session132 library132 service132 gateway132 storage132 network132", 10),
        ["session132", "library132", "service132", "gateway132", "storage132", "network132"],
    ),
    (
        ("session132 library132 service132 gateway132 storage132 network132", 18),
        ["session132", "library132", "service132", "gateway132", "storage132", "network132"],
    ),
    (
        ("session132 library132 service132 gateway132 storage132 network132", 28),
        ["session132 library132", "service132 gateway132", "storage132 network132"],
    ),
    (
        ("library132 service132 gateway132 storage132 network132 latency132", 6),
        ["library132", "service132", "gateway132", "storage132", "network132", "latency132"],
    ),
    (
        ("library132 service132 gateway132 storage132 network132 latency132", 10),
        ["library132", "service132", "gateway132", "storage132", "network132", "latency132"],
    ),
    (
        ("library132 service132 gateway132 storage132 network132 latency132", 18),
        ["library132", "service132", "gateway132", "storage132", "network132", "latency132"],
    ),
    (
        ("library132 service132 gateway132 storage132 network132 latency132", 28),
        ["library132 service132", "gateway132 storage132", "network132 latency132"],
    ),
    (
        ("service132 gateway132 storage132 network132 latency132 buffer132", 6),
        ["service132", "gateway132", "storage132", "network132", "latency132", "buffer132"],
    ),
    (
        ("service132 gateway132 storage132 network132 latency132 buffer132", 10),
        ["service132", "gateway132", "storage132", "network132", "latency132", "buffer132"],
    ),
    (
        ("service132 gateway132 storage132 network132 latency132 buffer132", 18),
        ["service132", "gateway132", "storage132", "network132", "latency132", "buffer132"],
    ),
    (
        ("service132 gateway132 storage132 network132 latency132 buffer132", 28),
        ["service132 gateway132", "storage132 network132", "latency132 buffer132"],
    ),
    (
        ("gateway132 storage132 network132 latency132 buffer132 queue132", 6),
        ["gateway132", "storage132", "network132", "latency132", "buffer132", "queue132"],
    ),
    (
        ("gateway132 storage132 network132 latency132 buffer132 queue132", 10),
        ["gateway132", "storage132", "network132", "latency132", "buffer132", "queue132"],
    ),
    (
        ("gateway132 storage132 network132 latency132 buffer132 queue132", 18),
        ["gateway132", "storage132", "network132", "latency132", "buffer132 queue132"],
    ),
    (
        ("gateway132 storage132 network132 latency132 buffer132 queue132", 28),
        ["gateway132 storage132", "network132 latency132", "buffer132 queue132"],
    ),
    (
        ("storage132 network132 latency132 buffer132 queue132 worker132", 6),
        ["storage132", "network132", "latency132", "buffer132", "queue132", "worker132"],
    ),
    (
        ("storage132 network132 latency132 buffer132 queue132 worker132", 10),
        ["storage132", "network132", "latency132", "buffer132", "queue132", "worker132"],
    ),
    (
        ("storage132 network132 latency132 buffer132 queue132 worker132", 18),
        ["storage132", "network132", "latency132", "buffer132 queue132", "worker132"],
    ),
    (
        ("storage132 network132 latency132 buffer132 queue132 worker132", 28),
        ["storage132 network132", "latency132 buffer132", "queue132 worker132"],
    ),
    (
        ("network132 latency132 buffer132 queue132 worker132 kernel132", 6),
        ["network132", "latency132", "buffer132", "queue132", "worker132", "kernel132"],
    ),
    (
        ("network132 latency132 buffer132 queue132 worker132 kernel132", 10),
        ["network132", "latency132", "buffer132", "queue132", "worker132", "kernel132"],
    ),
    (
        ("network132 latency132 buffer132 queue132 worker132 kernel132", 18),
        ["network132", "latency132", "buffer132 queue132", "worker132", "kernel132"],
    ),
    (
        ("network132 latency132 buffer132 queue132 worker132 kernel132", 28),
        ["network132 latency132", "buffer132 queue132 worker132", "kernel132"],
    ),
    (
        ("latency132 buffer132 queue132 worker132 kernel132 signal132", 6),
        ["latency132", "buffer132", "queue132", "worker132", "kernel132", "signal132"],
    ),
    (
        ("latency132 buffer132 queue132 worker132 kernel132 signal132", 10),
        ["latency132", "buffer132", "queue132", "worker132", "kernel132", "signal132"],
    ),
    (
        ("latency132 buffer132 queue132 worker132 kernel132 signal132", 18),
        ["latency132", "buffer132 queue132", "worker132", "kernel132", "signal132"],
    ),
    (
        ("latency132 buffer132 queue132 worker132 kernel132 signal132", 28),
        ["latency132 buffer132", "queue132 worker132 kernel132", "signal132"],
    ),
    (
        ("buffer132 queue132 worker132 kernel132 signal132 packet132", 6),
        ["buffer132", "queue132", "worker132", "kernel132", "signal132", "packet132"],
    ),
    (
        ("buffer132 queue132 worker132 kernel132 signal132 packet132", 10),
        ["buffer132", "queue132", "worker132", "kernel132", "signal132", "packet132"],
    ),
    (
        ("buffer132 queue132 worker132 kernel132 signal132 packet132", 18),
        ["buffer132 queue132", "worker132", "kernel132", "signal132", "packet132"],
    ),
    (
        ("buffer132 queue132 worker132 kernel132 signal132 packet132", 28),
        ["buffer132 queue132 worker132", "kernel132 signal132", "packet132"],
    ),
    (
        ("queue132 worker132 kernel132 signal132 packet132 router132", 6),
        ["queue132", "worker132", "kernel132", "signal132", "packet132", "router132"],
    ),
    (
        ("queue132 worker132 kernel132 signal132 packet132 router132", 10),
        ["queue132", "worker132", "kernel132", "signal132", "packet132", "router132"],
    ),
    (
        ("queue132 worker132 kernel132 signal132 packet132 router132", 18),
        ["queue132 worker132", "kernel132", "signal132", "packet132", "router132"],
    ),
    (
        ("queue132 worker132 kernel132 signal132 packet132 router132", 28),
        ["queue132 worker132 kernel132", "signal132 packet132", "router132"],
    ),
    (
        ("worker132 kernel132 signal132 packet132 router132 cluster132", 6),
        ["worker132", "kernel132", "signal132", "packet132", "router132", "cluster132"],
    ),
    (
        ("worker132 kernel132 signal132 packet132 router132 cluster132", 10),
        ["worker132", "kernel132", "signal132", "packet132", "router132", "cluster132"],
    ),
    (
        ("worker132 kernel132 signal132 packet132 router132 cluster132", 18),
        ["worker132", "kernel132", "signal132", "packet132", "router132", "cluster132"],
    ),
    (
        ("worker132 kernel132 signal132 packet132 router132 cluster132", 28),
        ["worker132 kernel132", "signal132 packet132", "router132 cluster132"],
    ),
    (
        ("kernel132 signal132 packet132 router132 cluster132 mirror132", 6),
        ["kernel132", "signal132", "packet132", "router132", "cluster132", "mirror132"],
    ),
    (
        ("kernel132 signal132 packet132 router132 cluster132 mirror132", 10),
        ["kernel132", "signal132", "packet132", "router132", "cluster132", "mirror132"],
    ),
    (
        ("kernel132 signal132 packet132 router132 cluster132 mirror132", 18),
        ["kernel132", "signal132", "packet132", "router132", "cluster132", "mirror132"],
    ),
    (
        ("kernel132 signal132 packet132 router132 cluster132 mirror132", 28),
        ["kernel132 signal132", "packet132 router132", "cluster132 mirror132"],
    ),
    (
        ("signal132 packet132 router132 cluster132 mirror132 filter132", 6),
        ["signal132", "packet132", "router132", "cluster132", "mirror132", "filter132"],
    ),
    (
        ("signal132 packet132 router132 cluster132 mirror132 filter132", 10),
        ["signal132", "packet132", "router132", "cluster132", "mirror132", "filter132"],
    ),
    (
        ("signal132 packet132 router132 cluster132 mirror132 filter132", 18),
        ["signal132", "packet132", "router132", "cluster132", "mirror132", "filter132"],
    ),
    (
        ("signal132 packet132 router132 cluster132 mirror132 filter132", 28),
        ["signal132 packet132", "router132 cluster132", "mirror132 filter132"],
    ),
    (
        ("packet132 router132 cluster132 mirror132 filter132 ranking132", 6),
        ["packet132", "router132", "cluster132", "mirror132", "filter132", "ranking132"],
    ),
    (
        ("packet132 router132 cluster132 mirror132 filter132 ranking132", 10),
        ["packet132", "router132", "cluster132", "mirror132", "filter132", "ranking132"],
    ),
    (
        ("packet132 router132 cluster132 mirror132 filter132 ranking132", 18),
        ["packet132", "router132", "cluster132", "mirror132", "filter132", "ranking132"],
    ),
    (
        ("packet132 router132 cluster132 mirror132 filter132 ranking132", 28),
        ["packet132 router132", "cluster132 mirror132", "filter132 ranking132"],
    ),
    (
        ("router132 cluster132 mirror132 filter132 ranking132 encoding132", 6),
        ["router132", "cluster132", "mirror132", "filter132", "ranking132", "encoding132"],
    ),
    (
        ("router132 cluster132 mirror132 filter132 ranking132 encoding132", 10),
        ["router132", "cluster132", "mirror132", "filter132", "ranking132", "encoding132"],
    ),
    (
        ("router132 cluster132 mirror132 filter132 ranking132 encoding132", 18),
        ["router132", "cluster132", "mirror132", "filter132", "ranking132", "encoding132"],
    ),
    (
        ("router132 cluster132 mirror132 filter132 ranking132 encoding132", 28),
        ["router132 cluster132", "mirror132 filter132", "ranking132 encoding132"],
    ),
    (
        ("cluster132 mirror132 filter132 ranking132 encoding132 mapping132", 6),
        ["cluster132", "mirror132", "filter132", "ranking132", "encoding132", "mapping132"],
    ),
    (
        ("cluster132 mirror132 filter132 ranking132 encoding132 mapping132", 10),
        ["cluster132", "mirror132", "filter132", "ranking132", "encoding132", "mapping132"],
    ),
    (
        ("cluster132 mirror132 filter132 ranking132 encoding132 mapping132", 18),
        ["cluster132", "mirror132", "filter132", "ranking132", "encoding132", "mapping132"],
    ),
    (
        ("cluster132 mirror132 filter132 ranking132 encoding132 mapping132", 28),
        ["cluster132 mirror132", "filter132 ranking132", "encoding132 mapping132"],
    ),
    (
        ("mirror132 filter132 ranking132 encoding132 mapping132 record132", 6),
        ["mirror132", "filter132", "ranking132", "encoding132", "mapping132", "record132"],
    ),
    (
        ("mirror132 filter132 ranking132 encoding132 mapping132 record132", 10),
        ["mirror132", "filter132", "ranking132", "encoding132", "mapping132", "record132"],
    ),
    (
        ("mirror132 filter132 ranking132 encoding132 mapping132 record132", 18),
        ["mirror132", "filter132", "ranking132", "encoding132", "mapping132", "record132"],
    ),
    (
        ("mirror132 filter132 ranking132 encoding132 mapping132 record132", 28),
        ["mirror132 filter132", "ranking132 encoding132", "mapping132 record132"],
    ),
    (
        ("filter132 ranking132 encoding132 mapping132 record132 candle132", 6),
        ["filter132", "ranking132", "encoding132", "mapping132", "record132", "candle132"],
    ),
    (
        ("filter132 ranking132 encoding132 mapping132 record132 candle132", 10),
        ["filter132", "ranking132", "encoding132", "mapping132", "record132", "candle132"],
    ),
    (
        ("filter132 ranking132 encoding132 mapping132 record132 candle132", 18),
        ["filter132", "ranking132", "encoding132", "mapping132", "record132", "candle132"],
    ),
    (
        ("filter132 ranking132 encoding132 mapping132 record132 candle132", 28),
        ["filter132 ranking132", "encoding132 mapping132", "record132 candle132"],
    ),
    (
        ("ranking132 encoding132 mapping132 record132 candle132 thread132", 6),
        ["ranking132", "encoding132", "mapping132", "record132", "candle132", "thread132"],
    ),
    (
        ("ranking132 encoding132 mapping132 record132 candle132 thread132", 10),
        ["ranking132", "encoding132", "mapping132", "record132", "candle132", "thread132"],
    ),
    (
        ("ranking132 encoding132 mapping132 record132 candle132 thread132", 18),
        ["ranking132", "encoding132", "mapping132", "record132", "candle132", "thread132"],
    ),
    (
        ("ranking132 encoding132 mapping132 record132 candle132 thread132", 28),
        ["ranking132 encoding132", "mapping132 record132", "candle132 thread132"],
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
