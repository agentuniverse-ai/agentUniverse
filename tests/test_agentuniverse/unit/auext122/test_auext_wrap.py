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
        ("round 122: the quick brown fox jumps over the lazy dog", 4),
        ["round", "122:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", 8),
        ["round", "122: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", 12),
        ["round 122:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", 16),
        ["round 122: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", 24),
        ["round 122: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 122: the quick brown fox jumps over the lazy dog", 32),
        ["round 122: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", 4),
        ["round", "122:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", 8),
        ["round", "122:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", 12),
        ["round 122:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", 16),
        ["round 122:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", 24),
        ["round 122: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 122: agentuniverse is a framework for multi agents", 32),
        ["round 122: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", 4),
        ["round", "122:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", 8),
        ["round", "122:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", 12),
        ["round 122:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", 16),
        ["round 122:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", 24),
        ["round 122: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 122: knowledge stored as vectors enables retrieval", 32),
        ["round 122: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 122: the processor reads the record then stops", 4),
        ["round", "122:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 122: the processor reads the record then stops", 8),
        ["round", "122: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 122: the processor reads the record then stops", 12),
        ["round 122:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 122: the processor reads the record then stops", 16),
        ["round 122: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 122: the processor reads the record then stops", 24),
        ["round 122: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 122: the processor reads the record then stops", 32),
        ["round 122: the processor reads", "the record then stops"],
    ),
    (
        ("round 122: a worker pulls the next task from the queue", 4),
        ["round", "122:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 122: a worker pulls the next task from the queue", 8),
        ["round", "122: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 122: a worker pulls the next task from the queue", 12),
        ["round 122: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 122: a worker pulls the next task from the queue", 16),
        ["round 122: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 122: a worker pulls the next task from the queue", 24),
        ["round 122: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 122: a worker pulls the next task from the queue", 32),
        ["round 122: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 122: signals travel through the network layer", 4),
        ["round", "122:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 122: signals travel through the network layer", 8),
        ["round", "122:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 122: signals travel through the network layer", 12),
        ["round 122:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 122: signals travel through the network layer", 16),
        ["round 122:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 122: signals travel through the network layer", 24),
        ["round 122: signals", "travel through the", "network layer"],
    ),
    (
        ("round 122: signals travel through the network layer", 32),
        ["round 122: signals travel", "through the network layer"],
    ),
    (
        ("round 122: the gateway routes each request by policy", 4),
        ["round", "122:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 122: the gateway routes each request by policy", 8),
        ["round", "122: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 122: the gateway routes each request by policy", 12),
        ["round 122:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 122: the gateway routes each request by policy", 16),
        ["round 122: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 122: the gateway routes each request by policy", 24),
        ["round 122: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 122: the gateway routes each request by policy", 32),
        ["round 122: the gateway routes", "each request by policy"],
    ),
    (
        ("round 122: memory grows until the buffer is full", 4),
        ["round", "122:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 122: memory grows until the buffer is full", 8),
        ["round", "122:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 122: memory grows until the buffer is full", 12),
        ["round 122:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 122: memory grows until the buffer is full", 16),
        ["round 122:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 122: memory grows until the buffer is full", 24), ["round 122: memory grows", "until the buffer is full"]),
    (("round 122: memory grows until the buffer is full", 32), ["round 122: memory grows until", "the buffer is full"]),
    (
        ("round 122: the cluster mirrors every packet twice", 4),
        ["round", "122:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 122: the cluster mirrors every packet twice", 8),
        ["round", "122: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 122: the cluster mirrors every packet twice", 12),
        ["round 122:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 122: the cluster mirrors every packet twice", 16),
        ["round 122: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 122: the cluster mirrors every packet twice", 24),
        ["round 122: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 122: the cluster mirrors every packet twice", 32),
        ["round 122: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", 4),
        ["round", "122:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", 8),
        ["round", "122:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", 12),
        ["round 122:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", 16),
        ["round 122:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", 24),
        ["round 122: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 122: ranking uses tokens learned from the corpus", 32),
        ["round 122: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 122: a long session ends when the candle dies", 4),
        ["round", "122:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 122: a long session ends when the candle dies", 8),
        ["round", "122: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 122: a long session ends when the candle dies", 12),
        ["round 122: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 122: a long session ends when the candle dies", 16),
        ["round 122: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 122: a long session ends when the candle dies", 24),
        ["round 122: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 122: a long session ends when the candle dies", 32),
        ["round 122: a long session ends", "when the candle dies"],
    ),
    (
        ("round 122: encode the prompt then map the result", 4),
        ["round", "122:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 122: encode the prompt then map the result", 8),
        ["round", "122:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 122: encode the prompt then map the result", 12),
        ["round 122:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 122: encode the prompt then map the result", 16),
        ["round 122:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 122: encode the prompt then map the result", 24),
        ["round 122: encode the", "prompt then map the", "result"],
    ),
    (("round 122: encode the prompt then map the result", 32), ["round 122: encode the prompt", "then map the result"]),
    (
        ("round 122: the kernel wakes the worker at dawn", 4),
        ["round", "122:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 122: the kernel wakes the worker at dawn", 8),
        ["round", "122: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 122: the kernel wakes the worker at dawn", 12),
        ["round 122:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 122: the kernel wakes the worker at dawn", 16), ["round 122: the", "kernel wakes the", "worker at dawn"]),
    (("round 122: the kernel wakes the worker at dawn", 24), ["round 122: the kernel", "wakes the worker at dawn"]),
    (("round 122: the kernel wakes the worker at dawn", 32), ["round 122: the kernel wakes the", "worker at dawn"]),
    (
        ("round 122: service latency drops after the patch", 4),
        ["round", "122:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 122: service latency drops after the patch", 8),
        ["round", "122:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 122: service latency drops after the patch", 12),
        ["round 122:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 122: service latency drops after the patch", 16),
        ["round 122:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 122: service latency drops after the patch", 24),
        ["round 122: service", "latency drops after the", "patch"],
    ),
    (("round 122: service latency drops after the patch", 32), ["round 122: service latency drops", "after the patch"]),
    (
        ("round 122: the library caches every vector it sees", 4),
        ["round", "122:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 122: the library caches every vector it sees", 8),
        ["round", "122: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 122: the library caches every vector it sees", 12),
        ["round 122:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 122: the library caches every vector it sees", 16),
        ["round 122: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 122: the library caches every vector it sees", 24),
        ["round 122: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 122: the library caches every vector it sees", 32),
        ["round 122: the library caches", "every vector it sees"],
    ),
    (
        ("round 122: agents argue then the debate resolves", 4),
        ["round", "122:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 122: agents argue then the debate resolves", 8),
        ["round", "122:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 122: agents argue then the debate resolves", 12),
        ["round 122:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 122: agents argue then the debate resolves", 16),
        ["round 122:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 122: agents argue then the debate resolves", 24), ["round 122: agents argue", "then the debate resolves"]),
    (("round 122: agents argue then the debate resolves", 32), ["round 122: agents argue then the", "debate resolves"]),
    (
        ("round 122: the filter keeps only strong matches", 4),
        ["round", "122:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 122: the filter keeps only strong matches", 8),
        ["round", "122: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 122: the filter keeps only strong matches", 12),
        ["round 122:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 122: the filter keeps only strong matches", 16),
        ["round 122: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 122: the filter keeps only strong matches", 24),
        ["round 122: the filter", "keeps only strong", "matches"],
    ),
    (("round 122: the filter keeps only strong matches", 32), ["round 122: the filter keeps only", "strong matches"]),
    (
        ("round 122: the model answers with a short reply", 4),
        ["round", "122:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 122: the model answers with a short reply", 8),
        ["round", "122: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 122: the model answers with a short reply", 12),
        ["round 122:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 122: the model answers with a short reply", 16),
        ["round 122: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 122: the model answers with a short reply", 24),
        ["round 122: the model", "answers with a short", "reply"],
    ),
    (("round 122: the model answers with a short reply", 32), ["round 122: the model answers", "with a short reply"]),
    (
        ("round 122: the recorder stores the reasoning trace", 4),
        ["round", "122:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 122: the recorder stores the reasoning trace", 8),
        ["round", "122: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 122: the recorder stores the reasoning trace", 12),
        ["round 122:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 122: the recorder stores the reasoning trace", 16),
        ["round 122: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 122: the recorder stores the reasoning trace", 24),
        ["round 122: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 122: the recorder stores the reasoning trace", 32),
        ["round 122: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 122: the angel watches the processor run", 4),
        ["round", "122:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 122: the angel watches the processor run", 8),
        ["round", "122: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 122: the angel watches the processor run", 12),
        ["round 122:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 122: the angel watches the processor run", 16),
        ["round 122: the", "angel watches", "the processor", "run"],
    ),
    (("round 122: the angel watches the processor run", 24), ["round 122: the angel", "watches the processor", "run"]),
    (("round 122: the angel watches the processor run", 32), ["round 122: the angel watches the", "processor run"]),
    (
        ("round 122: angle of the vector decides the match", 4),
        ["round", "122:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 122: angle of the vector decides the match", 8),
        ["round", "122:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 122: angle of the vector decides the match", 12),
        ["round 122:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 122: angle of the vector decides the match", 16),
        ["round 122: angle", "of the vector", "decides the", "match"],
    ),
    (("round 122: angle of the vector decides the match", 24), ["round 122: angle of the", "vector decides the match"]),
    (("round 122: angle of the vector decides the match", 32), ["round 122: angle of the vector", "decides the match"]),
    (
        ("round 122: the candle burns twice as long at night", 4),
        ["round", "122:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 122: the candle burns twice as long at night", 8),
        ["round", "122: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 122: the candle burns twice as long at night", 12),
        ["round 122:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 122: the candle burns twice as long at night", 16),
        ["round 122: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 122: the candle burns twice as long at night", 24),
        ["round 122: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 122: the candle burns twice as long at night", 32),
        ["round 122: the candle burns", "twice as long at night"],
    ),
    (
        ("round 122: a mirror of the universe in one line", 4),
        ["round", "122:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 122: a mirror of the universe in one line", 8),
        ["round", "122: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 122: a mirror of the universe in one line", 12),
        ["round 122: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 122: a mirror of the universe in one line", 16),
        ["round 122: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 122: a mirror of the universe in one line", 24), ["round 122: a mirror of", "the universe in one line"]),
    (("round 122: a mirror of the universe in one line", 32), ["round 122: a mirror of the", "universe in one line"]),
    (
        ("round 122: the queue drains before the storm", 4),
        ["round", "122:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 122: the queue drains before the storm", 8),
        ["round", "122: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 122: the queue drains before the storm", 12),
        ["round 122:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 122: the queue drains before the storm", 16), ["round 122: the", "queue drains", "before the storm"]),
    (("round 122: the queue drains before the storm", 24), ["round 122: the queue", "drains before the storm"]),
    (("round 122: the queue drains before the storm", 32), ["round 122: the queue drains", "before the storm"]),
    (
        ("kitten122 sitting122 agent122 angle122 universe122 memory122", 6),
        ["kitten122", "sitting122", "agent122", "angle122", "universe122", "memory122"],
    ),
    (
        ("kitten122 sitting122 agent122 angle122 universe122 memory122", 10),
        ["kitten122", "sitting122", "agent122", "angle122", "universe122", "memory122"],
    ),
    (
        ("kitten122 sitting122 agent122 angle122 universe122 memory122", 18),
        ["kitten122", "sitting122", "agent122 angle122", "universe122", "memory122"],
    ),
    (
        ("kitten122 sitting122 agent122 angle122 universe122 memory122", 28),
        ["kitten122 sitting122", "agent122 angle122", "universe122 memory122"],
    ),
    (
        ("sitting122 agent122 angle122 universe122 memory122 stream122", 6),
        ["sitting122", "agent122", "angle122", "universe122", "memory122", "stream122"],
    ),
    (
        ("sitting122 agent122 angle122 universe122 memory122 stream122", 10),
        ["sitting122", "agent122", "angle122", "universe122", "memory122", "stream122"],
    ),
    (
        ("sitting122 agent122 angle122 universe122 memory122 stream122", 18),
        ["sitting122", "agent122 angle122", "universe122", "memory122", "stream122"],
    ),
    (
        ("sitting122 agent122 angle122 universe122 memory122 stream122", 28),
        ["sitting122 agent122 angle122", "universe122 memory122", "stream122"],
    ),
    (
        ("agent122 angle122 universe122 memory122 stream122 context122", 6),
        ["agent122", "angle122", "universe122", "memory122", "stream122", "context122"],
    ),
    (
        ("agent122 angle122 universe122 memory122 stream122 context122", 10),
        ["agent122", "angle122", "universe122", "memory122", "stream122", "context122"],
    ),
    (
        ("agent122 angle122 universe122 memory122 stream122 context122", 18),
        ["agent122 angle122", "universe122", "memory122", "stream122", "context122"],
    ),
    (
        ("agent122 angle122 universe122 memory122 stream122 context122", 28),
        ["agent122 angle122", "universe122 memory122", "stream122 context122"],
    ),
    (
        ("angle122 universe122 memory122 stream122 context122 knowledge122", 6),
        ["angle122", "universe122", "memory122", "stream122", "context122", "knowledge122"],
    ),
    (
        ("angle122 universe122 memory122 stream122 context122 knowledge122", 10),
        ["angle122", "universe122", "memory122", "stream122", "context122", "knowledge122"],
    ),
    (
        ("angle122 universe122 memory122 stream122 context122 knowledge122", 18),
        ["angle122", "universe122", "memory122", "stream122", "context122", "knowledge122"],
    ),
    (
        ("angle122 universe122 memory122 stream122 context122 knowledge122", 28),
        ["angle122 universe122", "memory122 stream122", "context122 knowledge122"],
    ),
    (
        ("universe122 memory122 stream122 context122 knowledge122 vector122", 6),
        ["universe122", "memory122", "stream122", "context122", "knowledge122", "vector122"],
    ),
    (
        ("universe122 memory122 stream122 context122 knowledge122 vector122", 10),
        ["universe122", "memory122", "stream122", "context122", "knowledge122", "vector122"],
    ),
    (
        ("universe122 memory122 stream122 context122 knowledge122 vector122", 18),
        ["universe122", "memory122", "stream122", "context122", "knowledge122", "vector122"],
    ),
    (
        ("universe122 memory122 stream122 context122 knowledge122 vector122", 28),
        ["universe122 memory122", "stream122 context122", "knowledge122 vector122"],
    ),
    (
        ("memory122 stream122 context122 knowledge122 vector122 processor122", 6),
        ["memory122", "stream122", "context122", "knowledge122", "vector122", "processor122"],
    ),
    (
        ("memory122 stream122 context122 knowledge122 vector122 processor122", 10),
        ["memory122", "stream122", "context122", "knowledge122", "vector122", "processor122"],
    ),
    (
        ("memory122 stream122 context122 knowledge122 vector122 processor122", 18),
        ["memory122", "stream122", "context122", "knowledge122", "vector122", "processor122"],
    ),
    (
        ("memory122 stream122 context122 knowledge122 vector122 processor122", 28),
        ["memory122 stream122", "context122 knowledge122", "vector122 processor122"],
    ),
    (
        ("stream122 context122 knowledge122 vector122 processor122 reasoning122", 6),
        ["stream122", "context122", "knowledge122", "vector122", "processor122", "reasoning122"],
    ),
    (
        ("stream122 context122 knowledge122 vector122 processor122 reasoning122", 10),
        ["stream122", "context122", "knowledge122", "vector122", "processor122", "reasoning122"],
    ),
    (
        ("stream122 context122 knowledge122 vector122 processor122 reasoning122", 18),
        ["stream122", "context122", "knowledge122", "vector122", "processor122", "reasoning122"],
    ),
    (
        ("stream122 context122 knowledge122 vector122 processor122 reasoning122", 28),
        ["stream122 context122", "knowledge122 vector122", "processor122 reasoning122"],
    ),
    (
        ("context122 knowledge122 vector122 processor122 reasoning122 machine122", 6),
        ["context122", "knowledge122", "vector122", "processor122", "reasoning122", "machine122"],
    ),
    (
        ("context122 knowledge122 vector122 processor122 reasoning122 machine122", 10),
        ["context122", "knowledge122", "vector122", "processor122", "reasoning122", "machine122"],
    ),
    (
        ("context122 knowledge122 vector122 processor122 reasoning122 machine122", 18),
        ["context122", "knowledge122", "vector122", "processor122", "reasoning122", "machine122"],
    ),
    (
        ("context122 knowledge122 vector122 processor122 reasoning122 machine122", 28),
        ["context122 knowledge122", "vector122 processor122", "reasoning122 machine122"],
    ),
    (
        ("knowledge122 vector122 processor122 reasoning122 machine122 learning122", 6),
        ["knowledge122", "vector122", "processor122", "reasoning122", "machine122", "learning122"],
    ),
    (
        ("knowledge122 vector122 processor122 reasoning122 machine122 learning122", 10),
        ["knowledge122", "vector122", "processor122", "reasoning122", "machine122", "learning122"],
    ),
    (
        ("knowledge122 vector122 processor122 reasoning122 machine122 learning122", 18),
        ["knowledge122", "vector122", "processor122", "reasoning122", "machine122", "learning122"],
    ),
    (
        ("knowledge122 vector122 processor122 reasoning122 machine122 learning122", 28),
        ["knowledge122 vector122", "processor122 reasoning122", "machine122 learning122"],
    ),
    (
        ("vector122 processor122 reasoning122 machine122 learning122 model122", 6),
        ["vector122", "processor122", "reasoning122", "machine122", "learning122", "model122"],
    ),
    (
        ("vector122 processor122 reasoning122 machine122 learning122 model122", 10),
        ["vector122", "processor122", "reasoning122", "machine122", "learning122", "model122"],
    ),
    (
        ("vector122 processor122 reasoning122 machine122 learning122 model122", 18),
        ["vector122", "processor122", "reasoning122", "machine122", "learning122", "model122"],
    ),
    (
        ("vector122 processor122 reasoning122 machine122 learning122 model122", 28),
        ["vector122 processor122", "reasoning122 machine122", "learning122 model122"],
    ),
    (
        ("processor122 reasoning122 machine122 learning122 model122 token122", 6),
        ["processor122", "reasoning122", "machine122", "learning122", "model122", "token122"],
    ),
    (
        ("processor122 reasoning122 machine122 learning122 model122 token122", 10),
        ["processor122", "reasoning122", "machine122", "learning122", "model122", "token122"],
    ),
    (
        ("processor122 reasoning122 machine122 learning122 model122 token122", 18),
        ["processor122", "reasoning122", "machine122", "learning122", "model122 token122"],
    ),
    (
        ("processor122 reasoning122 machine122 learning122 model122 token122", 28),
        ["processor122 reasoning122", "machine122 learning122", "model122 token122"],
    ),
    (
        ("reasoning122 machine122 learning122 model122 token122 prompt122", 6),
        ["reasoning122", "machine122", "learning122", "model122", "token122", "prompt122"],
    ),
    (
        ("reasoning122 machine122 learning122 model122 token122 prompt122", 10),
        ["reasoning122", "machine122", "learning122", "model122", "token122", "prompt122"],
    ),
    (
        ("reasoning122 machine122 learning122 model122 token122 prompt122", 18),
        ["reasoning122", "machine122", "learning122", "model122 token122", "prompt122"],
    ),
    (
        ("reasoning122 machine122 learning122 model122 token122 prompt122", 28),
        ["reasoning122 machine122", "learning122 model122", "token122 prompt122"],
    ),
    (
        ("machine122 learning122 model122 token122 prompt122 session122", 6),
        ["machine122", "learning122", "model122", "token122", "prompt122", "session122"],
    ),
    (
        ("machine122 learning122 model122 token122 prompt122 session122", 10),
        ["machine122", "learning122", "model122", "token122", "prompt122", "session122"],
    ),
    (
        ("machine122 learning122 model122 token122 prompt122 session122", 18),
        ["machine122", "learning122", "model122 token122", "prompt122", "session122"],
    ),
    (
        ("machine122 learning122 model122 token122 prompt122 session122", 28),
        ["machine122 learning122", "model122 token122 prompt122", "session122"],
    ),
    (
        ("learning122 model122 token122 prompt122 session122 library122", 6),
        ["learning122", "model122", "token122", "prompt122", "session122", "library122"],
    ),
    (
        ("learning122 model122 token122 prompt122 session122 library122", 10),
        ["learning122", "model122", "token122", "prompt122", "session122", "library122"],
    ),
    (
        ("learning122 model122 token122 prompt122 session122 library122", 18),
        ["learning122", "model122 token122", "prompt122", "session122", "library122"],
    ),
    (
        ("learning122 model122 token122 prompt122 session122 library122", 28),
        ["learning122 model122", "token122 prompt122", "session122 library122"],
    ),
    (
        ("model122 token122 prompt122 session122 library122 service122", 6),
        ["model122", "token122", "prompt122", "session122", "library122", "service122"],
    ),
    (
        ("model122 token122 prompt122 session122 library122 service122", 10),
        ["model122", "token122", "prompt122", "session122", "library122", "service122"],
    ),
    (
        ("model122 token122 prompt122 session122 library122 service122", 18),
        ["model122 token122", "prompt122", "session122", "library122", "service122"],
    ),
    (
        ("model122 token122 prompt122 session122 library122 service122", 28),
        ["model122 token122 prompt122", "session122 library122", "service122"],
    ),
    (
        ("token122 prompt122 session122 library122 service122 gateway122", 6),
        ["token122", "prompt122", "session122", "library122", "service122", "gateway122"],
    ),
    (
        ("token122 prompt122 session122 library122 service122 gateway122", 10),
        ["token122", "prompt122", "session122", "library122", "service122", "gateway122"],
    ),
    (
        ("token122 prompt122 session122 library122 service122 gateway122", 18),
        ["token122 prompt122", "session122", "library122", "service122", "gateway122"],
    ),
    (
        ("token122 prompt122 session122 library122 service122 gateway122", 28),
        ["token122 prompt122", "session122 library122", "service122 gateway122"],
    ),
    (
        ("prompt122 session122 library122 service122 gateway122 storage122", 6),
        ["prompt122", "session122", "library122", "service122", "gateway122", "storage122"],
    ),
    (
        ("prompt122 session122 library122 service122 gateway122 storage122", 10),
        ["prompt122", "session122", "library122", "service122", "gateway122", "storage122"],
    ),
    (
        ("prompt122 session122 library122 service122 gateway122 storage122", 18),
        ["prompt122", "session122", "library122", "service122", "gateway122", "storage122"],
    ),
    (
        ("prompt122 session122 library122 service122 gateway122 storage122", 28),
        ["prompt122 session122", "library122 service122", "gateway122 storage122"],
    ),
    (
        ("session122 library122 service122 gateway122 storage122 network122", 6),
        ["session122", "library122", "service122", "gateway122", "storage122", "network122"],
    ),
    (
        ("session122 library122 service122 gateway122 storage122 network122", 10),
        ["session122", "library122", "service122", "gateway122", "storage122", "network122"],
    ),
    (
        ("session122 library122 service122 gateway122 storage122 network122", 18),
        ["session122", "library122", "service122", "gateway122", "storage122", "network122"],
    ),
    (
        ("session122 library122 service122 gateway122 storage122 network122", 28),
        ["session122 library122", "service122 gateway122", "storage122 network122"],
    ),
    (
        ("library122 service122 gateway122 storage122 network122 latency122", 6),
        ["library122", "service122", "gateway122", "storage122", "network122", "latency122"],
    ),
    (
        ("library122 service122 gateway122 storage122 network122 latency122", 10),
        ["library122", "service122", "gateway122", "storage122", "network122", "latency122"],
    ),
    (
        ("library122 service122 gateway122 storage122 network122 latency122", 18),
        ["library122", "service122", "gateway122", "storage122", "network122", "latency122"],
    ),
    (
        ("library122 service122 gateway122 storage122 network122 latency122", 28),
        ["library122 service122", "gateway122 storage122", "network122 latency122"],
    ),
    (
        ("service122 gateway122 storage122 network122 latency122 buffer122", 6),
        ["service122", "gateway122", "storage122", "network122", "latency122", "buffer122"],
    ),
    (
        ("service122 gateway122 storage122 network122 latency122 buffer122", 10),
        ["service122", "gateway122", "storage122", "network122", "latency122", "buffer122"],
    ),
    (
        ("service122 gateway122 storage122 network122 latency122 buffer122", 18),
        ["service122", "gateway122", "storage122", "network122", "latency122", "buffer122"],
    ),
    (
        ("service122 gateway122 storage122 network122 latency122 buffer122", 28),
        ["service122 gateway122", "storage122 network122", "latency122 buffer122"],
    ),
    (
        ("gateway122 storage122 network122 latency122 buffer122 queue122", 6),
        ["gateway122", "storage122", "network122", "latency122", "buffer122", "queue122"],
    ),
    (
        ("gateway122 storage122 network122 latency122 buffer122 queue122", 10),
        ["gateway122", "storage122", "network122", "latency122", "buffer122", "queue122"],
    ),
    (
        ("gateway122 storage122 network122 latency122 buffer122 queue122", 18),
        ["gateway122", "storage122", "network122", "latency122", "buffer122 queue122"],
    ),
    (
        ("gateway122 storage122 network122 latency122 buffer122 queue122", 28),
        ["gateway122 storage122", "network122 latency122", "buffer122 queue122"],
    ),
    (
        ("storage122 network122 latency122 buffer122 queue122 worker122", 6),
        ["storage122", "network122", "latency122", "buffer122", "queue122", "worker122"],
    ),
    (
        ("storage122 network122 latency122 buffer122 queue122 worker122", 10),
        ["storage122", "network122", "latency122", "buffer122", "queue122", "worker122"],
    ),
    (
        ("storage122 network122 latency122 buffer122 queue122 worker122", 18),
        ["storage122", "network122", "latency122", "buffer122 queue122", "worker122"],
    ),
    (
        ("storage122 network122 latency122 buffer122 queue122 worker122", 28),
        ["storage122 network122", "latency122 buffer122", "queue122 worker122"],
    ),
    (
        ("network122 latency122 buffer122 queue122 worker122 kernel122", 6),
        ["network122", "latency122", "buffer122", "queue122", "worker122", "kernel122"],
    ),
    (
        ("network122 latency122 buffer122 queue122 worker122 kernel122", 10),
        ["network122", "latency122", "buffer122", "queue122", "worker122", "kernel122"],
    ),
    (
        ("network122 latency122 buffer122 queue122 worker122 kernel122", 18),
        ["network122", "latency122", "buffer122 queue122", "worker122", "kernel122"],
    ),
    (
        ("network122 latency122 buffer122 queue122 worker122 kernel122", 28),
        ["network122 latency122", "buffer122 queue122 worker122", "kernel122"],
    ),
    (
        ("latency122 buffer122 queue122 worker122 kernel122 signal122", 6),
        ["latency122", "buffer122", "queue122", "worker122", "kernel122", "signal122"],
    ),
    (
        ("latency122 buffer122 queue122 worker122 kernel122 signal122", 10),
        ["latency122", "buffer122", "queue122", "worker122", "kernel122", "signal122"],
    ),
    (
        ("latency122 buffer122 queue122 worker122 kernel122 signal122", 18),
        ["latency122", "buffer122 queue122", "worker122", "kernel122", "signal122"],
    ),
    (
        ("latency122 buffer122 queue122 worker122 kernel122 signal122", 28),
        ["latency122 buffer122", "queue122 worker122 kernel122", "signal122"],
    ),
    (
        ("buffer122 queue122 worker122 kernel122 signal122 packet122", 6),
        ["buffer122", "queue122", "worker122", "kernel122", "signal122", "packet122"],
    ),
    (
        ("buffer122 queue122 worker122 kernel122 signal122 packet122", 10),
        ["buffer122", "queue122", "worker122", "kernel122", "signal122", "packet122"],
    ),
    (
        ("buffer122 queue122 worker122 kernel122 signal122 packet122", 18),
        ["buffer122 queue122", "worker122", "kernel122", "signal122", "packet122"],
    ),
    (
        ("buffer122 queue122 worker122 kernel122 signal122 packet122", 28),
        ["buffer122 queue122 worker122", "kernel122 signal122", "packet122"],
    ),
    (
        ("queue122 worker122 kernel122 signal122 packet122 router122", 6),
        ["queue122", "worker122", "kernel122", "signal122", "packet122", "router122"],
    ),
    (
        ("queue122 worker122 kernel122 signal122 packet122 router122", 10),
        ["queue122", "worker122", "kernel122", "signal122", "packet122", "router122"],
    ),
    (
        ("queue122 worker122 kernel122 signal122 packet122 router122", 18),
        ["queue122 worker122", "kernel122", "signal122", "packet122", "router122"],
    ),
    (
        ("queue122 worker122 kernel122 signal122 packet122 router122", 28),
        ["queue122 worker122 kernel122", "signal122 packet122", "router122"],
    ),
    (
        ("worker122 kernel122 signal122 packet122 router122 cluster122", 6),
        ["worker122", "kernel122", "signal122", "packet122", "router122", "cluster122"],
    ),
    (
        ("worker122 kernel122 signal122 packet122 router122 cluster122", 10),
        ["worker122", "kernel122", "signal122", "packet122", "router122", "cluster122"],
    ),
    (
        ("worker122 kernel122 signal122 packet122 router122 cluster122", 18),
        ["worker122", "kernel122", "signal122", "packet122", "router122", "cluster122"],
    ),
    (
        ("worker122 kernel122 signal122 packet122 router122 cluster122", 28),
        ["worker122 kernel122", "signal122 packet122", "router122 cluster122"],
    ),
    (
        ("kernel122 signal122 packet122 router122 cluster122 mirror122", 6),
        ["kernel122", "signal122", "packet122", "router122", "cluster122", "mirror122"],
    ),
    (
        ("kernel122 signal122 packet122 router122 cluster122 mirror122", 10),
        ["kernel122", "signal122", "packet122", "router122", "cluster122", "mirror122"],
    ),
    (
        ("kernel122 signal122 packet122 router122 cluster122 mirror122", 18),
        ["kernel122", "signal122", "packet122", "router122", "cluster122", "mirror122"],
    ),
    (
        ("kernel122 signal122 packet122 router122 cluster122 mirror122", 28),
        ["kernel122 signal122", "packet122 router122", "cluster122 mirror122"],
    ),
    (
        ("signal122 packet122 router122 cluster122 mirror122 filter122", 6),
        ["signal122", "packet122", "router122", "cluster122", "mirror122", "filter122"],
    ),
    (
        ("signal122 packet122 router122 cluster122 mirror122 filter122", 10),
        ["signal122", "packet122", "router122", "cluster122", "mirror122", "filter122"],
    ),
    (
        ("signal122 packet122 router122 cluster122 mirror122 filter122", 18),
        ["signal122", "packet122", "router122", "cluster122", "mirror122", "filter122"],
    ),
    (
        ("signal122 packet122 router122 cluster122 mirror122 filter122", 28),
        ["signal122 packet122", "router122 cluster122", "mirror122 filter122"],
    ),
    (
        ("packet122 router122 cluster122 mirror122 filter122 ranking122", 6),
        ["packet122", "router122", "cluster122", "mirror122", "filter122", "ranking122"],
    ),
    (
        ("packet122 router122 cluster122 mirror122 filter122 ranking122", 10),
        ["packet122", "router122", "cluster122", "mirror122", "filter122", "ranking122"],
    ),
    (
        ("packet122 router122 cluster122 mirror122 filter122 ranking122", 18),
        ["packet122", "router122", "cluster122", "mirror122", "filter122", "ranking122"],
    ),
    (
        ("packet122 router122 cluster122 mirror122 filter122 ranking122", 28),
        ["packet122 router122", "cluster122 mirror122", "filter122 ranking122"],
    ),
    (
        ("router122 cluster122 mirror122 filter122 ranking122 encoding122", 6),
        ["router122", "cluster122", "mirror122", "filter122", "ranking122", "encoding122"],
    ),
    (
        ("router122 cluster122 mirror122 filter122 ranking122 encoding122", 10),
        ["router122", "cluster122", "mirror122", "filter122", "ranking122", "encoding122"],
    ),
    (
        ("router122 cluster122 mirror122 filter122 ranking122 encoding122", 18),
        ["router122", "cluster122", "mirror122", "filter122", "ranking122", "encoding122"],
    ),
    (
        ("router122 cluster122 mirror122 filter122 ranking122 encoding122", 28),
        ["router122 cluster122", "mirror122 filter122", "ranking122 encoding122"],
    ),
    (
        ("cluster122 mirror122 filter122 ranking122 encoding122 mapping122", 6),
        ["cluster122", "mirror122", "filter122", "ranking122", "encoding122", "mapping122"],
    ),
    (
        ("cluster122 mirror122 filter122 ranking122 encoding122 mapping122", 10),
        ["cluster122", "mirror122", "filter122", "ranking122", "encoding122", "mapping122"],
    ),
    (
        ("cluster122 mirror122 filter122 ranking122 encoding122 mapping122", 18),
        ["cluster122", "mirror122", "filter122", "ranking122", "encoding122", "mapping122"],
    ),
    (
        ("cluster122 mirror122 filter122 ranking122 encoding122 mapping122", 28),
        ["cluster122 mirror122", "filter122 ranking122", "encoding122 mapping122"],
    ),
    (
        ("mirror122 filter122 ranking122 encoding122 mapping122 record122", 6),
        ["mirror122", "filter122", "ranking122", "encoding122", "mapping122", "record122"],
    ),
    (
        ("mirror122 filter122 ranking122 encoding122 mapping122 record122", 10),
        ["mirror122", "filter122", "ranking122", "encoding122", "mapping122", "record122"],
    ),
    (
        ("mirror122 filter122 ranking122 encoding122 mapping122 record122", 18),
        ["mirror122", "filter122", "ranking122", "encoding122", "mapping122", "record122"],
    ),
    (
        ("mirror122 filter122 ranking122 encoding122 mapping122 record122", 28),
        ["mirror122 filter122", "ranking122 encoding122", "mapping122 record122"],
    ),
    (
        ("filter122 ranking122 encoding122 mapping122 record122 candle122", 6),
        ["filter122", "ranking122", "encoding122", "mapping122", "record122", "candle122"],
    ),
    (
        ("filter122 ranking122 encoding122 mapping122 record122 candle122", 10),
        ["filter122", "ranking122", "encoding122", "mapping122", "record122", "candle122"],
    ),
    (
        ("filter122 ranking122 encoding122 mapping122 record122 candle122", 18),
        ["filter122", "ranking122", "encoding122", "mapping122", "record122", "candle122"],
    ),
    (
        ("filter122 ranking122 encoding122 mapping122 record122 candle122", 28),
        ["filter122 ranking122", "encoding122 mapping122", "record122 candle122"],
    ),
    (
        ("ranking122 encoding122 mapping122 record122 candle122 thread122", 6),
        ["ranking122", "encoding122", "mapping122", "record122", "candle122", "thread122"],
    ),
    (
        ("ranking122 encoding122 mapping122 record122 candle122 thread122", 10),
        ["ranking122", "encoding122", "mapping122", "record122", "candle122", "thread122"],
    ),
    (
        ("ranking122 encoding122 mapping122 record122 candle122 thread122", 18),
        ["ranking122", "encoding122", "mapping122", "record122", "candle122", "thread122"],
    ),
    (
        ("ranking122 encoding122 mapping122 record122 candle122 thread122", 28),
        ["ranking122 encoding122", "mapping122 record122", "candle122 thread122"],
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
