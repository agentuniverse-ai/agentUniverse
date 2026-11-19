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
        ("round 148: the quick brown fox jumps over the lazy dog", 4),
        ["round", "148:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", 8),
        ["round", "148: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", 12),
        ["round 148:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", 16),
        ["round 148: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", 24),
        ["round 148: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 148: the quick brown fox jumps over the lazy dog", 32),
        ["round 148: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", 4),
        ["round", "148:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", 8),
        ["round", "148:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", 12),
        ["round 148:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", 16),
        ["round 148:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", 24),
        ["round 148: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 148: agentuniverse is a framework for multi agents", 32),
        ["round 148: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", 4),
        ["round", "148:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", 8),
        ["round", "148:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", 12),
        ["round 148:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", 16),
        ["round 148:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", 24),
        ["round 148: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 148: knowledge stored as vectors enables retrieval", 32),
        ["round 148: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 148: the processor reads the record then stops", 4),
        ["round", "148:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 148: the processor reads the record then stops", 8),
        ["round", "148: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 148: the processor reads the record then stops", 12),
        ["round 148:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 148: the processor reads the record then stops", 16),
        ["round 148: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 148: the processor reads the record then stops", 24),
        ["round 148: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 148: the processor reads the record then stops", 32),
        ["round 148: the processor reads", "the record then stops"],
    ),
    (
        ("round 148: a worker pulls the next task from the queue", 4),
        ["round", "148:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 148: a worker pulls the next task from the queue", 8),
        ["round", "148: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 148: a worker pulls the next task from the queue", 12),
        ["round 148: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 148: a worker pulls the next task from the queue", 16),
        ["round 148: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 148: a worker pulls the next task from the queue", 24),
        ["round 148: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 148: a worker pulls the next task from the queue", 32),
        ["round 148: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 148: signals travel through the network layer", 4),
        ["round", "148:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 148: signals travel through the network layer", 8),
        ["round", "148:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 148: signals travel through the network layer", 12),
        ["round 148:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 148: signals travel through the network layer", 16),
        ["round 148:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 148: signals travel through the network layer", 24),
        ["round 148: signals", "travel through the", "network layer"],
    ),
    (
        ("round 148: signals travel through the network layer", 32),
        ["round 148: signals travel", "through the network layer"],
    ),
    (
        ("round 148: the gateway routes each request by policy", 4),
        ["round", "148:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 148: the gateway routes each request by policy", 8),
        ["round", "148: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 148: the gateway routes each request by policy", 12),
        ["round 148:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 148: the gateway routes each request by policy", 16),
        ["round 148: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 148: the gateway routes each request by policy", 24),
        ["round 148: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 148: the gateway routes each request by policy", 32),
        ["round 148: the gateway routes", "each request by policy"],
    ),
    (
        ("round 148: memory grows until the buffer is full", 4),
        ["round", "148:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 148: memory grows until the buffer is full", 8),
        ["round", "148:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 148: memory grows until the buffer is full", 12),
        ["round 148:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 148: memory grows until the buffer is full", 16),
        ["round 148:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 148: memory grows until the buffer is full", 24), ["round 148: memory grows", "until the buffer is full"]),
    (("round 148: memory grows until the buffer is full", 32), ["round 148: memory grows until", "the buffer is full"]),
    (
        ("round 148: the cluster mirrors every packet twice", 4),
        ["round", "148:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 148: the cluster mirrors every packet twice", 8),
        ["round", "148: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 148: the cluster mirrors every packet twice", 12),
        ["round 148:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 148: the cluster mirrors every packet twice", 16),
        ["round 148: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 148: the cluster mirrors every packet twice", 24),
        ["round 148: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 148: the cluster mirrors every packet twice", 32),
        ["round 148: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", 4),
        ["round", "148:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", 8),
        ["round", "148:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", 12),
        ["round 148:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", 16),
        ["round 148:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", 24),
        ["round 148: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 148: ranking uses tokens learned from the corpus", 32),
        ["round 148: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 148: a long session ends when the candle dies", 4),
        ["round", "148:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 148: a long session ends when the candle dies", 8),
        ["round", "148: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 148: a long session ends when the candle dies", 12),
        ["round 148: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 148: a long session ends when the candle dies", 16),
        ["round 148: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 148: a long session ends when the candle dies", 24),
        ["round 148: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 148: a long session ends when the candle dies", 32),
        ["round 148: a long session ends", "when the candle dies"],
    ),
    (
        ("round 148: encode the prompt then map the result", 4),
        ["round", "148:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 148: encode the prompt then map the result", 8),
        ["round", "148:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 148: encode the prompt then map the result", 12),
        ["round 148:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 148: encode the prompt then map the result", 16),
        ["round 148:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 148: encode the prompt then map the result", 24),
        ["round 148: encode the", "prompt then map the", "result"],
    ),
    (("round 148: encode the prompt then map the result", 32), ["round 148: encode the prompt", "then map the result"]),
    (
        ("round 148: the kernel wakes the worker at dawn", 4),
        ["round", "148:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 148: the kernel wakes the worker at dawn", 8),
        ["round", "148: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 148: the kernel wakes the worker at dawn", 12),
        ["round 148:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 148: the kernel wakes the worker at dawn", 16), ["round 148: the", "kernel wakes the", "worker at dawn"]),
    (("round 148: the kernel wakes the worker at dawn", 24), ["round 148: the kernel", "wakes the worker at dawn"]),
    (("round 148: the kernel wakes the worker at dawn", 32), ["round 148: the kernel wakes the", "worker at dawn"]),
    (
        ("round 148: service latency drops after the patch", 4),
        ["round", "148:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 148: service latency drops after the patch", 8),
        ["round", "148:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 148: service latency drops after the patch", 12),
        ["round 148:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 148: service latency drops after the patch", 16),
        ["round 148:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 148: service latency drops after the patch", 24),
        ["round 148: service", "latency drops after the", "patch"],
    ),
    (("round 148: service latency drops after the patch", 32), ["round 148: service latency drops", "after the patch"]),
    (
        ("round 148: the library caches every vector it sees", 4),
        ["round", "148:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 148: the library caches every vector it sees", 8),
        ["round", "148: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 148: the library caches every vector it sees", 12),
        ["round 148:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 148: the library caches every vector it sees", 16),
        ["round 148: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 148: the library caches every vector it sees", 24),
        ["round 148: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 148: the library caches every vector it sees", 32),
        ["round 148: the library caches", "every vector it sees"],
    ),
    (
        ("round 148: agents argue then the debate resolves", 4),
        ["round", "148:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 148: agents argue then the debate resolves", 8),
        ["round", "148:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 148: agents argue then the debate resolves", 12),
        ["round 148:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 148: agents argue then the debate resolves", 16),
        ["round 148:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 148: agents argue then the debate resolves", 24), ["round 148: agents argue", "then the debate resolves"]),
    (("round 148: agents argue then the debate resolves", 32), ["round 148: agents argue then the", "debate resolves"]),
    (
        ("round 148: the filter keeps only strong matches", 4),
        ["round", "148:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 148: the filter keeps only strong matches", 8),
        ["round", "148: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 148: the filter keeps only strong matches", 12),
        ["round 148:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 148: the filter keeps only strong matches", 16),
        ["round 148: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 148: the filter keeps only strong matches", 24),
        ["round 148: the filter", "keeps only strong", "matches"],
    ),
    (("round 148: the filter keeps only strong matches", 32), ["round 148: the filter keeps only", "strong matches"]),
    (
        ("round 148: the model answers with a short reply", 4),
        ["round", "148:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 148: the model answers with a short reply", 8),
        ["round", "148: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 148: the model answers with a short reply", 12),
        ["round 148:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 148: the model answers with a short reply", 16),
        ["round 148: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 148: the model answers with a short reply", 24),
        ["round 148: the model", "answers with a short", "reply"],
    ),
    (("round 148: the model answers with a short reply", 32), ["round 148: the model answers", "with a short reply"]),
    (
        ("round 148: the recorder stores the reasoning trace", 4),
        ["round", "148:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 148: the recorder stores the reasoning trace", 8),
        ["round", "148: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 148: the recorder stores the reasoning trace", 12),
        ["round 148:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 148: the recorder stores the reasoning trace", 16),
        ["round 148: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 148: the recorder stores the reasoning trace", 24),
        ["round 148: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 148: the recorder stores the reasoning trace", 32),
        ["round 148: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 148: the angel watches the processor run", 4),
        ["round", "148:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 148: the angel watches the processor run", 8),
        ["round", "148: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 148: the angel watches the processor run", 12),
        ["round 148:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 148: the angel watches the processor run", 16),
        ["round 148: the", "angel watches", "the processor", "run"],
    ),
    (("round 148: the angel watches the processor run", 24), ["round 148: the angel", "watches the processor", "run"]),
    (("round 148: the angel watches the processor run", 32), ["round 148: the angel watches the", "processor run"]),
    (
        ("round 148: angle of the vector decides the match", 4),
        ["round", "148:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 148: angle of the vector decides the match", 8),
        ["round", "148:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 148: angle of the vector decides the match", 12),
        ["round 148:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 148: angle of the vector decides the match", 16),
        ["round 148: angle", "of the vector", "decides the", "match"],
    ),
    (("round 148: angle of the vector decides the match", 24), ["round 148: angle of the", "vector decides the match"]),
    (("round 148: angle of the vector decides the match", 32), ["round 148: angle of the vector", "decides the match"]),
    (
        ("round 148: the candle burns twice as long at night", 4),
        ["round", "148:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 148: the candle burns twice as long at night", 8),
        ["round", "148: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 148: the candle burns twice as long at night", 12),
        ["round 148:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 148: the candle burns twice as long at night", 16),
        ["round 148: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 148: the candle burns twice as long at night", 24),
        ["round 148: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 148: the candle burns twice as long at night", 32),
        ["round 148: the candle burns", "twice as long at night"],
    ),
    (
        ("round 148: a mirror of the universe in one line", 4),
        ["round", "148:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 148: a mirror of the universe in one line", 8),
        ["round", "148: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 148: a mirror of the universe in one line", 12),
        ["round 148: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 148: a mirror of the universe in one line", 16),
        ["round 148: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 148: a mirror of the universe in one line", 24), ["round 148: a mirror of", "the universe in one line"]),
    (("round 148: a mirror of the universe in one line", 32), ["round 148: a mirror of the", "universe in one line"]),
    (
        ("round 148: the queue drains before the storm", 4),
        ["round", "148:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 148: the queue drains before the storm", 8),
        ["round", "148: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 148: the queue drains before the storm", 12),
        ["round 148:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 148: the queue drains before the storm", 16), ["round 148: the", "queue drains", "before the storm"]),
    (("round 148: the queue drains before the storm", 24), ["round 148: the queue", "drains before the storm"]),
    (("round 148: the queue drains before the storm", 32), ["round 148: the queue drains", "before the storm"]),
    (
        ("kitten148 sitting148 agent148 angle148 universe148 memory148", 6),
        ["kitten148", "sitting148", "agent148", "angle148", "universe148", "memory148"],
    ),
    (
        ("kitten148 sitting148 agent148 angle148 universe148 memory148", 10),
        ["kitten148", "sitting148", "agent148", "angle148", "universe148", "memory148"],
    ),
    (
        ("kitten148 sitting148 agent148 angle148 universe148 memory148", 18),
        ["kitten148", "sitting148", "agent148 angle148", "universe148", "memory148"],
    ),
    (
        ("kitten148 sitting148 agent148 angle148 universe148 memory148", 28),
        ["kitten148 sitting148", "agent148 angle148", "universe148 memory148"],
    ),
    (
        ("sitting148 agent148 angle148 universe148 memory148 stream148", 6),
        ["sitting148", "agent148", "angle148", "universe148", "memory148", "stream148"],
    ),
    (
        ("sitting148 agent148 angle148 universe148 memory148 stream148", 10),
        ["sitting148", "agent148", "angle148", "universe148", "memory148", "stream148"],
    ),
    (
        ("sitting148 agent148 angle148 universe148 memory148 stream148", 18),
        ["sitting148", "agent148 angle148", "universe148", "memory148", "stream148"],
    ),
    (
        ("sitting148 agent148 angle148 universe148 memory148 stream148", 28),
        ["sitting148 agent148 angle148", "universe148 memory148", "stream148"],
    ),
    (
        ("agent148 angle148 universe148 memory148 stream148 context148", 6),
        ["agent148", "angle148", "universe148", "memory148", "stream148", "context148"],
    ),
    (
        ("agent148 angle148 universe148 memory148 stream148 context148", 10),
        ["agent148", "angle148", "universe148", "memory148", "stream148", "context148"],
    ),
    (
        ("agent148 angle148 universe148 memory148 stream148 context148", 18),
        ["agent148 angle148", "universe148", "memory148", "stream148", "context148"],
    ),
    (
        ("agent148 angle148 universe148 memory148 stream148 context148", 28),
        ["agent148 angle148", "universe148 memory148", "stream148 context148"],
    ),
    (
        ("angle148 universe148 memory148 stream148 context148 knowledge148", 6),
        ["angle148", "universe148", "memory148", "stream148", "context148", "knowledge148"],
    ),
    (
        ("angle148 universe148 memory148 stream148 context148 knowledge148", 10),
        ["angle148", "universe148", "memory148", "stream148", "context148", "knowledge148"],
    ),
    (
        ("angle148 universe148 memory148 stream148 context148 knowledge148", 18),
        ["angle148", "universe148", "memory148", "stream148", "context148", "knowledge148"],
    ),
    (
        ("angle148 universe148 memory148 stream148 context148 knowledge148", 28),
        ["angle148 universe148", "memory148 stream148", "context148 knowledge148"],
    ),
    (
        ("universe148 memory148 stream148 context148 knowledge148 vector148", 6),
        ["universe148", "memory148", "stream148", "context148", "knowledge148", "vector148"],
    ),
    (
        ("universe148 memory148 stream148 context148 knowledge148 vector148", 10),
        ["universe148", "memory148", "stream148", "context148", "knowledge148", "vector148"],
    ),
    (
        ("universe148 memory148 stream148 context148 knowledge148 vector148", 18),
        ["universe148", "memory148", "stream148", "context148", "knowledge148", "vector148"],
    ),
    (
        ("universe148 memory148 stream148 context148 knowledge148 vector148", 28),
        ["universe148 memory148", "stream148 context148", "knowledge148 vector148"],
    ),
    (
        ("memory148 stream148 context148 knowledge148 vector148 processor148", 6),
        ["memory148", "stream148", "context148", "knowledge148", "vector148", "processor148"],
    ),
    (
        ("memory148 stream148 context148 knowledge148 vector148 processor148", 10),
        ["memory148", "stream148", "context148", "knowledge148", "vector148", "processor148"],
    ),
    (
        ("memory148 stream148 context148 knowledge148 vector148 processor148", 18),
        ["memory148", "stream148", "context148", "knowledge148", "vector148", "processor148"],
    ),
    (
        ("memory148 stream148 context148 knowledge148 vector148 processor148", 28),
        ["memory148 stream148", "context148 knowledge148", "vector148 processor148"],
    ),
    (
        ("stream148 context148 knowledge148 vector148 processor148 reasoning148", 6),
        ["stream148", "context148", "knowledge148", "vector148", "processor148", "reasoning148"],
    ),
    (
        ("stream148 context148 knowledge148 vector148 processor148 reasoning148", 10),
        ["stream148", "context148", "knowledge148", "vector148", "processor148", "reasoning148"],
    ),
    (
        ("stream148 context148 knowledge148 vector148 processor148 reasoning148", 18),
        ["stream148", "context148", "knowledge148", "vector148", "processor148", "reasoning148"],
    ),
    (
        ("stream148 context148 knowledge148 vector148 processor148 reasoning148", 28),
        ["stream148 context148", "knowledge148 vector148", "processor148 reasoning148"],
    ),
    (
        ("context148 knowledge148 vector148 processor148 reasoning148 machine148", 6),
        ["context148", "knowledge148", "vector148", "processor148", "reasoning148", "machine148"],
    ),
    (
        ("context148 knowledge148 vector148 processor148 reasoning148 machine148", 10),
        ["context148", "knowledge148", "vector148", "processor148", "reasoning148", "machine148"],
    ),
    (
        ("context148 knowledge148 vector148 processor148 reasoning148 machine148", 18),
        ["context148", "knowledge148", "vector148", "processor148", "reasoning148", "machine148"],
    ),
    (
        ("context148 knowledge148 vector148 processor148 reasoning148 machine148", 28),
        ["context148 knowledge148", "vector148 processor148", "reasoning148 machine148"],
    ),
    (
        ("knowledge148 vector148 processor148 reasoning148 machine148 learning148", 6),
        ["knowledge148", "vector148", "processor148", "reasoning148", "machine148", "learning148"],
    ),
    (
        ("knowledge148 vector148 processor148 reasoning148 machine148 learning148", 10),
        ["knowledge148", "vector148", "processor148", "reasoning148", "machine148", "learning148"],
    ),
    (
        ("knowledge148 vector148 processor148 reasoning148 machine148 learning148", 18),
        ["knowledge148", "vector148", "processor148", "reasoning148", "machine148", "learning148"],
    ),
    (
        ("knowledge148 vector148 processor148 reasoning148 machine148 learning148", 28),
        ["knowledge148 vector148", "processor148 reasoning148", "machine148 learning148"],
    ),
    (
        ("vector148 processor148 reasoning148 machine148 learning148 model148", 6),
        ["vector148", "processor148", "reasoning148", "machine148", "learning148", "model148"],
    ),
    (
        ("vector148 processor148 reasoning148 machine148 learning148 model148", 10),
        ["vector148", "processor148", "reasoning148", "machine148", "learning148", "model148"],
    ),
    (
        ("vector148 processor148 reasoning148 machine148 learning148 model148", 18),
        ["vector148", "processor148", "reasoning148", "machine148", "learning148", "model148"],
    ),
    (
        ("vector148 processor148 reasoning148 machine148 learning148 model148", 28),
        ["vector148 processor148", "reasoning148 machine148", "learning148 model148"],
    ),
    (
        ("processor148 reasoning148 machine148 learning148 model148 token148", 6),
        ["processor148", "reasoning148", "machine148", "learning148", "model148", "token148"],
    ),
    (
        ("processor148 reasoning148 machine148 learning148 model148 token148", 10),
        ["processor148", "reasoning148", "machine148", "learning148", "model148", "token148"],
    ),
    (
        ("processor148 reasoning148 machine148 learning148 model148 token148", 18),
        ["processor148", "reasoning148", "machine148", "learning148", "model148 token148"],
    ),
    (
        ("processor148 reasoning148 machine148 learning148 model148 token148", 28),
        ["processor148 reasoning148", "machine148 learning148", "model148 token148"],
    ),
    (
        ("reasoning148 machine148 learning148 model148 token148 prompt148", 6),
        ["reasoning148", "machine148", "learning148", "model148", "token148", "prompt148"],
    ),
    (
        ("reasoning148 machine148 learning148 model148 token148 prompt148", 10),
        ["reasoning148", "machine148", "learning148", "model148", "token148", "prompt148"],
    ),
    (
        ("reasoning148 machine148 learning148 model148 token148 prompt148", 18),
        ["reasoning148", "machine148", "learning148", "model148 token148", "prompt148"],
    ),
    (
        ("reasoning148 machine148 learning148 model148 token148 prompt148", 28),
        ["reasoning148 machine148", "learning148 model148", "token148 prompt148"],
    ),
    (
        ("machine148 learning148 model148 token148 prompt148 session148", 6),
        ["machine148", "learning148", "model148", "token148", "prompt148", "session148"],
    ),
    (
        ("machine148 learning148 model148 token148 prompt148 session148", 10),
        ["machine148", "learning148", "model148", "token148", "prompt148", "session148"],
    ),
    (
        ("machine148 learning148 model148 token148 prompt148 session148", 18),
        ["machine148", "learning148", "model148 token148", "prompt148", "session148"],
    ),
    (
        ("machine148 learning148 model148 token148 prompt148 session148", 28),
        ["machine148 learning148", "model148 token148 prompt148", "session148"],
    ),
    (
        ("learning148 model148 token148 prompt148 session148 library148", 6),
        ["learning148", "model148", "token148", "prompt148", "session148", "library148"],
    ),
    (
        ("learning148 model148 token148 prompt148 session148 library148", 10),
        ["learning148", "model148", "token148", "prompt148", "session148", "library148"],
    ),
    (
        ("learning148 model148 token148 prompt148 session148 library148", 18),
        ["learning148", "model148 token148", "prompt148", "session148", "library148"],
    ),
    (
        ("learning148 model148 token148 prompt148 session148 library148", 28),
        ["learning148 model148", "token148 prompt148", "session148 library148"],
    ),
    (
        ("model148 token148 prompt148 session148 library148 service148", 6),
        ["model148", "token148", "prompt148", "session148", "library148", "service148"],
    ),
    (
        ("model148 token148 prompt148 session148 library148 service148", 10),
        ["model148", "token148", "prompt148", "session148", "library148", "service148"],
    ),
    (
        ("model148 token148 prompt148 session148 library148 service148", 18),
        ["model148 token148", "prompt148", "session148", "library148", "service148"],
    ),
    (
        ("model148 token148 prompt148 session148 library148 service148", 28),
        ["model148 token148 prompt148", "session148 library148", "service148"],
    ),
    (
        ("token148 prompt148 session148 library148 service148 gateway148", 6),
        ["token148", "prompt148", "session148", "library148", "service148", "gateway148"],
    ),
    (
        ("token148 prompt148 session148 library148 service148 gateway148", 10),
        ["token148", "prompt148", "session148", "library148", "service148", "gateway148"],
    ),
    (
        ("token148 prompt148 session148 library148 service148 gateway148", 18),
        ["token148 prompt148", "session148", "library148", "service148", "gateway148"],
    ),
    (
        ("token148 prompt148 session148 library148 service148 gateway148", 28),
        ["token148 prompt148", "session148 library148", "service148 gateway148"],
    ),
    (
        ("prompt148 session148 library148 service148 gateway148 storage148", 6),
        ["prompt148", "session148", "library148", "service148", "gateway148", "storage148"],
    ),
    (
        ("prompt148 session148 library148 service148 gateway148 storage148", 10),
        ["prompt148", "session148", "library148", "service148", "gateway148", "storage148"],
    ),
    (
        ("prompt148 session148 library148 service148 gateway148 storage148", 18),
        ["prompt148", "session148", "library148", "service148", "gateway148", "storage148"],
    ),
    (
        ("prompt148 session148 library148 service148 gateway148 storage148", 28),
        ["prompt148 session148", "library148 service148", "gateway148 storage148"],
    ),
    (
        ("session148 library148 service148 gateway148 storage148 network148", 6),
        ["session148", "library148", "service148", "gateway148", "storage148", "network148"],
    ),
    (
        ("session148 library148 service148 gateway148 storage148 network148", 10),
        ["session148", "library148", "service148", "gateway148", "storage148", "network148"],
    ),
    (
        ("session148 library148 service148 gateway148 storage148 network148", 18),
        ["session148", "library148", "service148", "gateway148", "storage148", "network148"],
    ),
    (
        ("session148 library148 service148 gateway148 storage148 network148", 28),
        ["session148 library148", "service148 gateway148", "storage148 network148"],
    ),
    (
        ("library148 service148 gateway148 storage148 network148 latency148", 6),
        ["library148", "service148", "gateway148", "storage148", "network148", "latency148"],
    ),
    (
        ("library148 service148 gateway148 storage148 network148 latency148", 10),
        ["library148", "service148", "gateway148", "storage148", "network148", "latency148"],
    ),
    (
        ("library148 service148 gateway148 storage148 network148 latency148", 18),
        ["library148", "service148", "gateway148", "storage148", "network148", "latency148"],
    ),
    (
        ("library148 service148 gateway148 storage148 network148 latency148", 28),
        ["library148 service148", "gateway148 storage148", "network148 latency148"],
    ),
    (
        ("service148 gateway148 storage148 network148 latency148 buffer148", 6),
        ["service148", "gateway148", "storage148", "network148", "latency148", "buffer148"],
    ),
    (
        ("service148 gateway148 storage148 network148 latency148 buffer148", 10),
        ["service148", "gateway148", "storage148", "network148", "latency148", "buffer148"],
    ),
    (
        ("service148 gateway148 storage148 network148 latency148 buffer148", 18),
        ["service148", "gateway148", "storage148", "network148", "latency148", "buffer148"],
    ),
    (
        ("service148 gateway148 storage148 network148 latency148 buffer148", 28),
        ["service148 gateway148", "storage148 network148", "latency148 buffer148"],
    ),
    (
        ("gateway148 storage148 network148 latency148 buffer148 queue148", 6),
        ["gateway148", "storage148", "network148", "latency148", "buffer148", "queue148"],
    ),
    (
        ("gateway148 storage148 network148 latency148 buffer148 queue148", 10),
        ["gateway148", "storage148", "network148", "latency148", "buffer148", "queue148"],
    ),
    (
        ("gateway148 storage148 network148 latency148 buffer148 queue148", 18),
        ["gateway148", "storage148", "network148", "latency148", "buffer148 queue148"],
    ),
    (
        ("gateway148 storage148 network148 latency148 buffer148 queue148", 28),
        ["gateway148 storage148", "network148 latency148", "buffer148 queue148"],
    ),
    (
        ("storage148 network148 latency148 buffer148 queue148 worker148", 6),
        ["storage148", "network148", "latency148", "buffer148", "queue148", "worker148"],
    ),
    (
        ("storage148 network148 latency148 buffer148 queue148 worker148", 10),
        ["storage148", "network148", "latency148", "buffer148", "queue148", "worker148"],
    ),
    (
        ("storage148 network148 latency148 buffer148 queue148 worker148", 18),
        ["storage148", "network148", "latency148", "buffer148 queue148", "worker148"],
    ),
    (
        ("storage148 network148 latency148 buffer148 queue148 worker148", 28),
        ["storage148 network148", "latency148 buffer148", "queue148 worker148"],
    ),
    (
        ("network148 latency148 buffer148 queue148 worker148 kernel148", 6),
        ["network148", "latency148", "buffer148", "queue148", "worker148", "kernel148"],
    ),
    (
        ("network148 latency148 buffer148 queue148 worker148 kernel148", 10),
        ["network148", "latency148", "buffer148", "queue148", "worker148", "kernel148"],
    ),
    (
        ("network148 latency148 buffer148 queue148 worker148 kernel148", 18),
        ["network148", "latency148", "buffer148 queue148", "worker148", "kernel148"],
    ),
    (
        ("network148 latency148 buffer148 queue148 worker148 kernel148", 28),
        ["network148 latency148", "buffer148 queue148 worker148", "kernel148"],
    ),
    (
        ("latency148 buffer148 queue148 worker148 kernel148 signal148", 6),
        ["latency148", "buffer148", "queue148", "worker148", "kernel148", "signal148"],
    ),
    (
        ("latency148 buffer148 queue148 worker148 kernel148 signal148", 10),
        ["latency148", "buffer148", "queue148", "worker148", "kernel148", "signal148"],
    ),
    (
        ("latency148 buffer148 queue148 worker148 kernel148 signal148", 18),
        ["latency148", "buffer148 queue148", "worker148", "kernel148", "signal148"],
    ),
    (
        ("latency148 buffer148 queue148 worker148 kernel148 signal148", 28),
        ["latency148 buffer148", "queue148 worker148 kernel148", "signal148"],
    ),
    (
        ("buffer148 queue148 worker148 kernel148 signal148 packet148", 6),
        ["buffer148", "queue148", "worker148", "kernel148", "signal148", "packet148"],
    ),
    (
        ("buffer148 queue148 worker148 kernel148 signal148 packet148", 10),
        ["buffer148", "queue148", "worker148", "kernel148", "signal148", "packet148"],
    ),
    (
        ("buffer148 queue148 worker148 kernel148 signal148 packet148", 18),
        ["buffer148 queue148", "worker148", "kernel148", "signal148", "packet148"],
    ),
    (
        ("buffer148 queue148 worker148 kernel148 signal148 packet148", 28),
        ["buffer148 queue148 worker148", "kernel148 signal148", "packet148"],
    ),
    (
        ("queue148 worker148 kernel148 signal148 packet148 router148", 6),
        ["queue148", "worker148", "kernel148", "signal148", "packet148", "router148"],
    ),
    (
        ("queue148 worker148 kernel148 signal148 packet148 router148", 10),
        ["queue148", "worker148", "kernel148", "signal148", "packet148", "router148"],
    ),
    (
        ("queue148 worker148 kernel148 signal148 packet148 router148", 18),
        ["queue148 worker148", "kernel148", "signal148", "packet148", "router148"],
    ),
    (
        ("queue148 worker148 kernel148 signal148 packet148 router148", 28),
        ["queue148 worker148 kernel148", "signal148 packet148", "router148"],
    ),
    (
        ("worker148 kernel148 signal148 packet148 router148 cluster148", 6),
        ["worker148", "kernel148", "signal148", "packet148", "router148", "cluster148"],
    ),
    (
        ("worker148 kernel148 signal148 packet148 router148 cluster148", 10),
        ["worker148", "kernel148", "signal148", "packet148", "router148", "cluster148"],
    ),
    (
        ("worker148 kernel148 signal148 packet148 router148 cluster148", 18),
        ["worker148", "kernel148", "signal148", "packet148", "router148", "cluster148"],
    ),
    (
        ("worker148 kernel148 signal148 packet148 router148 cluster148", 28),
        ["worker148 kernel148", "signal148 packet148", "router148 cluster148"],
    ),
    (
        ("kernel148 signal148 packet148 router148 cluster148 mirror148", 6),
        ["kernel148", "signal148", "packet148", "router148", "cluster148", "mirror148"],
    ),
    (
        ("kernel148 signal148 packet148 router148 cluster148 mirror148", 10),
        ["kernel148", "signal148", "packet148", "router148", "cluster148", "mirror148"],
    ),
    (
        ("kernel148 signal148 packet148 router148 cluster148 mirror148", 18),
        ["kernel148", "signal148", "packet148", "router148", "cluster148", "mirror148"],
    ),
    (
        ("kernel148 signal148 packet148 router148 cluster148 mirror148", 28),
        ["kernel148 signal148", "packet148 router148", "cluster148 mirror148"],
    ),
    (
        ("signal148 packet148 router148 cluster148 mirror148 filter148", 6),
        ["signal148", "packet148", "router148", "cluster148", "mirror148", "filter148"],
    ),
    (
        ("signal148 packet148 router148 cluster148 mirror148 filter148", 10),
        ["signal148", "packet148", "router148", "cluster148", "mirror148", "filter148"],
    ),
    (
        ("signal148 packet148 router148 cluster148 mirror148 filter148", 18),
        ["signal148", "packet148", "router148", "cluster148", "mirror148", "filter148"],
    ),
    (
        ("signal148 packet148 router148 cluster148 mirror148 filter148", 28),
        ["signal148 packet148", "router148 cluster148", "mirror148 filter148"],
    ),
    (
        ("packet148 router148 cluster148 mirror148 filter148 ranking148", 6),
        ["packet148", "router148", "cluster148", "mirror148", "filter148", "ranking148"],
    ),
    (
        ("packet148 router148 cluster148 mirror148 filter148 ranking148", 10),
        ["packet148", "router148", "cluster148", "mirror148", "filter148", "ranking148"],
    ),
    (
        ("packet148 router148 cluster148 mirror148 filter148 ranking148", 18),
        ["packet148", "router148", "cluster148", "mirror148", "filter148", "ranking148"],
    ),
    (
        ("packet148 router148 cluster148 mirror148 filter148 ranking148", 28),
        ["packet148 router148", "cluster148 mirror148", "filter148 ranking148"],
    ),
    (
        ("router148 cluster148 mirror148 filter148 ranking148 encoding148", 6),
        ["router148", "cluster148", "mirror148", "filter148", "ranking148", "encoding148"],
    ),
    (
        ("router148 cluster148 mirror148 filter148 ranking148 encoding148", 10),
        ["router148", "cluster148", "mirror148", "filter148", "ranking148", "encoding148"],
    ),
    (
        ("router148 cluster148 mirror148 filter148 ranking148 encoding148", 18),
        ["router148", "cluster148", "mirror148", "filter148", "ranking148", "encoding148"],
    ),
    (
        ("router148 cluster148 mirror148 filter148 ranking148 encoding148", 28),
        ["router148 cluster148", "mirror148 filter148", "ranking148 encoding148"],
    ),
    (
        ("cluster148 mirror148 filter148 ranking148 encoding148 mapping148", 6),
        ["cluster148", "mirror148", "filter148", "ranking148", "encoding148", "mapping148"],
    ),
    (
        ("cluster148 mirror148 filter148 ranking148 encoding148 mapping148", 10),
        ["cluster148", "mirror148", "filter148", "ranking148", "encoding148", "mapping148"],
    ),
    (
        ("cluster148 mirror148 filter148 ranking148 encoding148 mapping148", 18),
        ["cluster148", "mirror148", "filter148", "ranking148", "encoding148", "mapping148"],
    ),
    (
        ("cluster148 mirror148 filter148 ranking148 encoding148 mapping148", 28),
        ["cluster148 mirror148", "filter148 ranking148", "encoding148 mapping148"],
    ),
    (
        ("mirror148 filter148 ranking148 encoding148 mapping148 record148", 6),
        ["mirror148", "filter148", "ranking148", "encoding148", "mapping148", "record148"],
    ),
    (
        ("mirror148 filter148 ranking148 encoding148 mapping148 record148", 10),
        ["mirror148", "filter148", "ranking148", "encoding148", "mapping148", "record148"],
    ),
    (
        ("mirror148 filter148 ranking148 encoding148 mapping148 record148", 18),
        ["mirror148", "filter148", "ranking148", "encoding148", "mapping148", "record148"],
    ),
    (
        ("mirror148 filter148 ranking148 encoding148 mapping148 record148", 28),
        ["mirror148 filter148", "ranking148 encoding148", "mapping148 record148"],
    ),
    (
        ("filter148 ranking148 encoding148 mapping148 record148 candle148", 6),
        ["filter148", "ranking148", "encoding148", "mapping148", "record148", "candle148"],
    ),
    (
        ("filter148 ranking148 encoding148 mapping148 record148 candle148", 10),
        ["filter148", "ranking148", "encoding148", "mapping148", "record148", "candle148"],
    ),
    (
        ("filter148 ranking148 encoding148 mapping148 record148 candle148", 18),
        ["filter148", "ranking148", "encoding148", "mapping148", "record148", "candle148"],
    ),
    (
        ("filter148 ranking148 encoding148 mapping148 record148 candle148", 28),
        ["filter148 ranking148", "encoding148 mapping148", "record148 candle148"],
    ),
    (
        ("ranking148 encoding148 mapping148 record148 candle148 thread148", 6),
        ["ranking148", "encoding148", "mapping148", "record148", "candle148", "thread148"],
    ),
    (
        ("ranking148 encoding148 mapping148 record148 candle148 thread148", 10),
        ["ranking148", "encoding148", "mapping148", "record148", "candle148", "thread148"],
    ),
    (
        ("ranking148 encoding148 mapping148 record148 candle148 thread148", 18),
        ["ranking148", "encoding148", "mapping148", "record148", "candle148", "thread148"],
    ),
    (
        ("ranking148 encoding148 mapping148 record148 candle148 thread148", 28),
        ["ranking148 encoding148", "mapping148 record148", "candle148 thread148"],
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
