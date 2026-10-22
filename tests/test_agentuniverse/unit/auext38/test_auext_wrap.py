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
        ("round 38: the quick brown fox jumps over the lazy dog", 4),
        ["round", "38:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 38: the quick brown fox jumps over the lazy dog", 8),
        ["round", "38: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 38: the quick brown fox jumps over the lazy dog", 12),
        ["round 38:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 38: the quick brown fox jumps over the lazy dog", 16),
        ["round 38: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 38: the quick brown fox jumps over the lazy dog", 24),
        ["round 38: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 38: the quick brown fox jumps over the lazy dog", 32),
        ["round 38: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 38: agentuniverse is a framework for multi agents", 4),
        ["round", "38:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 38: agentuniverse is a framework for multi agents", 8),
        ["round", "38:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 38: agentuniverse is a framework for multi agents", 12),
        ["round 38:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 38: agentuniverse is a framework for multi agents", 16),
        ["round 38:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 38: agentuniverse is a framework for multi agents", 24),
        ["round 38: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 38: agentuniverse is a framework for multi agents", 32),
        ["round 38: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 38: knowledge stored as vectors enables retrieval", 4),
        ["round", "38:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 38: knowledge stored as vectors enables retrieval", 8),
        ["round", "38:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 38: knowledge stored as vectors enables retrieval", 12),
        ["round 38:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 38: knowledge stored as vectors enables retrieval", 16),
        ["round 38:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 38: knowledge stored as vectors enables retrieval", 24),
        ["round 38: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 38: knowledge stored as vectors enables retrieval", 32),
        ["round 38: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 38: the processor reads the record then stops", 4),
        ["round", "38:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 38: the processor reads the record then stops", 8),
        ["round", "38: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 38: the processor reads the record then stops", 12),
        ["round 38:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 38: the processor reads the record then stops", 16),
        ["round 38: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 38: the processor reads the record then stops", 24),
        ["round 38: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 38: the processor reads the record then stops", 32),
        ["round 38: the processor reads", "the record then stops"],
    ),
    (
        ("round 38: a worker pulls the next task from the queue", 4),
        ["round", "38:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 38: a worker pulls the next task from the queue", 8),
        ["round", "38: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 38: a worker pulls the next task from the queue", 12),
        ["round 38: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 38: a worker pulls the next task from the queue", 16),
        ["round 38: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 38: a worker pulls the next task from the queue", 24),
        ["round 38: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 38: a worker pulls the next task from the queue", 32),
        ["round 38: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 38: signals travel through the network layer", 4),
        ["round", "38:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 38: signals travel through the network layer", 8),
        ["round", "38:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 38: signals travel through the network layer", 12),
        ["round 38:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 38: signals travel through the network layer", 16),
        ["round 38:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 38: signals travel through the network layer", 24),
        ["round 38: signals travel", "through the network", "layer"],
    ),
    (
        ("round 38: signals travel through the network layer", 32),
        ["round 38: signals travel through", "the network layer"],
    ),
    (
        ("round 38: the gateway routes each request by policy", 4),
        ["round", "38:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 38: the gateway routes each request by policy", 8),
        ["round", "38: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 38: the gateway routes each request by policy", 12),
        ["round 38:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 38: the gateway routes each request by policy", 16),
        ["round 38: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 38: the gateway routes each request by policy", 24),
        ["round 38: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 38: the gateway routes each request by policy", 32),
        ["round 38: the gateway routes", "each request by policy"],
    ),
    (
        ("round 38: memory grows until the buffer is full", 4),
        ["round", "38:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 38: memory grows until the buffer is full", 8),
        ["round", "38:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 38: memory grows until the buffer is full", 12),
        ["round 38:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 38: memory grows until the buffer is full", 16),
        ["round 38: memory", "grows until the", "buffer is full"],
    ),
    (("round 38: memory grows until the buffer is full", 24), ["round 38: memory grows", "until the buffer is full"]),
    (("round 38: memory grows until the buffer is full", 32), ["round 38: memory grows until the", "buffer is full"]),
    (
        ("round 38: the cluster mirrors every packet twice", 4),
        ["round", "38:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 38: the cluster mirrors every packet twice", 8),
        ["round", "38: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 38: the cluster mirrors every packet twice", 12),
        ["round 38:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 38: the cluster mirrors every packet twice", 16),
        ["round 38: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 38: the cluster mirrors every packet twice", 24),
        ["round 38: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 38: the cluster mirrors every packet twice", 32), ["round 38: the cluster mirrors", "every packet twice"]),
    (
        ("round 38: ranking uses tokens learned from the corpus", 4),
        ["round", "38:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 38: ranking uses tokens learned from the corpus", 8),
        ["round", "38:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 38: ranking uses tokens learned from the corpus", 12),
        ["round 38:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 38: ranking uses tokens learned from the corpus", 16),
        ["round 38:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 38: ranking uses tokens learned from the corpus", 24),
        ["round 38: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 38: ranking uses tokens learned from the corpus", 32),
        ["round 38: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 38: a long session ends when the candle dies", 4),
        ["round", "38:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 38: a long session ends when the candle dies", 8),
        ["round", "38: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 38: a long session ends when the candle dies", 12),
        ["round 38: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 38: a long session ends when the candle dies", 16),
        ["round 38: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 38: a long session ends when the candle dies", 24),
        ["round 38: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 38: a long session ends when the candle dies", 32),
        ["round 38: a long session ends", "when the candle dies"],
    ),
    (
        ("round 38: encode the prompt then map the result", 4),
        ["round", "38:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 38: encode the prompt then map the result", 8),
        ["round", "38:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 38: encode the prompt then map the result", 12),
        ["round 38:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 38: encode the prompt then map the result", 16),
        ["round 38: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 38: encode the prompt then map the result", 24),
        ["round 38: encode the", "prompt then map the", "result"],
    ),
    (("round 38: encode the prompt then map the result", 32), ["round 38: encode the prompt then", "map the result"]),
    (
        ("round 38: the kernel wakes the worker at dawn", 4),
        ["round", "38:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 38: the kernel wakes the worker at dawn", 8),
        ["round", "38: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 38: the kernel wakes the worker at dawn", 12),
        ["round 38:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 38: the kernel wakes the worker at dawn", 16), ["round 38: the", "kernel wakes the", "worker at dawn"]),
    (("round 38: the kernel wakes the worker at dawn", 24), ["round 38: the kernel", "wakes the worker at dawn"]),
    (("round 38: the kernel wakes the worker at dawn", 32), ["round 38: the kernel wakes the", "worker at dawn"]),
    (
        ("round 38: service latency drops after the patch", 4),
        ["round", "38:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 38: service latency drops after the patch", 8),
        ["round", "38:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 38: service latency drops after the patch", 12),
        ["round 38:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 38: service latency drops after the patch", 16),
        ["round 38:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 38: service latency drops after the patch", 24),
        ["round 38: service", "latency drops after the", "patch"],
    ),
    (("round 38: service latency drops after the patch", 32), ["round 38: service latency drops", "after the patch"]),
    (
        ("round 38: the library caches every vector it sees", 4),
        ["round", "38:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 38: the library caches every vector it sees", 8),
        ["round", "38: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 38: the library caches every vector it sees", 12),
        ["round 38:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 38: the library caches every vector it sees", 16),
        ["round 38: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 38: the library caches every vector it sees", 24),
        ["round 38: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 38: the library caches every vector it sees", 32),
        ["round 38: the library caches", "every vector it sees"],
    ),
    (
        ("round 38: agents argue then the debate resolves", 4),
        ["round", "38:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 38: agents argue then the debate resolves", 8),
        ["round", "38:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 38: agents argue then the debate resolves", 12),
        ["round 38:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 38: agents argue then the debate resolves", 16),
        ["round 38: agents", "argue then the", "debate resolves"],
    ),
    (("round 38: agents argue then the debate resolves", 24), ["round 38: agents argue", "then the debate resolves"]),
    (("round 38: agents argue then the debate resolves", 32), ["round 38: agents argue then the", "debate resolves"]),
    (
        ("round 38: the filter keeps only strong matches", 4),
        ["round", "38:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 38: the filter keeps only strong matches", 8),
        ["round", "38: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 38: the filter keeps only strong matches", 12),
        ["round 38:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 38: the filter keeps only strong matches", 16),
        ["round 38: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 38: the filter keeps only strong matches", 24), ["round 38: the filter", "keeps only strong", "matches"]),
    (("round 38: the filter keeps only strong matches", 32), ["round 38: the filter keeps only", "strong matches"]),
    (
        ("round 38: the model answers with a short reply", 4),
        ["round", "38:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 38: the model answers with a short reply", 8),
        ["round", "38: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 38: the model answers with a short reply", 12),
        ["round 38:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 38: the model answers with a short reply", 16),
        ["round 38: the", "model answers", "with a short", "reply"],
    ),
    (("round 38: the model answers with a short reply", 24), ["round 38: the model", "answers with a short", "reply"]),
    (("round 38: the model answers with a short reply", 32), ["round 38: the model answers with", "a short reply"]),
    (
        ("round 38: the recorder stores the reasoning trace", 4),
        ["round", "38:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 38: the recorder stores the reasoning trace", 8),
        ["round", "38: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 38: the recorder stores the reasoning trace", 12),
        ["round 38:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 38: the recorder stores the reasoning trace", 16),
        ["round 38: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 38: the recorder stores the reasoning trace", 24),
        ["round 38: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 38: the recorder stores the reasoning trace", 32),
        ["round 38: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 38: the angel watches the processor run", 4),
        ["round", "38:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 38: the angel watches the processor run", 8),
        ["round", "38: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 38: the angel watches the processor run", 12),
        ["round 38:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 38: the angel watches the processor run", 16), ["round 38: the", "angel watches", "the processor", "run"]),
    (("round 38: the angel watches the processor run", 24), ["round 38: the angel", "watches the processor", "run"]),
    (("round 38: the angel watches the processor run", 32), ["round 38: the angel watches the", "processor run"]),
    (
        ("round 38: angle of the vector decides the match", 4),
        ["round", "38:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 38: angle of the vector decides the match", 8),
        ["round", "38:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 38: angle of the vector decides the match", 12),
        ["round 38:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 38: angle of the vector decides the match", 16),
        ["round 38: angle", "of the vector", "decides the", "match"],
    ),
    (("round 38: angle of the vector decides the match", 24), ["round 38: angle of the", "vector decides the match"]),
    (("round 38: angle of the vector decides the match", 32), ["round 38: angle of the vector", "decides the match"]),
    (
        ("round 38: the candle burns twice as long at night", 4),
        ["round", "38:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 38: the candle burns twice as long at night", 8),
        ["round", "38: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 38: the candle burns twice as long at night", 12),
        ["round 38:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 38: the candle burns twice as long at night", 16),
        ["round 38: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 38: the candle burns twice as long at night", 24),
        ["round 38: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 38: the candle burns twice as long at night", 32),
        ["round 38: the candle burns twice", "as long at night"],
    ),
    (
        ("round 38: a mirror of the universe in one line", 4),
        ["round", "38:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 38: a mirror of the universe in one line", 8),
        ["round", "38: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 38: a mirror of the universe in one line", 12),
        ["round 38: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 38: a mirror of the universe in one line", 16),
        ["round 38: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 38: a mirror of the universe in one line", 24), ["round 38: a mirror of", "the universe in one line"]),
    (("round 38: a mirror of the universe in one line", 32), ["round 38: a mirror of the", "universe in one line"]),
    (
        ("round 38: the queue drains before the storm", 4),
        ["round", "38:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 38: the queue drains before the storm", 8),
        ["round", "38: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 38: the queue drains before the storm", 12), ["round 38:", "the queue", "drains", "before the", "storm"]),
    (("round 38: the queue drains before the storm", 16), ["round 38: the", "queue drains", "before the storm"]),
    (("round 38: the queue drains before the storm", 24), ["round 38: the queue", "drains before the storm"]),
    (("round 38: the queue drains before the storm", 32), ["round 38: the queue drains", "before the storm"]),
    (
        ("kitten38 sitting38 agent38 angle38 universe38 memory38", 6),
        ["kitten38", "sitting38", "agent38", "angle38", "universe38", "memory38"],
    ),
    (
        ("kitten38 sitting38 agent38 angle38 universe38 memory38", 10),
        ["kitten38", "sitting38", "agent38", "angle38", "universe38", "memory38"],
    ),
    (
        ("kitten38 sitting38 agent38 angle38 universe38 memory38", 18),
        ["kitten38 sitting38", "agent38 angle38", "universe38", "memory38"],
    ),
    (
        ("kitten38 sitting38 agent38 angle38 universe38 memory38", 28),
        ["kitten38 sitting38 agent38", "angle38 universe38 memory38"],
    ),
    (
        ("sitting38 agent38 angle38 universe38 memory38 stream38", 6),
        ["sitting38", "agent38", "angle38", "universe38", "memory38", "stream38"],
    ),
    (
        ("sitting38 agent38 angle38 universe38 memory38 stream38", 10),
        ["sitting38", "agent38", "angle38", "universe38", "memory38", "stream38"],
    ),
    (
        ("sitting38 agent38 angle38 universe38 memory38 stream38", 18),
        ["sitting38 agent38", "angle38 universe38", "memory38 stream38"],
    ),
    (
        ("sitting38 agent38 angle38 universe38 memory38 stream38", 28),
        ["sitting38 agent38 angle38", "universe38 memory38 stream38"],
    ),
    (
        ("agent38 angle38 universe38 memory38 stream38 context38", 6),
        ["agent38", "angle38", "universe38", "memory38", "stream38", "context38"],
    ),
    (
        ("agent38 angle38 universe38 memory38 stream38 context38", 10),
        ["agent38", "angle38", "universe38", "memory38", "stream38", "context38"],
    ),
    (
        ("agent38 angle38 universe38 memory38 stream38 context38", 18),
        ["agent38 angle38", "universe38", "memory38 stream38", "context38"],
    ),
    (
        ("agent38 angle38 universe38 memory38 stream38 context38", 28),
        ["agent38 angle38 universe38", "memory38 stream38 context38"],
    ),
    (
        ("angle38 universe38 memory38 stream38 context38 knowledge38", 6),
        ["angle38", "universe38", "memory38", "stream38", "context38", "knowledge38"],
    ),
    (
        ("angle38 universe38 memory38 stream38 context38 knowledge38", 10),
        ["angle38", "universe38", "memory38", "stream38", "context38", "knowledge38"],
    ),
    (
        ("angle38 universe38 memory38 stream38 context38 knowledge38", 18),
        ["angle38 universe38", "memory38 stream38", "context38", "knowledge38"],
    ),
    (
        ("angle38 universe38 memory38 stream38 context38 knowledge38", 28),
        ["angle38 universe38 memory38", "stream38 context38", "knowledge38"],
    ),
    (
        ("universe38 memory38 stream38 context38 knowledge38 vector38", 6),
        ["universe38", "memory38", "stream38", "context38", "knowledge38", "vector38"],
    ),
    (
        ("universe38 memory38 stream38 context38 knowledge38 vector38", 10),
        ["universe38", "memory38", "stream38", "context38", "knowledge38", "vector38"],
    ),
    (
        ("universe38 memory38 stream38 context38 knowledge38 vector38", 18),
        ["universe38", "memory38 stream38", "context38", "knowledge38", "vector38"],
    ),
    (
        ("universe38 memory38 stream38 context38 knowledge38 vector38", 28),
        ["universe38 memory38 stream38", "context38 knowledge38", "vector38"],
    ),
    (
        ("memory38 stream38 context38 knowledge38 vector38 processor38", 6),
        ["memory38", "stream38", "context38", "knowledge38", "vector38", "processor38"],
    ),
    (
        ("memory38 stream38 context38 knowledge38 vector38 processor38", 10),
        ["memory38", "stream38", "context38", "knowledge38", "vector38", "processor38"],
    ),
    (
        ("memory38 stream38 context38 knowledge38 vector38 processor38", 18),
        ["memory38 stream38", "context38", "knowledge38", "vector38", "processor38"],
    ),
    (
        ("memory38 stream38 context38 knowledge38 vector38 processor38", 28),
        ["memory38 stream38 context38", "knowledge38 vector38", "processor38"],
    ),
    (
        ("stream38 context38 knowledge38 vector38 processor38 reasoning38", 6),
        ["stream38", "context38", "knowledge38", "vector38", "processor38", "reasoning38"],
    ),
    (
        ("stream38 context38 knowledge38 vector38 processor38 reasoning38", 10),
        ["stream38", "context38", "knowledge38", "vector38", "processor38", "reasoning38"],
    ),
    (
        ("stream38 context38 knowledge38 vector38 processor38 reasoning38", 18),
        ["stream38 context38", "knowledge38", "vector38", "processor38", "reasoning38"],
    ),
    (
        ("stream38 context38 knowledge38 vector38 processor38 reasoning38", 28),
        ["stream38 context38", "knowledge38 vector38", "processor38 reasoning38"],
    ),
    (
        ("context38 knowledge38 vector38 processor38 reasoning38 machine38", 6),
        ["context38", "knowledge38", "vector38", "processor38", "reasoning38", "machine38"],
    ),
    (
        ("context38 knowledge38 vector38 processor38 reasoning38 machine38", 10),
        ["context38", "knowledge38", "vector38", "processor38", "reasoning38", "machine38"],
    ),
    (
        ("context38 knowledge38 vector38 processor38 reasoning38 machine38", 18),
        ["context38", "knowledge38", "vector38", "processor38", "reasoning38", "machine38"],
    ),
    (
        ("context38 knowledge38 vector38 processor38 reasoning38 machine38", 28),
        ["context38 knowledge38", "vector38 processor38", "reasoning38 machine38"],
    ),
    (
        ("knowledge38 vector38 processor38 reasoning38 machine38 learning38", 6),
        ["knowledge38", "vector38", "processor38", "reasoning38", "machine38", "learning38"],
    ),
    (
        ("knowledge38 vector38 processor38 reasoning38 machine38 learning38", 10),
        ["knowledge38", "vector38", "processor38", "reasoning38", "machine38", "learning38"],
    ),
    (
        ("knowledge38 vector38 processor38 reasoning38 machine38 learning38", 18),
        ["knowledge38", "vector38", "processor38", "reasoning38", "machine38", "learning38"],
    ),
    (
        ("knowledge38 vector38 processor38 reasoning38 machine38 learning38", 28),
        ["knowledge38 vector38", "processor38 reasoning38", "machine38 learning38"],
    ),
    (
        ("vector38 processor38 reasoning38 machine38 learning38 model38", 6),
        ["vector38", "processor38", "reasoning38", "machine38", "learning38", "model38"],
    ),
    (
        ("vector38 processor38 reasoning38 machine38 learning38 model38", 10),
        ["vector38", "processor38", "reasoning38", "machine38", "learning38", "model38"],
    ),
    (
        ("vector38 processor38 reasoning38 machine38 learning38 model38", 18),
        ["vector38", "processor38", "reasoning38", "machine38", "learning38 model38"],
    ),
    (
        ("vector38 processor38 reasoning38 machine38 learning38 model38", 28),
        ["vector38 processor38", "reasoning38 machine38", "learning38 model38"],
    ),
    (
        ("processor38 reasoning38 machine38 learning38 model38 token38", 6),
        ["processor38", "reasoning38", "machine38", "learning38", "model38", "token38"],
    ),
    (
        ("processor38 reasoning38 machine38 learning38 model38 token38", 10),
        ["processor38", "reasoning38", "machine38", "learning38", "model38", "token38"],
    ),
    (
        ("processor38 reasoning38 machine38 learning38 model38 token38", 18),
        ["processor38", "reasoning38", "machine38", "learning38 model38", "token38"],
    ),
    (
        ("processor38 reasoning38 machine38 learning38 model38 token38", 28),
        ["processor38 reasoning38", "machine38 learning38 model38", "token38"],
    ),
    (
        ("reasoning38 machine38 learning38 model38 token38 prompt38", 6),
        ["reasoning38", "machine38", "learning38", "model38", "token38", "prompt38"],
    ),
    (
        ("reasoning38 machine38 learning38 model38 token38 prompt38", 10),
        ["reasoning38", "machine38", "learning38", "model38", "token38", "prompt38"],
    ),
    (
        ("reasoning38 machine38 learning38 model38 token38 prompt38", 18),
        ["reasoning38", "machine38", "learning38 model38", "token38 prompt38"],
    ),
    (
        ("reasoning38 machine38 learning38 model38 token38 prompt38", 28),
        ["reasoning38 machine38", "learning38 model38 token38", "prompt38"],
    ),
    (
        ("machine38 learning38 model38 token38 prompt38 session38", 6),
        ["machine38", "learning38", "model38", "token38", "prompt38", "session38"],
    ),
    (
        ("machine38 learning38 model38 token38 prompt38 session38", 10),
        ["machine38", "learning38", "model38", "token38", "prompt38", "session38"],
    ),
    (
        ("machine38 learning38 model38 token38 prompt38 session38", 18),
        ["machine38", "learning38 model38", "token38 prompt38", "session38"],
    ),
    (
        ("machine38 learning38 model38 token38 prompt38 session38", 28),
        ["machine38 learning38 model38", "token38 prompt38 session38"],
    ),
    (
        ("learning38 model38 token38 prompt38 session38 library38", 6),
        ["learning38", "model38", "token38", "prompt38", "session38", "library38"],
    ),
    (
        ("learning38 model38 token38 prompt38 session38 library38", 10),
        ["learning38", "model38", "token38", "prompt38", "session38", "library38"],
    ),
    (
        ("learning38 model38 token38 prompt38 session38 library38", 18),
        ["learning38 model38", "token38 prompt38", "session38", "library38"],
    ),
    (
        ("learning38 model38 token38 prompt38 session38 library38", 28),
        ["learning38 model38 token38", "prompt38 session38 library38"],
    ),
    (
        ("model38 token38 prompt38 session38 library38 service38", 6),
        ["model38", "token38", "prompt38", "session38", "library38", "service38"],
    ),
    (
        ("model38 token38 prompt38 session38 library38 service38", 10),
        ["model38", "token38", "prompt38", "session38", "library38", "service38"],
    ),
    (
        ("model38 token38 prompt38 session38 library38 service38", 18),
        ["model38 token38", "prompt38 session38", "library38", "service38"],
    ),
    (
        ("model38 token38 prompt38 session38 library38 service38", 28),
        ["model38 token38 prompt38", "session38 library38", "service38"],
    ),
    (
        ("token38 prompt38 session38 library38 service38 gateway38", 6),
        ["token38", "prompt38", "session38", "library38", "service38", "gateway38"],
    ),
    (
        ("token38 prompt38 session38 library38 service38 gateway38", 10),
        ["token38", "prompt38", "session38", "library38", "service38", "gateway38"],
    ),
    (
        ("token38 prompt38 session38 library38 service38 gateway38", 18),
        ["token38 prompt38", "session38", "library38", "service38", "gateway38"],
    ),
    (
        ("token38 prompt38 session38 library38 service38 gateway38", 28),
        ["token38 prompt38 session38", "library38 service38", "gateway38"],
    ),
    (
        ("prompt38 session38 library38 service38 gateway38 storage38", 6),
        ["prompt38", "session38", "library38", "service38", "gateway38", "storage38"],
    ),
    (
        ("prompt38 session38 library38 service38 gateway38 storage38", 10),
        ["prompt38", "session38", "library38", "service38", "gateway38", "storage38"],
    ),
    (
        ("prompt38 session38 library38 service38 gateway38 storage38", 18),
        ["prompt38 session38", "library38", "service38", "gateway38", "storage38"],
    ),
    (
        ("prompt38 session38 library38 service38 gateway38 storage38", 28),
        ["prompt38 session38 library38", "service38 gateway38", "storage38"],
    ),
    (
        ("session38 library38 service38 gateway38 storage38 network38", 6),
        ["session38", "library38", "service38", "gateway38", "storage38", "network38"],
    ),
    (
        ("session38 library38 service38 gateway38 storage38 network38", 10),
        ["session38", "library38", "service38", "gateway38", "storage38", "network38"],
    ),
    (
        ("session38 library38 service38 gateway38 storage38 network38", 18),
        ["session38", "library38", "service38", "gateway38", "storage38", "network38"],
    ),
    (
        ("session38 library38 service38 gateway38 storage38 network38", 28),
        ["session38 library38", "service38 gateway38", "storage38 network38"],
    ),
    (
        ("library38 service38 gateway38 storage38 network38 latency38", 6),
        ["library38", "service38", "gateway38", "storage38", "network38", "latency38"],
    ),
    (
        ("library38 service38 gateway38 storage38 network38 latency38", 10),
        ["library38", "service38", "gateway38", "storage38", "network38", "latency38"],
    ),
    (
        ("library38 service38 gateway38 storage38 network38 latency38", 18),
        ["library38", "service38", "gateway38", "storage38", "network38", "latency38"],
    ),
    (
        ("library38 service38 gateway38 storage38 network38 latency38", 28),
        ["library38 service38", "gateway38 storage38", "network38 latency38"],
    ),
    (
        ("service38 gateway38 storage38 network38 latency38 buffer38", 6),
        ["service38", "gateway38", "storage38", "network38", "latency38", "buffer38"],
    ),
    (
        ("service38 gateway38 storage38 network38 latency38 buffer38", 10),
        ["service38", "gateway38", "storage38", "network38", "latency38", "buffer38"],
    ),
    (
        ("service38 gateway38 storage38 network38 latency38 buffer38", 18),
        ["service38", "gateway38", "storage38", "network38", "latency38 buffer38"],
    ),
    (
        ("service38 gateway38 storage38 network38 latency38 buffer38", 28),
        ["service38 gateway38", "storage38 network38", "latency38 buffer38"],
    ),
    (
        ("gateway38 storage38 network38 latency38 buffer38 queue38", 6),
        ["gateway38", "storage38", "network38", "latency38", "buffer38", "queue38"],
    ),
    (
        ("gateway38 storage38 network38 latency38 buffer38 queue38", 10),
        ["gateway38", "storage38", "network38", "latency38", "buffer38", "queue38"],
    ),
    (
        ("gateway38 storage38 network38 latency38 buffer38 queue38", 18),
        ["gateway38", "storage38", "network38", "latency38 buffer38", "queue38"],
    ),
    (
        ("gateway38 storage38 network38 latency38 buffer38 queue38", 28),
        ["gateway38 storage38", "network38 latency38 buffer38", "queue38"],
    ),
    (
        ("storage38 network38 latency38 buffer38 queue38 worker38", 6),
        ["storage38", "network38", "latency38", "buffer38", "queue38", "worker38"],
    ),
    (
        ("storage38 network38 latency38 buffer38 queue38 worker38", 10),
        ["storage38", "network38", "latency38", "buffer38", "queue38", "worker38"],
    ),
    (
        ("storage38 network38 latency38 buffer38 queue38 worker38", 18),
        ["storage38", "network38", "latency38 buffer38", "queue38 worker38"],
    ),
    (
        ("storage38 network38 latency38 buffer38 queue38 worker38", 28),
        ["storage38 network38", "latency38 buffer38 queue38", "worker38"],
    ),
    (
        ("network38 latency38 buffer38 queue38 worker38 kernel38", 6),
        ["network38", "latency38", "buffer38", "queue38", "worker38", "kernel38"],
    ),
    (
        ("network38 latency38 buffer38 queue38 worker38 kernel38", 10),
        ["network38", "latency38", "buffer38", "queue38", "worker38", "kernel38"],
    ),
    (
        ("network38 latency38 buffer38 queue38 worker38 kernel38", 18),
        ["network38", "latency38 buffer38", "queue38 worker38", "kernel38"],
    ),
    (
        ("network38 latency38 buffer38 queue38 worker38 kernel38", 28),
        ["network38 latency38 buffer38", "queue38 worker38 kernel38"],
    ),
    (
        ("latency38 buffer38 queue38 worker38 kernel38 signal38", 6),
        ["latency38", "buffer38", "queue38", "worker38", "kernel38", "signal38"],
    ),
    (
        ("latency38 buffer38 queue38 worker38 kernel38 signal38", 10),
        ["latency38", "buffer38", "queue38", "worker38", "kernel38", "signal38"],
    ),
    (
        ("latency38 buffer38 queue38 worker38 kernel38 signal38", 18),
        ["latency38 buffer38", "queue38 worker38", "kernel38 signal38"],
    ),
    (
        ("latency38 buffer38 queue38 worker38 kernel38 signal38", 28),
        ["latency38 buffer38 queue38", "worker38 kernel38 signal38"],
    ),
    (
        ("buffer38 queue38 worker38 kernel38 signal38 packet38", 6),
        ["buffer38", "queue38", "worker38", "kernel38", "signal38", "packet38"],
    ),
    (
        ("buffer38 queue38 worker38 kernel38 signal38 packet38", 10),
        ["buffer38", "queue38", "worker38", "kernel38", "signal38", "packet38"],
    ),
    (
        ("buffer38 queue38 worker38 kernel38 signal38 packet38", 18),
        ["buffer38 queue38", "worker38 kernel38", "signal38 packet38"],
    ),
    (
        ("buffer38 queue38 worker38 kernel38 signal38 packet38", 28),
        ["buffer38 queue38 worker38", "kernel38 signal38 packet38"],
    ),
    (
        ("queue38 worker38 kernel38 signal38 packet38 router38", 6),
        ["queue38", "worker38", "kernel38", "signal38", "packet38", "router38"],
    ),
    (
        ("queue38 worker38 kernel38 signal38 packet38 router38", 10),
        ["queue38", "worker38", "kernel38", "signal38", "packet38", "router38"],
    ),
    (
        ("queue38 worker38 kernel38 signal38 packet38 router38", 18),
        ["queue38 worker38", "kernel38 signal38", "packet38 router38"],
    ),
    (
        ("queue38 worker38 kernel38 signal38 packet38 router38", 28),
        ["queue38 worker38 kernel38", "signal38 packet38 router38"],
    ),
    (
        ("worker38 kernel38 signal38 packet38 router38 cluster38", 6),
        ["worker38", "kernel38", "signal38", "packet38", "router38", "cluster38"],
    ),
    (
        ("worker38 kernel38 signal38 packet38 router38 cluster38", 10),
        ["worker38", "kernel38", "signal38", "packet38", "router38", "cluster38"],
    ),
    (
        ("worker38 kernel38 signal38 packet38 router38 cluster38", 18),
        ["worker38 kernel38", "signal38 packet38", "router38 cluster38"],
    ),
    (
        ("worker38 kernel38 signal38 packet38 router38 cluster38", 28),
        ["worker38 kernel38 signal38", "packet38 router38 cluster38"],
    ),
    (
        ("kernel38 signal38 packet38 router38 cluster38 mirror38", 6),
        ["kernel38", "signal38", "packet38", "router38", "cluster38", "mirror38"],
    ),
    (
        ("kernel38 signal38 packet38 router38 cluster38 mirror38", 10),
        ["kernel38", "signal38", "packet38", "router38", "cluster38", "mirror38"],
    ),
    (
        ("kernel38 signal38 packet38 router38 cluster38 mirror38", 18),
        ["kernel38 signal38", "packet38 router38", "cluster38 mirror38"],
    ),
    (
        ("kernel38 signal38 packet38 router38 cluster38 mirror38", 28),
        ["kernel38 signal38 packet38", "router38 cluster38 mirror38"],
    ),
    (
        ("signal38 packet38 router38 cluster38 mirror38 filter38", 6),
        ["signal38", "packet38", "router38", "cluster38", "mirror38", "filter38"],
    ),
    (
        ("signal38 packet38 router38 cluster38 mirror38 filter38", 10),
        ["signal38", "packet38", "router38", "cluster38", "mirror38", "filter38"],
    ),
    (
        ("signal38 packet38 router38 cluster38 mirror38 filter38", 18),
        ["signal38 packet38", "router38 cluster38", "mirror38 filter38"],
    ),
    (
        ("signal38 packet38 router38 cluster38 mirror38 filter38", 28),
        ["signal38 packet38 router38", "cluster38 mirror38 filter38"],
    ),
    (
        ("packet38 router38 cluster38 mirror38 filter38 ranking38", 6),
        ["packet38", "router38", "cluster38", "mirror38", "filter38", "ranking38"],
    ),
    (
        ("packet38 router38 cluster38 mirror38 filter38 ranking38", 10),
        ["packet38", "router38", "cluster38", "mirror38", "filter38", "ranking38"],
    ),
    (
        ("packet38 router38 cluster38 mirror38 filter38 ranking38", 18),
        ["packet38 router38", "cluster38 mirror38", "filter38 ranking38"],
    ),
    (
        ("packet38 router38 cluster38 mirror38 filter38 ranking38", 28),
        ["packet38 router38 cluster38", "mirror38 filter38 ranking38"],
    ),
    (
        ("router38 cluster38 mirror38 filter38 ranking38 encoding38", 6),
        ["router38", "cluster38", "mirror38", "filter38", "ranking38", "encoding38"],
    ),
    (
        ("router38 cluster38 mirror38 filter38 ranking38 encoding38", 10),
        ["router38", "cluster38", "mirror38", "filter38", "ranking38", "encoding38"],
    ),
    (
        ("router38 cluster38 mirror38 filter38 ranking38 encoding38", 18),
        ["router38 cluster38", "mirror38 filter38", "ranking38", "encoding38"],
    ),
    (
        ("router38 cluster38 mirror38 filter38 ranking38 encoding38", 28),
        ["router38 cluster38 mirror38", "filter38 ranking38", "encoding38"],
    ),
    (
        ("cluster38 mirror38 filter38 ranking38 encoding38 mapping38", 6),
        ["cluster38", "mirror38", "filter38", "ranking38", "encoding38", "mapping38"],
    ),
    (
        ("cluster38 mirror38 filter38 ranking38 encoding38 mapping38", 10),
        ["cluster38", "mirror38", "filter38", "ranking38", "encoding38", "mapping38"],
    ),
    (
        ("cluster38 mirror38 filter38 ranking38 encoding38 mapping38", 18),
        ["cluster38 mirror38", "filter38 ranking38", "encoding38", "mapping38"],
    ),
    (
        ("cluster38 mirror38 filter38 ranking38 encoding38 mapping38", 28),
        ["cluster38 mirror38 filter38", "ranking38 encoding38", "mapping38"],
    ),
    (
        ("mirror38 filter38 ranking38 encoding38 mapping38 record38", 6),
        ["mirror38", "filter38", "ranking38", "encoding38", "mapping38", "record38"],
    ),
    (
        ("mirror38 filter38 ranking38 encoding38 mapping38 record38", 10),
        ["mirror38", "filter38", "ranking38", "encoding38", "mapping38", "record38"],
    ),
    (
        ("mirror38 filter38 ranking38 encoding38 mapping38 record38", 18),
        ["mirror38 filter38", "ranking38", "encoding38", "mapping38 record38"],
    ),
    (
        ("mirror38 filter38 ranking38 encoding38 mapping38 record38", 28),
        ["mirror38 filter38 ranking38", "encoding38 mapping38", "record38"],
    ),
    (
        ("filter38 ranking38 encoding38 mapping38 record38 candle38", 6),
        ["filter38", "ranking38", "encoding38", "mapping38", "record38", "candle38"],
    ),
    (
        ("filter38 ranking38 encoding38 mapping38 record38 candle38", 10),
        ["filter38", "ranking38", "encoding38", "mapping38", "record38", "candle38"],
    ),
    (
        ("filter38 ranking38 encoding38 mapping38 record38 candle38", 18),
        ["filter38 ranking38", "encoding38", "mapping38 record38", "candle38"],
    ),
    (
        ("filter38 ranking38 encoding38 mapping38 record38 candle38", 28),
        ["filter38 ranking38", "encoding38 mapping38", "record38 candle38"],
    ),
    (
        ("ranking38 encoding38 mapping38 record38 candle38 thread38", 6),
        ["ranking38", "encoding38", "mapping38", "record38", "candle38", "thread38"],
    ),
    (
        ("ranking38 encoding38 mapping38 record38 candle38 thread38", 10),
        ["ranking38", "encoding38", "mapping38", "record38", "candle38", "thread38"],
    ),
    (
        ("ranking38 encoding38 mapping38 record38 candle38 thread38", 18),
        ["ranking38", "encoding38", "mapping38 record38", "candle38 thread38"],
    ),
    (
        ("ranking38 encoding38 mapping38 record38 candle38 thread38", 28),
        ["ranking38 encoding38", "mapping38 record38 candle38", "thread38"],
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
