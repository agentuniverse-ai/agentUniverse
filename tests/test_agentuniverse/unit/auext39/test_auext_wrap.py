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
        ("round 39: the quick brown fox jumps over the lazy dog", 4),
        ["round", "39:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 39: the quick brown fox jumps over the lazy dog", 8),
        ["round", "39: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 39: the quick brown fox jumps over the lazy dog", 12),
        ["round 39:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 39: the quick brown fox jumps over the lazy dog", 16),
        ["round 39: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 39: the quick brown fox jumps over the lazy dog", 24),
        ["round 39: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 39: the quick brown fox jumps over the lazy dog", 32),
        ["round 39: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 39: agentuniverse is a framework for multi agents", 4),
        ["round", "39:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 39: agentuniverse is a framework for multi agents", 8),
        ["round", "39:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 39: agentuniverse is a framework for multi agents", 12),
        ["round 39:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 39: agentuniverse is a framework for multi agents", 16),
        ["round 39:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 39: agentuniverse is a framework for multi agents", 24),
        ["round 39: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 39: agentuniverse is a framework for multi agents", 32),
        ["round 39: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 39: knowledge stored as vectors enables retrieval", 4),
        ["round", "39:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 39: knowledge stored as vectors enables retrieval", 8),
        ["round", "39:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 39: knowledge stored as vectors enables retrieval", 12),
        ["round 39:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 39: knowledge stored as vectors enables retrieval", 16),
        ["round 39:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 39: knowledge stored as vectors enables retrieval", 24),
        ["round 39: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 39: knowledge stored as vectors enables retrieval", 32),
        ["round 39: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 39: the processor reads the record then stops", 4),
        ["round", "39:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 39: the processor reads the record then stops", 8),
        ["round", "39: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 39: the processor reads the record then stops", 12),
        ["round 39:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 39: the processor reads the record then stops", 16),
        ["round 39: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 39: the processor reads the record then stops", 24),
        ["round 39: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 39: the processor reads the record then stops", 32),
        ["round 39: the processor reads", "the record then stops"],
    ),
    (
        ("round 39: a worker pulls the next task from the queue", 4),
        ["round", "39:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 39: a worker pulls the next task from the queue", 8),
        ["round", "39: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 39: a worker pulls the next task from the queue", 12),
        ["round 39: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 39: a worker pulls the next task from the queue", 16),
        ["round 39: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 39: a worker pulls the next task from the queue", 24),
        ["round 39: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 39: a worker pulls the next task from the queue", 32),
        ["round 39: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 39: signals travel through the network layer", 4),
        ["round", "39:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 39: signals travel through the network layer", 8),
        ["round", "39:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 39: signals travel through the network layer", 12),
        ["round 39:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 39: signals travel through the network layer", 16),
        ["round 39:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 39: signals travel through the network layer", 24),
        ["round 39: signals travel", "through the network", "layer"],
    ),
    (
        ("round 39: signals travel through the network layer", 32),
        ["round 39: signals travel through", "the network layer"],
    ),
    (
        ("round 39: the gateway routes each request by policy", 4),
        ["round", "39:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 39: the gateway routes each request by policy", 8),
        ["round", "39: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 39: the gateway routes each request by policy", 12),
        ["round 39:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 39: the gateway routes each request by policy", 16),
        ["round 39: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 39: the gateway routes each request by policy", 24),
        ["round 39: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 39: the gateway routes each request by policy", 32),
        ["round 39: the gateway routes", "each request by policy"],
    ),
    (
        ("round 39: memory grows until the buffer is full", 4),
        ["round", "39:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 39: memory grows until the buffer is full", 8),
        ["round", "39:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 39: memory grows until the buffer is full", 12),
        ["round 39:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 39: memory grows until the buffer is full", 16),
        ["round 39: memory", "grows until the", "buffer is full"],
    ),
    (("round 39: memory grows until the buffer is full", 24), ["round 39: memory grows", "until the buffer is full"]),
    (("round 39: memory grows until the buffer is full", 32), ["round 39: memory grows until the", "buffer is full"]),
    (
        ("round 39: the cluster mirrors every packet twice", 4),
        ["round", "39:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 39: the cluster mirrors every packet twice", 8),
        ["round", "39: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 39: the cluster mirrors every packet twice", 12),
        ["round 39:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 39: the cluster mirrors every packet twice", 16),
        ["round 39: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 39: the cluster mirrors every packet twice", 24),
        ["round 39: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 39: the cluster mirrors every packet twice", 32), ["round 39: the cluster mirrors", "every packet twice"]),
    (
        ("round 39: ranking uses tokens learned from the corpus", 4),
        ["round", "39:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 39: ranking uses tokens learned from the corpus", 8),
        ["round", "39:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 39: ranking uses tokens learned from the corpus", 12),
        ["round 39:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 39: ranking uses tokens learned from the corpus", 16),
        ["round 39:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 39: ranking uses tokens learned from the corpus", 24),
        ["round 39: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 39: ranking uses tokens learned from the corpus", 32),
        ["round 39: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 39: a long session ends when the candle dies", 4),
        ["round", "39:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 39: a long session ends when the candle dies", 8),
        ["round", "39: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 39: a long session ends when the candle dies", 12),
        ["round 39: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 39: a long session ends when the candle dies", 16),
        ["round 39: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 39: a long session ends when the candle dies", 24),
        ["round 39: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 39: a long session ends when the candle dies", 32),
        ["round 39: a long session ends", "when the candle dies"],
    ),
    (
        ("round 39: encode the prompt then map the result", 4),
        ["round", "39:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 39: encode the prompt then map the result", 8),
        ["round", "39:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 39: encode the prompt then map the result", 12),
        ["round 39:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 39: encode the prompt then map the result", 16),
        ["round 39: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 39: encode the prompt then map the result", 24),
        ["round 39: encode the", "prompt then map the", "result"],
    ),
    (("round 39: encode the prompt then map the result", 32), ["round 39: encode the prompt then", "map the result"]),
    (
        ("round 39: the kernel wakes the worker at dawn", 4),
        ["round", "39:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 39: the kernel wakes the worker at dawn", 8),
        ["round", "39: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 39: the kernel wakes the worker at dawn", 12),
        ["round 39:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 39: the kernel wakes the worker at dawn", 16), ["round 39: the", "kernel wakes the", "worker at dawn"]),
    (("round 39: the kernel wakes the worker at dawn", 24), ["round 39: the kernel", "wakes the worker at dawn"]),
    (("round 39: the kernel wakes the worker at dawn", 32), ["round 39: the kernel wakes the", "worker at dawn"]),
    (
        ("round 39: service latency drops after the patch", 4),
        ["round", "39:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 39: service latency drops after the patch", 8),
        ["round", "39:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 39: service latency drops after the patch", 12),
        ["round 39:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 39: service latency drops after the patch", 16),
        ["round 39:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 39: service latency drops after the patch", 24),
        ["round 39: service", "latency drops after the", "patch"],
    ),
    (("round 39: service latency drops after the patch", 32), ["round 39: service latency drops", "after the patch"]),
    (
        ("round 39: the library caches every vector it sees", 4),
        ["round", "39:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 39: the library caches every vector it sees", 8),
        ["round", "39: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 39: the library caches every vector it sees", 12),
        ["round 39:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 39: the library caches every vector it sees", 16),
        ["round 39: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 39: the library caches every vector it sees", 24),
        ["round 39: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 39: the library caches every vector it sees", 32),
        ["round 39: the library caches", "every vector it sees"],
    ),
    (
        ("round 39: agents argue then the debate resolves", 4),
        ["round", "39:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 39: agents argue then the debate resolves", 8),
        ["round", "39:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 39: agents argue then the debate resolves", 12),
        ["round 39:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 39: agents argue then the debate resolves", 16),
        ["round 39: agents", "argue then the", "debate resolves"],
    ),
    (("round 39: agents argue then the debate resolves", 24), ["round 39: agents argue", "then the debate resolves"]),
    (("round 39: agents argue then the debate resolves", 32), ["round 39: agents argue then the", "debate resolves"]),
    (
        ("round 39: the filter keeps only strong matches", 4),
        ["round", "39:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 39: the filter keeps only strong matches", 8),
        ["round", "39: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 39: the filter keeps only strong matches", 12),
        ["round 39:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 39: the filter keeps only strong matches", 16),
        ["round 39: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 39: the filter keeps only strong matches", 24), ["round 39: the filter", "keeps only strong", "matches"]),
    (("round 39: the filter keeps only strong matches", 32), ["round 39: the filter keeps only", "strong matches"]),
    (
        ("round 39: the model answers with a short reply", 4),
        ["round", "39:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 39: the model answers with a short reply", 8),
        ["round", "39: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 39: the model answers with a short reply", 12),
        ["round 39:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 39: the model answers with a short reply", 16),
        ["round 39: the", "model answers", "with a short", "reply"],
    ),
    (("round 39: the model answers with a short reply", 24), ["round 39: the model", "answers with a short", "reply"]),
    (("round 39: the model answers with a short reply", 32), ["round 39: the model answers with", "a short reply"]),
    (
        ("round 39: the recorder stores the reasoning trace", 4),
        ["round", "39:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 39: the recorder stores the reasoning trace", 8),
        ["round", "39: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 39: the recorder stores the reasoning trace", 12),
        ["round 39:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 39: the recorder stores the reasoning trace", 16),
        ["round 39: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 39: the recorder stores the reasoning trace", 24),
        ["round 39: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 39: the recorder stores the reasoning trace", 32),
        ["round 39: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 39: the angel watches the processor run", 4),
        ["round", "39:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 39: the angel watches the processor run", 8),
        ["round", "39: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 39: the angel watches the processor run", 12),
        ["round 39:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 39: the angel watches the processor run", 16), ["round 39: the", "angel watches", "the processor", "run"]),
    (("round 39: the angel watches the processor run", 24), ["round 39: the angel", "watches the processor", "run"]),
    (("round 39: the angel watches the processor run", 32), ["round 39: the angel watches the", "processor run"]),
    (
        ("round 39: angle of the vector decides the match", 4),
        ["round", "39:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 39: angle of the vector decides the match", 8),
        ["round", "39:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 39: angle of the vector decides the match", 12),
        ["round 39:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 39: angle of the vector decides the match", 16),
        ["round 39: angle", "of the vector", "decides the", "match"],
    ),
    (("round 39: angle of the vector decides the match", 24), ["round 39: angle of the", "vector decides the match"]),
    (("round 39: angle of the vector decides the match", 32), ["round 39: angle of the vector", "decides the match"]),
    (
        ("round 39: the candle burns twice as long at night", 4),
        ["round", "39:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 39: the candle burns twice as long at night", 8),
        ["round", "39: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 39: the candle burns twice as long at night", 12),
        ["round 39:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 39: the candle burns twice as long at night", 16),
        ["round 39: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 39: the candle burns twice as long at night", 24),
        ["round 39: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 39: the candle burns twice as long at night", 32),
        ["round 39: the candle burns twice", "as long at night"],
    ),
    (
        ("round 39: a mirror of the universe in one line", 4),
        ["round", "39:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 39: a mirror of the universe in one line", 8),
        ["round", "39: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 39: a mirror of the universe in one line", 12),
        ["round 39: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 39: a mirror of the universe in one line", 16),
        ["round 39: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 39: a mirror of the universe in one line", 24), ["round 39: a mirror of", "the universe in one line"]),
    (("round 39: a mirror of the universe in one line", 32), ["round 39: a mirror of the", "universe in one line"]),
    (
        ("round 39: the queue drains before the storm", 4),
        ["round", "39:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 39: the queue drains before the storm", 8),
        ["round", "39: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 39: the queue drains before the storm", 12), ["round 39:", "the queue", "drains", "before the", "storm"]),
    (("round 39: the queue drains before the storm", 16), ["round 39: the", "queue drains", "before the storm"]),
    (("round 39: the queue drains before the storm", 24), ["round 39: the queue", "drains before the storm"]),
    (("round 39: the queue drains before the storm", 32), ["round 39: the queue drains", "before the storm"]),
    (
        ("kitten39 sitting39 agent39 angle39 universe39 memory39", 6),
        ["kitten39", "sitting39", "agent39", "angle39", "universe39", "memory39"],
    ),
    (
        ("kitten39 sitting39 agent39 angle39 universe39 memory39", 10),
        ["kitten39", "sitting39", "agent39", "angle39", "universe39", "memory39"],
    ),
    (
        ("kitten39 sitting39 agent39 angle39 universe39 memory39", 18),
        ["kitten39 sitting39", "agent39 angle39", "universe39", "memory39"],
    ),
    (
        ("kitten39 sitting39 agent39 angle39 universe39 memory39", 28),
        ["kitten39 sitting39 agent39", "angle39 universe39 memory39"],
    ),
    (
        ("sitting39 agent39 angle39 universe39 memory39 stream39", 6),
        ["sitting39", "agent39", "angle39", "universe39", "memory39", "stream39"],
    ),
    (
        ("sitting39 agent39 angle39 universe39 memory39 stream39", 10),
        ["sitting39", "agent39", "angle39", "universe39", "memory39", "stream39"],
    ),
    (
        ("sitting39 agent39 angle39 universe39 memory39 stream39", 18),
        ["sitting39 agent39", "angle39 universe39", "memory39 stream39"],
    ),
    (
        ("sitting39 agent39 angle39 universe39 memory39 stream39", 28),
        ["sitting39 agent39 angle39", "universe39 memory39 stream39"],
    ),
    (
        ("agent39 angle39 universe39 memory39 stream39 context39", 6),
        ["agent39", "angle39", "universe39", "memory39", "stream39", "context39"],
    ),
    (
        ("agent39 angle39 universe39 memory39 stream39 context39", 10),
        ["agent39", "angle39", "universe39", "memory39", "stream39", "context39"],
    ),
    (
        ("agent39 angle39 universe39 memory39 stream39 context39", 18),
        ["agent39 angle39", "universe39", "memory39 stream39", "context39"],
    ),
    (
        ("agent39 angle39 universe39 memory39 stream39 context39", 28),
        ["agent39 angle39 universe39", "memory39 stream39 context39"],
    ),
    (
        ("angle39 universe39 memory39 stream39 context39 knowledge39", 6),
        ["angle39", "universe39", "memory39", "stream39", "context39", "knowledge39"],
    ),
    (
        ("angle39 universe39 memory39 stream39 context39 knowledge39", 10),
        ["angle39", "universe39", "memory39", "stream39", "context39", "knowledge39"],
    ),
    (
        ("angle39 universe39 memory39 stream39 context39 knowledge39", 18),
        ["angle39 universe39", "memory39 stream39", "context39", "knowledge39"],
    ),
    (
        ("angle39 universe39 memory39 stream39 context39 knowledge39", 28),
        ["angle39 universe39 memory39", "stream39 context39", "knowledge39"],
    ),
    (
        ("universe39 memory39 stream39 context39 knowledge39 vector39", 6),
        ["universe39", "memory39", "stream39", "context39", "knowledge39", "vector39"],
    ),
    (
        ("universe39 memory39 stream39 context39 knowledge39 vector39", 10),
        ["universe39", "memory39", "stream39", "context39", "knowledge39", "vector39"],
    ),
    (
        ("universe39 memory39 stream39 context39 knowledge39 vector39", 18),
        ["universe39", "memory39 stream39", "context39", "knowledge39", "vector39"],
    ),
    (
        ("universe39 memory39 stream39 context39 knowledge39 vector39", 28),
        ["universe39 memory39 stream39", "context39 knowledge39", "vector39"],
    ),
    (
        ("memory39 stream39 context39 knowledge39 vector39 processor39", 6),
        ["memory39", "stream39", "context39", "knowledge39", "vector39", "processor39"],
    ),
    (
        ("memory39 stream39 context39 knowledge39 vector39 processor39", 10),
        ["memory39", "stream39", "context39", "knowledge39", "vector39", "processor39"],
    ),
    (
        ("memory39 stream39 context39 knowledge39 vector39 processor39", 18),
        ["memory39 stream39", "context39", "knowledge39", "vector39", "processor39"],
    ),
    (
        ("memory39 stream39 context39 knowledge39 vector39 processor39", 28),
        ["memory39 stream39 context39", "knowledge39 vector39", "processor39"],
    ),
    (
        ("stream39 context39 knowledge39 vector39 processor39 reasoning39", 6),
        ["stream39", "context39", "knowledge39", "vector39", "processor39", "reasoning39"],
    ),
    (
        ("stream39 context39 knowledge39 vector39 processor39 reasoning39", 10),
        ["stream39", "context39", "knowledge39", "vector39", "processor39", "reasoning39"],
    ),
    (
        ("stream39 context39 knowledge39 vector39 processor39 reasoning39", 18),
        ["stream39 context39", "knowledge39", "vector39", "processor39", "reasoning39"],
    ),
    (
        ("stream39 context39 knowledge39 vector39 processor39 reasoning39", 28),
        ["stream39 context39", "knowledge39 vector39", "processor39 reasoning39"],
    ),
    (
        ("context39 knowledge39 vector39 processor39 reasoning39 machine39", 6),
        ["context39", "knowledge39", "vector39", "processor39", "reasoning39", "machine39"],
    ),
    (
        ("context39 knowledge39 vector39 processor39 reasoning39 machine39", 10),
        ["context39", "knowledge39", "vector39", "processor39", "reasoning39", "machine39"],
    ),
    (
        ("context39 knowledge39 vector39 processor39 reasoning39 machine39", 18),
        ["context39", "knowledge39", "vector39", "processor39", "reasoning39", "machine39"],
    ),
    (
        ("context39 knowledge39 vector39 processor39 reasoning39 machine39", 28),
        ["context39 knowledge39", "vector39 processor39", "reasoning39 machine39"],
    ),
    (
        ("knowledge39 vector39 processor39 reasoning39 machine39 learning39", 6),
        ["knowledge39", "vector39", "processor39", "reasoning39", "machine39", "learning39"],
    ),
    (
        ("knowledge39 vector39 processor39 reasoning39 machine39 learning39", 10),
        ["knowledge39", "vector39", "processor39", "reasoning39", "machine39", "learning39"],
    ),
    (
        ("knowledge39 vector39 processor39 reasoning39 machine39 learning39", 18),
        ["knowledge39", "vector39", "processor39", "reasoning39", "machine39", "learning39"],
    ),
    (
        ("knowledge39 vector39 processor39 reasoning39 machine39 learning39", 28),
        ["knowledge39 vector39", "processor39 reasoning39", "machine39 learning39"],
    ),
    (
        ("vector39 processor39 reasoning39 machine39 learning39 model39", 6),
        ["vector39", "processor39", "reasoning39", "machine39", "learning39", "model39"],
    ),
    (
        ("vector39 processor39 reasoning39 machine39 learning39 model39", 10),
        ["vector39", "processor39", "reasoning39", "machine39", "learning39", "model39"],
    ),
    (
        ("vector39 processor39 reasoning39 machine39 learning39 model39", 18),
        ["vector39", "processor39", "reasoning39", "machine39", "learning39 model39"],
    ),
    (
        ("vector39 processor39 reasoning39 machine39 learning39 model39", 28),
        ["vector39 processor39", "reasoning39 machine39", "learning39 model39"],
    ),
    (
        ("processor39 reasoning39 machine39 learning39 model39 token39", 6),
        ["processor39", "reasoning39", "machine39", "learning39", "model39", "token39"],
    ),
    (
        ("processor39 reasoning39 machine39 learning39 model39 token39", 10),
        ["processor39", "reasoning39", "machine39", "learning39", "model39", "token39"],
    ),
    (
        ("processor39 reasoning39 machine39 learning39 model39 token39", 18),
        ["processor39", "reasoning39", "machine39", "learning39 model39", "token39"],
    ),
    (
        ("processor39 reasoning39 machine39 learning39 model39 token39", 28),
        ["processor39 reasoning39", "machine39 learning39 model39", "token39"],
    ),
    (
        ("reasoning39 machine39 learning39 model39 token39 prompt39", 6),
        ["reasoning39", "machine39", "learning39", "model39", "token39", "prompt39"],
    ),
    (
        ("reasoning39 machine39 learning39 model39 token39 prompt39", 10),
        ["reasoning39", "machine39", "learning39", "model39", "token39", "prompt39"],
    ),
    (
        ("reasoning39 machine39 learning39 model39 token39 prompt39", 18),
        ["reasoning39", "machine39", "learning39 model39", "token39 prompt39"],
    ),
    (
        ("reasoning39 machine39 learning39 model39 token39 prompt39", 28),
        ["reasoning39 machine39", "learning39 model39 token39", "prompt39"],
    ),
    (
        ("machine39 learning39 model39 token39 prompt39 session39", 6),
        ["machine39", "learning39", "model39", "token39", "prompt39", "session39"],
    ),
    (
        ("machine39 learning39 model39 token39 prompt39 session39", 10),
        ["machine39", "learning39", "model39", "token39", "prompt39", "session39"],
    ),
    (
        ("machine39 learning39 model39 token39 prompt39 session39", 18),
        ["machine39", "learning39 model39", "token39 prompt39", "session39"],
    ),
    (
        ("machine39 learning39 model39 token39 prompt39 session39", 28),
        ["machine39 learning39 model39", "token39 prompt39 session39"],
    ),
    (
        ("learning39 model39 token39 prompt39 session39 library39", 6),
        ["learning39", "model39", "token39", "prompt39", "session39", "library39"],
    ),
    (
        ("learning39 model39 token39 prompt39 session39 library39", 10),
        ["learning39", "model39", "token39", "prompt39", "session39", "library39"],
    ),
    (
        ("learning39 model39 token39 prompt39 session39 library39", 18),
        ["learning39 model39", "token39 prompt39", "session39", "library39"],
    ),
    (
        ("learning39 model39 token39 prompt39 session39 library39", 28),
        ["learning39 model39 token39", "prompt39 session39 library39"],
    ),
    (
        ("model39 token39 prompt39 session39 library39 service39", 6),
        ["model39", "token39", "prompt39", "session39", "library39", "service39"],
    ),
    (
        ("model39 token39 prompt39 session39 library39 service39", 10),
        ["model39", "token39", "prompt39", "session39", "library39", "service39"],
    ),
    (
        ("model39 token39 prompt39 session39 library39 service39", 18),
        ["model39 token39", "prompt39 session39", "library39", "service39"],
    ),
    (
        ("model39 token39 prompt39 session39 library39 service39", 28),
        ["model39 token39 prompt39", "session39 library39", "service39"],
    ),
    (
        ("token39 prompt39 session39 library39 service39 gateway39", 6),
        ["token39", "prompt39", "session39", "library39", "service39", "gateway39"],
    ),
    (
        ("token39 prompt39 session39 library39 service39 gateway39", 10),
        ["token39", "prompt39", "session39", "library39", "service39", "gateway39"],
    ),
    (
        ("token39 prompt39 session39 library39 service39 gateway39", 18),
        ["token39 prompt39", "session39", "library39", "service39", "gateway39"],
    ),
    (
        ("token39 prompt39 session39 library39 service39 gateway39", 28),
        ["token39 prompt39 session39", "library39 service39", "gateway39"],
    ),
    (
        ("prompt39 session39 library39 service39 gateway39 storage39", 6),
        ["prompt39", "session39", "library39", "service39", "gateway39", "storage39"],
    ),
    (
        ("prompt39 session39 library39 service39 gateway39 storage39", 10),
        ["prompt39", "session39", "library39", "service39", "gateway39", "storage39"],
    ),
    (
        ("prompt39 session39 library39 service39 gateway39 storage39", 18),
        ["prompt39 session39", "library39", "service39", "gateway39", "storage39"],
    ),
    (
        ("prompt39 session39 library39 service39 gateway39 storage39", 28),
        ["prompt39 session39 library39", "service39 gateway39", "storage39"],
    ),
    (
        ("session39 library39 service39 gateway39 storage39 network39", 6),
        ["session39", "library39", "service39", "gateway39", "storage39", "network39"],
    ),
    (
        ("session39 library39 service39 gateway39 storage39 network39", 10),
        ["session39", "library39", "service39", "gateway39", "storage39", "network39"],
    ),
    (
        ("session39 library39 service39 gateway39 storage39 network39", 18),
        ["session39", "library39", "service39", "gateway39", "storage39", "network39"],
    ),
    (
        ("session39 library39 service39 gateway39 storage39 network39", 28),
        ["session39 library39", "service39 gateway39", "storage39 network39"],
    ),
    (
        ("library39 service39 gateway39 storage39 network39 latency39", 6),
        ["library39", "service39", "gateway39", "storage39", "network39", "latency39"],
    ),
    (
        ("library39 service39 gateway39 storage39 network39 latency39", 10),
        ["library39", "service39", "gateway39", "storage39", "network39", "latency39"],
    ),
    (
        ("library39 service39 gateway39 storage39 network39 latency39", 18),
        ["library39", "service39", "gateway39", "storage39", "network39", "latency39"],
    ),
    (
        ("library39 service39 gateway39 storage39 network39 latency39", 28),
        ["library39 service39", "gateway39 storage39", "network39 latency39"],
    ),
    (
        ("service39 gateway39 storage39 network39 latency39 buffer39", 6),
        ["service39", "gateway39", "storage39", "network39", "latency39", "buffer39"],
    ),
    (
        ("service39 gateway39 storage39 network39 latency39 buffer39", 10),
        ["service39", "gateway39", "storage39", "network39", "latency39", "buffer39"],
    ),
    (
        ("service39 gateway39 storage39 network39 latency39 buffer39", 18),
        ["service39", "gateway39", "storage39", "network39", "latency39 buffer39"],
    ),
    (
        ("service39 gateway39 storage39 network39 latency39 buffer39", 28),
        ["service39 gateway39", "storage39 network39", "latency39 buffer39"],
    ),
    (
        ("gateway39 storage39 network39 latency39 buffer39 queue39", 6),
        ["gateway39", "storage39", "network39", "latency39", "buffer39", "queue39"],
    ),
    (
        ("gateway39 storage39 network39 latency39 buffer39 queue39", 10),
        ["gateway39", "storage39", "network39", "latency39", "buffer39", "queue39"],
    ),
    (
        ("gateway39 storage39 network39 latency39 buffer39 queue39", 18),
        ["gateway39", "storage39", "network39", "latency39 buffer39", "queue39"],
    ),
    (
        ("gateway39 storage39 network39 latency39 buffer39 queue39", 28),
        ["gateway39 storage39", "network39 latency39 buffer39", "queue39"],
    ),
    (
        ("storage39 network39 latency39 buffer39 queue39 worker39", 6),
        ["storage39", "network39", "latency39", "buffer39", "queue39", "worker39"],
    ),
    (
        ("storage39 network39 latency39 buffer39 queue39 worker39", 10),
        ["storage39", "network39", "latency39", "buffer39", "queue39", "worker39"],
    ),
    (
        ("storage39 network39 latency39 buffer39 queue39 worker39", 18),
        ["storage39", "network39", "latency39 buffer39", "queue39 worker39"],
    ),
    (
        ("storage39 network39 latency39 buffer39 queue39 worker39", 28),
        ["storage39 network39", "latency39 buffer39 queue39", "worker39"],
    ),
    (
        ("network39 latency39 buffer39 queue39 worker39 kernel39", 6),
        ["network39", "latency39", "buffer39", "queue39", "worker39", "kernel39"],
    ),
    (
        ("network39 latency39 buffer39 queue39 worker39 kernel39", 10),
        ["network39", "latency39", "buffer39", "queue39", "worker39", "kernel39"],
    ),
    (
        ("network39 latency39 buffer39 queue39 worker39 kernel39", 18),
        ["network39", "latency39 buffer39", "queue39 worker39", "kernel39"],
    ),
    (
        ("network39 latency39 buffer39 queue39 worker39 kernel39", 28),
        ["network39 latency39 buffer39", "queue39 worker39 kernel39"],
    ),
    (
        ("latency39 buffer39 queue39 worker39 kernel39 signal39", 6),
        ["latency39", "buffer39", "queue39", "worker39", "kernel39", "signal39"],
    ),
    (
        ("latency39 buffer39 queue39 worker39 kernel39 signal39", 10),
        ["latency39", "buffer39", "queue39", "worker39", "kernel39", "signal39"],
    ),
    (
        ("latency39 buffer39 queue39 worker39 kernel39 signal39", 18),
        ["latency39 buffer39", "queue39 worker39", "kernel39 signal39"],
    ),
    (
        ("latency39 buffer39 queue39 worker39 kernel39 signal39", 28),
        ["latency39 buffer39 queue39", "worker39 kernel39 signal39"],
    ),
    (
        ("buffer39 queue39 worker39 kernel39 signal39 packet39", 6),
        ["buffer39", "queue39", "worker39", "kernel39", "signal39", "packet39"],
    ),
    (
        ("buffer39 queue39 worker39 kernel39 signal39 packet39", 10),
        ["buffer39", "queue39", "worker39", "kernel39", "signal39", "packet39"],
    ),
    (
        ("buffer39 queue39 worker39 kernel39 signal39 packet39", 18),
        ["buffer39 queue39", "worker39 kernel39", "signal39 packet39"],
    ),
    (
        ("buffer39 queue39 worker39 kernel39 signal39 packet39", 28),
        ["buffer39 queue39 worker39", "kernel39 signal39 packet39"],
    ),
    (
        ("queue39 worker39 kernel39 signal39 packet39 router39", 6),
        ["queue39", "worker39", "kernel39", "signal39", "packet39", "router39"],
    ),
    (
        ("queue39 worker39 kernel39 signal39 packet39 router39", 10),
        ["queue39", "worker39", "kernel39", "signal39", "packet39", "router39"],
    ),
    (
        ("queue39 worker39 kernel39 signal39 packet39 router39", 18),
        ["queue39 worker39", "kernel39 signal39", "packet39 router39"],
    ),
    (
        ("queue39 worker39 kernel39 signal39 packet39 router39", 28),
        ["queue39 worker39 kernel39", "signal39 packet39 router39"],
    ),
    (
        ("worker39 kernel39 signal39 packet39 router39 cluster39", 6),
        ["worker39", "kernel39", "signal39", "packet39", "router39", "cluster39"],
    ),
    (
        ("worker39 kernel39 signal39 packet39 router39 cluster39", 10),
        ["worker39", "kernel39", "signal39", "packet39", "router39", "cluster39"],
    ),
    (
        ("worker39 kernel39 signal39 packet39 router39 cluster39", 18),
        ["worker39 kernel39", "signal39 packet39", "router39 cluster39"],
    ),
    (
        ("worker39 kernel39 signal39 packet39 router39 cluster39", 28),
        ["worker39 kernel39 signal39", "packet39 router39 cluster39"],
    ),
    (
        ("kernel39 signal39 packet39 router39 cluster39 mirror39", 6),
        ["kernel39", "signal39", "packet39", "router39", "cluster39", "mirror39"],
    ),
    (
        ("kernel39 signal39 packet39 router39 cluster39 mirror39", 10),
        ["kernel39", "signal39", "packet39", "router39", "cluster39", "mirror39"],
    ),
    (
        ("kernel39 signal39 packet39 router39 cluster39 mirror39", 18),
        ["kernel39 signal39", "packet39 router39", "cluster39 mirror39"],
    ),
    (
        ("kernel39 signal39 packet39 router39 cluster39 mirror39", 28),
        ["kernel39 signal39 packet39", "router39 cluster39 mirror39"],
    ),
    (
        ("signal39 packet39 router39 cluster39 mirror39 filter39", 6),
        ["signal39", "packet39", "router39", "cluster39", "mirror39", "filter39"],
    ),
    (
        ("signal39 packet39 router39 cluster39 mirror39 filter39", 10),
        ["signal39", "packet39", "router39", "cluster39", "mirror39", "filter39"],
    ),
    (
        ("signal39 packet39 router39 cluster39 mirror39 filter39", 18),
        ["signal39 packet39", "router39 cluster39", "mirror39 filter39"],
    ),
    (
        ("signal39 packet39 router39 cluster39 mirror39 filter39", 28),
        ["signal39 packet39 router39", "cluster39 mirror39 filter39"],
    ),
    (
        ("packet39 router39 cluster39 mirror39 filter39 ranking39", 6),
        ["packet39", "router39", "cluster39", "mirror39", "filter39", "ranking39"],
    ),
    (
        ("packet39 router39 cluster39 mirror39 filter39 ranking39", 10),
        ["packet39", "router39", "cluster39", "mirror39", "filter39", "ranking39"],
    ),
    (
        ("packet39 router39 cluster39 mirror39 filter39 ranking39", 18),
        ["packet39 router39", "cluster39 mirror39", "filter39 ranking39"],
    ),
    (
        ("packet39 router39 cluster39 mirror39 filter39 ranking39", 28),
        ["packet39 router39 cluster39", "mirror39 filter39 ranking39"],
    ),
    (
        ("router39 cluster39 mirror39 filter39 ranking39 encoding39", 6),
        ["router39", "cluster39", "mirror39", "filter39", "ranking39", "encoding39"],
    ),
    (
        ("router39 cluster39 mirror39 filter39 ranking39 encoding39", 10),
        ["router39", "cluster39", "mirror39", "filter39", "ranking39", "encoding39"],
    ),
    (
        ("router39 cluster39 mirror39 filter39 ranking39 encoding39", 18),
        ["router39 cluster39", "mirror39 filter39", "ranking39", "encoding39"],
    ),
    (
        ("router39 cluster39 mirror39 filter39 ranking39 encoding39", 28),
        ["router39 cluster39 mirror39", "filter39 ranking39", "encoding39"],
    ),
    (
        ("cluster39 mirror39 filter39 ranking39 encoding39 mapping39", 6),
        ["cluster39", "mirror39", "filter39", "ranking39", "encoding39", "mapping39"],
    ),
    (
        ("cluster39 mirror39 filter39 ranking39 encoding39 mapping39", 10),
        ["cluster39", "mirror39", "filter39", "ranking39", "encoding39", "mapping39"],
    ),
    (
        ("cluster39 mirror39 filter39 ranking39 encoding39 mapping39", 18),
        ["cluster39 mirror39", "filter39 ranking39", "encoding39", "mapping39"],
    ),
    (
        ("cluster39 mirror39 filter39 ranking39 encoding39 mapping39", 28),
        ["cluster39 mirror39 filter39", "ranking39 encoding39", "mapping39"],
    ),
    (
        ("mirror39 filter39 ranking39 encoding39 mapping39 record39", 6),
        ["mirror39", "filter39", "ranking39", "encoding39", "mapping39", "record39"],
    ),
    (
        ("mirror39 filter39 ranking39 encoding39 mapping39 record39", 10),
        ["mirror39", "filter39", "ranking39", "encoding39", "mapping39", "record39"],
    ),
    (
        ("mirror39 filter39 ranking39 encoding39 mapping39 record39", 18),
        ["mirror39 filter39", "ranking39", "encoding39", "mapping39 record39"],
    ),
    (
        ("mirror39 filter39 ranking39 encoding39 mapping39 record39", 28),
        ["mirror39 filter39 ranking39", "encoding39 mapping39", "record39"],
    ),
    (
        ("filter39 ranking39 encoding39 mapping39 record39 candle39", 6),
        ["filter39", "ranking39", "encoding39", "mapping39", "record39", "candle39"],
    ),
    (
        ("filter39 ranking39 encoding39 mapping39 record39 candle39", 10),
        ["filter39", "ranking39", "encoding39", "mapping39", "record39", "candle39"],
    ),
    (
        ("filter39 ranking39 encoding39 mapping39 record39 candle39", 18),
        ["filter39 ranking39", "encoding39", "mapping39 record39", "candle39"],
    ),
    (
        ("filter39 ranking39 encoding39 mapping39 record39 candle39", 28),
        ["filter39 ranking39", "encoding39 mapping39", "record39 candle39"],
    ),
    (
        ("ranking39 encoding39 mapping39 record39 candle39 thread39", 6),
        ["ranking39", "encoding39", "mapping39", "record39", "candle39", "thread39"],
    ),
    (
        ("ranking39 encoding39 mapping39 record39 candle39 thread39", 10),
        ["ranking39", "encoding39", "mapping39", "record39", "candle39", "thread39"],
    ),
    (
        ("ranking39 encoding39 mapping39 record39 candle39 thread39", 18),
        ["ranking39", "encoding39", "mapping39 record39", "candle39 thread39"],
    ),
    (
        ("ranking39 encoding39 mapping39 record39 candle39 thread39", 28),
        ["ranking39 encoding39", "mapping39 record39 candle39", "thread39"],
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
