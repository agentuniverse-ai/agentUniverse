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
        ("round 191: the quick brown fox jumps over the lazy dog", 4),
        ["round", "191:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", 8),
        ["round", "191: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", 12),
        ["round 191:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", 16),
        ["round 191: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", 24),
        ["round 191: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 191: the quick brown fox jumps over the lazy dog", 32),
        ["round 191: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", 4),
        ["round", "191:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", 8),
        ["round", "191:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", 12),
        ["round 191:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", 16),
        ["round 191:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", 24),
        ["round 191: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 191: agentuniverse is a framework for multi agents", 32),
        ["round 191: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", 4),
        ["round", "191:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", 8),
        ["round", "191:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", 12),
        ["round 191:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", 16),
        ["round 191:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", 24),
        ["round 191: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 191: knowledge stored as vectors enables retrieval", 32),
        ["round 191: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 191: the processor reads the record then stops", 4),
        ["round", "191:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 191: the processor reads the record then stops", 8),
        ["round", "191: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 191: the processor reads the record then stops", 12),
        ["round 191:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 191: the processor reads the record then stops", 16),
        ["round 191: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 191: the processor reads the record then stops", 24),
        ["round 191: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 191: the processor reads the record then stops", 32),
        ["round 191: the processor reads", "the record then stops"],
    ),
    (
        ("round 191: a worker pulls the next task from the queue", 4),
        ["round", "191:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 191: a worker pulls the next task from the queue", 8),
        ["round", "191: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 191: a worker pulls the next task from the queue", 12),
        ["round 191: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 191: a worker pulls the next task from the queue", 16),
        ["round 191: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 191: a worker pulls the next task from the queue", 24),
        ["round 191: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 191: a worker pulls the next task from the queue", 32),
        ["round 191: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 191: signals travel through the network layer", 4),
        ["round", "191:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 191: signals travel through the network layer", 8),
        ["round", "191:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 191: signals travel through the network layer", 12),
        ["round 191:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 191: signals travel through the network layer", 16),
        ["round 191:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 191: signals travel through the network layer", 24),
        ["round 191: signals", "travel through the", "network layer"],
    ),
    (
        ("round 191: signals travel through the network layer", 32),
        ["round 191: signals travel", "through the network layer"],
    ),
    (
        ("round 191: the gateway routes each request by policy", 4),
        ["round", "191:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 191: the gateway routes each request by policy", 8),
        ["round", "191: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 191: the gateway routes each request by policy", 12),
        ["round 191:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 191: the gateway routes each request by policy", 16),
        ["round 191: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 191: the gateway routes each request by policy", 24),
        ["round 191: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 191: the gateway routes each request by policy", 32),
        ["round 191: the gateway routes", "each request by policy"],
    ),
    (
        ("round 191: memory grows until the buffer is full", 4),
        ["round", "191:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 191: memory grows until the buffer is full", 8),
        ["round", "191:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 191: memory grows until the buffer is full", 12),
        ["round 191:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 191: memory grows until the buffer is full", 16),
        ["round 191:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 191: memory grows until the buffer is full", 24), ["round 191: memory grows", "until the buffer is full"]),
    (("round 191: memory grows until the buffer is full", 32), ["round 191: memory grows until", "the buffer is full"]),
    (
        ("round 191: the cluster mirrors every packet twice", 4),
        ["round", "191:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 191: the cluster mirrors every packet twice", 8),
        ["round", "191: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 191: the cluster mirrors every packet twice", 12),
        ["round 191:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 191: the cluster mirrors every packet twice", 16),
        ["round 191: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 191: the cluster mirrors every packet twice", 24),
        ["round 191: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 191: the cluster mirrors every packet twice", 32),
        ["round 191: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", 4),
        ["round", "191:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", 8),
        ["round", "191:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", 12),
        ["round 191:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", 16),
        ["round 191:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", 24),
        ["round 191: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 191: ranking uses tokens learned from the corpus", 32),
        ["round 191: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 191: a long session ends when the candle dies", 4),
        ["round", "191:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 191: a long session ends when the candle dies", 8),
        ["round", "191: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 191: a long session ends when the candle dies", 12),
        ["round 191: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 191: a long session ends when the candle dies", 16),
        ["round 191: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 191: a long session ends when the candle dies", 24),
        ["round 191: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 191: a long session ends when the candle dies", 32),
        ["round 191: a long session ends", "when the candle dies"],
    ),
    (
        ("round 191: encode the prompt then map the result", 4),
        ["round", "191:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 191: encode the prompt then map the result", 8),
        ["round", "191:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 191: encode the prompt then map the result", 12),
        ["round 191:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 191: encode the prompt then map the result", 16),
        ["round 191:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 191: encode the prompt then map the result", 24),
        ["round 191: encode the", "prompt then map the", "result"],
    ),
    (("round 191: encode the prompt then map the result", 32), ["round 191: encode the prompt", "then map the result"]),
    (
        ("round 191: the kernel wakes the worker at dawn", 4),
        ["round", "191:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 191: the kernel wakes the worker at dawn", 8),
        ["round", "191: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 191: the kernel wakes the worker at dawn", 12),
        ["round 191:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 191: the kernel wakes the worker at dawn", 16), ["round 191: the", "kernel wakes the", "worker at dawn"]),
    (("round 191: the kernel wakes the worker at dawn", 24), ["round 191: the kernel", "wakes the worker at dawn"]),
    (("round 191: the kernel wakes the worker at dawn", 32), ["round 191: the kernel wakes the", "worker at dawn"]),
    (
        ("round 191: service latency drops after the patch", 4),
        ["round", "191:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 191: service latency drops after the patch", 8),
        ["round", "191:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 191: service latency drops after the patch", 12),
        ["round 191:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 191: service latency drops after the patch", 16),
        ["round 191:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 191: service latency drops after the patch", 24),
        ["round 191: service", "latency drops after the", "patch"],
    ),
    (("round 191: service latency drops after the patch", 32), ["round 191: service latency drops", "after the patch"]),
    (
        ("round 191: the library caches every vector it sees", 4),
        ["round", "191:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 191: the library caches every vector it sees", 8),
        ["round", "191: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 191: the library caches every vector it sees", 12),
        ["round 191:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 191: the library caches every vector it sees", 16),
        ["round 191: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 191: the library caches every vector it sees", 24),
        ["round 191: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 191: the library caches every vector it sees", 32),
        ["round 191: the library caches", "every vector it sees"],
    ),
    (
        ("round 191: agents argue then the debate resolves", 4),
        ["round", "191:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 191: agents argue then the debate resolves", 8),
        ["round", "191:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 191: agents argue then the debate resolves", 12),
        ["round 191:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 191: agents argue then the debate resolves", 16),
        ["round 191:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 191: agents argue then the debate resolves", 24), ["round 191: agents argue", "then the debate resolves"]),
    (("round 191: agents argue then the debate resolves", 32), ["round 191: agents argue then the", "debate resolves"]),
    (
        ("round 191: the filter keeps only strong matches", 4),
        ["round", "191:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 191: the filter keeps only strong matches", 8),
        ["round", "191: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 191: the filter keeps only strong matches", 12),
        ["round 191:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 191: the filter keeps only strong matches", 16),
        ["round 191: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 191: the filter keeps only strong matches", 24),
        ["round 191: the filter", "keeps only strong", "matches"],
    ),
    (("round 191: the filter keeps only strong matches", 32), ["round 191: the filter keeps only", "strong matches"]),
    (
        ("round 191: the model answers with a short reply", 4),
        ["round", "191:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 191: the model answers with a short reply", 8),
        ["round", "191: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 191: the model answers with a short reply", 12),
        ["round 191:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 191: the model answers with a short reply", 16),
        ["round 191: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 191: the model answers with a short reply", 24),
        ["round 191: the model", "answers with a short", "reply"],
    ),
    (("round 191: the model answers with a short reply", 32), ["round 191: the model answers", "with a short reply"]),
    (
        ("round 191: the recorder stores the reasoning trace", 4),
        ["round", "191:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 191: the recorder stores the reasoning trace", 8),
        ["round", "191: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 191: the recorder stores the reasoning trace", 12),
        ["round 191:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 191: the recorder stores the reasoning trace", 16),
        ["round 191: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 191: the recorder stores the reasoning trace", 24),
        ["round 191: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 191: the recorder stores the reasoning trace", 32),
        ["round 191: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 191: the angel watches the processor run", 4),
        ["round", "191:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 191: the angel watches the processor run", 8),
        ["round", "191: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 191: the angel watches the processor run", 12),
        ["round 191:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 191: the angel watches the processor run", 16),
        ["round 191: the", "angel watches", "the processor", "run"],
    ),
    (("round 191: the angel watches the processor run", 24), ["round 191: the angel", "watches the processor", "run"]),
    (("round 191: the angel watches the processor run", 32), ["round 191: the angel watches the", "processor run"]),
    (
        ("round 191: angle of the vector decides the match", 4),
        ["round", "191:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 191: angle of the vector decides the match", 8),
        ["round", "191:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 191: angle of the vector decides the match", 12),
        ["round 191:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 191: angle of the vector decides the match", 16),
        ["round 191: angle", "of the vector", "decides the", "match"],
    ),
    (("round 191: angle of the vector decides the match", 24), ["round 191: angle of the", "vector decides the match"]),
    (("round 191: angle of the vector decides the match", 32), ["round 191: angle of the vector", "decides the match"]),
    (
        ("round 191: the candle burns twice as long at night", 4),
        ["round", "191:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 191: the candle burns twice as long at night", 8),
        ["round", "191: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 191: the candle burns twice as long at night", 12),
        ["round 191:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 191: the candle burns twice as long at night", 16),
        ["round 191: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 191: the candle burns twice as long at night", 24),
        ["round 191: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 191: the candle burns twice as long at night", 32),
        ["round 191: the candle burns", "twice as long at night"],
    ),
    (
        ("round 191: a mirror of the universe in one line", 4),
        ["round", "191:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 191: a mirror of the universe in one line", 8),
        ["round", "191: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 191: a mirror of the universe in one line", 12),
        ["round 191: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 191: a mirror of the universe in one line", 16),
        ["round 191: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 191: a mirror of the universe in one line", 24), ["round 191: a mirror of", "the universe in one line"]),
    (("round 191: a mirror of the universe in one line", 32), ["round 191: a mirror of the", "universe in one line"]),
    (
        ("round 191: the queue drains before the storm", 4),
        ["round", "191:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 191: the queue drains before the storm", 8),
        ["round", "191: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 191: the queue drains before the storm", 12),
        ["round 191:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 191: the queue drains before the storm", 16), ["round 191: the", "queue drains", "before the storm"]),
    (("round 191: the queue drains before the storm", 24), ["round 191: the queue", "drains before the storm"]),
    (("round 191: the queue drains before the storm", 32), ["round 191: the queue drains", "before the storm"]),
    (
        ("kitten191 sitting191 agent191 angle191 universe191 memory191", 6),
        ["kitten191", "sitting191", "agent191", "angle191", "universe191", "memory191"],
    ),
    (
        ("kitten191 sitting191 agent191 angle191 universe191 memory191", 10),
        ["kitten191", "sitting191", "agent191", "angle191", "universe191", "memory191"],
    ),
    (
        ("kitten191 sitting191 agent191 angle191 universe191 memory191", 18),
        ["kitten191", "sitting191", "agent191 angle191", "universe191", "memory191"],
    ),
    (
        ("kitten191 sitting191 agent191 angle191 universe191 memory191", 28),
        ["kitten191 sitting191", "agent191 angle191", "universe191 memory191"],
    ),
    (
        ("sitting191 agent191 angle191 universe191 memory191 stream191", 6),
        ["sitting191", "agent191", "angle191", "universe191", "memory191", "stream191"],
    ),
    (
        ("sitting191 agent191 angle191 universe191 memory191 stream191", 10),
        ["sitting191", "agent191", "angle191", "universe191", "memory191", "stream191"],
    ),
    (
        ("sitting191 agent191 angle191 universe191 memory191 stream191", 18),
        ["sitting191", "agent191 angle191", "universe191", "memory191", "stream191"],
    ),
    (
        ("sitting191 agent191 angle191 universe191 memory191 stream191", 28),
        ["sitting191 agent191 angle191", "universe191 memory191", "stream191"],
    ),
    (
        ("agent191 angle191 universe191 memory191 stream191 context191", 6),
        ["agent191", "angle191", "universe191", "memory191", "stream191", "context191"],
    ),
    (
        ("agent191 angle191 universe191 memory191 stream191 context191", 10),
        ["agent191", "angle191", "universe191", "memory191", "stream191", "context191"],
    ),
    (
        ("agent191 angle191 universe191 memory191 stream191 context191", 18),
        ["agent191 angle191", "universe191", "memory191", "stream191", "context191"],
    ),
    (
        ("agent191 angle191 universe191 memory191 stream191 context191", 28),
        ["agent191 angle191", "universe191 memory191", "stream191 context191"],
    ),
    (
        ("angle191 universe191 memory191 stream191 context191 knowledge191", 6),
        ["angle191", "universe191", "memory191", "stream191", "context191", "knowledge191"],
    ),
    (
        ("angle191 universe191 memory191 stream191 context191 knowledge191", 10),
        ["angle191", "universe191", "memory191", "stream191", "context191", "knowledge191"],
    ),
    (
        ("angle191 universe191 memory191 stream191 context191 knowledge191", 18),
        ["angle191", "universe191", "memory191", "stream191", "context191", "knowledge191"],
    ),
    (
        ("angle191 universe191 memory191 stream191 context191 knowledge191", 28),
        ["angle191 universe191", "memory191 stream191", "context191 knowledge191"],
    ),
    (
        ("universe191 memory191 stream191 context191 knowledge191 vector191", 6),
        ["universe191", "memory191", "stream191", "context191", "knowledge191", "vector191"],
    ),
    (
        ("universe191 memory191 stream191 context191 knowledge191 vector191", 10),
        ["universe191", "memory191", "stream191", "context191", "knowledge191", "vector191"],
    ),
    (
        ("universe191 memory191 stream191 context191 knowledge191 vector191", 18),
        ["universe191", "memory191", "stream191", "context191", "knowledge191", "vector191"],
    ),
    (
        ("universe191 memory191 stream191 context191 knowledge191 vector191", 28),
        ["universe191 memory191", "stream191 context191", "knowledge191 vector191"],
    ),
    (
        ("memory191 stream191 context191 knowledge191 vector191 processor191", 6),
        ["memory191", "stream191", "context191", "knowledge191", "vector191", "processor191"],
    ),
    (
        ("memory191 stream191 context191 knowledge191 vector191 processor191", 10),
        ["memory191", "stream191", "context191", "knowledge191", "vector191", "processor191"],
    ),
    (
        ("memory191 stream191 context191 knowledge191 vector191 processor191", 18),
        ["memory191", "stream191", "context191", "knowledge191", "vector191", "processor191"],
    ),
    (
        ("memory191 stream191 context191 knowledge191 vector191 processor191", 28),
        ["memory191 stream191", "context191 knowledge191", "vector191 processor191"],
    ),
    (
        ("stream191 context191 knowledge191 vector191 processor191 reasoning191", 6),
        ["stream191", "context191", "knowledge191", "vector191", "processor191", "reasoning191"],
    ),
    (
        ("stream191 context191 knowledge191 vector191 processor191 reasoning191", 10),
        ["stream191", "context191", "knowledge191", "vector191", "processor191", "reasoning191"],
    ),
    (
        ("stream191 context191 knowledge191 vector191 processor191 reasoning191", 18),
        ["stream191", "context191", "knowledge191", "vector191", "processor191", "reasoning191"],
    ),
    (
        ("stream191 context191 knowledge191 vector191 processor191 reasoning191", 28),
        ["stream191 context191", "knowledge191 vector191", "processor191 reasoning191"],
    ),
    (
        ("context191 knowledge191 vector191 processor191 reasoning191 machine191", 6),
        ["context191", "knowledge191", "vector191", "processor191", "reasoning191", "machine191"],
    ),
    (
        ("context191 knowledge191 vector191 processor191 reasoning191 machine191", 10),
        ["context191", "knowledge191", "vector191", "processor191", "reasoning191", "machine191"],
    ),
    (
        ("context191 knowledge191 vector191 processor191 reasoning191 machine191", 18),
        ["context191", "knowledge191", "vector191", "processor191", "reasoning191", "machine191"],
    ),
    (
        ("context191 knowledge191 vector191 processor191 reasoning191 machine191", 28),
        ["context191 knowledge191", "vector191 processor191", "reasoning191 machine191"],
    ),
    (
        ("knowledge191 vector191 processor191 reasoning191 machine191 learning191", 6),
        ["knowledge191", "vector191", "processor191", "reasoning191", "machine191", "learning191"],
    ),
    (
        ("knowledge191 vector191 processor191 reasoning191 machine191 learning191", 10),
        ["knowledge191", "vector191", "processor191", "reasoning191", "machine191", "learning191"],
    ),
    (
        ("knowledge191 vector191 processor191 reasoning191 machine191 learning191", 18),
        ["knowledge191", "vector191", "processor191", "reasoning191", "machine191", "learning191"],
    ),
    (
        ("knowledge191 vector191 processor191 reasoning191 machine191 learning191", 28),
        ["knowledge191 vector191", "processor191 reasoning191", "machine191 learning191"],
    ),
    (
        ("vector191 processor191 reasoning191 machine191 learning191 model191", 6),
        ["vector191", "processor191", "reasoning191", "machine191", "learning191", "model191"],
    ),
    (
        ("vector191 processor191 reasoning191 machine191 learning191 model191", 10),
        ["vector191", "processor191", "reasoning191", "machine191", "learning191", "model191"],
    ),
    (
        ("vector191 processor191 reasoning191 machine191 learning191 model191", 18),
        ["vector191", "processor191", "reasoning191", "machine191", "learning191", "model191"],
    ),
    (
        ("vector191 processor191 reasoning191 machine191 learning191 model191", 28),
        ["vector191 processor191", "reasoning191 machine191", "learning191 model191"],
    ),
    (
        ("processor191 reasoning191 machine191 learning191 model191 token191", 6),
        ["processor191", "reasoning191", "machine191", "learning191", "model191", "token191"],
    ),
    (
        ("processor191 reasoning191 machine191 learning191 model191 token191", 10),
        ["processor191", "reasoning191", "machine191", "learning191", "model191", "token191"],
    ),
    (
        ("processor191 reasoning191 machine191 learning191 model191 token191", 18),
        ["processor191", "reasoning191", "machine191", "learning191", "model191 token191"],
    ),
    (
        ("processor191 reasoning191 machine191 learning191 model191 token191", 28),
        ["processor191 reasoning191", "machine191 learning191", "model191 token191"],
    ),
    (
        ("reasoning191 machine191 learning191 model191 token191 prompt191", 6),
        ["reasoning191", "machine191", "learning191", "model191", "token191", "prompt191"],
    ),
    (
        ("reasoning191 machine191 learning191 model191 token191 prompt191", 10),
        ["reasoning191", "machine191", "learning191", "model191", "token191", "prompt191"],
    ),
    (
        ("reasoning191 machine191 learning191 model191 token191 prompt191", 18),
        ["reasoning191", "machine191", "learning191", "model191 token191", "prompt191"],
    ),
    (
        ("reasoning191 machine191 learning191 model191 token191 prompt191", 28),
        ["reasoning191 machine191", "learning191 model191", "token191 prompt191"],
    ),
    (
        ("machine191 learning191 model191 token191 prompt191 session191", 6),
        ["machine191", "learning191", "model191", "token191", "prompt191", "session191"],
    ),
    (
        ("machine191 learning191 model191 token191 prompt191 session191", 10),
        ["machine191", "learning191", "model191", "token191", "prompt191", "session191"],
    ),
    (
        ("machine191 learning191 model191 token191 prompt191 session191", 18),
        ["machine191", "learning191", "model191 token191", "prompt191", "session191"],
    ),
    (
        ("machine191 learning191 model191 token191 prompt191 session191", 28),
        ["machine191 learning191", "model191 token191 prompt191", "session191"],
    ),
    (
        ("learning191 model191 token191 prompt191 session191 library191", 6),
        ["learning191", "model191", "token191", "prompt191", "session191", "library191"],
    ),
    (
        ("learning191 model191 token191 prompt191 session191 library191", 10),
        ["learning191", "model191", "token191", "prompt191", "session191", "library191"],
    ),
    (
        ("learning191 model191 token191 prompt191 session191 library191", 18),
        ["learning191", "model191 token191", "prompt191", "session191", "library191"],
    ),
    (
        ("learning191 model191 token191 prompt191 session191 library191", 28),
        ["learning191 model191", "token191 prompt191", "session191 library191"],
    ),
    (
        ("model191 token191 prompt191 session191 library191 service191", 6),
        ["model191", "token191", "prompt191", "session191", "library191", "service191"],
    ),
    (
        ("model191 token191 prompt191 session191 library191 service191", 10),
        ["model191", "token191", "prompt191", "session191", "library191", "service191"],
    ),
    (
        ("model191 token191 prompt191 session191 library191 service191", 18),
        ["model191 token191", "prompt191", "session191", "library191", "service191"],
    ),
    (
        ("model191 token191 prompt191 session191 library191 service191", 28),
        ["model191 token191 prompt191", "session191 library191", "service191"],
    ),
    (
        ("token191 prompt191 session191 library191 service191 gateway191", 6),
        ["token191", "prompt191", "session191", "library191", "service191", "gateway191"],
    ),
    (
        ("token191 prompt191 session191 library191 service191 gateway191", 10),
        ["token191", "prompt191", "session191", "library191", "service191", "gateway191"],
    ),
    (
        ("token191 prompt191 session191 library191 service191 gateway191", 18),
        ["token191 prompt191", "session191", "library191", "service191", "gateway191"],
    ),
    (
        ("token191 prompt191 session191 library191 service191 gateway191", 28),
        ["token191 prompt191", "session191 library191", "service191 gateway191"],
    ),
    (
        ("prompt191 session191 library191 service191 gateway191 storage191", 6),
        ["prompt191", "session191", "library191", "service191", "gateway191", "storage191"],
    ),
    (
        ("prompt191 session191 library191 service191 gateway191 storage191", 10),
        ["prompt191", "session191", "library191", "service191", "gateway191", "storage191"],
    ),
    (
        ("prompt191 session191 library191 service191 gateway191 storage191", 18),
        ["prompt191", "session191", "library191", "service191", "gateway191", "storage191"],
    ),
    (
        ("prompt191 session191 library191 service191 gateway191 storage191", 28),
        ["prompt191 session191", "library191 service191", "gateway191 storage191"],
    ),
    (
        ("session191 library191 service191 gateway191 storage191 network191", 6),
        ["session191", "library191", "service191", "gateway191", "storage191", "network191"],
    ),
    (
        ("session191 library191 service191 gateway191 storage191 network191", 10),
        ["session191", "library191", "service191", "gateway191", "storage191", "network191"],
    ),
    (
        ("session191 library191 service191 gateway191 storage191 network191", 18),
        ["session191", "library191", "service191", "gateway191", "storage191", "network191"],
    ),
    (
        ("session191 library191 service191 gateway191 storage191 network191", 28),
        ["session191 library191", "service191 gateway191", "storage191 network191"],
    ),
    (
        ("library191 service191 gateway191 storage191 network191 latency191", 6),
        ["library191", "service191", "gateway191", "storage191", "network191", "latency191"],
    ),
    (
        ("library191 service191 gateway191 storage191 network191 latency191", 10),
        ["library191", "service191", "gateway191", "storage191", "network191", "latency191"],
    ),
    (
        ("library191 service191 gateway191 storage191 network191 latency191", 18),
        ["library191", "service191", "gateway191", "storage191", "network191", "latency191"],
    ),
    (
        ("library191 service191 gateway191 storage191 network191 latency191", 28),
        ["library191 service191", "gateway191 storage191", "network191 latency191"],
    ),
    (
        ("service191 gateway191 storage191 network191 latency191 buffer191", 6),
        ["service191", "gateway191", "storage191", "network191", "latency191", "buffer191"],
    ),
    (
        ("service191 gateway191 storage191 network191 latency191 buffer191", 10),
        ["service191", "gateway191", "storage191", "network191", "latency191", "buffer191"],
    ),
    (
        ("service191 gateway191 storage191 network191 latency191 buffer191", 18),
        ["service191", "gateway191", "storage191", "network191", "latency191", "buffer191"],
    ),
    (
        ("service191 gateway191 storage191 network191 latency191 buffer191", 28),
        ["service191 gateway191", "storage191 network191", "latency191 buffer191"],
    ),
    (
        ("gateway191 storage191 network191 latency191 buffer191 queue191", 6),
        ["gateway191", "storage191", "network191", "latency191", "buffer191", "queue191"],
    ),
    (
        ("gateway191 storage191 network191 latency191 buffer191 queue191", 10),
        ["gateway191", "storage191", "network191", "latency191", "buffer191", "queue191"],
    ),
    (
        ("gateway191 storage191 network191 latency191 buffer191 queue191", 18),
        ["gateway191", "storage191", "network191", "latency191", "buffer191 queue191"],
    ),
    (
        ("gateway191 storage191 network191 latency191 buffer191 queue191", 28),
        ["gateway191 storage191", "network191 latency191", "buffer191 queue191"],
    ),
    (
        ("storage191 network191 latency191 buffer191 queue191 worker191", 6),
        ["storage191", "network191", "latency191", "buffer191", "queue191", "worker191"],
    ),
    (
        ("storage191 network191 latency191 buffer191 queue191 worker191", 10),
        ["storage191", "network191", "latency191", "buffer191", "queue191", "worker191"],
    ),
    (
        ("storage191 network191 latency191 buffer191 queue191 worker191", 18),
        ["storage191", "network191", "latency191", "buffer191 queue191", "worker191"],
    ),
    (
        ("storage191 network191 latency191 buffer191 queue191 worker191", 28),
        ["storage191 network191", "latency191 buffer191", "queue191 worker191"],
    ),
    (
        ("network191 latency191 buffer191 queue191 worker191 kernel191", 6),
        ["network191", "latency191", "buffer191", "queue191", "worker191", "kernel191"],
    ),
    (
        ("network191 latency191 buffer191 queue191 worker191 kernel191", 10),
        ["network191", "latency191", "buffer191", "queue191", "worker191", "kernel191"],
    ),
    (
        ("network191 latency191 buffer191 queue191 worker191 kernel191", 18),
        ["network191", "latency191", "buffer191 queue191", "worker191", "kernel191"],
    ),
    (
        ("network191 latency191 buffer191 queue191 worker191 kernel191", 28),
        ["network191 latency191", "buffer191 queue191 worker191", "kernel191"],
    ),
    (
        ("latency191 buffer191 queue191 worker191 kernel191 signal191", 6),
        ["latency191", "buffer191", "queue191", "worker191", "kernel191", "signal191"],
    ),
    (
        ("latency191 buffer191 queue191 worker191 kernel191 signal191", 10),
        ["latency191", "buffer191", "queue191", "worker191", "kernel191", "signal191"],
    ),
    (
        ("latency191 buffer191 queue191 worker191 kernel191 signal191", 18),
        ["latency191", "buffer191 queue191", "worker191", "kernel191", "signal191"],
    ),
    (
        ("latency191 buffer191 queue191 worker191 kernel191 signal191", 28),
        ["latency191 buffer191", "queue191 worker191 kernel191", "signal191"],
    ),
    (
        ("buffer191 queue191 worker191 kernel191 signal191 packet191", 6),
        ["buffer191", "queue191", "worker191", "kernel191", "signal191", "packet191"],
    ),
    (
        ("buffer191 queue191 worker191 kernel191 signal191 packet191", 10),
        ["buffer191", "queue191", "worker191", "kernel191", "signal191", "packet191"],
    ),
    (
        ("buffer191 queue191 worker191 kernel191 signal191 packet191", 18),
        ["buffer191 queue191", "worker191", "kernel191", "signal191", "packet191"],
    ),
    (
        ("buffer191 queue191 worker191 kernel191 signal191 packet191", 28),
        ["buffer191 queue191 worker191", "kernel191 signal191", "packet191"],
    ),
    (
        ("queue191 worker191 kernel191 signal191 packet191 router191", 6),
        ["queue191", "worker191", "kernel191", "signal191", "packet191", "router191"],
    ),
    (
        ("queue191 worker191 kernel191 signal191 packet191 router191", 10),
        ["queue191", "worker191", "kernel191", "signal191", "packet191", "router191"],
    ),
    (
        ("queue191 worker191 kernel191 signal191 packet191 router191", 18),
        ["queue191 worker191", "kernel191", "signal191", "packet191", "router191"],
    ),
    (
        ("queue191 worker191 kernel191 signal191 packet191 router191", 28),
        ["queue191 worker191 kernel191", "signal191 packet191", "router191"],
    ),
    (
        ("worker191 kernel191 signal191 packet191 router191 cluster191", 6),
        ["worker191", "kernel191", "signal191", "packet191", "router191", "cluster191"],
    ),
    (
        ("worker191 kernel191 signal191 packet191 router191 cluster191", 10),
        ["worker191", "kernel191", "signal191", "packet191", "router191", "cluster191"],
    ),
    (
        ("worker191 kernel191 signal191 packet191 router191 cluster191", 18),
        ["worker191", "kernel191", "signal191", "packet191", "router191", "cluster191"],
    ),
    (
        ("worker191 kernel191 signal191 packet191 router191 cluster191", 28),
        ["worker191 kernel191", "signal191 packet191", "router191 cluster191"],
    ),
    (
        ("kernel191 signal191 packet191 router191 cluster191 mirror191", 6),
        ["kernel191", "signal191", "packet191", "router191", "cluster191", "mirror191"],
    ),
    (
        ("kernel191 signal191 packet191 router191 cluster191 mirror191", 10),
        ["kernel191", "signal191", "packet191", "router191", "cluster191", "mirror191"],
    ),
    (
        ("kernel191 signal191 packet191 router191 cluster191 mirror191", 18),
        ["kernel191", "signal191", "packet191", "router191", "cluster191", "mirror191"],
    ),
    (
        ("kernel191 signal191 packet191 router191 cluster191 mirror191", 28),
        ["kernel191 signal191", "packet191 router191", "cluster191 mirror191"],
    ),
    (
        ("signal191 packet191 router191 cluster191 mirror191 filter191", 6),
        ["signal191", "packet191", "router191", "cluster191", "mirror191", "filter191"],
    ),
    (
        ("signal191 packet191 router191 cluster191 mirror191 filter191", 10),
        ["signal191", "packet191", "router191", "cluster191", "mirror191", "filter191"],
    ),
    (
        ("signal191 packet191 router191 cluster191 mirror191 filter191", 18),
        ["signal191", "packet191", "router191", "cluster191", "mirror191", "filter191"],
    ),
    (
        ("signal191 packet191 router191 cluster191 mirror191 filter191", 28),
        ["signal191 packet191", "router191 cluster191", "mirror191 filter191"],
    ),
    (
        ("packet191 router191 cluster191 mirror191 filter191 ranking191", 6),
        ["packet191", "router191", "cluster191", "mirror191", "filter191", "ranking191"],
    ),
    (
        ("packet191 router191 cluster191 mirror191 filter191 ranking191", 10),
        ["packet191", "router191", "cluster191", "mirror191", "filter191", "ranking191"],
    ),
    (
        ("packet191 router191 cluster191 mirror191 filter191 ranking191", 18),
        ["packet191", "router191", "cluster191", "mirror191", "filter191", "ranking191"],
    ),
    (
        ("packet191 router191 cluster191 mirror191 filter191 ranking191", 28),
        ["packet191 router191", "cluster191 mirror191", "filter191 ranking191"],
    ),
    (
        ("router191 cluster191 mirror191 filter191 ranking191 encoding191", 6),
        ["router191", "cluster191", "mirror191", "filter191", "ranking191", "encoding191"],
    ),
    (
        ("router191 cluster191 mirror191 filter191 ranking191 encoding191", 10),
        ["router191", "cluster191", "mirror191", "filter191", "ranking191", "encoding191"],
    ),
    (
        ("router191 cluster191 mirror191 filter191 ranking191 encoding191", 18),
        ["router191", "cluster191", "mirror191", "filter191", "ranking191", "encoding191"],
    ),
    (
        ("router191 cluster191 mirror191 filter191 ranking191 encoding191", 28),
        ["router191 cluster191", "mirror191 filter191", "ranking191 encoding191"],
    ),
    (
        ("cluster191 mirror191 filter191 ranking191 encoding191 mapping191", 6),
        ["cluster191", "mirror191", "filter191", "ranking191", "encoding191", "mapping191"],
    ),
    (
        ("cluster191 mirror191 filter191 ranking191 encoding191 mapping191", 10),
        ["cluster191", "mirror191", "filter191", "ranking191", "encoding191", "mapping191"],
    ),
    (
        ("cluster191 mirror191 filter191 ranking191 encoding191 mapping191", 18),
        ["cluster191", "mirror191", "filter191", "ranking191", "encoding191", "mapping191"],
    ),
    (
        ("cluster191 mirror191 filter191 ranking191 encoding191 mapping191", 28),
        ["cluster191 mirror191", "filter191 ranking191", "encoding191 mapping191"],
    ),
    (
        ("mirror191 filter191 ranking191 encoding191 mapping191 record191", 6),
        ["mirror191", "filter191", "ranking191", "encoding191", "mapping191", "record191"],
    ),
    (
        ("mirror191 filter191 ranking191 encoding191 mapping191 record191", 10),
        ["mirror191", "filter191", "ranking191", "encoding191", "mapping191", "record191"],
    ),
    (
        ("mirror191 filter191 ranking191 encoding191 mapping191 record191", 18),
        ["mirror191", "filter191", "ranking191", "encoding191", "mapping191", "record191"],
    ),
    (
        ("mirror191 filter191 ranking191 encoding191 mapping191 record191", 28),
        ["mirror191 filter191", "ranking191 encoding191", "mapping191 record191"],
    ),
    (
        ("filter191 ranking191 encoding191 mapping191 record191 candle191", 6),
        ["filter191", "ranking191", "encoding191", "mapping191", "record191", "candle191"],
    ),
    (
        ("filter191 ranking191 encoding191 mapping191 record191 candle191", 10),
        ["filter191", "ranking191", "encoding191", "mapping191", "record191", "candle191"],
    ),
    (
        ("filter191 ranking191 encoding191 mapping191 record191 candle191", 18),
        ["filter191", "ranking191", "encoding191", "mapping191", "record191", "candle191"],
    ),
    (
        ("filter191 ranking191 encoding191 mapping191 record191 candle191", 28),
        ["filter191 ranking191", "encoding191 mapping191", "record191 candle191"],
    ),
    (
        ("ranking191 encoding191 mapping191 record191 candle191 thread191", 6),
        ["ranking191", "encoding191", "mapping191", "record191", "candle191", "thread191"],
    ),
    (
        ("ranking191 encoding191 mapping191 record191 candle191 thread191", 10),
        ["ranking191", "encoding191", "mapping191", "record191", "candle191", "thread191"],
    ),
    (
        ("ranking191 encoding191 mapping191 record191 candle191 thread191", 18),
        ["ranking191", "encoding191", "mapping191", "record191", "candle191", "thread191"],
    ),
    (
        ("ranking191 encoding191 mapping191 record191 candle191 thread191", 28),
        ["ranking191 encoding191", "mapping191 record191", "candle191 thread191"],
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
