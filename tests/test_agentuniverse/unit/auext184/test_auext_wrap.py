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
        ("round 184: the quick brown fox jumps over the lazy dog", 4),
        ["round", "184:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", 8),
        ["round", "184: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", 12),
        ["round 184:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", 16),
        ["round 184: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", 24),
        ["round 184: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 184: the quick brown fox jumps over the lazy dog", 32),
        ["round 184: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", 4),
        ["round", "184:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", 8),
        ["round", "184:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", 12),
        ["round 184:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", 16),
        ["round 184:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", 24),
        ["round 184: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 184: agentuniverse is a framework for multi agents", 32),
        ["round 184: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", 4),
        ["round", "184:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", 8),
        ["round", "184:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", 12),
        ["round 184:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", 16),
        ["round 184:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", 24),
        ["round 184: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 184: knowledge stored as vectors enables retrieval", 32),
        ["round 184: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 184: the processor reads the record then stops", 4),
        ["round", "184:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 184: the processor reads the record then stops", 8),
        ["round", "184: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 184: the processor reads the record then stops", 12),
        ["round 184:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 184: the processor reads the record then stops", 16),
        ["round 184: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 184: the processor reads the record then stops", 24),
        ["round 184: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 184: the processor reads the record then stops", 32),
        ["round 184: the processor reads", "the record then stops"],
    ),
    (
        ("round 184: a worker pulls the next task from the queue", 4),
        ["round", "184:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 184: a worker pulls the next task from the queue", 8),
        ["round", "184: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 184: a worker pulls the next task from the queue", 12),
        ["round 184: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 184: a worker pulls the next task from the queue", 16),
        ["round 184: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 184: a worker pulls the next task from the queue", 24),
        ["round 184: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 184: a worker pulls the next task from the queue", 32),
        ["round 184: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 184: signals travel through the network layer", 4),
        ["round", "184:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 184: signals travel through the network layer", 8),
        ["round", "184:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 184: signals travel through the network layer", 12),
        ["round 184:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 184: signals travel through the network layer", 16),
        ["round 184:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 184: signals travel through the network layer", 24),
        ["round 184: signals", "travel through the", "network layer"],
    ),
    (
        ("round 184: signals travel through the network layer", 32),
        ["round 184: signals travel", "through the network layer"],
    ),
    (
        ("round 184: the gateway routes each request by policy", 4),
        ["round", "184:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 184: the gateway routes each request by policy", 8),
        ["round", "184: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 184: the gateway routes each request by policy", 12),
        ["round 184:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 184: the gateway routes each request by policy", 16),
        ["round 184: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 184: the gateway routes each request by policy", 24),
        ["round 184: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 184: the gateway routes each request by policy", 32),
        ["round 184: the gateway routes", "each request by policy"],
    ),
    (
        ("round 184: memory grows until the buffer is full", 4),
        ["round", "184:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 184: memory grows until the buffer is full", 8),
        ["round", "184:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 184: memory grows until the buffer is full", 12),
        ["round 184:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 184: memory grows until the buffer is full", 16),
        ["round 184:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 184: memory grows until the buffer is full", 24), ["round 184: memory grows", "until the buffer is full"]),
    (("round 184: memory grows until the buffer is full", 32), ["round 184: memory grows until", "the buffer is full"]),
    (
        ("round 184: the cluster mirrors every packet twice", 4),
        ["round", "184:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 184: the cluster mirrors every packet twice", 8),
        ["round", "184: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 184: the cluster mirrors every packet twice", 12),
        ["round 184:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 184: the cluster mirrors every packet twice", 16),
        ["round 184: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 184: the cluster mirrors every packet twice", 24),
        ["round 184: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 184: the cluster mirrors every packet twice", 32),
        ["round 184: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", 4),
        ["round", "184:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", 8),
        ["round", "184:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", 12),
        ["round 184:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", 16),
        ["round 184:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", 24),
        ["round 184: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 184: ranking uses tokens learned from the corpus", 32),
        ["round 184: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 184: a long session ends when the candle dies", 4),
        ["round", "184:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 184: a long session ends when the candle dies", 8),
        ["round", "184: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 184: a long session ends when the candle dies", 12),
        ["round 184: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 184: a long session ends when the candle dies", 16),
        ["round 184: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 184: a long session ends when the candle dies", 24),
        ["round 184: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 184: a long session ends when the candle dies", 32),
        ["round 184: a long session ends", "when the candle dies"],
    ),
    (
        ("round 184: encode the prompt then map the result", 4),
        ["round", "184:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 184: encode the prompt then map the result", 8),
        ["round", "184:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 184: encode the prompt then map the result", 12),
        ["round 184:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 184: encode the prompt then map the result", 16),
        ["round 184:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 184: encode the prompt then map the result", 24),
        ["round 184: encode the", "prompt then map the", "result"],
    ),
    (("round 184: encode the prompt then map the result", 32), ["round 184: encode the prompt", "then map the result"]),
    (
        ("round 184: the kernel wakes the worker at dawn", 4),
        ["round", "184:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 184: the kernel wakes the worker at dawn", 8),
        ["round", "184: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 184: the kernel wakes the worker at dawn", 12),
        ["round 184:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 184: the kernel wakes the worker at dawn", 16), ["round 184: the", "kernel wakes the", "worker at dawn"]),
    (("round 184: the kernel wakes the worker at dawn", 24), ["round 184: the kernel", "wakes the worker at dawn"]),
    (("round 184: the kernel wakes the worker at dawn", 32), ["round 184: the kernel wakes the", "worker at dawn"]),
    (
        ("round 184: service latency drops after the patch", 4),
        ["round", "184:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 184: service latency drops after the patch", 8),
        ["round", "184:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 184: service latency drops after the patch", 12),
        ["round 184:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 184: service latency drops after the patch", 16),
        ["round 184:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 184: service latency drops after the patch", 24),
        ["round 184: service", "latency drops after the", "patch"],
    ),
    (("round 184: service latency drops after the patch", 32), ["round 184: service latency drops", "after the patch"]),
    (
        ("round 184: the library caches every vector it sees", 4),
        ["round", "184:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 184: the library caches every vector it sees", 8),
        ["round", "184: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 184: the library caches every vector it sees", 12),
        ["round 184:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 184: the library caches every vector it sees", 16),
        ["round 184: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 184: the library caches every vector it sees", 24),
        ["round 184: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 184: the library caches every vector it sees", 32),
        ["round 184: the library caches", "every vector it sees"],
    ),
    (
        ("round 184: agents argue then the debate resolves", 4),
        ["round", "184:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 184: agents argue then the debate resolves", 8),
        ["round", "184:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 184: agents argue then the debate resolves", 12),
        ["round 184:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 184: agents argue then the debate resolves", 16),
        ["round 184:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 184: agents argue then the debate resolves", 24), ["round 184: agents argue", "then the debate resolves"]),
    (("round 184: agents argue then the debate resolves", 32), ["round 184: agents argue then the", "debate resolves"]),
    (
        ("round 184: the filter keeps only strong matches", 4),
        ["round", "184:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 184: the filter keeps only strong matches", 8),
        ["round", "184: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 184: the filter keeps only strong matches", 12),
        ["round 184:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 184: the filter keeps only strong matches", 16),
        ["round 184: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 184: the filter keeps only strong matches", 24),
        ["round 184: the filter", "keeps only strong", "matches"],
    ),
    (("round 184: the filter keeps only strong matches", 32), ["round 184: the filter keeps only", "strong matches"]),
    (
        ("round 184: the model answers with a short reply", 4),
        ["round", "184:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 184: the model answers with a short reply", 8),
        ["round", "184: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 184: the model answers with a short reply", 12),
        ["round 184:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 184: the model answers with a short reply", 16),
        ["round 184: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 184: the model answers with a short reply", 24),
        ["round 184: the model", "answers with a short", "reply"],
    ),
    (("round 184: the model answers with a short reply", 32), ["round 184: the model answers", "with a short reply"]),
    (
        ("round 184: the recorder stores the reasoning trace", 4),
        ["round", "184:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 184: the recorder stores the reasoning trace", 8),
        ["round", "184: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 184: the recorder stores the reasoning trace", 12),
        ["round 184:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 184: the recorder stores the reasoning trace", 16),
        ["round 184: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 184: the recorder stores the reasoning trace", 24),
        ["round 184: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 184: the recorder stores the reasoning trace", 32),
        ["round 184: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 184: the angel watches the processor run", 4),
        ["round", "184:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 184: the angel watches the processor run", 8),
        ["round", "184: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 184: the angel watches the processor run", 12),
        ["round 184:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 184: the angel watches the processor run", 16),
        ["round 184: the", "angel watches", "the processor", "run"],
    ),
    (("round 184: the angel watches the processor run", 24), ["round 184: the angel", "watches the processor", "run"]),
    (("round 184: the angel watches the processor run", 32), ["round 184: the angel watches the", "processor run"]),
    (
        ("round 184: angle of the vector decides the match", 4),
        ["round", "184:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 184: angle of the vector decides the match", 8),
        ["round", "184:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 184: angle of the vector decides the match", 12),
        ["round 184:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 184: angle of the vector decides the match", 16),
        ["round 184: angle", "of the vector", "decides the", "match"],
    ),
    (("round 184: angle of the vector decides the match", 24), ["round 184: angle of the", "vector decides the match"]),
    (("round 184: angle of the vector decides the match", 32), ["round 184: angle of the vector", "decides the match"]),
    (
        ("round 184: the candle burns twice as long at night", 4),
        ["round", "184:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 184: the candle burns twice as long at night", 8),
        ["round", "184: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 184: the candle burns twice as long at night", 12),
        ["round 184:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 184: the candle burns twice as long at night", 16),
        ["round 184: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 184: the candle burns twice as long at night", 24),
        ["round 184: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 184: the candle burns twice as long at night", 32),
        ["round 184: the candle burns", "twice as long at night"],
    ),
    (
        ("round 184: a mirror of the universe in one line", 4),
        ["round", "184:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 184: a mirror of the universe in one line", 8),
        ["round", "184: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 184: a mirror of the universe in one line", 12),
        ["round 184: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 184: a mirror of the universe in one line", 16),
        ["round 184: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 184: a mirror of the universe in one line", 24), ["round 184: a mirror of", "the universe in one line"]),
    (("round 184: a mirror of the universe in one line", 32), ["round 184: a mirror of the", "universe in one line"]),
    (
        ("round 184: the queue drains before the storm", 4),
        ["round", "184:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 184: the queue drains before the storm", 8),
        ["round", "184: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 184: the queue drains before the storm", 12),
        ["round 184:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 184: the queue drains before the storm", 16), ["round 184: the", "queue drains", "before the storm"]),
    (("round 184: the queue drains before the storm", 24), ["round 184: the queue", "drains before the storm"]),
    (("round 184: the queue drains before the storm", 32), ["round 184: the queue drains", "before the storm"]),
    (
        ("kitten184 sitting184 agent184 angle184 universe184 memory184", 6),
        ["kitten184", "sitting184", "agent184", "angle184", "universe184", "memory184"],
    ),
    (
        ("kitten184 sitting184 agent184 angle184 universe184 memory184", 10),
        ["kitten184", "sitting184", "agent184", "angle184", "universe184", "memory184"],
    ),
    (
        ("kitten184 sitting184 agent184 angle184 universe184 memory184", 18),
        ["kitten184", "sitting184", "agent184 angle184", "universe184", "memory184"],
    ),
    (
        ("kitten184 sitting184 agent184 angle184 universe184 memory184", 28),
        ["kitten184 sitting184", "agent184 angle184", "universe184 memory184"],
    ),
    (
        ("sitting184 agent184 angle184 universe184 memory184 stream184", 6),
        ["sitting184", "agent184", "angle184", "universe184", "memory184", "stream184"],
    ),
    (
        ("sitting184 agent184 angle184 universe184 memory184 stream184", 10),
        ["sitting184", "agent184", "angle184", "universe184", "memory184", "stream184"],
    ),
    (
        ("sitting184 agent184 angle184 universe184 memory184 stream184", 18),
        ["sitting184", "agent184 angle184", "universe184", "memory184", "stream184"],
    ),
    (
        ("sitting184 agent184 angle184 universe184 memory184 stream184", 28),
        ["sitting184 agent184 angle184", "universe184 memory184", "stream184"],
    ),
    (
        ("agent184 angle184 universe184 memory184 stream184 context184", 6),
        ["agent184", "angle184", "universe184", "memory184", "stream184", "context184"],
    ),
    (
        ("agent184 angle184 universe184 memory184 stream184 context184", 10),
        ["agent184", "angle184", "universe184", "memory184", "stream184", "context184"],
    ),
    (
        ("agent184 angle184 universe184 memory184 stream184 context184", 18),
        ["agent184 angle184", "universe184", "memory184", "stream184", "context184"],
    ),
    (
        ("agent184 angle184 universe184 memory184 stream184 context184", 28),
        ["agent184 angle184", "universe184 memory184", "stream184 context184"],
    ),
    (
        ("angle184 universe184 memory184 stream184 context184 knowledge184", 6),
        ["angle184", "universe184", "memory184", "stream184", "context184", "knowledge184"],
    ),
    (
        ("angle184 universe184 memory184 stream184 context184 knowledge184", 10),
        ["angle184", "universe184", "memory184", "stream184", "context184", "knowledge184"],
    ),
    (
        ("angle184 universe184 memory184 stream184 context184 knowledge184", 18),
        ["angle184", "universe184", "memory184", "stream184", "context184", "knowledge184"],
    ),
    (
        ("angle184 universe184 memory184 stream184 context184 knowledge184", 28),
        ["angle184 universe184", "memory184 stream184", "context184 knowledge184"],
    ),
    (
        ("universe184 memory184 stream184 context184 knowledge184 vector184", 6),
        ["universe184", "memory184", "stream184", "context184", "knowledge184", "vector184"],
    ),
    (
        ("universe184 memory184 stream184 context184 knowledge184 vector184", 10),
        ["universe184", "memory184", "stream184", "context184", "knowledge184", "vector184"],
    ),
    (
        ("universe184 memory184 stream184 context184 knowledge184 vector184", 18),
        ["universe184", "memory184", "stream184", "context184", "knowledge184", "vector184"],
    ),
    (
        ("universe184 memory184 stream184 context184 knowledge184 vector184", 28),
        ["universe184 memory184", "stream184 context184", "knowledge184 vector184"],
    ),
    (
        ("memory184 stream184 context184 knowledge184 vector184 processor184", 6),
        ["memory184", "stream184", "context184", "knowledge184", "vector184", "processor184"],
    ),
    (
        ("memory184 stream184 context184 knowledge184 vector184 processor184", 10),
        ["memory184", "stream184", "context184", "knowledge184", "vector184", "processor184"],
    ),
    (
        ("memory184 stream184 context184 knowledge184 vector184 processor184", 18),
        ["memory184", "stream184", "context184", "knowledge184", "vector184", "processor184"],
    ),
    (
        ("memory184 stream184 context184 knowledge184 vector184 processor184", 28),
        ["memory184 stream184", "context184 knowledge184", "vector184 processor184"],
    ),
    (
        ("stream184 context184 knowledge184 vector184 processor184 reasoning184", 6),
        ["stream184", "context184", "knowledge184", "vector184", "processor184", "reasoning184"],
    ),
    (
        ("stream184 context184 knowledge184 vector184 processor184 reasoning184", 10),
        ["stream184", "context184", "knowledge184", "vector184", "processor184", "reasoning184"],
    ),
    (
        ("stream184 context184 knowledge184 vector184 processor184 reasoning184", 18),
        ["stream184", "context184", "knowledge184", "vector184", "processor184", "reasoning184"],
    ),
    (
        ("stream184 context184 knowledge184 vector184 processor184 reasoning184", 28),
        ["stream184 context184", "knowledge184 vector184", "processor184 reasoning184"],
    ),
    (
        ("context184 knowledge184 vector184 processor184 reasoning184 machine184", 6),
        ["context184", "knowledge184", "vector184", "processor184", "reasoning184", "machine184"],
    ),
    (
        ("context184 knowledge184 vector184 processor184 reasoning184 machine184", 10),
        ["context184", "knowledge184", "vector184", "processor184", "reasoning184", "machine184"],
    ),
    (
        ("context184 knowledge184 vector184 processor184 reasoning184 machine184", 18),
        ["context184", "knowledge184", "vector184", "processor184", "reasoning184", "machine184"],
    ),
    (
        ("context184 knowledge184 vector184 processor184 reasoning184 machine184", 28),
        ["context184 knowledge184", "vector184 processor184", "reasoning184 machine184"],
    ),
    (
        ("knowledge184 vector184 processor184 reasoning184 machine184 learning184", 6),
        ["knowledge184", "vector184", "processor184", "reasoning184", "machine184", "learning184"],
    ),
    (
        ("knowledge184 vector184 processor184 reasoning184 machine184 learning184", 10),
        ["knowledge184", "vector184", "processor184", "reasoning184", "machine184", "learning184"],
    ),
    (
        ("knowledge184 vector184 processor184 reasoning184 machine184 learning184", 18),
        ["knowledge184", "vector184", "processor184", "reasoning184", "machine184", "learning184"],
    ),
    (
        ("knowledge184 vector184 processor184 reasoning184 machine184 learning184", 28),
        ["knowledge184 vector184", "processor184 reasoning184", "machine184 learning184"],
    ),
    (
        ("vector184 processor184 reasoning184 machine184 learning184 model184", 6),
        ["vector184", "processor184", "reasoning184", "machine184", "learning184", "model184"],
    ),
    (
        ("vector184 processor184 reasoning184 machine184 learning184 model184", 10),
        ["vector184", "processor184", "reasoning184", "machine184", "learning184", "model184"],
    ),
    (
        ("vector184 processor184 reasoning184 machine184 learning184 model184", 18),
        ["vector184", "processor184", "reasoning184", "machine184", "learning184", "model184"],
    ),
    (
        ("vector184 processor184 reasoning184 machine184 learning184 model184", 28),
        ["vector184 processor184", "reasoning184 machine184", "learning184 model184"],
    ),
    (
        ("processor184 reasoning184 machine184 learning184 model184 token184", 6),
        ["processor184", "reasoning184", "machine184", "learning184", "model184", "token184"],
    ),
    (
        ("processor184 reasoning184 machine184 learning184 model184 token184", 10),
        ["processor184", "reasoning184", "machine184", "learning184", "model184", "token184"],
    ),
    (
        ("processor184 reasoning184 machine184 learning184 model184 token184", 18),
        ["processor184", "reasoning184", "machine184", "learning184", "model184 token184"],
    ),
    (
        ("processor184 reasoning184 machine184 learning184 model184 token184", 28),
        ["processor184 reasoning184", "machine184 learning184", "model184 token184"],
    ),
    (
        ("reasoning184 machine184 learning184 model184 token184 prompt184", 6),
        ["reasoning184", "machine184", "learning184", "model184", "token184", "prompt184"],
    ),
    (
        ("reasoning184 machine184 learning184 model184 token184 prompt184", 10),
        ["reasoning184", "machine184", "learning184", "model184", "token184", "prompt184"],
    ),
    (
        ("reasoning184 machine184 learning184 model184 token184 prompt184", 18),
        ["reasoning184", "machine184", "learning184", "model184 token184", "prompt184"],
    ),
    (
        ("reasoning184 machine184 learning184 model184 token184 prompt184", 28),
        ["reasoning184 machine184", "learning184 model184", "token184 prompt184"],
    ),
    (
        ("machine184 learning184 model184 token184 prompt184 session184", 6),
        ["machine184", "learning184", "model184", "token184", "prompt184", "session184"],
    ),
    (
        ("machine184 learning184 model184 token184 prompt184 session184", 10),
        ["machine184", "learning184", "model184", "token184", "prompt184", "session184"],
    ),
    (
        ("machine184 learning184 model184 token184 prompt184 session184", 18),
        ["machine184", "learning184", "model184 token184", "prompt184", "session184"],
    ),
    (
        ("machine184 learning184 model184 token184 prompt184 session184", 28),
        ["machine184 learning184", "model184 token184 prompt184", "session184"],
    ),
    (
        ("learning184 model184 token184 prompt184 session184 library184", 6),
        ["learning184", "model184", "token184", "prompt184", "session184", "library184"],
    ),
    (
        ("learning184 model184 token184 prompt184 session184 library184", 10),
        ["learning184", "model184", "token184", "prompt184", "session184", "library184"],
    ),
    (
        ("learning184 model184 token184 prompt184 session184 library184", 18),
        ["learning184", "model184 token184", "prompt184", "session184", "library184"],
    ),
    (
        ("learning184 model184 token184 prompt184 session184 library184", 28),
        ["learning184 model184", "token184 prompt184", "session184 library184"],
    ),
    (
        ("model184 token184 prompt184 session184 library184 service184", 6),
        ["model184", "token184", "prompt184", "session184", "library184", "service184"],
    ),
    (
        ("model184 token184 prompt184 session184 library184 service184", 10),
        ["model184", "token184", "prompt184", "session184", "library184", "service184"],
    ),
    (
        ("model184 token184 prompt184 session184 library184 service184", 18),
        ["model184 token184", "prompt184", "session184", "library184", "service184"],
    ),
    (
        ("model184 token184 prompt184 session184 library184 service184", 28),
        ["model184 token184 prompt184", "session184 library184", "service184"],
    ),
    (
        ("token184 prompt184 session184 library184 service184 gateway184", 6),
        ["token184", "prompt184", "session184", "library184", "service184", "gateway184"],
    ),
    (
        ("token184 prompt184 session184 library184 service184 gateway184", 10),
        ["token184", "prompt184", "session184", "library184", "service184", "gateway184"],
    ),
    (
        ("token184 prompt184 session184 library184 service184 gateway184", 18),
        ["token184 prompt184", "session184", "library184", "service184", "gateway184"],
    ),
    (
        ("token184 prompt184 session184 library184 service184 gateway184", 28),
        ["token184 prompt184", "session184 library184", "service184 gateway184"],
    ),
    (
        ("prompt184 session184 library184 service184 gateway184 storage184", 6),
        ["prompt184", "session184", "library184", "service184", "gateway184", "storage184"],
    ),
    (
        ("prompt184 session184 library184 service184 gateway184 storage184", 10),
        ["prompt184", "session184", "library184", "service184", "gateway184", "storage184"],
    ),
    (
        ("prompt184 session184 library184 service184 gateway184 storage184", 18),
        ["prompt184", "session184", "library184", "service184", "gateway184", "storage184"],
    ),
    (
        ("prompt184 session184 library184 service184 gateway184 storage184", 28),
        ["prompt184 session184", "library184 service184", "gateway184 storage184"],
    ),
    (
        ("session184 library184 service184 gateway184 storage184 network184", 6),
        ["session184", "library184", "service184", "gateway184", "storage184", "network184"],
    ),
    (
        ("session184 library184 service184 gateway184 storage184 network184", 10),
        ["session184", "library184", "service184", "gateway184", "storage184", "network184"],
    ),
    (
        ("session184 library184 service184 gateway184 storage184 network184", 18),
        ["session184", "library184", "service184", "gateway184", "storage184", "network184"],
    ),
    (
        ("session184 library184 service184 gateway184 storage184 network184", 28),
        ["session184 library184", "service184 gateway184", "storage184 network184"],
    ),
    (
        ("library184 service184 gateway184 storage184 network184 latency184", 6),
        ["library184", "service184", "gateway184", "storage184", "network184", "latency184"],
    ),
    (
        ("library184 service184 gateway184 storage184 network184 latency184", 10),
        ["library184", "service184", "gateway184", "storage184", "network184", "latency184"],
    ),
    (
        ("library184 service184 gateway184 storage184 network184 latency184", 18),
        ["library184", "service184", "gateway184", "storage184", "network184", "latency184"],
    ),
    (
        ("library184 service184 gateway184 storage184 network184 latency184", 28),
        ["library184 service184", "gateway184 storage184", "network184 latency184"],
    ),
    (
        ("service184 gateway184 storage184 network184 latency184 buffer184", 6),
        ["service184", "gateway184", "storage184", "network184", "latency184", "buffer184"],
    ),
    (
        ("service184 gateway184 storage184 network184 latency184 buffer184", 10),
        ["service184", "gateway184", "storage184", "network184", "latency184", "buffer184"],
    ),
    (
        ("service184 gateway184 storage184 network184 latency184 buffer184", 18),
        ["service184", "gateway184", "storage184", "network184", "latency184", "buffer184"],
    ),
    (
        ("service184 gateway184 storage184 network184 latency184 buffer184", 28),
        ["service184 gateway184", "storage184 network184", "latency184 buffer184"],
    ),
    (
        ("gateway184 storage184 network184 latency184 buffer184 queue184", 6),
        ["gateway184", "storage184", "network184", "latency184", "buffer184", "queue184"],
    ),
    (
        ("gateway184 storage184 network184 latency184 buffer184 queue184", 10),
        ["gateway184", "storage184", "network184", "latency184", "buffer184", "queue184"],
    ),
    (
        ("gateway184 storage184 network184 latency184 buffer184 queue184", 18),
        ["gateway184", "storage184", "network184", "latency184", "buffer184 queue184"],
    ),
    (
        ("gateway184 storage184 network184 latency184 buffer184 queue184", 28),
        ["gateway184 storage184", "network184 latency184", "buffer184 queue184"],
    ),
    (
        ("storage184 network184 latency184 buffer184 queue184 worker184", 6),
        ["storage184", "network184", "latency184", "buffer184", "queue184", "worker184"],
    ),
    (
        ("storage184 network184 latency184 buffer184 queue184 worker184", 10),
        ["storage184", "network184", "latency184", "buffer184", "queue184", "worker184"],
    ),
    (
        ("storage184 network184 latency184 buffer184 queue184 worker184", 18),
        ["storage184", "network184", "latency184", "buffer184 queue184", "worker184"],
    ),
    (
        ("storage184 network184 latency184 buffer184 queue184 worker184", 28),
        ["storage184 network184", "latency184 buffer184", "queue184 worker184"],
    ),
    (
        ("network184 latency184 buffer184 queue184 worker184 kernel184", 6),
        ["network184", "latency184", "buffer184", "queue184", "worker184", "kernel184"],
    ),
    (
        ("network184 latency184 buffer184 queue184 worker184 kernel184", 10),
        ["network184", "latency184", "buffer184", "queue184", "worker184", "kernel184"],
    ),
    (
        ("network184 latency184 buffer184 queue184 worker184 kernel184", 18),
        ["network184", "latency184", "buffer184 queue184", "worker184", "kernel184"],
    ),
    (
        ("network184 latency184 buffer184 queue184 worker184 kernel184", 28),
        ["network184 latency184", "buffer184 queue184 worker184", "kernel184"],
    ),
    (
        ("latency184 buffer184 queue184 worker184 kernel184 signal184", 6),
        ["latency184", "buffer184", "queue184", "worker184", "kernel184", "signal184"],
    ),
    (
        ("latency184 buffer184 queue184 worker184 kernel184 signal184", 10),
        ["latency184", "buffer184", "queue184", "worker184", "kernel184", "signal184"],
    ),
    (
        ("latency184 buffer184 queue184 worker184 kernel184 signal184", 18),
        ["latency184", "buffer184 queue184", "worker184", "kernel184", "signal184"],
    ),
    (
        ("latency184 buffer184 queue184 worker184 kernel184 signal184", 28),
        ["latency184 buffer184", "queue184 worker184 kernel184", "signal184"],
    ),
    (
        ("buffer184 queue184 worker184 kernel184 signal184 packet184", 6),
        ["buffer184", "queue184", "worker184", "kernel184", "signal184", "packet184"],
    ),
    (
        ("buffer184 queue184 worker184 kernel184 signal184 packet184", 10),
        ["buffer184", "queue184", "worker184", "kernel184", "signal184", "packet184"],
    ),
    (
        ("buffer184 queue184 worker184 kernel184 signal184 packet184", 18),
        ["buffer184 queue184", "worker184", "kernel184", "signal184", "packet184"],
    ),
    (
        ("buffer184 queue184 worker184 kernel184 signal184 packet184", 28),
        ["buffer184 queue184 worker184", "kernel184 signal184", "packet184"],
    ),
    (
        ("queue184 worker184 kernel184 signal184 packet184 router184", 6),
        ["queue184", "worker184", "kernel184", "signal184", "packet184", "router184"],
    ),
    (
        ("queue184 worker184 kernel184 signal184 packet184 router184", 10),
        ["queue184", "worker184", "kernel184", "signal184", "packet184", "router184"],
    ),
    (
        ("queue184 worker184 kernel184 signal184 packet184 router184", 18),
        ["queue184 worker184", "kernel184", "signal184", "packet184", "router184"],
    ),
    (
        ("queue184 worker184 kernel184 signal184 packet184 router184", 28),
        ["queue184 worker184 kernel184", "signal184 packet184", "router184"],
    ),
    (
        ("worker184 kernel184 signal184 packet184 router184 cluster184", 6),
        ["worker184", "kernel184", "signal184", "packet184", "router184", "cluster184"],
    ),
    (
        ("worker184 kernel184 signal184 packet184 router184 cluster184", 10),
        ["worker184", "kernel184", "signal184", "packet184", "router184", "cluster184"],
    ),
    (
        ("worker184 kernel184 signal184 packet184 router184 cluster184", 18),
        ["worker184", "kernel184", "signal184", "packet184", "router184", "cluster184"],
    ),
    (
        ("worker184 kernel184 signal184 packet184 router184 cluster184", 28),
        ["worker184 kernel184", "signal184 packet184", "router184 cluster184"],
    ),
    (
        ("kernel184 signal184 packet184 router184 cluster184 mirror184", 6),
        ["kernel184", "signal184", "packet184", "router184", "cluster184", "mirror184"],
    ),
    (
        ("kernel184 signal184 packet184 router184 cluster184 mirror184", 10),
        ["kernel184", "signal184", "packet184", "router184", "cluster184", "mirror184"],
    ),
    (
        ("kernel184 signal184 packet184 router184 cluster184 mirror184", 18),
        ["kernel184", "signal184", "packet184", "router184", "cluster184", "mirror184"],
    ),
    (
        ("kernel184 signal184 packet184 router184 cluster184 mirror184", 28),
        ["kernel184 signal184", "packet184 router184", "cluster184 mirror184"],
    ),
    (
        ("signal184 packet184 router184 cluster184 mirror184 filter184", 6),
        ["signal184", "packet184", "router184", "cluster184", "mirror184", "filter184"],
    ),
    (
        ("signal184 packet184 router184 cluster184 mirror184 filter184", 10),
        ["signal184", "packet184", "router184", "cluster184", "mirror184", "filter184"],
    ),
    (
        ("signal184 packet184 router184 cluster184 mirror184 filter184", 18),
        ["signal184", "packet184", "router184", "cluster184", "mirror184", "filter184"],
    ),
    (
        ("signal184 packet184 router184 cluster184 mirror184 filter184", 28),
        ["signal184 packet184", "router184 cluster184", "mirror184 filter184"],
    ),
    (
        ("packet184 router184 cluster184 mirror184 filter184 ranking184", 6),
        ["packet184", "router184", "cluster184", "mirror184", "filter184", "ranking184"],
    ),
    (
        ("packet184 router184 cluster184 mirror184 filter184 ranking184", 10),
        ["packet184", "router184", "cluster184", "mirror184", "filter184", "ranking184"],
    ),
    (
        ("packet184 router184 cluster184 mirror184 filter184 ranking184", 18),
        ["packet184", "router184", "cluster184", "mirror184", "filter184", "ranking184"],
    ),
    (
        ("packet184 router184 cluster184 mirror184 filter184 ranking184", 28),
        ["packet184 router184", "cluster184 mirror184", "filter184 ranking184"],
    ),
    (
        ("router184 cluster184 mirror184 filter184 ranking184 encoding184", 6),
        ["router184", "cluster184", "mirror184", "filter184", "ranking184", "encoding184"],
    ),
    (
        ("router184 cluster184 mirror184 filter184 ranking184 encoding184", 10),
        ["router184", "cluster184", "mirror184", "filter184", "ranking184", "encoding184"],
    ),
    (
        ("router184 cluster184 mirror184 filter184 ranking184 encoding184", 18),
        ["router184", "cluster184", "mirror184", "filter184", "ranking184", "encoding184"],
    ),
    (
        ("router184 cluster184 mirror184 filter184 ranking184 encoding184", 28),
        ["router184 cluster184", "mirror184 filter184", "ranking184 encoding184"],
    ),
    (
        ("cluster184 mirror184 filter184 ranking184 encoding184 mapping184", 6),
        ["cluster184", "mirror184", "filter184", "ranking184", "encoding184", "mapping184"],
    ),
    (
        ("cluster184 mirror184 filter184 ranking184 encoding184 mapping184", 10),
        ["cluster184", "mirror184", "filter184", "ranking184", "encoding184", "mapping184"],
    ),
    (
        ("cluster184 mirror184 filter184 ranking184 encoding184 mapping184", 18),
        ["cluster184", "mirror184", "filter184", "ranking184", "encoding184", "mapping184"],
    ),
    (
        ("cluster184 mirror184 filter184 ranking184 encoding184 mapping184", 28),
        ["cluster184 mirror184", "filter184 ranking184", "encoding184 mapping184"],
    ),
    (
        ("mirror184 filter184 ranking184 encoding184 mapping184 record184", 6),
        ["mirror184", "filter184", "ranking184", "encoding184", "mapping184", "record184"],
    ),
    (
        ("mirror184 filter184 ranking184 encoding184 mapping184 record184", 10),
        ["mirror184", "filter184", "ranking184", "encoding184", "mapping184", "record184"],
    ),
    (
        ("mirror184 filter184 ranking184 encoding184 mapping184 record184", 18),
        ["mirror184", "filter184", "ranking184", "encoding184", "mapping184", "record184"],
    ),
    (
        ("mirror184 filter184 ranking184 encoding184 mapping184 record184", 28),
        ["mirror184 filter184", "ranking184 encoding184", "mapping184 record184"],
    ),
    (
        ("filter184 ranking184 encoding184 mapping184 record184 candle184", 6),
        ["filter184", "ranking184", "encoding184", "mapping184", "record184", "candle184"],
    ),
    (
        ("filter184 ranking184 encoding184 mapping184 record184 candle184", 10),
        ["filter184", "ranking184", "encoding184", "mapping184", "record184", "candle184"],
    ),
    (
        ("filter184 ranking184 encoding184 mapping184 record184 candle184", 18),
        ["filter184", "ranking184", "encoding184", "mapping184", "record184", "candle184"],
    ),
    (
        ("filter184 ranking184 encoding184 mapping184 record184 candle184", 28),
        ["filter184 ranking184", "encoding184 mapping184", "record184 candle184"],
    ),
    (
        ("ranking184 encoding184 mapping184 record184 candle184 thread184", 6),
        ["ranking184", "encoding184", "mapping184", "record184", "candle184", "thread184"],
    ),
    (
        ("ranking184 encoding184 mapping184 record184 candle184 thread184", 10),
        ["ranking184", "encoding184", "mapping184", "record184", "candle184", "thread184"],
    ),
    (
        ("ranking184 encoding184 mapping184 record184 candle184 thread184", 18),
        ["ranking184", "encoding184", "mapping184", "record184", "candle184", "thread184"],
    ),
    (
        ("ranking184 encoding184 mapping184 record184 candle184 thread184", 28),
        ["ranking184 encoding184", "mapping184 record184", "candle184 thread184"],
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
