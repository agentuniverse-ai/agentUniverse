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
        ("round 157: the quick brown fox jumps over the lazy dog", 4),
        ["round", "157:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", 8),
        ["round", "157: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", 12),
        ["round 157:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", 16),
        ["round 157: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", 24),
        ["round 157: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 157: the quick brown fox jumps over the lazy dog", 32),
        ["round 157: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", 4),
        ["round", "157:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", 8),
        ["round", "157:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", 12),
        ["round 157:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", 16),
        ["round 157:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", 24),
        ["round 157: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 157: agentuniverse is a framework for multi agents", 32),
        ["round 157: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", 4),
        ["round", "157:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", 8),
        ["round", "157:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", 12),
        ["round 157:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", 16),
        ["round 157:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", 24),
        ["round 157: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 157: knowledge stored as vectors enables retrieval", 32),
        ["round 157: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 157: the processor reads the record then stops", 4),
        ["round", "157:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 157: the processor reads the record then stops", 8),
        ["round", "157: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 157: the processor reads the record then stops", 12),
        ["round 157:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 157: the processor reads the record then stops", 16),
        ["round 157: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 157: the processor reads the record then stops", 24),
        ["round 157: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 157: the processor reads the record then stops", 32),
        ["round 157: the processor reads", "the record then stops"],
    ),
    (
        ("round 157: a worker pulls the next task from the queue", 4),
        ["round", "157:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 157: a worker pulls the next task from the queue", 8),
        ["round", "157: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 157: a worker pulls the next task from the queue", 12),
        ["round 157: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 157: a worker pulls the next task from the queue", 16),
        ["round 157: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 157: a worker pulls the next task from the queue", 24),
        ["round 157: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 157: a worker pulls the next task from the queue", 32),
        ["round 157: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 157: signals travel through the network layer", 4),
        ["round", "157:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 157: signals travel through the network layer", 8),
        ["round", "157:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 157: signals travel through the network layer", 12),
        ["round 157:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 157: signals travel through the network layer", 16),
        ["round 157:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 157: signals travel through the network layer", 24),
        ["round 157: signals", "travel through the", "network layer"],
    ),
    (
        ("round 157: signals travel through the network layer", 32),
        ["round 157: signals travel", "through the network layer"],
    ),
    (
        ("round 157: the gateway routes each request by policy", 4),
        ["round", "157:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 157: the gateway routes each request by policy", 8),
        ["round", "157: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 157: the gateway routes each request by policy", 12),
        ["round 157:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 157: the gateway routes each request by policy", 16),
        ["round 157: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 157: the gateway routes each request by policy", 24),
        ["round 157: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 157: the gateway routes each request by policy", 32),
        ["round 157: the gateway routes", "each request by policy"],
    ),
    (
        ("round 157: memory grows until the buffer is full", 4),
        ["round", "157:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 157: memory grows until the buffer is full", 8),
        ["round", "157:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 157: memory grows until the buffer is full", 12),
        ["round 157:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 157: memory grows until the buffer is full", 16),
        ["round 157:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 157: memory grows until the buffer is full", 24), ["round 157: memory grows", "until the buffer is full"]),
    (("round 157: memory grows until the buffer is full", 32), ["round 157: memory grows until", "the buffer is full"]),
    (
        ("round 157: the cluster mirrors every packet twice", 4),
        ["round", "157:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 157: the cluster mirrors every packet twice", 8),
        ["round", "157: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 157: the cluster mirrors every packet twice", 12),
        ["round 157:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 157: the cluster mirrors every packet twice", 16),
        ["round 157: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 157: the cluster mirrors every packet twice", 24),
        ["round 157: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 157: the cluster mirrors every packet twice", 32),
        ["round 157: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", 4),
        ["round", "157:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", 8),
        ["round", "157:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", 12),
        ["round 157:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", 16),
        ["round 157:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", 24),
        ["round 157: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 157: ranking uses tokens learned from the corpus", 32),
        ["round 157: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 157: a long session ends when the candle dies", 4),
        ["round", "157:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 157: a long session ends when the candle dies", 8),
        ["round", "157: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 157: a long session ends when the candle dies", 12),
        ["round 157: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 157: a long session ends when the candle dies", 16),
        ["round 157: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 157: a long session ends when the candle dies", 24),
        ["round 157: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 157: a long session ends when the candle dies", 32),
        ["round 157: a long session ends", "when the candle dies"],
    ),
    (
        ("round 157: encode the prompt then map the result", 4),
        ["round", "157:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 157: encode the prompt then map the result", 8),
        ["round", "157:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 157: encode the prompt then map the result", 12),
        ["round 157:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 157: encode the prompt then map the result", 16),
        ["round 157:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 157: encode the prompt then map the result", 24),
        ["round 157: encode the", "prompt then map the", "result"],
    ),
    (("round 157: encode the prompt then map the result", 32), ["round 157: encode the prompt", "then map the result"]),
    (
        ("round 157: the kernel wakes the worker at dawn", 4),
        ["round", "157:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 157: the kernel wakes the worker at dawn", 8),
        ["round", "157: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 157: the kernel wakes the worker at dawn", 12),
        ["round 157:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 157: the kernel wakes the worker at dawn", 16), ["round 157: the", "kernel wakes the", "worker at dawn"]),
    (("round 157: the kernel wakes the worker at dawn", 24), ["round 157: the kernel", "wakes the worker at dawn"]),
    (("round 157: the kernel wakes the worker at dawn", 32), ["round 157: the kernel wakes the", "worker at dawn"]),
    (
        ("round 157: service latency drops after the patch", 4),
        ["round", "157:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 157: service latency drops after the patch", 8),
        ["round", "157:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 157: service latency drops after the patch", 12),
        ["round 157:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 157: service latency drops after the patch", 16),
        ["round 157:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 157: service latency drops after the patch", 24),
        ["round 157: service", "latency drops after the", "patch"],
    ),
    (("round 157: service latency drops after the patch", 32), ["round 157: service latency drops", "after the patch"]),
    (
        ("round 157: the library caches every vector it sees", 4),
        ["round", "157:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 157: the library caches every vector it sees", 8),
        ["round", "157: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 157: the library caches every vector it sees", 12),
        ["round 157:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 157: the library caches every vector it sees", 16),
        ["round 157: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 157: the library caches every vector it sees", 24),
        ["round 157: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 157: the library caches every vector it sees", 32),
        ["round 157: the library caches", "every vector it sees"],
    ),
    (
        ("round 157: agents argue then the debate resolves", 4),
        ["round", "157:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 157: agents argue then the debate resolves", 8),
        ["round", "157:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 157: agents argue then the debate resolves", 12),
        ["round 157:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 157: agents argue then the debate resolves", 16),
        ["round 157:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 157: agents argue then the debate resolves", 24), ["round 157: agents argue", "then the debate resolves"]),
    (("round 157: agents argue then the debate resolves", 32), ["round 157: agents argue then the", "debate resolves"]),
    (
        ("round 157: the filter keeps only strong matches", 4),
        ["round", "157:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 157: the filter keeps only strong matches", 8),
        ["round", "157: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 157: the filter keeps only strong matches", 12),
        ["round 157:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 157: the filter keeps only strong matches", 16),
        ["round 157: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 157: the filter keeps only strong matches", 24),
        ["round 157: the filter", "keeps only strong", "matches"],
    ),
    (("round 157: the filter keeps only strong matches", 32), ["round 157: the filter keeps only", "strong matches"]),
    (
        ("round 157: the model answers with a short reply", 4),
        ["round", "157:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 157: the model answers with a short reply", 8),
        ["round", "157: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 157: the model answers with a short reply", 12),
        ["round 157:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 157: the model answers with a short reply", 16),
        ["round 157: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 157: the model answers with a short reply", 24),
        ["round 157: the model", "answers with a short", "reply"],
    ),
    (("round 157: the model answers with a short reply", 32), ["round 157: the model answers", "with a short reply"]),
    (
        ("round 157: the recorder stores the reasoning trace", 4),
        ["round", "157:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 157: the recorder stores the reasoning trace", 8),
        ["round", "157: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 157: the recorder stores the reasoning trace", 12),
        ["round 157:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 157: the recorder stores the reasoning trace", 16),
        ["round 157: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 157: the recorder stores the reasoning trace", 24),
        ["round 157: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 157: the recorder stores the reasoning trace", 32),
        ["round 157: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 157: the angel watches the processor run", 4),
        ["round", "157:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 157: the angel watches the processor run", 8),
        ["round", "157: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 157: the angel watches the processor run", 12),
        ["round 157:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 157: the angel watches the processor run", 16),
        ["round 157: the", "angel watches", "the processor", "run"],
    ),
    (("round 157: the angel watches the processor run", 24), ["round 157: the angel", "watches the processor", "run"]),
    (("round 157: the angel watches the processor run", 32), ["round 157: the angel watches the", "processor run"]),
    (
        ("round 157: angle of the vector decides the match", 4),
        ["round", "157:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 157: angle of the vector decides the match", 8),
        ["round", "157:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 157: angle of the vector decides the match", 12),
        ["round 157:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 157: angle of the vector decides the match", 16),
        ["round 157: angle", "of the vector", "decides the", "match"],
    ),
    (("round 157: angle of the vector decides the match", 24), ["round 157: angle of the", "vector decides the match"]),
    (("round 157: angle of the vector decides the match", 32), ["round 157: angle of the vector", "decides the match"]),
    (
        ("round 157: the candle burns twice as long at night", 4),
        ["round", "157:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 157: the candle burns twice as long at night", 8),
        ["round", "157: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 157: the candle burns twice as long at night", 12),
        ["round 157:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 157: the candle burns twice as long at night", 16),
        ["round 157: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 157: the candle burns twice as long at night", 24),
        ["round 157: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 157: the candle burns twice as long at night", 32),
        ["round 157: the candle burns", "twice as long at night"],
    ),
    (
        ("round 157: a mirror of the universe in one line", 4),
        ["round", "157:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 157: a mirror of the universe in one line", 8),
        ["round", "157: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 157: a mirror of the universe in one line", 12),
        ["round 157: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 157: a mirror of the universe in one line", 16),
        ["round 157: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 157: a mirror of the universe in one line", 24), ["round 157: a mirror of", "the universe in one line"]),
    (("round 157: a mirror of the universe in one line", 32), ["round 157: a mirror of the", "universe in one line"]),
    (
        ("round 157: the queue drains before the storm", 4),
        ["round", "157:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 157: the queue drains before the storm", 8),
        ["round", "157: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 157: the queue drains before the storm", 12),
        ["round 157:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 157: the queue drains before the storm", 16), ["round 157: the", "queue drains", "before the storm"]),
    (("round 157: the queue drains before the storm", 24), ["round 157: the queue", "drains before the storm"]),
    (("round 157: the queue drains before the storm", 32), ["round 157: the queue drains", "before the storm"]),
    (
        ("kitten157 sitting157 agent157 angle157 universe157 memory157", 6),
        ["kitten157", "sitting157", "agent157", "angle157", "universe157", "memory157"],
    ),
    (
        ("kitten157 sitting157 agent157 angle157 universe157 memory157", 10),
        ["kitten157", "sitting157", "agent157", "angle157", "universe157", "memory157"],
    ),
    (
        ("kitten157 sitting157 agent157 angle157 universe157 memory157", 18),
        ["kitten157", "sitting157", "agent157 angle157", "universe157", "memory157"],
    ),
    (
        ("kitten157 sitting157 agent157 angle157 universe157 memory157", 28),
        ["kitten157 sitting157", "agent157 angle157", "universe157 memory157"],
    ),
    (
        ("sitting157 agent157 angle157 universe157 memory157 stream157", 6),
        ["sitting157", "agent157", "angle157", "universe157", "memory157", "stream157"],
    ),
    (
        ("sitting157 agent157 angle157 universe157 memory157 stream157", 10),
        ["sitting157", "agent157", "angle157", "universe157", "memory157", "stream157"],
    ),
    (
        ("sitting157 agent157 angle157 universe157 memory157 stream157", 18),
        ["sitting157", "agent157 angle157", "universe157", "memory157", "stream157"],
    ),
    (
        ("sitting157 agent157 angle157 universe157 memory157 stream157", 28),
        ["sitting157 agent157 angle157", "universe157 memory157", "stream157"],
    ),
    (
        ("agent157 angle157 universe157 memory157 stream157 context157", 6),
        ["agent157", "angle157", "universe157", "memory157", "stream157", "context157"],
    ),
    (
        ("agent157 angle157 universe157 memory157 stream157 context157", 10),
        ["agent157", "angle157", "universe157", "memory157", "stream157", "context157"],
    ),
    (
        ("agent157 angle157 universe157 memory157 stream157 context157", 18),
        ["agent157 angle157", "universe157", "memory157", "stream157", "context157"],
    ),
    (
        ("agent157 angle157 universe157 memory157 stream157 context157", 28),
        ["agent157 angle157", "universe157 memory157", "stream157 context157"],
    ),
    (
        ("angle157 universe157 memory157 stream157 context157 knowledge157", 6),
        ["angle157", "universe157", "memory157", "stream157", "context157", "knowledge157"],
    ),
    (
        ("angle157 universe157 memory157 stream157 context157 knowledge157", 10),
        ["angle157", "universe157", "memory157", "stream157", "context157", "knowledge157"],
    ),
    (
        ("angle157 universe157 memory157 stream157 context157 knowledge157", 18),
        ["angle157", "universe157", "memory157", "stream157", "context157", "knowledge157"],
    ),
    (
        ("angle157 universe157 memory157 stream157 context157 knowledge157", 28),
        ["angle157 universe157", "memory157 stream157", "context157 knowledge157"],
    ),
    (
        ("universe157 memory157 stream157 context157 knowledge157 vector157", 6),
        ["universe157", "memory157", "stream157", "context157", "knowledge157", "vector157"],
    ),
    (
        ("universe157 memory157 stream157 context157 knowledge157 vector157", 10),
        ["universe157", "memory157", "stream157", "context157", "knowledge157", "vector157"],
    ),
    (
        ("universe157 memory157 stream157 context157 knowledge157 vector157", 18),
        ["universe157", "memory157", "stream157", "context157", "knowledge157", "vector157"],
    ),
    (
        ("universe157 memory157 stream157 context157 knowledge157 vector157", 28),
        ["universe157 memory157", "stream157 context157", "knowledge157 vector157"],
    ),
    (
        ("memory157 stream157 context157 knowledge157 vector157 processor157", 6),
        ["memory157", "stream157", "context157", "knowledge157", "vector157", "processor157"],
    ),
    (
        ("memory157 stream157 context157 knowledge157 vector157 processor157", 10),
        ["memory157", "stream157", "context157", "knowledge157", "vector157", "processor157"],
    ),
    (
        ("memory157 stream157 context157 knowledge157 vector157 processor157", 18),
        ["memory157", "stream157", "context157", "knowledge157", "vector157", "processor157"],
    ),
    (
        ("memory157 stream157 context157 knowledge157 vector157 processor157", 28),
        ["memory157 stream157", "context157 knowledge157", "vector157 processor157"],
    ),
    (
        ("stream157 context157 knowledge157 vector157 processor157 reasoning157", 6),
        ["stream157", "context157", "knowledge157", "vector157", "processor157", "reasoning157"],
    ),
    (
        ("stream157 context157 knowledge157 vector157 processor157 reasoning157", 10),
        ["stream157", "context157", "knowledge157", "vector157", "processor157", "reasoning157"],
    ),
    (
        ("stream157 context157 knowledge157 vector157 processor157 reasoning157", 18),
        ["stream157", "context157", "knowledge157", "vector157", "processor157", "reasoning157"],
    ),
    (
        ("stream157 context157 knowledge157 vector157 processor157 reasoning157", 28),
        ["stream157 context157", "knowledge157 vector157", "processor157 reasoning157"],
    ),
    (
        ("context157 knowledge157 vector157 processor157 reasoning157 machine157", 6),
        ["context157", "knowledge157", "vector157", "processor157", "reasoning157", "machine157"],
    ),
    (
        ("context157 knowledge157 vector157 processor157 reasoning157 machine157", 10),
        ["context157", "knowledge157", "vector157", "processor157", "reasoning157", "machine157"],
    ),
    (
        ("context157 knowledge157 vector157 processor157 reasoning157 machine157", 18),
        ["context157", "knowledge157", "vector157", "processor157", "reasoning157", "machine157"],
    ),
    (
        ("context157 knowledge157 vector157 processor157 reasoning157 machine157", 28),
        ["context157 knowledge157", "vector157 processor157", "reasoning157 machine157"],
    ),
    (
        ("knowledge157 vector157 processor157 reasoning157 machine157 learning157", 6),
        ["knowledge157", "vector157", "processor157", "reasoning157", "machine157", "learning157"],
    ),
    (
        ("knowledge157 vector157 processor157 reasoning157 machine157 learning157", 10),
        ["knowledge157", "vector157", "processor157", "reasoning157", "machine157", "learning157"],
    ),
    (
        ("knowledge157 vector157 processor157 reasoning157 machine157 learning157", 18),
        ["knowledge157", "vector157", "processor157", "reasoning157", "machine157", "learning157"],
    ),
    (
        ("knowledge157 vector157 processor157 reasoning157 machine157 learning157", 28),
        ["knowledge157 vector157", "processor157 reasoning157", "machine157 learning157"],
    ),
    (
        ("vector157 processor157 reasoning157 machine157 learning157 model157", 6),
        ["vector157", "processor157", "reasoning157", "machine157", "learning157", "model157"],
    ),
    (
        ("vector157 processor157 reasoning157 machine157 learning157 model157", 10),
        ["vector157", "processor157", "reasoning157", "machine157", "learning157", "model157"],
    ),
    (
        ("vector157 processor157 reasoning157 machine157 learning157 model157", 18),
        ["vector157", "processor157", "reasoning157", "machine157", "learning157", "model157"],
    ),
    (
        ("vector157 processor157 reasoning157 machine157 learning157 model157", 28),
        ["vector157 processor157", "reasoning157 machine157", "learning157 model157"],
    ),
    (
        ("processor157 reasoning157 machine157 learning157 model157 token157", 6),
        ["processor157", "reasoning157", "machine157", "learning157", "model157", "token157"],
    ),
    (
        ("processor157 reasoning157 machine157 learning157 model157 token157", 10),
        ["processor157", "reasoning157", "machine157", "learning157", "model157", "token157"],
    ),
    (
        ("processor157 reasoning157 machine157 learning157 model157 token157", 18),
        ["processor157", "reasoning157", "machine157", "learning157", "model157 token157"],
    ),
    (
        ("processor157 reasoning157 machine157 learning157 model157 token157", 28),
        ["processor157 reasoning157", "machine157 learning157", "model157 token157"],
    ),
    (
        ("reasoning157 machine157 learning157 model157 token157 prompt157", 6),
        ["reasoning157", "machine157", "learning157", "model157", "token157", "prompt157"],
    ),
    (
        ("reasoning157 machine157 learning157 model157 token157 prompt157", 10),
        ["reasoning157", "machine157", "learning157", "model157", "token157", "prompt157"],
    ),
    (
        ("reasoning157 machine157 learning157 model157 token157 prompt157", 18),
        ["reasoning157", "machine157", "learning157", "model157 token157", "prompt157"],
    ),
    (
        ("reasoning157 machine157 learning157 model157 token157 prompt157", 28),
        ["reasoning157 machine157", "learning157 model157", "token157 prompt157"],
    ),
    (
        ("machine157 learning157 model157 token157 prompt157 session157", 6),
        ["machine157", "learning157", "model157", "token157", "prompt157", "session157"],
    ),
    (
        ("machine157 learning157 model157 token157 prompt157 session157", 10),
        ["machine157", "learning157", "model157", "token157", "prompt157", "session157"],
    ),
    (
        ("machine157 learning157 model157 token157 prompt157 session157", 18),
        ["machine157", "learning157", "model157 token157", "prompt157", "session157"],
    ),
    (
        ("machine157 learning157 model157 token157 prompt157 session157", 28),
        ["machine157 learning157", "model157 token157 prompt157", "session157"],
    ),
    (
        ("learning157 model157 token157 prompt157 session157 library157", 6),
        ["learning157", "model157", "token157", "prompt157", "session157", "library157"],
    ),
    (
        ("learning157 model157 token157 prompt157 session157 library157", 10),
        ["learning157", "model157", "token157", "prompt157", "session157", "library157"],
    ),
    (
        ("learning157 model157 token157 prompt157 session157 library157", 18),
        ["learning157", "model157 token157", "prompt157", "session157", "library157"],
    ),
    (
        ("learning157 model157 token157 prompt157 session157 library157", 28),
        ["learning157 model157", "token157 prompt157", "session157 library157"],
    ),
    (
        ("model157 token157 prompt157 session157 library157 service157", 6),
        ["model157", "token157", "prompt157", "session157", "library157", "service157"],
    ),
    (
        ("model157 token157 prompt157 session157 library157 service157", 10),
        ["model157", "token157", "prompt157", "session157", "library157", "service157"],
    ),
    (
        ("model157 token157 prompt157 session157 library157 service157", 18),
        ["model157 token157", "prompt157", "session157", "library157", "service157"],
    ),
    (
        ("model157 token157 prompt157 session157 library157 service157", 28),
        ["model157 token157 prompt157", "session157 library157", "service157"],
    ),
    (
        ("token157 prompt157 session157 library157 service157 gateway157", 6),
        ["token157", "prompt157", "session157", "library157", "service157", "gateway157"],
    ),
    (
        ("token157 prompt157 session157 library157 service157 gateway157", 10),
        ["token157", "prompt157", "session157", "library157", "service157", "gateway157"],
    ),
    (
        ("token157 prompt157 session157 library157 service157 gateway157", 18),
        ["token157 prompt157", "session157", "library157", "service157", "gateway157"],
    ),
    (
        ("token157 prompt157 session157 library157 service157 gateway157", 28),
        ["token157 prompt157", "session157 library157", "service157 gateway157"],
    ),
    (
        ("prompt157 session157 library157 service157 gateway157 storage157", 6),
        ["prompt157", "session157", "library157", "service157", "gateway157", "storage157"],
    ),
    (
        ("prompt157 session157 library157 service157 gateway157 storage157", 10),
        ["prompt157", "session157", "library157", "service157", "gateway157", "storage157"],
    ),
    (
        ("prompt157 session157 library157 service157 gateway157 storage157", 18),
        ["prompt157", "session157", "library157", "service157", "gateway157", "storage157"],
    ),
    (
        ("prompt157 session157 library157 service157 gateway157 storage157", 28),
        ["prompt157 session157", "library157 service157", "gateway157 storage157"],
    ),
    (
        ("session157 library157 service157 gateway157 storage157 network157", 6),
        ["session157", "library157", "service157", "gateway157", "storage157", "network157"],
    ),
    (
        ("session157 library157 service157 gateway157 storage157 network157", 10),
        ["session157", "library157", "service157", "gateway157", "storage157", "network157"],
    ),
    (
        ("session157 library157 service157 gateway157 storage157 network157", 18),
        ["session157", "library157", "service157", "gateway157", "storage157", "network157"],
    ),
    (
        ("session157 library157 service157 gateway157 storage157 network157", 28),
        ["session157 library157", "service157 gateway157", "storage157 network157"],
    ),
    (
        ("library157 service157 gateway157 storage157 network157 latency157", 6),
        ["library157", "service157", "gateway157", "storage157", "network157", "latency157"],
    ),
    (
        ("library157 service157 gateway157 storage157 network157 latency157", 10),
        ["library157", "service157", "gateway157", "storage157", "network157", "latency157"],
    ),
    (
        ("library157 service157 gateway157 storage157 network157 latency157", 18),
        ["library157", "service157", "gateway157", "storage157", "network157", "latency157"],
    ),
    (
        ("library157 service157 gateway157 storage157 network157 latency157", 28),
        ["library157 service157", "gateway157 storage157", "network157 latency157"],
    ),
    (
        ("service157 gateway157 storage157 network157 latency157 buffer157", 6),
        ["service157", "gateway157", "storage157", "network157", "latency157", "buffer157"],
    ),
    (
        ("service157 gateway157 storage157 network157 latency157 buffer157", 10),
        ["service157", "gateway157", "storage157", "network157", "latency157", "buffer157"],
    ),
    (
        ("service157 gateway157 storage157 network157 latency157 buffer157", 18),
        ["service157", "gateway157", "storage157", "network157", "latency157", "buffer157"],
    ),
    (
        ("service157 gateway157 storage157 network157 latency157 buffer157", 28),
        ["service157 gateway157", "storage157 network157", "latency157 buffer157"],
    ),
    (
        ("gateway157 storage157 network157 latency157 buffer157 queue157", 6),
        ["gateway157", "storage157", "network157", "latency157", "buffer157", "queue157"],
    ),
    (
        ("gateway157 storage157 network157 latency157 buffer157 queue157", 10),
        ["gateway157", "storage157", "network157", "latency157", "buffer157", "queue157"],
    ),
    (
        ("gateway157 storage157 network157 latency157 buffer157 queue157", 18),
        ["gateway157", "storage157", "network157", "latency157", "buffer157 queue157"],
    ),
    (
        ("gateway157 storage157 network157 latency157 buffer157 queue157", 28),
        ["gateway157 storage157", "network157 latency157", "buffer157 queue157"],
    ),
    (
        ("storage157 network157 latency157 buffer157 queue157 worker157", 6),
        ["storage157", "network157", "latency157", "buffer157", "queue157", "worker157"],
    ),
    (
        ("storage157 network157 latency157 buffer157 queue157 worker157", 10),
        ["storage157", "network157", "latency157", "buffer157", "queue157", "worker157"],
    ),
    (
        ("storage157 network157 latency157 buffer157 queue157 worker157", 18),
        ["storage157", "network157", "latency157", "buffer157 queue157", "worker157"],
    ),
    (
        ("storage157 network157 latency157 buffer157 queue157 worker157", 28),
        ["storage157 network157", "latency157 buffer157", "queue157 worker157"],
    ),
    (
        ("network157 latency157 buffer157 queue157 worker157 kernel157", 6),
        ["network157", "latency157", "buffer157", "queue157", "worker157", "kernel157"],
    ),
    (
        ("network157 latency157 buffer157 queue157 worker157 kernel157", 10),
        ["network157", "latency157", "buffer157", "queue157", "worker157", "kernel157"],
    ),
    (
        ("network157 latency157 buffer157 queue157 worker157 kernel157", 18),
        ["network157", "latency157", "buffer157 queue157", "worker157", "kernel157"],
    ),
    (
        ("network157 latency157 buffer157 queue157 worker157 kernel157", 28),
        ["network157 latency157", "buffer157 queue157 worker157", "kernel157"],
    ),
    (
        ("latency157 buffer157 queue157 worker157 kernel157 signal157", 6),
        ["latency157", "buffer157", "queue157", "worker157", "kernel157", "signal157"],
    ),
    (
        ("latency157 buffer157 queue157 worker157 kernel157 signal157", 10),
        ["latency157", "buffer157", "queue157", "worker157", "kernel157", "signal157"],
    ),
    (
        ("latency157 buffer157 queue157 worker157 kernel157 signal157", 18),
        ["latency157", "buffer157 queue157", "worker157", "kernel157", "signal157"],
    ),
    (
        ("latency157 buffer157 queue157 worker157 kernel157 signal157", 28),
        ["latency157 buffer157", "queue157 worker157 kernel157", "signal157"],
    ),
    (
        ("buffer157 queue157 worker157 kernel157 signal157 packet157", 6),
        ["buffer157", "queue157", "worker157", "kernel157", "signal157", "packet157"],
    ),
    (
        ("buffer157 queue157 worker157 kernel157 signal157 packet157", 10),
        ["buffer157", "queue157", "worker157", "kernel157", "signal157", "packet157"],
    ),
    (
        ("buffer157 queue157 worker157 kernel157 signal157 packet157", 18),
        ["buffer157 queue157", "worker157", "kernel157", "signal157", "packet157"],
    ),
    (
        ("buffer157 queue157 worker157 kernel157 signal157 packet157", 28),
        ["buffer157 queue157 worker157", "kernel157 signal157", "packet157"],
    ),
    (
        ("queue157 worker157 kernel157 signal157 packet157 router157", 6),
        ["queue157", "worker157", "kernel157", "signal157", "packet157", "router157"],
    ),
    (
        ("queue157 worker157 kernel157 signal157 packet157 router157", 10),
        ["queue157", "worker157", "kernel157", "signal157", "packet157", "router157"],
    ),
    (
        ("queue157 worker157 kernel157 signal157 packet157 router157", 18),
        ["queue157 worker157", "kernel157", "signal157", "packet157", "router157"],
    ),
    (
        ("queue157 worker157 kernel157 signal157 packet157 router157", 28),
        ["queue157 worker157 kernel157", "signal157 packet157", "router157"],
    ),
    (
        ("worker157 kernel157 signal157 packet157 router157 cluster157", 6),
        ["worker157", "kernel157", "signal157", "packet157", "router157", "cluster157"],
    ),
    (
        ("worker157 kernel157 signal157 packet157 router157 cluster157", 10),
        ["worker157", "kernel157", "signal157", "packet157", "router157", "cluster157"],
    ),
    (
        ("worker157 kernel157 signal157 packet157 router157 cluster157", 18),
        ["worker157", "kernel157", "signal157", "packet157", "router157", "cluster157"],
    ),
    (
        ("worker157 kernel157 signal157 packet157 router157 cluster157", 28),
        ["worker157 kernel157", "signal157 packet157", "router157 cluster157"],
    ),
    (
        ("kernel157 signal157 packet157 router157 cluster157 mirror157", 6),
        ["kernel157", "signal157", "packet157", "router157", "cluster157", "mirror157"],
    ),
    (
        ("kernel157 signal157 packet157 router157 cluster157 mirror157", 10),
        ["kernel157", "signal157", "packet157", "router157", "cluster157", "mirror157"],
    ),
    (
        ("kernel157 signal157 packet157 router157 cluster157 mirror157", 18),
        ["kernel157", "signal157", "packet157", "router157", "cluster157", "mirror157"],
    ),
    (
        ("kernel157 signal157 packet157 router157 cluster157 mirror157", 28),
        ["kernel157 signal157", "packet157 router157", "cluster157 mirror157"],
    ),
    (
        ("signal157 packet157 router157 cluster157 mirror157 filter157", 6),
        ["signal157", "packet157", "router157", "cluster157", "mirror157", "filter157"],
    ),
    (
        ("signal157 packet157 router157 cluster157 mirror157 filter157", 10),
        ["signal157", "packet157", "router157", "cluster157", "mirror157", "filter157"],
    ),
    (
        ("signal157 packet157 router157 cluster157 mirror157 filter157", 18),
        ["signal157", "packet157", "router157", "cluster157", "mirror157", "filter157"],
    ),
    (
        ("signal157 packet157 router157 cluster157 mirror157 filter157", 28),
        ["signal157 packet157", "router157 cluster157", "mirror157 filter157"],
    ),
    (
        ("packet157 router157 cluster157 mirror157 filter157 ranking157", 6),
        ["packet157", "router157", "cluster157", "mirror157", "filter157", "ranking157"],
    ),
    (
        ("packet157 router157 cluster157 mirror157 filter157 ranking157", 10),
        ["packet157", "router157", "cluster157", "mirror157", "filter157", "ranking157"],
    ),
    (
        ("packet157 router157 cluster157 mirror157 filter157 ranking157", 18),
        ["packet157", "router157", "cluster157", "mirror157", "filter157", "ranking157"],
    ),
    (
        ("packet157 router157 cluster157 mirror157 filter157 ranking157", 28),
        ["packet157 router157", "cluster157 mirror157", "filter157 ranking157"],
    ),
    (
        ("router157 cluster157 mirror157 filter157 ranking157 encoding157", 6),
        ["router157", "cluster157", "mirror157", "filter157", "ranking157", "encoding157"],
    ),
    (
        ("router157 cluster157 mirror157 filter157 ranking157 encoding157", 10),
        ["router157", "cluster157", "mirror157", "filter157", "ranking157", "encoding157"],
    ),
    (
        ("router157 cluster157 mirror157 filter157 ranking157 encoding157", 18),
        ["router157", "cluster157", "mirror157", "filter157", "ranking157", "encoding157"],
    ),
    (
        ("router157 cluster157 mirror157 filter157 ranking157 encoding157", 28),
        ["router157 cluster157", "mirror157 filter157", "ranking157 encoding157"],
    ),
    (
        ("cluster157 mirror157 filter157 ranking157 encoding157 mapping157", 6),
        ["cluster157", "mirror157", "filter157", "ranking157", "encoding157", "mapping157"],
    ),
    (
        ("cluster157 mirror157 filter157 ranking157 encoding157 mapping157", 10),
        ["cluster157", "mirror157", "filter157", "ranking157", "encoding157", "mapping157"],
    ),
    (
        ("cluster157 mirror157 filter157 ranking157 encoding157 mapping157", 18),
        ["cluster157", "mirror157", "filter157", "ranking157", "encoding157", "mapping157"],
    ),
    (
        ("cluster157 mirror157 filter157 ranking157 encoding157 mapping157", 28),
        ["cluster157 mirror157", "filter157 ranking157", "encoding157 mapping157"],
    ),
    (
        ("mirror157 filter157 ranking157 encoding157 mapping157 record157", 6),
        ["mirror157", "filter157", "ranking157", "encoding157", "mapping157", "record157"],
    ),
    (
        ("mirror157 filter157 ranking157 encoding157 mapping157 record157", 10),
        ["mirror157", "filter157", "ranking157", "encoding157", "mapping157", "record157"],
    ),
    (
        ("mirror157 filter157 ranking157 encoding157 mapping157 record157", 18),
        ["mirror157", "filter157", "ranking157", "encoding157", "mapping157", "record157"],
    ),
    (
        ("mirror157 filter157 ranking157 encoding157 mapping157 record157", 28),
        ["mirror157 filter157", "ranking157 encoding157", "mapping157 record157"],
    ),
    (
        ("filter157 ranking157 encoding157 mapping157 record157 candle157", 6),
        ["filter157", "ranking157", "encoding157", "mapping157", "record157", "candle157"],
    ),
    (
        ("filter157 ranking157 encoding157 mapping157 record157 candle157", 10),
        ["filter157", "ranking157", "encoding157", "mapping157", "record157", "candle157"],
    ),
    (
        ("filter157 ranking157 encoding157 mapping157 record157 candle157", 18),
        ["filter157", "ranking157", "encoding157", "mapping157", "record157", "candle157"],
    ),
    (
        ("filter157 ranking157 encoding157 mapping157 record157 candle157", 28),
        ["filter157 ranking157", "encoding157 mapping157", "record157 candle157"],
    ),
    (
        ("ranking157 encoding157 mapping157 record157 candle157 thread157", 6),
        ["ranking157", "encoding157", "mapping157", "record157", "candle157", "thread157"],
    ),
    (
        ("ranking157 encoding157 mapping157 record157 candle157 thread157", 10),
        ["ranking157", "encoding157", "mapping157", "record157", "candle157", "thread157"],
    ),
    (
        ("ranking157 encoding157 mapping157 record157 candle157 thread157", 18),
        ["ranking157", "encoding157", "mapping157", "record157", "candle157", "thread157"],
    ),
    (
        ("ranking157 encoding157 mapping157 record157 candle157 thread157", 28),
        ["ranking157 encoding157", "mapping157 record157", "candle157 thread157"],
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
