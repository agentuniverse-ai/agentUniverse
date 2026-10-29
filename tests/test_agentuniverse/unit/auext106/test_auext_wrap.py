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
        ("round 106: the quick brown fox jumps over the lazy dog", 4),
        ["round", "106:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", 8),
        ["round", "106: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", 12),
        ["round 106:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", 16),
        ["round 106: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", 24),
        ["round 106: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 106: the quick brown fox jumps over the lazy dog", 32),
        ["round 106: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", 4),
        ["round", "106:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", 8),
        ["round", "106:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", 12),
        ["round 106:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", 16),
        ["round 106:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", 24),
        ["round 106: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 106: agentuniverse is a framework for multi agents", 32),
        ["round 106: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", 4),
        ["round", "106:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", 8),
        ["round", "106:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", 12),
        ["round 106:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", 16),
        ["round 106:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", 24),
        ["round 106: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 106: knowledge stored as vectors enables retrieval", 32),
        ["round 106: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 106: the processor reads the record then stops", 4),
        ["round", "106:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 106: the processor reads the record then stops", 8),
        ["round", "106: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 106: the processor reads the record then stops", 12),
        ["round 106:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 106: the processor reads the record then stops", 16),
        ["round 106: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 106: the processor reads the record then stops", 24),
        ["round 106: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 106: the processor reads the record then stops", 32),
        ["round 106: the processor reads", "the record then stops"],
    ),
    (
        ("round 106: a worker pulls the next task from the queue", 4),
        ["round", "106:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 106: a worker pulls the next task from the queue", 8),
        ["round", "106: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 106: a worker pulls the next task from the queue", 12),
        ["round 106: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 106: a worker pulls the next task from the queue", 16),
        ["round 106: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 106: a worker pulls the next task from the queue", 24),
        ["round 106: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 106: a worker pulls the next task from the queue", 32),
        ["round 106: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 106: signals travel through the network layer", 4),
        ["round", "106:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 106: signals travel through the network layer", 8),
        ["round", "106:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 106: signals travel through the network layer", 12),
        ["round 106:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 106: signals travel through the network layer", 16),
        ["round 106:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 106: signals travel through the network layer", 24),
        ["round 106: signals", "travel through the", "network layer"],
    ),
    (
        ("round 106: signals travel through the network layer", 32),
        ["round 106: signals travel", "through the network layer"],
    ),
    (
        ("round 106: the gateway routes each request by policy", 4),
        ["round", "106:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 106: the gateway routes each request by policy", 8),
        ["round", "106: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 106: the gateway routes each request by policy", 12),
        ["round 106:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 106: the gateway routes each request by policy", 16),
        ["round 106: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 106: the gateway routes each request by policy", 24),
        ["round 106: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 106: the gateway routes each request by policy", 32),
        ["round 106: the gateway routes", "each request by policy"],
    ),
    (
        ("round 106: memory grows until the buffer is full", 4),
        ["round", "106:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 106: memory grows until the buffer is full", 8),
        ["round", "106:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 106: memory grows until the buffer is full", 12),
        ["round 106:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 106: memory grows until the buffer is full", 16),
        ["round 106:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 106: memory grows until the buffer is full", 24), ["round 106: memory grows", "until the buffer is full"]),
    (("round 106: memory grows until the buffer is full", 32), ["round 106: memory grows until", "the buffer is full"]),
    (
        ("round 106: the cluster mirrors every packet twice", 4),
        ["round", "106:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 106: the cluster mirrors every packet twice", 8),
        ["round", "106: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 106: the cluster mirrors every packet twice", 12),
        ["round 106:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 106: the cluster mirrors every packet twice", 16),
        ["round 106: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 106: the cluster mirrors every packet twice", 24),
        ["round 106: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 106: the cluster mirrors every packet twice", 32),
        ["round 106: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", 4),
        ["round", "106:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", 8),
        ["round", "106:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", 12),
        ["round 106:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", 16),
        ["round 106:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", 24),
        ["round 106: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 106: ranking uses tokens learned from the corpus", 32),
        ["round 106: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 106: a long session ends when the candle dies", 4),
        ["round", "106:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 106: a long session ends when the candle dies", 8),
        ["round", "106: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 106: a long session ends when the candle dies", 12),
        ["round 106: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 106: a long session ends when the candle dies", 16),
        ["round 106: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 106: a long session ends when the candle dies", 24),
        ["round 106: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 106: a long session ends when the candle dies", 32),
        ["round 106: a long session ends", "when the candle dies"],
    ),
    (
        ("round 106: encode the prompt then map the result", 4),
        ["round", "106:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 106: encode the prompt then map the result", 8),
        ["round", "106:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 106: encode the prompt then map the result", 12),
        ["round 106:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 106: encode the prompt then map the result", 16),
        ["round 106:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 106: encode the prompt then map the result", 24),
        ["round 106: encode the", "prompt then map the", "result"],
    ),
    (("round 106: encode the prompt then map the result", 32), ["round 106: encode the prompt", "then map the result"]),
    (
        ("round 106: the kernel wakes the worker at dawn", 4),
        ["round", "106:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 106: the kernel wakes the worker at dawn", 8),
        ["round", "106: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 106: the kernel wakes the worker at dawn", 12),
        ["round 106:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 106: the kernel wakes the worker at dawn", 16), ["round 106: the", "kernel wakes the", "worker at dawn"]),
    (("round 106: the kernel wakes the worker at dawn", 24), ["round 106: the kernel", "wakes the worker at dawn"]),
    (("round 106: the kernel wakes the worker at dawn", 32), ["round 106: the kernel wakes the", "worker at dawn"]),
    (
        ("round 106: service latency drops after the patch", 4),
        ["round", "106:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 106: service latency drops after the patch", 8),
        ["round", "106:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 106: service latency drops after the patch", 12),
        ["round 106:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 106: service latency drops after the patch", 16),
        ["round 106:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 106: service latency drops after the patch", 24),
        ["round 106: service", "latency drops after the", "patch"],
    ),
    (("round 106: service latency drops after the patch", 32), ["round 106: service latency drops", "after the patch"]),
    (
        ("round 106: the library caches every vector it sees", 4),
        ["round", "106:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 106: the library caches every vector it sees", 8),
        ["round", "106: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 106: the library caches every vector it sees", 12),
        ["round 106:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 106: the library caches every vector it sees", 16),
        ["round 106: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 106: the library caches every vector it sees", 24),
        ["round 106: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 106: the library caches every vector it sees", 32),
        ["round 106: the library caches", "every vector it sees"],
    ),
    (
        ("round 106: agents argue then the debate resolves", 4),
        ["round", "106:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 106: agents argue then the debate resolves", 8),
        ["round", "106:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 106: agents argue then the debate resolves", 12),
        ["round 106:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 106: agents argue then the debate resolves", 16),
        ["round 106:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 106: agents argue then the debate resolves", 24), ["round 106: agents argue", "then the debate resolves"]),
    (("round 106: agents argue then the debate resolves", 32), ["round 106: agents argue then the", "debate resolves"]),
    (
        ("round 106: the filter keeps only strong matches", 4),
        ["round", "106:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 106: the filter keeps only strong matches", 8),
        ["round", "106: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 106: the filter keeps only strong matches", 12),
        ["round 106:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 106: the filter keeps only strong matches", 16),
        ["round 106: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 106: the filter keeps only strong matches", 24),
        ["round 106: the filter", "keeps only strong", "matches"],
    ),
    (("round 106: the filter keeps only strong matches", 32), ["round 106: the filter keeps only", "strong matches"]),
    (
        ("round 106: the model answers with a short reply", 4),
        ["round", "106:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 106: the model answers with a short reply", 8),
        ["round", "106: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 106: the model answers with a short reply", 12),
        ["round 106:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 106: the model answers with a short reply", 16),
        ["round 106: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 106: the model answers with a short reply", 24),
        ["round 106: the model", "answers with a short", "reply"],
    ),
    (("round 106: the model answers with a short reply", 32), ["round 106: the model answers", "with a short reply"]),
    (
        ("round 106: the recorder stores the reasoning trace", 4),
        ["round", "106:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 106: the recorder stores the reasoning trace", 8),
        ["round", "106: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 106: the recorder stores the reasoning trace", 12),
        ["round 106:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 106: the recorder stores the reasoning trace", 16),
        ["round 106: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 106: the recorder stores the reasoning trace", 24),
        ["round 106: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 106: the recorder stores the reasoning trace", 32),
        ["round 106: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 106: the angel watches the processor run", 4),
        ["round", "106:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 106: the angel watches the processor run", 8),
        ["round", "106: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 106: the angel watches the processor run", 12),
        ["round 106:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 106: the angel watches the processor run", 16),
        ["round 106: the", "angel watches", "the processor", "run"],
    ),
    (("round 106: the angel watches the processor run", 24), ["round 106: the angel", "watches the processor", "run"]),
    (("round 106: the angel watches the processor run", 32), ["round 106: the angel watches the", "processor run"]),
    (
        ("round 106: angle of the vector decides the match", 4),
        ["round", "106:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 106: angle of the vector decides the match", 8),
        ["round", "106:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 106: angle of the vector decides the match", 12),
        ["round 106:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 106: angle of the vector decides the match", 16),
        ["round 106: angle", "of the vector", "decides the", "match"],
    ),
    (("round 106: angle of the vector decides the match", 24), ["round 106: angle of the", "vector decides the match"]),
    (("round 106: angle of the vector decides the match", 32), ["round 106: angle of the vector", "decides the match"]),
    (
        ("round 106: the candle burns twice as long at night", 4),
        ["round", "106:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 106: the candle burns twice as long at night", 8),
        ["round", "106: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 106: the candle burns twice as long at night", 12),
        ["round 106:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 106: the candle burns twice as long at night", 16),
        ["round 106: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 106: the candle burns twice as long at night", 24),
        ["round 106: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 106: the candle burns twice as long at night", 32),
        ["round 106: the candle burns", "twice as long at night"],
    ),
    (
        ("round 106: a mirror of the universe in one line", 4),
        ["round", "106:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 106: a mirror of the universe in one line", 8),
        ["round", "106: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 106: a mirror of the universe in one line", 12),
        ["round 106: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 106: a mirror of the universe in one line", 16),
        ["round 106: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 106: a mirror of the universe in one line", 24), ["round 106: a mirror of", "the universe in one line"]),
    (("round 106: a mirror of the universe in one line", 32), ["round 106: a mirror of the", "universe in one line"]),
    (
        ("round 106: the queue drains before the storm", 4),
        ["round", "106:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 106: the queue drains before the storm", 8),
        ["round", "106: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 106: the queue drains before the storm", 12),
        ["round 106:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 106: the queue drains before the storm", 16), ["round 106: the", "queue drains", "before the storm"]),
    (("round 106: the queue drains before the storm", 24), ["round 106: the queue", "drains before the storm"]),
    (("round 106: the queue drains before the storm", 32), ["round 106: the queue drains", "before the storm"]),
    (
        ("kitten106 sitting106 agent106 angle106 universe106 memory106", 6),
        ["kitten106", "sitting106", "agent106", "angle106", "universe106", "memory106"],
    ),
    (
        ("kitten106 sitting106 agent106 angle106 universe106 memory106", 10),
        ["kitten106", "sitting106", "agent106", "angle106", "universe106", "memory106"],
    ),
    (
        ("kitten106 sitting106 agent106 angle106 universe106 memory106", 18),
        ["kitten106", "sitting106", "agent106 angle106", "universe106", "memory106"],
    ),
    (
        ("kitten106 sitting106 agent106 angle106 universe106 memory106", 28),
        ["kitten106 sitting106", "agent106 angle106", "universe106 memory106"],
    ),
    (
        ("sitting106 agent106 angle106 universe106 memory106 stream106", 6),
        ["sitting106", "agent106", "angle106", "universe106", "memory106", "stream106"],
    ),
    (
        ("sitting106 agent106 angle106 universe106 memory106 stream106", 10),
        ["sitting106", "agent106", "angle106", "universe106", "memory106", "stream106"],
    ),
    (
        ("sitting106 agent106 angle106 universe106 memory106 stream106", 18),
        ["sitting106", "agent106 angle106", "universe106", "memory106", "stream106"],
    ),
    (
        ("sitting106 agent106 angle106 universe106 memory106 stream106", 28),
        ["sitting106 agent106 angle106", "universe106 memory106", "stream106"],
    ),
    (
        ("agent106 angle106 universe106 memory106 stream106 context106", 6),
        ["agent106", "angle106", "universe106", "memory106", "stream106", "context106"],
    ),
    (
        ("agent106 angle106 universe106 memory106 stream106 context106", 10),
        ["agent106", "angle106", "universe106", "memory106", "stream106", "context106"],
    ),
    (
        ("agent106 angle106 universe106 memory106 stream106 context106", 18),
        ["agent106 angle106", "universe106", "memory106", "stream106", "context106"],
    ),
    (
        ("agent106 angle106 universe106 memory106 stream106 context106", 28),
        ["agent106 angle106", "universe106 memory106", "stream106 context106"],
    ),
    (
        ("angle106 universe106 memory106 stream106 context106 knowledge106", 6),
        ["angle106", "universe106", "memory106", "stream106", "context106", "knowledge106"],
    ),
    (
        ("angle106 universe106 memory106 stream106 context106 knowledge106", 10),
        ["angle106", "universe106", "memory106", "stream106", "context106", "knowledge106"],
    ),
    (
        ("angle106 universe106 memory106 stream106 context106 knowledge106", 18),
        ["angle106", "universe106", "memory106", "stream106", "context106", "knowledge106"],
    ),
    (
        ("angle106 universe106 memory106 stream106 context106 knowledge106", 28),
        ["angle106 universe106", "memory106 stream106", "context106 knowledge106"],
    ),
    (
        ("universe106 memory106 stream106 context106 knowledge106 vector106", 6),
        ["universe106", "memory106", "stream106", "context106", "knowledge106", "vector106"],
    ),
    (
        ("universe106 memory106 stream106 context106 knowledge106 vector106", 10),
        ["universe106", "memory106", "stream106", "context106", "knowledge106", "vector106"],
    ),
    (
        ("universe106 memory106 stream106 context106 knowledge106 vector106", 18),
        ["universe106", "memory106", "stream106", "context106", "knowledge106", "vector106"],
    ),
    (
        ("universe106 memory106 stream106 context106 knowledge106 vector106", 28),
        ["universe106 memory106", "stream106 context106", "knowledge106 vector106"],
    ),
    (
        ("memory106 stream106 context106 knowledge106 vector106 processor106", 6),
        ["memory106", "stream106", "context106", "knowledge106", "vector106", "processor106"],
    ),
    (
        ("memory106 stream106 context106 knowledge106 vector106 processor106", 10),
        ["memory106", "stream106", "context106", "knowledge106", "vector106", "processor106"],
    ),
    (
        ("memory106 stream106 context106 knowledge106 vector106 processor106", 18),
        ["memory106", "stream106", "context106", "knowledge106", "vector106", "processor106"],
    ),
    (
        ("memory106 stream106 context106 knowledge106 vector106 processor106", 28),
        ["memory106 stream106", "context106 knowledge106", "vector106 processor106"],
    ),
    (
        ("stream106 context106 knowledge106 vector106 processor106 reasoning106", 6),
        ["stream106", "context106", "knowledge106", "vector106", "processor106", "reasoning106"],
    ),
    (
        ("stream106 context106 knowledge106 vector106 processor106 reasoning106", 10),
        ["stream106", "context106", "knowledge106", "vector106", "processor106", "reasoning106"],
    ),
    (
        ("stream106 context106 knowledge106 vector106 processor106 reasoning106", 18),
        ["stream106", "context106", "knowledge106", "vector106", "processor106", "reasoning106"],
    ),
    (
        ("stream106 context106 knowledge106 vector106 processor106 reasoning106", 28),
        ["stream106 context106", "knowledge106 vector106", "processor106 reasoning106"],
    ),
    (
        ("context106 knowledge106 vector106 processor106 reasoning106 machine106", 6),
        ["context106", "knowledge106", "vector106", "processor106", "reasoning106", "machine106"],
    ),
    (
        ("context106 knowledge106 vector106 processor106 reasoning106 machine106", 10),
        ["context106", "knowledge106", "vector106", "processor106", "reasoning106", "machine106"],
    ),
    (
        ("context106 knowledge106 vector106 processor106 reasoning106 machine106", 18),
        ["context106", "knowledge106", "vector106", "processor106", "reasoning106", "machine106"],
    ),
    (
        ("context106 knowledge106 vector106 processor106 reasoning106 machine106", 28),
        ["context106 knowledge106", "vector106 processor106", "reasoning106 machine106"],
    ),
    (
        ("knowledge106 vector106 processor106 reasoning106 machine106 learning106", 6),
        ["knowledge106", "vector106", "processor106", "reasoning106", "machine106", "learning106"],
    ),
    (
        ("knowledge106 vector106 processor106 reasoning106 machine106 learning106", 10),
        ["knowledge106", "vector106", "processor106", "reasoning106", "machine106", "learning106"],
    ),
    (
        ("knowledge106 vector106 processor106 reasoning106 machine106 learning106", 18),
        ["knowledge106", "vector106", "processor106", "reasoning106", "machine106", "learning106"],
    ),
    (
        ("knowledge106 vector106 processor106 reasoning106 machine106 learning106", 28),
        ["knowledge106 vector106", "processor106 reasoning106", "machine106 learning106"],
    ),
    (
        ("vector106 processor106 reasoning106 machine106 learning106 model106", 6),
        ["vector106", "processor106", "reasoning106", "machine106", "learning106", "model106"],
    ),
    (
        ("vector106 processor106 reasoning106 machine106 learning106 model106", 10),
        ["vector106", "processor106", "reasoning106", "machine106", "learning106", "model106"],
    ),
    (
        ("vector106 processor106 reasoning106 machine106 learning106 model106", 18),
        ["vector106", "processor106", "reasoning106", "machine106", "learning106", "model106"],
    ),
    (
        ("vector106 processor106 reasoning106 machine106 learning106 model106", 28),
        ["vector106 processor106", "reasoning106 machine106", "learning106 model106"],
    ),
    (
        ("processor106 reasoning106 machine106 learning106 model106 token106", 6),
        ["processor106", "reasoning106", "machine106", "learning106", "model106", "token106"],
    ),
    (
        ("processor106 reasoning106 machine106 learning106 model106 token106", 10),
        ["processor106", "reasoning106", "machine106", "learning106", "model106", "token106"],
    ),
    (
        ("processor106 reasoning106 machine106 learning106 model106 token106", 18),
        ["processor106", "reasoning106", "machine106", "learning106", "model106 token106"],
    ),
    (
        ("processor106 reasoning106 machine106 learning106 model106 token106", 28),
        ["processor106 reasoning106", "machine106 learning106", "model106 token106"],
    ),
    (
        ("reasoning106 machine106 learning106 model106 token106 prompt106", 6),
        ["reasoning106", "machine106", "learning106", "model106", "token106", "prompt106"],
    ),
    (
        ("reasoning106 machine106 learning106 model106 token106 prompt106", 10),
        ["reasoning106", "machine106", "learning106", "model106", "token106", "prompt106"],
    ),
    (
        ("reasoning106 machine106 learning106 model106 token106 prompt106", 18),
        ["reasoning106", "machine106", "learning106", "model106 token106", "prompt106"],
    ),
    (
        ("reasoning106 machine106 learning106 model106 token106 prompt106", 28),
        ["reasoning106 machine106", "learning106 model106", "token106 prompt106"],
    ),
    (
        ("machine106 learning106 model106 token106 prompt106 session106", 6),
        ["machine106", "learning106", "model106", "token106", "prompt106", "session106"],
    ),
    (
        ("machine106 learning106 model106 token106 prompt106 session106", 10),
        ["machine106", "learning106", "model106", "token106", "prompt106", "session106"],
    ),
    (
        ("machine106 learning106 model106 token106 prompt106 session106", 18),
        ["machine106", "learning106", "model106 token106", "prompt106", "session106"],
    ),
    (
        ("machine106 learning106 model106 token106 prompt106 session106", 28),
        ["machine106 learning106", "model106 token106 prompt106", "session106"],
    ),
    (
        ("learning106 model106 token106 prompt106 session106 library106", 6),
        ["learning106", "model106", "token106", "prompt106", "session106", "library106"],
    ),
    (
        ("learning106 model106 token106 prompt106 session106 library106", 10),
        ["learning106", "model106", "token106", "prompt106", "session106", "library106"],
    ),
    (
        ("learning106 model106 token106 prompt106 session106 library106", 18),
        ["learning106", "model106 token106", "prompt106", "session106", "library106"],
    ),
    (
        ("learning106 model106 token106 prompt106 session106 library106", 28),
        ["learning106 model106", "token106 prompt106", "session106 library106"],
    ),
    (
        ("model106 token106 prompt106 session106 library106 service106", 6),
        ["model106", "token106", "prompt106", "session106", "library106", "service106"],
    ),
    (
        ("model106 token106 prompt106 session106 library106 service106", 10),
        ["model106", "token106", "prompt106", "session106", "library106", "service106"],
    ),
    (
        ("model106 token106 prompt106 session106 library106 service106", 18),
        ["model106 token106", "prompt106", "session106", "library106", "service106"],
    ),
    (
        ("model106 token106 prompt106 session106 library106 service106", 28),
        ["model106 token106 prompt106", "session106 library106", "service106"],
    ),
    (
        ("token106 prompt106 session106 library106 service106 gateway106", 6),
        ["token106", "prompt106", "session106", "library106", "service106", "gateway106"],
    ),
    (
        ("token106 prompt106 session106 library106 service106 gateway106", 10),
        ["token106", "prompt106", "session106", "library106", "service106", "gateway106"],
    ),
    (
        ("token106 prompt106 session106 library106 service106 gateway106", 18),
        ["token106 prompt106", "session106", "library106", "service106", "gateway106"],
    ),
    (
        ("token106 prompt106 session106 library106 service106 gateway106", 28),
        ["token106 prompt106", "session106 library106", "service106 gateway106"],
    ),
    (
        ("prompt106 session106 library106 service106 gateway106 storage106", 6),
        ["prompt106", "session106", "library106", "service106", "gateway106", "storage106"],
    ),
    (
        ("prompt106 session106 library106 service106 gateway106 storage106", 10),
        ["prompt106", "session106", "library106", "service106", "gateway106", "storage106"],
    ),
    (
        ("prompt106 session106 library106 service106 gateway106 storage106", 18),
        ["prompt106", "session106", "library106", "service106", "gateway106", "storage106"],
    ),
    (
        ("prompt106 session106 library106 service106 gateway106 storage106", 28),
        ["prompt106 session106", "library106 service106", "gateway106 storage106"],
    ),
    (
        ("session106 library106 service106 gateway106 storage106 network106", 6),
        ["session106", "library106", "service106", "gateway106", "storage106", "network106"],
    ),
    (
        ("session106 library106 service106 gateway106 storage106 network106", 10),
        ["session106", "library106", "service106", "gateway106", "storage106", "network106"],
    ),
    (
        ("session106 library106 service106 gateway106 storage106 network106", 18),
        ["session106", "library106", "service106", "gateway106", "storage106", "network106"],
    ),
    (
        ("session106 library106 service106 gateway106 storage106 network106", 28),
        ["session106 library106", "service106 gateway106", "storage106 network106"],
    ),
    (
        ("library106 service106 gateway106 storage106 network106 latency106", 6),
        ["library106", "service106", "gateway106", "storage106", "network106", "latency106"],
    ),
    (
        ("library106 service106 gateway106 storage106 network106 latency106", 10),
        ["library106", "service106", "gateway106", "storage106", "network106", "latency106"],
    ),
    (
        ("library106 service106 gateway106 storage106 network106 latency106", 18),
        ["library106", "service106", "gateway106", "storage106", "network106", "latency106"],
    ),
    (
        ("library106 service106 gateway106 storage106 network106 latency106", 28),
        ["library106 service106", "gateway106 storage106", "network106 latency106"],
    ),
    (
        ("service106 gateway106 storage106 network106 latency106 buffer106", 6),
        ["service106", "gateway106", "storage106", "network106", "latency106", "buffer106"],
    ),
    (
        ("service106 gateway106 storage106 network106 latency106 buffer106", 10),
        ["service106", "gateway106", "storage106", "network106", "latency106", "buffer106"],
    ),
    (
        ("service106 gateway106 storage106 network106 latency106 buffer106", 18),
        ["service106", "gateway106", "storage106", "network106", "latency106", "buffer106"],
    ),
    (
        ("service106 gateway106 storage106 network106 latency106 buffer106", 28),
        ["service106 gateway106", "storage106 network106", "latency106 buffer106"],
    ),
    (
        ("gateway106 storage106 network106 latency106 buffer106 queue106", 6),
        ["gateway106", "storage106", "network106", "latency106", "buffer106", "queue106"],
    ),
    (
        ("gateway106 storage106 network106 latency106 buffer106 queue106", 10),
        ["gateway106", "storage106", "network106", "latency106", "buffer106", "queue106"],
    ),
    (
        ("gateway106 storage106 network106 latency106 buffer106 queue106", 18),
        ["gateway106", "storage106", "network106", "latency106", "buffer106 queue106"],
    ),
    (
        ("gateway106 storage106 network106 latency106 buffer106 queue106", 28),
        ["gateway106 storage106", "network106 latency106", "buffer106 queue106"],
    ),
    (
        ("storage106 network106 latency106 buffer106 queue106 worker106", 6),
        ["storage106", "network106", "latency106", "buffer106", "queue106", "worker106"],
    ),
    (
        ("storage106 network106 latency106 buffer106 queue106 worker106", 10),
        ["storage106", "network106", "latency106", "buffer106", "queue106", "worker106"],
    ),
    (
        ("storage106 network106 latency106 buffer106 queue106 worker106", 18),
        ["storage106", "network106", "latency106", "buffer106 queue106", "worker106"],
    ),
    (
        ("storage106 network106 latency106 buffer106 queue106 worker106", 28),
        ["storage106 network106", "latency106 buffer106", "queue106 worker106"],
    ),
    (
        ("network106 latency106 buffer106 queue106 worker106 kernel106", 6),
        ["network106", "latency106", "buffer106", "queue106", "worker106", "kernel106"],
    ),
    (
        ("network106 latency106 buffer106 queue106 worker106 kernel106", 10),
        ["network106", "latency106", "buffer106", "queue106", "worker106", "kernel106"],
    ),
    (
        ("network106 latency106 buffer106 queue106 worker106 kernel106", 18),
        ["network106", "latency106", "buffer106 queue106", "worker106", "kernel106"],
    ),
    (
        ("network106 latency106 buffer106 queue106 worker106 kernel106", 28),
        ["network106 latency106", "buffer106 queue106 worker106", "kernel106"],
    ),
    (
        ("latency106 buffer106 queue106 worker106 kernel106 signal106", 6),
        ["latency106", "buffer106", "queue106", "worker106", "kernel106", "signal106"],
    ),
    (
        ("latency106 buffer106 queue106 worker106 kernel106 signal106", 10),
        ["latency106", "buffer106", "queue106", "worker106", "kernel106", "signal106"],
    ),
    (
        ("latency106 buffer106 queue106 worker106 kernel106 signal106", 18),
        ["latency106", "buffer106 queue106", "worker106", "kernel106", "signal106"],
    ),
    (
        ("latency106 buffer106 queue106 worker106 kernel106 signal106", 28),
        ["latency106 buffer106", "queue106 worker106 kernel106", "signal106"],
    ),
    (
        ("buffer106 queue106 worker106 kernel106 signal106 packet106", 6),
        ["buffer106", "queue106", "worker106", "kernel106", "signal106", "packet106"],
    ),
    (
        ("buffer106 queue106 worker106 kernel106 signal106 packet106", 10),
        ["buffer106", "queue106", "worker106", "kernel106", "signal106", "packet106"],
    ),
    (
        ("buffer106 queue106 worker106 kernel106 signal106 packet106", 18),
        ["buffer106 queue106", "worker106", "kernel106", "signal106", "packet106"],
    ),
    (
        ("buffer106 queue106 worker106 kernel106 signal106 packet106", 28),
        ["buffer106 queue106 worker106", "kernel106 signal106", "packet106"],
    ),
    (
        ("queue106 worker106 kernel106 signal106 packet106 router106", 6),
        ["queue106", "worker106", "kernel106", "signal106", "packet106", "router106"],
    ),
    (
        ("queue106 worker106 kernel106 signal106 packet106 router106", 10),
        ["queue106", "worker106", "kernel106", "signal106", "packet106", "router106"],
    ),
    (
        ("queue106 worker106 kernel106 signal106 packet106 router106", 18),
        ["queue106 worker106", "kernel106", "signal106", "packet106", "router106"],
    ),
    (
        ("queue106 worker106 kernel106 signal106 packet106 router106", 28),
        ["queue106 worker106 kernel106", "signal106 packet106", "router106"],
    ),
    (
        ("worker106 kernel106 signal106 packet106 router106 cluster106", 6),
        ["worker106", "kernel106", "signal106", "packet106", "router106", "cluster106"],
    ),
    (
        ("worker106 kernel106 signal106 packet106 router106 cluster106", 10),
        ["worker106", "kernel106", "signal106", "packet106", "router106", "cluster106"],
    ),
    (
        ("worker106 kernel106 signal106 packet106 router106 cluster106", 18),
        ["worker106", "kernel106", "signal106", "packet106", "router106", "cluster106"],
    ),
    (
        ("worker106 kernel106 signal106 packet106 router106 cluster106", 28),
        ["worker106 kernel106", "signal106 packet106", "router106 cluster106"],
    ),
    (
        ("kernel106 signal106 packet106 router106 cluster106 mirror106", 6),
        ["kernel106", "signal106", "packet106", "router106", "cluster106", "mirror106"],
    ),
    (
        ("kernel106 signal106 packet106 router106 cluster106 mirror106", 10),
        ["kernel106", "signal106", "packet106", "router106", "cluster106", "mirror106"],
    ),
    (
        ("kernel106 signal106 packet106 router106 cluster106 mirror106", 18),
        ["kernel106", "signal106", "packet106", "router106", "cluster106", "mirror106"],
    ),
    (
        ("kernel106 signal106 packet106 router106 cluster106 mirror106", 28),
        ["kernel106 signal106", "packet106 router106", "cluster106 mirror106"],
    ),
    (
        ("signal106 packet106 router106 cluster106 mirror106 filter106", 6),
        ["signal106", "packet106", "router106", "cluster106", "mirror106", "filter106"],
    ),
    (
        ("signal106 packet106 router106 cluster106 mirror106 filter106", 10),
        ["signal106", "packet106", "router106", "cluster106", "mirror106", "filter106"],
    ),
    (
        ("signal106 packet106 router106 cluster106 mirror106 filter106", 18),
        ["signal106", "packet106", "router106", "cluster106", "mirror106", "filter106"],
    ),
    (
        ("signal106 packet106 router106 cluster106 mirror106 filter106", 28),
        ["signal106 packet106", "router106 cluster106", "mirror106 filter106"],
    ),
    (
        ("packet106 router106 cluster106 mirror106 filter106 ranking106", 6),
        ["packet106", "router106", "cluster106", "mirror106", "filter106", "ranking106"],
    ),
    (
        ("packet106 router106 cluster106 mirror106 filter106 ranking106", 10),
        ["packet106", "router106", "cluster106", "mirror106", "filter106", "ranking106"],
    ),
    (
        ("packet106 router106 cluster106 mirror106 filter106 ranking106", 18),
        ["packet106", "router106", "cluster106", "mirror106", "filter106", "ranking106"],
    ),
    (
        ("packet106 router106 cluster106 mirror106 filter106 ranking106", 28),
        ["packet106 router106", "cluster106 mirror106", "filter106 ranking106"],
    ),
    (
        ("router106 cluster106 mirror106 filter106 ranking106 encoding106", 6),
        ["router106", "cluster106", "mirror106", "filter106", "ranking106", "encoding106"],
    ),
    (
        ("router106 cluster106 mirror106 filter106 ranking106 encoding106", 10),
        ["router106", "cluster106", "mirror106", "filter106", "ranking106", "encoding106"],
    ),
    (
        ("router106 cluster106 mirror106 filter106 ranking106 encoding106", 18),
        ["router106", "cluster106", "mirror106", "filter106", "ranking106", "encoding106"],
    ),
    (
        ("router106 cluster106 mirror106 filter106 ranking106 encoding106", 28),
        ["router106 cluster106", "mirror106 filter106", "ranking106 encoding106"],
    ),
    (
        ("cluster106 mirror106 filter106 ranking106 encoding106 mapping106", 6),
        ["cluster106", "mirror106", "filter106", "ranking106", "encoding106", "mapping106"],
    ),
    (
        ("cluster106 mirror106 filter106 ranking106 encoding106 mapping106", 10),
        ["cluster106", "mirror106", "filter106", "ranking106", "encoding106", "mapping106"],
    ),
    (
        ("cluster106 mirror106 filter106 ranking106 encoding106 mapping106", 18),
        ["cluster106", "mirror106", "filter106", "ranking106", "encoding106", "mapping106"],
    ),
    (
        ("cluster106 mirror106 filter106 ranking106 encoding106 mapping106", 28),
        ["cluster106 mirror106", "filter106 ranking106", "encoding106 mapping106"],
    ),
    (
        ("mirror106 filter106 ranking106 encoding106 mapping106 record106", 6),
        ["mirror106", "filter106", "ranking106", "encoding106", "mapping106", "record106"],
    ),
    (
        ("mirror106 filter106 ranking106 encoding106 mapping106 record106", 10),
        ["mirror106", "filter106", "ranking106", "encoding106", "mapping106", "record106"],
    ),
    (
        ("mirror106 filter106 ranking106 encoding106 mapping106 record106", 18),
        ["mirror106", "filter106", "ranking106", "encoding106", "mapping106", "record106"],
    ),
    (
        ("mirror106 filter106 ranking106 encoding106 mapping106 record106", 28),
        ["mirror106 filter106", "ranking106 encoding106", "mapping106 record106"],
    ),
    (
        ("filter106 ranking106 encoding106 mapping106 record106 candle106", 6),
        ["filter106", "ranking106", "encoding106", "mapping106", "record106", "candle106"],
    ),
    (
        ("filter106 ranking106 encoding106 mapping106 record106 candle106", 10),
        ["filter106", "ranking106", "encoding106", "mapping106", "record106", "candle106"],
    ),
    (
        ("filter106 ranking106 encoding106 mapping106 record106 candle106", 18),
        ["filter106", "ranking106", "encoding106", "mapping106", "record106", "candle106"],
    ),
    (
        ("filter106 ranking106 encoding106 mapping106 record106 candle106", 28),
        ["filter106 ranking106", "encoding106 mapping106", "record106 candle106"],
    ),
    (
        ("ranking106 encoding106 mapping106 record106 candle106 thread106", 6),
        ["ranking106", "encoding106", "mapping106", "record106", "candle106", "thread106"],
    ),
    (
        ("ranking106 encoding106 mapping106 record106 candle106 thread106", 10),
        ["ranking106", "encoding106", "mapping106", "record106", "candle106", "thread106"],
    ),
    (
        ("ranking106 encoding106 mapping106 record106 candle106 thread106", 18),
        ["ranking106", "encoding106", "mapping106", "record106", "candle106", "thread106"],
    ),
    (
        ("ranking106 encoding106 mapping106 record106 candle106 thread106", 28),
        ["ranking106 encoding106", "mapping106 record106", "candle106 thread106"],
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
