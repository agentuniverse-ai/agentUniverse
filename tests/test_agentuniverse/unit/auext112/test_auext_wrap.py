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
        ("round 112: the quick brown fox jumps over the lazy dog", 4),
        ["round", "112:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", 8),
        ["round", "112: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", 12),
        ["round 112:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", 16),
        ["round 112: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", 24),
        ["round 112: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 112: the quick brown fox jumps over the lazy dog", 32),
        ["round 112: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", 4),
        ["round", "112:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", 8),
        ["round", "112:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", 12),
        ["round 112:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", 16),
        ["round 112:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", 24),
        ["round 112: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 112: agentuniverse is a framework for multi agents", 32),
        ["round 112: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", 4),
        ["round", "112:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", 8),
        ["round", "112:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", 12),
        ["round 112:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", 16),
        ["round 112:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", 24),
        ["round 112: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 112: knowledge stored as vectors enables retrieval", 32),
        ["round 112: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 112: the processor reads the record then stops", 4),
        ["round", "112:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 112: the processor reads the record then stops", 8),
        ["round", "112: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 112: the processor reads the record then stops", 12),
        ["round 112:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 112: the processor reads the record then stops", 16),
        ["round 112: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 112: the processor reads the record then stops", 24),
        ["round 112: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 112: the processor reads the record then stops", 32),
        ["round 112: the processor reads", "the record then stops"],
    ),
    (
        ("round 112: a worker pulls the next task from the queue", 4),
        ["round", "112:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 112: a worker pulls the next task from the queue", 8),
        ["round", "112: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 112: a worker pulls the next task from the queue", 12),
        ["round 112: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 112: a worker pulls the next task from the queue", 16),
        ["round 112: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 112: a worker pulls the next task from the queue", 24),
        ["round 112: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 112: a worker pulls the next task from the queue", 32),
        ["round 112: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 112: signals travel through the network layer", 4),
        ["round", "112:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 112: signals travel through the network layer", 8),
        ["round", "112:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 112: signals travel through the network layer", 12),
        ["round 112:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 112: signals travel through the network layer", 16),
        ["round 112:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 112: signals travel through the network layer", 24),
        ["round 112: signals", "travel through the", "network layer"],
    ),
    (
        ("round 112: signals travel through the network layer", 32),
        ["round 112: signals travel", "through the network layer"],
    ),
    (
        ("round 112: the gateway routes each request by policy", 4),
        ["round", "112:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 112: the gateway routes each request by policy", 8),
        ["round", "112: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 112: the gateway routes each request by policy", 12),
        ["round 112:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 112: the gateway routes each request by policy", 16),
        ["round 112: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 112: the gateway routes each request by policy", 24),
        ["round 112: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 112: the gateway routes each request by policy", 32),
        ["round 112: the gateway routes", "each request by policy"],
    ),
    (
        ("round 112: memory grows until the buffer is full", 4),
        ["round", "112:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 112: memory grows until the buffer is full", 8),
        ["round", "112:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 112: memory grows until the buffer is full", 12),
        ["round 112:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 112: memory grows until the buffer is full", 16),
        ["round 112:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 112: memory grows until the buffer is full", 24), ["round 112: memory grows", "until the buffer is full"]),
    (("round 112: memory grows until the buffer is full", 32), ["round 112: memory grows until", "the buffer is full"]),
    (
        ("round 112: the cluster mirrors every packet twice", 4),
        ["round", "112:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 112: the cluster mirrors every packet twice", 8),
        ["round", "112: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 112: the cluster mirrors every packet twice", 12),
        ["round 112:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 112: the cluster mirrors every packet twice", 16),
        ["round 112: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 112: the cluster mirrors every packet twice", 24),
        ["round 112: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 112: the cluster mirrors every packet twice", 32),
        ["round 112: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", 4),
        ["round", "112:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", 8),
        ["round", "112:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", 12),
        ["round 112:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", 16),
        ["round 112:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", 24),
        ["round 112: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 112: ranking uses tokens learned from the corpus", 32),
        ["round 112: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 112: a long session ends when the candle dies", 4),
        ["round", "112:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 112: a long session ends when the candle dies", 8),
        ["round", "112: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 112: a long session ends when the candle dies", 12),
        ["round 112: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 112: a long session ends when the candle dies", 16),
        ["round 112: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 112: a long session ends when the candle dies", 24),
        ["round 112: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 112: a long session ends when the candle dies", 32),
        ["round 112: a long session ends", "when the candle dies"],
    ),
    (
        ("round 112: encode the prompt then map the result", 4),
        ["round", "112:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 112: encode the prompt then map the result", 8),
        ["round", "112:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 112: encode the prompt then map the result", 12),
        ["round 112:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 112: encode the prompt then map the result", 16),
        ["round 112:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 112: encode the prompt then map the result", 24),
        ["round 112: encode the", "prompt then map the", "result"],
    ),
    (("round 112: encode the prompt then map the result", 32), ["round 112: encode the prompt", "then map the result"]),
    (
        ("round 112: the kernel wakes the worker at dawn", 4),
        ["round", "112:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 112: the kernel wakes the worker at dawn", 8),
        ["round", "112: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 112: the kernel wakes the worker at dawn", 12),
        ["round 112:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 112: the kernel wakes the worker at dawn", 16), ["round 112: the", "kernel wakes the", "worker at dawn"]),
    (("round 112: the kernel wakes the worker at dawn", 24), ["round 112: the kernel", "wakes the worker at dawn"]),
    (("round 112: the kernel wakes the worker at dawn", 32), ["round 112: the kernel wakes the", "worker at dawn"]),
    (
        ("round 112: service latency drops after the patch", 4),
        ["round", "112:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 112: service latency drops after the patch", 8),
        ["round", "112:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 112: service latency drops after the patch", 12),
        ["round 112:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 112: service latency drops after the patch", 16),
        ["round 112:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 112: service latency drops after the patch", 24),
        ["round 112: service", "latency drops after the", "patch"],
    ),
    (("round 112: service latency drops after the patch", 32), ["round 112: service latency drops", "after the patch"]),
    (
        ("round 112: the library caches every vector it sees", 4),
        ["round", "112:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 112: the library caches every vector it sees", 8),
        ["round", "112: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 112: the library caches every vector it sees", 12),
        ["round 112:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 112: the library caches every vector it sees", 16),
        ["round 112: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 112: the library caches every vector it sees", 24),
        ["round 112: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 112: the library caches every vector it sees", 32),
        ["round 112: the library caches", "every vector it sees"],
    ),
    (
        ("round 112: agents argue then the debate resolves", 4),
        ["round", "112:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 112: agents argue then the debate resolves", 8),
        ["round", "112:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 112: agents argue then the debate resolves", 12),
        ["round 112:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 112: agents argue then the debate resolves", 16),
        ["round 112:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 112: agents argue then the debate resolves", 24), ["round 112: agents argue", "then the debate resolves"]),
    (("round 112: agents argue then the debate resolves", 32), ["round 112: agents argue then the", "debate resolves"]),
    (
        ("round 112: the filter keeps only strong matches", 4),
        ["round", "112:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 112: the filter keeps only strong matches", 8),
        ["round", "112: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 112: the filter keeps only strong matches", 12),
        ["round 112:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 112: the filter keeps only strong matches", 16),
        ["round 112: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 112: the filter keeps only strong matches", 24),
        ["round 112: the filter", "keeps only strong", "matches"],
    ),
    (("round 112: the filter keeps only strong matches", 32), ["round 112: the filter keeps only", "strong matches"]),
    (
        ("round 112: the model answers with a short reply", 4),
        ["round", "112:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 112: the model answers with a short reply", 8),
        ["round", "112: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 112: the model answers with a short reply", 12),
        ["round 112:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 112: the model answers with a short reply", 16),
        ["round 112: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 112: the model answers with a short reply", 24),
        ["round 112: the model", "answers with a short", "reply"],
    ),
    (("round 112: the model answers with a short reply", 32), ["round 112: the model answers", "with a short reply"]),
    (
        ("round 112: the recorder stores the reasoning trace", 4),
        ["round", "112:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 112: the recorder stores the reasoning trace", 8),
        ["round", "112: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 112: the recorder stores the reasoning trace", 12),
        ["round 112:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 112: the recorder stores the reasoning trace", 16),
        ["round 112: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 112: the recorder stores the reasoning trace", 24),
        ["round 112: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 112: the recorder stores the reasoning trace", 32),
        ["round 112: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 112: the angel watches the processor run", 4),
        ["round", "112:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 112: the angel watches the processor run", 8),
        ["round", "112: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 112: the angel watches the processor run", 12),
        ["round 112:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 112: the angel watches the processor run", 16),
        ["round 112: the", "angel watches", "the processor", "run"],
    ),
    (("round 112: the angel watches the processor run", 24), ["round 112: the angel", "watches the processor", "run"]),
    (("round 112: the angel watches the processor run", 32), ["round 112: the angel watches the", "processor run"]),
    (
        ("round 112: angle of the vector decides the match", 4),
        ["round", "112:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 112: angle of the vector decides the match", 8),
        ["round", "112:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 112: angle of the vector decides the match", 12),
        ["round 112:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 112: angle of the vector decides the match", 16),
        ["round 112: angle", "of the vector", "decides the", "match"],
    ),
    (("round 112: angle of the vector decides the match", 24), ["round 112: angle of the", "vector decides the match"]),
    (("round 112: angle of the vector decides the match", 32), ["round 112: angle of the vector", "decides the match"]),
    (
        ("round 112: the candle burns twice as long at night", 4),
        ["round", "112:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 112: the candle burns twice as long at night", 8),
        ["round", "112: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 112: the candle burns twice as long at night", 12),
        ["round 112:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 112: the candle burns twice as long at night", 16),
        ["round 112: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 112: the candle burns twice as long at night", 24),
        ["round 112: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 112: the candle burns twice as long at night", 32),
        ["round 112: the candle burns", "twice as long at night"],
    ),
    (
        ("round 112: a mirror of the universe in one line", 4),
        ["round", "112:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 112: a mirror of the universe in one line", 8),
        ["round", "112: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 112: a mirror of the universe in one line", 12),
        ["round 112: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 112: a mirror of the universe in one line", 16),
        ["round 112: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 112: a mirror of the universe in one line", 24), ["round 112: a mirror of", "the universe in one line"]),
    (("round 112: a mirror of the universe in one line", 32), ["round 112: a mirror of the", "universe in one line"]),
    (
        ("round 112: the queue drains before the storm", 4),
        ["round", "112:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 112: the queue drains before the storm", 8),
        ["round", "112: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 112: the queue drains before the storm", 12),
        ["round 112:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 112: the queue drains before the storm", 16), ["round 112: the", "queue drains", "before the storm"]),
    (("round 112: the queue drains before the storm", 24), ["round 112: the queue", "drains before the storm"]),
    (("round 112: the queue drains before the storm", 32), ["round 112: the queue drains", "before the storm"]),
    (
        ("kitten112 sitting112 agent112 angle112 universe112 memory112", 6),
        ["kitten112", "sitting112", "agent112", "angle112", "universe112", "memory112"],
    ),
    (
        ("kitten112 sitting112 agent112 angle112 universe112 memory112", 10),
        ["kitten112", "sitting112", "agent112", "angle112", "universe112", "memory112"],
    ),
    (
        ("kitten112 sitting112 agent112 angle112 universe112 memory112", 18),
        ["kitten112", "sitting112", "agent112 angle112", "universe112", "memory112"],
    ),
    (
        ("kitten112 sitting112 agent112 angle112 universe112 memory112", 28),
        ["kitten112 sitting112", "agent112 angle112", "universe112 memory112"],
    ),
    (
        ("sitting112 agent112 angle112 universe112 memory112 stream112", 6),
        ["sitting112", "agent112", "angle112", "universe112", "memory112", "stream112"],
    ),
    (
        ("sitting112 agent112 angle112 universe112 memory112 stream112", 10),
        ["sitting112", "agent112", "angle112", "universe112", "memory112", "stream112"],
    ),
    (
        ("sitting112 agent112 angle112 universe112 memory112 stream112", 18),
        ["sitting112", "agent112 angle112", "universe112", "memory112", "stream112"],
    ),
    (
        ("sitting112 agent112 angle112 universe112 memory112 stream112", 28),
        ["sitting112 agent112 angle112", "universe112 memory112", "stream112"],
    ),
    (
        ("agent112 angle112 universe112 memory112 stream112 context112", 6),
        ["agent112", "angle112", "universe112", "memory112", "stream112", "context112"],
    ),
    (
        ("agent112 angle112 universe112 memory112 stream112 context112", 10),
        ["agent112", "angle112", "universe112", "memory112", "stream112", "context112"],
    ),
    (
        ("agent112 angle112 universe112 memory112 stream112 context112", 18),
        ["agent112 angle112", "universe112", "memory112", "stream112", "context112"],
    ),
    (
        ("agent112 angle112 universe112 memory112 stream112 context112", 28),
        ["agent112 angle112", "universe112 memory112", "stream112 context112"],
    ),
    (
        ("angle112 universe112 memory112 stream112 context112 knowledge112", 6),
        ["angle112", "universe112", "memory112", "stream112", "context112", "knowledge112"],
    ),
    (
        ("angle112 universe112 memory112 stream112 context112 knowledge112", 10),
        ["angle112", "universe112", "memory112", "stream112", "context112", "knowledge112"],
    ),
    (
        ("angle112 universe112 memory112 stream112 context112 knowledge112", 18),
        ["angle112", "universe112", "memory112", "stream112", "context112", "knowledge112"],
    ),
    (
        ("angle112 universe112 memory112 stream112 context112 knowledge112", 28),
        ["angle112 universe112", "memory112 stream112", "context112 knowledge112"],
    ),
    (
        ("universe112 memory112 stream112 context112 knowledge112 vector112", 6),
        ["universe112", "memory112", "stream112", "context112", "knowledge112", "vector112"],
    ),
    (
        ("universe112 memory112 stream112 context112 knowledge112 vector112", 10),
        ["universe112", "memory112", "stream112", "context112", "knowledge112", "vector112"],
    ),
    (
        ("universe112 memory112 stream112 context112 knowledge112 vector112", 18),
        ["universe112", "memory112", "stream112", "context112", "knowledge112", "vector112"],
    ),
    (
        ("universe112 memory112 stream112 context112 knowledge112 vector112", 28),
        ["universe112 memory112", "stream112 context112", "knowledge112 vector112"],
    ),
    (
        ("memory112 stream112 context112 knowledge112 vector112 processor112", 6),
        ["memory112", "stream112", "context112", "knowledge112", "vector112", "processor112"],
    ),
    (
        ("memory112 stream112 context112 knowledge112 vector112 processor112", 10),
        ["memory112", "stream112", "context112", "knowledge112", "vector112", "processor112"],
    ),
    (
        ("memory112 stream112 context112 knowledge112 vector112 processor112", 18),
        ["memory112", "stream112", "context112", "knowledge112", "vector112", "processor112"],
    ),
    (
        ("memory112 stream112 context112 knowledge112 vector112 processor112", 28),
        ["memory112 stream112", "context112 knowledge112", "vector112 processor112"],
    ),
    (
        ("stream112 context112 knowledge112 vector112 processor112 reasoning112", 6),
        ["stream112", "context112", "knowledge112", "vector112", "processor112", "reasoning112"],
    ),
    (
        ("stream112 context112 knowledge112 vector112 processor112 reasoning112", 10),
        ["stream112", "context112", "knowledge112", "vector112", "processor112", "reasoning112"],
    ),
    (
        ("stream112 context112 knowledge112 vector112 processor112 reasoning112", 18),
        ["stream112", "context112", "knowledge112", "vector112", "processor112", "reasoning112"],
    ),
    (
        ("stream112 context112 knowledge112 vector112 processor112 reasoning112", 28),
        ["stream112 context112", "knowledge112 vector112", "processor112 reasoning112"],
    ),
    (
        ("context112 knowledge112 vector112 processor112 reasoning112 machine112", 6),
        ["context112", "knowledge112", "vector112", "processor112", "reasoning112", "machine112"],
    ),
    (
        ("context112 knowledge112 vector112 processor112 reasoning112 machine112", 10),
        ["context112", "knowledge112", "vector112", "processor112", "reasoning112", "machine112"],
    ),
    (
        ("context112 knowledge112 vector112 processor112 reasoning112 machine112", 18),
        ["context112", "knowledge112", "vector112", "processor112", "reasoning112", "machine112"],
    ),
    (
        ("context112 knowledge112 vector112 processor112 reasoning112 machine112", 28),
        ["context112 knowledge112", "vector112 processor112", "reasoning112 machine112"],
    ),
    (
        ("knowledge112 vector112 processor112 reasoning112 machine112 learning112", 6),
        ["knowledge112", "vector112", "processor112", "reasoning112", "machine112", "learning112"],
    ),
    (
        ("knowledge112 vector112 processor112 reasoning112 machine112 learning112", 10),
        ["knowledge112", "vector112", "processor112", "reasoning112", "machine112", "learning112"],
    ),
    (
        ("knowledge112 vector112 processor112 reasoning112 machine112 learning112", 18),
        ["knowledge112", "vector112", "processor112", "reasoning112", "machine112", "learning112"],
    ),
    (
        ("knowledge112 vector112 processor112 reasoning112 machine112 learning112", 28),
        ["knowledge112 vector112", "processor112 reasoning112", "machine112 learning112"],
    ),
    (
        ("vector112 processor112 reasoning112 machine112 learning112 model112", 6),
        ["vector112", "processor112", "reasoning112", "machine112", "learning112", "model112"],
    ),
    (
        ("vector112 processor112 reasoning112 machine112 learning112 model112", 10),
        ["vector112", "processor112", "reasoning112", "machine112", "learning112", "model112"],
    ),
    (
        ("vector112 processor112 reasoning112 machine112 learning112 model112", 18),
        ["vector112", "processor112", "reasoning112", "machine112", "learning112", "model112"],
    ),
    (
        ("vector112 processor112 reasoning112 machine112 learning112 model112", 28),
        ["vector112 processor112", "reasoning112 machine112", "learning112 model112"],
    ),
    (
        ("processor112 reasoning112 machine112 learning112 model112 token112", 6),
        ["processor112", "reasoning112", "machine112", "learning112", "model112", "token112"],
    ),
    (
        ("processor112 reasoning112 machine112 learning112 model112 token112", 10),
        ["processor112", "reasoning112", "machine112", "learning112", "model112", "token112"],
    ),
    (
        ("processor112 reasoning112 machine112 learning112 model112 token112", 18),
        ["processor112", "reasoning112", "machine112", "learning112", "model112 token112"],
    ),
    (
        ("processor112 reasoning112 machine112 learning112 model112 token112", 28),
        ["processor112 reasoning112", "machine112 learning112", "model112 token112"],
    ),
    (
        ("reasoning112 machine112 learning112 model112 token112 prompt112", 6),
        ["reasoning112", "machine112", "learning112", "model112", "token112", "prompt112"],
    ),
    (
        ("reasoning112 machine112 learning112 model112 token112 prompt112", 10),
        ["reasoning112", "machine112", "learning112", "model112", "token112", "prompt112"],
    ),
    (
        ("reasoning112 machine112 learning112 model112 token112 prompt112", 18),
        ["reasoning112", "machine112", "learning112", "model112 token112", "prompt112"],
    ),
    (
        ("reasoning112 machine112 learning112 model112 token112 prompt112", 28),
        ["reasoning112 machine112", "learning112 model112", "token112 prompt112"],
    ),
    (
        ("machine112 learning112 model112 token112 prompt112 session112", 6),
        ["machine112", "learning112", "model112", "token112", "prompt112", "session112"],
    ),
    (
        ("machine112 learning112 model112 token112 prompt112 session112", 10),
        ["machine112", "learning112", "model112", "token112", "prompt112", "session112"],
    ),
    (
        ("machine112 learning112 model112 token112 prompt112 session112", 18),
        ["machine112", "learning112", "model112 token112", "prompt112", "session112"],
    ),
    (
        ("machine112 learning112 model112 token112 prompt112 session112", 28),
        ["machine112 learning112", "model112 token112 prompt112", "session112"],
    ),
    (
        ("learning112 model112 token112 prompt112 session112 library112", 6),
        ["learning112", "model112", "token112", "prompt112", "session112", "library112"],
    ),
    (
        ("learning112 model112 token112 prompt112 session112 library112", 10),
        ["learning112", "model112", "token112", "prompt112", "session112", "library112"],
    ),
    (
        ("learning112 model112 token112 prompt112 session112 library112", 18),
        ["learning112", "model112 token112", "prompt112", "session112", "library112"],
    ),
    (
        ("learning112 model112 token112 prompt112 session112 library112", 28),
        ["learning112 model112", "token112 prompt112", "session112 library112"],
    ),
    (
        ("model112 token112 prompt112 session112 library112 service112", 6),
        ["model112", "token112", "prompt112", "session112", "library112", "service112"],
    ),
    (
        ("model112 token112 prompt112 session112 library112 service112", 10),
        ["model112", "token112", "prompt112", "session112", "library112", "service112"],
    ),
    (
        ("model112 token112 prompt112 session112 library112 service112", 18),
        ["model112 token112", "prompt112", "session112", "library112", "service112"],
    ),
    (
        ("model112 token112 prompt112 session112 library112 service112", 28),
        ["model112 token112 prompt112", "session112 library112", "service112"],
    ),
    (
        ("token112 prompt112 session112 library112 service112 gateway112", 6),
        ["token112", "prompt112", "session112", "library112", "service112", "gateway112"],
    ),
    (
        ("token112 prompt112 session112 library112 service112 gateway112", 10),
        ["token112", "prompt112", "session112", "library112", "service112", "gateway112"],
    ),
    (
        ("token112 prompt112 session112 library112 service112 gateway112", 18),
        ["token112 prompt112", "session112", "library112", "service112", "gateway112"],
    ),
    (
        ("token112 prompt112 session112 library112 service112 gateway112", 28),
        ["token112 prompt112", "session112 library112", "service112 gateway112"],
    ),
    (
        ("prompt112 session112 library112 service112 gateway112 storage112", 6),
        ["prompt112", "session112", "library112", "service112", "gateway112", "storage112"],
    ),
    (
        ("prompt112 session112 library112 service112 gateway112 storage112", 10),
        ["prompt112", "session112", "library112", "service112", "gateway112", "storage112"],
    ),
    (
        ("prompt112 session112 library112 service112 gateway112 storage112", 18),
        ["prompt112", "session112", "library112", "service112", "gateway112", "storage112"],
    ),
    (
        ("prompt112 session112 library112 service112 gateway112 storage112", 28),
        ["prompt112 session112", "library112 service112", "gateway112 storage112"],
    ),
    (
        ("session112 library112 service112 gateway112 storage112 network112", 6),
        ["session112", "library112", "service112", "gateway112", "storage112", "network112"],
    ),
    (
        ("session112 library112 service112 gateway112 storage112 network112", 10),
        ["session112", "library112", "service112", "gateway112", "storage112", "network112"],
    ),
    (
        ("session112 library112 service112 gateway112 storage112 network112", 18),
        ["session112", "library112", "service112", "gateway112", "storage112", "network112"],
    ),
    (
        ("session112 library112 service112 gateway112 storage112 network112", 28),
        ["session112 library112", "service112 gateway112", "storage112 network112"],
    ),
    (
        ("library112 service112 gateway112 storage112 network112 latency112", 6),
        ["library112", "service112", "gateway112", "storage112", "network112", "latency112"],
    ),
    (
        ("library112 service112 gateway112 storage112 network112 latency112", 10),
        ["library112", "service112", "gateway112", "storage112", "network112", "latency112"],
    ),
    (
        ("library112 service112 gateway112 storage112 network112 latency112", 18),
        ["library112", "service112", "gateway112", "storage112", "network112", "latency112"],
    ),
    (
        ("library112 service112 gateway112 storage112 network112 latency112", 28),
        ["library112 service112", "gateway112 storage112", "network112 latency112"],
    ),
    (
        ("service112 gateway112 storage112 network112 latency112 buffer112", 6),
        ["service112", "gateway112", "storage112", "network112", "latency112", "buffer112"],
    ),
    (
        ("service112 gateway112 storage112 network112 latency112 buffer112", 10),
        ["service112", "gateway112", "storage112", "network112", "latency112", "buffer112"],
    ),
    (
        ("service112 gateway112 storage112 network112 latency112 buffer112", 18),
        ["service112", "gateway112", "storage112", "network112", "latency112", "buffer112"],
    ),
    (
        ("service112 gateway112 storage112 network112 latency112 buffer112", 28),
        ["service112 gateway112", "storage112 network112", "latency112 buffer112"],
    ),
    (
        ("gateway112 storage112 network112 latency112 buffer112 queue112", 6),
        ["gateway112", "storage112", "network112", "latency112", "buffer112", "queue112"],
    ),
    (
        ("gateway112 storage112 network112 latency112 buffer112 queue112", 10),
        ["gateway112", "storage112", "network112", "latency112", "buffer112", "queue112"],
    ),
    (
        ("gateway112 storage112 network112 latency112 buffer112 queue112", 18),
        ["gateway112", "storage112", "network112", "latency112", "buffer112 queue112"],
    ),
    (
        ("gateway112 storage112 network112 latency112 buffer112 queue112", 28),
        ["gateway112 storage112", "network112 latency112", "buffer112 queue112"],
    ),
    (
        ("storage112 network112 latency112 buffer112 queue112 worker112", 6),
        ["storage112", "network112", "latency112", "buffer112", "queue112", "worker112"],
    ),
    (
        ("storage112 network112 latency112 buffer112 queue112 worker112", 10),
        ["storage112", "network112", "latency112", "buffer112", "queue112", "worker112"],
    ),
    (
        ("storage112 network112 latency112 buffer112 queue112 worker112", 18),
        ["storage112", "network112", "latency112", "buffer112 queue112", "worker112"],
    ),
    (
        ("storage112 network112 latency112 buffer112 queue112 worker112", 28),
        ["storage112 network112", "latency112 buffer112", "queue112 worker112"],
    ),
    (
        ("network112 latency112 buffer112 queue112 worker112 kernel112", 6),
        ["network112", "latency112", "buffer112", "queue112", "worker112", "kernel112"],
    ),
    (
        ("network112 latency112 buffer112 queue112 worker112 kernel112", 10),
        ["network112", "latency112", "buffer112", "queue112", "worker112", "kernel112"],
    ),
    (
        ("network112 latency112 buffer112 queue112 worker112 kernel112", 18),
        ["network112", "latency112", "buffer112 queue112", "worker112", "kernel112"],
    ),
    (
        ("network112 latency112 buffer112 queue112 worker112 kernel112", 28),
        ["network112 latency112", "buffer112 queue112 worker112", "kernel112"],
    ),
    (
        ("latency112 buffer112 queue112 worker112 kernel112 signal112", 6),
        ["latency112", "buffer112", "queue112", "worker112", "kernel112", "signal112"],
    ),
    (
        ("latency112 buffer112 queue112 worker112 kernel112 signal112", 10),
        ["latency112", "buffer112", "queue112", "worker112", "kernel112", "signal112"],
    ),
    (
        ("latency112 buffer112 queue112 worker112 kernel112 signal112", 18),
        ["latency112", "buffer112 queue112", "worker112", "kernel112", "signal112"],
    ),
    (
        ("latency112 buffer112 queue112 worker112 kernel112 signal112", 28),
        ["latency112 buffer112", "queue112 worker112 kernel112", "signal112"],
    ),
    (
        ("buffer112 queue112 worker112 kernel112 signal112 packet112", 6),
        ["buffer112", "queue112", "worker112", "kernel112", "signal112", "packet112"],
    ),
    (
        ("buffer112 queue112 worker112 kernel112 signal112 packet112", 10),
        ["buffer112", "queue112", "worker112", "kernel112", "signal112", "packet112"],
    ),
    (
        ("buffer112 queue112 worker112 kernel112 signal112 packet112", 18),
        ["buffer112 queue112", "worker112", "kernel112", "signal112", "packet112"],
    ),
    (
        ("buffer112 queue112 worker112 kernel112 signal112 packet112", 28),
        ["buffer112 queue112 worker112", "kernel112 signal112", "packet112"],
    ),
    (
        ("queue112 worker112 kernel112 signal112 packet112 router112", 6),
        ["queue112", "worker112", "kernel112", "signal112", "packet112", "router112"],
    ),
    (
        ("queue112 worker112 kernel112 signal112 packet112 router112", 10),
        ["queue112", "worker112", "kernel112", "signal112", "packet112", "router112"],
    ),
    (
        ("queue112 worker112 kernel112 signal112 packet112 router112", 18),
        ["queue112 worker112", "kernel112", "signal112", "packet112", "router112"],
    ),
    (
        ("queue112 worker112 kernel112 signal112 packet112 router112", 28),
        ["queue112 worker112 kernel112", "signal112 packet112", "router112"],
    ),
    (
        ("worker112 kernel112 signal112 packet112 router112 cluster112", 6),
        ["worker112", "kernel112", "signal112", "packet112", "router112", "cluster112"],
    ),
    (
        ("worker112 kernel112 signal112 packet112 router112 cluster112", 10),
        ["worker112", "kernel112", "signal112", "packet112", "router112", "cluster112"],
    ),
    (
        ("worker112 kernel112 signal112 packet112 router112 cluster112", 18),
        ["worker112", "kernel112", "signal112", "packet112", "router112", "cluster112"],
    ),
    (
        ("worker112 kernel112 signal112 packet112 router112 cluster112", 28),
        ["worker112 kernel112", "signal112 packet112", "router112 cluster112"],
    ),
    (
        ("kernel112 signal112 packet112 router112 cluster112 mirror112", 6),
        ["kernel112", "signal112", "packet112", "router112", "cluster112", "mirror112"],
    ),
    (
        ("kernel112 signal112 packet112 router112 cluster112 mirror112", 10),
        ["kernel112", "signal112", "packet112", "router112", "cluster112", "mirror112"],
    ),
    (
        ("kernel112 signal112 packet112 router112 cluster112 mirror112", 18),
        ["kernel112", "signal112", "packet112", "router112", "cluster112", "mirror112"],
    ),
    (
        ("kernel112 signal112 packet112 router112 cluster112 mirror112", 28),
        ["kernel112 signal112", "packet112 router112", "cluster112 mirror112"],
    ),
    (
        ("signal112 packet112 router112 cluster112 mirror112 filter112", 6),
        ["signal112", "packet112", "router112", "cluster112", "mirror112", "filter112"],
    ),
    (
        ("signal112 packet112 router112 cluster112 mirror112 filter112", 10),
        ["signal112", "packet112", "router112", "cluster112", "mirror112", "filter112"],
    ),
    (
        ("signal112 packet112 router112 cluster112 mirror112 filter112", 18),
        ["signal112", "packet112", "router112", "cluster112", "mirror112", "filter112"],
    ),
    (
        ("signal112 packet112 router112 cluster112 mirror112 filter112", 28),
        ["signal112 packet112", "router112 cluster112", "mirror112 filter112"],
    ),
    (
        ("packet112 router112 cluster112 mirror112 filter112 ranking112", 6),
        ["packet112", "router112", "cluster112", "mirror112", "filter112", "ranking112"],
    ),
    (
        ("packet112 router112 cluster112 mirror112 filter112 ranking112", 10),
        ["packet112", "router112", "cluster112", "mirror112", "filter112", "ranking112"],
    ),
    (
        ("packet112 router112 cluster112 mirror112 filter112 ranking112", 18),
        ["packet112", "router112", "cluster112", "mirror112", "filter112", "ranking112"],
    ),
    (
        ("packet112 router112 cluster112 mirror112 filter112 ranking112", 28),
        ["packet112 router112", "cluster112 mirror112", "filter112 ranking112"],
    ),
    (
        ("router112 cluster112 mirror112 filter112 ranking112 encoding112", 6),
        ["router112", "cluster112", "mirror112", "filter112", "ranking112", "encoding112"],
    ),
    (
        ("router112 cluster112 mirror112 filter112 ranking112 encoding112", 10),
        ["router112", "cluster112", "mirror112", "filter112", "ranking112", "encoding112"],
    ),
    (
        ("router112 cluster112 mirror112 filter112 ranking112 encoding112", 18),
        ["router112", "cluster112", "mirror112", "filter112", "ranking112", "encoding112"],
    ),
    (
        ("router112 cluster112 mirror112 filter112 ranking112 encoding112", 28),
        ["router112 cluster112", "mirror112 filter112", "ranking112 encoding112"],
    ),
    (
        ("cluster112 mirror112 filter112 ranking112 encoding112 mapping112", 6),
        ["cluster112", "mirror112", "filter112", "ranking112", "encoding112", "mapping112"],
    ),
    (
        ("cluster112 mirror112 filter112 ranking112 encoding112 mapping112", 10),
        ["cluster112", "mirror112", "filter112", "ranking112", "encoding112", "mapping112"],
    ),
    (
        ("cluster112 mirror112 filter112 ranking112 encoding112 mapping112", 18),
        ["cluster112", "mirror112", "filter112", "ranking112", "encoding112", "mapping112"],
    ),
    (
        ("cluster112 mirror112 filter112 ranking112 encoding112 mapping112", 28),
        ["cluster112 mirror112", "filter112 ranking112", "encoding112 mapping112"],
    ),
    (
        ("mirror112 filter112 ranking112 encoding112 mapping112 record112", 6),
        ["mirror112", "filter112", "ranking112", "encoding112", "mapping112", "record112"],
    ),
    (
        ("mirror112 filter112 ranking112 encoding112 mapping112 record112", 10),
        ["mirror112", "filter112", "ranking112", "encoding112", "mapping112", "record112"],
    ),
    (
        ("mirror112 filter112 ranking112 encoding112 mapping112 record112", 18),
        ["mirror112", "filter112", "ranking112", "encoding112", "mapping112", "record112"],
    ),
    (
        ("mirror112 filter112 ranking112 encoding112 mapping112 record112", 28),
        ["mirror112 filter112", "ranking112 encoding112", "mapping112 record112"],
    ),
    (
        ("filter112 ranking112 encoding112 mapping112 record112 candle112", 6),
        ["filter112", "ranking112", "encoding112", "mapping112", "record112", "candle112"],
    ),
    (
        ("filter112 ranking112 encoding112 mapping112 record112 candle112", 10),
        ["filter112", "ranking112", "encoding112", "mapping112", "record112", "candle112"],
    ),
    (
        ("filter112 ranking112 encoding112 mapping112 record112 candle112", 18),
        ["filter112", "ranking112", "encoding112", "mapping112", "record112", "candle112"],
    ),
    (
        ("filter112 ranking112 encoding112 mapping112 record112 candle112", 28),
        ["filter112 ranking112", "encoding112 mapping112", "record112 candle112"],
    ),
    (
        ("ranking112 encoding112 mapping112 record112 candle112 thread112", 6),
        ["ranking112", "encoding112", "mapping112", "record112", "candle112", "thread112"],
    ),
    (
        ("ranking112 encoding112 mapping112 record112 candle112 thread112", 10),
        ["ranking112", "encoding112", "mapping112", "record112", "candle112", "thread112"],
    ),
    (
        ("ranking112 encoding112 mapping112 record112 candle112 thread112", 18),
        ["ranking112", "encoding112", "mapping112", "record112", "candle112", "thread112"],
    ),
    (
        ("ranking112 encoding112 mapping112 record112 candle112 thread112", 28),
        ["ranking112 encoding112", "mapping112 record112", "candle112 thread112"],
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
