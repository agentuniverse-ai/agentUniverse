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
        ("round 24: the quick brown fox jumps over the lazy dog", 4),
        ["round", "24:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 24: the quick brown fox jumps over the lazy dog", 8),
        ["round", "24: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 24: the quick brown fox jumps over the lazy dog", 12),
        ["round 24:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 24: the quick brown fox jumps over the lazy dog", 16),
        ["round 24: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 24: the quick brown fox jumps over the lazy dog", 24),
        ["round 24: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 24: the quick brown fox jumps over the lazy dog", 32),
        ["round 24: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 24: agentuniverse is a framework for multi agents", 4),
        ["round", "24:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 24: agentuniverse is a framework for multi agents", 8),
        ["round", "24:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 24: agentuniverse is a framework for multi agents", 12),
        ["round 24:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 24: agentuniverse is a framework for multi agents", 16),
        ["round 24:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 24: agentuniverse is a framework for multi agents", 24),
        ["round 24: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 24: agentuniverse is a framework for multi agents", 32),
        ["round 24: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 24: knowledge stored as vectors enables retrieval", 4),
        ["round", "24:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 24: knowledge stored as vectors enables retrieval", 8),
        ["round", "24:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 24: knowledge stored as vectors enables retrieval", 12),
        ["round 24:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 24: knowledge stored as vectors enables retrieval", 16),
        ["round 24:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 24: knowledge stored as vectors enables retrieval", 24),
        ["round 24: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 24: knowledge stored as vectors enables retrieval", 32),
        ["round 24: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 24: the processor reads the record then stops", 4),
        ["round", "24:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 24: the processor reads the record then stops", 8),
        ["round", "24: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 24: the processor reads the record then stops", 12),
        ["round 24:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 24: the processor reads the record then stops", 16),
        ["round 24: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 24: the processor reads the record then stops", 24),
        ["round 24: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 24: the processor reads the record then stops", 32),
        ["round 24: the processor reads", "the record then stops"],
    ),
    (
        ("round 24: a worker pulls the next task from the queue", 4),
        ["round", "24:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 24: a worker pulls the next task from the queue", 8),
        ["round", "24: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 24: a worker pulls the next task from the queue", 12),
        ["round 24: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 24: a worker pulls the next task from the queue", 16),
        ["round 24: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 24: a worker pulls the next task from the queue", 24),
        ["round 24: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 24: a worker pulls the next task from the queue", 32),
        ["round 24: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 24: signals travel through the network layer", 4),
        ["round", "24:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 24: signals travel through the network layer", 8),
        ["round", "24:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 24: signals travel through the network layer", 12),
        ["round 24:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 24: signals travel through the network layer", 16),
        ["round 24:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 24: signals travel through the network layer", 24),
        ["round 24: signals travel", "through the network", "layer"],
    ),
    (
        ("round 24: signals travel through the network layer", 32),
        ["round 24: signals travel through", "the network layer"],
    ),
    (
        ("round 24: the gateway routes each request by policy", 4),
        ["round", "24:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 24: the gateway routes each request by policy", 8),
        ["round", "24: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 24: the gateway routes each request by policy", 12),
        ["round 24:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 24: the gateway routes each request by policy", 16),
        ["round 24: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 24: the gateway routes each request by policy", 24),
        ["round 24: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 24: the gateway routes each request by policy", 32),
        ["round 24: the gateway routes", "each request by policy"],
    ),
    (
        ("round 24: memory grows until the buffer is full", 4),
        ["round", "24:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 24: memory grows until the buffer is full", 8),
        ["round", "24:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 24: memory grows until the buffer is full", 12),
        ["round 24:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 24: memory grows until the buffer is full", 16),
        ["round 24: memory", "grows until the", "buffer is full"],
    ),
    (("round 24: memory grows until the buffer is full", 24), ["round 24: memory grows", "until the buffer is full"]),
    (("round 24: memory grows until the buffer is full", 32), ["round 24: memory grows until the", "buffer is full"]),
    (
        ("round 24: the cluster mirrors every packet twice", 4),
        ["round", "24:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 24: the cluster mirrors every packet twice", 8),
        ["round", "24: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 24: the cluster mirrors every packet twice", 12),
        ["round 24:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 24: the cluster mirrors every packet twice", 16),
        ["round 24: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 24: the cluster mirrors every packet twice", 24),
        ["round 24: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 24: the cluster mirrors every packet twice", 32), ["round 24: the cluster mirrors", "every packet twice"]),
    (
        ("round 24: ranking uses tokens learned from the corpus", 4),
        ["round", "24:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 24: ranking uses tokens learned from the corpus", 8),
        ["round", "24:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 24: ranking uses tokens learned from the corpus", 12),
        ["round 24:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 24: ranking uses tokens learned from the corpus", 16),
        ["round 24:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 24: ranking uses tokens learned from the corpus", 24),
        ["round 24: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 24: ranking uses tokens learned from the corpus", 32),
        ["round 24: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 24: a long session ends when the candle dies", 4),
        ["round", "24:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 24: a long session ends when the candle dies", 8),
        ["round", "24: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 24: a long session ends when the candle dies", 12),
        ["round 24: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 24: a long session ends when the candle dies", 16),
        ["round 24: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 24: a long session ends when the candle dies", 24),
        ["round 24: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 24: a long session ends when the candle dies", 32),
        ["round 24: a long session ends", "when the candle dies"],
    ),
    (
        ("round 24: encode the prompt then map the result", 4),
        ["round", "24:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 24: encode the prompt then map the result", 8),
        ["round", "24:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 24: encode the prompt then map the result", 12),
        ["round 24:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 24: encode the prompt then map the result", 16),
        ["round 24: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 24: encode the prompt then map the result", 24),
        ["round 24: encode the", "prompt then map the", "result"],
    ),
    (("round 24: encode the prompt then map the result", 32), ["round 24: encode the prompt then", "map the result"]),
    (
        ("round 24: the kernel wakes the worker at dawn", 4),
        ["round", "24:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 24: the kernel wakes the worker at dawn", 8),
        ["round", "24: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 24: the kernel wakes the worker at dawn", 12),
        ["round 24:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 24: the kernel wakes the worker at dawn", 16), ["round 24: the", "kernel wakes the", "worker at dawn"]),
    (("round 24: the kernel wakes the worker at dawn", 24), ["round 24: the kernel", "wakes the worker at dawn"]),
    (("round 24: the kernel wakes the worker at dawn", 32), ["round 24: the kernel wakes the", "worker at dawn"]),
    (
        ("round 24: service latency drops after the patch", 4),
        ["round", "24:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 24: service latency drops after the patch", 8),
        ["round", "24:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 24: service latency drops after the patch", 12),
        ["round 24:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 24: service latency drops after the patch", 16),
        ["round 24:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 24: service latency drops after the patch", 24),
        ["round 24: service", "latency drops after the", "patch"],
    ),
    (("round 24: service latency drops after the patch", 32), ["round 24: service latency drops", "after the patch"]),
    (
        ("round 24: the library caches every vector it sees", 4),
        ["round", "24:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 24: the library caches every vector it sees", 8),
        ["round", "24: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 24: the library caches every vector it sees", 12),
        ["round 24:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 24: the library caches every vector it sees", 16),
        ["round 24: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 24: the library caches every vector it sees", 24),
        ["round 24: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 24: the library caches every vector it sees", 32),
        ["round 24: the library caches", "every vector it sees"],
    ),
    (
        ("round 24: agents argue then the debate resolves", 4),
        ["round", "24:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 24: agents argue then the debate resolves", 8),
        ["round", "24:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 24: agents argue then the debate resolves", 12),
        ["round 24:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 24: agents argue then the debate resolves", 16),
        ["round 24: agents", "argue then the", "debate resolves"],
    ),
    (("round 24: agents argue then the debate resolves", 24), ["round 24: agents argue", "then the debate resolves"]),
    (("round 24: agents argue then the debate resolves", 32), ["round 24: agents argue then the", "debate resolves"]),
    (
        ("round 24: the filter keeps only strong matches", 4),
        ["round", "24:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 24: the filter keeps only strong matches", 8),
        ["round", "24: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 24: the filter keeps only strong matches", 12),
        ["round 24:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 24: the filter keeps only strong matches", 16),
        ["round 24: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 24: the filter keeps only strong matches", 24), ["round 24: the filter", "keeps only strong", "matches"]),
    (("round 24: the filter keeps only strong matches", 32), ["round 24: the filter keeps only", "strong matches"]),
    (
        ("round 24: the model answers with a short reply", 4),
        ["round", "24:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 24: the model answers with a short reply", 8),
        ["round", "24: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 24: the model answers with a short reply", 12),
        ["round 24:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 24: the model answers with a short reply", 16),
        ["round 24: the", "model answers", "with a short", "reply"],
    ),
    (("round 24: the model answers with a short reply", 24), ["round 24: the model", "answers with a short", "reply"]),
    (("round 24: the model answers with a short reply", 32), ["round 24: the model answers with", "a short reply"]),
    (
        ("round 24: the recorder stores the reasoning trace", 4),
        ["round", "24:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 24: the recorder stores the reasoning trace", 8),
        ["round", "24: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 24: the recorder stores the reasoning trace", 12),
        ["round 24:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 24: the recorder stores the reasoning trace", 16),
        ["round 24: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 24: the recorder stores the reasoning trace", 24),
        ["round 24: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 24: the recorder stores the reasoning trace", 32),
        ["round 24: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 24: the angel watches the processor run", 4),
        ["round", "24:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 24: the angel watches the processor run", 8),
        ["round", "24: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 24: the angel watches the processor run", 12),
        ["round 24:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 24: the angel watches the processor run", 16), ["round 24: the", "angel watches", "the processor", "run"]),
    (("round 24: the angel watches the processor run", 24), ["round 24: the angel", "watches the processor", "run"]),
    (("round 24: the angel watches the processor run", 32), ["round 24: the angel watches the", "processor run"]),
    (
        ("round 24: angle of the vector decides the match", 4),
        ["round", "24:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 24: angle of the vector decides the match", 8),
        ["round", "24:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 24: angle of the vector decides the match", 12),
        ["round 24:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 24: angle of the vector decides the match", 16),
        ["round 24: angle", "of the vector", "decides the", "match"],
    ),
    (("round 24: angle of the vector decides the match", 24), ["round 24: angle of the", "vector decides the match"]),
    (("round 24: angle of the vector decides the match", 32), ["round 24: angle of the vector", "decides the match"]),
    (
        ("round 24: the candle burns twice as long at night", 4),
        ["round", "24:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 24: the candle burns twice as long at night", 8),
        ["round", "24: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 24: the candle burns twice as long at night", 12),
        ["round 24:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 24: the candle burns twice as long at night", 16),
        ["round 24: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 24: the candle burns twice as long at night", 24),
        ["round 24: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 24: the candle burns twice as long at night", 32),
        ["round 24: the candle burns twice", "as long at night"],
    ),
    (
        ("round 24: a mirror of the universe in one line", 4),
        ["round", "24:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 24: a mirror of the universe in one line", 8),
        ["round", "24: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 24: a mirror of the universe in one line", 12),
        ["round 24: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 24: a mirror of the universe in one line", 16),
        ["round 24: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 24: a mirror of the universe in one line", 24), ["round 24: a mirror of", "the universe in one line"]),
    (("round 24: a mirror of the universe in one line", 32), ["round 24: a mirror of the", "universe in one line"]),
    (
        ("round 24: the queue drains before the storm", 4),
        ["round", "24:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 24: the queue drains before the storm", 8),
        ["round", "24: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 24: the queue drains before the storm", 12), ["round 24:", "the queue", "drains", "before the", "storm"]),
    (("round 24: the queue drains before the storm", 16), ["round 24: the", "queue drains", "before the storm"]),
    (("round 24: the queue drains before the storm", 24), ["round 24: the queue", "drains before the storm"]),
    (("round 24: the queue drains before the storm", 32), ["round 24: the queue drains", "before the storm"]),
    (
        ("kitten24 sitting24 agent24 angle24 universe24 memory24", 6),
        ["kitten24", "sitting24", "agent24", "angle24", "universe24", "memory24"],
    ),
    (
        ("kitten24 sitting24 agent24 angle24 universe24 memory24", 10),
        ["kitten24", "sitting24", "agent24", "angle24", "universe24", "memory24"],
    ),
    (
        ("kitten24 sitting24 agent24 angle24 universe24 memory24", 18),
        ["kitten24 sitting24", "agent24 angle24", "universe24", "memory24"],
    ),
    (
        ("kitten24 sitting24 agent24 angle24 universe24 memory24", 28),
        ["kitten24 sitting24 agent24", "angle24 universe24 memory24"],
    ),
    (
        ("sitting24 agent24 angle24 universe24 memory24 stream24", 6),
        ["sitting24", "agent24", "angle24", "universe24", "memory24", "stream24"],
    ),
    (
        ("sitting24 agent24 angle24 universe24 memory24 stream24", 10),
        ["sitting24", "agent24", "angle24", "universe24", "memory24", "stream24"],
    ),
    (
        ("sitting24 agent24 angle24 universe24 memory24 stream24", 18),
        ["sitting24 agent24", "angle24 universe24", "memory24 stream24"],
    ),
    (
        ("sitting24 agent24 angle24 universe24 memory24 stream24", 28),
        ["sitting24 agent24 angle24", "universe24 memory24 stream24"],
    ),
    (
        ("agent24 angle24 universe24 memory24 stream24 context24", 6),
        ["agent24", "angle24", "universe24", "memory24", "stream24", "context24"],
    ),
    (
        ("agent24 angle24 universe24 memory24 stream24 context24", 10),
        ["agent24", "angle24", "universe24", "memory24", "stream24", "context24"],
    ),
    (
        ("agent24 angle24 universe24 memory24 stream24 context24", 18),
        ["agent24 angle24", "universe24", "memory24 stream24", "context24"],
    ),
    (
        ("agent24 angle24 universe24 memory24 stream24 context24", 28),
        ["agent24 angle24 universe24", "memory24 stream24 context24"],
    ),
    (
        ("angle24 universe24 memory24 stream24 context24 knowledge24", 6),
        ["angle24", "universe24", "memory24", "stream24", "context24", "knowledge24"],
    ),
    (
        ("angle24 universe24 memory24 stream24 context24 knowledge24", 10),
        ["angle24", "universe24", "memory24", "stream24", "context24", "knowledge24"],
    ),
    (
        ("angle24 universe24 memory24 stream24 context24 knowledge24", 18),
        ["angle24 universe24", "memory24 stream24", "context24", "knowledge24"],
    ),
    (
        ("angle24 universe24 memory24 stream24 context24 knowledge24", 28),
        ["angle24 universe24 memory24", "stream24 context24", "knowledge24"],
    ),
    (
        ("universe24 memory24 stream24 context24 knowledge24 vector24", 6),
        ["universe24", "memory24", "stream24", "context24", "knowledge24", "vector24"],
    ),
    (
        ("universe24 memory24 stream24 context24 knowledge24 vector24", 10),
        ["universe24", "memory24", "stream24", "context24", "knowledge24", "vector24"],
    ),
    (
        ("universe24 memory24 stream24 context24 knowledge24 vector24", 18),
        ["universe24", "memory24 stream24", "context24", "knowledge24", "vector24"],
    ),
    (
        ("universe24 memory24 stream24 context24 knowledge24 vector24", 28),
        ["universe24 memory24 stream24", "context24 knowledge24", "vector24"],
    ),
    (
        ("memory24 stream24 context24 knowledge24 vector24 processor24", 6),
        ["memory24", "stream24", "context24", "knowledge24", "vector24", "processor24"],
    ),
    (
        ("memory24 stream24 context24 knowledge24 vector24 processor24", 10),
        ["memory24", "stream24", "context24", "knowledge24", "vector24", "processor24"],
    ),
    (
        ("memory24 stream24 context24 knowledge24 vector24 processor24", 18),
        ["memory24 stream24", "context24", "knowledge24", "vector24", "processor24"],
    ),
    (
        ("memory24 stream24 context24 knowledge24 vector24 processor24", 28),
        ["memory24 stream24 context24", "knowledge24 vector24", "processor24"],
    ),
    (
        ("stream24 context24 knowledge24 vector24 processor24 reasoning24", 6),
        ["stream24", "context24", "knowledge24", "vector24", "processor24", "reasoning24"],
    ),
    (
        ("stream24 context24 knowledge24 vector24 processor24 reasoning24", 10),
        ["stream24", "context24", "knowledge24", "vector24", "processor24", "reasoning24"],
    ),
    (
        ("stream24 context24 knowledge24 vector24 processor24 reasoning24", 18),
        ["stream24 context24", "knowledge24", "vector24", "processor24", "reasoning24"],
    ),
    (
        ("stream24 context24 knowledge24 vector24 processor24 reasoning24", 28),
        ["stream24 context24", "knowledge24 vector24", "processor24 reasoning24"],
    ),
    (
        ("context24 knowledge24 vector24 processor24 reasoning24 machine24", 6),
        ["context24", "knowledge24", "vector24", "processor24", "reasoning24", "machine24"],
    ),
    (
        ("context24 knowledge24 vector24 processor24 reasoning24 machine24", 10),
        ["context24", "knowledge24", "vector24", "processor24", "reasoning24", "machine24"],
    ),
    (
        ("context24 knowledge24 vector24 processor24 reasoning24 machine24", 18),
        ["context24", "knowledge24", "vector24", "processor24", "reasoning24", "machine24"],
    ),
    (
        ("context24 knowledge24 vector24 processor24 reasoning24 machine24", 28),
        ["context24 knowledge24", "vector24 processor24", "reasoning24 machine24"],
    ),
    (
        ("knowledge24 vector24 processor24 reasoning24 machine24 learning24", 6),
        ["knowledge24", "vector24", "processor24", "reasoning24", "machine24", "learning24"],
    ),
    (
        ("knowledge24 vector24 processor24 reasoning24 machine24 learning24", 10),
        ["knowledge24", "vector24", "processor24", "reasoning24", "machine24", "learning24"],
    ),
    (
        ("knowledge24 vector24 processor24 reasoning24 machine24 learning24", 18),
        ["knowledge24", "vector24", "processor24", "reasoning24", "machine24", "learning24"],
    ),
    (
        ("knowledge24 vector24 processor24 reasoning24 machine24 learning24", 28),
        ["knowledge24 vector24", "processor24 reasoning24", "machine24 learning24"],
    ),
    (
        ("vector24 processor24 reasoning24 machine24 learning24 model24", 6),
        ["vector24", "processor24", "reasoning24", "machine24", "learning24", "model24"],
    ),
    (
        ("vector24 processor24 reasoning24 machine24 learning24 model24", 10),
        ["vector24", "processor24", "reasoning24", "machine24", "learning24", "model24"],
    ),
    (
        ("vector24 processor24 reasoning24 machine24 learning24 model24", 18),
        ["vector24", "processor24", "reasoning24", "machine24", "learning24 model24"],
    ),
    (
        ("vector24 processor24 reasoning24 machine24 learning24 model24", 28),
        ["vector24 processor24", "reasoning24 machine24", "learning24 model24"],
    ),
    (
        ("processor24 reasoning24 machine24 learning24 model24 token24", 6),
        ["processor24", "reasoning24", "machine24", "learning24", "model24", "token24"],
    ),
    (
        ("processor24 reasoning24 machine24 learning24 model24 token24", 10),
        ["processor24", "reasoning24", "machine24", "learning24", "model24", "token24"],
    ),
    (
        ("processor24 reasoning24 machine24 learning24 model24 token24", 18),
        ["processor24", "reasoning24", "machine24", "learning24 model24", "token24"],
    ),
    (
        ("processor24 reasoning24 machine24 learning24 model24 token24", 28),
        ["processor24 reasoning24", "machine24 learning24 model24", "token24"],
    ),
    (
        ("reasoning24 machine24 learning24 model24 token24 prompt24", 6),
        ["reasoning24", "machine24", "learning24", "model24", "token24", "prompt24"],
    ),
    (
        ("reasoning24 machine24 learning24 model24 token24 prompt24", 10),
        ["reasoning24", "machine24", "learning24", "model24", "token24", "prompt24"],
    ),
    (
        ("reasoning24 machine24 learning24 model24 token24 prompt24", 18),
        ["reasoning24", "machine24", "learning24 model24", "token24 prompt24"],
    ),
    (
        ("reasoning24 machine24 learning24 model24 token24 prompt24", 28),
        ["reasoning24 machine24", "learning24 model24 token24", "prompt24"],
    ),
    (
        ("machine24 learning24 model24 token24 prompt24 session24", 6),
        ["machine24", "learning24", "model24", "token24", "prompt24", "session24"],
    ),
    (
        ("machine24 learning24 model24 token24 prompt24 session24", 10),
        ["machine24", "learning24", "model24", "token24", "prompt24", "session24"],
    ),
    (
        ("machine24 learning24 model24 token24 prompt24 session24", 18),
        ["machine24", "learning24 model24", "token24 prompt24", "session24"],
    ),
    (
        ("machine24 learning24 model24 token24 prompt24 session24", 28),
        ["machine24 learning24 model24", "token24 prompt24 session24"],
    ),
    (
        ("learning24 model24 token24 prompt24 session24 library24", 6),
        ["learning24", "model24", "token24", "prompt24", "session24", "library24"],
    ),
    (
        ("learning24 model24 token24 prompt24 session24 library24", 10),
        ["learning24", "model24", "token24", "prompt24", "session24", "library24"],
    ),
    (
        ("learning24 model24 token24 prompt24 session24 library24", 18),
        ["learning24 model24", "token24 prompt24", "session24", "library24"],
    ),
    (
        ("learning24 model24 token24 prompt24 session24 library24", 28),
        ["learning24 model24 token24", "prompt24 session24 library24"],
    ),
    (
        ("model24 token24 prompt24 session24 library24 service24", 6),
        ["model24", "token24", "prompt24", "session24", "library24", "service24"],
    ),
    (
        ("model24 token24 prompt24 session24 library24 service24", 10),
        ["model24", "token24", "prompt24", "session24", "library24", "service24"],
    ),
    (
        ("model24 token24 prompt24 session24 library24 service24", 18),
        ["model24 token24", "prompt24 session24", "library24", "service24"],
    ),
    (
        ("model24 token24 prompt24 session24 library24 service24", 28),
        ["model24 token24 prompt24", "session24 library24", "service24"],
    ),
    (
        ("token24 prompt24 session24 library24 service24 gateway24", 6),
        ["token24", "prompt24", "session24", "library24", "service24", "gateway24"],
    ),
    (
        ("token24 prompt24 session24 library24 service24 gateway24", 10),
        ["token24", "prompt24", "session24", "library24", "service24", "gateway24"],
    ),
    (
        ("token24 prompt24 session24 library24 service24 gateway24", 18),
        ["token24 prompt24", "session24", "library24", "service24", "gateway24"],
    ),
    (
        ("token24 prompt24 session24 library24 service24 gateway24", 28),
        ["token24 prompt24 session24", "library24 service24", "gateway24"],
    ),
    (
        ("prompt24 session24 library24 service24 gateway24 storage24", 6),
        ["prompt24", "session24", "library24", "service24", "gateway24", "storage24"],
    ),
    (
        ("prompt24 session24 library24 service24 gateway24 storage24", 10),
        ["prompt24", "session24", "library24", "service24", "gateway24", "storage24"],
    ),
    (
        ("prompt24 session24 library24 service24 gateway24 storage24", 18),
        ["prompt24 session24", "library24", "service24", "gateway24", "storage24"],
    ),
    (
        ("prompt24 session24 library24 service24 gateway24 storage24", 28),
        ["prompt24 session24 library24", "service24 gateway24", "storage24"],
    ),
    (
        ("session24 library24 service24 gateway24 storage24 network24", 6),
        ["session24", "library24", "service24", "gateway24", "storage24", "network24"],
    ),
    (
        ("session24 library24 service24 gateway24 storage24 network24", 10),
        ["session24", "library24", "service24", "gateway24", "storage24", "network24"],
    ),
    (
        ("session24 library24 service24 gateway24 storage24 network24", 18),
        ["session24", "library24", "service24", "gateway24", "storage24", "network24"],
    ),
    (
        ("session24 library24 service24 gateway24 storage24 network24", 28),
        ["session24 library24", "service24 gateway24", "storage24 network24"],
    ),
    (
        ("library24 service24 gateway24 storage24 network24 latency24", 6),
        ["library24", "service24", "gateway24", "storage24", "network24", "latency24"],
    ),
    (
        ("library24 service24 gateway24 storage24 network24 latency24", 10),
        ["library24", "service24", "gateway24", "storage24", "network24", "latency24"],
    ),
    (
        ("library24 service24 gateway24 storage24 network24 latency24", 18),
        ["library24", "service24", "gateway24", "storage24", "network24", "latency24"],
    ),
    (
        ("library24 service24 gateway24 storage24 network24 latency24", 28),
        ["library24 service24", "gateway24 storage24", "network24 latency24"],
    ),
    (
        ("service24 gateway24 storage24 network24 latency24 buffer24", 6),
        ["service24", "gateway24", "storage24", "network24", "latency24", "buffer24"],
    ),
    (
        ("service24 gateway24 storage24 network24 latency24 buffer24", 10),
        ["service24", "gateway24", "storage24", "network24", "latency24", "buffer24"],
    ),
    (
        ("service24 gateway24 storage24 network24 latency24 buffer24", 18),
        ["service24", "gateway24", "storage24", "network24", "latency24 buffer24"],
    ),
    (
        ("service24 gateway24 storage24 network24 latency24 buffer24", 28),
        ["service24 gateway24", "storage24 network24", "latency24 buffer24"],
    ),
    (
        ("gateway24 storage24 network24 latency24 buffer24 queue24", 6),
        ["gateway24", "storage24", "network24", "latency24", "buffer24", "queue24"],
    ),
    (
        ("gateway24 storage24 network24 latency24 buffer24 queue24", 10),
        ["gateway24", "storage24", "network24", "latency24", "buffer24", "queue24"],
    ),
    (
        ("gateway24 storage24 network24 latency24 buffer24 queue24", 18),
        ["gateway24", "storage24", "network24", "latency24 buffer24", "queue24"],
    ),
    (
        ("gateway24 storage24 network24 latency24 buffer24 queue24", 28),
        ["gateway24 storage24", "network24 latency24 buffer24", "queue24"],
    ),
    (
        ("storage24 network24 latency24 buffer24 queue24 worker24", 6),
        ["storage24", "network24", "latency24", "buffer24", "queue24", "worker24"],
    ),
    (
        ("storage24 network24 latency24 buffer24 queue24 worker24", 10),
        ["storage24", "network24", "latency24", "buffer24", "queue24", "worker24"],
    ),
    (
        ("storage24 network24 latency24 buffer24 queue24 worker24", 18),
        ["storage24", "network24", "latency24 buffer24", "queue24 worker24"],
    ),
    (
        ("storage24 network24 latency24 buffer24 queue24 worker24", 28),
        ["storage24 network24", "latency24 buffer24 queue24", "worker24"],
    ),
    (
        ("network24 latency24 buffer24 queue24 worker24 kernel24", 6),
        ["network24", "latency24", "buffer24", "queue24", "worker24", "kernel24"],
    ),
    (
        ("network24 latency24 buffer24 queue24 worker24 kernel24", 10),
        ["network24", "latency24", "buffer24", "queue24", "worker24", "kernel24"],
    ),
    (
        ("network24 latency24 buffer24 queue24 worker24 kernel24", 18),
        ["network24", "latency24 buffer24", "queue24 worker24", "kernel24"],
    ),
    (
        ("network24 latency24 buffer24 queue24 worker24 kernel24", 28),
        ["network24 latency24 buffer24", "queue24 worker24 kernel24"],
    ),
    (
        ("latency24 buffer24 queue24 worker24 kernel24 signal24", 6),
        ["latency24", "buffer24", "queue24", "worker24", "kernel24", "signal24"],
    ),
    (
        ("latency24 buffer24 queue24 worker24 kernel24 signal24", 10),
        ["latency24", "buffer24", "queue24", "worker24", "kernel24", "signal24"],
    ),
    (
        ("latency24 buffer24 queue24 worker24 kernel24 signal24", 18),
        ["latency24 buffer24", "queue24 worker24", "kernel24 signal24"],
    ),
    (
        ("latency24 buffer24 queue24 worker24 kernel24 signal24", 28),
        ["latency24 buffer24 queue24", "worker24 kernel24 signal24"],
    ),
    (
        ("buffer24 queue24 worker24 kernel24 signal24 packet24", 6),
        ["buffer24", "queue24", "worker24", "kernel24", "signal24", "packet24"],
    ),
    (
        ("buffer24 queue24 worker24 kernel24 signal24 packet24", 10),
        ["buffer24", "queue24", "worker24", "kernel24", "signal24", "packet24"],
    ),
    (
        ("buffer24 queue24 worker24 kernel24 signal24 packet24", 18),
        ["buffer24 queue24", "worker24 kernel24", "signal24 packet24"],
    ),
    (
        ("buffer24 queue24 worker24 kernel24 signal24 packet24", 28),
        ["buffer24 queue24 worker24", "kernel24 signal24 packet24"],
    ),
    (
        ("queue24 worker24 kernel24 signal24 packet24 router24", 6),
        ["queue24", "worker24", "kernel24", "signal24", "packet24", "router24"],
    ),
    (
        ("queue24 worker24 kernel24 signal24 packet24 router24", 10),
        ["queue24", "worker24", "kernel24", "signal24", "packet24", "router24"],
    ),
    (
        ("queue24 worker24 kernel24 signal24 packet24 router24", 18),
        ["queue24 worker24", "kernel24 signal24", "packet24 router24"],
    ),
    (
        ("queue24 worker24 kernel24 signal24 packet24 router24", 28),
        ["queue24 worker24 kernel24", "signal24 packet24 router24"],
    ),
    (
        ("worker24 kernel24 signal24 packet24 router24 cluster24", 6),
        ["worker24", "kernel24", "signal24", "packet24", "router24", "cluster24"],
    ),
    (
        ("worker24 kernel24 signal24 packet24 router24 cluster24", 10),
        ["worker24", "kernel24", "signal24", "packet24", "router24", "cluster24"],
    ),
    (
        ("worker24 kernel24 signal24 packet24 router24 cluster24", 18),
        ["worker24 kernel24", "signal24 packet24", "router24 cluster24"],
    ),
    (
        ("worker24 kernel24 signal24 packet24 router24 cluster24", 28),
        ["worker24 kernel24 signal24", "packet24 router24 cluster24"],
    ),
    (
        ("kernel24 signal24 packet24 router24 cluster24 mirror24", 6),
        ["kernel24", "signal24", "packet24", "router24", "cluster24", "mirror24"],
    ),
    (
        ("kernel24 signal24 packet24 router24 cluster24 mirror24", 10),
        ["kernel24", "signal24", "packet24", "router24", "cluster24", "mirror24"],
    ),
    (
        ("kernel24 signal24 packet24 router24 cluster24 mirror24", 18),
        ["kernel24 signal24", "packet24 router24", "cluster24 mirror24"],
    ),
    (
        ("kernel24 signal24 packet24 router24 cluster24 mirror24", 28),
        ["kernel24 signal24 packet24", "router24 cluster24 mirror24"],
    ),
    (
        ("signal24 packet24 router24 cluster24 mirror24 filter24", 6),
        ["signal24", "packet24", "router24", "cluster24", "mirror24", "filter24"],
    ),
    (
        ("signal24 packet24 router24 cluster24 mirror24 filter24", 10),
        ["signal24", "packet24", "router24", "cluster24", "mirror24", "filter24"],
    ),
    (
        ("signal24 packet24 router24 cluster24 mirror24 filter24", 18),
        ["signal24 packet24", "router24 cluster24", "mirror24 filter24"],
    ),
    (
        ("signal24 packet24 router24 cluster24 mirror24 filter24", 28),
        ["signal24 packet24 router24", "cluster24 mirror24 filter24"],
    ),
    (
        ("packet24 router24 cluster24 mirror24 filter24 ranking24", 6),
        ["packet24", "router24", "cluster24", "mirror24", "filter24", "ranking24"],
    ),
    (
        ("packet24 router24 cluster24 mirror24 filter24 ranking24", 10),
        ["packet24", "router24", "cluster24", "mirror24", "filter24", "ranking24"],
    ),
    (
        ("packet24 router24 cluster24 mirror24 filter24 ranking24", 18),
        ["packet24 router24", "cluster24 mirror24", "filter24 ranking24"],
    ),
    (
        ("packet24 router24 cluster24 mirror24 filter24 ranking24", 28),
        ["packet24 router24 cluster24", "mirror24 filter24 ranking24"],
    ),
    (
        ("router24 cluster24 mirror24 filter24 ranking24 encoding24", 6),
        ["router24", "cluster24", "mirror24", "filter24", "ranking24", "encoding24"],
    ),
    (
        ("router24 cluster24 mirror24 filter24 ranking24 encoding24", 10),
        ["router24", "cluster24", "mirror24", "filter24", "ranking24", "encoding24"],
    ),
    (
        ("router24 cluster24 mirror24 filter24 ranking24 encoding24", 18),
        ["router24 cluster24", "mirror24 filter24", "ranking24", "encoding24"],
    ),
    (
        ("router24 cluster24 mirror24 filter24 ranking24 encoding24", 28),
        ["router24 cluster24 mirror24", "filter24 ranking24", "encoding24"],
    ),
    (
        ("cluster24 mirror24 filter24 ranking24 encoding24 mapping24", 6),
        ["cluster24", "mirror24", "filter24", "ranking24", "encoding24", "mapping24"],
    ),
    (
        ("cluster24 mirror24 filter24 ranking24 encoding24 mapping24", 10),
        ["cluster24", "mirror24", "filter24", "ranking24", "encoding24", "mapping24"],
    ),
    (
        ("cluster24 mirror24 filter24 ranking24 encoding24 mapping24", 18),
        ["cluster24 mirror24", "filter24 ranking24", "encoding24", "mapping24"],
    ),
    (
        ("cluster24 mirror24 filter24 ranking24 encoding24 mapping24", 28),
        ["cluster24 mirror24 filter24", "ranking24 encoding24", "mapping24"],
    ),
    (
        ("mirror24 filter24 ranking24 encoding24 mapping24 record24", 6),
        ["mirror24", "filter24", "ranking24", "encoding24", "mapping24", "record24"],
    ),
    (
        ("mirror24 filter24 ranking24 encoding24 mapping24 record24", 10),
        ["mirror24", "filter24", "ranking24", "encoding24", "mapping24", "record24"],
    ),
    (
        ("mirror24 filter24 ranking24 encoding24 mapping24 record24", 18),
        ["mirror24 filter24", "ranking24", "encoding24", "mapping24 record24"],
    ),
    (
        ("mirror24 filter24 ranking24 encoding24 mapping24 record24", 28),
        ["mirror24 filter24 ranking24", "encoding24 mapping24", "record24"],
    ),
    (
        ("filter24 ranking24 encoding24 mapping24 record24 candle24", 6),
        ["filter24", "ranking24", "encoding24", "mapping24", "record24", "candle24"],
    ),
    (
        ("filter24 ranking24 encoding24 mapping24 record24 candle24", 10),
        ["filter24", "ranking24", "encoding24", "mapping24", "record24", "candle24"],
    ),
    (
        ("filter24 ranking24 encoding24 mapping24 record24 candle24", 18),
        ["filter24 ranking24", "encoding24", "mapping24 record24", "candle24"],
    ),
    (
        ("filter24 ranking24 encoding24 mapping24 record24 candle24", 28),
        ["filter24 ranking24", "encoding24 mapping24", "record24 candle24"],
    ),
    (
        ("ranking24 encoding24 mapping24 record24 candle24 thread24", 6),
        ["ranking24", "encoding24", "mapping24", "record24", "candle24", "thread24"],
    ),
    (
        ("ranking24 encoding24 mapping24 record24 candle24 thread24", 10),
        ["ranking24", "encoding24", "mapping24", "record24", "candle24", "thread24"],
    ),
    (
        ("ranking24 encoding24 mapping24 record24 candle24 thread24", 18),
        ["ranking24", "encoding24", "mapping24 record24", "candle24 thread24"],
    ),
    (
        ("ranking24 encoding24 mapping24 record24 candle24 thread24", 28),
        ["ranking24 encoding24", "mapping24 record24 candle24", "thread24"],
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
