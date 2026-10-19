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
        ("round 60: the quick brown fox jumps over the lazy dog", 4),
        ["round", "60:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 60: the quick brown fox jumps over the lazy dog", 8),
        ["round", "60: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 60: the quick brown fox jumps over the lazy dog", 12),
        ["round 60:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 60: the quick brown fox jumps over the lazy dog", 16),
        ["round 60: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 60: the quick brown fox jumps over the lazy dog", 24),
        ["round 60: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 60: the quick brown fox jumps over the lazy dog", 32),
        ["round 60: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 60: agentuniverse is a framework for multi agents", 4),
        ["round", "60:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 60: agentuniverse is a framework for multi agents", 8),
        ["round", "60:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 60: agentuniverse is a framework for multi agents", 12),
        ["round 60:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 60: agentuniverse is a framework for multi agents", 16),
        ["round 60:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 60: agentuniverse is a framework for multi agents", 24),
        ["round 60: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 60: agentuniverse is a framework for multi agents", 32),
        ["round 60: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 60: knowledge stored as vectors enables retrieval", 4),
        ["round", "60:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 60: knowledge stored as vectors enables retrieval", 8),
        ["round", "60:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 60: knowledge stored as vectors enables retrieval", 12),
        ["round 60:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 60: knowledge stored as vectors enables retrieval", 16),
        ["round 60:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 60: knowledge stored as vectors enables retrieval", 24),
        ["round 60: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 60: knowledge stored as vectors enables retrieval", 32),
        ["round 60: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 60: the processor reads the record then stops", 4),
        ["round", "60:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 60: the processor reads the record then stops", 8),
        ["round", "60: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 60: the processor reads the record then stops", 12),
        ["round 60:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 60: the processor reads the record then stops", 16),
        ["round 60: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 60: the processor reads the record then stops", 24),
        ["round 60: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 60: the processor reads the record then stops", 32),
        ["round 60: the processor reads", "the record then stops"],
    ),
    (
        ("round 60: a worker pulls the next task from the queue", 4),
        ["round", "60:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 60: a worker pulls the next task from the queue", 8),
        ["round", "60: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 60: a worker pulls the next task from the queue", 12),
        ["round 60: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 60: a worker pulls the next task from the queue", 16),
        ["round 60: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 60: a worker pulls the next task from the queue", 24),
        ["round 60: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 60: a worker pulls the next task from the queue", 32),
        ["round 60: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 60: signals travel through the network layer", 4),
        ["round", "60:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 60: signals travel through the network layer", 8),
        ["round", "60:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 60: signals travel through the network layer", 12),
        ["round 60:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 60: signals travel through the network layer", 16),
        ["round 60:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 60: signals travel through the network layer", 24),
        ["round 60: signals travel", "through the network", "layer"],
    ),
    (
        ("round 60: signals travel through the network layer", 32),
        ["round 60: signals travel through", "the network layer"],
    ),
    (
        ("round 60: the gateway routes each request by policy", 4),
        ["round", "60:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 60: the gateway routes each request by policy", 8),
        ["round", "60: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 60: the gateway routes each request by policy", 12),
        ["round 60:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 60: the gateway routes each request by policy", 16),
        ["round 60: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 60: the gateway routes each request by policy", 24),
        ["round 60: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 60: the gateway routes each request by policy", 32),
        ["round 60: the gateway routes", "each request by policy"],
    ),
    (
        ("round 60: memory grows until the buffer is full", 4),
        ["round", "60:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 60: memory grows until the buffer is full", 8),
        ["round", "60:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 60: memory grows until the buffer is full", 12),
        ["round 60:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 60: memory grows until the buffer is full", 16),
        ["round 60: memory", "grows until the", "buffer is full"],
    ),
    (("round 60: memory grows until the buffer is full", 24), ["round 60: memory grows", "until the buffer is full"]),
    (("round 60: memory grows until the buffer is full", 32), ["round 60: memory grows until the", "buffer is full"]),
    (
        ("round 60: the cluster mirrors every packet twice", 4),
        ["round", "60:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 60: the cluster mirrors every packet twice", 8),
        ["round", "60: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 60: the cluster mirrors every packet twice", 12),
        ["round 60:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 60: the cluster mirrors every packet twice", 16),
        ["round 60: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 60: the cluster mirrors every packet twice", 24),
        ["round 60: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 60: the cluster mirrors every packet twice", 32), ["round 60: the cluster mirrors", "every packet twice"]),
    (
        ("round 60: ranking uses tokens learned from the corpus", 4),
        ["round", "60:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 60: ranking uses tokens learned from the corpus", 8),
        ["round", "60:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 60: ranking uses tokens learned from the corpus", 12),
        ["round 60:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 60: ranking uses tokens learned from the corpus", 16),
        ["round 60:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 60: ranking uses tokens learned from the corpus", 24),
        ["round 60: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 60: ranking uses tokens learned from the corpus", 32),
        ["round 60: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 60: a long session ends when the candle dies", 4),
        ["round", "60:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 60: a long session ends when the candle dies", 8),
        ["round", "60: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 60: a long session ends when the candle dies", 12),
        ["round 60: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 60: a long session ends when the candle dies", 16),
        ["round 60: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 60: a long session ends when the candle dies", 24),
        ["round 60: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 60: a long session ends when the candle dies", 32),
        ["round 60: a long session ends", "when the candle dies"],
    ),
    (
        ("round 60: encode the prompt then map the result", 4),
        ["round", "60:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 60: encode the prompt then map the result", 8),
        ["round", "60:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 60: encode the prompt then map the result", 12),
        ["round 60:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 60: encode the prompt then map the result", 16),
        ["round 60: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 60: encode the prompt then map the result", 24),
        ["round 60: encode the", "prompt then map the", "result"],
    ),
    (("round 60: encode the prompt then map the result", 32), ["round 60: encode the prompt then", "map the result"]),
    (
        ("round 60: the kernel wakes the worker at dawn", 4),
        ["round", "60:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 60: the kernel wakes the worker at dawn", 8),
        ["round", "60: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 60: the kernel wakes the worker at dawn", 12),
        ["round 60:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 60: the kernel wakes the worker at dawn", 16), ["round 60: the", "kernel wakes the", "worker at dawn"]),
    (("round 60: the kernel wakes the worker at dawn", 24), ["round 60: the kernel", "wakes the worker at dawn"]),
    (("round 60: the kernel wakes the worker at dawn", 32), ["round 60: the kernel wakes the", "worker at dawn"]),
    (
        ("round 60: service latency drops after the patch", 4),
        ["round", "60:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 60: service latency drops after the patch", 8),
        ["round", "60:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 60: service latency drops after the patch", 12),
        ["round 60:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 60: service latency drops after the patch", 16),
        ["round 60:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 60: service latency drops after the patch", 24),
        ["round 60: service", "latency drops after the", "patch"],
    ),
    (("round 60: service latency drops after the patch", 32), ["round 60: service latency drops", "after the patch"]),
    (
        ("round 60: the library caches every vector it sees", 4),
        ["round", "60:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 60: the library caches every vector it sees", 8),
        ["round", "60: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 60: the library caches every vector it sees", 12),
        ["round 60:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 60: the library caches every vector it sees", 16),
        ["round 60: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 60: the library caches every vector it sees", 24),
        ["round 60: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 60: the library caches every vector it sees", 32),
        ["round 60: the library caches", "every vector it sees"],
    ),
    (
        ("round 60: agents argue then the debate resolves", 4),
        ["round", "60:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 60: agents argue then the debate resolves", 8),
        ["round", "60:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 60: agents argue then the debate resolves", 12),
        ["round 60:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 60: agents argue then the debate resolves", 16),
        ["round 60: agents", "argue then the", "debate resolves"],
    ),
    (("round 60: agents argue then the debate resolves", 24), ["round 60: agents argue", "then the debate resolves"]),
    (("round 60: agents argue then the debate resolves", 32), ["round 60: agents argue then the", "debate resolves"]),
    (
        ("round 60: the filter keeps only strong matches", 4),
        ["round", "60:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 60: the filter keeps only strong matches", 8),
        ["round", "60: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 60: the filter keeps only strong matches", 12),
        ["round 60:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 60: the filter keeps only strong matches", 16),
        ["round 60: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 60: the filter keeps only strong matches", 24), ["round 60: the filter", "keeps only strong", "matches"]),
    (("round 60: the filter keeps only strong matches", 32), ["round 60: the filter keeps only", "strong matches"]),
    (
        ("round 60: the model answers with a short reply", 4),
        ["round", "60:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 60: the model answers with a short reply", 8),
        ["round", "60: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 60: the model answers with a short reply", 12),
        ["round 60:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 60: the model answers with a short reply", 16),
        ["round 60: the", "model answers", "with a short", "reply"],
    ),
    (("round 60: the model answers with a short reply", 24), ["round 60: the model", "answers with a short", "reply"]),
    (("round 60: the model answers with a short reply", 32), ["round 60: the model answers with", "a short reply"]),
    (
        ("round 60: the recorder stores the reasoning trace", 4),
        ["round", "60:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 60: the recorder stores the reasoning trace", 8),
        ["round", "60: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 60: the recorder stores the reasoning trace", 12),
        ["round 60:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 60: the recorder stores the reasoning trace", 16),
        ["round 60: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 60: the recorder stores the reasoning trace", 24),
        ["round 60: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 60: the recorder stores the reasoning trace", 32),
        ["round 60: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 60: the angel watches the processor run", 4),
        ["round", "60:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 60: the angel watches the processor run", 8),
        ["round", "60: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 60: the angel watches the processor run", 12),
        ["round 60:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 60: the angel watches the processor run", 16), ["round 60: the", "angel watches", "the processor", "run"]),
    (("round 60: the angel watches the processor run", 24), ["round 60: the angel", "watches the processor", "run"]),
    (("round 60: the angel watches the processor run", 32), ["round 60: the angel watches the", "processor run"]),
    (
        ("round 60: angle of the vector decides the match", 4),
        ["round", "60:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 60: angle of the vector decides the match", 8),
        ["round", "60:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 60: angle of the vector decides the match", 12),
        ["round 60:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 60: angle of the vector decides the match", 16),
        ["round 60: angle", "of the vector", "decides the", "match"],
    ),
    (("round 60: angle of the vector decides the match", 24), ["round 60: angle of the", "vector decides the match"]),
    (("round 60: angle of the vector decides the match", 32), ["round 60: angle of the vector", "decides the match"]),
    (
        ("round 60: the candle burns twice as long at night", 4),
        ["round", "60:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 60: the candle burns twice as long at night", 8),
        ["round", "60: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 60: the candle burns twice as long at night", 12),
        ["round 60:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 60: the candle burns twice as long at night", 16),
        ["round 60: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 60: the candle burns twice as long at night", 24),
        ["round 60: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 60: the candle burns twice as long at night", 32),
        ["round 60: the candle burns twice", "as long at night"],
    ),
    (
        ("round 60: a mirror of the universe in one line", 4),
        ["round", "60:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 60: a mirror of the universe in one line", 8),
        ["round", "60: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 60: a mirror of the universe in one line", 12),
        ["round 60: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 60: a mirror of the universe in one line", 16),
        ["round 60: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 60: a mirror of the universe in one line", 24), ["round 60: a mirror of", "the universe in one line"]),
    (("round 60: a mirror of the universe in one line", 32), ["round 60: a mirror of the", "universe in one line"]),
    (
        ("round 60: the queue drains before the storm", 4),
        ["round", "60:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 60: the queue drains before the storm", 8),
        ["round", "60: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 60: the queue drains before the storm", 12), ["round 60:", "the queue", "drains", "before the", "storm"]),
    (("round 60: the queue drains before the storm", 16), ["round 60: the", "queue drains", "before the storm"]),
    (("round 60: the queue drains before the storm", 24), ["round 60: the queue", "drains before the storm"]),
    (("round 60: the queue drains before the storm", 32), ["round 60: the queue drains", "before the storm"]),
    (
        ("kitten60 sitting60 agent60 angle60 universe60 memory60", 6),
        ["kitten60", "sitting60", "agent60", "angle60", "universe60", "memory60"],
    ),
    (
        ("kitten60 sitting60 agent60 angle60 universe60 memory60", 10),
        ["kitten60", "sitting60", "agent60", "angle60", "universe60", "memory60"],
    ),
    (
        ("kitten60 sitting60 agent60 angle60 universe60 memory60", 18),
        ["kitten60 sitting60", "agent60 angle60", "universe60", "memory60"],
    ),
    (
        ("kitten60 sitting60 agent60 angle60 universe60 memory60", 28),
        ["kitten60 sitting60 agent60", "angle60 universe60 memory60"],
    ),
    (
        ("sitting60 agent60 angle60 universe60 memory60 stream60", 6),
        ["sitting60", "agent60", "angle60", "universe60", "memory60", "stream60"],
    ),
    (
        ("sitting60 agent60 angle60 universe60 memory60 stream60", 10),
        ["sitting60", "agent60", "angle60", "universe60", "memory60", "stream60"],
    ),
    (
        ("sitting60 agent60 angle60 universe60 memory60 stream60", 18),
        ["sitting60 agent60", "angle60 universe60", "memory60 stream60"],
    ),
    (
        ("sitting60 agent60 angle60 universe60 memory60 stream60", 28),
        ["sitting60 agent60 angle60", "universe60 memory60 stream60"],
    ),
    (
        ("agent60 angle60 universe60 memory60 stream60 context60", 6),
        ["agent60", "angle60", "universe60", "memory60", "stream60", "context60"],
    ),
    (
        ("agent60 angle60 universe60 memory60 stream60 context60", 10),
        ["agent60", "angle60", "universe60", "memory60", "stream60", "context60"],
    ),
    (
        ("agent60 angle60 universe60 memory60 stream60 context60", 18),
        ["agent60 angle60", "universe60", "memory60 stream60", "context60"],
    ),
    (
        ("agent60 angle60 universe60 memory60 stream60 context60", 28),
        ["agent60 angle60 universe60", "memory60 stream60 context60"],
    ),
    (
        ("angle60 universe60 memory60 stream60 context60 knowledge60", 6),
        ["angle60", "universe60", "memory60", "stream60", "context60", "knowledge60"],
    ),
    (
        ("angle60 universe60 memory60 stream60 context60 knowledge60", 10),
        ["angle60", "universe60", "memory60", "stream60", "context60", "knowledge60"],
    ),
    (
        ("angle60 universe60 memory60 stream60 context60 knowledge60", 18),
        ["angle60 universe60", "memory60 stream60", "context60", "knowledge60"],
    ),
    (
        ("angle60 universe60 memory60 stream60 context60 knowledge60", 28),
        ["angle60 universe60 memory60", "stream60 context60", "knowledge60"],
    ),
    (
        ("universe60 memory60 stream60 context60 knowledge60 vector60", 6),
        ["universe60", "memory60", "stream60", "context60", "knowledge60", "vector60"],
    ),
    (
        ("universe60 memory60 stream60 context60 knowledge60 vector60", 10),
        ["universe60", "memory60", "stream60", "context60", "knowledge60", "vector60"],
    ),
    (
        ("universe60 memory60 stream60 context60 knowledge60 vector60", 18),
        ["universe60", "memory60 stream60", "context60", "knowledge60", "vector60"],
    ),
    (
        ("universe60 memory60 stream60 context60 knowledge60 vector60", 28),
        ["universe60 memory60 stream60", "context60 knowledge60", "vector60"],
    ),
    (
        ("memory60 stream60 context60 knowledge60 vector60 processor60", 6),
        ["memory60", "stream60", "context60", "knowledge60", "vector60", "processor60"],
    ),
    (
        ("memory60 stream60 context60 knowledge60 vector60 processor60", 10),
        ["memory60", "stream60", "context60", "knowledge60", "vector60", "processor60"],
    ),
    (
        ("memory60 stream60 context60 knowledge60 vector60 processor60", 18),
        ["memory60 stream60", "context60", "knowledge60", "vector60", "processor60"],
    ),
    (
        ("memory60 stream60 context60 knowledge60 vector60 processor60", 28),
        ["memory60 stream60 context60", "knowledge60 vector60", "processor60"],
    ),
    (
        ("stream60 context60 knowledge60 vector60 processor60 reasoning60", 6),
        ["stream60", "context60", "knowledge60", "vector60", "processor60", "reasoning60"],
    ),
    (
        ("stream60 context60 knowledge60 vector60 processor60 reasoning60", 10),
        ["stream60", "context60", "knowledge60", "vector60", "processor60", "reasoning60"],
    ),
    (
        ("stream60 context60 knowledge60 vector60 processor60 reasoning60", 18),
        ["stream60 context60", "knowledge60", "vector60", "processor60", "reasoning60"],
    ),
    (
        ("stream60 context60 knowledge60 vector60 processor60 reasoning60", 28),
        ["stream60 context60", "knowledge60 vector60", "processor60 reasoning60"],
    ),
    (
        ("context60 knowledge60 vector60 processor60 reasoning60 machine60", 6),
        ["context60", "knowledge60", "vector60", "processor60", "reasoning60", "machine60"],
    ),
    (
        ("context60 knowledge60 vector60 processor60 reasoning60 machine60", 10),
        ["context60", "knowledge60", "vector60", "processor60", "reasoning60", "machine60"],
    ),
    (
        ("context60 knowledge60 vector60 processor60 reasoning60 machine60", 18),
        ["context60", "knowledge60", "vector60", "processor60", "reasoning60", "machine60"],
    ),
    (
        ("context60 knowledge60 vector60 processor60 reasoning60 machine60", 28),
        ["context60 knowledge60", "vector60 processor60", "reasoning60 machine60"],
    ),
    (
        ("knowledge60 vector60 processor60 reasoning60 machine60 learning60", 6),
        ["knowledge60", "vector60", "processor60", "reasoning60", "machine60", "learning60"],
    ),
    (
        ("knowledge60 vector60 processor60 reasoning60 machine60 learning60", 10),
        ["knowledge60", "vector60", "processor60", "reasoning60", "machine60", "learning60"],
    ),
    (
        ("knowledge60 vector60 processor60 reasoning60 machine60 learning60", 18),
        ["knowledge60", "vector60", "processor60", "reasoning60", "machine60", "learning60"],
    ),
    (
        ("knowledge60 vector60 processor60 reasoning60 machine60 learning60", 28),
        ["knowledge60 vector60", "processor60 reasoning60", "machine60 learning60"],
    ),
    (
        ("vector60 processor60 reasoning60 machine60 learning60 model60", 6),
        ["vector60", "processor60", "reasoning60", "machine60", "learning60", "model60"],
    ),
    (
        ("vector60 processor60 reasoning60 machine60 learning60 model60", 10),
        ["vector60", "processor60", "reasoning60", "machine60", "learning60", "model60"],
    ),
    (
        ("vector60 processor60 reasoning60 machine60 learning60 model60", 18),
        ["vector60", "processor60", "reasoning60", "machine60", "learning60 model60"],
    ),
    (
        ("vector60 processor60 reasoning60 machine60 learning60 model60", 28),
        ["vector60 processor60", "reasoning60 machine60", "learning60 model60"],
    ),
    (
        ("processor60 reasoning60 machine60 learning60 model60 token60", 6),
        ["processor60", "reasoning60", "machine60", "learning60", "model60", "token60"],
    ),
    (
        ("processor60 reasoning60 machine60 learning60 model60 token60", 10),
        ["processor60", "reasoning60", "machine60", "learning60", "model60", "token60"],
    ),
    (
        ("processor60 reasoning60 machine60 learning60 model60 token60", 18),
        ["processor60", "reasoning60", "machine60", "learning60 model60", "token60"],
    ),
    (
        ("processor60 reasoning60 machine60 learning60 model60 token60", 28),
        ["processor60 reasoning60", "machine60 learning60 model60", "token60"],
    ),
    (
        ("reasoning60 machine60 learning60 model60 token60 prompt60", 6),
        ["reasoning60", "machine60", "learning60", "model60", "token60", "prompt60"],
    ),
    (
        ("reasoning60 machine60 learning60 model60 token60 prompt60", 10),
        ["reasoning60", "machine60", "learning60", "model60", "token60", "prompt60"],
    ),
    (
        ("reasoning60 machine60 learning60 model60 token60 prompt60", 18),
        ["reasoning60", "machine60", "learning60 model60", "token60 prompt60"],
    ),
    (
        ("reasoning60 machine60 learning60 model60 token60 prompt60", 28),
        ["reasoning60 machine60", "learning60 model60 token60", "prompt60"],
    ),
    (
        ("machine60 learning60 model60 token60 prompt60 session60", 6),
        ["machine60", "learning60", "model60", "token60", "prompt60", "session60"],
    ),
    (
        ("machine60 learning60 model60 token60 prompt60 session60", 10),
        ["machine60", "learning60", "model60", "token60", "prompt60", "session60"],
    ),
    (
        ("machine60 learning60 model60 token60 prompt60 session60", 18),
        ["machine60", "learning60 model60", "token60 prompt60", "session60"],
    ),
    (
        ("machine60 learning60 model60 token60 prompt60 session60", 28),
        ["machine60 learning60 model60", "token60 prompt60 session60"],
    ),
    (
        ("learning60 model60 token60 prompt60 session60 library60", 6),
        ["learning60", "model60", "token60", "prompt60", "session60", "library60"],
    ),
    (
        ("learning60 model60 token60 prompt60 session60 library60", 10),
        ["learning60", "model60", "token60", "prompt60", "session60", "library60"],
    ),
    (
        ("learning60 model60 token60 prompt60 session60 library60", 18),
        ["learning60 model60", "token60 prompt60", "session60", "library60"],
    ),
    (
        ("learning60 model60 token60 prompt60 session60 library60", 28),
        ["learning60 model60 token60", "prompt60 session60 library60"],
    ),
    (
        ("model60 token60 prompt60 session60 library60 service60", 6),
        ["model60", "token60", "prompt60", "session60", "library60", "service60"],
    ),
    (
        ("model60 token60 prompt60 session60 library60 service60", 10),
        ["model60", "token60", "prompt60", "session60", "library60", "service60"],
    ),
    (
        ("model60 token60 prompt60 session60 library60 service60", 18),
        ["model60 token60", "prompt60 session60", "library60", "service60"],
    ),
    (
        ("model60 token60 prompt60 session60 library60 service60", 28),
        ["model60 token60 prompt60", "session60 library60", "service60"],
    ),
    (
        ("token60 prompt60 session60 library60 service60 gateway60", 6),
        ["token60", "prompt60", "session60", "library60", "service60", "gateway60"],
    ),
    (
        ("token60 prompt60 session60 library60 service60 gateway60", 10),
        ["token60", "prompt60", "session60", "library60", "service60", "gateway60"],
    ),
    (
        ("token60 prompt60 session60 library60 service60 gateway60", 18),
        ["token60 prompt60", "session60", "library60", "service60", "gateway60"],
    ),
    (
        ("token60 prompt60 session60 library60 service60 gateway60", 28),
        ["token60 prompt60 session60", "library60 service60", "gateway60"],
    ),
    (
        ("prompt60 session60 library60 service60 gateway60 storage60", 6),
        ["prompt60", "session60", "library60", "service60", "gateway60", "storage60"],
    ),
    (
        ("prompt60 session60 library60 service60 gateway60 storage60", 10),
        ["prompt60", "session60", "library60", "service60", "gateway60", "storage60"],
    ),
    (
        ("prompt60 session60 library60 service60 gateway60 storage60", 18),
        ["prompt60 session60", "library60", "service60", "gateway60", "storage60"],
    ),
    (
        ("prompt60 session60 library60 service60 gateway60 storage60", 28),
        ["prompt60 session60 library60", "service60 gateway60", "storage60"],
    ),
    (
        ("session60 library60 service60 gateway60 storage60 network60", 6),
        ["session60", "library60", "service60", "gateway60", "storage60", "network60"],
    ),
    (
        ("session60 library60 service60 gateway60 storage60 network60", 10),
        ["session60", "library60", "service60", "gateway60", "storage60", "network60"],
    ),
    (
        ("session60 library60 service60 gateway60 storage60 network60", 18),
        ["session60", "library60", "service60", "gateway60", "storage60", "network60"],
    ),
    (
        ("session60 library60 service60 gateway60 storage60 network60", 28),
        ["session60 library60", "service60 gateway60", "storage60 network60"],
    ),
    (
        ("library60 service60 gateway60 storage60 network60 latency60", 6),
        ["library60", "service60", "gateway60", "storage60", "network60", "latency60"],
    ),
    (
        ("library60 service60 gateway60 storage60 network60 latency60", 10),
        ["library60", "service60", "gateway60", "storage60", "network60", "latency60"],
    ),
    (
        ("library60 service60 gateway60 storage60 network60 latency60", 18),
        ["library60", "service60", "gateway60", "storage60", "network60", "latency60"],
    ),
    (
        ("library60 service60 gateway60 storage60 network60 latency60", 28),
        ["library60 service60", "gateway60 storage60", "network60 latency60"],
    ),
    (
        ("service60 gateway60 storage60 network60 latency60 buffer60", 6),
        ["service60", "gateway60", "storage60", "network60", "latency60", "buffer60"],
    ),
    (
        ("service60 gateway60 storage60 network60 latency60 buffer60", 10),
        ["service60", "gateway60", "storage60", "network60", "latency60", "buffer60"],
    ),
    (
        ("service60 gateway60 storage60 network60 latency60 buffer60", 18),
        ["service60", "gateway60", "storage60", "network60", "latency60 buffer60"],
    ),
    (
        ("service60 gateway60 storage60 network60 latency60 buffer60", 28),
        ["service60 gateway60", "storage60 network60", "latency60 buffer60"],
    ),
    (
        ("gateway60 storage60 network60 latency60 buffer60 queue60", 6),
        ["gateway60", "storage60", "network60", "latency60", "buffer60", "queue60"],
    ),
    (
        ("gateway60 storage60 network60 latency60 buffer60 queue60", 10),
        ["gateway60", "storage60", "network60", "latency60", "buffer60", "queue60"],
    ),
    (
        ("gateway60 storage60 network60 latency60 buffer60 queue60", 18),
        ["gateway60", "storage60", "network60", "latency60 buffer60", "queue60"],
    ),
    (
        ("gateway60 storage60 network60 latency60 buffer60 queue60", 28),
        ["gateway60 storage60", "network60 latency60 buffer60", "queue60"],
    ),
    (
        ("storage60 network60 latency60 buffer60 queue60 worker60", 6),
        ["storage60", "network60", "latency60", "buffer60", "queue60", "worker60"],
    ),
    (
        ("storage60 network60 latency60 buffer60 queue60 worker60", 10),
        ["storage60", "network60", "latency60", "buffer60", "queue60", "worker60"],
    ),
    (
        ("storage60 network60 latency60 buffer60 queue60 worker60", 18),
        ["storage60", "network60", "latency60 buffer60", "queue60 worker60"],
    ),
    (
        ("storage60 network60 latency60 buffer60 queue60 worker60", 28),
        ["storage60 network60", "latency60 buffer60 queue60", "worker60"],
    ),
    (
        ("network60 latency60 buffer60 queue60 worker60 kernel60", 6),
        ["network60", "latency60", "buffer60", "queue60", "worker60", "kernel60"],
    ),
    (
        ("network60 latency60 buffer60 queue60 worker60 kernel60", 10),
        ["network60", "latency60", "buffer60", "queue60", "worker60", "kernel60"],
    ),
    (
        ("network60 latency60 buffer60 queue60 worker60 kernel60", 18),
        ["network60", "latency60 buffer60", "queue60 worker60", "kernel60"],
    ),
    (
        ("network60 latency60 buffer60 queue60 worker60 kernel60", 28),
        ["network60 latency60 buffer60", "queue60 worker60 kernel60"],
    ),
    (
        ("latency60 buffer60 queue60 worker60 kernel60 signal60", 6),
        ["latency60", "buffer60", "queue60", "worker60", "kernel60", "signal60"],
    ),
    (
        ("latency60 buffer60 queue60 worker60 kernel60 signal60", 10),
        ["latency60", "buffer60", "queue60", "worker60", "kernel60", "signal60"],
    ),
    (
        ("latency60 buffer60 queue60 worker60 kernel60 signal60", 18),
        ["latency60 buffer60", "queue60 worker60", "kernel60 signal60"],
    ),
    (
        ("latency60 buffer60 queue60 worker60 kernel60 signal60", 28),
        ["latency60 buffer60 queue60", "worker60 kernel60 signal60"],
    ),
    (
        ("buffer60 queue60 worker60 kernel60 signal60 packet60", 6),
        ["buffer60", "queue60", "worker60", "kernel60", "signal60", "packet60"],
    ),
    (
        ("buffer60 queue60 worker60 kernel60 signal60 packet60", 10),
        ["buffer60", "queue60", "worker60", "kernel60", "signal60", "packet60"],
    ),
    (
        ("buffer60 queue60 worker60 kernel60 signal60 packet60", 18),
        ["buffer60 queue60", "worker60 kernel60", "signal60 packet60"],
    ),
    (
        ("buffer60 queue60 worker60 kernel60 signal60 packet60", 28),
        ["buffer60 queue60 worker60", "kernel60 signal60 packet60"],
    ),
    (
        ("queue60 worker60 kernel60 signal60 packet60 router60", 6),
        ["queue60", "worker60", "kernel60", "signal60", "packet60", "router60"],
    ),
    (
        ("queue60 worker60 kernel60 signal60 packet60 router60", 10),
        ["queue60", "worker60", "kernel60", "signal60", "packet60", "router60"],
    ),
    (
        ("queue60 worker60 kernel60 signal60 packet60 router60", 18),
        ["queue60 worker60", "kernel60 signal60", "packet60 router60"],
    ),
    (
        ("queue60 worker60 kernel60 signal60 packet60 router60", 28),
        ["queue60 worker60 kernel60", "signal60 packet60 router60"],
    ),
    (
        ("worker60 kernel60 signal60 packet60 router60 cluster60", 6),
        ["worker60", "kernel60", "signal60", "packet60", "router60", "cluster60"],
    ),
    (
        ("worker60 kernel60 signal60 packet60 router60 cluster60", 10),
        ["worker60", "kernel60", "signal60", "packet60", "router60", "cluster60"],
    ),
    (
        ("worker60 kernel60 signal60 packet60 router60 cluster60", 18),
        ["worker60 kernel60", "signal60 packet60", "router60 cluster60"],
    ),
    (
        ("worker60 kernel60 signal60 packet60 router60 cluster60", 28),
        ["worker60 kernel60 signal60", "packet60 router60 cluster60"],
    ),
    (
        ("kernel60 signal60 packet60 router60 cluster60 mirror60", 6),
        ["kernel60", "signal60", "packet60", "router60", "cluster60", "mirror60"],
    ),
    (
        ("kernel60 signal60 packet60 router60 cluster60 mirror60", 10),
        ["kernel60", "signal60", "packet60", "router60", "cluster60", "mirror60"],
    ),
    (
        ("kernel60 signal60 packet60 router60 cluster60 mirror60", 18),
        ["kernel60 signal60", "packet60 router60", "cluster60 mirror60"],
    ),
    (
        ("kernel60 signal60 packet60 router60 cluster60 mirror60", 28),
        ["kernel60 signal60 packet60", "router60 cluster60 mirror60"],
    ),
    (
        ("signal60 packet60 router60 cluster60 mirror60 filter60", 6),
        ["signal60", "packet60", "router60", "cluster60", "mirror60", "filter60"],
    ),
    (
        ("signal60 packet60 router60 cluster60 mirror60 filter60", 10),
        ["signal60", "packet60", "router60", "cluster60", "mirror60", "filter60"],
    ),
    (
        ("signal60 packet60 router60 cluster60 mirror60 filter60", 18),
        ["signal60 packet60", "router60 cluster60", "mirror60 filter60"],
    ),
    (
        ("signal60 packet60 router60 cluster60 mirror60 filter60", 28),
        ["signal60 packet60 router60", "cluster60 mirror60 filter60"],
    ),
    (
        ("packet60 router60 cluster60 mirror60 filter60 ranking60", 6),
        ["packet60", "router60", "cluster60", "mirror60", "filter60", "ranking60"],
    ),
    (
        ("packet60 router60 cluster60 mirror60 filter60 ranking60", 10),
        ["packet60", "router60", "cluster60", "mirror60", "filter60", "ranking60"],
    ),
    (
        ("packet60 router60 cluster60 mirror60 filter60 ranking60", 18),
        ["packet60 router60", "cluster60 mirror60", "filter60 ranking60"],
    ),
    (
        ("packet60 router60 cluster60 mirror60 filter60 ranking60", 28),
        ["packet60 router60 cluster60", "mirror60 filter60 ranking60"],
    ),
    (
        ("router60 cluster60 mirror60 filter60 ranking60 encoding60", 6),
        ["router60", "cluster60", "mirror60", "filter60", "ranking60", "encoding60"],
    ),
    (
        ("router60 cluster60 mirror60 filter60 ranking60 encoding60", 10),
        ["router60", "cluster60", "mirror60", "filter60", "ranking60", "encoding60"],
    ),
    (
        ("router60 cluster60 mirror60 filter60 ranking60 encoding60", 18),
        ["router60 cluster60", "mirror60 filter60", "ranking60", "encoding60"],
    ),
    (
        ("router60 cluster60 mirror60 filter60 ranking60 encoding60", 28),
        ["router60 cluster60 mirror60", "filter60 ranking60", "encoding60"],
    ),
    (
        ("cluster60 mirror60 filter60 ranking60 encoding60 mapping60", 6),
        ["cluster60", "mirror60", "filter60", "ranking60", "encoding60", "mapping60"],
    ),
    (
        ("cluster60 mirror60 filter60 ranking60 encoding60 mapping60", 10),
        ["cluster60", "mirror60", "filter60", "ranking60", "encoding60", "mapping60"],
    ),
    (
        ("cluster60 mirror60 filter60 ranking60 encoding60 mapping60", 18),
        ["cluster60 mirror60", "filter60 ranking60", "encoding60", "mapping60"],
    ),
    (
        ("cluster60 mirror60 filter60 ranking60 encoding60 mapping60", 28),
        ["cluster60 mirror60 filter60", "ranking60 encoding60", "mapping60"],
    ),
    (
        ("mirror60 filter60 ranking60 encoding60 mapping60 record60", 6),
        ["mirror60", "filter60", "ranking60", "encoding60", "mapping60", "record60"],
    ),
    (
        ("mirror60 filter60 ranking60 encoding60 mapping60 record60", 10),
        ["mirror60", "filter60", "ranking60", "encoding60", "mapping60", "record60"],
    ),
    (
        ("mirror60 filter60 ranking60 encoding60 mapping60 record60", 18),
        ["mirror60 filter60", "ranking60", "encoding60", "mapping60 record60"],
    ),
    (
        ("mirror60 filter60 ranking60 encoding60 mapping60 record60", 28),
        ["mirror60 filter60 ranking60", "encoding60 mapping60", "record60"],
    ),
    (
        ("filter60 ranking60 encoding60 mapping60 record60 candle60", 6),
        ["filter60", "ranking60", "encoding60", "mapping60", "record60", "candle60"],
    ),
    (
        ("filter60 ranking60 encoding60 mapping60 record60 candle60", 10),
        ["filter60", "ranking60", "encoding60", "mapping60", "record60", "candle60"],
    ),
    (
        ("filter60 ranking60 encoding60 mapping60 record60 candle60", 18),
        ["filter60 ranking60", "encoding60", "mapping60 record60", "candle60"],
    ),
    (
        ("filter60 ranking60 encoding60 mapping60 record60 candle60", 28),
        ["filter60 ranking60", "encoding60 mapping60", "record60 candle60"],
    ),
    (
        ("ranking60 encoding60 mapping60 record60 candle60 thread60", 6),
        ["ranking60", "encoding60", "mapping60", "record60", "candle60", "thread60"],
    ),
    (
        ("ranking60 encoding60 mapping60 record60 candle60 thread60", 10),
        ["ranking60", "encoding60", "mapping60", "record60", "candle60", "thread60"],
    ),
    (
        ("ranking60 encoding60 mapping60 record60 candle60 thread60", 18),
        ["ranking60", "encoding60", "mapping60 record60", "candle60 thread60"],
    ),
    (
        ("ranking60 encoding60 mapping60 record60 candle60 thread60", 28),
        ["ranking60 encoding60", "mapping60 record60 candle60", "thread60"],
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
