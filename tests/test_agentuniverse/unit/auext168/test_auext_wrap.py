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
        ("round 168: the quick brown fox jumps over the lazy dog", 4),
        ["round", "168:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", 8),
        ["round", "168: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", 12),
        ["round 168:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", 16),
        ["round 168: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", 24),
        ["round 168: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 168: the quick brown fox jumps over the lazy dog", 32),
        ["round 168: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", 4),
        ["round", "168:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", 8),
        ["round", "168:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", 12),
        ["round 168:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", 16),
        ["round 168:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", 24),
        ["round 168: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 168: agentuniverse is a framework for multi agents", 32),
        ["round 168: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", 4),
        ["round", "168:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", 8),
        ["round", "168:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", 12),
        ["round 168:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", 16),
        ["round 168:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", 24),
        ["round 168: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 168: knowledge stored as vectors enables retrieval", 32),
        ["round 168: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 168: the processor reads the record then stops", 4),
        ["round", "168:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 168: the processor reads the record then stops", 8),
        ["round", "168: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 168: the processor reads the record then stops", 12),
        ["round 168:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 168: the processor reads the record then stops", 16),
        ["round 168: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 168: the processor reads the record then stops", 24),
        ["round 168: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 168: the processor reads the record then stops", 32),
        ["round 168: the processor reads", "the record then stops"],
    ),
    (
        ("round 168: a worker pulls the next task from the queue", 4),
        ["round", "168:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 168: a worker pulls the next task from the queue", 8),
        ["round", "168: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 168: a worker pulls the next task from the queue", 12),
        ["round 168: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 168: a worker pulls the next task from the queue", 16),
        ["round 168: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 168: a worker pulls the next task from the queue", 24),
        ["round 168: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 168: a worker pulls the next task from the queue", 32),
        ["round 168: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 168: signals travel through the network layer", 4),
        ["round", "168:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 168: signals travel through the network layer", 8),
        ["round", "168:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 168: signals travel through the network layer", 12),
        ["round 168:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 168: signals travel through the network layer", 16),
        ["round 168:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 168: signals travel through the network layer", 24),
        ["round 168: signals", "travel through the", "network layer"],
    ),
    (
        ("round 168: signals travel through the network layer", 32),
        ["round 168: signals travel", "through the network layer"],
    ),
    (
        ("round 168: the gateway routes each request by policy", 4),
        ["round", "168:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 168: the gateway routes each request by policy", 8),
        ["round", "168: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 168: the gateway routes each request by policy", 12),
        ["round 168:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 168: the gateway routes each request by policy", 16),
        ["round 168: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 168: the gateway routes each request by policy", 24),
        ["round 168: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 168: the gateway routes each request by policy", 32),
        ["round 168: the gateway routes", "each request by policy"],
    ),
    (
        ("round 168: memory grows until the buffer is full", 4),
        ["round", "168:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 168: memory grows until the buffer is full", 8),
        ["round", "168:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 168: memory grows until the buffer is full", 12),
        ["round 168:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 168: memory grows until the buffer is full", 16),
        ["round 168:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 168: memory grows until the buffer is full", 24), ["round 168: memory grows", "until the buffer is full"]),
    (("round 168: memory grows until the buffer is full", 32), ["round 168: memory grows until", "the buffer is full"]),
    (
        ("round 168: the cluster mirrors every packet twice", 4),
        ["round", "168:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 168: the cluster mirrors every packet twice", 8),
        ["round", "168: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 168: the cluster mirrors every packet twice", 12),
        ["round 168:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 168: the cluster mirrors every packet twice", 16),
        ["round 168: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 168: the cluster mirrors every packet twice", 24),
        ["round 168: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 168: the cluster mirrors every packet twice", 32),
        ["round 168: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", 4),
        ["round", "168:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", 8),
        ["round", "168:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", 12),
        ["round 168:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", 16),
        ["round 168:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", 24),
        ["round 168: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 168: ranking uses tokens learned from the corpus", 32),
        ["round 168: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 168: a long session ends when the candle dies", 4),
        ["round", "168:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 168: a long session ends when the candle dies", 8),
        ["round", "168: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 168: a long session ends when the candle dies", 12),
        ["round 168: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 168: a long session ends when the candle dies", 16),
        ["round 168: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 168: a long session ends when the candle dies", 24),
        ["round 168: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 168: a long session ends when the candle dies", 32),
        ["round 168: a long session ends", "when the candle dies"],
    ),
    (
        ("round 168: encode the prompt then map the result", 4),
        ["round", "168:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 168: encode the prompt then map the result", 8),
        ["round", "168:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 168: encode the prompt then map the result", 12),
        ["round 168:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 168: encode the prompt then map the result", 16),
        ["round 168:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 168: encode the prompt then map the result", 24),
        ["round 168: encode the", "prompt then map the", "result"],
    ),
    (("round 168: encode the prompt then map the result", 32), ["round 168: encode the prompt", "then map the result"]),
    (
        ("round 168: the kernel wakes the worker at dawn", 4),
        ["round", "168:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 168: the kernel wakes the worker at dawn", 8),
        ["round", "168: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 168: the kernel wakes the worker at dawn", 12),
        ["round 168:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 168: the kernel wakes the worker at dawn", 16), ["round 168: the", "kernel wakes the", "worker at dawn"]),
    (("round 168: the kernel wakes the worker at dawn", 24), ["round 168: the kernel", "wakes the worker at dawn"]),
    (("round 168: the kernel wakes the worker at dawn", 32), ["round 168: the kernel wakes the", "worker at dawn"]),
    (
        ("round 168: service latency drops after the patch", 4),
        ["round", "168:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 168: service latency drops after the patch", 8),
        ["round", "168:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 168: service latency drops after the patch", 12),
        ["round 168:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 168: service latency drops after the patch", 16),
        ["round 168:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 168: service latency drops after the patch", 24),
        ["round 168: service", "latency drops after the", "patch"],
    ),
    (("round 168: service latency drops after the patch", 32), ["round 168: service latency drops", "after the patch"]),
    (
        ("round 168: the library caches every vector it sees", 4),
        ["round", "168:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 168: the library caches every vector it sees", 8),
        ["round", "168: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 168: the library caches every vector it sees", 12),
        ["round 168:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 168: the library caches every vector it sees", 16),
        ["round 168: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 168: the library caches every vector it sees", 24),
        ["round 168: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 168: the library caches every vector it sees", 32),
        ["round 168: the library caches", "every vector it sees"],
    ),
    (
        ("round 168: agents argue then the debate resolves", 4),
        ["round", "168:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 168: agents argue then the debate resolves", 8),
        ["round", "168:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 168: agents argue then the debate resolves", 12),
        ["round 168:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 168: agents argue then the debate resolves", 16),
        ["round 168:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 168: agents argue then the debate resolves", 24), ["round 168: agents argue", "then the debate resolves"]),
    (("round 168: agents argue then the debate resolves", 32), ["round 168: agents argue then the", "debate resolves"]),
    (
        ("round 168: the filter keeps only strong matches", 4),
        ["round", "168:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 168: the filter keeps only strong matches", 8),
        ["round", "168: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 168: the filter keeps only strong matches", 12),
        ["round 168:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 168: the filter keeps only strong matches", 16),
        ["round 168: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 168: the filter keeps only strong matches", 24),
        ["round 168: the filter", "keeps only strong", "matches"],
    ),
    (("round 168: the filter keeps only strong matches", 32), ["round 168: the filter keeps only", "strong matches"]),
    (
        ("round 168: the model answers with a short reply", 4),
        ["round", "168:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 168: the model answers with a short reply", 8),
        ["round", "168: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 168: the model answers with a short reply", 12),
        ["round 168:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 168: the model answers with a short reply", 16),
        ["round 168: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 168: the model answers with a short reply", 24),
        ["round 168: the model", "answers with a short", "reply"],
    ),
    (("round 168: the model answers with a short reply", 32), ["round 168: the model answers", "with a short reply"]),
    (
        ("round 168: the recorder stores the reasoning trace", 4),
        ["round", "168:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 168: the recorder stores the reasoning trace", 8),
        ["round", "168: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 168: the recorder stores the reasoning trace", 12),
        ["round 168:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 168: the recorder stores the reasoning trace", 16),
        ["round 168: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 168: the recorder stores the reasoning trace", 24),
        ["round 168: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 168: the recorder stores the reasoning trace", 32),
        ["round 168: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 168: the angel watches the processor run", 4),
        ["round", "168:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 168: the angel watches the processor run", 8),
        ["round", "168: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 168: the angel watches the processor run", 12),
        ["round 168:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 168: the angel watches the processor run", 16),
        ["round 168: the", "angel watches", "the processor", "run"],
    ),
    (("round 168: the angel watches the processor run", 24), ["round 168: the angel", "watches the processor", "run"]),
    (("round 168: the angel watches the processor run", 32), ["round 168: the angel watches the", "processor run"]),
    (
        ("round 168: angle of the vector decides the match", 4),
        ["round", "168:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 168: angle of the vector decides the match", 8),
        ["round", "168:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 168: angle of the vector decides the match", 12),
        ["round 168:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 168: angle of the vector decides the match", 16),
        ["round 168: angle", "of the vector", "decides the", "match"],
    ),
    (("round 168: angle of the vector decides the match", 24), ["round 168: angle of the", "vector decides the match"]),
    (("round 168: angle of the vector decides the match", 32), ["round 168: angle of the vector", "decides the match"]),
    (
        ("round 168: the candle burns twice as long at night", 4),
        ["round", "168:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 168: the candle burns twice as long at night", 8),
        ["round", "168: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 168: the candle burns twice as long at night", 12),
        ["round 168:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 168: the candle burns twice as long at night", 16),
        ["round 168: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 168: the candle burns twice as long at night", 24),
        ["round 168: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 168: the candle burns twice as long at night", 32),
        ["round 168: the candle burns", "twice as long at night"],
    ),
    (
        ("round 168: a mirror of the universe in one line", 4),
        ["round", "168:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 168: a mirror of the universe in one line", 8),
        ["round", "168: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 168: a mirror of the universe in one line", 12),
        ["round 168: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 168: a mirror of the universe in one line", 16),
        ["round 168: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 168: a mirror of the universe in one line", 24), ["round 168: a mirror of", "the universe in one line"]),
    (("round 168: a mirror of the universe in one line", 32), ["round 168: a mirror of the", "universe in one line"]),
    (
        ("round 168: the queue drains before the storm", 4),
        ["round", "168:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 168: the queue drains before the storm", 8),
        ["round", "168: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 168: the queue drains before the storm", 12),
        ["round 168:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 168: the queue drains before the storm", 16), ["round 168: the", "queue drains", "before the storm"]),
    (("round 168: the queue drains before the storm", 24), ["round 168: the queue", "drains before the storm"]),
    (("round 168: the queue drains before the storm", 32), ["round 168: the queue drains", "before the storm"]),
    (
        ("kitten168 sitting168 agent168 angle168 universe168 memory168", 6),
        ["kitten168", "sitting168", "agent168", "angle168", "universe168", "memory168"],
    ),
    (
        ("kitten168 sitting168 agent168 angle168 universe168 memory168", 10),
        ["kitten168", "sitting168", "agent168", "angle168", "universe168", "memory168"],
    ),
    (
        ("kitten168 sitting168 agent168 angle168 universe168 memory168", 18),
        ["kitten168", "sitting168", "agent168 angle168", "universe168", "memory168"],
    ),
    (
        ("kitten168 sitting168 agent168 angle168 universe168 memory168", 28),
        ["kitten168 sitting168", "agent168 angle168", "universe168 memory168"],
    ),
    (
        ("sitting168 agent168 angle168 universe168 memory168 stream168", 6),
        ["sitting168", "agent168", "angle168", "universe168", "memory168", "stream168"],
    ),
    (
        ("sitting168 agent168 angle168 universe168 memory168 stream168", 10),
        ["sitting168", "agent168", "angle168", "universe168", "memory168", "stream168"],
    ),
    (
        ("sitting168 agent168 angle168 universe168 memory168 stream168", 18),
        ["sitting168", "agent168 angle168", "universe168", "memory168", "stream168"],
    ),
    (
        ("sitting168 agent168 angle168 universe168 memory168 stream168", 28),
        ["sitting168 agent168 angle168", "universe168 memory168", "stream168"],
    ),
    (
        ("agent168 angle168 universe168 memory168 stream168 context168", 6),
        ["agent168", "angle168", "universe168", "memory168", "stream168", "context168"],
    ),
    (
        ("agent168 angle168 universe168 memory168 stream168 context168", 10),
        ["agent168", "angle168", "universe168", "memory168", "stream168", "context168"],
    ),
    (
        ("agent168 angle168 universe168 memory168 stream168 context168", 18),
        ["agent168 angle168", "universe168", "memory168", "stream168", "context168"],
    ),
    (
        ("agent168 angle168 universe168 memory168 stream168 context168", 28),
        ["agent168 angle168", "universe168 memory168", "stream168 context168"],
    ),
    (
        ("angle168 universe168 memory168 stream168 context168 knowledge168", 6),
        ["angle168", "universe168", "memory168", "stream168", "context168", "knowledge168"],
    ),
    (
        ("angle168 universe168 memory168 stream168 context168 knowledge168", 10),
        ["angle168", "universe168", "memory168", "stream168", "context168", "knowledge168"],
    ),
    (
        ("angle168 universe168 memory168 stream168 context168 knowledge168", 18),
        ["angle168", "universe168", "memory168", "stream168", "context168", "knowledge168"],
    ),
    (
        ("angle168 universe168 memory168 stream168 context168 knowledge168", 28),
        ["angle168 universe168", "memory168 stream168", "context168 knowledge168"],
    ),
    (
        ("universe168 memory168 stream168 context168 knowledge168 vector168", 6),
        ["universe168", "memory168", "stream168", "context168", "knowledge168", "vector168"],
    ),
    (
        ("universe168 memory168 stream168 context168 knowledge168 vector168", 10),
        ["universe168", "memory168", "stream168", "context168", "knowledge168", "vector168"],
    ),
    (
        ("universe168 memory168 stream168 context168 knowledge168 vector168", 18),
        ["universe168", "memory168", "stream168", "context168", "knowledge168", "vector168"],
    ),
    (
        ("universe168 memory168 stream168 context168 knowledge168 vector168", 28),
        ["universe168 memory168", "stream168 context168", "knowledge168 vector168"],
    ),
    (
        ("memory168 stream168 context168 knowledge168 vector168 processor168", 6),
        ["memory168", "stream168", "context168", "knowledge168", "vector168", "processor168"],
    ),
    (
        ("memory168 stream168 context168 knowledge168 vector168 processor168", 10),
        ["memory168", "stream168", "context168", "knowledge168", "vector168", "processor168"],
    ),
    (
        ("memory168 stream168 context168 knowledge168 vector168 processor168", 18),
        ["memory168", "stream168", "context168", "knowledge168", "vector168", "processor168"],
    ),
    (
        ("memory168 stream168 context168 knowledge168 vector168 processor168", 28),
        ["memory168 stream168", "context168 knowledge168", "vector168 processor168"],
    ),
    (
        ("stream168 context168 knowledge168 vector168 processor168 reasoning168", 6),
        ["stream168", "context168", "knowledge168", "vector168", "processor168", "reasoning168"],
    ),
    (
        ("stream168 context168 knowledge168 vector168 processor168 reasoning168", 10),
        ["stream168", "context168", "knowledge168", "vector168", "processor168", "reasoning168"],
    ),
    (
        ("stream168 context168 knowledge168 vector168 processor168 reasoning168", 18),
        ["stream168", "context168", "knowledge168", "vector168", "processor168", "reasoning168"],
    ),
    (
        ("stream168 context168 knowledge168 vector168 processor168 reasoning168", 28),
        ["stream168 context168", "knowledge168 vector168", "processor168 reasoning168"],
    ),
    (
        ("context168 knowledge168 vector168 processor168 reasoning168 machine168", 6),
        ["context168", "knowledge168", "vector168", "processor168", "reasoning168", "machine168"],
    ),
    (
        ("context168 knowledge168 vector168 processor168 reasoning168 machine168", 10),
        ["context168", "knowledge168", "vector168", "processor168", "reasoning168", "machine168"],
    ),
    (
        ("context168 knowledge168 vector168 processor168 reasoning168 machine168", 18),
        ["context168", "knowledge168", "vector168", "processor168", "reasoning168", "machine168"],
    ),
    (
        ("context168 knowledge168 vector168 processor168 reasoning168 machine168", 28),
        ["context168 knowledge168", "vector168 processor168", "reasoning168 machine168"],
    ),
    (
        ("knowledge168 vector168 processor168 reasoning168 machine168 learning168", 6),
        ["knowledge168", "vector168", "processor168", "reasoning168", "machine168", "learning168"],
    ),
    (
        ("knowledge168 vector168 processor168 reasoning168 machine168 learning168", 10),
        ["knowledge168", "vector168", "processor168", "reasoning168", "machine168", "learning168"],
    ),
    (
        ("knowledge168 vector168 processor168 reasoning168 machine168 learning168", 18),
        ["knowledge168", "vector168", "processor168", "reasoning168", "machine168", "learning168"],
    ),
    (
        ("knowledge168 vector168 processor168 reasoning168 machine168 learning168", 28),
        ["knowledge168 vector168", "processor168 reasoning168", "machine168 learning168"],
    ),
    (
        ("vector168 processor168 reasoning168 machine168 learning168 model168", 6),
        ["vector168", "processor168", "reasoning168", "machine168", "learning168", "model168"],
    ),
    (
        ("vector168 processor168 reasoning168 machine168 learning168 model168", 10),
        ["vector168", "processor168", "reasoning168", "machine168", "learning168", "model168"],
    ),
    (
        ("vector168 processor168 reasoning168 machine168 learning168 model168", 18),
        ["vector168", "processor168", "reasoning168", "machine168", "learning168", "model168"],
    ),
    (
        ("vector168 processor168 reasoning168 machine168 learning168 model168", 28),
        ["vector168 processor168", "reasoning168 machine168", "learning168 model168"],
    ),
    (
        ("processor168 reasoning168 machine168 learning168 model168 token168", 6),
        ["processor168", "reasoning168", "machine168", "learning168", "model168", "token168"],
    ),
    (
        ("processor168 reasoning168 machine168 learning168 model168 token168", 10),
        ["processor168", "reasoning168", "machine168", "learning168", "model168", "token168"],
    ),
    (
        ("processor168 reasoning168 machine168 learning168 model168 token168", 18),
        ["processor168", "reasoning168", "machine168", "learning168", "model168 token168"],
    ),
    (
        ("processor168 reasoning168 machine168 learning168 model168 token168", 28),
        ["processor168 reasoning168", "machine168 learning168", "model168 token168"],
    ),
    (
        ("reasoning168 machine168 learning168 model168 token168 prompt168", 6),
        ["reasoning168", "machine168", "learning168", "model168", "token168", "prompt168"],
    ),
    (
        ("reasoning168 machine168 learning168 model168 token168 prompt168", 10),
        ["reasoning168", "machine168", "learning168", "model168", "token168", "prompt168"],
    ),
    (
        ("reasoning168 machine168 learning168 model168 token168 prompt168", 18),
        ["reasoning168", "machine168", "learning168", "model168 token168", "prompt168"],
    ),
    (
        ("reasoning168 machine168 learning168 model168 token168 prompt168", 28),
        ["reasoning168 machine168", "learning168 model168", "token168 prompt168"],
    ),
    (
        ("machine168 learning168 model168 token168 prompt168 session168", 6),
        ["machine168", "learning168", "model168", "token168", "prompt168", "session168"],
    ),
    (
        ("machine168 learning168 model168 token168 prompt168 session168", 10),
        ["machine168", "learning168", "model168", "token168", "prompt168", "session168"],
    ),
    (
        ("machine168 learning168 model168 token168 prompt168 session168", 18),
        ["machine168", "learning168", "model168 token168", "prompt168", "session168"],
    ),
    (
        ("machine168 learning168 model168 token168 prompt168 session168", 28),
        ["machine168 learning168", "model168 token168 prompt168", "session168"],
    ),
    (
        ("learning168 model168 token168 prompt168 session168 library168", 6),
        ["learning168", "model168", "token168", "prompt168", "session168", "library168"],
    ),
    (
        ("learning168 model168 token168 prompt168 session168 library168", 10),
        ["learning168", "model168", "token168", "prompt168", "session168", "library168"],
    ),
    (
        ("learning168 model168 token168 prompt168 session168 library168", 18),
        ["learning168", "model168 token168", "prompt168", "session168", "library168"],
    ),
    (
        ("learning168 model168 token168 prompt168 session168 library168", 28),
        ["learning168 model168", "token168 prompt168", "session168 library168"],
    ),
    (
        ("model168 token168 prompt168 session168 library168 service168", 6),
        ["model168", "token168", "prompt168", "session168", "library168", "service168"],
    ),
    (
        ("model168 token168 prompt168 session168 library168 service168", 10),
        ["model168", "token168", "prompt168", "session168", "library168", "service168"],
    ),
    (
        ("model168 token168 prompt168 session168 library168 service168", 18),
        ["model168 token168", "prompt168", "session168", "library168", "service168"],
    ),
    (
        ("model168 token168 prompt168 session168 library168 service168", 28),
        ["model168 token168 prompt168", "session168 library168", "service168"],
    ),
    (
        ("token168 prompt168 session168 library168 service168 gateway168", 6),
        ["token168", "prompt168", "session168", "library168", "service168", "gateway168"],
    ),
    (
        ("token168 prompt168 session168 library168 service168 gateway168", 10),
        ["token168", "prompt168", "session168", "library168", "service168", "gateway168"],
    ),
    (
        ("token168 prompt168 session168 library168 service168 gateway168", 18),
        ["token168 prompt168", "session168", "library168", "service168", "gateway168"],
    ),
    (
        ("token168 prompt168 session168 library168 service168 gateway168", 28),
        ["token168 prompt168", "session168 library168", "service168 gateway168"],
    ),
    (
        ("prompt168 session168 library168 service168 gateway168 storage168", 6),
        ["prompt168", "session168", "library168", "service168", "gateway168", "storage168"],
    ),
    (
        ("prompt168 session168 library168 service168 gateway168 storage168", 10),
        ["prompt168", "session168", "library168", "service168", "gateway168", "storage168"],
    ),
    (
        ("prompt168 session168 library168 service168 gateway168 storage168", 18),
        ["prompt168", "session168", "library168", "service168", "gateway168", "storage168"],
    ),
    (
        ("prompt168 session168 library168 service168 gateway168 storage168", 28),
        ["prompt168 session168", "library168 service168", "gateway168 storage168"],
    ),
    (
        ("session168 library168 service168 gateway168 storage168 network168", 6),
        ["session168", "library168", "service168", "gateway168", "storage168", "network168"],
    ),
    (
        ("session168 library168 service168 gateway168 storage168 network168", 10),
        ["session168", "library168", "service168", "gateway168", "storage168", "network168"],
    ),
    (
        ("session168 library168 service168 gateway168 storage168 network168", 18),
        ["session168", "library168", "service168", "gateway168", "storage168", "network168"],
    ),
    (
        ("session168 library168 service168 gateway168 storage168 network168", 28),
        ["session168 library168", "service168 gateway168", "storage168 network168"],
    ),
    (
        ("library168 service168 gateway168 storage168 network168 latency168", 6),
        ["library168", "service168", "gateway168", "storage168", "network168", "latency168"],
    ),
    (
        ("library168 service168 gateway168 storage168 network168 latency168", 10),
        ["library168", "service168", "gateway168", "storage168", "network168", "latency168"],
    ),
    (
        ("library168 service168 gateway168 storage168 network168 latency168", 18),
        ["library168", "service168", "gateway168", "storage168", "network168", "latency168"],
    ),
    (
        ("library168 service168 gateway168 storage168 network168 latency168", 28),
        ["library168 service168", "gateway168 storage168", "network168 latency168"],
    ),
    (
        ("service168 gateway168 storage168 network168 latency168 buffer168", 6),
        ["service168", "gateway168", "storage168", "network168", "latency168", "buffer168"],
    ),
    (
        ("service168 gateway168 storage168 network168 latency168 buffer168", 10),
        ["service168", "gateway168", "storage168", "network168", "latency168", "buffer168"],
    ),
    (
        ("service168 gateway168 storage168 network168 latency168 buffer168", 18),
        ["service168", "gateway168", "storage168", "network168", "latency168", "buffer168"],
    ),
    (
        ("service168 gateway168 storage168 network168 latency168 buffer168", 28),
        ["service168 gateway168", "storage168 network168", "latency168 buffer168"],
    ),
    (
        ("gateway168 storage168 network168 latency168 buffer168 queue168", 6),
        ["gateway168", "storage168", "network168", "latency168", "buffer168", "queue168"],
    ),
    (
        ("gateway168 storage168 network168 latency168 buffer168 queue168", 10),
        ["gateway168", "storage168", "network168", "latency168", "buffer168", "queue168"],
    ),
    (
        ("gateway168 storage168 network168 latency168 buffer168 queue168", 18),
        ["gateway168", "storage168", "network168", "latency168", "buffer168 queue168"],
    ),
    (
        ("gateway168 storage168 network168 latency168 buffer168 queue168", 28),
        ["gateway168 storage168", "network168 latency168", "buffer168 queue168"],
    ),
    (
        ("storage168 network168 latency168 buffer168 queue168 worker168", 6),
        ["storage168", "network168", "latency168", "buffer168", "queue168", "worker168"],
    ),
    (
        ("storage168 network168 latency168 buffer168 queue168 worker168", 10),
        ["storage168", "network168", "latency168", "buffer168", "queue168", "worker168"],
    ),
    (
        ("storage168 network168 latency168 buffer168 queue168 worker168", 18),
        ["storage168", "network168", "latency168", "buffer168 queue168", "worker168"],
    ),
    (
        ("storage168 network168 latency168 buffer168 queue168 worker168", 28),
        ["storage168 network168", "latency168 buffer168", "queue168 worker168"],
    ),
    (
        ("network168 latency168 buffer168 queue168 worker168 kernel168", 6),
        ["network168", "latency168", "buffer168", "queue168", "worker168", "kernel168"],
    ),
    (
        ("network168 latency168 buffer168 queue168 worker168 kernel168", 10),
        ["network168", "latency168", "buffer168", "queue168", "worker168", "kernel168"],
    ),
    (
        ("network168 latency168 buffer168 queue168 worker168 kernel168", 18),
        ["network168", "latency168", "buffer168 queue168", "worker168", "kernel168"],
    ),
    (
        ("network168 latency168 buffer168 queue168 worker168 kernel168", 28),
        ["network168 latency168", "buffer168 queue168 worker168", "kernel168"],
    ),
    (
        ("latency168 buffer168 queue168 worker168 kernel168 signal168", 6),
        ["latency168", "buffer168", "queue168", "worker168", "kernel168", "signal168"],
    ),
    (
        ("latency168 buffer168 queue168 worker168 kernel168 signal168", 10),
        ["latency168", "buffer168", "queue168", "worker168", "kernel168", "signal168"],
    ),
    (
        ("latency168 buffer168 queue168 worker168 kernel168 signal168", 18),
        ["latency168", "buffer168 queue168", "worker168", "kernel168", "signal168"],
    ),
    (
        ("latency168 buffer168 queue168 worker168 kernel168 signal168", 28),
        ["latency168 buffer168", "queue168 worker168 kernel168", "signal168"],
    ),
    (
        ("buffer168 queue168 worker168 kernel168 signal168 packet168", 6),
        ["buffer168", "queue168", "worker168", "kernel168", "signal168", "packet168"],
    ),
    (
        ("buffer168 queue168 worker168 kernel168 signal168 packet168", 10),
        ["buffer168", "queue168", "worker168", "kernel168", "signal168", "packet168"],
    ),
    (
        ("buffer168 queue168 worker168 kernel168 signal168 packet168", 18),
        ["buffer168 queue168", "worker168", "kernel168", "signal168", "packet168"],
    ),
    (
        ("buffer168 queue168 worker168 kernel168 signal168 packet168", 28),
        ["buffer168 queue168 worker168", "kernel168 signal168", "packet168"],
    ),
    (
        ("queue168 worker168 kernel168 signal168 packet168 router168", 6),
        ["queue168", "worker168", "kernel168", "signal168", "packet168", "router168"],
    ),
    (
        ("queue168 worker168 kernel168 signal168 packet168 router168", 10),
        ["queue168", "worker168", "kernel168", "signal168", "packet168", "router168"],
    ),
    (
        ("queue168 worker168 kernel168 signal168 packet168 router168", 18),
        ["queue168 worker168", "kernel168", "signal168", "packet168", "router168"],
    ),
    (
        ("queue168 worker168 kernel168 signal168 packet168 router168", 28),
        ["queue168 worker168 kernel168", "signal168 packet168", "router168"],
    ),
    (
        ("worker168 kernel168 signal168 packet168 router168 cluster168", 6),
        ["worker168", "kernel168", "signal168", "packet168", "router168", "cluster168"],
    ),
    (
        ("worker168 kernel168 signal168 packet168 router168 cluster168", 10),
        ["worker168", "kernel168", "signal168", "packet168", "router168", "cluster168"],
    ),
    (
        ("worker168 kernel168 signal168 packet168 router168 cluster168", 18),
        ["worker168", "kernel168", "signal168", "packet168", "router168", "cluster168"],
    ),
    (
        ("worker168 kernel168 signal168 packet168 router168 cluster168", 28),
        ["worker168 kernel168", "signal168 packet168", "router168 cluster168"],
    ),
    (
        ("kernel168 signal168 packet168 router168 cluster168 mirror168", 6),
        ["kernel168", "signal168", "packet168", "router168", "cluster168", "mirror168"],
    ),
    (
        ("kernel168 signal168 packet168 router168 cluster168 mirror168", 10),
        ["kernel168", "signal168", "packet168", "router168", "cluster168", "mirror168"],
    ),
    (
        ("kernel168 signal168 packet168 router168 cluster168 mirror168", 18),
        ["kernel168", "signal168", "packet168", "router168", "cluster168", "mirror168"],
    ),
    (
        ("kernel168 signal168 packet168 router168 cluster168 mirror168", 28),
        ["kernel168 signal168", "packet168 router168", "cluster168 mirror168"],
    ),
    (
        ("signal168 packet168 router168 cluster168 mirror168 filter168", 6),
        ["signal168", "packet168", "router168", "cluster168", "mirror168", "filter168"],
    ),
    (
        ("signal168 packet168 router168 cluster168 mirror168 filter168", 10),
        ["signal168", "packet168", "router168", "cluster168", "mirror168", "filter168"],
    ),
    (
        ("signal168 packet168 router168 cluster168 mirror168 filter168", 18),
        ["signal168", "packet168", "router168", "cluster168", "mirror168", "filter168"],
    ),
    (
        ("signal168 packet168 router168 cluster168 mirror168 filter168", 28),
        ["signal168 packet168", "router168 cluster168", "mirror168 filter168"],
    ),
    (
        ("packet168 router168 cluster168 mirror168 filter168 ranking168", 6),
        ["packet168", "router168", "cluster168", "mirror168", "filter168", "ranking168"],
    ),
    (
        ("packet168 router168 cluster168 mirror168 filter168 ranking168", 10),
        ["packet168", "router168", "cluster168", "mirror168", "filter168", "ranking168"],
    ),
    (
        ("packet168 router168 cluster168 mirror168 filter168 ranking168", 18),
        ["packet168", "router168", "cluster168", "mirror168", "filter168", "ranking168"],
    ),
    (
        ("packet168 router168 cluster168 mirror168 filter168 ranking168", 28),
        ["packet168 router168", "cluster168 mirror168", "filter168 ranking168"],
    ),
    (
        ("router168 cluster168 mirror168 filter168 ranking168 encoding168", 6),
        ["router168", "cluster168", "mirror168", "filter168", "ranking168", "encoding168"],
    ),
    (
        ("router168 cluster168 mirror168 filter168 ranking168 encoding168", 10),
        ["router168", "cluster168", "mirror168", "filter168", "ranking168", "encoding168"],
    ),
    (
        ("router168 cluster168 mirror168 filter168 ranking168 encoding168", 18),
        ["router168", "cluster168", "mirror168", "filter168", "ranking168", "encoding168"],
    ),
    (
        ("router168 cluster168 mirror168 filter168 ranking168 encoding168", 28),
        ["router168 cluster168", "mirror168 filter168", "ranking168 encoding168"],
    ),
    (
        ("cluster168 mirror168 filter168 ranking168 encoding168 mapping168", 6),
        ["cluster168", "mirror168", "filter168", "ranking168", "encoding168", "mapping168"],
    ),
    (
        ("cluster168 mirror168 filter168 ranking168 encoding168 mapping168", 10),
        ["cluster168", "mirror168", "filter168", "ranking168", "encoding168", "mapping168"],
    ),
    (
        ("cluster168 mirror168 filter168 ranking168 encoding168 mapping168", 18),
        ["cluster168", "mirror168", "filter168", "ranking168", "encoding168", "mapping168"],
    ),
    (
        ("cluster168 mirror168 filter168 ranking168 encoding168 mapping168", 28),
        ["cluster168 mirror168", "filter168 ranking168", "encoding168 mapping168"],
    ),
    (
        ("mirror168 filter168 ranking168 encoding168 mapping168 record168", 6),
        ["mirror168", "filter168", "ranking168", "encoding168", "mapping168", "record168"],
    ),
    (
        ("mirror168 filter168 ranking168 encoding168 mapping168 record168", 10),
        ["mirror168", "filter168", "ranking168", "encoding168", "mapping168", "record168"],
    ),
    (
        ("mirror168 filter168 ranking168 encoding168 mapping168 record168", 18),
        ["mirror168", "filter168", "ranking168", "encoding168", "mapping168", "record168"],
    ),
    (
        ("mirror168 filter168 ranking168 encoding168 mapping168 record168", 28),
        ["mirror168 filter168", "ranking168 encoding168", "mapping168 record168"],
    ),
    (
        ("filter168 ranking168 encoding168 mapping168 record168 candle168", 6),
        ["filter168", "ranking168", "encoding168", "mapping168", "record168", "candle168"],
    ),
    (
        ("filter168 ranking168 encoding168 mapping168 record168 candle168", 10),
        ["filter168", "ranking168", "encoding168", "mapping168", "record168", "candle168"],
    ),
    (
        ("filter168 ranking168 encoding168 mapping168 record168 candle168", 18),
        ["filter168", "ranking168", "encoding168", "mapping168", "record168", "candle168"],
    ),
    (
        ("filter168 ranking168 encoding168 mapping168 record168 candle168", 28),
        ["filter168 ranking168", "encoding168 mapping168", "record168 candle168"],
    ),
    (
        ("ranking168 encoding168 mapping168 record168 candle168 thread168", 6),
        ["ranking168", "encoding168", "mapping168", "record168", "candle168", "thread168"],
    ),
    (
        ("ranking168 encoding168 mapping168 record168 candle168 thread168", 10),
        ["ranking168", "encoding168", "mapping168", "record168", "candle168", "thread168"],
    ),
    (
        ("ranking168 encoding168 mapping168 record168 candle168 thread168", 18),
        ["ranking168", "encoding168", "mapping168", "record168", "candle168", "thread168"],
    ),
    (
        ("ranking168 encoding168 mapping168 record168 candle168 thread168", 28),
        ["ranking168 encoding168", "mapping168 record168", "candle168 thread168"],
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
