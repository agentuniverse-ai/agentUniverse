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
        ("round 58: the quick brown fox jumps over the lazy dog", 4),
        ["round", "58:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 58: the quick brown fox jumps over the lazy dog", 8),
        ["round", "58: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 58: the quick brown fox jumps over the lazy dog", 12),
        ["round 58:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 58: the quick brown fox jumps over the lazy dog", 16),
        ["round 58: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 58: the quick brown fox jumps over the lazy dog", 24),
        ["round 58: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 58: the quick brown fox jumps over the lazy dog", 32),
        ["round 58: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 58: agentuniverse is a framework for multi agents", 4),
        ["round", "58:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 58: agentuniverse is a framework for multi agents", 8),
        ["round", "58:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 58: agentuniverse is a framework for multi agents", 12),
        ["round 58:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 58: agentuniverse is a framework for multi agents", 16),
        ["round 58:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 58: agentuniverse is a framework for multi agents", 24),
        ["round 58: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 58: agentuniverse is a framework for multi agents", 32),
        ["round 58: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 58: knowledge stored as vectors enables retrieval", 4),
        ["round", "58:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 58: knowledge stored as vectors enables retrieval", 8),
        ["round", "58:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 58: knowledge stored as vectors enables retrieval", 12),
        ["round 58:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 58: knowledge stored as vectors enables retrieval", 16),
        ["round 58:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 58: knowledge stored as vectors enables retrieval", 24),
        ["round 58: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 58: knowledge stored as vectors enables retrieval", 32),
        ["round 58: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 58: the processor reads the record then stops", 4),
        ["round", "58:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 58: the processor reads the record then stops", 8),
        ["round", "58: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 58: the processor reads the record then stops", 12),
        ["round 58:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 58: the processor reads the record then stops", 16),
        ["round 58: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 58: the processor reads the record then stops", 24),
        ["round 58: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 58: the processor reads the record then stops", 32),
        ["round 58: the processor reads", "the record then stops"],
    ),
    (
        ("round 58: a worker pulls the next task from the queue", 4),
        ["round", "58:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 58: a worker pulls the next task from the queue", 8),
        ["round", "58: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 58: a worker pulls the next task from the queue", 12),
        ["round 58: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 58: a worker pulls the next task from the queue", 16),
        ["round 58: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 58: a worker pulls the next task from the queue", 24),
        ["round 58: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 58: a worker pulls the next task from the queue", 32),
        ["round 58: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 58: signals travel through the network layer", 4),
        ["round", "58:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 58: signals travel through the network layer", 8),
        ["round", "58:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 58: signals travel through the network layer", 12),
        ["round 58:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 58: signals travel through the network layer", 16),
        ["round 58:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 58: signals travel through the network layer", 24),
        ["round 58: signals travel", "through the network", "layer"],
    ),
    (
        ("round 58: signals travel through the network layer", 32),
        ["round 58: signals travel through", "the network layer"],
    ),
    (
        ("round 58: the gateway routes each request by policy", 4),
        ["round", "58:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 58: the gateway routes each request by policy", 8),
        ["round", "58: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 58: the gateway routes each request by policy", 12),
        ["round 58:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 58: the gateway routes each request by policy", 16),
        ["round 58: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 58: the gateway routes each request by policy", 24),
        ["round 58: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 58: the gateway routes each request by policy", 32),
        ["round 58: the gateway routes", "each request by policy"],
    ),
    (
        ("round 58: memory grows until the buffer is full", 4),
        ["round", "58:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 58: memory grows until the buffer is full", 8),
        ["round", "58:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 58: memory grows until the buffer is full", 12),
        ["round 58:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 58: memory grows until the buffer is full", 16),
        ["round 58: memory", "grows until the", "buffer is full"],
    ),
    (("round 58: memory grows until the buffer is full", 24), ["round 58: memory grows", "until the buffer is full"]),
    (("round 58: memory grows until the buffer is full", 32), ["round 58: memory grows until the", "buffer is full"]),
    (
        ("round 58: the cluster mirrors every packet twice", 4),
        ["round", "58:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 58: the cluster mirrors every packet twice", 8),
        ["round", "58: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 58: the cluster mirrors every packet twice", 12),
        ["round 58:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 58: the cluster mirrors every packet twice", 16),
        ["round 58: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 58: the cluster mirrors every packet twice", 24),
        ["round 58: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 58: the cluster mirrors every packet twice", 32), ["round 58: the cluster mirrors", "every packet twice"]),
    (
        ("round 58: ranking uses tokens learned from the corpus", 4),
        ["round", "58:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 58: ranking uses tokens learned from the corpus", 8),
        ["round", "58:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 58: ranking uses tokens learned from the corpus", 12),
        ["round 58:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 58: ranking uses tokens learned from the corpus", 16),
        ["round 58:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 58: ranking uses tokens learned from the corpus", 24),
        ["round 58: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 58: ranking uses tokens learned from the corpus", 32),
        ["round 58: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 58: a long session ends when the candle dies", 4),
        ["round", "58:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 58: a long session ends when the candle dies", 8),
        ["round", "58: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 58: a long session ends when the candle dies", 12),
        ["round 58: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 58: a long session ends when the candle dies", 16),
        ["round 58: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 58: a long session ends when the candle dies", 24),
        ["round 58: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 58: a long session ends when the candle dies", 32),
        ["round 58: a long session ends", "when the candle dies"],
    ),
    (
        ("round 58: encode the prompt then map the result", 4),
        ["round", "58:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 58: encode the prompt then map the result", 8),
        ["round", "58:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 58: encode the prompt then map the result", 12),
        ["round 58:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 58: encode the prompt then map the result", 16),
        ["round 58: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 58: encode the prompt then map the result", 24),
        ["round 58: encode the", "prompt then map the", "result"],
    ),
    (("round 58: encode the prompt then map the result", 32), ["round 58: encode the prompt then", "map the result"]),
    (
        ("round 58: the kernel wakes the worker at dawn", 4),
        ["round", "58:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 58: the kernel wakes the worker at dawn", 8),
        ["round", "58: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 58: the kernel wakes the worker at dawn", 12),
        ["round 58:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 58: the kernel wakes the worker at dawn", 16), ["round 58: the", "kernel wakes the", "worker at dawn"]),
    (("round 58: the kernel wakes the worker at dawn", 24), ["round 58: the kernel", "wakes the worker at dawn"]),
    (("round 58: the kernel wakes the worker at dawn", 32), ["round 58: the kernel wakes the", "worker at dawn"]),
    (
        ("round 58: service latency drops after the patch", 4),
        ["round", "58:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 58: service latency drops after the patch", 8),
        ["round", "58:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 58: service latency drops after the patch", 12),
        ["round 58:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 58: service latency drops after the patch", 16),
        ["round 58:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 58: service latency drops after the patch", 24),
        ["round 58: service", "latency drops after the", "patch"],
    ),
    (("round 58: service latency drops after the patch", 32), ["round 58: service latency drops", "after the patch"]),
    (
        ("round 58: the library caches every vector it sees", 4),
        ["round", "58:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 58: the library caches every vector it sees", 8),
        ["round", "58: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 58: the library caches every vector it sees", 12),
        ["round 58:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 58: the library caches every vector it sees", 16),
        ["round 58: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 58: the library caches every vector it sees", 24),
        ["round 58: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 58: the library caches every vector it sees", 32),
        ["round 58: the library caches", "every vector it sees"],
    ),
    (
        ("round 58: agents argue then the debate resolves", 4),
        ["round", "58:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 58: agents argue then the debate resolves", 8),
        ["round", "58:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 58: agents argue then the debate resolves", 12),
        ["round 58:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 58: agents argue then the debate resolves", 16),
        ["round 58: agents", "argue then the", "debate resolves"],
    ),
    (("round 58: agents argue then the debate resolves", 24), ["round 58: agents argue", "then the debate resolves"]),
    (("round 58: agents argue then the debate resolves", 32), ["round 58: agents argue then the", "debate resolves"]),
    (
        ("round 58: the filter keeps only strong matches", 4),
        ["round", "58:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 58: the filter keeps only strong matches", 8),
        ["round", "58: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 58: the filter keeps only strong matches", 12),
        ["round 58:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 58: the filter keeps only strong matches", 16),
        ["round 58: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 58: the filter keeps only strong matches", 24), ["round 58: the filter", "keeps only strong", "matches"]),
    (("round 58: the filter keeps only strong matches", 32), ["round 58: the filter keeps only", "strong matches"]),
    (
        ("round 58: the model answers with a short reply", 4),
        ["round", "58:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 58: the model answers with a short reply", 8),
        ["round", "58: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 58: the model answers with a short reply", 12),
        ["round 58:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 58: the model answers with a short reply", 16),
        ["round 58: the", "model answers", "with a short", "reply"],
    ),
    (("round 58: the model answers with a short reply", 24), ["round 58: the model", "answers with a short", "reply"]),
    (("round 58: the model answers with a short reply", 32), ["round 58: the model answers with", "a short reply"]),
    (
        ("round 58: the recorder stores the reasoning trace", 4),
        ["round", "58:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 58: the recorder stores the reasoning trace", 8),
        ["round", "58: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 58: the recorder stores the reasoning trace", 12),
        ["round 58:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 58: the recorder stores the reasoning trace", 16),
        ["round 58: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 58: the recorder stores the reasoning trace", 24),
        ["round 58: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 58: the recorder stores the reasoning trace", 32),
        ["round 58: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 58: the angel watches the processor run", 4),
        ["round", "58:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 58: the angel watches the processor run", 8),
        ["round", "58: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 58: the angel watches the processor run", 12),
        ["round 58:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 58: the angel watches the processor run", 16), ["round 58: the", "angel watches", "the processor", "run"]),
    (("round 58: the angel watches the processor run", 24), ["round 58: the angel", "watches the processor", "run"]),
    (("round 58: the angel watches the processor run", 32), ["round 58: the angel watches the", "processor run"]),
    (
        ("round 58: angle of the vector decides the match", 4),
        ["round", "58:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 58: angle of the vector decides the match", 8),
        ["round", "58:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 58: angle of the vector decides the match", 12),
        ["round 58:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 58: angle of the vector decides the match", 16),
        ["round 58: angle", "of the vector", "decides the", "match"],
    ),
    (("round 58: angle of the vector decides the match", 24), ["round 58: angle of the", "vector decides the match"]),
    (("round 58: angle of the vector decides the match", 32), ["round 58: angle of the vector", "decides the match"]),
    (
        ("round 58: the candle burns twice as long at night", 4),
        ["round", "58:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 58: the candle burns twice as long at night", 8),
        ["round", "58: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 58: the candle burns twice as long at night", 12),
        ["round 58:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 58: the candle burns twice as long at night", 16),
        ["round 58: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 58: the candle burns twice as long at night", 24),
        ["round 58: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 58: the candle burns twice as long at night", 32),
        ["round 58: the candle burns twice", "as long at night"],
    ),
    (
        ("round 58: a mirror of the universe in one line", 4),
        ["round", "58:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 58: a mirror of the universe in one line", 8),
        ["round", "58: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 58: a mirror of the universe in one line", 12),
        ["round 58: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 58: a mirror of the universe in one line", 16),
        ["round 58: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 58: a mirror of the universe in one line", 24), ["round 58: a mirror of", "the universe in one line"]),
    (("round 58: a mirror of the universe in one line", 32), ["round 58: a mirror of the", "universe in one line"]),
    (
        ("round 58: the queue drains before the storm", 4),
        ["round", "58:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 58: the queue drains before the storm", 8),
        ["round", "58: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 58: the queue drains before the storm", 12), ["round 58:", "the queue", "drains", "before the", "storm"]),
    (("round 58: the queue drains before the storm", 16), ["round 58: the", "queue drains", "before the storm"]),
    (("round 58: the queue drains before the storm", 24), ["round 58: the queue", "drains before the storm"]),
    (("round 58: the queue drains before the storm", 32), ["round 58: the queue drains", "before the storm"]),
    (
        ("kitten58 sitting58 agent58 angle58 universe58 memory58", 6),
        ["kitten58", "sitting58", "agent58", "angle58", "universe58", "memory58"],
    ),
    (
        ("kitten58 sitting58 agent58 angle58 universe58 memory58", 10),
        ["kitten58", "sitting58", "agent58", "angle58", "universe58", "memory58"],
    ),
    (
        ("kitten58 sitting58 agent58 angle58 universe58 memory58", 18),
        ["kitten58 sitting58", "agent58 angle58", "universe58", "memory58"],
    ),
    (
        ("kitten58 sitting58 agent58 angle58 universe58 memory58", 28),
        ["kitten58 sitting58 agent58", "angle58 universe58 memory58"],
    ),
    (
        ("sitting58 agent58 angle58 universe58 memory58 stream58", 6),
        ["sitting58", "agent58", "angle58", "universe58", "memory58", "stream58"],
    ),
    (
        ("sitting58 agent58 angle58 universe58 memory58 stream58", 10),
        ["sitting58", "agent58", "angle58", "universe58", "memory58", "stream58"],
    ),
    (
        ("sitting58 agent58 angle58 universe58 memory58 stream58", 18),
        ["sitting58 agent58", "angle58 universe58", "memory58 stream58"],
    ),
    (
        ("sitting58 agent58 angle58 universe58 memory58 stream58", 28),
        ["sitting58 agent58 angle58", "universe58 memory58 stream58"],
    ),
    (
        ("agent58 angle58 universe58 memory58 stream58 context58", 6),
        ["agent58", "angle58", "universe58", "memory58", "stream58", "context58"],
    ),
    (
        ("agent58 angle58 universe58 memory58 stream58 context58", 10),
        ["agent58", "angle58", "universe58", "memory58", "stream58", "context58"],
    ),
    (
        ("agent58 angle58 universe58 memory58 stream58 context58", 18),
        ["agent58 angle58", "universe58", "memory58 stream58", "context58"],
    ),
    (
        ("agent58 angle58 universe58 memory58 stream58 context58", 28),
        ["agent58 angle58 universe58", "memory58 stream58 context58"],
    ),
    (
        ("angle58 universe58 memory58 stream58 context58 knowledge58", 6),
        ["angle58", "universe58", "memory58", "stream58", "context58", "knowledge58"],
    ),
    (
        ("angle58 universe58 memory58 stream58 context58 knowledge58", 10),
        ["angle58", "universe58", "memory58", "stream58", "context58", "knowledge58"],
    ),
    (
        ("angle58 universe58 memory58 stream58 context58 knowledge58", 18),
        ["angle58 universe58", "memory58 stream58", "context58", "knowledge58"],
    ),
    (
        ("angle58 universe58 memory58 stream58 context58 knowledge58", 28),
        ["angle58 universe58 memory58", "stream58 context58", "knowledge58"],
    ),
    (
        ("universe58 memory58 stream58 context58 knowledge58 vector58", 6),
        ["universe58", "memory58", "stream58", "context58", "knowledge58", "vector58"],
    ),
    (
        ("universe58 memory58 stream58 context58 knowledge58 vector58", 10),
        ["universe58", "memory58", "stream58", "context58", "knowledge58", "vector58"],
    ),
    (
        ("universe58 memory58 stream58 context58 knowledge58 vector58", 18),
        ["universe58", "memory58 stream58", "context58", "knowledge58", "vector58"],
    ),
    (
        ("universe58 memory58 stream58 context58 knowledge58 vector58", 28),
        ["universe58 memory58 stream58", "context58 knowledge58", "vector58"],
    ),
    (
        ("memory58 stream58 context58 knowledge58 vector58 processor58", 6),
        ["memory58", "stream58", "context58", "knowledge58", "vector58", "processor58"],
    ),
    (
        ("memory58 stream58 context58 knowledge58 vector58 processor58", 10),
        ["memory58", "stream58", "context58", "knowledge58", "vector58", "processor58"],
    ),
    (
        ("memory58 stream58 context58 knowledge58 vector58 processor58", 18),
        ["memory58 stream58", "context58", "knowledge58", "vector58", "processor58"],
    ),
    (
        ("memory58 stream58 context58 knowledge58 vector58 processor58", 28),
        ["memory58 stream58 context58", "knowledge58 vector58", "processor58"],
    ),
    (
        ("stream58 context58 knowledge58 vector58 processor58 reasoning58", 6),
        ["stream58", "context58", "knowledge58", "vector58", "processor58", "reasoning58"],
    ),
    (
        ("stream58 context58 knowledge58 vector58 processor58 reasoning58", 10),
        ["stream58", "context58", "knowledge58", "vector58", "processor58", "reasoning58"],
    ),
    (
        ("stream58 context58 knowledge58 vector58 processor58 reasoning58", 18),
        ["stream58 context58", "knowledge58", "vector58", "processor58", "reasoning58"],
    ),
    (
        ("stream58 context58 knowledge58 vector58 processor58 reasoning58", 28),
        ["stream58 context58", "knowledge58 vector58", "processor58 reasoning58"],
    ),
    (
        ("context58 knowledge58 vector58 processor58 reasoning58 machine58", 6),
        ["context58", "knowledge58", "vector58", "processor58", "reasoning58", "machine58"],
    ),
    (
        ("context58 knowledge58 vector58 processor58 reasoning58 machine58", 10),
        ["context58", "knowledge58", "vector58", "processor58", "reasoning58", "machine58"],
    ),
    (
        ("context58 knowledge58 vector58 processor58 reasoning58 machine58", 18),
        ["context58", "knowledge58", "vector58", "processor58", "reasoning58", "machine58"],
    ),
    (
        ("context58 knowledge58 vector58 processor58 reasoning58 machine58", 28),
        ["context58 knowledge58", "vector58 processor58", "reasoning58 machine58"],
    ),
    (
        ("knowledge58 vector58 processor58 reasoning58 machine58 learning58", 6),
        ["knowledge58", "vector58", "processor58", "reasoning58", "machine58", "learning58"],
    ),
    (
        ("knowledge58 vector58 processor58 reasoning58 machine58 learning58", 10),
        ["knowledge58", "vector58", "processor58", "reasoning58", "machine58", "learning58"],
    ),
    (
        ("knowledge58 vector58 processor58 reasoning58 machine58 learning58", 18),
        ["knowledge58", "vector58", "processor58", "reasoning58", "machine58", "learning58"],
    ),
    (
        ("knowledge58 vector58 processor58 reasoning58 machine58 learning58", 28),
        ["knowledge58 vector58", "processor58 reasoning58", "machine58 learning58"],
    ),
    (
        ("vector58 processor58 reasoning58 machine58 learning58 model58", 6),
        ["vector58", "processor58", "reasoning58", "machine58", "learning58", "model58"],
    ),
    (
        ("vector58 processor58 reasoning58 machine58 learning58 model58", 10),
        ["vector58", "processor58", "reasoning58", "machine58", "learning58", "model58"],
    ),
    (
        ("vector58 processor58 reasoning58 machine58 learning58 model58", 18),
        ["vector58", "processor58", "reasoning58", "machine58", "learning58 model58"],
    ),
    (
        ("vector58 processor58 reasoning58 machine58 learning58 model58", 28),
        ["vector58 processor58", "reasoning58 machine58", "learning58 model58"],
    ),
    (
        ("processor58 reasoning58 machine58 learning58 model58 token58", 6),
        ["processor58", "reasoning58", "machine58", "learning58", "model58", "token58"],
    ),
    (
        ("processor58 reasoning58 machine58 learning58 model58 token58", 10),
        ["processor58", "reasoning58", "machine58", "learning58", "model58", "token58"],
    ),
    (
        ("processor58 reasoning58 machine58 learning58 model58 token58", 18),
        ["processor58", "reasoning58", "machine58", "learning58 model58", "token58"],
    ),
    (
        ("processor58 reasoning58 machine58 learning58 model58 token58", 28),
        ["processor58 reasoning58", "machine58 learning58 model58", "token58"],
    ),
    (
        ("reasoning58 machine58 learning58 model58 token58 prompt58", 6),
        ["reasoning58", "machine58", "learning58", "model58", "token58", "prompt58"],
    ),
    (
        ("reasoning58 machine58 learning58 model58 token58 prompt58", 10),
        ["reasoning58", "machine58", "learning58", "model58", "token58", "prompt58"],
    ),
    (
        ("reasoning58 machine58 learning58 model58 token58 prompt58", 18),
        ["reasoning58", "machine58", "learning58 model58", "token58 prompt58"],
    ),
    (
        ("reasoning58 machine58 learning58 model58 token58 prompt58", 28),
        ["reasoning58 machine58", "learning58 model58 token58", "prompt58"],
    ),
    (
        ("machine58 learning58 model58 token58 prompt58 session58", 6),
        ["machine58", "learning58", "model58", "token58", "prompt58", "session58"],
    ),
    (
        ("machine58 learning58 model58 token58 prompt58 session58", 10),
        ["machine58", "learning58", "model58", "token58", "prompt58", "session58"],
    ),
    (
        ("machine58 learning58 model58 token58 prompt58 session58", 18),
        ["machine58", "learning58 model58", "token58 prompt58", "session58"],
    ),
    (
        ("machine58 learning58 model58 token58 prompt58 session58", 28),
        ["machine58 learning58 model58", "token58 prompt58 session58"],
    ),
    (
        ("learning58 model58 token58 prompt58 session58 library58", 6),
        ["learning58", "model58", "token58", "prompt58", "session58", "library58"],
    ),
    (
        ("learning58 model58 token58 prompt58 session58 library58", 10),
        ["learning58", "model58", "token58", "prompt58", "session58", "library58"],
    ),
    (
        ("learning58 model58 token58 prompt58 session58 library58", 18),
        ["learning58 model58", "token58 prompt58", "session58", "library58"],
    ),
    (
        ("learning58 model58 token58 prompt58 session58 library58", 28),
        ["learning58 model58 token58", "prompt58 session58 library58"],
    ),
    (
        ("model58 token58 prompt58 session58 library58 service58", 6),
        ["model58", "token58", "prompt58", "session58", "library58", "service58"],
    ),
    (
        ("model58 token58 prompt58 session58 library58 service58", 10),
        ["model58", "token58", "prompt58", "session58", "library58", "service58"],
    ),
    (
        ("model58 token58 prompt58 session58 library58 service58", 18),
        ["model58 token58", "prompt58 session58", "library58", "service58"],
    ),
    (
        ("model58 token58 prompt58 session58 library58 service58", 28),
        ["model58 token58 prompt58", "session58 library58", "service58"],
    ),
    (
        ("token58 prompt58 session58 library58 service58 gateway58", 6),
        ["token58", "prompt58", "session58", "library58", "service58", "gateway58"],
    ),
    (
        ("token58 prompt58 session58 library58 service58 gateway58", 10),
        ["token58", "prompt58", "session58", "library58", "service58", "gateway58"],
    ),
    (
        ("token58 prompt58 session58 library58 service58 gateway58", 18),
        ["token58 prompt58", "session58", "library58", "service58", "gateway58"],
    ),
    (
        ("token58 prompt58 session58 library58 service58 gateway58", 28),
        ["token58 prompt58 session58", "library58 service58", "gateway58"],
    ),
    (
        ("prompt58 session58 library58 service58 gateway58 storage58", 6),
        ["prompt58", "session58", "library58", "service58", "gateway58", "storage58"],
    ),
    (
        ("prompt58 session58 library58 service58 gateway58 storage58", 10),
        ["prompt58", "session58", "library58", "service58", "gateway58", "storage58"],
    ),
    (
        ("prompt58 session58 library58 service58 gateway58 storage58", 18),
        ["prompt58 session58", "library58", "service58", "gateway58", "storage58"],
    ),
    (
        ("prompt58 session58 library58 service58 gateway58 storage58", 28),
        ["prompt58 session58 library58", "service58 gateway58", "storage58"],
    ),
    (
        ("session58 library58 service58 gateway58 storage58 network58", 6),
        ["session58", "library58", "service58", "gateway58", "storage58", "network58"],
    ),
    (
        ("session58 library58 service58 gateway58 storage58 network58", 10),
        ["session58", "library58", "service58", "gateway58", "storage58", "network58"],
    ),
    (
        ("session58 library58 service58 gateway58 storage58 network58", 18),
        ["session58", "library58", "service58", "gateway58", "storage58", "network58"],
    ),
    (
        ("session58 library58 service58 gateway58 storage58 network58", 28),
        ["session58 library58", "service58 gateway58", "storage58 network58"],
    ),
    (
        ("library58 service58 gateway58 storage58 network58 latency58", 6),
        ["library58", "service58", "gateway58", "storage58", "network58", "latency58"],
    ),
    (
        ("library58 service58 gateway58 storage58 network58 latency58", 10),
        ["library58", "service58", "gateway58", "storage58", "network58", "latency58"],
    ),
    (
        ("library58 service58 gateway58 storage58 network58 latency58", 18),
        ["library58", "service58", "gateway58", "storage58", "network58", "latency58"],
    ),
    (
        ("library58 service58 gateway58 storage58 network58 latency58", 28),
        ["library58 service58", "gateway58 storage58", "network58 latency58"],
    ),
    (
        ("service58 gateway58 storage58 network58 latency58 buffer58", 6),
        ["service58", "gateway58", "storage58", "network58", "latency58", "buffer58"],
    ),
    (
        ("service58 gateway58 storage58 network58 latency58 buffer58", 10),
        ["service58", "gateway58", "storage58", "network58", "latency58", "buffer58"],
    ),
    (
        ("service58 gateway58 storage58 network58 latency58 buffer58", 18),
        ["service58", "gateway58", "storage58", "network58", "latency58 buffer58"],
    ),
    (
        ("service58 gateway58 storage58 network58 latency58 buffer58", 28),
        ["service58 gateway58", "storage58 network58", "latency58 buffer58"],
    ),
    (
        ("gateway58 storage58 network58 latency58 buffer58 queue58", 6),
        ["gateway58", "storage58", "network58", "latency58", "buffer58", "queue58"],
    ),
    (
        ("gateway58 storage58 network58 latency58 buffer58 queue58", 10),
        ["gateway58", "storage58", "network58", "latency58", "buffer58", "queue58"],
    ),
    (
        ("gateway58 storage58 network58 latency58 buffer58 queue58", 18),
        ["gateway58", "storage58", "network58", "latency58 buffer58", "queue58"],
    ),
    (
        ("gateway58 storage58 network58 latency58 buffer58 queue58", 28),
        ["gateway58 storage58", "network58 latency58 buffer58", "queue58"],
    ),
    (
        ("storage58 network58 latency58 buffer58 queue58 worker58", 6),
        ["storage58", "network58", "latency58", "buffer58", "queue58", "worker58"],
    ),
    (
        ("storage58 network58 latency58 buffer58 queue58 worker58", 10),
        ["storage58", "network58", "latency58", "buffer58", "queue58", "worker58"],
    ),
    (
        ("storage58 network58 latency58 buffer58 queue58 worker58", 18),
        ["storage58", "network58", "latency58 buffer58", "queue58 worker58"],
    ),
    (
        ("storage58 network58 latency58 buffer58 queue58 worker58", 28),
        ["storage58 network58", "latency58 buffer58 queue58", "worker58"],
    ),
    (
        ("network58 latency58 buffer58 queue58 worker58 kernel58", 6),
        ["network58", "latency58", "buffer58", "queue58", "worker58", "kernel58"],
    ),
    (
        ("network58 latency58 buffer58 queue58 worker58 kernel58", 10),
        ["network58", "latency58", "buffer58", "queue58", "worker58", "kernel58"],
    ),
    (
        ("network58 latency58 buffer58 queue58 worker58 kernel58", 18),
        ["network58", "latency58 buffer58", "queue58 worker58", "kernel58"],
    ),
    (
        ("network58 latency58 buffer58 queue58 worker58 kernel58", 28),
        ["network58 latency58 buffer58", "queue58 worker58 kernel58"],
    ),
    (
        ("latency58 buffer58 queue58 worker58 kernel58 signal58", 6),
        ["latency58", "buffer58", "queue58", "worker58", "kernel58", "signal58"],
    ),
    (
        ("latency58 buffer58 queue58 worker58 kernel58 signal58", 10),
        ["latency58", "buffer58", "queue58", "worker58", "kernel58", "signal58"],
    ),
    (
        ("latency58 buffer58 queue58 worker58 kernel58 signal58", 18),
        ["latency58 buffer58", "queue58 worker58", "kernel58 signal58"],
    ),
    (
        ("latency58 buffer58 queue58 worker58 kernel58 signal58", 28),
        ["latency58 buffer58 queue58", "worker58 kernel58 signal58"],
    ),
    (
        ("buffer58 queue58 worker58 kernel58 signal58 packet58", 6),
        ["buffer58", "queue58", "worker58", "kernel58", "signal58", "packet58"],
    ),
    (
        ("buffer58 queue58 worker58 kernel58 signal58 packet58", 10),
        ["buffer58", "queue58", "worker58", "kernel58", "signal58", "packet58"],
    ),
    (
        ("buffer58 queue58 worker58 kernel58 signal58 packet58", 18),
        ["buffer58 queue58", "worker58 kernel58", "signal58 packet58"],
    ),
    (
        ("buffer58 queue58 worker58 kernel58 signal58 packet58", 28),
        ["buffer58 queue58 worker58", "kernel58 signal58 packet58"],
    ),
    (
        ("queue58 worker58 kernel58 signal58 packet58 router58", 6),
        ["queue58", "worker58", "kernel58", "signal58", "packet58", "router58"],
    ),
    (
        ("queue58 worker58 kernel58 signal58 packet58 router58", 10),
        ["queue58", "worker58", "kernel58", "signal58", "packet58", "router58"],
    ),
    (
        ("queue58 worker58 kernel58 signal58 packet58 router58", 18),
        ["queue58 worker58", "kernel58 signal58", "packet58 router58"],
    ),
    (
        ("queue58 worker58 kernel58 signal58 packet58 router58", 28),
        ["queue58 worker58 kernel58", "signal58 packet58 router58"],
    ),
    (
        ("worker58 kernel58 signal58 packet58 router58 cluster58", 6),
        ["worker58", "kernel58", "signal58", "packet58", "router58", "cluster58"],
    ),
    (
        ("worker58 kernel58 signal58 packet58 router58 cluster58", 10),
        ["worker58", "kernel58", "signal58", "packet58", "router58", "cluster58"],
    ),
    (
        ("worker58 kernel58 signal58 packet58 router58 cluster58", 18),
        ["worker58 kernel58", "signal58 packet58", "router58 cluster58"],
    ),
    (
        ("worker58 kernel58 signal58 packet58 router58 cluster58", 28),
        ["worker58 kernel58 signal58", "packet58 router58 cluster58"],
    ),
    (
        ("kernel58 signal58 packet58 router58 cluster58 mirror58", 6),
        ["kernel58", "signal58", "packet58", "router58", "cluster58", "mirror58"],
    ),
    (
        ("kernel58 signal58 packet58 router58 cluster58 mirror58", 10),
        ["kernel58", "signal58", "packet58", "router58", "cluster58", "mirror58"],
    ),
    (
        ("kernel58 signal58 packet58 router58 cluster58 mirror58", 18),
        ["kernel58 signal58", "packet58 router58", "cluster58 mirror58"],
    ),
    (
        ("kernel58 signal58 packet58 router58 cluster58 mirror58", 28),
        ["kernel58 signal58 packet58", "router58 cluster58 mirror58"],
    ),
    (
        ("signal58 packet58 router58 cluster58 mirror58 filter58", 6),
        ["signal58", "packet58", "router58", "cluster58", "mirror58", "filter58"],
    ),
    (
        ("signal58 packet58 router58 cluster58 mirror58 filter58", 10),
        ["signal58", "packet58", "router58", "cluster58", "mirror58", "filter58"],
    ),
    (
        ("signal58 packet58 router58 cluster58 mirror58 filter58", 18),
        ["signal58 packet58", "router58 cluster58", "mirror58 filter58"],
    ),
    (
        ("signal58 packet58 router58 cluster58 mirror58 filter58", 28),
        ["signal58 packet58 router58", "cluster58 mirror58 filter58"],
    ),
    (
        ("packet58 router58 cluster58 mirror58 filter58 ranking58", 6),
        ["packet58", "router58", "cluster58", "mirror58", "filter58", "ranking58"],
    ),
    (
        ("packet58 router58 cluster58 mirror58 filter58 ranking58", 10),
        ["packet58", "router58", "cluster58", "mirror58", "filter58", "ranking58"],
    ),
    (
        ("packet58 router58 cluster58 mirror58 filter58 ranking58", 18),
        ["packet58 router58", "cluster58 mirror58", "filter58 ranking58"],
    ),
    (
        ("packet58 router58 cluster58 mirror58 filter58 ranking58", 28),
        ["packet58 router58 cluster58", "mirror58 filter58 ranking58"],
    ),
    (
        ("router58 cluster58 mirror58 filter58 ranking58 encoding58", 6),
        ["router58", "cluster58", "mirror58", "filter58", "ranking58", "encoding58"],
    ),
    (
        ("router58 cluster58 mirror58 filter58 ranking58 encoding58", 10),
        ["router58", "cluster58", "mirror58", "filter58", "ranking58", "encoding58"],
    ),
    (
        ("router58 cluster58 mirror58 filter58 ranking58 encoding58", 18),
        ["router58 cluster58", "mirror58 filter58", "ranking58", "encoding58"],
    ),
    (
        ("router58 cluster58 mirror58 filter58 ranking58 encoding58", 28),
        ["router58 cluster58 mirror58", "filter58 ranking58", "encoding58"],
    ),
    (
        ("cluster58 mirror58 filter58 ranking58 encoding58 mapping58", 6),
        ["cluster58", "mirror58", "filter58", "ranking58", "encoding58", "mapping58"],
    ),
    (
        ("cluster58 mirror58 filter58 ranking58 encoding58 mapping58", 10),
        ["cluster58", "mirror58", "filter58", "ranking58", "encoding58", "mapping58"],
    ),
    (
        ("cluster58 mirror58 filter58 ranking58 encoding58 mapping58", 18),
        ["cluster58 mirror58", "filter58 ranking58", "encoding58", "mapping58"],
    ),
    (
        ("cluster58 mirror58 filter58 ranking58 encoding58 mapping58", 28),
        ["cluster58 mirror58 filter58", "ranking58 encoding58", "mapping58"],
    ),
    (
        ("mirror58 filter58 ranking58 encoding58 mapping58 record58", 6),
        ["mirror58", "filter58", "ranking58", "encoding58", "mapping58", "record58"],
    ),
    (
        ("mirror58 filter58 ranking58 encoding58 mapping58 record58", 10),
        ["mirror58", "filter58", "ranking58", "encoding58", "mapping58", "record58"],
    ),
    (
        ("mirror58 filter58 ranking58 encoding58 mapping58 record58", 18),
        ["mirror58 filter58", "ranking58", "encoding58", "mapping58 record58"],
    ),
    (
        ("mirror58 filter58 ranking58 encoding58 mapping58 record58", 28),
        ["mirror58 filter58 ranking58", "encoding58 mapping58", "record58"],
    ),
    (
        ("filter58 ranking58 encoding58 mapping58 record58 candle58", 6),
        ["filter58", "ranking58", "encoding58", "mapping58", "record58", "candle58"],
    ),
    (
        ("filter58 ranking58 encoding58 mapping58 record58 candle58", 10),
        ["filter58", "ranking58", "encoding58", "mapping58", "record58", "candle58"],
    ),
    (
        ("filter58 ranking58 encoding58 mapping58 record58 candle58", 18),
        ["filter58 ranking58", "encoding58", "mapping58 record58", "candle58"],
    ),
    (
        ("filter58 ranking58 encoding58 mapping58 record58 candle58", 28),
        ["filter58 ranking58", "encoding58 mapping58", "record58 candle58"],
    ),
    (
        ("ranking58 encoding58 mapping58 record58 candle58 thread58", 6),
        ["ranking58", "encoding58", "mapping58", "record58", "candle58", "thread58"],
    ),
    (
        ("ranking58 encoding58 mapping58 record58 candle58 thread58", 10),
        ["ranking58", "encoding58", "mapping58", "record58", "candle58", "thread58"],
    ),
    (
        ("ranking58 encoding58 mapping58 record58 candle58 thread58", 18),
        ["ranking58", "encoding58", "mapping58 record58", "candle58 thread58"],
    ),
    (
        ("ranking58 encoding58 mapping58 record58 candle58 thread58", 28),
        ["ranking58 encoding58", "mapping58 record58 candle58", "thread58"],
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
