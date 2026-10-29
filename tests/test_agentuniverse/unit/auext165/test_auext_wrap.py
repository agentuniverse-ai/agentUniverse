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
        ("round 165: the quick brown fox jumps over the lazy dog", 4),
        ["round", "165:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", 8),
        ["round", "165: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", 12),
        ["round 165:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", 16),
        ["round 165: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", 24),
        ["round 165: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 165: the quick brown fox jumps over the lazy dog", 32),
        ["round 165: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", 4),
        ["round", "165:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", 8),
        ["round", "165:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", 12),
        ["round 165:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", 16),
        ["round 165:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", 24),
        ["round 165: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 165: agentuniverse is a framework for multi agents", 32),
        ["round 165: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", 4),
        ["round", "165:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", 8),
        ["round", "165:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", 12),
        ["round 165:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", 16),
        ["round 165:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", 24),
        ["round 165: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 165: knowledge stored as vectors enables retrieval", 32),
        ["round 165: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 165: the processor reads the record then stops", 4),
        ["round", "165:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 165: the processor reads the record then stops", 8),
        ["round", "165: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 165: the processor reads the record then stops", 12),
        ["round 165:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 165: the processor reads the record then stops", 16),
        ["round 165: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 165: the processor reads the record then stops", 24),
        ["round 165: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 165: the processor reads the record then stops", 32),
        ["round 165: the processor reads", "the record then stops"],
    ),
    (
        ("round 165: a worker pulls the next task from the queue", 4),
        ["round", "165:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 165: a worker pulls the next task from the queue", 8),
        ["round", "165: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 165: a worker pulls the next task from the queue", 12),
        ["round 165: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 165: a worker pulls the next task from the queue", 16),
        ["round 165: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 165: a worker pulls the next task from the queue", 24),
        ["round 165: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 165: a worker pulls the next task from the queue", 32),
        ["round 165: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 165: signals travel through the network layer", 4),
        ["round", "165:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 165: signals travel through the network layer", 8),
        ["round", "165:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 165: signals travel through the network layer", 12),
        ["round 165:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 165: signals travel through the network layer", 16),
        ["round 165:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 165: signals travel through the network layer", 24),
        ["round 165: signals", "travel through the", "network layer"],
    ),
    (
        ("round 165: signals travel through the network layer", 32),
        ["round 165: signals travel", "through the network layer"],
    ),
    (
        ("round 165: the gateway routes each request by policy", 4),
        ["round", "165:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 165: the gateway routes each request by policy", 8),
        ["round", "165: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 165: the gateway routes each request by policy", 12),
        ["round 165:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 165: the gateway routes each request by policy", 16),
        ["round 165: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 165: the gateway routes each request by policy", 24),
        ["round 165: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 165: the gateway routes each request by policy", 32),
        ["round 165: the gateway routes", "each request by policy"],
    ),
    (
        ("round 165: memory grows until the buffer is full", 4),
        ["round", "165:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 165: memory grows until the buffer is full", 8),
        ["round", "165:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 165: memory grows until the buffer is full", 12),
        ["round 165:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 165: memory grows until the buffer is full", 16),
        ["round 165:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 165: memory grows until the buffer is full", 24), ["round 165: memory grows", "until the buffer is full"]),
    (("round 165: memory grows until the buffer is full", 32), ["round 165: memory grows until", "the buffer is full"]),
    (
        ("round 165: the cluster mirrors every packet twice", 4),
        ["round", "165:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 165: the cluster mirrors every packet twice", 8),
        ["round", "165: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 165: the cluster mirrors every packet twice", 12),
        ["round 165:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 165: the cluster mirrors every packet twice", 16),
        ["round 165: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 165: the cluster mirrors every packet twice", 24),
        ["round 165: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 165: the cluster mirrors every packet twice", 32),
        ["round 165: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", 4),
        ["round", "165:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", 8),
        ["round", "165:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", 12),
        ["round 165:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", 16),
        ["round 165:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", 24),
        ["round 165: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 165: ranking uses tokens learned from the corpus", 32),
        ["round 165: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 165: a long session ends when the candle dies", 4),
        ["round", "165:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 165: a long session ends when the candle dies", 8),
        ["round", "165: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 165: a long session ends when the candle dies", 12),
        ["round 165: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 165: a long session ends when the candle dies", 16),
        ["round 165: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 165: a long session ends when the candle dies", 24),
        ["round 165: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 165: a long session ends when the candle dies", 32),
        ["round 165: a long session ends", "when the candle dies"],
    ),
    (
        ("round 165: encode the prompt then map the result", 4),
        ["round", "165:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 165: encode the prompt then map the result", 8),
        ["round", "165:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 165: encode the prompt then map the result", 12),
        ["round 165:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 165: encode the prompt then map the result", 16),
        ["round 165:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 165: encode the prompt then map the result", 24),
        ["round 165: encode the", "prompt then map the", "result"],
    ),
    (("round 165: encode the prompt then map the result", 32), ["round 165: encode the prompt", "then map the result"]),
    (
        ("round 165: the kernel wakes the worker at dawn", 4),
        ["round", "165:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 165: the kernel wakes the worker at dawn", 8),
        ["round", "165: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 165: the kernel wakes the worker at dawn", 12),
        ["round 165:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 165: the kernel wakes the worker at dawn", 16), ["round 165: the", "kernel wakes the", "worker at dawn"]),
    (("round 165: the kernel wakes the worker at dawn", 24), ["round 165: the kernel", "wakes the worker at dawn"]),
    (("round 165: the kernel wakes the worker at dawn", 32), ["round 165: the kernel wakes the", "worker at dawn"]),
    (
        ("round 165: service latency drops after the patch", 4),
        ["round", "165:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 165: service latency drops after the patch", 8),
        ["round", "165:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 165: service latency drops after the patch", 12),
        ["round 165:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 165: service latency drops after the patch", 16),
        ["round 165:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 165: service latency drops after the patch", 24),
        ["round 165: service", "latency drops after the", "patch"],
    ),
    (("round 165: service latency drops after the patch", 32), ["round 165: service latency drops", "after the patch"]),
    (
        ("round 165: the library caches every vector it sees", 4),
        ["round", "165:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 165: the library caches every vector it sees", 8),
        ["round", "165: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 165: the library caches every vector it sees", 12),
        ["round 165:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 165: the library caches every vector it sees", 16),
        ["round 165: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 165: the library caches every vector it sees", 24),
        ["round 165: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 165: the library caches every vector it sees", 32),
        ["round 165: the library caches", "every vector it sees"],
    ),
    (
        ("round 165: agents argue then the debate resolves", 4),
        ["round", "165:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 165: agents argue then the debate resolves", 8),
        ["round", "165:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 165: agents argue then the debate resolves", 12),
        ["round 165:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 165: agents argue then the debate resolves", 16),
        ["round 165:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 165: agents argue then the debate resolves", 24), ["round 165: agents argue", "then the debate resolves"]),
    (("round 165: agents argue then the debate resolves", 32), ["round 165: agents argue then the", "debate resolves"]),
    (
        ("round 165: the filter keeps only strong matches", 4),
        ["round", "165:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 165: the filter keeps only strong matches", 8),
        ["round", "165: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 165: the filter keeps only strong matches", 12),
        ["round 165:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 165: the filter keeps only strong matches", 16),
        ["round 165: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 165: the filter keeps only strong matches", 24),
        ["round 165: the filter", "keeps only strong", "matches"],
    ),
    (("round 165: the filter keeps only strong matches", 32), ["round 165: the filter keeps only", "strong matches"]),
    (
        ("round 165: the model answers with a short reply", 4),
        ["round", "165:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 165: the model answers with a short reply", 8),
        ["round", "165: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 165: the model answers with a short reply", 12),
        ["round 165:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 165: the model answers with a short reply", 16),
        ["round 165: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 165: the model answers with a short reply", 24),
        ["round 165: the model", "answers with a short", "reply"],
    ),
    (("round 165: the model answers with a short reply", 32), ["round 165: the model answers", "with a short reply"]),
    (
        ("round 165: the recorder stores the reasoning trace", 4),
        ["round", "165:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 165: the recorder stores the reasoning trace", 8),
        ["round", "165: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 165: the recorder stores the reasoning trace", 12),
        ["round 165:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 165: the recorder stores the reasoning trace", 16),
        ["round 165: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 165: the recorder stores the reasoning trace", 24),
        ["round 165: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 165: the recorder stores the reasoning trace", 32),
        ["round 165: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 165: the angel watches the processor run", 4),
        ["round", "165:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 165: the angel watches the processor run", 8),
        ["round", "165: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 165: the angel watches the processor run", 12),
        ["round 165:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 165: the angel watches the processor run", 16),
        ["round 165: the", "angel watches", "the processor", "run"],
    ),
    (("round 165: the angel watches the processor run", 24), ["round 165: the angel", "watches the processor", "run"]),
    (("round 165: the angel watches the processor run", 32), ["round 165: the angel watches the", "processor run"]),
    (
        ("round 165: angle of the vector decides the match", 4),
        ["round", "165:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 165: angle of the vector decides the match", 8),
        ["round", "165:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 165: angle of the vector decides the match", 12),
        ["round 165:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 165: angle of the vector decides the match", 16),
        ["round 165: angle", "of the vector", "decides the", "match"],
    ),
    (("round 165: angle of the vector decides the match", 24), ["round 165: angle of the", "vector decides the match"]),
    (("round 165: angle of the vector decides the match", 32), ["round 165: angle of the vector", "decides the match"]),
    (
        ("round 165: the candle burns twice as long at night", 4),
        ["round", "165:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 165: the candle burns twice as long at night", 8),
        ["round", "165: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 165: the candle burns twice as long at night", 12),
        ["round 165:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 165: the candle burns twice as long at night", 16),
        ["round 165: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 165: the candle burns twice as long at night", 24),
        ["round 165: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 165: the candle burns twice as long at night", 32),
        ["round 165: the candle burns", "twice as long at night"],
    ),
    (
        ("round 165: a mirror of the universe in one line", 4),
        ["round", "165:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 165: a mirror of the universe in one line", 8),
        ["round", "165: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 165: a mirror of the universe in one line", 12),
        ["round 165: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 165: a mirror of the universe in one line", 16),
        ["round 165: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 165: a mirror of the universe in one line", 24), ["round 165: a mirror of", "the universe in one line"]),
    (("round 165: a mirror of the universe in one line", 32), ["round 165: a mirror of the", "universe in one line"]),
    (
        ("round 165: the queue drains before the storm", 4),
        ["round", "165:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 165: the queue drains before the storm", 8),
        ["round", "165: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 165: the queue drains before the storm", 12),
        ["round 165:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 165: the queue drains before the storm", 16), ["round 165: the", "queue drains", "before the storm"]),
    (("round 165: the queue drains before the storm", 24), ["round 165: the queue", "drains before the storm"]),
    (("round 165: the queue drains before the storm", 32), ["round 165: the queue drains", "before the storm"]),
    (
        ("kitten165 sitting165 agent165 angle165 universe165 memory165", 6),
        ["kitten165", "sitting165", "agent165", "angle165", "universe165", "memory165"],
    ),
    (
        ("kitten165 sitting165 agent165 angle165 universe165 memory165", 10),
        ["kitten165", "sitting165", "agent165", "angle165", "universe165", "memory165"],
    ),
    (
        ("kitten165 sitting165 agent165 angle165 universe165 memory165", 18),
        ["kitten165", "sitting165", "agent165 angle165", "universe165", "memory165"],
    ),
    (
        ("kitten165 sitting165 agent165 angle165 universe165 memory165", 28),
        ["kitten165 sitting165", "agent165 angle165", "universe165 memory165"],
    ),
    (
        ("sitting165 agent165 angle165 universe165 memory165 stream165", 6),
        ["sitting165", "agent165", "angle165", "universe165", "memory165", "stream165"],
    ),
    (
        ("sitting165 agent165 angle165 universe165 memory165 stream165", 10),
        ["sitting165", "agent165", "angle165", "universe165", "memory165", "stream165"],
    ),
    (
        ("sitting165 agent165 angle165 universe165 memory165 stream165", 18),
        ["sitting165", "agent165 angle165", "universe165", "memory165", "stream165"],
    ),
    (
        ("sitting165 agent165 angle165 universe165 memory165 stream165", 28),
        ["sitting165 agent165 angle165", "universe165 memory165", "stream165"],
    ),
    (
        ("agent165 angle165 universe165 memory165 stream165 context165", 6),
        ["agent165", "angle165", "universe165", "memory165", "stream165", "context165"],
    ),
    (
        ("agent165 angle165 universe165 memory165 stream165 context165", 10),
        ["agent165", "angle165", "universe165", "memory165", "stream165", "context165"],
    ),
    (
        ("agent165 angle165 universe165 memory165 stream165 context165", 18),
        ["agent165 angle165", "universe165", "memory165", "stream165", "context165"],
    ),
    (
        ("agent165 angle165 universe165 memory165 stream165 context165", 28),
        ["agent165 angle165", "universe165 memory165", "stream165 context165"],
    ),
    (
        ("angle165 universe165 memory165 stream165 context165 knowledge165", 6),
        ["angle165", "universe165", "memory165", "stream165", "context165", "knowledge165"],
    ),
    (
        ("angle165 universe165 memory165 stream165 context165 knowledge165", 10),
        ["angle165", "universe165", "memory165", "stream165", "context165", "knowledge165"],
    ),
    (
        ("angle165 universe165 memory165 stream165 context165 knowledge165", 18),
        ["angle165", "universe165", "memory165", "stream165", "context165", "knowledge165"],
    ),
    (
        ("angle165 universe165 memory165 stream165 context165 knowledge165", 28),
        ["angle165 universe165", "memory165 stream165", "context165 knowledge165"],
    ),
    (
        ("universe165 memory165 stream165 context165 knowledge165 vector165", 6),
        ["universe165", "memory165", "stream165", "context165", "knowledge165", "vector165"],
    ),
    (
        ("universe165 memory165 stream165 context165 knowledge165 vector165", 10),
        ["universe165", "memory165", "stream165", "context165", "knowledge165", "vector165"],
    ),
    (
        ("universe165 memory165 stream165 context165 knowledge165 vector165", 18),
        ["universe165", "memory165", "stream165", "context165", "knowledge165", "vector165"],
    ),
    (
        ("universe165 memory165 stream165 context165 knowledge165 vector165", 28),
        ["universe165 memory165", "stream165 context165", "knowledge165 vector165"],
    ),
    (
        ("memory165 stream165 context165 knowledge165 vector165 processor165", 6),
        ["memory165", "stream165", "context165", "knowledge165", "vector165", "processor165"],
    ),
    (
        ("memory165 stream165 context165 knowledge165 vector165 processor165", 10),
        ["memory165", "stream165", "context165", "knowledge165", "vector165", "processor165"],
    ),
    (
        ("memory165 stream165 context165 knowledge165 vector165 processor165", 18),
        ["memory165", "stream165", "context165", "knowledge165", "vector165", "processor165"],
    ),
    (
        ("memory165 stream165 context165 knowledge165 vector165 processor165", 28),
        ["memory165 stream165", "context165 knowledge165", "vector165 processor165"],
    ),
    (
        ("stream165 context165 knowledge165 vector165 processor165 reasoning165", 6),
        ["stream165", "context165", "knowledge165", "vector165", "processor165", "reasoning165"],
    ),
    (
        ("stream165 context165 knowledge165 vector165 processor165 reasoning165", 10),
        ["stream165", "context165", "knowledge165", "vector165", "processor165", "reasoning165"],
    ),
    (
        ("stream165 context165 knowledge165 vector165 processor165 reasoning165", 18),
        ["stream165", "context165", "knowledge165", "vector165", "processor165", "reasoning165"],
    ),
    (
        ("stream165 context165 knowledge165 vector165 processor165 reasoning165", 28),
        ["stream165 context165", "knowledge165 vector165", "processor165 reasoning165"],
    ),
    (
        ("context165 knowledge165 vector165 processor165 reasoning165 machine165", 6),
        ["context165", "knowledge165", "vector165", "processor165", "reasoning165", "machine165"],
    ),
    (
        ("context165 knowledge165 vector165 processor165 reasoning165 machine165", 10),
        ["context165", "knowledge165", "vector165", "processor165", "reasoning165", "machine165"],
    ),
    (
        ("context165 knowledge165 vector165 processor165 reasoning165 machine165", 18),
        ["context165", "knowledge165", "vector165", "processor165", "reasoning165", "machine165"],
    ),
    (
        ("context165 knowledge165 vector165 processor165 reasoning165 machine165", 28),
        ["context165 knowledge165", "vector165 processor165", "reasoning165 machine165"],
    ),
    (
        ("knowledge165 vector165 processor165 reasoning165 machine165 learning165", 6),
        ["knowledge165", "vector165", "processor165", "reasoning165", "machine165", "learning165"],
    ),
    (
        ("knowledge165 vector165 processor165 reasoning165 machine165 learning165", 10),
        ["knowledge165", "vector165", "processor165", "reasoning165", "machine165", "learning165"],
    ),
    (
        ("knowledge165 vector165 processor165 reasoning165 machine165 learning165", 18),
        ["knowledge165", "vector165", "processor165", "reasoning165", "machine165", "learning165"],
    ),
    (
        ("knowledge165 vector165 processor165 reasoning165 machine165 learning165", 28),
        ["knowledge165 vector165", "processor165 reasoning165", "machine165 learning165"],
    ),
    (
        ("vector165 processor165 reasoning165 machine165 learning165 model165", 6),
        ["vector165", "processor165", "reasoning165", "machine165", "learning165", "model165"],
    ),
    (
        ("vector165 processor165 reasoning165 machine165 learning165 model165", 10),
        ["vector165", "processor165", "reasoning165", "machine165", "learning165", "model165"],
    ),
    (
        ("vector165 processor165 reasoning165 machine165 learning165 model165", 18),
        ["vector165", "processor165", "reasoning165", "machine165", "learning165", "model165"],
    ),
    (
        ("vector165 processor165 reasoning165 machine165 learning165 model165", 28),
        ["vector165 processor165", "reasoning165 machine165", "learning165 model165"],
    ),
    (
        ("processor165 reasoning165 machine165 learning165 model165 token165", 6),
        ["processor165", "reasoning165", "machine165", "learning165", "model165", "token165"],
    ),
    (
        ("processor165 reasoning165 machine165 learning165 model165 token165", 10),
        ["processor165", "reasoning165", "machine165", "learning165", "model165", "token165"],
    ),
    (
        ("processor165 reasoning165 machine165 learning165 model165 token165", 18),
        ["processor165", "reasoning165", "machine165", "learning165", "model165 token165"],
    ),
    (
        ("processor165 reasoning165 machine165 learning165 model165 token165", 28),
        ["processor165 reasoning165", "machine165 learning165", "model165 token165"],
    ),
    (
        ("reasoning165 machine165 learning165 model165 token165 prompt165", 6),
        ["reasoning165", "machine165", "learning165", "model165", "token165", "prompt165"],
    ),
    (
        ("reasoning165 machine165 learning165 model165 token165 prompt165", 10),
        ["reasoning165", "machine165", "learning165", "model165", "token165", "prompt165"],
    ),
    (
        ("reasoning165 machine165 learning165 model165 token165 prompt165", 18),
        ["reasoning165", "machine165", "learning165", "model165 token165", "prompt165"],
    ),
    (
        ("reasoning165 machine165 learning165 model165 token165 prompt165", 28),
        ["reasoning165 machine165", "learning165 model165", "token165 prompt165"],
    ),
    (
        ("machine165 learning165 model165 token165 prompt165 session165", 6),
        ["machine165", "learning165", "model165", "token165", "prompt165", "session165"],
    ),
    (
        ("machine165 learning165 model165 token165 prompt165 session165", 10),
        ["machine165", "learning165", "model165", "token165", "prompt165", "session165"],
    ),
    (
        ("machine165 learning165 model165 token165 prompt165 session165", 18),
        ["machine165", "learning165", "model165 token165", "prompt165", "session165"],
    ),
    (
        ("machine165 learning165 model165 token165 prompt165 session165", 28),
        ["machine165 learning165", "model165 token165 prompt165", "session165"],
    ),
    (
        ("learning165 model165 token165 prompt165 session165 library165", 6),
        ["learning165", "model165", "token165", "prompt165", "session165", "library165"],
    ),
    (
        ("learning165 model165 token165 prompt165 session165 library165", 10),
        ["learning165", "model165", "token165", "prompt165", "session165", "library165"],
    ),
    (
        ("learning165 model165 token165 prompt165 session165 library165", 18),
        ["learning165", "model165 token165", "prompt165", "session165", "library165"],
    ),
    (
        ("learning165 model165 token165 prompt165 session165 library165", 28),
        ["learning165 model165", "token165 prompt165", "session165 library165"],
    ),
    (
        ("model165 token165 prompt165 session165 library165 service165", 6),
        ["model165", "token165", "prompt165", "session165", "library165", "service165"],
    ),
    (
        ("model165 token165 prompt165 session165 library165 service165", 10),
        ["model165", "token165", "prompt165", "session165", "library165", "service165"],
    ),
    (
        ("model165 token165 prompt165 session165 library165 service165", 18),
        ["model165 token165", "prompt165", "session165", "library165", "service165"],
    ),
    (
        ("model165 token165 prompt165 session165 library165 service165", 28),
        ["model165 token165 prompt165", "session165 library165", "service165"],
    ),
    (
        ("token165 prompt165 session165 library165 service165 gateway165", 6),
        ["token165", "prompt165", "session165", "library165", "service165", "gateway165"],
    ),
    (
        ("token165 prompt165 session165 library165 service165 gateway165", 10),
        ["token165", "prompt165", "session165", "library165", "service165", "gateway165"],
    ),
    (
        ("token165 prompt165 session165 library165 service165 gateway165", 18),
        ["token165 prompt165", "session165", "library165", "service165", "gateway165"],
    ),
    (
        ("token165 prompt165 session165 library165 service165 gateway165", 28),
        ["token165 prompt165", "session165 library165", "service165 gateway165"],
    ),
    (
        ("prompt165 session165 library165 service165 gateway165 storage165", 6),
        ["prompt165", "session165", "library165", "service165", "gateway165", "storage165"],
    ),
    (
        ("prompt165 session165 library165 service165 gateway165 storage165", 10),
        ["prompt165", "session165", "library165", "service165", "gateway165", "storage165"],
    ),
    (
        ("prompt165 session165 library165 service165 gateway165 storage165", 18),
        ["prompt165", "session165", "library165", "service165", "gateway165", "storage165"],
    ),
    (
        ("prompt165 session165 library165 service165 gateway165 storage165", 28),
        ["prompt165 session165", "library165 service165", "gateway165 storage165"],
    ),
    (
        ("session165 library165 service165 gateway165 storage165 network165", 6),
        ["session165", "library165", "service165", "gateway165", "storage165", "network165"],
    ),
    (
        ("session165 library165 service165 gateway165 storage165 network165", 10),
        ["session165", "library165", "service165", "gateway165", "storage165", "network165"],
    ),
    (
        ("session165 library165 service165 gateway165 storage165 network165", 18),
        ["session165", "library165", "service165", "gateway165", "storage165", "network165"],
    ),
    (
        ("session165 library165 service165 gateway165 storage165 network165", 28),
        ["session165 library165", "service165 gateway165", "storage165 network165"],
    ),
    (
        ("library165 service165 gateway165 storage165 network165 latency165", 6),
        ["library165", "service165", "gateway165", "storage165", "network165", "latency165"],
    ),
    (
        ("library165 service165 gateway165 storage165 network165 latency165", 10),
        ["library165", "service165", "gateway165", "storage165", "network165", "latency165"],
    ),
    (
        ("library165 service165 gateway165 storage165 network165 latency165", 18),
        ["library165", "service165", "gateway165", "storage165", "network165", "latency165"],
    ),
    (
        ("library165 service165 gateway165 storage165 network165 latency165", 28),
        ["library165 service165", "gateway165 storage165", "network165 latency165"],
    ),
    (
        ("service165 gateway165 storage165 network165 latency165 buffer165", 6),
        ["service165", "gateway165", "storage165", "network165", "latency165", "buffer165"],
    ),
    (
        ("service165 gateway165 storage165 network165 latency165 buffer165", 10),
        ["service165", "gateway165", "storage165", "network165", "latency165", "buffer165"],
    ),
    (
        ("service165 gateway165 storage165 network165 latency165 buffer165", 18),
        ["service165", "gateway165", "storage165", "network165", "latency165", "buffer165"],
    ),
    (
        ("service165 gateway165 storage165 network165 latency165 buffer165", 28),
        ["service165 gateway165", "storage165 network165", "latency165 buffer165"],
    ),
    (
        ("gateway165 storage165 network165 latency165 buffer165 queue165", 6),
        ["gateway165", "storage165", "network165", "latency165", "buffer165", "queue165"],
    ),
    (
        ("gateway165 storage165 network165 latency165 buffer165 queue165", 10),
        ["gateway165", "storage165", "network165", "latency165", "buffer165", "queue165"],
    ),
    (
        ("gateway165 storage165 network165 latency165 buffer165 queue165", 18),
        ["gateway165", "storage165", "network165", "latency165", "buffer165 queue165"],
    ),
    (
        ("gateway165 storage165 network165 latency165 buffer165 queue165", 28),
        ["gateway165 storage165", "network165 latency165", "buffer165 queue165"],
    ),
    (
        ("storage165 network165 latency165 buffer165 queue165 worker165", 6),
        ["storage165", "network165", "latency165", "buffer165", "queue165", "worker165"],
    ),
    (
        ("storage165 network165 latency165 buffer165 queue165 worker165", 10),
        ["storage165", "network165", "latency165", "buffer165", "queue165", "worker165"],
    ),
    (
        ("storage165 network165 latency165 buffer165 queue165 worker165", 18),
        ["storage165", "network165", "latency165", "buffer165 queue165", "worker165"],
    ),
    (
        ("storage165 network165 latency165 buffer165 queue165 worker165", 28),
        ["storage165 network165", "latency165 buffer165", "queue165 worker165"],
    ),
    (
        ("network165 latency165 buffer165 queue165 worker165 kernel165", 6),
        ["network165", "latency165", "buffer165", "queue165", "worker165", "kernel165"],
    ),
    (
        ("network165 latency165 buffer165 queue165 worker165 kernel165", 10),
        ["network165", "latency165", "buffer165", "queue165", "worker165", "kernel165"],
    ),
    (
        ("network165 latency165 buffer165 queue165 worker165 kernel165", 18),
        ["network165", "latency165", "buffer165 queue165", "worker165", "kernel165"],
    ),
    (
        ("network165 latency165 buffer165 queue165 worker165 kernel165", 28),
        ["network165 latency165", "buffer165 queue165 worker165", "kernel165"],
    ),
    (
        ("latency165 buffer165 queue165 worker165 kernel165 signal165", 6),
        ["latency165", "buffer165", "queue165", "worker165", "kernel165", "signal165"],
    ),
    (
        ("latency165 buffer165 queue165 worker165 kernel165 signal165", 10),
        ["latency165", "buffer165", "queue165", "worker165", "kernel165", "signal165"],
    ),
    (
        ("latency165 buffer165 queue165 worker165 kernel165 signal165", 18),
        ["latency165", "buffer165 queue165", "worker165", "kernel165", "signal165"],
    ),
    (
        ("latency165 buffer165 queue165 worker165 kernel165 signal165", 28),
        ["latency165 buffer165", "queue165 worker165 kernel165", "signal165"],
    ),
    (
        ("buffer165 queue165 worker165 kernel165 signal165 packet165", 6),
        ["buffer165", "queue165", "worker165", "kernel165", "signal165", "packet165"],
    ),
    (
        ("buffer165 queue165 worker165 kernel165 signal165 packet165", 10),
        ["buffer165", "queue165", "worker165", "kernel165", "signal165", "packet165"],
    ),
    (
        ("buffer165 queue165 worker165 kernel165 signal165 packet165", 18),
        ["buffer165 queue165", "worker165", "kernel165", "signal165", "packet165"],
    ),
    (
        ("buffer165 queue165 worker165 kernel165 signal165 packet165", 28),
        ["buffer165 queue165 worker165", "kernel165 signal165", "packet165"],
    ),
    (
        ("queue165 worker165 kernel165 signal165 packet165 router165", 6),
        ["queue165", "worker165", "kernel165", "signal165", "packet165", "router165"],
    ),
    (
        ("queue165 worker165 kernel165 signal165 packet165 router165", 10),
        ["queue165", "worker165", "kernel165", "signal165", "packet165", "router165"],
    ),
    (
        ("queue165 worker165 kernel165 signal165 packet165 router165", 18),
        ["queue165 worker165", "kernel165", "signal165", "packet165", "router165"],
    ),
    (
        ("queue165 worker165 kernel165 signal165 packet165 router165", 28),
        ["queue165 worker165 kernel165", "signal165 packet165", "router165"],
    ),
    (
        ("worker165 kernel165 signal165 packet165 router165 cluster165", 6),
        ["worker165", "kernel165", "signal165", "packet165", "router165", "cluster165"],
    ),
    (
        ("worker165 kernel165 signal165 packet165 router165 cluster165", 10),
        ["worker165", "kernel165", "signal165", "packet165", "router165", "cluster165"],
    ),
    (
        ("worker165 kernel165 signal165 packet165 router165 cluster165", 18),
        ["worker165", "kernel165", "signal165", "packet165", "router165", "cluster165"],
    ),
    (
        ("worker165 kernel165 signal165 packet165 router165 cluster165", 28),
        ["worker165 kernel165", "signal165 packet165", "router165 cluster165"],
    ),
    (
        ("kernel165 signal165 packet165 router165 cluster165 mirror165", 6),
        ["kernel165", "signal165", "packet165", "router165", "cluster165", "mirror165"],
    ),
    (
        ("kernel165 signal165 packet165 router165 cluster165 mirror165", 10),
        ["kernel165", "signal165", "packet165", "router165", "cluster165", "mirror165"],
    ),
    (
        ("kernel165 signal165 packet165 router165 cluster165 mirror165", 18),
        ["kernel165", "signal165", "packet165", "router165", "cluster165", "mirror165"],
    ),
    (
        ("kernel165 signal165 packet165 router165 cluster165 mirror165", 28),
        ["kernel165 signal165", "packet165 router165", "cluster165 mirror165"],
    ),
    (
        ("signal165 packet165 router165 cluster165 mirror165 filter165", 6),
        ["signal165", "packet165", "router165", "cluster165", "mirror165", "filter165"],
    ),
    (
        ("signal165 packet165 router165 cluster165 mirror165 filter165", 10),
        ["signal165", "packet165", "router165", "cluster165", "mirror165", "filter165"],
    ),
    (
        ("signal165 packet165 router165 cluster165 mirror165 filter165", 18),
        ["signal165", "packet165", "router165", "cluster165", "mirror165", "filter165"],
    ),
    (
        ("signal165 packet165 router165 cluster165 mirror165 filter165", 28),
        ["signal165 packet165", "router165 cluster165", "mirror165 filter165"],
    ),
    (
        ("packet165 router165 cluster165 mirror165 filter165 ranking165", 6),
        ["packet165", "router165", "cluster165", "mirror165", "filter165", "ranking165"],
    ),
    (
        ("packet165 router165 cluster165 mirror165 filter165 ranking165", 10),
        ["packet165", "router165", "cluster165", "mirror165", "filter165", "ranking165"],
    ),
    (
        ("packet165 router165 cluster165 mirror165 filter165 ranking165", 18),
        ["packet165", "router165", "cluster165", "mirror165", "filter165", "ranking165"],
    ),
    (
        ("packet165 router165 cluster165 mirror165 filter165 ranking165", 28),
        ["packet165 router165", "cluster165 mirror165", "filter165 ranking165"],
    ),
    (
        ("router165 cluster165 mirror165 filter165 ranking165 encoding165", 6),
        ["router165", "cluster165", "mirror165", "filter165", "ranking165", "encoding165"],
    ),
    (
        ("router165 cluster165 mirror165 filter165 ranking165 encoding165", 10),
        ["router165", "cluster165", "mirror165", "filter165", "ranking165", "encoding165"],
    ),
    (
        ("router165 cluster165 mirror165 filter165 ranking165 encoding165", 18),
        ["router165", "cluster165", "mirror165", "filter165", "ranking165", "encoding165"],
    ),
    (
        ("router165 cluster165 mirror165 filter165 ranking165 encoding165", 28),
        ["router165 cluster165", "mirror165 filter165", "ranking165 encoding165"],
    ),
    (
        ("cluster165 mirror165 filter165 ranking165 encoding165 mapping165", 6),
        ["cluster165", "mirror165", "filter165", "ranking165", "encoding165", "mapping165"],
    ),
    (
        ("cluster165 mirror165 filter165 ranking165 encoding165 mapping165", 10),
        ["cluster165", "mirror165", "filter165", "ranking165", "encoding165", "mapping165"],
    ),
    (
        ("cluster165 mirror165 filter165 ranking165 encoding165 mapping165", 18),
        ["cluster165", "mirror165", "filter165", "ranking165", "encoding165", "mapping165"],
    ),
    (
        ("cluster165 mirror165 filter165 ranking165 encoding165 mapping165", 28),
        ["cluster165 mirror165", "filter165 ranking165", "encoding165 mapping165"],
    ),
    (
        ("mirror165 filter165 ranking165 encoding165 mapping165 record165", 6),
        ["mirror165", "filter165", "ranking165", "encoding165", "mapping165", "record165"],
    ),
    (
        ("mirror165 filter165 ranking165 encoding165 mapping165 record165", 10),
        ["mirror165", "filter165", "ranking165", "encoding165", "mapping165", "record165"],
    ),
    (
        ("mirror165 filter165 ranking165 encoding165 mapping165 record165", 18),
        ["mirror165", "filter165", "ranking165", "encoding165", "mapping165", "record165"],
    ),
    (
        ("mirror165 filter165 ranking165 encoding165 mapping165 record165", 28),
        ["mirror165 filter165", "ranking165 encoding165", "mapping165 record165"],
    ),
    (
        ("filter165 ranking165 encoding165 mapping165 record165 candle165", 6),
        ["filter165", "ranking165", "encoding165", "mapping165", "record165", "candle165"],
    ),
    (
        ("filter165 ranking165 encoding165 mapping165 record165 candle165", 10),
        ["filter165", "ranking165", "encoding165", "mapping165", "record165", "candle165"],
    ),
    (
        ("filter165 ranking165 encoding165 mapping165 record165 candle165", 18),
        ["filter165", "ranking165", "encoding165", "mapping165", "record165", "candle165"],
    ),
    (
        ("filter165 ranking165 encoding165 mapping165 record165 candle165", 28),
        ["filter165 ranking165", "encoding165 mapping165", "record165 candle165"],
    ),
    (
        ("ranking165 encoding165 mapping165 record165 candle165 thread165", 6),
        ["ranking165", "encoding165", "mapping165", "record165", "candle165", "thread165"],
    ),
    (
        ("ranking165 encoding165 mapping165 record165 candle165 thread165", 10),
        ["ranking165", "encoding165", "mapping165", "record165", "candle165", "thread165"],
    ),
    (
        ("ranking165 encoding165 mapping165 record165 candle165 thread165", 18),
        ["ranking165", "encoding165", "mapping165", "record165", "candle165", "thread165"],
    ),
    (
        ("ranking165 encoding165 mapping165 record165 candle165 thread165", 28),
        ["ranking165 encoding165", "mapping165 record165", "candle165 thread165"],
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
