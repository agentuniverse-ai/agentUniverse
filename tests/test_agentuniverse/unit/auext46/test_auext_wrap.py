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
        ("round 46: the quick brown fox jumps over the lazy dog", 4),
        ["round", "46:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 46: the quick brown fox jumps over the lazy dog", 8),
        ["round", "46: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 46: the quick brown fox jumps over the lazy dog", 12),
        ["round 46:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 46: the quick brown fox jumps over the lazy dog", 16),
        ["round 46: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 46: the quick brown fox jumps over the lazy dog", 24),
        ["round 46: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 46: the quick brown fox jumps over the lazy dog", 32),
        ["round 46: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 46: agentuniverse is a framework for multi agents", 4),
        ["round", "46:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 46: agentuniverse is a framework for multi agents", 8),
        ["round", "46:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 46: agentuniverse is a framework for multi agents", 12),
        ["round 46:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 46: agentuniverse is a framework for multi agents", 16),
        ["round 46:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 46: agentuniverse is a framework for multi agents", 24),
        ["round 46: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 46: agentuniverse is a framework for multi agents", 32),
        ["round 46: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 46: knowledge stored as vectors enables retrieval", 4),
        ["round", "46:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 46: knowledge stored as vectors enables retrieval", 8),
        ["round", "46:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 46: knowledge stored as vectors enables retrieval", 12),
        ["round 46:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 46: knowledge stored as vectors enables retrieval", 16),
        ["round 46:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 46: knowledge stored as vectors enables retrieval", 24),
        ["round 46: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 46: knowledge stored as vectors enables retrieval", 32),
        ["round 46: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 46: the processor reads the record then stops", 4),
        ["round", "46:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 46: the processor reads the record then stops", 8),
        ["round", "46: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 46: the processor reads the record then stops", 12),
        ["round 46:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 46: the processor reads the record then stops", 16),
        ["round 46: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 46: the processor reads the record then stops", 24),
        ["round 46: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 46: the processor reads the record then stops", 32),
        ["round 46: the processor reads", "the record then stops"],
    ),
    (
        ("round 46: a worker pulls the next task from the queue", 4),
        ["round", "46:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 46: a worker pulls the next task from the queue", 8),
        ["round", "46: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 46: a worker pulls the next task from the queue", 12),
        ["round 46: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 46: a worker pulls the next task from the queue", 16),
        ["round 46: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 46: a worker pulls the next task from the queue", 24),
        ["round 46: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 46: a worker pulls the next task from the queue", 32),
        ["round 46: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 46: signals travel through the network layer", 4),
        ["round", "46:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 46: signals travel through the network layer", 8),
        ["round", "46:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 46: signals travel through the network layer", 12),
        ["round 46:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 46: signals travel through the network layer", 16),
        ["round 46:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 46: signals travel through the network layer", 24),
        ["round 46: signals travel", "through the network", "layer"],
    ),
    (
        ("round 46: signals travel through the network layer", 32),
        ["round 46: signals travel through", "the network layer"],
    ),
    (
        ("round 46: the gateway routes each request by policy", 4),
        ["round", "46:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 46: the gateway routes each request by policy", 8),
        ["round", "46: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 46: the gateway routes each request by policy", 12),
        ["round 46:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 46: the gateway routes each request by policy", 16),
        ["round 46: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 46: the gateway routes each request by policy", 24),
        ["round 46: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 46: the gateway routes each request by policy", 32),
        ["round 46: the gateway routes", "each request by policy"],
    ),
    (
        ("round 46: memory grows until the buffer is full", 4),
        ["round", "46:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 46: memory grows until the buffer is full", 8),
        ["round", "46:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 46: memory grows until the buffer is full", 12),
        ["round 46:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 46: memory grows until the buffer is full", 16),
        ["round 46: memory", "grows until the", "buffer is full"],
    ),
    (("round 46: memory grows until the buffer is full", 24), ["round 46: memory grows", "until the buffer is full"]),
    (("round 46: memory grows until the buffer is full", 32), ["round 46: memory grows until the", "buffer is full"]),
    (
        ("round 46: the cluster mirrors every packet twice", 4),
        ["round", "46:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 46: the cluster mirrors every packet twice", 8),
        ["round", "46: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 46: the cluster mirrors every packet twice", 12),
        ["round 46:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 46: the cluster mirrors every packet twice", 16),
        ["round 46: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 46: the cluster mirrors every packet twice", 24),
        ["round 46: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 46: the cluster mirrors every packet twice", 32), ["round 46: the cluster mirrors", "every packet twice"]),
    (
        ("round 46: ranking uses tokens learned from the corpus", 4),
        ["round", "46:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 46: ranking uses tokens learned from the corpus", 8),
        ["round", "46:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 46: ranking uses tokens learned from the corpus", 12),
        ["round 46:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 46: ranking uses tokens learned from the corpus", 16),
        ["round 46:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 46: ranking uses tokens learned from the corpus", 24),
        ["round 46: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 46: ranking uses tokens learned from the corpus", 32),
        ["round 46: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 46: a long session ends when the candle dies", 4),
        ["round", "46:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 46: a long session ends when the candle dies", 8),
        ["round", "46: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 46: a long session ends when the candle dies", 12),
        ["round 46: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 46: a long session ends when the candle dies", 16),
        ["round 46: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 46: a long session ends when the candle dies", 24),
        ["round 46: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 46: a long session ends when the candle dies", 32),
        ["round 46: a long session ends", "when the candle dies"],
    ),
    (
        ("round 46: encode the prompt then map the result", 4),
        ["round", "46:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 46: encode the prompt then map the result", 8),
        ["round", "46:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 46: encode the prompt then map the result", 12),
        ["round 46:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 46: encode the prompt then map the result", 16),
        ["round 46: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 46: encode the prompt then map the result", 24),
        ["round 46: encode the", "prompt then map the", "result"],
    ),
    (("round 46: encode the prompt then map the result", 32), ["round 46: encode the prompt then", "map the result"]),
    (
        ("round 46: the kernel wakes the worker at dawn", 4),
        ["round", "46:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 46: the kernel wakes the worker at dawn", 8),
        ["round", "46: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 46: the kernel wakes the worker at dawn", 12),
        ["round 46:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 46: the kernel wakes the worker at dawn", 16), ["round 46: the", "kernel wakes the", "worker at dawn"]),
    (("round 46: the kernel wakes the worker at dawn", 24), ["round 46: the kernel", "wakes the worker at dawn"]),
    (("round 46: the kernel wakes the worker at dawn", 32), ["round 46: the kernel wakes the", "worker at dawn"]),
    (
        ("round 46: service latency drops after the patch", 4),
        ["round", "46:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 46: service latency drops after the patch", 8),
        ["round", "46:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 46: service latency drops after the patch", 12),
        ["round 46:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 46: service latency drops after the patch", 16),
        ["round 46:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 46: service latency drops after the patch", 24),
        ["round 46: service", "latency drops after the", "patch"],
    ),
    (("round 46: service latency drops after the patch", 32), ["round 46: service latency drops", "after the patch"]),
    (
        ("round 46: the library caches every vector it sees", 4),
        ["round", "46:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 46: the library caches every vector it sees", 8),
        ["round", "46: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 46: the library caches every vector it sees", 12),
        ["round 46:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 46: the library caches every vector it sees", 16),
        ["round 46: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 46: the library caches every vector it sees", 24),
        ["round 46: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 46: the library caches every vector it sees", 32),
        ["round 46: the library caches", "every vector it sees"],
    ),
    (
        ("round 46: agents argue then the debate resolves", 4),
        ["round", "46:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 46: agents argue then the debate resolves", 8),
        ["round", "46:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 46: agents argue then the debate resolves", 12),
        ["round 46:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 46: agents argue then the debate resolves", 16),
        ["round 46: agents", "argue then the", "debate resolves"],
    ),
    (("round 46: agents argue then the debate resolves", 24), ["round 46: agents argue", "then the debate resolves"]),
    (("round 46: agents argue then the debate resolves", 32), ["round 46: agents argue then the", "debate resolves"]),
    (
        ("round 46: the filter keeps only strong matches", 4),
        ["round", "46:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 46: the filter keeps only strong matches", 8),
        ["round", "46: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 46: the filter keeps only strong matches", 12),
        ["round 46:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 46: the filter keeps only strong matches", 16),
        ["round 46: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 46: the filter keeps only strong matches", 24), ["round 46: the filter", "keeps only strong", "matches"]),
    (("round 46: the filter keeps only strong matches", 32), ["round 46: the filter keeps only", "strong matches"]),
    (
        ("round 46: the model answers with a short reply", 4),
        ["round", "46:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 46: the model answers with a short reply", 8),
        ["round", "46: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 46: the model answers with a short reply", 12),
        ["round 46:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 46: the model answers with a short reply", 16),
        ["round 46: the", "model answers", "with a short", "reply"],
    ),
    (("round 46: the model answers with a short reply", 24), ["round 46: the model", "answers with a short", "reply"]),
    (("round 46: the model answers with a short reply", 32), ["round 46: the model answers with", "a short reply"]),
    (
        ("round 46: the recorder stores the reasoning trace", 4),
        ["round", "46:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 46: the recorder stores the reasoning trace", 8),
        ["round", "46: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 46: the recorder stores the reasoning trace", 12),
        ["round 46:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 46: the recorder stores the reasoning trace", 16),
        ["round 46: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 46: the recorder stores the reasoning trace", 24),
        ["round 46: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 46: the recorder stores the reasoning trace", 32),
        ["round 46: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 46: the angel watches the processor run", 4),
        ["round", "46:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 46: the angel watches the processor run", 8),
        ["round", "46: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 46: the angel watches the processor run", 12),
        ["round 46:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 46: the angel watches the processor run", 16), ["round 46: the", "angel watches", "the processor", "run"]),
    (("round 46: the angel watches the processor run", 24), ["round 46: the angel", "watches the processor", "run"]),
    (("round 46: the angel watches the processor run", 32), ["round 46: the angel watches the", "processor run"]),
    (
        ("round 46: angle of the vector decides the match", 4),
        ["round", "46:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 46: angle of the vector decides the match", 8),
        ["round", "46:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 46: angle of the vector decides the match", 12),
        ["round 46:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 46: angle of the vector decides the match", 16),
        ["round 46: angle", "of the vector", "decides the", "match"],
    ),
    (("round 46: angle of the vector decides the match", 24), ["round 46: angle of the", "vector decides the match"]),
    (("round 46: angle of the vector decides the match", 32), ["round 46: angle of the vector", "decides the match"]),
    (
        ("round 46: the candle burns twice as long at night", 4),
        ["round", "46:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 46: the candle burns twice as long at night", 8),
        ["round", "46: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 46: the candle burns twice as long at night", 12),
        ["round 46:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 46: the candle burns twice as long at night", 16),
        ["round 46: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 46: the candle burns twice as long at night", 24),
        ["round 46: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 46: the candle burns twice as long at night", 32),
        ["round 46: the candle burns twice", "as long at night"],
    ),
    (
        ("round 46: a mirror of the universe in one line", 4),
        ["round", "46:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 46: a mirror of the universe in one line", 8),
        ["round", "46: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 46: a mirror of the universe in one line", 12),
        ["round 46: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 46: a mirror of the universe in one line", 16),
        ["round 46: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 46: a mirror of the universe in one line", 24), ["round 46: a mirror of", "the universe in one line"]),
    (("round 46: a mirror of the universe in one line", 32), ["round 46: a mirror of the", "universe in one line"]),
    (
        ("round 46: the queue drains before the storm", 4),
        ["round", "46:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 46: the queue drains before the storm", 8),
        ["round", "46: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 46: the queue drains before the storm", 12), ["round 46:", "the queue", "drains", "before the", "storm"]),
    (("round 46: the queue drains before the storm", 16), ["round 46: the", "queue drains", "before the storm"]),
    (("round 46: the queue drains before the storm", 24), ["round 46: the queue", "drains before the storm"]),
    (("round 46: the queue drains before the storm", 32), ["round 46: the queue drains", "before the storm"]),
    (
        ("kitten46 sitting46 agent46 angle46 universe46 memory46", 6),
        ["kitten46", "sitting46", "agent46", "angle46", "universe46", "memory46"],
    ),
    (
        ("kitten46 sitting46 agent46 angle46 universe46 memory46", 10),
        ["kitten46", "sitting46", "agent46", "angle46", "universe46", "memory46"],
    ),
    (
        ("kitten46 sitting46 agent46 angle46 universe46 memory46", 18),
        ["kitten46 sitting46", "agent46 angle46", "universe46", "memory46"],
    ),
    (
        ("kitten46 sitting46 agent46 angle46 universe46 memory46", 28),
        ["kitten46 sitting46 agent46", "angle46 universe46 memory46"],
    ),
    (
        ("sitting46 agent46 angle46 universe46 memory46 stream46", 6),
        ["sitting46", "agent46", "angle46", "universe46", "memory46", "stream46"],
    ),
    (
        ("sitting46 agent46 angle46 universe46 memory46 stream46", 10),
        ["sitting46", "agent46", "angle46", "universe46", "memory46", "stream46"],
    ),
    (
        ("sitting46 agent46 angle46 universe46 memory46 stream46", 18),
        ["sitting46 agent46", "angle46 universe46", "memory46 stream46"],
    ),
    (
        ("sitting46 agent46 angle46 universe46 memory46 stream46", 28),
        ["sitting46 agent46 angle46", "universe46 memory46 stream46"],
    ),
    (
        ("agent46 angle46 universe46 memory46 stream46 context46", 6),
        ["agent46", "angle46", "universe46", "memory46", "stream46", "context46"],
    ),
    (
        ("agent46 angle46 universe46 memory46 stream46 context46", 10),
        ["agent46", "angle46", "universe46", "memory46", "stream46", "context46"],
    ),
    (
        ("agent46 angle46 universe46 memory46 stream46 context46", 18),
        ["agent46 angle46", "universe46", "memory46 stream46", "context46"],
    ),
    (
        ("agent46 angle46 universe46 memory46 stream46 context46", 28),
        ["agent46 angle46 universe46", "memory46 stream46 context46"],
    ),
    (
        ("angle46 universe46 memory46 stream46 context46 knowledge46", 6),
        ["angle46", "universe46", "memory46", "stream46", "context46", "knowledge46"],
    ),
    (
        ("angle46 universe46 memory46 stream46 context46 knowledge46", 10),
        ["angle46", "universe46", "memory46", "stream46", "context46", "knowledge46"],
    ),
    (
        ("angle46 universe46 memory46 stream46 context46 knowledge46", 18),
        ["angle46 universe46", "memory46 stream46", "context46", "knowledge46"],
    ),
    (
        ("angle46 universe46 memory46 stream46 context46 knowledge46", 28),
        ["angle46 universe46 memory46", "stream46 context46", "knowledge46"],
    ),
    (
        ("universe46 memory46 stream46 context46 knowledge46 vector46", 6),
        ["universe46", "memory46", "stream46", "context46", "knowledge46", "vector46"],
    ),
    (
        ("universe46 memory46 stream46 context46 knowledge46 vector46", 10),
        ["universe46", "memory46", "stream46", "context46", "knowledge46", "vector46"],
    ),
    (
        ("universe46 memory46 stream46 context46 knowledge46 vector46", 18),
        ["universe46", "memory46 stream46", "context46", "knowledge46", "vector46"],
    ),
    (
        ("universe46 memory46 stream46 context46 knowledge46 vector46", 28),
        ["universe46 memory46 stream46", "context46 knowledge46", "vector46"],
    ),
    (
        ("memory46 stream46 context46 knowledge46 vector46 processor46", 6),
        ["memory46", "stream46", "context46", "knowledge46", "vector46", "processor46"],
    ),
    (
        ("memory46 stream46 context46 knowledge46 vector46 processor46", 10),
        ["memory46", "stream46", "context46", "knowledge46", "vector46", "processor46"],
    ),
    (
        ("memory46 stream46 context46 knowledge46 vector46 processor46", 18),
        ["memory46 stream46", "context46", "knowledge46", "vector46", "processor46"],
    ),
    (
        ("memory46 stream46 context46 knowledge46 vector46 processor46", 28),
        ["memory46 stream46 context46", "knowledge46 vector46", "processor46"],
    ),
    (
        ("stream46 context46 knowledge46 vector46 processor46 reasoning46", 6),
        ["stream46", "context46", "knowledge46", "vector46", "processor46", "reasoning46"],
    ),
    (
        ("stream46 context46 knowledge46 vector46 processor46 reasoning46", 10),
        ["stream46", "context46", "knowledge46", "vector46", "processor46", "reasoning46"],
    ),
    (
        ("stream46 context46 knowledge46 vector46 processor46 reasoning46", 18),
        ["stream46 context46", "knowledge46", "vector46", "processor46", "reasoning46"],
    ),
    (
        ("stream46 context46 knowledge46 vector46 processor46 reasoning46", 28),
        ["stream46 context46", "knowledge46 vector46", "processor46 reasoning46"],
    ),
    (
        ("context46 knowledge46 vector46 processor46 reasoning46 machine46", 6),
        ["context46", "knowledge46", "vector46", "processor46", "reasoning46", "machine46"],
    ),
    (
        ("context46 knowledge46 vector46 processor46 reasoning46 machine46", 10),
        ["context46", "knowledge46", "vector46", "processor46", "reasoning46", "machine46"],
    ),
    (
        ("context46 knowledge46 vector46 processor46 reasoning46 machine46", 18),
        ["context46", "knowledge46", "vector46", "processor46", "reasoning46", "machine46"],
    ),
    (
        ("context46 knowledge46 vector46 processor46 reasoning46 machine46", 28),
        ["context46 knowledge46", "vector46 processor46", "reasoning46 machine46"],
    ),
    (
        ("knowledge46 vector46 processor46 reasoning46 machine46 learning46", 6),
        ["knowledge46", "vector46", "processor46", "reasoning46", "machine46", "learning46"],
    ),
    (
        ("knowledge46 vector46 processor46 reasoning46 machine46 learning46", 10),
        ["knowledge46", "vector46", "processor46", "reasoning46", "machine46", "learning46"],
    ),
    (
        ("knowledge46 vector46 processor46 reasoning46 machine46 learning46", 18),
        ["knowledge46", "vector46", "processor46", "reasoning46", "machine46", "learning46"],
    ),
    (
        ("knowledge46 vector46 processor46 reasoning46 machine46 learning46", 28),
        ["knowledge46 vector46", "processor46 reasoning46", "machine46 learning46"],
    ),
    (
        ("vector46 processor46 reasoning46 machine46 learning46 model46", 6),
        ["vector46", "processor46", "reasoning46", "machine46", "learning46", "model46"],
    ),
    (
        ("vector46 processor46 reasoning46 machine46 learning46 model46", 10),
        ["vector46", "processor46", "reasoning46", "machine46", "learning46", "model46"],
    ),
    (
        ("vector46 processor46 reasoning46 machine46 learning46 model46", 18),
        ["vector46", "processor46", "reasoning46", "machine46", "learning46 model46"],
    ),
    (
        ("vector46 processor46 reasoning46 machine46 learning46 model46", 28),
        ["vector46 processor46", "reasoning46 machine46", "learning46 model46"],
    ),
    (
        ("processor46 reasoning46 machine46 learning46 model46 token46", 6),
        ["processor46", "reasoning46", "machine46", "learning46", "model46", "token46"],
    ),
    (
        ("processor46 reasoning46 machine46 learning46 model46 token46", 10),
        ["processor46", "reasoning46", "machine46", "learning46", "model46", "token46"],
    ),
    (
        ("processor46 reasoning46 machine46 learning46 model46 token46", 18),
        ["processor46", "reasoning46", "machine46", "learning46 model46", "token46"],
    ),
    (
        ("processor46 reasoning46 machine46 learning46 model46 token46", 28),
        ["processor46 reasoning46", "machine46 learning46 model46", "token46"],
    ),
    (
        ("reasoning46 machine46 learning46 model46 token46 prompt46", 6),
        ["reasoning46", "machine46", "learning46", "model46", "token46", "prompt46"],
    ),
    (
        ("reasoning46 machine46 learning46 model46 token46 prompt46", 10),
        ["reasoning46", "machine46", "learning46", "model46", "token46", "prompt46"],
    ),
    (
        ("reasoning46 machine46 learning46 model46 token46 prompt46", 18),
        ["reasoning46", "machine46", "learning46 model46", "token46 prompt46"],
    ),
    (
        ("reasoning46 machine46 learning46 model46 token46 prompt46", 28),
        ["reasoning46 machine46", "learning46 model46 token46", "prompt46"],
    ),
    (
        ("machine46 learning46 model46 token46 prompt46 session46", 6),
        ["machine46", "learning46", "model46", "token46", "prompt46", "session46"],
    ),
    (
        ("machine46 learning46 model46 token46 prompt46 session46", 10),
        ["machine46", "learning46", "model46", "token46", "prompt46", "session46"],
    ),
    (
        ("machine46 learning46 model46 token46 prompt46 session46", 18),
        ["machine46", "learning46 model46", "token46 prompt46", "session46"],
    ),
    (
        ("machine46 learning46 model46 token46 prompt46 session46", 28),
        ["machine46 learning46 model46", "token46 prompt46 session46"],
    ),
    (
        ("learning46 model46 token46 prompt46 session46 library46", 6),
        ["learning46", "model46", "token46", "prompt46", "session46", "library46"],
    ),
    (
        ("learning46 model46 token46 prompt46 session46 library46", 10),
        ["learning46", "model46", "token46", "prompt46", "session46", "library46"],
    ),
    (
        ("learning46 model46 token46 prompt46 session46 library46", 18),
        ["learning46 model46", "token46 prompt46", "session46", "library46"],
    ),
    (
        ("learning46 model46 token46 prompt46 session46 library46", 28),
        ["learning46 model46 token46", "prompt46 session46 library46"],
    ),
    (
        ("model46 token46 prompt46 session46 library46 service46", 6),
        ["model46", "token46", "prompt46", "session46", "library46", "service46"],
    ),
    (
        ("model46 token46 prompt46 session46 library46 service46", 10),
        ["model46", "token46", "prompt46", "session46", "library46", "service46"],
    ),
    (
        ("model46 token46 prompt46 session46 library46 service46", 18),
        ["model46 token46", "prompt46 session46", "library46", "service46"],
    ),
    (
        ("model46 token46 prompt46 session46 library46 service46", 28),
        ["model46 token46 prompt46", "session46 library46", "service46"],
    ),
    (
        ("token46 prompt46 session46 library46 service46 gateway46", 6),
        ["token46", "prompt46", "session46", "library46", "service46", "gateway46"],
    ),
    (
        ("token46 prompt46 session46 library46 service46 gateway46", 10),
        ["token46", "prompt46", "session46", "library46", "service46", "gateway46"],
    ),
    (
        ("token46 prompt46 session46 library46 service46 gateway46", 18),
        ["token46 prompt46", "session46", "library46", "service46", "gateway46"],
    ),
    (
        ("token46 prompt46 session46 library46 service46 gateway46", 28),
        ["token46 prompt46 session46", "library46 service46", "gateway46"],
    ),
    (
        ("prompt46 session46 library46 service46 gateway46 storage46", 6),
        ["prompt46", "session46", "library46", "service46", "gateway46", "storage46"],
    ),
    (
        ("prompt46 session46 library46 service46 gateway46 storage46", 10),
        ["prompt46", "session46", "library46", "service46", "gateway46", "storage46"],
    ),
    (
        ("prompt46 session46 library46 service46 gateway46 storage46", 18),
        ["prompt46 session46", "library46", "service46", "gateway46", "storage46"],
    ),
    (
        ("prompt46 session46 library46 service46 gateway46 storage46", 28),
        ["prompt46 session46 library46", "service46 gateway46", "storage46"],
    ),
    (
        ("session46 library46 service46 gateway46 storage46 network46", 6),
        ["session46", "library46", "service46", "gateway46", "storage46", "network46"],
    ),
    (
        ("session46 library46 service46 gateway46 storage46 network46", 10),
        ["session46", "library46", "service46", "gateway46", "storage46", "network46"],
    ),
    (
        ("session46 library46 service46 gateway46 storage46 network46", 18),
        ["session46", "library46", "service46", "gateway46", "storage46", "network46"],
    ),
    (
        ("session46 library46 service46 gateway46 storage46 network46", 28),
        ["session46 library46", "service46 gateway46", "storage46 network46"],
    ),
    (
        ("library46 service46 gateway46 storage46 network46 latency46", 6),
        ["library46", "service46", "gateway46", "storage46", "network46", "latency46"],
    ),
    (
        ("library46 service46 gateway46 storage46 network46 latency46", 10),
        ["library46", "service46", "gateway46", "storage46", "network46", "latency46"],
    ),
    (
        ("library46 service46 gateway46 storage46 network46 latency46", 18),
        ["library46", "service46", "gateway46", "storage46", "network46", "latency46"],
    ),
    (
        ("library46 service46 gateway46 storage46 network46 latency46", 28),
        ["library46 service46", "gateway46 storage46", "network46 latency46"],
    ),
    (
        ("service46 gateway46 storage46 network46 latency46 buffer46", 6),
        ["service46", "gateway46", "storage46", "network46", "latency46", "buffer46"],
    ),
    (
        ("service46 gateway46 storage46 network46 latency46 buffer46", 10),
        ["service46", "gateway46", "storage46", "network46", "latency46", "buffer46"],
    ),
    (
        ("service46 gateway46 storage46 network46 latency46 buffer46", 18),
        ["service46", "gateway46", "storage46", "network46", "latency46 buffer46"],
    ),
    (
        ("service46 gateway46 storage46 network46 latency46 buffer46", 28),
        ["service46 gateway46", "storage46 network46", "latency46 buffer46"],
    ),
    (
        ("gateway46 storage46 network46 latency46 buffer46 queue46", 6),
        ["gateway46", "storage46", "network46", "latency46", "buffer46", "queue46"],
    ),
    (
        ("gateway46 storage46 network46 latency46 buffer46 queue46", 10),
        ["gateway46", "storage46", "network46", "latency46", "buffer46", "queue46"],
    ),
    (
        ("gateway46 storage46 network46 latency46 buffer46 queue46", 18),
        ["gateway46", "storage46", "network46", "latency46 buffer46", "queue46"],
    ),
    (
        ("gateway46 storage46 network46 latency46 buffer46 queue46", 28),
        ["gateway46 storage46", "network46 latency46 buffer46", "queue46"],
    ),
    (
        ("storage46 network46 latency46 buffer46 queue46 worker46", 6),
        ["storage46", "network46", "latency46", "buffer46", "queue46", "worker46"],
    ),
    (
        ("storage46 network46 latency46 buffer46 queue46 worker46", 10),
        ["storage46", "network46", "latency46", "buffer46", "queue46", "worker46"],
    ),
    (
        ("storage46 network46 latency46 buffer46 queue46 worker46", 18),
        ["storage46", "network46", "latency46 buffer46", "queue46 worker46"],
    ),
    (
        ("storage46 network46 latency46 buffer46 queue46 worker46", 28),
        ["storage46 network46", "latency46 buffer46 queue46", "worker46"],
    ),
    (
        ("network46 latency46 buffer46 queue46 worker46 kernel46", 6),
        ["network46", "latency46", "buffer46", "queue46", "worker46", "kernel46"],
    ),
    (
        ("network46 latency46 buffer46 queue46 worker46 kernel46", 10),
        ["network46", "latency46", "buffer46", "queue46", "worker46", "kernel46"],
    ),
    (
        ("network46 latency46 buffer46 queue46 worker46 kernel46", 18),
        ["network46", "latency46 buffer46", "queue46 worker46", "kernel46"],
    ),
    (
        ("network46 latency46 buffer46 queue46 worker46 kernel46", 28),
        ["network46 latency46 buffer46", "queue46 worker46 kernel46"],
    ),
    (
        ("latency46 buffer46 queue46 worker46 kernel46 signal46", 6),
        ["latency46", "buffer46", "queue46", "worker46", "kernel46", "signal46"],
    ),
    (
        ("latency46 buffer46 queue46 worker46 kernel46 signal46", 10),
        ["latency46", "buffer46", "queue46", "worker46", "kernel46", "signal46"],
    ),
    (
        ("latency46 buffer46 queue46 worker46 kernel46 signal46", 18),
        ["latency46 buffer46", "queue46 worker46", "kernel46 signal46"],
    ),
    (
        ("latency46 buffer46 queue46 worker46 kernel46 signal46", 28),
        ["latency46 buffer46 queue46", "worker46 kernel46 signal46"],
    ),
    (
        ("buffer46 queue46 worker46 kernel46 signal46 packet46", 6),
        ["buffer46", "queue46", "worker46", "kernel46", "signal46", "packet46"],
    ),
    (
        ("buffer46 queue46 worker46 kernel46 signal46 packet46", 10),
        ["buffer46", "queue46", "worker46", "kernel46", "signal46", "packet46"],
    ),
    (
        ("buffer46 queue46 worker46 kernel46 signal46 packet46", 18),
        ["buffer46 queue46", "worker46 kernel46", "signal46 packet46"],
    ),
    (
        ("buffer46 queue46 worker46 kernel46 signal46 packet46", 28),
        ["buffer46 queue46 worker46", "kernel46 signal46 packet46"],
    ),
    (
        ("queue46 worker46 kernel46 signal46 packet46 router46", 6),
        ["queue46", "worker46", "kernel46", "signal46", "packet46", "router46"],
    ),
    (
        ("queue46 worker46 kernel46 signal46 packet46 router46", 10),
        ["queue46", "worker46", "kernel46", "signal46", "packet46", "router46"],
    ),
    (
        ("queue46 worker46 kernel46 signal46 packet46 router46", 18),
        ["queue46 worker46", "kernel46 signal46", "packet46 router46"],
    ),
    (
        ("queue46 worker46 kernel46 signal46 packet46 router46", 28),
        ["queue46 worker46 kernel46", "signal46 packet46 router46"],
    ),
    (
        ("worker46 kernel46 signal46 packet46 router46 cluster46", 6),
        ["worker46", "kernel46", "signal46", "packet46", "router46", "cluster46"],
    ),
    (
        ("worker46 kernel46 signal46 packet46 router46 cluster46", 10),
        ["worker46", "kernel46", "signal46", "packet46", "router46", "cluster46"],
    ),
    (
        ("worker46 kernel46 signal46 packet46 router46 cluster46", 18),
        ["worker46 kernel46", "signal46 packet46", "router46 cluster46"],
    ),
    (
        ("worker46 kernel46 signal46 packet46 router46 cluster46", 28),
        ["worker46 kernel46 signal46", "packet46 router46 cluster46"],
    ),
    (
        ("kernel46 signal46 packet46 router46 cluster46 mirror46", 6),
        ["kernel46", "signal46", "packet46", "router46", "cluster46", "mirror46"],
    ),
    (
        ("kernel46 signal46 packet46 router46 cluster46 mirror46", 10),
        ["kernel46", "signal46", "packet46", "router46", "cluster46", "mirror46"],
    ),
    (
        ("kernel46 signal46 packet46 router46 cluster46 mirror46", 18),
        ["kernel46 signal46", "packet46 router46", "cluster46 mirror46"],
    ),
    (
        ("kernel46 signal46 packet46 router46 cluster46 mirror46", 28),
        ["kernel46 signal46 packet46", "router46 cluster46 mirror46"],
    ),
    (
        ("signal46 packet46 router46 cluster46 mirror46 filter46", 6),
        ["signal46", "packet46", "router46", "cluster46", "mirror46", "filter46"],
    ),
    (
        ("signal46 packet46 router46 cluster46 mirror46 filter46", 10),
        ["signal46", "packet46", "router46", "cluster46", "mirror46", "filter46"],
    ),
    (
        ("signal46 packet46 router46 cluster46 mirror46 filter46", 18),
        ["signal46 packet46", "router46 cluster46", "mirror46 filter46"],
    ),
    (
        ("signal46 packet46 router46 cluster46 mirror46 filter46", 28),
        ["signal46 packet46 router46", "cluster46 mirror46 filter46"],
    ),
    (
        ("packet46 router46 cluster46 mirror46 filter46 ranking46", 6),
        ["packet46", "router46", "cluster46", "mirror46", "filter46", "ranking46"],
    ),
    (
        ("packet46 router46 cluster46 mirror46 filter46 ranking46", 10),
        ["packet46", "router46", "cluster46", "mirror46", "filter46", "ranking46"],
    ),
    (
        ("packet46 router46 cluster46 mirror46 filter46 ranking46", 18),
        ["packet46 router46", "cluster46 mirror46", "filter46 ranking46"],
    ),
    (
        ("packet46 router46 cluster46 mirror46 filter46 ranking46", 28),
        ["packet46 router46 cluster46", "mirror46 filter46 ranking46"],
    ),
    (
        ("router46 cluster46 mirror46 filter46 ranking46 encoding46", 6),
        ["router46", "cluster46", "mirror46", "filter46", "ranking46", "encoding46"],
    ),
    (
        ("router46 cluster46 mirror46 filter46 ranking46 encoding46", 10),
        ["router46", "cluster46", "mirror46", "filter46", "ranking46", "encoding46"],
    ),
    (
        ("router46 cluster46 mirror46 filter46 ranking46 encoding46", 18),
        ["router46 cluster46", "mirror46 filter46", "ranking46", "encoding46"],
    ),
    (
        ("router46 cluster46 mirror46 filter46 ranking46 encoding46", 28),
        ["router46 cluster46 mirror46", "filter46 ranking46", "encoding46"],
    ),
    (
        ("cluster46 mirror46 filter46 ranking46 encoding46 mapping46", 6),
        ["cluster46", "mirror46", "filter46", "ranking46", "encoding46", "mapping46"],
    ),
    (
        ("cluster46 mirror46 filter46 ranking46 encoding46 mapping46", 10),
        ["cluster46", "mirror46", "filter46", "ranking46", "encoding46", "mapping46"],
    ),
    (
        ("cluster46 mirror46 filter46 ranking46 encoding46 mapping46", 18),
        ["cluster46 mirror46", "filter46 ranking46", "encoding46", "mapping46"],
    ),
    (
        ("cluster46 mirror46 filter46 ranking46 encoding46 mapping46", 28),
        ["cluster46 mirror46 filter46", "ranking46 encoding46", "mapping46"],
    ),
    (
        ("mirror46 filter46 ranking46 encoding46 mapping46 record46", 6),
        ["mirror46", "filter46", "ranking46", "encoding46", "mapping46", "record46"],
    ),
    (
        ("mirror46 filter46 ranking46 encoding46 mapping46 record46", 10),
        ["mirror46", "filter46", "ranking46", "encoding46", "mapping46", "record46"],
    ),
    (
        ("mirror46 filter46 ranking46 encoding46 mapping46 record46", 18),
        ["mirror46 filter46", "ranking46", "encoding46", "mapping46 record46"],
    ),
    (
        ("mirror46 filter46 ranking46 encoding46 mapping46 record46", 28),
        ["mirror46 filter46 ranking46", "encoding46 mapping46", "record46"],
    ),
    (
        ("filter46 ranking46 encoding46 mapping46 record46 candle46", 6),
        ["filter46", "ranking46", "encoding46", "mapping46", "record46", "candle46"],
    ),
    (
        ("filter46 ranking46 encoding46 mapping46 record46 candle46", 10),
        ["filter46", "ranking46", "encoding46", "mapping46", "record46", "candle46"],
    ),
    (
        ("filter46 ranking46 encoding46 mapping46 record46 candle46", 18),
        ["filter46 ranking46", "encoding46", "mapping46 record46", "candle46"],
    ),
    (
        ("filter46 ranking46 encoding46 mapping46 record46 candle46", 28),
        ["filter46 ranking46", "encoding46 mapping46", "record46 candle46"],
    ),
    (
        ("ranking46 encoding46 mapping46 record46 candle46 thread46", 6),
        ["ranking46", "encoding46", "mapping46", "record46", "candle46", "thread46"],
    ),
    (
        ("ranking46 encoding46 mapping46 record46 candle46 thread46", 10),
        ["ranking46", "encoding46", "mapping46", "record46", "candle46", "thread46"],
    ),
    (
        ("ranking46 encoding46 mapping46 record46 candle46 thread46", 18),
        ["ranking46", "encoding46", "mapping46 record46", "candle46 thread46"],
    ),
    (
        ("ranking46 encoding46 mapping46 record46 candle46 thread46", 28),
        ["ranking46 encoding46", "mapping46 record46 candle46", "thread46"],
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
