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
        ("round 144: the quick brown fox jumps over the lazy dog", 4),
        ["round", "144:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", 8),
        ["round", "144: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", 12),
        ["round 144:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", 16),
        ["round 144: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", 24),
        ["round 144: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 144: the quick brown fox jumps over the lazy dog", 32),
        ["round 144: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", 4),
        ["round", "144:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", 8),
        ["round", "144:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", 12),
        ["round 144:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", 16),
        ["round 144:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", 24),
        ["round 144: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 144: agentuniverse is a framework for multi agents", 32),
        ["round 144: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", 4),
        ["round", "144:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", 8),
        ["round", "144:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", 12),
        ["round 144:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", 16),
        ["round 144:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", 24),
        ["round 144: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 144: knowledge stored as vectors enables retrieval", 32),
        ["round 144: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 144: the processor reads the record then stops", 4),
        ["round", "144:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 144: the processor reads the record then stops", 8),
        ["round", "144: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 144: the processor reads the record then stops", 12),
        ["round 144:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 144: the processor reads the record then stops", 16),
        ["round 144: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 144: the processor reads the record then stops", 24),
        ["round 144: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 144: the processor reads the record then stops", 32),
        ["round 144: the processor reads", "the record then stops"],
    ),
    (
        ("round 144: a worker pulls the next task from the queue", 4),
        ["round", "144:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 144: a worker pulls the next task from the queue", 8),
        ["round", "144: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 144: a worker pulls the next task from the queue", 12),
        ["round 144: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 144: a worker pulls the next task from the queue", 16),
        ["round 144: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 144: a worker pulls the next task from the queue", 24),
        ["round 144: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 144: a worker pulls the next task from the queue", 32),
        ["round 144: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 144: signals travel through the network layer", 4),
        ["round", "144:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 144: signals travel through the network layer", 8),
        ["round", "144:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 144: signals travel through the network layer", 12),
        ["round 144:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 144: signals travel through the network layer", 16),
        ["round 144:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 144: signals travel through the network layer", 24),
        ["round 144: signals", "travel through the", "network layer"],
    ),
    (
        ("round 144: signals travel through the network layer", 32),
        ["round 144: signals travel", "through the network layer"],
    ),
    (
        ("round 144: the gateway routes each request by policy", 4),
        ["round", "144:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 144: the gateway routes each request by policy", 8),
        ["round", "144: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 144: the gateway routes each request by policy", 12),
        ["round 144:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 144: the gateway routes each request by policy", 16),
        ["round 144: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 144: the gateway routes each request by policy", 24),
        ["round 144: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 144: the gateway routes each request by policy", 32),
        ["round 144: the gateway routes", "each request by policy"],
    ),
    (
        ("round 144: memory grows until the buffer is full", 4),
        ["round", "144:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 144: memory grows until the buffer is full", 8),
        ["round", "144:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 144: memory grows until the buffer is full", 12),
        ["round 144:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 144: memory grows until the buffer is full", 16),
        ["round 144:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 144: memory grows until the buffer is full", 24), ["round 144: memory grows", "until the buffer is full"]),
    (("round 144: memory grows until the buffer is full", 32), ["round 144: memory grows until", "the buffer is full"]),
    (
        ("round 144: the cluster mirrors every packet twice", 4),
        ["round", "144:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 144: the cluster mirrors every packet twice", 8),
        ["round", "144: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 144: the cluster mirrors every packet twice", 12),
        ["round 144:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 144: the cluster mirrors every packet twice", 16),
        ["round 144: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 144: the cluster mirrors every packet twice", 24),
        ["round 144: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 144: the cluster mirrors every packet twice", 32),
        ["round 144: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", 4),
        ["round", "144:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", 8),
        ["round", "144:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", 12),
        ["round 144:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", 16),
        ["round 144:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", 24),
        ["round 144: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 144: ranking uses tokens learned from the corpus", 32),
        ["round 144: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 144: a long session ends when the candle dies", 4),
        ["round", "144:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 144: a long session ends when the candle dies", 8),
        ["round", "144: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 144: a long session ends when the candle dies", 12),
        ["round 144: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 144: a long session ends when the candle dies", 16),
        ["round 144: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 144: a long session ends when the candle dies", 24),
        ["round 144: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 144: a long session ends when the candle dies", 32),
        ["round 144: a long session ends", "when the candle dies"],
    ),
    (
        ("round 144: encode the prompt then map the result", 4),
        ["round", "144:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 144: encode the prompt then map the result", 8),
        ["round", "144:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 144: encode the prompt then map the result", 12),
        ["round 144:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 144: encode the prompt then map the result", 16),
        ["round 144:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 144: encode the prompt then map the result", 24),
        ["round 144: encode the", "prompt then map the", "result"],
    ),
    (("round 144: encode the prompt then map the result", 32), ["round 144: encode the prompt", "then map the result"]),
    (
        ("round 144: the kernel wakes the worker at dawn", 4),
        ["round", "144:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 144: the kernel wakes the worker at dawn", 8),
        ["round", "144: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 144: the kernel wakes the worker at dawn", 12),
        ["round 144:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 144: the kernel wakes the worker at dawn", 16), ["round 144: the", "kernel wakes the", "worker at dawn"]),
    (("round 144: the kernel wakes the worker at dawn", 24), ["round 144: the kernel", "wakes the worker at dawn"]),
    (("round 144: the kernel wakes the worker at dawn", 32), ["round 144: the kernel wakes the", "worker at dawn"]),
    (
        ("round 144: service latency drops after the patch", 4),
        ["round", "144:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 144: service latency drops after the patch", 8),
        ["round", "144:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 144: service latency drops after the patch", 12),
        ["round 144:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 144: service latency drops after the patch", 16),
        ["round 144:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 144: service latency drops after the patch", 24),
        ["round 144: service", "latency drops after the", "patch"],
    ),
    (("round 144: service latency drops after the patch", 32), ["round 144: service latency drops", "after the patch"]),
    (
        ("round 144: the library caches every vector it sees", 4),
        ["round", "144:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 144: the library caches every vector it sees", 8),
        ["round", "144: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 144: the library caches every vector it sees", 12),
        ["round 144:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 144: the library caches every vector it sees", 16),
        ["round 144: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 144: the library caches every vector it sees", 24),
        ["round 144: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 144: the library caches every vector it sees", 32),
        ["round 144: the library caches", "every vector it sees"],
    ),
    (
        ("round 144: agents argue then the debate resolves", 4),
        ["round", "144:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 144: agents argue then the debate resolves", 8),
        ["round", "144:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 144: agents argue then the debate resolves", 12),
        ["round 144:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 144: agents argue then the debate resolves", 16),
        ["round 144:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 144: agents argue then the debate resolves", 24), ["round 144: agents argue", "then the debate resolves"]),
    (("round 144: agents argue then the debate resolves", 32), ["round 144: agents argue then the", "debate resolves"]),
    (
        ("round 144: the filter keeps only strong matches", 4),
        ["round", "144:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 144: the filter keeps only strong matches", 8),
        ["round", "144: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 144: the filter keeps only strong matches", 12),
        ["round 144:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 144: the filter keeps only strong matches", 16),
        ["round 144: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 144: the filter keeps only strong matches", 24),
        ["round 144: the filter", "keeps only strong", "matches"],
    ),
    (("round 144: the filter keeps only strong matches", 32), ["round 144: the filter keeps only", "strong matches"]),
    (
        ("round 144: the model answers with a short reply", 4),
        ["round", "144:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 144: the model answers with a short reply", 8),
        ["round", "144: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 144: the model answers with a short reply", 12),
        ["round 144:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 144: the model answers with a short reply", 16),
        ["round 144: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 144: the model answers with a short reply", 24),
        ["round 144: the model", "answers with a short", "reply"],
    ),
    (("round 144: the model answers with a short reply", 32), ["round 144: the model answers", "with a short reply"]),
    (
        ("round 144: the recorder stores the reasoning trace", 4),
        ["round", "144:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 144: the recorder stores the reasoning trace", 8),
        ["round", "144: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 144: the recorder stores the reasoning trace", 12),
        ["round 144:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 144: the recorder stores the reasoning trace", 16),
        ["round 144: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 144: the recorder stores the reasoning trace", 24),
        ["round 144: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 144: the recorder stores the reasoning trace", 32),
        ["round 144: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 144: the angel watches the processor run", 4),
        ["round", "144:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 144: the angel watches the processor run", 8),
        ["round", "144: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 144: the angel watches the processor run", 12),
        ["round 144:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 144: the angel watches the processor run", 16),
        ["round 144: the", "angel watches", "the processor", "run"],
    ),
    (("round 144: the angel watches the processor run", 24), ["round 144: the angel", "watches the processor", "run"]),
    (("round 144: the angel watches the processor run", 32), ["round 144: the angel watches the", "processor run"]),
    (
        ("round 144: angle of the vector decides the match", 4),
        ["round", "144:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 144: angle of the vector decides the match", 8),
        ["round", "144:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 144: angle of the vector decides the match", 12),
        ["round 144:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 144: angle of the vector decides the match", 16),
        ["round 144: angle", "of the vector", "decides the", "match"],
    ),
    (("round 144: angle of the vector decides the match", 24), ["round 144: angle of the", "vector decides the match"]),
    (("round 144: angle of the vector decides the match", 32), ["round 144: angle of the vector", "decides the match"]),
    (
        ("round 144: the candle burns twice as long at night", 4),
        ["round", "144:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 144: the candle burns twice as long at night", 8),
        ["round", "144: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 144: the candle burns twice as long at night", 12),
        ["round 144:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 144: the candle burns twice as long at night", 16),
        ["round 144: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 144: the candle burns twice as long at night", 24),
        ["round 144: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 144: the candle burns twice as long at night", 32),
        ["round 144: the candle burns", "twice as long at night"],
    ),
    (
        ("round 144: a mirror of the universe in one line", 4),
        ["round", "144:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 144: a mirror of the universe in one line", 8),
        ["round", "144: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 144: a mirror of the universe in one line", 12),
        ["round 144: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 144: a mirror of the universe in one line", 16),
        ["round 144: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 144: a mirror of the universe in one line", 24), ["round 144: a mirror of", "the universe in one line"]),
    (("round 144: a mirror of the universe in one line", 32), ["round 144: a mirror of the", "universe in one line"]),
    (
        ("round 144: the queue drains before the storm", 4),
        ["round", "144:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 144: the queue drains before the storm", 8),
        ["round", "144: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 144: the queue drains before the storm", 12),
        ["round 144:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 144: the queue drains before the storm", 16), ["round 144: the", "queue drains", "before the storm"]),
    (("round 144: the queue drains before the storm", 24), ["round 144: the queue", "drains before the storm"]),
    (("round 144: the queue drains before the storm", 32), ["round 144: the queue drains", "before the storm"]),
    (
        ("kitten144 sitting144 agent144 angle144 universe144 memory144", 6),
        ["kitten144", "sitting144", "agent144", "angle144", "universe144", "memory144"],
    ),
    (
        ("kitten144 sitting144 agent144 angle144 universe144 memory144", 10),
        ["kitten144", "sitting144", "agent144", "angle144", "universe144", "memory144"],
    ),
    (
        ("kitten144 sitting144 agent144 angle144 universe144 memory144", 18),
        ["kitten144", "sitting144", "agent144 angle144", "universe144", "memory144"],
    ),
    (
        ("kitten144 sitting144 agent144 angle144 universe144 memory144", 28),
        ["kitten144 sitting144", "agent144 angle144", "universe144 memory144"],
    ),
    (
        ("sitting144 agent144 angle144 universe144 memory144 stream144", 6),
        ["sitting144", "agent144", "angle144", "universe144", "memory144", "stream144"],
    ),
    (
        ("sitting144 agent144 angle144 universe144 memory144 stream144", 10),
        ["sitting144", "agent144", "angle144", "universe144", "memory144", "stream144"],
    ),
    (
        ("sitting144 agent144 angle144 universe144 memory144 stream144", 18),
        ["sitting144", "agent144 angle144", "universe144", "memory144", "stream144"],
    ),
    (
        ("sitting144 agent144 angle144 universe144 memory144 stream144", 28),
        ["sitting144 agent144 angle144", "universe144 memory144", "stream144"],
    ),
    (
        ("agent144 angle144 universe144 memory144 stream144 context144", 6),
        ["agent144", "angle144", "universe144", "memory144", "stream144", "context144"],
    ),
    (
        ("agent144 angle144 universe144 memory144 stream144 context144", 10),
        ["agent144", "angle144", "universe144", "memory144", "stream144", "context144"],
    ),
    (
        ("agent144 angle144 universe144 memory144 stream144 context144", 18),
        ["agent144 angle144", "universe144", "memory144", "stream144", "context144"],
    ),
    (
        ("agent144 angle144 universe144 memory144 stream144 context144", 28),
        ["agent144 angle144", "universe144 memory144", "stream144 context144"],
    ),
    (
        ("angle144 universe144 memory144 stream144 context144 knowledge144", 6),
        ["angle144", "universe144", "memory144", "stream144", "context144", "knowledge144"],
    ),
    (
        ("angle144 universe144 memory144 stream144 context144 knowledge144", 10),
        ["angle144", "universe144", "memory144", "stream144", "context144", "knowledge144"],
    ),
    (
        ("angle144 universe144 memory144 stream144 context144 knowledge144", 18),
        ["angle144", "universe144", "memory144", "stream144", "context144", "knowledge144"],
    ),
    (
        ("angle144 universe144 memory144 stream144 context144 knowledge144", 28),
        ["angle144 universe144", "memory144 stream144", "context144 knowledge144"],
    ),
    (
        ("universe144 memory144 stream144 context144 knowledge144 vector144", 6),
        ["universe144", "memory144", "stream144", "context144", "knowledge144", "vector144"],
    ),
    (
        ("universe144 memory144 stream144 context144 knowledge144 vector144", 10),
        ["universe144", "memory144", "stream144", "context144", "knowledge144", "vector144"],
    ),
    (
        ("universe144 memory144 stream144 context144 knowledge144 vector144", 18),
        ["universe144", "memory144", "stream144", "context144", "knowledge144", "vector144"],
    ),
    (
        ("universe144 memory144 stream144 context144 knowledge144 vector144", 28),
        ["universe144 memory144", "stream144 context144", "knowledge144 vector144"],
    ),
    (
        ("memory144 stream144 context144 knowledge144 vector144 processor144", 6),
        ["memory144", "stream144", "context144", "knowledge144", "vector144", "processor144"],
    ),
    (
        ("memory144 stream144 context144 knowledge144 vector144 processor144", 10),
        ["memory144", "stream144", "context144", "knowledge144", "vector144", "processor144"],
    ),
    (
        ("memory144 stream144 context144 knowledge144 vector144 processor144", 18),
        ["memory144", "stream144", "context144", "knowledge144", "vector144", "processor144"],
    ),
    (
        ("memory144 stream144 context144 knowledge144 vector144 processor144", 28),
        ["memory144 stream144", "context144 knowledge144", "vector144 processor144"],
    ),
    (
        ("stream144 context144 knowledge144 vector144 processor144 reasoning144", 6),
        ["stream144", "context144", "knowledge144", "vector144", "processor144", "reasoning144"],
    ),
    (
        ("stream144 context144 knowledge144 vector144 processor144 reasoning144", 10),
        ["stream144", "context144", "knowledge144", "vector144", "processor144", "reasoning144"],
    ),
    (
        ("stream144 context144 knowledge144 vector144 processor144 reasoning144", 18),
        ["stream144", "context144", "knowledge144", "vector144", "processor144", "reasoning144"],
    ),
    (
        ("stream144 context144 knowledge144 vector144 processor144 reasoning144", 28),
        ["stream144 context144", "knowledge144 vector144", "processor144 reasoning144"],
    ),
    (
        ("context144 knowledge144 vector144 processor144 reasoning144 machine144", 6),
        ["context144", "knowledge144", "vector144", "processor144", "reasoning144", "machine144"],
    ),
    (
        ("context144 knowledge144 vector144 processor144 reasoning144 machine144", 10),
        ["context144", "knowledge144", "vector144", "processor144", "reasoning144", "machine144"],
    ),
    (
        ("context144 knowledge144 vector144 processor144 reasoning144 machine144", 18),
        ["context144", "knowledge144", "vector144", "processor144", "reasoning144", "machine144"],
    ),
    (
        ("context144 knowledge144 vector144 processor144 reasoning144 machine144", 28),
        ["context144 knowledge144", "vector144 processor144", "reasoning144 machine144"],
    ),
    (
        ("knowledge144 vector144 processor144 reasoning144 machine144 learning144", 6),
        ["knowledge144", "vector144", "processor144", "reasoning144", "machine144", "learning144"],
    ),
    (
        ("knowledge144 vector144 processor144 reasoning144 machine144 learning144", 10),
        ["knowledge144", "vector144", "processor144", "reasoning144", "machine144", "learning144"],
    ),
    (
        ("knowledge144 vector144 processor144 reasoning144 machine144 learning144", 18),
        ["knowledge144", "vector144", "processor144", "reasoning144", "machine144", "learning144"],
    ),
    (
        ("knowledge144 vector144 processor144 reasoning144 machine144 learning144", 28),
        ["knowledge144 vector144", "processor144 reasoning144", "machine144 learning144"],
    ),
    (
        ("vector144 processor144 reasoning144 machine144 learning144 model144", 6),
        ["vector144", "processor144", "reasoning144", "machine144", "learning144", "model144"],
    ),
    (
        ("vector144 processor144 reasoning144 machine144 learning144 model144", 10),
        ["vector144", "processor144", "reasoning144", "machine144", "learning144", "model144"],
    ),
    (
        ("vector144 processor144 reasoning144 machine144 learning144 model144", 18),
        ["vector144", "processor144", "reasoning144", "machine144", "learning144", "model144"],
    ),
    (
        ("vector144 processor144 reasoning144 machine144 learning144 model144", 28),
        ["vector144 processor144", "reasoning144 machine144", "learning144 model144"],
    ),
    (
        ("processor144 reasoning144 machine144 learning144 model144 token144", 6),
        ["processor144", "reasoning144", "machine144", "learning144", "model144", "token144"],
    ),
    (
        ("processor144 reasoning144 machine144 learning144 model144 token144", 10),
        ["processor144", "reasoning144", "machine144", "learning144", "model144", "token144"],
    ),
    (
        ("processor144 reasoning144 machine144 learning144 model144 token144", 18),
        ["processor144", "reasoning144", "machine144", "learning144", "model144 token144"],
    ),
    (
        ("processor144 reasoning144 machine144 learning144 model144 token144", 28),
        ["processor144 reasoning144", "machine144 learning144", "model144 token144"],
    ),
    (
        ("reasoning144 machine144 learning144 model144 token144 prompt144", 6),
        ["reasoning144", "machine144", "learning144", "model144", "token144", "prompt144"],
    ),
    (
        ("reasoning144 machine144 learning144 model144 token144 prompt144", 10),
        ["reasoning144", "machine144", "learning144", "model144", "token144", "prompt144"],
    ),
    (
        ("reasoning144 machine144 learning144 model144 token144 prompt144", 18),
        ["reasoning144", "machine144", "learning144", "model144 token144", "prompt144"],
    ),
    (
        ("reasoning144 machine144 learning144 model144 token144 prompt144", 28),
        ["reasoning144 machine144", "learning144 model144", "token144 prompt144"],
    ),
    (
        ("machine144 learning144 model144 token144 prompt144 session144", 6),
        ["machine144", "learning144", "model144", "token144", "prompt144", "session144"],
    ),
    (
        ("machine144 learning144 model144 token144 prompt144 session144", 10),
        ["machine144", "learning144", "model144", "token144", "prompt144", "session144"],
    ),
    (
        ("machine144 learning144 model144 token144 prompt144 session144", 18),
        ["machine144", "learning144", "model144 token144", "prompt144", "session144"],
    ),
    (
        ("machine144 learning144 model144 token144 prompt144 session144", 28),
        ["machine144 learning144", "model144 token144 prompt144", "session144"],
    ),
    (
        ("learning144 model144 token144 prompt144 session144 library144", 6),
        ["learning144", "model144", "token144", "prompt144", "session144", "library144"],
    ),
    (
        ("learning144 model144 token144 prompt144 session144 library144", 10),
        ["learning144", "model144", "token144", "prompt144", "session144", "library144"],
    ),
    (
        ("learning144 model144 token144 prompt144 session144 library144", 18),
        ["learning144", "model144 token144", "prompt144", "session144", "library144"],
    ),
    (
        ("learning144 model144 token144 prompt144 session144 library144", 28),
        ["learning144 model144", "token144 prompt144", "session144 library144"],
    ),
    (
        ("model144 token144 prompt144 session144 library144 service144", 6),
        ["model144", "token144", "prompt144", "session144", "library144", "service144"],
    ),
    (
        ("model144 token144 prompt144 session144 library144 service144", 10),
        ["model144", "token144", "prompt144", "session144", "library144", "service144"],
    ),
    (
        ("model144 token144 prompt144 session144 library144 service144", 18),
        ["model144 token144", "prompt144", "session144", "library144", "service144"],
    ),
    (
        ("model144 token144 prompt144 session144 library144 service144", 28),
        ["model144 token144 prompt144", "session144 library144", "service144"],
    ),
    (
        ("token144 prompt144 session144 library144 service144 gateway144", 6),
        ["token144", "prompt144", "session144", "library144", "service144", "gateway144"],
    ),
    (
        ("token144 prompt144 session144 library144 service144 gateway144", 10),
        ["token144", "prompt144", "session144", "library144", "service144", "gateway144"],
    ),
    (
        ("token144 prompt144 session144 library144 service144 gateway144", 18),
        ["token144 prompt144", "session144", "library144", "service144", "gateway144"],
    ),
    (
        ("token144 prompt144 session144 library144 service144 gateway144", 28),
        ["token144 prompt144", "session144 library144", "service144 gateway144"],
    ),
    (
        ("prompt144 session144 library144 service144 gateway144 storage144", 6),
        ["prompt144", "session144", "library144", "service144", "gateway144", "storage144"],
    ),
    (
        ("prompt144 session144 library144 service144 gateway144 storage144", 10),
        ["prompt144", "session144", "library144", "service144", "gateway144", "storage144"],
    ),
    (
        ("prompt144 session144 library144 service144 gateway144 storage144", 18),
        ["prompt144", "session144", "library144", "service144", "gateway144", "storage144"],
    ),
    (
        ("prompt144 session144 library144 service144 gateway144 storage144", 28),
        ["prompt144 session144", "library144 service144", "gateway144 storage144"],
    ),
    (
        ("session144 library144 service144 gateway144 storage144 network144", 6),
        ["session144", "library144", "service144", "gateway144", "storage144", "network144"],
    ),
    (
        ("session144 library144 service144 gateway144 storage144 network144", 10),
        ["session144", "library144", "service144", "gateway144", "storage144", "network144"],
    ),
    (
        ("session144 library144 service144 gateway144 storage144 network144", 18),
        ["session144", "library144", "service144", "gateway144", "storage144", "network144"],
    ),
    (
        ("session144 library144 service144 gateway144 storage144 network144", 28),
        ["session144 library144", "service144 gateway144", "storage144 network144"],
    ),
    (
        ("library144 service144 gateway144 storage144 network144 latency144", 6),
        ["library144", "service144", "gateway144", "storage144", "network144", "latency144"],
    ),
    (
        ("library144 service144 gateway144 storage144 network144 latency144", 10),
        ["library144", "service144", "gateway144", "storage144", "network144", "latency144"],
    ),
    (
        ("library144 service144 gateway144 storage144 network144 latency144", 18),
        ["library144", "service144", "gateway144", "storage144", "network144", "latency144"],
    ),
    (
        ("library144 service144 gateway144 storage144 network144 latency144", 28),
        ["library144 service144", "gateway144 storage144", "network144 latency144"],
    ),
    (
        ("service144 gateway144 storage144 network144 latency144 buffer144", 6),
        ["service144", "gateway144", "storage144", "network144", "latency144", "buffer144"],
    ),
    (
        ("service144 gateway144 storage144 network144 latency144 buffer144", 10),
        ["service144", "gateway144", "storage144", "network144", "latency144", "buffer144"],
    ),
    (
        ("service144 gateway144 storage144 network144 latency144 buffer144", 18),
        ["service144", "gateway144", "storage144", "network144", "latency144", "buffer144"],
    ),
    (
        ("service144 gateway144 storage144 network144 latency144 buffer144", 28),
        ["service144 gateway144", "storage144 network144", "latency144 buffer144"],
    ),
    (
        ("gateway144 storage144 network144 latency144 buffer144 queue144", 6),
        ["gateway144", "storage144", "network144", "latency144", "buffer144", "queue144"],
    ),
    (
        ("gateway144 storage144 network144 latency144 buffer144 queue144", 10),
        ["gateway144", "storage144", "network144", "latency144", "buffer144", "queue144"],
    ),
    (
        ("gateway144 storage144 network144 latency144 buffer144 queue144", 18),
        ["gateway144", "storage144", "network144", "latency144", "buffer144 queue144"],
    ),
    (
        ("gateway144 storage144 network144 latency144 buffer144 queue144", 28),
        ["gateway144 storage144", "network144 latency144", "buffer144 queue144"],
    ),
    (
        ("storage144 network144 latency144 buffer144 queue144 worker144", 6),
        ["storage144", "network144", "latency144", "buffer144", "queue144", "worker144"],
    ),
    (
        ("storage144 network144 latency144 buffer144 queue144 worker144", 10),
        ["storage144", "network144", "latency144", "buffer144", "queue144", "worker144"],
    ),
    (
        ("storage144 network144 latency144 buffer144 queue144 worker144", 18),
        ["storage144", "network144", "latency144", "buffer144 queue144", "worker144"],
    ),
    (
        ("storage144 network144 latency144 buffer144 queue144 worker144", 28),
        ["storage144 network144", "latency144 buffer144", "queue144 worker144"],
    ),
    (
        ("network144 latency144 buffer144 queue144 worker144 kernel144", 6),
        ["network144", "latency144", "buffer144", "queue144", "worker144", "kernel144"],
    ),
    (
        ("network144 latency144 buffer144 queue144 worker144 kernel144", 10),
        ["network144", "latency144", "buffer144", "queue144", "worker144", "kernel144"],
    ),
    (
        ("network144 latency144 buffer144 queue144 worker144 kernel144", 18),
        ["network144", "latency144", "buffer144 queue144", "worker144", "kernel144"],
    ),
    (
        ("network144 latency144 buffer144 queue144 worker144 kernel144", 28),
        ["network144 latency144", "buffer144 queue144 worker144", "kernel144"],
    ),
    (
        ("latency144 buffer144 queue144 worker144 kernel144 signal144", 6),
        ["latency144", "buffer144", "queue144", "worker144", "kernel144", "signal144"],
    ),
    (
        ("latency144 buffer144 queue144 worker144 kernel144 signal144", 10),
        ["latency144", "buffer144", "queue144", "worker144", "kernel144", "signal144"],
    ),
    (
        ("latency144 buffer144 queue144 worker144 kernel144 signal144", 18),
        ["latency144", "buffer144 queue144", "worker144", "kernel144", "signal144"],
    ),
    (
        ("latency144 buffer144 queue144 worker144 kernel144 signal144", 28),
        ["latency144 buffer144", "queue144 worker144 kernel144", "signal144"],
    ),
    (
        ("buffer144 queue144 worker144 kernel144 signal144 packet144", 6),
        ["buffer144", "queue144", "worker144", "kernel144", "signal144", "packet144"],
    ),
    (
        ("buffer144 queue144 worker144 kernel144 signal144 packet144", 10),
        ["buffer144", "queue144", "worker144", "kernel144", "signal144", "packet144"],
    ),
    (
        ("buffer144 queue144 worker144 kernel144 signal144 packet144", 18),
        ["buffer144 queue144", "worker144", "kernel144", "signal144", "packet144"],
    ),
    (
        ("buffer144 queue144 worker144 kernel144 signal144 packet144", 28),
        ["buffer144 queue144 worker144", "kernel144 signal144", "packet144"],
    ),
    (
        ("queue144 worker144 kernel144 signal144 packet144 router144", 6),
        ["queue144", "worker144", "kernel144", "signal144", "packet144", "router144"],
    ),
    (
        ("queue144 worker144 kernel144 signal144 packet144 router144", 10),
        ["queue144", "worker144", "kernel144", "signal144", "packet144", "router144"],
    ),
    (
        ("queue144 worker144 kernel144 signal144 packet144 router144", 18),
        ["queue144 worker144", "kernel144", "signal144", "packet144", "router144"],
    ),
    (
        ("queue144 worker144 kernel144 signal144 packet144 router144", 28),
        ["queue144 worker144 kernel144", "signal144 packet144", "router144"],
    ),
    (
        ("worker144 kernel144 signal144 packet144 router144 cluster144", 6),
        ["worker144", "kernel144", "signal144", "packet144", "router144", "cluster144"],
    ),
    (
        ("worker144 kernel144 signal144 packet144 router144 cluster144", 10),
        ["worker144", "kernel144", "signal144", "packet144", "router144", "cluster144"],
    ),
    (
        ("worker144 kernel144 signal144 packet144 router144 cluster144", 18),
        ["worker144", "kernel144", "signal144", "packet144", "router144", "cluster144"],
    ),
    (
        ("worker144 kernel144 signal144 packet144 router144 cluster144", 28),
        ["worker144 kernel144", "signal144 packet144", "router144 cluster144"],
    ),
    (
        ("kernel144 signal144 packet144 router144 cluster144 mirror144", 6),
        ["kernel144", "signal144", "packet144", "router144", "cluster144", "mirror144"],
    ),
    (
        ("kernel144 signal144 packet144 router144 cluster144 mirror144", 10),
        ["kernel144", "signal144", "packet144", "router144", "cluster144", "mirror144"],
    ),
    (
        ("kernel144 signal144 packet144 router144 cluster144 mirror144", 18),
        ["kernel144", "signal144", "packet144", "router144", "cluster144", "mirror144"],
    ),
    (
        ("kernel144 signal144 packet144 router144 cluster144 mirror144", 28),
        ["kernel144 signal144", "packet144 router144", "cluster144 mirror144"],
    ),
    (
        ("signal144 packet144 router144 cluster144 mirror144 filter144", 6),
        ["signal144", "packet144", "router144", "cluster144", "mirror144", "filter144"],
    ),
    (
        ("signal144 packet144 router144 cluster144 mirror144 filter144", 10),
        ["signal144", "packet144", "router144", "cluster144", "mirror144", "filter144"],
    ),
    (
        ("signal144 packet144 router144 cluster144 mirror144 filter144", 18),
        ["signal144", "packet144", "router144", "cluster144", "mirror144", "filter144"],
    ),
    (
        ("signal144 packet144 router144 cluster144 mirror144 filter144", 28),
        ["signal144 packet144", "router144 cluster144", "mirror144 filter144"],
    ),
    (
        ("packet144 router144 cluster144 mirror144 filter144 ranking144", 6),
        ["packet144", "router144", "cluster144", "mirror144", "filter144", "ranking144"],
    ),
    (
        ("packet144 router144 cluster144 mirror144 filter144 ranking144", 10),
        ["packet144", "router144", "cluster144", "mirror144", "filter144", "ranking144"],
    ),
    (
        ("packet144 router144 cluster144 mirror144 filter144 ranking144", 18),
        ["packet144", "router144", "cluster144", "mirror144", "filter144", "ranking144"],
    ),
    (
        ("packet144 router144 cluster144 mirror144 filter144 ranking144", 28),
        ["packet144 router144", "cluster144 mirror144", "filter144 ranking144"],
    ),
    (
        ("router144 cluster144 mirror144 filter144 ranking144 encoding144", 6),
        ["router144", "cluster144", "mirror144", "filter144", "ranking144", "encoding144"],
    ),
    (
        ("router144 cluster144 mirror144 filter144 ranking144 encoding144", 10),
        ["router144", "cluster144", "mirror144", "filter144", "ranking144", "encoding144"],
    ),
    (
        ("router144 cluster144 mirror144 filter144 ranking144 encoding144", 18),
        ["router144", "cluster144", "mirror144", "filter144", "ranking144", "encoding144"],
    ),
    (
        ("router144 cluster144 mirror144 filter144 ranking144 encoding144", 28),
        ["router144 cluster144", "mirror144 filter144", "ranking144 encoding144"],
    ),
    (
        ("cluster144 mirror144 filter144 ranking144 encoding144 mapping144", 6),
        ["cluster144", "mirror144", "filter144", "ranking144", "encoding144", "mapping144"],
    ),
    (
        ("cluster144 mirror144 filter144 ranking144 encoding144 mapping144", 10),
        ["cluster144", "mirror144", "filter144", "ranking144", "encoding144", "mapping144"],
    ),
    (
        ("cluster144 mirror144 filter144 ranking144 encoding144 mapping144", 18),
        ["cluster144", "mirror144", "filter144", "ranking144", "encoding144", "mapping144"],
    ),
    (
        ("cluster144 mirror144 filter144 ranking144 encoding144 mapping144", 28),
        ["cluster144 mirror144", "filter144 ranking144", "encoding144 mapping144"],
    ),
    (
        ("mirror144 filter144 ranking144 encoding144 mapping144 record144", 6),
        ["mirror144", "filter144", "ranking144", "encoding144", "mapping144", "record144"],
    ),
    (
        ("mirror144 filter144 ranking144 encoding144 mapping144 record144", 10),
        ["mirror144", "filter144", "ranking144", "encoding144", "mapping144", "record144"],
    ),
    (
        ("mirror144 filter144 ranking144 encoding144 mapping144 record144", 18),
        ["mirror144", "filter144", "ranking144", "encoding144", "mapping144", "record144"],
    ),
    (
        ("mirror144 filter144 ranking144 encoding144 mapping144 record144", 28),
        ["mirror144 filter144", "ranking144 encoding144", "mapping144 record144"],
    ),
    (
        ("filter144 ranking144 encoding144 mapping144 record144 candle144", 6),
        ["filter144", "ranking144", "encoding144", "mapping144", "record144", "candle144"],
    ),
    (
        ("filter144 ranking144 encoding144 mapping144 record144 candle144", 10),
        ["filter144", "ranking144", "encoding144", "mapping144", "record144", "candle144"],
    ),
    (
        ("filter144 ranking144 encoding144 mapping144 record144 candle144", 18),
        ["filter144", "ranking144", "encoding144", "mapping144", "record144", "candle144"],
    ),
    (
        ("filter144 ranking144 encoding144 mapping144 record144 candle144", 28),
        ["filter144 ranking144", "encoding144 mapping144", "record144 candle144"],
    ),
    (
        ("ranking144 encoding144 mapping144 record144 candle144 thread144", 6),
        ["ranking144", "encoding144", "mapping144", "record144", "candle144", "thread144"],
    ),
    (
        ("ranking144 encoding144 mapping144 record144 candle144 thread144", 10),
        ["ranking144", "encoding144", "mapping144", "record144", "candle144", "thread144"],
    ),
    (
        ("ranking144 encoding144 mapping144 record144 candle144 thread144", 18),
        ["ranking144", "encoding144", "mapping144", "record144", "candle144", "thread144"],
    ),
    (
        ("ranking144 encoding144 mapping144 record144 candle144 thread144", 28),
        ["ranking144 encoding144", "mapping144 record144", "candle144 thread144"],
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
