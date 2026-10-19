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
        ("round 110: the quick brown fox jumps over the lazy dog", 4),
        ["round", "110:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", 8),
        ["round", "110: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", 12),
        ["round 110:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", 16),
        ["round 110: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", 24),
        ["round 110: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 110: the quick brown fox jumps over the lazy dog", 32),
        ["round 110: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", 4),
        ["round", "110:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", 8),
        ["round", "110:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", 12),
        ["round 110:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", 16),
        ["round 110:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", 24),
        ["round 110: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 110: agentuniverse is a framework for multi agents", 32),
        ["round 110: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", 4),
        ["round", "110:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", 8),
        ["round", "110:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", 12),
        ["round 110:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", 16),
        ["round 110:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", 24),
        ["round 110: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 110: knowledge stored as vectors enables retrieval", 32),
        ["round 110: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 110: the processor reads the record then stops", 4),
        ["round", "110:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 110: the processor reads the record then stops", 8),
        ["round", "110: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 110: the processor reads the record then stops", 12),
        ["round 110:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 110: the processor reads the record then stops", 16),
        ["round 110: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 110: the processor reads the record then stops", 24),
        ["round 110: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 110: the processor reads the record then stops", 32),
        ["round 110: the processor reads", "the record then stops"],
    ),
    (
        ("round 110: a worker pulls the next task from the queue", 4),
        ["round", "110:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 110: a worker pulls the next task from the queue", 8),
        ["round", "110: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 110: a worker pulls the next task from the queue", 12),
        ["round 110: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 110: a worker pulls the next task from the queue", 16),
        ["round 110: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 110: a worker pulls the next task from the queue", 24),
        ["round 110: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 110: a worker pulls the next task from the queue", 32),
        ["round 110: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 110: signals travel through the network layer", 4),
        ["round", "110:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 110: signals travel through the network layer", 8),
        ["round", "110:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 110: signals travel through the network layer", 12),
        ["round 110:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 110: signals travel through the network layer", 16),
        ["round 110:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 110: signals travel through the network layer", 24),
        ["round 110: signals", "travel through the", "network layer"],
    ),
    (
        ("round 110: signals travel through the network layer", 32),
        ["round 110: signals travel", "through the network layer"],
    ),
    (
        ("round 110: the gateway routes each request by policy", 4),
        ["round", "110:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 110: the gateway routes each request by policy", 8),
        ["round", "110: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 110: the gateway routes each request by policy", 12),
        ["round 110:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 110: the gateway routes each request by policy", 16),
        ["round 110: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 110: the gateway routes each request by policy", 24),
        ["round 110: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 110: the gateway routes each request by policy", 32),
        ["round 110: the gateway routes", "each request by policy"],
    ),
    (
        ("round 110: memory grows until the buffer is full", 4),
        ["round", "110:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 110: memory grows until the buffer is full", 8),
        ["round", "110:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 110: memory grows until the buffer is full", 12),
        ["round 110:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 110: memory grows until the buffer is full", 16),
        ["round 110:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 110: memory grows until the buffer is full", 24), ["round 110: memory grows", "until the buffer is full"]),
    (("round 110: memory grows until the buffer is full", 32), ["round 110: memory grows until", "the buffer is full"]),
    (
        ("round 110: the cluster mirrors every packet twice", 4),
        ["round", "110:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 110: the cluster mirrors every packet twice", 8),
        ["round", "110: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 110: the cluster mirrors every packet twice", 12),
        ["round 110:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 110: the cluster mirrors every packet twice", 16),
        ["round 110: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 110: the cluster mirrors every packet twice", 24),
        ["round 110: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 110: the cluster mirrors every packet twice", 32),
        ["round 110: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", 4),
        ["round", "110:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", 8),
        ["round", "110:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", 12),
        ["round 110:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", 16),
        ["round 110:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", 24),
        ["round 110: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 110: ranking uses tokens learned from the corpus", 32),
        ["round 110: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 110: a long session ends when the candle dies", 4),
        ["round", "110:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 110: a long session ends when the candle dies", 8),
        ["round", "110: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 110: a long session ends when the candle dies", 12),
        ["round 110: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 110: a long session ends when the candle dies", 16),
        ["round 110: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 110: a long session ends when the candle dies", 24),
        ["round 110: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 110: a long session ends when the candle dies", 32),
        ["round 110: a long session ends", "when the candle dies"],
    ),
    (
        ("round 110: encode the prompt then map the result", 4),
        ["round", "110:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 110: encode the prompt then map the result", 8),
        ["round", "110:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 110: encode the prompt then map the result", 12),
        ["round 110:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 110: encode the prompt then map the result", 16),
        ["round 110:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 110: encode the prompt then map the result", 24),
        ["round 110: encode the", "prompt then map the", "result"],
    ),
    (("round 110: encode the prompt then map the result", 32), ["round 110: encode the prompt", "then map the result"]),
    (
        ("round 110: the kernel wakes the worker at dawn", 4),
        ["round", "110:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 110: the kernel wakes the worker at dawn", 8),
        ["round", "110: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 110: the kernel wakes the worker at dawn", 12),
        ["round 110:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 110: the kernel wakes the worker at dawn", 16), ["round 110: the", "kernel wakes the", "worker at dawn"]),
    (("round 110: the kernel wakes the worker at dawn", 24), ["round 110: the kernel", "wakes the worker at dawn"]),
    (("round 110: the kernel wakes the worker at dawn", 32), ["round 110: the kernel wakes the", "worker at dawn"]),
    (
        ("round 110: service latency drops after the patch", 4),
        ["round", "110:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 110: service latency drops after the patch", 8),
        ["round", "110:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 110: service latency drops after the patch", 12),
        ["round 110:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 110: service latency drops after the patch", 16),
        ["round 110:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 110: service latency drops after the patch", 24),
        ["round 110: service", "latency drops after the", "patch"],
    ),
    (("round 110: service latency drops after the patch", 32), ["round 110: service latency drops", "after the patch"]),
    (
        ("round 110: the library caches every vector it sees", 4),
        ["round", "110:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 110: the library caches every vector it sees", 8),
        ["round", "110: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 110: the library caches every vector it sees", 12),
        ["round 110:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 110: the library caches every vector it sees", 16),
        ["round 110: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 110: the library caches every vector it sees", 24),
        ["round 110: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 110: the library caches every vector it sees", 32),
        ["round 110: the library caches", "every vector it sees"],
    ),
    (
        ("round 110: agents argue then the debate resolves", 4),
        ["round", "110:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 110: agents argue then the debate resolves", 8),
        ["round", "110:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 110: agents argue then the debate resolves", 12),
        ["round 110:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 110: agents argue then the debate resolves", 16),
        ["round 110:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 110: agents argue then the debate resolves", 24), ["round 110: agents argue", "then the debate resolves"]),
    (("round 110: agents argue then the debate resolves", 32), ["round 110: agents argue then the", "debate resolves"]),
    (
        ("round 110: the filter keeps only strong matches", 4),
        ["round", "110:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 110: the filter keeps only strong matches", 8),
        ["round", "110: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 110: the filter keeps only strong matches", 12),
        ["round 110:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 110: the filter keeps only strong matches", 16),
        ["round 110: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 110: the filter keeps only strong matches", 24),
        ["round 110: the filter", "keeps only strong", "matches"],
    ),
    (("round 110: the filter keeps only strong matches", 32), ["round 110: the filter keeps only", "strong matches"]),
    (
        ("round 110: the model answers with a short reply", 4),
        ["round", "110:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 110: the model answers with a short reply", 8),
        ["round", "110: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 110: the model answers with a short reply", 12),
        ["round 110:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 110: the model answers with a short reply", 16),
        ["round 110: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 110: the model answers with a short reply", 24),
        ["round 110: the model", "answers with a short", "reply"],
    ),
    (("round 110: the model answers with a short reply", 32), ["round 110: the model answers", "with a short reply"]),
    (
        ("round 110: the recorder stores the reasoning trace", 4),
        ["round", "110:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 110: the recorder stores the reasoning trace", 8),
        ["round", "110: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 110: the recorder stores the reasoning trace", 12),
        ["round 110:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 110: the recorder stores the reasoning trace", 16),
        ["round 110: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 110: the recorder stores the reasoning trace", 24),
        ["round 110: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 110: the recorder stores the reasoning trace", 32),
        ["round 110: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 110: the angel watches the processor run", 4),
        ["round", "110:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 110: the angel watches the processor run", 8),
        ["round", "110: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 110: the angel watches the processor run", 12),
        ["round 110:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 110: the angel watches the processor run", 16),
        ["round 110: the", "angel watches", "the processor", "run"],
    ),
    (("round 110: the angel watches the processor run", 24), ["round 110: the angel", "watches the processor", "run"]),
    (("round 110: the angel watches the processor run", 32), ["round 110: the angel watches the", "processor run"]),
    (
        ("round 110: angle of the vector decides the match", 4),
        ["round", "110:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 110: angle of the vector decides the match", 8),
        ["round", "110:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 110: angle of the vector decides the match", 12),
        ["round 110:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 110: angle of the vector decides the match", 16),
        ["round 110: angle", "of the vector", "decides the", "match"],
    ),
    (("round 110: angle of the vector decides the match", 24), ["round 110: angle of the", "vector decides the match"]),
    (("round 110: angle of the vector decides the match", 32), ["round 110: angle of the vector", "decides the match"]),
    (
        ("round 110: the candle burns twice as long at night", 4),
        ["round", "110:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 110: the candle burns twice as long at night", 8),
        ["round", "110: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 110: the candle burns twice as long at night", 12),
        ["round 110:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 110: the candle burns twice as long at night", 16),
        ["round 110: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 110: the candle burns twice as long at night", 24),
        ["round 110: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 110: the candle burns twice as long at night", 32),
        ["round 110: the candle burns", "twice as long at night"],
    ),
    (
        ("round 110: a mirror of the universe in one line", 4),
        ["round", "110:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 110: a mirror of the universe in one line", 8),
        ["round", "110: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 110: a mirror of the universe in one line", 12),
        ["round 110: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 110: a mirror of the universe in one line", 16),
        ["round 110: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 110: a mirror of the universe in one line", 24), ["round 110: a mirror of", "the universe in one line"]),
    (("round 110: a mirror of the universe in one line", 32), ["round 110: a mirror of the", "universe in one line"]),
    (
        ("round 110: the queue drains before the storm", 4),
        ["round", "110:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 110: the queue drains before the storm", 8),
        ["round", "110: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 110: the queue drains before the storm", 12),
        ["round 110:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 110: the queue drains before the storm", 16), ["round 110: the", "queue drains", "before the storm"]),
    (("round 110: the queue drains before the storm", 24), ["round 110: the queue", "drains before the storm"]),
    (("round 110: the queue drains before the storm", 32), ["round 110: the queue drains", "before the storm"]),
    (
        ("kitten110 sitting110 agent110 angle110 universe110 memory110", 6),
        ["kitten110", "sitting110", "agent110", "angle110", "universe110", "memory110"],
    ),
    (
        ("kitten110 sitting110 agent110 angle110 universe110 memory110", 10),
        ["kitten110", "sitting110", "agent110", "angle110", "universe110", "memory110"],
    ),
    (
        ("kitten110 sitting110 agent110 angle110 universe110 memory110", 18),
        ["kitten110", "sitting110", "agent110 angle110", "universe110", "memory110"],
    ),
    (
        ("kitten110 sitting110 agent110 angle110 universe110 memory110", 28),
        ["kitten110 sitting110", "agent110 angle110", "universe110 memory110"],
    ),
    (
        ("sitting110 agent110 angle110 universe110 memory110 stream110", 6),
        ["sitting110", "agent110", "angle110", "universe110", "memory110", "stream110"],
    ),
    (
        ("sitting110 agent110 angle110 universe110 memory110 stream110", 10),
        ["sitting110", "agent110", "angle110", "universe110", "memory110", "stream110"],
    ),
    (
        ("sitting110 agent110 angle110 universe110 memory110 stream110", 18),
        ["sitting110", "agent110 angle110", "universe110", "memory110", "stream110"],
    ),
    (
        ("sitting110 agent110 angle110 universe110 memory110 stream110", 28),
        ["sitting110 agent110 angle110", "universe110 memory110", "stream110"],
    ),
    (
        ("agent110 angle110 universe110 memory110 stream110 context110", 6),
        ["agent110", "angle110", "universe110", "memory110", "stream110", "context110"],
    ),
    (
        ("agent110 angle110 universe110 memory110 stream110 context110", 10),
        ["agent110", "angle110", "universe110", "memory110", "stream110", "context110"],
    ),
    (
        ("agent110 angle110 universe110 memory110 stream110 context110", 18),
        ["agent110 angle110", "universe110", "memory110", "stream110", "context110"],
    ),
    (
        ("agent110 angle110 universe110 memory110 stream110 context110", 28),
        ["agent110 angle110", "universe110 memory110", "stream110 context110"],
    ),
    (
        ("angle110 universe110 memory110 stream110 context110 knowledge110", 6),
        ["angle110", "universe110", "memory110", "stream110", "context110", "knowledge110"],
    ),
    (
        ("angle110 universe110 memory110 stream110 context110 knowledge110", 10),
        ["angle110", "universe110", "memory110", "stream110", "context110", "knowledge110"],
    ),
    (
        ("angle110 universe110 memory110 stream110 context110 knowledge110", 18),
        ["angle110", "universe110", "memory110", "stream110", "context110", "knowledge110"],
    ),
    (
        ("angle110 universe110 memory110 stream110 context110 knowledge110", 28),
        ["angle110 universe110", "memory110 stream110", "context110 knowledge110"],
    ),
    (
        ("universe110 memory110 stream110 context110 knowledge110 vector110", 6),
        ["universe110", "memory110", "stream110", "context110", "knowledge110", "vector110"],
    ),
    (
        ("universe110 memory110 stream110 context110 knowledge110 vector110", 10),
        ["universe110", "memory110", "stream110", "context110", "knowledge110", "vector110"],
    ),
    (
        ("universe110 memory110 stream110 context110 knowledge110 vector110", 18),
        ["universe110", "memory110", "stream110", "context110", "knowledge110", "vector110"],
    ),
    (
        ("universe110 memory110 stream110 context110 knowledge110 vector110", 28),
        ["universe110 memory110", "stream110 context110", "knowledge110 vector110"],
    ),
    (
        ("memory110 stream110 context110 knowledge110 vector110 processor110", 6),
        ["memory110", "stream110", "context110", "knowledge110", "vector110", "processor110"],
    ),
    (
        ("memory110 stream110 context110 knowledge110 vector110 processor110", 10),
        ["memory110", "stream110", "context110", "knowledge110", "vector110", "processor110"],
    ),
    (
        ("memory110 stream110 context110 knowledge110 vector110 processor110", 18),
        ["memory110", "stream110", "context110", "knowledge110", "vector110", "processor110"],
    ),
    (
        ("memory110 stream110 context110 knowledge110 vector110 processor110", 28),
        ["memory110 stream110", "context110 knowledge110", "vector110 processor110"],
    ),
    (
        ("stream110 context110 knowledge110 vector110 processor110 reasoning110", 6),
        ["stream110", "context110", "knowledge110", "vector110", "processor110", "reasoning110"],
    ),
    (
        ("stream110 context110 knowledge110 vector110 processor110 reasoning110", 10),
        ["stream110", "context110", "knowledge110", "vector110", "processor110", "reasoning110"],
    ),
    (
        ("stream110 context110 knowledge110 vector110 processor110 reasoning110", 18),
        ["stream110", "context110", "knowledge110", "vector110", "processor110", "reasoning110"],
    ),
    (
        ("stream110 context110 knowledge110 vector110 processor110 reasoning110", 28),
        ["stream110 context110", "knowledge110 vector110", "processor110 reasoning110"],
    ),
    (
        ("context110 knowledge110 vector110 processor110 reasoning110 machine110", 6),
        ["context110", "knowledge110", "vector110", "processor110", "reasoning110", "machine110"],
    ),
    (
        ("context110 knowledge110 vector110 processor110 reasoning110 machine110", 10),
        ["context110", "knowledge110", "vector110", "processor110", "reasoning110", "machine110"],
    ),
    (
        ("context110 knowledge110 vector110 processor110 reasoning110 machine110", 18),
        ["context110", "knowledge110", "vector110", "processor110", "reasoning110", "machine110"],
    ),
    (
        ("context110 knowledge110 vector110 processor110 reasoning110 machine110", 28),
        ["context110 knowledge110", "vector110 processor110", "reasoning110 machine110"],
    ),
    (
        ("knowledge110 vector110 processor110 reasoning110 machine110 learning110", 6),
        ["knowledge110", "vector110", "processor110", "reasoning110", "machine110", "learning110"],
    ),
    (
        ("knowledge110 vector110 processor110 reasoning110 machine110 learning110", 10),
        ["knowledge110", "vector110", "processor110", "reasoning110", "machine110", "learning110"],
    ),
    (
        ("knowledge110 vector110 processor110 reasoning110 machine110 learning110", 18),
        ["knowledge110", "vector110", "processor110", "reasoning110", "machine110", "learning110"],
    ),
    (
        ("knowledge110 vector110 processor110 reasoning110 machine110 learning110", 28),
        ["knowledge110 vector110", "processor110 reasoning110", "machine110 learning110"],
    ),
    (
        ("vector110 processor110 reasoning110 machine110 learning110 model110", 6),
        ["vector110", "processor110", "reasoning110", "machine110", "learning110", "model110"],
    ),
    (
        ("vector110 processor110 reasoning110 machine110 learning110 model110", 10),
        ["vector110", "processor110", "reasoning110", "machine110", "learning110", "model110"],
    ),
    (
        ("vector110 processor110 reasoning110 machine110 learning110 model110", 18),
        ["vector110", "processor110", "reasoning110", "machine110", "learning110", "model110"],
    ),
    (
        ("vector110 processor110 reasoning110 machine110 learning110 model110", 28),
        ["vector110 processor110", "reasoning110 machine110", "learning110 model110"],
    ),
    (
        ("processor110 reasoning110 machine110 learning110 model110 token110", 6),
        ["processor110", "reasoning110", "machine110", "learning110", "model110", "token110"],
    ),
    (
        ("processor110 reasoning110 machine110 learning110 model110 token110", 10),
        ["processor110", "reasoning110", "machine110", "learning110", "model110", "token110"],
    ),
    (
        ("processor110 reasoning110 machine110 learning110 model110 token110", 18),
        ["processor110", "reasoning110", "machine110", "learning110", "model110 token110"],
    ),
    (
        ("processor110 reasoning110 machine110 learning110 model110 token110", 28),
        ["processor110 reasoning110", "machine110 learning110", "model110 token110"],
    ),
    (
        ("reasoning110 machine110 learning110 model110 token110 prompt110", 6),
        ["reasoning110", "machine110", "learning110", "model110", "token110", "prompt110"],
    ),
    (
        ("reasoning110 machine110 learning110 model110 token110 prompt110", 10),
        ["reasoning110", "machine110", "learning110", "model110", "token110", "prompt110"],
    ),
    (
        ("reasoning110 machine110 learning110 model110 token110 prompt110", 18),
        ["reasoning110", "machine110", "learning110", "model110 token110", "prompt110"],
    ),
    (
        ("reasoning110 machine110 learning110 model110 token110 prompt110", 28),
        ["reasoning110 machine110", "learning110 model110", "token110 prompt110"],
    ),
    (
        ("machine110 learning110 model110 token110 prompt110 session110", 6),
        ["machine110", "learning110", "model110", "token110", "prompt110", "session110"],
    ),
    (
        ("machine110 learning110 model110 token110 prompt110 session110", 10),
        ["machine110", "learning110", "model110", "token110", "prompt110", "session110"],
    ),
    (
        ("machine110 learning110 model110 token110 prompt110 session110", 18),
        ["machine110", "learning110", "model110 token110", "prompt110", "session110"],
    ),
    (
        ("machine110 learning110 model110 token110 prompt110 session110", 28),
        ["machine110 learning110", "model110 token110 prompt110", "session110"],
    ),
    (
        ("learning110 model110 token110 prompt110 session110 library110", 6),
        ["learning110", "model110", "token110", "prompt110", "session110", "library110"],
    ),
    (
        ("learning110 model110 token110 prompt110 session110 library110", 10),
        ["learning110", "model110", "token110", "prompt110", "session110", "library110"],
    ),
    (
        ("learning110 model110 token110 prompt110 session110 library110", 18),
        ["learning110", "model110 token110", "prompt110", "session110", "library110"],
    ),
    (
        ("learning110 model110 token110 prompt110 session110 library110", 28),
        ["learning110 model110", "token110 prompt110", "session110 library110"],
    ),
    (
        ("model110 token110 prompt110 session110 library110 service110", 6),
        ["model110", "token110", "prompt110", "session110", "library110", "service110"],
    ),
    (
        ("model110 token110 prompt110 session110 library110 service110", 10),
        ["model110", "token110", "prompt110", "session110", "library110", "service110"],
    ),
    (
        ("model110 token110 prompt110 session110 library110 service110", 18),
        ["model110 token110", "prompt110", "session110", "library110", "service110"],
    ),
    (
        ("model110 token110 prompt110 session110 library110 service110", 28),
        ["model110 token110 prompt110", "session110 library110", "service110"],
    ),
    (
        ("token110 prompt110 session110 library110 service110 gateway110", 6),
        ["token110", "prompt110", "session110", "library110", "service110", "gateway110"],
    ),
    (
        ("token110 prompt110 session110 library110 service110 gateway110", 10),
        ["token110", "prompt110", "session110", "library110", "service110", "gateway110"],
    ),
    (
        ("token110 prompt110 session110 library110 service110 gateway110", 18),
        ["token110 prompt110", "session110", "library110", "service110", "gateway110"],
    ),
    (
        ("token110 prompt110 session110 library110 service110 gateway110", 28),
        ["token110 prompt110", "session110 library110", "service110 gateway110"],
    ),
    (
        ("prompt110 session110 library110 service110 gateway110 storage110", 6),
        ["prompt110", "session110", "library110", "service110", "gateway110", "storage110"],
    ),
    (
        ("prompt110 session110 library110 service110 gateway110 storage110", 10),
        ["prompt110", "session110", "library110", "service110", "gateway110", "storage110"],
    ),
    (
        ("prompt110 session110 library110 service110 gateway110 storage110", 18),
        ["prompt110", "session110", "library110", "service110", "gateway110", "storage110"],
    ),
    (
        ("prompt110 session110 library110 service110 gateway110 storage110", 28),
        ["prompt110 session110", "library110 service110", "gateway110 storage110"],
    ),
    (
        ("session110 library110 service110 gateway110 storage110 network110", 6),
        ["session110", "library110", "service110", "gateway110", "storage110", "network110"],
    ),
    (
        ("session110 library110 service110 gateway110 storage110 network110", 10),
        ["session110", "library110", "service110", "gateway110", "storage110", "network110"],
    ),
    (
        ("session110 library110 service110 gateway110 storage110 network110", 18),
        ["session110", "library110", "service110", "gateway110", "storage110", "network110"],
    ),
    (
        ("session110 library110 service110 gateway110 storage110 network110", 28),
        ["session110 library110", "service110 gateway110", "storage110 network110"],
    ),
    (
        ("library110 service110 gateway110 storage110 network110 latency110", 6),
        ["library110", "service110", "gateway110", "storage110", "network110", "latency110"],
    ),
    (
        ("library110 service110 gateway110 storage110 network110 latency110", 10),
        ["library110", "service110", "gateway110", "storage110", "network110", "latency110"],
    ),
    (
        ("library110 service110 gateway110 storage110 network110 latency110", 18),
        ["library110", "service110", "gateway110", "storage110", "network110", "latency110"],
    ),
    (
        ("library110 service110 gateway110 storage110 network110 latency110", 28),
        ["library110 service110", "gateway110 storage110", "network110 latency110"],
    ),
    (
        ("service110 gateway110 storage110 network110 latency110 buffer110", 6),
        ["service110", "gateway110", "storage110", "network110", "latency110", "buffer110"],
    ),
    (
        ("service110 gateway110 storage110 network110 latency110 buffer110", 10),
        ["service110", "gateway110", "storage110", "network110", "latency110", "buffer110"],
    ),
    (
        ("service110 gateway110 storage110 network110 latency110 buffer110", 18),
        ["service110", "gateway110", "storage110", "network110", "latency110", "buffer110"],
    ),
    (
        ("service110 gateway110 storage110 network110 latency110 buffer110", 28),
        ["service110 gateway110", "storage110 network110", "latency110 buffer110"],
    ),
    (
        ("gateway110 storage110 network110 latency110 buffer110 queue110", 6),
        ["gateway110", "storage110", "network110", "latency110", "buffer110", "queue110"],
    ),
    (
        ("gateway110 storage110 network110 latency110 buffer110 queue110", 10),
        ["gateway110", "storage110", "network110", "latency110", "buffer110", "queue110"],
    ),
    (
        ("gateway110 storage110 network110 latency110 buffer110 queue110", 18),
        ["gateway110", "storage110", "network110", "latency110", "buffer110 queue110"],
    ),
    (
        ("gateway110 storage110 network110 latency110 buffer110 queue110", 28),
        ["gateway110 storage110", "network110 latency110", "buffer110 queue110"],
    ),
    (
        ("storage110 network110 latency110 buffer110 queue110 worker110", 6),
        ["storage110", "network110", "latency110", "buffer110", "queue110", "worker110"],
    ),
    (
        ("storage110 network110 latency110 buffer110 queue110 worker110", 10),
        ["storage110", "network110", "latency110", "buffer110", "queue110", "worker110"],
    ),
    (
        ("storage110 network110 latency110 buffer110 queue110 worker110", 18),
        ["storage110", "network110", "latency110", "buffer110 queue110", "worker110"],
    ),
    (
        ("storage110 network110 latency110 buffer110 queue110 worker110", 28),
        ["storage110 network110", "latency110 buffer110", "queue110 worker110"],
    ),
    (
        ("network110 latency110 buffer110 queue110 worker110 kernel110", 6),
        ["network110", "latency110", "buffer110", "queue110", "worker110", "kernel110"],
    ),
    (
        ("network110 latency110 buffer110 queue110 worker110 kernel110", 10),
        ["network110", "latency110", "buffer110", "queue110", "worker110", "kernel110"],
    ),
    (
        ("network110 latency110 buffer110 queue110 worker110 kernel110", 18),
        ["network110", "latency110", "buffer110 queue110", "worker110", "kernel110"],
    ),
    (
        ("network110 latency110 buffer110 queue110 worker110 kernel110", 28),
        ["network110 latency110", "buffer110 queue110 worker110", "kernel110"],
    ),
    (
        ("latency110 buffer110 queue110 worker110 kernel110 signal110", 6),
        ["latency110", "buffer110", "queue110", "worker110", "kernel110", "signal110"],
    ),
    (
        ("latency110 buffer110 queue110 worker110 kernel110 signal110", 10),
        ["latency110", "buffer110", "queue110", "worker110", "kernel110", "signal110"],
    ),
    (
        ("latency110 buffer110 queue110 worker110 kernel110 signal110", 18),
        ["latency110", "buffer110 queue110", "worker110", "kernel110", "signal110"],
    ),
    (
        ("latency110 buffer110 queue110 worker110 kernel110 signal110", 28),
        ["latency110 buffer110", "queue110 worker110 kernel110", "signal110"],
    ),
    (
        ("buffer110 queue110 worker110 kernel110 signal110 packet110", 6),
        ["buffer110", "queue110", "worker110", "kernel110", "signal110", "packet110"],
    ),
    (
        ("buffer110 queue110 worker110 kernel110 signal110 packet110", 10),
        ["buffer110", "queue110", "worker110", "kernel110", "signal110", "packet110"],
    ),
    (
        ("buffer110 queue110 worker110 kernel110 signal110 packet110", 18),
        ["buffer110 queue110", "worker110", "kernel110", "signal110", "packet110"],
    ),
    (
        ("buffer110 queue110 worker110 kernel110 signal110 packet110", 28),
        ["buffer110 queue110 worker110", "kernel110 signal110", "packet110"],
    ),
    (
        ("queue110 worker110 kernel110 signal110 packet110 router110", 6),
        ["queue110", "worker110", "kernel110", "signal110", "packet110", "router110"],
    ),
    (
        ("queue110 worker110 kernel110 signal110 packet110 router110", 10),
        ["queue110", "worker110", "kernel110", "signal110", "packet110", "router110"],
    ),
    (
        ("queue110 worker110 kernel110 signal110 packet110 router110", 18),
        ["queue110 worker110", "kernel110", "signal110", "packet110", "router110"],
    ),
    (
        ("queue110 worker110 kernel110 signal110 packet110 router110", 28),
        ["queue110 worker110 kernel110", "signal110 packet110", "router110"],
    ),
    (
        ("worker110 kernel110 signal110 packet110 router110 cluster110", 6),
        ["worker110", "kernel110", "signal110", "packet110", "router110", "cluster110"],
    ),
    (
        ("worker110 kernel110 signal110 packet110 router110 cluster110", 10),
        ["worker110", "kernel110", "signal110", "packet110", "router110", "cluster110"],
    ),
    (
        ("worker110 kernel110 signal110 packet110 router110 cluster110", 18),
        ["worker110", "kernel110", "signal110", "packet110", "router110", "cluster110"],
    ),
    (
        ("worker110 kernel110 signal110 packet110 router110 cluster110", 28),
        ["worker110 kernel110", "signal110 packet110", "router110 cluster110"],
    ),
    (
        ("kernel110 signal110 packet110 router110 cluster110 mirror110", 6),
        ["kernel110", "signal110", "packet110", "router110", "cluster110", "mirror110"],
    ),
    (
        ("kernel110 signal110 packet110 router110 cluster110 mirror110", 10),
        ["kernel110", "signal110", "packet110", "router110", "cluster110", "mirror110"],
    ),
    (
        ("kernel110 signal110 packet110 router110 cluster110 mirror110", 18),
        ["kernel110", "signal110", "packet110", "router110", "cluster110", "mirror110"],
    ),
    (
        ("kernel110 signal110 packet110 router110 cluster110 mirror110", 28),
        ["kernel110 signal110", "packet110 router110", "cluster110 mirror110"],
    ),
    (
        ("signal110 packet110 router110 cluster110 mirror110 filter110", 6),
        ["signal110", "packet110", "router110", "cluster110", "mirror110", "filter110"],
    ),
    (
        ("signal110 packet110 router110 cluster110 mirror110 filter110", 10),
        ["signal110", "packet110", "router110", "cluster110", "mirror110", "filter110"],
    ),
    (
        ("signal110 packet110 router110 cluster110 mirror110 filter110", 18),
        ["signal110", "packet110", "router110", "cluster110", "mirror110", "filter110"],
    ),
    (
        ("signal110 packet110 router110 cluster110 mirror110 filter110", 28),
        ["signal110 packet110", "router110 cluster110", "mirror110 filter110"],
    ),
    (
        ("packet110 router110 cluster110 mirror110 filter110 ranking110", 6),
        ["packet110", "router110", "cluster110", "mirror110", "filter110", "ranking110"],
    ),
    (
        ("packet110 router110 cluster110 mirror110 filter110 ranking110", 10),
        ["packet110", "router110", "cluster110", "mirror110", "filter110", "ranking110"],
    ),
    (
        ("packet110 router110 cluster110 mirror110 filter110 ranking110", 18),
        ["packet110", "router110", "cluster110", "mirror110", "filter110", "ranking110"],
    ),
    (
        ("packet110 router110 cluster110 mirror110 filter110 ranking110", 28),
        ["packet110 router110", "cluster110 mirror110", "filter110 ranking110"],
    ),
    (
        ("router110 cluster110 mirror110 filter110 ranking110 encoding110", 6),
        ["router110", "cluster110", "mirror110", "filter110", "ranking110", "encoding110"],
    ),
    (
        ("router110 cluster110 mirror110 filter110 ranking110 encoding110", 10),
        ["router110", "cluster110", "mirror110", "filter110", "ranking110", "encoding110"],
    ),
    (
        ("router110 cluster110 mirror110 filter110 ranking110 encoding110", 18),
        ["router110", "cluster110", "mirror110", "filter110", "ranking110", "encoding110"],
    ),
    (
        ("router110 cluster110 mirror110 filter110 ranking110 encoding110", 28),
        ["router110 cluster110", "mirror110 filter110", "ranking110 encoding110"],
    ),
    (
        ("cluster110 mirror110 filter110 ranking110 encoding110 mapping110", 6),
        ["cluster110", "mirror110", "filter110", "ranking110", "encoding110", "mapping110"],
    ),
    (
        ("cluster110 mirror110 filter110 ranking110 encoding110 mapping110", 10),
        ["cluster110", "mirror110", "filter110", "ranking110", "encoding110", "mapping110"],
    ),
    (
        ("cluster110 mirror110 filter110 ranking110 encoding110 mapping110", 18),
        ["cluster110", "mirror110", "filter110", "ranking110", "encoding110", "mapping110"],
    ),
    (
        ("cluster110 mirror110 filter110 ranking110 encoding110 mapping110", 28),
        ["cluster110 mirror110", "filter110 ranking110", "encoding110 mapping110"],
    ),
    (
        ("mirror110 filter110 ranking110 encoding110 mapping110 record110", 6),
        ["mirror110", "filter110", "ranking110", "encoding110", "mapping110", "record110"],
    ),
    (
        ("mirror110 filter110 ranking110 encoding110 mapping110 record110", 10),
        ["mirror110", "filter110", "ranking110", "encoding110", "mapping110", "record110"],
    ),
    (
        ("mirror110 filter110 ranking110 encoding110 mapping110 record110", 18),
        ["mirror110", "filter110", "ranking110", "encoding110", "mapping110", "record110"],
    ),
    (
        ("mirror110 filter110 ranking110 encoding110 mapping110 record110", 28),
        ["mirror110 filter110", "ranking110 encoding110", "mapping110 record110"],
    ),
    (
        ("filter110 ranking110 encoding110 mapping110 record110 candle110", 6),
        ["filter110", "ranking110", "encoding110", "mapping110", "record110", "candle110"],
    ),
    (
        ("filter110 ranking110 encoding110 mapping110 record110 candle110", 10),
        ["filter110", "ranking110", "encoding110", "mapping110", "record110", "candle110"],
    ),
    (
        ("filter110 ranking110 encoding110 mapping110 record110 candle110", 18),
        ["filter110", "ranking110", "encoding110", "mapping110", "record110", "candle110"],
    ),
    (
        ("filter110 ranking110 encoding110 mapping110 record110 candle110", 28),
        ["filter110 ranking110", "encoding110 mapping110", "record110 candle110"],
    ),
    (
        ("ranking110 encoding110 mapping110 record110 candle110 thread110", 6),
        ["ranking110", "encoding110", "mapping110", "record110", "candle110", "thread110"],
    ),
    (
        ("ranking110 encoding110 mapping110 record110 candle110 thread110", 10),
        ["ranking110", "encoding110", "mapping110", "record110", "candle110", "thread110"],
    ),
    (
        ("ranking110 encoding110 mapping110 record110 candle110 thread110", 18),
        ["ranking110", "encoding110", "mapping110", "record110", "candle110", "thread110"],
    ),
    (
        ("ranking110 encoding110 mapping110 record110 candle110 thread110", 28),
        ["ranking110 encoding110", "mapping110 record110", "candle110 thread110"],
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
