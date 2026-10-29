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
        ("round 107: the quick brown fox jumps over the lazy dog", 4),
        ["round", "107:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", 8),
        ["round", "107: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", 12),
        ["round 107:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", 16),
        ["round 107: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", 24),
        ["round 107: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 107: the quick brown fox jumps over the lazy dog", 32),
        ["round 107: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", 4),
        ["round", "107:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", 8),
        ["round", "107:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", 12),
        ["round 107:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", 16),
        ["round 107:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", 24),
        ["round 107: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 107: agentuniverse is a framework for multi agents", 32),
        ["round 107: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", 4),
        ["round", "107:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", 8),
        ["round", "107:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", 12),
        ["round 107:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", 16),
        ["round 107:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", 24),
        ["round 107: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 107: knowledge stored as vectors enables retrieval", 32),
        ["round 107: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 107: the processor reads the record then stops", 4),
        ["round", "107:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 107: the processor reads the record then stops", 8),
        ["round", "107: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 107: the processor reads the record then stops", 12),
        ["round 107:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 107: the processor reads the record then stops", 16),
        ["round 107: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 107: the processor reads the record then stops", 24),
        ["round 107: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 107: the processor reads the record then stops", 32),
        ["round 107: the processor reads", "the record then stops"],
    ),
    (
        ("round 107: a worker pulls the next task from the queue", 4),
        ["round", "107:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 107: a worker pulls the next task from the queue", 8),
        ["round", "107: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 107: a worker pulls the next task from the queue", 12),
        ["round 107: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 107: a worker pulls the next task from the queue", 16),
        ["round 107: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 107: a worker pulls the next task from the queue", 24),
        ["round 107: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 107: a worker pulls the next task from the queue", 32),
        ["round 107: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 107: signals travel through the network layer", 4),
        ["round", "107:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 107: signals travel through the network layer", 8),
        ["round", "107:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 107: signals travel through the network layer", 12),
        ["round 107:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 107: signals travel through the network layer", 16),
        ["round 107:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 107: signals travel through the network layer", 24),
        ["round 107: signals", "travel through the", "network layer"],
    ),
    (
        ("round 107: signals travel through the network layer", 32),
        ["round 107: signals travel", "through the network layer"],
    ),
    (
        ("round 107: the gateway routes each request by policy", 4),
        ["round", "107:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 107: the gateway routes each request by policy", 8),
        ["round", "107: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 107: the gateway routes each request by policy", 12),
        ["round 107:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 107: the gateway routes each request by policy", 16),
        ["round 107: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 107: the gateway routes each request by policy", 24),
        ["round 107: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 107: the gateway routes each request by policy", 32),
        ["round 107: the gateway routes", "each request by policy"],
    ),
    (
        ("round 107: memory grows until the buffer is full", 4),
        ["round", "107:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 107: memory grows until the buffer is full", 8),
        ["round", "107:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 107: memory grows until the buffer is full", 12),
        ["round 107:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 107: memory grows until the buffer is full", 16),
        ["round 107:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 107: memory grows until the buffer is full", 24), ["round 107: memory grows", "until the buffer is full"]),
    (("round 107: memory grows until the buffer is full", 32), ["round 107: memory grows until", "the buffer is full"]),
    (
        ("round 107: the cluster mirrors every packet twice", 4),
        ["round", "107:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 107: the cluster mirrors every packet twice", 8),
        ["round", "107: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 107: the cluster mirrors every packet twice", 12),
        ["round 107:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 107: the cluster mirrors every packet twice", 16),
        ["round 107: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 107: the cluster mirrors every packet twice", 24),
        ["round 107: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 107: the cluster mirrors every packet twice", 32),
        ["round 107: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", 4),
        ["round", "107:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", 8),
        ["round", "107:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", 12),
        ["round 107:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", 16),
        ["round 107:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", 24),
        ["round 107: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 107: ranking uses tokens learned from the corpus", 32),
        ["round 107: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 107: a long session ends when the candle dies", 4),
        ["round", "107:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 107: a long session ends when the candle dies", 8),
        ["round", "107: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 107: a long session ends when the candle dies", 12),
        ["round 107: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 107: a long session ends when the candle dies", 16),
        ["round 107: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 107: a long session ends when the candle dies", 24),
        ["round 107: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 107: a long session ends when the candle dies", 32),
        ["round 107: a long session ends", "when the candle dies"],
    ),
    (
        ("round 107: encode the prompt then map the result", 4),
        ["round", "107:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 107: encode the prompt then map the result", 8),
        ["round", "107:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 107: encode the prompt then map the result", 12),
        ["round 107:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 107: encode the prompt then map the result", 16),
        ["round 107:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 107: encode the prompt then map the result", 24),
        ["round 107: encode the", "prompt then map the", "result"],
    ),
    (("round 107: encode the prompt then map the result", 32), ["round 107: encode the prompt", "then map the result"]),
    (
        ("round 107: the kernel wakes the worker at dawn", 4),
        ["round", "107:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 107: the kernel wakes the worker at dawn", 8),
        ["round", "107: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 107: the kernel wakes the worker at dawn", 12),
        ["round 107:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 107: the kernel wakes the worker at dawn", 16), ["round 107: the", "kernel wakes the", "worker at dawn"]),
    (("round 107: the kernel wakes the worker at dawn", 24), ["round 107: the kernel", "wakes the worker at dawn"]),
    (("round 107: the kernel wakes the worker at dawn", 32), ["round 107: the kernel wakes the", "worker at dawn"]),
    (
        ("round 107: service latency drops after the patch", 4),
        ["round", "107:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 107: service latency drops after the patch", 8),
        ["round", "107:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 107: service latency drops after the patch", 12),
        ["round 107:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 107: service latency drops after the patch", 16),
        ["round 107:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 107: service latency drops after the patch", 24),
        ["round 107: service", "latency drops after the", "patch"],
    ),
    (("round 107: service latency drops after the patch", 32), ["round 107: service latency drops", "after the patch"]),
    (
        ("round 107: the library caches every vector it sees", 4),
        ["round", "107:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 107: the library caches every vector it sees", 8),
        ["round", "107: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 107: the library caches every vector it sees", 12),
        ["round 107:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 107: the library caches every vector it sees", 16),
        ["round 107: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 107: the library caches every vector it sees", 24),
        ["round 107: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 107: the library caches every vector it sees", 32),
        ["round 107: the library caches", "every vector it sees"],
    ),
    (
        ("round 107: agents argue then the debate resolves", 4),
        ["round", "107:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 107: agents argue then the debate resolves", 8),
        ["round", "107:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 107: agents argue then the debate resolves", 12),
        ["round 107:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 107: agents argue then the debate resolves", 16),
        ["round 107:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 107: agents argue then the debate resolves", 24), ["round 107: agents argue", "then the debate resolves"]),
    (("round 107: agents argue then the debate resolves", 32), ["round 107: agents argue then the", "debate resolves"]),
    (
        ("round 107: the filter keeps only strong matches", 4),
        ["round", "107:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 107: the filter keeps only strong matches", 8),
        ["round", "107: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 107: the filter keeps only strong matches", 12),
        ["round 107:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 107: the filter keeps only strong matches", 16),
        ["round 107: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 107: the filter keeps only strong matches", 24),
        ["round 107: the filter", "keeps only strong", "matches"],
    ),
    (("round 107: the filter keeps only strong matches", 32), ["round 107: the filter keeps only", "strong matches"]),
    (
        ("round 107: the model answers with a short reply", 4),
        ["round", "107:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 107: the model answers with a short reply", 8),
        ["round", "107: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 107: the model answers with a short reply", 12),
        ["round 107:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 107: the model answers with a short reply", 16),
        ["round 107: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 107: the model answers with a short reply", 24),
        ["round 107: the model", "answers with a short", "reply"],
    ),
    (("round 107: the model answers with a short reply", 32), ["round 107: the model answers", "with a short reply"]),
    (
        ("round 107: the recorder stores the reasoning trace", 4),
        ["round", "107:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 107: the recorder stores the reasoning trace", 8),
        ["round", "107: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 107: the recorder stores the reasoning trace", 12),
        ["round 107:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 107: the recorder stores the reasoning trace", 16),
        ["round 107: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 107: the recorder stores the reasoning trace", 24),
        ["round 107: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 107: the recorder stores the reasoning trace", 32),
        ["round 107: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 107: the angel watches the processor run", 4),
        ["round", "107:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 107: the angel watches the processor run", 8),
        ["round", "107: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 107: the angel watches the processor run", 12),
        ["round 107:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 107: the angel watches the processor run", 16),
        ["round 107: the", "angel watches", "the processor", "run"],
    ),
    (("round 107: the angel watches the processor run", 24), ["round 107: the angel", "watches the processor", "run"]),
    (("round 107: the angel watches the processor run", 32), ["round 107: the angel watches the", "processor run"]),
    (
        ("round 107: angle of the vector decides the match", 4),
        ["round", "107:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 107: angle of the vector decides the match", 8),
        ["round", "107:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 107: angle of the vector decides the match", 12),
        ["round 107:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 107: angle of the vector decides the match", 16),
        ["round 107: angle", "of the vector", "decides the", "match"],
    ),
    (("round 107: angle of the vector decides the match", 24), ["round 107: angle of the", "vector decides the match"]),
    (("round 107: angle of the vector decides the match", 32), ["round 107: angle of the vector", "decides the match"]),
    (
        ("round 107: the candle burns twice as long at night", 4),
        ["round", "107:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 107: the candle burns twice as long at night", 8),
        ["round", "107: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 107: the candle burns twice as long at night", 12),
        ["round 107:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 107: the candle burns twice as long at night", 16),
        ["round 107: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 107: the candle burns twice as long at night", 24),
        ["round 107: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 107: the candle burns twice as long at night", 32),
        ["round 107: the candle burns", "twice as long at night"],
    ),
    (
        ("round 107: a mirror of the universe in one line", 4),
        ["round", "107:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 107: a mirror of the universe in one line", 8),
        ["round", "107: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 107: a mirror of the universe in one line", 12),
        ["round 107: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 107: a mirror of the universe in one line", 16),
        ["round 107: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 107: a mirror of the universe in one line", 24), ["round 107: a mirror of", "the universe in one line"]),
    (("round 107: a mirror of the universe in one line", 32), ["round 107: a mirror of the", "universe in one line"]),
    (
        ("round 107: the queue drains before the storm", 4),
        ["round", "107:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 107: the queue drains before the storm", 8),
        ["round", "107: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 107: the queue drains before the storm", 12),
        ["round 107:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 107: the queue drains before the storm", 16), ["round 107: the", "queue drains", "before the storm"]),
    (("round 107: the queue drains before the storm", 24), ["round 107: the queue", "drains before the storm"]),
    (("round 107: the queue drains before the storm", 32), ["round 107: the queue drains", "before the storm"]),
    (
        ("kitten107 sitting107 agent107 angle107 universe107 memory107", 6),
        ["kitten107", "sitting107", "agent107", "angle107", "universe107", "memory107"],
    ),
    (
        ("kitten107 sitting107 agent107 angle107 universe107 memory107", 10),
        ["kitten107", "sitting107", "agent107", "angle107", "universe107", "memory107"],
    ),
    (
        ("kitten107 sitting107 agent107 angle107 universe107 memory107", 18),
        ["kitten107", "sitting107", "agent107 angle107", "universe107", "memory107"],
    ),
    (
        ("kitten107 sitting107 agent107 angle107 universe107 memory107", 28),
        ["kitten107 sitting107", "agent107 angle107", "universe107 memory107"],
    ),
    (
        ("sitting107 agent107 angle107 universe107 memory107 stream107", 6),
        ["sitting107", "agent107", "angle107", "universe107", "memory107", "stream107"],
    ),
    (
        ("sitting107 agent107 angle107 universe107 memory107 stream107", 10),
        ["sitting107", "agent107", "angle107", "universe107", "memory107", "stream107"],
    ),
    (
        ("sitting107 agent107 angle107 universe107 memory107 stream107", 18),
        ["sitting107", "agent107 angle107", "universe107", "memory107", "stream107"],
    ),
    (
        ("sitting107 agent107 angle107 universe107 memory107 stream107", 28),
        ["sitting107 agent107 angle107", "universe107 memory107", "stream107"],
    ),
    (
        ("agent107 angle107 universe107 memory107 stream107 context107", 6),
        ["agent107", "angle107", "universe107", "memory107", "stream107", "context107"],
    ),
    (
        ("agent107 angle107 universe107 memory107 stream107 context107", 10),
        ["agent107", "angle107", "universe107", "memory107", "stream107", "context107"],
    ),
    (
        ("agent107 angle107 universe107 memory107 stream107 context107", 18),
        ["agent107 angle107", "universe107", "memory107", "stream107", "context107"],
    ),
    (
        ("agent107 angle107 universe107 memory107 stream107 context107", 28),
        ["agent107 angle107", "universe107 memory107", "stream107 context107"],
    ),
    (
        ("angle107 universe107 memory107 stream107 context107 knowledge107", 6),
        ["angle107", "universe107", "memory107", "stream107", "context107", "knowledge107"],
    ),
    (
        ("angle107 universe107 memory107 stream107 context107 knowledge107", 10),
        ["angle107", "universe107", "memory107", "stream107", "context107", "knowledge107"],
    ),
    (
        ("angle107 universe107 memory107 stream107 context107 knowledge107", 18),
        ["angle107", "universe107", "memory107", "stream107", "context107", "knowledge107"],
    ),
    (
        ("angle107 universe107 memory107 stream107 context107 knowledge107", 28),
        ["angle107 universe107", "memory107 stream107", "context107 knowledge107"],
    ),
    (
        ("universe107 memory107 stream107 context107 knowledge107 vector107", 6),
        ["universe107", "memory107", "stream107", "context107", "knowledge107", "vector107"],
    ),
    (
        ("universe107 memory107 stream107 context107 knowledge107 vector107", 10),
        ["universe107", "memory107", "stream107", "context107", "knowledge107", "vector107"],
    ),
    (
        ("universe107 memory107 stream107 context107 knowledge107 vector107", 18),
        ["universe107", "memory107", "stream107", "context107", "knowledge107", "vector107"],
    ),
    (
        ("universe107 memory107 stream107 context107 knowledge107 vector107", 28),
        ["universe107 memory107", "stream107 context107", "knowledge107 vector107"],
    ),
    (
        ("memory107 stream107 context107 knowledge107 vector107 processor107", 6),
        ["memory107", "stream107", "context107", "knowledge107", "vector107", "processor107"],
    ),
    (
        ("memory107 stream107 context107 knowledge107 vector107 processor107", 10),
        ["memory107", "stream107", "context107", "knowledge107", "vector107", "processor107"],
    ),
    (
        ("memory107 stream107 context107 knowledge107 vector107 processor107", 18),
        ["memory107", "stream107", "context107", "knowledge107", "vector107", "processor107"],
    ),
    (
        ("memory107 stream107 context107 knowledge107 vector107 processor107", 28),
        ["memory107 stream107", "context107 knowledge107", "vector107 processor107"],
    ),
    (
        ("stream107 context107 knowledge107 vector107 processor107 reasoning107", 6),
        ["stream107", "context107", "knowledge107", "vector107", "processor107", "reasoning107"],
    ),
    (
        ("stream107 context107 knowledge107 vector107 processor107 reasoning107", 10),
        ["stream107", "context107", "knowledge107", "vector107", "processor107", "reasoning107"],
    ),
    (
        ("stream107 context107 knowledge107 vector107 processor107 reasoning107", 18),
        ["stream107", "context107", "knowledge107", "vector107", "processor107", "reasoning107"],
    ),
    (
        ("stream107 context107 knowledge107 vector107 processor107 reasoning107", 28),
        ["stream107 context107", "knowledge107 vector107", "processor107 reasoning107"],
    ),
    (
        ("context107 knowledge107 vector107 processor107 reasoning107 machine107", 6),
        ["context107", "knowledge107", "vector107", "processor107", "reasoning107", "machine107"],
    ),
    (
        ("context107 knowledge107 vector107 processor107 reasoning107 machine107", 10),
        ["context107", "knowledge107", "vector107", "processor107", "reasoning107", "machine107"],
    ),
    (
        ("context107 knowledge107 vector107 processor107 reasoning107 machine107", 18),
        ["context107", "knowledge107", "vector107", "processor107", "reasoning107", "machine107"],
    ),
    (
        ("context107 knowledge107 vector107 processor107 reasoning107 machine107", 28),
        ["context107 knowledge107", "vector107 processor107", "reasoning107 machine107"],
    ),
    (
        ("knowledge107 vector107 processor107 reasoning107 machine107 learning107", 6),
        ["knowledge107", "vector107", "processor107", "reasoning107", "machine107", "learning107"],
    ),
    (
        ("knowledge107 vector107 processor107 reasoning107 machine107 learning107", 10),
        ["knowledge107", "vector107", "processor107", "reasoning107", "machine107", "learning107"],
    ),
    (
        ("knowledge107 vector107 processor107 reasoning107 machine107 learning107", 18),
        ["knowledge107", "vector107", "processor107", "reasoning107", "machine107", "learning107"],
    ),
    (
        ("knowledge107 vector107 processor107 reasoning107 machine107 learning107", 28),
        ["knowledge107 vector107", "processor107 reasoning107", "machine107 learning107"],
    ),
    (
        ("vector107 processor107 reasoning107 machine107 learning107 model107", 6),
        ["vector107", "processor107", "reasoning107", "machine107", "learning107", "model107"],
    ),
    (
        ("vector107 processor107 reasoning107 machine107 learning107 model107", 10),
        ["vector107", "processor107", "reasoning107", "machine107", "learning107", "model107"],
    ),
    (
        ("vector107 processor107 reasoning107 machine107 learning107 model107", 18),
        ["vector107", "processor107", "reasoning107", "machine107", "learning107", "model107"],
    ),
    (
        ("vector107 processor107 reasoning107 machine107 learning107 model107", 28),
        ["vector107 processor107", "reasoning107 machine107", "learning107 model107"],
    ),
    (
        ("processor107 reasoning107 machine107 learning107 model107 token107", 6),
        ["processor107", "reasoning107", "machine107", "learning107", "model107", "token107"],
    ),
    (
        ("processor107 reasoning107 machine107 learning107 model107 token107", 10),
        ["processor107", "reasoning107", "machine107", "learning107", "model107", "token107"],
    ),
    (
        ("processor107 reasoning107 machine107 learning107 model107 token107", 18),
        ["processor107", "reasoning107", "machine107", "learning107", "model107 token107"],
    ),
    (
        ("processor107 reasoning107 machine107 learning107 model107 token107", 28),
        ["processor107 reasoning107", "machine107 learning107", "model107 token107"],
    ),
    (
        ("reasoning107 machine107 learning107 model107 token107 prompt107", 6),
        ["reasoning107", "machine107", "learning107", "model107", "token107", "prompt107"],
    ),
    (
        ("reasoning107 machine107 learning107 model107 token107 prompt107", 10),
        ["reasoning107", "machine107", "learning107", "model107", "token107", "prompt107"],
    ),
    (
        ("reasoning107 machine107 learning107 model107 token107 prompt107", 18),
        ["reasoning107", "machine107", "learning107", "model107 token107", "prompt107"],
    ),
    (
        ("reasoning107 machine107 learning107 model107 token107 prompt107", 28),
        ["reasoning107 machine107", "learning107 model107", "token107 prompt107"],
    ),
    (
        ("machine107 learning107 model107 token107 prompt107 session107", 6),
        ["machine107", "learning107", "model107", "token107", "prompt107", "session107"],
    ),
    (
        ("machine107 learning107 model107 token107 prompt107 session107", 10),
        ["machine107", "learning107", "model107", "token107", "prompt107", "session107"],
    ),
    (
        ("machine107 learning107 model107 token107 prompt107 session107", 18),
        ["machine107", "learning107", "model107 token107", "prompt107", "session107"],
    ),
    (
        ("machine107 learning107 model107 token107 prompt107 session107", 28),
        ["machine107 learning107", "model107 token107 prompt107", "session107"],
    ),
    (
        ("learning107 model107 token107 prompt107 session107 library107", 6),
        ["learning107", "model107", "token107", "prompt107", "session107", "library107"],
    ),
    (
        ("learning107 model107 token107 prompt107 session107 library107", 10),
        ["learning107", "model107", "token107", "prompt107", "session107", "library107"],
    ),
    (
        ("learning107 model107 token107 prompt107 session107 library107", 18),
        ["learning107", "model107 token107", "prompt107", "session107", "library107"],
    ),
    (
        ("learning107 model107 token107 prompt107 session107 library107", 28),
        ["learning107 model107", "token107 prompt107", "session107 library107"],
    ),
    (
        ("model107 token107 prompt107 session107 library107 service107", 6),
        ["model107", "token107", "prompt107", "session107", "library107", "service107"],
    ),
    (
        ("model107 token107 prompt107 session107 library107 service107", 10),
        ["model107", "token107", "prompt107", "session107", "library107", "service107"],
    ),
    (
        ("model107 token107 prompt107 session107 library107 service107", 18),
        ["model107 token107", "prompt107", "session107", "library107", "service107"],
    ),
    (
        ("model107 token107 prompt107 session107 library107 service107", 28),
        ["model107 token107 prompt107", "session107 library107", "service107"],
    ),
    (
        ("token107 prompt107 session107 library107 service107 gateway107", 6),
        ["token107", "prompt107", "session107", "library107", "service107", "gateway107"],
    ),
    (
        ("token107 prompt107 session107 library107 service107 gateway107", 10),
        ["token107", "prompt107", "session107", "library107", "service107", "gateway107"],
    ),
    (
        ("token107 prompt107 session107 library107 service107 gateway107", 18),
        ["token107 prompt107", "session107", "library107", "service107", "gateway107"],
    ),
    (
        ("token107 prompt107 session107 library107 service107 gateway107", 28),
        ["token107 prompt107", "session107 library107", "service107 gateway107"],
    ),
    (
        ("prompt107 session107 library107 service107 gateway107 storage107", 6),
        ["prompt107", "session107", "library107", "service107", "gateway107", "storage107"],
    ),
    (
        ("prompt107 session107 library107 service107 gateway107 storage107", 10),
        ["prompt107", "session107", "library107", "service107", "gateway107", "storage107"],
    ),
    (
        ("prompt107 session107 library107 service107 gateway107 storage107", 18),
        ["prompt107", "session107", "library107", "service107", "gateway107", "storage107"],
    ),
    (
        ("prompt107 session107 library107 service107 gateway107 storage107", 28),
        ["prompt107 session107", "library107 service107", "gateway107 storage107"],
    ),
    (
        ("session107 library107 service107 gateway107 storage107 network107", 6),
        ["session107", "library107", "service107", "gateway107", "storage107", "network107"],
    ),
    (
        ("session107 library107 service107 gateway107 storage107 network107", 10),
        ["session107", "library107", "service107", "gateway107", "storage107", "network107"],
    ),
    (
        ("session107 library107 service107 gateway107 storage107 network107", 18),
        ["session107", "library107", "service107", "gateway107", "storage107", "network107"],
    ),
    (
        ("session107 library107 service107 gateway107 storage107 network107", 28),
        ["session107 library107", "service107 gateway107", "storage107 network107"],
    ),
    (
        ("library107 service107 gateway107 storage107 network107 latency107", 6),
        ["library107", "service107", "gateway107", "storage107", "network107", "latency107"],
    ),
    (
        ("library107 service107 gateway107 storage107 network107 latency107", 10),
        ["library107", "service107", "gateway107", "storage107", "network107", "latency107"],
    ),
    (
        ("library107 service107 gateway107 storage107 network107 latency107", 18),
        ["library107", "service107", "gateway107", "storage107", "network107", "latency107"],
    ),
    (
        ("library107 service107 gateway107 storage107 network107 latency107", 28),
        ["library107 service107", "gateway107 storage107", "network107 latency107"],
    ),
    (
        ("service107 gateway107 storage107 network107 latency107 buffer107", 6),
        ["service107", "gateway107", "storage107", "network107", "latency107", "buffer107"],
    ),
    (
        ("service107 gateway107 storage107 network107 latency107 buffer107", 10),
        ["service107", "gateway107", "storage107", "network107", "latency107", "buffer107"],
    ),
    (
        ("service107 gateway107 storage107 network107 latency107 buffer107", 18),
        ["service107", "gateway107", "storage107", "network107", "latency107", "buffer107"],
    ),
    (
        ("service107 gateway107 storage107 network107 latency107 buffer107", 28),
        ["service107 gateway107", "storage107 network107", "latency107 buffer107"],
    ),
    (
        ("gateway107 storage107 network107 latency107 buffer107 queue107", 6),
        ["gateway107", "storage107", "network107", "latency107", "buffer107", "queue107"],
    ),
    (
        ("gateway107 storage107 network107 latency107 buffer107 queue107", 10),
        ["gateway107", "storage107", "network107", "latency107", "buffer107", "queue107"],
    ),
    (
        ("gateway107 storage107 network107 latency107 buffer107 queue107", 18),
        ["gateway107", "storage107", "network107", "latency107", "buffer107 queue107"],
    ),
    (
        ("gateway107 storage107 network107 latency107 buffer107 queue107", 28),
        ["gateway107 storage107", "network107 latency107", "buffer107 queue107"],
    ),
    (
        ("storage107 network107 latency107 buffer107 queue107 worker107", 6),
        ["storage107", "network107", "latency107", "buffer107", "queue107", "worker107"],
    ),
    (
        ("storage107 network107 latency107 buffer107 queue107 worker107", 10),
        ["storage107", "network107", "latency107", "buffer107", "queue107", "worker107"],
    ),
    (
        ("storage107 network107 latency107 buffer107 queue107 worker107", 18),
        ["storage107", "network107", "latency107", "buffer107 queue107", "worker107"],
    ),
    (
        ("storage107 network107 latency107 buffer107 queue107 worker107", 28),
        ["storage107 network107", "latency107 buffer107", "queue107 worker107"],
    ),
    (
        ("network107 latency107 buffer107 queue107 worker107 kernel107", 6),
        ["network107", "latency107", "buffer107", "queue107", "worker107", "kernel107"],
    ),
    (
        ("network107 latency107 buffer107 queue107 worker107 kernel107", 10),
        ["network107", "latency107", "buffer107", "queue107", "worker107", "kernel107"],
    ),
    (
        ("network107 latency107 buffer107 queue107 worker107 kernel107", 18),
        ["network107", "latency107", "buffer107 queue107", "worker107", "kernel107"],
    ),
    (
        ("network107 latency107 buffer107 queue107 worker107 kernel107", 28),
        ["network107 latency107", "buffer107 queue107 worker107", "kernel107"],
    ),
    (
        ("latency107 buffer107 queue107 worker107 kernel107 signal107", 6),
        ["latency107", "buffer107", "queue107", "worker107", "kernel107", "signal107"],
    ),
    (
        ("latency107 buffer107 queue107 worker107 kernel107 signal107", 10),
        ["latency107", "buffer107", "queue107", "worker107", "kernel107", "signal107"],
    ),
    (
        ("latency107 buffer107 queue107 worker107 kernel107 signal107", 18),
        ["latency107", "buffer107 queue107", "worker107", "kernel107", "signal107"],
    ),
    (
        ("latency107 buffer107 queue107 worker107 kernel107 signal107", 28),
        ["latency107 buffer107", "queue107 worker107 kernel107", "signal107"],
    ),
    (
        ("buffer107 queue107 worker107 kernel107 signal107 packet107", 6),
        ["buffer107", "queue107", "worker107", "kernel107", "signal107", "packet107"],
    ),
    (
        ("buffer107 queue107 worker107 kernel107 signal107 packet107", 10),
        ["buffer107", "queue107", "worker107", "kernel107", "signal107", "packet107"],
    ),
    (
        ("buffer107 queue107 worker107 kernel107 signal107 packet107", 18),
        ["buffer107 queue107", "worker107", "kernel107", "signal107", "packet107"],
    ),
    (
        ("buffer107 queue107 worker107 kernel107 signal107 packet107", 28),
        ["buffer107 queue107 worker107", "kernel107 signal107", "packet107"],
    ),
    (
        ("queue107 worker107 kernel107 signal107 packet107 router107", 6),
        ["queue107", "worker107", "kernel107", "signal107", "packet107", "router107"],
    ),
    (
        ("queue107 worker107 kernel107 signal107 packet107 router107", 10),
        ["queue107", "worker107", "kernel107", "signal107", "packet107", "router107"],
    ),
    (
        ("queue107 worker107 kernel107 signal107 packet107 router107", 18),
        ["queue107 worker107", "kernel107", "signal107", "packet107", "router107"],
    ),
    (
        ("queue107 worker107 kernel107 signal107 packet107 router107", 28),
        ["queue107 worker107 kernel107", "signal107 packet107", "router107"],
    ),
    (
        ("worker107 kernel107 signal107 packet107 router107 cluster107", 6),
        ["worker107", "kernel107", "signal107", "packet107", "router107", "cluster107"],
    ),
    (
        ("worker107 kernel107 signal107 packet107 router107 cluster107", 10),
        ["worker107", "kernel107", "signal107", "packet107", "router107", "cluster107"],
    ),
    (
        ("worker107 kernel107 signal107 packet107 router107 cluster107", 18),
        ["worker107", "kernel107", "signal107", "packet107", "router107", "cluster107"],
    ),
    (
        ("worker107 kernel107 signal107 packet107 router107 cluster107", 28),
        ["worker107 kernel107", "signal107 packet107", "router107 cluster107"],
    ),
    (
        ("kernel107 signal107 packet107 router107 cluster107 mirror107", 6),
        ["kernel107", "signal107", "packet107", "router107", "cluster107", "mirror107"],
    ),
    (
        ("kernel107 signal107 packet107 router107 cluster107 mirror107", 10),
        ["kernel107", "signal107", "packet107", "router107", "cluster107", "mirror107"],
    ),
    (
        ("kernel107 signal107 packet107 router107 cluster107 mirror107", 18),
        ["kernel107", "signal107", "packet107", "router107", "cluster107", "mirror107"],
    ),
    (
        ("kernel107 signal107 packet107 router107 cluster107 mirror107", 28),
        ["kernel107 signal107", "packet107 router107", "cluster107 mirror107"],
    ),
    (
        ("signal107 packet107 router107 cluster107 mirror107 filter107", 6),
        ["signal107", "packet107", "router107", "cluster107", "mirror107", "filter107"],
    ),
    (
        ("signal107 packet107 router107 cluster107 mirror107 filter107", 10),
        ["signal107", "packet107", "router107", "cluster107", "mirror107", "filter107"],
    ),
    (
        ("signal107 packet107 router107 cluster107 mirror107 filter107", 18),
        ["signal107", "packet107", "router107", "cluster107", "mirror107", "filter107"],
    ),
    (
        ("signal107 packet107 router107 cluster107 mirror107 filter107", 28),
        ["signal107 packet107", "router107 cluster107", "mirror107 filter107"],
    ),
    (
        ("packet107 router107 cluster107 mirror107 filter107 ranking107", 6),
        ["packet107", "router107", "cluster107", "mirror107", "filter107", "ranking107"],
    ),
    (
        ("packet107 router107 cluster107 mirror107 filter107 ranking107", 10),
        ["packet107", "router107", "cluster107", "mirror107", "filter107", "ranking107"],
    ),
    (
        ("packet107 router107 cluster107 mirror107 filter107 ranking107", 18),
        ["packet107", "router107", "cluster107", "mirror107", "filter107", "ranking107"],
    ),
    (
        ("packet107 router107 cluster107 mirror107 filter107 ranking107", 28),
        ["packet107 router107", "cluster107 mirror107", "filter107 ranking107"],
    ),
    (
        ("router107 cluster107 mirror107 filter107 ranking107 encoding107", 6),
        ["router107", "cluster107", "mirror107", "filter107", "ranking107", "encoding107"],
    ),
    (
        ("router107 cluster107 mirror107 filter107 ranking107 encoding107", 10),
        ["router107", "cluster107", "mirror107", "filter107", "ranking107", "encoding107"],
    ),
    (
        ("router107 cluster107 mirror107 filter107 ranking107 encoding107", 18),
        ["router107", "cluster107", "mirror107", "filter107", "ranking107", "encoding107"],
    ),
    (
        ("router107 cluster107 mirror107 filter107 ranking107 encoding107", 28),
        ["router107 cluster107", "mirror107 filter107", "ranking107 encoding107"],
    ),
    (
        ("cluster107 mirror107 filter107 ranking107 encoding107 mapping107", 6),
        ["cluster107", "mirror107", "filter107", "ranking107", "encoding107", "mapping107"],
    ),
    (
        ("cluster107 mirror107 filter107 ranking107 encoding107 mapping107", 10),
        ["cluster107", "mirror107", "filter107", "ranking107", "encoding107", "mapping107"],
    ),
    (
        ("cluster107 mirror107 filter107 ranking107 encoding107 mapping107", 18),
        ["cluster107", "mirror107", "filter107", "ranking107", "encoding107", "mapping107"],
    ),
    (
        ("cluster107 mirror107 filter107 ranking107 encoding107 mapping107", 28),
        ["cluster107 mirror107", "filter107 ranking107", "encoding107 mapping107"],
    ),
    (
        ("mirror107 filter107 ranking107 encoding107 mapping107 record107", 6),
        ["mirror107", "filter107", "ranking107", "encoding107", "mapping107", "record107"],
    ),
    (
        ("mirror107 filter107 ranking107 encoding107 mapping107 record107", 10),
        ["mirror107", "filter107", "ranking107", "encoding107", "mapping107", "record107"],
    ),
    (
        ("mirror107 filter107 ranking107 encoding107 mapping107 record107", 18),
        ["mirror107", "filter107", "ranking107", "encoding107", "mapping107", "record107"],
    ),
    (
        ("mirror107 filter107 ranking107 encoding107 mapping107 record107", 28),
        ["mirror107 filter107", "ranking107 encoding107", "mapping107 record107"],
    ),
    (
        ("filter107 ranking107 encoding107 mapping107 record107 candle107", 6),
        ["filter107", "ranking107", "encoding107", "mapping107", "record107", "candle107"],
    ),
    (
        ("filter107 ranking107 encoding107 mapping107 record107 candle107", 10),
        ["filter107", "ranking107", "encoding107", "mapping107", "record107", "candle107"],
    ),
    (
        ("filter107 ranking107 encoding107 mapping107 record107 candle107", 18),
        ["filter107", "ranking107", "encoding107", "mapping107", "record107", "candle107"],
    ),
    (
        ("filter107 ranking107 encoding107 mapping107 record107 candle107", 28),
        ["filter107 ranking107", "encoding107 mapping107", "record107 candle107"],
    ),
    (
        ("ranking107 encoding107 mapping107 record107 candle107 thread107", 6),
        ["ranking107", "encoding107", "mapping107", "record107", "candle107", "thread107"],
    ),
    (
        ("ranking107 encoding107 mapping107 record107 candle107 thread107", 10),
        ["ranking107", "encoding107", "mapping107", "record107", "candle107", "thread107"],
    ),
    (
        ("ranking107 encoding107 mapping107 record107 candle107 thread107", 18),
        ["ranking107", "encoding107", "mapping107", "record107", "candle107", "thread107"],
    ),
    (
        ("ranking107 encoding107 mapping107 record107 candle107 thread107", 28),
        ["ranking107 encoding107", "mapping107 record107", "candle107 thread107"],
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
