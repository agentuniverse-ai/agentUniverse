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
        ("round 76: the quick brown fox jumps over the lazy dog", 4),
        ["round", "76:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 76: the quick brown fox jumps over the lazy dog", 8),
        ["round", "76: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 76: the quick brown fox jumps over the lazy dog", 12),
        ["round 76:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 76: the quick brown fox jumps over the lazy dog", 16),
        ["round 76: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 76: the quick brown fox jumps over the lazy dog", 24),
        ["round 76: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 76: the quick brown fox jumps over the lazy dog", 32),
        ["round 76: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 76: agentuniverse is a framework for multi agents", 4),
        ["round", "76:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 76: agentuniverse is a framework for multi agents", 8),
        ["round", "76:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 76: agentuniverse is a framework for multi agents", 12),
        ["round 76:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 76: agentuniverse is a framework for multi agents", 16),
        ["round 76:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 76: agentuniverse is a framework for multi agents", 24),
        ["round 76: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 76: agentuniverse is a framework for multi agents", 32),
        ["round 76: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 76: knowledge stored as vectors enables retrieval", 4),
        ["round", "76:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 76: knowledge stored as vectors enables retrieval", 8),
        ["round", "76:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 76: knowledge stored as vectors enables retrieval", 12),
        ["round 76:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 76: knowledge stored as vectors enables retrieval", 16),
        ["round 76:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 76: knowledge stored as vectors enables retrieval", 24),
        ["round 76: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 76: knowledge stored as vectors enables retrieval", 32),
        ["round 76: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 76: the processor reads the record then stops", 4),
        ["round", "76:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 76: the processor reads the record then stops", 8),
        ["round", "76: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 76: the processor reads the record then stops", 12),
        ["round 76:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 76: the processor reads the record then stops", 16),
        ["round 76: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 76: the processor reads the record then stops", 24),
        ["round 76: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 76: the processor reads the record then stops", 32),
        ["round 76: the processor reads", "the record then stops"],
    ),
    (
        ("round 76: a worker pulls the next task from the queue", 4),
        ["round", "76:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 76: a worker pulls the next task from the queue", 8),
        ["round", "76: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 76: a worker pulls the next task from the queue", 12),
        ["round 76: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 76: a worker pulls the next task from the queue", 16),
        ["round 76: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 76: a worker pulls the next task from the queue", 24),
        ["round 76: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 76: a worker pulls the next task from the queue", 32),
        ["round 76: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 76: signals travel through the network layer", 4),
        ["round", "76:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 76: signals travel through the network layer", 8),
        ["round", "76:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 76: signals travel through the network layer", 12),
        ["round 76:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 76: signals travel through the network layer", 16),
        ["round 76:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 76: signals travel through the network layer", 24),
        ["round 76: signals travel", "through the network", "layer"],
    ),
    (
        ("round 76: signals travel through the network layer", 32),
        ["round 76: signals travel through", "the network layer"],
    ),
    (
        ("round 76: the gateway routes each request by policy", 4),
        ["round", "76:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 76: the gateway routes each request by policy", 8),
        ["round", "76: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 76: the gateway routes each request by policy", 12),
        ["round 76:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 76: the gateway routes each request by policy", 16),
        ["round 76: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 76: the gateway routes each request by policy", 24),
        ["round 76: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 76: the gateway routes each request by policy", 32),
        ["round 76: the gateway routes", "each request by policy"],
    ),
    (
        ("round 76: memory grows until the buffer is full", 4),
        ["round", "76:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 76: memory grows until the buffer is full", 8),
        ["round", "76:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 76: memory grows until the buffer is full", 12),
        ["round 76:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 76: memory grows until the buffer is full", 16),
        ["round 76: memory", "grows until the", "buffer is full"],
    ),
    (("round 76: memory grows until the buffer is full", 24), ["round 76: memory grows", "until the buffer is full"]),
    (("round 76: memory grows until the buffer is full", 32), ["round 76: memory grows until the", "buffer is full"]),
    (
        ("round 76: the cluster mirrors every packet twice", 4),
        ["round", "76:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 76: the cluster mirrors every packet twice", 8),
        ["round", "76: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 76: the cluster mirrors every packet twice", 12),
        ["round 76:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 76: the cluster mirrors every packet twice", 16),
        ["round 76: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 76: the cluster mirrors every packet twice", 24),
        ["round 76: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 76: the cluster mirrors every packet twice", 32), ["round 76: the cluster mirrors", "every packet twice"]),
    (
        ("round 76: ranking uses tokens learned from the corpus", 4),
        ["round", "76:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 76: ranking uses tokens learned from the corpus", 8),
        ["round", "76:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 76: ranking uses tokens learned from the corpus", 12),
        ["round 76:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 76: ranking uses tokens learned from the corpus", 16),
        ["round 76:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 76: ranking uses tokens learned from the corpus", 24),
        ["round 76: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 76: ranking uses tokens learned from the corpus", 32),
        ["round 76: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 76: a long session ends when the candle dies", 4),
        ["round", "76:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 76: a long session ends when the candle dies", 8),
        ["round", "76: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 76: a long session ends when the candle dies", 12),
        ["round 76: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 76: a long session ends when the candle dies", 16),
        ["round 76: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 76: a long session ends when the candle dies", 24),
        ["round 76: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 76: a long session ends when the candle dies", 32),
        ["round 76: a long session ends", "when the candle dies"],
    ),
    (
        ("round 76: encode the prompt then map the result", 4),
        ["round", "76:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 76: encode the prompt then map the result", 8),
        ["round", "76:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 76: encode the prompt then map the result", 12),
        ["round 76:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 76: encode the prompt then map the result", 16),
        ["round 76: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 76: encode the prompt then map the result", 24),
        ["round 76: encode the", "prompt then map the", "result"],
    ),
    (("round 76: encode the prompt then map the result", 32), ["round 76: encode the prompt then", "map the result"]),
    (
        ("round 76: the kernel wakes the worker at dawn", 4),
        ["round", "76:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 76: the kernel wakes the worker at dawn", 8),
        ["round", "76: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 76: the kernel wakes the worker at dawn", 12),
        ["round 76:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 76: the kernel wakes the worker at dawn", 16), ["round 76: the", "kernel wakes the", "worker at dawn"]),
    (("round 76: the kernel wakes the worker at dawn", 24), ["round 76: the kernel", "wakes the worker at dawn"]),
    (("round 76: the kernel wakes the worker at dawn", 32), ["round 76: the kernel wakes the", "worker at dawn"]),
    (
        ("round 76: service latency drops after the patch", 4),
        ["round", "76:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 76: service latency drops after the patch", 8),
        ["round", "76:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 76: service latency drops after the patch", 12),
        ["round 76:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 76: service latency drops after the patch", 16),
        ["round 76:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 76: service latency drops after the patch", 24),
        ["round 76: service", "latency drops after the", "patch"],
    ),
    (("round 76: service latency drops after the patch", 32), ["round 76: service latency drops", "after the patch"]),
    (
        ("round 76: the library caches every vector it sees", 4),
        ["round", "76:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 76: the library caches every vector it sees", 8),
        ["round", "76: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 76: the library caches every vector it sees", 12),
        ["round 76:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 76: the library caches every vector it sees", 16),
        ["round 76: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 76: the library caches every vector it sees", 24),
        ["round 76: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 76: the library caches every vector it sees", 32),
        ["round 76: the library caches", "every vector it sees"],
    ),
    (
        ("round 76: agents argue then the debate resolves", 4),
        ["round", "76:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 76: agents argue then the debate resolves", 8),
        ["round", "76:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 76: agents argue then the debate resolves", 12),
        ["round 76:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 76: agents argue then the debate resolves", 16),
        ["round 76: agents", "argue then the", "debate resolves"],
    ),
    (("round 76: agents argue then the debate resolves", 24), ["round 76: agents argue", "then the debate resolves"]),
    (("round 76: agents argue then the debate resolves", 32), ["round 76: agents argue then the", "debate resolves"]),
    (
        ("round 76: the filter keeps only strong matches", 4),
        ["round", "76:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 76: the filter keeps only strong matches", 8),
        ["round", "76: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 76: the filter keeps only strong matches", 12),
        ["round 76:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 76: the filter keeps only strong matches", 16),
        ["round 76: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 76: the filter keeps only strong matches", 24), ["round 76: the filter", "keeps only strong", "matches"]),
    (("round 76: the filter keeps only strong matches", 32), ["round 76: the filter keeps only", "strong matches"]),
    (
        ("round 76: the model answers with a short reply", 4),
        ["round", "76:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 76: the model answers with a short reply", 8),
        ["round", "76: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 76: the model answers with a short reply", 12),
        ["round 76:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 76: the model answers with a short reply", 16),
        ["round 76: the", "model answers", "with a short", "reply"],
    ),
    (("round 76: the model answers with a short reply", 24), ["round 76: the model", "answers with a short", "reply"]),
    (("round 76: the model answers with a short reply", 32), ["round 76: the model answers with", "a short reply"]),
    (
        ("round 76: the recorder stores the reasoning trace", 4),
        ["round", "76:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 76: the recorder stores the reasoning trace", 8),
        ["round", "76: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 76: the recorder stores the reasoning trace", 12),
        ["round 76:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 76: the recorder stores the reasoning trace", 16),
        ["round 76: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 76: the recorder stores the reasoning trace", 24),
        ["round 76: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 76: the recorder stores the reasoning trace", 32),
        ["round 76: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 76: the angel watches the processor run", 4),
        ["round", "76:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 76: the angel watches the processor run", 8),
        ["round", "76: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 76: the angel watches the processor run", 12),
        ["round 76:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 76: the angel watches the processor run", 16), ["round 76: the", "angel watches", "the processor", "run"]),
    (("round 76: the angel watches the processor run", 24), ["round 76: the angel", "watches the processor", "run"]),
    (("round 76: the angel watches the processor run", 32), ["round 76: the angel watches the", "processor run"]),
    (
        ("round 76: angle of the vector decides the match", 4),
        ["round", "76:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 76: angle of the vector decides the match", 8),
        ["round", "76:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 76: angle of the vector decides the match", 12),
        ["round 76:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 76: angle of the vector decides the match", 16),
        ["round 76: angle", "of the vector", "decides the", "match"],
    ),
    (("round 76: angle of the vector decides the match", 24), ["round 76: angle of the", "vector decides the match"]),
    (("round 76: angle of the vector decides the match", 32), ["round 76: angle of the vector", "decides the match"]),
    (
        ("round 76: the candle burns twice as long at night", 4),
        ["round", "76:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 76: the candle burns twice as long at night", 8),
        ["round", "76: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 76: the candle burns twice as long at night", 12),
        ["round 76:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 76: the candle burns twice as long at night", 16),
        ["round 76: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 76: the candle burns twice as long at night", 24),
        ["round 76: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 76: the candle burns twice as long at night", 32),
        ["round 76: the candle burns twice", "as long at night"],
    ),
    (
        ("round 76: a mirror of the universe in one line", 4),
        ["round", "76:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 76: a mirror of the universe in one line", 8),
        ["round", "76: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 76: a mirror of the universe in one line", 12),
        ["round 76: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 76: a mirror of the universe in one line", 16),
        ["round 76: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 76: a mirror of the universe in one line", 24), ["round 76: a mirror of", "the universe in one line"]),
    (("round 76: a mirror of the universe in one line", 32), ["round 76: a mirror of the", "universe in one line"]),
    (
        ("round 76: the queue drains before the storm", 4),
        ["round", "76:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 76: the queue drains before the storm", 8),
        ["round", "76: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 76: the queue drains before the storm", 12), ["round 76:", "the queue", "drains", "before the", "storm"]),
    (("round 76: the queue drains before the storm", 16), ["round 76: the", "queue drains", "before the storm"]),
    (("round 76: the queue drains before the storm", 24), ["round 76: the queue", "drains before the storm"]),
    (("round 76: the queue drains before the storm", 32), ["round 76: the queue drains", "before the storm"]),
    (
        ("kitten76 sitting76 agent76 angle76 universe76 memory76", 6),
        ["kitten76", "sitting76", "agent76", "angle76", "universe76", "memory76"],
    ),
    (
        ("kitten76 sitting76 agent76 angle76 universe76 memory76", 10),
        ["kitten76", "sitting76", "agent76", "angle76", "universe76", "memory76"],
    ),
    (
        ("kitten76 sitting76 agent76 angle76 universe76 memory76", 18),
        ["kitten76 sitting76", "agent76 angle76", "universe76", "memory76"],
    ),
    (
        ("kitten76 sitting76 agent76 angle76 universe76 memory76", 28),
        ["kitten76 sitting76 agent76", "angle76 universe76 memory76"],
    ),
    (
        ("sitting76 agent76 angle76 universe76 memory76 stream76", 6),
        ["sitting76", "agent76", "angle76", "universe76", "memory76", "stream76"],
    ),
    (
        ("sitting76 agent76 angle76 universe76 memory76 stream76", 10),
        ["sitting76", "agent76", "angle76", "universe76", "memory76", "stream76"],
    ),
    (
        ("sitting76 agent76 angle76 universe76 memory76 stream76", 18),
        ["sitting76 agent76", "angle76 universe76", "memory76 stream76"],
    ),
    (
        ("sitting76 agent76 angle76 universe76 memory76 stream76", 28),
        ["sitting76 agent76 angle76", "universe76 memory76 stream76"],
    ),
    (
        ("agent76 angle76 universe76 memory76 stream76 context76", 6),
        ["agent76", "angle76", "universe76", "memory76", "stream76", "context76"],
    ),
    (
        ("agent76 angle76 universe76 memory76 stream76 context76", 10),
        ["agent76", "angle76", "universe76", "memory76", "stream76", "context76"],
    ),
    (
        ("agent76 angle76 universe76 memory76 stream76 context76", 18),
        ["agent76 angle76", "universe76", "memory76 stream76", "context76"],
    ),
    (
        ("agent76 angle76 universe76 memory76 stream76 context76", 28),
        ["agent76 angle76 universe76", "memory76 stream76 context76"],
    ),
    (
        ("angle76 universe76 memory76 stream76 context76 knowledge76", 6),
        ["angle76", "universe76", "memory76", "stream76", "context76", "knowledge76"],
    ),
    (
        ("angle76 universe76 memory76 stream76 context76 knowledge76", 10),
        ["angle76", "universe76", "memory76", "stream76", "context76", "knowledge76"],
    ),
    (
        ("angle76 universe76 memory76 stream76 context76 knowledge76", 18),
        ["angle76 universe76", "memory76 stream76", "context76", "knowledge76"],
    ),
    (
        ("angle76 universe76 memory76 stream76 context76 knowledge76", 28),
        ["angle76 universe76 memory76", "stream76 context76", "knowledge76"],
    ),
    (
        ("universe76 memory76 stream76 context76 knowledge76 vector76", 6),
        ["universe76", "memory76", "stream76", "context76", "knowledge76", "vector76"],
    ),
    (
        ("universe76 memory76 stream76 context76 knowledge76 vector76", 10),
        ["universe76", "memory76", "stream76", "context76", "knowledge76", "vector76"],
    ),
    (
        ("universe76 memory76 stream76 context76 knowledge76 vector76", 18),
        ["universe76", "memory76 stream76", "context76", "knowledge76", "vector76"],
    ),
    (
        ("universe76 memory76 stream76 context76 knowledge76 vector76", 28),
        ["universe76 memory76 stream76", "context76 knowledge76", "vector76"],
    ),
    (
        ("memory76 stream76 context76 knowledge76 vector76 processor76", 6),
        ["memory76", "stream76", "context76", "knowledge76", "vector76", "processor76"],
    ),
    (
        ("memory76 stream76 context76 knowledge76 vector76 processor76", 10),
        ["memory76", "stream76", "context76", "knowledge76", "vector76", "processor76"],
    ),
    (
        ("memory76 stream76 context76 knowledge76 vector76 processor76", 18),
        ["memory76 stream76", "context76", "knowledge76", "vector76", "processor76"],
    ),
    (
        ("memory76 stream76 context76 knowledge76 vector76 processor76", 28),
        ["memory76 stream76 context76", "knowledge76 vector76", "processor76"],
    ),
    (
        ("stream76 context76 knowledge76 vector76 processor76 reasoning76", 6),
        ["stream76", "context76", "knowledge76", "vector76", "processor76", "reasoning76"],
    ),
    (
        ("stream76 context76 knowledge76 vector76 processor76 reasoning76", 10),
        ["stream76", "context76", "knowledge76", "vector76", "processor76", "reasoning76"],
    ),
    (
        ("stream76 context76 knowledge76 vector76 processor76 reasoning76", 18),
        ["stream76 context76", "knowledge76", "vector76", "processor76", "reasoning76"],
    ),
    (
        ("stream76 context76 knowledge76 vector76 processor76 reasoning76", 28),
        ["stream76 context76", "knowledge76 vector76", "processor76 reasoning76"],
    ),
    (
        ("context76 knowledge76 vector76 processor76 reasoning76 machine76", 6),
        ["context76", "knowledge76", "vector76", "processor76", "reasoning76", "machine76"],
    ),
    (
        ("context76 knowledge76 vector76 processor76 reasoning76 machine76", 10),
        ["context76", "knowledge76", "vector76", "processor76", "reasoning76", "machine76"],
    ),
    (
        ("context76 knowledge76 vector76 processor76 reasoning76 machine76", 18),
        ["context76", "knowledge76", "vector76", "processor76", "reasoning76", "machine76"],
    ),
    (
        ("context76 knowledge76 vector76 processor76 reasoning76 machine76", 28),
        ["context76 knowledge76", "vector76 processor76", "reasoning76 machine76"],
    ),
    (
        ("knowledge76 vector76 processor76 reasoning76 machine76 learning76", 6),
        ["knowledge76", "vector76", "processor76", "reasoning76", "machine76", "learning76"],
    ),
    (
        ("knowledge76 vector76 processor76 reasoning76 machine76 learning76", 10),
        ["knowledge76", "vector76", "processor76", "reasoning76", "machine76", "learning76"],
    ),
    (
        ("knowledge76 vector76 processor76 reasoning76 machine76 learning76", 18),
        ["knowledge76", "vector76", "processor76", "reasoning76", "machine76", "learning76"],
    ),
    (
        ("knowledge76 vector76 processor76 reasoning76 machine76 learning76", 28),
        ["knowledge76 vector76", "processor76 reasoning76", "machine76 learning76"],
    ),
    (
        ("vector76 processor76 reasoning76 machine76 learning76 model76", 6),
        ["vector76", "processor76", "reasoning76", "machine76", "learning76", "model76"],
    ),
    (
        ("vector76 processor76 reasoning76 machine76 learning76 model76", 10),
        ["vector76", "processor76", "reasoning76", "machine76", "learning76", "model76"],
    ),
    (
        ("vector76 processor76 reasoning76 machine76 learning76 model76", 18),
        ["vector76", "processor76", "reasoning76", "machine76", "learning76 model76"],
    ),
    (
        ("vector76 processor76 reasoning76 machine76 learning76 model76", 28),
        ["vector76 processor76", "reasoning76 machine76", "learning76 model76"],
    ),
    (
        ("processor76 reasoning76 machine76 learning76 model76 token76", 6),
        ["processor76", "reasoning76", "machine76", "learning76", "model76", "token76"],
    ),
    (
        ("processor76 reasoning76 machine76 learning76 model76 token76", 10),
        ["processor76", "reasoning76", "machine76", "learning76", "model76", "token76"],
    ),
    (
        ("processor76 reasoning76 machine76 learning76 model76 token76", 18),
        ["processor76", "reasoning76", "machine76", "learning76 model76", "token76"],
    ),
    (
        ("processor76 reasoning76 machine76 learning76 model76 token76", 28),
        ["processor76 reasoning76", "machine76 learning76 model76", "token76"],
    ),
    (
        ("reasoning76 machine76 learning76 model76 token76 prompt76", 6),
        ["reasoning76", "machine76", "learning76", "model76", "token76", "prompt76"],
    ),
    (
        ("reasoning76 machine76 learning76 model76 token76 prompt76", 10),
        ["reasoning76", "machine76", "learning76", "model76", "token76", "prompt76"],
    ),
    (
        ("reasoning76 machine76 learning76 model76 token76 prompt76", 18),
        ["reasoning76", "machine76", "learning76 model76", "token76 prompt76"],
    ),
    (
        ("reasoning76 machine76 learning76 model76 token76 prompt76", 28),
        ["reasoning76 machine76", "learning76 model76 token76", "prompt76"],
    ),
    (
        ("machine76 learning76 model76 token76 prompt76 session76", 6),
        ["machine76", "learning76", "model76", "token76", "prompt76", "session76"],
    ),
    (
        ("machine76 learning76 model76 token76 prompt76 session76", 10),
        ["machine76", "learning76", "model76", "token76", "prompt76", "session76"],
    ),
    (
        ("machine76 learning76 model76 token76 prompt76 session76", 18),
        ["machine76", "learning76 model76", "token76 prompt76", "session76"],
    ),
    (
        ("machine76 learning76 model76 token76 prompt76 session76", 28),
        ["machine76 learning76 model76", "token76 prompt76 session76"],
    ),
    (
        ("learning76 model76 token76 prompt76 session76 library76", 6),
        ["learning76", "model76", "token76", "prompt76", "session76", "library76"],
    ),
    (
        ("learning76 model76 token76 prompt76 session76 library76", 10),
        ["learning76", "model76", "token76", "prompt76", "session76", "library76"],
    ),
    (
        ("learning76 model76 token76 prompt76 session76 library76", 18),
        ["learning76 model76", "token76 prompt76", "session76", "library76"],
    ),
    (
        ("learning76 model76 token76 prompt76 session76 library76", 28),
        ["learning76 model76 token76", "prompt76 session76 library76"],
    ),
    (
        ("model76 token76 prompt76 session76 library76 service76", 6),
        ["model76", "token76", "prompt76", "session76", "library76", "service76"],
    ),
    (
        ("model76 token76 prompt76 session76 library76 service76", 10),
        ["model76", "token76", "prompt76", "session76", "library76", "service76"],
    ),
    (
        ("model76 token76 prompt76 session76 library76 service76", 18),
        ["model76 token76", "prompt76 session76", "library76", "service76"],
    ),
    (
        ("model76 token76 prompt76 session76 library76 service76", 28),
        ["model76 token76 prompt76", "session76 library76", "service76"],
    ),
    (
        ("token76 prompt76 session76 library76 service76 gateway76", 6),
        ["token76", "prompt76", "session76", "library76", "service76", "gateway76"],
    ),
    (
        ("token76 prompt76 session76 library76 service76 gateway76", 10),
        ["token76", "prompt76", "session76", "library76", "service76", "gateway76"],
    ),
    (
        ("token76 prompt76 session76 library76 service76 gateway76", 18),
        ["token76 prompt76", "session76", "library76", "service76", "gateway76"],
    ),
    (
        ("token76 prompt76 session76 library76 service76 gateway76", 28),
        ["token76 prompt76 session76", "library76 service76", "gateway76"],
    ),
    (
        ("prompt76 session76 library76 service76 gateway76 storage76", 6),
        ["prompt76", "session76", "library76", "service76", "gateway76", "storage76"],
    ),
    (
        ("prompt76 session76 library76 service76 gateway76 storage76", 10),
        ["prompt76", "session76", "library76", "service76", "gateway76", "storage76"],
    ),
    (
        ("prompt76 session76 library76 service76 gateway76 storage76", 18),
        ["prompt76 session76", "library76", "service76", "gateway76", "storage76"],
    ),
    (
        ("prompt76 session76 library76 service76 gateway76 storage76", 28),
        ["prompt76 session76 library76", "service76 gateway76", "storage76"],
    ),
    (
        ("session76 library76 service76 gateway76 storage76 network76", 6),
        ["session76", "library76", "service76", "gateway76", "storage76", "network76"],
    ),
    (
        ("session76 library76 service76 gateway76 storage76 network76", 10),
        ["session76", "library76", "service76", "gateway76", "storage76", "network76"],
    ),
    (
        ("session76 library76 service76 gateway76 storage76 network76", 18),
        ["session76", "library76", "service76", "gateway76", "storage76", "network76"],
    ),
    (
        ("session76 library76 service76 gateway76 storage76 network76", 28),
        ["session76 library76", "service76 gateway76", "storage76 network76"],
    ),
    (
        ("library76 service76 gateway76 storage76 network76 latency76", 6),
        ["library76", "service76", "gateway76", "storage76", "network76", "latency76"],
    ),
    (
        ("library76 service76 gateway76 storage76 network76 latency76", 10),
        ["library76", "service76", "gateway76", "storage76", "network76", "latency76"],
    ),
    (
        ("library76 service76 gateway76 storage76 network76 latency76", 18),
        ["library76", "service76", "gateway76", "storage76", "network76", "latency76"],
    ),
    (
        ("library76 service76 gateway76 storage76 network76 latency76", 28),
        ["library76 service76", "gateway76 storage76", "network76 latency76"],
    ),
    (
        ("service76 gateway76 storage76 network76 latency76 buffer76", 6),
        ["service76", "gateway76", "storage76", "network76", "latency76", "buffer76"],
    ),
    (
        ("service76 gateway76 storage76 network76 latency76 buffer76", 10),
        ["service76", "gateway76", "storage76", "network76", "latency76", "buffer76"],
    ),
    (
        ("service76 gateway76 storage76 network76 latency76 buffer76", 18),
        ["service76", "gateway76", "storage76", "network76", "latency76 buffer76"],
    ),
    (
        ("service76 gateway76 storage76 network76 latency76 buffer76", 28),
        ["service76 gateway76", "storage76 network76", "latency76 buffer76"],
    ),
    (
        ("gateway76 storage76 network76 latency76 buffer76 queue76", 6),
        ["gateway76", "storage76", "network76", "latency76", "buffer76", "queue76"],
    ),
    (
        ("gateway76 storage76 network76 latency76 buffer76 queue76", 10),
        ["gateway76", "storage76", "network76", "latency76", "buffer76", "queue76"],
    ),
    (
        ("gateway76 storage76 network76 latency76 buffer76 queue76", 18),
        ["gateway76", "storage76", "network76", "latency76 buffer76", "queue76"],
    ),
    (
        ("gateway76 storage76 network76 latency76 buffer76 queue76", 28),
        ["gateway76 storage76", "network76 latency76 buffer76", "queue76"],
    ),
    (
        ("storage76 network76 latency76 buffer76 queue76 worker76", 6),
        ["storage76", "network76", "latency76", "buffer76", "queue76", "worker76"],
    ),
    (
        ("storage76 network76 latency76 buffer76 queue76 worker76", 10),
        ["storage76", "network76", "latency76", "buffer76", "queue76", "worker76"],
    ),
    (
        ("storage76 network76 latency76 buffer76 queue76 worker76", 18),
        ["storage76", "network76", "latency76 buffer76", "queue76 worker76"],
    ),
    (
        ("storage76 network76 latency76 buffer76 queue76 worker76", 28),
        ["storage76 network76", "latency76 buffer76 queue76", "worker76"],
    ),
    (
        ("network76 latency76 buffer76 queue76 worker76 kernel76", 6),
        ["network76", "latency76", "buffer76", "queue76", "worker76", "kernel76"],
    ),
    (
        ("network76 latency76 buffer76 queue76 worker76 kernel76", 10),
        ["network76", "latency76", "buffer76", "queue76", "worker76", "kernel76"],
    ),
    (
        ("network76 latency76 buffer76 queue76 worker76 kernel76", 18),
        ["network76", "latency76 buffer76", "queue76 worker76", "kernel76"],
    ),
    (
        ("network76 latency76 buffer76 queue76 worker76 kernel76", 28),
        ["network76 latency76 buffer76", "queue76 worker76 kernel76"],
    ),
    (
        ("latency76 buffer76 queue76 worker76 kernel76 signal76", 6),
        ["latency76", "buffer76", "queue76", "worker76", "kernel76", "signal76"],
    ),
    (
        ("latency76 buffer76 queue76 worker76 kernel76 signal76", 10),
        ["latency76", "buffer76", "queue76", "worker76", "kernel76", "signal76"],
    ),
    (
        ("latency76 buffer76 queue76 worker76 kernel76 signal76", 18),
        ["latency76 buffer76", "queue76 worker76", "kernel76 signal76"],
    ),
    (
        ("latency76 buffer76 queue76 worker76 kernel76 signal76", 28),
        ["latency76 buffer76 queue76", "worker76 kernel76 signal76"],
    ),
    (
        ("buffer76 queue76 worker76 kernel76 signal76 packet76", 6),
        ["buffer76", "queue76", "worker76", "kernel76", "signal76", "packet76"],
    ),
    (
        ("buffer76 queue76 worker76 kernel76 signal76 packet76", 10),
        ["buffer76", "queue76", "worker76", "kernel76", "signal76", "packet76"],
    ),
    (
        ("buffer76 queue76 worker76 kernel76 signal76 packet76", 18),
        ["buffer76 queue76", "worker76 kernel76", "signal76 packet76"],
    ),
    (
        ("buffer76 queue76 worker76 kernel76 signal76 packet76", 28),
        ["buffer76 queue76 worker76", "kernel76 signal76 packet76"],
    ),
    (
        ("queue76 worker76 kernel76 signal76 packet76 router76", 6),
        ["queue76", "worker76", "kernel76", "signal76", "packet76", "router76"],
    ),
    (
        ("queue76 worker76 kernel76 signal76 packet76 router76", 10),
        ["queue76", "worker76", "kernel76", "signal76", "packet76", "router76"],
    ),
    (
        ("queue76 worker76 kernel76 signal76 packet76 router76", 18),
        ["queue76 worker76", "kernel76 signal76", "packet76 router76"],
    ),
    (
        ("queue76 worker76 kernel76 signal76 packet76 router76", 28),
        ["queue76 worker76 kernel76", "signal76 packet76 router76"],
    ),
    (
        ("worker76 kernel76 signal76 packet76 router76 cluster76", 6),
        ["worker76", "kernel76", "signal76", "packet76", "router76", "cluster76"],
    ),
    (
        ("worker76 kernel76 signal76 packet76 router76 cluster76", 10),
        ["worker76", "kernel76", "signal76", "packet76", "router76", "cluster76"],
    ),
    (
        ("worker76 kernel76 signal76 packet76 router76 cluster76", 18),
        ["worker76 kernel76", "signal76 packet76", "router76 cluster76"],
    ),
    (
        ("worker76 kernel76 signal76 packet76 router76 cluster76", 28),
        ["worker76 kernel76 signal76", "packet76 router76 cluster76"],
    ),
    (
        ("kernel76 signal76 packet76 router76 cluster76 mirror76", 6),
        ["kernel76", "signal76", "packet76", "router76", "cluster76", "mirror76"],
    ),
    (
        ("kernel76 signal76 packet76 router76 cluster76 mirror76", 10),
        ["kernel76", "signal76", "packet76", "router76", "cluster76", "mirror76"],
    ),
    (
        ("kernel76 signal76 packet76 router76 cluster76 mirror76", 18),
        ["kernel76 signal76", "packet76 router76", "cluster76 mirror76"],
    ),
    (
        ("kernel76 signal76 packet76 router76 cluster76 mirror76", 28),
        ["kernel76 signal76 packet76", "router76 cluster76 mirror76"],
    ),
    (
        ("signal76 packet76 router76 cluster76 mirror76 filter76", 6),
        ["signal76", "packet76", "router76", "cluster76", "mirror76", "filter76"],
    ),
    (
        ("signal76 packet76 router76 cluster76 mirror76 filter76", 10),
        ["signal76", "packet76", "router76", "cluster76", "mirror76", "filter76"],
    ),
    (
        ("signal76 packet76 router76 cluster76 mirror76 filter76", 18),
        ["signal76 packet76", "router76 cluster76", "mirror76 filter76"],
    ),
    (
        ("signal76 packet76 router76 cluster76 mirror76 filter76", 28),
        ["signal76 packet76 router76", "cluster76 mirror76 filter76"],
    ),
    (
        ("packet76 router76 cluster76 mirror76 filter76 ranking76", 6),
        ["packet76", "router76", "cluster76", "mirror76", "filter76", "ranking76"],
    ),
    (
        ("packet76 router76 cluster76 mirror76 filter76 ranking76", 10),
        ["packet76", "router76", "cluster76", "mirror76", "filter76", "ranking76"],
    ),
    (
        ("packet76 router76 cluster76 mirror76 filter76 ranking76", 18),
        ["packet76 router76", "cluster76 mirror76", "filter76 ranking76"],
    ),
    (
        ("packet76 router76 cluster76 mirror76 filter76 ranking76", 28),
        ["packet76 router76 cluster76", "mirror76 filter76 ranking76"],
    ),
    (
        ("router76 cluster76 mirror76 filter76 ranking76 encoding76", 6),
        ["router76", "cluster76", "mirror76", "filter76", "ranking76", "encoding76"],
    ),
    (
        ("router76 cluster76 mirror76 filter76 ranking76 encoding76", 10),
        ["router76", "cluster76", "mirror76", "filter76", "ranking76", "encoding76"],
    ),
    (
        ("router76 cluster76 mirror76 filter76 ranking76 encoding76", 18),
        ["router76 cluster76", "mirror76 filter76", "ranking76", "encoding76"],
    ),
    (
        ("router76 cluster76 mirror76 filter76 ranking76 encoding76", 28),
        ["router76 cluster76 mirror76", "filter76 ranking76", "encoding76"],
    ),
    (
        ("cluster76 mirror76 filter76 ranking76 encoding76 mapping76", 6),
        ["cluster76", "mirror76", "filter76", "ranking76", "encoding76", "mapping76"],
    ),
    (
        ("cluster76 mirror76 filter76 ranking76 encoding76 mapping76", 10),
        ["cluster76", "mirror76", "filter76", "ranking76", "encoding76", "mapping76"],
    ),
    (
        ("cluster76 mirror76 filter76 ranking76 encoding76 mapping76", 18),
        ["cluster76 mirror76", "filter76 ranking76", "encoding76", "mapping76"],
    ),
    (
        ("cluster76 mirror76 filter76 ranking76 encoding76 mapping76", 28),
        ["cluster76 mirror76 filter76", "ranking76 encoding76", "mapping76"],
    ),
    (
        ("mirror76 filter76 ranking76 encoding76 mapping76 record76", 6),
        ["mirror76", "filter76", "ranking76", "encoding76", "mapping76", "record76"],
    ),
    (
        ("mirror76 filter76 ranking76 encoding76 mapping76 record76", 10),
        ["mirror76", "filter76", "ranking76", "encoding76", "mapping76", "record76"],
    ),
    (
        ("mirror76 filter76 ranking76 encoding76 mapping76 record76", 18),
        ["mirror76 filter76", "ranking76", "encoding76", "mapping76 record76"],
    ),
    (
        ("mirror76 filter76 ranking76 encoding76 mapping76 record76", 28),
        ["mirror76 filter76 ranking76", "encoding76 mapping76", "record76"],
    ),
    (
        ("filter76 ranking76 encoding76 mapping76 record76 candle76", 6),
        ["filter76", "ranking76", "encoding76", "mapping76", "record76", "candle76"],
    ),
    (
        ("filter76 ranking76 encoding76 mapping76 record76 candle76", 10),
        ["filter76", "ranking76", "encoding76", "mapping76", "record76", "candle76"],
    ),
    (
        ("filter76 ranking76 encoding76 mapping76 record76 candle76", 18),
        ["filter76 ranking76", "encoding76", "mapping76 record76", "candle76"],
    ),
    (
        ("filter76 ranking76 encoding76 mapping76 record76 candle76", 28),
        ["filter76 ranking76", "encoding76 mapping76", "record76 candle76"],
    ),
    (
        ("ranking76 encoding76 mapping76 record76 candle76 thread76", 6),
        ["ranking76", "encoding76", "mapping76", "record76", "candle76", "thread76"],
    ),
    (
        ("ranking76 encoding76 mapping76 record76 candle76 thread76", 10),
        ["ranking76", "encoding76", "mapping76", "record76", "candle76", "thread76"],
    ),
    (
        ("ranking76 encoding76 mapping76 record76 candle76 thread76", 18),
        ["ranking76", "encoding76", "mapping76 record76", "candle76 thread76"],
    ),
    (
        ("ranking76 encoding76 mapping76 record76 candle76 thread76", 28),
        ["ranking76 encoding76", "mapping76 record76 candle76", "thread76"],
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
