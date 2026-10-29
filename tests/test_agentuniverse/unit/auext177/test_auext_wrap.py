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
        ("round 177: the quick brown fox jumps over the lazy dog", 4),
        ["round", "177:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", 8),
        ["round", "177: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", 12),
        ["round 177:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", 16),
        ["round 177: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", 24),
        ["round 177: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 177: the quick brown fox jumps over the lazy dog", 32),
        ["round 177: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", 4),
        ["round", "177:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", 8),
        ["round", "177:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", 12),
        ["round 177:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", 16),
        ["round 177:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", 24),
        ["round 177: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 177: agentuniverse is a framework for multi agents", 32),
        ["round 177: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", 4),
        ["round", "177:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", 8),
        ["round", "177:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", 12),
        ["round 177:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", 16),
        ["round 177:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", 24),
        ["round 177: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 177: knowledge stored as vectors enables retrieval", 32),
        ["round 177: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 177: the processor reads the record then stops", 4),
        ["round", "177:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 177: the processor reads the record then stops", 8),
        ["round", "177: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 177: the processor reads the record then stops", 12),
        ["round 177:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 177: the processor reads the record then stops", 16),
        ["round 177: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 177: the processor reads the record then stops", 24),
        ["round 177: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 177: the processor reads the record then stops", 32),
        ["round 177: the processor reads", "the record then stops"],
    ),
    (
        ("round 177: a worker pulls the next task from the queue", 4),
        ["round", "177:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 177: a worker pulls the next task from the queue", 8),
        ["round", "177: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 177: a worker pulls the next task from the queue", 12),
        ["round 177: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 177: a worker pulls the next task from the queue", 16),
        ["round 177: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 177: a worker pulls the next task from the queue", 24),
        ["round 177: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 177: a worker pulls the next task from the queue", 32),
        ["round 177: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 177: signals travel through the network layer", 4),
        ["round", "177:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 177: signals travel through the network layer", 8),
        ["round", "177:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 177: signals travel through the network layer", 12),
        ["round 177:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 177: signals travel through the network layer", 16),
        ["round 177:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 177: signals travel through the network layer", 24),
        ["round 177: signals", "travel through the", "network layer"],
    ),
    (
        ("round 177: signals travel through the network layer", 32),
        ["round 177: signals travel", "through the network layer"],
    ),
    (
        ("round 177: the gateway routes each request by policy", 4),
        ["round", "177:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 177: the gateway routes each request by policy", 8),
        ["round", "177: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 177: the gateway routes each request by policy", 12),
        ["round 177:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 177: the gateway routes each request by policy", 16),
        ["round 177: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 177: the gateway routes each request by policy", 24),
        ["round 177: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 177: the gateway routes each request by policy", 32),
        ["round 177: the gateway routes", "each request by policy"],
    ),
    (
        ("round 177: memory grows until the buffer is full", 4),
        ["round", "177:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 177: memory grows until the buffer is full", 8),
        ["round", "177:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 177: memory grows until the buffer is full", 12),
        ["round 177:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 177: memory grows until the buffer is full", 16),
        ["round 177:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 177: memory grows until the buffer is full", 24), ["round 177: memory grows", "until the buffer is full"]),
    (("round 177: memory grows until the buffer is full", 32), ["round 177: memory grows until", "the buffer is full"]),
    (
        ("round 177: the cluster mirrors every packet twice", 4),
        ["round", "177:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 177: the cluster mirrors every packet twice", 8),
        ["round", "177: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 177: the cluster mirrors every packet twice", 12),
        ["round 177:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 177: the cluster mirrors every packet twice", 16),
        ["round 177: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 177: the cluster mirrors every packet twice", 24),
        ["round 177: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 177: the cluster mirrors every packet twice", 32),
        ["round 177: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", 4),
        ["round", "177:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", 8),
        ["round", "177:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", 12),
        ["round 177:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", 16),
        ["round 177:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", 24),
        ["round 177: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 177: ranking uses tokens learned from the corpus", 32),
        ["round 177: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 177: a long session ends when the candle dies", 4),
        ["round", "177:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 177: a long session ends when the candle dies", 8),
        ["round", "177: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 177: a long session ends when the candle dies", 12),
        ["round 177: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 177: a long session ends when the candle dies", 16),
        ["round 177: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 177: a long session ends when the candle dies", 24),
        ["round 177: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 177: a long session ends when the candle dies", 32),
        ["round 177: a long session ends", "when the candle dies"],
    ),
    (
        ("round 177: encode the prompt then map the result", 4),
        ["round", "177:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 177: encode the prompt then map the result", 8),
        ["round", "177:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 177: encode the prompt then map the result", 12),
        ["round 177:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 177: encode the prompt then map the result", 16),
        ["round 177:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 177: encode the prompt then map the result", 24),
        ["round 177: encode the", "prompt then map the", "result"],
    ),
    (("round 177: encode the prompt then map the result", 32), ["round 177: encode the prompt", "then map the result"]),
    (
        ("round 177: the kernel wakes the worker at dawn", 4),
        ["round", "177:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 177: the kernel wakes the worker at dawn", 8),
        ["round", "177: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 177: the kernel wakes the worker at dawn", 12),
        ["round 177:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 177: the kernel wakes the worker at dawn", 16), ["round 177: the", "kernel wakes the", "worker at dawn"]),
    (("round 177: the kernel wakes the worker at dawn", 24), ["round 177: the kernel", "wakes the worker at dawn"]),
    (("round 177: the kernel wakes the worker at dawn", 32), ["round 177: the kernel wakes the", "worker at dawn"]),
    (
        ("round 177: service latency drops after the patch", 4),
        ["round", "177:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 177: service latency drops after the patch", 8),
        ["round", "177:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 177: service latency drops after the patch", 12),
        ["round 177:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 177: service latency drops after the patch", 16),
        ["round 177:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 177: service latency drops after the patch", 24),
        ["round 177: service", "latency drops after the", "patch"],
    ),
    (("round 177: service latency drops after the patch", 32), ["round 177: service latency drops", "after the patch"]),
    (
        ("round 177: the library caches every vector it sees", 4),
        ["round", "177:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 177: the library caches every vector it sees", 8),
        ["round", "177: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 177: the library caches every vector it sees", 12),
        ["round 177:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 177: the library caches every vector it sees", 16),
        ["round 177: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 177: the library caches every vector it sees", 24),
        ["round 177: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 177: the library caches every vector it sees", 32),
        ["round 177: the library caches", "every vector it sees"],
    ),
    (
        ("round 177: agents argue then the debate resolves", 4),
        ["round", "177:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 177: agents argue then the debate resolves", 8),
        ["round", "177:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 177: agents argue then the debate resolves", 12),
        ["round 177:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 177: agents argue then the debate resolves", 16),
        ["round 177:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 177: agents argue then the debate resolves", 24), ["round 177: agents argue", "then the debate resolves"]),
    (("round 177: agents argue then the debate resolves", 32), ["round 177: agents argue then the", "debate resolves"]),
    (
        ("round 177: the filter keeps only strong matches", 4),
        ["round", "177:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 177: the filter keeps only strong matches", 8),
        ["round", "177: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 177: the filter keeps only strong matches", 12),
        ["round 177:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 177: the filter keeps only strong matches", 16),
        ["round 177: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 177: the filter keeps only strong matches", 24),
        ["round 177: the filter", "keeps only strong", "matches"],
    ),
    (("round 177: the filter keeps only strong matches", 32), ["round 177: the filter keeps only", "strong matches"]),
    (
        ("round 177: the model answers with a short reply", 4),
        ["round", "177:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 177: the model answers with a short reply", 8),
        ["round", "177: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 177: the model answers with a short reply", 12),
        ["round 177:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 177: the model answers with a short reply", 16),
        ["round 177: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 177: the model answers with a short reply", 24),
        ["round 177: the model", "answers with a short", "reply"],
    ),
    (("round 177: the model answers with a short reply", 32), ["round 177: the model answers", "with a short reply"]),
    (
        ("round 177: the recorder stores the reasoning trace", 4),
        ["round", "177:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 177: the recorder stores the reasoning trace", 8),
        ["round", "177: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 177: the recorder stores the reasoning trace", 12),
        ["round 177:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 177: the recorder stores the reasoning trace", 16),
        ["round 177: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 177: the recorder stores the reasoning trace", 24),
        ["round 177: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 177: the recorder stores the reasoning trace", 32),
        ["round 177: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 177: the angel watches the processor run", 4),
        ["round", "177:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 177: the angel watches the processor run", 8),
        ["round", "177: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 177: the angel watches the processor run", 12),
        ["round 177:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 177: the angel watches the processor run", 16),
        ["round 177: the", "angel watches", "the processor", "run"],
    ),
    (("round 177: the angel watches the processor run", 24), ["round 177: the angel", "watches the processor", "run"]),
    (("round 177: the angel watches the processor run", 32), ["round 177: the angel watches the", "processor run"]),
    (
        ("round 177: angle of the vector decides the match", 4),
        ["round", "177:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 177: angle of the vector decides the match", 8),
        ["round", "177:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 177: angle of the vector decides the match", 12),
        ["round 177:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 177: angle of the vector decides the match", 16),
        ["round 177: angle", "of the vector", "decides the", "match"],
    ),
    (("round 177: angle of the vector decides the match", 24), ["round 177: angle of the", "vector decides the match"]),
    (("round 177: angle of the vector decides the match", 32), ["round 177: angle of the vector", "decides the match"]),
    (
        ("round 177: the candle burns twice as long at night", 4),
        ["round", "177:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 177: the candle burns twice as long at night", 8),
        ["round", "177: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 177: the candle burns twice as long at night", 12),
        ["round 177:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 177: the candle burns twice as long at night", 16),
        ["round 177: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 177: the candle burns twice as long at night", 24),
        ["round 177: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 177: the candle burns twice as long at night", 32),
        ["round 177: the candle burns", "twice as long at night"],
    ),
    (
        ("round 177: a mirror of the universe in one line", 4),
        ["round", "177:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 177: a mirror of the universe in one line", 8),
        ["round", "177: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 177: a mirror of the universe in one line", 12),
        ["round 177: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 177: a mirror of the universe in one line", 16),
        ["round 177: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 177: a mirror of the universe in one line", 24), ["round 177: a mirror of", "the universe in one line"]),
    (("round 177: a mirror of the universe in one line", 32), ["round 177: a mirror of the", "universe in one line"]),
    (
        ("round 177: the queue drains before the storm", 4),
        ["round", "177:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 177: the queue drains before the storm", 8),
        ["round", "177: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 177: the queue drains before the storm", 12),
        ["round 177:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 177: the queue drains before the storm", 16), ["round 177: the", "queue drains", "before the storm"]),
    (("round 177: the queue drains before the storm", 24), ["round 177: the queue", "drains before the storm"]),
    (("round 177: the queue drains before the storm", 32), ["round 177: the queue drains", "before the storm"]),
    (
        ("kitten177 sitting177 agent177 angle177 universe177 memory177", 6),
        ["kitten177", "sitting177", "agent177", "angle177", "universe177", "memory177"],
    ),
    (
        ("kitten177 sitting177 agent177 angle177 universe177 memory177", 10),
        ["kitten177", "sitting177", "agent177", "angle177", "universe177", "memory177"],
    ),
    (
        ("kitten177 sitting177 agent177 angle177 universe177 memory177", 18),
        ["kitten177", "sitting177", "agent177 angle177", "universe177", "memory177"],
    ),
    (
        ("kitten177 sitting177 agent177 angle177 universe177 memory177", 28),
        ["kitten177 sitting177", "agent177 angle177", "universe177 memory177"],
    ),
    (
        ("sitting177 agent177 angle177 universe177 memory177 stream177", 6),
        ["sitting177", "agent177", "angle177", "universe177", "memory177", "stream177"],
    ),
    (
        ("sitting177 agent177 angle177 universe177 memory177 stream177", 10),
        ["sitting177", "agent177", "angle177", "universe177", "memory177", "stream177"],
    ),
    (
        ("sitting177 agent177 angle177 universe177 memory177 stream177", 18),
        ["sitting177", "agent177 angle177", "universe177", "memory177", "stream177"],
    ),
    (
        ("sitting177 agent177 angle177 universe177 memory177 stream177", 28),
        ["sitting177 agent177 angle177", "universe177 memory177", "stream177"],
    ),
    (
        ("agent177 angle177 universe177 memory177 stream177 context177", 6),
        ["agent177", "angle177", "universe177", "memory177", "stream177", "context177"],
    ),
    (
        ("agent177 angle177 universe177 memory177 stream177 context177", 10),
        ["agent177", "angle177", "universe177", "memory177", "stream177", "context177"],
    ),
    (
        ("agent177 angle177 universe177 memory177 stream177 context177", 18),
        ["agent177 angle177", "universe177", "memory177", "stream177", "context177"],
    ),
    (
        ("agent177 angle177 universe177 memory177 stream177 context177", 28),
        ["agent177 angle177", "universe177 memory177", "stream177 context177"],
    ),
    (
        ("angle177 universe177 memory177 stream177 context177 knowledge177", 6),
        ["angle177", "universe177", "memory177", "stream177", "context177", "knowledge177"],
    ),
    (
        ("angle177 universe177 memory177 stream177 context177 knowledge177", 10),
        ["angle177", "universe177", "memory177", "stream177", "context177", "knowledge177"],
    ),
    (
        ("angle177 universe177 memory177 stream177 context177 knowledge177", 18),
        ["angle177", "universe177", "memory177", "stream177", "context177", "knowledge177"],
    ),
    (
        ("angle177 universe177 memory177 stream177 context177 knowledge177", 28),
        ["angle177 universe177", "memory177 stream177", "context177 knowledge177"],
    ),
    (
        ("universe177 memory177 stream177 context177 knowledge177 vector177", 6),
        ["universe177", "memory177", "stream177", "context177", "knowledge177", "vector177"],
    ),
    (
        ("universe177 memory177 stream177 context177 knowledge177 vector177", 10),
        ["universe177", "memory177", "stream177", "context177", "knowledge177", "vector177"],
    ),
    (
        ("universe177 memory177 stream177 context177 knowledge177 vector177", 18),
        ["universe177", "memory177", "stream177", "context177", "knowledge177", "vector177"],
    ),
    (
        ("universe177 memory177 stream177 context177 knowledge177 vector177", 28),
        ["universe177 memory177", "stream177 context177", "knowledge177 vector177"],
    ),
    (
        ("memory177 stream177 context177 knowledge177 vector177 processor177", 6),
        ["memory177", "stream177", "context177", "knowledge177", "vector177", "processor177"],
    ),
    (
        ("memory177 stream177 context177 knowledge177 vector177 processor177", 10),
        ["memory177", "stream177", "context177", "knowledge177", "vector177", "processor177"],
    ),
    (
        ("memory177 stream177 context177 knowledge177 vector177 processor177", 18),
        ["memory177", "stream177", "context177", "knowledge177", "vector177", "processor177"],
    ),
    (
        ("memory177 stream177 context177 knowledge177 vector177 processor177", 28),
        ["memory177 stream177", "context177 knowledge177", "vector177 processor177"],
    ),
    (
        ("stream177 context177 knowledge177 vector177 processor177 reasoning177", 6),
        ["stream177", "context177", "knowledge177", "vector177", "processor177", "reasoning177"],
    ),
    (
        ("stream177 context177 knowledge177 vector177 processor177 reasoning177", 10),
        ["stream177", "context177", "knowledge177", "vector177", "processor177", "reasoning177"],
    ),
    (
        ("stream177 context177 knowledge177 vector177 processor177 reasoning177", 18),
        ["stream177", "context177", "knowledge177", "vector177", "processor177", "reasoning177"],
    ),
    (
        ("stream177 context177 knowledge177 vector177 processor177 reasoning177", 28),
        ["stream177 context177", "knowledge177 vector177", "processor177 reasoning177"],
    ),
    (
        ("context177 knowledge177 vector177 processor177 reasoning177 machine177", 6),
        ["context177", "knowledge177", "vector177", "processor177", "reasoning177", "machine177"],
    ),
    (
        ("context177 knowledge177 vector177 processor177 reasoning177 machine177", 10),
        ["context177", "knowledge177", "vector177", "processor177", "reasoning177", "machine177"],
    ),
    (
        ("context177 knowledge177 vector177 processor177 reasoning177 machine177", 18),
        ["context177", "knowledge177", "vector177", "processor177", "reasoning177", "machine177"],
    ),
    (
        ("context177 knowledge177 vector177 processor177 reasoning177 machine177", 28),
        ["context177 knowledge177", "vector177 processor177", "reasoning177 machine177"],
    ),
    (
        ("knowledge177 vector177 processor177 reasoning177 machine177 learning177", 6),
        ["knowledge177", "vector177", "processor177", "reasoning177", "machine177", "learning177"],
    ),
    (
        ("knowledge177 vector177 processor177 reasoning177 machine177 learning177", 10),
        ["knowledge177", "vector177", "processor177", "reasoning177", "machine177", "learning177"],
    ),
    (
        ("knowledge177 vector177 processor177 reasoning177 machine177 learning177", 18),
        ["knowledge177", "vector177", "processor177", "reasoning177", "machine177", "learning177"],
    ),
    (
        ("knowledge177 vector177 processor177 reasoning177 machine177 learning177", 28),
        ["knowledge177 vector177", "processor177 reasoning177", "machine177 learning177"],
    ),
    (
        ("vector177 processor177 reasoning177 machine177 learning177 model177", 6),
        ["vector177", "processor177", "reasoning177", "machine177", "learning177", "model177"],
    ),
    (
        ("vector177 processor177 reasoning177 machine177 learning177 model177", 10),
        ["vector177", "processor177", "reasoning177", "machine177", "learning177", "model177"],
    ),
    (
        ("vector177 processor177 reasoning177 machine177 learning177 model177", 18),
        ["vector177", "processor177", "reasoning177", "machine177", "learning177", "model177"],
    ),
    (
        ("vector177 processor177 reasoning177 machine177 learning177 model177", 28),
        ["vector177 processor177", "reasoning177 machine177", "learning177 model177"],
    ),
    (
        ("processor177 reasoning177 machine177 learning177 model177 token177", 6),
        ["processor177", "reasoning177", "machine177", "learning177", "model177", "token177"],
    ),
    (
        ("processor177 reasoning177 machine177 learning177 model177 token177", 10),
        ["processor177", "reasoning177", "machine177", "learning177", "model177", "token177"],
    ),
    (
        ("processor177 reasoning177 machine177 learning177 model177 token177", 18),
        ["processor177", "reasoning177", "machine177", "learning177", "model177 token177"],
    ),
    (
        ("processor177 reasoning177 machine177 learning177 model177 token177", 28),
        ["processor177 reasoning177", "machine177 learning177", "model177 token177"],
    ),
    (
        ("reasoning177 machine177 learning177 model177 token177 prompt177", 6),
        ["reasoning177", "machine177", "learning177", "model177", "token177", "prompt177"],
    ),
    (
        ("reasoning177 machine177 learning177 model177 token177 prompt177", 10),
        ["reasoning177", "machine177", "learning177", "model177", "token177", "prompt177"],
    ),
    (
        ("reasoning177 machine177 learning177 model177 token177 prompt177", 18),
        ["reasoning177", "machine177", "learning177", "model177 token177", "prompt177"],
    ),
    (
        ("reasoning177 machine177 learning177 model177 token177 prompt177", 28),
        ["reasoning177 machine177", "learning177 model177", "token177 prompt177"],
    ),
    (
        ("machine177 learning177 model177 token177 prompt177 session177", 6),
        ["machine177", "learning177", "model177", "token177", "prompt177", "session177"],
    ),
    (
        ("machine177 learning177 model177 token177 prompt177 session177", 10),
        ["machine177", "learning177", "model177", "token177", "prompt177", "session177"],
    ),
    (
        ("machine177 learning177 model177 token177 prompt177 session177", 18),
        ["machine177", "learning177", "model177 token177", "prompt177", "session177"],
    ),
    (
        ("machine177 learning177 model177 token177 prompt177 session177", 28),
        ["machine177 learning177", "model177 token177 prompt177", "session177"],
    ),
    (
        ("learning177 model177 token177 prompt177 session177 library177", 6),
        ["learning177", "model177", "token177", "prompt177", "session177", "library177"],
    ),
    (
        ("learning177 model177 token177 prompt177 session177 library177", 10),
        ["learning177", "model177", "token177", "prompt177", "session177", "library177"],
    ),
    (
        ("learning177 model177 token177 prompt177 session177 library177", 18),
        ["learning177", "model177 token177", "prompt177", "session177", "library177"],
    ),
    (
        ("learning177 model177 token177 prompt177 session177 library177", 28),
        ["learning177 model177", "token177 prompt177", "session177 library177"],
    ),
    (
        ("model177 token177 prompt177 session177 library177 service177", 6),
        ["model177", "token177", "prompt177", "session177", "library177", "service177"],
    ),
    (
        ("model177 token177 prompt177 session177 library177 service177", 10),
        ["model177", "token177", "prompt177", "session177", "library177", "service177"],
    ),
    (
        ("model177 token177 prompt177 session177 library177 service177", 18),
        ["model177 token177", "prompt177", "session177", "library177", "service177"],
    ),
    (
        ("model177 token177 prompt177 session177 library177 service177", 28),
        ["model177 token177 prompt177", "session177 library177", "service177"],
    ),
    (
        ("token177 prompt177 session177 library177 service177 gateway177", 6),
        ["token177", "prompt177", "session177", "library177", "service177", "gateway177"],
    ),
    (
        ("token177 prompt177 session177 library177 service177 gateway177", 10),
        ["token177", "prompt177", "session177", "library177", "service177", "gateway177"],
    ),
    (
        ("token177 prompt177 session177 library177 service177 gateway177", 18),
        ["token177 prompt177", "session177", "library177", "service177", "gateway177"],
    ),
    (
        ("token177 prompt177 session177 library177 service177 gateway177", 28),
        ["token177 prompt177", "session177 library177", "service177 gateway177"],
    ),
    (
        ("prompt177 session177 library177 service177 gateway177 storage177", 6),
        ["prompt177", "session177", "library177", "service177", "gateway177", "storage177"],
    ),
    (
        ("prompt177 session177 library177 service177 gateway177 storage177", 10),
        ["prompt177", "session177", "library177", "service177", "gateway177", "storage177"],
    ),
    (
        ("prompt177 session177 library177 service177 gateway177 storage177", 18),
        ["prompt177", "session177", "library177", "service177", "gateway177", "storage177"],
    ),
    (
        ("prompt177 session177 library177 service177 gateway177 storage177", 28),
        ["prompt177 session177", "library177 service177", "gateway177 storage177"],
    ),
    (
        ("session177 library177 service177 gateway177 storage177 network177", 6),
        ["session177", "library177", "service177", "gateway177", "storage177", "network177"],
    ),
    (
        ("session177 library177 service177 gateway177 storage177 network177", 10),
        ["session177", "library177", "service177", "gateway177", "storage177", "network177"],
    ),
    (
        ("session177 library177 service177 gateway177 storage177 network177", 18),
        ["session177", "library177", "service177", "gateway177", "storage177", "network177"],
    ),
    (
        ("session177 library177 service177 gateway177 storage177 network177", 28),
        ["session177 library177", "service177 gateway177", "storage177 network177"],
    ),
    (
        ("library177 service177 gateway177 storage177 network177 latency177", 6),
        ["library177", "service177", "gateway177", "storage177", "network177", "latency177"],
    ),
    (
        ("library177 service177 gateway177 storage177 network177 latency177", 10),
        ["library177", "service177", "gateway177", "storage177", "network177", "latency177"],
    ),
    (
        ("library177 service177 gateway177 storage177 network177 latency177", 18),
        ["library177", "service177", "gateway177", "storage177", "network177", "latency177"],
    ),
    (
        ("library177 service177 gateway177 storage177 network177 latency177", 28),
        ["library177 service177", "gateway177 storage177", "network177 latency177"],
    ),
    (
        ("service177 gateway177 storage177 network177 latency177 buffer177", 6),
        ["service177", "gateway177", "storage177", "network177", "latency177", "buffer177"],
    ),
    (
        ("service177 gateway177 storage177 network177 latency177 buffer177", 10),
        ["service177", "gateway177", "storage177", "network177", "latency177", "buffer177"],
    ),
    (
        ("service177 gateway177 storage177 network177 latency177 buffer177", 18),
        ["service177", "gateway177", "storage177", "network177", "latency177", "buffer177"],
    ),
    (
        ("service177 gateway177 storage177 network177 latency177 buffer177", 28),
        ["service177 gateway177", "storage177 network177", "latency177 buffer177"],
    ),
    (
        ("gateway177 storage177 network177 latency177 buffer177 queue177", 6),
        ["gateway177", "storage177", "network177", "latency177", "buffer177", "queue177"],
    ),
    (
        ("gateway177 storage177 network177 latency177 buffer177 queue177", 10),
        ["gateway177", "storage177", "network177", "latency177", "buffer177", "queue177"],
    ),
    (
        ("gateway177 storage177 network177 latency177 buffer177 queue177", 18),
        ["gateway177", "storage177", "network177", "latency177", "buffer177 queue177"],
    ),
    (
        ("gateway177 storage177 network177 latency177 buffer177 queue177", 28),
        ["gateway177 storage177", "network177 latency177", "buffer177 queue177"],
    ),
    (
        ("storage177 network177 latency177 buffer177 queue177 worker177", 6),
        ["storage177", "network177", "latency177", "buffer177", "queue177", "worker177"],
    ),
    (
        ("storage177 network177 latency177 buffer177 queue177 worker177", 10),
        ["storage177", "network177", "latency177", "buffer177", "queue177", "worker177"],
    ),
    (
        ("storage177 network177 latency177 buffer177 queue177 worker177", 18),
        ["storage177", "network177", "latency177", "buffer177 queue177", "worker177"],
    ),
    (
        ("storage177 network177 latency177 buffer177 queue177 worker177", 28),
        ["storage177 network177", "latency177 buffer177", "queue177 worker177"],
    ),
    (
        ("network177 latency177 buffer177 queue177 worker177 kernel177", 6),
        ["network177", "latency177", "buffer177", "queue177", "worker177", "kernel177"],
    ),
    (
        ("network177 latency177 buffer177 queue177 worker177 kernel177", 10),
        ["network177", "latency177", "buffer177", "queue177", "worker177", "kernel177"],
    ),
    (
        ("network177 latency177 buffer177 queue177 worker177 kernel177", 18),
        ["network177", "latency177", "buffer177 queue177", "worker177", "kernel177"],
    ),
    (
        ("network177 latency177 buffer177 queue177 worker177 kernel177", 28),
        ["network177 latency177", "buffer177 queue177 worker177", "kernel177"],
    ),
    (
        ("latency177 buffer177 queue177 worker177 kernel177 signal177", 6),
        ["latency177", "buffer177", "queue177", "worker177", "kernel177", "signal177"],
    ),
    (
        ("latency177 buffer177 queue177 worker177 kernel177 signal177", 10),
        ["latency177", "buffer177", "queue177", "worker177", "kernel177", "signal177"],
    ),
    (
        ("latency177 buffer177 queue177 worker177 kernel177 signal177", 18),
        ["latency177", "buffer177 queue177", "worker177", "kernel177", "signal177"],
    ),
    (
        ("latency177 buffer177 queue177 worker177 kernel177 signal177", 28),
        ["latency177 buffer177", "queue177 worker177 kernel177", "signal177"],
    ),
    (
        ("buffer177 queue177 worker177 kernel177 signal177 packet177", 6),
        ["buffer177", "queue177", "worker177", "kernel177", "signal177", "packet177"],
    ),
    (
        ("buffer177 queue177 worker177 kernel177 signal177 packet177", 10),
        ["buffer177", "queue177", "worker177", "kernel177", "signal177", "packet177"],
    ),
    (
        ("buffer177 queue177 worker177 kernel177 signal177 packet177", 18),
        ["buffer177 queue177", "worker177", "kernel177", "signal177", "packet177"],
    ),
    (
        ("buffer177 queue177 worker177 kernel177 signal177 packet177", 28),
        ["buffer177 queue177 worker177", "kernel177 signal177", "packet177"],
    ),
    (
        ("queue177 worker177 kernel177 signal177 packet177 router177", 6),
        ["queue177", "worker177", "kernel177", "signal177", "packet177", "router177"],
    ),
    (
        ("queue177 worker177 kernel177 signal177 packet177 router177", 10),
        ["queue177", "worker177", "kernel177", "signal177", "packet177", "router177"],
    ),
    (
        ("queue177 worker177 kernel177 signal177 packet177 router177", 18),
        ["queue177 worker177", "kernel177", "signal177", "packet177", "router177"],
    ),
    (
        ("queue177 worker177 kernel177 signal177 packet177 router177", 28),
        ["queue177 worker177 kernel177", "signal177 packet177", "router177"],
    ),
    (
        ("worker177 kernel177 signal177 packet177 router177 cluster177", 6),
        ["worker177", "kernel177", "signal177", "packet177", "router177", "cluster177"],
    ),
    (
        ("worker177 kernel177 signal177 packet177 router177 cluster177", 10),
        ["worker177", "kernel177", "signal177", "packet177", "router177", "cluster177"],
    ),
    (
        ("worker177 kernel177 signal177 packet177 router177 cluster177", 18),
        ["worker177", "kernel177", "signal177", "packet177", "router177", "cluster177"],
    ),
    (
        ("worker177 kernel177 signal177 packet177 router177 cluster177", 28),
        ["worker177 kernel177", "signal177 packet177", "router177 cluster177"],
    ),
    (
        ("kernel177 signal177 packet177 router177 cluster177 mirror177", 6),
        ["kernel177", "signal177", "packet177", "router177", "cluster177", "mirror177"],
    ),
    (
        ("kernel177 signal177 packet177 router177 cluster177 mirror177", 10),
        ["kernel177", "signal177", "packet177", "router177", "cluster177", "mirror177"],
    ),
    (
        ("kernel177 signal177 packet177 router177 cluster177 mirror177", 18),
        ["kernel177", "signal177", "packet177", "router177", "cluster177", "mirror177"],
    ),
    (
        ("kernel177 signal177 packet177 router177 cluster177 mirror177", 28),
        ["kernel177 signal177", "packet177 router177", "cluster177 mirror177"],
    ),
    (
        ("signal177 packet177 router177 cluster177 mirror177 filter177", 6),
        ["signal177", "packet177", "router177", "cluster177", "mirror177", "filter177"],
    ),
    (
        ("signal177 packet177 router177 cluster177 mirror177 filter177", 10),
        ["signal177", "packet177", "router177", "cluster177", "mirror177", "filter177"],
    ),
    (
        ("signal177 packet177 router177 cluster177 mirror177 filter177", 18),
        ["signal177", "packet177", "router177", "cluster177", "mirror177", "filter177"],
    ),
    (
        ("signal177 packet177 router177 cluster177 mirror177 filter177", 28),
        ["signal177 packet177", "router177 cluster177", "mirror177 filter177"],
    ),
    (
        ("packet177 router177 cluster177 mirror177 filter177 ranking177", 6),
        ["packet177", "router177", "cluster177", "mirror177", "filter177", "ranking177"],
    ),
    (
        ("packet177 router177 cluster177 mirror177 filter177 ranking177", 10),
        ["packet177", "router177", "cluster177", "mirror177", "filter177", "ranking177"],
    ),
    (
        ("packet177 router177 cluster177 mirror177 filter177 ranking177", 18),
        ["packet177", "router177", "cluster177", "mirror177", "filter177", "ranking177"],
    ),
    (
        ("packet177 router177 cluster177 mirror177 filter177 ranking177", 28),
        ["packet177 router177", "cluster177 mirror177", "filter177 ranking177"],
    ),
    (
        ("router177 cluster177 mirror177 filter177 ranking177 encoding177", 6),
        ["router177", "cluster177", "mirror177", "filter177", "ranking177", "encoding177"],
    ),
    (
        ("router177 cluster177 mirror177 filter177 ranking177 encoding177", 10),
        ["router177", "cluster177", "mirror177", "filter177", "ranking177", "encoding177"],
    ),
    (
        ("router177 cluster177 mirror177 filter177 ranking177 encoding177", 18),
        ["router177", "cluster177", "mirror177", "filter177", "ranking177", "encoding177"],
    ),
    (
        ("router177 cluster177 mirror177 filter177 ranking177 encoding177", 28),
        ["router177 cluster177", "mirror177 filter177", "ranking177 encoding177"],
    ),
    (
        ("cluster177 mirror177 filter177 ranking177 encoding177 mapping177", 6),
        ["cluster177", "mirror177", "filter177", "ranking177", "encoding177", "mapping177"],
    ),
    (
        ("cluster177 mirror177 filter177 ranking177 encoding177 mapping177", 10),
        ["cluster177", "mirror177", "filter177", "ranking177", "encoding177", "mapping177"],
    ),
    (
        ("cluster177 mirror177 filter177 ranking177 encoding177 mapping177", 18),
        ["cluster177", "mirror177", "filter177", "ranking177", "encoding177", "mapping177"],
    ),
    (
        ("cluster177 mirror177 filter177 ranking177 encoding177 mapping177", 28),
        ["cluster177 mirror177", "filter177 ranking177", "encoding177 mapping177"],
    ),
    (
        ("mirror177 filter177 ranking177 encoding177 mapping177 record177", 6),
        ["mirror177", "filter177", "ranking177", "encoding177", "mapping177", "record177"],
    ),
    (
        ("mirror177 filter177 ranking177 encoding177 mapping177 record177", 10),
        ["mirror177", "filter177", "ranking177", "encoding177", "mapping177", "record177"],
    ),
    (
        ("mirror177 filter177 ranking177 encoding177 mapping177 record177", 18),
        ["mirror177", "filter177", "ranking177", "encoding177", "mapping177", "record177"],
    ),
    (
        ("mirror177 filter177 ranking177 encoding177 mapping177 record177", 28),
        ["mirror177 filter177", "ranking177 encoding177", "mapping177 record177"],
    ),
    (
        ("filter177 ranking177 encoding177 mapping177 record177 candle177", 6),
        ["filter177", "ranking177", "encoding177", "mapping177", "record177", "candle177"],
    ),
    (
        ("filter177 ranking177 encoding177 mapping177 record177 candle177", 10),
        ["filter177", "ranking177", "encoding177", "mapping177", "record177", "candle177"],
    ),
    (
        ("filter177 ranking177 encoding177 mapping177 record177 candle177", 18),
        ["filter177", "ranking177", "encoding177", "mapping177", "record177", "candle177"],
    ),
    (
        ("filter177 ranking177 encoding177 mapping177 record177 candle177", 28),
        ["filter177 ranking177", "encoding177 mapping177", "record177 candle177"],
    ),
    (
        ("ranking177 encoding177 mapping177 record177 candle177 thread177", 6),
        ["ranking177", "encoding177", "mapping177", "record177", "candle177", "thread177"],
    ),
    (
        ("ranking177 encoding177 mapping177 record177 candle177 thread177", 10),
        ["ranking177", "encoding177", "mapping177", "record177", "candle177", "thread177"],
    ),
    (
        ("ranking177 encoding177 mapping177 record177 candle177 thread177", 18),
        ["ranking177", "encoding177", "mapping177", "record177", "candle177", "thread177"],
    ),
    (
        ("ranking177 encoding177 mapping177 record177 candle177 thread177", 28),
        ["ranking177 encoding177", "mapping177 record177", "candle177 thread177"],
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
