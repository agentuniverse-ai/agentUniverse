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
        ("round 80: the quick brown fox jumps over the lazy dog", 4),
        ["round", "80:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 80: the quick brown fox jumps over the lazy dog", 8),
        ["round", "80: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 80: the quick brown fox jumps over the lazy dog", 12),
        ["round 80:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 80: the quick brown fox jumps over the lazy dog", 16),
        ["round 80: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 80: the quick brown fox jumps over the lazy dog", 24),
        ["round 80: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 80: the quick brown fox jumps over the lazy dog", 32),
        ["round 80: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 80: agentuniverse is a framework for multi agents", 4),
        ["round", "80:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 80: agentuniverse is a framework for multi agents", 8),
        ["round", "80:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 80: agentuniverse is a framework for multi agents", 12),
        ["round 80:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 80: agentuniverse is a framework for multi agents", 16),
        ["round 80:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 80: agentuniverse is a framework for multi agents", 24),
        ["round 80: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 80: agentuniverse is a framework for multi agents", 32),
        ["round 80: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 80: knowledge stored as vectors enables retrieval", 4),
        ["round", "80:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 80: knowledge stored as vectors enables retrieval", 8),
        ["round", "80:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 80: knowledge stored as vectors enables retrieval", 12),
        ["round 80:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 80: knowledge stored as vectors enables retrieval", 16),
        ["round 80:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 80: knowledge stored as vectors enables retrieval", 24),
        ["round 80: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 80: knowledge stored as vectors enables retrieval", 32),
        ["round 80: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 80: the processor reads the record then stops", 4),
        ["round", "80:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 80: the processor reads the record then stops", 8),
        ["round", "80: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 80: the processor reads the record then stops", 12),
        ["round 80:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 80: the processor reads the record then stops", 16),
        ["round 80: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 80: the processor reads the record then stops", 24),
        ["round 80: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 80: the processor reads the record then stops", 32),
        ["round 80: the processor reads", "the record then stops"],
    ),
    (
        ("round 80: a worker pulls the next task from the queue", 4),
        ["round", "80:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 80: a worker pulls the next task from the queue", 8),
        ["round", "80: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 80: a worker pulls the next task from the queue", 12),
        ["round 80: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 80: a worker pulls the next task from the queue", 16),
        ["round 80: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 80: a worker pulls the next task from the queue", 24),
        ["round 80: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 80: a worker pulls the next task from the queue", 32),
        ["round 80: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 80: signals travel through the network layer", 4),
        ["round", "80:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 80: signals travel through the network layer", 8),
        ["round", "80:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 80: signals travel through the network layer", 12),
        ["round 80:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 80: signals travel through the network layer", 16),
        ["round 80:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 80: signals travel through the network layer", 24),
        ["round 80: signals travel", "through the network", "layer"],
    ),
    (
        ("round 80: signals travel through the network layer", 32),
        ["round 80: signals travel through", "the network layer"],
    ),
    (
        ("round 80: the gateway routes each request by policy", 4),
        ["round", "80:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 80: the gateway routes each request by policy", 8),
        ["round", "80: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 80: the gateway routes each request by policy", 12),
        ["round 80:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 80: the gateway routes each request by policy", 16),
        ["round 80: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 80: the gateway routes each request by policy", 24),
        ["round 80: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 80: the gateway routes each request by policy", 32),
        ["round 80: the gateway routes", "each request by policy"],
    ),
    (
        ("round 80: memory grows until the buffer is full", 4),
        ["round", "80:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 80: memory grows until the buffer is full", 8),
        ["round", "80:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 80: memory grows until the buffer is full", 12),
        ["round 80:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 80: memory grows until the buffer is full", 16),
        ["round 80: memory", "grows until the", "buffer is full"],
    ),
    (("round 80: memory grows until the buffer is full", 24), ["round 80: memory grows", "until the buffer is full"]),
    (("round 80: memory grows until the buffer is full", 32), ["round 80: memory grows until the", "buffer is full"]),
    (
        ("round 80: the cluster mirrors every packet twice", 4),
        ["round", "80:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 80: the cluster mirrors every packet twice", 8),
        ["round", "80: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 80: the cluster mirrors every packet twice", 12),
        ["round 80:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 80: the cluster mirrors every packet twice", 16),
        ["round 80: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 80: the cluster mirrors every packet twice", 24),
        ["round 80: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 80: the cluster mirrors every packet twice", 32), ["round 80: the cluster mirrors", "every packet twice"]),
    (
        ("round 80: ranking uses tokens learned from the corpus", 4),
        ["round", "80:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 80: ranking uses tokens learned from the corpus", 8),
        ["round", "80:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 80: ranking uses tokens learned from the corpus", 12),
        ["round 80:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 80: ranking uses tokens learned from the corpus", 16),
        ["round 80:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 80: ranking uses tokens learned from the corpus", 24),
        ["round 80: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 80: ranking uses tokens learned from the corpus", 32),
        ["round 80: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 80: a long session ends when the candle dies", 4),
        ["round", "80:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 80: a long session ends when the candle dies", 8),
        ["round", "80: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 80: a long session ends when the candle dies", 12),
        ["round 80: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 80: a long session ends when the candle dies", 16),
        ["round 80: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 80: a long session ends when the candle dies", 24),
        ["round 80: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 80: a long session ends when the candle dies", 32),
        ["round 80: a long session ends", "when the candle dies"],
    ),
    (
        ("round 80: encode the prompt then map the result", 4),
        ["round", "80:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 80: encode the prompt then map the result", 8),
        ["round", "80:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 80: encode the prompt then map the result", 12),
        ["round 80:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 80: encode the prompt then map the result", 16),
        ["round 80: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 80: encode the prompt then map the result", 24),
        ["round 80: encode the", "prompt then map the", "result"],
    ),
    (("round 80: encode the prompt then map the result", 32), ["round 80: encode the prompt then", "map the result"]),
    (
        ("round 80: the kernel wakes the worker at dawn", 4),
        ["round", "80:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 80: the kernel wakes the worker at dawn", 8),
        ["round", "80: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 80: the kernel wakes the worker at dawn", 12),
        ["round 80:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 80: the kernel wakes the worker at dawn", 16), ["round 80: the", "kernel wakes the", "worker at dawn"]),
    (("round 80: the kernel wakes the worker at dawn", 24), ["round 80: the kernel", "wakes the worker at dawn"]),
    (("round 80: the kernel wakes the worker at dawn", 32), ["round 80: the kernel wakes the", "worker at dawn"]),
    (
        ("round 80: service latency drops after the patch", 4),
        ["round", "80:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 80: service latency drops after the patch", 8),
        ["round", "80:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 80: service latency drops after the patch", 12),
        ["round 80:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 80: service latency drops after the patch", 16),
        ["round 80:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 80: service latency drops after the patch", 24),
        ["round 80: service", "latency drops after the", "patch"],
    ),
    (("round 80: service latency drops after the patch", 32), ["round 80: service latency drops", "after the patch"]),
    (
        ("round 80: the library caches every vector it sees", 4),
        ["round", "80:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 80: the library caches every vector it sees", 8),
        ["round", "80: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 80: the library caches every vector it sees", 12),
        ["round 80:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 80: the library caches every vector it sees", 16),
        ["round 80: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 80: the library caches every vector it sees", 24),
        ["round 80: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 80: the library caches every vector it sees", 32),
        ["round 80: the library caches", "every vector it sees"],
    ),
    (
        ("round 80: agents argue then the debate resolves", 4),
        ["round", "80:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 80: agents argue then the debate resolves", 8),
        ["round", "80:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 80: agents argue then the debate resolves", 12),
        ["round 80:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 80: agents argue then the debate resolves", 16),
        ["round 80: agents", "argue then the", "debate resolves"],
    ),
    (("round 80: agents argue then the debate resolves", 24), ["round 80: agents argue", "then the debate resolves"]),
    (("round 80: agents argue then the debate resolves", 32), ["round 80: agents argue then the", "debate resolves"]),
    (
        ("round 80: the filter keeps only strong matches", 4),
        ["round", "80:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 80: the filter keeps only strong matches", 8),
        ["round", "80: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 80: the filter keeps only strong matches", 12),
        ["round 80:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 80: the filter keeps only strong matches", 16),
        ["round 80: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 80: the filter keeps only strong matches", 24), ["round 80: the filter", "keeps only strong", "matches"]),
    (("round 80: the filter keeps only strong matches", 32), ["round 80: the filter keeps only", "strong matches"]),
    (
        ("round 80: the model answers with a short reply", 4),
        ["round", "80:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 80: the model answers with a short reply", 8),
        ["round", "80: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 80: the model answers with a short reply", 12),
        ["round 80:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 80: the model answers with a short reply", 16),
        ["round 80: the", "model answers", "with a short", "reply"],
    ),
    (("round 80: the model answers with a short reply", 24), ["round 80: the model", "answers with a short", "reply"]),
    (("round 80: the model answers with a short reply", 32), ["round 80: the model answers with", "a short reply"]),
    (
        ("round 80: the recorder stores the reasoning trace", 4),
        ["round", "80:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 80: the recorder stores the reasoning trace", 8),
        ["round", "80: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 80: the recorder stores the reasoning trace", 12),
        ["round 80:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 80: the recorder stores the reasoning trace", 16),
        ["round 80: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 80: the recorder stores the reasoning trace", 24),
        ["round 80: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 80: the recorder stores the reasoning trace", 32),
        ["round 80: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 80: the angel watches the processor run", 4),
        ["round", "80:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 80: the angel watches the processor run", 8),
        ["round", "80: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 80: the angel watches the processor run", 12),
        ["round 80:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 80: the angel watches the processor run", 16), ["round 80: the", "angel watches", "the processor", "run"]),
    (("round 80: the angel watches the processor run", 24), ["round 80: the angel", "watches the processor", "run"]),
    (("round 80: the angel watches the processor run", 32), ["round 80: the angel watches the", "processor run"]),
    (
        ("round 80: angle of the vector decides the match", 4),
        ["round", "80:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 80: angle of the vector decides the match", 8),
        ["round", "80:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 80: angle of the vector decides the match", 12),
        ["round 80:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 80: angle of the vector decides the match", 16),
        ["round 80: angle", "of the vector", "decides the", "match"],
    ),
    (("round 80: angle of the vector decides the match", 24), ["round 80: angle of the", "vector decides the match"]),
    (("round 80: angle of the vector decides the match", 32), ["round 80: angle of the vector", "decides the match"]),
    (
        ("round 80: the candle burns twice as long at night", 4),
        ["round", "80:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 80: the candle burns twice as long at night", 8),
        ["round", "80: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 80: the candle burns twice as long at night", 12),
        ["round 80:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 80: the candle burns twice as long at night", 16),
        ["round 80: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 80: the candle burns twice as long at night", 24),
        ["round 80: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 80: the candle burns twice as long at night", 32),
        ["round 80: the candle burns twice", "as long at night"],
    ),
    (
        ("round 80: a mirror of the universe in one line", 4),
        ["round", "80:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 80: a mirror of the universe in one line", 8),
        ["round", "80: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 80: a mirror of the universe in one line", 12),
        ["round 80: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 80: a mirror of the universe in one line", 16),
        ["round 80: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 80: a mirror of the universe in one line", 24), ["round 80: a mirror of", "the universe in one line"]),
    (("round 80: a mirror of the universe in one line", 32), ["round 80: a mirror of the", "universe in one line"]),
    (
        ("round 80: the queue drains before the storm", 4),
        ["round", "80:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 80: the queue drains before the storm", 8),
        ["round", "80: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 80: the queue drains before the storm", 12), ["round 80:", "the queue", "drains", "before the", "storm"]),
    (("round 80: the queue drains before the storm", 16), ["round 80: the", "queue drains", "before the storm"]),
    (("round 80: the queue drains before the storm", 24), ["round 80: the queue", "drains before the storm"]),
    (("round 80: the queue drains before the storm", 32), ["round 80: the queue drains", "before the storm"]),
    (
        ("kitten80 sitting80 agent80 angle80 universe80 memory80", 6),
        ["kitten80", "sitting80", "agent80", "angle80", "universe80", "memory80"],
    ),
    (
        ("kitten80 sitting80 agent80 angle80 universe80 memory80", 10),
        ["kitten80", "sitting80", "agent80", "angle80", "universe80", "memory80"],
    ),
    (
        ("kitten80 sitting80 agent80 angle80 universe80 memory80", 18),
        ["kitten80 sitting80", "agent80 angle80", "universe80", "memory80"],
    ),
    (
        ("kitten80 sitting80 agent80 angle80 universe80 memory80", 28),
        ["kitten80 sitting80 agent80", "angle80 universe80 memory80"],
    ),
    (
        ("sitting80 agent80 angle80 universe80 memory80 stream80", 6),
        ["sitting80", "agent80", "angle80", "universe80", "memory80", "stream80"],
    ),
    (
        ("sitting80 agent80 angle80 universe80 memory80 stream80", 10),
        ["sitting80", "agent80", "angle80", "universe80", "memory80", "stream80"],
    ),
    (
        ("sitting80 agent80 angle80 universe80 memory80 stream80", 18),
        ["sitting80 agent80", "angle80 universe80", "memory80 stream80"],
    ),
    (
        ("sitting80 agent80 angle80 universe80 memory80 stream80", 28),
        ["sitting80 agent80 angle80", "universe80 memory80 stream80"],
    ),
    (
        ("agent80 angle80 universe80 memory80 stream80 context80", 6),
        ["agent80", "angle80", "universe80", "memory80", "stream80", "context80"],
    ),
    (
        ("agent80 angle80 universe80 memory80 stream80 context80", 10),
        ["agent80", "angle80", "universe80", "memory80", "stream80", "context80"],
    ),
    (
        ("agent80 angle80 universe80 memory80 stream80 context80", 18),
        ["agent80 angle80", "universe80", "memory80 stream80", "context80"],
    ),
    (
        ("agent80 angle80 universe80 memory80 stream80 context80", 28),
        ["agent80 angle80 universe80", "memory80 stream80 context80"],
    ),
    (
        ("angle80 universe80 memory80 stream80 context80 knowledge80", 6),
        ["angle80", "universe80", "memory80", "stream80", "context80", "knowledge80"],
    ),
    (
        ("angle80 universe80 memory80 stream80 context80 knowledge80", 10),
        ["angle80", "universe80", "memory80", "stream80", "context80", "knowledge80"],
    ),
    (
        ("angle80 universe80 memory80 stream80 context80 knowledge80", 18),
        ["angle80 universe80", "memory80 stream80", "context80", "knowledge80"],
    ),
    (
        ("angle80 universe80 memory80 stream80 context80 knowledge80", 28),
        ["angle80 universe80 memory80", "stream80 context80", "knowledge80"],
    ),
    (
        ("universe80 memory80 stream80 context80 knowledge80 vector80", 6),
        ["universe80", "memory80", "stream80", "context80", "knowledge80", "vector80"],
    ),
    (
        ("universe80 memory80 stream80 context80 knowledge80 vector80", 10),
        ["universe80", "memory80", "stream80", "context80", "knowledge80", "vector80"],
    ),
    (
        ("universe80 memory80 stream80 context80 knowledge80 vector80", 18),
        ["universe80", "memory80 stream80", "context80", "knowledge80", "vector80"],
    ),
    (
        ("universe80 memory80 stream80 context80 knowledge80 vector80", 28),
        ["universe80 memory80 stream80", "context80 knowledge80", "vector80"],
    ),
    (
        ("memory80 stream80 context80 knowledge80 vector80 processor80", 6),
        ["memory80", "stream80", "context80", "knowledge80", "vector80", "processor80"],
    ),
    (
        ("memory80 stream80 context80 knowledge80 vector80 processor80", 10),
        ["memory80", "stream80", "context80", "knowledge80", "vector80", "processor80"],
    ),
    (
        ("memory80 stream80 context80 knowledge80 vector80 processor80", 18),
        ["memory80 stream80", "context80", "knowledge80", "vector80", "processor80"],
    ),
    (
        ("memory80 stream80 context80 knowledge80 vector80 processor80", 28),
        ["memory80 stream80 context80", "knowledge80 vector80", "processor80"],
    ),
    (
        ("stream80 context80 knowledge80 vector80 processor80 reasoning80", 6),
        ["stream80", "context80", "knowledge80", "vector80", "processor80", "reasoning80"],
    ),
    (
        ("stream80 context80 knowledge80 vector80 processor80 reasoning80", 10),
        ["stream80", "context80", "knowledge80", "vector80", "processor80", "reasoning80"],
    ),
    (
        ("stream80 context80 knowledge80 vector80 processor80 reasoning80", 18),
        ["stream80 context80", "knowledge80", "vector80", "processor80", "reasoning80"],
    ),
    (
        ("stream80 context80 knowledge80 vector80 processor80 reasoning80", 28),
        ["stream80 context80", "knowledge80 vector80", "processor80 reasoning80"],
    ),
    (
        ("context80 knowledge80 vector80 processor80 reasoning80 machine80", 6),
        ["context80", "knowledge80", "vector80", "processor80", "reasoning80", "machine80"],
    ),
    (
        ("context80 knowledge80 vector80 processor80 reasoning80 machine80", 10),
        ["context80", "knowledge80", "vector80", "processor80", "reasoning80", "machine80"],
    ),
    (
        ("context80 knowledge80 vector80 processor80 reasoning80 machine80", 18),
        ["context80", "knowledge80", "vector80", "processor80", "reasoning80", "machine80"],
    ),
    (
        ("context80 knowledge80 vector80 processor80 reasoning80 machine80", 28),
        ["context80 knowledge80", "vector80 processor80", "reasoning80 machine80"],
    ),
    (
        ("knowledge80 vector80 processor80 reasoning80 machine80 learning80", 6),
        ["knowledge80", "vector80", "processor80", "reasoning80", "machine80", "learning80"],
    ),
    (
        ("knowledge80 vector80 processor80 reasoning80 machine80 learning80", 10),
        ["knowledge80", "vector80", "processor80", "reasoning80", "machine80", "learning80"],
    ),
    (
        ("knowledge80 vector80 processor80 reasoning80 machine80 learning80", 18),
        ["knowledge80", "vector80", "processor80", "reasoning80", "machine80", "learning80"],
    ),
    (
        ("knowledge80 vector80 processor80 reasoning80 machine80 learning80", 28),
        ["knowledge80 vector80", "processor80 reasoning80", "machine80 learning80"],
    ),
    (
        ("vector80 processor80 reasoning80 machine80 learning80 model80", 6),
        ["vector80", "processor80", "reasoning80", "machine80", "learning80", "model80"],
    ),
    (
        ("vector80 processor80 reasoning80 machine80 learning80 model80", 10),
        ["vector80", "processor80", "reasoning80", "machine80", "learning80", "model80"],
    ),
    (
        ("vector80 processor80 reasoning80 machine80 learning80 model80", 18),
        ["vector80", "processor80", "reasoning80", "machine80", "learning80 model80"],
    ),
    (
        ("vector80 processor80 reasoning80 machine80 learning80 model80", 28),
        ["vector80 processor80", "reasoning80 machine80", "learning80 model80"],
    ),
    (
        ("processor80 reasoning80 machine80 learning80 model80 token80", 6),
        ["processor80", "reasoning80", "machine80", "learning80", "model80", "token80"],
    ),
    (
        ("processor80 reasoning80 machine80 learning80 model80 token80", 10),
        ["processor80", "reasoning80", "machine80", "learning80", "model80", "token80"],
    ),
    (
        ("processor80 reasoning80 machine80 learning80 model80 token80", 18),
        ["processor80", "reasoning80", "machine80", "learning80 model80", "token80"],
    ),
    (
        ("processor80 reasoning80 machine80 learning80 model80 token80", 28),
        ["processor80 reasoning80", "machine80 learning80 model80", "token80"],
    ),
    (
        ("reasoning80 machine80 learning80 model80 token80 prompt80", 6),
        ["reasoning80", "machine80", "learning80", "model80", "token80", "prompt80"],
    ),
    (
        ("reasoning80 machine80 learning80 model80 token80 prompt80", 10),
        ["reasoning80", "machine80", "learning80", "model80", "token80", "prompt80"],
    ),
    (
        ("reasoning80 machine80 learning80 model80 token80 prompt80", 18),
        ["reasoning80", "machine80", "learning80 model80", "token80 prompt80"],
    ),
    (
        ("reasoning80 machine80 learning80 model80 token80 prompt80", 28),
        ["reasoning80 machine80", "learning80 model80 token80", "prompt80"],
    ),
    (
        ("machine80 learning80 model80 token80 prompt80 session80", 6),
        ["machine80", "learning80", "model80", "token80", "prompt80", "session80"],
    ),
    (
        ("machine80 learning80 model80 token80 prompt80 session80", 10),
        ["machine80", "learning80", "model80", "token80", "prompt80", "session80"],
    ),
    (
        ("machine80 learning80 model80 token80 prompt80 session80", 18),
        ["machine80", "learning80 model80", "token80 prompt80", "session80"],
    ),
    (
        ("machine80 learning80 model80 token80 prompt80 session80", 28),
        ["machine80 learning80 model80", "token80 prompt80 session80"],
    ),
    (
        ("learning80 model80 token80 prompt80 session80 library80", 6),
        ["learning80", "model80", "token80", "prompt80", "session80", "library80"],
    ),
    (
        ("learning80 model80 token80 prompt80 session80 library80", 10),
        ["learning80", "model80", "token80", "prompt80", "session80", "library80"],
    ),
    (
        ("learning80 model80 token80 prompt80 session80 library80", 18),
        ["learning80 model80", "token80 prompt80", "session80", "library80"],
    ),
    (
        ("learning80 model80 token80 prompt80 session80 library80", 28),
        ["learning80 model80 token80", "prompt80 session80 library80"],
    ),
    (
        ("model80 token80 prompt80 session80 library80 service80", 6),
        ["model80", "token80", "prompt80", "session80", "library80", "service80"],
    ),
    (
        ("model80 token80 prompt80 session80 library80 service80", 10),
        ["model80", "token80", "prompt80", "session80", "library80", "service80"],
    ),
    (
        ("model80 token80 prompt80 session80 library80 service80", 18),
        ["model80 token80", "prompt80 session80", "library80", "service80"],
    ),
    (
        ("model80 token80 prompt80 session80 library80 service80", 28),
        ["model80 token80 prompt80", "session80 library80", "service80"],
    ),
    (
        ("token80 prompt80 session80 library80 service80 gateway80", 6),
        ["token80", "prompt80", "session80", "library80", "service80", "gateway80"],
    ),
    (
        ("token80 prompt80 session80 library80 service80 gateway80", 10),
        ["token80", "prompt80", "session80", "library80", "service80", "gateway80"],
    ),
    (
        ("token80 prompt80 session80 library80 service80 gateway80", 18),
        ["token80 prompt80", "session80", "library80", "service80", "gateway80"],
    ),
    (
        ("token80 prompt80 session80 library80 service80 gateway80", 28),
        ["token80 prompt80 session80", "library80 service80", "gateway80"],
    ),
    (
        ("prompt80 session80 library80 service80 gateway80 storage80", 6),
        ["prompt80", "session80", "library80", "service80", "gateway80", "storage80"],
    ),
    (
        ("prompt80 session80 library80 service80 gateway80 storage80", 10),
        ["prompt80", "session80", "library80", "service80", "gateway80", "storage80"],
    ),
    (
        ("prompt80 session80 library80 service80 gateway80 storage80", 18),
        ["prompt80 session80", "library80", "service80", "gateway80", "storage80"],
    ),
    (
        ("prompt80 session80 library80 service80 gateway80 storage80", 28),
        ["prompt80 session80 library80", "service80 gateway80", "storage80"],
    ),
    (
        ("session80 library80 service80 gateway80 storage80 network80", 6),
        ["session80", "library80", "service80", "gateway80", "storage80", "network80"],
    ),
    (
        ("session80 library80 service80 gateway80 storage80 network80", 10),
        ["session80", "library80", "service80", "gateway80", "storage80", "network80"],
    ),
    (
        ("session80 library80 service80 gateway80 storage80 network80", 18),
        ["session80", "library80", "service80", "gateway80", "storage80", "network80"],
    ),
    (
        ("session80 library80 service80 gateway80 storage80 network80", 28),
        ["session80 library80", "service80 gateway80", "storage80 network80"],
    ),
    (
        ("library80 service80 gateway80 storage80 network80 latency80", 6),
        ["library80", "service80", "gateway80", "storage80", "network80", "latency80"],
    ),
    (
        ("library80 service80 gateway80 storage80 network80 latency80", 10),
        ["library80", "service80", "gateway80", "storage80", "network80", "latency80"],
    ),
    (
        ("library80 service80 gateway80 storage80 network80 latency80", 18),
        ["library80", "service80", "gateway80", "storage80", "network80", "latency80"],
    ),
    (
        ("library80 service80 gateway80 storage80 network80 latency80", 28),
        ["library80 service80", "gateway80 storage80", "network80 latency80"],
    ),
    (
        ("service80 gateway80 storage80 network80 latency80 buffer80", 6),
        ["service80", "gateway80", "storage80", "network80", "latency80", "buffer80"],
    ),
    (
        ("service80 gateway80 storage80 network80 latency80 buffer80", 10),
        ["service80", "gateway80", "storage80", "network80", "latency80", "buffer80"],
    ),
    (
        ("service80 gateway80 storage80 network80 latency80 buffer80", 18),
        ["service80", "gateway80", "storage80", "network80", "latency80 buffer80"],
    ),
    (
        ("service80 gateway80 storage80 network80 latency80 buffer80", 28),
        ["service80 gateway80", "storage80 network80", "latency80 buffer80"],
    ),
    (
        ("gateway80 storage80 network80 latency80 buffer80 queue80", 6),
        ["gateway80", "storage80", "network80", "latency80", "buffer80", "queue80"],
    ),
    (
        ("gateway80 storage80 network80 latency80 buffer80 queue80", 10),
        ["gateway80", "storage80", "network80", "latency80", "buffer80", "queue80"],
    ),
    (
        ("gateway80 storage80 network80 latency80 buffer80 queue80", 18),
        ["gateway80", "storage80", "network80", "latency80 buffer80", "queue80"],
    ),
    (
        ("gateway80 storage80 network80 latency80 buffer80 queue80", 28),
        ["gateway80 storage80", "network80 latency80 buffer80", "queue80"],
    ),
    (
        ("storage80 network80 latency80 buffer80 queue80 worker80", 6),
        ["storage80", "network80", "latency80", "buffer80", "queue80", "worker80"],
    ),
    (
        ("storage80 network80 latency80 buffer80 queue80 worker80", 10),
        ["storage80", "network80", "latency80", "buffer80", "queue80", "worker80"],
    ),
    (
        ("storage80 network80 latency80 buffer80 queue80 worker80", 18),
        ["storage80", "network80", "latency80 buffer80", "queue80 worker80"],
    ),
    (
        ("storage80 network80 latency80 buffer80 queue80 worker80", 28),
        ["storage80 network80", "latency80 buffer80 queue80", "worker80"],
    ),
    (
        ("network80 latency80 buffer80 queue80 worker80 kernel80", 6),
        ["network80", "latency80", "buffer80", "queue80", "worker80", "kernel80"],
    ),
    (
        ("network80 latency80 buffer80 queue80 worker80 kernel80", 10),
        ["network80", "latency80", "buffer80", "queue80", "worker80", "kernel80"],
    ),
    (
        ("network80 latency80 buffer80 queue80 worker80 kernel80", 18),
        ["network80", "latency80 buffer80", "queue80 worker80", "kernel80"],
    ),
    (
        ("network80 latency80 buffer80 queue80 worker80 kernel80", 28),
        ["network80 latency80 buffer80", "queue80 worker80 kernel80"],
    ),
    (
        ("latency80 buffer80 queue80 worker80 kernel80 signal80", 6),
        ["latency80", "buffer80", "queue80", "worker80", "kernel80", "signal80"],
    ),
    (
        ("latency80 buffer80 queue80 worker80 kernel80 signal80", 10),
        ["latency80", "buffer80", "queue80", "worker80", "kernel80", "signal80"],
    ),
    (
        ("latency80 buffer80 queue80 worker80 kernel80 signal80", 18),
        ["latency80 buffer80", "queue80 worker80", "kernel80 signal80"],
    ),
    (
        ("latency80 buffer80 queue80 worker80 kernel80 signal80", 28),
        ["latency80 buffer80 queue80", "worker80 kernel80 signal80"],
    ),
    (
        ("buffer80 queue80 worker80 kernel80 signal80 packet80", 6),
        ["buffer80", "queue80", "worker80", "kernel80", "signal80", "packet80"],
    ),
    (
        ("buffer80 queue80 worker80 kernel80 signal80 packet80", 10),
        ["buffer80", "queue80", "worker80", "kernel80", "signal80", "packet80"],
    ),
    (
        ("buffer80 queue80 worker80 kernel80 signal80 packet80", 18),
        ["buffer80 queue80", "worker80 kernel80", "signal80 packet80"],
    ),
    (
        ("buffer80 queue80 worker80 kernel80 signal80 packet80", 28),
        ["buffer80 queue80 worker80", "kernel80 signal80 packet80"],
    ),
    (
        ("queue80 worker80 kernel80 signal80 packet80 router80", 6),
        ["queue80", "worker80", "kernel80", "signal80", "packet80", "router80"],
    ),
    (
        ("queue80 worker80 kernel80 signal80 packet80 router80", 10),
        ["queue80", "worker80", "kernel80", "signal80", "packet80", "router80"],
    ),
    (
        ("queue80 worker80 kernel80 signal80 packet80 router80", 18),
        ["queue80 worker80", "kernel80 signal80", "packet80 router80"],
    ),
    (
        ("queue80 worker80 kernel80 signal80 packet80 router80", 28),
        ["queue80 worker80 kernel80", "signal80 packet80 router80"],
    ),
    (
        ("worker80 kernel80 signal80 packet80 router80 cluster80", 6),
        ["worker80", "kernel80", "signal80", "packet80", "router80", "cluster80"],
    ),
    (
        ("worker80 kernel80 signal80 packet80 router80 cluster80", 10),
        ["worker80", "kernel80", "signal80", "packet80", "router80", "cluster80"],
    ),
    (
        ("worker80 kernel80 signal80 packet80 router80 cluster80", 18),
        ["worker80 kernel80", "signal80 packet80", "router80 cluster80"],
    ),
    (
        ("worker80 kernel80 signal80 packet80 router80 cluster80", 28),
        ["worker80 kernel80 signal80", "packet80 router80 cluster80"],
    ),
    (
        ("kernel80 signal80 packet80 router80 cluster80 mirror80", 6),
        ["kernel80", "signal80", "packet80", "router80", "cluster80", "mirror80"],
    ),
    (
        ("kernel80 signal80 packet80 router80 cluster80 mirror80", 10),
        ["kernel80", "signal80", "packet80", "router80", "cluster80", "mirror80"],
    ),
    (
        ("kernel80 signal80 packet80 router80 cluster80 mirror80", 18),
        ["kernel80 signal80", "packet80 router80", "cluster80 mirror80"],
    ),
    (
        ("kernel80 signal80 packet80 router80 cluster80 mirror80", 28),
        ["kernel80 signal80 packet80", "router80 cluster80 mirror80"],
    ),
    (
        ("signal80 packet80 router80 cluster80 mirror80 filter80", 6),
        ["signal80", "packet80", "router80", "cluster80", "mirror80", "filter80"],
    ),
    (
        ("signal80 packet80 router80 cluster80 mirror80 filter80", 10),
        ["signal80", "packet80", "router80", "cluster80", "mirror80", "filter80"],
    ),
    (
        ("signal80 packet80 router80 cluster80 mirror80 filter80", 18),
        ["signal80 packet80", "router80 cluster80", "mirror80 filter80"],
    ),
    (
        ("signal80 packet80 router80 cluster80 mirror80 filter80", 28),
        ["signal80 packet80 router80", "cluster80 mirror80 filter80"],
    ),
    (
        ("packet80 router80 cluster80 mirror80 filter80 ranking80", 6),
        ["packet80", "router80", "cluster80", "mirror80", "filter80", "ranking80"],
    ),
    (
        ("packet80 router80 cluster80 mirror80 filter80 ranking80", 10),
        ["packet80", "router80", "cluster80", "mirror80", "filter80", "ranking80"],
    ),
    (
        ("packet80 router80 cluster80 mirror80 filter80 ranking80", 18),
        ["packet80 router80", "cluster80 mirror80", "filter80 ranking80"],
    ),
    (
        ("packet80 router80 cluster80 mirror80 filter80 ranking80", 28),
        ["packet80 router80 cluster80", "mirror80 filter80 ranking80"],
    ),
    (
        ("router80 cluster80 mirror80 filter80 ranking80 encoding80", 6),
        ["router80", "cluster80", "mirror80", "filter80", "ranking80", "encoding80"],
    ),
    (
        ("router80 cluster80 mirror80 filter80 ranking80 encoding80", 10),
        ["router80", "cluster80", "mirror80", "filter80", "ranking80", "encoding80"],
    ),
    (
        ("router80 cluster80 mirror80 filter80 ranking80 encoding80", 18),
        ["router80 cluster80", "mirror80 filter80", "ranking80", "encoding80"],
    ),
    (
        ("router80 cluster80 mirror80 filter80 ranking80 encoding80", 28),
        ["router80 cluster80 mirror80", "filter80 ranking80", "encoding80"],
    ),
    (
        ("cluster80 mirror80 filter80 ranking80 encoding80 mapping80", 6),
        ["cluster80", "mirror80", "filter80", "ranking80", "encoding80", "mapping80"],
    ),
    (
        ("cluster80 mirror80 filter80 ranking80 encoding80 mapping80", 10),
        ["cluster80", "mirror80", "filter80", "ranking80", "encoding80", "mapping80"],
    ),
    (
        ("cluster80 mirror80 filter80 ranking80 encoding80 mapping80", 18),
        ["cluster80 mirror80", "filter80 ranking80", "encoding80", "mapping80"],
    ),
    (
        ("cluster80 mirror80 filter80 ranking80 encoding80 mapping80", 28),
        ["cluster80 mirror80 filter80", "ranking80 encoding80", "mapping80"],
    ),
    (
        ("mirror80 filter80 ranking80 encoding80 mapping80 record80", 6),
        ["mirror80", "filter80", "ranking80", "encoding80", "mapping80", "record80"],
    ),
    (
        ("mirror80 filter80 ranking80 encoding80 mapping80 record80", 10),
        ["mirror80", "filter80", "ranking80", "encoding80", "mapping80", "record80"],
    ),
    (
        ("mirror80 filter80 ranking80 encoding80 mapping80 record80", 18),
        ["mirror80 filter80", "ranking80", "encoding80", "mapping80 record80"],
    ),
    (
        ("mirror80 filter80 ranking80 encoding80 mapping80 record80", 28),
        ["mirror80 filter80 ranking80", "encoding80 mapping80", "record80"],
    ),
    (
        ("filter80 ranking80 encoding80 mapping80 record80 candle80", 6),
        ["filter80", "ranking80", "encoding80", "mapping80", "record80", "candle80"],
    ),
    (
        ("filter80 ranking80 encoding80 mapping80 record80 candle80", 10),
        ["filter80", "ranking80", "encoding80", "mapping80", "record80", "candle80"],
    ),
    (
        ("filter80 ranking80 encoding80 mapping80 record80 candle80", 18),
        ["filter80 ranking80", "encoding80", "mapping80 record80", "candle80"],
    ),
    (
        ("filter80 ranking80 encoding80 mapping80 record80 candle80", 28),
        ["filter80 ranking80", "encoding80 mapping80", "record80 candle80"],
    ),
    (
        ("ranking80 encoding80 mapping80 record80 candle80 thread80", 6),
        ["ranking80", "encoding80", "mapping80", "record80", "candle80", "thread80"],
    ),
    (
        ("ranking80 encoding80 mapping80 record80 candle80 thread80", 10),
        ["ranking80", "encoding80", "mapping80", "record80", "candle80", "thread80"],
    ),
    (
        ("ranking80 encoding80 mapping80 record80 candle80 thread80", 18),
        ["ranking80", "encoding80", "mapping80 record80", "candle80 thread80"],
    ),
    (
        ("ranking80 encoding80 mapping80 record80 candle80 thread80", 28),
        ["ranking80 encoding80", "mapping80 record80 candle80", "thread80"],
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
