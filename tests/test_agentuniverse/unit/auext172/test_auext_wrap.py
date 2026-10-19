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
        ("round 172: the quick brown fox jumps over the lazy dog", 4),
        ["round", "172:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", 8),
        ["round", "172: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", 12),
        ["round 172:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", 16),
        ["round 172: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", 24),
        ["round 172: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 172: the quick brown fox jumps over the lazy dog", 32),
        ["round 172: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", 4),
        ["round", "172:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", 8),
        ["round", "172:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", 12),
        ["round 172:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", 16),
        ["round 172:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", 24),
        ["round 172: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 172: agentuniverse is a framework for multi agents", 32),
        ["round 172: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", 4),
        ["round", "172:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", 8),
        ["round", "172:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", 12),
        ["round 172:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", 16),
        ["round 172:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", 24),
        ["round 172: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 172: knowledge stored as vectors enables retrieval", 32),
        ["round 172: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 172: the processor reads the record then stops", 4),
        ["round", "172:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 172: the processor reads the record then stops", 8),
        ["round", "172: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 172: the processor reads the record then stops", 12),
        ["round 172:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 172: the processor reads the record then stops", 16),
        ["round 172: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 172: the processor reads the record then stops", 24),
        ["round 172: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 172: the processor reads the record then stops", 32),
        ["round 172: the processor reads", "the record then stops"],
    ),
    (
        ("round 172: a worker pulls the next task from the queue", 4),
        ["round", "172:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 172: a worker pulls the next task from the queue", 8),
        ["round", "172: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 172: a worker pulls the next task from the queue", 12),
        ["round 172: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 172: a worker pulls the next task from the queue", 16),
        ["round 172: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 172: a worker pulls the next task from the queue", 24),
        ["round 172: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 172: a worker pulls the next task from the queue", 32),
        ["round 172: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 172: signals travel through the network layer", 4),
        ["round", "172:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 172: signals travel through the network layer", 8),
        ["round", "172:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 172: signals travel through the network layer", 12),
        ["round 172:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 172: signals travel through the network layer", 16),
        ["round 172:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 172: signals travel through the network layer", 24),
        ["round 172: signals", "travel through the", "network layer"],
    ),
    (
        ("round 172: signals travel through the network layer", 32),
        ["round 172: signals travel", "through the network layer"],
    ),
    (
        ("round 172: the gateway routes each request by policy", 4),
        ["round", "172:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 172: the gateway routes each request by policy", 8),
        ["round", "172: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 172: the gateway routes each request by policy", 12),
        ["round 172:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 172: the gateway routes each request by policy", 16),
        ["round 172: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 172: the gateway routes each request by policy", 24),
        ["round 172: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 172: the gateway routes each request by policy", 32),
        ["round 172: the gateway routes", "each request by policy"],
    ),
    (
        ("round 172: memory grows until the buffer is full", 4),
        ["round", "172:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 172: memory grows until the buffer is full", 8),
        ["round", "172:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 172: memory grows until the buffer is full", 12),
        ["round 172:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 172: memory grows until the buffer is full", 16),
        ["round 172:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 172: memory grows until the buffer is full", 24), ["round 172: memory grows", "until the buffer is full"]),
    (("round 172: memory grows until the buffer is full", 32), ["round 172: memory grows until", "the buffer is full"]),
    (
        ("round 172: the cluster mirrors every packet twice", 4),
        ["round", "172:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 172: the cluster mirrors every packet twice", 8),
        ["round", "172: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 172: the cluster mirrors every packet twice", 12),
        ["round 172:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 172: the cluster mirrors every packet twice", 16),
        ["round 172: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 172: the cluster mirrors every packet twice", 24),
        ["round 172: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 172: the cluster mirrors every packet twice", 32),
        ["round 172: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", 4),
        ["round", "172:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", 8),
        ["round", "172:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", 12),
        ["round 172:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", 16),
        ["round 172:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", 24),
        ["round 172: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 172: ranking uses tokens learned from the corpus", 32),
        ["round 172: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 172: a long session ends when the candle dies", 4),
        ["round", "172:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 172: a long session ends when the candle dies", 8),
        ["round", "172: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 172: a long session ends when the candle dies", 12),
        ["round 172: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 172: a long session ends when the candle dies", 16),
        ["round 172: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 172: a long session ends when the candle dies", 24),
        ["round 172: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 172: a long session ends when the candle dies", 32),
        ["round 172: a long session ends", "when the candle dies"],
    ),
    (
        ("round 172: encode the prompt then map the result", 4),
        ["round", "172:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 172: encode the prompt then map the result", 8),
        ["round", "172:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 172: encode the prompt then map the result", 12),
        ["round 172:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 172: encode the prompt then map the result", 16),
        ["round 172:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 172: encode the prompt then map the result", 24),
        ["round 172: encode the", "prompt then map the", "result"],
    ),
    (("round 172: encode the prompt then map the result", 32), ["round 172: encode the prompt", "then map the result"]),
    (
        ("round 172: the kernel wakes the worker at dawn", 4),
        ["round", "172:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 172: the kernel wakes the worker at dawn", 8),
        ["round", "172: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 172: the kernel wakes the worker at dawn", 12),
        ["round 172:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 172: the kernel wakes the worker at dawn", 16), ["round 172: the", "kernel wakes the", "worker at dawn"]),
    (("round 172: the kernel wakes the worker at dawn", 24), ["round 172: the kernel", "wakes the worker at dawn"]),
    (("round 172: the kernel wakes the worker at dawn", 32), ["round 172: the kernel wakes the", "worker at dawn"]),
    (
        ("round 172: service latency drops after the patch", 4),
        ["round", "172:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 172: service latency drops after the patch", 8),
        ["round", "172:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 172: service latency drops after the patch", 12),
        ["round 172:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 172: service latency drops after the patch", 16),
        ["round 172:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 172: service latency drops after the patch", 24),
        ["round 172: service", "latency drops after the", "patch"],
    ),
    (("round 172: service latency drops after the patch", 32), ["round 172: service latency drops", "after the patch"]),
    (
        ("round 172: the library caches every vector it sees", 4),
        ["round", "172:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 172: the library caches every vector it sees", 8),
        ["round", "172: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 172: the library caches every vector it sees", 12),
        ["round 172:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 172: the library caches every vector it sees", 16),
        ["round 172: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 172: the library caches every vector it sees", 24),
        ["round 172: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 172: the library caches every vector it sees", 32),
        ["round 172: the library caches", "every vector it sees"],
    ),
    (
        ("round 172: agents argue then the debate resolves", 4),
        ["round", "172:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 172: agents argue then the debate resolves", 8),
        ["round", "172:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 172: agents argue then the debate resolves", 12),
        ["round 172:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 172: agents argue then the debate resolves", 16),
        ["round 172:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 172: agents argue then the debate resolves", 24), ["round 172: agents argue", "then the debate resolves"]),
    (("round 172: agents argue then the debate resolves", 32), ["round 172: agents argue then the", "debate resolves"]),
    (
        ("round 172: the filter keeps only strong matches", 4),
        ["round", "172:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 172: the filter keeps only strong matches", 8),
        ["round", "172: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 172: the filter keeps only strong matches", 12),
        ["round 172:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 172: the filter keeps only strong matches", 16),
        ["round 172: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 172: the filter keeps only strong matches", 24),
        ["round 172: the filter", "keeps only strong", "matches"],
    ),
    (("round 172: the filter keeps only strong matches", 32), ["round 172: the filter keeps only", "strong matches"]),
    (
        ("round 172: the model answers with a short reply", 4),
        ["round", "172:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 172: the model answers with a short reply", 8),
        ["round", "172: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 172: the model answers with a short reply", 12),
        ["round 172:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 172: the model answers with a short reply", 16),
        ["round 172: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 172: the model answers with a short reply", 24),
        ["round 172: the model", "answers with a short", "reply"],
    ),
    (("round 172: the model answers with a short reply", 32), ["round 172: the model answers", "with a short reply"]),
    (
        ("round 172: the recorder stores the reasoning trace", 4),
        ["round", "172:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 172: the recorder stores the reasoning trace", 8),
        ["round", "172: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 172: the recorder stores the reasoning trace", 12),
        ["round 172:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 172: the recorder stores the reasoning trace", 16),
        ["round 172: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 172: the recorder stores the reasoning trace", 24),
        ["round 172: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 172: the recorder stores the reasoning trace", 32),
        ["round 172: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 172: the angel watches the processor run", 4),
        ["round", "172:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 172: the angel watches the processor run", 8),
        ["round", "172: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 172: the angel watches the processor run", 12),
        ["round 172:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 172: the angel watches the processor run", 16),
        ["round 172: the", "angel watches", "the processor", "run"],
    ),
    (("round 172: the angel watches the processor run", 24), ["round 172: the angel", "watches the processor", "run"]),
    (("round 172: the angel watches the processor run", 32), ["round 172: the angel watches the", "processor run"]),
    (
        ("round 172: angle of the vector decides the match", 4),
        ["round", "172:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 172: angle of the vector decides the match", 8),
        ["round", "172:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 172: angle of the vector decides the match", 12),
        ["round 172:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 172: angle of the vector decides the match", 16),
        ["round 172: angle", "of the vector", "decides the", "match"],
    ),
    (("round 172: angle of the vector decides the match", 24), ["round 172: angle of the", "vector decides the match"]),
    (("round 172: angle of the vector decides the match", 32), ["round 172: angle of the vector", "decides the match"]),
    (
        ("round 172: the candle burns twice as long at night", 4),
        ["round", "172:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 172: the candle burns twice as long at night", 8),
        ["round", "172: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 172: the candle burns twice as long at night", 12),
        ["round 172:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 172: the candle burns twice as long at night", 16),
        ["round 172: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 172: the candle burns twice as long at night", 24),
        ["round 172: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 172: the candle burns twice as long at night", 32),
        ["round 172: the candle burns", "twice as long at night"],
    ),
    (
        ("round 172: a mirror of the universe in one line", 4),
        ["round", "172:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 172: a mirror of the universe in one line", 8),
        ["round", "172: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 172: a mirror of the universe in one line", 12),
        ["round 172: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 172: a mirror of the universe in one line", 16),
        ["round 172: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 172: a mirror of the universe in one line", 24), ["round 172: a mirror of", "the universe in one line"]),
    (("round 172: a mirror of the universe in one line", 32), ["round 172: a mirror of the", "universe in one line"]),
    (
        ("round 172: the queue drains before the storm", 4),
        ["round", "172:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 172: the queue drains before the storm", 8),
        ["round", "172: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 172: the queue drains before the storm", 12),
        ["round 172:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 172: the queue drains before the storm", 16), ["round 172: the", "queue drains", "before the storm"]),
    (("round 172: the queue drains before the storm", 24), ["round 172: the queue", "drains before the storm"]),
    (("round 172: the queue drains before the storm", 32), ["round 172: the queue drains", "before the storm"]),
    (
        ("kitten172 sitting172 agent172 angle172 universe172 memory172", 6),
        ["kitten172", "sitting172", "agent172", "angle172", "universe172", "memory172"],
    ),
    (
        ("kitten172 sitting172 agent172 angle172 universe172 memory172", 10),
        ["kitten172", "sitting172", "agent172", "angle172", "universe172", "memory172"],
    ),
    (
        ("kitten172 sitting172 agent172 angle172 universe172 memory172", 18),
        ["kitten172", "sitting172", "agent172 angle172", "universe172", "memory172"],
    ),
    (
        ("kitten172 sitting172 agent172 angle172 universe172 memory172", 28),
        ["kitten172 sitting172", "agent172 angle172", "universe172 memory172"],
    ),
    (
        ("sitting172 agent172 angle172 universe172 memory172 stream172", 6),
        ["sitting172", "agent172", "angle172", "universe172", "memory172", "stream172"],
    ),
    (
        ("sitting172 agent172 angle172 universe172 memory172 stream172", 10),
        ["sitting172", "agent172", "angle172", "universe172", "memory172", "stream172"],
    ),
    (
        ("sitting172 agent172 angle172 universe172 memory172 stream172", 18),
        ["sitting172", "agent172 angle172", "universe172", "memory172", "stream172"],
    ),
    (
        ("sitting172 agent172 angle172 universe172 memory172 stream172", 28),
        ["sitting172 agent172 angle172", "universe172 memory172", "stream172"],
    ),
    (
        ("agent172 angle172 universe172 memory172 stream172 context172", 6),
        ["agent172", "angle172", "universe172", "memory172", "stream172", "context172"],
    ),
    (
        ("agent172 angle172 universe172 memory172 stream172 context172", 10),
        ["agent172", "angle172", "universe172", "memory172", "stream172", "context172"],
    ),
    (
        ("agent172 angle172 universe172 memory172 stream172 context172", 18),
        ["agent172 angle172", "universe172", "memory172", "stream172", "context172"],
    ),
    (
        ("agent172 angle172 universe172 memory172 stream172 context172", 28),
        ["agent172 angle172", "universe172 memory172", "stream172 context172"],
    ),
    (
        ("angle172 universe172 memory172 stream172 context172 knowledge172", 6),
        ["angle172", "universe172", "memory172", "stream172", "context172", "knowledge172"],
    ),
    (
        ("angle172 universe172 memory172 stream172 context172 knowledge172", 10),
        ["angle172", "universe172", "memory172", "stream172", "context172", "knowledge172"],
    ),
    (
        ("angle172 universe172 memory172 stream172 context172 knowledge172", 18),
        ["angle172", "universe172", "memory172", "stream172", "context172", "knowledge172"],
    ),
    (
        ("angle172 universe172 memory172 stream172 context172 knowledge172", 28),
        ["angle172 universe172", "memory172 stream172", "context172 knowledge172"],
    ),
    (
        ("universe172 memory172 stream172 context172 knowledge172 vector172", 6),
        ["universe172", "memory172", "stream172", "context172", "knowledge172", "vector172"],
    ),
    (
        ("universe172 memory172 stream172 context172 knowledge172 vector172", 10),
        ["universe172", "memory172", "stream172", "context172", "knowledge172", "vector172"],
    ),
    (
        ("universe172 memory172 stream172 context172 knowledge172 vector172", 18),
        ["universe172", "memory172", "stream172", "context172", "knowledge172", "vector172"],
    ),
    (
        ("universe172 memory172 stream172 context172 knowledge172 vector172", 28),
        ["universe172 memory172", "stream172 context172", "knowledge172 vector172"],
    ),
    (
        ("memory172 stream172 context172 knowledge172 vector172 processor172", 6),
        ["memory172", "stream172", "context172", "knowledge172", "vector172", "processor172"],
    ),
    (
        ("memory172 stream172 context172 knowledge172 vector172 processor172", 10),
        ["memory172", "stream172", "context172", "knowledge172", "vector172", "processor172"],
    ),
    (
        ("memory172 stream172 context172 knowledge172 vector172 processor172", 18),
        ["memory172", "stream172", "context172", "knowledge172", "vector172", "processor172"],
    ),
    (
        ("memory172 stream172 context172 knowledge172 vector172 processor172", 28),
        ["memory172 stream172", "context172 knowledge172", "vector172 processor172"],
    ),
    (
        ("stream172 context172 knowledge172 vector172 processor172 reasoning172", 6),
        ["stream172", "context172", "knowledge172", "vector172", "processor172", "reasoning172"],
    ),
    (
        ("stream172 context172 knowledge172 vector172 processor172 reasoning172", 10),
        ["stream172", "context172", "knowledge172", "vector172", "processor172", "reasoning172"],
    ),
    (
        ("stream172 context172 knowledge172 vector172 processor172 reasoning172", 18),
        ["stream172", "context172", "knowledge172", "vector172", "processor172", "reasoning172"],
    ),
    (
        ("stream172 context172 knowledge172 vector172 processor172 reasoning172", 28),
        ["stream172 context172", "knowledge172 vector172", "processor172 reasoning172"],
    ),
    (
        ("context172 knowledge172 vector172 processor172 reasoning172 machine172", 6),
        ["context172", "knowledge172", "vector172", "processor172", "reasoning172", "machine172"],
    ),
    (
        ("context172 knowledge172 vector172 processor172 reasoning172 machine172", 10),
        ["context172", "knowledge172", "vector172", "processor172", "reasoning172", "machine172"],
    ),
    (
        ("context172 knowledge172 vector172 processor172 reasoning172 machine172", 18),
        ["context172", "knowledge172", "vector172", "processor172", "reasoning172", "machine172"],
    ),
    (
        ("context172 knowledge172 vector172 processor172 reasoning172 machine172", 28),
        ["context172 knowledge172", "vector172 processor172", "reasoning172 machine172"],
    ),
    (
        ("knowledge172 vector172 processor172 reasoning172 machine172 learning172", 6),
        ["knowledge172", "vector172", "processor172", "reasoning172", "machine172", "learning172"],
    ),
    (
        ("knowledge172 vector172 processor172 reasoning172 machine172 learning172", 10),
        ["knowledge172", "vector172", "processor172", "reasoning172", "machine172", "learning172"],
    ),
    (
        ("knowledge172 vector172 processor172 reasoning172 machine172 learning172", 18),
        ["knowledge172", "vector172", "processor172", "reasoning172", "machine172", "learning172"],
    ),
    (
        ("knowledge172 vector172 processor172 reasoning172 machine172 learning172", 28),
        ["knowledge172 vector172", "processor172 reasoning172", "machine172 learning172"],
    ),
    (
        ("vector172 processor172 reasoning172 machine172 learning172 model172", 6),
        ["vector172", "processor172", "reasoning172", "machine172", "learning172", "model172"],
    ),
    (
        ("vector172 processor172 reasoning172 machine172 learning172 model172", 10),
        ["vector172", "processor172", "reasoning172", "machine172", "learning172", "model172"],
    ),
    (
        ("vector172 processor172 reasoning172 machine172 learning172 model172", 18),
        ["vector172", "processor172", "reasoning172", "machine172", "learning172", "model172"],
    ),
    (
        ("vector172 processor172 reasoning172 machine172 learning172 model172", 28),
        ["vector172 processor172", "reasoning172 machine172", "learning172 model172"],
    ),
    (
        ("processor172 reasoning172 machine172 learning172 model172 token172", 6),
        ["processor172", "reasoning172", "machine172", "learning172", "model172", "token172"],
    ),
    (
        ("processor172 reasoning172 machine172 learning172 model172 token172", 10),
        ["processor172", "reasoning172", "machine172", "learning172", "model172", "token172"],
    ),
    (
        ("processor172 reasoning172 machine172 learning172 model172 token172", 18),
        ["processor172", "reasoning172", "machine172", "learning172", "model172 token172"],
    ),
    (
        ("processor172 reasoning172 machine172 learning172 model172 token172", 28),
        ["processor172 reasoning172", "machine172 learning172", "model172 token172"],
    ),
    (
        ("reasoning172 machine172 learning172 model172 token172 prompt172", 6),
        ["reasoning172", "machine172", "learning172", "model172", "token172", "prompt172"],
    ),
    (
        ("reasoning172 machine172 learning172 model172 token172 prompt172", 10),
        ["reasoning172", "machine172", "learning172", "model172", "token172", "prompt172"],
    ),
    (
        ("reasoning172 machine172 learning172 model172 token172 prompt172", 18),
        ["reasoning172", "machine172", "learning172", "model172 token172", "prompt172"],
    ),
    (
        ("reasoning172 machine172 learning172 model172 token172 prompt172", 28),
        ["reasoning172 machine172", "learning172 model172", "token172 prompt172"],
    ),
    (
        ("machine172 learning172 model172 token172 prompt172 session172", 6),
        ["machine172", "learning172", "model172", "token172", "prompt172", "session172"],
    ),
    (
        ("machine172 learning172 model172 token172 prompt172 session172", 10),
        ["machine172", "learning172", "model172", "token172", "prompt172", "session172"],
    ),
    (
        ("machine172 learning172 model172 token172 prompt172 session172", 18),
        ["machine172", "learning172", "model172 token172", "prompt172", "session172"],
    ),
    (
        ("machine172 learning172 model172 token172 prompt172 session172", 28),
        ["machine172 learning172", "model172 token172 prompt172", "session172"],
    ),
    (
        ("learning172 model172 token172 prompt172 session172 library172", 6),
        ["learning172", "model172", "token172", "prompt172", "session172", "library172"],
    ),
    (
        ("learning172 model172 token172 prompt172 session172 library172", 10),
        ["learning172", "model172", "token172", "prompt172", "session172", "library172"],
    ),
    (
        ("learning172 model172 token172 prompt172 session172 library172", 18),
        ["learning172", "model172 token172", "prompt172", "session172", "library172"],
    ),
    (
        ("learning172 model172 token172 prompt172 session172 library172", 28),
        ["learning172 model172", "token172 prompt172", "session172 library172"],
    ),
    (
        ("model172 token172 prompt172 session172 library172 service172", 6),
        ["model172", "token172", "prompt172", "session172", "library172", "service172"],
    ),
    (
        ("model172 token172 prompt172 session172 library172 service172", 10),
        ["model172", "token172", "prompt172", "session172", "library172", "service172"],
    ),
    (
        ("model172 token172 prompt172 session172 library172 service172", 18),
        ["model172 token172", "prompt172", "session172", "library172", "service172"],
    ),
    (
        ("model172 token172 prompt172 session172 library172 service172", 28),
        ["model172 token172 prompt172", "session172 library172", "service172"],
    ),
    (
        ("token172 prompt172 session172 library172 service172 gateway172", 6),
        ["token172", "prompt172", "session172", "library172", "service172", "gateway172"],
    ),
    (
        ("token172 prompt172 session172 library172 service172 gateway172", 10),
        ["token172", "prompt172", "session172", "library172", "service172", "gateway172"],
    ),
    (
        ("token172 prompt172 session172 library172 service172 gateway172", 18),
        ["token172 prompt172", "session172", "library172", "service172", "gateway172"],
    ),
    (
        ("token172 prompt172 session172 library172 service172 gateway172", 28),
        ["token172 prompt172", "session172 library172", "service172 gateway172"],
    ),
    (
        ("prompt172 session172 library172 service172 gateway172 storage172", 6),
        ["prompt172", "session172", "library172", "service172", "gateway172", "storage172"],
    ),
    (
        ("prompt172 session172 library172 service172 gateway172 storage172", 10),
        ["prompt172", "session172", "library172", "service172", "gateway172", "storage172"],
    ),
    (
        ("prompt172 session172 library172 service172 gateway172 storage172", 18),
        ["prompt172", "session172", "library172", "service172", "gateway172", "storage172"],
    ),
    (
        ("prompt172 session172 library172 service172 gateway172 storage172", 28),
        ["prompt172 session172", "library172 service172", "gateway172 storage172"],
    ),
    (
        ("session172 library172 service172 gateway172 storage172 network172", 6),
        ["session172", "library172", "service172", "gateway172", "storage172", "network172"],
    ),
    (
        ("session172 library172 service172 gateway172 storage172 network172", 10),
        ["session172", "library172", "service172", "gateway172", "storage172", "network172"],
    ),
    (
        ("session172 library172 service172 gateway172 storage172 network172", 18),
        ["session172", "library172", "service172", "gateway172", "storage172", "network172"],
    ),
    (
        ("session172 library172 service172 gateway172 storage172 network172", 28),
        ["session172 library172", "service172 gateway172", "storage172 network172"],
    ),
    (
        ("library172 service172 gateway172 storage172 network172 latency172", 6),
        ["library172", "service172", "gateway172", "storage172", "network172", "latency172"],
    ),
    (
        ("library172 service172 gateway172 storage172 network172 latency172", 10),
        ["library172", "service172", "gateway172", "storage172", "network172", "latency172"],
    ),
    (
        ("library172 service172 gateway172 storage172 network172 latency172", 18),
        ["library172", "service172", "gateway172", "storage172", "network172", "latency172"],
    ),
    (
        ("library172 service172 gateway172 storage172 network172 latency172", 28),
        ["library172 service172", "gateway172 storage172", "network172 latency172"],
    ),
    (
        ("service172 gateway172 storage172 network172 latency172 buffer172", 6),
        ["service172", "gateway172", "storage172", "network172", "latency172", "buffer172"],
    ),
    (
        ("service172 gateway172 storage172 network172 latency172 buffer172", 10),
        ["service172", "gateway172", "storage172", "network172", "latency172", "buffer172"],
    ),
    (
        ("service172 gateway172 storage172 network172 latency172 buffer172", 18),
        ["service172", "gateway172", "storage172", "network172", "latency172", "buffer172"],
    ),
    (
        ("service172 gateway172 storage172 network172 latency172 buffer172", 28),
        ["service172 gateway172", "storage172 network172", "latency172 buffer172"],
    ),
    (
        ("gateway172 storage172 network172 latency172 buffer172 queue172", 6),
        ["gateway172", "storage172", "network172", "latency172", "buffer172", "queue172"],
    ),
    (
        ("gateway172 storage172 network172 latency172 buffer172 queue172", 10),
        ["gateway172", "storage172", "network172", "latency172", "buffer172", "queue172"],
    ),
    (
        ("gateway172 storage172 network172 latency172 buffer172 queue172", 18),
        ["gateway172", "storage172", "network172", "latency172", "buffer172 queue172"],
    ),
    (
        ("gateway172 storage172 network172 latency172 buffer172 queue172", 28),
        ["gateway172 storage172", "network172 latency172", "buffer172 queue172"],
    ),
    (
        ("storage172 network172 latency172 buffer172 queue172 worker172", 6),
        ["storage172", "network172", "latency172", "buffer172", "queue172", "worker172"],
    ),
    (
        ("storage172 network172 latency172 buffer172 queue172 worker172", 10),
        ["storage172", "network172", "latency172", "buffer172", "queue172", "worker172"],
    ),
    (
        ("storage172 network172 latency172 buffer172 queue172 worker172", 18),
        ["storage172", "network172", "latency172", "buffer172 queue172", "worker172"],
    ),
    (
        ("storage172 network172 latency172 buffer172 queue172 worker172", 28),
        ["storage172 network172", "latency172 buffer172", "queue172 worker172"],
    ),
    (
        ("network172 latency172 buffer172 queue172 worker172 kernel172", 6),
        ["network172", "latency172", "buffer172", "queue172", "worker172", "kernel172"],
    ),
    (
        ("network172 latency172 buffer172 queue172 worker172 kernel172", 10),
        ["network172", "latency172", "buffer172", "queue172", "worker172", "kernel172"],
    ),
    (
        ("network172 latency172 buffer172 queue172 worker172 kernel172", 18),
        ["network172", "latency172", "buffer172 queue172", "worker172", "kernel172"],
    ),
    (
        ("network172 latency172 buffer172 queue172 worker172 kernel172", 28),
        ["network172 latency172", "buffer172 queue172 worker172", "kernel172"],
    ),
    (
        ("latency172 buffer172 queue172 worker172 kernel172 signal172", 6),
        ["latency172", "buffer172", "queue172", "worker172", "kernel172", "signal172"],
    ),
    (
        ("latency172 buffer172 queue172 worker172 kernel172 signal172", 10),
        ["latency172", "buffer172", "queue172", "worker172", "kernel172", "signal172"],
    ),
    (
        ("latency172 buffer172 queue172 worker172 kernel172 signal172", 18),
        ["latency172", "buffer172 queue172", "worker172", "kernel172", "signal172"],
    ),
    (
        ("latency172 buffer172 queue172 worker172 kernel172 signal172", 28),
        ["latency172 buffer172", "queue172 worker172 kernel172", "signal172"],
    ),
    (
        ("buffer172 queue172 worker172 kernel172 signal172 packet172", 6),
        ["buffer172", "queue172", "worker172", "kernel172", "signal172", "packet172"],
    ),
    (
        ("buffer172 queue172 worker172 kernel172 signal172 packet172", 10),
        ["buffer172", "queue172", "worker172", "kernel172", "signal172", "packet172"],
    ),
    (
        ("buffer172 queue172 worker172 kernel172 signal172 packet172", 18),
        ["buffer172 queue172", "worker172", "kernel172", "signal172", "packet172"],
    ),
    (
        ("buffer172 queue172 worker172 kernel172 signal172 packet172", 28),
        ["buffer172 queue172 worker172", "kernel172 signal172", "packet172"],
    ),
    (
        ("queue172 worker172 kernel172 signal172 packet172 router172", 6),
        ["queue172", "worker172", "kernel172", "signal172", "packet172", "router172"],
    ),
    (
        ("queue172 worker172 kernel172 signal172 packet172 router172", 10),
        ["queue172", "worker172", "kernel172", "signal172", "packet172", "router172"],
    ),
    (
        ("queue172 worker172 kernel172 signal172 packet172 router172", 18),
        ["queue172 worker172", "kernel172", "signal172", "packet172", "router172"],
    ),
    (
        ("queue172 worker172 kernel172 signal172 packet172 router172", 28),
        ["queue172 worker172 kernel172", "signal172 packet172", "router172"],
    ),
    (
        ("worker172 kernel172 signal172 packet172 router172 cluster172", 6),
        ["worker172", "kernel172", "signal172", "packet172", "router172", "cluster172"],
    ),
    (
        ("worker172 kernel172 signal172 packet172 router172 cluster172", 10),
        ["worker172", "kernel172", "signal172", "packet172", "router172", "cluster172"],
    ),
    (
        ("worker172 kernel172 signal172 packet172 router172 cluster172", 18),
        ["worker172", "kernel172", "signal172", "packet172", "router172", "cluster172"],
    ),
    (
        ("worker172 kernel172 signal172 packet172 router172 cluster172", 28),
        ["worker172 kernel172", "signal172 packet172", "router172 cluster172"],
    ),
    (
        ("kernel172 signal172 packet172 router172 cluster172 mirror172", 6),
        ["kernel172", "signal172", "packet172", "router172", "cluster172", "mirror172"],
    ),
    (
        ("kernel172 signal172 packet172 router172 cluster172 mirror172", 10),
        ["kernel172", "signal172", "packet172", "router172", "cluster172", "mirror172"],
    ),
    (
        ("kernel172 signal172 packet172 router172 cluster172 mirror172", 18),
        ["kernel172", "signal172", "packet172", "router172", "cluster172", "mirror172"],
    ),
    (
        ("kernel172 signal172 packet172 router172 cluster172 mirror172", 28),
        ["kernel172 signal172", "packet172 router172", "cluster172 mirror172"],
    ),
    (
        ("signal172 packet172 router172 cluster172 mirror172 filter172", 6),
        ["signal172", "packet172", "router172", "cluster172", "mirror172", "filter172"],
    ),
    (
        ("signal172 packet172 router172 cluster172 mirror172 filter172", 10),
        ["signal172", "packet172", "router172", "cluster172", "mirror172", "filter172"],
    ),
    (
        ("signal172 packet172 router172 cluster172 mirror172 filter172", 18),
        ["signal172", "packet172", "router172", "cluster172", "mirror172", "filter172"],
    ),
    (
        ("signal172 packet172 router172 cluster172 mirror172 filter172", 28),
        ["signal172 packet172", "router172 cluster172", "mirror172 filter172"],
    ),
    (
        ("packet172 router172 cluster172 mirror172 filter172 ranking172", 6),
        ["packet172", "router172", "cluster172", "mirror172", "filter172", "ranking172"],
    ),
    (
        ("packet172 router172 cluster172 mirror172 filter172 ranking172", 10),
        ["packet172", "router172", "cluster172", "mirror172", "filter172", "ranking172"],
    ),
    (
        ("packet172 router172 cluster172 mirror172 filter172 ranking172", 18),
        ["packet172", "router172", "cluster172", "mirror172", "filter172", "ranking172"],
    ),
    (
        ("packet172 router172 cluster172 mirror172 filter172 ranking172", 28),
        ["packet172 router172", "cluster172 mirror172", "filter172 ranking172"],
    ),
    (
        ("router172 cluster172 mirror172 filter172 ranking172 encoding172", 6),
        ["router172", "cluster172", "mirror172", "filter172", "ranking172", "encoding172"],
    ),
    (
        ("router172 cluster172 mirror172 filter172 ranking172 encoding172", 10),
        ["router172", "cluster172", "mirror172", "filter172", "ranking172", "encoding172"],
    ),
    (
        ("router172 cluster172 mirror172 filter172 ranking172 encoding172", 18),
        ["router172", "cluster172", "mirror172", "filter172", "ranking172", "encoding172"],
    ),
    (
        ("router172 cluster172 mirror172 filter172 ranking172 encoding172", 28),
        ["router172 cluster172", "mirror172 filter172", "ranking172 encoding172"],
    ),
    (
        ("cluster172 mirror172 filter172 ranking172 encoding172 mapping172", 6),
        ["cluster172", "mirror172", "filter172", "ranking172", "encoding172", "mapping172"],
    ),
    (
        ("cluster172 mirror172 filter172 ranking172 encoding172 mapping172", 10),
        ["cluster172", "mirror172", "filter172", "ranking172", "encoding172", "mapping172"],
    ),
    (
        ("cluster172 mirror172 filter172 ranking172 encoding172 mapping172", 18),
        ["cluster172", "mirror172", "filter172", "ranking172", "encoding172", "mapping172"],
    ),
    (
        ("cluster172 mirror172 filter172 ranking172 encoding172 mapping172", 28),
        ["cluster172 mirror172", "filter172 ranking172", "encoding172 mapping172"],
    ),
    (
        ("mirror172 filter172 ranking172 encoding172 mapping172 record172", 6),
        ["mirror172", "filter172", "ranking172", "encoding172", "mapping172", "record172"],
    ),
    (
        ("mirror172 filter172 ranking172 encoding172 mapping172 record172", 10),
        ["mirror172", "filter172", "ranking172", "encoding172", "mapping172", "record172"],
    ),
    (
        ("mirror172 filter172 ranking172 encoding172 mapping172 record172", 18),
        ["mirror172", "filter172", "ranking172", "encoding172", "mapping172", "record172"],
    ),
    (
        ("mirror172 filter172 ranking172 encoding172 mapping172 record172", 28),
        ["mirror172 filter172", "ranking172 encoding172", "mapping172 record172"],
    ),
    (
        ("filter172 ranking172 encoding172 mapping172 record172 candle172", 6),
        ["filter172", "ranking172", "encoding172", "mapping172", "record172", "candle172"],
    ),
    (
        ("filter172 ranking172 encoding172 mapping172 record172 candle172", 10),
        ["filter172", "ranking172", "encoding172", "mapping172", "record172", "candle172"],
    ),
    (
        ("filter172 ranking172 encoding172 mapping172 record172 candle172", 18),
        ["filter172", "ranking172", "encoding172", "mapping172", "record172", "candle172"],
    ),
    (
        ("filter172 ranking172 encoding172 mapping172 record172 candle172", 28),
        ["filter172 ranking172", "encoding172 mapping172", "record172 candle172"],
    ),
    (
        ("ranking172 encoding172 mapping172 record172 candle172 thread172", 6),
        ["ranking172", "encoding172", "mapping172", "record172", "candle172", "thread172"],
    ),
    (
        ("ranking172 encoding172 mapping172 record172 candle172 thread172", 10),
        ["ranking172", "encoding172", "mapping172", "record172", "candle172", "thread172"],
    ),
    (
        ("ranking172 encoding172 mapping172 record172 candle172 thread172", 18),
        ["ranking172", "encoding172", "mapping172", "record172", "candle172", "thread172"],
    ),
    (
        ("ranking172 encoding172 mapping172 record172 candle172 thread172", 28),
        ["ranking172 encoding172", "mapping172 record172", "candle172 thread172"],
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
