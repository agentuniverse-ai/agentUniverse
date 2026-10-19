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
        ("round 738: the quick brown fox jumps over the lazy dog", 4),
        ["round", "738:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", 8),
        ["round", "738: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", 12),
        ["round 738:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", 16),
        ["round 738: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", 24),
        ["round 738: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 738: the quick brown fox jumps over the lazy dog", 32),
        ["round 738: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", 4),
        ["round", "738:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", 8),
        ["round", "738:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", 12),
        ["round 738:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", 16),
        ["round 738:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", 24),
        ["round 738: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 738: agentuniverse is a framework for multi agents", 32),
        ["round 738: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", 4),
        ["round", "738:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", 8),
        ["round", "738:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", 12),
        ["round 738:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", 16),
        ["round 738:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", 24),
        ["round 738: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 738: knowledge stored as vectors enables retrieval", 32),
        ["round 738: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 738: the processor reads the record then stops", 4),
        ["round", "738:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 738: the processor reads the record then stops", 8),
        ["round", "738: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 738: the processor reads the record then stops", 12),
        ["round 738:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 738: the processor reads the record then stops", 16),
        ["round 738: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 738: the processor reads the record then stops", 24),
        ["round 738: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 738: the processor reads the record then stops", 32),
        ["round 738: the processor reads", "the record then stops"],
    ),
    (
        ("round 738: a worker pulls the next task from the queue", 4),
        ["round", "738:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 738: a worker pulls the next task from the queue", 8),
        ["round", "738: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 738: a worker pulls the next task from the queue", 12),
        ["round 738: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 738: a worker pulls the next task from the queue", 16),
        ["round 738: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 738: a worker pulls the next task from the queue", 24),
        ["round 738: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 738: a worker pulls the next task from the queue", 32),
        ["round 738: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 738: signals travel through the network layer", 4),
        ["round", "738:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 738: signals travel through the network layer", 8),
        ["round", "738:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 738: signals travel through the network layer", 12),
        ["round 738:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 738: signals travel through the network layer", 16),
        ["round 738:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 738: signals travel through the network layer", 24),
        ["round 738: signals", "travel through the", "network layer"],
    ),
    (
        ("round 738: signals travel through the network layer", 32),
        ["round 738: signals travel", "through the network layer"],
    ),
    (
        ("round 738: the gateway routes each request by policy", 4),
        ["round", "738:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 738: the gateway routes each request by policy", 8),
        ["round", "738: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 738: the gateway routes each request by policy", 12),
        ["round 738:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 738: the gateway routes each request by policy", 16),
        ["round 738: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 738: the gateway routes each request by policy", 24),
        ["round 738: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 738: the gateway routes each request by policy", 32),
        ["round 738: the gateway routes", "each request by policy"],
    ),
    (
        ("round 738: memory grows until the buffer is full", 4),
        ["round", "738:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 738: memory grows until the buffer is full", 8),
        ["round", "738:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 738: memory grows until the buffer is full", 12),
        ["round 738:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 738: memory grows until the buffer is full", 16),
        ["round 738:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 738: memory grows until the buffer is full", 24), ["round 738: memory grows", "until the buffer is full"]),
    (("round 738: memory grows until the buffer is full", 32), ["round 738: memory grows until", "the buffer is full"]),
    (
        ("round 738: the cluster mirrors every packet twice", 4),
        ["round", "738:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 738: the cluster mirrors every packet twice", 8),
        ["round", "738: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 738: the cluster mirrors every packet twice", 12),
        ["round 738:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 738: the cluster mirrors every packet twice", 16),
        ["round 738: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 738: the cluster mirrors every packet twice", 24),
        ["round 738: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 738: the cluster mirrors every packet twice", 32),
        ["round 738: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", 4),
        ["round", "738:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", 8),
        ["round", "738:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", 12),
        ["round 738:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", 16),
        ["round 738:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", 24),
        ["round 738: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 738: ranking uses tokens learned from the corpus", 32),
        ["round 738: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 738: a long session ends when the candle dies", 4),
        ["round", "738:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 738: a long session ends when the candle dies", 8),
        ["round", "738: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 738: a long session ends when the candle dies", 12),
        ["round 738: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 738: a long session ends when the candle dies", 16),
        ["round 738: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 738: a long session ends when the candle dies", 24),
        ["round 738: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 738: a long session ends when the candle dies", 32),
        ["round 738: a long session ends", "when the candle dies"],
    ),
    (
        ("round 738: encode the prompt then map the result", 4),
        ["round", "738:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 738: encode the prompt then map the result", 8),
        ["round", "738:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 738: encode the prompt then map the result", 12),
        ["round 738:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 738: encode the prompt then map the result", 16),
        ["round 738:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 738: encode the prompt then map the result", 24),
        ["round 738: encode the", "prompt then map the", "result"],
    ),
    (("round 738: encode the prompt then map the result", 32), ["round 738: encode the prompt", "then map the result"]),
    (
        ("round 738: the kernel wakes the worker at dawn", 4),
        ["round", "738:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 738: the kernel wakes the worker at dawn", 8),
        ["round", "738: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 738: the kernel wakes the worker at dawn", 12),
        ["round 738:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 738: the kernel wakes the worker at dawn", 16), ["round 738: the", "kernel wakes the", "worker at dawn"]),
    (("round 738: the kernel wakes the worker at dawn", 24), ["round 738: the kernel", "wakes the worker at dawn"]),
    (("round 738: the kernel wakes the worker at dawn", 32), ["round 738: the kernel wakes the", "worker at dawn"]),
    (
        ("round 738: service latency drops after the patch", 4),
        ["round", "738:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 738: service latency drops after the patch", 8),
        ["round", "738:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 738: service latency drops after the patch", 12),
        ["round 738:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 738: service latency drops after the patch", 16),
        ["round 738:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 738: service latency drops after the patch", 24),
        ["round 738: service", "latency drops after the", "patch"],
    ),
    (("round 738: service latency drops after the patch", 32), ["round 738: service latency drops", "after the patch"]),
    (
        ("round 738: the library caches every vector it sees", 4),
        ["round", "738:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 738: the library caches every vector it sees", 8),
        ["round", "738: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 738: the library caches every vector it sees", 12),
        ["round 738:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 738: the library caches every vector it sees", 16),
        ["round 738: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 738: the library caches every vector it sees", 24),
        ["round 738: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 738: the library caches every vector it sees", 32),
        ["round 738: the library caches", "every vector it sees"],
    ),
    (
        ("round 738: agents argue then the debate resolves", 4),
        ["round", "738:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 738: agents argue then the debate resolves", 8),
        ["round", "738:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 738: agents argue then the debate resolves", 12),
        ["round 738:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 738: agents argue then the debate resolves", 16),
        ["round 738:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 738: agents argue then the debate resolves", 24), ["round 738: agents argue", "then the debate resolves"]),
    (("round 738: agents argue then the debate resolves", 32), ["round 738: agents argue then the", "debate resolves"]),
    (
        ("round 738: the filter keeps only strong matches", 4),
        ["round", "738:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 738: the filter keeps only strong matches", 8),
        ["round", "738: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 738: the filter keeps only strong matches", 12),
        ["round 738:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 738: the filter keeps only strong matches", 16),
        ["round 738: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 738: the filter keeps only strong matches", 24),
        ["round 738: the filter", "keeps only strong", "matches"],
    ),
    (("round 738: the filter keeps only strong matches", 32), ["round 738: the filter keeps only", "strong matches"]),
    (
        ("round 738: the model answers with a short reply", 4),
        ["round", "738:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 738: the model answers with a short reply", 8),
        ["round", "738: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 738: the model answers with a short reply", 12),
        ["round 738:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 738: the model answers with a short reply", 16),
        ["round 738: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 738: the model answers with a short reply", 24),
        ["round 738: the model", "answers with a short", "reply"],
    ),
    (("round 738: the model answers with a short reply", 32), ["round 738: the model answers", "with a short reply"]),
    (
        ("round 738: the recorder stores the reasoning trace", 4),
        ["round", "738:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 738: the recorder stores the reasoning trace", 8),
        ["round", "738: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 738: the recorder stores the reasoning trace", 12),
        ["round 738:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 738: the recorder stores the reasoning trace", 16),
        ["round 738: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 738: the recorder stores the reasoning trace", 24),
        ["round 738: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 738: the recorder stores the reasoning trace", 32),
        ["round 738: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 738: the angel watches the processor run", 4),
        ["round", "738:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 738: the angel watches the processor run", 8),
        ["round", "738: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 738: the angel watches the processor run", 12),
        ["round 738:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 738: the angel watches the processor run", 16),
        ["round 738: the", "angel watches", "the processor", "run"],
    ),
    (("round 738: the angel watches the processor run", 24), ["round 738: the angel", "watches the processor", "run"]),
    (("round 738: the angel watches the processor run", 32), ["round 738: the angel watches the", "processor run"]),
    (
        ("round 738: angle of the vector decides the match", 4),
        ["round", "738:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 738: angle of the vector decides the match", 8),
        ["round", "738:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 738: angle of the vector decides the match", 12),
        ["round 738:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 738: angle of the vector decides the match", 16),
        ["round 738: angle", "of the vector", "decides the", "match"],
    ),
    (("round 738: angle of the vector decides the match", 24), ["round 738: angle of the", "vector decides the match"]),
    (("round 738: angle of the vector decides the match", 32), ["round 738: angle of the vector", "decides the match"]),
    (
        ("round 738: the candle burns twice as long at night", 4),
        ["round", "738:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 738: the candle burns twice as long at night", 8),
        ["round", "738: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 738: the candle burns twice as long at night", 12),
        ["round 738:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 738: the candle burns twice as long at night", 16),
        ["round 738: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 738: the candle burns twice as long at night", 24),
        ["round 738: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 738: the candle burns twice as long at night", 32),
        ["round 738: the candle burns", "twice as long at night"],
    ),
    (
        ("round 738: a mirror of the universe in one line", 4),
        ["round", "738:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 738: a mirror of the universe in one line", 8),
        ["round", "738: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 738: a mirror of the universe in one line", 12),
        ["round 738: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 738: a mirror of the universe in one line", 16),
        ["round 738: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 738: a mirror of the universe in one line", 24), ["round 738: a mirror of", "the universe in one line"]),
    (("round 738: a mirror of the universe in one line", 32), ["round 738: a mirror of the", "universe in one line"]),
    (
        ("round 738: the queue drains before the storm", 4),
        ["round", "738:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 738: the queue drains before the storm", 8),
        ["round", "738: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 738: the queue drains before the storm", 12),
        ["round 738:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 738: the queue drains before the storm", 16), ["round 738: the", "queue drains", "before the storm"]),
    (("round 738: the queue drains before the storm", 24), ["round 738: the queue", "drains before the storm"]),
    (("round 738: the queue drains before the storm", 32), ["round 738: the queue drains", "before the storm"]),
    (
        ("kitten738 sitting738 agent738 angle738 universe738 memory738", 6),
        ["kitten738", "sitting738", "agent738", "angle738", "universe738", "memory738"],
    ),
    (
        ("kitten738 sitting738 agent738 angle738 universe738 memory738", 10),
        ["kitten738", "sitting738", "agent738", "angle738", "universe738", "memory738"],
    ),
    (
        ("kitten738 sitting738 agent738 angle738 universe738 memory738", 18),
        ["kitten738", "sitting738", "agent738 angle738", "universe738", "memory738"],
    ),
    (
        ("kitten738 sitting738 agent738 angle738 universe738 memory738", 28),
        ["kitten738 sitting738", "agent738 angle738", "universe738 memory738"],
    ),
    (
        ("sitting738 agent738 angle738 universe738 memory738 stream738", 6),
        ["sitting738", "agent738", "angle738", "universe738", "memory738", "stream738"],
    ),
    (
        ("sitting738 agent738 angle738 universe738 memory738 stream738", 10),
        ["sitting738", "agent738", "angle738", "universe738", "memory738", "stream738"],
    ),
    (
        ("sitting738 agent738 angle738 universe738 memory738 stream738", 18),
        ["sitting738", "agent738 angle738", "universe738", "memory738", "stream738"],
    ),
    (
        ("sitting738 agent738 angle738 universe738 memory738 stream738", 28),
        ["sitting738 agent738 angle738", "universe738 memory738", "stream738"],
    ),
    (
        ("agent738 angle738 universe738 memory738 stream738 context738", 6),
        ["agent738", "angle738", "universe738", "memory738", "stream738", "context738"],
    ),
    (
        ("agent738 angle738 universe738 memory738 stream738 context738", 10),
        ["agent738", "angle738", "universe738", "memory738", "stream738", "context738"],
    ),
    (
        ("agent738 angle738 universe738 memory738 stream738 context738", 18),
        ["agent738 angle738", "universe738", "memory738", "stream738", "context738"],
    ),
    (
        ("agent738 angle738 universe738 memory738 stream738 context738", 28),
        ["agent738 angle738", "universe738 memory738", "stream738 context738"],
    ),
    (
        ("angle738 universe738 memory738 stream738 context738 knowledge738", 6),
        ["angle738", "universe738", "memory738", "stream738", "context738", "knowledge738"],
    ),
    (
        ("angle738 universe738 memory738 stream738 context738 knowledge738", 10),
        ["angle738", "universe738", "memory738", "stream738", "context738", "knowledge738"],
    ),
    (
        ("angle738 universe738 memory738 stream738 context738 knowledge738", 18),
        ["angle738", "universe738", "memory738", "stream738", "context738", "knowledge738"],
    ),
    (
        ("angle738 universe738 memory738 stream738 context738 knowledge738", 28),
        ["angle738 universe738", "memory738 stream738", "context738 knowledge738"],
    ),
    (
        ("universe738 memory738 stream738 context738 knowledge738 vector738", 6),
        ["universe738", "memory738", "stream738", "context738", "knowledge738", "vector738"],
    ),
    (
        ("universe738 memory738 stream738 context738 knowledge738 vector738", 10),
        ["universe738", "memory738", "stream738", "context738", "knowledge738", "vector738"],
    ),
    (
        ("universe738 memory738 stream738 context738 knowledge738 vector738", 18),
        ["universe738", "memory738", "stream738", "context738", "knowledge738", "vector738"],
    ),
    (
        ("universe738 memory738 stream738 context738 knowledge738 vector738", 28),
        ["universe738 memory738", "stream738 context738", "knowledge738 vector738"],
    ),
    (
        ("memory738 stream738 context738 knowledge738 vector738 processor738", 6),
        ["memory738", "stream738", "context738", "knowledge738", "vector738", "processor738"],
    ),
    (
        ("memory738 stream738 context738 knowledge738 vector738 processor738", 10),
        ["memory738", "stream738", "context738", "knowledge738", "vector738", "processor738"],
    ),
    (
        ("memory738 stream738 context738 knowledge738 vector738 processor738", 18),
        ["memory738", "stream738", "context738", "knowledge738", "vector738", "processor738"],
    ),
    (
        ("memory738 stream738 context738 knowledge738 vector738 processor738", 28),
        ["memory738 stream738", "context738 knowledge738", "vector738 processor738"],
    ),
    (
        ("stream738 context738 knowledge738 vector738 processor738 reasoning738", 6),
        ["stream738", "context738", "knowledge738", "vector738", "processor738", "reasoning738"],
    ),
    (
        ("stream738 context738 knowledge738 vector738 processor738 reasoning738", 10),
        ["stream738", "context738", "knowledge738", "vector738", "processor738", "reasoning738"],
    ),
    (
        ("stream738 context738 knowledge738 vector738 processor738 reasoning738", 18),
        ["stream738", "context738", "knowledge738", "vector738", "processor738", "reasoning738"],
    ),
    (
        ("stream738 context738 knowledge738 vector738 processor738 reasoning738", 28),
        ["stream738 context738", "knowledge738 vector738", "processor738 reasoning738"],
    ),
    (
        ("context738 knowledge738 vector738 processor738 reasoning738 machine738", 6),
        ["context738", "knowledge738", "vector738", "processor738", "reasoning738", "machine738"],
    ),
    (
        ("context738 knowledge738 vector738 processor738 reasoning738 machine738", 10),
        ["context738", "knowledge738", "vector738", "processor738", "reasoning738", "machine738"],
    ),
    (
        ("context738 knowledge738 vector738 processor738 reasoning738 machine738", 18),
        ["context738", "knowledge738", "vector738", "processor738", "reasoning738", "machine738"],
    ),
    (
        ("context738 knowledge738 vector738 processor738 reasoning738 machine738", 28),
        ["context738 knowledge738", "vector738 processor738", "reasoning738 machine738"],
    ),
    (
        ("knowledge738 vector738 processor738 reasoning738 machine738 learning738", 6),
        ["knowledge738", "vector738", "processor738", "reasoning738", "machine738", "learning738"],
    ),
    (
        ("knowledge738 vector738 processor738 reasoning738 machine738 learning738", 10),
        ["knowledge738", "vector738", "processor738", "reasoning738", "machine738", "learning738"],
    ),
    (
        ("knowledge738 vector738 processor738 reasoning738 machine738 learning738", 18),
        ["knowledge738", "vector738", "processor738", "reasoning738", "machine738", "learning738"],
    ),
    (
        ("knowledge738 vector738 processor738 reasoning738 machine738 learning738", 28),
        ["knowledge738 vector738", "processor738 reasoning738", "machine738 learning738"],
    ),
    (
        ("vector738 processor738 reasoning738 machine738 learning738 model738", 6),
        ["vector738", "processor738", "reasoning738", "machine738", "learning738", "model738"],
    ),
    (
        ("vector738 processor738 reasoning738 machine738 learning738 model738", 10),
        ["vector738", "processor738", "reasoning738", "machine738", "learning738", "model738"],
    ),
    (
        ("vector738 processor738 reasoning738 machine738 learning738 model738", 18),
        ["vector738", "processor738", "reasoning738", "machine738", "learning738", "model738"],
    ),
    (
        ("vector738 processor738 reasoning738 machine738 learning738 model738", 28),
        ["vector738 processor738", "reasoning738 machine738", "learning738 model738"],
    ),
    (
        ("processor738 reasoning738 machine738 learning738 model738 token738", 6),
        ["processor738", "reasoning738", "machine738", "learning738", "model738", "token738"],
    ),
    (
        ("processor738 reasoning738 machine738 learning738 model738 token738", 10),
        ["processor738", "reasoning738", "machine738", "learning738", "model738", "token738"],
    ),
    (
        ("processor738 reasoning738 machine738 learning738 model738 token738", 18),
        ["processor738", "reasoning738", "machine738", "learning738", "model738 token738"],
    ),
    (
        ("processor738 reasoning738 machine738 learning738 model738 token738", 28),
        ["processor738 reasoning738", "machine738 learning738", "model738 token738"],
    ),
    (
        ("reasoning738 machine738 learning738 model738 token738 prompt738", 6),
        ["reasoning738", "machine738", "learning738", "model738", "token738", "prompt738"],
    ),
    (
        ("reasoning738 machine738 learning738 model738 token738 prompt738", 10),
        ["reasoning738", "machine738", "learning738", "model738", "token738", "prompt738"],
    ),
    (
        ("reasoning738 machine738 learning738 model738 token738 prompt738", 18),
        ["reasoning738", "machine738", "learning738", "model738 token738", "prompt738"],
    ),
    (
        ("reasoning738 machine738 learning738 model738 token738 prompt738", 28),
        ["reasoning738 machine738", "learning738 model738", "token738 prompt738"],
    ),
    (
        ("machine738 learning738 model738 token738 prompt738 session738", 6),
        ["machine738", "learning738", "model738", "token738", "prompt738", "session738"],
    ),
    (
        ("machine738 learning738 model738 token738 prompt738 session738", 10),
        ["machine738", "learning738", "model738", "token738", "prompt738", "session738"],
    ),
    (
        ("machine738 learning738 model738 token738 prompt738 session738", 18),
        ["machine738", "learning738", "model738 token738", "prompt738", "session738"],
    ),
    (
        ("machine738 learning738 model738 token738 prompt738 session738", 28),
        ["machine738 learning738", "model738 token738 prompt738", "session738"],
    ),
    (
        ("learning738 model738 token738 prompt738 session738 library738", 6),
        ["learning738", "model738", "token738", "prompt738", "session738", "library738"],
    ),
    (
        ("learning738 model738 token738 prompt738 session738 library738", 10),
        ["learning738", "model738", "token738", "prompt738", "session738", "library738"],
    ),
    (
        ("learning738 model738 token738 prompt738 session738 library738", 18),
        ["learning738", "model738 token738", "prompt738", "session738", "library738"],
    ),
    (
        ("learning738 model738 token738 prompt738 session738 library738", 28),
        ["learning738 model738", "token738 prompt738", "session738 library738"],
    ),
    (
        ("model738 token738 prompt738 session738 library738 service738", 6),
        ["model738", "token738", "prompt738", "session738", "library738", "service738"],
    ),
    (
        ("model738 token738 prompt738 session738 library738 service738", 10),
        ["model738", "token738", "prompt738", "session738", "library738", "service738"],
    ),
    (
        ("model738 token738 prompt738 session738 library738 service738", 18),
        ["model738 token738", "prompt738", "session738", "library738", "service738"],
    ),
    (
        ("model738 token738 prompt738 session738 library738 service738", 28),
        ["model738 token738 prompt738", "session738 library738", "service738"],
    ),
    (
        ("token738 prompt738 session738 library738 service738 gateway738", 6),
        ["token738", "prompt738", "session738", "library738", "service738", "gateway738"],
    ),
    (
        ("token738 prompt738 session738 library738 service738 gateway738", 10),
        ["token738", "prompt738", "session738", "library738", "service738", "gateway738"],
    ),
    (
        ("token738 prompt738 session738 library738 service738 gateway738", 18),
        ["token738 prompt738", "session738", "library738", "service738", "gateway738"],
    ),
    (
        ("token738 prompt738 session738 library738 service738 gateway738", 28),
        ["token738 prompt738", "session738 library738", "service738 gateway738"],
    ),
    (
        ("prompt738 session738 library738 service738 gateway738 storage738", 6),
        ["prompt738", "session738", "library738", "service738", "gateway738", "storage738"],
    ),
    (
        ("prompt738 session738 library738 service738 gateway738 storage738", 10),
        ["prompt738", "session738", "library738", "service738", "gateway738", "storage738"],
    ),
    (
        ("prompt738 session738 library738 service738 gateway738 storage738", 18),
        ["prompt738", "session738", "library738", "service738", "gateway738", "storage738"],
    ),
    (
        ("prompt738 session738 library738 service738 gateway738 storage738", 28),
        ["prompt738 session738", "library738 service738", "gateway738 storage738"],
    ),
    (
        ("session738 library738 service738 gateway738 storage738 network738", 6),
        ["session738", "library738", "service738", "gateway738", "storage738", "network738"],
    ),
    (
        ("session738 library738 service738 gateway738 storage738 network738", 10),
        ["session738", "library738", "service738", "gateway738", "storage738", "network738"],
    ),
    (
        ("session738 library738 service738 gateway738 storage738 network738", 18),
        ["session738", "library738", "service738", "gateway738", "storage738", "network738"],
    ),
    (
        ("session738 library738 service738 gateway738 storage738 network738", 28),
        ["session738 library738", "service738 gateway738", "storage738 network738"],
    ),
    (
        ("library738 service738 gateway738 storage738 network738 latency738", 6),
        ["library738", "service738", "gateway738", "storage738", "network738", "latency738"],
    ),
    (
        ("library738 service738 gateway738 storage738 network738 latency738", 10),
        ["library738", "service738", "gateway738", "storage738", "network738", "latency738"],
    ),
    (
        ("library738 service738 gateway738 storage738 network738 latency738", 18),
        ["library738", "service738", "gateway738", "storage738", "network738", "latency738"],
    ),
    (
        ("library738 service738 gateway738 storage738 network738 latency738", 28),
        ["library738 service738", "gateway738 storage738", "network738 latency738"],
    ),
    (
        ("service738 gateway738 storage738 network738 latency738 buffer738", 6),
        ["service738", "gateway738", "storage738", "network738", "latency738", "buffer738"],
    ),
    (
        ("service738 gateway738 storage738 network738 latency738 buffer738", 10),
        ["service738", "gateway738", "storage738", "network738", "latency738", "buffer738"],
    ),
    (
        ("service738 gateway738 storage738 network738 latency738 buffer738", 18),
        ["service738", "gateway738", "storage738", "network738", "latency738", "buffer738"],
    ),
    (
        ("service738 gateway738 storage738 network738 latency738 buffer738", 28),
        ["service738 gateway738", "storage738 network738", "latency738 buffer738"],
    ),
    (
        ("gateway738 storage738 network738 latency738 buffer738 queue738", 6),
        ["gateway738", "storage738", "network738", "latency738", "buffer738", "queue738"],
    ),
    (
        ("gateway738 storage738 network738 latency738 buffer738 queue738", 10),
        ["gateway738", "storage738", "network738", "latency738", "buffer738", "queue738"],
    ),
    (
        ("gateway738 storage738 network738 latency738 buffer738 queue738", 18),
        ["gateway738", "storage738", "network738", "latency738", "buffer738 queue738"],
    ),
    (
        ("gateway738 storage738 network738 latency738 buffer738 queue738", 28),
        ["gateway738 storage738", "network738 latency738", "buffer738 queue738"],
    ),
    (
        ("storage738 network738 latency738 buffer738 queue738 worker738", 6),
        ["storage738", "network738", "latency738", "buffer738", "queue738", "worker738"],
    ),
    (
        ("storage738 network738 latency738 buffer738 queue738 worker738", 10),
        ["storage738", "network738", "latency738", "buffer738", "queue738", "worker738"],
    ),
    (
        ("storage738 network738 latency738 buffer738 queue738 worker738", 18),
        ["storage738", "network738", "latency738", "buffer738 queue738", "worker738"],
    ),
    (
        ("storage738 network738 latency738 buffer738 queue738 worker738", 28),
        ["storage738 network738", "latency738 buffer738", "queue738 worker738"],
    ),
    (
        ("network738 latency738 buffer738 queue738 worker738 kernel738", 6),
        ["network738", "latency738", "buffer738", "queue738", "worker738", "kernel738"],
    ),
    (
        ("network738 latency738 buffer738 queue738 worker738 kernel738", 10),
        ["network738", "latency738", "buffer738", "queue738", "worker738", "kernel738"],
    ),
    (
        ("network738 latency738 buffer738 queue738 worker738 kernel738", 18),
        ["network738", "latency738", "buffer738 queue738", "worker738", "kernel738"],
    ),
    (
        ("network738 latency738 buffer738 queue738 worker738 kernel738", 28),
        ["network738 latency738", "buffer738 queue738 worker738", "kernel738"],
    ),
    (
        ("latency738 buffer738 queue738 worker738 kernel738 signal738", 6),
        ["latency738", "buffer738", "queue738", "worker738", "kernel738", "signal738"],
    ),
    (
        ("latency738 buffer738 queue738 worker738 kernel738 signal738", 10),
        ["latency738", "buffer738", "queue738", "worker738", "kernel738", "signal738"],
    ),
    (
        ("latency738 buffer738 queue738 worker738 kernel738 signal738", 18),
        ["latency738", "buffer738 queue738", "worker738", "kernel738", "signal738"],
    ),
    (
        ("latency738 buffer738 queue738 worker738 kernel738 signal738", 28),
        ["latency738 buffer738", "queue738 worker738 kernel738", "signal738"],
    ),
    (
        ("buffer738 queue738 worker738 kernel738 signal738 packet738", 6),
        ["buffer738", "queue738", "worker738", "kernel738", "signal738", "packet738"],
    ),
    (
        ("buffer738 queue738 worker738 kernel738 signal738 packet738", 10),
        ["buffer738", "queue738", "worker738", "kernel738", "signal738", "packet738"],
    ),
    (
        ("buffer738 queue738 worker738 kernel738 signal738 packet738", 18),
        ["buffer738 queue738", "worker738", "kernel738", "signal738", "packet738"],
    ),
    (
        ("buffer738 queue738 worker738 kernel738 signal738 packet738", 28),
        ["buffer738 queue738 worker738", "kernel738 signal738", "packet738"],
    ),
    (
        ("queue738 worker738 kernel738 signal738 packet738 router738", 6),
        ["queue738", "worker738", "kernel738", "signal738", "packet738", "router738"],
    ),
    (
        ("queue738 worker738 kernel738 signal738 packet738 router738", 10),
        ["queue738", "worker738", "kernel738", "signal738", "packet738", "router738"],
    ),
    (
        ("queue738 worker738 kernel738 signal738 packet738 router738", 18),
        ["queue738 worker738", "kernel738", "signal738", "packet738", "router738"],
    ),
    (
        ("queue738 worker738 kernel738 signal738 packet738 router738", 28),
        ["queue738 worker738 kernel738", "signal738 packet738", "router738"],
    ),
    (
        ("worker738 kernel738 signal738 packet738 router738 cluster738", 6),
        ["worker738", "kernel738", "signal738", "packet738", "router738", "cluster738"],
    ),
    (
        ("worker738 kernel738 signal738 packet738 router738 cluster738", 10),
        ["worker738", "kernel738", "signal738", "packet738", "router738", "cluster738"],
    ),
    (
        ("worker738 kernel738 signal738 packet738 router738 cluster738", 18),
        ["worker738", "kernel738", "signal738", "packet738", "router738", "cluster738"],
    ),
    (
        ("worker738 kernel738 signal738 packet738 router738 cluster738", 28),
        ["worker738 kernel738", "signal738 packet738", "router738 cluster738"],
    ),
    (
        ("kernel738 signal738 packet738 router738 cluster738 mirror738", 6),
        ["kernel738", "signal738", "packet738", "router738", "cluster738", "mirror738"],
    ),
    (
        ("kernel738 signal738 packet738 router738 cluster738 mirror738", 10),
        ["kernel738", "signal738", "packet738", "router738", "cluster738", "mirror738"],
    ),
    (
        ("kernel738 signal738 packet738 router738 cluster738 mirror738", 18),
        ["kernel738", "signal738", "packet738", "router738", "cluster738", "mirror738"],
    ),
    (
        ("kernel738 signal738 packet738 router738 cluster738 mirror738", 28),
        ["kernel738 signal738", "packet738 router738", "cluster738 mirror738"],
    ),
    (
        ("signal738 packet738 router738 cluster738 mirror738 filter738", 6),
        ["signal738", "packet738", "router738", "cluster738", "mirror738", "filter738"],
    ),
    (
        ("signal738 packet738 router738 cluster738 mirror738 filter738", 10),
        ["signal738", "packet738", "router738", "cluster738", "mirror738", "filter738"],
    ),
    (
        ("signal738 packet738 router738 cluster738 mirror738 filter738", 18),
        ["signal738", "packet738", "router738", "cluster738", "mirror738", "filter738"],
    ),
    (
        ("signal738 packet738 router738 cluster738 mirror738 filter738", 28),
        ["signal738 packet738", "router738 cluster738", "mirror738 filter738"],
    ),
    (
        ("packet738 router738 cluster738 mirror738 filter738 ranking738", 6),
        ["packet738", "router738", "cluster738", "mirror738", "filter738", "ranking738"],
    ),
    (
        ("packet738 router738 cluster738 mirror738 filter738 ranking738", 10),
        ["packet738", "router738", "cluster738", "mirror738", "filter738", "ranking738"],
    ),
    (
        ("packet738 router738 cluster738 mirror738 filter738 ranking738", 18),
        ["packet738", "router738", "cluster738", "mirror738", "filter738", "ranking738"],
    ),
    (
        ("packet738 router738 cluster738 mirror738 filter738 ranking738", 28),
        ["packet738 router738", "cluster738 mirror738", "filter738 ranking738"],
    ),
    (
        ("router738 cluster738 mirror738 filter738 ranking738 encoding738", 6),
        ["router738", "cluster738", "mirror738", "filter738", "ranking738", "encoding738"],
    ),
    (
        ("router738 cluster738 mirror738 filter738 ranking738 encoding738", 10),
        ["router738", "cluster738", "mirror738", "filter738", "ranking738", "encoding738"],
    ),
    (
        ("router738 cluster738 mirror738 filter738 ranking738 encoding738", 18),
        ["router738", "cluster738", "mirror738", "filter738", "ranking738", "encoding738"],
    ),
    (
        ("router738 cluster738 mirror738 filter738 ranking738 encoding738", 28),
        ["router738 cluster738", "mirror738 filter738", "ranking738 encoding738"],
    ),
    (
        ("cluster738 mirror738 filter738 ranking738 encoding738 mapping738", 6),
        ["cluster738", "mirror738", "filter738", "ranking738", "encoding738", "mapping738"],
    ),
    (
        ("cluster738 mirror738 filter738 ranking738 encoding738 mapping738", 10),
        ["cluster738", "mirror738", "filter738", "ranking738", "encoding738", "mapping738"],
    ),
    (
        ("cluster738 mirror738 filter738 ranking738 encoding738 mapping738", 18),
        ["cluster738", "mirror738", "filter738", "ranking738", "encoding738", "mapping738"],
    ),
    (
        ("cluster738 mirror738 filter738 ranking738 encoding738 mapping738", 28),
        ["cluster738 mirror738", "filter738 ranking738", "encoding738 mapping738"],
    ),
    (
        ("mirror738 filter738 ranking738 encoding738 mapping738 record738", 6),
        ["mirror738", "filter738", "ranking738", "encoding738", "mapping738", "record738"],
    ),
    (
        ("mirror738 filter738 ranking738 encoding738 mapping738 record738", 10),
        ["mirror738", "filter738", "ranking738", "encoding738", "mapping738", "record738"],
    ),
    (
        ("mirror738 filter738 ranking738 encoding738 mapping738 record738", 18),
        ["mirror738", "filter738", "ranking738", "encoding738", "mapping738", "record738"],
    ),
    (
        ("mirror738 filter738 ranking738 encoding738 mapping738 record738", 28),
        ["mirror738 filter738", "ranking738 encoding738", "mapping738 record738"],
    ),
    (
        ("filter738 ranking738 encoding738 mapping738 record738 candle738", 6),
        ["filter738", "ranking738", "encoding738", "mapping738", "record738", "candle738"],
    ),
    (
        ("filter738 ranking738 encoding738 mapping738 record738 candle738", 10),
        ["filter738", "ranking738", "encoding738", "mapping738", "record738", "candle738"],
    ),
    (
        ("filter738 ranking738 encoding738 mapping738 record738 candle738", 18),
        ["filter738", "ranking738", "encoding738", "mapping738", "record738", "candle738"],
    ),
    (
        ("filter738 ranking738 encoding738 mapping738 record738 candle738", 28),
        ["filter738 ranking738", "encoding738 mapping738", "record738 candle738"],
    ),
    (
        ("ranking738 encoding738 mapping738 record738 candle738 thread738", 6),
        ["ranking738", "encoding738", "mapping738", "record738", "candle738", "thread738"],
    ),
    (
        ("ranking738 encoding738 mapping738 record738 candle738 thread738", 10),
        ["ranking738", "encoding738", "mapping738", "record738", "candle738", "thread738"],
    ),
    (
        ("ranking738 encoding738 mapping738 record738 candle738 thread738", 18),
        ["ranking738", "encoding738", "mapping738", "record738", "candle738", "thread738"],
    ),
    (
        ("ranking738 encoding738 mapping738 record738 candle738 thread738", 28),
        ["ranking738 encoding738", "mapping738 record738", "candle738 thread738"],
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
