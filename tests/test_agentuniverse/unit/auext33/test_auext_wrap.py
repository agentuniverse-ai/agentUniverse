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
        ("round 33: the quick brown fox jumps over the lazy dog", 4),
        ["round", "33:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 33: the quick brown fox jumps over the lazy dog", 8),
        ["round", "33: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 33: the quick brown fox jumps over the lazy dog", 12),
        ["round 33:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 33: the quick brown fox jumps over the lazy dog", 16),
        ["round 33: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 33: the quick brown fox jumps over the lazy dog", 24),
        ["round 33: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 33: the quick brown fox jumps over the lazy dog", 32),
        ["round 33: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 33: agentuniverse is a framework for multi agents", 4),
        ["round", "33:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 33: agentuniverse is a framework for multi agents", 8),
        ["round", "33:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 33: agentuniverse is a framework for multi agents", 12),
        ["round 33:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 33: agentuniverse is a framework for multi agents", 16),
        ["round 33:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 33: agentuniverse is a framework for multi agents", 24),
        ["round 33: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 33: agentuniverse is a framework for multi agents", 32),
        ["round 33: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 33: knowledge stored as vectors enables retrieval", 4),
        ["round", "33:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 33: knowledge stored as vectors enables retrieval", 8),
        ["round", "33:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 33: knowledge stored as vectors enables retrieval", 12),
        ["round 33:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 33: knowledge stored as vectors enables retrieval", 16),
        ["round 33:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 33: knowledge stored as vectors enables retrieval", 24),
        ["round 33: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 33: knowledge stored as vectors enables retrieval", 32),
        ["round 33: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 33: the processor reads the record then stops", 4),
        ["round", "33:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 33: the processor reads the record then stops", 8),
        ["round", "33: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 33: the processor reads the record then stops", 12),
        ["round 33:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 33: the processor reads the record then stops", 16),
        ["round 33: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 33: the processor reads the record then stops", 24),
        ["round 33: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 33: the processor reads the record then stops", 32),
        ["round 33: the processor reads", "the record then stops"],
    ),
    (
        ("round 33: a worker pulls the next task from the queue", 4),
        ["round", "33:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 33: a worker pulls the next task from the queue", 8),
        ["round", "33: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 33: a worker pulls the next task from the queue", 12),
        ["round 33: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 33: a worker pulls the next task from the queue", 16),
        ["round 33: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 33: a worker pulls the next task from the queue", 24),
        ["round 33: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 33: a worker pulls the next task from the queue", 32),
        ["round 33: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 33: signals travel through the network layer", 4),
        ["round", "33:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 33: signals travel through the network layer", 8),
        ["round", "33:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 33: signals travel through the network layer", 12),
        ["round 33:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 33: signals travel through the network layer", 16),
        ["round 33:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 33: signals travel through the network layer", 24),
        ["round 33: signals travel", "through the network", "layer"],
    ),
    (
        ("round 33: signals travel through the network layer", 32),
        ["round 33: signals travel through", "the network layer"],
    ),
    (
        ("round 33: the gateway routes each request by policy", 4),
        ["round", "33:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 33: the gateway routes each request by policy", 8),
        ["round", "33: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 33: the gateway routes each request by policy", 12),
        ["round 33:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 33: the gateway routes each request by policy", 16),
        ["round 33: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 33: the gateway routes each request by policy", 24),
        ["round 33: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 33: the gateway routes each request by policy", 32),
        ["round 33: the gateway routes", "each request by policy"],
    ),
    (
        ("round 33: memory grows until the buffer is full", 4),
        ["round", "33:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 33: memory grows until the buffer is full", 8),
        ["round", "33:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 33: memory grows until the buffer is full", 12),
        ["round 33:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 33: memory grows until the buffer is full", 16),
        ["round 33: memory", "grows until the", "buffer is full"],
    ),
    (("round 33: memory grows until the buffer is full", 24), ["round 33: memory grows", "until the buffer is full"]),
    (("round 33: memory grows until the buffer is full", 32), ["round 33: memory grows until the", "buffer is full"]),
    (
        ("round 33: the cluster mirrors every packet twice", 4),
        ["round", "33:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 33: the cluster mirrors every packet twice", 8),
        ["round", "33: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 33: the cluster mirrors every packet twice", 12),
        ["round 33:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 33: the cluster mirrors every packet twice", 16),
        ["round 33: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 33: the cluster mirrors every packet twice", 24),
        ["round 33: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 33: the cluster mirrors every packet twice", 32), ["round 33: the cluster mirrors", "every packet twice"]),
    (
        ("round 33: ranking uses tokens learned from the corpus", 4),
        ["round", "33:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 33: ranking uses tokens learned from the corpus", 8),
        ["round", "33:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 33: ranking uses tokens learned from the corpus", 12),
        ["round 33:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 33: ranking uses tokens learned from the corpus", 16),
        ["round 33:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 33: ranking uses tokens learned from the corpus", 24),
        ["round 33: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 33: ranking uses tokens learned from the corpus", 32),
        ["round 33: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 33: a long session ends when the candle dies", 4),
        ["round", "33:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 33: a long session ends when the candle dies", 8),
        ["round", "33: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 33: a long session ends when the candle dies", 12),
        ["round 33: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 33: a long session ends when the candle dies", 16),
        ["round 33: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 33: a long session ends when the candle dies", 24),
        ["round 33: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 33: a long session ends when the candle dies", 32),
        ["round 33: a long session ends", "when the candle dies"],
    ),
    (
        ("round 33: encode the prompt then map the result", 4),
        ["round", "33:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 33: encode the prompt then map the result", 8),
        ["round", "33:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 33: encode the prompt then map the result", 12),
        ["round 33:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 33: encode the prompt then map the result", 16),
        ["round 33: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 33: encode the prompt then map the result", 24),
        ["round 33: encode the", "prompt then map the", "result"],
    ),
    (("round 33: encode the prompt then map the result", 32), ["round 33: encode the prompt then", "map the result"]),
    (
        ("round 33: the kernel wakes the worker at dawn", 4),
        ["round", "33:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 33: the kernel wakes the worker at dawn", 8),
        ["round", "33: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 33: the kernel wakes the worker at dawn", 12),
        ["round 33:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 33: the kernel wakes the worker at dawn", 16), ["round 33: the", "kernel wakes the", "worker at dawn"]),
    (("round 33: the kernel wakes the worker at dawn", 24), ["round 33: the kernel", "wakes the worker at dawn"]),
    (("round 33: the kernel wakes the worker at dawn", 32), ["round 33: the kernel wakes the", "worker at dawn"]),
    (
        ("round 33: service latency drops after the patch", 4),
        ["round", "33:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 33: service latency drops after the patch", 8),
        ["round", "33:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 33: service latency drops after the patch", 12),
        ["round 33:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 33: service latency drops after the patch", 16),
        ["round 33:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 33: service latency drops after the patch", 24),
        ["round 33: service", "latency drops after the", "patch"],
    ),
    (("round 33: service latency drops after the patch", 32), ["round 33: service latency drops", "after the patch"]),
    (
        ("round 33: the library caches every vector it sees", 4),
        ["round", "33:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 33: the library caches every vector it sees", 8),
        ["round", "33: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 33: the library caches every vector it sees", 12),
        ["round 33:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 33: the library caches every vector it sees", 16),
        ["round 33: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 33: the library caches every vector it sees", 24),
        ["round 33: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 33: the library caches every vector it sees", 32),
        ["round 33: the library caches", "every vector it sees"],
    ),
    (
        ("round 33: agents argue then the debate resolves", 4),
        ["round", "33:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 33: agents argue then the debate resolves", 8),
        ["round", "33:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 33: agents argue then the debate resolves", 12),
        ["round 33:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 33: agents argue then the debate resolves", 16),
        ["round 33: agents", "argue then the", "debate resolves"],
    ),
    (("round 33: agents argue then the debate resolves", 24), ["round 33: agents argue", "then the debate resolves"]),
    (("round 33: agents argue then the debate resolves", 32), ["round 33: agents argue then the", "debate resolves"]),
    (
        ("round 33: the filter keeps only strong matches", 4),
        ["round", "33:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 33: the filter keeps only strong matches", 8),
        ["round", "33: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 33: the filter keeps only strong matches", 12),
        ["round 33:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 33: the filter keeps only strong matches", 16),
        ["round 33: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 33: the filter keeps only strong matches", 24), ["round 33: the filter", "keeps only strong", "matches"]),
    (("round 33: the filter keeps only strong matches", 32), ["round 33: the filter keeps only", "strong matches"]),
    (
        ("round 33: the model answers with a short reply", 4),
        ["round", "33:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 33: the model answers with a short reply", 8),
        ["round", "33: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 33: the model answers with a short reply", 12),
        ["round 33:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 33: the model answers with a short reply", 16),
        ["round 33: the", "model answers", "with a short", "reply"],
    ),
    (("round 33: the model answers with a short reply", 24), ["round 33: the model", "answers with a short", "reply"]),
    (("round 33: the model answers with a short reply", 32), ["round 33: the model answers with", "a short reply"]),
    (
        ("round 33: the recorder stores the reasoning trace", 4),
        ["round", "33:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 33: the recorder stores the reasoning trace", 8),
        ["round", "33: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 33: the recorder stores the reasoning trace", 12),
        ["round 33:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 33: the recorder stores the reasoning trace", 16),
        ["round 33: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 33: the recorder stores the reasoning trace", 24),
        ["round 33: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 33: the recorder stores the reasoning trace", 32),
        ["round 33: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 33: the angel watches the processor run", 4),
        ["round", "33:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 33: the angel watches the processor run", 8),
        ["round", "33: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 33: the angel watches the processor run", 12),
        ["round 33:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 33: the angel watches the processor run", 16), ["round 33: the", "angel watches", "the processor", "run"]),
    (("round 33: the angel watches the processor run", 24), ["round 33: the angel", "watches the processor", "run"]),
    (("round 33: the angel watches the processor run", 32), ["round 33: the angel watches the", "processor run"]),
    (
        ("round 33: angle of the vector decides the match", 4),
        ["round", "33:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 33: angle of the vector decides the match", 8),
        ["round", "33:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 33: angle of the vector decides the match", 12),
        ["round 33:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 33: angle of the vector decides the match", 16),
        ["round 33: angle", "of the vector", "decides the", "match"],
    ),
    (("round 33: angle of the vector decides the match", 24), ["round 33: angle of the", "vector decides the match"]),
    (("round 33: angle of the vector decides the match", 32), ["round 33: angle of the vector", "decides the match"]),
    (
        ("round 33: the candle burns twice as long at night", 4),
        ["round", "33:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 33: the candle burns twice as long at night", 8),
        ["round", "33: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 33: the candle burns twice as long at night", 12),
        ["round 33:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 33: the candle burns twice as long at night", 16),
        ["round 33: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 33: the candle burns twice as long at night", 24),
        ["round 33: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 33: the candle burns twice as long at night", 32),
        ["round 33: the candle burns twice", "as long at night"],
    ),
    (
        ("round 33: a mirror of the universe in one line", 4),
        ["round", "33:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 33: a mirror of the universe in one line", 8),
        ["round", "33: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 33: a mirror of the universe in one line", 12),
        ["round 33: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 33: a mirror of the universe in one line", 16),
        ["round 33: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 33: a mirror of the universe in one line", 24), ["round 33: a mirror of", "the universe in one line"]),
    (("round 33: a mirror of the universe in one line", 32), ["round 33: a mirror of the", "universe in one line"]),
    (
        ("round 33: the queue drains before the storm", 4),
        ["round", "33:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 33: the queue drains before the storm", 8),
        ["round", "33: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 33: the queue drains before the storm", 12), ["round 33:", "the queue", "drains", "before the", "storm"]),
    (("round 33: the queue drains before the storm", 16), ["round 33: the", "queue drains", "before the storm"]),
    (("round 33: the queue drains before the storm", 24), ["round 33: the queue", "drains before the storm"]),
    (("round 33: the queue drains before the storm", 32), ["round 33: the queue drains", "before the storm"]),
    (
        ("kitten33 sitting33 agent33 angle33 universe33 memory33", 6),
        ["kitten33", "sitting33", "agent33", "angle33", "universe33", "memory33"],
    ),
    (
        ("kitten33 sitting33 agent33 angle33 universe33 memory33", 10),
        ["kitten33", "sitting33", "agent33", "angle33", "universe33", "memory33"],
    ),
    (
        ("kitten33 sitting33 agent33 angle33 universe33 memory33", 18),
        ["kitten33 sitting33", "agent33 angle33", "universe33", "memory33"],
    ),
    (
        ("kitten33 sitting33 agent33 angle33 universe33 memory33", 28),
        ["kitten33 sitting33 agent33", "angle33 universe33 memory33"],
    ),
    (
        ("sitting33 agent33 angle33 universe33 memory33 stream33", 6),
        ["sitting33", "agent33", "angle33", "universe33", "memory33", "stream33"],
    ),
    (
        ("sitting33 agent33 angle33 universe33 memory33 stream33", 10),
        ["sitting33", "agent33", "angle33", "universe33", "memory33", "stream33"],
    ),
    (
        ("sitting33 agent33 angle33 universe33 memory33 stream33", 18),
        ["sitting33 agent33", "angle33 universe33", "memory33 stream33"],
    ),
    (
        ("sitting33 agent33 angle33 universe33 memory33 stream33", 28),
        ["sitting33 agent33 angle33", "universe33 memory33 stream33"],
    ),
    (
        ("agent33 angle33 universe33 memory33 stream33 context33", 6),
        ["agent33", "angle33", "universe33", "memory33", "stream33", "context33"],
    ),
    (
        ("agent33 angle33 universe33 memory33 stream33 context33", 10),
        ["agent33", "angle33", "universe33", "memory33", "stream33", "context33"],
    ),
    (
        ("agent33 angle33 universe33 memory33 stream33 context33", 18),
        ["agent33 angle33", "universe33", "memory33 stream33", "context33"],
    ),
    (
        ("agent33 angle33 universe33 memory33 stream33 context33", 28),
        ["agent33 angle33 universe33", "memory33 stream33 context33"],
    ),
    (
        ("angle33 universe33 memory33 stream33 context33 knowledge33", 6),
        ["angle33", "universe33", "memory33", "stream33", "context33", "knowledge33"],
    ),
    (
        ("angle33 universe33 memory33 stream33 context33 knowledge33", 10),
        ["angle33", "universe33", "memory33", "stream33", "context33", "knowledge33"],
    ),
    (
        ("angle33 universe33 memory33 stream33 context33 knowledge33", 18),
        ["angle33 universe33", "memory33 stream33", "context33", "knowledge33"],
    ),
    (
        ("angle33 universe33 memory33 stream33 context33 knowledge33", 28),
        ["angle33 universe33 memory33", "stream33 context33", "knowledge33"],
    ),
    (
        ("universe33 memory33 stream33 context33 knowledge33 vector33", 6),
        ["universe33", "memory33", "stream33", "context33", "knowledge33", "vector33"],
    ),
    (
        ("universe33 memory33 stream33 context33 knowledge33 vector33", 10),
        ["universe33", "memory33", "stream33", "context33", "knowledge33", "vector33"],
    ),
    (
        ("universe33 memory33 stream33 context33 knowledge33 vector33", 18),
        ["universe33", "memory33 stream33", "context33", "knowledge33", "vector33"],
    ),
    (
        ("universe33 memory33 stream33 context33 knowledge33 vector33", 28),
        ["universe33 memory33 stream33", "context33 knowledge33", "vector33"],
    ),
    (
        ("memory33 stream33 context33 knowledge33 vector33 processor33", 6),
        ["memory33", "stream33", "context33", "knowledge33", "vector33", "processor33"],
    ),
    (
        ("memory33 stream33 context33 knowledge33 vector33 processor33", 10),
        ["memory33", "stream33", "context33", "knowledge33", "vector33", "processor33"],
    ),
    (
        ("memory33 stream33 context33 knowledge33 vector33 processor33", 18),
        ["memory33 stream33", "context33", "knowledge33", "vector33", "processor33"],
    ),
    (
        ("memory33 stream33 context33 knowledge33 vector33 processor33", 28),
        ["memory33 stream33 context33", "knowledge33 vector33", "processor33"],
    ),
    (
        ("stream33 context33 knowledge33 vector33 processor33 reasoning33", 6),
        ["stream33", "context33", "knowledge33", "vector33", "processor33", "reasoning33"],
    ),
    (
        ("stream33 context33 knowledge33 vector33 processor33 reasoning33", 10),
        ["stream33", "context33", "knowledge33", "vector33", "processor33", "reasoning33"],
    ),
    (
        ("stream33 context33 knowledge33 vector33 processor33 reasoning33", 18),
        ["stream33 context33", "knowledge33", "vector33", "processor33", "reasoning33"],
    ),
    (
        ("stream33 context33 knowledge33 vector33 processor33 reasoning33", 28),
        ["stream33 context33", "knowledge33 vector33", "processor33 reasoning33"],
    ),
    (
        ("context33 knowledge33 vector33 processor33 reasoning33 machine33", 6),
        ["context33", "knowledge33", "vector33", "processor33", "reasoning33", "machine33"],
    ),
    (
        ("context33 knowledge33 vector33 processor33 reasoning33 machine33", 10),
        ["context33", "knowledge33", "vector33", "processor33", "reasoning33", "machine33"],
    ),
    (
        ("context33 knowledge33 vector33 processor33 reasoning33 machine33", 18),
        ["context33", "knowledge33", "vector33", "processor33", "reasoning33", "machine33"],
    ),
    (
        ("context33 knowledge33 vector33 processor33 reasoning33 machine33", 28),
        ["context33 knowledge33", "vector33 processor33", "reasoning33 machine33"],
    ),
    (
        ("knowledge33 vector33 processor33 reasoning33 machine33 learning33", 6),
        ["knowledge33", "vector33", "processor33", "reasoning33", "machine33", "learning33"],
    ),
    (
        ("knowledge33 vector33 processor33 reasoning33 machine33 learning33", 10),
        ["knowledge33", "vector33", "processor33", "reasoning33", "machine33", "learning33"],
    ),
    (
        ("knowledge33 vector33 processor33 reasoning33 machine33 learning33", 18),
        ["knowledge33", "vector33", "processor33", "reasoning33", "machine33", "learning33"],
    ),
    (
        ("knowledge33 vector33 processor33 reasoning33 machine33 learning33", 28),
        ["knowledge33 vector33", "processor33 reasoning33", "machine33 learning33"],
    ),
    (
        ("vector33 processor33 reasoning33 machine33 learning33 model33", 6),
        ["vector33", "processor33", "reasoning33", "machine33", "learning33", "model33"],
    ),
    (
        ("vector33 processor33 reasoning33 machine33 learning33 model33", 10),
        ["vector33", "processor33", "reasoning33", "machine33", "learning33", "model33"],
    ),
    (
        ("vector33 processor33 reasoning33 machine33 learning33 model33", 18),
        ["vector33", "processor33", "reasoning33", "machine33", "learning33 model33"],
    ),
    (
        ("vector33 processor33 reasoning33 machine33 learning33 model33", 28),
        ["vector33 processor33", "reasoning33 machine33", "learning33 model33"],
    ),
    (
        ("processor33 reasoning33 machine33 learning33 model33 token33", 6),
        ["processor33", "reasoning33", "machine33", "learning33", "model33", "token33"],
    ),
    (
        ("processor33 reasoning33 machine33 learning33 model33 token33", 10),
        ["processor33", "reasoning33", "machine33", "learning33", "model33", "token33"],
    ),
    (
        ("processor33 reasoning33 machine33 learning33 model33 token33", 18),
        ["processor33", "reasoning33", "machine33", "learning33 model33", "token33"],
    ),
    (
        ("processor33 reasoning33 machine33 learning33 model33 token33", 28),
        ["processor33 reasoning33", "machine33 learning33 model33", "token33"],
    ),
    (
        ("reasoning33 machine33 learning33 model33 token33 prompt33", 6),
        ["reasoning33", "machine33", "learning33", "model33", "token33", "prompt33"],
    ),
    (
        ("reasoning33 machine33 learning33 model33 token33 prompt33", 10),
        ["reasoning33", "machine33", "learning33", "model33", "token33", "prompt33"],
    ),
    (
        ("reasoning33 machine33 learning33 model33 token33 prompt33", 18),
        ["reasoning33", "machine33", "learning33 model33", "token33 prompt33"],
    ),
    (
        ("reasoning33 machine33 learning33 model33 token33 prompt33", 28),
        ["reasoning33 machine33", "learning33 model33 token33", "prompt33"],
    ),
    (
        ("machine33 learning33 model33 token33 prompt33 session33", 6),
        ["machine33", "learning33", "model33", "token33", "prompt33", "session33"],
    ),
    (
        ("machine33 learning33 model33 token33 prompt33 session33", 10),
        ["machine33", "learning33", "model33", "token33", "prompt33", "session33"],
    ),
    (
        ("machine33 learning33 model33 token33 prompt33 session33", 18),
        ["machine33", "learning33 model33", "token33 prompt33", "session33"],
    ),
    (
        ("machine33 learning33 model33 token33 prompt33 session33", 28),
        ["machine33 learning33 model33", "token33 prompt33 session33"],
    ),
    (
        ("learning33 model33 token33 prompt33 session33 library33", 6),
        ["learning33", "model33", "token33", "prompt33", "session33", "library33"],
    ),
    (
        ("learning33 model33 token33 prompt33 session33 library33", 10),
        ["learning33", "model33", "token33", "prompt33", "session33", "library33"],
    ),
    (
        ("learning33 model33 token33 prompt33 session33 library33", 18),
        ["learning33 model33", "token33 prompt33", "session33", "library33"],
    ),
    (
        ("learning33 model33 token33 prompt33 session33 library33", 28),
        ["learning33 model33 token33", "prompt33 session33 library33"],
    ),
    (
        ("model33 token33 prompt33 session33 library33 service33", 6),
        ["model33", "token33", "prompt33", "session33", "library33", "service33"],
    ),
    (
        ("model33 token33 prompt33 session33 library33 service33", 10),
        ["model33", "token33", "prompt33", "session33", "library33", "service33"],
    ),
    (
        ("model33 token33 prompt33 session33 library33 service33", 18),
        ["model33 token33", "prompt33 session33", "library33", "service33"],
    ),
    (
        ("model33 token33 prompt33 session33 library33 service33", 28),
        ["model33 token33 prompt33", "session33 library33", "service33"],
    ),
    (
        ("token33 prompt33 session33 library33 service33 gateway33", 6),
        ["token33", "prompt33", "session33", "library33", "service33", "gateway33"],
    ),
    (
        ("token33 prompt33 session33 library33 service33 gateway33", 10),
        ["token33", "prompt33", "session33", "library33", "service33", "gateway33"],
    ),
    (
        ("token33 prompt33 session33 library33 service33 gateway33", 18),
        ["token33 prompt33", "session33", "library33", "service33", "gateway33"],
    ),
    (
        ("token33 prompt33 session33 library33 service33 gateway33", 28),
        ["token33 prompt33 session33", "library33 service33", "gateway33"],
    ),
    (
        ("prompt33 session33 library33 service33 gateway33 storage33", 6),
        ["prompt33", "session33", "library33", "service33", "gateway33", "storage33"],
    ),
    (
        ("prompt33 session33 library33 service33 gateway33 storage33", 10),
        ["prompt33", "session33", "library33", "service33", "gateway33", "storage33"],
    ),
    (
        ("prompt33 session33 library33 service33 gateway33 storage33", 18),
        ["prompt33 session33", "library33", "service33", "gateway33", "storage33"],
    ),
    (
        ("prompt33 session33 library33 service33 gateway33 storage33", 28),
        ["prompt33 session33 library33", "service33 gateway33", "storage33"],
    ),
    (
        ("session33 library33 service33 gateway33 storage33 network33", 6),
        ["session33", "library33", "service33", "gateway33", "storage33", "network33"],
    ),
    (
        ("session33 library33 service33 gateway33 storage33 network33", 10),
        ["session33", "library33", "service33", "gateway33", "storage33", "network33"],
    ),
    (
        ("session33 library33 service33 gateway33 storage33 network33", 18),
        ["session33", "library33", "service33", "gateway33", "storage33", "network33"],
    ),
    (
        ("session33 library33 service33 gateway33 storage33 network33", 28),
        ["session33 library33", "service33 gateway33", "storage33 network33"],
    ),
    (
        ("library33 service33 gateway33 storage33 network33 latency33", 6),
        ["library33", "service33", "gateway33", "storage33", "network33", "latency33"],
    ),
    (
        ("library33 service33 gateway33 storage33 network33 latency33", 10),
        ["library33", "service33", "gateway33", "storage33", "network33", "latency33"],
    ),
    (
        ("library33 service33 gateway33 storage33 network33 latency33", 18),
        ["library33", "service33", "gateway33", "storage33", "network33", "latency33"],
    ),
    (
        ("library33 service33 gateway33 storage33 network33 latency33", 28),
        ["library33 service33", "gateway33 storage33", "network33 latency33"],
    ),
    (
        ("service33 gateway33 storage33 network33 latency33 buffer33", 6),
        ["service33", "gateway33", "storage33", "network33", "latency33", "buffer33"],
    ),
    (
        ("service33 gateway33 storage33 network33 latency33 buffer33", 10),
        ["service33", "gateway33", "storage33", "network33", "latency33", "buffer33"],
    ),
    (
        ("service33 gateway33 storage33 network33 latency33 buffer33", 18),
        ["service33", "gateway33", "storage33", "network33", "latency33 buffer33"],
    ),
    (
        ("service33 gateway33 storage33 network33 latency33 buffer33", 28),
        ["service33 gateway33", "storage33 network33", "latency33 buffer33"],
    ),
    (
        ("gateway33 storage33 network33 latency33 buffer33 queue33", 6),
        ["gateway33", "storage33", "network33", "latency33", "buffer33", "queue33"],
    ),
    (
        ("gateway33 storage33 network33 latency33 buffer33 queue33", 10),
        ["gateway33", "storage33", "network33", "latency33", "buffer33", "queue33"],
    ),
    (
        ("gateway33 storage33 network33 latency33 buffer33 queue33", 18),
        ["gateway33", "storage33", "network33", "latency33 buffer33", "queue33"],
    ),
    (
        ("gateway33 storage33 network33 latency33 buffer33 queue33", 28),
        ["gateway33 storage33", "network33 latency33 buffer33", "queue33"],
    ),
    (
        ("storage33 network33 latency33 buffer33 queue33 worker33", 6),
        ["storage33", "network33", "latency33", "buffer33", "queue33", "worker33"],
    ),
    (
        ("storage33 network33 latency33 buffer33 queue33 worker33", 10),
        ["storage33", "network33", "latency33", "buffer33", "queue33", "worker33"],
    ),
    (
        ("storage33 network33 latency33 buffer33 queue33 worker33", 18),
        ["storage33", "network33", "latency33 buffer33", "queue33 worker33"],
    ),
    (
        ("storage33 network33 latency33 buffer33 queue33 worker33", 28),
        ["storage33 network33", "latency33 buffer33 queue33", "worker33"],
    ),
    (
        ("network33 latency33 buffer33 queue33 worker33 kernel33", 6),
        ["network33", "latency33", "buffer33", "queue33", "worker33", "kernel33"],
    ),
    (
        ("network33 latency33 buffer33 queue33 worker33 kernel33", 10),
        ["network33", "latency33", "buffer33", "queue33", "worker33", "kernel33"],
    ),
    (
        ("network33 latency33 buffer33 queue33 worker33 kernel33", 18),
        ["network33", "latency33 buffer33", "queue33 worker33", "kernel33"],
    ),
    (
        ("network33 latency33 buffer33 queue33 worker33 kernel33", 28),
        ["network33 latency33 buffer33", "queue33 worker33 kernel33"],
    ),
    (
        ("latency33 buffer33 queue33 worker33 kernel33 signal33", 6),
        ["latency33", "buffer33", "queue33", "worker33", "kernel33", "signal33"],
    ),
    (
        ("latency33 buffer33 queue33 worker33 kernel33 signal33", 10),
        ["latency33", "buffer33", "queue33", "worker33", "kernel33", "signal33"],
    ),
    (
        ("latency33 buffer33 queue33 worker33 kernel33 signal33", 18),
        ["latency33 buffer33", "queue33 worker33", "kernel33 signal33"],
    ),
    (
        ("latency33 buffer33 queue33 worker33 kernel33 signal33", 28),
        ["latency33 buffer33 queue33", "worker33 kernel33 signal33"],
    ),
    (
        ("buffer33 queue33 worker33 kernel33 signal33 packet33", 6),
        ["buffer33", "queue33", "worker33", "kernel33", "signal33", "packet33"],
    ),
    (
        ("buffer33 queue33 worker33 kernel33 signal33 packet33", 10),
        ["buffer33", "queue33", "worker33", "kernel33", "signal33", "packet33"],
    ),
    (
        ("buffer33 queue33 worker33 kernel33 signal33 packet33", 18),
        ["buffer33 queue33", "worker33 kernel33", "signal33 packet33"],
    ),
    (
        ("buffer33 queue33 worker33 kernel33 signal33 packet33", 28),
        ["buffer33 queue33 worker33", "kernel33 signal33 packet33"],
    ),
    (
        ("queue33 worker33 kernel33 signal33 packet33 router33", 6),
        ["queue33", "worker33", "kernel33", "signal33", "packet33", "router33"],
    ),
    (
        ("queue33 worker33 kernel33 signal33 packet33 router33", 10),
        ["queue33", "worker33", "kernel33", "signal33", "packet33", "router33"],
    ),
    (
        ("queue33 worker33 kernel33 signal33 packet33 router33", 18),
        ["queue33 worker33", "kernel33 signal33", "packet33 router33"],
    ),
    (
        ("queue33 worker33 kernel33 signal33 packet33 router33", 28),
        ["queue33 worker33 kernel33", "signal33 packet33 router33"],
    ),
    (
        ("worker33 kernel33 signal33 packet33 router33 cluster33", 6),
        ["worker33", "kernel33", "signal33", "packet33", "router33", "cluster33"],
    ),
    (
        ("worker33 kernel33 signal33 packet33 router33 cluster33", 10),
        ["worker33", "kernel33", "signal33", "packet33", "router33", "cluster33"],
    ),
    (
        ("worker33 kernel33 signal33 packet33 router33 cluster33", 18),
        ["worker33 kernel33", "signal33 packet33", "router33 cluster33"],
    ),
    (
        ("worker33 kernel33 signal33 packet33 router33 cluster33", 28),
        ["worker33 kernel33 signal33", "packet33 router33 cluster33"],
    ),
    (
        ("kernel33 signal33 packet33 router33 cluster33 mirror33", 6),
        ["kernel33", "signal33", "packet33", "router33", "cluster33", "mirror33"],
    ),
    (
        ("kernel33 signal33 packet33 router33 cluster33 mirror33", 10),
        ["kernel33", "signal33", "packet33", "router33", "cluster33", "mirror33"],
    ),
    (
        ("kernel33 signal33 packet33 router33 cluster33 mirror33", 18),
        ["kernel33 signal33", "packet33 router33", "cluster33 mirror33"],
    ),
    (
        ("kernel33 signal33 packet33 router33 cluster33 mirror33", 28),
        ["kernel33 signal33 packet33", "router33 cluster33 mirror33"],
    ),
    (
        ("signal33 packet33 router33 cluster33 mirror33 filter33", 6),
        ["signal33", "packet33", "router33", "cluster33", "mirror33", "filter33"],
    ),
    (
        ("signal33 packet33 router33 cluster33 mirror33 filter33", 10),
        ["signal33", "packet33", "router33", "cluster33", "mirror33", "filter33"],
    ),
    (
        ("signal33 packet33 router33 cluster33 mirror33 filter33", 18),
        ["signal33 packet33", "router33 cluster33", "mirror33 filter33"],
    ),
    (
        ("signal33 packet33 router33 cluster33 mirror33 filter33", 28),
        ["signal33 packet33 router33", "cluster33 mirror33 filter33"],
    ),
    (
        ("packet33 router33 cluster33 mirror33 filter33 ranking33", 6),
        ["packet33", "router33", "cluster33", "mirror33", "filter33", "ranking33"],
    ),
    (
        ("packet33 router33 cluster33 mirror33 filter33 ranking33", 10),
        ["packet33", "router33", "cluster33", "mirror33", "filter33", "ranking33"],
    ),
    (
        ("packet33 router33 cluster33 mirror33 filter33 ranking33", 18),
        ["packet33 router33", "cluster33 mirror33", "filter33 ranking33"],
    ),
    (
        ("packet33 router33 cluster33 mirror33 filter33 ranking33", 28),
        ["packet33 router33 cluster33", "mirror33 filter33 ranking33"],
    ),
    (
        ("router33 cluster33 mirror33 filter33 ranking33 encoding33", 6),
        ["router33", "cluster33", "mirror33", "filter33", "ranking33", "encoding33"],
    ),
    (
        ("router33 cluster33 mirror33 filter33 ranking33 encoding33", 10),
        ["router33", "cluster33", "mirror33", "filter33", "ranking33", "encoding33"],
    ),
    (
        ("router33 cluster33 mirror33 filter33 ranking33 encoding33", 18),
        ["router33 cluster33", "mirror33 filter33", "ranking33", "encoding33"],
    ),
    (
        ("router33 cluster33 mirror33 filter33 ranking33 encoding33", 28),
        ["router33 cluster33 mirror33", "filter33 ranking33", "encoding33"],
    ),
    (
        ("cluster33 mirror33 filter33 ranking33 encoding33 mapping33", 6),
        ["cluster33", "mirror33", "filter33", "ranking33", "encoding33", "mapping33"],
    ),
    (
        ("cluster33 mirror33 filter33 ranking33 encoding33 mapping33", 10),
        ["cluster33", "mirror33", "filter33", "ranking33", "encoding33", "mapping33"],
    ),
    (
        ("cluster33 mirror33 filter33 ranking33 encoding33 mapping33", 18),
        ["cluster33 mirror33", "filter33 ranking33", "encoding33", "mapping33"],
    ),
    (
        ("cluster33 mirror33 filter33 ranking33 encoding33 mapping33", 28),
        ["cluster33 mirror33 filter33", "ranking33 encoding33", "mapping33"],
    ),
    (
        ("mirror33 filter33 ranking33 encoding33 mapping33 record33", 6),
        ["mirror33", "filter33", "ranking33", "encoding33", "mapping33", "record33"],
    ),
    (
        ("mirror33 filter33 ranking33 encoding33 mapping33 record33", 10),
        ["mirror33", "filter33", "ranking33", "encoding33", "mapping33", "record33"],
    ),
    (
        ("mirror33 filter33 ranking33 encoding33 mapping33 record33", 18),
        ["mirror33 filter33", "ranking33", "encoding33", "mapping33 record33"],
    ),
    (
        ("mirror33 filter33 ranking33 encoding33 mapping33 record33", 28),
        ["mirror33 filter33 ranking33", "encoding33 mapping33", "record33"],
    ),
    (
        ("filter33 ranking33 encoding33 mapping33 record33 candle33", 6),
        ["filter33", "ranking33", "encoding33", "mapping33", "record33", "candle33"],
    ),
    (
        ("filter33 ranking33 encoding33 mapping33 record33 candle33", 10),
        ["filter33", "ranking33", "encoding33", "mapping33", "record33", "candle33"],
    ),
    (
        ("filter33 ranking33 encoding33 mapping33 record33 candle33", 18),
        ["filter33 ranking33", "encoding33", "mapping33 record33", "candle33"],
    ),
    (
        ("filter33 ranking33 encoding33 mapping33 record33 candle33", 28),
        ["filter33 ranking33", "encoding33 mapping33", "record33 candle33"],
    ),
    (
        ("ranking33 encoding33 mapping33 record33 candle33 thread33", 6),
        ["ranking33", "encoding33", "mapping33", "record33", "candle33", "thread33"],
    ),
    (
        ("ranking33 encoding33 mapping33 record33 candle33 thread33", 10),
        ["ranking33", "encoding33", "mapping33", "record33", "candle33", "thread33"],
    ),
    (
        ("ranking33 encoding33 mapping33 record33 candle33 thread33", 18),
        ["ranking33", "encoding33", "mapping33 record33", "candle33 thread33"],
    ),
    (
        ("ranking33 encoding33 mapping33 record33 candle33 thread33", 28),
        ["ranking33 encoding33", "mapping33 record33 candle33", "thread33"],
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
