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
        ("round 63: the quick brown fox jumps over the lazy dog", 4),
        ["round", "63:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 63: the quick brown fox jumps over the lazy dog", 8),
        ["round", "63: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 63: the quick brown fox jumps over the lazy dog", 12),
        ["round 63:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 63: the quick brown fox jumps over the lazy dog", 16),
        ["round 63: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 63: the quick brown fox jumps over the lazy dog", 24),
        ["round 63: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 63: the quick brown fox jumps over the lazy dog", 32),
        ["round 63: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 63: agentuniverse is a framework for multi agents", 4),
        ["round", "63:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 63: agentuniverse is a framework for multi agents", 8),
        ["round", "63:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 63: agentuniverse is a framework for multi agents", 12),
        ["round 63:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 63: agentuniverse is a framework for multi agents", 16),
        ["round 63:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 63: agentuniverse is a framework for multi agents", 24),
        ["round 63: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 63: agentuniverse is a framework for multi agents", 32),
        ["round 63: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 63: knowledge stored as vectors enables retrieval", 4),
        ["round", "63:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 63: knowledge stored as vectors enables retrieval", 8),
        ["round", "63:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 63: knowledge stored as vectors enables retrieval", 12),
        ["round 63:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 63: knowledge stored as vectors enables retrieval", 16),
        ["round 63:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 63: knowledge stored as vectors enables retrieval", 24),
        ["round 63: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 63: knowledge stored as vectors enables retrieval", 32),
        ["round 63: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 63: the processor reads the record then stops", 4),
        ["round", "63:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 63: the processor reads the record then stops", 8),
        ["round", "63: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 63: the processor reads the record then stops", 12),
        ["round 63:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 63: the processor reads the record then stops", 16),
        ["round 63: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 63: the processor reads the record then stops", 24),
        ["round 63: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 63: the processor reads the record then stops", 32),
        ["round 63: the processor reads", "the record then stops"],
    ),
    (
        ("round 63: a worker pulls the next task from the queue", 4),
        ["round", "63:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 63: a worker pulls the next task from the queue", 8),
        ["round", "63: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 63: a worker pulls the next task from the queue", 12),
        ["round 63: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 63: a worker pulls the next task from the queue", 16),
        ["round 63: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 63: a worker pulls the next task from the queue", 24),
        ["round 63: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 63: a worker pulls the next task from the queue", 32),
        ["round 63: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 63: signals travel through the network layer", 4),
        ["round", "63:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 63: signals travel through the network layer", 8),
        ["round", "63:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 63: signals travel through the network layer", 12),
        ["round 63:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 63: signals travel through the network layer", 16),
        ["round 63:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 63: signals travel through the network layer", 24),
        ["round 63: signals travel", "through the network", "layer"],
    ),
    (
        ("round 63: signals travel through the network layer", 32),
        ["round 63: signals travel through", "the network layer"],
    ),
    (
        ("round 63: the gateway routes each request by policy", 4),
        ["round", "63:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 63: the gateway routes each request by policy", 8),
        ["round", "63: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 63: the gateway routes each request by policy", 12),
        ["round 63:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 63: the gateway routes each request by policy", 16),
        ["round 63: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 63: the gateway routes each request by policy", 24),
        ["round 63: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 63: the gateway routes each request by policy", 32),
        ["round 63: the gateway routes", "each request by policy"],
    ),
    (
        ("round 63: memory grows until the buffer is full", 4),
        ["round", "63:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 63: memory grows until the buffer is full", 8),
        ["round", "63:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 63: memory grows until the buffer is full", 12),
        ["round 63:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 63: memory grows until the buffer is full", 16),
        ["round 63: memory", "grows until the", "buffer is full"],
    ),
    (("round 63: memory grows until the buffer is full", 24), ["round 63: memory grows", "until the buffer is full"]),
    (("round 63: memory grows until the buffer is full", 32), ["round 63: memory grows until the", "buffer is full"]),
    (
        ("round 63: the cluster mirrors every packet twice", 4),
        ["round", "63:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 63: the cluster mirrors every packet twice", 8),
        ["round", "63: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 63: the cluster mirrors every packet twice", 12),
        ["round 63:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 63: the cluster mirrors every packet twice", 16),
        ["round 63: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 63: the cluster mirrors every packet twice", 24),
        ["round 63: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 63: the cluster mirrors every packet twice", 32), ["round 63: the cluster mirrors", "every packet twice"]),
    (
        ("round 63: ranking uses tokens learned from the corpus", 4),
        ["round", "63:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 63: ranking uses tokens learned from the corpus", 8),
        ["round", "63:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 63: ranking uses tokens learned from the corpus", 12),
        ["round 63:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 63: ranking uses tokens learned from the corpus", 16),
        ["round 63:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 63: ranking uses tokens learned from the corpus", 24),
        ["round 63: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 63: ranking uses tokens learned from the corpus", 32),
        ["round 63: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 63: a long session ends when the candle dies", 4),
        ["round", "63:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 63: a long session ends when the candle dies", 8),
        ["round", "63: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 63: a long session ends when the candle dies", 12),
        ["round 63: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 63: a long session ends when the candle dies", 16),
        ["round 63: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 63: a long session ends when the candle dies", 24),
        ["round 63: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 63: a long session ends when the candle dies", 32),
        ["round 63: a long session ends", "when the candle dies"],
    ),
    (
        ("round 63: encode the prompt then map the result", 4),
        ["round", "63:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 63: encode the prompt then map the result", 8),
        ["round", "63:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 63: encode the prompt then map the result", 12),
        ["round 63:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 63: encode the prompt then map the result", 16),
        ["round 63: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 63: encode the prompt then map the result", 24),
        ["round 63: encode the", "prompt then map the", "result"],
    ),
    (("round 63: encode the prompt then map the result", 32), ["round 63: encode the prompt then", "map the result"]),
    (
        ("round 63: the kernel wakes the worker at dawn", 4),
        ["round", "63:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 63: the kernel wakes the worker at dawn", 8),
        ["round", "63: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 63: the kernel wakes the worker at dawn", 12),
        ["round 63:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 63: the kernel wakes the worker at dawn", 16), ["round 63: the", "kernel wakes the", "worker at dawn"]),
    (("round 63: the kernel wakes the worker at dawn", 24), ["round 63: the kernel", "wakes the worker at dawn"]),
    (("round 63: the kernel wakes the worker at dawn", 32), ["round 63: the kernel wakes the", "worker at dawn"]),
    (
        ("round 63: service latency drops after the patch", 4),
        ["round", "63:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 63: service latency drops after the patch", 8),
        ["round", "63:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 63: service latency drops after the patch", 12),
        ["round 63:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 63: service latency drops after the patch", 16),
        ["round 63:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 63: service latency drops after the patch", 24),
        ["round 63: service", "latency drops after the", "patch"],
    ),
    (("round 63: service latency drops after the patch", 32), ["round 63: service latency drops", "after the patch"]),
    (
        ("round 63: the library caches every vector it sees", 4),
        ["round", "63:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 63: the library caches every vector it sees", 8),
        ["round", "63: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 63: the library caches every vector it sees", 12),
        ["round 63:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 63: the library caches every vector it sees", 16),
        ["round 63: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 63: the library caches every vector it sees", 24),
        ["round 63: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 63: the library caches every vector it sees", 32),
        ["round 63: the library caches", "every vector it sees"],
    ),
    (
        ("round 63: agents argue then the debate resolves", 4),
        ["round", "63:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 63: agents argue then the debate resolves", 8),
        ["round", "63:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 63: agents argue then the debate resolves", 12),
        ["round 63:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 63: agents argue then the debate resolves", 16),
        ["round 63: agents", "argue then the", "debate resolves"],
    ),
    (("round 63: agents argue then the debate resolves", 24), ["round 63: agents argue", "then the debate resolves"]),
    (("round 63: agents argue then the debate resolves", 32), ["round 63: agents argue then the", "debate resolves"]),
    (
        ("round 63: the filter keeps only strong matches", 4),
        ["round", "63:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 63: the filter keeps only strong matches", 8),
        ["round", "63: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 63: the filter keeps only strong matches", 12),
        ["round 63:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 63: the filter keeps only strong matches", 16),
        ["round 63: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 63: the filter keeps only strong matches", 24), ["round 63: the filter", "keeps only strong", "matches"]),
    (("round 63: the filter keeps only strong matches", 32), ["round 63: the filter keeps only", "strong matches"]),
    (
        ("round 63: the model answers with a short reply", 4),
        ["round", "63:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 63: the model answers with a short reply", 8),
        ["round", "63: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 63: the model answers with a short reply", 12),
        ["round 63:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 63: the model answers with a short reply", 16),
        ["round 63: the", "model answers", "with a short", "reply"],
    ),
    (("round 63: the model answers with a short reply", 24), ["round 63: the model", "answers with a short", "reply"]),
    (("round 63: the model answers with a short reply", 32), ["round 63: the model answers with", "a short reply"]),
    (
        ("round 63: the recorder stores the reasoning trace", 4),
        ["round", "63:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 63: the recorder stores the reasoning trace", 8),
        ["round", "63: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 63: the recorder stores the reasoning trace", 12),
        ["round 63:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 63: the recorder stores the reasoning trace", 16),
        ["round 63: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 63: the recorder stores the reasoning trace", 24),
        ["round 63: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 63: the recorder stores the reasoning trace", 32),
        ["round 63: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 63: the angel watches the processor run", 4),
        ["round", "63:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 63: the angel watches the processor run", 8),
        ["round", "63: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 63: the angel watches the processor run", 12),
        ["round 63:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 63: the angel watches the processor run", 16), ["round 63: the", "angel watches", "the processor", "run"]),
    (("round 63: the angel watches the processor run", 24), ["round 63: the angel", "watches the processor", "run"]),
    (("round 63: the angel watches the processor run", 32), ["round 63: the angel watches the", "processor run"]),
    (
        ("round 63: angle of the vector decides the match", 4),
        ["round", "63:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 63: angle of the vector decides the match", 8),
        ["round", "63:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 63: angle of the vector decides the match", 12),
        ["round 63:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 63: angle of the vector decides the match", 16),
        ["round 63: angle", "of the vector", "decides the", "match"],
    ),
    (("round 63: angle of the vector decides the match", 24), ["round 63: angle of the", "vector decides the match"]),
    (("round 63: angle of the vector decides the match", 32), ["round 63: angle of the vector", "decides the match"]),
    (
        ("round 63: the candle burns twice as long at night", 4),
        ["round", "63:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 63: the candle burns twice as long at night", 8),
        ["round", "63: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 63: the candle burns twice as long at night", 12),
        ["round 63:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 63: the candle burns twice as long at night", 16),
        ["round 63: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 63: the candle burns twice as long at night", 24),
        ["round 63: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 63: the candle burns twice as long at night", 32),
        ["round 63: the candle burns twice", "as long at night"],
    ),
    (
        ("round 63: a mirror of the universe in one line", 4),
        ["round", "63:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 63: a mirror of the universe in one line", 8),
        ["round", "63: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 63: a mirror of the universe in one line", 12),
        ["round 63: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 63: a mirror of the universe in one line", 16),
        ["round 63: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 63: a mirror of the universe in one line", 24), ["round 63: a mirror of", "the universe in one line"]),
    (("round 63: a mirror of the universe in one line", 32), ["round 63: a mirror of the", "universe in one line"]),
    (
        ("round 63: the queue drains before the storm", 4),
        ["round", "63:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 63: the queue drains before the storm", 8),
        ["round", "63: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 63: the queue drains before the storm", 12), ["round 63:", "the queue", "drains", "before the", "storm"]),
    (("round 63: the queue drains before the storm", 16), ["round 63: the", "queue drains", "before the storm"]),
    (("round 63: the queue drains before the storm", 24), ["round 63: the queue", "drains before the storm"]),
    (("round 63: the queue drains before the storm", 32), ["round 63: the queue drains", "before the storm"]),
    (
        ("kitten63 sitting63 agent63 angle63 universe63 memory63", 6),
        ["kitten63", "sitting63", "agent63", "angle63", "universe63", "memory63"],
    ),
    (
        ("kitten63 sitting63 agent63 angle63 universe63 memory63", 10),
        ["kitten63", "sitting63", "agent63", "angle63", "universe63", "memory63"],
    ),
    (
        ("kitten63 sitting63 agent63 angle63 universe63 memory63", 18),
        ["kitten63 sitting63", "agent63 angle63", "universe63", "memory63"],
    ),
    (
        ("kitten63 sitting63 agent63 angle63 universe63 memory63", 28),
        ["kitten63 sitting63 agent63", "angle63 universe63 memory63"],
    ),
    (
        ("sitting63 agent63 angle63 universe63 memory63 stream63", 6),
        ["sitting63", "agent63", "angle63", "universe63", "memory63", "stream63"],
    ),
    (
        ("sitting63 agent63 angle63 universe63 memory63 stream63", 10),
        ["sitting63", "agent63", "angle63", "universe63", "memory63", "stream63"],
    ),
    (
        ("sitting63 agent63 angle63 universe63 memory63 stream63", 18),
        ["sitting63 agent63", "angle63 universe63", "memory63 stream63"],
    ),
    (
        ("sitting63 agent63 angle63 universe63 memory63 stream63", 28),
        ["sitting63 agent63 angle63", "universe63 memory63 stream63"],
    ),
    (
        ("agent63 angle63 universe63 memory63 stream63 context63", 6),
        ["agent63", "angle63", "universe63", "memory63", "stream63", "context63"],
    ),
    (
        ("agent63 angle63 universe63 memory63 stream63 context63", 10),
        ["agent63", "angle63", "universe63", "memory63", "stream63", "context63"],
    ),
    (
        ("agent63 angle63 universe63 memory63 stream63 context63", 18),
        ["agent63 angle63", "universe63", "memory63 stream63", "context63"],
    ),
    (
        ("agent63 angle63 universe63 memory63 stream63 context63", 28),
        ["agent63 angle63 universe63", "memory63 stream63 context63"],
    ),
    (
        ("angle63 universe63 memory63 stream63 context63 knowledge63", 6),
        ["angle63", "universe63", "memory63", "stream63", "context63", "knowledge63"],
    ),
    (
        ("angle63 universe63 memory63 stream63 context63 knowledge63", 10),
        ["angle63", "universe63", "memory63", "stream63", "context63", "knowledge63"],
    ),
    (
        ("angle63 universe63 memory63 stream63 context63 knowledge63", 18),
        ["angle63 universe63", "memory63 stream63", "context63", "knowledge63"],
    ),
    (
        ("angle63 universe63 memory63 stream63 context63 knowledge63", 28),
        ["angle63 universe63 memory63", "stream63 context63", "knowledge63"],
    ),
    (
        ("universe63 memory63 stream63 context63 knowledge63 vector63", 6),
        ["universe63", "memory63", "stream63", "context63", "knowledge63", "vector63"],
    ),
    (
        ("universe63 memory63 stream63 context63 knowledge63 vector63", 10),
        ["universe63", "memory63", "stream63", "context63", "knowledge63", "vector63"],
    ),
    (
        ("universe63 memory63 stream63 context63 knowledge63 vector63", 18),
        ["universe63", "memory63 stream63", "context63", "knowledge63", "vector63"],
    ),
    (
        ("universe63 memory63 stream63 context63 knowledge63 vector63", 28),
        ["universe63 memory63 stream63", "context63 knowledge63", "vector63"],
    ),
    (
        ("memory63 stream63 context63 knowledge63 vector63 processor63", 6),
        ["memory63", "stream63", "context63", "knowledge63", "vector63", "processor63"],
    ),
    (
        ("memory63 stream63 context63 knowledge63 vector63 processor63", 10),
        ["memory63", "stream63", "context63", "knowledge63", "vector63", "processor63"],
    ),
    (
        ("memory63 stream63 context63 knowledge63 vector63 processor63", 18),
        ["memory63 stream63", "context63", "knowledge63", "vector63", "processor63"],
    ),
    (
        ("memory63 stream63 context63 knowledge63 vector63 processor63", 28),
        ["memory63 stream63 context63", "knowledge63 vector63", "processor63"],
    ),
    (
        ("stream63 context63 knowledge63 vector63 processor63 reasoning63", 6),
        ["stream63", "context63", "knowledge63", "vector63", "processor63", "reasoning63"],
    ),
    (
        ("stream63 context63 knowledge63 vector63 processor63 reasoning63", 10),
        ["stream63", "context63", "knowledge63", "vector63", "processor63", "reasoning63"],
    ),
    (
        ("stream63 context63 knowledge63 vector63 processor63 reasoning63", 18),
        ["stream63 context63", "knowledge63", "vector63", "processor63", "reasoning63"],
    ),
    (
        ("stream63 context63 knowledge63 vector63 processor63 reasoning63", 28),
        ["stream63 context63", "knowledge63 vector63", "processor63 reasoning63"],
    ),
    (
        ("context63 knowledge63 vector63 processor63 reasoning63 machine63", 6),
        ["context63", "knowledge63", "vector63", "processor63", "reasoning63", "machine63"],
    ),
    (
        ("context63 knowledge63 vector63 processor63 reasoning63 machine63", 10),
        ["context63", "knowledge63", "vector63", "processor63", "reasoning63", "machine63"],
    ),
    (
        ("context63 knowledge63 vector63 processor63 reasoning63 machine63", 18),
        ["context63", "knowledge63", "vector63", "processor63", "reasoning63", "machine63"],
    ),
    (
        ("context63 knowledge63 vector63 processor63 reasoning63 machine63", 28),
        ["context63 knowledge63", "vector63 processor63", "reasoning63 machine63"],
    ),
    (
        ("knowledge63 vector63 processor63 reasoning63 machine63 learning63", 6),
        ["knowledge63", "vector63", "processor63", "reasoning63", "machine63", "learning63"],
    ),
    (
        ("knowledge63 vector63 processor63 reasoning63 machine63 learning63", 10),
        ["knowledge63", "vector63", "processor63", "reasoning63", "machine63", "learning63"],
    ),
    (
        ("knowledge63 vector63 processor63 reasoning63 machine63 learning63", 18),
        ["knowledge63", "vector63", "processor63", "reasoning63", "machine63", "learning63"],
    ),
    (
        ("knowledge63 vector63 processor63 reasoning63 machine63 learning63", 28),
        ["knowledge63 vector63", "processor63 reasoning63", "machine63 learning63"],
    ),
    (
        ("vector63 processor63 reasoning63 machine63 learning63 model63", 6),
        ["vector63", "processor63", "reasoning63", "machine63", "learning63", "model63"],
    ),
    (
        ("vector63 processor63 reasoning63 machine63 learning63 model63", 10),
        ["vector63", "processor63", "reasoning63", "machine63", "learning63", "model63"],
    ),
    (
        ("vector63 processor63 reasoning63 machine63 learning63 model63", 18),
        ["vector63", "processor63", "reasoning63", "machine63", "learning63 model63"],
    ),
    (
        ("vector63 processor63 reasoning63 machine63 learning63 model63", 28),
        ["vector63 processor63", "reasoning63 machine63", "learning63 model63"],
    ),
    (
        ("processor63 reasoning63 machine63 learning63 model63 token63", 6),
        ["processor63", "reasoning63", "machine63", "learning63", "model63", "token63"],
    ),
    (
        ("processor63 reasoning63 machine63 learning63 model63 token63", 10),
        ["processor63", "reasoning63", "machine63", "learning63", "model63", "token63"],
    ),
    (
        ("processor63 reasoning63 machine63 learning63 model63 token63", 18),
        ["processor63", "reasoning63", "machine63", "learning63 model63", "token63"],
    ),
    (
        ("processor63 reasoning63 machine63 learning63 model63 token63", 28),
        ["processor63 reasoning63", "machine63 learning63 model63", "token63"],
    ),
    (
        ("reasoning63 machine63 learning63 model63 token63 prompt63", 6),
        ["reasoning63", "machine63", "learning63", "model63", "token63", "prompt63"],
    ),
    (
        ("reasoning63 machine63 learning63 model63 token63 prompt63", 10),
        ["reasoning63", "machine63", "learning63", "model63", "token63", "prompt63"],
    ),
    (
        ("reasoning63 machine63 learning63 model63 token63 prompt63", 18),
        ["reasoning63", "machine63", "learning63 model63", "token63 prompt63"],
    ),
    (
        ("reasoning63 machine63 learning63 model63 token63 prompt63", 28),
        ["reasoning63 machine63", "learning63 model63 token63", "prompt63"],
    ),
    (
        ("machine63 learning63 model63 token63 prompt63 session63", 6),
        ["machine63", "learning63", "model63", "token63", "prompt63", "session63"],
    ),
    (
        ("machine63 learning63 model63 token63 prompt63 session63", 10),
        ["machine63", "learning63", "model63", "token63", "prompt63", "session63"],
    ),
    (
        ("machine63 learning63 model63 token63 prompt63 session63", 18),
        ["machine63", "learning63 model63", "token63 prompt63", "session63"],
    ),
    (
        ("machine63 learning63 model63 token63 prompt63 session63", 28),
        ["machine63 learning63 model63", "token63 prompt63 session63"],
    ),
    (
        ("learning63 model63 token63 prompt63 session63 library63", 6),
        ["learning63", "model63", "token63", "prompt63", "session63", "library63"],
    ),
    (
        ("learning63 model63 token63 prompt63 session63 library63", 10),
        ["learning63", "model63", "token63", "prompt63", "session63", "library63"],
    ),
    (
        ("learning63 model63 token63 prompt63 session63 library63", 18),
        ["learning63 model63", "token63 prompt63", "session63", "library63"],
    ),
    (
        ("learning63 model63 token63 prompt63 session63 library63", 28),
        ["learning63 model63 token63", "prompt63 session63 library63"],
    ),
    (
        ("model63 token63 prompt63 session63 library63 service63", 6),
        ["model63", "token63", "prompt63", "session63", "library63", "service63"],
    ),
    (
        ("model63 token63 prompt63 session63 library63 service63", 10),
        ["model63", "token63", "prompt63", "session63", "library63", "service63"],
    ),
    (
        ("model63 token63 prompt63 session63 library63 service63", 18),
        ["model63 token63", "prompt63 session63", "library63", "service63"],
    ),
    (
        ("model63 token63 prompt63 session63 library63 service63", 28),
        ["model63 token63 prompt63", "session63 library63", "service63"],
    ),
    (
        ("token63 prompt63 session63 library63 service63 gateway63", 6),
        ["token63", "prompt63", "session63", "library63", "service63", "gateway63"],
    ),
    (
        ("token63 prompt63 session63 library63 service63 gateway63", 10),
        ["token63", "prompt63", "session63", "library63", "service63", "gateway63"],
    ),
    (
        ("token63 prompt63 session63 library63 service63 gateway63", 18),
        ["token63 prompt63", "session63", "library63", "service63", "gateway63"],
    ),
    (
        ("token63 prompt63 session63 library63 service63 gateway63", 28),
        ["token63 prompt63 session63", "library63 service63", "gateway63"],
    ),
    (
        ("prompt63 session63 library63 service63 gateway63 storage63", 6),
        ["prompt63", "session63", "library63", "service63", "gateway63", "storage63"],
    ),
    (
        ("prompt63 session63 library63 service63 gateway63 storage63", 10),
        ["prompt63", "session63", "library63", "service63", "gateway63", "storage63"],
    ),
    (
        ("prompt63 session63 library63 service63 gateway63 storage63", 18),
        ["prompt63 session63", "library63", "service63", "gateway63", "storage63"],
    ),
    (
        ("prompt63 session63 library63 service63 gateway63 storage63", 28),
        ["prompt63 session63 library63", "service63 gateway63", "storage63"],
    ),
    (
        ("session63 library63 service63 gateway63 storage63 network63", 6),
        ["session63", "library63", "service63", "gateway63", "storage63", "network63"],
    ),
    (
        ("session63 library63 service63 gateway63 storage63 network63", 10),
        ["session63", "library63", "service63", "gateway63", "storage63", "network63"],
    ),
    (
        ("session63 library63 service63 gateway63 storage63 network63", 18),
        ["session63", "library63", "service63", "gateway63", "storage63", "network63"],
    ),
    (
        ("session63 library63 service63 gateway63 storage63 network63", 28),
        ["session63 library63", "service63 gateway63", "storage63 network63"],
    ),
    (
        ("library63 service63 gateway63 storage63 network63 latency63", 6),
        ["library63", "service63", "gateway63", "storage63", "network63", "latency63"],
    ),
    (
        ("library63 service63 gateway63 storage63 network63 latency63", 10),
        ["library63", "service63", "gateway63", "storage63", "network63", "latency63"],
    ),
    (
        ("library63 service63 gateway63 storage63 network63 latency63", 18),
        ["library63", "service63", "gateway63", "storage63", "network63", "latency63"],
    ),
    (
        ("library63 service63 gateway63 storage63 network63 latency63", 28),
        ["library63 service63", "gateway63 storage63", "network63 latency63"],
    ),
    (
        ("service63 gateway63 storage63 network63 latency63 buffer63", 6),
        ["service63", "gateway63", "storage63", "network63", "latency63", "buffer63"],
    ),
    (
        ("service63 gateway63 storage63 network63 latency63 buffer63", 10),
        ["service63", "gateway63", "storage63", "network63", "latency63", "buffer63"],
    ),
    (
        ("service63 gateway63 storage63 network63 latency63 buffer63", 18),
        ["service63", "gateway63", "storage63", "network63", "latency63 buffer63"],
    ),
    (
        ("service63 gateway63 storage63 network63 latency63 buffer63", 28),
        ["service63 gateway63", "storage63 network63", "latency63 buffer63"],
    ),
    (
        ("gateway63 storage63 network63 latency63 buffer63 queue63", 6),
        ["gateway63", "storage63", "network63", "latency63", "buffer63", "queue63"],
    ),
    (
        ("gateway63 storage63 network63 latency63 buffer63 queue63", 10),
        ["gateway63", "storage63", "network63", "latency63", "buffer63", "queue63"],
    ),
    (
        ("gateway63 storage63 network63 latency63 buffer63 queue63", 18),
        ["gateway63", "storage63", "network63", "latency63 buffer63", "queue63"],
    ),
    (
        ("gateway63 storage63 network63 latency63 buffer63 queue63", 28),
        ["gateway63 storage63", "network63 latency63 buffer63", "queue63"],
    ),
    (
        ("storage63 network63 latency63 buffer63 queue63 worker63", 6),
        ["storage63", "network63", "latency63", "buffer63", "queue63", "worker63"],
    ),
    (
        ("storage63 network63 latency63 buffer63 queue63 worker63", 10),
        ["storage63", "network63", "latency63", "buffer63", "queue63", "worker63"],
    ),
    (
        ("storage63 network63 latency63 buffer63 queue63 worker63", 18),
        ["storage63", "network63", "latency63 buffer63", "queue63 worker63"],
    ),
    (
        ("storage63 network63 latency63 buffer63 queue63 worker63", 28),
        ["storage63 network63", "latency63 buffer63 queue63", "worker63"],
    ),
    (
        ("network63 latency63 buffer63 queue63 worker63 kernel63", 6),
        ["network63", "latency63", "buffer63", "queue63", "worker63", "kernel63"],
    ),
    (
        ("network63 latency63 buffer63 queue63 worker63 kernel63", 10),
        ["network63", "latency63", "buffer63", "queue63", "worker63", "kernel63"],
    ),
    (
        ("network63 latency63 buffer63 queue63 worker63 kernel63", 18),
        ["network63", "latency63 buffer63", "queue63 worker63", "kernel63"],
    ),
    (
        ("network63 latency63 buffer63 queue63 worker63 kernel63", 28),
        ["network63 latency63 buffer63", "queue63 worker63 kernel63"],
    ),
    (
        ("latency63 buffer63 queue63 worker63 kernel63 signal63", 6),
        ["latency63", "buffer63", "queue63", "worker63", "kernel63", "signal63"],
    ),
    (
        ("latency63 buffer63 queue63 worker63 kernel63 signal63", 10),
        ["latency63", "buffer63", "queue63", "worker63", "kernel63", "signal63"],
    ),
    (
        ("latency63 buffer63 queue63 worker63 kernel63 signal63", 18),
        ["latency63 buffer63", "queue63 worker63", "kernel63 signal63"],
    ),
    (
        ("latency63 buffer63 queue63 worker63 kernel63 signal63", 28),
        ["latency63 buffer63 queue63", "worker63 kernel63 signal63"],
    ),
    (
        ("buffer63 queue63 worker63 kernel63 signal63 packet63", 6),
        ["buffer63", "queue63", "worker63", "kernel63", "signal63", "packet63"],
    ),
    (
        ("buffer63 queue63 worker63 kernel63 signal63 packet63", 10),
        ["buffer63", "queue63", "worker63", "kernel63", "signal63", "packet63"],
    ),
    (
        ("buffer63 queue63 worker63 kernel63 signal63 packet63", 18),
        ["buffer63 queue63", "worker63 kernel63", "signal63 packet63"],
    ),
    (
        ("buffer63 queue63 worker63 kernel63 signal63 packet63", 28),
        ["buffer63 queue63 worker63", "kernel63 signal63 packet63"],
    ),
    (
        ("queue63 worker63 kernel63 signal63 packet63 router63", 6),
        ["queue63", "worker63", "kernel63", "signal63", "packet63", "router63"],
    ),
    (
        ("queue63 worker63 kernel63 signal63 packet63 router63", 10),
        ["queue63", "worker63", "kernel63", "signal63", "packet63", "router63"],
    ),
    (
        ("queue63 worker63 kernel63 signal63 packet63 router63", 18),
        ["queue63 worker63", "kernel63 signal63", "packet63 router63"],
    ),
    (
        ("queue63 worker63 kernel63 signal63 packet63 router63", 28),
        ["queue63 worker63 kernel63", "signal63 packet63 router63"],
    ),
    (
        ("worker63 kernel63 signal63 packet63 router63 cluster63", 6),
        ["worker63", "kernel63", "signal63", "packet63", "router63", "cluster63"],
    ),
    (
        ("worker63 kernel63 signal63 packet63 router63 cluster63", 10),
        ["worker63", "kernel63", "signal63", "packet63", "router63", "cluster63"],
    ),
    (
        ("worker63 kernel63 signal63 packet63 router63 cluster63", 18),
        ["worker63 kernel63", "signal63 packet63", "router63 cluster63"],
    ),
    (
        ("worker63 kernel63 signal63 packet63 router63 cluster63", 28),
        ["worker63 kernel63 signal63", "packet63 router63 cluster63"],
    ),
    (
        ("kernel63 signal63 packet63 router63 cluster63 mirror63", 6),
        ["kernel63", "signal63", "packet63", "router63", "cluster63", "mirror63"],
    ),
    (
        ("kernel63 signal63 packet63 router63 cluster63 mirror63", 10),
        ["kernel63", "signal63", "packet63", "router63", "cluster63", "mirror63"],
    ),
    (
        ("kernel63 signal63 packet63 router63 cluster63 mirror63", 18),
        ["kernel63 signal63", "packet63 router63", "cluster63 mirror63"],
    ),
    (
        ("kernel63 signal63 packet63 router63 cluster63 mirror63", 28),
        ["kernel63 signal63 packet63", "router63 cluster63 mirror63"],
    ),
    (
        ("signal63 packet63 router63 cluster63 mirror63 filter63", 6),
        ["signal63", "packet63", "router63", "cluster63", "mirror63", "filter63"],
    ),
    (
        ("signal63 packet63 router63 cluster63 mirror63 filter63", 10),
        ["signal63", "packet63", "router63", "cluster63", "mirror63", "filter63"],
    ),
    (
        ("signal63 packet63 router63 cluster63 mirror63 filter63", 18),
        ["signal63 packet63", "router63 cluster63", "mirror63 filter63"],
    ),
    (
        ("signal63 packet63 router63 cluster63 mirror63 filter63", 28),
        ["signal63 packet63 router63", "cluster63 mirror63 filter63"],
    ),
    (
        ("packet63 router63 cluster63 mirror63 filter63 ranking63", 6),
        ["packet63", "router63", "cluster63", "mirror63", "filter63", "ranking63"],
    ),
    (
        ("packet63 router63 cluster63 mirror63 filter63 ranking63", 10),
        ["packet63", "router63", "cluster63", "mirror63", "filter63", "ranking63"],
    ),
    (
        ("packet63 router63 cluster63 mirror63 filter63 ranking63", 18),
        ["packet63 router63", "cluster63 mirror63", "filter63 ranking63"],
    ),
    (
        ("packet63 router63 cluster63 mirror63 filter63 ranking63", 28),
        ["packet63 router63 cluster63", "mirror63 filter63 ranking63"],
    ),
    (
        ("router63 cluster63 mirror63 filter63 ranking63 encoding63", 6),
        ["router63", "cluster63", "mirror63", "filter63", "ranking63", "encoding63"],
    ),
    (
        ("router63 cluster63 mirror63 filter63 ranking63 encoding63", 10),
        ["router63", "cluster63", "mirror63", "filter63", "ranking63", "encoding63"],
    ),
    (
        ("router63 cluster63 mirror63 filter63 ranking63 encoding63", 18),
        ["router63 cluster63", "mirror63 filter63", "ranking63", "encoding63"],
    ),
    (
        ("router63 cluster63 mirror63 filter63 ranking63 encoding63", 28),
        ["router63 cluster63 mirror63", "filter63 ranking63", "encoding63"],
    ),
    (
        ("cluster63 mirror63 filter63 ranking63 encoding63 mapping63", 6),
        ["cluster63", "mirror63", "filter63", "ranking63", "encoding63", "mapping63"],
    ),
    (
        ("cluster63 mirror63 filter63 ranking63 encoding63 mapping63", 10),
        ["cluster63", "mirror63", "filter63", "ranking63", "encoding63", "mapping63"],
    ),
    (
        ("cluster63 mirror63 filter63 ranking63 encoding63 mapping63", 18),
        ["cluster63 mirror63", "filter63 ranking63", "encoding63", "mapping63"],
    ),
    (
        ("cluster63 mirror63 filter63 ranking63 encoding63 mapping63", 28),
        ["cluster63 mirror63 filter63", "ranking63 encoding63", "mapping63"],
    ),
    (
        ("mirror63 filter63 ranking63 encoding63 mapping63 record63", 6),
        ["mirror63", "filter63", "ranking63", "encoding63", "mapping63", "record63"],
    ),
    (
        ("mirror63 filter63 ranking63 encoding63 mapping63 record63", 10),
        ["mirror63", "filter63", "ranking63", "encoding63", "mapping63", "record63"],
    ),
    (
        ("mirror63 filter63 ranking63 encoding63 mapping63 record63", 18),
        ["mirror63 filter63", "ranking63", "encoding63", "mapping63 record63"],
    ),
    (
        ("mirror63 filter63 ranking63 encoding63 mapping63 record63", 28),
        ["mirror63 filter63 ranking63", "encoding63 mapping63", "record63"],
    ),
    (
        ("filter63 ranking63 encoding63 mapping63 record63 candle63", 6),
        ["filter63", "ranking63", "encoding63", "mapping63", "record63", "candle63"],
    ),
    (
        ("filter63 ranking63 encoding63 mapping63 record63 candle63", 10),
        ["filter63", "ranking63", "encoding63", "mapping63", "record63", "candle63"],
    ),
    (
        ("filter63 ranking63 encoding63 mapping63 record63 candle63", 18),
        ["filter63 ranking63", "encoding63", "mapping63 record63", "candle63"],
    ),
    (
        ("filter63 ranking63 encoding63 mapping63 record63 candle63", 28),
        ["filter63 ranking63", "encoding63 mapping63", "record63 candle63"],
    ),
    (
        ("ranking63 encoding63 mapping63 record63 candle63 thread63", 6),
        ["ranking63", "encoding63", "mapping63", "record63", "candle63", "thread63"],
    ),
    (
        ("ranking63 encoding63 mapping63 record63 candle63 thread63", 10),
        ["ranking63", "encoding63", "mapping63", "record63", "candle63", "thread63"],
    ),
    (
        ("ranking63 encoding63 mapping63 record63 candle63 thread63", 18),
        ["ranking63", "encoding63", "mapping63 record63", "candle63 thread63"],
    ),
    (
        ("ranking63 encoding63 mapping63 record63 candle63 thread63", 28),
        ["ranking63 encoding63", "mapping63 record63 candle63", "thread63"],
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
