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
        ("round 48: the quick brown fox jumps over the lazy dog", 4),
        ["round", "48:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 48: the quick brown fox jumps over the lazy dog", 8),
        ["round", "48: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 48: the quick brown fox jumps over the lazy dog", 12),
        ["round 48:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 48: the quick brown fox jumps over the lazy dog", 16),
        ["round 48: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 48: the quick brown fox jumps over the lazy dog", 24),
        ["round 48: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 48: the quick brown fox jumps over the lazy dog", 32),
        ["round 48: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 48: agentuniverse is a framework for multi agents", 4),
        ["round", "48:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 48: agentuniverse is a framework for multi agents", 8),
        ["round", "48:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 48: agentuniverse is a framework for multi agents", 12),
        ["round 48:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 48: agentuniverse is a framework for multi agents", 16),
        ["round 48:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 48: agentuniverse is a framework for multi agents", 24),
        ["round 48: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 48: agentuniverse is a framework for multi agents", 32),
        ["round 48: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 48: knowledge stored as vectors enables retrieval", 4),
        ["round", "48:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 48: knowledge stored as vectors enables retrieval", 8),
        ["round", "48:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 48: knowledge stored as vectors enables retrieval", 12),
        ["round 48:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 48: knowledge stored as vectors enables retrieval", 16),
        ["round 48:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 48: knowledge stored as vectors enables retrieval", 24),
        ["round 48: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 48: knowledge stored as vectors enables retrieval", 32),
        ["round 48: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 48: the processor reads the record then stops", 4),
        ["round", "48:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 48: the processor reads the record then stops", 8),
        ["round", "48: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 48: the processor reads the record then stops", 12),
        ["round 48:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 48: the processor reads the record then stops", 16),
        ["round 48: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 48: the processor reads the record then stops", 24),
        ["round 48: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 48: the processor reads the record then stops", 32),
        ["round 48: the processor reads", "the record then stops"],
    ),
    (
        ("round 48: a worker pulls the next task from the queue", 4),
        ["round", "48:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 48: a worker pulls the next task from the queue", 8),
        ["round", "48: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 48: a worker pulls the next task from the queue", 12),
        ["round 48: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 48: a worker pulls the next task from the queue", 16),
        ["round 48: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 48: a worker pulls the next task from the queue", 24),
        ["round 48: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 48: a worker pulls the next task from the queue", 32),
        ["round 48: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 48: signals travel through the network layer", 4),
        ["round", "48:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 48: signals travel through the network layer", 8),
        ["round", "48:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 48: signals travel through the network layer", 12),
        ["round 48:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 48: signals travel through the network layer", 16),
        ["round 48:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 48: signals travel through the network layer", 24),
        ["round 48: signals travel", "through the network", "layer"],
    ),
    (
        ("round 48: signals travel through the network layer", 32),
        ["round 48: signals travel through", "the network layer"],
    ),
    (
        ("round 48: the gateway routes each request by policy", 4),
        ["round", "48:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 48: the gateway routes each request by policy", 8),
        ["round", "48: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 48: the gateway routes each request by policy", 12),
        ["round 48:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 48: the gateway routes each request by policy", 16),
        ["round 48: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 48: the gateway routes each request by policy", 24),
        ["round 48: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 48: the gateway routes each request by policy", 32),
        ["round 48: the gateway routes", "each request by policy"],
    ),
    (
        ("round 48: memory grows until the buffer is full", 4),
        ["round", "48:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 48: memory grows until the buffer is full", 8),
        ["round", "48:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 48: memory grows until the buffer is full", 12),
        ["round 48:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 48: memory grows until the buffer is full", 16),
        ["round 48: memory", "grows until the", "buffer is full"],
    ),
    (("round 48: memory grows until the buffer is full", 24), ["round 48: memory grows", "until the buffer is full"]),
    (("round 48: memory grows until the buffer is full", 32), ["round 48: memory grows until the", "buffer is full"]),
    (
        ("round 48: the cluster mirrors every packet twice", 4),
        ["round", "48:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 48: the cluster mirrors every packet twice", 8),
        ["round", "48: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 48: the cluster mirrors every packet twice", 12),
        ["round 48:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 48: the cluster mirrors every packet twice", 16),
        ["round 48: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 48: the cluster mirrors every packet twice", 24),
        ["round 48: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 48: the cluster mirrors every packet twice", 32), ["round 48: the cluster mirrors", "every packet twice"]),
    (
        ("round 48: ranking uses tokens learned from the corpus", 4),
        ["round", "48:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 48: ranking uses tokens learned from the corpus", 8),
        ["round", "48:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 48: ranking uses tokens learned from the corpus", 12),
        ["round 48:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 48: ranking uses tokens learned from the corpus", 16),
        ["round 48:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 48: ranking uses tokens learned from the corpus", 24),
        ["round 48: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 48: ranking uses tokens learned from the corpus", 32),
        ["round 48: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 48: a long session ends when the candle dies", 4),
        ["round", "48:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 48: a long session ends when the candle dies", 8),
        ["round", "48: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 48: a long session ends when the candle dies", 12),
        ["round 48: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 48: a long session ends when the candle dies", 16),
        ["round 48: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 48: a long session ends when the candle dies", 24),
        ["round 48: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 48: a long session ends when the candle dies", 32),
        ["round 48: a long session ends", "when the candle dies"],
    ),
    (
        ("round 48: encode the prompt then map the result", 4),
        ["round", "48:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 48: encode the prompt then map the result", 8),
        ["round", "48:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 48: encode the prompt then map the result", 12),
        ["round 48:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 48: encode the prompt then map the result", 16),
        ["round 48: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 48: encode the prompt then map the result", 24),
        ["round 48: encode the", "prompt then map the", "result"],
    ),
    (("round 48: encode the prompt then map the result", 32), ["round 48: encode the prompt then", "map the result"]),
    (
        ("round 48: the kernel wakes the worker at dawn", 4),
        ["round", "48:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 48: the kernel wakes the worker at dawn", 8),
        ["round", "48: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 48: the kernel wakes the worker at dawn", 12),
        ["round 48:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 48: the kernel wakes the worker at dawn", 16), ["round 48: the", "kernel wakes the", "worker at dawn"]),
    (("round 48: the kernel wakes the worker at dawn", 24), ["round 48: the kernel", "wakes the worker at dawn"]),
    (("round 48: the kernel wakes the worker at dawn", 32), ["round 48: the kernel wakes the", "worker at dawn"]),
    (
        ("round 48: service latency drops after the patch", 4),
        ["round", "48:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 48: service latency drops after the patch", 8),
        ["round", "48:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 48: service latency drops after the patch", 12),
        ["round 48:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 48: service latency drops after the patch", 16),
        ["round 48:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 48: service latency drops after the patch", 24),
        ["round 48: service", "latency drops after the", "patch"],
    ),
    (("round 48: service latency drops after the patch", 32), ["round 48: service latency drops", "after the patch"]),
    (
        ("round 48: the library caches every vector it sees", 4),
        ["round", "48:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 48: the library caches every vector it sees", 8),
        ["round", "48: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 48: the library caches every vector it sees", 12),
        ["round 48:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 48: the library caches every vector it sees", 16),
        ["round 48: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 48: the library caches every vector it sees", 24),
        ["round 48: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 48: the library caches every vector it sees", 32),
        ["round 48: the library caches", "every vector it sees"],
    ),
    (
        ("round 48: agents argue then the debate resolves", 4),
        ["round", "48:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 48: agents argue then the debate resolves", 8),
        ["round", "48:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 48: agents argue then the debate resolves", 12),
        ["round 48:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 48: agents argue then the debate resolves", 16),
        ["round 48: agents", "argue then the", "debate resolves"],
    ),
    (("round 48: agents argue then the debate resolves", 24), ["round 48: agents argue", "then the debate resolves"]),
    (("round 48: agents argue then the debate resolves", 32), ["round 48: agents argue then the", "debate resolves"]),
    (
        ("round 48: the filter keeps only strong matches", 4),
        ["round", "48:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 48: the filter keeps only strong matches", 8),
        ["round", "48: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 48: the filter keeps only strong matches", 12),
        ["round 48:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 48: the filter keeps only strong matches", 16),
        ["round 48: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 48: the filter keeps only strong matches", 24), ["round 48: the filter", "keeps only strong", "matches"]),
    (("round 48: the filter keeps only strong matches", 32), ["round 48: the filter keeps only", "strong matches"]),
    (
        ("round 48: the model answers with a short reply", 4),
        ["round", "48:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 48: the model answers with a short reply", 8),
        ["round", "48: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 48: the model answers with a short reply", 12),
        ["round 48:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 48: the model answers with a short reply", 16),
        ["round 48: the", "model answers", "with a short", "reply"],
    ),
    (("round 48: the model answers with a short reply", 24), ["round 48: the model", "answers with a short", "reply"]),
    (("round 48: the model answers with a short reply", 32), ["round 48: the model answers with", "a short reply"]),
    (
        ("round 48: the recorder stores the reasoning trace", 4),
        ["round", "48:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 48: the recorder stores the reasoning trace", 8),
        ["round", "48: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 48: the recorder stores the reasoning trace", 12),
        ["round 48:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 48: the recorder stores the reasoning trace", 16),
        ["round 48: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 48: the recorder stores the reasoning trace", 24),
        ["round 48: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 48: the recorder stores the reasoning trace", 32),
        ["round 48: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 48: the angel watches the processor run", 4),
        ["round", "48:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 48: the angel watches the processor run", 8),
        ["round", "48: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 48: the angel watches the processor run", 12),
        ["round 48:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 48: the angel watches the processor run", 16), ["round 48: the", "angel watches", "the processor", "run"]),
    (("round 48: the angel watches the processor run", 24), ["round 48: the angel", "watches the processor", "run"]),
    (("round 48: the angel watches the processor run", 32), ["round 48: the angel watches the", "processor run"]),
    (
        ("round 48: angle of the vector decides the match", 4),
        ["round", "48:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 48: angle of the vector decides the match", 8),
        ["round", "48:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 48: angle of the vector decides the match", 12),
        ["round 48:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 48: angle of the vector decides the match", 16),
        ["round 48: angle", "of the vector", "decides the", "match"],
    ),
    (("round 48: angle of the vector decides the match", 24), ["round 48: angle of the", "vector decides the match"]),
    (("round 48: angle of the vector decides the match", 32), ["round 48: angle of the vector", "decides the match"]),
    (
        ("round 48: the candle burns twice as long at night", 4),
        ["round", "48:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 48: the candle burns twice as long at night", 8),
        ["round", "48: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 48: the candle burns twice as long at night", 12),
        ["round 48:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 48: the candle burns twice as long at night", 16),
        ["round 48: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 48: the candle burns twice as long at night", 24),
        ["round 48: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 48: the candle burns twice as long at night", 32),
        ["round 48: the candle burns twice", "as long at night"],
    ),
    (
        ("round 48: a mirror of the universe in one line", 4),
        ["round", "48:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 48: a mirror of the universe in one line", 8),
        ["round", "48: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 48: a mirror of the universe in one line", 12),
        ["round 48: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 48: a mirror of the universe in one line", 16),
        ["round 48: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 48: a mirror of the universe in one line", 24), ["round 48: a mirror of", "the universe in one line"]),
    (("round 48: a mirror of the universe in one line", 32), ["round 48: a mirror of the", "universe in one line"]),
    (
        ("round 48: the queue drains before the storm", 4),
        ["round", "48:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 48: the queue drains before the storm", 8),
        ["round", "48: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 48: the queue drains before the storm", 12), ["round 48:", "the queue", "drains", "before the", "storm"]),
    (("round 48: the queue drains before the storm", 16), ["round 48: the", "queue drains", "before the storm"]),
    (("round 48: the queue drains before the storm", 24), ["round 48: the queue", "drains before the storm"]),
    (("round 48: the queue drains before the storm", 32), ["round 48: the queue drains", "before the storm"]),
    (
        ("kitten48 sitting48 agent48 angle48 universe48 memory48", 6),
        ["kitten48", "sitting48", "agent48", "angle48", "universe48", "memory48"],
    ),
    (
        ("kitten48 sitting48 agent48 angle48 universe48 memory48", 10),
        ["kitten48", "sitting48", "agent48", "angle48", "universe48", "memory48"],
    ),
    (
        ("kitten48 sitting48 agent48 angle48 universe48 memory48", 18),
        ["kitten48 sitting48", "agent48 angle48", "universe48", "memory48"],
    ),
    (
        ("kitten48 sitting48 agent48 angle48 universe48 memory48", 28),
        ["kitten48 sitting48 agent48", "angle48 universe48 memory48"],
    ),
    (
        ("sitting48 agent48 angle48 universe48 memory48 stream48", 6),
        ["sitting48", "agent48", "angle48", "universe48", "memory48", "stream48"],
    ),
    (
        ("sitting48 agent48 angle48 universe48 memory48 stream48", 10),
        ["sitting48", "agent48", "angle48", "universe48", "memory48", "stream48"],
    ),
    (
        ("sitting48 agent48 angle48 universe48 memory48 stream48", 18),
        ["sitting48 agent48", "angle48 universe48", "memory48 stream48"],
    ),
    (
        ("sitting48 agent48 angle48 universe48 memory48 stream48", 28),
        ["sitting48 agent48 angle48", "universe48 memory48 stream48"],
    ),
    (
        ("agent48 angle48 universe48 memory48 stream48 context48", 6),
        ["agent48", "angle48", "universe48", "memory48", "stream48", "context48"],
    ),
    (
        ("agent48 angle48 universe48 memory48 stream48 context48", 10),
        ["agent48", "angle48", "universe48", "memory48", "stream48", "context48"],
    ),
    (
        ("agent48 angle48 universe48 memory48 stream48 context48", 18),
        ["agent48 angle48", "universe48", "memory48 stream48", "context48"],
    ),
    (
        ("agent48 angle48 universe48 memory48 stream48 context48", 28),
        ["agent48 angle48 universe48", "memory48 stream48 context48"],
    ),
    (
        ("angle48 universe48 memory48 stream48 context48 knowledge48", 6),
        ["angle48", "universe48", "memory48", "stream48", "context48", "knowledge48"],
    ),
    (
        ("angle48 universe48 memory48 stream48 context48 knowledge48", 10),
        ["angle48", "universe48", "memory48", "stream48", "context48", "knowledge48"],
    ),
    (
        ("angle48 universe48 memory48 stream48 context48 knowledge48", 18),
        ["angle48 universe48", "memory48 stream48", "context48", "knowledge48"],
    ),
    (
        ("angle48 universe48 memory48 stream48 context48 knowledge48", 28),
        ["angle48 universe48 memory48", "stream48 context48", "knowledge48"],
    ),
    (
        ("universe48 memory48 stream48 context48 knowledge48 vector48", 6),
        ["universe48", "memory48", "stream48", "context48", "knowledge48", "vector48"],
    ),
    (
        ("universe48 memory48 stream48 context48 knowledge48 vector48", 10),
        ["universe48", "memory48", "stream48", "context48", "knowledge48", "vector48"],
    ),
    (
        ("universe48 memory48 stream48 context48 knowledge48 vector48", 18),
        ["universe48", "memory48 stream48", "context48", "knowledge48", "vector48"],
    ),
    (
        ("universe48 memory48 stream48 context48 knowledge48 vector48", 28),
        ["universe48 memory48 stream48", "context48 knowledge48", "vector48"],
    ),
    (
        ("memory48 stream48 context48 knowledge48 vector48 processor48", 6),
        ["memory48", "stream48", "context48", "knowledge48", "vector48", "processor48"],
    ),
    (
        ("memory48 stream48 context48 knowledge48 vector48 processor48", 10),
        ["memory48", "stream48", "context48", "knowledge48", "vector48", "processor48"],
    ),
    (
        ("memory48 stream48 context48 knowledge48 vector48 processor48", 18),
        ["memory48 stream48", "context48", "knowledge48", "vector48", "processor48"],
    ),
    (
        ("memory48 stream48 context48 knowledge48 vector48 processor48", 28),
        ["memory48 stream48 context48", "knowledge48 vector48", "processor48"],
    ),
    (
        ("stream48 context48 knowledge48 vector48 processor48 reasoning48", 6),
        ["stream48", "context48", "knowledge48", "vector48", "processor48", "reasoning48"],
    ),
    (
        ("stream48 context48 knowledge48 vector48 processor48 reasoning48", 10),
        ["stream48", "context48", "knowledge48", "vector48", "processor48", "reasoning48"],
    ),
    (
        ("stream48 context48 knowledge48 vector48 processor48 reasoning48", 18),
        ["stream48 context48", "knowledge48", "vector48", "processor48", "reasoning48"],
    ),
    (
        ("stream48 context48 knowledge48 vector48 processor48 reasoning48", 28),
        ["stream48 context48", "knowledge48 vector48", "processor48 reasoning48"],
    ),
    (
        ("context48 knowledge48 vector48 processor48 reasoning48 machine48", 6),
        ["context48", "knowledge48", "vector48", "processor48", "reasoning48", "machine48"],
    ),
    (
        ("context48 knowledge48 vector48 processor48 reasoning48 machine48", 10),
        ["context48", "knowledge48", "vector48", "processor48", "reasoning48", "machine48"],
    ),
    (
        ("context48 knowledge48 vector48 processor48 reasoning48 machine48", 18),
        ["context48", "knowledge48", "vector48", "processor48", "reasoning48", "machine48"],
    ),
    (
        ("context48 knowledge48 vector48 processor48 reasoning48 machine48", 28),
        ["context48 knowledge48", "vector48 processor48", "reasoning48 machine48"],
    ),
    (
        ("knowledge48 vector48 processor48 reasoning48 machine48 learning48", 6),
        ["knowledge48", "vector48", "processor48", "reasoning48", "machine48", "learning48"],
    ),
    (
        ("knowledge48 vector48 processor48 reasoning48 machine48 learning48", 10),
        ["knowledge48", "vector48", "processor48", "reasoning48", "machine48", "learning48"],
    ),
    (
        ("knowledge48 vector48 processor48 reasoning48 machine48 learning48", 18),
        ["knowledge48", "vector48", "processor48", "reasoning48", "machine48", "learning48"],
    ),
    (
        ("knowledge48 vector48 processor48 reasoning48 machine48 learning48", 28),
        ["knowledge48 vector48", "processor48 reasoning48", "machine48 learning48"],
    ),
    (
        ("vector48 processor48 reasoning48 machine48 learning48 model48", 6),
        ["vector48", "processor48", "reasoning48", "machine48", "learning48", "model48"],
    ),
    (
        ("vector48 processor48 reasoning48 machine48 learning48 model48", 10),
        ["vector48", "processor48", "reasoning48", "machine48", "learning48", "model48"],
    ),
    (
        ("vector48 processor48 reasoning48 machine48 learning48 model48", 18),
        ["vector48", "processor48", "reasoning48", "machine48", "learning48 model48"],
    ),
    (
        ("vector48 processor48 reasoning48 machine48 learning48 model48", 28),
        ["vector48 processor48", "reasoning48 machine48", "learning48 model48"],
    ),
    (
        ("processor48 reasoning48 machine48 learning48 model48 token48", 6),
        ["processor48", "reasoning48", "machine48", "learning48", "model48", "token48"],
    ),
    (
        ("processor48 reasoning48 machine48 learning48 model48 token48", 10),
        ["processor48", "reasoning48", "machine48", "learning48", "model48", "token48"],
    ),
    (
        ("processor48 reasoning48 machine48 learning48 model48 token48", 18),
        ["processor48", "reasoning48", "machine48", "learning48 model48", "token48"],
    ),
    (
        ("processor48 reasoning48 machine48 learning48 model48 token48", 28),
        ["processor48 reasoning48", "machine48 learning48 model48", "token48"],
    ),
    (
        ("reasoning48 machine48 learning48 model48 token48 prompt48", 6),
        ["reasoning48", "machine48", "learning48", "model48", "token48", "prompt48"],
    ),
    (
        ("reasoning48 machine48 learning48 model48 token48 prompt48", 10),
        ["reasoning48", "machine48", "learning48", "model48", "token48", "prompt48"],
    ),
    (
        ("reasoning48 machine48 learning48 model48 token48 prompt48", 18),
        ["reasoning48", "machine48", "learning48 model48", "token48 prompt48"],
    ),
    (
        ("reasoning48 machine48 learning48 model48 token48 prompt48", 28),
        ["reasoning48 machine48", "learning48 model48 token48", "prompt48"],
    ),
    (
        ("machine48 learning48 model48 token48 prompt48 session48", 6),
        ["machine48", "learning48", "model48", "token48", "prompt48", "session48"],
    ),
    (
        ("machine48 learning48 model48 token48 prompt48 session48", 10),
        ["machine48", "learning48", "model48", "token48", "prompt48", "session48"],
    ),
    (
        ("machine48 learning48 model48 token48 prompt48 session48", 18),
        ["machine48", "learning48 model48", "token48 prompt48", "session48"],
    ),
    (
        ("machine48 learning48 model48 token48 prompt48 session48", 28),
        ["machine48 learning48 model48", "token48 prompt48 session48"],
    ),
    (
        ("learning48 model48 token48 prompt48 session48 library48", 6),
        ["learning48", "model48", "token48", "prompt48", "session48", "library48"],
    ),
    (
        ("learning48 model48 token48 prompt48 session48 library48", 10),
        ["learning48", "model48", "token48", "prompt48", "session48", "library48"],
    ),
    (
        ("learning48 model48 token48 prompt48 session48 library48", 18),
        ["learning48 model48", "token48 prompt48", "session48", "library48"],
    ),
    (
        ("learning48 model48 token48 prompt48 session48 library48", 28),
        ["learning48 model48 token48", "prompt48 session48 library48"],
    ),
    (
        ("model48 token48 prompt48 session48 library48 service48", 6),
        ["model48", "token48", "prompt48", "session48", "library48", "service48"],
    ),
    (
        ("model48 token48 prompt48 session48 library48 service48", 10),
        ["model48", "token48", "prompt48", "session48", "library48", "service48"],
    ),
    (
        ("model48 token48 prompt48 session48 library48 service48", 18),
        ["model48 token48", "prompt48 session48", "library48", "service48"],
    ),
    (
        ("model48 token48 prompt48 session48 library48 service48", 28),
        ["model48 token48 prompt48", "session48 library48", "service48"],
    ),
    (
        ("token48 prompt48 session48 library48 service48 gateway48", 6),
        ["token48", "prompt48", "session48", "library48", "service48", "gateway48"],
    ),
    (
        ("token48 prompt48 session48 library48 service48 gateway48", 10),
        ["token48", "prompt48", "session48", "library48", "service48", "gateway48"],
    ),
    (
        ("token48 prompt48 session48 library48 service48 gateway48", 18),
        ["token48 prompt48", "session48", "library48", "service48", "gateway48"],
    ),
    (
        ("token48 prompt48 session48 library48 service48 gateway48", 28),
        ["token48 prompt48 session48", "library48 service48", "gateway48"],
    ),
    (
        ("prompt48 session48 library48 service48 gateway48 storage48", 6),
        ["prompt48", "session48", "library48", "service48", "gateway48", "storage48"],
    ),
    (
        ("prompt48 session48 library48 service48 gateway48 storage48", 10),
        ["prompt48", "session48", "library48", "service48", "gateway48", "storage48"],
    ),
    (
        ("prompt48 session48 library48 service48 gateway48 storage48", 18),
        ["prompt48 session48", "library48", "service48", "gateway48", "storage48"],
    ),
    (
        ("prompt48 session48 library48 service48 gateway48 storage48", 28),
        ["prompt48 session48 library48", "service48 gateway48", "storage48"],
    ),
    (
        ("session48 library48 service48 gateway48 storage48 network48", 6),
        ["session48", "library48", "service48", "gateway48", "storage48", "network48"],
    ),
    (
        ("session48 library48 service48 gateway48 storage48 network48", 10),
        ["session48", "library48", "service48", "gateway48", "storage48", "network48"],
    ),
    (
        ("session48 library48 service48 gateway48 storage48 network48", 18),
        ["session48", "library48", "service48", "gateway48", "storage48", "network48"],
    ),
    (
        ("session48 library48 service48 gateway48 storage48 network48", 28),
        ["session48 library48", "service48 gateway48", "storage48 network48"],
    ),
    (
        ("library48 service48 gateway48 storage48 network48 latency48", 6),
        ["library48", "service48", "gateway48", "storage48", "network48", "latency48"],
    ),
    (
        ("library48 service48 gateway48 storage48 network48 latency48", 10),
        ["library48", "service48", "gateway48", "storage48", "network48", "latency48"],
    ),
    (
        ("library48 service48 gateway48 storage48 network48 latency48", 18),
        ["library48", "service48", "gateway48", "storage48", "network48", "latency48"],
    ),
    (
        ("library48 service48 gateway48 storage48 network48 latency48", 28),
        ["library48 service48", "gateway48 storage48", "network48 latency48"],
    ),
    (
        ("service48 gateway48 storage48 network48 latency48 buffer48", 6),
        ["service48", "gateway48", "storage48", "network48", "latency48", "buffer48"],
    ),
    (
        ("service48 gateway48 storage48 network48 latency48 buffer48", 10),
        ["service48", "gateway48", "storage48", "network48", "latency48", "buffer48"],
    ),
    (
        ("service48 gateway48 storage48 network48 latency48 buffer48", 18),
        ["service48", "gateway48", "storage48", "network48", "latency48 buffer48"],
    ),
    (
        ("service48 gateway48 storage48 network48 latency48 buffer48", 28),
        ["service48 gateway48", "storage48 network48", "latency48 buffer48"],
    ),
    (
        ("gateway48 storage48 network48 latency48 buffer48 queue48", 6),
        ["gateway48", "storage48", "network48", "latency48", "buffer48", "queue48"],
    ),
    (
        ("gateway48 storage48 network48 latency48 buffer48 queue48", 10),
        ["gateway48", "storage48", "network48", "latency48", "buffer48", "queue48"],
    ),
    (
        ("gateway48 storage48 network48 latency48 buffer48 queue48", 18),
        ["gateway48", "storage48", "network48", "latency48 buffer48", "queue48"],
    ),
    (
        ("gateway48 storage48 network48 latency48 buffer48 queue48", 28),
        ["gateway48 storage48", "network48 latency48 buffer48", "queue48"],
    ),
    (
        ("storage48 network48 latency48 buffer48 queue48 worker48", 6),
        ["storage48", "network48", "latency48", "buffer48", "queue48", "worker48"],
    ),
    (
        ("storage48 network48 latency48 buffer48 queue48 worker48", 10),
        ["storage48", "network48", "latency48", "buffer48", "queue48", "worker48"],
    ),
    (
        ("storage48 network48 latency48 buffer48 queue48 worker48", 18),
        ["storage48", "network48", "latency48 buffer48", "queue48 worker48"],
    ),
    (
        ("storage48 network48 latency48 buffer48 queue48 worker48", 28),
        ["storage48 network48", "latency48 buffer48 queue48", "worker48"],
    ),
    (
        ("network48 latency48 buffer48 queue48 worker48 kernel48", 6),
        ["network48", "latency48", "buffer48", "queue48", "worker48", "kernel48"],
    ),
    (
        ("network48 latency48 buffer48 queue48 worker48 kernel48", 10),
        ["network48", "latency48", "buffer48", "queue48", "worker48", "kernel48"],
    ),
    (
        ("network48 latency48 buffer48 queue48 worker48 kernel48", 18),
        ["network48", "latency48 buffer48", "queue48 worker48", "kernel48"],
    ),
    (
        ("network48 latency48 buffer48 queue48 worker48 kernel48", 28),
        ["network48 latency48 buffer48", "queue48 worker48 kernel48"],
    ),
    (
        ("latency48 buffer48 queue48 worker48 kernel48 signal48", 6),
        ["latency48", "buffer48", "queue48", "worker48", "kernel48", "signal48"],
    ),
    (
        ("latency48 buffer48 queue48 worker48 kernel48 signal48", 10),
        ["latency48", "buffer48", "queue48", "worker48", "kernel48", "signal48"],
    ),
    (
        ("latency48 buffer48 queue48 worker48 kernel48 signal48", 18),
        ["latency48 buffer48", "queue48 worker48", "kernel48 signal48"],
    ),
    (
        ("latency48 buffer48 queue48 worker48 kernel48 signal48", 28),
        ["latency48 buffer48 queue48", "worker48 kernel48 signal48"],
    ),
    (
        ("buffer48 queue48 worker48 kernel48 signal48 packet48", 6),
        ["buffer48", "queue48", "worker48", "kernel48", "signal48", "packet48"],
    ),
    (
        ("buffer48 queue48 worker48 kernel48 signal48 packet48", 10),
        ["buffer48", "queue48", "worker48", "kernel48", "signal48", "packet48"],
    ),
    (
        ("buffer48 queue48 worker48 kernel48 signal48 packet48", 18),
        ["buffer48 queue48", "worker48 kernel48", "signal48 packet48"],
    ),
    (
        ("buffer48 queue48 worker48 kernel48 signal48 packet48", 28),
        ["buffer48 queue48 worker48", "kernel48 signal48 packet48"],
    ),
    (
        ("queue48 worker48 kernel48 signal48 packet48 router48", 6),
        ["queue48", "worker48", "kernel48", "signal48", "packet48", "router48"],
    ),
    (
        ("queue48 worker48 kernel48 signal48 packet48 router48", 10),
        ["queue48", "worker48", "kernel48", "signal48", "packet48", "router48"],
    ),
    (
        ("queue48 worker48 kernel48 signal48 packet48 router48", 18),
        ["queue48 worker48", "kernel48 signal48", "packet48 router48"],
    ),
    (
        ("queue48 worker48 kernel48 signal48 packet48 router48", 28),
        ["queue48 worker48 kernel48", "signal48 packet48 router48"],
    ),
    (
        ("worker48 kernel48 signal48 packet48 router48 cluster48", 6),
        ["worker48", "kernel48", "signal48", "packet48", "router48", "cluster48"],
    ),
    (
        ("worker48 kernel48 signal48 packet48 router48 cluster48", 10),
        ["worker48", "kernel48", "signal48", "packet48", "router48", "cluster48"],
    ),
    (
        ("worker48 kernel48 signal48 packet48 router48 cluster48", 18),
        ["worker48 kernel48", "signal48 packet48", "router48 cluster48"],
    ),
    (
        ("worker48 kernel48 signal48 packet48 router48 cluster48", 28),
        ["worker48 kernel48 signal48", "packet48 router48 cluster48"],
    ),
    (
        ("kernel48 signal48 packet48 router48 cluster48 mirror48", 6),
        ["kernel48", "signal48", "packet48", "router48", "cluster48", "mirror48"],
    ),
    (
        ("kernel48 signal48 packet48 router48 cluster48 mirror48", 10),
        ["kernel48", "signal48", "packet48", "router48", "cluster48", "mirror48"],
    ),
    (
        ("kernel48 signal48 packet48 router48 cluster48 mirror48", 18),
        ["kernel48 signal48", "packet48 router48", "cluster48 mirror48"],
    ),
    (
        ("kernel48 signal48 packet48 router48 cluster48 mirror48", 28),
        ["kernel48 signal48 packet48", "router48 cluster48 mirror48"],
    ),
    (
        ("signal48 packet48 router48 cluster48 mirror48 filter48", 6),
        ["signal48", "packet48", "router48", "cluster48", "mirror48", "filter48"],
    ),
    (
        ("signal48 packet48 router48 cluster48 mirror48 filter48", 10),
        ["signal48", "packet48", "router48", "cluster48", "mirror48", "filter48"],
    ),
    (
        ("signal48 packet48 router48 cluster48 mirror48 filter48", 18),
        ["signal48 packet48", "router48 cluster48", "mirror48 filter48"],
    ),
    (
        ("signal48 packet48 router48 cluster48 mirror48 filter48", 28),
        ["signal48 packet48 router48", "cluster48 mirror48 filter48"],
    ),
    (
        ("packet48 router48 cluster48 mirror48 filter48 ranking48", 6),
        ["packet48", "router48", "cluster48", "mirror48", "filter48", "ranking48"],
    ),
    (
        ("packet48 router48 cluster48 mirror48 filter48 ranking48", 10),
        ["packet48", "router48", "cluster48", "mirror48", "filter48", "ranking48"],
    ),
    (
        ("packet48 router48 cluster48 mirror48 filter48 ranking48", 18),
        ["packet48 router48", "cluster48 mirror48", "filter48 ranking48"],
    ),
    (
        ("packet48 router48 cluster48 mirror48 filter48 ranking48", 28),
        ["packet48 router48 cluster48", "mirror48 filter48 ranking48"],
    ),
    (
        ("router48 cluster48 mirror48 filter48 ranking48 encoding48", 6),
        ["router48", "cluster48", "mirror48", "filter48", "ranking48", "encoding48"],
    ),
    (
        ("router48 cluster48 mirror48 filter48 ranking48 encoding48", 10),
        ["router48", "cluster48", "mirror48", "filter48", "ranking48", "encoding48"],
    ),
    (
        ("router48 cluster48 mirror48 filter48 ranking48 encoding48", 18),
        ["router48 cluster48", "mirror48 filter48", "ranking48", "encoding48"],
    ),
    (
        ("router48 cluster48 mirror48 filter48 ranking48 encoding48", 28),
        ["router48 cluster48 mirror48", "filter48 ranking48", "encoding48"],
    ),
    (
        ("cluster48 mirror48 filter48 ranking48 encoding48 mapping48", 6),
        ["cluster48", "mirror48", "filter48", "ranking48", "encoding48", "mapping48"],
    ),
    (
        ("cluster48 mirror48 filter48 ranking48 encoding48 mapping48", 10),
        ["cluster48", "mirror48", "filter48", "ranking48", "encoding48", "mapping48"],
    ),
    (
        ("cluster48 mirror48 filter48 ranking48 encoding48 mapping48", 18),
        ["cluster48 mirror48", "filter48 ranking48", "encoding48", "mapping48"],
    ),
    (
        ("cluster48 mirror48 filter48 ranking48 encoding48 mapping48", 28),
        ["cluster48 mirror48 filter48", "ranking48 encoding48", "mapping48"],
    ),
    (
        ("mirror48 filter48 ranking48 encoding48 mapping48 record48", 6),
        ["mirror48", "filter48", "ranking48", "encoding48", "mapping48", "record48"],
    ),
    (
        ("mirror48 filter48 ranking48 encoding48 mapping48 record48", 10),
        ["mirror48", "filter48", "ranking48", "encoding48", "mapping48", "record48"],
    ),
    (
        ("mirror48 filter48 ranking48 encoding48 mapping48 record48", 18),
        ["mirror48 filter48", "ranking48", "encoding48", "mapping48 record48"],
    ),
    (
        ("mirror48 filter48 ranking48 encoding48 mapping48 record48", 28),
        ["mirror48 filter48 ranking48", "encoding48 mapping48", "record48"],
    ),
    (
        ("filter48 ranking48 encoding48 mapping48 record48 candle48", 6),
        ["filter48", "ranking48", "encoding48", "mapping48", "record48", "candle48"],
    ),
    (
        ("filter48 ranking48 encoding48 mapping48 record48 candle48", 10),
        ["filter48", "ranking48", "encoding48", "mapping48", "record48", "candle48"],
    ),
    (
        ("filter48 ranking48 encoding48 mapping48 record48 candle48", 18),
        ["filter48 ranking48", "encoding48", "mapping48 record48", "candle48"],
    ),
    (
        ("filter48 ranking48 encoding48 mapping48 record48 candle48", 28),
        ["filter48 ranking48", "encoding48 mapping48", "record48 candle48"],
    ),
    (
        ("ranking48 encoding48 mapping48 record48 candle48 thread48", 6),
        ["ranking48", "encoding48", "mapping48", "record48", "candle48", "thread48"],
    ),
    (
        ("ranking48 encoding48 mapping48 record48 candle48 thread48", 10),
        ["ranking48", "encoding48", "mapping48", "record48", "candle48", "thread48"],
    ),
    (
        ("ranking48 encoding48 mapping48 record48 candle48 thread48", 18),
        ["ranking48", "encoding48", "mapping48 record48", "candle48 thread48"],
    ),
    (
        ("ranking48 encoding48 mapping48 record48 candle48 thread48", 28),
        ["ranking48 encoding48", "mapping48 record48 candle48", "thread48"],
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
