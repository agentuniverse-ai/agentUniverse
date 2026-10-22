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
        ("round 138: the quick brown fox jumps over the lazy dog", 4),
        ["round", "138:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", 8),
        ["round", "138: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", 12),
        ["round 138:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", 16),
        ["round 138: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", 24),
        ["round 138: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 138: the quick brown fox jumps over the lazy dog", 32),
        ["round 138: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", 4),
        ["round", "138:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", 8),
        ["round", "138:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", 12),
        ["round 138:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", 16),
        ["round 138:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", 24),
        ["round 138: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 138: agentuniverse is a framework for multi agents", 32),
        ["round 138: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", 4),
        ["round", "138:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", 8),
        ["round", "138:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", 12),
        ["round 138:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", 16),
        ["round 138:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", 24),
        ["round 138: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 138: knowledge stored as vectors enables retrieval", 32),
        ["round 138: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 138: the processor reads the record then stops", 4),
        ["round", "138:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 138: the processor reads the record then stops", 8),
        ["round", "138: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 138: the processor reads the record then stops", 12),
        ["round 138:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 138: the processor reads the record then stops", 16),
        ["round 138: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 138: the processor reads the record then stops", 24),
        ["round 138: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 138: the processor reads the record then stops", 32),
        ["round 138: the processor reads", "the record then stops"],
    ),
    (
        ("round 138: a worker pulls the next task from the queue", 4),
        ["round", "138:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 138: a worker pulls the next task from the queue", 8),
        ["round", "138: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 138: a worker pulls the next task from the queue", 12),
        ["round 138: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 138: a worker pulls the next task from the queue", 16),
        ["round 138: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 138: a worker pulls the next task from the queue", 24),
        ["round 138: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 138: a worker pulls the next task from the queue", 32),
        ["round 138: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 138: signals travel through the network layer", 4),
        ["round", "138:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 138: signals travel through the network layer", 8),
        ["round", "138:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 138: signals travel through the network layer", 12),
        ["round 138:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 138: signals travel through the network layer", 16),
        ["round 138:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 138: signals travel through the network layer", 24),
        ["round 138: signals", "travel through the", "network layer"],
    ),
    (
        ("round 138: signals travel through the network layer", 32),
        ["round 138: signals travel", "through the network layer"],
    ),
    (
        ("round 138: the gateway routes each request by policy", 4),
        ["round", "138:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 138: the gateway routes each request by policy", 8),
        ["round", "138: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 138: the gateway routes each request by policy", 12),
        ["round 138:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 138: the gateway routes each request by policy", 16),
        ["round 138: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 138: the gateway routes each request by policy", 24),
        ["round 138: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 138: the gateway routes each request by policy", 32),
        ["round 138: the gateway routes", "each request by policy"],
    ),
    (
        ("round 138: memory grows until the buffer is full", 4),
        ["round", "138:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 138: memory grows until the buffer is full", 8),
        ["round", "138:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 138: memory grows until the buffer is full", 12),
        ["round 138:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 138: memory grows until the buffer is full", 16),
        ["round 138:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 138: memory grows until the buffer is full", 24), ["round 138: memory grows", "until the buffer is full"]),
    (("round 138: memory grows until the buffer is full", 32), ["round 138: memory grows until", "the buffer is full"]),
    (
        ("round 138: the cluster mirrors every packet twice", 4),
        ["round", "138:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 138: the cluster mirrors every packet twice", 8),
        ["round", "138: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 138: the cluster mirrors every packet twice", 12),
        ["round 138:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 138: the cluster mirrors every packet twice", 16),
        ["round 138: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 138: the cluster mirrors every packet twice", 24),
        ["round 138: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 138: the cluster mirrors every packet twice", 32),
        ["round 138: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", 4),
        ["round", "138:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", 8),
        ["round", "138:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", 12),
        ["round 138:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", 16),
        ["round 138:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", 24),
        ["round 138: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 138: ranking uses tokens learned from the corpus", 32),
        ["round 138: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 138: a long session ends when the candle dies", 4),
        ["round", "138:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 138: a long session ends when the candle dies", 8),
        ["round", "138: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 138: a long session ends when the candle dies", 12),
        ["round 138: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 138: a long session ends when the candle dies", 16),
        ["round 138: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 138: a long session ends when the candle dies", 24),
        ["round 138: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 138: a long session ends when the candle dies", 32),
        ["round 138: a long session ends", "when the candle dies"],
    ),
    (
        ("round 138: encode the prompt then map the result", 4),
        ["round", "138:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 138: encode the prompt then map the result", 8),
        ["round", "138:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 138: encode the prompt then map the result", 12),
        ["round 138:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 138: encode the prompt then map the result", 16),
        ["round 138:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 138: encode the prompt then map the result", 24),
        ["round 138: encode the", "prompt then map the", "result"],
    ),
    (("round 138: encode the prompt then map the result", 32), ["round 138: encode the prompt", "then map the result"]),
    (
        ("round 138: the kernel wakes the worker at dawn", 4),
        ["round", "138:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 138: the kernel wakes the worker at dawn", 8),
        ["round", "138: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 138: the kernel wakes the worker at dawn", 12),
        ["round 138:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 138: the kernel wakes the worker at dawn", 16), ["round 138: the", "kernel wakes the", "worker at dawn"]),
    (("round 138: the kernel wakes the worker at dawn", 24), ["round 138: the kernel", "wakes the worker at dawn"]),
    (("round 138: the kernel wakes the worker at dawn", 32), ["round 138: the kernel wakes the", "worker at dawn"]),
    (
        ("round 138: service latency drops after the patch", 4),
        ["round", "138:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 138: service latency drops after the patch", 8),
        ["round", "138:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 138: service latency drops after the patch", 12),
        ["round 138:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 138: service latency drops after the patch", 16),
        ["round 138:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 138: service latency drops after the patch", 24),
        ["round 138: service", "latency drops after the", "patch"],
    ),
    (("round 138: service latency drops after the patch", 32), ["round 138: service latency drops", "after the patch"]),
    (
        ("round 138: the library caches every vector it sees", 4),
        ["round", "138:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 138: the library caches every vector it sees", 8),
        ["round", "138: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 138: the library caches every vector it sees", 12),
        ["round 138:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 138: the library caches every vector it sees", 16),
        ["round 138: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 138: the library caches every vector it sees", 24),
        ["round 138: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 138: the library caches every vector it sees", 32),
        ["round 138: the library caches", "every vector it sees"],
    ),
    (
        ("round 138: agents argue then the debate resolves", 4),
        ["round", "138:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 138: agents argue then the debate resolves", 8),
        ["round", "138:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 138: agents argue then the debate resolves", 12),
        ["round 138:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 138: agents argue then the debate resolves", 16),
        ["round 138:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 138: agents argue then the debate resolves", 24), ["round 138: agents argue", "then the debate resolves"]),
    (("round 138: agents argue then the debate resolves", 32), ["round 138: agents argue then the", "debate resolves"]),
    (
        ("round 138: the filter keeps only strong matches", 4),
        ["round", "138:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 138: the filter keeps only strong matches", 8),
        ["round", "138: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 138: the filter keeps only strong matches", 12),
        ["round 138:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 138: the filter keeps only strong matches", 16),
        ["round 138: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 138: the filter keeps only strong matches", 24),
        ["round 138: the filter", "keeps only strong", "matches"],
    ),
    (("round 138: the filter keeps only strong matches", 32), ["round 138: the filter keeps only", "strong matches"]),
    (
        ("round 138: the model answers with a short reply", 4),
        ["round", "138:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 138: the model answers with a short reply", 8),
        ["round", "138: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 138: the model answers with a short reply", 12),
        ["round 138:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 138: the model answers with a short reply", 16),
        ["round 138: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 138: the model answers with a short reply", 24),
        ["round 138: the model", "answers with a short", "reply"],
    ),
    (("round 138: the model answers with a short reply", 32), ["round 138: the model answers", "with a short reply"]),
    (
        ("round 138: the recorder stores the reasoning trace", 4),
        ["round", "138:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 138: the recorder stores the reasoning trace", 8),
        ["round", "138: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 138: the recorder stores the reasoning trace", 12),
        ["round 138:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 138: the recorder stores the reasoning trace", 16),
        ["round 138: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 138: the recorder stores the reasoning trace", 24),
        ["round 138: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 138: the recorder stores the reasoning trace", 32),
        ["round 138: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 138: the angel watches the processor run", 4),
        ["round", "138:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 138: the angel watches the processor run", 8),
        ["round", "138: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 138: the angel watches the processor run", 12),
        ["round 138:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 138: the angel watches the processor run", 16),
        ["round 138: the", "angel watches", "the processor", "run"],
    ),
    (("round 138: the angel watches the processor run", 24), ["round 138: the angel", "watches the processor", "run"]),
    (("round 138: the angel watches the processor run", 32), ["round 138: the angel watches the", "processor run"]),
    (
        ("round 138: angle of the vector decides the match", 4),
        ["round", "138:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 138: angle of the vector decides the match", 8),
        ["round", "138:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 138: angle of the vector decides the match", 12),
        ["round 138:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 138: angle of the vector decides the match", 16),
        ["round 138: angle", "of the vector", "decides the", "match"],
    ),
    (("round 138: angle of the vector decides the match", 24), ["round 138: angle of the", "vector decides the match"]),
    (("round 138: angle of the vector decides the match", 32), ["round 138: angle of the vector", "decides the match"]),
    (
        ("round 138: the candle burns twice as long at night", 4),
        ["round", "138:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 138: the candle burns twice as long at night", 8),
        ["round", "138: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 138: the candle burns twice as long at night", 12),
        ["round 138:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 138: the candle burns twice as long at night", 16),
        ["round 138: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 138: the candle burns twice as long at night", 24),
        ["round 138: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 138: the candle burns twice as long at night", 32),
        ["round 138: the candle burns", "twice as long at night"],
    ),
    (
        ("round 138: a mirror of the universe in one line", 4),
        ["round", "138:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 138: a mirror of the universe in one line", 8),
        ["round", "138: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 138: a mirror of the universe in one line", 12),
        ["round 138: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 138: a mirror of the universe in one line", 16),
        ["round 138: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 138: a mirror of the universe in one line", 24), ["round 138: a mirror of", "the universe in one line"]),
    (("round 138: a mirror of the universe in one line", 32), ["round 138: a mirror of the", "universe in one line"]),
    (
        ("round 138: the queue drains before the storm", 4),
        ["round", "138:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 138: the queue drains before the storm", 8),
        ["round", "138: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 138: the queue drains before the storm", 12),
        ["round 138:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 138: the queue drains before the storm", 16), ["round 138: the", "queue drains", "before the storm"]),
    (("round 138: the queue drains before the storm", 24), ["round 138: the queue", "drains before the storm"]),
    (("round 138: the queue drains before the storm", 32), ["round 138: the queue drains", "before the storm"]),
    (
        ("kitten138 sitting138 agent138 angle138 universe138 memory138", 6),
        ["kitten138", "sitting138", "agent138", "angle138", "universe138", "memory138"],
    ),
    (
        ("kitten138 sitting138 agent138 angle138 universe138 memory138", 10),
        ["kitten138", "sitting138", "agent138", "angle138", "universe138", "memory138"],
    ),
    (
        ("kitten138 sitting138 agent138 angle138 universe138 memory138", 18),
        ["kitten138", "sitting138", "agent138 angle138", "universe138", "memory138"],
    ),
    (
        ("kitten138 sitting138 agent138 angle138 universe138 memory138", 28),
        ["kitten138 sitting138", "agent138 angle138", "universe138 memory138"],
    ),
    (
        ("sitting138 agent138 angle138 universe138 memory138 stream138", 6),
        ["sitting138", "agent138", "angle138", "universe138", "memory138", "stream138"],
    ),
    (
        ("sitting138 agent138 angle138 universe138 memory138 stream138", 10),
        ["sitting138", "agent138", "angle138", "universe138", "memory138", "stream138"],
    ),
    (
        ("sitting138 agent138 angle138 universe138 memory138 stream138", 18),
        ["sitting138", "agent138 angle138", "universe138", "memory138", "stream138"],
    ),
    (
        ("sitting138 agent138 angle138 universe138 memory138 stream138", 28),
        ["sitting138 agent138 angle138", "universe138 memory138", "stream138"],
    ),
    (
        ("agent138 angle138 universe138 memory138 stream138 context138", 6),
        ["agent138", "angle138", "universe138", "memory138", "stream138", "context138"],
    ),
    (
        ("agent138 angle138 universe138 memory138 stream138 context138", 10),
        ["agent138", "angle138", "universe138", "memory138", "stream138", "context138"],
    ),
    (
        ("agent138 angle138 universe138 memory138 stream138 context138", 18),
        ["agent138 angle138", "universe138", "memory138", "stream138", "context138"],
    ),
    (
        ("agent138 angle138 universe138 memory138 stream138 context138", 28),
        ["agent138 angle138", "universe138 memory138", "stream138 context138"],
    ),
    (
        ("angle138 universe138 memory138 stream138 context138 knowledge138", 6),
        ["angle138", "universe138", "memory138", "stream138", "context138", "knowledge138"],
    ),
    (
        ("angle138 universe138 memory138 stream138 context138 knowledge138", 10),
        ["angle138", "universe138", "memory138", "stream138", "context138", "knowledge138"],
    ),
    (
        ("angle138 universe138 memory138 stream138 context138 knowledge138", 18),
        ["angle138", "universe138", "memory138", "stream138", "context138", "knowledge138"],
    ),
    (
        ("angle138 universe138 memory138 stream138 context138 knowledge138", 28),
        ["angle138 universe138", "memory138 stream138", "context138 knowledge138"],
    ),
    (
        ("universe138 memory138 stream138 context138 knowledge138 vector138", 6),
        ["universe138", "memory138", "stream138", "context138", "knowledge138", "vector138"],
    ),
    (
        ("universe138 memory138 stream138 context138 knowledge138 vector138", 10),
        ["universe138", "memory138", "stream138", "context138", "knowledge138", "vector138"],
    ),
    (
        ("universe138 memory138 stream138 context138 knowledge138 vector138", 18),
        ["universe138", "memory138", "stream138", "context138", "knowledge138", "vector138"],
    ),
    (
        ("universe138 memory138 stream138 context138 knowledge138 vector138", 28),
        ["universe138 memory138", "stream138 context138", "knowledge138 vector138"],
    ),
    (
        ("memory138 stream138 context138 knowledge138 vector138 processor138", 6),
        ["memory138", "stream138", "context138", "knowledge138", "vector138", "processor138"],
    ),
    (
        ("memory138 stream138 context138 knowledge138 vector138 processor138", 10),
        ["memory138", "stream138", "context138", "knowledge138", "vector138", "processor138"],
    ),
    (
        ("memory138 stream138 context138 knowledge138 vector138 processor138", 18),
        ["memory138", "stream138", "context138", "knowledge138", "vector138", "processor138"],
    ),
    (
        ("memory138 stream138 context138 knowledge138 vector138 processor138", 28),
        ["memory138 stream138", "context138 knowledge138", "vector138 processor138"],
    ),
    (
        ("stream138 context138 knowledge138 vector138 processor138 reasoning138", 6),
        ["stream138", "context138", "knowledge138", "vector138", "processor138", "reasoning138"],
    ),
    (
        ("stream138 context138 knowledge138 vector138 processor138 reasoning138", 10),
        ["stream138", "context138", "knowledge138", "vector138", "processor138", "reasoning138"],
    ),
    (
        ("stream138 context138 knowledge138 vector138 processor138 reasoning138", 18),
        ["stream138", "context138", "knowledge138", "vector138", "processor138", "reasoning138"],
    ),
    (
        ("stream138 context138 knowledge138 vector138 processor138 reasoning138", 28),
        ["stream138 context138", "knowledge138 vector138", "processor138 reasoning138"],
    ),
    (
        ("context138 knowledge138 vector138 processor138 reasoning138 machine138", 6),
        ["context138", "knowledge138", "vector138", "processor138", "reasoning138", "machine138"],
    ),
    (
        ("context138 knowledge138 vector138 processor138 reasoning138 machine138", 10),
        ["context138", "knowledge138", "vector138", "processor138", "reasoning138", "machine138"],
    ),
    (
        ("context138 knowledge138 vector138 processor138 reasoning138 machine138", 18),
        ["context138", "knowledge138", "vector138", "processor138", "reasoning138", "machine138"],
    ),
    (
        ("context138 knowledge138 vector138 processor138 reasoning138 machine138", 28),
        ["context138 knowledge138", "vector138 processor138", "reasoning138 machine138"],
    ),
    (
        ("knowledge138 vector138 processor138 reasoning138 machine138 learning138", 6),
        ["knowledge138", "vector138", "processor138", "reasoning138", "machine138", "learning138"],
    ),
    (
        ("knowledge138 vector138 processor138 reasoning138 machine138 learning138", 10),
        ["knowledge138", "vector138", "processor138", "reasoning138", "machine138", "learning138"],
    ),
    (
        ("knowledge138 vector138 processor138 reasoning138 machine138 learning138", 18),
        ["knowledge138", "vector138", "processor138", "reasoning138", "machine138", "learning138"],
    ),
    (
        ("knowledge138 vector138 processor138 reasoning138 machine138 learning138", 28),
        ["knowledge138 vector138", "processor138 reasoning138", "machine138 learning138"],
    ),
    (
        ("vector138 processor138 reasoning138 machine138 learning138 model138", 6),
        ["vector138", "processor138", "reasoning138", "machine138", "learning138", "model138"],
    ),
    (
        ("vector138 processor138 reasoning138 machine138 learning138 model138", 10),
        ["vector138", "processor138", "reasoning138", "machine138", "learning138", "model138"],
    ),
    (
        ("vector138 processor138 reasoning138 machine138 learning138 model138", 18),
        ["vector138", "processor138", "reasoning138", "machine138", "learning138", "model138"],
    ),
    (
        ("vector138 processor138 reasoning138 machine138 learning138 model138", 28),
        ["vector138 processor138", "reasoning138 machine138", "learning138 model138"],
    ),
    (
        ("processor138 reasoning138 machine138 learning138 model138 token138", 6),
        ["processor138", "reasoning138", "machine138", "learning138", "model138", "token138"],
    ),
    (
        ("processor138 reasoning138 machine138 learning138 model138 token138", 10),
        ["processor138", "reasoning138", "machine138", "learning138", "model138", "token138"],
    ),
    (
        ("processor138 reasoning138 machine138 learning138 model138 token138", 18),
        ["processor138", "reasoning138", "machine138", "learning138", "model138 token138"],
    ),
    (
        ("processor138 reasoning138 machine138 learning138 model138 token138", 28),
        ["processor138 reasoning138", "machine138 learning138", "model138 token138"],
    ),
    (
        ("reasoning138 machine138 learning138 model138 token138 prompt138", 6),
        ["reasoning138", "machine138", "learning138", "model138", "token138", "prompt138"],
    ),
    (
        ("reasoning138 machine138 learning138 model138 token138 prompt138", 10),
        ["reasoning138", "machine138", "learning138", "model138", "token138", "prompt138"],
    ),
    (
        ("reasoning138 machine138 learning138 model138 token138 prompt138", 18),
        ["reasoning138", "machine138", "learning138", "model138 token138", "prompt138"],
    ),
    (
        ("reasoning138 machine138 learning138 model138 token138 prompt138", 28),
        ["reasoning138 machine138", "learning138 model138", "token138 prompt138"],
    ),
    (
        ("machine138 learning138 model138 token138 prompt138 session138", 6),
        ["machine138", "learning138", "model138", "token138", "prompt138", "session138"],
    ),
    (
        ("machine138 learning138 model138 token138 prompt138 session138", 10),
        ["machine138", "learning138", "model138", "token138", "prompt138", "session138"],
    ),
    (
        ("machine138 learning138 model138 token138 prompt138 session138", 18),
        ["machine138", "learning138", "model138 token138", "prompt138", "session138"],
    ),
    (
        ("machine138 learning138 model138 token138 prompt138 session138", 28),
        ["machine138 learning138", "model138 token138 prompt138", "session138"],
    ),
    (
        ("learning138 model138 token138 prompt138 session138 library138", 6),
        ["learning138", "model138", "token138", "prompt138", "session138", "library138"],
    ),
    (
        ("learning138 model138 token138 prompt138 session138 library138", 10),
        ["learning138", "model138", "token138", "prompt138", "session138", "library138"],
    ),
    (
        ("learning138 model138 token138 prompt138 session138 library138", 18),
        ["learning138", "model138 token138", "prompt138", "session138", "library138"],
    ),
    (
        ("learning138 model138 token138 prompt138 session138 library138", 28),
        ["learning138 model138", "token138 prompt138", "session138 library138"],
    ),
    (
        ("model138 token138 prompt138 session138 library138 service138", 6),
        ["model138", "token138", "prompt138", "session138", "library138", "service138"],
    ),
    (
        ("model138 token138 prompt138 session138 library138 service138", 10),
        ["model138", "token138", "prompt138", "session138", "library138", "service138"],
    ),
    (
        ("model138 token138 prompt138 session138 library138 service138", 18),
        ["model138 token138", "prompt138", "session138", "library138", "service138"],
    ),
    (
        ("model138 token138 prompt138 session138 library138 service138", 28),
        ["model138 token138 prompt138", "session138 library138", "service138"],
    ),
    (
        ("token138 prompt138 session138 library138 service138 gateway138", 6),
        ["token138", "prompt138", "session138", "library138", "service138", "gateway138"],
    ),
    (
        ("token138 prompt138 session138 library138 service138 gateway138", 10),
        ["token138", "prompt138", "session138", "library138", "service138", "gateway138"],
    ),
    (
        ("token138 prompt138 session138 library138 service138 gateway138", 18),
        ["token138 prompt138", "session138", "library138", "service138", "gateway138"],
    ),
    (
        ("token138 prompt138 session138 library138 service138 gateway138", 28),
        ["token138 prompt138", "session138 library138", "service138 gateway138"],
    ),
    (
        ("prompt138 session138 library138 service138 gateway138 storage138", 6),
        ["prompt138", "session138", "library138", "service138", "gateway138", "storage138"],
    ),
    (
        ("prompt138 session138 library138 service138 gateway138 storage138", 10),
        ["prompt138", "session138", "library138", "service138", "gateway138", "storage138"],
    ),
    (
        ("prompt138 session138 library138 service138 gateway138 storage138", 18),
        ["prompt138", "session138", "library138", "service138", "gateway138", "storage138"],
    ),
    (
        ("prompt138 session138 library138 service138 gateway138 storage138", 28),
        ["prompt138 session138", "library138 service138", "gateway138 storage138"],
    ),
    (
        ("session138 library138 service138 gateway138 storage138 network138", 6),
        ["session138", "library138", "service138", "gateway138", "storage138", "network138"],
    ),
    (
        ("session138 library138 service138 gateway138 storage138 network138", 10),
        ["session138", "library138", "service138", "gateway138", "storage138", "network138"],
    ),
    (
        ("session138 library138 service138 gateway138 storage138 network138", 18),
        ["session138", "library138", "service138", "gateway138", "storage138", "network138"],
    ),
    (
        ("session138 library138 service138 gateway138 storage138 network138", 28),
        ["session138 library138", "service138 gateway138", "storage138 network138"],
    ),
    (
        ("library138 service138 gateway138 storage138 network138 latency138", 6),
        ["library138", "service138", "gateway138", "storage138", "network138", "latency138"],
    ),
    (
        ("library138 service138 gateway138 storage138 network138 latency138", 10),
        ["library138", "service138", "gateway138", "storage138", "network138", "latency138"],
    ),
    (
        ("library138 service138 gateway138 storage138 network138 latency138", 18),
        ["library138", "service138", "gateway138", "storage138", "network138", "latency138"],
    ),
    (
        ("library138 service138 gateway138 storage138 network138 latency138", 28),
        ["library138 service138", "gateway138 storage138", "network138 latency138"],
    ),
    (
        ("service138 gateway138 storage138 network138 latency138 buffer138", 6),
        ["service138", "gateway138", "storage138", "network138", "latency138", "buffer138"],
    ),
    (
        ("service138 gateway138 storage138 network138 latency138 buffer138", 10),
        ["service138", "gateway138", "storage138", "network138", "latency138", "buffer138"],
    ),
    (
        ("service138 gateway138 storage138 network138 latency138 buffer138", 18),
        ["service138", "gateway138", "storage138", "network138", "latency138", "buffer138"],
    ),
    (
        ("service138 gateway138 storage138 network138 latency138 buffer138", 28),
        ["service138 gateway138", "storage138 network138", "latency138 buffer138"],
    ),
    (
        ("gateway138 storage138 network138 latency138 buffer138 queue138", 6),
        ["gateway138", "storage138", "network138", "latency138", "buffer138", "queue138"],
    ),
    (
        ("gateway138 storage138 network138 latency138 buffer138 queue138", 10),
        ["gateway138", "storage138", "network138", "latency138", "buffer138", "queue138"],
    ),
    (
        ("gateway138 storage138 network138 latency138 buffer138 queue138", 18),
        ["gateway138", "storage138", "network138", "latency138", "buffer138 queue138"],
    ),
    (
        ("gateway138 storage138 network138 latency138 buffer138 queue138", 28),
        ["gateway138 storage138", "network138 latency138", "buffer138 queue138"],
    ),
    (
        ("storage138 network138 latency138 buffer138 queue138 worker138", 6),
        ["storage138", "network138", "latency138", "buffer138", "queue138", "worker138"],
    ),
    (
        ("storage138 network138 latency138 buffer138 queue138 worker138", 10),
        ["storage138", "network138", "latency138", "buffer138", "queue138", "worker138"],
    ),
    (
        ("storage138 network138 latency138 buffer138 queue138 worker138", 18),
        ["storage138", "network138", "latency138", "buffer138 queue138", "worker138"],
    ),
    (
        ("storage138 network138 latency138 buffer138 queue138 worker138", 28),
        ["storage138 network138", "latency138 buffer138", "queue138 worker138"],
    ),
    (
        ("network138 latency138 buffer138 queue138 worker138 kernel138", 6),
        ["network138", "latency138", "buffer138", "queue138", "worker138", "kernel138"],
    ),
    (
        ("network138 latency138 buffer138 queue138 worker138 kernel138", 10),
        ["network138", "latency138", "buffer138", "queue138", "worker138", "kernel138"],
    ),
    (
        ("network138 latency138 buffer138 queue138 worker138 kernel138", 18),
        ["network138", "latency138", "buffer138 queue138", "worker138", "kernel138"],
    ),
    (
        ("network138 latency138 buffer138 queue138 worker138 kernel138", 28),
        ["network138 latency138", "buffer138 queue138 worker138", "kernel138"],
    ),
    (
        ("latency138 buffer138 queue138 worker138 kernel138 signal138", 6),
        ["latency138", "buffer138", "queue138", "worker138", "kernel138", "signal138"],
    ),
    (
        ("latency138 buffer138 queue138 worker138 kernel138 signal138", 10),
        ["latency138", "buffer138", "queue138", "worker138", "kernel138", "signal138"],
    ),
    (
        ("latency138 buffer138 queue138 worker138 kernel138 signal138", 18),
        ["latency138", "buffer138 queue138", "worker138", "kernel138", "signal138"],
    ),
    (
        ("latency138 buffer138 queue138 worker138 kernel138 signal138", 28),
        ["latency138 buffer138", "queue138 worker138 kernel138", "signal138"],
    ),
    (
        ("buffer138 queue138 worker138 kernel138 signal138 packet138", 6),
        ["buffer138", "queue138", "worker138", "kernel138", "signal138", "packet138"],
    ),
    (
        ("buffer138 queue138 worker138 kernel138 signal138 packet138", 10),
        ["buffer138", "queue138", "worker138", "kernel138", "signal138", "packet138"],
    ),
    (
        ("buffer138 queue138 worker138 kernel138 signal138 packet138", 18),
        ["buffer138 queue138", "worker138", "kernel138", "signal138", "packet138"],
    ),
    (
        ("buffer138 queue138 worker138 kernel138 signal138 packet138", 28),
        ["buffer138 queue138 worker138", "kernel138 signal138", "packet138"],
    ),
    (
        ("queue138 worker138 kernel138 signal138 packet138 router138", 6),
        ["queue138", "worker138", "kernel138", "signal138", "packet138", "router138"],
    ),
    (
        ("queue138 worker138 kernel138 signal138 packet138 router138", 10),
        ["queue138", "worker138", "kernel138", "signal138", "packet138", "router138"],
    ),
    (
        ("queue138 worker138 kernel138 signal138 packet138 router138", 18),
        ["queue138 worker138", "kernel138", "signal138", "packet138", "router138"],
    ),
    (
        ("queue138 worker138 kernel138 signal138 packet138 router138", 28),
        ["queue138 worker138 kernel138", "signal138 packet138", "router138"],
    ),
    (
        ("worker138 kernel138 signal138 packet138 router138 cluster138", 6),
        ["worker138", "kernel138", "signal138", "packet138", "router138", "cluster138"],
    ),
    (
        ("worker138 kernel138 signal138 packet138 router138 cluster138", 10),
        ["worker138", "kernel138", "signal138", "packet138", "router138", "cluster138"],
    ),
    (
        ("worker138 kernel138 signal138 packet138 router138 cluster138", 18),
        ["worker138", "kernel138", "signal138", "packet138", "router138", "cluster138"],
    ),
    (
        ("worker138 kernel138 signal138 packet138 router138 cluster138", 28),
        ["worker138 kernel138", "signal138 packet138", "router138 cluster138"],
    ),
    (
        ("kernel138 signal138 packet138 router138 cluster138 mirror138", 6),
        ["kernel138", "signal138", "packet138", "router138", "cluster138", "mirror138"],
    ),
    (
        ("kernel138 signal138 packet138 router138 cluster138 mirror138", 10),
        ["kernel138", "signal138", "packet138", "router138", "cluster138", "mirror138"],
    ),
    (
        ("kernel138 signal138 packet138 router138 cluster138 mirror138", 18),
        ["kernel138", "signal138", "packet138", "router138", "cluster138", "mirror138"],
    ),
    (
        ("kernel138 signal138 packet138 router138 cluster138 mirror138", 28),
        ["kernel138 signal138", "packet138 router138", "cluster138 mirror138"],
    ),
    (
        ("signal138 packet138 router138 cluster138 mirror138 filter138", 6),
        ["signal138", "packet138", "router138", "cluster138", "mirror138", "filter138"],
    ),
    (
        ("signal138 packet138 router138 cluster138 mirror138 filter138", 10),
        ["signal138", "packet138", "router138", "cluster138", "mirror138", "filter138"],
    ),
    (
        ("signal138 packet138 router138 cluster138 mirror138 filter138", 18),
        ["signal138", "packet138", "router138", "cluster138", "mirror138", "filter138"],
    ),
    (
        ("signal138 packet138 router138 cluster138 mirror138 filter138", 28),
        ["signal138 packet138", "router138 cluster138", "mirror138 filter138"],
    ),
    (
        ("packet138 router138 cluster138 mirror138 filter138 ranking138", 6),
        ["packet138", "router138", "cluster138", "mirror138", "filter138", "ranking138"],
    ),
    (
        ("packet138 router138 cluster138 mirror138 filter138 ranking138", 10),
        ["packet138", "router138", "cluster138", "mirror138", "filter138", "ranking138"],
    ),
    (
        ("packet138 router138 cluster138 mirror138 filter138 ranking138", 18),
        ["packet138", "router138", "cluster138", "mirror138", "filter138", "ranking138"],
    ),
    (
        ("packet138 router138 cluster138 mirror138 filter138 ranking138", 28),
        ["packet138 router138", "cluster138 mirror138", "filter138 ranking138"],
    ),
    (
        ("router138 cluster138 mirror138 filter138 ranking138 encoding138", 6),
        ["router138", "cluster138", "mirror138", "filter138", "ranking138", "encoding138"],
    ),
    (
        ("router138 cluster138 mirror138 filter138 ranking138 encoding138", 10),
        ["router138", "cluster138", "mirror138", "filter138", "ranking138", "encoding138"],
    ),
    (
        ("router138 cluster138 mirror138 filter138 ranking138 encoding138", 18),
        ["router138", "cluster138", "mirror138", "filter138", "ranking138", "encoding138"],
    ),
    (
        ("router138 cluster138 mirror138 filter138 ranking138 encoding138", 28),
        ["router138 cluster138", "mirror138 filter138", "ranking138 encoding138"],
    ),
    (
        ("cluster138 mirror138 filter138 ranking138 encoding138 mapping138", 6),
        ["cluster138", "mirror138", "filter138", "ranking138", "encoding138", "mapping138"],
    ),
    (
        ("cluster138 mirror138 filter138 ranking138 encoding138 mapping138", 10),
        ["cluster138", "mirror138", "filter138", "ranking138", "encoding138", "mapping138"],
    ),
    (
        ("cluster138 mirror138 filter138 ranking138 encoding138 mapping138", 18),
        ["cluster138", "mirror138", "filter138", "ranking138", "encoding138", "mapping138"],
    ),
    (
        ("cluster138 mirror138 filter138 ranking138 encoding138 mapping138", 28),
        ["cluster138 mirror138", "filter138 ranking138", "encoding138 mapping138"],
    ),
    (
        ("mirror138 filter138 ranking138 encoding138 mapping138 record138", 6),
        ["mirror138", "filter138", "ranking138", "encoding138", "mapping138", "record138"],
    ),
    (
        ("mirror138 filter138 ranking138 encoding138 mapping138 record138", 10),
        ["mirror138", "filter138", "ranking138", "encoding138", "mapping138", "record138"],
    ),
    (
        ("mirror138 filter138 ranking138 encoding138 mapping138 record138", 18),
        ["mirror138", "filter138", "ranking138", "encoding138", "mapping138", "record138"],
    ),
    (
        ("mirror138 filter138 ranking138 encoding138 mapping138 record138", 28),
        ["mirror138 filter138", "ranking138 encoding138", "mapping138 record138"],
    ),
    (
        ("filter138 ranking138 encoding138 mapping138 record138 candle138", 6),
        ["filter138", "ranking138", "encoding138", "mapping138", "record138", "candle138"],
    ),
    (
        ("filter138 ranking138 encoding138 mapping138 record138 candle138", 10),
        ["filter138", "ranking138", "encoding138", "mapping138", "record138", "candle138"],
    ),
    (
        ("filter138 ranking138 encoding138 mapping138 record138 candle138", 18),
        ["filter138", "ranking138", "encoding138", "mapping138", "record138", "candle138"],
    ),
    (
        ("filter138 ranking138 encoding138 mapping138 record138 candle138", 28),
        ["filter138 ranking138", "encoding138 mapping138", "record138 candle138"],
    ),
    (
        ("ranking138 encoding138 mapping138 record138 candle138 thread138", 6),
        ["ranking138", "encoding138", "mapping138", "record138", "candle138", "thread138"],
    ),
    (
        ("ranking138 encoding138 mapping138 record138 candle138 thread138", 10),
        ["ranking138", "encoding138", "mapping138", "record138", "candle138", "thread138"],
    ),
    (
        ("ranking138 encoding138 mapping138 record138 candle138 thread138", 18),
        ["ranking138", "encoding138", "mapping138", "record138", "candle138", "thread138"],
    ),
    (
        ("ranking138 encoding138 mapping138 record138 candle138 thread138", 28),
        ["ranking138 encoding138", "mapping138 record138", "candle138 thread138"],
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
