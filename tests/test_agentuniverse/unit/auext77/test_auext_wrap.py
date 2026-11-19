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
        ("round 77: the quick brown fox jumps over the lazy dog", 4),
        ["round", "77:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 77: the quick brown fox jumps over the lazy dog", 8),
        ["round", "77: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 77: the quick brown fox jumps over the lazy dog", 12),
        ["round 77:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 77: the quick brown fox jumps over the lazy dog", 16),
        ["round 77: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 77: the quick brown fox jumps over the lazy dog", 24),
        ["round 77: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 77: the quick brown fox jumps over the lazy dog", 32),
        ["round 77: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 77: agentuniverse is a framework for multi agents", 4),
        ["round", "77:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 77: agentuniverse is a framework for multi agents", 8),
        ["round", "77:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 77: agentuniverse is a framework for multi agents", 12),
        ["round 77:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 77: agentuniverse is a framework for multi agents", 16),
        ["round 77:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 77: agentuniverse is a framework for multi agents", 24),
        ["round 77: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 77: agentuniverse is a framework for multi agents", 32),
        ["round 77: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 77: knowledge stored as vectors enables retrieval", 4),
        ["round", "77:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 77: knowledge stored as vectors enables retrieval", 8),
        ["round", "77:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 77: knowledge stored as vectors enables retrieval", 12),
        ["round 77:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 77: knowledge stored as vectors enables retrieval", 16),
        ["round 77:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 77: knowledge stored as vectors enables retrieval", 24),
        ["round 77: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 77: knowledge stored as vectors enables retrieval", 32),
        ["round 77: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 77: the processor reads the record then stops", 4),
        ["round", "77:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 77: the processor reads the record then stops", 8),
        ["round", "77: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 77: the processor reads the record then stops", 12),
        ["round 77:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 77: the processor reads the record then stops", 16),
        ["round 77: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 77: the processor reads the record then stops", 24),
        ["round 77: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 77: the processor reads the record then stops", 32),
        ["round 77: the processor reads", "the record then stops"],
    ),
    (
        ("round 77: a worker pulls the next task from the queue", 4),
        ["round", "77:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 77: a worker pulls the next task from the queue", 8),
        ["round", "77: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 77: a worker pulls the next task from the queue", 12),
        ["round 77: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 77: a worker pulls the next task from the queue", 16),
        ["round 77: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 77: a worker pulls the next task from the queue", 24),
        ["round 77: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 77: a worker pulls the next task from the queue", 32),
        ["round 77: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 77: signals travel through the network layer", 4),
        ["round", "77:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 77: signals travel through the network layer", 8),
        ["round", "77:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 77: signals travel through the network layer", 12),
        ["round 77:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 77: signals travel through the network layer", 16),
        ["round 77:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 77: signals travel through the network layer", 24),
        ["round 77: signals travel", "through the network", "layer"],
    ),
    (
        ("round 77: signals travel through the network layer", 32),
        ["round 77: signals travel through", "the network layer"],
    ),
    (
        ("round 77: the gateway routes each request by policy", 4),
        ["round", "77:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 77: the gateway routes each request by policy", 8),
        ["round", "77: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 77: the gateway routes each request by policy", 12),
        ["round 77:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 77: the gateway routes each request by policy", 16),
        ["round 77: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 77: the gateway routes each request by policy", 24),
        ["round 77: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 77: the gateway routes each request by policy", 32),
        ["round 77: the gateway routes", "each request by policy"],
    ),
    (
        ("round 77: memory grows until the buffer is full", 4),
        ["round", "77:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 77: memory grows until the buffer is full", 8),
        ["round", "77:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 77: memory grows until the buffer is full", 12),
        ["round 77:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 77: memory grows until the buffer is full", 16),
        ["round 77: memory", "grows until the", "buffer is full"],
    ),
    (("round 77: memory grows until the buffer is full", 24), ["round 77: memory grows", "until the buffer is full"]),
    (("round 77: memory grows until the buffer is full", 32), ["round 77: memory grows until the", "buffer is full"]),
    (
        ("round 77: the cluster mirrors every packet twice", 4),
        ["round", "77:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 77: the cluster mirrors every packet twice", 8),
        ["round", "77: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 77: the cluster mirrors every packet twice", 12),
        ["round 77:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 77: the cluster mirrors every packet twice", 16),
        ["round 77: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 77: the cluster mirrors every packet twice", 24),
        ["round 77: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 77: the cluster mirrors every packet twice", 32), ["round 77: the cluster mirrors", "every packet twice"]),
    (
        ("round 77: ranking uses tokens learned from the corpus", 4),
        ["round", "77:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 77: ranking uses tokens learned from the corpus", 8),
        ["round", "77:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 77: ranking uses tokens learned from the corpus", 12),
        ["round 77:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 77: ranking uses tokens learned from the corpus", 16),
        ["round 77:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 77: ranking uses tokens learned from the corpus", 24),
        ["round 77: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 77: ranking uses tokens learned from the corpus", 32),
        ["round 77: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 77: a long session ends when the candle dies", 4),
        ["round", "77:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 77: a long session ends when the candle dies", 8),
        ["round", "77: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 77: a long session ends when the candle dies", 12),
        ["round 77: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 77: a long session ends when the candle dies", 16),
        ["round 77: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 77: a long session ends when the candle dies", 24),
        ["round 77: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 77: a long session ends when the candle dies", 32),
        ["round 77: a long session ends", "when the candle dies"],
    ),
    (
        ("round 77: encode the prompt then map the result", 4),
        ["round", "77:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 77: encode the prompt then map the result", 8),
        ["round", "77:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 77: encode the prompt then map the result", 12),
        ["round 77:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 77: encode the prompt then map the result", 16),
        ["round 77: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 77: encode the prompt then map the result", 24),
        ["round 77: encode the", "prompt then map the", "result"],
    ),
    (("round 77: encode the prompt then map the result", 32), ["round 77: encode the prompt then", "map the result"]),
    (
        ("round 77: the kernel wakes the worker at dawn", 4),
        ["round", "77:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 77: the kernel wakes the worker at dawn", 8),
        ["round", "77: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 77: the kernel wakes the worker at dawn", 12),
        ["round 77:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 77: the kernel wakes the worker at dawn", 16), ["round 77: the", "kernel wakes the", "worker at dawn"]),
    (("round 77: the kernel wakes the worker at dawn", 24), ["round 77: the kernel", "wakes the worker at dawn"]),
    (("round 77: the kernel wakes the worker at dawn", 32), ["round 77: the kernel wakes the", "worker at dawn"]),
    (
        ("round 77: service latency drops after the patch", 4),
        ["round", "77:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 77: service latency drops after the patch", 8),
        ["round", "77:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 77: service latency drops after the patch", 12),
        ["round 77:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 77: service latency drops after the patch", 16),
        ["round 77:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 77: service latency drops after the patch", 24),
        ["round 77: service", "latency drops after the", "patch"],
    ),
    (("round 77: service latency drops after the patch", 32), ["round 77: service latency drops", "after the patch"]),
    (
        ("round 77: the library caches every vector it sees", 4),
        ["round", "77:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 77: the library caches every vector it sees", 8),
        ["round", "77: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 77: the library caches every vector it sees", 12),
        ["round 77:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 77: the library caches every vector it sees", 16),
        ["round 77: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 77: the library caches every vector it sees", 24),
        ["round 77: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 77: the library caches every vector it sees", 32),
        ["round 77: the library caches", "every vector it sees"],
    ),
    (
        ("round 77: agents argue then the debate resolves", 4),
        ["round", "77:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 77: agents argue then the debate resolves", 8),
        ["round", "77:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 77: agents argue then the debate resolves", 12),
        ["round 77:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 77: agents argue then the debate resolves", 16),
        ["round 77: agents", "argue then the", "debate resolves"],
    ),
    (("round 77: agents argue then the debate resolves", 24), ["round 77: agents argue", "then the debate resolves"]),
    (("round 77: agents argue then the debate resolves", 32), ["round 77: agents argue then the", "debate resolves"]),
    (
        ("round 77: the filter keeps only strong matches", 4),
        ["round", "77:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 77: the filter keeps only strong matches", 8),
        ["round", "77: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 77: the filter keeps only strong matches", 12),
        ["round 77:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 77: the filter keeps only strong matches", 16),
        ["round 77: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 77: the filter keeps only strong matches", 24), ["round 77: the filter", "keeps only strong", "matches"]),
    (("round 77: the filter keeps only strong matches", 32), ["round 77: the filter keeps only", "strong matches"]),
    (
        ("round 77: the model answers with a short reply", 4),
        ["round", "77:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 77: the model answers with a short reply", 8),
        ["round", "77: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 77: the model answers with a short reply", 12),
        ["round 77:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 77: the model answers with a short reply", 16),
        ["round 77: the", "model answers", "with a short", "reply"],
    ),
    (("round 77: the model answers with a short reply", 24), ["round 77: the model", "answers with a short", "reply"]),
    (("round 77: the model answers with a short reply", 32), ["round 77: the model answers with", "a short reply"]),
    (
        ("round 77: the recorder stores the reasoning trace", 4),
        ["round", "77:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 77: the recorder stores the reasoning trace", 8),
        ["round", "77: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 77: the recorder stores the reasoning trace", 12),
        ["round 77:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 77: the recorder stores the reasoning trace", 16),
        ["round 77: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 77: the recorder stores the reasoning trace", 24),
        ["round 77: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 77: the recorder stores the reasoning trace", 32),
        ["round 77: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 77: the angel watches the processor run", 4),
        ["round", "77:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 77: the angel watches the processor run", 8),
        ["round", "77: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 77: the angel watches the processor run", 12),
        ["round 77:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 77: the angel watches the processor run", 16), ["round 77: the", "angel watches", "the processor", "run"]),
    (("round 77: the angel watches the processor run", 24), ["round 77: the angel", "watches the processor", "run"]),
    (("round 77: the angel watches the processor run", 32), ["round 77: the angel watches the", "processor run"]),
    (
        ("round 77: angle of the vector decides the match", 4),
        ["round", "77:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 77: angle of the vector decides the match", 8),
        ["round", "77:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 77: angle of the vector decides the match", 12),
        ["round 77:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 77: angle of the vector decides the match", 16),
        ["round 77: angle", "of the vector", "decides the", "match"],
    ),
    (("round 77: angle of the vector decides the match", 24), ["round 77: angle of the", "vector decides the match"]),
    (("round 77: angle of the vector decides the match", 32), ["round 77: angle of the vector", "decides the match"]),
    (
        ("round 77: the candle burns twice as long at night", 4),
        ["round", "77:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 77: the candle burns twice as long at night", 8),
        ["round", "77: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 77: the candle burns twice as long at night", 12),
        ["round 77:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 77: the candle burns twice as long at night", 16),
        ["round 77: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 77: the candle burns twice as long at night", 24),
        ["round 77: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 77: the candle burns twice as long at night", 32),
        ["round 77: the candle burns twice", "as long at night"],
    ),
    (
        ("round 77: a mirror of the universe in one line", 4),
        ["round", "77:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 77: a mirror of the universe in one line", 8),
        ["round", "77: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 77: a mirror of the universe in one line", 12),
        ["round 77: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 77: a mirror of the universe in one line", 16),
        ["round 77: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 77: a mirror of the universe in one line", 24), ["round 77: a mirror of", "the universe in one line"]),
    (("round 77: a mirror of the universe in one line", 32), ["round 77: a mirror of the", "universe in one line"]),
    (
        ("round 77: the queue drains before the storm", 4),
        ["round", "77:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 77: the queue drains before the storm", 8),
        ["round", "77: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 77: the queue drains before the storm", 12), ["round 77:", "the queue", "drains", "before the", "storm"]),
    (("round 77: the queue drains before the storm", 16), ["round 77: the", "queue drains", "before the storm"]),
    (("round 77: the queue drains before the storm", 24), ["round 77: the queue", "drains before the storm"]),
    (("round 77: the queue drains before the storm", 32), ["round 77: the queue drains", "before the storm"]),
    (
        ("kitten77 sitting77 agent77 angle77 universe77 memory77", 6),
        ["kitten77", "sitting77", "agent77", "angle77", "universe77", "memory77"],
    ),
    (
        ("kitten77 sitting77 agent77 angle77 universe77 memory77", 10),
        ["kitten77", "sitting77", "agent77", "angle77", "universe77", "memory77"],
    ),
    (
        ("kitten77 sitting77 agent77 angle77 universe77 memory77", 18),
        ["kitten77 sitting77", "agent77 angle77", "universe77", "memory77"],
    ),
    (
        ("kitten77 sitting77 agent77 angle77 universe77 memory77", 28),
        ["kitten77 sitting77 agent77", "angle77 universe77 memory77"],
    ),
    (
        ("sitting77 agent77 angle77 universe77 memory77 stream77", 6),
        ["sitting77", "agent77", "angle77", "universe77", "memory77", "stream77"],
    ),
    (
        ("sitting77 agent77 angle77 universe77 memory77 stream77", 10),
        ["sitting77", "agent77", "angle77", "universe77", "memory77", "stream77"],
    ),
    (
        ("sitting77 agent77 angle77 universe77 memory77 stream77", 18),
        ["sitting77 agent77", "angle77 universe77", "memory77 stream77"],
    ),
    (
        ("sitting77 agent77 angle77 universe77 memory77 stream77", 28),
        ["sitting77 agent77 angle77", "universe77 memory77 stream77"],
    ),
    (
        ("agent77 angle77 universe77 memory77 stream77 context77", 6),
        ["agent77", "angle77", "universe77", "memory77", "stream77", "context77"],
    ),
    (
        ("agent77 angle77 universe77 memory77 stream77 context77", 10),
        ["agent77", "angle77", "universe77", "memory77", "stream77", "context77"],
    ),
    (
        ("agent77 angle77 universe77 memory77 stream77 context77", 18),
        ["agent77 angle77", "universe77", "memory77 stream77", "context77"],
    ),
    (
        ("agent77 angle77 universe77 memory77 stream77 context77", 28),
        ["agent77 angle77 universe77", "memory77 stream77 context77"],
    ),
    (
        ("angle77 universe77 memory77 stream77 context77 knowledge77", 6),
        ["angle77", "universe77", "memory77", "stream77", "context77", "knowledge77"],
    ),
    (
        ("angle77 universe77 memory77 stream77 context77 knowledge77", 10),
        ["angle77", "universe77", "memory77", "stream77", "context77", "knowledge77"],
    ),
    (
        ("angle77 universe77 memory77 stream77 context77 knowledge77", 18),
        ["angle77 universe77", "memory77 stream77", "context77", "knowledge77"],
    ),
    (
        ("angle77 universe77 memory77 stream77 context77 knowledge77", 28),
        ["angle77 universe77 memory77", "stream77 context77", "knowledge77"],
    ),
    (
        ("universe77 memory77 stream77 context77 knowledge77 vector77", 6),
        ["universe77", "memory77", "stream77", "context77", "knowledge77", "vector77"],
    ),
    (
        ("universe77 memory77 stream77 context77 knowledge77 vector77", 10),
        ["universe77", "memory77", "stream77", "context77", "knowledge77", "vector77"],
    ),
    (
        ("universe77 memory77 stream77 context77 knowledge77 vector77", 18),
        ["universe77", "memory77 stream77", "context77", "knowledge77", "vector77"],
    ),
    (
        ("universe77 memory77 stream77 context77 knowledge77 vector77", 28),
        ["universe77 memory77 stream77", "context77 knowledge77", "vector77"],
    ),
    (
        ("memory77 stream77 context77 knowledge77 vector77 processor77", 6),
        ["memory77", "stream77", "context77", "knowledge77", "vector77", "processor77"],
    ),
    (
        ("memory77 stream77 context77 knowledge77 vector77 processor77", 10),
        ["memory77", "stream77", "context77", "knowledge77", "vector77", "processor77"],
    ),
    (
        ("memory77 stream77 context77 knowledge77 vector77 processor77", 18),
        ["memory77 stream77", "context77", "knowledge77", "vector77", "processor77"],
    ),
    (
        ("memory77 stream77 context77 knowledge77 vector77 processor77", 28),
        ["memory77 stream77 context77", "knowledge77 vector77", "processor77"],
    ),
    (
        ("stream77 context77 knowledge77 vector77 processor77 reasoning77", 6),
        ["stream77", "context77", "knowledge77", "vector77", "processor77", "reasoning77"],
    ),
    (
        ("stream77 context77 knowledge77 vector77 processor77 reasoning77", 10),
        ["stream77", "context77", "knowledge77", "vector77", "processor77", "reasoning77"],
    ),
    (
        ("stream77 context77 knowledge77 vector77 processor77 reasoning77", 18),
        ["stream77 context77", "knowledge77", "vector77", "processor77", "reasoning77"],
    ),
    (
        ("stream77 context77 knowledge77 vector77 processor77 reasoning77", 28),
        ["stream77 context77", "knowledge77 vector77", "processor77 reasoning77"],
    ),
    (
        ("context77 knowledge77 vector77 processor77 reasoning77 machine77", 6),
        ["context77", "knowledge77", "vector77", "processor77", "reasoning77", "machine77"],
    ),
    (
        ("context77 knowledge77 vector77 processor77 reasoning77 machine77", 10),
        ["context77", "knowledge77", "vector77", "processor77", "reasoning77", "machine77"],
    ),
    (
        ("context77 knowledge77 vector77 processor77 reasoning77 machine77", 18),
        ["context77", "knowledge77", "vector77", "processor77", "reasoning77", "machine77"],
    ),
    (
        ("context77 knowledge77 vector77 processor77 reasoning77 machine77", 28),
        ["context77 knowledge77", "vector77 processor77", "reasoning77 machine77"],
    ),
    (
        ("knowledge77 vector77 processor77 reasoning77 machine77 learning77", 6),
        ["knowledge77", "vector77", "processor77", "reasoning77", "machine77", "learning77"],
    ),
    (
        ("knowledge77 vector77 processor77 reasoning77 machine77 learning77", 10),
        ["knowledge77", "vector77", "processor77", "reasoning77", "machine77", "learning77"],
    ),
    (
        ("knowledge77 vector77 processor77 reasoning77 machine77 learning77", 18),
        ["knowledge77", "vector77", "processor77", "reasoning77", "machine77", "learning77"],
    ),
    (
        ("knowledge77 vector77 processor77 reasoning77 machine77 learning77", 28),
        ["knowledge77 vector77", "processor77 reasoning77", "machine77 learning77"],
    ),
    (
        ("vector77 processor77 reasoning77 machine77 learning77 model77", 6),
        ["vector77", "processor77", "reasoning77", "machine77", "learning77", "model77"],
    ),
    (
        ("vector77 processor77 reasoning77 machine77 learning77 model77", 10),
        ["vector77", "processor77", "reasoning77", "machine77", "learning77", "model77"],
    ),
    (
        ("vector77 processor77 reasoning77 machine77 learning77 model77", 18),
        ["vector77", "processor77", "reasoning77", "machine77", "learning77 model77"],
    ),
    (
        ("vector77 processor77 reasoning77 machine77 learning77 model77", 28),
        ["vector77 processor77", "reasoning77 machine77", "learning77 model77"],
    ),
    (
        ("processor77 reasoning77 machine77 learning77 model77 token77", 6),
        ["processor77", "reasoning77", "machine77", "learning77", "model77", "token77"],
    ),
    (
        ("processor77 reasoning77 machine77 learning77 model77 token77", 10),
        ["processor77", "reasoning77", "machine77", "learning77", "model77", "token77"],
    ),
    (
        ("processor77 reasoning77 machine77 learning77 model77 token77", 18),
        ["processor77", "reasoning77", "machine77", "learning77 model77", "token77"],
    ),
    (
        ("processor77 reasoning77 machine77 learning77 model77 token77", 28),
        ["processor77 reasoning77", "machine77 learning77 model77", "token77"],
    ),
    (
        ("reasoning77 machine77 learning77 model77 token77 prompt77", 6),
        ["reasoning77", "machine77", "learning77", "model77", "token77", "prompt77"],
    ),
    (
        ("reasoning77 machine77 learning77 model77 token77 prompt77", 10),
        ["reasoning77", "machine77", "learning77", "model77", "token77", "prompt77"],
    ),
    (
        ("reasoning77 machine77 learning77 model77 token77 prompt77", 18),
        ["reasoning77", "machine77", "learning77 model77", "token77 prompt77"],
    ),
    (
        ("reasoning77 machine77 learning77 model77 token77 prompt77", 28),
        ["reasoning77 machine77", "learning77 model77 token77", "prompt77"],
    ),
    (
        ("machine77 learning77 model77 token77 prompt77 session77", 6),
        ["machine77", "learning77", "model77", "token77", "prompt77", "session77"],
    ),
    (
        ("machine77 learning77 model77 token77 prompt77 session77", 10),
        ["machine77", "learning77", "model77", "token77", "prompt77", "session77"],
    ),
    (
        ("machine77 learning77 model77 token77 prompt77 session77", 18),
        ["machine77", "learning77 model77", "token77 prompt77", "session77"],
    ),
    (
        ("machine77 learning77 model77 token77 prompt77 session77", 28),
        ["machine77 learning77 model77", "token77 prompt77 session77"],
    ),
    (
        ("learning77 model77 token77 prompt77 session77 library77", 6),
        ["learning77", "model77", "token77", "prompt77", "session77", "library77"],
    ),
    (
        ("learning77 model77 token77 prompt77 session77 library77", 10),
        ["learning77", "model77", "token77", "prompt77", "session77", "library77"],
    ),
    (
        ("learning77 model77 token77 prompt77 session77 library77", 18),
        ["learning77 model77", "token77 prompt77", "session77", "library77"],
    ),
    (
        ("learning77 model77 token77 prompt77 session77 library77", 28),
        ["learning77 model77 token77", "prompt77 session77 library77"],
    ),
    (
        ("model77 token77 prompt77 session77 library77 service77", 6),
        ["model77", "token77", "prompt77", "session77", "library77", "service77"],
    ),
    (
        ("model77 token77 prompt77 session77 library77 service77", 10),
        ["model77", "token77", "prompt77", "session77", "library77", "service77"],
    ),
    (
        ("model77 token77 prompt77 session77 library77 service77", 18),
        ["model77 token77", "prompt77 session77", "library77", "service77"],
    ),
    (
        ("model77 token77 prompt77 session77 library77 service77", 28),
        ["model77 token77 prompt77", "session77 library77", "service77"],
    ),
    (
        ("token77 prompt77 session77 library77 service77 gateway77", 6),
        ["token77", "prompt77", "session77", "library77", "service77", "gateway77"],
    ),
    (
        ("token77 prompt77 session77 library77 service77 gateway77", 10),
        ["token77", "prompt77", "session77", "library77", "service77", "gateway77"],
    ),
    (
        ("token77 prompt77 session77 library77 service77 gateway77", 18),
        ["token77 prompt77", "session77", "library77", "service77", "gateway77"],
    ),
    (
        ("token77 prompt77 session77 library77 service77 gateway77", 28),
        ["token77 prompt77 session77", "library77 service77", "gateway77"],
    ),
    (
        ("prompt77 session77 library77 service77 gateway77 storage77", 6),
        ["prompt77", "session77", "library77", "service77", "gateway77", "storage77"],
    ),
    (
        ("prompt77 session77 library77 service77 gateway77 storage77", 10),
        ["prompt77", "session77", "library77", "service77", "gateway77", "storage77"],
    ),
    (
        ("prompt77 session77 library77 service77 gateway77 storage77", 18),
        ["prompt77 session77", "library77", "service77", "gateway77", "storage77"],
    ),
    (
        ("prompt77 session77 library77 service77 gateway77 storage77", 28),
        ["prompt77 session77 library77", "service77 gateway77", "storage77"],
    ),
    (
        ("session77 library77 service77 gateway77 storage77 network77", 6),
        ["session77", "library77", "service77", "gateway77", "storage77", "network77"],
    ),
    (
        ("session77 library77 service77 gateway77 storage77 network77", 10),
        ["session77", "library77", "service77", "gateway77", "storage77", "network77"],
    ),
    (
        ("session77 library77 service77 gateway77 storage77 network77", 18),
        ["session77", "library77", "service77", "gateway77", "storage77", "network77"],
    ),
    (
        ("session77 library77 service77 gateway77 storage77 network77", 28),
        ["session77 library77", "service77 gateway77", "storage77 network77"],
    ),
    (
        ("library77 service77 gateway77 storage77 network77 latency77", 6),
        ["library77", "service77", "gateway77", "storage77", "network77", "latency77"],
    ),
    (
        ("library77 service77 gateway77 storage77 network77 latency77", 10),
        ["library77", "service77", "gateway77", "storage77", "network77", "latency77"],
    ),
    (
        ("library77 service77 gateway77 storage77 network77 latency77", 18),
        ["library77", "service77", "gateway77", "storage77", "network77", "latency77"],
    ),
    (
        ("library77 service77 gateway77 storage77 network77 latency77", 28),
        ["library77 service77", "gateway77 storage77", "network77 latency77"],
    ),
    (
        ("service77 gateway77 storage77 network77 latency77 buffer77", 6),
        ["service77", "gateway77", "storage77", "network77", "latency77", "buffer77"],
    ),
    (
        ("service77 gateway77 storage77 network77 latency77 buffer77", 10),
        ["service77", "gateway77", "storage77", "network77", "latency77", "buffer77"],
    ),
    (
        ("service77 gateway77 storage77 network77 latency77 buffer77", 18),
        ["service77", "gateway77", "storage77", "network77", "latency77 buffer77"],
    ),
    (
        ("service77 gateway77 storage77 network77 latency77 buffer77", 28),
        ["service77 gateway77", "storage77 network77", "latency77 buffer77"],
    ),
    (
        ("gateway77 storage77 network77 latency77 buffer77 queue77", 6),
        ["gateway77", "storage77", "network77", "latency77", "buffer77", "queue77"],
    ),
    (
        ("gateway77 storage77 network77 latency77 buffer77 queue77", 10),
        ["gateway77", "storage77", "network77", "latency77", "buffer77", "queue77"],
    ),
    (
        ("gateway77 storage77 network77 latency77 buffer77 queue77", 18),
        ["gateway77", "storage77", "network77", "latency77 buffer77", "queue77"],
    ),
    (
        ("gateway77 storage77 network77 latency77 buffer77 queue77", 28),
        ["gateway77 storage77", "network77 latency77 buffer77", "queue77"],
    ),
    (
        ("storage77 network77 latency77 buffer77 queue77 worker77", 6),
        ["storage77", "network77", "latency77", "buffer77", "queue77", "worker77"],
    ),
    (
        ("storage77 network77 latency77 buffer77 queue77 worker77", 10),
        ["storage77", "network77", "latency77", "buffer77", "queue77", "worker77"],
    ),
    (
        ("storage77 network77 latency77 buffer77 queue77 worker77", 18),
        ["storage77", "network77", "latency77 buffer77", "queue77 worker77"],
    ),
    (
        ("storage77 network77 latency77 buffer77 queue77 worker77", 28),
        ["storage77 network77", "latency77 buffer77 queue77", "worker77"],
    ),
    (
        ("network77 latency77 buffer77 queue77 worker77 kernel77", 6),
        ["network77", "latency77", "buffer77", "queue77", "worker77", "kernel77"],
    ),
    (
        ("network77 latency77 buffer77 queue77 worker77 kernel77", 10),
        ["network77", "latency77", "buffer77", "queue77", "worker77", "kernel77"],
    ),
    (
        ("network77 latency77 buffer77 queue77 worker77 kernel77", 18),
        ["network77", "latency77 buffer77", "queue77 worker77", "kernel77"],
    ),
    (
        ("network77 latency77 buffer77 queue77 worker77 kernel77", 28),
        ["network77 latency77 buffer77", "queue77 worker77 kernel77"],
    ),
    (
        ("latency77 buffer77 queue77 worker77 kernel77 signal77", 6),
        ["latency77", "buffer77", "queue77", "worker77", "kernel77", "signal77"],
    ),
    (
        ("latency77 buffer77 queue77 worker77 kernel77 signal77", 10),
        ["latency77", "buffer77", "queue77", "worker77", "kernel77", "signal77"],
    ),
    (
        ("latency77 buffer77 queue77 worker77 kernel77 signal77", 18),
        ["latency77 buffer77", "queue77 worker77", "kernel77 signal77"],
    ),
    (
        ("latency77 buffer77 queue77 worker77 kernel77 signal77", 28),
        ["latency77 buffer77 queue77", "worker77 kernel77 signal77"],
    ),
    (
        ("buffer77 queue77 worker77 kernel77 signal77 packet77", 6),
        ["buffer77", "queue77", "worker77", "kernel77", "signal77", "packet77"],
    ),
    (
        ("buffer77 queue77 worker77 kernel77 signal77 packet77", 10),
        ["buffer77", "queue77", "worker77", "kernel77", "signal77", "packet77"],
    ),
    (
        ("buffer77 queue77 worker77 kernel77 signal77 packet77", 18),
        ["buffer77 queue77", "worker77 kernel77", "signal77 packet77"],
    ),
    (
        ("buffer77 queue77 worker77 kernel77 signal77 packet77", 28),
        ["buffer77 queue77 worker77", "kernel77 signal77 packet77"],
    ),
    (
        ("queue77 worker77 kernel77 signal77 packet77 router77", 6),
        ["queue77", "worker77", "kernel77", "signal77", "packet77", "router77"],
    ),
    (
        ("queue77 worker77 kernel77 signal77 packet77 router77", 10),
        ["queue77", "worker77", "kernel77", "signal77", "packet77", "router77"],
    ),
    (
        ("queue77 worker77 kernel77 signal77 packet77 router77", 18),
        ["queue77 worker77", "kernel77 signal77", "packet77 router77"],
    ),
    (
        ("queue77 worker77 kernel77 signal77 packet77 router77", 28),
        ["queue77 worker77 kernel77", "signal77 packet77 router77"],
    ),
    (
        ("worker77 kernel77 signal77 packet77 router77 cluster77", 6),
        ["worker77", "kernel77", "signal77", "packet77", "router77", "cluster77"],
    ),
    (
        ("worker77 kernel77 signal77 packet77 router77 cluster77", 10),
        ["worker77", "kernel77", "signal77", "packet77", "router77", "cluster77"],
    ),
    (
        ("worker77 kernel77 signal77 packet77 router77 cluster77", 18),
        ["worker77 kernel77", "signal77 packet77", "router77 cluster77"],
    ),
    (
        ("worker77 kernel77 signal77 packet77 router77 cluster77", 28),
        ["worker77 kernel77 signal77", "packet77 router77 cluster77"],
    ),
    (
        ("kernel77 signal77 packet77 router77 cluster77 mirror77", 6),
        ["kernel77", "signal77", "packet77", "router77", "cluster77", "mirror77"],
    ),
    (
        ("kernel77 signal77 packet77 router77 cluster77 mirror77", 10),
        ["kernel77", "signal77", "packet77", "router77", "cluster77", "mirror77"],
    ),
    (
        ("kernel77 signal77 packet77 router77 cluster77 mirror77", 18),
        ["kernel77 signal77", "packet77 router77", "cluster77 mirror77"],
    ),
    (
        ("kernel77 signal77 packet77 router77 cluster77 mirror77", 28),
        ["kernel77 signal77 packet77", "router77 cluster77 mirror77"],
    ),
    (
        ("signal77 packet77 router77 cluster77 mirror77 filter77", 6),
        ["signal77", "packet77", "router77", "cluster77", "mirror77", "filter77"],
    ),
    (
        ("signal77 packet77 router77 cluster77 mirror77 filter77", 10),
        ["signal77", "packet77", "router77", "cluster77", "mirror77", "filter77"],
    ),
    (
        ("signal77 packet77 router77 cluster77 mirror77 filter77", 18),
        ["signal77 packet77", "router77 cluster77", "mirror77 filter77"],
    ),
    (
        ("signal77 packet77 router77 cluster77 mirror77 filter77", 28),
        ["signal77 packet77 router77", "cluster77 mirror77 filter77"],
    ),
    (
        ("packet77 router77 cluster77 mirror77 filter77 ranking77", 6),
        ["packet77", "router77", "cluster77", "mirror77", "filter77", "ranking77"],
    ),
    (
        ("packet77 router77 cluster77 mirror77 filter77 ranking77", 10),
        ["packet77", "router77", "cluster77", "mirror77", "filter77", "ranking77"],
    ),
    (
        ("packet77 router77 cluster77 mirror77 filter77 ranking77", 18),
        ["packet77 router77", "cluster77 mirror77", "filter77 ranking77"],
    ),
    (
        ("packet77 router77 cluster77 mirror77 filter77 ranking77", 28),
        ["packet77 router77 cluster77", "mirror77 filter77 ranking77"],
    ),
    (
        ("router77 cluster77 mirror77 filter77 ranking77 encoding77", 6),
        ["router77", "cluster77", "mirror77", "filter77", "ranking77", "encoding77"],
    ),
    (
        ("router77 cluster77 mirror77 filter77 ranking77 encoding77", 10),
        ["router77", "cluster77", "mirror77", "filter77", "ranking77", "encoding77"],
    ),
    (
        ("router77 cluster77 mirror77 filter77 ranking77 encoding77", 18),
        ["router77 cluster77", "mirror77 filter77", "ranking77", "encoding77"],
    ),
    (
        ("router77 cluster77 mirror77 filter77 ranking77 encoding77", 28),
        ["router77 cluster77 mirror77", "filter77 ranking77", "encoding77"],
    ),
    (
        ("cluster77 mirror77 filter77 ranking77 encoding77 mapping77", 6),
        ["cluster77", "mirror77", "filter77", "ranking77", "encoding77", "mapping77"],
    ),
    (
        ("cluster77 mirror77 filter77 ranking77 encoding77 mapping77", 10),
        ["cluster77", "mirror77", "filter77", "ranking77", "encoding77", "mapping77"],
    ),
    (
        ("cluster77 mirror77 filter77 ranking77 encoding77 mapping77", 18),
        ["cluster77 mirror77", "filter77 ranking77", "encoding77", "mapping77"],
    ),
    (
        ("cluster77 mirror77 filter77 ranking77 encoding77 mapping77", 28),
        ["cluster77 mirror77 filter77", "ranking77 encoding77", "mapping77"],
    ),
    (
        ("mirror77 filter77 ranking77 encoding77 mapping77 record77", 6),
        ["mirror77", "filter77", "ranking77", "encoding77", "mapping77", "record77"],
    ),
    (
        ("mirror77 filter77 ranking77 encoding77 mapping77 record77", 10),
        ["mirror77", "filter77", "ranking77", "encoding77", "mapping77", "record77"],
    ),
    (
        ("mirror77 filter77 ranking77 encoding77 mapping77 record77", 18),
        ["mirror77 filter77", "ranking77", "encoding77", "mapping77 record77"],
    ),
    (
        ("mirror77 filter77 ranking77 encoding77 mapping77 record77", 28),
        ["mirror77 filter77 ranking77", "encoding77 mapping77", "record77"],
    ),
    (
        ("filter77 ranking77 encoding77 mapping77 record77 candle77", 6),
        ["filter77", "ranking77", "encoding77", "mapping77", "record77", "candle77"],
    ),
    (
        ("filter77 ranking77 encoding77 mapping77 record77 candle77", 10),
        ["filter77", "ranking77", "encoding77", "mapping77", "record77", "candle77"],
    ),
    (
        ("filter77 ranking77 encoding77 mapping77 record77 candle77", 18),
        ["filter77 ranking77", "encoding77", "mapping77 record77", "candle77"],
    ),
    (
        ("filter77 ranking77 encoding77 mapping77 record77 candle77", 28),
        ["filter77 ranking77", "encoding77 mapping77", "record77 candle77"],
    ),
    (
        ("ranking77 encoding77 mapping77 record77 candle77 thread77", 6),
        ["ranking77", "encoding77", "mapping77", "record77", "candle77", "thread77"],
    ),
    (
        ("ranking77 encoding77 mapping77 record77 candle77 thread77", 10),
        ["ranking77", "encoding77", "mapping77", "record77", "candle77", "thread77"],
    ),
    (
        ("ranking77 encoding77 mapping77 record77 candle77 thread77", 18),
        ["ranking77", "encoding77", "mapping77 record77", "candle77 thread77"],
    ),
    (
        ("ranking77 encoding77 mapping77 record77 candle77 thread77", 28),
        ["ranking77 encoding77", "mapping77 record77 candle77", "thread77"],
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
