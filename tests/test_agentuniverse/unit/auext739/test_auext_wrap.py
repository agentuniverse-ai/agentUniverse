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
        ("round 739: the quick brown fox jumps over the lazy dog", 4),
        ["round", "739:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", 8),
        ["round", "739: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", 12),
        ["round 739:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", 16),
        ["round 739: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", 24),
        ["round 739: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 739: the quick brown fox jumps over the lazy dog", 32),
        ["round 739: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", 4),
        ["round", "739:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", 8),
        ["round", "739:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", 12),
        ["round 739:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", 16),
        ["round 739:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", 24),
        ["round 739: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 739: agentuniverse is a framework for multi agents", 32),
        ["round 739: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", 4),
        ["round", "739:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", 8),
        ["round", "739:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", 12),
        ["round 739:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", 16),
        ["round 739:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", 24),
        ["round 739: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 739: knowledge stored as vectors enables retrieval", 32),
        ["round 739: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 739: the processor reads the record then stops", 4),
        ["round", "739:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 739: the processor reads the record then stops", 8),
        ["round", "739: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 739: the processor reads the record then stops", 12),
        ["round 739:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 739: the processor reads the record then stops", 16),
        ["round 739: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 739: the processor reads the record then stops", 24),
        ["round 739: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 739: the processor reads the record then stops", 32),
        ["round 739: the processor reads", "the record then stops"],
    ),
    (
        ("round 739: a worker pulls the next task from the queue", 4),
        ["round", "739:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 739: a worker pulls the next task from the queue", 8),
        ["round", "739: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 739: a worker pulls the next task from the queue", 12),
        ["round 739: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 739: a worker pulls the next task from the queue", 16),
        ["round 739: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 739: a worker pulls the next task from the queue", 24),
        ["round 739: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 739: a worker pulls the next task from the queue", 32),
        ["round 739: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 739: signals travel through the network layer", 4),
        ["round", "739:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 739: signals travel through the network layer", 8),
        ["round", "739:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 739: signals travel through the network layer", 12),
        ["round 739:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 739: signals travel through the network layer", 16),
        ["round 739:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 739: signals travel through the network layer", 24),
        ["round 739: signals", "travel through the", "network layer"],
    ),
    (
        ("round 739: signals travel through the network layer", 32),
        ["round 739: signals travel", "through the network layer"],
    ),
    (
        ("round 739: the gateway routes each request by policy", 4),
        ["round", "739:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 739: the gateway routes each request by policy", 8),
        ["round", "739: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 739: the gateway routes each request by policy", 12),
        ["round 739:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 739: the gateway routes each request by policy", 16),
        ["round 739: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 739: the gateway routes each request by policy", 24),
        ["round 739: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 739: the gateway routes each request by policy", 32),
        ["round 739: the gateway routes", "each request by policy"],
    ),
    (
        ("round 739: memory grows until the buffer is full", 4),
        ["round", "739:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 739: memory grows until the buffer is full", 8),
        ["round", "739:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 739: memory grows until the buffer is full", 12),
        ["round 739:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 739: memory grows until the buffer is full", 16),
        ["round 739:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 739: memory grows until the buffer is full", 24), ["round 739: memory grows", "until the buffer is full"]),
    (("round 739: memory grows until the buffer is full", 32), ["round 739: memory grows until", "the buffer is full"]),
    (
        ("round 739: the cluster mirrors every packet twice", 4),
        ["round", "739:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 739: the cluster mirrors every packet twice", 8),
        ["round", "739: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 739: the cluster mirrors every packet twice", 12),
        ["round 739:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 739: the cluster mirrors every packet twice", 16),
        ["round 739: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 739: the cluster mirrors every packet twice", 24),
        ["round 739: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 739: the cluster mirrors every packet twice", 32),
        ["round 739: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", 4),
        ["round", "739:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", 8),
        ["round", "739:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", 12),
        ["round 739:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", 16),
        ["round 739:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", 24),
        ["round 739: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 739: ranking uses tokens learned from the corpus", 32),
        ["round 739: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 739: a long session ends when the candle dies", 4),
        ["round", "739:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 739: a long session ends when the candle dies", 8),
        ["round", "739: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 739: a long session ends when the candle dies", 12),
        ["round 739: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 739: a long session ends when the candle dies", 16),
        ["round 739: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 739: a long session ends when the candle dies", 24),
        ["round 739: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 739: a long session ends when the candle dies", 32),
        ["round 739: a long session ends", "when the candle dies"],
    ),
    (
        ("round 739: encode the prompt then map the result", 4),
        ["round", "739:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 739: encode the prompt then map the result", 8),
        ["round", "739:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 739: encode the prompt then map the result", 12),
        ["round 739:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 739: encode the prompt then map the result", 16),
        ["round 739:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 739: encode the prompt then map the result", 24),
        ["round 739: encode the", "prompt then map the", "result"],
    ),
    (("round 739: encode the prompt then map the result", 32), ["round 739: encode the prompt", "then map the result"]),
    (
        ("round 739: the kernel wakes the worker at dawn", 4),
        ["round", "739:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 739: the kernel wakes the worker at dawn", 8),
        ["round", "739: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 739: the kernel wakes the worker at dawn", 12),
        ["round 739:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 739: the kernel wakes the worker at dawn", 16), ["round 739: the", "kernel wakes the", "worker at dawn"]),
    (("round 739: the kernel wakes the worker at dawn", 24), ["round 739: the kernel", "wakes the worker at dawn"]),
    (("round 739: the kernel wakes the worker at dawn", 32), ["round 739: the kernel wakes the", "worker at dawn"]),
    (
        ("round 739: service latency drops after the patch", 4),
        ["round", "739:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 739: service latency drops after the patch", 8),
        ["round", "739:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 739: service latency drops after the patch", 12),
        ["round 739:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 739: service latency drops after the patch", 16),
        ["round 739:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 739: service latency drops after the patch", 24),
        ["round 739: service", "latency drops after the", "patch"],
    ),
    (("round 739: service latency drops after the patch", 32), ["round 739: service latency drops", "after the patch"]),
    (
        ("round 739: the library caches every vector it sees", 4),
        ["round", "739:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 739: the library caches every vector it sees", 8),
        ["round", "739: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 739: the library caches every vector it sees", 12),
        ["round 739:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 739: the library caches every vector it sees", 16),
        ["round 739: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 739: the library caches every vector it sees", 24),
        ["round 739: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 739: the library caches every vector it sees", 32),
        ["round 739: the library caches", "every vector it sees"],
    ),
    (
        ("round 739: agents argue then the debate resolves", 4),
        ["round", "739:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 739: agents argue then the debate resolves", 8),
        ["round", "739:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 739: agents argue then the debate resolves", 12),
        ["round 739:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 739: agents argue then the debate resolves", 16),
        ["round 739:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 739: agents argue then the debate resolves", 24), ["round 739: agents argue", "then the debate resolves"]),
    (("round 739: agents argue then the debate resolves", 32), ["round 739: agents argue then the", "debate resolves"]),
    (
        ("round 739: the filter keeps only strong matches", 4),
        ["round", "739:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 739: the filter keeps only strong matches", 8),
        ["round", "739: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 739: the filter keeps only strong matches", 12),
        ["round 739:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 739: the filter keeps only strong matches", 16),
        ["round 739: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 739: the filter keeps only strong matches", 24),
        ["round 739: the filter", "keeps only strong", "matches"],
    ),
    (("round 739: the filter keeps only strong matches", 32), ["round 739: the filter keeps only", "strong matches"]),
    (
        ("round 739: the model answers with a short reply", 4),
        ["round", "739:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 739: the model answers with a short reply", 8),
        ["round", "739: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 739: the model answers with a short reply", 12),
        ["round 739:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 739: the model answers with a short reply", 16),
        ["round 739: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 739: the model answers with a short reply", 24),
        ["round 739: the model", "answers with a short", "reply"],
    ),
    (("round 739: the model answers with a short reply", 32), ["round 739: the model answers", "with a short reply"]),
    (
        ("round 739: the recorder stores the reasoning trace", 4),
        ["round", "739:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 739: the recorder stores the reasoning trace", 8),
        ["round", "739: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 739: the recorder stores the reasoning trace", 12),
        ["round 739:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 739: the recorder stores the reasoning trace", 16),
        ["round 739: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 739: the recorder stores the reasoning trace", 24),
        ["round 739: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 739: the recorder stores the reasoning trace", 32),
        ["round 739: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 739: the angel watches the processor run", 4),
        ["round", "739:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 739: the angel watches the processor run", 8),
        ["round", "739: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 739: the angel watches the processor run", 12),
        ["round 739:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 739: the angel watches the processor run", 16),
        ["round 739: the", "angel watches", "the processor", "run"],
    ),
    (("round 739: the angel watches the processor run", 24), ["round 739: the angel", "watches the processor", "run"]),
    (("round 739: the angel watches the processor run", 32), ["round 739: the angel watches the", "processor run"]),
    (
        ("round 739: angle of the vector decides the match", 4),
        ["round", "739:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 739: angle of the vector decides the match", 8),
        ["round", "739:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 739: angle of the vector decides the match", 12),
        ["round 739:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 739: angle of the vector decides the match", 16),
        ["round 739: angle", "of the vector", "decides the", "match"],
    ),
    (("round 739: angle of the vector decides the match", 24), ["round 739: angle of the", "vector decides the match"]),
    (("round 739: angle of the vector decides the match", 32), ["round 739: angle of the vector", "decides the match"]),
    (
        ("round 739: the candle burns twice as long at night", 4),
        ["round", "739:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 739: the candle burns twice as long at night", 8),
        ["round", "739: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 739: the candle burns twice as long at night", 12),
        ["round 739:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 739: the candle burns twice as long at night", 16),
        ["round 739: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 739: the candle burns twice as long at night", 24),
        ["round 739: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 739: the candle burns twice as long at night", 32),
        ["round 739: the candle burns", "twice as long at night"],
    ),
    (
        ("round 739: a mirror of the universe in one line", 4),
        ["round", "739:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 739: a mirror of the universe in one line", 8),
        ["round", "739: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 739: a mirror of the universe in one line", 12),
        ["round 739: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 739: a mirror of the universe in one line", 16),
        ["round 739: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 739: a mirror of the universe in one line", 24), ["round 739: a mirror of", "the universe in one line"]),
    (("round 739: a mirror of the universe in one line", 32), ["round 739: a mirror of the", "universe in one line"]),
    (
        ("round 739: the queue drains before the storm", 4),
        ["round", "739:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 739: the queue drains before the storm", 8),
        ["round", "739: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 739: the queue drains before the storm", 12),
        ["round 739:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 739: the queue drains before the storm", 16), ["round 739: the", "queue drains", "before the storm"]),
    (("round 739: the queue drains before the storm", 24), ["round 739: the queue", "drains before the storm"]),
    (("round 739: the queue drains before the storm", 32), ["round 739: the queue drains", "before the storm"]),
    (
        ("kitten739 sitting739 agent739 angle739 universe739 memory739", 6),
        ["kitten739", "sitting739", "agent739", "angle739", "universe739", "memory739"],
    ),
    (
        ("kitten739 sitting739 agent739 angle739 universe739 memory739", 10),
        ["kitten739", "sitting739", "agent739", "angle739", "universe739", "memory739"],
    ),
    (
        ("kitten739 sitting739 agent739 angle739 universe739 memory739", 18),
        ["kitten739", "sitting739", "agent739 angle739", "universe739", "memory739"],
    ),
    (
        ("kitten739 sitting739 agent739 angle739 universe739 memory739", 28),
        ["kitten739 sitting739", "agent739 angle739", "universe739 memory739"],
    ),
    (
        ("sitting739 agent739 angle739 universe739 memory739 stream739", 6),
        ["sitting739", "agent739", "angle739", "universe739", "memory739", "stream739"],
    ),
    (
        ("sitting739 agent739 angle739 universe739 memory739 stream739", 10),
        ["sitting739", "agent739", "angle739", "universe739", "memory739", "stream739"],
    ),
    (
        ("sitting739 agent739 angle739 universe739 memory739 stream739", 18),
        ["sitting739", "agent739 angle739", "universe739", "memory739", "stream739"],
    ),
    (
        ("sitting739 agent739 angle739 universe739 memory739 stream739", 28),
        ["sitting739 agent739 angle739", "universe739 memory739", "stream739"],
    ),
    (
        ("agent739 angle739 universe739 memory739 stream739 context739", 6),
        ["agent739", "angle739", "universe739", "memory739", "stream739", "context739"],
    ),
    (
        ("agent739 angle739 universe739 memory739 stream739 context739", 10),
        ["agent739", "angle739", "universe739", "memory739", "stream739", "context739"],
    ),
    (
        ("agent739 angle739 universe739 memory739 stream739 context739", 18),
        ["agent739 angle739", "universe739", "memory739", "stream739", "context739"],
    ),
    (
        ("agent739 angle739 universe739 memory739 stream739 context739", 28),
        ["agent739 angle739", "universe739 memory739", "stream739 context739"],
    ),
    (
        ("angle739 universe739 memory739 stream739 context739 knowledge739", 6),
        ["angle739", "universe739", "memory739", "stream739", "context739", "knowledge739"],
    ),
    (
        ("angle739 universe739 memory739 stream739 context739 knowledge739", 10),
        ["angle739", "universe739", "memory739", "stream739", "context739", "knowledge739"],
    ),
    (
        ("angle739 universe739 memory739 stream739 context739 knowledge739", 18),
        ["angle739", "universe739", "memory739", "stream739", "context739", "knowledge739"],
    ),
    (
        ("angle739 universe739 memory739 stream739 context739 knowledge739", 28),
        ["angle739 universe739", "memory739 stream739", "context739 knowledge739"],
    ),
    (
        ("universe739 memory739 stream739 context739 knowledge739 vector739", 6),
        ["universe739", "memory739", "stream739", "context739", "knowledge739", "vector739"],
    ),
    (
        ("universe739 memory739 stream739 context739 knowledge739 vector739", 10),
        ["universe739", "memory739", "stream739", "context739", "knowledge739", "vector739"],
    ),
    (
        ("universe739 memory739 stream739 context739 knowledge739 vector739", 18),
        ["universe739", "memory739", "stream739", "context739", "knowledge739", "vector739"],
    ),
    (
        ("universe739 memory739 stream739 context739 knowledge739 vector739", 28),
        ["universe739 memory739", "stream739 context739", "knowledge739 vector739"],
    ),
    (
        ("memory739 stream739 context739 knowledge739 vector739 processor739", 6),
        ["memory739", "stream739", "context739", "knowledge739", "vector739", "processor739"],
    ),
    (
        ("memory739 stream739 context739 knowledge739 vector739 processor739", 10),
        ["memory739", "stream739", "context739", "knowledge739", "vector739", "processor739"],
    ),
    (
        ("memory739 stream739 context739 knowledge739 vector739 processor739", 18),
        ["memory739", "stream739", "context739", "knowledge739", "vector739", "processor739"],
    ),
    (
        ("memory739 stream739 context739 knowledge739 vector739 processor739", 28),
        ["memory739 stream739", "context739 knowledge739", "vector739 processor739"],
    ),
    (
        ("stream739 context739 knowledge739 vector739 processor739 reasoning739", 6),
        ["stream739", "context739", "knowledge739", "vector739", "processor739", "reasoning739"],
    ),
    (
        ("stream739 context739 knowledge739 vector739 processor739 reasoning739", 10),
        ["stream739", "context739", "knowledge739", "vector739", "processor739", "reasoning739"],
    ),
    (
        ("stream739 context739 knowledge739 vector739 processor739 reasoning739", 18),
        ["stream739", "context739", "knowledge739", "vector739", "processor739", "reasoning739"],
    ),
    (
        ("stream739 context739 knowledge739 vector739 processor739 reasoning739", 28),
        ["stream739 context739", "knowledge739 vector739", "processor739 reasoning739"],
    ),
    (
        ("context739 knowledge739 vector739 processor739 reasoning739 machine739", 6),
        ["context739", "knowledge739", "vector739", "processor739", "reasoning739", "machine739"],
    ),
    (
        ("context739 knowledge739 vector739 processor739 reasoning739 machine739", 10),
        ["context739", "knowledge739", "vector739", "processor739", "reasoning739", "machine739"],
    ),
    (
        ("context739 knowledge739 vector739 processor739 reasoning739 machine739", 18),
        ["context739", "knowledge739", "vector739", "processor739", "reasoning739", "machine739"],
    ),
    (
        ("context739 knowledge739 vector739 processor739 reasoning739 machine739", 28),
        ["context739 knowledge739", "vector739 processor739", "reasoning739 machine739"],
    ),
    (
        ("knowledge739 vector739 processor739 reasoning739 machine739 learning739", 6),
        ["knowledge739", "vector739", "processor739", "reasoning739", "machine739", "learning739"],
    ),
    (
        ("knowledge739 vector739 processor739 reasoning739 machine739 learning739", 10),
        ["knowledge739", "vector739", "processor739", "reasoning739", "machine739", "learning739"],
    ),
    (
        ("knowledge739 vector739 processor739 reasoning739 machine739 learning739", 18),
        ["knowledge739", "vector739", "processor739", "reasoning739", "machine739", "learning739"],
    ),
    (
        ("knowledge739 vector739 processor739 reasoning739 machine739 learning739", 28),
        ["knowledge739 vector739", "processor739 reasoning739", "machine739 learning739"],
    ),
    (
        ("vector739 processor739 reasoning739 machine739 learning739 model739", 6),
        ["vector739", "processor739", "reasoning739", "machine739", "learning739", "model739"],
    ),
    (
        ("vector739 processor739 reasoning739 machine739 learning739 model739", 10),
        ["vector739", "processor739", "reasoning739", "machine739", "learning739", "model739"],
    ),
    (
        ("vector739 processor739 reasoning739 machine739 learning739 model739", 18),
        ["vector739", "processor739", "reasoning739", "machine739", "learning739", "model739"],
    ),
    (
        ("vector739 processor739 reasoning739 machine739 learning739 model739", 28),
        ["vector739 processor739", "reasoning739 machine739", "learning739 model739"],
    ),
    (
        ("processor739 reasoning739 machine739 learning739 model739 token739", 6),
        ["processor739", "reasoning739", "machine739", "learning739", "model739", "token739"],
    ),
    (
        ("processor739 reasoning739 machine739 learning739 model739 token739", 10),
        ["processor739", "reasoning739", "machine739", "learning739", "model739", "token739"],
    ),
    (
        ("processor739 reasoning739 machine739 learning739 model739 token739", 18),
        ["processor739", "reasoning739", "machine739", "learning739", "model739 token739"],
    ),
    (
        ("processor739 reasoning739 machine739 learning739 model739 token739", 28),
        ["processor739 reasoning739", "machine739 learning739", "model739 token739"],
    ),
    (
        ("reasoning739 machine739 learning739 model739 token739 prompt739", 6),
        ["reasoning739", "machine739", "learning739", "model739", "token739", "prompt739"],
    ),
    (
        ("reasoning739 machine739 learning739 model739 token739 prompt739", 10),
        ["reasoning739", "machine739", "learning739", "model739", "token739", "prompt739"],
    ),
    (
        ("reasoning739 machine739 learning739 model739 token739 prompt739", 18),
        ["reasoning739", "machine739", "learning739", "model739 token739", "prompt739"],
    ),
    (
        ("reasoning739 machine739 learning739 model739 token739 prompt739", 28),
        ["reasoning739 machine739", "learning739 model739", "token739 prompt739"],
    ),
    (
        ("machine739 learning739 model739 token739 prompt739 session739", 6),
        ["machine739", "learning739", "model739", "token739", "prompt739", "session739"],
    ),
    (
        ("machine739 learning739 model739 token739 prompt739 session739", 10),
        ["machine739", "learning739", "model739", "token739", "prompt739", "session739"],
    ),
    (
        ("machine739 learning739 model739 token739 prompt739 session739", 18),
        ["machine739", "learning739", "model739 token739", "prompt739", "session739"],
    ),
    (
        ("machine739 learning739 model739 token739 prompt739 session739", 28),
        ["machine739 learning739", "model739 token739 prompt739", "session739"],
    ),
    (
        ("learning739 model739 token739 prompt739 session739 library739", 6),
        ["learning739", "model739", "token739", "prompt739", "session739", "library739"],
    ),
    (
        ("learning739 model739 token739 prompt739 session739 library739", 10),
        ["learning739", "model739", "token739", "prompt739", "session739", "library739"],
    ),
    (
        ("learning739 model739 token739 prompt739 session739 library739", 18),
        ["learning739", "model739 token739", "prompt739", "session739", "library739"],
    ),
    (
        ("learning739 model739 token739 prompt739 session739 library739", 28),
        ["learning739 model739", "token739 prompt739", "session739 library739"],
    ),
    (
        ("model739 token739 prompt739 session739 library739 service739", 6),
        ["model739", "token739", "prompt739", "session739", "library739", "service739"],
    ),
    (
        ("model739 token739 prompt739 session739 library739 service739", 10),
        ["model739", "token739", "prompt739", "session739", "library739", "service739"],
    ),
    (
        ("model739 token739 prompt739 session739 library739 service739", 18),
        ["model739 token739", "prompt739", "session739", "library739", "service739"],
    ),
    (
        ("model739 token739 prompt739 session739 library739 service739", 28),
        ["model739 token739 prompt739", "session739 library739", "service739"],
    ),
    (
        ("token739 prompt739 session739 library739 service739 gateway739", 6),
        ["token739", "prompt739", "session739", "library739", "service739", "gateway739"],
    ),
    (
        ("token739 prompt739 session739 library739 service739 gateway739", 10),
        ["token739", "prompt739", "session739", "library739", "service739", "gateway739"],
    ),
    (
        ("token739 prompt739 session739 library739 service739 gateway739", 18),
        ["token739 prompt739", "session739", "library739", "service739", "gateway739"],
    ),
    (
        ("token739 prompt739 session739 library739 service739 gateway739", 28),
        ["token739 prompt739", "session739 library739", "service739 gateway739"],
    ),
    (
        ("prompt739 session739 library739 service739 gateway739 storage739", 6),
        ["prompt739", "session739", "library739", "service739", "gateway739", "storage739"],
    ),
    (
        ("prompt739 session739 library739 service739 gateway739 storage739", 10),
        ["prompt739", "session739", "library739", "service739", "gateway739", "storage739"],
    ),
    (
        ("prompt739 session739 library739 service739 gateway739 storage739", 18),
        ["prompt739", "session739", "library739", "service739", "gateway739", "storage739"],
    ),
    (
        ("prompt739 session739 library739 service739 gateway739 storage739", 28),
        ["prompt739 session739", "library739 service739", "gateway739 storage739"],
    ),
    (
        ("session739 library739 service739 gateway739 storage739 network739", 6),
        ["session739", "library739", "service739", "gateway739", "storage739", "network739"],
    ),
    (
        ("session739 library739 service739 gateway739 storage739 network739", 10),
        ["session739", "library739", "service739", "gateway739", "storage739", "network739"],
    ),
    (
        ("session739 library739 service739 gateway739 storage739 network739", 18),
        ["session739", "library739", "service739", "gateway739", "storage739", "network739"],
    ),
    (
        ("session739 library739 service739 gateway739 storage739 network739", 28),
        ["session739 library739", "service739 gateway739", "storage739 network739"],
    ),
    (
        ("library739 service739 gateway739 storage739 network739 latency739", 6),
        ["library739", "service739", "gateway739", "storage739", "network739", "latency739"],
    ),
    (
        ("library739 service739 gateway739 storage739 network739 latency739", 10),
        ["library739", "service739", "gateway739", "storage739", "network739", "latency739"],
    ),
    (
        ("library739 service739 gateway739 storage739 network739 latency739", 18),
        ["library739", "service739", "gateway739", "storage739", "network739", "latency739"],
    ),
    (
        ("library739 service739 gateway739 storage739 network739 latency739", 28),
        ["library739 service739", "gateway739 storage739", "network739 latency739"],
    ),
    (
        ("service739 gateway739 storage739 network739 latency739 buffer739", 6),
        ["service739", "gateway739", "storage739", "network739", "latency739", "buffer739"],
    ),
    (
        ("service739 gateway739 storage739 network739 latency739 buffer739", 10),
        ["service739", "gateway739", "storage739", "network739", "latency739", "buffer739"],
    ),
    (
        ("service739 gateway739 storage739 network739 latency739 buffer739", 18),
        ["service739", "gateway739", "storage739", "network739", "latency739", "buffer739"],
    ),
    (
        ("service739 gateway739 storage739 network739 latency739 buffer739", 28),
        ["service739 gateway739", "storage739 network739", "latency739 buffer739"],
    ),
    (
        ("gateway739 storage739 network739 latency739 buffer739 queue739", 6),
        ["gateway739", "storage739", "network739", "latency739", "buffer739", "queue739"],
    ),
    (
        ("gateway739 storage739 network739 latency739 buffer739 queue739", 10),
        ["gateway739", "storage739", "network739", "latency739", "buffer739", "queue739"],
    ),
    (
        ("gateway739 storage739 network739 latency739 buffer739 queue739", 18),
        ["gateway739", "storage739", "network739", "latency739", "buffer739 queue739"],
    ),
    (
        ("gateway739 storage739 network739 latency739 buffer739 queue739", 28),
        ["gateway739 storage739", "network739 latency739", "buffer739 queue739"],
    ),
    (
        ("storage739 network739 latency739 buffer739 queue739 worker739", 6),
        ["storage739", "network739", "latency739", "buffer739", "queue739", "worker739"],
    ),
    (
        ("storage739 network739 latency739 buffer739 queue739 worker739", 10),
        ["storage739", "network739", "latency739", "buffer739", "queue739", "worker739"],
    ),
    (
        ("storage739 network739 latency739 buffer739 queue739 worker739", 18),
        ["storage739", "network739", "latency739", "buffer739 queue739", "worker739"],
    ),
    (
        ("storage739 network739 latency739 buffer739 queue739 worker739", 28),
        ["storage739 network739", "latency739 buffer739", "queue739 worker739"],
    ),
    (
        ("network739 latency739 buffer739 queue739 worker739 kernel739", 6),
        ["network739", "latency739", "buffer739", "queue739", "worker739", "kernel739"],
    ),
    (
        ("network739 latency739 buffer739 queue739 worker739 kernel739", 10),
        ["network739", "latency739", "buffer739", "queue739", "worker739", "kernel739"],
    ),
    (
        ("network739 latency739 buffer739 queue739 worker739 kernel739", 18),
        ["network739", "latency739", "buffer739 queue739", "worker739", "kernel739"],
    ),
    (
        ("network739 latency739 buffer739 queue739 worker739 kernel739", 28),
        ["network739 latency739", "buffer739 queue739 worker739", "kernel739"],
    ),
    (
        ("latency739 buffer739 queue739 worker739 kernel739 signal739", 6),
        ["latency739", "buffer739", "queue739", "worker739", "kernel739", "signal739"],
    ),
    (
        ("latency739 buffer739 queue739 worker739 kernel739 signal739", 10),
        ["latency739", "buffer739", "queue739", "worker739", "kernel739", "signal739"],
    ),
    (
        ("latency739 buffer739 queue739 worker739 kernel739 signal739", 18),
        ["latency739", "buffer739 queue739", "worker739", "kernel739", "signal739"],
    ),
    (
        ("latency739 buffer739 queue739 worker739 kernel739 signal739", 28),
        ["latency739 buffer739", "queue739 worker739 kernel739", "signal739"],
    ),
    (
        ("buffer739 queue739 worker739 kernel739 signal739 packet739", 6),
        ["buffer739", "queue739", "worker739", "kernel739", "signal739", "packet739"],
    ),
    (
        ("buffer739 queue739 worker739 kernel739 signal739 packet739", 10),
        ["buffer739", "queue739", "worker739", "kernel739", "signal739", "packet739"],
    ),
    (
        ("buffer739 queue739 worker739 kernel739 signal739 packet739", 18),
        ["buffer739 queue739", "worker739", "kernel739", "signal739", "packet739"],
    ),
    (
        ("buffer739 queue739 worker739 kernel739 signal739 packet739", 28),
        ["buffer739 queue739 worker739", "kernel739 signal739", "packet739"],
    ),
    (
        ("queue739 worker739 kernel739 signal739 packet739 router739", 6),
        ["queue739", "worker739", "kernel739", "signal739", "packet739", "router739"],
    ),
    (
        ("queue739 worker739 kernel739 signal739 packet739 router739", 10),
        ["queue739", "worker739", "kernel739", "signal739", "packet739", "router739"],
    ),
    (
        ("queue739 worker739 kernel739 signal739 packet739 router739", 18),
        ["queue739 worker739", "kernel739", "signal739", "packet739", "router739"],
    ),
    (
        ("queue739 worker739 kernel739 signal739 packet739 router739", 28),
        ["queue739 worker739 kernel739", "signal739 packet739", "router739"],
    ),
    (
        ("worker739 kernel739 signal739 packet739 router739 cluster739", 6),
        ["worker739", "kernel739", "signal739", "packet739", "router739", "cluster739"],
    ),
    (
        ("worker739 kernel739 signal739 packet739 router739 cluster739", 10),
        ["worker739", "kernel739", "signal739", "packet739", "router739", "cluster739"],
    ),
    (
        ("worker739 kernel739 signal739 packet739 router739 cluster739", 18),
        ["worker739", "kernel739", "signal739", "packet739", "router739", "cluster739"],
    ),
    (
        ("worker739 kernel739 signal739 packet739 router739 cluster739", 28),
        ["worker739 kernel739", "signal739 packet739", "router739 cluster739"],
    ),
    (
        ("kernel739 signal739 packet739 router739 cluster739 mirror739", 6),
        ["kernel739", "signal739", "packet739", "router739", "cluster739", "mirror739"],
    ),
    (
        ("kernel739 signal739 packet739 router739 cluster739 mirror739", 10),
        ["kernel739", "signal739", "packet739", "router739", "cluster739", "mirror739"],
    ),
    (
        ("kernel739 signal739 packet739 router739 cluster739 mirror739", 18),
        ["kernel739", "signal739", "packet739", "router739", "cluster739", "mirror739"],
    ),
    (
        ("kernel739 signal739 packet739 router739 cluster739 mirror739", 28),
        ["kernel739 signal739", "packet739 router739", "cluster739 mirror739"],
    ),
    (
        ("signal739 packet739 router739 cluster739 mirror739 filter739", 6),
        ["signal739", "packet739", "router739", "cluster739", "mirror739", "filter739"],
    ),
    (
        ("signal739 packet739 router739 cluster739 mirror739 filter739", 10),
        ["signal739", "packet739", "router739", "cluster739", "mirror739", "filter739"],
    ),
    (
        ("signal739 packet739 router739 cluster739 mirror739 filter739", 18),
        ["signal739", "packet739", "router739", "cluster739", "mirror739", "filter739"],
    ),
    (
        ("signal739 packet739 router739 cluster739 mirror739 filter739", 28),
        ["signal739 packet739", "router739 cluster739", "mirror739 filter739"],
    ),
    (
        ("packet739 router739 cluster739 mirror739 filter739 ranking739", 6),
        ["packet739", "router739", "cluster739", "mirror739", "filter739", "ranking739"],
    ),
    (
        ("packet739 router739 cluster739 mirror739 filter739 ranking739", 10),
        ["packet739", "router739", "cluster739", "mirror739", "filter739", "ranking739"],
    ),
    (
        ("packet739 router739 cluster739 mirror739 filter739 ranking739", 18),
        ["packet739", "router739", "cluster739", "mirror739", "filter739", "ranking739"],
    ),
    (
        ("packet739 router739 cluster739 mirror739 filter739 ranking739", 28),
        ["packet739 router739", "cluster739 mirror739", "filter739 ranking739"],
    ),
    (
        ("router739 cluster739 mirror739 filter739 ranking739 encoding739", 6),
        ["router739", "cluster739", "mirror739", "filter739", "ranking739", "encoding739"],
    ),
    (
        ("router739 cluster739 mirror739 filter739 ranking739 encoding739", 10),
        ["router739", "cluster739", "mirror739", "filter739", "ranking739", "encoding739"],
    ),
    (
        ("router739 cluster739 mirror739 filter739 ranking739 encoding739", 18),
        ["router739", "cluster739", "mirror739", "filter739", "ranking739", "encoding739"],
    ),
    (
        ("router739 cluster739 mirror739 filter739 ranking739 encoding739", 28),
        ["router739 cluster739", "mirror739 filter739", "ranking739 encoding739"],
    ),
    (
        ("cluster739 mirror739 filter739 ranking739 encoding739 mapping739", 6),
        ["cluster739", "mirror739", "filter739", "ranking739", "encoding739", "mapping739"],
    ),
    (
        ("cluster739 mirror739 filter739 ranking739 encoding739 mapping739", 10),
        ["cluster739", "mirror739", "filter739", "ranking739", "encoding739", "mapping739"],
    ),
    (
        ("cluster739 mirror739 filter739 ranking739 encoding739 mapping739", 18),
        ["cluster739", "mirror739", "filter739", "ranking739", "encoding739", "mapping739"],
    ),
    (
        ("cluster739 mirror739 filter739 ranking739 encoding739 mapping739", 28),
        ["cluster739 mirror739", "filter739 ranking739", "encoding739 mapping739"],
    ),
    (
        ("mirror739 filter739 ranking739 encoding739 mapping739 record739", 6),
        ["mirror739", "filter739", "ranking739", "encoding739", "mapping739", "record739"],
    ),
    (
        ("mirror739 filter739 ranking739 encoding739 mapping739 record739", 10),
        ["mirror739", "filter739", "ranking739", "encoding739", "mapping739", "record739"],
    ),
    (
        ("mirror739 filter739 ranking739 encoding739 mapping739 record739", 18),
        ["mirror739", "filter739", "ranking739", "encoding739", "mapping739", "record739"],
    ),
    (
        ("mirror739 filter739 ranking739 encoding739 mapping739 record739", 28),
        ["mirror739 filter739", "ranking739 encoding739", "mapping739 record739"],
    ),
    (
        ("filter739 ranking739 encoding739 mapping739 record739 candle739", 6),
        ["filter739", "ranking739", "encoding739", "mapping739", "record739", "candle739"],
    ),
    (
        ("filter739 ranking739 encoding739 mapping739 record739 candle739", 10),
        ["filter739", "ranking739", "encoding739", "mapping739", "record739", "candle739"],
    ),
    (
        ("filter739 ranking739 encoding739 mapping739 record739 candle739", 18),
        ["filter739", "ranking739", "encoding739", "mapping739", "record739", "candle739"],
    ),
    (
        ("filter739 ranking739 encoding739 mapping739 record739 candle739", 28),
        ["filter739 ranking739", "encoding739 mapping739", "record739 candle739"],
    ),
    (
        ("ranking739 encoding739 mapping739 record739 candle739 thread739", 6),
        ["ranking739", "encoding739", "mapping739", "record739", "candle739", "thread739"],
    ),
    (
        ("ranking739 encoding739 mapping739 record739 candle739 thread739", 10),
        ["ranking739", "encoding739", "mapping739", "record739", "candle739", "thread739"],
    ),
    (
        ("ranking739 encoding739 mapping739 record739 candle739 thread739", 18),
        ["ranking739", "encoding739", "mapping739", "record739", "candle739", "thread739"],
    ),
    (
        ("ranking739 encoding739 mapping739 record739 candle739 thread739", 28),
        ["ranking739 encoding739", "mapping739 record739", "candle739 thread739"],
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
