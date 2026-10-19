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
        ("round 57: the quick brown fox jumps over the lazy dog", 4),
        ["round", "57:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 57: the quick brown fox jumps over the lazy dog", 8),
        ["round", "57: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 57: the quick brown fox jumps over the lazy dog", 12),
        ["round 57:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 57: the quick brown fox jumps over the lazy dog", 16),
        ["round 57: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 57: the quick brown fox jumps over the lazy dog", 24),
        ["round 57: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 57: the quick brown fox jumps over the lazy dog", 32),
        ["round 57: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 57: agentuniverse is a framework for multi agents", 4),
        ["round", "57:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 57: agentuniverse is a framework for multi agents", 8),
        ["round", "57:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 57: agentuniverse is a framework for multi agents", 12),
        ["round 57:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 57: agentuniverse is a framework for multi agents", 16),
        ["round 57:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 57: agentuniverse is a framework for multi agents", 24),
        ["round 57: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 57: agentuniverse is a framework for multi agents", 32),
        ["round 57: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 57: knowledge stored as vectors enables retrieval", 4),
        ["round", "57:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 57: knowledge stored as vectors enables retrieval", 8),
        ["round", "57:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 57: knowledge stored as vectors enables retrieval", 12),
        ["round 57:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 57: knowledge stored as vectors enables retrieval", 16),
        ["round 57:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 57: knowledge stored as vectors enables retrieval", 24),
        ["round 57: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 57: knowledge stored as vectors enables retrieval", 32),
        ["round 57: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 57: the processor reads the record then stops", 4),
        ["round", "57:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 57: the processor reads the record then stops", 8),
        ["round", "57: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 57: the processor reads the record then stops", 12),
        ["round 57:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 57: the processor reads the record then stops", 16),
        ["round 57: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 57: the processor reads the record then stops", 24),
        ["round 57: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 57: the processor reads the record then stops", 32),
        ["round 57: the processor reads", "the record then stops"],
    ),
    (
        ("round 57: a worker pulls the next task from the queue", 4),
        ["round", "57:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 57: a worker pulls the next task from the queue", 8),
        ["round", "57: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 57: a worker pulls the next task from the queue", 12),
        ["round 57: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 57: a worker pulls the next task from the queue", 16),
        ["round 57: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 57: a worker pulls the next task from the queue", 24),
        ["round 57: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 57: a worker pulls the next task from the queue", 32),
        ["round 57: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 57: signals travel through the network layer", 4),
        ["round", "57:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 57: signals travel through the network layer", 8),
        ["round", "57:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 57: signals travel through the network layer", 12),
        ["round 57:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 57: signals travel through the network layer", 16),
        ["round 57:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 57: signals travel through the network layer", 24),
        ["round 57: signals travel", "through the network", "layer"],
    ),
    (
        ("round 57: signals travel through the network layer", 32),
        ["round 57: signals travel through", "the network layer"],
    ),
    (
        ("round 57: the gateway routes each request by policy", 4),
        ["round", "57:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 57: the gateway routes each request by policy", 8),
        ["round", "57: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 57: the gateway routes each request by policy", 12),
        ["round 57:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 57: the gateway routes each request by policy", 16),
        ["round 57: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 57: the gateway routes each request by policy", 24),
        ["round 57: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 57: the gateway routes each request by policy", 32),
        ["round 57: the gateway routes", "each request by policy"],
    ),
    (
        ("round 57: memory grows until the buffer is full", 4),
        ["round", "57:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 57: memory grows until the buffer is full", 8),
        ["round", "57:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 57: memory grows until the buffer is full", 12),
        ["round 57:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 57: memory grows until the buffer is full", 16),
        ["round 57: memory", "grows until the", "buffer is full"],
    ),
    (("round 57: memory grows until the buffer is full", 24), ["round 57: memory grows", "until the buffer is full"]),
    (("round 57: memory grows until the buffer is full", 32), ["round 57: memory grows until the", "buffer is full"]),
    (
        ("round 57: the cluster mirrors every packet twice", 4),
        ["round", "57:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 57: the cluster mirrors every packet twice", 8),
        ["round", "57: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 57: the cluster mirrors every packet twice", 12),
        ["round 57:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 57: the cluster mirrors every packet twice", 16),
        ["round 57: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 57: the cluster mirrors every packet twice", 24),
        ["round 57: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 57: the cluster mirrors every packet twice", 32), ["round 57: the cluster mirrors", "every packet twice"]),
    (
        ("round 57: ranking uses tokens learned from the corpus", 4),
        ["round", "57:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 57: ranking uses tokens learned from the corpus", 8),
        ["round", "57:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 57: ranking uses tokens learned from the corpus", 12),
        ["round 57:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 57: ranking uses tokens learned from the corpus", 16),
        ["round 57:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 57: ranking uses tokens learned from the corpus", 24),
        ["round 57: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 57: ranking uses tokens learned from the corpus", 32),
        ["round 57: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 57: a long session ends when the candle dies", 4),
        ["round", "57:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 57: a long session ends when the candle dies", 8),
        ["round", "57: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 57: a long session ends when the candle dies", 12),
        ["round 57: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 57: a long session ends when the candle dies", 16),
        ["round 57: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 57: a long session ends when the candle dies", 24),
        ["round 57: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 57: a long session ends when the candle dies", 32),
        ["round 57: a long session ends", "when the candle dies"],
    ),
    (
        ("round 57: encode the prompt then map the result", 4),
        ["round", "57:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 57: encode the prompt then map the result", 8),
        ["round", "57:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 57: encode the prompt then map the result", 12),
        ["round 57:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 57: encode the prompt then map the result", 16),
        ["round 57: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 57: encode the prompt then map the result", 24),
        ["round 57: encode the", "prompt then map the", "result"],
    ),
    (("round 57: encode the prompt then map the result", 32), ["round 57: encode the prompt then", "map the result"]),
    (
        ("round 57: the kernel wakes the worker at dawn", 4),
        ["round", "57:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 57: the kernel wakes the worker at dawn", 8),
        ["round", "57: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 57: the kernel wakes the worker at dawn", 12),
        ["round 57:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 57: the kernel wakes the worker at dawn", 16), ["round 57: the", "kernel wakes the", "worker at dawn"]),
    (("round 57: the kernel wakes the worker at dawn", 24), ["round 57: the kernel", "wakes the worker at dawn"]),
    (("round 57: the kernel wakes the worker at dawn", 32), ["round 57: the kernel wakes the", "worker at dawn"]),
    (
        ("round 57: service latency drops after the patch", 4),
        ["round", "57:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 57: service latency drops after the patch", 8),
        ["round", "57:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 57: service latency drops after the patch", 12),
        ["round 57:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 57: service latency drops after the patch", 16),
        ["round 57:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 57: service latency drops after the patch", 24),
        ["round 57: service", "latency drops after the", "patch"],
    ),
    (("round 57: service latency drops after the patch", 32), ["round 57: service latency drops", "after the patch"]),
    (
        ("round 57: the library caches every vector it sees", 4),
        ["round", "57:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 57: the library caches every vector it sees", 8),
        ["round", "57: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 57: the library caches every vector it sees", 12),
        ["round 57:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 57: the library caches every vector it sees", 16),
        ["round 57: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 57: the library caches every vector it sees", 24),
        ["round 57: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 57: the library caches every vector it sees", 32),
        ["round 57: the library caches", "every vector it sees"],
    ),
    (
        ("round 57: agents argue then the debate resolves", 4),
        ["round", "57:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 57: agents argue then the debate resolves", 8),
        ["round", "57:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 57: agents argue then the debate resolves", 12),
        ["round 57:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 57: agents argue then the debate resolves", 16),
        ["round 57: agents", "argue then the", "debate resolves"],
    ),
    (("round 57: agents argue then the debate resolves", 24), ["round 57: agents argue", "then the debate resolves"]),
    (("round 57: agents argue then the debate resolves", 32), ["round 57: agents argue then the", "debate resolves"]),
    (
        ("round 57: the filter keeps only strong matches", 4),
        ["round", "57:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 57: the filter keeps only strong matches", 8),
        ["round", "57: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 57: the filter keeps only strong matches", 12),
        ["round 57:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 57: the filter keeps only strong matches", 16),
        ["round 57: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 57: the filter keeps only strong matches", 24), ["round 57: the filter", "keeps only strong", "matches"]),
    (("round 57: the filter keeps only strong matches", 32), ["round 57: the filter keeps only", "strong matches"]),
    (
        ("round 57: the model answers with a short reply", 4),
        ["round", "57:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 57: the model answers with a short reply", 8),
        ["round", "57: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 57: the model answers with a short reply", 12),
        ["round 57:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 57: the model answers with a short reply", 16),
        ["round 57: the", "model answers", "with a short", "reply"],
    ),
    (("round 57: the model answers with a short reply", 24), ["round 57: the model", "answers with a short", "reply"]),
    (("round 57: the model answers with a short reply", 32), ["round 57: the model answers with", "a short reply"]),
    (
        ("round 57: the recorder stores the reasoning trace", 4),
        ["round", "57:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 57: the recorder stores the reasoning trace", 8),
        ["round", "57: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 57: the recorder stores the reasoning trace", 12),
        ["round 57:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 57: the recorder stores the reasoning trace", 16),
        ["round 57: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 57: the recorder stores the reasoning trace", 24),
        ["round 57: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 57: the recorder stores the reasoning trace", 32),
        ["round 57: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 57: the angel watches the processor run", 4),
        ["round", "57:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 57: the angel watches the processor run", 8),
        ["round", "57: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 57: the angel watches the processor run", 12),
        ["round 57:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 57: the angel watches the processor run", 16), ["round 57: the", "angel watches", "the processor", "run"]),
    (("round 57: the angel watches the processor run", 24), ["round 57: the angel", "watches the processor", "run"]),
    (("round 57: the angel watches the processor run", 32), ["round 57: the angel watches the", "processor run"]),
    (
        ("round 57: angle of the vector decides the match", 4),
        ["round", "57:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 57: angle of the vector decides the match", 8),
        ["round", "57:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 57: angle of the vector decides the match", 12),
        ["round 57:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 57: angle of the vector decides the match", 16),
        ["round 57: angle", "of the vector", "decides the", "match"],
    ),
    (("round 57: angle of the vector decides the match", 24), ["round 57: angle of the", "vector decides the match"]),
    (("round 57: angle of the vector decides the match", 32), ["round 57: angle of the vector", "decides the match"]),
    (
        ("round 57: the candle burns twice as long at night", 4),
        ["round", "57:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 57: the candle burns twice as long at night", 8),
        ["round", "57: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 57: the candle burns twice as long at night", 12),
        ["round 57:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 57: the candle burns twice as long at night", 16),
        ["round 57: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 57: the candle burns twice as long at night", 24),
        ["round 57: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 57: the candle burns twice as long at night", 32),
        ["round 57: the candle burns twice", "as long at night"],
    ),
    (
        ("round 57: a mirror of the universe in one line", 4),
        ["round", "57:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 57: a mirror of the universe in one line", 8),
        ["round", "57: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 57: a mirror of the universe in one line", 12),
        ["round 57: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 57: a mirror of the universe in one line", 16),
        ["round 57: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 57: a mirror of the universe in one line", 24), ["round 57: a mirror of", "the universe in one line"]),
    (("round 57: a mirror of the universe in one line", 32), ["round 57: a mirror of the", "universe in one line"]),
    (
        ("round 57: the queue drains before the storm", 4),
        ["round", "57:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 57: the queue drains before the storm", 8),
        ["round", "57: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 57: the queue drains before the storm", 12), ["round 57:", "the queue", "drains", "before the", "storm"]),
    (("round 57: the queue drains before the storm", 16), ["round 57: the", "queue drains", "before the storm"]),
    (("round 57: the queue drains before the storm", 24), ["round 57: the queue", "drains before the storm"]),
    (("round 57: the queue drains before the storm", 32), ["round 57: the queue drains", "before the storm"]),
    (
        ("kitten57 sitting57 agent57 angle57 universe57 memory57", 6),
        ["kitten57", "sitting57", "agent57", "angle57", "universe57", "memory57"],
    ),
    (
        ("kitten57 sitting57 agent57 angle57 universe57 memory57", 10),
        ["kitten57", "sitting57", "agent57", "angle57", "universe57", "memory57"],
    ),
    (
        ("kitten57 sitting57 agent57 angle57 universe57 memory57", 18),
        ["kitten57 sitting57", "agent57 angle57", "universe57", "memory57"],
    ),
    (
        ("kitten57 sitting57 agent57 angle57 universe57 memory57", 28),
        ["kitten57 sitting57 agent57", "angle57 universe57 memory57"],
    ),
    (
        ("sitting57 agent57 angle57 universe57 memory57 stream57", 6),
        ["sitting57", "agent57", "angle57", "universe57", "memory57", "stream57"],
    ),
    (
        ("sitting57 agent57 angle57 universe57 memory57 stream57", 10),
        ["sitting57", "agent57", "angle57", "universe57", "memory57", "stream57"],
    ),
    (
        ("sitting57 agent57 angle57 universe57 memory57 stream57", 18),
        ["sitting57 agent57", "angle57 universe57", "memory57 stream57"],
    ),
    (
        ("sitting57 agent57 angle57 universe57 memory57 stream57", 28),
        ["sitting57 agent57 angle57", "universe57 memory57 stream57"],
    ),
    (
        ("agent57 angle57 universe57 memory57 stream57 context57", 6),
        ["agent57", "angle57", "universe57", "memory57", "stream57", "context57"],
    ),
    (
        ("agent57 angle57 universe57 memory57 stream57 context57", 10),
        ["agent57", "angle57", "universe57", "memory57", "stream57", "context57"],
    ),
    (
        ("agent57 angle57 universe57 memory57 stream57 context57", 18),
        ["agent57 angle57", "universe57", "memory57 stream57", "context57"],
    ),
    (
        ("agent57 angle57 universe57 memory57 stream57 context57", 28),
        ["agent57 angle57 universe57", "memory57 stream57 context57"],
    ),
    (
        ("angle57 universe57 memory57 stream57 context57 knowledge57", 6),
        ["angle57", "universe57", "memory57", "stream57", "context57", "knowledge57"],
    ),
    (
        ("angle57 universe57 memory57 stream57 context57 knowledge57", 10),
        ["angle57", "universe57", "memory57", "stream57", "context57", "knowledge57"],
    ),
    (
        ("angle57 universe57 memory57 stream57 context57 knowledge57", 18),
        ["angle57 universe57", "memory57 stream57", "context57", "knowledge57"],
    ),
    (
        ("angle57 universe57 memory57 stream57 context57 knowledge57", 28),
        ["angle57 universe57 memory57", "stream57 context57", "knowledge57"],
    ),
    (
        ("universe57 memory57 stream57 context57 knowledge57 vector57", 6),
        ["universe57", "memory57", "stream57", "context57", "knowledge57", "vector57"],
    ),
    (
        ("universe57 memory57 stream57 context57 knowledge57 vector57", 10),
        ["universe57", "memory57", "stream57", "context57", "knowledge57", "vector57"],
    ),
    (
        ("universe57 memory57 stream57 context57 knowledge57 vector57", 18),
        ["universe57", "memory57 stream57", "context57", "knowledge57", "vector57"],
    ),
    (
        ("universe57 memory57 stream57 context57 knowledge57 vector57", 28),
        ["universe57 memory57 stream57", "context57 knowledge57", "vector57"],
    ),
    (
        ("memory57 stream57 context57 knowledge57 vector57 processor57", 6),
        ["memory57", "stream57", "context57", "knowledge57", "vector57", "processor57"],
    ),
    (
        ("memory57 stream57 context57 knowledge57 vector57 processor57", 10),
        ["memory57", "stream57", "context57", "knowledge57", "vector57", "processor57"],
    ),
    (
        ("memory57 stream57 context57 knowledge57 vector57 processor57", 18),
        ["memory57 stream57", "context57", "knowledge57", "vector57", "processor57"],
    ),
    (
        ("memory57 stream57 context57 knowledge57 vector57 processor57", 28),
        ["memory57 stream57 context57", "knowledge57 vector57", "processor57"],
    ),
    (
        ("stream57 context57 knowledge57 vector57 processor57 reasoning57", 6),
        ["stream57", "context57", "knowledge57", "vector57", "processor57", "reasoning57"],
    ),
    (
        ("stream57 context57 knowledge57 vector57 processor57 reasoning57", 10),
        ["stream57", "context57", "knowledge57", "vector57", "processor57", "reasoning57"],
    ),
    (
        ("stream57 context57 knowledge57 vector57 processor57 reasoning57", 18),
        ["stream57 context57", "knowledge57", "vector57", "processor57", "reasoning57"],
    ),
    (
        ("stream57 context57 knowledge57 vector57 processor57 reasoning57", 28),
        ["stream57 context57", "knowledge57 vector57", "processor57 reasoning57"],
    ),
    (
        ("context57 knowledge57 vector57 processor57 reasoning57 machine57", 6),
        ["context57", "knowledge57", "vector57", "processor57", "reasoning57", "machine57"],
    ),
    (
        ("context57 knowledge57 vector57 processor57 reasoning57 machine57", 10),
        ["context57", "knowledge57", "vector57", "processor57", "reasoning57", "machine57"],
    ),
    (
        ("context57 knowledge57 vector57 processor57 reasoning57 machine57", 18),
        ["context57", "knowledge57", "vector57", "processor57", "reasoning57", "machine57"],
    ),
    (
        ("context57 knowledge57 vector57 processor57 reasoning57 machine57", 28),
        ["context57 knowledge57", "vector57 processor57", "reasoning57 machine57"],
    ),
    (
        ("knowledge57 vector57 processor57 reasoning57 machine57 learning57", 6),
        ["knowledge57", "vector57", "processor57", "reasoning57", "machine57", "learning57"],
    ),
    (
        ("knowledge57 vector57 processor57 reasoning57 machine57 learning57", 10),
        ["knowledge57", "vector57", "processor57", "reasoning57", "machine57", "learning57"],
    ),
    (
        ("knowledge57 vector57 processor57 reasoning57 machine57 learning57", 18),
        ["knowledge57", "vector57", "processor57", "reasoning57", "machine57", "learning57"],
    ),
    (
        ("knowledge57 vector57 processor57 reasoning57 machine57 learning57", 28),
        ["knowledge57 vector57", "processor57 reasoning57", "machine57 learning57"],
    ),
    (
        ("vector57 processor57 reasoning57 machine57 learning57 model57", 6),
        ["vector57", "processor57", "reasoning57", "machine57", "learning57", "model57"],
    ),
    (
        ("vector57 processor57 reasoning57 machine57 learning57 model57", 10),
        ["vector57", "processor57", "reasoning57", "machine57", "learning57", "model57"],
    ),
    (
        ("vector57 processor57 reasoning57 machine57 learning57 model57", 18),
        ["vector57", "processor57", "reasoning57", "machine57", "learning57 model57"],
    ),
    (
        ("vector57 processor57 reasoning57 machine57 learning57 model57", 28),
        ["vector57 processor57", "reasoning57 machine57", "learning57 model57"],
    ),
    (
        ("processor57 reasoning57 machine57 learning57 model57 token57", 6),
        ["processor57", "reasoning57", "machine57", "learning57", "model57", "token57"],
    ),
    (
        ("processor57 reasoning57 machine57 learning57 model57 token57", 10),
        ["processor57", "reasoning57", "machine57", "learning57", "model57", "token57"],
    ),
    (
        ("processor57 reasoning57 machine57 learning57 model57 token57", 18),
        ["processor57", "reasoning57", "machine57", "learning57 model57", "token57"],
    ),
    (
        ("processor57 reasoning57 machine57 learning57 model57 token57", 28),
        ["processor57 reasoning57", "machine57 learning57 model57", "token57"],
    ),
    (
        ("reasoning57 machine57 learning57 model57 token57 prompt57", 6),
        ["reasoning57", "machine57", "learning57", "model57", "token57", "prompt57"],
    ),
    (
        ("reasoning57 machine57 learning57 model57 token57 prompt57", 10),
        ["reasoning57", "machine57", "learning57", "model57", "token57", "prompt57"],
    ),
    (
        ("reasoning57 machine57 learning57 model57 token57 prompt57", 18),
        ["reasoning57", "machine57", "learning57 model57", "token57 prompt57"],
    ),
    (
        ("reasoning57 machine57 learning57 model57 token57 prompt57", 28),
        ["reasoning57 machine57", "learning57 model57 token57", "prompt57"],
    ),
    (
        ("machine57 learning57 model57 token57 prompt57 session57", 6),
        ["machine57", "learning57", "model57", "token57", "prompt57", "session57"],
    ),
    (
        ("machine57 learning57 model57 token57 prompt57 session57", 10),
        ["machine57", "learning57", "model57", "token57", "prompt57", "session57"],
    ),
    (
        ("machine57 learning57 model57 token57 prompt57 session57", 18),
        ["machine57", "learning57 model57", "token57 prompt57", "session57"],
    ),
    (
        ("machine57 learning57 model57 token57 prompt57 session57", 28),
        ["machine57 learning57 model57", "token57 prompt57 session57"],
    ),
    (
        ("learning57 model57 token57 prompt57 session57 library57", 6),
        ["learning57", "model57", "token57", "prompt57", "session57", "library57"],
    ),
    (
        ("learning57 model57 token57 prompt57 session57 library57", 10),
        ["learning57", "model57", "token57", "prompt57", "session57", "library57"],
    ),
    (
        ("learning57 model57 token57 prompt57 session57 library57", 18),
        ["learning57 model57", "token57 prompt57", "session57", "library57"],
    ),
    (
        ("learning57 model57 token57 prompt57 session57 library57", 28),
        ["learning57 model57 token57", "prompt57 session57 library57"],
    ),
    (
        ("model57 token57 prompt57 session57 library57 service57", 6),
        ["model57", "token57", "prompt57", "session57", "library57", "service57"],
    ),
    (
        ("model57 token57 prompt57 session57 library57 service57", 10),
        ["model57", "token57", "prompt57", "session57", "library57", "service57"],
    ),
    (
        ("model57 token57 prompt57 session57 library57 service57", 18),
        ["model57 token57", "prompt57 session57", "library57", "service57"],
    ),
    (
        ("model57 token57 prompt57 session57 library57 service57", 28),
        ["model57 token57 prompt57", "session57 library57", "service57"],
    ),
    (
        ("token57 prompt57 session57 library57 service57 gateway57", 6),
        ["token57", "prompt57", "session57", "library57", "service57", "gateway57"],
    ),
    (
        ("token57 prompt57 session57 library57 service57 gateway57", 10),
        ["token57", "prompt57", "session57", "library57", "service57", "gateway57"],
    ),
    (
        ("token57 prompt57 session57 library57 service57 gateway57", 18),
        ["token57 prompt57", "session57", "library57", "service57", "gateway57"],
    ),
    (
        ("token57 prompt57 session57 library57 service57 gateway57", 28),
        ["token57 prompt57 session57", "library57 service57", "gateway57"],
    ),
    (
        ("prompt57 session57 library57 service57 gateway57 storage57", 6),
        ["prompt57", "session57", "library57", "service57", "gateway57", "storage57"],
    ),
    (
        ("prompt57 session57 library57 service57 gateway57 storage57", 10),
        ["prompt57", "session57", "library57", "service57", "gateway57", "storage57"],
    ),
    (
        ("prompt57 session57 library57 service57 gateway57 storage57", 18),
        ["prompt57 session57", "library57", "service57", "gateway57", "storage57"],
    ),
    (
        ("prompt57 session57 library57 service57 gateway57 storage57", 28),
        ["prompt57 session57 library57", "service57 gateway57", "storage57"],
    ),
    (
        ("session57 library57 service57 gateway57 storage57 network57", 6),
        ["session57", "library57", "service57", "gateway57", "storage57", "network57"],
    ),
    (
        ("session57 library57 service57 gateway57 storage57 network57", 10),
        ["session57", "library57", "service57", "gateway57", "storage57", "network57"],
    ),
    (
        ("session57 library57 service57 gateway57 storage57 network57", 18),
        ["session57", "library57", "service57", "gateway57", "storage57", "network57"],
    ),
    (
        ("session57 library57 service57 gateway57 storage57 network57", 28),
        ["session57 library57", "service57 gateway57", "storage57 network57"],
    ),
    (
        ("library57 service57 gateway57 storage57 network57 latency57", 6),
        ["library57", "service57", "gateway57", "storage57", "network57", "latency57"],
    ),
    (
        ("library57 service57 gateway57 storage57 network57 latency57", 10),
        ["library57", "service57", "gateway57", "storage57", "network57", "latency57"],
    ),
    (
        ("library57 service57 gateway57 storage57 network57 latency57", 18),
        ["library57", "service57", "gateway57", "storage57", "network57", "latency57"],
    ),
    (
        ("library57 service57 gateway57 storage57 network57 latency57", 28),
        ["library57 service57", "gateway57 storage57", "network57 latency57"],
    ),
    (
        ("service57 gateway57 storage57 network57 latency57 buffer57", 6),
        ["service57", "gateway57", "storage57", "network57", "latency57", "buffer57"],
    ),
    (
        ("service57 gateway57 storage57 network57 latency57 buffer57", 10),
        ["service57", "gateway57", "storage57", "network57", "latency57", "buffer57"],
    ),
    (
        ("service57 gateway57 storage57 network57 latency57 buffer57", 18),
        ["service57", "gateway57", "storage57", "network57", "latency57 buffer57"],
    ),
    (
        ("service57 gateway57 storage57 network57 latency57 buffer57", 28),
        ["service57 gateway57", "storage57 network57", "latency57 buffer57"],
    ),
    (
        ("gateway57 storage57 network57 latency57 buffer57 queue57", 6),
        ["gateway57", "storage57", "network57", "latency57", "buffer57", "queue57"],
    ),
    (
        ("gateway57 storage57 network57 latency57 buffer57 queue57", 10),
        ["gateway57", "storage57", "network57", "latency57", "buffer57", "queue57"],
    ),
    (
        ("gateway57 storage57 network57 latency57 buffer57 queue57", 18),
        ["gateway57", "storage57", "network57", "latency57 buffer57", "queue57"],
    ),
    (
        ("gateway57 storage57 network57 latency57 buffer57 queue57", 28),
        ["gateway57 storage57", "network57 latency57 buffer57", "queue57"],
    ),
    (
        ("storage57 network57 latency57 buffer57 queue57 worker57", 6),
        ["storage57", "network57", "latency57", "buffer57", "queue57", "worker57"],
    ),
    (
        ("storage57 network57 latency57 buffer57 queue57 worker57", 10),
        ["storage57", "network57", "latency57", "buffer57", "queue57", "worker57"],
    ),
    (
        ("storage57 network57 latency57 buffer57 queue57 worker57", 18),
        ["storage57", "network57", "latency57 buffer57", "queue57 worker57"],
    ),
    (
        ("storage57 network57 latency57 buffer57 queue57 worker57", 28),
        ["storage57 network57", "latency57 buffer57 queue57", "worker57"],
    ),
    (
        ("network57 latency57 buffer57 queue57 worker57 kernel57", 6),
        ["network57", "latency57", "buffer57", "queue57", "worker57", "kernel57"],
    ),
    (
        ("network57 latency57 buffer57 queue57 worker57 kernel57", 10),
        ["network57", "latency57", "buffer57", "queue57", "worker57", "kernel57"],
    ),
    (
        ("network57 latency57 buffer57 queue57 worker57 kernel57", 18),
        ["network57", "latency57 buffer57", "queue57 worker57", "kernel57"],
    ),
    (
        ("network57 latency57 buffer57 queue57 worker57 kernel57", 28),
        ["network57 latency57 buffer57", "queue57 worker57 kernel57"],
    ),
    (
        ("latency57 buffer57 queue57 worker57 kernel57 signal57", 6),
        ["latency57", "buffer57", "queue57", "worker57", "kernel57", "signal57"],
    ),
    (
        ("latency57 buffer57 queue57 worker57 kernel57 signal57", 10),
        ["latency57", "buffer57", "queue57", "worker57", "kernel57", "signal57"],
    ),
    (
        ("latency57 buffer57 queue57 worker57 kernel57 signal57", 18),
        ["latency57 buffer57", "queue57 worker57", "kernel57 signal57"],
    ),
    (
        ("latency57 buffer57 queue57 worker57 kernel57 signal57", 28),
        ["latency57 buffer57 queue57", "worker57 kernel57 signal57"],
    ),
    (
        ("buffer57 queue57 worker57 kernel57 signal57 packet57", 6),
        ["buffer57", "queue57", "worker57", "kernel57", "signal57", "packet57"],
    ),
    (
        ("buffer57 queue57 worker57 kernel57 signal57 packet57", 10),
        ["buffer57", "queue57", "worker57", "kernel57", "signal57", "packet57"],
    ),
    (
        ("buffer57 queue57 worker57 kernel57 signal57 packet57", 18),
        ["buffer57 queue57", "worker57 kernel57", "signal57 packet57"],
    ),
    (
        ("buffer57 queue57 worker57 kernel57 signal57 packet57", 28),
        ["buffer57 queue57 worker57", "kernel57 signal57 packet57"],
    ),
    (
        ("queue57 worker57 kernel57 signal57 packet57 router57", 6),
        ["queue57", "worker57", "kernel57", "signal57", "packet57", "router57"],
    ),
    (
        ("queue57 worker57 kernel57 signal57 packet57 router57", 10),
        ["queue57", "worker57", "kernel57", "signal57", "packet57", "router57"],
    ),
    (
        ("queue57 worker57 kernel57 signal57 packet57 router57", 18),
        ["queue57 worker57", "kernel57 signal57", "packet57 router57"],
    ),
    (
        ("queue57 worker57 kernel57 signal57 packet57 router57", 28),
        ["queue57 worker57 kernel57", "signal57 packet57 router57"],
    ),
    (
        ("worker57 kernel57 signal57 packet57 router57 cluster57", 6),
        ["worker57", "kernel57", "signal57", "packet57", "router57", "cluster57"],
    ),
    (
        ("worker57 kernel57 signal57 packet57 router57 cluster57", 10),
        ["worker57", "kernel57", "signal57", "packet57", "router57", "cluster57"],
    ),
    (
        ("worker57 kernel57 signal57 packet57 router57 cluster57", 18),
        ["worker57 kernel57", "signal57 packet57", "router57 cluster57"],
    ),
    (
        ("worker57 kernel57 signal57 packet57 router57 cluster57", 28),
        ["worker57 kernel57 signal57", "packet57 router57 cluster57"],
    ),
    (
        ("kernel57 signal57 packet57 router57 cluster57 mirror57", 6),
        ["kernel57", "signal57", "packet57", "router57", "cluster57", "mirror57"],
    ),
    (
        ("kernel57 signal57 packet57 router57 cluster57 mirror57", 10),
        ["kernel57", "signal57", "packet57", "router57", "cluster57", "mirror57"],
    ),
    (
        ("kernel57 signal57 packet57 router57 cluster57 mirror57", 18),
        ["kernel57 signal57", "packet57 router57", "cluster57 mirror57"],
    ),
    (
        ("kernel57 signal57 packet57 router57 cluster57 mirror57", 28),
        ["kernel57 signal57 packet57", "router57 cluster57 mirror57"],
    ),
    (
        ("signal57 packet57 router57 cluster57 mirror57 filter57", 6),
        ["signal57", "packet57", "router57", "cluster57", "mirror57", "filter57"],
    ),
    (
        ("signal57 packet57 router57 cluster57 mirror57 filter57", 10),
        ["signal57", "packet57", "router57", "cluster57", "mirror57", "filter57"],
    ),
    (
        ("signal57 packet57 router57 cluster57 mirror57 filter57", 18),
        ["signal57 packet57", "router57 cluster57", "mirror57 filter57"],
    ),
    (
        ("signal57 packet57 router57 cluster57 mirror57 filter57", 28),
        ["signal57 packet57 router57", "cluster57 mirror57 filter57"],
    ),
    (
        ("packet57 router57 cluster57 mirror57 filter57 ranking57", 6),
        ["packet57", "router57", "cluster57", "mirror57", "filter57", "ranking57"],
    ),
    (
        ("packet57 router57 cluster57 mirror57 filter57 ranking57", 10),
        ["packet57", "router57", "cluster57", "mirror57", "filter57", "ranking57"],
    ),
    (
        ("packet57 router57 cluster57 mirror57 filter57 ranking57", 18),
        ["packet57 router57", "cluster57 mirror57", "filter57 ranking57"],
    ),
    (
        ("packet57 router57 cluster57 mirror57 filter57 ranking57", 28),
        ["packet57 router57 cluster57", "mirror57 filter57 ranking57"],
    ),
    (
        ("router57 cluster57 mirror57 filter57 ranking57 encoding57", 6),
        ["router57", "cluster57", "mirror57", "filter57", "ranking57", "encoding57"],
    ),
    (
        ("router57 cluster57 mirror57 filter57 ranking57 encoding57", 10),
        ["router57", "cluster57", "mirror57", "filter57", "ranking57", "encoding57"],
    ),
    (
        ("router57 cluster57 mirror57 filter57 ranking57 encoding57", 18),
        ["router57 cluster57", "mirror57 filter57", "ranking57", "encoding57"],
    ),
    (
        ("router57 cluster57 mirror57 filter57 ranking57 encoding57", 28),
        ["router57 cluster57 mirror57", "filter57 ranking57", "encoding57"],
    ),
    (
        ("cluster57 mirror57 filter57 ranking57 encoding57 mapping57", 6),
        ["cluster57", "mirror57", "filter57", "ranking57", "encoding57", "mapping57"],
    ),
    (
        ("cluster57 mirror57 filter57 ranking57 encoding57 mapping57", 10),
        ["cluster57", "mirror57", "filter57", "ranking57", "encoding57", "mapping57"],
    ),
    (
        ("cluster57 mirror57 filter57 ranking57 encoding57 mapping57", 18),
        ["cluster57 mirror57", "filter57 ranking57", "encoding57", "mapping57"],
    ),
    (
        ("cluster57 mirror57 filter57 ranking57 encoding57 mapping57", 28),
        ["cluster57 mirror57 filter57", "ranking57 encoding57", "mapping57"],
    ),
    (
        ("mirror57 filter57 ranking57 encoding57 mapping57 record57", 6),
        ["mirror57", "filter57", "ranking57", "encoding57", "mapping57", "record57"],
    ),
    (
        ("mirror57 filter57 ranking57 encoding57 mapping57 record57", 10),
        ["mirror57", "filter57", "ranking57", "encoding57", "mapping57", "record57"],
    ),
    (
        ("mirror57 filter57 ranking57 encoding57 mapping57 record57", 18),
        ["mirror57 filter57", "ranking57", "encoding57", "mapping57 record57"],
    ),
    (
        ("mirror57 filter57 ranking57 encoding57 mapping57 record57", 28),
        ["mirror57 filter57 ranking57", "encoding57 mapping57", "record57"],
    ),
    (
        ("filter57 ranking57 encoding57 mapping57 record57 candle57", 6),
        ["filter57", "ranking57", "encoding57", "mapping57", "record57", "candle57"],
    ),
    (
        ("filter57 ranking57 encoding57 mapping57 record57 candle57", 10),
        ["filter57", "ranking57", "encoding57", "mapping57", "record57", "candle57"],
    ),
    (
        ("filter57 ranking57 encoding57 mapping57 record57 candle57", 18),
        ["filter57 ranking57", "encoding57", "mapping57 record57", "candle57"],
    ),
    (
        ("filter57 ranking57 encoding57 mapping57 record57 candle57", 28),
        ["filter57 ranking57", "encoding57 mapping57", "record57 candle57"],
    ),
    (
        ("ranking57 encoding57 mapping57 record57 candle57 thread57", 6),
        ["ranking57", "encoding57", "mapping57", "record57", "candle57", "thread57"],
    ),
    (
        ("ranking57 encoding57 mapping57 record57 candle57 thread57", 10),
        ["ranking57", "encoding57", "mapping57", "record57", "candle57", "thread57"],
    ),
    (
        ("ranking57 encoding57 mapping57 record57 candle57 thread57", 18),
        ["ranking57", "encoding57", "mapping57 record57", "candle57 thread57"],
    ),
    (
        ("ranking57 encoding57 mapping57 record57 candle57 thread57", 28),
        ["ranking57 encoding57", "mapping57 record57 candle57", "thread57"],
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
