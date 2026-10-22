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
        ("round 113: the quick brown fox jumps over the lazy dog", 4),
        ["round", "113:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", 8),
        ["round", "113: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", 12),
        ["round 113:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", 16),
        ["round 113: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", 24),
        ["round 113: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 113: the quick brown fox jumps over the lazy dog", 32),
        ["round 113: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", 4),
        ["round", "113:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", 8),
        ["round", "113:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", 12),
        ["round 113:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", 16),
        ["round 113:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", 24),
        ["round 113: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 113: agentuniverse is a framework for multi agents", 32),
        ["round 113: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", 4),
        ["round", "113:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", 8),
        ["round", "113:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", 12),
        ["round 113:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", 16),
        ["round 113:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", 24),
        ["round 113: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 113: knowledge stored as vectors enables retrieval", 32),
        ["round 113: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 113: the processor reads the record then stops", 4),
        ["round", "113:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 113: the processor reads the record then stops", 8),
        ["round", "113: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 113: the processor reads the record then stops", 12),
        ["round 113:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 113: the processor reads the record then stops", 16),
        ["round 113: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 113: the processor reads the record then stops", 24),
        ["round 113: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 113: the processor reads the record then stops", 32),
        ["round 113: the processor reads", "the record then stops"],
    ),
    (
        ("round 113: a worker pulls the next task from the queue", 4),
        ["round", "113:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 113: a worker pulls the next task from the queue", 8),
        ["round", "113: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 113: a worker pulls the next task from the queue", 12),
        ["round 113: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 113: a worker pulls the next task from the queue", 16),
        ["round 113: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 113: a worker pulls the next task from the queue", 24),
        ["round 113: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 113: a worker pulls the next task from the queue", 32),
        ["round 113: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 113: signals travel through the network layer", 4),
        ["round", "113:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 113: signals travel through the network layer", 8),
        ["round", "113:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 113: signals travel through the network layer", 12),
        ["round 113:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 113: signals travel through the network layer", 16),
        ["round 113:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 113: signals travel through the network layer", 24),
        ["round 113: signals", "travel through the", "network layer"],
    ),
    (
        ("round 113: signals travel through the network layer", 32),
        ["round 113: signals travel", "through the network layer"],
    ),
    (
        ("round 113: the gateway routes each request by policy", 4),
        ["round", "113:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 113: the gateway routes each request by policy", 8),
        ["round", "113: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 113: the gateway routes each request by policy", 12),
        ["round 113:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 113: the gateway routes each request by policy", 16),
        ["round 113: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 113: the gateway routes each request by policy", 24),
        ["round 113: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 113: the gateway routes each request by policy", 32),
        ["round 113: the gateway routes", "each request by policy"],
    ),
    (
        ("round 113: memory grows until the buffer is full", 4),
        ["round", "113:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 113: memory grows until the buffer is full", 8),
        ["round", "113:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 113: memory grows until the buffer is full", 12),
        ["round 113:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 113: memory grows until the buffer is full", 16),
        ["round 113:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 113: memory grows until the buffer is full", 24), ["round 113: memory grows", "until the buffer is full"]),
    (("round 113: memory grows until the buffer is full", 32), ["round 113: memory grows until", "the buffer is full"]),
    (
        ("round 113: the cluster mirrors every packet twice", 4),
        ["round", "113:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 113: the cluster mirrors every packet twice", 8),
        ["round", "113: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 113: the cluster mirrors every packet twice", 12),
        ["round 113:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 113: the cluster mirrors every packet twice", 16),
        ["round 113: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 113: the cluster mirrors every packet twice", 24),
        ["round 113: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 113: the cluster mirrors every packet twice", 32),
        ["round 113: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", 4),
        ["round", "113:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", 8),
        ["round", "113:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", 12),
        ["round 113:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", 16),
        ["round 113:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", 24),
        ["round 113: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 113: ranking uses tokens learned from the corpus", 32),
        ["round 113: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 113: a long session ends when the candle dies", 4),
        ["round", "113:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 113: a long session ends when the candle dies", 8),
        ["round", "113: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 113: a long session ends when the candle dies", 12),
        ["round 113: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 113: a long session ends when the candle dies", 16),
        ["round 113: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 113: a long session ends when the candle dies", 24),
        ["round 113: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 113: a long session ends when the candle dies", 32),
        ["round 113: a long session ends", "when the candle dies"],
    ),
    (
        ("round 113: encode the prompt then map the result", 4),
        ["round", "113:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 113: encode the prompt then map the result", 8),
        ["round", "113:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 113: encode the prompt then map the result", 12),
        ["round 113:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 113: encode the prompt then map the result", 16),
        ["round 113:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 113: encode the prompt then map the result", 24),
        ["round 113: encode the", "prompt then map the", "result"],
    ),
    (("round 113: encode the prompt then map the result", 32), ["round 113: encode the prompt", "then map the result"]),
    (
        ("round 113: the kernel wakes the worker at dawn", 4),
        ["round", "113:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 113: the kernel wakes the worker at dawn", 8),
        ["round", "113: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 113: the kernel wakes the worker at dawn", 12),
        ["round 113:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 113: the kernel wakes the worker at dawn", 16), ["round 113: the", "kernel wakes the", "worker at dawn"]),
    (("round 113: the kernel wakes the worker at dawn", 24), ["round 113: the kernel", "wakes the worker at dawn"]),
    (("round 113: the kernel wakes the worker at dawn", 32), ["round 113: the kernel wakes the", "worker at dawn"]),
    (
        ("round 113: service latency drops after the patch", 4),
        ["round", "113:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 113: service latency drops after the patch", 8),
        ["round", "113:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 113: service latency drops after the patch", 12),
        ["round 113:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 113: service latency drops after the patch", 16),
        ["round 113:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 113: service latency drops after the patch", 24),
        ["round 113: service", "latency drops after the", "patch"],
    ),
    (("round 113: service latency drops after the patch", 32), ["round 113: service latency drops", "after the patch"]),
    (
        ("round 113: the library caches every vector it sees", 4),
        ["round", "113:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 113: the library caches every vector it sees", 8),
        ["round", "113: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 113: the library caches every vector it sees", 12),
        ["round 113:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 113: the library caches every vector it sees", 16),
        ["round 113: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 113: the library caches every vector it sees", 24),
        ["round 113: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 113: the library caches every vector it sees", 32),
        ["round 113: the library caches", "every vector it sees"],
    ),
    (
        ("round 113: agents argue then the debate resolves", 4),
        ["round", "113:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 113: agents argue then the debate resolves", 8),
        ["round", "113:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 113: agents argue then the debate resolves", 12),
        ["round 113:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 113: agents argue then the debate resolves", 16),
        ["round 113:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 113: agents argue then the debate resolves", 24), ["round 113: agents argue", "then the debate resolves"]),
    (("round 113: agents argue then the debate resolves", 32), ["round 113: agents argue then the", "debate resolves"]),
    (
        ("round 113: the filter keeps only strong matches", 4),
        ["round", "113:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 113: the filter keeps only strong matches", 8),
        ["round", "113: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 113: the filter keeps only strong matches", 12),
        ["round 113:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 113: the filter keeps only strong matches", 16),
        ["round 113: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 113: the filter keeps only strong matches", 24),
        ["round 113: the filter", "keeps only strong", "matches"],
    ),
    (("round 113: the filter keeps only strong matches", 32), ["round 113: the filter keeps only", "strong matches"]),
    (
        ("round 113: the model answers with a short reply", 4),
        ["round", "113:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 113: the model answers with a short reply", 8),
        ["round", "113: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 113: the model answers with a short reply", 12),
        ["round 113:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 113: the model answers with a short reply", 16),
        ["round 113: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 113: the model answers with a short reply", 24),
        ["round 113: the model", "answers with a short", "reply"],
    ),
    (("round 113: the model answers with a short reply", 32), ["round 113: the model answers", "with a short reply"]),
    (
        ("round 113: the recorder stores the reasoning trace", 4),
        ["round", "113:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 113: the recorder stores the reasoning trace", 8),
        ["round", "113: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 113: the recorder stores the reasoning trace", 12),
        ["round 113:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 113: the recorder stores the reasoning trace", 16),
        ["round 113: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 113: the recorder stores the reasoning trace", 24),
        ["round 113: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 113: the recorder stores the reasoning trace", 32),
        ["round 113: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 113: the angel watches the processor run", 4),
        ["round", "113:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 113: the angel watches the processor run", 8),
        ["round", "113: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 113: the angel watches the processor run", 12),
        ["round 113:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 113: the angel watches the processor run", 16),
        ["round 113: the", "angel watches", "the processor", "run"],
    ),
    (("round 113: the angel watches the processor run", 24), ["round 113: the angel", "watches the processor", "run"]),
    (("round 113: the angel watches the processor run", 32), ["round 113: the angel watches the", "processor run"]),
    (
        ("round 113: angle of the vector decides the match", 4),
        ["round", "113:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 113: angle of the vector decides the match", 8),
        ["round", "113:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 113: angle of the vector decides the match", 12),
        ["round 113:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 113: angle of the vector decides the match", 16),
        ["round 113: angle", "of the vector", "decides the", "match"],
    ),
    (("round 113: angle of the vector decides the match", 24), ["round 113: angle of the", "vector decides the match"]),
    (("round 113: angle of the vector decides the match", 32), ["round 113: angle of the vector", "decides the match"]),
    (
        ("round 113: the candle burns twice as long at night", 4),
        ["round", "113:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 113: the candle burns twice as long at night", 8),
        ["round", "113: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 113: the candle burns twice as long at night", 12),
        ["round 113:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 113: the candle burns twice as long at night", 16),
        ["round 113: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 113: the candle burns twice as long at night", 24),
        ["round 113: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 113: the candle burns twice as long at night", 32),
        ["round 113: the candle burns", "twice as long at night"],
    ),
    (
        ("round 113: a mirror of the universe in one line", 4),
        ["round", "113:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 113: a mirror of the universe in one line", 8),
        ["round", "113: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 113: a mirror of the universe in one line", 12),
        ["round 113: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 113: a mirror of the universe in one line", 16),
        ["round 113: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 113: a mirror of the universe in one line", 24), ["round 113: a mirror of", "the universe in one line"]),
    (("round 113: a mirror of the universe in one line", 32), ["round 113: a mirror of the", "universe in one line"]),
    (
        ("round 113: the queue drains before the storm", 4),
        ["round", "113:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 113: the queue drains before the storm", 8),
        ["round", "113: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 113: the queue drains before the storm", 12),
        ["round 113:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 113: the queue drains before the storm", 16), ["round 113: the", "queue drains", "before the storm"]),
    (("round 113: the queue drains before the storm", 24), ["round 113: the queue", "drains before the storm"]),
    (("round 113: the queue drains before the storm", 32), ["round 113: the queue drains", "before the storm"]),
    (
        ("kitten113 sitting113 agent113 angle113 universe113 memory113", 6),
        ["kitten113", "sitting113", "agent113", "angle113", "universe113", "memory113"],
    ),
    (
        ("kitten113 sitting113 agent113 angle113 universe113 memory113", 10),
        ["kitten113", "sitting113", "agent113", "angle113", "universe113", "memory113"],
    ),
    (
        ("kitten113 sitting113 agent113 angle113 universe113 memory113", 18),
        ["kitten113", "sitting113", "agent113 angle113", "universe113", "memory113"],
    ),
    (
        ("kitten113 sitting113 agent113 angle113 universe113 memory113", 28),
        ["kitten113 sitting113", "agent113 angle113", "universe113 memory113"],
    ),
    (
        ("sitting113 agent113 angle113 universe113 memory113 stream113", 6),
        ["sitting113", "agent113", "angle113", "universe113", "memory113", "stream113"],
    ),
    (
        ("sitting113 agent113 angle113 universe113 memory113 stream113", 10),
        ["sitting113", "agent113", "angle113", "universe113", "memory113", "stream113"],
    ),
    (
        ("sitting113 agent113 angle113 universe113 memory113 stream113", 18),
        ["sitting113", "agent113 angle113", "universe113", "memory113", "stream113"],
    ),
    (
        ("sitting113 agent113 angle113 universe113 memory113 stream113", 28),
        ["sitting113 agent113 angle113", "universe113 memory113", "stream113"],
    ),
    (
        ("agent113 angle113 universe113 memory113 stream113 context113", 6),
        ["agent113", "angle113", "universe113", "memory113", "stream113", "context113"],
    ),
    (
        ("agent113 angle113 universe113 memory113 stream113 context113", 10),
        ["agent113", "angle113", "universe113", "memory113", "stream113", "context113"],
    ),
    (
        ("agent113 angle113 universe113 memory113 stream113 context113", 18),
        ["agent113 angle113", "universe113", "memory113", "stream113", "context113"],
    ),
    (
        ("agent113 angle113 universe113 memory113 stream113 context113", 28),
        ["agent113 angle113", "universe113 memory113", "stream113 context113"],
    ),
    (
        ("angle113 universe113 memory113 stream113 context113 knowledge113", 6),
        ["angle113", "universe113", "memory113", "stream113", "context113", "knowledge113"],
    ),
    (
        ("angle113 universe113 memory113 stream113 context113 knowledge113", 10),
        ["angle113", "universe113", "memory113", "stream113", "context113", "knowledge113"],
    ),
    (
        ("angle113 universe113 memory113 stream113 context113 knowledge113", 18),
        ["angle113", "universe113", "memory113", "stream113", "context113", "knowledge113"],
    ),
    (
        ("angle113 universe113 memory113 stream113 context113 knowledge113", 28),
        ["angle113 universe113", "memory113 stream113", "context113 knowledge113"],
    ),
    (
        ("universe113 memory113 stream113 context113 knowledge113 vector113", 6),
        ["universe113", "memory113", "stream113", "context113", "knowledge113", "vector113"],
    ),
    (
        ("universe113 memory113 stream113 context113 knowledge113 vector113", 10),
        ["universe113", "memory113", "stream113", "context113", "knowledge113", "vector113"],
    ),
    (
        ("universe113 memory113 stream113 context113 knowledge113 vector113", 18),
        ["universe113", "memory113", "stream113", "context113", "knowledge113", "vector113"],
    ),
    (
        ("universe113 memory113 stream113 context113 knowledge113 vector113", 28),
        ["universe113 memory113", "stream113 context113", "knowledge113 vector113"],
    ),
    (
        ("memory113 stream113 context113 knowledge113 vector113 processor113", 6),
        ["memory113", "stream113", "context113", "knowledge113", "vector113", "processor113"],
    ),
    (
        ("memory113 stream113 context113 knowledge113 vector113 processor113", 10),
        ["memory113", "stream113", "context113", "knowledge113", "vector113", "processor113"],
    ),
    (
        ("memory113 stream113 context113 knowledge113 vector113 processor113", 18),
        ["memory113", "stream113", "context113", "knowledge113", "vector113", "processor113"],
    ),
    (
        ("memory113 stream113 context113 knowledge113 vector113 processor113", 28),
        ["memory113 stream113", "context113 knowledge113", "vector113 processor113"],
    ),
    (
        ("stream113 context113 knowledge113 vector113 processor113 reasoning113", 6),
        ["stream113", "context113", "knowledge113", "vector113", "processor113", "reasoning113"],
    ),
    (
        ("stream113 context113 knowledge113 vector113 processor113 reasoning113", 10),
        ["stream113", "context113", "knowledge113", "vector113", "processor113", "reasoning113"],
    ),
    (
        ("stream113 context113 knowledge113 vector113 processor113 reasoning113", 18),
        ["stream113", "context113", "knowledge113", "vector113", "processor113", "reasoning113"],
    ),
    (
        ("stream113 context113 knowledge113 vector113 processor113 reasoning113", 28),
        ["stream113 context113", "knowledge113 vector113", "processor113 reasoning113"],
    ),
    (
        ("context113 knowledge113 vector113 processor113 reasoning113 machine113", 6),
        ["context113", "knowledge113", "vector113", "processor113", "reasoning113", "machine113"],
    ),
    (
        ("context113 knowledge113 vector113 processor113 reasoning113 machine113", 10),
        ["context113", "knowledge113", "vector113", "processor113", "reasoning113", "machine113"],
    ),
    (
        ("context113 knowledge113 vector113 processor113 reasoning113 machine113", 18),
        ["context113", "knowledge113", "vector113", "processor113", "reasoning113", "machine113"],
    ),
    (
        ("context113 knowledge113 vector113 processor113 reasoning113 machine113", 28),
        ["context113 knowledge113", "vector113 processor113", "reasoning113 machine113"],
    ),
    (
        ("knowledge113 vector113 processor113 reasoning113 machine113 learning113", 6),
        ["knowledge113", "vector113", "processor113", "reasoning113", "machine113", "learning113"],
    ),
    (
        ("knowledge113 vector113 processor113 reasoning113 machine113 learning113", 10),
        ["knowledge113", "vector113", "processor113", "reasoning113", "machine113", "learning113"],
    ),
    (
        ("knowledge113 vector113 processor113 reasoning113 machine113 learning113", 18),
        ["knowledge113", "vector113", "processor113", "reasoning113", "machine113", "learning113"],
    ),
    (
        ("knowledge113 vector113 processor113 reasoning113 machine113 learning113", 28),
        ["knowledge113 vector113", "processor113 reasoning113", "machine113 learning113"],
    ),
    (
        ("vector113 processor113 reasoning113 machine113 learning113 model113", 6),
        ["vector113", "processor113", "reasoning113", "machine113", "learning113", "model113"],
    ),
    (
        ("vector113 processor113 reasoning113 machine113 learning113 model113", 10),
        ["vector113", "processor113", "reasoning113", "machine113", "learning113", "model113"],
    ),
    (
        ("vector113 processor113 reasoning113 machine113 learning113 model113", 18),
        ["vector113", "processor113", "reasoning113", "machine113", "learning113", "model113"],
    ),
    (
        ("vector113 processor113 reasoning113 machine113 learning113 model113", 28),
        ["vector113 processor113", "reasoning113 machine113", "learning113 model113"],
    ),
    (
        ("processor113 reasoning113 machine113 learning113 model113 token113", 6),
        ["processor113", "reasoning113", "machine113", "learning113", "model113", "token113"],
    ),
    (
        ("processor113 reasoning113 machine113 learning113 model113 token113", 10),
        ["processor113", "reasoning113", "machine113", "learning113", "model113", "token113"],
    ),
    (
        ("processor113 reasoning113 machine113 learning113 model113 token113", 18),
        ["processor113", "reasoning113", "machine113", "learning113", "model113 token113"],
    ),
    (
        ("processor113 reasoning113 machine113 learning113 model113 token113", 28),
        ["processor113 reasoning113", "machine113 learning113", "model113 token113"],
    ),
    (
        ("reasoning113 machine113 learning113 model113 token113 prompt113", 6),
        ["reasoning113", "machine113", "learning113", "model113", "token113", "prompt113"],
    ),
    (
        ("reasoning113 machine113 learning113 model113 token113 prompt113", 10),
        ["reasoning113", "machine113", "learning113", "model113", "token113", "prompt113"],
    ),
    (
        ("reasoning113 machine113 learning113 model113 token113 prompt113", 18),
        ["reasoning113", "machine113", "learning113", "model113 token113", "prompt113"],
    ),
    (
        ("reasoning113 machine113 learning113 model113 token113 prompt113", 28),
        ["reasoning113 machine113", "learning113 model113", "token113 prompt113"],
    ),
    (
        ("machine113 learning113 model113 token113 prompt113 session113", 6),
        ["machine113", "learning113", "model113", "token113", "prompt113", "session113"],
    ),
    (
        ("machine113 learning113 model113 token113 prompt113 session113", 10),
        ["machine113", "learning113", "model113", "token113", "prompt113", "session113"],
    ),
    (
        ("machine113 learning113 model113 token113 prompt113 session113", 18),
        ["machine113", "learning113", "model113 token113", "prompt113", "session113"],
    ),
    (
        ("machine113 learning113 model113 token113 prompt113 session113", 28),
        ["machine113 learning113", "model113 token113 prompt113", "session113"],
    ),
    (
        ("learning113 model113 token113 prompt113 session113 library113", 6),
        ["learning113", "model113", "token113", "prompt113", "session113", "library113"],
    ),
    (
        ("learning113 model113 token113 prompt113 session113 library113", 10),
        ["learning113", "model113", "token113", "prompt113", "session113", "library113"],
    ),
    (
        ("learning113 model113 token113 prompt113 session113 library113", 18),
        ["learning113", "model113 token113", "prompt113", "session113", "library113"],
    ),
    (
        ("learning113 model113 token113 prompt113 session113 library113", 28),
        ["learning113 model113", "token113 prompt113", "session113 library113"],
    ),
    (
        ("model113 token113 prompt113 session113 library113 service113", 6),
        ["model113", "token113", "prompt113", "session113", "library113", "service113"],
    ),
    (
        ("model113 token113 prompt113 session113 library113 service113", 10),
        ["model113", "token113", "prompt113", "session113", "library113", "service113"],
    ),
    (
        ("model113 token113 prompt113 session113 library113 service113", 18),
        ["model113 token113", "prompt113", "session113", "library113", "service113"],
    ),
    (
        ("model113 token113 prompt113 session113 library113 service113", 28),
        ["model113 token113 prompt113", "session113 library113", "service113"],
    ),
    (
        ("token113 prompt113 session113 library113 service113 gateway113", 6),
        ["token113", "prompt113", "session113", "library113", "service113", "gateway113"],
    ),
    (
        ("token113 prompt113 session113 library113 service113 gateway113", 10),
        ["token113", "prompt113", "session113", "library113", "service113", "gateway113"],
    ),
    (
        ("token113 prompt113 session113 library113 service113 gateway113", 18),
        ["token113 prompt113", "session113", "library113", "service113", "gateway113"],
    ),
    (
        ("token113 prompt113 session113 library113 service113 gateway113", 28),
        ["token113 prompt113", "session113 library113", "service113 gateway113"],
    ),
    (
        ("prompt113 session113 library113 service113 gateway113 storage113", 6),
        ["prompt113", "session113", "library113", "service113", "gateway113", "storage113"],
    ),
    (
        ("prompt113 session113 library113 service113 gateway113 storage113", 10),
        ["prompt113", "session113", "library113", "service113", "gateway113", "storage113"],
    ),
    (
        ("prompt113 session113 library113 service113 gateway113 storage113", 18),
        ["prompt113", "session113", "library113", "service113", "gateway113", "storage113"],
    ),
    (
        ("prompt113 session113 library113 service113 gateway113 storage113", 28),
        ["prompt113 session113", "library113 service113", "gateway113 storage113"],
    ),
    (
        ("session113 library113 service113 gateway113 storage113 network113", 6),
        ["session113", "library113", "service113", "gateway113", "storage113", "network113"],
    ),
    (
        ("session113 library113 service113 gateway113 storage113 network113", 10),
        ["session113", "library113", "service113", "gateway113", "storage113", "network113"],
    ),
    (
        ("session113 library113 service113 gateway113 storage113 network113", 18),
        ["session113", "library113", "service113", "gateway113", "storage113", "network113"],
    ),
    (
        ("session113 library113 service113 gateway113 storage113 network113", 28),
        ["session113 library113", "service113 gateway113", "storage113 network113"],
    ),
    (
        ("library113 service113 gateway113 storage113 network113 latency113", 6),
        ["library113", "service113", "gateway113", "storage113", "network113", "latency113"],
    ),
    (
        ("library113 service113 gateway113 storage113 network113 latency113", 10),
        ["library113", "service113", "gateway113", "storage113", "network113", "latency113"],
    ),
    (
        ("library113 service113 gateway113 storage113 network113 latency113", 18),
        ["library113", "service113", "gateway113", "storage113", "network113", "latency113"],
    ),
    (
        ("library113 service113 gateway113 storage113 network113 latency113", 28),
        ["library113 service113", "gateway113 storage113", "network113 latency113"],
    ),
    (
        ("service113 gateway113 storage113 network113 latency113 buffer113", 6),
        ["service113", "gateway113", "storage113", "network113", "latency113", "buffer113"],
    ),
    (
        ("service113 gateway113 storage113 network113 latency113 buffer113", 10),
        ["service113", "gateway113", "storage113", "network113", "latency113", "buffer113"],
    ),
    (
        ("service113 gateway113 storage113 network113 latency113 buffer113", 18),
        ["service113", "gateway113", "storage113", "network113", "latency113", "buffer113"],
    ),
    (
        ("service113 gateway113 storage113 network113 latency113 buffer113", 28),
        ["service113 gateway113", "storage113 network113", "latency113 buffer113"],
    ),
    (
        ("gateway113 storage113 network113 latency113 buffer113 queue113", 6),
        ["gateway113", "storage113", "network113", "latency113", "buffer113", "queue113"],
    ),
    (
        ("gateway113 storage113 network113 latency113 buffer113 queue113", 10),
        ["gateway113", "storage113", "network113", "latency113", "buffer113", "queue113"],
    ),
    (
        ("gateway113 storage113 network113 latency113 buffer113 queue113", 18),
        ["gateway113", "storage113", "network113", "latency113", "buffer113 queue113"],
    ),
    (
        ("gateway113 storage113 network113 latency113 buffer113 queue113", 28),
        ["gateway113 storage113", "network113 latency113", "buffer113 queue113"],
    ),
    (
        ("storage113 network113 latency113 buffer113 queue113 worker113", 6),
        ["storage113", "network113", "latency113", "buffer113", "queue113", "worker113"],
    ),
    (
        ("storage113 network113 latency113 buffer113 queue113 worker113", 10),
        ["storage113", "network113", "latency113", "buffer113", "queue113", "worker113"],
    ),
    (
        ("storage113 network113 latency113 buffer113 queue113 worker113", 18),
        ["storage113", "network113", "latency113", "buffer113 queue113", "worker113"],
    ),
    (
        ("storage113 network113 latency113 buffer113 queue113 worker113", 28),
        ["storage113 network113", "latency113 buffer113", "queue113 worker113"],
    ),
    (
        ("network113 latency113 buffer113 queue113 worker113 kernel113", 6),
        ["network113", "latency113", "buffer113", "queue113", "worker113", "kernel113"],
    ),
    (
        ("network113 latency113 buffer113 queue113 worker113 kernel113", 10),
        ["network113", "latency113", "buffer113", "queue113", "worker113", "kernel113"],
    ),
    (
        ("network113 latency113 buffer113 queue113 worker113 kernel113", 18),
        ["network113", "latency113", "buffer113 queue113", "worker113", "kernel113"],
    ),
    (
        ("network113 latency113 buffer113 queue113 worker113 kernel113", 28),
        ["network113 latency113", "buffer113 queue113 worker113", "kernel113"],
    ),
    (
        ("latency113 buffer113 queue113 worker113 kernel113 signal113", 6),
        ["latency113", "buffer113", "queue113", "worker113", "kernel113", "signal113"],
    ),
    (
        ("latency113 buffer113 queue113 worker113 kernel113 signal113", 10),
        ["latency113", "buffer113", "queue113", "worker113", "kernel113", "signal113"],
    ),
    (
        ("latency113 buffer113 queue113 worker113 kernel113 signal113", 18),
        ["latency113", "buffer113 queue113", "worker113", "kernel113", "signal113"],
    ),
    (
        ("latency113 buffer113 queue113 worker113 kernel113 signal113", 28),
        ["latency113 buffer113", "queue113 worker113 kernel113", "signal113"],
    ),
    (
        ("buffer113 queue113 worker113 kernel113 signal113 packet113", 6),
        ["buffer113", "queue113", "worker113", "kernel113", "signal113", "packet113"],
    ),
    (
        ("buffer113 queue113 worker113 kernel113 signal113 packet113", 10),
        ["buffer113", "queue113", "worker113", "kernel113", "signal113", "packet113"],
    ),
    (
        ("buffer113 queue113 worker113 kernel113 signal113 packet113", 18),
        ["buffer113 queue113", "worker113", "kernel113", "signal113", "packet113"],
    ),
    (
        ("buffer113 queue113 worker113 kernel113 signal113 packet113", 28),
        ["buffer113 queue113 worker113", "kernel113 signal113", "packet113"],
    ),
    (
        ("queue113 worker113 kernel113 signal113 packet113 router113", 6),
        ["queue113", "worker113", "kernel113", "signal113", "packet113", "router113"],
    ),
    (
        ("queue113 worker113 kernel113 signal113 packet113 router113", 10),
        ["queue113", "worker113", "kernel113", "signal113", "packet113", "router113"],
    ),
    (
        ("queue113 worker113 kernel113 signal113 packet113 router113", 18),
        ["queue113 worker113", "kernel113", "signal113", "packet113", "router113"],
    ),
    (
        ("queue113 worker113 kernel113 signal113 packet113 router113", 28),
        ["queue113 worker113 kernel113", "signal113 packet113", "router113"],
    ),
    (
        ("worker113 kernel113 signal113 packet113 router113 cluster113", 6),
        ["worker113", "kernel113", "signal113", "packet113", "router113", "cluster113"],
    ),
    (
        ("worker113 kernel113 signal113 packet113 router113 cluster113", 10),
        ["worker113", "kernel113", "signal113", "packet113", "router113", "cluster113"],
    ),
    (
        ("worker113 kernel113 signal113 packet113 router113 cluster113", 18),
        ["worker113", "kernel113", "signal113", "packet113", "router113", "cluster113"],
    ),
    (
        ("worker113 kernel113 signal113 packet113 router113 cluster113", 28),
        ["worker113 kernel113", "signal113 packet113", "router113 cluster113"],
    ),
    (
        ("kernel113 signal113 packet113 router113 cluster113 mirror113", 6),
        ["kernel113", "signal113", "packet113", "router113", "cluster113", "mirror113"],
    ),
    (
        ("kernel113 signal113 packet113 router113 cluster113 mirror113", 10),
        ["kernel113", "signal113", "packet113", "router113", "cluster113", "mirror113"],
    ),
    (
        ("kernel113 signal113 packet113 router113 cluster113 mirror113", 18),
        ["kernel113", "signal113", "packet113", "router113", "cluster113", "mirror113"],
    ),
    (
        ("kernel113 signal113 packet113 router113 cluster113 mirror113", 28),
        ["kernel113 signal113", "packet113 router113", "cluster113 mirror113"],
    ),
    (
        ("signal113 packet113 router113 cluster113 mirror113 filter113", 6),
        ["signal113", "packet113", "router113", "cluster113", "mirror113", "filter113"],
    ),
    (
        ("signal113 packet113 router113 cluster113 mirror113 filter113", 10),
        ["signal113", "packet113", "router113", "cluster113", "mirror113", "filter113"],
    ),
    (
        ("signal113 packet113 router113 cluster113 mirror113 filter113", 18),
        ["signal113", "packet113", "router113", "cluster113", "mirror113", "filter113"],
    ),
    (
        ("signal113 packet113 router113 cluster113 mirror113 filter113", 28),
        ["signal113 packet113", "router113 cluster113", "mirror113 filter113"],
    ),
    (
        ("packet113 router113 cluster113 mirror113 filter113 ranking113", 6),
        ["packet113", "router113", "cluster113", "mirror113", "filter113", "ranking113"],
    ),
    (
        ("packet113 router113 cluster113 mirror113 filter113 ranking113", 10),
        ["packet113", "router113", "cluster113", "mirror113", "filter113", "ranking113"],
    ),
    (
        ("packet113 router113 cluster113 mirror113 filter113 ranking113", 18),
        ["packet113", "router113", "cluster113", "mirror113", "filter113", "ranking113"],
    ),
    (
        ("packet113 router113 cluster113 mirror113 filter113 ranking113", 28),
        ["packet113 router113", "cluster113 mirror113", "filter113 ranking113"],
    ),
    (
        ("router113 cluster113 mirror113 filter113 ranking113 encoding113", 6),
        ["router113", "cluster113", "mirror113", "filter113", "ranking113", "encoding113"],
    ),
    (
        ("router113 cluster113 mirror113 filter113 ranking113 encoding113", 10),
        ["router113", "cluster113", "mirror113", "filter113", "ranking113", "encoding113"],
    ),
    (
        ("router113 cluster113 mirror113 filter113 ranking113 encoding113", 18),
        ["router113", "cluster113", "mirror113", "filter113", "ranking113", "encoding113"],
    ),
    (
        ("router113 cluster113 mirror113 filter113 ranking113 encoding113", 28),
        ["router113 cluster113", "mirror113 filter113", "ranking113 encoding113"],
    ),
    (
        ("cluster113 mirror113 filter113 ranking113 encoding113 mapping113", 6),
        ["cluster113", "mirror113", "filter113", "ranking113", "encoding113", "mapping113"],
    ),
    (
        ("cluster113 mirror113 filter113 ranking113 encoding113 mapping113", 10),
        ["cluster113", "mirror113", "filter113", "ranking113", "encoding113", "mapping113"],
    ),
    (
        ("cluster113 mirror113 filter113 ranking113 encoding113 mapping113", 18),
        ["cluster113", "mirror113", "filter113", "ranking113", "encoding113", "mapping113"],
    ),
    (
        ("cluster113 mirror113 filter113 ranking113 encoding113 mapping113", 28),
        ["cluster113 mirror113", "filter113 ranking113", "encoding113 mapping113"],
    ),
    (
        ("mirror113 filter113 ranking113 encoding113 mapping113 record113", 6),
        ["mirror113", "filter113", "ranking113", "encoding113", "mapping113", "record113"],
    ),
    (
        ("mirror113 filter113 ranking113 encoding113 mapping113 record113", 10),
        ["mirror113", "filter113", "ranking113", "encoding113", "mapping113", "record113"],
    ),
    (
        ("mirror113 filter113 ranking113 encoding113 mapping113 record113", 18),
        ["mirror113", "filter113", "ranking113", "encoding113", "mapping113", "record113"],
    ),
    (
        ("mirror113 filter113 ranking113 encoding113 mapping113 record113", 28),
        ["mirror113 filter113", "ranking113 encoding113", "mapping113 record113"],
    ),
    (
        ("filter113 ranking113 encoding113 mapping113 record113 candle113", 6),
        ["filter113", "ranking113", "encoding113", "mapping113", "record113", "candle113"],
    ),
    (
        ("filter113 ranking113 encoding113 mapping113 record113 candle113", 10),
        ["filter113", "ranking113", "encoding113", "mapping113", "record113", "candle113"],
    ),
    (
        ("filter113 ranking113 encoding113 mapping113 record113 candle113", 18),
        ["filter113", "ranking113", "encoding113", "mapping113", "record113", "candle113"],
    ),
    (
        ("filter113 ranking113 encoding113 mapping113 record113 candle113", 28),
        ["filter113 ranking113", "encoding113 mapping113", "record113 candle113"],
    ),
    (
        ("ranking113 encoding113 mapping113 record113 candle113 thread113", 6),
        ["ranking113", "encoding113", "mapping113", "record113", "candle113", "thread113"],
    ),
    (
        ("ranking113 encoding113 mapping113 record113 candle113 thread113", 10),
        ["ranking113", "encoding113", "mapping113", "record113", "candle113", "thread113"],
    ),
    (
        ("ranking113 encoding113 mapping113 record113 candle113 thread113", 18),
        ["ranking113", "encoding113", "mapping113", "record113", "candle113", "thread113"],
    ),
    (
        ("ranking113 encoding113 mapping113 record113 candle113 thread113", 28),
        ["ranking113 encoding113", "mapping113 record113", "candle113 thread113"],
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
