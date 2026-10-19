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
        ("round 750: the quick brown fox jumps over the lazy dog", 4),
        ["round", "750:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", 8),
        ["round", "750: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", 12),
        ["round 750:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", 16),
        ["round 750: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", 24),
        ["round 750: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 750: the quick brown fox jumps over the lazy dog", 32),
        ["round 750: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", 4),
        ["round", "750:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", 8),
        ["round", "750:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", 12),
        ["round 750:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", 16),
        ["round 750:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", 24),
        ["round 750: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 750: agentuniverse is a framework for multi agents", 32),
        ["round 750: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", 4),
        ["round", "750:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", 8),
        ["round", "750:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", 12),
        ["round 750:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", 16),
        ["round 750:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", 24),
        ["round 750: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 750: knowledge stored as vectors enables retrieval", 32),
        ["round 750: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 750: the processor reads the record then stops", 4),
        ["round", "750:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 750: the processor reads the record then stops", 8),
        ["round", "750: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 750: the processor reads the record then stops", 12),
        ["round 750:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 750: the processor reads the record then stops", 16),
        ["round 750: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 750: the processor reads the record then stops", 24),
        ["round 750: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 750: the processor reads the record then stops", 32),
        ["round 750: the processor reads", "the record then stops"],
    ),
    (
        ("round 750: a worker pulls the next task from the queue", 4),
        ["round", "750:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 750: a worker pulls the next task from the queue", 8),
        ["round", "750: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 750: a worker pulls the next task from the queue", 12),
        ["round 750: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 750: a worker pulls the next task from the queue", 16),
        ["round 750: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 750: a worker pulls the next task from the queue", 24),
        ["round 750: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 750: a worker pulls the next task from the queue", 32),
        ["round 750: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 750: signals travel through the network layer", 4),
        ["round", "750:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 750: signals travel through the network layer", 8),
        ["round", "750:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 750: signals travel through the network layer", 12),
        ["round 750:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 750: signals travel through the network layer", 16),
        ["round 750:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 750: signals travel through the network layer", 24),
        ["round 750: signals", "travel through the", "network layer"],
    ),
    (
        ("round 750: signals travel through the network layer", 32),
        ["round 750: signals travel", "through the network layer"],
    ),
    (
        ("round 750: the gateway routes each request by policy", 4),
        ["round", "750:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 750: the gateway routes each request by policy", 8),
        ["round", "750: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 750: the gateway routes each request by policy", 12),
        ["round 750:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 750: the gateway routes each request by policy", 16),
        ["round 750: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 750: the gateway routes each request by policy", 24),
        ["round 750: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 750: the gateway routes each request by policy", 32),
        ["round 750: the gateway routes", "each request by policy"],
    ),
    (
        ("round 750: memory grows until the buffer is full", 4),
        ["round", "750:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 750: memory grows until the buffer is full", 8),
        ["round", "750:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 750: memory grows until the buffer is full", 12),
        ["round 750:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 750: memory grows until the buffer is full", 16),
        ["round 750:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 750: memory grows until the buffer is full", 24), ["round 750: memory grows", "until the buffer is full"]),
    (("round 750: memory grows until the buffer is full", 32), ["round 750: memory grows until", "the buffer is full"]),
    (
        ("round 750: the cluster mirrors every packet twice", 4),
        ["round", "750:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 750: the cluster mirrors every packet twice", 8),
        ["round", "750: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 750: the cluster mirrors every packet twice", 12),
        ["round 750:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 750: the cluster mirrors every packet twice", 16),
        ["round 750: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 750: the cluster mirrors every packet twice", 24),
        ["round 750: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 750: the cluster mirrors every packet twice", 32),
        ["round 750: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", 4),
        ["round", "750:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", 8),
        ["round", "750:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", 12),
        ["round 750:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", 16),
        ["round 750:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", 24),
        ["round 750: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 750: ranking uses tokens learned from the corpus", 32),
        ["round 750: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 750: a long session ends when the candle dies", 4),
        ["round", "750:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 750: a long session ends when the candle dies", 8),
        ["round", "750: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 750: a long session ends when the candle dies", 12),
        ["round 750: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 750: a long session ends when the candle dies", 16),
        ["round 750: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 750: a long session ends when the candle dies", 24),
        ["round 750: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 750: a long session ends when the candle dies", 32),
        ["round 750: a long session ends", "when the candle dies"],
    ),
    (
        ("round 750: encode the prompt then map the result", 4),
        ["round", "750:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 750: encode the prompt then map the result", 8),
        ["round", "750:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 750: encode the prompt then map the result", 12),
        ["round 750:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 750: encode the prompt then map the result", 16),
        ["round 750:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 750: encode the prompt then map the result", 24),
        ["round 750: encode the", "prompt then map the", "result"],
    ),
    (("round 750: encode the prompt then map the result", 32), ["round 750: encode the prompt", "then map the result"]),
    (
        ("round 750: the kernel wakes the worker at dawn", 4),
        ["round", "750:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 750: the kernel wakes the worker at dawn", 8),
        ["round", "750: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 750: the kernel wakes the worker at dawn", 12),
        ["round 750:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 750: the kernel wakes the worker at dawn", 16), ["round 750: the", "kernel wakes the", "worker at dawn"]),
    (("round 750: the kernel wakes the worker at dawn", 24), ["round 750: the kernel", "wakes the worker at dawn"]),
    (("round 750: the kernel wakes the worker at dawn", 32), ["round 750: the kernel wakes the", "worker at dawn"]),
    (
        ("round 750: service latency drops after the patch", 4),
        ["round", "750:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 750: service latency drops after the patch", 8),
        ["round", "750:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 750: service latency drops after the patch", 12),
        ["round 750:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 750: service latency drops after the patch", 16),
        ["round 750:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 750: service latency drops after the patch", 24),
        ["round 750: service", "latency drops after the", "patch"],
    ),
    (("round 750: service latency drops after the patch", 32), ["round 750: service latency drops", "after the patch"]),
    (
        ("round 750: the library caches every vector it sees", 4),
        ["round", "750:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 750: the library caches every vector it sees", 8),
        ["round", "750: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 750: the library caches every vector it sees", 12),
        ["round 750:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 750: the library caches every vector it sees", 16),
        ["round 750: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 750: the library caches every vector it sees", 24),
        ["round 750: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 750: the library caches every vector it sees", 32),
        ["round 750: the library caches", "every vector it sees"],
    ),
    (
        ("round 750: agents argue then the debate resolves", 4),
        ["round", "750:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 750: agents argue then the debate resolves", 8),
        ["round", "750:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 750: agents argue then the debate resolves", 12),
        ["round 750:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 750: agents argue then the debate resolves", 16),
        ["round 750:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 750: agents argue then the debate resolves", 24), ["round 750: agents argue", "then the debate resolves"]),
    (("round 750: agents argue then the debate resolves", 32), ["round 750: agents argue then the", "debate resolves"]),
    (
        ("round 750: the filter keeps only strong matches", 4),
        ["round", "750:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 750: the filter keeps only strong matches", 8),
        ["round", "750: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 750: the filter keeps only strong matches", 12),
        ["round 750:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 750: the filter keeps only strong matches", 16),
        ["round 750: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 750: the filter keeps only strong matches", 24),
        ["round 750: the filter", "keeps only strong", "matches"],
    ),
    (("round 750: the filter keeps only strong matches", 32), ["round 750: the filter keeps only", "strong matches"]),
    (
        ("round 750: the model answers with a short reply", 4),
        ["round", "750:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 750: the model answers with a short reply", 8),
        ["round", "750: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 750: the model answers with a short reply", 12),
        ["round 750:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 750: the model answers with a short reply", 16),
        ["round 750: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 750: the model answers with a short reply", 24),
        ["round 750: the model", "answers with a short", "reply"],
    ),
    (("round 750: the model answers with a short reply", 32), ["round 750: the model answers", "with a short reply"]),
    (
        ("round 750: the recorder stores the reasoning trace", 4),
        ["round", "750:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 750: the recorder stores the reasoning trace", 8),
        ["round", "750: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 750: the recorder stores the reasoning trace", 12),
        ["round 750:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 750: the recorder stores the reasoning trace", 16),
        ["round 750: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 750: the recorder stores the reasoning trace", 24),
        ["round 750: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 750: the recorder stores the reasoning trace", 32),
        ["round 750: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 750: the angel watches the processor run", 4),
        ["round", "750:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 750: the angel watches the processor run", 8),
        ["round", "750: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 750: the angel watches the processor run", 12),
        ["round 750:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 750: the angel watches the processor run", 16),
        ["round 750: the", "angel watches", "the processor", "run"],
    ),
    (("round 750: the angel watches the processor run", 24), ["round 750: the angel", "watches the processor", "run"]),
    (("round 750: the angel watches the processor run", 32), ["round 750: the angel watches the", "processor run"]),
    (
        ("round 750: angle of the vector decides the match", 4),
        ["round", "750:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 750: angle of the vector decides the match", 8),
        ["round", "750:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 750: angle of the vector decides the match", 12),
        ["round 750:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 750: angle of the vector decides the match", 16),
        ["round 750: angle", "of the vector", "decides the", "match"],
    ),
    (("round 750: angle of the vector decides the match", 24), ["round 750: angle of the", "vector decides the match"]),
    (("round 750: angle of the vector decides the match", 32), ["round 750: angle of the vector", "decides the match"]),
    (
        ("round 750: the candle burns twice as long at night", 4),
        ["round", "750:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 750: the candle burns twice as long at night", 8),
        ["round", "750: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 750: the candle burns twice as long at night", 12),
        ["round 750:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 750: the candle burns twice as long at night", 16),
        ["round 750: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 750: the candle burns twice as long at night", 24),
        ["round 750: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 750: the candle burns twice as long at night", 32),
        ["round 750: the candle burns", "twice as long at night"],
    ),
    (
        ("round 750: a mirror of the universe in one line", 4),
        ["round", "750:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 750: a mirror of the universe in one line", 8),
        ["round", "750: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 750: a mirror of the universe in one line", 12),
        ["round 750: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 750: a mirror of the universe in one line", 16),
        ["round 750: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 750: a mirror of the universe in one line", 24), ["round 750: a mirror of", "the universe in one line"]),
    (("round 750: a mirror of the universe in one line", 32), ["round 750: a mirror of the", "universe in one line"]),
    (
        ("round 750: the queue drains before the storm", 4),
        ["round", "750:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 750: the queue drains before the storm", 8),
        ["round", "750: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 750: the queue drains before the storm", 12),
        ["round 750:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 750: the queue drains before the storm", 16), ["round 750: the", "queue drains", "before the storm"]),
    (("round 750: the queue drains before the storm", 24), ["round 750: the queue", "drains before the storm"]),
    (("round 750: the queue drains before the storm", 32), ["round 750: the queue drains", "before the storm"]),
    (
        ("kitten750 sitting750 agent750 angle750 universe750 memory750", 6),
        ["kitten750", "sitting750", "agent750", "angle750", "universe750", "memory750"],
    ),
    (
        ("kitten750 sitting750 agent750 angle750 universe750 memory750", 10),
        ["kitten750", "sitting750", "agent750", "angle750", "universe750", "memory750"],
    ),
    (
        ("kitten750 sitting750 agent750 angle750 universe750 memory750", 18),
        ["kitten750", "sitting750", "agent750 angle750", "universe750", "memory750"],
    ),
    (
        ("kitten750 sitting750 agent750 angle750 universe750 memory750", 28),
        ["kitten750 sitting750", "agent750 angle750", "universe750 memory750"],
    ),
    (
        ("sitting750 agent750 angle750 universe750 memory750 stream750", 6),
        ["sitting750", "agent750", "angle750", "universe750", "memory750", "stream750"],
    ),
    (
        ("sitting750 agent750 angle750 universe750 memory750 stream750", 10),
        ["sitting750", "agent750", "angle750", "universe750", "memory750", "stream750"],
    ),
    (
        ("sitting750 agent750 angle750 universe750 memory750 stream750", 18),
        ["sitting750", "agent750 angle750", "universe750", "memory750", "stream750"],
    ),
    (
        ("sitting750 agent750 angle750 universe750 memory750 stream750", 28),
        ["sitting750 agent750 angle750", "universe750 memory750", "stream750"],
    ),
    (
        ("agent750 angle750 universe750 memory750 stream750 context750", 6),
        ["agent750", "angle750", "universe750", "memory750", "stream750", "context750"],
    ),
    (
        ("agent750 angle750 universe750 memory750 stream750 context750", 10),
        ["agent750", "angle750", "universe750", "memory750", "stream750", "context750"],
    ),
    (
        ("agent750 angle750 universe750 memory750 stream750 context750", 18),
        ["agent750 angle750", "universe750", "memory750", "stream750", "context750"],
    ),
    (
        ("agent750 angle750 universe750 memory750 stream750 context750", 28),
        ["agent750 angle750", "universe750 memory750", "stream750 context750"],
    ),
    (
        ("angle750 universe750 memory750 stream750 context750 knowledge750", 6),
        ["angle750", "universe750", "memory750", "stream750", "context750", "knowledge750"],
    ),
    (
        ("angle750 universe750 memory750 stream750 context750 knowledge750", 10),
        ["angle750", "universe750", "memory750", "stream750", "context750", "knowledge750"],
    ),
    (
        ("angle750 universe750 memory750 stream750 context750 knowledge750", 18),
        ["angle750", "universe750", "memory750", "stream750", "context750", "knowledge750"],
    ),
    (
        ("angle750 universe750 memory750 stream750 context750 knowledge750", 28),
        ["angle750 universe750", "memory750 stream750", "context750 knowledge750"],
    ),
    (
        ("universe750 memory750 stream750 context750 knowledge750 vector750", 6),
        ["universe750", "memory750", "stream750", "context750", "knowledge750", "vector750"],
    ),
    (
        ("universe750 memory750 stream750 context750 knowledge750 vector750", 10),
        ["universe750", "memory750", "stream750", "context750", "knowledge750", "vector750"],
    ),
    (
        ("universe750 memory750 stream750 context750 knowledge750 vector750", 18),
        ["universe750", "memory750", "stream750", "context750", "knowledge750", "vector750"],
    ),
    (
        ("universe750 memory750 stream750 context750 knowledge750 vector750", 28),
        ["universe750 memory750", "stream750 context750", "knowledge750 vector750"],
    ),
    (
        ("memory750 stream750 context750 knowledge750 vector750 processor750", 6),
        ["memory750", "stream750", "context750", "knowledge750", "vector750", "processor750"],
    ),
    (
        ("memory750 stream750 context750 knowledge750 vector750 processor750", 10),
        ["memory750", "stream750", "context750", "knowledge750", "vector750", "processor750"],
    ),
    (
        ("memory750 stream750 context750 knowledge750 vector750 processor750", 18),
        ["memory750", "stream750", "context750", "knowledge750", "vector750", "processor750"],
    ),
    (
        ("memory750 stream750 context750 knowledge750 vector750 processor750", 28),
        ["memory750 stream750", "context750 knowledge750", "vector750 processor750"],
    ),
    (
        ("stream750 context750 knowledge750 vector750 processor750 reasoning750", 6),
        ["stream750", "context750", "knowledge750", "vector750", "processor750", "reasoning750"],
    ),
    (
        ("stream750 context750 knowledge750 vector750 processor750 reasoning750", 10),
        ["stream750", "context750", "knowledge750", "vector750", "processor750", "reasoning750"],
    ),
    (
        ("stream750 context750 knowledge750 vector750 processor750 reasoning750", 18),
        ["stream750", "context750", "knowledge750", "vector750", "processor750", "reasoning750"],
    ),
    (
        ("stream750 context750 knowledge750 vector750 processor750 reasoning750", 28),
        ["stream750 context750", "knowledge750 vector750", "processor750 reasoning750"],
    ),
    (
        ("context750 knowledge750 vector750 processor750 reasoning750 machine750", 6),
        ["context750", "knowledge750", "vector750", "processor750", "reasoning750", "machine750"],
    ),
    (
        ("context750 knowledge750 vector750 processor750 reasoning750 machine750", 10),
        ["context750", "knowledge750", "vector750", "processor750", "reasoning750", "machine750"],
    ),
    (
        ("context750 knowledge750 vector750 processor750 reasoning750 machine750", 18),
        ["context750", "knowledge750", "vector750", "processor750", "reasoning750", "machine750"],
    ),
    (
        ("context750 knowledge750 vector750 processor750 reasoning750 machine750", 28),
        ["context750 knowledge750", "vector750 processor750", "reasoning750 machine750"],
    ),
    (
        ("knowledge750 vector750 processor750 reasoning750 machine750 learning750", 6),
        ["knowledge750", "vector750", "processor750", "reasoning750", "machine750", "learning750"],
    ),
    (
        ("knowledge750 vector750 processor750 reasoning750 machine750 learning750", 10),
        ["knowledge750", "vector750", "processor750", "reasoning750", "machine750", "learning750"],
    ),
    (
        ("knowledge750 vector750 processor750 reasoning750 machine750 learning750", 18),
        ["knowledge750", "vector750", "processor750", "reasoning750", "machine750", "learning750"],
    ),
    (
        ("knowledge750 vector750 processor750 reasoning750 machine750 learning750", 28),
        ["knowledge750 vector750", "processor750 reasoning750", "machine750 learning750"],
    ),
    (
        ("vector750 processor750 reasoning750 machine750 learning750 model750", 6),
        ["vector750", "processor750", "reasoning750", "machine750", "learning750", "model750"],
    ),
    (
        ("vector750 processor750 reasoning750 machine750 learning750 model750", 10),
        ["vector750", "processor750", "reasoning750", "machine750", "learning750", "model750"],
    ),
    (
        ("vector750 processor750 reasoning750 machine750 learning750 model750", 18),
        ["vector750", "processor750", "reasoning750", "machine750", "learning750", "model750"],
    ),
    (
        ("vector750 processor750 reasoning750 machine750 learning750 model750", 28),
        ["vector750 processor750", "reasoning750 machine750", "learning750 model750"],
    ),
    (
        ("processor750 reasoning750 machine750 learning750 model750 token750", 6),
        ["processor750", "reasoning750", "machine750", "learning750", "model750", "token750"],
    ),
    (
        ("processor750 reasoning750 machine750 learning750 model750 token750", 10),
        ["processor750", "reasoning750", "machine750", "learning750", "model750", "token750"],
    ),
    (
        ("processor750 reasoning750 machine750 learning750 model750 token750", 18),
        ["processor750", "reasoning750", "machine750", "learning750", "model750 token750"],
    ),
    (
        ("processor750 reasoning750 machine750 learning750 model750 token750", 28),
        ["processor750 reasoning750", "machine750 learning750", "model750 token750"],
    ),
    (
        ("reasoning750 machine750 learning750 model750 token750 prompt750", 6),
        ["reasoning750", "machine750", "learning750", "model750", "token750", "prompt750"],
    ),
    (
        ("reasoning750 machine750 learning750 model750 token750 prompt750", 10),
        ["reasoning750", "machine750", "learning750", "model750", "token750", "prompt750"],
    ),
    (
        ("reasoning750 machine750 learning750 model750 token750 prompt750", 18),
        ["reasoning750", "machine750", "learning750", "model750 token750", "prompt750"],
    ),
    (
        ("reasoning750 machine750 learning750 model750 token750 prompt750", 28),
        ["reasoning750 machine750", "learning750 model750", "token750 prompt750"],
    ),
    (
        ("machine750 learning750 model750 token750 prompt750 session750", 6),
        ["machine750", "learning750", "model750", "token750", "prompt750", "session750"],
    ),
    (
        ("machine750 learning750 model750 token750 prompt750 session750", 10),
        ["machine750", "learning750", "model750", "token750", "prompt750", "session750"],
    ),
    (
        ("machine750 learning750 model750 token750 prompt750 session750", 18),
        ["machine750", "learning750", "model750 token750", "prompt750", "session750"],
    ),
    (
        ("machine750 learning750 model750 token750 prompt750 session750", 28),
        ["machine750 learning750", "model750 token750 prompt750", "session750"],
    ),
    (
        ("learning750 model750 token750 prompt750 session750 library750", 6),
        ["learning750", "model750", "token750", "prompt750", "session750", "library750"],
    ),
    (
        ("learning750 model750 token750 prompt750 session750 library750", 10),
        ["learning750", "model750", "token750", "prompt750", "session750", "library750"],
    ),
    (
        ("learning750 model750 token750 prompt750 session750 library750", 18),
        ["learning750", "model750 token750", "prompt750", "session750", "library750"],
    ),
    (
        ("learning750 model750 token750 prompt750 session750 library750", 28),
        ["learning750 model750", "token750 prompt750", "session750 library750"],
    ),
    (
        ("model750 token750 prompt750 session750 library750 service750", 6),
        ["model750", "token750", "prompt750", "session750", "library750", "service750"],
    ),
    (
        ("model750 token750 prompt750 session750 library750 service750", 10),
        ["model750", "token750", "prompt750", "session750", "library750", "service750"],
    ),
    (
        ("model750 token750 prompt750 session750 library750 service750", 18),
        ["model750 token750", "prompt750", "session750", "library750", "service750"],
    ),
    (
        ("model750 token750 prompt750 session750 library750 service750", 28),
        ["model750 token750 prompt750", "session750 library750", "service750"],
    ),
    (
        ("token750 prompt750 session750 library750 service750 gateway750", 6),
        ["token750", "prompt750", "session750", "library750", "service750", "gateway750"],
    ),
    (
        ("token750 prompt750 session750 library750 service750 gateway750", 10),
        ["token750", "prompt750", "session750", "library750", "service750", "gateway750"],
    ),
    (
        ("token750 prompt750 session750 library750 service750 gateway750", 18),
        ["token750 prompt750", "session750", "library750", "service750", "gateway750"],
    ),
    (
        ("token750 prompt750 session750 library750 service750 gateway750", 28),
        ["token750 prompt750", "session750 library750", "service750 gateway750"],
    ),
    (
        ("prompt750 session750 library750 service750 gateway750 storage750", 6),
        ["prompt750", "session750", "library750", "service750", "gateway750", "storage750"],
    ),
    (
        ("prompt750 session750 library750 service750 gateway750 storage750", 10),
        ["prompt750", "session750", "library750", "service750", "gateway750", "storage750"],
    ),
    (
        ("prompt750 session750 library750 service750 gateway750 storage750", 18),
        ["prompt750", "session750", "library750", "service750", "gateway750", "storage750"],
    ),
    (
        ("prompt750 session750 library750 service750 gateway750 storage750", 28),
        ["prompt750 session750", "library750 service750", "gateway750 storage750"],
    ),
    (
        ("session750 library750 service750 gateway750 storage750 network750", 6),
        ["session750", "library750", "service750", "gateway750", "storage750", "network750"],
    ),
    (
        ("session750 library750 service750 gateway750 storage750 network750", 10),
        ["session750", "library750", "service750", "gateway750", "storage750", "network750"],
    ),
    (
        ("session750 library750 service750 gateway750 storage750 network750", 18),
        ["session750", "library750", "service750", "gateway750", "storage750", "network750"],
    ),
    (
        ("session750 library750 service750 gateway750 storage750 network750", 28),
        ["session750 library750", "service750 gateway750", "storage750 network750"],
    ),
    (
        ("library750 service750 gateway750 storage750 network750 latency750", 6),
        ["library750", "service750", "gateway750", "storage750", "network750", "latency750"],
    ),
    (
        ("library750 service750 gateway750 storage750 network750 latency750", 10),
        ["library750", "service750", "gateway750", "storage750", "network750", "latency750"],
    ),
    (
        ("library750 service750 gateway750 storage750 network750 latency750", 18),
        ["library750", "service750", "gateway750", "storage750", "network750", "latency750"],
    ),
    (
        ("library750 service750 gateway750 storage750 network750 latency750", 28),
        ["library750 service750", "gateway750 storage750", "network750 latency750"],
    ),
    (
        ("service750 gateway750 storage750 network750 latency750 buffer750", 6),
        ["service750", "gateway750", "storage750", "network750", "latency750", "buffer750"],
    ),
    (
        ("service750 gateway750 storage750 network750 latency750 buffer750", 10),
        ["service750", "gateway750", "storage750", "network750", "latency750", "buffer750"],
    ),
    (
        ("service750 gateway750 storage750 network750 latency750 buffer750", 18),
        ["service750", "gateway750", "storage750", "network750", "latency750", "buffer750"],
    ),
    (
        ("service750 gateway750 storage750 network750 latency750 buffer750", 28),
        ["service750 gateway750", "storage750 network750", "latency750 buffer750"],
    ),
    (
        ("gateway750 storage750 network750 latency750 buffer750 queue750", 6),
        ["gateway750", "storage750", "network750", "latency750", "buffer750", "queue750"],
    ),
    (
        ("gateway750 storage750 network750 latency750 buffer750 queue750", 10),
        ["gateway750", "storage750", "network750", "latency750", "buffer750", "queue750"],
    ),
    (
        ("gateway750 storage750 network750 latency750 buffer750 queue750", 18),
        ["gateway750", "storage750", "network750", "latency750", "buffer750 queue750"],
    ),
    (
        ("gateway750 storage750 network750 latency750 buffer750 queue750", 28),
        ["gateway750 storage750", "network750 latency750", "buffer750 queue750"],
    ),
    (
        ("storage750 network750 latency750 buffer750 queue750 worker750", 6),
        ["storage750", "network750", "latency750", "buffer750", "queue750", "worker750"],
    ),
    (
        ("storage750 network750 latency750 buffer750 queue750 worker750", 10),
        ["storage750", "network750", "latency750", "buffer750", "queue750", "worker750"],
    ),
    (
        ("storage750 network750 latency750 buffer750 queue750 worker750", 18),
        ["storage750", "network750", "latency750", "buffer750 queue750", "worker750"],
    ),
    (
        ("storage750 network750 latency750 buffer750 queue750 worker750", 28),
        ["storage750 network750", "latency750 buffer750", "queue750 worker750"],
    ),
    (
        ("network750 latency750 buffer750 queue750 worker750 kernel750", 6),
        ["network750", "latency750", "buffer750", "queue750", "worker750", "kernel750"],
    ),
    (
        ("network750 latency750 buffer750 queue750 worker750 kernel750", 10),
        ["network750", "latency750", "buffer750", "queue750", "worker750", "kernel750"],
    ),
    (
        ("network750 latency750 buffer750 queue750 worker750 kernel750", 18),
        ["network750", "latency750", "buffer750 queue750", "worker750", "kernel750"],
    ),
    (
        ("network750 latency750 buffer750 queue750 worker750 kernel750", 28),
        ["network750 latency750", "buffer750 queue750 worker750", "kernel750"],
    ),
    (
        ("latency750 buffer750 queue750 worker750 kernel750 signal750", 6),
        ["latency750", "buffer750", "queue750", "worker750", "kernel750", "signal750"],
    ),
    (
        ("latency750 buffer750 queue750 worker750 kernel750 signal750", 10),
        ["latency750", "buffer750", "queue750", "worker750", "kernel750", "signal750"],
    ),
    (
        ("latency750 buffer750 queue750 worker750 kernel750 signal750", 18),
        ["latency750", "buffer750 queue750", "worker750", "kernel750", "signal750"],
    ),
    (
        ("latency750 buffer750 queue750 worker750 kernel750 signal750", 28),
        ["latency750 buffer750", "queue750 worker750 kernel750", "signal750"],
    ),
    (
        ("buffer750 queue750 worker750 kernel750 signal750 packet750", 6),
        ["buffer750", "queue750", "worker750", "kernel750", "signal750", "packet750"],
    ),
    (
        ("buffer750 queue750 worker750 kernel750 signal750 packet750", 10),
        ["buffer750", "queue750", "worker750", "kernel750", "signal750", "packet750"],
    ),
    (
        ("buffer750 queue750 worker750 kernel750 signal750 packet750", 18),
        ["buffer750 queue750", "worker750", "kernel750", "signal750", "packet750"],
    ),
    (
        ("buffer750 queue750 worker750 kernel750 signal750 packet750", 28),
        ["buffer750 queue750 worker750", "kernel750 signal750", "packet750"],
    ),
    (
        ("queue750 worker750 kernel750 signal750 packet750 router750", 6),
        ["queue750", "worker750", "kernel750", "signal750", "packet750", "router750"],
    ),
    (
        ("queue750 worker750 kernel750 signal750 packet750 router750", 10),
        ["queue750", "worker750", "kernel750", "signal750", "packet750", "router750"],
    ),
    (
        ("queue750 worker750 kernel750 signal750 packet750 router750", 18),
        ["queue750 worker750", "kernel750", "signal750", "packet750", "router750"],
    ),
    (
        ("queue750 worker750 kernel750 signal750 packet750 router750", 28),
        ["queue750 worker750 kernel750", "signal750 packet750", "router750"],
    ),
    (
        ("worker750 kernel750 signal750 packet750 router750 cluster750", 6),
        ["worker750", "kernel750", "signal750", "packet750", "router750", "cluster750"],
    ),
    (
        ("worker750 kernel750 signal750 packet750 router750 cluster750", 10),
        ["worker750", "kernel750", "signal750", "packet750", "router750", "cluster750"],
    ),
    (
        ("worker750 kernel750 signal750 packet750 router750 cluster750", 18),
        ["worker750", "kernel750", "signal750", "packet750", "router750", "cluster750"],
    ),
    (
        ("worker750 kernel750 signal750 packet750 router750 cluster750", 28),
        ["worker750 kernel750", "signal750 packet750", "router750 cluster750"],
    ),
    (
        ("kernel750 signal750 packet750 router750 cluster750 mirror750", 6),
        ["kernel750", "signal750", "packet750", "router750", "cluster750", "mirror750"],
    ),
    (
        ("kernel750 signal750 packet750 router750 cluster750 mirror750", 10),
        ["kernel750", "signal750", "packet750", "router750", "cluster750", "mirror750"],
    ),
    (
        ("kernel750 signal750 packet750 router750 cluster750 mirror750", 18),
        ["kernel750", "signal750", "packet750", "router750", "cluster750", "mirror750"],
    ),
    (
        ("kernel750 signal750 packet750 router750 cluster750 mirror750", 28),
        ["kernel750 signal750", "packet750 router750", "cluster750 mirror750"],
    ),
    (
        ("signal750 packet750 router750 cluster750 mirror750 filter750", 6),
        ["signal750", "packet750", "router750", "cluster750", "mirror750", "filter750"],
    ),
    (
        ("signal750 packet750 router750 cluster750 mirror750 filter750", 10),
        ["signal750", "packet750", "router750", "cluster750", "mirror750", "filter750"],
    ),
    (
        ("signal750 packet750 router750 cluster750 mirror750 filter750", 18),
        ["signal750", "packet750", "router750", "cluster750", "mirror750", "filter750"],
    ),
    (
        ("signal750 packet750 router750 cluster750 mirror750 filter750", 28),
        ["signal750 packet750", "router750 cluster750", "mirror750 filter750"],
    ),
    (
        ("packet750 router750 cluster750 mirror750 filter750 ranking750", 6),
        ["packet750", "router750", "cluster750", "mirror750", "filter750", "ranking750"],
    ),
    (
        ("packet750 router750 cluster750 mirror750 filter750 ranking750", 10),
        ["packet750", "router750", "cluster750", "mirror750", "filter750", "ranking750"],
    ),
    (
        ("packet750 router750 cluster750 mirror750 filter750 ranking750", 18),
        ["packet750", "router750", "cluster750", "mirror750", "filter750", "ranking750"],
    ),
    (
        ("packet750 router750 cluster750 mirror750 filter750 ranking750", 28),
        ["packet750 router750", "cluster750 mirror750", "filter750 ranking750"],
    ),
    (
        ("router750 cluster750 mirror750 filter750 ranking750 encoding750", 6),
        ["router750", "cluster750", "mirror750", "filter750", "ranking750", "encoding750"],
    ),
    (
        ("router750 cluster750 mirror750 filter750 ranking750 encoding750", 10),
        ["router750", "cluster750", "mirror750", "filter750", "ranking750", "encoding750"],
    ),
    (
        ("router750 cluster750 mirror750 filter750 ranking750 encoding750", 18),
        ["router750", "cluster750", "mirror750", "filter750", "ranking750", "encoding750"],
    ),
    (
        ("router750 cluster750 mirror750 filter750 ranking750 encoding750", 28),
        ["router750 cluster750", "mirror750 filter750", "ranking750 encoding750"],
    ),
    (
        ("cluster750 mirror750 filter750 ranking750 encoding750 mapping750", 6),
        ["cluster750", "mirror750", "filter750", "ranking750", "encoding750", "mapping750"],
    ),
    (
        ("cluster750 mirror750 filter750 ranking750 encoding750 mapping750", 10),
        ["cluster750", "mirror750", "filter750", "ranking750", "encoding750", "mapping750"],
    ),
    (
        ("cluster750 mirror750 filter750 ranking750 encoding750 mapping750", 18),
        ["cluster750", "mirror750", "filter750", "ranking750", "encoding750", "mapping750"],
    ),
    (
        ("cluster750 mirror750 filter750 ranking750 encoding750 mapping750", 28),
        ["cluster750 mirror750", "filter750 ranking750", "encoding750 mapping750"],
    ),
    (
        ("mirror750 filter750 ranking750 encoding750 mapping750 record750", 6),
        ["mirror750", "filter750", "ranking750", "encoding750", "mapping750", "record750"],
    ),
    (
        ("mirror750 filter750 ranking750 encoding750 mapping750 record750", 10),
        ["mirror750", "filter750", "ranking750", "encoding750", "mapping750", "record750"],
    ),
    (
        ("mirror750 filter750 ranking750 encoding750 mapping750 record750", 18),
        ["mirror750", "filter750", "ranking750", "encoding750", "mapping750", "record750"],
    ),
    (
        ("mirror750 filter750 ranking750 encoding750 mapping750 record750", 28),
        ["mirror750 filter750", "ranking750 encoding750", "mapping750 record750"],
    ),
    (
        ("filter750 ranking750 encoding750 mapping750 record750 candle750", 6),
        ["filter750", "ranking750", "encoding750", "mapping750", "record750", "candle750"],
    ),
    (
        ("filter750 ranking750 encoding750 mapping750 record750 candle750", 10),
        ["filter750", "ranking750", "encoding750", "mapping750", "record750", "candle750"],
    ),
    (
        ("filter750 ranking750 encoding750 mapping750 record750 candle750", 18),
        ["filter750", "ranking750", "encoding750", "mapping750", "record750", "candle750"],
    ),
    (
        ("filter750 ranking750 encoding750 mapping750 record750 candle750", 28),
        ["filter750 ranking750", "encoding750 mapping750", "record750 candle750"],
    ),
    (
        ("ranking750 encoding750 mapping750 record750 candle750 thread750", 6),
        ["ranking750", "encoding750", "mapping750", "record750", "candle750", "thread750"],
    ),
    (
        ("ranking750 encoding750 mapping750 record750 candle750 thread750", 10),
        ["ranking750", "encoding750", "mapping750", "record750", "candle750", "thread750"],
    ),
    (
        ("ranking750 encoding750 mapping750 record750 candle750 thread750", 18),
        ["ranking750", "encoding750", "mapping750", "record750", "candle750", "thread750"],
    ),
    (
        ("ranking750 encoding750 mapping750 record750 candle750 thread750", 28),
        ["ranking750 encoding750", "mapping750 record750", "candle750 thread750"],
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
