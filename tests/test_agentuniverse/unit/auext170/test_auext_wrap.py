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
        ("round 170: the quick brown fox jumps over the lazy dog", 4),
        ["round", "170:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", 8),
        ["round", "170: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", 12),
        ["round 170:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", 16),
        ["round 170: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", 24),
        ["round 170: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 170: the quick brown fox jumps over the lazy dog", 32),
        ["round 170: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", 4),
        ["round", "170:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", 8),
        ["round", "170:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", 12),
        ["round 170:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", 16),
        ["round 170:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", 24),
        ["round 170: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 170: agentuniverse is a framework for multi agents", 32),
        ["round 170: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", 4),
        ["round", "170:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", 8),
        ["round", "170:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", 12),
        ["round 170:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", 16),
        ["round 170:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", 24),
        ["round 170: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 170: knowledge stored as vectors enables retrieval", 32),
        ["round 170: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 170: the processor reads the record then stops", 4),
        ["round", "170:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 170: the processor reads the record then stops", 8),
        ["round", "170: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 170: the processor reads the record then stops", 12),
        ["round 170:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 170: the processor reads the record then stops", 16),
        ["round 170: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 170: the processor reads the record then stops", 24),
        ["round 170: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 170: the processor reads the record then stops", 32),
        ["round 170: the processor reads", "the record then stops"],
    ),
    (
        ("round 170: a worker pulls the next task from the queue", 4),
        ["round", "170:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 170: a worker pulls the next task from the queue", 8),
        ["round", "170: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 170: a worker pulls the next task from the queue", 12),
        ["round 170: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 170: a worker pulls the next task from the queue", 16),
        ["round 170: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 170: a worker pulls the next task from the queue", 24),
        ["round 170: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 170: a worker pulls the next task from the queue", 32),
        ["round 170: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 170: signals travel through the network layer", 4),
        ["round", "170:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 170: signals travel through the network layer", 8),
        ["round", "170:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 170: signals travel through the network layer", 12),
        ["round 170:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 170: signals travel through the network layer", 16),
        ["round 170:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 170: signals travel through the network layer", 24),
        ["round 170: signals", "travel through the", "network layer"],
    ),
    (
        ("round 170: signals travel through the network layer", 32),
        ["round 170: signals travel", "through the network layer"],
    ),
    (
        ("round 170: the gateway routes each request by policy", 4),
        ["round", "170:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 170: the gateway routes each request by policy", 8),
        ["round", "170: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 170: the gateway routes each request by policy", 12),
        ["round 170:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 170: the gateway routes each request by policy", 16),
        ["round 170: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 170: the gateway routes each request by policy", 24),
        ["round 170: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 170: the gateway routes each request by policy", 32),
        ["round 170: the gateway routes", "each request by policy"],
    ),
    (
        ("round 170: memory grows until the buffer is full", 4),
        ["round", "170:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 170: memory grows until the buffer is full", 8),
        ["round", "170:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 170: memory grows until the buffer is full", 12),
        ["round 170:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 170: memory grows until the buffer is full", 16),
        ["round 170:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 170: memory grows until the buffer is full", 24), ["round 170: memory grows", "until the buffer is full"]),
    (("round 170: memory grows until the buffer is full", 32), ["round 170: memory grows until", "the buffer is full"]),
    (
        ("round 170: the cluster mirrors every packet twice", 4),
        ["round", "170:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 170: the cluster mirrors every packet twice", 8),
        ["round", "170: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 170: the cluster mirrors every packet twice", 12),
        ["round 170:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 170: the cluster mirrors every packet twice", 16),
        ["round 170: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 170: the cluster mirrors every packet twice", 24),
        ["round 170: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 170: the cluster mirrors every packet twice", 32),
        ["round 170: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", 4),
        ["round", "170:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", 8),
        ["round", "170:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", 12),
        ["round 170:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", 16),
        ["round 170:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", 24),
        ["round 170: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 170: ranking uses tokens learned from the corpus", 32),
        ["round 170: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 170: a long session ends when the candle dies", 4),
        ["round", "170:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 170: a long session ends when the candle dies", 8),
        ["round", "170: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 170: a long session ends when the candle dies", 12),
        ["round 170: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 170: a long session ends when the candle dies", 16),
        ["round 170: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 170: a long session ends when the candle dies", 24),
        ["round 170: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 170: a long session ends when the candle dies", 32),
        ["round 170: a long session ends", "when the candle dies"],
    ),
    (
        ("round 170: encode the prompt then map the result", 4),
        ["round", "170:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 170: encode the prompt then map the result", 8),
        ["round", "170:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 170: encode the prompt then map the result", 12),
        ["round 170:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 170: encode the prompt then map the result", 16),
        ["round 170:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 170: encode the prompt then map the result", 24),
        ["round 170: encode the", "prompt then map the", "result"],
    ),
    (("round 170: encode the prompt then map the result", 32), ["round 170: encode the prompt", "then map the result"]),
    (
        ("round 170: the kernel wakes the worker at dawn", 4),
        ["round", "170:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 170: the kernel wakes the worker at dawn", 8),
        ["round", "170: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 170: the kernel wakes the worker at dawn", 12),
        ["round 170:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 170: the kernel wakes the worker at dawn", 16), ["round 170: the", "kernel wakes the", "worker at dawn"]),
    (("round 170: the kernel wakes the worker at dawn", 24), ["round 170: the kernel", "wakes the worker at dawn"]),
    (("round 170: the kernel wakes the worker at dawn", 32), ["round 170: the kernel wakes the", "worker at dawn"]),
    (
        ("round 170: service latency drops after the patch", 4),
        ["round", "170:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 170: service latency drops after the patch", 8),
        ["round", "170:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 170: service latency drops after the patch", 12),
        ["round 170:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 170: service latency drops after the patch", 16),
        ["round 170:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 170: service latency drops after the patch", 24),
        ["round 170: service", "latency drops after the", "patch"],
    ),
    (("round 170: service latency drops after the patch", 32), ["round 170: service latency drops", "after the patch"]),
    (
        ("round 170: the library caches every vector it sees", 4),
        ["round", "170:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 170: the library caches every vector it sees", 8),
        ["round", "170: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 170: the library caches every vector it sees", 12),
        ["round 170:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 170: the library caches every vector it sees", 16),
        ["round 170: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 170: the library caches every vector it sees", 24),
        ["round 170: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 170: the library caches every vector it sees", 32),
        ["round 170: the library caches", "every vector it sees"],
    ),
    (
        ("round 170: agents argue then the debate resolves", 4),
        ["round", "170:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 170: agents argue then the debate resolves", 8),
        ["round", "170:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 170: agents argue then the debate resolves", 12),
        ["round 170:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 170: agents argue then the debate resolves", 16),
        ["round 170:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 170: agents argue then the debate resolves", 24), ["round 170: agents argue", "then the debate resolves"]),
    (("round 170: agents argue then the debate resolves", 32), ["round 170: agents argue then the", "debate resolves"]),
    (
        ("round 170: the filter keeps only strong matches", 4),
        ["round", "170:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 170: the filter keeps only strong matches", 8),
        ["round", "170: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 170: the filter keeps only strong matches", 12),
        ["round 170:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 170: the filter keeps only strong matches", 16),
        ["round 170: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 170: the filter keeps only strong matches", 24),
        ["round 170: the filter", "keeps only strong", "matches"],
    ),
    (("round 170: the filter keeps only strong matches", 32), ["round 170: the filter keeps only", "strong matches"]),
    (
        ("round 170: the model answers with a short reply", 4),
        ["round", "170:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 170: the model answers with a short reply", 8),
        ["round", "170: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 170: the model answers with a short reply", 12),
        ["round 170:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 170: the model answers with a short reply", 16),
        ["round 170: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 170: the model answers with a short reply", 24),
        ["round 170: the model", "answers with a short", "reply"],
    ),
    (("round 170: the model answers with a short reply", 32), ["round 170: the model answers", "with a short reply"]),
    (
        ("round 170: the recorder stores the reasoning trace", 4),
        ["round", "170:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 170: the recorder stores the reasoning trace", 8),
        ["round", "170: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 170: the recorder stores the reasoning trace", 12),
        ["round 170:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 170: the recorder stores the reasoning trace", 16),
        ["round 170: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 170: the recorder stores the reasoning trace", 24),
        ["round 170: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 170: the recorder stores the reasoning trace", 32),
        ["round 170: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 170: the angel watches the processor run", 4),
        ["round", "170:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 170: the angel watches the processor run", 8),
        ["round", "170: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 170: the angel watches the processor run", 12),
        ["round 170:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 170: the angel watches the processor run", 16),
        ["round 170: the", "angel watches", "the processor", "run"],
    ),
    (("round 170: the angel watches the processor run", 24), ["round 170: the angel", "watches the processor", "run"]),
    (("round 170: the angel watches the processor run", 32), ["round 170: the angel watches the", "processor run"]),
    (
        ("round 170: angle of the vector decides the match", 4),
        ["round", "170:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 170: angle of the vector decides the match", 8),
        ["round", "170:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 170: angle of the vector decides the match", 12),
        ["round 170:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 170: angle of the vector decides the match", 16),
        ["round 170: angle", "of the vector", "decides the", "match"],
    ),
    (("round 170: angle of the vector decides the match", 24), ["round 170: angle of the", "vector decides the match"]),
    (("round 170: angle of the vector decides the match", 32), ["round 170: angle of the vector", "decides the match"]),
    (
        ("round 170: the candle burns twice as long at night", 4),
        ["round", "170:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 170: the candle burns twice as long at night", 8),
        ["round", "170: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 170: the candle burns twice as long at night", 12),
        ["round 170:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 170: the candle burns twice as long at night", 16),
        ["round 170: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 170: the candle burns twice as long at night", 24),
        ["round 170: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 170: the candle burns twice as long at night", 32),
        ["round 170: the candle burns", "twice as long at night"],
    ),
    (
        ("round 170: a mirror of the universe in one line", 4),
        ["round", "170:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 170: a mirror of the universe in one line", 8),
        ["round", "170: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 170: a mirror of the universe in one line", 12),
        ["round 170: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 170: a mirror of the universe in one line", 16),
        ["round 170: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 170: a mirror of the universe in one line", 24), ["round 170: a mirror of", "the universe in one line"]),
    (("round 170: a mirror of the universe in one line", 32), ["round 170: a mirror of the", "universe in one line"]),
    (
        ("round 170: the queue drains before the storm", 4),
        ["round", "170:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 170: the queue drains before the storm", 8),
        ["round", "170: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 170: the queue drains before the storm", 12),
        ["round 170:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 170: the queue drains before the storm", 16), ["round 170: the", "queue drains", "before the storm"]),
    (("round 170: the queue drains before the storm", 24), ["round 170: the queue", "drains before the storm"]),
    (("round 170: the queue drains before the storm", 32), ["round 170: the queue drains", "before the storm"]),
    (
        ("kitten170 sitting170 agent170 angle170 universe170 memory170", 6),
        ["kitten170", "sitting170", "agent170", "angle170", "universe170", "memory170"],
    ),
    (
        ("kitten170 sitting170 agent170 angle170 universe170 memory170", 10),
        ["kitten170", "sitting170", "agent170", "angle170", "universe170", "memory170"],
    ),
    (
        ("kitten170 sitting170 agent170 angle170 universe170 memory170", 18),
        ["kitten170", "sitting170", "agent170 angle170", "universe170", "memory170"],
    ),
    (
        ("kitten170 sitting170 agent170 angle170 universe170 memory170", 28),
        ["kitten170 sitting170", "agent170 angle170", "universe170 memory170"],
    ),
    (
        ("sitting170 agent170 angle170 universe170 memory170 stream170", 6),
        ["sitting170", "agent170", "angle170", "universe170", "memory170", "stream170"],
    ),
    (
        ("sitting170 agent170 angle170 universe170 memory170 stream170", 10),
        ["sitting170", "agent170", "angle170", "universe170", "memory170", "stream170"],
    ),
    (
        ("sitting170 agent170 angle170 universe170 memory170 stream170", 18),
        ["sitting170", "agent170 angle170", "universe170", "memory170", "stream170"],
    ),
    (
        ("sitting170 agent170 angle170 universe170 memory170 stream170", 28),
        ["sitting170 agent170 angle170", "universe170 memory170", "stream170"],
    ),
    (
        ("agent170 angle170 universe170 memory170 stream170 context170", 6),
        ["agent170", "angle170", "universe170", "memory170", "stream170", "context170"],
    ),
    (
        ("agent170 angle170 universe170 memory170 stream170 context170", 10),
        ["agent170", "angle170", "universe170", "memory170", "stream170", "context170"],
    ),
    (
        ("agent170 angle170 universe170 memory170 stream170 context170", 18),
        ["agent170 angle170", "universe170", "memory170", "stream170", "context170"],
    ),
    (
        ("agent170 angle170 universe170 memory170 stream170 context170", 28),
        ["agent170 angle170", "universe170 memory170", "stream170 context170"],
    ),
    (
        ("angle170 universe170 memory170 stream170 context170 knowledge170", 6),
        ["angle170", "universe170", "memory170", "stream170", "context170", "knowledge170"],
    ),
    (
        ("angle170 universe170 memory170 stream170 context170 knowledge170", 10),
        ["angle170", "universe170", "memory170", "stream170", "context170", "knowledge170"],
    ),
    (
        ("angle170 universe170 memory170 stream170 context170 knowledge170", 18),
        ["angle170", "universe170", "memory170", "stream170", "context170", "knowledge170"],
    ),
    (
        ("angle170 universe170 memory170 stream170 context170 knowledge170", 28),
        ["angle170 universe170", "memory170 stream170", "context170 knowledge170"],
    ),
    (
        ("universe170 memory170 stream170 context170 knowledge170 vector170", 6),
        ["universe170", "memory170", "stream170", "context170", "knowledge170", "vector170"],
    ),
    (
        ("universe170 memory170 stream170 context170 knowledge170 vector170", 10),
        ["universe170", "memory170", "stream170", "context170", "knowledge170", "vector170"],
    ),
    (
        ("universe170 memory170 stream170 context170 knowledge170 vector170", 18),
        ["universe170", "memory170", "stream170", "context170", "knowledge170", "vector170"],
    ),
    (
        ("universe170 memory170 stream170 context170 knowledge170 vector170", 28),
        ["universe170 memory170", "stream170 context170", "knowledge170 vector170"],
    ),
    (
        ("memory170 stream170 context170 knowledge170 vector170 processor170", 6),
        ["memory170", "stream170", "context170", "knowledge170", "vector170", "processor170"],
    ),
    (
        ("memory170 stream170 context170 knowledge170 vector170 processor170", 10),
        ["memory170", "stream170", "context170", "knowledge170", "vector170", "processor170"],
    ),
    (
        ("memory170 stream170 context170 knowledge170 vector170 processor170", 18),
        ["memory170", "stream170", "context170", "knowledge170", "vector170", "processor170"],
    ),
    (
        ("memory170 stream170 context170 knowledge170 vector170 processor170", 28),
        ["memory170 stream170", "context170 knowledge170", "vector170 processor170"],
    ),
    (
        ("stream170 context170 knowledge170 vector170 processor170 reasoning170", 6),
        ["stream170", "context170", "knowledge170", "vector170", "processor170", "reasoning170"],
    ),
    (
        ("stream170 context170 knowledge170 vector170 processor170 reasoning170", 10),
        ["stream170", "context170", "knowledge170", "vector170", "processor170", "reasoning170"],
    ),
    (
        ("stream170 context170 knowledge170 vector170 processor170 reasoning170", 18),
        ["stream170", "context170", "knowledge170", "vector170", "processor170", "reasoning170"],
    ),
    (
        ("stream170 context170 knowledge170 vector170 processor170 reasoning170", 28),
        ["stream170 context170", "knowledge170 vector170", "processor170 reasoning170"],
    ),
    (
        ("context170 knowledge170 vector170 processor170 reasoning170 machine170", 6),
        ["context170", "knowledge170", "vector170", "processor170", "reasoning170", "machine170"],
    ),
    (
        ("context170 knowledge170 vector170 processor170 reasoning170 machine170", 10),
        ["context170", "knowledge170", "vector170", "processor170", "reasoning170", "machine170"],
    ),
    (
        ("context170 knowledge170 vector170 processor170 reasoning170 machine170", 18),
        ["context170", "knowledge170", "vector170", "processor170", "reasoning170", "machine170"],
    ),
    (
        ("context170 knowledge170 vector170 processor170 reasoning170 machine170", 28),
        ["context170 knowledge170", "vector170 processor170", "reasoning170 machine170"],
    ),
    (
        ("knowledge170 vector170 processor170 reasoning170 machine170 learning170", 6),
        ["knowledge170", "vector170", "processor170", "reasoning170", "machine170", "learning170"],
    ),
    (
        ("knowledge170 vector170 processor170 reasoning170 machine170 learning170", 10),
        ["knowledge170", "vector170", "processor170", "reasoning170", "machine170", "learning170"],
    ),
    (
        ("knowledge170 vector170 processor170 reasoning170 machine170 learning170", 18),
        ["knowledge170", "vector170", "processor170", "reasoning170", "machine170", "learning170"],
    ),
    (
        ("knowledge170 vector170 processor170 reasoning170 machine170 learning170", 28),
        ["knowledge170 vector170", "processor170 reasoning170", "machine170 learning170"],
    ),
    (
        ("vector170 processor170 reasoning170 machine170 learning170 model170", 6),
        ["vector170", "processor170", "reasoning170", "machine170", "learning170", "model170"],
    ),
    (
        ("vector170 processor170 reasoning170 machine170 learning170 model170", 10),
        ["vector170", "processor170", "reasoning170", "machine170", "learning170", "model170"],
    ),
    (
        ("vector170 processor170 reasoning170 machine170 learning170 model170", 18),
        ["vector170", "processor170", "reasoning170", "machine170", "learning170", "model170"],
    ),
    (
        ("vector170 processor170 reasoning170 machine170 learning170 model170", 28),
        ["vector170 processor170", "reasoning170 machine170", "learning170 model170"],
    ),
    (
        ("processor170 reasoning170 machine170 learning170 model170 token170", 6),
        ["processor170", "reasoning170", "machine170", "learning170", "model170", "token170"],
    ),
    (
        ("processor170 reasoning170 machine170 learning170 model170 token170", 10),
        ["processor170", "reasoning170", "machine170", "learning170", "model170", "token170"],
    ),
    (
        ("processor170 reasoning170 machine170 learning170 model170 token170", 18),
        ["processor170", "reasoning170", "machine170", "learning170", "model170 token170"],
    ),
    (
        ("processor170 reasoning170 machine170 learning170 model170 token170", 28),
        ["processor170 reasoning170", "machine170 learning170", "model170 token170"],
    ),
    (
        ("reasoning170 machine170 learning170 model170 token170 prompt170", 6),
        ["reasoning170", "machine170", "learning170", "model170", "token170", "prompt170"],
    ),
    (
        ("reasoning170 machine170 learning170 model170 token170 prompt170", 10),
        ["reasoning170", "machine170", "learning170", "model170", "token170", "prompt170"],
    ),
    (
        ("reasoning170 machine170 learning170 model170 token170 prompt170", 18),
        ["reasoning170", "machine170", "learning170", "model170 token170", "prompt170"],
    ),
    (
        ("reasoning170 machine170 learning170 model170 token170 prompt170", 28),
        ["reasoning170 machine170", "learning170 model170", "token170 prompt170"],
    ),
    (
        ("machine170 learning170 model170 token170 prompt170 session170", 6),
        ["machine170", "learning170", "model170", "token170", "prompt170", "session170"],
    ),
    (
        ("machine170 learning170 model170 token170 prompt170 session170", 10),
        ["machine170", "learning170", "model170", "token170", "prompt170", "session170"],
    ),
    (
        ("machine170 learning170 model170 token170 prompt170 session170", 18),
        ["machine170", "learning170", "model170 token170", "prompt170", "session170"],
    ),
    (
        ("machine170 learning170 model170 token170 prompt170 session170", 28),
        ["machine170 learning170", "model170 token170 prompt170", "session170"],
    ),
    (
        ("learning170 model170 token170 prompt170 session170 library170", 6),
        ["learning170", "model170", "token170", "prompt170", "session170", "library170"],
    ),
    (
        ("learning170 model170 token170 prompt170 session170 library170", 10),
        ["learning170", "model170", "token170", "prompt170", "session170", "library170"],
    ),
    (
        ("learning170 model170 token170 prompt170 session170 library170", 18),
        ["learning170", "model170 token170", "prompt170", "session170", "library170"],
    ),
    (
        ("learning170 model170 token170 prompt170 session170 library170", 28),
        ["learning170 model170", "token170 prompt170", "session170 library170"],
    ),
    (
        ("model170 token170 prompt170 session170 library170 service170", 6),
        ["model170", "token170", "prompt170", "session170", "library170", "service170"],
    ),
    (
        ("model170 token170 prompt170 session170 library170 service170", 10),
        ["model170", "token170", "prompt170", "session170", "library170", "service170"],
    ),
    (
        ("model170 token170 prompt170 session170 library170 service170", 18),
        ["model170 token170", "prompt170", "session170", "library170", "service170"],
    ),
    (
        ("model170 token170 prompt170 session170 library170 service170", 28),
        ["model170 token170 prompt170", "session170 library170", "service170"],
    ),
    (
        ("token170 prompt170 session170 library170 service170 gateway170", 6),
        ["token170", "prompt170", "session170", "library170", "service170", "gateway170"],
    ),
    (
        ("token170 prompt170 session170 library170 service170 gateway170", 10),
        ["token170", "prompt170", "session170", "library170", "service170", "gateway170"],
    ),
    (
        ("token170 prompt170 session170 library170 service170 gateway170", 18),
        ["token170 prompt170", "session170", "library170", "service170", "gateway170"],
    ),
    (
        ("token170 prompt170 session170 library170 service170 gateway170", 28),
        ["token170 prompt170", "session170 library170", "service170 gateway170"],
    ),
    (
        ("prompt170 session170 library170 service170 gateway170 storage170", 6),
        ["prompt170", "session170", "library170", "service170", "gateway170", "storage170"],
    ),
    (
        ("prompt170 session170 library170 service170 gateway170 storage170", 10),
        ["prompt170", "session170", "library170", "service170", "gateway170", "storage170"],
    ),
    (
        ("prompt170 session170 library170 service170 gateway170 storage170", 18),
        ["prompt170", "session170", "library170", "service170", "gateway170", "storage170"],
    ),
    (
        ("prompt170 session170 library170 service170 gateway170 storage170", 28),
        ["prompt170 session170", "library170 service170", "gateway170 storage170"],
    ),
    (
        ("session170 library170 service170 gateway170 storage170 network170", 6),
        ["session170", "library170", "service170", "gateway170", "storage170", "network170"],
    ),
    (
        ("session170 library170 service170 gateway170 storage170 network170", 10),
        ["session170", "library170", "service170", "gateway170", "storage170", "network170"],
    ),
    (
        ("session170 library170 service170 gateway170 storage170 network170", 18),
        ["session170", "library170", "service170", "gateway170", "storage170", "network170"],
    ),
    (
        ("session170 library170 service170 gateway170 storage170 network170", 28),
        ["session170 library170", "service170 gateway170", "storage170 network170"],
    ),
    (
        ("library170 service170 gateway170 storage170 network170 latency170", 6),
        ["library170", "service170", "gateway170", "storage170", "network170", "latency170"],
    ),
    (
        ("library170 service170 gateway170 storage170 network170 latency170", 10),
        ["library170", "service170", "gateway170", "storage170", "network170", "latency170"],
    ),
    (
        ("library170 service170 gateway170 storage170 network170 latency170", 18),
        ["library170", "service170", "gateway170", "storage170", "network170", "latency170"],
    ),
    (
        ("library170 service170 gateway170 storage170 network170 latency170", 28),
        ["library170 service170", "gateway170 storage170", "network170 latency170"],
    ),
    (
        ("service170 gateway170 storage170 network170 latency170 buffer170", 6),
        ["service170", "gateway170", "storage170", "network170", "latency170", "buffer170"],
    ),
    (
        ("service170 gateway170 storage170 network170 latency170 buffer170", 10),
        ["service170", "gateway170", "storage170", "network170", "latency170", "buffer170"],
    ),
    (
        ("service170 gateway170 storage170 network170 latency170 buffer170", 18),
        ["service170", "gateway170", "storage170", "network170", "latency170", "buffer170"],
    ),
    (
        ("service170 gateway170 storage170 network170 latency170 buffer170", 28),
        ["service170 gateway170", "storage170 network170", "latency170 buffer170"],
    ),
    (
        ("gateway170 storage170 network170 latency170 buffer170 queue170", 6),
        ["gateway170", "storage170", "network170", "latency170", "buffer170", "queue170"],
    ),
    (
        ("gateway170 storage170 network170 latency170 buffer170 queue170", 10),
        ["gateway170", "storage170", "network170", "latency170", "buffer170", "queue170"],
    ),
    (
        ("gateway170 storage170 network170 latency170 buffer170 queue170", 18),
        ["gateway170", "storage170", "network170", "latency170", "buffer170 queue170"],
    ),
    (
        ("gateway170 storage170 network170 latency170 buffer170 queue170", 28),
        ["gateway170 storage170", "network170 latency170", "buffer170 queue170"],
    ),
    (
        ("storage170 network170 latency170 buffer170 queue170 worker170", 6),
        ["storage170", "network170", "latency170", "buffer170", "queue170", "worker170"],
    ),
    (
        ("storage170 network170 latency170 buffer170 queue170 worker170", 10),
        ["storage170", "network170", "latency170", "buffer170", "queue170", "worker170"],
    ),
    (
        ("storage170 network170 latency170 buffer170 queue170 worker170", 18),
        ["storage170", "network170", "latency170", "buffer170 queue170", "worker170"],
    ),
    (
        ("storage170 network170 latency170 buffer170 queue170 worker170", 28),
        ["storage170 network170", "latency170 buffer170", "queue170 worker170"],
    ),
    (
        ("network170 latency170 buffer170 queue170 worker170 kernel170", 6),
        ["network170", "latency170", "buffer170", "queue170", "worker170", "kernel170"],
    ),
    (
        ("network170 latency170 buffer170 queue170 worker170 kernel170", 10),
        ["network170", "latency170", "buffer170", "queue170", "worker170", "kernel170"],
    ),
    (
        ("network170 latency170 buffer170 queue170 worker170 kernel170", 18),
        ["network170", "latency170", "buffer170 queue170", "worker170", "kernel170"],
    ),
    (
        ("network170 latency170 buffer170 queue170 worker170 kernel170", 28),
        ["network170 latency170", "buffer170 queue170 worker170", "kernel170"],
    ),
    (
        ("latency170 buffer170 queue170 worker170 kernel170 signal170", 6),
        ["latency170", "buffer170", "queue170", "worker170", "kernel170", "signal170"],
    ),
    (
        ("latency170 buffer170 queue170 worker170 kernel170 signal170", 10),
        ["latency170", "buffer170", "queue170", "worker170", "kernel170", "signal170"],
    ),
    (
        ("latency170 buffer170 queue170 worker170 kernel170 signal170", 18),
        ["latency170", "buffer170 queue170", "worker170", "kernel170", "signal170"],
    ),
    (
        ("latency170 buffer170 queue170 worker170 kernel170 signal170", 28),
        ["latency170 buffer170", "queue170 worker170 kernel170", "signal170"],
    ),
    (
        ("buffer170 queue170 worker170 kernel170 signal170 packet170", 6),
        ["buffer170", "queue170", "worker170", "kernel170", "signal170", "packet170"],
    ),
    (
        ("buffer170 queue170 worker170 kernel170 signal170 packet170", 10),
        ["buffer170", "queue170", "worker170", "kernel170", "signal170", "packet170"],
    ),
    (
        ("buffer170 queue170 worker170 kernel170 signal170 packet170", 18),
        ["buffer170 queue170", "worker170", "kernel170", "signal170", "packet170"],
    ),
    (
        ("buffer170 queue170 worker170 kernel170 signal170 packet170", 28),
        ["buffer170 queue170 worker170", "kernel170 signal170", "packet170"],
    ),
    (
        ("queue170 worker170 kernel170 signal170 packet170 router170", 6),
        ["queue170", "worker170", "kernel170", "signal170", "packet170", "router170"],
    ),
    (
        ("queue170 worker170 kernel170 signal170 packet170 router170", 10),
        ["queue170", "worker170", "kernel170", "signal170", "packet170", "router170"],
    ),
    (
        ("queue170 worker170 kernel170 signal170 packet170 router170", 18),
        ["queue170 worker170", "kernel170", "signal170", "packet170", "router170"],
    ),
    (
        ("queue170 worker170 kernel170 signal170 packet170 router170", 28),
        ["queue170 worker170 kernel170", "signal170 packet170", "router170"],
    ),
    (
        ("worker170 kernel170 signal170 packet170 router170 cluster170", 6),
        ["worker170", "kernel170", "signal170", "packet170", "router170", "cluster170"],
    ),
    (
        ("worker170 kernel170 signal170 packet170 router170 cluster170", 10),
        ["worker170", "kernel170", "signal170", "packet170", "router170", "cluster170"],
    ),
    (
        ("worker170 kernel170 signal170 packet170 router170 cluster170", 18),
        ["worker170", "kernel170", "signal170", "packet170", "router170", "cluster170"],
    ),
    (
        ("worker170 kernel170 signal170 packet170 router170 cluster170", 28),
        ["worker170 kernel170", "signal170 packet170", "router170 cluster170"],
    ),
    (
        ("kernel170 signal170 packet170 router170 cluster170 mirror170", 6),
        ["kernel170", "signal170", "packet170", "router170", "cluster170", "mirror170"],
    ),
    (
        ("kernel170 signal170 packet170 router170 cluster170 mirror170", 10),
        ["kernel170", "signal170", "packet170", "router170", "cluster170", "mirror170"],
    ),
    (
        ("kernel170 signal170 packet170 router170 cluster170 mirror170", 18),
        ["kernel170", "signal170", "packet170", "router170", "cluster170", "mirror170"],
    ),
    (
        ("kernel170 signal170 packet170 router170 cluster170 mirror170", 28),
        ["kernel170 signal170", "packet170 router170", "cluster170 mirror170"],
    ),
    (
        ("signal170 packet170 router170 cluster170 mirror170 filter170", 6),
        ["signal170", "packet170", "router170", "cluster170", "mirror170", "filter170"],
    ),
    (
        ("signal170 packet170 router170 cluster170 mirror170 filter170", 10),
        ["signal170", "packet170", "router170", "cluster170", "mirror170", "filter170"],
    ),
    (
        ("signal170 packet170 router170 cluster170 mirror170 filter170", 18),
        ["signal170", "packet170", "router170", "cluster170", "mirror170", "filter170"],
    ),
    (
        ("signal170 packet170 router170 cluster170 mirror170 filter170", 28),
        ["signal170 packet170", "router170 cluster170", "mirror170 filter170"],
    ),
    (
        ("packet170 router170 cluster170 mirror170 filter170 ranking170", 6),
        ["packet170", "router170", "cluster170", "mirror170", "filter170", "ranking170"],
    ),
    (
        ("packet170 router170 cluster170 mirror170 filter170 ranking170", 10),
        ["packet170", "router170", "cluster170", "mirror170", "filter170", "ranking170"],
    ),
    (
        ("packet170 router170 cluster170 mirror170 filter170 ranking170", 18),
        ["packet170", "router170", "cluster170", "mirror170", "filter170", "ranking170"],
    ),
    (
        ("packet170 router170 cluster170 mirror170 filter170 ranking170", 28),
        ["packet170 router170", "cluster170 mirror170", "filter170 ranking170"],
    ),
    (
        ("router170 cluster170 mirror170 filter170 ranking170 encoding170", 6),
        ["router170", "cluster170", "mirror170", "filter170", "ranking170", "encoding170"],
    ),
    (
        ("router170 cluster170 mirror170 filter170 ranking170 encoding170", 10),
        ["router170", "cluster170", "mirror170", "filter170", "ranking170", "encoding170"],
    ),
    (
        ("router170 cluster170 mirror170 filter170 ranking170 encoding170", 18),
        ["router170", "cluster170", "mirror170", "filter170", "ranking170", "encoding170"],
    ),
    (
        ("router170 cluster170 mirror170 filter170 ranking170 encoding170", 28),
        ["router170 cluster170", "mirror170 filter170", "ranking170 encoding170"],
    ),
    (
        ("cluster170 mirror170 filter170 ranking170 encoding170 mapping170", 6),
        ["cluster170", "mirror170", "filter170", "ranking170", "encoding170", "mapping170"],
    ),
    (
        ("cluster170 mirror170 filter170 ranking170 encoding170 mapping170", 10),
        ["cluster170", "mirror170", "filter170", "ranking170", "encoding170", "mapping170"],
    ),
    (
        ("cluster170 mirror170 filter170 ranking170 encoding170 mapping170", 18),
        ["cluster170", "mirror170", "filter170", "ranking170", "encoding170", "mapping170"],
    ),
    (
        ("cluster170 mirror170 filter170 ranking170 encoding170 mapping170", 28),
        ["cluster170 mirror170", "filter170 ranking170", "encoding170 mapping170"],
    ),
    (
        ("mirror170 filter170 ranking170 encoding170 mapping170 record170", 6),
        ["mirror170", "filter170", "ranking170", "encoding170", "mapping170", "record170"],
    ),
    (
        ("mirror170 filter170 ranking170 encoding170 mapping170 record170", 10),
        ["mirror170", "filter170", "ranking170", "encoding170", "mapping170", "record170"],
    ),
    (
        ("mirror170 filter170 ranking170 encoding170 mapping170 record170", 18),
        ["mirror170", "filter170", "ranking170", "encoding170", "mapping170", "record170"],
    ),
    (
        ("mirror170 filter170 ranking170 encoding170 mapping170 record170", 28),
        ["mirror170 filter170", "ranking170 encoding170", "mapping170 record170"],
    ),
    (
        ("filter170 ranking170 encoding170 mapping170 record170 candle170", 6),
        ["filter170", "ranking170", "encoding170", "mapping170", "record170", "candle170"],
    ),
    (
        ("filter170 ranking170 encoding170 mapping170 record170 candle170", 10),
        ["filter170", "ranking170", "encoding170", "mapping170", "record170", "candle170"],
    ),
    (
        ("filter170 ranking170 encoding170 mapping170 record170 candle170", 18),
        ["filter170", "ranking170", "encoding170", "mapping170", "record170", "candle170"],
    ),
    (
        ("filter170 ranking170 encoding170 mapping170 record170 candle170", 28),
        ["filter170 ranking170", "encoding170 mapping170", "record170 candle170"],
    ),
    (
        ("ranking170 encoding170 mapping170 record170 candle170 thread170", 6),
        ["ranking170", "encoding170", "mapping170", "record170", "candle170", "thread170"],
    ),
    (
        ("ranking170 encoding170 mapping170 record170 candle170 thread170", 10),
        ["ranking170", "encoding170", "mapping170", "record170", "candle170", "thread170"],
    ),
    (
        ("ranking170 encoding170 mapping170 record170 candle170 thread170", 18),
        ["ranking170", "encoding170", "mapping170", "record170", "candle170", "thread170"],
    ),
    (
        ("ranking170 encoding170 mapping170 record170 candle170 thread170", 28),
        ["ranking170 encoding170", "mapping170 record170", "candle170 thread170"],
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
