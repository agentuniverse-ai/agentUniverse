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
        ("round 54: the quick brown fox jumps over the lazy dog", 4),
        ["round", "54:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 54: the quick brown fox jumps over the lazy dog", 8),
        ["round", "54: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 54: the quick brown fox jumps over the lazy dog", 12),
        ["round 54:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 54: the quick brown fox jumps over the lazy dog", 16),
        ["round 54: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 54: the quick brown fox jumps over the lazy dog", 24),
        ["round 54: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 54: the quick brown fox jumps over the lazy dog", 32),
        ["round 54: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 54: agentuniverse is a framework for multi agents", 4),
        ["round", "54:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 54: agentuniverse is a framework for multi agents", 8),
        ["round", "54:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 54: agentuniverse is a framework for multi agents", 12),
        ["round 54:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 54: agentuniverse is a framework for multi agents", 16),
        ["round 54:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 54: agentuniverse is a framework for multi agents", 24),
        ["round 54: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 54: agentuniverse is a framework for multi agents", 32),
        ["round 54: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 54: knowledge stored as vectors enables retrieval", 4),
        ["round", "54:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 54: knowledge stored as vectors enables retrieval", 8),
        ["round", "54:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 54: knowledge stored as vectors enables retrieval", 12),
        ["round 54:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 54: knowledge stored as vectors enables retrieval", 16),
        ["round 54:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 54: knowledge stored as vectors enables retrieval", 24),
        ["round 54: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 54: knowledge stored as vectors enables retrieval", 32),
        ["round 54: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 54: the processor reads the record then stops", 4),
        ["round", "54:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 54: the processor reads the record then stops", 8),
        ["round", "54: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 54: the processor reads the record then stops", 12),
        ["round 54:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 54: the processor reads the record then stops", 16),
        ["round 54: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 54: the processor reads the record then stops", 24),
        ["round 54: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 54: the processor reads the record then stops", 32),
        ["round 54: the processor reads", "the record then stops"],
    ),
    (
        ("round 54: a worker pulls the next task from the queue", 4),
        ["round", "54:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 54: a worker pulls the next task from the queue", 8),
        ["round", "54: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 54: a worker pulls the next task from the queue", 12),
        ["round 54: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 54: a worker pulls the next task from the queue", 16),
        ["round 54: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 54: a worker pulls the next task from the queue", 24),
        ["round 54: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 54: a worker pulls the next task from the queue", 32),
        ["round 54: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 54: signals travel through the network layer", 4),
        ["round", "54:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 54: signals travel through the network layer", 8),
        ["round", "54:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 54: signals travel through the network layer", 12),
        ["round 54:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 54: signals travel through the network layer", 16),
        ["round 54:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 54: signals travel through the network layer", 24),
        ["round 54: signals travel", "through the network", "layer"],
    ),
    (
        ("round 54: signals travel through the network layer", 32),
        ["round 54: signals travel through", "the network layer"],
    ),
    (
        ("round 54: the gateway routes each request by policy", 4),
        ["round", "54:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 54: the gateway routes each request by policy", 8),
        ["round", "54: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 54: the gateway routes each request by policy", 12),
        ["round 54:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 54: the gateway routes each request by policy", 16),
        ["round 54: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 54: the gateway routes each request by policy", 24),
        ["round 54: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 54: the gateway routes each request by policy", 32),
        ["round 54: the gateway routes", "each request by policy"],
    ),
    (
        ("round 54: memory grows until the buffer is full", 4),
        ["round", "54:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 54: memory grows until the buffer is full", 8),
        ["round", "54:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 54: memory grows until the buffer is full", 12),
        ["round 54:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 54: memory grows until the buffer is full", 16),
        ["round 54: memory", "grows until the", "buffer is full"],
    ),
    (("round 54: memory grows until the buffer is full", 24), ["round 54: memory grows", "until the buffer is full"]),
    (("round 54: memory grows until the buffer is full", 32), ["round 54: memory grows until the", "buffer is full"]),
    (
        ("round 54: the cluster mirrors every packet twice", 4),
        ["round", "54:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 54: the cluster mirrors every packet twice", 8),
        ["round", "54: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 54: the cluster mirrors every packet twice", 12),
        ["round 54:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 54: the cluster mirrors every packet twice", 16),
        ["round 54: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 54: the cluster mirrors every packet twice", 24),
        ["round 54: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 54: the cluster mirrors every packet twice", 32), ["round 54: the cluster mirrors", "every packet twice"]),
    (
        ("round 54: ranking uses tokens learned from the corpus", 4),
        ["round", "54:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 54: ranking uses tokens learned from the corpus", 8),
        ["round", "54:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 54: ranking uses tokens learned from the corpus", 12),
        ["round 54:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 54: ranking uses tokens learned from the corpus", 16),
        ["round 54:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 54: ranking uses tokens learned from the corpus", 24),
        ["round 54: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 54: ranking uses tokens learned from the corpus", 32),
        ["round 54: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 54: a long session ends when the candle dies", 4),
        ["round", "54:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 54: a long session ends when the candle dies", 8),
        ["round", "54: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 54: a long session ends when the candle dies", 12),
        ["round 54: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 54: a long session ends when the candle dies", 16),
        ["round 54: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 54: a long session ends when the candle dies", 24),
        ["round 54: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 54: a long session ends when the candle dies", 32),
        ["round 54: a long session ends", "when the candle dies"],
    ),
    (
        ("round 54: encode the prompt then map the result", 4),
        ["round", "54:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 54: encode the prompt then map the result", 8),
        ["round", "54:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 54: encode the prompt then map the result", 12),
        ["round 54:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 54: encode the prompt then map the result", 16),
        ["round 54: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 54: encode the prompt then map the result", 24),
        ["round 54: encode the", "prompt then map the", "result"],
    ),
    (("round 54: encode the prompt then map the result", 32), ["round 54: encode the prompt then", "map the result"]),
    (
        ("round 54: the kernel wakes the worker at dawn", 4),
        ["round", "54:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 54: the kernel wakes the worker at dawn", 8),
        ["round", "54: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 54: the kernel wakes the worker at dawn", 12),
        ["round 54:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 54: the kernel wakes the worker at dawn", 16), ["round 54: the", "kernel wakes the", "worker at dawn"]),
    (("round 54: the kernel wakes the worker at dawn", 24), ["round 54: the kernel", "wakes the worker at dawn"]),
    (("round 54: the kernel wakes the worker at dawn", 32), ["round 54: the kernel wakes the", "worker at dawn"]),
    (
        ("round 54: service latency drops after the patch", 4),
        ["round", "54:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 54: service latency drops after the patch", 8),
        ["round", "54:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 54: service latency drops after the patch", 12),
        ["round 54:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 54: service latency drops after the patch", 16),
        ["round 54:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 54: service latency drops after the patch", 24),
        ["round 54: service", "latency drops after the", "patch"],
    ),
    (("round 54: service latency drops after the patch", 32), ["round 54: service latency drops", "after the patch"]),
    (
        ("round 54: the library caches every vector it sees", 4),
        ["round", "54:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 54: the library caches every vector it sees", 8),
        ["round", "54: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 54: the library caches every vector it sees", 12),
        ["round 54:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 54: the library caches every vector it sees", 16),
        ["round 54: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 54: the library caches every vector it sees", 24),
        ["round 54: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 54: the library caches every vector it sees", 32),
        ["round 54: the library caches", "every vector it sees"],
    ),
    (
        ("round 54: agents argue then the debate resolves", 4),
        ["round", "54:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 54: agents argue then the debate resolves", 8),
        ["round", "54:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 54: agents argue then the debate resolves", 12),
        ["round 54:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 54: agents argue then the debate resolves", 16),
        ["round 54: agents", "argue then the", "debate resolves"],
    ),
    (("round 54: agents argue then the debate resolves", 24), ["round 54: agents argue", "then the debate resolves"]),
    (("round 54: agents argue then the debate resolves", 32), ["round 54: agents argue then the", "debate resolves"]),
    (
        ("round 54: the filter keeps only strong matches", 4),
        ["round", "54:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 54: the filter keeps only strong matches", 8),
        ["round", "54: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 54: the filter keeps only strong matches", 12),
        ["round 54:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 54: the filter keeps only strong matches", 16),
        ["round 54: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 54: the filter keeps only strong matches", 24), ["round 54: the filter", "keeps only strong", "matches"]),
    (("round 54: the filter keeps only strong matches", 32), ["round 54: the filter keeps only", "strong matches"]),
    (
        ("round 54: the model answers with a short reply", 4),
        ["round", "54:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 54: the model answers with a short reply", 8),
        ["round", "54: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 54: the model answers with a short reply", 12),
        ["round 54:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 54: the model answers with a short reply", 16),
        ["round 54: the", "model answers", "with a short", "reply"],
    ),
    (("round 54: the model answers with a short reply", 24), ["round 54: the model", "answers with a short", "reply"]),
    (("round 54: the model answers with a short reply", 32), ["round 54: the model answers with", "a short reply"]),
    (
        ("round 54: the recorder stores the reasoning trace", 4),
        ["round", "54:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 54: the recorder stores the reasoning trace", 8),
        ["round", "54: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 54: the recorder stores the reasoning trace", 12),
        ["round 54:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 54: the recorder stores the reasoning trace", 16),
        ["round 54: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 54: the recorder stores the reasoning trace", 24),
        ["round 54: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 54: the recorder stores the reasoning trace", 32),
        ["round 54: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 54: the angel watches the processor run", 4),
        ["round", "54:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 54: the angel watches the processor run", 8),
        ["round", "54: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 54: the angel watches the processor run", 12),
        ["round 54:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 54: the angel watches the processor run", 16), ["round 54: the", "angel watches", "the processor", "run"]),
    (("round 54: the angel watches the processor run", 24), ["round 54: the angel", "watches the processor", "run"]),
    (("round 54: the angel watches the processor run", 32), ["round 54: the angel watches the", "processor run"]),
    (
        ("round 54: angle of the vector decides the match", 4),
        ["round", "54:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 54: angle of the vector decides the match", 8),
        ["round", "54:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 54: angle of the vector decides the match", 12),
        ["round 54:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 54: angle of the vector decides the match", 16),
        ["round 54: angle", "of the vector", "decides the", "match"],
    ),
    (("round 54: angle of the vector decides the match", 24), ["round 54: angle of the", "vector decides the match"]),
    (("round 54: angle of the vector decides the match", 32), ["round 54: angle of the vector", "decides the match"]),
    (
        ("round 54: the candle burns twice as long at night", 4),
        ["round", "54:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 54: the candle burns twice as long at night", 8),
        ["round", "54: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 54: the candle burns twice as long at night", 12),
        ["round 54:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 54: the candle burns twice as long at night", 16),
        ["round 54: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 54: the candle burns twice as long at night", 24),
        ["round 54: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 54: the candle burns twice as long at night", 32),
        ["round 54: the candle burns twice", "as long at night"],
    ),
    (
        ("round 54: a mirror of the universe in one line", 4),
        ["round", "54:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 54: a mirror of the universe in one line", 8),
        ["round", "54: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 54: a mirror of the universe in one line", 12),
        ["round 54: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 54: a mirror of the universe in one line", 16),
        ["round 54: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 54: a mirror of the universe in one line", 24), ["round 54: a mirror of", "the universe in one line"]),
    (("round 54: a mirror of the universe in one line", 32), ["round 54: a mirror of the", "universe in one line"]),
    (
        ("round 54: the queue drains before the storm", 4),
        ["round", "54:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 54: the queue drains before the storm", 8),
        ["round", "54: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 54: the queue drains before the storm", 12), ["round 54:", "the queue", "drains", "before the", "storm"]),
    (("round 54: the queue drains before the storm", 16), ["round 54: the", "queue drains", "before the storm"]),
    (("round 54: the queue drains before the storm", 24), ["round 54: the queue", "drains before the storm"]),
    (("round 54: the queue drains before the storm", 32), ["round 54: the queue drains", "before the storm"]),
    (
        ("kitten54 sitting54 agent54 angle54 universe54 memory54", 6),
        ["kitten54", "sitting54", "agent54", "angle54", "universe54", "memory54"],
    ),
    (
        ("kitten54 sitting54 agent54 angle54 universe54 memory54", 10),
        ["kitten54", "sitting54", "agent54", "angle54", "universe54", "memory54"],
    ),
    (
        ("kitten54 sitting54 agent54 angle54 universe54 memory54", 18),
        ["kitten54 sitting54", "agent54 angle54", "universe54", "memory54"],
    ),
    (
        ("kitten54 sitting54 agent54 angle54 universe54 memory54", 28),
        ["kitten54 sitting54 agent54", "angle54 universe54 memory54"],
    ),
    (
        ("sitting54 agent54 angle54 universe54 memory54 stream54", 6),
        ["sitting54", "agent54", "angle54", "universe54", "memory54", "stream54"],
    ),
    (
        ("sitting54 agent54 angle54 universe54 memory54 stream54", 10),
        ["sitting54", "agent54", "angle54", "universe54", "memory54", "stream54"],
    ),
    (
        ("sitting54 agent54 angle54 universe54 memory54 stream54", 18),
        ["sitting54 agent54", "angle54 universe54", "memory54 stream54"],
    ),
    (
        ("sitting54 agent54 angle54 universe54 memory54 stream54", 28),
        ["sitting54 agent54 angle54", "universe54 memory54 stream54"],
    ),
    (
        ("agent54 angle54 universe54 memory54 stream54 context54", 6),
        ["agent54", "angle54", "universe54", "memory54", "stream54", "context54"],
    ),
    (
        ("agent54 angle54 universe54 memory54 stream54 context54", 10),
        ["agent54", "angle54", "universe54", "memory54", "stream54", "context54"],
    ),
    (
        ("agent54 angle54 universe54 memory54 stream54 context54", 18),
        ["agent54 angle54", "universe54", "memory54 stream54", "context54"],
    ),
    (
        ("agent54 angle54 universe54 memory54 stream54 context54", 28),
        ["agent54 angle54 universe54", "memory54 stream54 context54"],
    ),
    (
        ("angle54 universe54 memory54 stream54 context54 knowledge54", 6),
        ["angle54", "universe54", "memory54", "stream54", "context54", "knowledge54"],
    ),
    (
        ("angle54 universe54 memory54 stream54 context54 knowledge54", 10),
        ["angle54", "universe54", "memory54", "stream54", "context54", "knowledge54"],
    ),
    (
        ("angle54 universe54 memory54 stream54 context54 knowledge54", 18),
        ["angle54 universe54", "memory54 stream54", "context54", "knowledge54"],
    ),
    (
        ("angle54 universe54 memory54 stream54 context54 knowledge54", 28),
        ["angle54 universe54 memory54", "stream54 context54", "knowledge54"],
    ),
    (
        ("universe54 memory54 stream54 context54 knowledge54 vector54", 6),
        ["universe54", "memory54", "stream54", "context54", "knowledge54", "vector54"],
    ),
    (
        ("universe54 memory54 stream54 context54 knowledge54 vector54", 10),
        ["universe54", "memory54", "stream54", "context54", "knowledge54", "vector54"],
    ),
    (
        ("universe54 memory54 stream54 context54 knowledge54 vector54", 18),
        ["universe54", "memory54 stream54", "context54", "knowledge54", "vector54"],
    ),
    (
        ("universe54 memory54 stream54 context54 knowledge54 vector54", 28),
        ["universe54 memory54 stream54", "context54 knowledge54", "vector54"],
    ),
    (
        ("memory54 stream54 context54 knowledge54 vector54 processor54", 6),
        ["memory54", "stream54", "context54", "knowledge54", "vector54", "processor54"],
    ),
    (
        ("memory54 stream54 context54 knowledge54 vector54 processor54", 10),
        ["memory54", "stream54", "context54", "knowledge54", "vector54", "processor54"],
    ),
    (
        ("memory54 stream54 context54 knowledge54 vector54 processor54", 18),
        ["memory54 stream54", "context54", "knowledge54", "vector54", "processor54"],
    ),
    (
        ("memory54 stream54 context54 knowledge54 vector54 processor54", 28),
        ["memory54 stream54 context54", "knowledge54 vector54", "processor54"],
    ),
    (
        ("stream54 context54 knowledge54 vector54 processor54 reasoning54", 6),
        ["stream54", "context54", "knowledge54", "vector54", "processor54", "reasoning54"],
    ),
    (
        ("stream54 context54 knowledge54 vector54 processor54 reasoning54", 10),
        ["stream54", "context54", "knowledge54", "vector54", "processor54", "reasoning54"],
    ),
    (
        ("stream54 context54 knowledge54 vector54 processor54 reasoning54", 18),
        ["stream54 context54", "knowledge54", "vector54", "processor54", "reasoning54"],
    ),
    (
        ("stream54 context54 knowledge54 vector54 processor54 reasoning54", 28),
        ["stream54 context54", "knowledge54 vector54", "processor54 reasoning54"],
    ),
    (
        ("context54 knowledge54 vector54 processor54 reasoning54 machine54", 6),
        ["context54", "knowledge54", "vector54", "processor54", "reasoning54", "machine54"],
    ),
    (
        ("context54 knowledge54 vector54 processor54 reasoning54 machine54", 10),
        ["context54", "knowledge54", "vector54", "processor54", "reasoning54", "machine54"],
    ),
    (
        ("context54 knowledge54 vector54 processor54 reasoning54 machine54", 18),
        ["context54", "knowledge54", "vector54", "processor54", "reasoning54", "machine54"],
    ),
    (
        ("context54 knowledge54 vector54 processor54 reasoning54 machine54", 28),
        ["context54 knowledge54", "vector54 processor54", "reasoning54 machine54"],
    ),
    (
        ("knowledge54 vector54 processor54 reasoning54 machine54 learning54", 6),
        ["knowledge54", "vector54", "processor54", "reasoning54", "machine54", "learning54"],
    ),
    (
        ("knowledge54 vector54 processor54 reasoning54 machine54 learning54", 10),
        ["knowledge54", "vector54", "processor54", "reasoning54", "machine54", "learning54"],
    ),
    (
        ("knowledge54 vector54 processor54 reasoning54 machine54 learning54", 18),
        ["knowledge54", "vector54", "processor54", "reasoning54", "machine54", "learning54"],
    ),
    (
        ("knowledge54 vector54 processor54 reasoning54 machine54 learning54", 28),
        ["knowledge54 vector54", "processor54 reasoning54", "machine54 learning54"],
    ),
    (
        ("vector54 processor54 reasoning54 machine54 learning54 model54", 6),
        ["vector54", "processor54", "reasoning54", "machine54", "learning54", "model54"],
    ),
    (
        ("vector54 processor54 reasoning54 machine54 learning54 model54", 10),
        ["vector54", "processor54", "reasoning54", "machine54", "learning54", "model54"],
    ),
    (
        ("vector54 processor54 reasoning54 machine54 learning54 model54", 18),
        ["vector54", "processor54", "reasoning54", "machine54", "learning54 model54"],
    ),
    (
        ("vector54 processor54 reasoning54 machine54 learning54 model54", 28),
        ["vector54 processor54", "reasoning54 machine54", "learning54 model54"],
    ),
    (
        ("processor54 reasoning54 machine54 learning54 model54 token54", 6),
        ["processor54", "reasoning54", "machine54", "learning54", "model54", "token54"],
    ),
    (
        ("processor54 reasoning54 machine54 learning54 model54 token54", 10),
        ["processor54", "reasoning54", "machine54", "learning54", "model54", "token54"],
    ),
    (
        ("processor54 reasoning54 machine54 learning54 model54 token54", 18),
        ["processor54", "reasoning54", "machine54", "learning54 model54", "token54"],
    ),
    (
        ("processor54 reasoning54 machine54 learning54 model54 token54", 28),
        ["processor54 reasoning54", "machine54 learning54 model54", "token54"],
    ),
    (
        ("reasoning54 machine54 learning54 model54 token54 prompt54", 6),
        ["reasoning54", "machine54", "learning54", "model54", "token54", "prompt54"],
    ),
    (
        ("reasoning54 machine54 learning54 model54 token54 prompt54", 10),
        ["reasoning54", "machine54", "learning54", "model54", "token54", "prompt54"],
    ),
    (
        ("reasoning54 machine54 learning54 model54 token54 prompt54", 18),
        ["reasoning54", "machine54", "learning54 model54", "token54 prompt54"],
    ),
    (
        ("reasoning54 machine54 learning54 model54 token54 prompt54", 28),
        ["reasoning54 machine54", "learning54 model54 token54", "prompt54"],
    ),
    (
        ("machine54 learning54 model54 token54 prompt54 session54", 6),
        ["machine54", "learning54", "model54", "token54", "prompt54", "session54"],
    ),
    (
        ("machine54 learning54 model54 token54 prompt54 session54", 10),
        ["machine54", "learning54", "model54", "token54", "prompt54", "session54"],
    ),
    (
        ("machine54 learning54 model54 token54 prompt54 session54", 18),
        ["machine54", "learning54 model54", "token54 prompt54", "session54"],
    ),
    (
        ("machine54 learning54 model54 token54 prompt54 session54", 28),
        ["machine54 learning54 model54", "token54 prompt54 session54"],
    ),
    (
        ("learning54 model54 token54 prompt54 session54 library54", 6),
        ["learning54", "model54", "token54", "prompt54", "session54", "library54"],
    ),
    (
        ("learning54 model54 token54 prompt54 session54 library54", 10),
        ["learning54", "model54", "token54", "prompt54", "session54", "library54"],
    ),
    (
        ("learning54 model54 token54 prompt54 session54 library54", 18),
        ["learning54 model54", "token54 prompt54", "session54", "library54"],
    ),
    (
        ("learning54 model54 token54 prompt54 session54 library54", 28),
        ["learning54 model54 token54", "prompt54 session54 library54"],
    ),
    (
        ("model54 token54 prompt54 session54 library54 service54", 6),
        ["model54", "token54", "prompt54", "session54", "library54", "service54"],
    ),
    (
        ("model54 token54 prompt54 session54 library54 service54", 10),
        ["model54", "token54", "prompt54", "session54", "library54", "service54"],
    ),
    (
        ("model54 token54 prompt54 session54 library54 service54", 18),
        ["model54 token54", "prompt54 session54", "library54", "service54"],
    ),
    (
        ("model54 token54 prompt54 session54 library54 service54", 28),
        ["model54 token54 prompt54", "session54 library54", "service54"],
    ),
    (
        ("token54 prompt54 session54 library54 service54 gateway54", 6),
        ["token54", "prompt54", "session54", "library54", "service54", "gateway54"],
    ),
    (
        ("token54 prompt54 session54 library54 service54 gateway54", 10),
        ["token54", "prompt54", "session54", "library54", "service54", "gateway54"],
    ),
    (
        ("token54 prompt54 session54 library54 service54 gateway54", 18),
        ["token54 prompt54", "session54", "library54", "service54", "gateway54"],
    ),
    (
        ("token54 prompt54 session54 library54 service54 gateway54", 28),
        ["token54 prompt54 session54", "library54 service54", "gateway54"],
    ),
    (
        ("prompt54 session54 library54 service54 gateway54 storage54", 6),
        ["prompt54", "session54", "library54", "service54", "gateway54", "storage54"],
    ),
    (
        ("prompt54 session54 library54 service54 gateway54 storage54", 10),
        ["prompt54", "session54", "library54", "service54", "gateway54", "storage54"],
    ),
    (
        ("prompt54 session54 library54 service54 gateway54 storage54", 18),
        ["prompt54 session54", "library54", "service54", "gateway54", "storage54"],
    ),
    (
        ("prompt54 session54 library54 service54 gateway54 storage54", 28),
        ["prompt54 session54 library54", "service54 gateway54", "storage54"],
    ),
    (
        ("session54 library54 service54 gateway54 storage54 network54", 6),
        ["session54", "library54", "service54", "gateway54", "storage54", "network54"],
    ),
    (
        ("session54 library54 service54 gateway54 storage54 network54", 10),
        ["session54", "library54", "service54", "gateway54", "storage54", "network54"],
    ),
    (
        ("session54 library54 service54 gateway54 storage54 network54", 18),
        ["session54", "library54", "service54", "gateway54", "storage54", "network54"],
    ),
    (
        ("session54 library54 service54 gateway54 storage54 network54", 28),
        ["session54 library54", "service54 gateway54", "storage54 network54"],
    ),
    (
        ("library54 service54 gateway54 storage54 network54 latency54", 6),
        ["library54", "service54", "gateway54", "storage54", "network54", "latency54"],
    ),
    (
        ("library54 service54 gateway54 storage54 network54 latency54", 10),
        ["library54", "service54", "gateway54", "storage54", "network54", "latency54"],
    ),
    (
        ("library54 service54 gateway54 storage54 network54 latency54", 18),
        ["library54", "service54", "gateway54", "storage54", "network54", "latency54"],
    ),
    (
        ("library54 service54 gateway54 storage54 network54 latency54", 28),
        ["library54 service54", "gateway54 storage54", "network54 latency54"],
    ),
    (
        ("service54 gateway54 storage54 network54 latency54 buffer54", 6),
        ["service54", "gateway54", "storage54", "network54", "latency54", "buffer54"],
    ),
    (
        ("service54 gateway54 storage54 network54 latency54 buffer54", 10),
        ["service54", "gateway54", "storage54", "network54", "latency54", "buffer54"],
    ),
    (
        ("service54 gateway54 storage54 network54 latency54 buffer54", 18),
        ["service54", "gateway54", "storage54", "network54", "latency54 buffer54"],
    ),
    (
        ("service54 gateway54 storage54 network54 latency54 buffer54", 28),
        ["service54 gateway54", "storage54 network54", "latency54 buffer54"],
    ),
    (
        ("gateway54 storage54 network54 latency54 buffer54 queue54", 6),
        ["gateway54", "storage54", "network54", "latency54", "buffer54", "queue54"],
    ),
    (
        ("gateway54 storage54 network54 latency54 buffer54 queue54", 10),
        ["gateway54", "storage54", "network54", "latency54", "buffer54", "queue54"],
    ),
    (
        ("gateway54 storage54 network54 latency54 buffer54 queue54", 18),
        ["gateway54", "storage54", "network54", "latency54 buffer54", "queue54"],
    ),
    (
        ("gateway54 storage54 network54 latency54 buffer54 queue54", 28),
        ["gateway54 storage54", "network54 latency54 buffer54", "queue54"],
    ),
    (
        ("storage54 network54 latency54 buffer54 queue54 worker54", 6),
        ["storage54", "network54", "latency54", "buffer54", "queue54", "worker54"],
    ),
    (
        ("storage54 network54 latency54 buffer54 queue54 worker54", 10),
        ["storage54", "network54", "latency54", "buffer54", "queue54", "worker54"],
    ),
    (
        ("storage54 network54 latency54 buffer54 queue54 worker54", 18),
        ["storage54", "network54", "latency54 buffer54", "queue54 worker54"],
    ),
    (
        ("storage54 network54 latency54 buffer54 queue54 worker54", 28),
        ["storage54 network54", "latency54 buffer54 queue54", "worker54"],
    ),
    (
        ("network54 latency54 buffer54 queue54 worker54 kernel54", 6),
        ["network54", "latency54", "buffer54", "queue54", "worker54", "kernel54"],
    ),
    (
        ("network54 latency54 buffer54 queue54 worker54 kernel54", 10),
        ["network54", "latency54", "buffer54", "queue54", "worker54", "kernel54"],
    ),
    (
        ("network54 latency54 buffer54 queue54 worker54 kernel54", 18),
        ["network54", "latency54 buffer54", "queue54 worker54", "kernel54"],
    ),
    (
        ("network54 latency54 buffer54 queue54 worker54 kernel54", 28),
        ["network54 latency54 buffer54", "queue54 worker54 kernel54"],
    ),
    (
        ("latency54 buffer54 queue54 worker54 kernel54 signal54", 6),
        ["latency54", "buffer54", "queue54", "worker54", "kernel54", "signal54"],
    ),
    (
        ("latency54 buffer54 queue54 worker54 kernel54 signal54", 10),
        ["latency54", "buffer54", "queue54", "worker54", "kernel54", "signal54"],
    ),
    (
        ("latency54 buffer54 queue54 worker54 kernel54 signal54", 18),
        ["latency54 buffer54", "queue54 worker54", "kernel54 signal54"],
    ),
    (
        ("latency54 buffer54 queue54 worker54 kernel54 signal54", 28),
        ["latency54 buffer54 queue54", "worker54 kernel54 signal54"],
    ),
    (
        ("buffer54 queue54 worker54 kernel54 signal54 packet54", 6),
        ["buffer54", "queue54", "worker54", "kernel54", "signal54", "packet54"],
    ),
    (
        ("buffer54 queue54 worker54 kernel54 signal54 packet54", 10),
        ["buffer54", "queue54", "worker54", "kernel54", "signal54", "packet54"],
    ),
    (
        ("buffer54 queue54 worker54 kernel54 signal54 packet54", 18),
        ["buffer54 queue54", "worker54 kernel54", "signal54 packet54"],
    ),
    (
        ("buffer54 queue54 worker54 kernel54 signal54 packet54", 28),
        ["buffer54 queue54 worker54", "kernel54 signal54 packet54"],
    ),
    (
        ("queue54 worker54 kernel54 signal54 packet54 router54", 6),
        ["queue54", "worker54", "kernel54", "signal54", "packet54", "router54"],
    ),
    (
        ("queue54 worker54 kernel54 signal54 packet54 router54", 10),
        ["queue54", "worker54", "kernel54", "signal54", "packet54", "router54"],
    ),
    (
        ("queue54 worker54 kernel54 signal54 packet54 router54", 18),
        ["queue54 worker54", "kernel54 signal54", "packet54 router54"],
    ),
    (
        ("queue54 worker54 kernel54 signal54 packet54 router54", 28),
        ["queue54 worker54 kernel54", "signal54 packet54 router54"],
    ),
    (
        ("worker54 kernel54 signal54 packet54 router54 cluster54", 6),
        ["worker54", "kernel54", "signal54", "packet54", "router54", "cluster54"],
    ),
    (
        ("worker54 kernel54 signal54 packet54 router54 cluster54", 10),
        ["worker54", "kernel54", "signal54", "packet54", "router54", "cluster54"],
    ),
    (
        ("worker54 kernel54 signal54 packet54 router54 cluster54", 18),
        ["worker54 kernel54", "signal54 packet54", "router54 cluster54"],
    ),
    (
        ("worker54 kernel54 signal54 packet54 router54 cluster54", 28),
        ["worker54 kernel54 signal54", "packet54 router54 cluster54"],
    ),
    (
        ("kernel54 signal54 packet54 router54 cluster54 mirror54", 6),
        ["kernel54", "signal54", "packet54", "router54", "cluster54", "mirror54"],
    ),
    (
        ("kernel54 signal54 packet54 router54 cluster54 mirror54", 10),
        ["kernel54", "signal54", "packet54", "router54", "cluster54", "mirror54"],
    ),
    (
        ("kernel54 signal54 packet54 router54 cluster54 mirror54", 18),
        ["kernel54 signal54", "packet54 router54", "cluster54 mirror54"],
    ),
    (
        ("kernel54 signal54 packet54 router54 cluster54 mirror54", 28),
        ["kernel54 signal54 packet54", "router54 cluster54 mirror54"],
    ),
    (
        ("signal54 packet54 router54 cluster54 mirror54 filter54", 6),
        ["signal54", "packet54", "router54", "cluster54", "mirror54", "filter54"],
    ),
    (
        ("signal54 packet54 router54 cluster54 mirror54 filter54", 10),
        ["signal54", "packet54", "router54", "cluster54", "mirror54", "filter54"],
    ),
    (
        ("signal54 packet54 router54 cluster54 mirror54 filter54", 18),
        ["signal54 packet54", "router54 cluster54", "mirror54 filter54"],
    ),
    (
        ("signal54 packet54 router54 cluster54 mirror54 filter54", 28),
        ["signal54 packet54 router54", "cluster54 mirror54 filter54"],
    ),
    (
        ("packet54 router54 cluster54 mirror54 filter54 ranking54", 6),
        ["packet54", "router54", "cluster54", "mirror54", "filter54", "ranking54"],
    ),
    (
        ("packet54 router54 cluster54 mirror54 filter54 ranking54", 10),
        ["packet54", "router54", "cluster54", "mirror54", "filter54", "ranking54"],
    ),
    (
        ("packet54 router54 cluster54 mirror54 filter54 ranking54", 18),
        ["packet54 router54", "cluster54 mirror54", "filter54 ranking54"],
    ),
    (
        ("packet54 router54 cluster54 mirror54 filter54 ranking54", 28),
        ["packet54 router54 cluster54", "mirror54 filter54 ranking54"],
    ),
    (
        ("router54 cluster54 mirror54 filter54 ranking54 encoding54", 6),
        ["router54", "cluster54", "mirror54", "filter54", "ranking54", "encoding54"],
    ),
    (
        ("router54 cluster54 mirror54 filter54 ranking54 encoding54", 10),
        ["router54", "cluster54", "mirror54", "filter54", "ranking54", "encoding54"],
    ),
    (
        ("router54 cluster54 mirror54 filter54 ranking54 encoding54", 18),
        ["router54 cluster54", "mirror54 filter54", "ranking54", "encoding54"],
    ),
    (
        ("router54 cluster54 mirror54 filter54 ranking54 encoding54", 28),
        ["router54 cluster54 mirror54", "filter54 ranking54", "encoding54"],
    ),
    (
        ("cluster54 mirror54 filter54 ranking54 encoding54 mapping54", 6),
        ["cluster54", "mirror54", "filter54", "ranking54", "encoding54", "mapping54"],
    ),
    (
        ("cluster54 mirror54 filter54 ranking54 encoding54 mapping54", 10),
        ["cluster54", "mirror54", "filter54", "ranking54", "encoding54", "mapping54"],
    ),
    (
        ("cluster54 mirror54 filter54 ranking54 encoding54 mapping54", 18),
        ["cluster54 mirror54", "filter54 ranking54", "encoding54", "mapping54"],
    ),
    (
        ("cluster54 mirror54 filter54 ranking54 encoding54 mapping54", 28),
        ["cluster54 mirror54 filter54", "ranking54 encoding54", "mapping54"],
    ),
    (
        ("mirror54 filter54 ranking54 encoding54 mapping54 record54", 6),
        ["mirror54", "filter54", "ranking54", "encoding54", "mapping54", "record54"],
    ),
    (
        ("mirror54 filter54 ranking54 encoding54 mapping54 record54", 10),
        ["mirror54", "filter54", "ranking54", "encoding54", "mapping54", "record54"],
    ),
    (
        ("mirror54 filter54 ranking54 encoding54 mapping54 record54", 18),
        ["mirror54 filter54", "ranking54", "encoding54", "mapping54 record54"],
    ),
    (
        ("mirror54 filter54 ranking54 encoding54 mapping54 record54", 28),
        ["mirror54 filter54 ranking54", "encoding54 mapping54", "record54"],
    ),
    (
        ("filter54 ranking54 encoding54 mapping54 record54 candle54", 6),
        ["filter54", "ranking54", "encoding54", "mapping54", "record54", "candle54"],
    ),
    (
        ("filter54 ranking54 encoding54 mapping54 record54 candle54", 10),
        ["filter54", "ranking54", "encoding54", "mapping54", "record54", "candle54"],
    ),
    (
        ("filter54 ranking54 encoding54 mapping54 record54 candle54", 18),
        ["filter54 ranking54", "encoding54", "mapping54 record54", "candle54"],
    ),
    (
        ("filter54 ranking54 encoding54 mapping54 record54 candle54", 28),
        ["filter54 ranking54", "encoding54 mapping54", "record54 candle54"],
    ),
    (
        ("ranking54 encoding54 mapping54 record54 candle54 thread54", 6),
        ["ranking54", "encoding54", "mapping54", "record54", "candle54", "thread54"],
    ),
    (
        ("ranking54 encoding54 mapping54 record54 candle54 thread54", 10),
        ["ranking54", "encoding54", "mapping54", "record54", "candle54", "thread54"],
    ),
    (
        ("ranking54 encoding54 mapping54 record54 candle54 thread54", 18),
        ["ranking54", "encoding54", "mapping54 record54", "candle54 thread54"],
    ),
    (
        ("ranking54 encoding54 mapping54 record54 candle54 thread54", 28),
        ["ranking54 encoding54", "mapping54 record54 candle54", "thread54"],
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
