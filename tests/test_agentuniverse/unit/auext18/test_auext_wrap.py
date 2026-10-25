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
        ("round 18: the quick brown fox jumps over the lazy dog", 4),
        ["round", "18:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 18: the quick brown fox jumps over the lazy dog", 8),
        ["round", "18: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 18: the quick brown fox jumps over the lazy dog", 12),
        ["round 18:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 18: the quick brown fox jumps over the lazy dog", 16),
        ["round 18: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 18: the quick brown fox jumps over the lazy dog", 24),
        ["round 18: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 18: the quick brown fox jumps over the lazy dog", 32),
        ["round 18: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 18: agentuniverse is a framework for multi agents", 4),
        ["round", "18:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 18: agentuniverse is a framework for multi agents", 8),
        ["round", "18:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 18: agentuniverse is a framework for multi agents", 12),
        ["round 18:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 18: agentuniverse is a framework for multi agents", 16),
        ["round 18:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 18: agentuniverse is a framework for multi agents", 24),
        ["round 18: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 18: agentuniverse is a framework for multi agents", 32),
        ["round 18: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 18: knowledge stored as vectors enables retrieval", 4),
        ["round", "18:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 18: knowledge stored as vectors enables retrieval", 8),
        ["round", "18:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 18: knowledge stored as vectors enables retrieval", 12),
        ["round 18:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 18: knowledge stored as vectors enables retrieval", 16),
        ["round 18:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 18: knowledge stored as vectors enables retrieval", 24),
        ["round 18: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 18: knowledge stored as vectors enables retrieval", 32),
        ["round 18: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 18: the processor reads the record then stops", 4),
        ["round", "18:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 18: the processor reads the record then stops", 8),
        ["round", "18: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 18: the processor reads the record then stops", 12),
        ["round 18:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 18: the processor reads the record then stops", 16),
        ["round 18: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 18: the processor reads the record then stops", 24),
        ["round 18: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 18: the processor reads the record then stops", 32),
        ["round 18: the processor reads", "the record then stops"],
    ),
    (
        ("round 18: a worker pulls the next task from the queue", 4),
        ["round", "18:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 18: a worker pulls the next task from the queue", 8),
        ["round", "18: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 18: a worker pulls the next task from the queue", 12),
        ["round 18: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 18: a worker pulls the next task from the queue", 16),
        ["round 18: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 18: a worker pulls the next task from the queue", 24),
        ["round 18: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 18: a worker pulls the next task from the queue", 32),
        ["round 18: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 18: signals travel through the network layer", 4),
        ["round", "18:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 18: signals travel through the network layer", 8),
        ["round", "18:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 18: signals travel through the network layer", 12),
        ["round 18:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 18: signals travel through the network layer", 16),
        ["round 18:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 18: signals travel through the network layer", 24),
        ["round 18: signals travel", "through the network", "layer"],
    ),
    (
        ("round 18: signals travel through the network layer", 32),
        ["round 18: signals travel through", "the network layer"],
    ),
    (
        ("round 18: the gateway routes each request by policy", 4),
        ["round", "18:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 18: the gateway routes each request by policy", 8),
        ["round", "18: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 18: the gateway routes each request by policy", 12),
        ["round 18:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 18: the gateway routes each request by policy", 16),
        ["round 18: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 18: the gateway routes each request by policy", 24),
        ["round 18: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 18: the gateway routes each request by policy", 32),
        ["round 18: the gateway routes", "each request by policy"],
    ),
    (
        ("round 18: memory grows until the buffer is full", 4),
        ["round", "18:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 18: memory grows until the buffer is full", 8),
        ["round", "18:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 18: memory grows until the buffer is full", 12),
        ["round 18:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 18: memory grows until the buffer is full", 16),
        ["round 18: memory", "grows until the", "buffer is full"],
    ),
    (("round 18: memory grows until the buffer is full", 24), ["round 18: memory grows", "until the buffer is full"]),
    (("round 18: memory grows until the buffer is full", 32), ["round 18: memory grows until the", "buffer is full"]),
    (
        ("round 18: the cluster mirrors every packet twice", 4),
        ["round", "18:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 18: the cluster mirrors every packet twice", 8),
        ["round", "18: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 18: the cluster mirrors every packet twice", 12),
        ["round 18:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 18: the cluster mirrors every packet twice", 16),
        ["round 18: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 18: the cluster mirrors every packet twice", 24),
        ["round 18: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 18: the cluster mirrors every packet twice", 32), ["round 18: the cluster mirrors", "every packet twice"]),
    (
        ("round 18: ranking uses tokens learned from the corpus", 4),
        ["round", "18:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 18: ranking uses tokens learned from the corpus", 8),
        ["round", "18:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 18: ranking uses tokens learned from the corpus", 12),
        ["round 18:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 18: ranking uses tokens learned from the corpus", 16),
        ["round 18:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 18: ranking uses tokens learned from the corpus", 24),
        ["round 18: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 18: ranking uses tokens learned from the corpus", 32),
        ["round 18: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 18: a long session ends when the candle dies", 4),
        ["round", "18:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 18: a long session ends when the candle dies", 8),
        ["round", "18: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 18: a long session ends when the candle dies", 12),
        ["round 18: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 18: a long session ends when the candle dies", 16),
        ["round 18: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 18: a long session ends when the candle dies", 24),
        ["round 18: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 18: a long session ends when the candle dies", 32),
        ["round 18: a long session ends", "when the candle dies"],
    ),
    (
        ("round 18: encode the prompt then map the result", 4),
        ["round", "18:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 18: encode the prompt then map the result", 8),
        ["round", "18:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 18: encode the prompt then map the result", 12),
        ["round 18:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 18: encode the prompt then map the result", 16),
        ["round 18: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 18: encode the prompt then map the result", 24),
        ["round 18: encode the", "prompt then map the", "result"],
    ),
    (("round 18: encode the prompt then map the result", 32), ["round 18: encode the prompt then", "map the result"]),
    (
        ("round 18: the kernel wakes the worker at dawn", 4),
        ["round", "18:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 18: the kernel wakes the worker at dawn", 8),
        ["round", "18: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 18: the kernel wakes the worker at dawn", 12),
        ["round 18:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 18: the kernel wakes the worker at dawn", 16), ["round 18: the", "kernel wakes the", "worker at dawn"]),
    (("round 18: the kernel wakes the worker at dawn", 24), ["round 18: the kernel", "wakes the worker at dawn"]),
    (("round 18: the kernel wakes the worker at dawn", 32), ["round 18: the kernel wakes the", "worker at dawn"]),
    (
        ("round 18: service latency drops after the patch", 4),
        ["round", "18:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 18: service latency drops after the patch", 8),
        ["round", "18:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 18: service latency drops after the patch", 12),
        ["round 18:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 18: service latency drops after the patch", 16),
        ["round 18:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 18: service latency drops after the patch", 24),
        ["round 18: service", "latency drops after the", "patch"],
    ),
    (("round 18: service latency drops after the patch", 32), ["round 18: service latency drops", "after the patch"]),
    (
        ("round 18: the library caches every vector it sees", 4),
        ["round", "18:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 18: the library caches every vector it sees", 8),
        ["round", "18: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 18: the library caches every vector it sees", 12),
        ["round 18:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 18: the library caches every vector it sees", 16),
        ["round 18: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 18: the library caches every vector it sees", 24),
        ["round 18: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 18: the library caches every vector it sees", 32),
        ["round 18: the library caches", "every vector it sees"],
    ),
    (
        ("round 18: agents argue then the debate resolves", 4),
        ["round", "18:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 18: agents argue then the debate resolves", 8),
        ["round", "18:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 18: agents argue then the debate resolves", 12),
        ["round 18:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 18: agents argue then the debate resolves", 16),
        ["round 18: agents", "argue then the", "debate resolves"],
    ),
    (("round 18: agents argue then the debate resolves", 24), ["round 18: agents argue", "then the debate resolves"]),
    (("round 18: agents argue then the debate resolves", 32), ["round 18: agents argue then the", "debate resolves"]),
    (
        ("round 18: the filter keeps only strong matches", 4),
        ["round", "18:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 18: the filter keeps only strong matches", 8),
        ["round", "18: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 18: the filter keeps only strong matches", 12),
        ["round 18:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 18: the filter keeps only strong matches", 16),
        ["round 18: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 18: the filter keeps only strong matches", 24), ["round 18: the filter", "keeps only strong", "matches"]),
    (("round 18: the filter keeps only strong matches", 32), ["round 18: the filter keeps only", "strong matches"]),
    (
        ("round 18: the model answers with a short reply", 4),
        ["round", "18:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 18: the model answers with a short reply", 8),
        ["round", "18: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 18: the model answers with a short reply", 12),
        ["round 18:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 18: the model answers with a short reply", 16),
        ["round 18: the", "model answers", "with a short", "reply"],
    ),
    (("round 18: the model answers with a short reply", 24), ["round 18: the model", "answers with a short", "reply"]),
    (("round 18: the model answers with a short reply", 32), ["round 18: the model answers with", "a short reply"]),
    (
        ("round 18: the recorder stores the reasoning trace", 4),
        ["round", "18:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 18: the recorder stores the reasoning trace", 8),
        ["round", "18: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 18: the recorder stores the reasoning trace", 12),
        ["round 18:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 18: the recorder stores the reasoning trace", 16),
        ["round 18: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 18: the recorder stores the reasoning trace", 24),
        ["round 18: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 18: the recorder stores the reasoning trace", 32),
        ["round 18: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 18: the angel watches the processor run", 4),
        ["round", "18:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 18: the angel watches the processor run", 8),
        ["round", "18: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 18: the angel watches the processor run", 12),
        ["round 18:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 18: the angel watches the processor run", 16), ["round 18: the", "angel watches", "the processor", "run"]),
    (("round 18: the angel watches the processor run", 24), ["round 18: the angel", "watches the processor", "run"]),
    (("round 18: the angel watches the processor run", 32), ["round 18: the angel watches the", "processor run"]),
    (
        ("round 18: angle of the vector decides the match", 4),
        ["round", "18:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 18: angle of the vector decides the match", 8),
        ["round", "18:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 18: angle of the vector decides the match", 12),
        ["round 18:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 18: angle of the vector decides the match", 16),
        ["round 18: angle", "of the vector", "decides the", "match"],
    ),
    (("round 18: angle of the vector decides the match", 24), ["round 18: angle of the", "vector decides the match"]),
    (("round 18: angle of the vector decides the match", 32), ["round 18: angle of the vector", "decides the match"]),
    (
        ("round 18: the candle burns twice as long at night", 4),
        ["round", "18:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 18: the candle burns twice as long at night", 8),
        ["round", "18: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 18: the candle burns twice as long at night", 12),
        ["round 18:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 18: the candle burns twice as long at night", 16),
        ["round 18: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 18: the candle burns twice as long at night", 24),
        ["round 18: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 18: the candle burns twice as long at night", 32),
        ["round 18: the candle burns twice", "as long at night"],
    ),
    (
        ("round 18: a mirror of the universe in one line", 4),
        ["round", "18:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 18: a mirror of the universe in one line", 8),
        ["round", "18: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 18: a mirror of the universe in one line", 12),
        ["round 18: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 18: a mirror of the universe in one line", 16),
        ["round 18: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 18: a mirror of the universe in one line", 24), ["round 18: a mirror of", "the universe in one line"]),
    (("round 18: a mirror of the universe in one line", 32), ["round 18: a mirror of the", "universe in one line"]),
    (
        ("round 18: the queue drains before the storm", 4),
        ["round", "18:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 18: the queue drains before the storm", 8),
        ["round", "18: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 18: the queue drains before the storm", 12), ["round 18:", "the queue", "drains", "before the", "storm"]),
    (("round 18: the queue drains before the storm", 16), ["round 18: the", "queue drains", "before the storm"]),
    (("round 18: the queue drains before the storm", 24), ["round 18: the queue", "drains before the storm"]),
    (("round 18: the queue drains before the storm", 32), ["round 18: the queue drains", "before the storm"]),
    (
        ("kitten18 sitting18 agent18 angle18 universe18 memory18", 6),
        ["kitten18", "sitting18", "agent18", "angle18", "universe18", "memory18"],
    ),
    (
        ("kitten18 sitting18 agent18 angle18 universe18 memory18", 10),
        ["kitten18", "sitting18", "agent18", "angle18", "universe18", "memory18"],
    ),
    (
        ("kitten18 sitting18 agent18 angle18 universe18 memory18", 18),
        ["kitten18 sitting18", "agent18 angle18", "universe18", "memory18"],
    ),
    (
        ("kitten18 sitting18 agent18 angle18 universe18 memory18", 28),
        ["kitten18 sitting18 agent18", "angle18 universe18 memory18"],
    ),
    (
        ("sitting18 agent18 angle18 universe18 memory18 stream18", 6),
        ["sitting18", "agent18", "angle18", "universe18", "memory18", "stream18"],
    ),
    (
        ("sitting18 agent18 angle18 universe18 memory18 stream18", 10),
        ["sitting18", "agent18", "angle18", "universe18", "memory18", "stream18"],
    ),
    (
        ("sitting18 agent18 angle18 universe18 memory18 stream18", 18),
        ["sitting18 agent18", "angle18 universe18", "memory18 stream18"],
    ),
    (
        ("sitting18 agent18 angle18 universe18 memory18 stream18", 28),
        ["sitting18 agent18 angle18", "universe18 memory18 stream18"],
    ),
    (
        ("agent18 angle18 universe18 memory18 stream18 context18", 6),
        ["agent18", "angle18", "universe18", "memory18", "stream18", "context18"],
    ),
    (
        ("agent18 angle18 universe18 memory18 stream18 context18", 10),
        ["agent18", "angle18", "universe18", "memory18", "stream18", "context18"],
    ),
    (
        ("agent18 angle18 universe18 memory18 stream18 context18", 18),
        ["agent18 angle18", "universe18", "memory18 stream18", "context18"],
    ),
    (
        ("agent18 angle18 universe18 memory18 stream18 context18", 28),
        ["agent18 angle18 universe18", "memory18 stream18 context18"],
    ),
    (
        ("angle18 universe18 memory18 stream18 context18 knowledge18", 6),
        ["angle18", "universe18", "memory18", "stream18", "context18", "knowledge18"],
    ),
    (
        ("angle18 universe18 memory18 stream18 context18 knowledge18", 10),
        ["angle18", "universe18", "memory18", "stream18", "context18", "knowledge18"],
    ),
    (
        ("angle18 universe18 memory18 stream18 context18 knowledge18", 18),
        ["angle18 universe18", "memory18 stream18", "context18", "knowledge18"],
    ),
    (
        ("angle18 universe18 memory18 stream18 context18 knowledge18", 28),
        ["angle18 universe18 memory18", "stream18 context18", "knowledge18"],
    ),
    (
        ("universe18 memory18 stream18 context18 knowledge18 vector18", 6),
        ["universe18", "memory18", "stream18", "context18", "knowledge18", "vector18"],
    ),
    (
        ("universe18 memory18 stream18 context18 knowledge18 vector18", 10),
        ["universe18", "memory18", "stream18", "context18", "knowledge18", "vector18"],
    ),
    (
        ("universe18 memory18 stream18 context18 knowledge18 vector18", 18),
        ["universe18", "memory18 stream18", "context18", "knowledge18", "vector18"],
    ),
    (
        ("universe18 memory18 stream18 context18 knowledge18 vector18", 28),
        ["universe18 memory18 stream18", "context18 knowledge18", "vector18"],
    ),
    (
        ("memory18 stream18 context18 knowledge18 vector18 processor18", 6),
        ["memory18", "stream18", "context18", "knowledge18", "vector18", "processor18"],
    ),
    (
        ("memory18 stream18 context18 knowledge18 vector18 processor18", 10),
        ["memory18", "stream18", "context18", "knowledge18", "vector18", "processor18"],
    ),
    (
        ("memory18 stream18 context18 knowledge18 vector18 processor18", 18),
        ["memory18 stream18", "context18", "knowledge18", "vector18", "processor18"],
    ),
    (
        ("memory18 stream18 context18 knowledge18 vector18 processor18", 28),
        ["memory18 stream18 context18", "knowledge18 vector18", "processor18"],
    ),
    (
        ("stream18 context18 knowledge18 vector18 processor18 reasoning18", 6),
        ["stream18", "context18", "knowledge18", "vector18", "processor18", "reasoning18"],
    ),
    (
        ("stream18 context18 knowledge18 vector18 processor18 reasoning18", 10),
        ["stream18", "context18", "knowledge18", "vector18", "processor18", "reasoning18"],
    ),
    (
        ("stream18 context18 knowledge18 vector18 processor18 reasoning18", 18),
        ["stream18 context18", "knowledge18", "vector18", "processor18", "reasoning18"],
    ),
    (
        ("stream18 context18 knowledge18 vector18 processor18 reasoning18", 28),
        ["stream18 context18", "knowledge18 vector18", "processor18 reasoning18"],
    ),
    (
        ("context18 knowledge18 vector18 processor18 reasoning18 machine18", 6),
        ["context18", "knowledge18", "vector18", "processor18", "reasoning18", "machine18"],
    ),
    (
        ("context18 knowledge18 vector18 processor18 reasoning18 machine18", 10),
        ["context18", "knowledge18", "vector18", "processor18", "reasoning18", "machine18"],
    ),
    (
        ("context18 knowledge18 vector18 processor18 reasoning18 machine18", 18),
        ["context18", "knowledge18", "vector18", "processor18", "reasoning18", "machine18"],
    ),
    (
        ("context18 knowledge18 vector18 processor18 reasoning18 machine18", 28),
        ["context18 knowledge18", "vector18 processor18", "reasoning18 machine18"],
    ),
    (
        ("knowledge18 vector18 processor18 reasoning18 machine18 learning18", 6),
        ["knowledge18", "vector18", "processor18", "reasoning18", "machine18", "learning18"],
    ),
    (
        ("knowledge18 vector18 processor18 reasoning18 machine18 learning18", 10),
        ["knowledge18", "vector18", "processor18", "reasoning18", "machine18", "learning18"],
    ),
    (
        ("knowledge18 vector18 processor18 reasoning18 machine18 learning18", 18),
        ["knowledge18", "vector18", "processor18", "reasoning18", "machine18", "learning18"],
    ),
    (
        ("knowledge18 vector18 processor18 reasoning18 machine18 learning18", 28),
        ["knowledge18 vector18", "processor18 reasoning18", "machine18 learning18"],
    ),
    (
        ("vector18 processor18 reasoning18 machine18 learning18 model18", 6),
        ["vector18", "processor18", "reasoning18", "machine18", "learning18", "model18"],
    ),
    (
        ("vector18 processor18 reasoning18 machine18 learning18 model18", 10),
        ["vector18", "processor18", "reasoning18", "machine18", "learning18", "model18"],
    ),
    (
        ("vector18 processor18 reasoning18 machine18 learning18 model18", 18),
        ["vector18", "processor18", "reasoning18", "machine18", "learning18 model18"],
    ),
    (
        ("vector18 processor18 reasoning18 machine18 learning18 model18", 28),
        ["vector18 processor18", "reasoning18 machine18", "learning18 model18"],
    ),
    (
        ("processor18 reasoning18 machine18 learning18 model18 token18", 6),
        ["processor18", "reasoning18", "machine18", "learning18", "model18", "token18"],
    ),
    (
        ("processor18 reasoning18 machine18 learning18 model18 token18", 10),
        ["processor18", "reasoning18", "machine18", "learning18", "model18", "token18"],
    ),
    (
        ("processor18 reasoning18 machine18 learning18 model18 token18", 18),
        ["processor18", "reasoning18", "machine18", "learning18 model18", "token18"],
    ),
    (
        ("processor18 reasoning18 machine18 learning18 model18 token18", 28),
        ["processor18 reasoning18", "machine18 learning18 model18", "token18"],
    ),
    (
        ("reasoning18 machine18 learning18 model18 token18 prompt18", 6),
        ["reasoning18", "machine18", "learning18", "model18", "token18", "prompt18"],
    ),
    (
        ("reasoning18 machine18 learning18 model18 token18 prompt18", 10),
        ["reasoning18", "machine18", "learning18", "model18", "token18", "prompt18"],
    ),
    (
        ("reasoning18 machine18 learning18 model18 token18 prompt18", 18),
        ["reasoning18", "machine18", "learning18 model18", "token18 prompt18"],
    ),
    (
        ("reasoning18 machine18 learning18 model18 token18 prompt18", 28),
        ["reasoning18 machine18", "learning18 model18 token18", "prompt18"],
    ),
    (
        ("machine18 learning18 model18 token18 prompt18 session18", 6),
        ["machine18", "learning18", "model18", "token18", "prompt18", "session18"],
    ),
    (
        ("machine18 learning18 model18 token18 prompt18 session18", 10),
        ["machine18", "learning18", "model18", "token18", "prompt18", "session18"],
    ),
    (
        ("machine18 learning18 model18 token18 prompt18 session18", 18),
        ["machine18", "learning18 model18", "token18 prompt18", "session18"],
    ),
    (
        ("machine18 learning18 model18 token18 prompt18 session18", 28),
        ["machine18 learning18 model18", "token18 prompt18 session18"],
    ),
    (
        ("learning18 model18 token18 prompt18 session18 library18", 6),
        ["learning18", "model18", "token18", "prompt18", "session18", "library18"],
    ),
    (
        ("learning18 model18 token18 prompt18 session18 library18", 10),
        ["learning18", "model18", "token18", "prompt18", "session18", "library18"],
    ),
    (
        ("learning18 model18 token18 prompt18 session18 library18", 18),
        ["learning18 model18", "token18 prompt18", "session18", "library18"],
    ),
    (
        ("learning18 model18 token18 prompt18 session18 library18", 28),
        ["learning18 model18 token18", "prompt18 session18 library18"],
    ),
    (
        ("model18 token18 prompt18 session18 library18 service18", 6),
        ["model18", "token18", "prompt18", "session18", "library18", "service18"],
    ),
    (
        ("model18 token18 prompt18 session18 library18 service18", 10),
        ["model18", "token18", "prompt18", "session18", "library18", "service18"],
    ),
    (
        ("model18 token18 prompt18 session18 library18 service18", 18),
        ["model18 token18", "prompt18 session18", "library18", "service18"],
    ),
    (
        ("model18 token18 prompt18 session18 library18 service18", 28),
        ["model18 token18 prompt18", "session18 library18", "service18"],
    ),
    (
        ("token18 prompt18 session18 library18 service18 gateway18", 6),
        ["token18", "prompt18", "session18", "library18", "service18", "gateway18"],
    ),
    (
        ("token18 prompt18 session18 library18 service18 gateway18", 10),
        ["token18", "prompt18", "session18", "library18", "service18", "gateway18"],
    ),
    (
        ("token18 prompt18 session18 library18 service18 gateway18", 18),
        ["token18 prompt18", "session18", "library18", "service18", "gateway18"],
    ),
    (
        ("token18 prompt18 session18 library18 service18 gateway18", 28),
        ["token18 prompt18 session18", "library18 service18", "gateway18"],
    ),
    (
        ("prompt18 session18 library18 service18 gateway18 storage18", 6),
        ["prompt18", "session18", "library18", "service18", "gateway18", "storage18"],
    ),
    (
        ("prompt18 session18 library18 service18 gateway18 storage18", 10),
        ["prompt18", "session18", "library18", "service18", "gateway18", "storage18"],
    ),
    (
        ("prompt18 session18 library18 service18 gateway18 storage18", 18),
        ["prompt18 session18", "library18", "service18", "gateway18", "storage18"],
    ),
    (
        ("prompt18 session18 library18 service18 gateway18 storage18", 28),
        ["prompt18 session18 library18", "service18 gateway18", "storage18"],
    ),
    (
        ("session18 library18 service18 gateway18 storage18 network18", 6),
        ["session18", "library18", "service18", "gateway18", "storage18", "network18"],
    ),
    (
        ("session18 library18 service18 gateway18 storage18 network18", 10),
        ["session18", "library18", "service18", "gateway18", "storage18", "network18"],
    ),
    (
        ("session18 library18 service18 gateway18 storage18 network18", 18),
        ["session18", "library18", "service18", "gateway18", "storage18", "network18"],
    ),
    (
        ("session18 library18 service18 gateway18 storage18 network18", 28),
        ["session18 library18", "service18 gateway18", "storage18 network18"],
    ),
    (
        ("library18 service18 gateway18 storage18 network18 latency18", 6),
        ["library18", "service18", "gateway18", "storage18", "network18", "latency18"],
    ),
    (
        ("library18 service18 gateway18 storage18 network18 latency18", 10),
        ["library18", "service18", "gateway18", "storage18", "network18", "latency18"],
    ),
    (
        ("library18 service18 gateway18 storage18 network18 latency18", 18),
        ["library18", "service18", "gateway18", "storage18", "network18", "latency18"],
    ),
    (
        ("library18 service18 gateway18 storage18 network18 latency18", 28),
        ["library18 service18", "gateway18 storage18", "network18 latency18"],
    ),
    (
        ("service18 gateway18 storage18 network18 latency18 buffer18", 6),
        ["service18", "gateway18", "storage18", "network18", "latency18", "buffer18"],
    ),
    (
        ("service18 gateway18 storage18 network18 latency18 buffer18", 10),
        ["service18", "gateway18", "storage18", "network18", "latency18", "buffer18"],
    ),
    (
        ("service18 gateway18 storage18 network18 latency18 buffer18", 18),
        ["service18", "gateway18", "storage18", "network18", "latency18 buffer18"],
    ),
    (
        ("service18 gateway18 storage18 network18 latency18 buffer18", 28),
        ["service18 gateway18", "storage18 network18", "latency18 buffer18"],
    ),
    (
        ("gateway18 storage18 network18 latency18 buffer18 queue18", 6),
        ["gateway18", "storage18", "network18", "latency18", "buffer18", "queue18"],
    ),
    (
        ("gateway18 storage18 network18 latency18 buffer18 queue18", 10),
        ["gateway18", "storage18", "network18", "latency18", "buffer18", "queue18"],
    ),
    (
        ("gateway18 storage18 network18 latency18 buffer18 queue18", 18),
        ["gateway18", "storage18", "network18", "latency18 buffer18", "queue18"],
    ),
    (
        ("gateway18 storage18 network18 latency18 buffer18 queue18", 28),
        ["gateway18 storage18", "network18 latency18 buffer18", "queue18"],
    ),
    (
        ("storage18 network18 latency18 buffer18 queue18 worker18", 6),
        ["storage18", "network18", "latency18", "buffer18", "queue18", "worker18"],
    ),
    (
        ("storage18 network18 latency18 buffer18 queue18 worker18", 10),
        ["storage18", "network18", "latency18", "buffer18", "queue18", "worker18"],
    ),
    (
        ("storage18 network18 latency18 buffer18 queue18 worker18", 18),
        ["storage18", "network18", "latency18 buffer18", "queue18 worker18"],
    ),
    (
        ("storage18 network18 latency18 buffer18 queue18 worker18", 28),
        ["storage18 network18", "latency18 buffer18 queue18", "worker18"],
    ),
    (
        ("network18 latency18 buffer18 queue18 worker18 kernel18", 6),
        ["network18", "latency18", "buffer18", "queue18", "worker18", "kernel18"],
    ),
    (
        ("network18 latency18 buffer18 queue18 worker18 kernel18", 10),
        ["network18", "latency18", "buffer18", "queue18", "worker18", "kernel18"],
    ),
    (
        ("network18 latency18 buffer18 queue18 worker18 kernel18", 18),
        ["network18", "latency18 buffer18", "queue18 worker18", "kernel18"],
    ),
    (
        ("network18 latency18 buffer18 queue18 worker18 kernel18", 28),
        ["network18 latency18 buffer18", "queue18 worker18 kernel18"],
    ),
    (
        ("latency18 buffer18 queue18 worker18 kernel18 signal18", 6),
        ["latency18", "buffer18", "queue18", "worker18", "kernel18", "signal18"],
    ),
    (
        ("latency18 buffer18 queue18 worker18 kernel18 signal18", 10),
        ["latency18", "buffer18", "queue18", "worker18", "kernel18", "signal18"],
    ),
    (
        ("latency18 buffer18 queue18 worker18 kernel18 signal18", 18),
        ["latency18 buffer18", "queue18 worker18", "kernel18 signal18"],
    ),
    (
        ("latency18 buffer18 queue18 worker18 kernel18 signal18", 28),
        ["latency18 buffer18 queue18", "worker18 kernel18 signal18"],
    ),
    (
        ("buffer18 queue18 worker18 kernel18 signal18 packet18", 6),
        ["buffer18", "queue18", "worker18", "kernel18", "signal18", "packet18"],
    ),
    (
        ("buffer18 queue18 worker18 kernel18 signal18 packet18", 10),
        ["buffer18", "queue18", "worker18", "kernel18", "signal18", "packet18"],
    ),
    (
        ("buffer18 queue18 worker18 kernel18 signal18 packet18", 18),
        ["buffer18 queue18", "worker18 kernel18", "signal18 packet18"],
    ),
    (
        ("buffer18 queue18 worker18 kernel18 signal18 packet18", 28),
        ["buffer18 queue18 worker18", "kernel18 signal18 packet18"],
    ),
    (
        ("queue18 worker18 kernel18 signal18 packet18 router18", 6),
        ["queue18", "worker18", "kernel18", "signal18", "packet18", "router18"],
    ),
    (
        ("queue18 worker18 kernel18 signal18 packet18 router18", 10),
        ["queue18", "worker18", "kernel18", "signal18", "packet18", "router18"],
    ),
    (
        ("queue18 worker18 kernel18 signal18 packet18 router18", 18),
        ["queue18 worker18", "kernel18 signal18", "packet18 router18"],
    ),
    (
        ("queue18 worker18 kernel18 signal18 packet18 router18", 28),
        ["queue18 worker18 kernel18", "signal18 packet18 router18"],
    ),
    (
        ("worker18 kernel18 signal18 packet18 router18 cluster18", 6),
        ["worker18", "kernel18", "signal18", "packet18", "router18", "cluster18"],
    ),
    (
        ("worker18 kernel18 signal18 packet18 router18 cluster18", 10),
        ["worker18", "kernel18", "signal18", "packet18", "router18", "cluster18"],
    ),
    (
        ("worker18 kernel18 signal18 packet18 router18 cluster18", 18),
        ["worker18 kernel18", "signal18 packet18", "router18 cluster18"],
    ),
    (
        ("worker18 kernel18 signal18 packet18 router18 cluster18", 28),
        ["worker18 kernel18 signal18", "packet18 router18 cluster18"],
    ),
    (
        ("kernel18 signal18 packet18 router18 cluster18 mirror18", 6),
        ["kernel18", "signal18", "packet18", "router18", "cluster18", "mirror18"],
    ),
    (
        ("kernel18 signal18 packet18 router18 cluster18 mirror18", 10),
        ["kernel18", "signal18", "packet18", "router18", "cluster18", "mirror18"],
    ),
    (
        ("kernel18 signal18 packet18 router18 cluster18 mirror18", 18),
        ["kernel18 signal18", "packet18 router18", "cluster18 mirror18"],
    ),
    (
        ("kernel18 signal18 packet18 router18 cluster18 mirror18", 28),
        ["kernel18 signal18 packet18", "router18 cluster18 mirror18"],
    ),
    (
        ("signal18 packet18 router18 cluster18 mirror18 filter18", 6),
        ["signal18", "packet18", "router18", "cluster18", "mirror18", "filter18"],
    ),
    (
        ("signal18 packet18 router18 cluster18 mirror18 filter18", 10),
        ["signal18", "packet18", "router18", "cluster18", "mirror18", "filter18"],
    ),
    (
        ("signal18 packet18 router18 cluster18 mirror18 filter18", 18),
        ["signal18 packet18", "router18 cluster18", "mirror18 filter18"],
    ),
    (
        ("signal18 packet18 router18 cluster18 mirror18 filter18", 28),
        ["signal18 packet18 router18", "cluster18 mirror18 filter18"],
    ),
    (
        ("packet18 router18 cluster18 mirror18 filter18 ranking18", 6),
        ["packet18", "router18", "cluster18", "mirror18", "filter18", "ranking18"],
    ),
    (
        ("packet18 router18 cluster18 mirror18 filter18 ranking18", 10),
        ["packet18", "router18", "cluster18", "mirror18", "filter18", "ranking18"],
    ),
    (
        ("packet18 router18 cluster18 mirror18 filter18 ranking18", 18),
        ["packet18 router18", "cluster18 mirror18", "filter18 ranking18"],
    ),
    (
        ("packet18 router18 cluster18 mirror18 filter18 ranking18", 28),
        ["packet18 router18 cluster18", "mirror18 filter18 ranking18"],
    ),
    (
        ("router18 cluster18 mirror18 filter18 ranking18 encoding18", 6),
        ["router18", "cluster18", "mirror18", "filter18", "ranking18", "encoding18"],
    ),
    (
        ("router18 cluster18 mirror18 filter18 ranking18 encoding18", 10),
        ["router18", "cluster18", "mirror18", "filter18", "ranking18", "encoding18"],
    ),
    (
        ("router18 cluster18 mirror18 filter18 ranking18 encoding18", 18),
        ["router18 cluster18", "mirror18 filter18", "ranking18", "encoding18"],
    ),
    (
        ("router18 cluster18 mirror18 filter18 ranking18 encoding18", 28),
        ["router18 cluster18 mirror18", "filter18 ranking18", "encoding18"],
    ),
    (
        ("cluster18 mirror18 filter18 ranking18 encoding18 mapping18", 6),
        ["cluster18", "mirror18", "filter18", "ranking18", "encoding18", "mapping18"],
    ),
    (
        ("cluster18 mirror18 filter18 ranking18 encoding18 mapping18", 10),
        ["cluster18", "mirror18", "filter18", "ranking18", "encoding18", "mapping18"],
    ),
    (
        ("cluster18 mirror18 filter18 ranking18 encoding18 mapping18", 18),
        ["cluster18 mirror18", "filter18 ranking18", "encoding18", "mapping18"],
    ),
    (
        ("cluster18 mirror18 filter18 ranking18 encoding18 mapping18", 28),
        ["cluster18 mirror18 filter18", "ranking18 encoding18", "mapping18"],
    ),
    (
        ("mirror18 filter18 ranking18 encoding18 mapping18 record18", 6),
        ["mirror18", "filter18", "ranking18", "encoding18", "mapping18", "record18"],
    ),
    (
        ("mirror18 filter18 ranking18 encoding18 mapping18 record18", 10),
        ["mirror18", "filter18", "ranking18", "encoding18", "mapping18", "record18"],
    ),
    (
        ("mirror18 filter18 ranking18 encoding18 mapping18 record18", 18),
        ["mirror18 filter18", "ranking18", "encoding18", "mapping18 record18"],
    ),
    (
        ("mirror18 filter18 ranking18 encoding18 mapping18 record18", 28),
        ["mirror18 filter18 ranking18", "encoding18 mapping18", "record18"],
    ),
    (
        ("filter18 ranking18 encoding18 mapping18 record18 candle18", 6),
        ["filter18", "ranking18", "encoding18", "mapping18", "record18", "candle18"],
    ),
    (
        ("filter18 ranking18 encoding18 mapping18 record18 candle18", 10),
        ["filter18", "ranking18", "encoding18", "mapping18", "record18", "candle18"],
    ),
    (
        ("filter18 ranking18 encoding18 mapping18 record18 candle18", 18),
        ["filter18 ranking18", "encoding18", "mapping18 record18", "candle18"],
    ),
    (
        ("filter18 ranking18 encoding18 mapping18 record18 candle18", 28),
        ["filter18 ranking18", "encoding18 mapping18", "record18 candle18"],
    ),
    (
        ("ranking18 encoding18 mapping18 record18 candle18 thread18", 6),
        ["ranking18", "encoding18", "mapping18", "record18", "candle18", "thread18"],
    ),
    (
        ("ranking18 encoding18 mapping18 record18 candle18 thread18", 10),
        ["ranking18", "encoding18", "mapping18", "record18", "candle18", "thread18"],
    ),
    (
        ("ranking18 encoding18 mapping18 record18 candle18 thread18", 18),
        ["ranking18", "encoding18", "mapping18 record18", "candle18 thread18"],
    ),
    (
        ("ranking18 encoding18 mapping18 record18 candle18 thread18", 28),
        ["ranking18 encoding18", "mapping18 record18 candle18", "thread18"],
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
