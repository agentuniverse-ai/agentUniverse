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
        ("round 140: the quick brown fox jumps over the lazy dog", 4),
        ["round", "140:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", 8),
        ["round", "140: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", 12),
        ["round 140:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", 16),
        ["round 140: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", 24),
        ["round 140: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 140: the quick brown fox jumps over the lazy dog", 32),
        ["round 140: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", 4),
        ["round", "140:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", 8),
        ["round", "140:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", 12),
        ["round 140:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", 16),
        ["round 140:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", 24),
        ["round 140: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 140: agentuniverse is a framework for multi agents", 32),
        ["round 140: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", 4),
        ["round", "140:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", 8),
        ["round", "140:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", 12),
        ["round 140:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", 16),
        ["round 140:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", 24),
        ["round 140: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 140: knowledge stored as vectors enables retrieval", 32),
        ["round 140: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 140: the processor reads the record then stops", 4),
        ["round", "140:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 140: the processor reads the record then stops", 8),
        ["round", "140: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 140: the processor reads the record then stops", 12),
        ["round 140:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 140: the processor reads the record then stops", 16),
        ["round 140: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 140: the processor reads the record then stops", 24),
        ["round 140: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 140: the processor reads the record then stops", 32),
        ["round 140: the processor reads", "the record then stops"],
    ),
    (
        ("round 140: a worker pulls the next task from the queue", 4),
        ["round", "140:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 140: a worker pulls the next task from the queue", 8),
        ["round", "140: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 140: a worker pulls the next task from the queue", 12),
        ["round 140: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 140: a worker pulls the next task from the queue", 16),
        ["round 140: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 140: a worker pulls the next task from the queue", 24),
        ["round 140: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 140: a worker pulls the next task from the queue", 32),
        ["round 140: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 140: signals travel through the network layer", 4),
        ["round", "140:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 140: signals travel through the network layer", 8),
        ["round", "140:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 140: signals travel through the network layer", 12),
        ["round 140:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 140: signals travel through the network layer", 16),
        ["round 140:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 140: signals travel through the network layer", 24),
        ["round 140: signals", "travel through the", "network layer"],
    ),
    (
        ("round 140: signals travel through the network layer", 32),
        ["round 140: signals travel", "through the network layer"],
    ),
    (
        ("round 140: the gateway routes each request by policy", 4),
        ["round", "140:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 140: the gateway routes each request by policy", 8),
        ["round", "140: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 140: the gateway routes each request by policy", 12),
        ["round 140:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 140: the gateway routes each request by policy", 16),
        ["round 140: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 140: the gateway routes each request by policy", 24),
        ["round 140: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 140: the gateway routes each request by policy", 32),
        ["round 140: the gateway routes", "each request by policy"],
    ),
    (
        ("round 140: memory grows until the buffer is full", 4),
        ["round", "140:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 140: memory grows until the buffer is full", 8),
        ["round", "140:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 140: memory grows until the buffer is full", 12),
        ["round 140:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 140: memory grows until the buffer is full", 16),
        ["round 140:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 140: memory grows until the buffer is full", 24), ["round 140: memory grows", "until the buffer is full"]),
    (("round 140: memory grows until the buffer is full", 32), ["round 140: memory grows until", "the buffer is full"]),
    (
        ("round 140: the cluster mirrors every packet twice", 4),
        ["round", "140:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 140: the cluster mirrors every packet twice", 8),
        ["round", "140: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 140: the cluster mirrors every packet twice", 12),
        ["round 140:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 140: the cluster mirrors every packet twice", 16),
        ["round 140: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 140: the cluster mirrors every packet twice", 24),
        ["round 140: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 140: the cluster mirrors every packet twice", 32),
        ["round 140: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", 4),
        ["round", "140:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", 8),
        ["round", "140:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", 12),
        ["round 140:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", 16),
        ["round 140:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", 24),
        ["round 140: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 140: ranking uses tokens learned from the corpus", 32),
        ["round 140: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 140: a long session ends when the candle dies", 4),
        ["round", "140:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 140: a long session ends when the candle dies", 8),
        ["round", "140: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 140: a long session ends when the candle dies", 12),
        ["round 140: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 140: a long session ends when the candle dies", 16),
        ["round 140: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 140: a long session ends when the candle dies", 24),
        ["round 140: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 140: a long session ends when the candle dies", 32),
        ["round 140: a long session ends", "when the candle dies"],
    ),
    (
        ("round 140: encode the prompt then map the result", 4),
        ["round", "140:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 140: encode the prompt then map the result", 8),
        ["round", "140:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 140: encode the prompt then map the result", 12),
        ["round 140:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 140: encode the prompt then map the result", 16),
        ["round 140:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 140: encode the prompt then map the result", 24),
        ["round 140: encode the", "prompt then map the", "result"],
    ),
    (("round 140: encode the prompt then map the result", 32), ["round 140: encode the prompt", "then map the result"]),
    (
        ("round 140: the kernel wakes the worker at dawn", 4),
        ["round", "140:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 140: the kernel wakes the worker at dawn", 8),
        ["round", "140: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 140: the kernel wakes the worker at dawn", 12),
        ["round 140:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 140: the kernel wakes the worker at dawn", 16), ["round 140: the", "kernel wakes the", "worker at dawn"]),
    (("round 140: the kernel wakes the worker at dawn", 24), ["round 140: the kernel", "wakes the worker at dawn"]),
    (("round 140: the kernel wakes the worker at dawn", 32), ["round 140: the kernel wakes the", "worker at dawn"]),
    (
        ("round 140: service latency drops after the patch", 4),
        ["round", "140:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 140: service latency drops after the patch", 8),
        ["round", "140:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 140: service latency drops after the patch", 12),
        ["round 140:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 140: service latency drops after the patch", 16),
        ["round 140:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 140: service latency drops after the patch", 24),
        ["round 140: service", "latency drops after the", "patch"],
    ),
    (("round 140: service latency drops after the patch", 32), ["round 140: service latency drops", "after the patch"]),
    (
        ("round 140: the library caches every vector it sees", 4),
        ["round", "140:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 140: the library caches every vector it sees", 8),
        ["round", "140: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 140: the library caches every vector it sees", 12),
        ["round 140:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 140: the library caches every vector it sees", 16),
        ["round 140: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 140: the library caches every vector it sees", 24),
        ["round 140: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 140: the library caches every vector it sees", 32),
        ["round 140: the library caches", "every vector it sees"],
    ),
    (
        ("round 140: agents argue then the debate resolves", 4),
        ["round", "140:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 140: agents argue then the debate resolves", 8),
        ["round", "140:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 140: agents argue then the debate resolves", 12),
        ["round 140:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 140: agents argue then the debate resolves", 16),
        ["round 140:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 140: agents argue then the debate resolves", 24), ["round 140: agents argue", "then the debate resolves"]),
    (("round 140: agents argue then the debate resolves", 32), ["round 140: agents argue then the", "debate resolves"]),
    (
        ("round 140: the filter keeps only strong matches", 4),
        ["round", "140:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 140: the filter keeps only strong matches", 8),
        ["round", "140: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 140: the filter keeps only strong matches", 12),
        ["round 140:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 140: the filter keeps only strong matches", 16),
        ["round 140: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 140: the filter keeps only strong matches", 24),
        ["round 140: the filter", "keeps only strong", "matches"],
    ),
    (("round 140: the filter keeps only strong matches", 32), ["round 140: the filter keeps only", "strong matches"]),
    (
        ("round 140: the model answers with a short reply", 4),
        ["round", "140:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 140: the model answers with a short reply", 8),
        ["round", "140: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 140: the model answers with a short reply", 12),
        ["round 140:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 140: the model answers with a short reply", 16),
        ["round 140: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 140: the model answers with a short reply", 24),
        ["round 140: the model", "answers with a short", "reply"],
    ),
    (("round 140: the model answers with a short reply", 32), ["round 140: the model answers", "with a short reply"]),
    (
        ("round 140: the recorder stores the reasoning trace", 4),
        ["round", "140:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 140: the recorder stores the reasoning trace", 8),
        ["round", "140: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 140: the recorder stores the reasoning trace", 12),
        ["round 140:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 140: the recorder stores the reasoning trace", 16),
        ["round 140: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 140: the recorder stores the reasoning trace", 24),
        ["round 140: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 140: the recorder stores the reasoning trace", 32),
        ["round 140: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 140: the angel watches the processor run", 4),
        ["round", "140:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 140: the angel watches the processor run", 8),
        ["round", "140: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 140: the angel watches the processor run", 12),
        ["round 140:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 140: the angel watches the processor run", 16),
        ["round 140: the", "angel watches", "the processor", "run"],
    ),
    (("round 140: the angel watches the processor run", 24), ["round 140: the angel", "watches the processor", "run"]),
    (("round 140: the angel watches the processor run", 32), ["round 140: the angel watches the", "processor run"]),
    (
        ("round 140: angle of the vector decides the match", 4),
        ["round", "140:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 140: angle of the vector decides the match", 8),
        ["round", "140:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 140: angle of the vector decides the match", 12),
        ["round 140:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 140: angle of the vector decides the match", 16),
        ["round 140: angle", "of the vector", "decides the", "match"],
    ),
    (("round 140: angle of the vector decides the match", 24), ["round 140: angle of the", "vector decides the match"]),
    (("round 140: angle of the vector decides the match", 32), ["round 140: angle of the vector", "decides the match"]),
    (
        ("round 140: the candle burns twice as long at night", 4),
        ["round", "140:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 140: the candle burns twice as long at night", 8),
        ["round", "140: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 140: the candle burns twice as long at night", 12),
        ["round 140:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 140: the candle burns twice as long at night", 16),
        ["round 140: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 140: the candle burns twice as long at night", 24),
        ["round 140: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 140: the candle burns twice as long at night", 32),
        ["round 140: the candle burns", "twice as long at night"],
    ),
    (
        ("round 140: a mirror of the universe in one line", 4),
        ["round", "140:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 140: a mirror of the universe in one line", 8),
        ["round", "140: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 140: a mirror of the universe in one line", 12),
        ["round 140: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 140: a mirror of the universe in one line", 16),
        ["round 140: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 140: a mirror of the universe in one line", 24), ["round 140: a mirror of", "the universe in one line"]),
    (("round 140: a mirror of the universe in one line", 32), ["round 140: a mirror of the", "universe in one line"]),
    (
        ("round 140: the queue drains before the storm", 4),
        ["round", "140:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 140: the queue drains before the storm", 8),
        ["round", "140: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 140: the queue drains before the storm", 12),
        ["round 140:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 140: the queue drains before the storm", 16), ["round 140: the", "queue drains", "before the storm"]),
    (("round 140: the queue drains before the storm", 24), ["round 140: the queue", "drains before the storm"]),
    (("round 140: the queue drains before the storm", 32), ["round 140: the queue drains", "before the storm"]),
    (
        ("kitten140 sitting140 agent140 angle140 universe140 memory140", 6),
        ["kitten140", "sitting140", "agent140", "angle140", "universe140", "memory140"],
    ),
    (
        ("kitten140 sitting140 agent140 angle140 universe140 memory140", 10),
        ["kitten140", "sitting140", "agent140", "angle140", "universe140", "memory140"],
    ),
    (
        ("kitten140 sitting140 agent140 angle140 universe140 memory140", 18),
        ["kitten140", "sitting140", "agent140 angle140", "universe140", "memory140"],
    ),
    (
        ("kitten140 sitting140 agent140 angle140 universe140 memory140", 28),
        ["kitten140 sitting140", "agent140 angle140", "universe140 memory140"],
    ),
    (
        ("sitting140 agent140 angle140 universe140 memory140 stream140", 6),
        ["sitting140", "agent140", "angle140", "universe140", "memory140", "stream140"],
    ),
    (
        ("sitting140 agent140 angle140 universe140 memory140 stream140", 10),
        ["sitting140", "agent140", "angle140", "universe140", "memory140", "stream140"],
    ),
    (
        ("sitting140 agent140 angle140 universe140 memory140 stream140", 18),
        ["sitting140", "agent140 angle140", "universe140", "memory140", "stream140"],
    ),
    (
        ("sitting140 agent140 angle140 universe140 memory140 stream140", 28),
        ["sitting140 agent140 angle140", "universe140 memory140", "stream140"],
    ),
    (
        ("agent140 angle140 universe140 memory140 stream140 context140", 6),
        ["agent140", "angle140", "universe140", "memory140", "stream140", "context140"],
    ),
    (
        ("agent140 angle140 universe140 memory140 stream140 context140", 10),
        ["agent140", "angle140", "universe140", "memory140", "stream140", "context140"],
    ),
    (
        ("agent140 angle140 universe140 memory140 stream140 context140", 18),
        ["agent140 angle140", "universe140", "memory140", "stream140", "context140"],
    ),
    (
        ("agent140 angle140 universe140 memory140 stream140 context140", 28),
        ["agent140 angle140", "universe140 memory140", "stream140 context140"],
    ),
    (
        ("angle140 universe140 memory140 stream140 context140 knowledge140", 6),
        ["angle140", "universe140", "memory140", "stream140", "context140", "knowledge140"],
    ),
    (
        ("angle140 universe140 memory140 stream140 context140 knowledge140", 10),
        ["angle140", "universe140", "memory140", "stream140", "context140", "knowledge140"],
    ),
    (
        ("angle140 universe140 memory140 stream140 context140 knowledge140", 18),
        ["angle140", "universe140", "memory140", "stream140", "context140", "knowledge140"],
    ),
    (
        ("angle140 universe140 memory140 stream140 context140 knowledge140", 28),
        ["angle140 universe140", "memory140 stream140", "context140 knowledge140"],
    ),
    (
        ("universe140 memory140 stream140 context140 knowledge140 vector140", 6),
        ["universe140", "memory140", "stream140", "context140", "knowledge140", "vector140"],
    ),
    (
        ("universe140 memory140 stream140 context140 knowledge140 vector140", 10),
        ["universe140", "memory140", "stream140", "context140", "knowledge140", "vector140"],
    ),
    (
        ("universe140 memory140 stream140 context140 knowledge140 vector140", 18),
        ["universe140", "memory140", "stream140", "context140", "knowledge140", "vector140"],
    ),
    (
        ("universe140 memory140 stream140 context140 knowledge140 vector140", 28),
        ["universe140 memory140", "stream140 context140", "knowledge140 vector140"],
    ),
    (
        ("memory140 stream140 context140 knowledge140 vector140 processor140", 6),
        ["memory140", "stream140", "context140", "knowledge140", "vector140", "processor140"],
    ),
    (
        ("memory140 stream140 context140 knowledge140 vector140 processor140", 10),
        ["memory140", "stream140", "context140", "knowledge140", "vector140", "processor140"],
    ),
    (
        ("memory140 stream140 context140 knowledge140 vector140 processor140", 18),
        ["memory140", "stream140", "context140", "knowledge140", "vector140", "processor140"],
    ),
    (
        ("memory140 stream140 context140 knowledge140 vector140 processor140", 28),
        ["memory140 stream140", "context140 knowledge140", "vector140 processor140"],
    ),
    (
        ("stream140 context140 knowledge140 vector140 processor140 reasoning140", 6),
        ["stream140", "context140", "knowledge140", "vector140", "processor140", "reasoning140"],
    ),
    (
        ("stream140 context140 knowledge140 vector140 processor140 reasoning140", 10),
        ["stream140", "context140", "knowledge140", "vector140", "processor140", "reasoning140"],
    ),
    (
        ("stream140 context140 knowledge140 vector140 processor140 reasoning140", 18),
        ["stream140", "context140", "knowledge140", "vector140", "processor140", "reasoning140"],
    ),
    (
        ("stream140 context140 knowledge140 vector140 processor140 reasoning140", 28),
        ["stream140 context140", "knowledge140 vector140", "processor140 reasoning140"],
    ),
    (
        ("context140 knowledge140 vector140 processor140 reasoning140 machine140", 6),
        ["context140", "knowledge140", "vector140", "processor140", "reasoning140", "machine140"],
    ),
    (
        ("context140 knowledge140 vector140 processor140 reasoning140 machine140", 10),
        ["context140", "knowledge140", "vector140", "processor140", "reasoning140", "machine140"],
    ),
    (
        ("context140 knowledge140 vector140 processor140 reasoning140 machine140", 18),
        ["context140", "knowledge140", "vector140", "processor140", "reasoning140", "machine140"],
    ),
    (
        ("context140 knowledge140 vector140 processor140 reasoning140 machine140", 28),
        ["context140 knowledge140", "vector140 processor140", "reasoning140 machine140"],
    ),
    (
        ("knowledge140 vector140 processor140 reasoning140 machine140 learning140", 6),
        ["knowledge140", "vector140", "processor140", "reasoning140", "machine140", "learning140"],
    ),
    (
        ("knowledge140 vector140 processor140 reasoning140 machine140 learning140", 10),
        ["knowledge140", "vector140", "processor140", "reasoning140", "machine140", "learning140"],
    ),
    (
        ("knowledge140 vector140 processor140 reasoning140 machine140 learning140", 18),
        ["knowledge140", "vector140", "processor140", "reasoning140", "machine140", "learning140"],
    ),
    (
        ("knowledge140 vector140 processor140 reasoning140 machine140 learning140", 28),
        ["knowledge140 vector140", "processor140 reasoning140", "machine140 learning140"],
    ),
    (
        ("vector140 processor140 reasoning140 machine140 learning140 model140", 6),
        ["vector140", "processor140", "reasoning140", "machine140", "learning140", "model140"],
    ),
    (
        ("vector140 processor140 reasoning140 machine140 learning140 model140", 10),
        ["vector140", "processor140", "reasoning140", "machine140", "learning140", "model140"],
    ),
    (
        ("vector140 processor140 reasoning140 machine140 learning140 model140", 18),
        ["vector140", "processor140", "reasoning140", "machine140", "learning140", "model140"],
    ),
    (
        ("vector140 processor140 reasoning140 machine140 learning140 model140", 28),
        ["vector140 processor140", "reasoning140 machine140", "learning140 model140"],
    ),
    (
        ("processor140 reasoning140 machine140 learning140 model140 token140", 6),
        ["processor140", "reasoning140", "machine140", "learning140", "model140", "token140"],
    ),
    (
        ("processor140 reasoning140 machine140 learning140 model140 token140", 10),
        ["processor140", "reasoning140", "machine140", "learning140", "model140", "token140"],
    ),
    (
        ("processor140 reasoning140 machine140 learning140 model140 token140", 18),
        ["processor140", "reasoning140", "machine140", "learning140", "model140 token140"],
    ),
    (
        ("processor140 reasoning140 machine140 learning140 model140 token140", 28),
        ["processor140 reasoning140", "machine140 learning140", "model140 token140"],
    ),
    (
        ("reasoning140 machine140 learning140 model140 token140 prompt140", 6),
        ["reasoning140", "machine140", "learning140", "model140", "token140", "prompt140"],
    ),
    (
        ("reasoning140 machine140 learning140 model140 token140 prompt140", 10),
        ["reasoning140", "machine140", "learning140", "model140", "token140", "prompt140"],
    ),
    (
        ("reasoning140 machine140 learning140 model140 token140 prompt140", 18),
        ["reasoning140", "machine140", "learning140", "model140 token140", "prompt140"],
    ),
    (
        ("reasoning140 machine140 learning140 model140 token140 prompt140", 28),
        ["reasoning140 machine140", "learning140 model140", "token140 prompt140"],
    ),
    (
        ("machine140 learning140 model140 token140 prompt140 session140", 6),
        ["machine140", "learning140", "model140", "token140", "prompt140", "session140"],
    ),
    (
        ("machine140 learning140 model140 token140 prompt140 session140", 10),
        ["machine140", "learning140", "model140", "token140", "prompt140", "session140"],
    ),
    (
        ("machine140 learning140 model140 token140 prompt140 session140", 18),
        ["machine140", "learning140", "model140 token140", "prompt140", "session140"],
    ),
    (
        ("machine140 learning140 model140 token140 prompt140 session140", 28),
        ["machine140 learning140", "model140 token140 prompt140", "session140"],
    ),
    (
        ("learning140 model140 token140 prompt140 session140 library140", 6),
        ["learning140", "model140", "token140", "prompt140", "session140", "library140"],
    ),
    (
        ("learning140 model140 token140 prompt140 session140 library140", 10),
        ["learning140", "model140", "token140", "prompt140", "session140", "library140"],
    ),
    (
        ("learning140 model140 token140 prompt140 session140 library140", 18),
        ["learning140", "model140 token140", "prompt140", "session140", "library140"],
    ),
    (
        ("learning140 model140 token140 prompt140 session140 library140", 28),
        ["learning140 model140", "token140 prompt140", "session140 library140"],
    ),
    (
        ("model140 token140 prompt140 session140 library140 service140", 6),
        ["model140", "token140", "prompt140", "session140", "library140", "service140"],
    ),
    (
        ("model140 token140 prompt140 session140 library140 service140", 10),
        ["model140", "token140", "prompt140", "session140", "library140", "service140"],
    ),
    (
        ("model140 token140 prompt140 session140 library140 service140", 18),
        ["model140 token140", "prompt140", "session140", "library140", "service140"],
    ),
    (
        ("model140 token140 prompt140 session140 library140 service140", 28),
        ["model140 token140 prompt140", "session140 library140", "service140"],
    ),
    (
        ("token140 prompt140 session140 library140 service140 gateway140", 6),
        ["token140", "prompt140", "session140", "library140", "service140", "gateway140"],
    ),
    (
        ("token140 prompt140 session140 library140 service140 gateway140", 10),
        ["token140", "prompt140", "session140", "library140", "service140", "gateway140"],
    ),
    (
        ("token140 prompt140 session140 library140 service140 gateway140", 18),
        ["token140 prompt140", "session140", "library140", "service140", "gateway140"],
    ),
    (
        ("token140 prompt140 session140 library140 service140 gateway140", 28),
        ["token140 prompt140", "session140 library140", "service140 gateway140"],
    ),
    (
        ("prompt140 session140 library140 service140 gateway140 storage140", 6),
        ["prompt140", "session140", "library140", "service140", "gateway140", "storage140"],
    ),
    (
        ("prompt140 session140 library140 service140 gateway140 storage140", 10),
        ["prompt140", "session140", "library140", "service140", "gateway140", "storage140"],
    ),
    (
        ("prompt140 session140 library140 service140 gateway140 storage140", 18),
        ["prompt140", "session140", "library140", "service140", "gateway140", "storage140"],
    ),
    (
        ("prompt140 session140 library140 service140 gateway140 storage140", 28),
        ["prompt140 session140", "library140 service140", "gateway140 storage140"],
    ),
    (
        ("session140 library140 service140 gateway140 storage140 network140", 6),
        ["session140", "library140", "service140", "gateway140", "storage140", "network140"],
    ),
    (
        ("session140 library140 service140 gateway140 storage140 network140", 10),
        ["session140", "library140", "service140", "gateway140", "storage140", "network140"],
    ),
    (
        ("session140 library140 service140 gateway140 storage140 network140", 18),
        ["session140", "library140", "service140", "gateway140", "storage140", "network140"],
    ),
    (
        ("session140 library140 service140 gateway140 storage140 network140", 28),
        ["session140 library140", "service140 gateway140", "storage140 network140"],
    ),
    (
        ("library140 service140 gateway140 storage140 network140 latency140", 6),
        ["library140", "service140", "gateway140", "storage140", "network140", "latency140"],
    ),
    (
        ("library140 service140 gateway140 storage140 network140 latency140", 10),
        ["library140", "service140", "gateway140", "storage140", "network140", "latency140"],
    ),
    (
        ("library140 service140 gateway140 storage140 network140 latency140", 18),
        ["library140", "service140", "gateway140", "storage140", "network140", "latency140"],
    ),
    (
        ("library140 service140 gateway140 storage140 network140 latency140", 28),
        ["library140 service140", "gateway140 storage140", "network140 latency140"],
    ),
    (
        ("service140 gateway140 storage140 network140 latency140 buffer140", 6),
        ["service140", "gateway140", "storage140", "network140", "latency140", "buffer140"],
    ),
    (
        ("service140 gateway140 storage140 network140 latency140 buffer140", 10),
        ["service140", "gateway140", "storage140", "network140", "latency140", "buffer140"],
    ),
    (
        ("service140 gateway140 storage140 network140 latency140 buffer140", 18),
        ["service140", "gateway140", "storage140", "network140", "latency140", "buffer140"],
    ),
    (
        ("service140 gateway140 storage140 network140 latency140 buffer140", 28),
        ["service140 gateway140", "storage140 network140", "latency140 buffer140"],
    ),
    (
        ("gateway140 storage140 network140 latency140 buffer140 queue140", 6),
        ["gateway140", "storage140", "network140", "latency140", "buffer140", "queue140"],
    ),
    (
        ("gateway140 storage140 network140 latency140 buffer140 queue140", 10),
        ["gateway140", "storage140", "network140", "latency140", "buffer140", "queue140"],
    ),
    (
        ("gateway140 storage140 network140 latency140 buffer140 queue140", 18),
        ["gateway140", "storage140", "network140", "latency140", "buffer140 queue140"],
    ),
    (
        ("gateway140 storage140 network140 latency140 buffer140 queue140", 28),
        ["gateway140 storage140", "network140 latency140", "buffer140 queue140"],
    ),
    (
        ("storage140 network140 latency140 buffer140 queue140 worker140", 6),
        ["storage140", "network140", "latency140", "buffer140", "queue140", "worker140"],
    ),
    (
        ("storage140 network140 latency140 buffer140 queue140 worker140", 10),
        ["storage140", "network140", "latency140", "buffer140", "queue140", "worker140"],
    ),
    (
        ("storage140 network140 latency140 buffer140 queue140 worker140", 18),
        ["storage140", "network140", "latency140", "buffer140 queue140", "worker140"],
    ),
    (
        ("storage140 network140 latency140 buffer140 queue140 worker140", 28),
        ["storage140 network140", "latency140 buffer140", "queue140 worker140"],
    ),
    (
        ("network140 latency140 buffer140 queue140 worker140 kernel140", 6),
        ["network140", "latency140", "buffer140", "queue140", "worker140", "kernel140"],
    ),
    (
        ("network140 latency140 buffer140 queue140 worker140 kernel140", 10),
        ["network140", "latency140", "buffer140", "queue140", "worker140", "kernel140"],
    ),
    (
        ("network140 latency140 buffer140 queue140 worker140 kernel140", 18),
        ["network140", "latency140", "buffer140 queue140", "worker140", "kernel140"],
    ),
    (
        ("network140 latency140 buffer140 queue140 worker140 kernel140", 28),
        ["network140 latency140", "buffer140 queue140 worker140", "kernel140"],
    ),
    (
        ("latency140 buffer140 queue140 worker140 kernel140 signal140", 6),
        ["latency140", "buffer140", "queue140", "worker140", "kernel140", "signal140"],
    ),
    (
        ("latency140 buffer140 queue140 worker140 kernel140 signal140", 10),
        ["latency140", "buffer140", "queue140", "worker140", "kernel140", "signal140"],
    ),
    (
        ("latency140 buffer140 queue140 worker140 kernel140 signal140", 18),
        ["latency140", "buffer140 queue140", "worker140", "kernel140", "signal140"],
    ),
    (
        ("latency140 buffer140 queue140 worker140 kernel140 signal140", 28),
        ["latency140 buffer140", "queue140 worker140 kernel140", "signal140"],
    ),
    (
        ("buffer140 queue140 worker140 kernel140 signal140 packet140", 6),
        ["buffer140", "queue140", "worker140", "kernel140", "signal140", "packet140"],
    ),
    (
        ("buffer140 queue140 worker140 kernel140 signal140 packet140", 10),
        ["buffer140", "queue140", "worker140", "kernel140", "signal140", "packet140"],
    ),
    (
        ("buffer140 queue140 worker140 kernel140 signal140 packet140", 18),
        ["buffer140 queue140", "worker140", "kernel140", "signal140", "packet140"],
    ),
    (
        ("buffer140 queue140 worker140 kernel140 signal140 packet140", 28),
        ["buffer140 queue140 worker140", "kernel140 signal140", "packet140"],
    ),
    (
        ("queue140 worker140 kernel140 signal140 packet140 router140", 6),
        ["queue140", "worker140", "kernel140", "signal140", "packet140", "router140"],
    ),
    (
        ("queue140 worker140 kernel140 signal140 packet140 router140", 10),
        ["queue140", "worker140", "kernel140", "signal140", "packet140", "router140"],
    ),
    (
        ("queue140 worker140 kernel140 signal140 packet140 router140", 18),
        ["queue140 worker140", "kernel140", "signal140", "packet140", "router140"],
    ),
    (
        ("queue140 worker140 kernel140 signal140 packet140 router140", 28),
        ["queue140 worker140 kernel140", "signal140 packet140", "router140"],
    ),
    (
        ("worker140 kernel140 signal140 packet140 router140 cluster140", 6),
        ["worker140", "kernel140", "signal140", "packet140", "router140", "cluster140"],
    ),
    (
        ("worker140 kernel140 signal140 packet140 router140 cluster140", 10),
        ["worker140", "kernel140", "signal140", "packet140", "router140", "cluster140"],
    ),
    (
        ("worker140 kernel140 signal140 packet140 router140 cluster140", 18),
        ["worker140", "kernel140", "signal140", "packet140", "router140", "cluster140"],
    ),
    (
        ("worker140 kernel140 signal140 packet140 router140 cluster140", 28),
        ["worker140 kernel140", "signal140 packet140", "router140 cluster140"],
    ),
    (
        ("kernel140 signal140 packet140 router140 cluster140 mirror140", 6),
        ["kernel140", "signal140", "packet140", "router140", "cluster140", "mirror140"],
    ),
    (
        ("kernel140 signal140 packet140 router140 cluster140 mirror140", 10),
        ["kernel140", "signal140", "packet140", "router140", "cluster140", "mirror140"],
    ),
    (
        ("kernel140 signal140 packet140 router140 cluster140 mirror140", 18),
        ["kernel140", "signal140", "packet140", "router140", "cluster140", "mirror140"],
    ),
    (
        ("kernel140 signal140 packet140 router140 cluster140 mirror140", 28),
        ["kernel140 signal140", "packet140 router140", "cluster140 mirror140"],
    ),
    (
        ("signal140 packet140 router140 cluster140 mirror140 filter140", 6),
        ["signal140", "packet140", "router140", "cluster140", "mirror140", "filter140"],
    ),
    (
        ("signal140 packet140 router140 cluster140 mirror140 filter140", 10),
        ["signal140", "packet140", "router140", "cluster140", "mirror140", "filter140"],
    ),
    (
        ("signal140 packet140 router140 cluster140 mirror140 filter140", 18),
        ["signal140", "packet140", "router140", "cluster140", "mirror140", "filter140"],
    ),
    (
        ("signal140 packet140 router140 cluster140 mirror140 filter140", 28),
        ["signal140 packet140", "router140 cluster140", "mirror140 filter140"],
    ),
    (
        ("packet140 router140 cluster140 mirror140 filter140 ranking140", 6),
        ["packet140", "router140", "cluster140", "mirror140", "filter140", "ranking140"],
    ),
    (
        ("packet140 router140 cluster140 mirror140 filter140 ranking140", 10),
        ["packet140", "router140", "cluster140", "mirror140", "filter140", "ranking140"],
    ),
    (
        ("packet140 router140 cluster140 mirror140 filter140 ranking140", 18),
        ["packet140", "router140", "cluster140", "mirror140", "filter140", "ranking140"],
    ),
    (
        ("packet140 router140 cluster140 mirror140 filter140 ranking140", 28),
        ["packet140 router140", "cluster140 mirror140", "filter140 ranking140"],
    ),
    (
        ("router140 cluster140 mirror140 filter140 ranking140 encoding140", 6),
        ["router140", "cluster140", "mirror140", "filter140", "ranking140", "encoding140"],
    ),
    (
        ("router140 cluster140 mirror140 filter140 ranking140 encoding140", 10),
        ["router140", "cluster140", "mirror140", "filter140", "ranking140", "encoding140"],
    ),
    (
        ("router140 cluster140 mirror140 filter140 ranking140 encoding140", 18),
        ["router140", "cluster140", "mirror140", "filter140", "ranking140", "encoding140"],
    ),
    (
        ("router140 cluster140 mirror140 filter140 ranking140 encoding140", 28),
        ["router140 cluster140", "mirror140 filter140", "ranking140 encoding140"],
    ),
    (
        ("cluster140 mirror140 filter140 ranking140 encoding140 mapping140", 6),
        ["cluster140", "mirror140", "filter140", "ranking140", "encoding140", "mapping140"],
    ),
    (
        ("cluster140 mirror140 filter140 ranking140 encoding140 mapping140", 10),
        ["cluster140", "mirror140", "filter140", "ranking140", "encoding140", "mapping140"],
    ),
    (
        ("cluster140 mirror140 filter140 ranking140 encoding140 mapping140", 18),
        ["cluster140", "mirror140", "filter140", "ranking140", "encoding140", "mapping140"],
    ),
    (
        ("cluster140 mirror140 filter140 ranking140 encoding140 mapping140", 28),
        ["cluster140 mirror140", "filter140 ranking140", "encoding140 mapping140"],
    ),
    (
        ("mirror140 filter140 ranking140 encoding140 mapping140 record140", 6),
        ["mirror140", "filter140", "ranking140", "encoding140", "mapping140", "record140"],
    ),
    (
        ("mirror140 filter140 ranking140 encoding140 mapping140 record140", 10),
        ["mirror140", "filter140", "ranking140", "encoding140", "mapping140", "record140"],
    ),
    (
        ("mirror140 filter140 ranking140 encoding140 mapping140 record140", 18),
        ["mirror140", "filter140", "ranking140", "encoding140", "mapping140", "record140"],
    ),
    (
        ("mirror140 filter140 ranking140 encoding140 mapping140 record140", 28),
        ["mirror140 filter140", "ranking140 encoding140", "mapping140 record140"],
    ),
    (
        ("filter140 ranking140 encoding140 mapping140 record140 candle140", 6),
        ["filter140", "ranking140", "encoding140", "mapping140", "record140", "candle140"],
    ),
    (
        ("filter140 ranking140 encoding140 mapping140 record140 candle140", 10),
        ["filter140", "ranking140", "encoding140", "mapping140", "record140", "candle140"],
    ),
    (
        ("filter140 ranking140 encoding140 mapping140 record140 candle140", 18),
        ["filter140", "ranking140", "encoding140", "mapping140", "record140", "candle140"],
    ),
    (
        ("filter140 ranking140 encoding140 mapping140 record140 candle140", 28),
        ["filter140 ranking140", "encoding140 mapping140", "record140 candle140"],
    ),
    (
        ("ranking140 encoding140 mapping140 record140 candle140 thread140", 6),
        ["ranking140", "encoding140", "mapping140", "record140", "candle140", "thread140"],
    ),
    (
        ("ranking140 encoding140 mapping140 record140 candle140 thread140", 10),
        ["ranking140", "encoding140", "mapping140", "record140", "candle140", "thread140"],
    ),
    (
        ("ranking140 encoding140 mapping140 record140 candle140 thread140", 18),
        ["ranking140", "encoding140", "mapping140", "record140", "candle140", "thread140"],
    ),
    (
        ("ranking140 encoding140 mapping140 record140 candle140 thread140", 28),
        ["ranking140 encoding140", "mapping140 record140", "candle140 thread140"],
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
