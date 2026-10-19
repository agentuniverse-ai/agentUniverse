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
        ("round 99: the quick brown fox jumps over the lazy dog", 4),
        ["round", "99:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 99: the quick brown fox jumps over the lazy dog", 8),
        ["round", "99: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 99: the quick brown fox jumps over the lazy dog", 12),
        ["round 99:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 99: the quick brown fox jumps over the lazy dog", 16),
        ["round 99: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 99: the quick brown fox jumps over the lazy dog", 24),
        ["round 99: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 99: the quick brown fox jumps over the lazy dog", 32),
        ["round 99: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 99: agentuniverse is a framework for multi agents", 4),
        ["round", "99:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 99: agentuniverse is a framework for multi agents", 8),
        ["round", "99:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 99: agentuniverse is a framework for multi agents", 12),
        ["round 99:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 99: agentuniverse is a framework for multi agents", 16),
        ["round 99:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 99: agentuniverse is a framework for multi agents", 24),
        ["round 99: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 99: agentuniverse is a framework for multi agents", 32),
        ["round 99: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 99: knowledge stored as vectors enables retrieval", 4),
        ["round", "99:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 99: knowledge stored as vectors enables retrieval", 8),
        ["round", "99:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 99: knowledge stored as vectors enables retrieval", 12),
        ["round 99:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 99: knowledge stored as vectors enables retrieval", 16),
        ["round 99:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 99: knowledge stored as vectors enables retrieval", 24),
        ["round 99: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 99: knowledge stored as vectors enables retrieval", 32),
        ["round 99: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 99: the processor reads the record then stops", 4),
        ["round", "99:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 99: the processor reads the record then stops", 8),
        ["round", "99: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 99: the processor reads the record then stops", 12),
        ["round 99:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 99: the processor reads the record then stops", 16),
        ["round 99: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 99: the processor reads the record then stops", 24),
        ["round 99: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 99: the processor reads the record then stops", 32),
        ["round 99: the processor reads", "the record then stops"],
    ),
    (
        ("round 99: a worker pulls the next task from the queue", 4),
        ["round", "99:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 99: a worker pulls the next task from the queue", 8),
        ["round", "99: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 99: a worker pulls the next task from the queue", 12),
        ["round 99: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 99: a worker pulls the next task from the queue", 16),
        ["round 99: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 99: a worker pulls the next task from the queue", 24),
        ["round 99: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 99: a worker pulls the next task from the queue", 32),
        ["round 99: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 99: signals travel through the network layer", 4),
        ["round", "99:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 99: signals travel through the network layer", 8),
        ["round", "99:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 99: signals travel through the network layer", 12),
        ["round 99:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 99: signals travel through the network layer", 16),
        ["round 99:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 99: signals travel through the network layer", 24),
        ["round 99: signals travel", "through the network", "layer"],
    ),
    (
        ("round 99: signals travel through the network layer", 32),
        ["round 99: signals travel through", "the network layer"],
    ),
    (
        ("round 99: the gateway routes each request by policy", 4),
        ["round", "99:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 99: the gateway routes each request by policy", 8),
        ["round", "99: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 99: the gateway routes each request by policy", 12),
        ["round 99:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 99: the gateway routes each request by policy", 16),
        ["round 99: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 99: the gateway routes each request by policy", 24),
        ["round 99: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 99: the gateway routes each request by policy", 32),
        ["round 99: the gateway routes", "each request by policy"],
    ),
    (
        ("round 99: memory grows until the buffer is full", 4),
        ["round", "99:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 99: memory grows until the buffer is full", 8),
        ["round", "99:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 99: memory grows until the buffer is full", 12),
        ["round 99:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 99: memory grows until the buffer is full", 16),
        ["round 99: memory", "grows until the", "buffer is full"],
    ),
    (("round 99: memory grows until the buffer is full", 24), ["round 99: memory grows", "until the buffer is full"]),
    (("round 99: memory grows until the buffer is full", 32), ["round 99: memory grows until the", "buffer is full"]),
    (
        ("round 99: the cluster mirrors every packet twice", 4),
        ["round", "99:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 99: the cluster mirrors every packet twice", 8),
        ["round", "99: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 99: the cluster mirrors every packet twice", 12),
        ["round 99:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 99: the cluster mirrors every packet twice", 16),
        ["round 99: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 99: the cluster mirrors every packet twice", 24),
        ["round 99: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 99: the cluster mirrors every packet twice", 32), ["round 99: the cluster mirrors", "every packet twice"]),
    (
        ("round 99: ranking uses tokens learned from the corpus", 4),
        ["round", "99:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 99: ranking uses tokens learned from the corpus", 8),
        ["round", "99:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 99: ranking uses tokens learned from the corpus", 12),
        ["round 99:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 99: ranking uses tokens learned from the corpus", 16),
        ["round 99:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 99: ranking uses tokens learned from the corpus", 24),
        ["round 99: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 99: ranking uses tokens learned from the corpus", 32),
        ["round 99: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 99: a long session ends when the candle dies", 4),
        ["round", "99:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 99: a long session ends when the candle dies", 8),
        ["round", "99: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 99: a long session ends when the candle dies", 12),
        ["round 99: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 99: a long session ends when the candle dies", 16),
        ["round 99: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 99: a long session ends when the candle dies", 24),
        ["round 99: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 99: a long session ends when the candle dies", 32),
        ["round 99: a long session ends", "when the candle dies"],
    ),
    (
        ("round 99: encode the prompt then map the result", 4),
        ["round", "99:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 99: encode the prompt then map the result", 8),
        ["round", "99:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 99: encode the prompt then map the result", 12),
        ["round 99:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 99: encode the prompt then map the result", 16),
        ["round 99: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 99: encode the prompt then map the result", 24),
        ["round 99: encode the", "prompt then map the", "result"],
    ),
    (("round 99: encode the prompt then map the result", 32), ["round 99: encode the prompt then", "map the result"]),
    (
        ("round 99: the kernel wakes the worker at dawn", 4),
        ["round", "99:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 99: the kernel wakes the worker at dawn", 8),
        ["round", "99: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 99: the kernel wakes the worker at dawn", 12),
        ["round 99:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 99: the kernel wakes the worker at dawn", 16), ["round 99: the", "kernel wakes the", "worker at dawn"]),
    (("round 99: the kernel wakes the worker at dawn", 24), ["round 99: the kernel", "wakes the worker at dawn"]),
    (("round 99: the kernel wakes the worker at dawn", 32), ["round 99: the kernel wakes the", "worker at dawn"]),
    (
        ("round 99: service latency drops after the patch", 4),
        ["round", "99:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 99: service latency drops after the patch", 8),
        ["round", "99:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 99: service latency drops after the patch", 12),
        ["round 99:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 99: service latency drops after the patch", 16),
        ["round 99:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 99: service latency drops after the patch", 24),
        ["round 99: service", "latency drops after the", "patch"],
    ),
    (("round 99: service latency drops after the patch", 32), ["round 99: service latency drops", "after the patch"]),
    (
        ("round 99: the library caches every vector it sees", 4),
        ["round", "99:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 99: the library caches every vector it sees", 8),
        ["round", "99: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 99: the library caches every vector it sees", 12),
        ["round 99:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 99: the library caches every vector it sees", 16),
        ["round 99: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 99: the library caches every vector it sees", 24),
        ["round 99: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 99: the library caches every vector it sees", 32),
        ["round 99: the library caches", "every vector it sees"],
    ),
    (
        ("round 99: agents argue then the debate resolves", 4),
        ["round", "99:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 99: agents argue then the debate resolves", 8),
        ["round", "99:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 99: agents argue then the debate resolves", 12),
        ["round 99:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 99: agents argue then the debate resolves", 16),
        ["round 99: agents", "argue then the", "debate resolves"],
    ),
    (("round 99: agents argue then the debate resolves", 24), ["round 99: agents argue", "then the debate resolves"]),
    (("round 99: agents argue then the debate resolves", 32), ["round 99: agents argue then the", "debate resolves"]),
    (
        ("round 99: the filter keeps only strong matches", 4),
        ["round", "99:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 99: the filter keeps only strong matches", 8),
        ["round", "99: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 99: the filter keeps only strong matches", 12),
        ["round 99:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 99: the filter keeps only strong matches", 16),
        ["round 99: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 99: the filter keeps only strong matches", 24), ["round 99: the filter", "keeps only strong", "matches"]),
    (("round 99: the filter keeps only strong matches", 32), ["round 99: the filter keeps only", "strong matches"]),
    (
        ("round 99: the model answers with a short reply", 4),
        ["round", "99:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 99: the model answers with a short reply", 8),
        ["round", "99: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 99: the model answers with a short reply", 12),
        ["round 99:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 99: the model answers with a short reply", 16),
        ["round 99: the", "model answers", "with a short", "reply"],
    ),
    (("round 99: the model answers with a short reply", 24), ["round 99: the model", "answers with a short", "reply"]),
    (("round 99: the model answers with a short reply", 32), ["round 99: the model answers with", "a short reply"]),
    (
        ("round 99: the recorder stores the reasoning trace", 4),
        ["round", "99:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 99: the recorder stores the reasoning trace", 8),
        ["round", "99: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 99: the recorder stores the reasoning trace", 12),
        ["round 99:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 99: the recorder stores the reasoning trace", 16),
        ["round 99: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 99: the recorder stores the reasoning trace", 24),
        ["round 99: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 99: the recorder stores the reasoning trace", 32),
        ["round 99: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 99: the angel watches the processor run", 4),
        ["round", "99:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 99: the angel watches the processor run", 8),
        ["round", "99: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 99: the angel watches the processor run", 12),
        ["round 99:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 99: the angel watches the processor run", 16), ["round 99: the", "angel watches", "the processor", "run"]),
    (("round 99: the angel watches the processor run", 24), ["round 99: the angel", "watches the processor", "run"]),
    (("round 99: the angel watches the processor run", 32), ["round 99: the angel watches the", "processor run"]),
    (
        ("round 99: angle of the vector decides the match", 4),
        ["round", "99:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 99: angle of the vector decides the match", 8),
        ["round", "99:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 99: angle of the vector decides the match", 12),
        ["round 99:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 99: angle of the vector decides the match", 16),
        ["round 99: angle", "of the vector", "decides the", "match"],
    ),
    (("round 99: angle of the vector decides the match", 24), ["round 99: angle of the", "vector decides the match"]),
    (("round 99: angle of the vector decides the match", 32), ["round 99: angle of the vector", "decides the match"]),
    (
        ("round 99: the candle burns twice as long at night", 4),
        ["round", "99:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 99: the candle burns twice as long at night", 8),
        ["round", "99: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 99: the candle burns twice as long at night", 12),
        ["round 99:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 99: the candle burns twice as long at night", 16),
        ["round 99: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 99: the candle burns twice as long at night", 24),
        ["round 99: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 99: the candle burns twice as long at night", 32),
        ["round 99: the candle burns twice", "as long at night"],
    ),
    (
        ("round 99: a mirror of the universe in one line", 4),
        ["round", "99:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 99: a mirror of the universe in one line", 8),
        ["round", "99: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 99: a mirror of the universe in one line", 12),
        ["round 99: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 99: a mirror of the universe in one line", 16),
        ["round 99: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 99: a mirror of the universe in one line", 24), ["round 99: a mirror of", "the universe in one line"]),
    (("round 99: a mirror of the universe in one line", 32), ["round 99: a mirror of the", "universe in one line"]),
    (
        ("round 99: the queue drains before the storm", 4),
        ["round", "99:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 99: the queue drains before the storm", 8),
        ["round", "99: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 99: the queue drains before the storm", 12), ["round 99:", "the queue", "drains", "before the", "storm"]),
    (("round 99: the queue drains before the storm", 16), ["round 99: the", "queue drains", "before the storm"]),
    (("round 99: the queue drains before the storm", 24), ["round 99: the queue", "drains before the storm"]),
    (("round 99: the queue drains before the storm", 32), ["round 99: the queue drains", "before the storm"]),
    (
        ("kitten99 sitting99 agent99 angle99 universe99 memory99", 6),
        ["kitten99", "sitting99", "agent99", "angle99", "universe99", "memory99"],
    ),
    (
        ("kitten99 sitting99 agent99 angle99 universe99 memory99", 10),
        ["kitten99", "sitting99", "agent99", "angle99", "universe99", "memory99"],
    ),
    (
        ("kitten99 sitting99 agent99 angle99 universe99 memory99", 18),
        ["kitten99 sitting99", "agent99 angle99", "universe99", "memory99"],
    ),
    (
        ("kitten99 sitting99 agent99 angle99 universe99 memory99", 28),
        ["kitten99 sitting99 agent99", "angle99 universe99 memory99"],
    ),
    (
        ("sitting99 agent99 angle99 universe99 memory99 stream99", 6),
        ["sitting99", "agent99", "angle99", "universe99", "memory99", "stream99"],
    ),
    (
        ("sitting99 agent99 angle99 universe99 memory99 stream99", 10),
        ["sitting99", "agent99", "angle99", "universe99", "memory99", "stream99"],
    ),
    (
        ("sitting99 agent99 angle99 universe99 memory99 stream99", 18),
        ["sitting99 agent99", "angle99 universe99", "memory99 stream99"],
    ),
    (
        ("sitting99 agent99 angle99 universe99 memory99 stream99", 28),
        ["sitting99 agent99 angle99", "universe99 memory99 stream99"],
    ),
    (
        ("agent99 angle99 universe99 memory99 stream99 context99", 6),
        ["agent99", "angle99", "universe99", "memory99", "stream99", "context99"],
    ),
    (
        ("agent99 angle99 universe99 memory99 stream99 context99", 10),
        ["agent99", "angle99", "universe99", "memory99", "stream99", "context99"],
    ),
    (
        ("agent99 angle99 universe99 memory99 stream99 context99", 18),
        ["agent99 angle99", "universe99", "memory99 stream99", "context99"],
    ),
    (
        ("agent99 angle99 universe99 memory99 stream99 context99", 28),
        ["agent99 angle99 universe99", "memory99 stream99 context99"],
    ),
    (
        ("angle99 universe99 memory99 stream99 context99 knowledge99", 6),
        ["angle99", "universe99", "memory99", "stream99", "context99", "knowledge99"],
    ),
    (
        ("angle99 universe99 memory99 stream99 context99 knowledge99", 10),
        ["angle99", "universe99", "memory99", "stream99", "context99", "knowledge99"],
    ),
    (
        ("angle99 universe99 memory99 stream99 context99 knowledge99", 18),
        ["angle99 universe99", "memory99 stream99", "context99", "knowledge99"],
    ),
    (
        ("angle99 universe99 memory99 stream99 context99 knowledge99", 28),
        ["angle99 universe99 memory99", "stream99 context99", "knowledge99"],
    ),
    (
        ("universe99 memory99 stream99 context99 knowledge99 vector99", 6),
        ["universe99", "memory99", "stream99", "context99", "knowledge99", "vector99"],
    ),
    (
        ("universe99 memory99 stream99 context99 knowledge99 vector99", 10),
        ["universe99", "memory99", "stream99", "context99", "knowledge99", "vector99"],
    ),
    (
        ("universe99 memory99 stream99 context99 knowledge99 vector99", 18),
        ["universe99", "memory99 stream99", "context99", "knowledge99", "vector99"],
    ),
    (
        ("universe99 memory99 stream99 context99 knowledge99 vector99", 28),
        ["universe99 memory99 stream99", "context99 knowledge99", "vector99"],
    ),
    (
        ("memory99 stream99 context99 knowledge99 vector99 processor99", 6),
        ["memory99", "stream99", "context99", "knowledge99", "vector99", "processor99"],
    ),
    (
        ("memory99 stream99 context99 knowledge99 vector99 processor99", 10),
        ["memory99", "stream99", "context99", "knowledge99", "vector99", "processor99"],
    ),
    (
        ("memory99 stream99 context99 knowledge99 vector99 processor99", 18),
        ["memory99 stream99", "context99", "knowledge99", "vector99", "processor99"],
    ),
    (
        ("memory99 stream99 context99 knowledge99 vector99 processor99", 28),
        ["memory99 stream99 context99", "knowledge99 vector99", "processor99"],
    ),
    (
        ("stream99 context99 knowledge99 vector99 processor99 reasoning99", 6),
        ["stream99", "context99", "knowledge99", "vector99", "processor99", "reasoning99"],
    ),
    (
        ("stream99 context99 knowledge99 vector99 processor99 reasoning99", 10),
        ["stream99", "context99", "knowledge99", "vector99", "processor99", "reasoning99"],
    ),
    (
        ("stream99 context99 knowledge99 vector99 processor99 reasoning99", 18),
        ["stream99 context99", "knowledge99", "vector99", "processor99", "reasoning99"],
    ),
    (
        ("stream99 context99 knowledge99 vector99 processor99 reasoning99", 28),
        ["stream99 context99", "knowledge99 vector99", "processor99 reasoning99"],
    ),
    (
        ("context99 knowledge99 vector99 processor99 reasoning99 machine99", 6),
        ["context99", "knowledge99", "vector99", "processor99", "reasoning99", "machine99"],
    ),
    (
        ("context99 knowledge99 vector99 processor99 reasoning99 machine99", 10),
        ["context99", "knowledge99", "vector99", "processor99", "reasoning99", "machine99"],
    ),
    (
        ("context99 knowledge99 vector99 processor99 reasoning99 machine99", 18),
        ["context99", "knowledge99", "vector99", "processor99", "reasoning99", "machine99"],
    ),
    (
        ("context99 knowledge99 vector99 processor99 reasoning99 machine99", 28),
        ["context99 knowledge99", "vector99 processor99", "reasoning99 machine99"],
    ),
    (
        ("knowledge99 vector99 processor99 reasoning99 machine99 learning99", 6),
        ["knowledge99", "vector99", "processor99", "reasoning99", "machine99", "learning99"],
    ),
    (
        ("knowledge99 vector99 processor99 reasoning99 machine99 learning99", 10),
        ["knowledge99", "vector99", "processor99", "reasoning99", "machine99", "learning99"],
    ),
    (
        ("knowledge99 vector99 processor99 reasoning99 machine99 learning99", 18),
        ["knowledge99", "vector99", "processor99", "reasoning99", "machine99", "learning99"],
    ),
    (
        ("knowledge99 vector99 processor99 reasoning99 machine99 learning99", 28),
        ["knowledge99 vector99", "processor99 reasoning99", "machine99 learning99"],
    ),
    (
        ("vector99 processor99 reasoning99 machine99 learning99 model99", 6),
        ["vector99", "processor99", "reasoning99", "machine99", "learning99", "model99"],
    ),
    (
        ("vector99 processor99 reasoning99 machine99 learning99 model99", 10),
        ["vector99", "processor99", "reasoning99", "machine99", "learning99", "model99"],
    ),
    (
        ("vector99 processor99 reasoning99 machine99 learning99 model99", 18),
        ["vector99", "processor99", "reasoning99", "machine99", "learning99 model99"],
    ),
    (
        ("vector99 processor99 reasoning99 machine99 learning99 model99", 28),
        ["vector99 processor99", "reasoning99 machine99", "learning99 model99"],
    ),
    (
        ("processor99 reasoning99 machine99 learning99 model99 token99", 6),
        ["processor99", "reasoning99", "machine99", "learning99", "model99", "token99"],
    ),
    (
        ("processor99 reasoning99 machine99 learning99 model99 token99", 10),
        ["processor99", "reasoning99", "machine99", "learning99", "model99", "token99"],
    ),
    (
        ("processor99 reasoning99 machine99 learning99 model99 token99", 18),
        ["processor99", "reasoning99", "machine99", "learning99 model99", "token99"],
    ),
    (
        ("processor99 reasoning99 machine99 learning99 model99 token99", 28),
        ["processor99 reasoning99", "machine99 learning99 model99", "token99"],
    ),
    (
        ("reasoning99 machine99 learning99 model99 token99 prompt99", 6),
        ["reasoning99", "machine99", "learning99", "model99", "token99", "prompt99"],
    ),
    (
        ("reasoning99 machine99 learning99 model99 token99 prompt99", 10),
        ["reasoning99", "machine99", "learning99", "model99", "token99", "prompt99"],
    ),
    (
        ("reasoning99 machine99 learning99 model99 token99 prompt99", 18),
        ["reasoning99", "machine99", "learning99 model99", "token99 prompt99"],
    ),
    (
        ("reasoning99 machine99 learning99 model99 token99 prompt99", 28),
        ["reasoning99 machine99", "learning99 model99 token99", "prompt99"],
    ),
    (
        ("machine99 learning99 model99 token99 prompt99 session99", 6),
        ["machine99", "learning99", "model99", "token99", "prompt99", "session99"],
    ),
    (
        ("machine99 learning99 model99 token99 prompt99 session99", 10),
        ["machine99", "learning99", "model99", "token99", "prompt99", "session99"],
    ),
    (
        ("machine99 learning99 model99 token99 prompt99 session99", 18),
        ["machine99", "learning99 model99", "token99 prompt99", "session99"],
    ),
    (
        ("machine99 learning99 model99 token99 prompt99 session99", 28),
        ["machine99 learning99 model99", "token99 prompt99 session99"],
    ),
    (
        ("learning99 model99 token99 prompt99 session99 library99", 6),
        ["learning99", "model99", "token99", "prompt99", "session99", "library99"],
    ),
    (
        ("learning99 model99 token99 prompt99 session99 library99", 10),
        ["learning99", "model99", "token99", "prompt99", "session99", "library99"],
    ),
    (
        ("learning99 model99 token99 prompt99 session99 library99", 18),
        ["learning99 model99", "token99 prompt99", "session99", "library99"],
    ),
    (
        ("learning99 model99 token99 prompt99 session99 library99", 28),
        ["learning99 model99 token99", "prompt99 session99 library99"],
    ),
    (
        ("model99 token99 prompt99 session99 library99 service99", 6),
        ["model99", "token99", "prompt99", "session99", "library99", "service99"],
    ),
    (
        ("model99 token99 prompt99 session99 library99 service99", 10),
        ["model99", "token99", "prompt99", "session99", "library99", "service99"],
    ),
    (
        ("model99 token99 prompt99 session99 library99 service99", 18),
        ["model99 token99", "prompt99 session99", "library99", "service99"],
    ),
    (
        ("model99 token99 prompt99 session99 library99 service99", 28),
        ["model99 token99 prompt99", "session99 library99", "service99"],
    ),
    (
        ("token99 prompt99 session99 library99 service99 gateway99", 6),
        ["token99", "prompt99", "session99", "library99", "service99", "gateway99"],
    ),
    (
        ("token99 prompt99 session99 library99 service99 gateway99", 10),
        ["token99", "prompt99", "session99", "library99", "service99", "gateway99"],
    ),
    (
        ("token99 prompt99 session99 library99 service99 gateway99", 18),
        ["token99 prompt99", "session99", "library99", "service99", "gateway99"],
    ),
    (
        ("token99 prompt99 session99 library99 service99 gateway99", 28),
        ["token99 prompt99 session99", "library99 service99", "gateway99"],
    ),
    (
        ("prompt99 session99 library99 service99 gateway99 storage99", 6),
        ["prompt99", "session99", "library99", "service99", "gateway99", "storage99"],
    ),
    (
        ("prompt99 session99 library99 service99 gateway99 storage99", 10),
        ["prompt99", "session99", "library99", "service99", "gateway99", "storage99"],
    ),
    (
        ("prompt99 session99 library99 service99 gateway99 storage99", 18),
        ["prompt99 session99", "library99", "service99", "gateway99", "storage99"],
    ),
    (
        ("prompt99 session99 library99 service99 gateway99 storage99", 28),
        ["prompt99 session99 library99", "service99 gateway99", "storage99"],
    ),
    (
        ("session99 library99 service99 gateway99 storage99 network99", 6),
        ["session99", "library99", "service99", "gateway99", "storage99", "network99"],
    ),
    (
        ("session99 library99 service99 gateway99 storage99 network99", 10),
        ["session99", "library99", "service99", "gateway99", "storage99", "network99"],
    ),
    (
        ("session99 library99 service99 gateway99 storage99 network99", 18),
        ["session99", "library99", "service99", "gateway99", "storage99", "network99"],
    ),
    (
        ("session99 library99 service99 gateway99 storage99 network99", 28),
        ["session99 library99", "service99 gateway99", "storage99 network99"],
    ),
    (
        ("library99 service99 gateway99 storage99 network99 latency99", 6),
        ["library99", "service99", "gateway99", "storage99", "network99", "latency99"],
    ),
    (
        ("library99 service99 gateway99 storage99 network99 latency99", 10),
        ["library99", "service99", "gateway99", "storage99", "network99", "latency99"],
    ),
    (
        ("library99 service99 gateway99 storage99 network99 latency99", 18),
        ["library99", "service99", "gateway99", "storage99", "network99", "latency99"],
    ),
    (
        ("library99 service99 gateway99 storage99 network99 latency99", 28),
        ["library99 service99", "gateway99 storage99", "network99 latency99"],
    ),
    (
        ("service99 gateway99 storage99 network99 latency99 buffer99", 6),
        ["service99", "gateway99", "storage99", "network99", "latency99", "buffer99"],
    ),
    (
        ("service99 gateway99 storage99 network99 latency99 buffer99", 10),
        ["service99", "gateway99", "storage99", "network99", "latency99", "buffer99"],
    ),
    (
        ("service99 gateway99 storage99 network99 latency99 buffer99", 18),
        ["service99", "gateway99", "storage99", "network99", "latency99 buffer99"],
    ),
    (
        ("service99 gateway99 storage99 network99 latency99 buffer99", 28),
        ["service99 gateway99", "storage99 network99", "latency99 buffer99"],
    ),
    (
        ("gateway99 storage99 network99 latency99 buffer99 queue99", 6),
        ["gateway99", "storage99", "network99", "latency99", "buffer99", "queue99"],
    ),
    (
        ("gateway99 storage99 network99 latency99 buffer99 queue99", 10),
        ["gateway99", "storage99", "network99", "latency99", "buffer99", "queue99"],
    ),
    (
        ("gateway99 storage99 network99 latency99 buffer99 queue99", 18),
        ["gateway99", "storage99", "network99", "latency99 buffer99", "queue99"],
    ),
    (
        ("gateway99 storage99 network99 latency99 buffer99 queue99", 28),
        ["gateway99 storage99", "network99 latency99 buffer99", "queue99"],
    ),
    (
        ("storage99 network99 latency99 buffer99 queue99 worker99", 6),
        ["storage99", "network99", "latency99", "buffer99", "queue99", "worker99"],
    ),
    (
        ("storage99 network99 latency99 buffer99 queue99 worker99", 10),
        ["storage99", "network99", "latency99", "buffer99", "queue99", "worker99"],
    ),
    (
        ("storage99 network99 latency99 buffer99 queue99 worker99", 18),
        ["storage99", "network99", "latency99 buffer99", "queue99 worker99"],
    ),
    (
        ("storage99 network99 latency99 buffer99 queue99 worker99", 28),
        ["storage99 network99", "latency99 buffer99 queue99", "worker99"],
    ),
    (
        ("network99 latency99 buffer99 queue99 worker99 kernel99", 6),
        ["network99", "latency99", "buffer99", "queue99", "worker99", "kernel99"],
    ),
    (
        ("network99 latency99 buffer99 queue99 worker99 kernel99", 10),
        ["network99", "latency99", "buffer99", "queue99", "worker99", "kernel99"],
    ),
    (
        ("network99 latency99 buffer99 queue99 worker99 kernel99", 18),
        ["network99", "latency99 buffer99", "queue99 worker99", "kernel99"],
    ),
    (
        ("network99 latency99 buffer99 queue99 worker99 kernel99", 28),
        ["network99 latency99 buffer99", "queue99 worker99 kernel99"],
    ),
    (
        ("latency99 buffer99 queue99 worker99 kernel99 signal99", 6),
        ["latency99", "buffer99", "queue99", "worker99", "kernel99", "signal99"],
    ),
    (
        ("latency99 buffer99 queue99 worker99 kernel99 signal99", 10),
        ["latency99", "buffer99", "queue99", "worker99", "kernel99", "signal99"],
    ),
    (
        ("latency99 buffer99 queue99 worker99 kernel99 signal99", 18),
        ["latency99 buffer99", "queue99 worker99", "kernel99 signal99"],
    ),
    (
        ("latency99 buffer99 queue99 worker99 kernel99 signal99", 28),
        ["latency99 buffer99 queue99", "worker99 kernel99 signal99"],
    ),
    (
        ("buffer99 queue99 worker99 kernel99 signal99 packet99", 6),
        ["buffer99", "queue99", "worker99", "kernel99", "signal99", "packet99"],
    ),
    (
        ("buffer99 queue99 worker99 kernel99 signal99 packet99", 10),
        ["buffer99", "queue99", "worker99", "kernel99", "signal99", "packet99"],
    ),
    (
        ("buffer99 queue99 worker99 kernel99 signal99 packet99", 18),
        ["buffer99 queue99", "worker99 kernel99", "signal99 packet99"],
    ),
    (
        ("buffer99 queue99 worker99 kernel99 signal99 packet99", 28),
        ["buffer99 queue99 worker99", "kernel99 signal99 packet99"],
    ),
    (
        ("queue99 worker99 kernel99 signal99 packet99 router99", 6),
        ["queue99", "worker99", "kernel99", "signal99", "packet99", "router99"],
    ),
    (
        ("queue99 worker99 kernel99 signal99 packet99 router99", 10),
        ["queue99", "worker99", "kernel99", "signal99", "packet99", "router99"],
    ),
    (
        ("queue99 worker99 kernel99 signal99 packet99 router99", 18),
        ["queue99 worker99", "kernel99 signal99", "packet99 router99"],
    ),
    (
        ("queue99 worker99 kernel99 signal99 packet99 router99", 28),
        ["queue99 worker99 kernel99", "signal99 packet99 router99"],
    ),
    (
        ("worker99 kernel99 signal99 packet99 router99 cluster99", 6),
        ["worker99", "kernel99", "signal99", "packet99", "router99", "cluster99"],
    ),
    (
        ("worker99 kernel99 signal99 packet99 router99 cluster99", 10),
        ["worker99", "kernel99", "signal99", "packet99", "router99", "cluster99"],
    ),
    (
        ("worker99 kernel99 signal99 packet99 router99 cluster99", 18),
        ["worker99 kernel99", "signal99 packet99", "router99 cluster99"],
    ),
    (
        ("worker99 kernel99 signal99 packet99 router99 cluster99", 28),
        ["worker99 kernel99 signal99", "packet99 router99 cluster99"],
    ),
    (
        ("kernel99 signal99 packet99 router99 cluster99 mirror99", 6),
        ["kernel99", "signal99", "packet99", "router99", "cluster99", "mirror99"],
    ),
    (
        ("kernel99 signal99 packet99 router99 cluster99 mirror99", 10),
        ["kernel99", "signal99", "packet99", "router99", "cluster99", "mirror99"],
    ),
    (
        ("kernel99 signal99 packet99 router99 cluster99 mirror99", 18),
        ["kernel99 signal99", "packet99 router99", "cluster99 mirror99"],
    ),
    (
        ("kernel99 signal99 packet99 router99 cluster99 mirror99", 28),
        ["kernel99 signal99 packet99", "router99 cluster99 mirror99"],
    ),
    (
        ("signal99 packet99 router99 cluster99 mirror99 filter99", 6),
        ["signal99", "packet99", "router99", "cluster99", "mirror99", "filter99"],
    ),
    (
        ("signal99 packet99 router99 cluster99 mirror99 filter99", 10),
        ["signal99", "packet99", "router99", "cluster99", "mirror99", "filter99"],
    ),
    (
        ("signal99 packet99 router99 cluster99 mirror99 filter99", 18),
        ["signal99 packet99", "router99 cluster99", "mirror99 filter99"],
    ),
    (
        ("signal99 packet99 router99 cluster99 mirror99 filter99", 28),
        ["signal99 packet99 router99", "cluster99 mirror99 filter99"],
    ),
    (
        ("packet99 router99 cluster99 mirror99 filter99 ranking99", 6),
        ["packet99", "router99", "cluster99", "mirror99", "filter99", "ranking99"],
    ),
    (
        ("packet99 router99 cluster99 mirror99 filter99 ranking99", 10),
        ["packet99", "router99", "cluster99", "mirror99", "filter99", "ranking99"],
    ),
    (
        ("packet99 router99 cluster99 mirror99 filter99 ranking99", 18),
        ["packet99 router99", "cluster99 mirror99", "filter99 ranking99"],
    ),
    (
        ("packet99 router99 cluster99 mirror99 filter99 ranking99", 28),
        ["packet99 router99 cluster99", "mirror99 filter99 ranking99"],
    ),
    (
        ("router99 cluster99 mirror99 filter99 ranking99 encoding99", 6),
        ["router99", "cluster99", "mirror99", "filter99", "ranking99", "encoding99"],
    ),
    (
        ("router99 cluster99 mirror99 filter99 ranking99 encoding99", 10),
        ["router99", "cluster99", "mirror99", "filter99", "ranking99", "encoding99"],
    ),
    (
        ("router99 cluster99 mirror99 filter99 ranking99 encoding99", 18),
        ["router99 cluster99", "mirror99 filter99", "ranking99", "encoding99"],
    ),
    (
        ("router99 cluster99 mirror99 filter99 ranking99 encoding99", 28),
        ["router99 cluster99 mirror99", "filter99 ranking99", "encoding99"],
    ),
    (
        ("cluster99 mirror99 filter99 ranking99 encoding99 mapping99", 6),
        ["cluster99", "mirror99", "filter99", "ranking99", "encoding99", "mapping99"],
    ),
    (
        ("cluster99 mirror99 filter99 ranking99 encoding99 mapping99", 10),
        ["cluster99", "mirror99", "filter99", "ranking99", "encoding99", "mapping99"],
    ),
    (
        ("cluster99 mirror99 filter99 ranking99 encoding99 mapping99", 18),
        ["cluster99 mirror99", "filter99 ranking99", "encoding99", "mapping99"],
    ),
    (
        ("cluster99 mirror99 filter99 ranking99 encoding99 mapping99", 28),
        ["cluster99 mirror99 filter99", "ranking99 encoding99", "mapping99"],
    ),
    (
        ("mirror99 filter99 ranking99 encoding99 mapping99 record99", 6),
        ["mirror99", "filter99", "ranking99", "encoding99", "mapping99", "record99"],
    ),
    (
        ("mirror99 filter99 ranking99 encoding99 mapping99 record99", 10),
        ["mirror99", "filter99", "ranking99", "encoding99", "mapping99", "record99"],
    ),
    (
        ("mirror99 filter99 ranking99 encoding99 mapping99 record99", 18),
        ["mirror99 filter99", "ranking99", "encoding99", "mapping99 record99"],
    ),
    (
        ("mirror99 filter99 ranking99 encoding99 mapping99 record99", 28),
        ["mirror99 filter99 ranking99", "encoding99 mapping99", "record99"],
    ),
    (
        ("filter99 ranking99 encoding99 mapping99 record99 candle99", 6),
        ["filter99", "ranking99", "encoding99", "mapping99", "record99", "candle99"],
    ),
    (
        ("filter99 ranking99 encoding99 mapping99 record99 candle99", 10),
        ["filter99", "ranking99", "encoding99", "mapping99", "record99", "candle99"],
    ),
    (
        ("filter99 ranking99 encoding99 mapping99 record99 candle99", 18),
        ["filter99 ranking99", "encoding99", "mapping99 record99", "candle99"],
    ),
    (
        ("filter99 ranking99 encoding99 mapping99 record99 candle99", 28),
        ["filter99 ranking99", "encoding99 mapping99", "record99 candle99"],
    ),
    (
        ("ranking99 encoding99 mapping99 record99 candle99 thread99", 6),
        ["ranking99", "encoding99", "mapping99", "record99", "candle99", "thread99"],
    ),
    (
        ("ranking99 encoding99 mapping99 record99 candle99 thread99", 10),
        ["ranking99", "encoding99", "mapping99", "record99", "candle99", "thread99"],
    ),
    (
        ("ranking99 encoding99 mapping99 record99 candle99 thread99", 18),
        ["ranking99", "encoding99", "mapping99 record99", "candle99 thread99"],
    ),
    (
        ("ranking99 encoding99 mapping99 record99 candle99 thread99", 28),
        ["ranking99 encoding99", "mapping99 record99 candle99", "thread99"],
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
