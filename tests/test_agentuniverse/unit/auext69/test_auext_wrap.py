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
        ("round 69: the quick brown fox jumps over the lazy dog", 4),
        ["round", "69:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 69: the quick brown fox jumps over the lazy dog", 8),
        ["round", "69: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 69: the quick brown fox jumps over the lazy dog", 12),
        ["round 69:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 69: the quick brown fox jumps over the lazy dog", 16),
        ["round 69: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 69: the quick brown fox jumps over the lazy dog", 24),
        ["round 69: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 69: the quick brown fox jumps over the lazy dog", 32),
        ["round 69: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 69: agentuniverse is a framework for multi agents", 4),
        ["round", "69:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 69: agentuniverse is a framework for multi agents", 8),
        ["round", "69:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 69: agentuniverse is a framework for multi agents", 12),
        ["round 69:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 69: agentuniverse is a framework for multi agents", 16),
        ["round 69:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 69: agentuniverse is a framework for multi agents", 24),
        ["round 69: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 69: agentuniverse is a framework for multi agents", 32),
        ["round 69: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 69: knowledge stored as vectors enables retrieval", 4),
        ["round", "69:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 69: knowledge stored as vectors enables retrieval", 8),
        ["round", "69:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 69: knowledge stored as vectors enables retrieval", 12),
        ["round 69:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 69: knowledge stored as vectors enables retrieval", 16),
        ["round 69:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 69: knowledge stored as vectors enables retrieval", 24),
        ["round 69: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 69: knowledge stored as vectors enables retrieval", 32),
        ["round 69: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 69: the processor reads the record then stops", 4),
        ["round", "69:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 69: the processor reads the record then stops", 8),
        ["round", "69: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 69: the processor reads the record then stops", 12),
        ["round 69:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 69: the processor reads the record then stops", 16),
        ["round 69: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 69: the processor reads the record then stops", 24),
        ["round 69: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 69: the processor reads the record then stops", 32),
        ["round 69: the processor reads", "the record then stops"],
    ),
    (
        ("round 69: a worker pulls the next task from the queue", 4),
        ["round", "69:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 69: a worker pulls the next task from the queue", 8),
        ["round", "69: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 69: a worker pulls the next task from the queue", 12),
        ["round 69: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 69: a worker pulls the next task from the queue", 16),
        ["round 69: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 69: a worker pulls the next task from the queue", 24),
        ["round 69: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 69: a worker pulls the next task from the queue", 32),
        ["round 69: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 69: signals travel through the network layer", 4),
        ["round", "69:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 69: signals travel through the network layer", 8),
        ["round", "69:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 69: signals travel through the network layer", 12),
        ["round 69:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 69: signals travel through the network layer", 16),
        ["round 69:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 69: signals travel through the network layer", 24),
        ["round 69: signals travel", "through the network", "layer"],
    ),
    (
        ("round 69: signals travel through the network layer", 32),
        ["round 69: signals travel through", "the network layer"],
    ),
    (
        ("round 69: the gateway routes each request by policy", 4),
        ["round", "69:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 69: the gateway routes each request by policy", 8),
        ["round", "69: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 69: the gateway routes each request by policy", 12),
        ["round 69:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 69: the gateway routes each request by policy", 16),
        ["round 69: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 69: the gateway routes each request by policy", 24),
        ["round 69: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 69: the gateway routes each request by policy", 32),
        ["round 69: the gateway routes", "each request by policy"],
    ),
    (
        ("round 69: memory grows until the buffer is full", 4),
        ["round", "69:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 69: memory grows until the buffer is full", 8),
        ["round", "69:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 69: memory grows until the buffer is full", 12),
        ["round 69:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 69: memory grows until the buffer is full", 16),
        ["round 69: memory", "grows until the", "buffer is full"],
    ),
    (("round 69: memory grows until the buffer is full", 24), ["round 69: memory grows", "until the buffer is full"]),
    (("round 69: memory grows until the buffer is full", 32), ["round 69: memory grows until the", "buffer is full"]),
    (
        ("round 69: the cluster mirrors every packet twice", 4),
        ["round", "69:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 69: the cluster mirrors every packet twice", 8),
        ["round", "69: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 69: the cluster mirrors every packet twice", 12),
        ["round 69:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 69: the cluster mirrors every packet twice", 16),
        ["round 69: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 69: the cluster mirrors every packet twice", 24),
        ["round 69: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 69: the cluster mirrors every packet twice", 32), ["round 69: the cluster mirrors", "every packet twice"]),
    (
        ("round 69: ranking uses tokens learned from the corpus", 4),
        ["round", "69:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 69: ranking uses tokens learned from the corpus", 8),
        ["round", "69:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 69: ranking uses tokens learned from the corpus", 12),
        ["round 69:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 69: ranking uses tokens learned from the corpus", 16),
        ["round 69:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 69: ranking uses tokens learned from the corpus", 24),
        ["round 69: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 69: ranking uses tokens learned from the corpus", 32),
        ["round 69: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 69: a long session ends when the candle dies", 4),
        ["round", "69:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 69: a long session ends when the candle dies", 8),
        ["round", "69: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 69: a long session ends when the candle dies", 12),
        ["round 69: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 69: a long session ends when the candle dies", 16),
        ["round 69: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 69: a long session ends when the candle dies", 24),
        ["round 69: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 69: a long session ends when the candle dies", 32),
        ["round 69: a long session ends", "when the candle dies"],
    ),
    (
        ("round 69: encode the prompt then map the result", 4),
        ["round", "69:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 69: encode the prompt then map the result", 8),
        ["round", "69:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 69: encode the prompt then map the result", 12),
        ["round 69:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 69: encode the prompt then map the result", 16),
        ["round 69: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 69: encode the prompt then map the result", 24),
        ["round 69: encode the", "prompt then map the", "result"],
    ),
    (("round 69: encode the prompt then map the result", 32), ["round 69: encode the prompt then", "map the result"]),
    (
        ("round 69: the kernel wakes the worker at dawn", 4),
        ["round", "69:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 69: the kernel wakes the worker at dawn", 8),
        ["round", "69: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 69: the kernel wakes the worker at dawn", 12),
        ["round 69:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 69: the kernel wakes the worker at dawn", 16), ["round 69: the", "kernel wakes the", "worker at dawn"]),
    (("round 69: the kernel wakes the worker at dawn", 24), ["round 69: the kernel", "wakes the worker at dawn"]),
    (("round 69: the kernel wakes the worker at dawn", 32), ["round 69: the kernel wakes the", "worker at dawn"]),
    (
        ("round 69: service latency drops after the patch", 4),
        ["round", "69:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 69: service latency drops after the patch", 8),
        ["round", "69:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 69: service latency drops after the patch", 12),
        ["round 69:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 69: service latency drops after the patch", 16),
        ["round 69:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 69: service latency drops after the patch", 24),
        ["round 69: service", "latency drops after the", "patch"],
    ),
    (("round 69: service latency drops after the patch", 32), ["round 69: service latency drops", "after the patch"]),
    (
        ("round 69: the library caches every vector it sees", 4),
        ["round", "69:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 69: the library caches every vector it sees", 8),
        ["round", "69: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 69: the library caches every vector it sees", 12),
        ["round 69:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 69: the library caches every vector it sees", 16),
        ["round 69: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 69: the library caches every vector it sees", 24),
        ["round 69: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 69: the library caches every vector it sees", 32),
        ["round 69: the library caches", "every vector it sees"],
    ),
    (
        ("round 69: agents argue then the debate resolves", 4),
        ["round", "69:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 69: agents argue then the debate resolves", 8),
        ["round", "69:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 69: agents argue then the debate resolves", 12),
        ["round 69:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 69: agents argue then the debate resolves", 16),
        ["round 69: agents", "argue then the", "debate resolves"],
    ),
    (("round 69: agents argue then the debate resolves", 24), ["round 69: agents argue", "then the debate resolves"]),
    (("round 69: agents argue then the debate resolves", 32), ["round 69: agents argue then the", "debate resolves"]),
    (
        ("round 69: the filter keeps only strong matches", 4),
        ["round", "69:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 69: the filter keeps only strong matches", 8),
        ["round", "69: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 69: the filter keeps only strong matches", 12),
        ["round 69:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 69: the filter keeps only strong matches", 16),
        ["round 69: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 69: the filter keeps only strong matches", 24), ["round 69: the filter", "keeps only strong", "matches"]),
    (("round 69: the filter keeps only strong matches", 32), ["round 69: the filter keeps only", "strong matches"]),
    (
        ("round 69: the model answers with a short reply", 4),
        ["round", "69:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 69: the model answers with a short reply", 8),
        ["round", "69: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 69: the model answers with a short reply", 12),
        ["round 69:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 69: the model answers with a short reply", 16),
        ["round 69: the", "model answers", "with a short", "reply"],
    ),
    (("round 69: the model answers with a short reply", 24), ["round 69: the model", "answers with a short", "reply"]),
    (("round 69: the model answers with a short reply", 32), ["round 69: the model answers with", "a short reply"]),
    (
        ("round 69: the recorder stores the reasoning trace", 4),
        ["round", "69:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 69: the recorder stores the reasoning trace", 8),
        ["round", "69: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 69: the recorder stores the reasoning trace", 12),
        ["round 69:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 69: the recorder stores the reasoning trace", 16),
        ["round 69: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 69: the recorder stores the reasoning trace", 24),
        ["round 69: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 69: the recorder stores the reasoning trace", 32),
        ["round 69: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 69: the angel watches the processor run", 4),
        ["round", "69:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 69: the angel watches the processor run", 8),
        ["round", "69: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 69: the angel watches the processor run", 12),
        ["round 69:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 69: the angel watches the processor run", 16), ["round 69: the", "angel watches", "the processor", "run"]),
    (("round 69: the angel watches the processor run", 24), ["round 69: the angel", "watches the processor", "run"]),
    (("round 69: the angel watches the processor run", 32), ["round 69: the angel watches the", "processor run"]),
    (
        ("round 69: angle of the vector decides the match", 4),
        ["round", "69:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 69: angle of the vector decides the match", 8),
        ["round", "69:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 69: angle of the vector decides the match", 12),
        ["round 69:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 69: angle of the vector decides the match", 16),
        ["round 69: angle", "of the vector", "decides the", "match"],
    ),
    (("round 69: angle of the vector decides the match", 24), ["round 69: angle of the", "vector decides the match"]),
    (("round 69: angle of the vector decides the match", 32), ["round 69: angle of the vector", "decides the match"]),
    (
        ("round 69: the candle burns twice as long at night", 4),
        ["round", "69:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 69: the candle burns twice as long at night", 8),
        ["round", "69: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 69: the candle burns twice as long at night", 12),
        ["round 69:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 69: the candle burns twice as long at night", 16),
        ["round 69: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 69: the candle burns twice as long at night", 24),
        ["round 69: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 69: the candle burns twice as long at night", 32),
        ["round 69: the candle burns twice", "as long at night"],
    ),
    (
        ("round 69: a mirror of the universe in one line", 4),
        ["round", "69:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 69: a mirror of the universe in one line", 8),
        ["round", "69: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 69: a mirror of the universe in one line", 12),
        ["round 69: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 69: a mirror of the universe in one line", 16),
        ["round 69: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 69: a mirror of the universe in one line", 24), ["round 69: a mirror of", "the universe in one line"]),
    (("round 69: a mirror of the universe in one line", 32), ["round 69: a mirror of the", "universe in one line"]),
    (
        ("round 69: the queue drains before the storm", 4),
        ["round", "69:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 69: the queue drains before the storm", 8),
        ["round", "69: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 69: the queue drains before the storm", 12), ["round 69:", "the queue", "drains", "before the", "storm"]),
    (("round 69: the queue drains before the storm", 16), ["round 69: the", "queue drains", "before the storm"]),
    (("round 69: the queue drains before the storm", 24), ["round 69: the queue", "drains before the storm"]),
    (("round 69: the queue drains before the storm", 32), ["round 69: the queue drains", "before the storm"]),
    (
        ("kitten69 sitting69 agent69 angle69 universe69 memory69", 6),
        ["kitten69", "sitting69", "agent69", "angle69", "universe69", "memory69"],
    ),
    (
        ("kitten69 sitting69 agent69 angle69 universe69 memory69", 10),
        ["kitten69", "sitting69", "agent69", "angle69", "universe69", "memory69"],
    ),
    (
        ("kitten69 sitting69 agent69 angle69 universe69 memory69", 18),
        ["kitten69 sitting69", "agent69 angle69", "universe69", "memory69"],
    ),
    (
        ("kitten69 sitting69 agent69 angle69 universe69 memory69", 28),
        ["kitten69 sitting69 agent69", "angle69 universe69 memory69"],
    ),
    (
        ("sitting69 agent69 angle69 universe69 memory69 stream69", 6),
        ["sitting69", "agent69", "angle69", "universe69", "memory69", "stream69"],
    ),
    (
        ("sitting69 agent69 angle69 universe69 memory69 stream69", 10),
        ["sitting69", "agent69", "angle69", "universe69", "memory69", "stream69"],
    ),
    (
        ("sitting69 agent69 angle69 universe69 memory69 stream69", 18),
        ["sitting69 agent69", "angle69 universe69", "memory69 stream69"],
    ),
    (
        ("sitting69 agent69 angle69 universe69 memory69 stream69", 28),
        ["sitting69 agent69 angle69", "universe69 memory69 stream69"],
    ),
    (
        ("agent69 angle69 universe69 memory69 stream69 context69", 6),
        ["agent69", "angle69", "universe69", "memory69", "stream69", "context69"],
    ),
    (
        ("agent69 angle69 universe69 memory69 stream69 context69", 10),
        ["agent69", "angle69", "universe69", "memory69", "stream69", "context69"],
    ),
    (
        ("agent69 angle69 universe69 memory69 stream69 context69", 18),
        ["agent69 angle69", "universe69", "memory69 stream69", "context69"],
    ),
    (
        ("agent69 angle69 universe69 memory69 stream69 context69", 28),
        ["agent69 angle69 universe69", "memory69 stream69 context69"],
    ),
    (
        ("angle69 universe69 memory69 stream69 context69 knowledge69", 6),
        ["angle69", "universe69", "memory69", "stream69", "context69", "knowledge69"],
    ),
    (
        ("angle69 universe69 memory69 stream69 context69 knowledge69", 10),
        ["angle69", "universe69", "memory69", "stream69", "context69", "knowledge69"],
    ),
    (
        ("angle69 universe69 memory69 stream69 context69 knowledge69", 18),
        ["angle69 universe69", "memory69 stream69", "context69", "knowledge69"],
    ),
    (
        ("angle69 universe69 memory69 stream69 context69 knowledge69", 28),
        ["angle69 universe69 memory69", "stream69 context69", "knowledge69"],
    ),
    (
        ("universe69 memory69 stream69 context69 knowledge69 vector69", 6),
        ["universe69", "memory69", "stream69", "context69", "knowledge69", "vector69"],
    ),
    (
        ("universe69 memory69 stream69 context69 knowledge69 vector69", 10),
        ["universe69", "memory69", "stream69", "context69", "knowledge69", "vector69"],
    ),
    (
        ("universe69 memory69 stream69 context69 knowledge69 vector69", 18),
        ["universe69", "memory69 stream69", "context69", "knowledge69", "vector69"],
    ),
    (
        ("universe69 memory69 stream69 context69 knowledge69 vector69", 28),
        ["universe69 memory69 stream69", "context69 knowledge69", "vector69"],
    ),
    (
        ("memory69 stream69 context69 knowledge69 vector69 processor69", 6),
        ["memory69", "stream69", "context69", "knowledge69", "vector69", "processor69"],
    ),
    (
        ("memory69 stream69 context69 knowledge69 vector69 processor69", 10),
        ["memory69", "stream69", "context69", "knowledge69", "vector69", "processor69"],
    ),
    (
        ("memory69 stream69 context69 knowledge69 vector69 processor69", 18),
        ["memory69 stream69", "context69", "knowledge69", "vector69", "processor69"],
    ),
    (
        ("memory69 stream69 context69 knowledge69 vector69 processor69", 28),
        ["memory69 stream69 context69", "knowledge69 vector69", "processor69"],
    ),
    (
        ("stream69 context69 knowledge69 vector69 processor69 reasoning69", 6),
        ["stream69", "context69", "knowledge69", "vector69", "processor69", "reasoning69"],
    ),
    (
        ("stream69 context69 knowledge69 vector69 processor69 reasoning69", 10),
        ["stream69", "context69", "knowledge69", "vector69", "processor69", "reasoning69"],
    ),
    (
        ("stream69 context69 knowledge69 vector69 processor69 reasoning69", 18),
        ["stream69 context69", "knowledge69", "vector69", "processor69", "reasoning69"],
    ),
    (
        ("stream69 context69 knowledge69 vector69 processor69 reasoning69", 28),
        ["stream69 context69", "knowledge69 vector69", "processor69 reasoning69"],
    ),
    (
        ("context69 knowledge69 vector69 processor69 reasoning69 machine69", 6),
        ["context69", "knowledge69", "vector69", "processor69", "reasoning69", "machine69"],
    ),
    (
        ("context69 knowledge69 vector69 processor69 reasoning69 machine69", 10),
        ["context69", "knowledge69", "vector69", "processor69", "reasoning69", "machine69"],
    ),
    (
        ("context69 knowledge69 vector69 processor69 reasoning69 machine69", 18),
        ["context69", "knowledge69", "vector69", "processor69", "reasoning69", "machine69"],
    ),
    (
        ("context69 knowledge69 vector69 processor69 reasoning69 machine69", 28),
        ["context69 knowledge69", "vector69 processor69", "reasoning69 machine69"],
    ),
    (
        ("knowledge69 vector69 processor69 reasoning69 machine69 learning69", 6),
        ["knowledge69", "vector69", "processor69", "reasoning69", "machine69", "learning69"],
    ),
    (
        ("knowledge69 vector69 processor69 reasoning69 machine69 learning69", 10),
        ["knowledge69", "vector69", "processor69", "reasoning69", "machine69", "learning69"],
    ),
    (
        ("knowledge69 vector69 processor69 reasoning69 machine69 learning69", 18),
        ["knowledge69", "vector69", "processor69", "reasoning69", "machine69", "learning69"],
    ),
    (
        ("knowledge69 vector69 processor69 reasoning69 machine69 learning69", 28),
        ["knowledge69 vector69", "processor69 reasoning69", "machine69 learning69"],
    ),
    (
        ("vector69 processor69 reasoning69 machine69 learning69 model69", 6),
        ["vector69", "processor69", "reasoning69", "machine69", "learning69", "model69"],
    ),
    (
        ("vector69 processor69 reasoning69 machine69 learning69 model69", 10),
        ["vector69", "processor69", "reasoning69", "machine69", "learning69", "model69"],
    ),
    (
        ("vector69 processor69 reasoning69 machine69 learning69 model69", 18),
        ["vector69", "processor69", "reasoning69", "machine69", "learning69 model69"],
    ),
    (
        ("vector69 processor69 reasoning69 machine69 learning69 model69", 28),
        ["vector69 processor69", "reasoning69 machine69", "learning69 model69"],
    ),
    (
        ("processor69 reasoning69 machine69 learning69 model69 token69", 6),
        ["processor69", "reasoning69", "machine69", "learning69", "model69", "token69"],
    ),
    (
        ("processor69 reasoning69 machine69 learning69 model69 token69", 10),
        ["processor69", "reasoning69", "machine69", "learning69", "model69", "token69"],
    ),
    (
        ("processor69 reasoning69 machine69 learning69 model69 token69", 18),
        ["processor69", "reasoning69", "machine69", "learning69 model69", "token69"],
    ),
    (
        ("processor69 reasoning69 machine69 learning69 model69 token69", 28),
        ["processor69 reasoning69", "machine69 learning69 model69", "token69"],
    ),
    (
        ("reasoning69 machine69 learning69 model69 token69 prompt69", 6),
        ["reasoning69", "machine69", "learning69", "model69", "token69", "prompt69"],
    ),
    (
        ("reasoning69 machine69 learning69 model69 token69 prompt69", 10),
        ["reasoning69", "machine69", "learning69", "model69", "token69", "prompt69"],
    ),
    (
        ("reasoning69 machine69 learning69 model69 token69 prompt69", 18),
        ["reasoning69", "machine69", "learning69 model69", "token69 prompt69"],
    ),
    (
        ("reasoning69 machine69 learning69 model69 token69 prompt69", 28),
        ["reasoning69 machine69", "learning69 model69 token69", "prompt69"],
    ),
    (
        ("machine69 learning69 model69 token69 prompt69 session69", 6),
        ["machine69", "learning69", "model69", "token69", "prompt69", "session69"],
    ),
    (
        ("machine69 learning69 model69 token69 prompt69 session69", 10),
        ["machine69", "learning69", "model69", "token69", "prompt69", "session69"],
    ),
    (
        ("machine69 learning69 model69 token69 prompt69 session69", 18),
        ["machine69", "learning69 model69", "token69 prompt69", "session69"],
    ),
    (
        ("machine69 learning69 model69 token69 prompt69 session69", 28),
        ["machine69 learning69 model69", "token69 prompt69 session69"],
    ),
    (
        ("learning69 model69 token69 prompt69 session69 library69", 6),
        ["learning69", "model69", "token69", "prompt69", "session69", "library69"],
    ),
    (
        ("learning69 model69 token69 prompt69 session69 library69", 10),
        ["learning69", "model69", "token69", "prompt69", "session69", "library69"],
    ),
    (
        ("learning69 model69 token69 prompt69 session69 library69", 18),
        ["learning69 model69", "token69 prompt69", "session69", "library69"],
    ),
    (
        ("learning69 model69 token69 prompt69 session69 library69", 28),
        ["learning69 model69 token69", "prompt69 session69 library69"],
    ),
    (
        ("model69 token69 prompt69 session69 library69 service69", 6),
        ["model69", "token69", "prompt69", "session69", "library69", "service69"],
    ),
    (
        ("model69 token69 prompt69 session69 library69 service69", 10),
        ["model69", "token69", "prompt69", "session69", "library69", "service69"],
    ),
    (
        ("model69 token69 prompt69 session69 library69 service69", 18),
        ["model69 token69", "prompt69 session69", "library69", "service69"],
    ),
    (
        ("model69 token69 prompt69 session69 library69 service69", 28),
        ["model69 token69 prompt69", "session69 library69", "service69"],
    ),
    (
        ("token69 prompt69 session69 library69 service69 gateway69", 6),
        ["token69", "prompt69", "session69", "library69", "service69", "gateway69"],
    ),
    (
        ("token69 prompt69 session69 library69 service69 gateway69", 10),
        ["token69", "prompt69", "session69", "library69", "service69", "gateway69"],
    ),
    (
        ("token69 prompt69 session69 library69 service69 gateway69", 18),
        ["token69 prompt69", "session69", "library69", "service69", "gateway69"],
    ),
    (
        ("token69 prompt69 session69 library69 service69 gateway69", 28),
        ["token69 prompt69 session69", "library69 service69", "gateway69"],
    ),
    (
        ("prompt69 session69 library69 service69 gateway69 storage69", 6),
        ["prompt69", "session69", "library69", "service69", "gateway69", "storage69"],
    ),
    (
        ("prompt69 session69 library69 service69 gateway69 storage69", 10),
        ["prompt69", "session69", "library69", "service69", "gateway69", "storage69"],
    ),
    (
        ("prompt69 session69 library69 service69 gateway69 storage69", 18),
        ["prompt69 session69", "library69", "service69", "gateway69", "storage69"],
    ),
    (
        ("prompt69 session69 library69 service69 gateway69 storage69", 28),
        ["prompt69 session69 library69", "service69 gateway69", "storage69"],
    ),
    (
        ("session69 library69 service69 gateway69 storage69 network69", 6),
        ["session69", "library69", "service69", "gateway69", "storage69", "network69"],
    ),
    (
        ("session69 library69 service69 gateway69 storage69 network69", 10),
        ["session69", "library69", "service69", "gateway69", "storage69", "network69"],
    ),
    (
        ("session69 library69 service69 gateway69 storage69 network69", 18),
        ["session69", "library69", "service69", "gateway69", "storage69", "network69"],
    ),
    (
        ("session69 library69 service69 gateway69 storage69 network69", 28),
        ["session69 library69", "service69 gateway69", "storage69 network69"],
    ),
    (
        ("library69 service69 gateway69 storage69 network69 latency69", 6),
        ["library69", "service69", "gateway69", "storage69", "network69", "latency69"],
    ),
    (
        ("library69 service69 gateway69 storage69 network69 latency69", 10),
        ["library69", "service69", "gateway69", "storage69", "network69", "latency69"],
    ),
    (
        ("library69 service69 gateway69 storage69 network69 latency69", 18),
        ["library69", "service69", "gateway69", "storage69", "network69", "latency69"],
    ),
    (
        ("library69 service69 gateway69 storage69 network69 latency69", 28),
        ["library69 service69", "gateway69 storage69", "network69 latency69"],
    ),
    (
        ("service69 gateway69 storage69 network69 latency69 buffer69", 6),
        ["service69", "gateway69", "storage69", "network69", "latency69", "buffer69"],
    ),
    (
        ("service69 gateway69 storage69 network69 latency69 buffer69", 10),
        ["service69", "gateway69", "storage69", "network69", "latency69", "buffer69"],
    ),
    (
        ("service69 gateway69 storage69 network69 latency69 buffer69", 18),
        ["service69", "gateway69", "storage69", "network69", "latency69 buffer69"],
    ),
    (
        ("service69 gateway69 storage69 network69 latency69 buffer69", 28),
        ["service69 gateway69", "storage69 network69", "latency69 buffer69"],
    ),
    (
        ("gateway69 storage69 network69 latency69 buffer69 queue69", 6),
        ["gateway69", "storage69", "network69", "latency69", "buffer69", "queue69"],
    ),
    (
        ("gateway69 storage69 network69 latency69 buffer69 queue69", 10),
        ["gateway69", "storage69", "network69", "latency69", "buffer69", "queue69"],
    ),
    (
        ("gateway69 storage69 network69 latency69 buffer69 queue69", 18),
        ["gateway69", "storage69", "network69", "latency69 buffer69", "queue69"],
    ),
    (
        ("gateway69 storage69 network69 latency69 buffer69 queue69", 28),
        ["gateway69 storage69", "network69 latency69 buffer69", "queue69"],
    ),
    (
        ("storage69 network69 latency69 buffer69 queue69 worker69", 6),
        ["storage69", "network69", "latency69", "buffer69", "queue69", "worker69"],
    ),
    (
        ("storage69 network69 latency69 buffer69 queue69 worker69", 10),
        ["storage69", "network69", "latency69", "buffer69", "queue69", "worker69"],
    ),
    (
        ("storage69 network69 latency69 buffer69 queue69 worker69", 18),
        ["storage69", "network69", "latency69 buffer69", "queue69 worker69"],
    ),
    (
        ("storage69 network69 latency69 buffer69 queue69 worker69", 28),
        ["storage69 network69", "latency69 buffer69 queue69", "worker69"],
    ),
    (
        ("network69 latency69 buffer69 queue69 worker69 kernel69", 6),
        ["network69", "latency69", "buffer69", "queue69", "worker69", "kernel69"],
    ),
    (
        ("network69 latency69 buffer69 queue69 worker69 kernel69", 10),
        ["network69", "latency69", "buffer69", "queue69", "worker69", "kernel69"],
    ),
    (
        ("network69 latency69 buffer69 queue69 worker69 kernel69", 18),
        ["network69", "latency69 buffer69", "queue69 worker69", "kernel69"],
    ),
    (
        ("network69 latency69 buffer69 queue69 worker69 kernel69", 28),
        ["network69 latency69 buffer69", "queue69 worker69 kernel69"],
    ),
    (
        ("latency69 buffer69 queue69 worker69 kernel69 signal69", 6),
        ["latency69", "buffer69", "queue69", "worker69", "kernel69", "signal69"],
    ),
    (
        ("latency69 buffer69 queue69 worker69 kernel69 signal69", 10),
        ["latency69", "buffer69", "queue69", "worker69", "kernel69", "signal69"],
    ),
    (
        ("latency69 buffer69 queue69 worker69 kernel69 signal69", 18),
        ["latency69 buffer69", "queue69 worker69", "kernel69 signal69"],
    ),
    (
        ("latency69 buffer69 queue69 worker69 kernel69 signal69", 28),
        ["latency69 buffer69 queue69", "worker69 kernel69 signal69"],
    ),
    (
        ("buffer69 queue69 worker69 kernel69 signal69 packet69", 6),
        ["buffer69", "queue69", "worker69", "kernel69", "signal69", "packet69"],
    ),
    (
        ("buffer69 queue69 worker69 kernel69 signal69 packet69", 10),
        ["buffer69", "queue69", "worker69", "kernel69", "signal69", "packet69"],
    ),
    (
        ("buffer69 queue69 worker69 kernel69 signal69 packet69", 18),
        ["buffer69 queue69", "worker69 kernel69", "signal69 packet69"],
    ),
    (
        ("buffer69 queue69 worker69 kernel69 signal69 packet69", 28),
        ["buffer69 queue69 worker69", "kernel69 signal69 packet69"],
    ),
    (
        ("queue69 worker69 kernel69 signal69 packet69 router69", 6),
        ["queue69", "worker69", "kernel69", "signal69", "packet69", "router69"],
    ),
    (
        ("queue69 worker69 kernel69 signal69 packet69 router69", 10),
        ["queue69", "worker69", "kernel69", "signal69", "packet69", "router69"],
    ),
    (
        ("queue69 worker69 kernel69 signal69 packet69 router69", 18),
        ["queue69 worker69", "kernel69 signal69", "packet69 router69"],
    ),
    (
        ("queue69 worker69 kernel69 signal69 packet69 router69", 28),
        ["queue69 worker69 kernel69", "signal69 packet69 router69"],
    ),
    (
        ("worker69 kernel69 signal69 packet69 router69 cluster69", 6),
        ["worker69", "kernel69", "signal69", "packet69", "router69", "cluster69"],
    ),
    (
        ("worker69 kernel69 signal69 packet69 router69 cluster69", 10),
        ["worker69", "kernel69", "signal69", "packet69", "router69", "cluster69"],
    ),
    (
        ("worker69 kernel69 signal69 packet69 router69 cluster69", 18),
        ["worker69 kernel69", "signal69 packet69", "router69 cluster69"],
    ),
    (
        ("worker69 kernel69 signal69 packet69 router69 cluster69", 28),
        ["worker69 kernel69 signal69", "packet69 router69 cluster69"],
    ),
    (
        ("kernel69 signal69 packet69 router69 cluster69 mirror69", 6),
        ["kernel69", "signal69", "packet69", "router69", "cluster69", "mirror69"],
    ),
    (
        ("kernel69 signal69 packet69 router69 cluster69 mirror69", 10),
        ["kernel69", "signal69", "packet69", "router69", "cluster69", "mirror69"],
    ),
    (
        ("kernel69 signal69 packet69 router69 cluster69 mirror69", 18),
        ["kernel69 signal69", "packet69 router69", "cluster69 mirror69"],
    ),
    (
        ("kernel69 signal69 packet69 router69 cluster69 mirror69", 28),
        ["kernel69 signal69 packet69", "router69 cluster69 mirror69"],
    ),
    (
        ("signal69 packet69 router69 cluster69 mirror69 filter69", 6),
        ["signal69", "packet69", "router69", "cluster69", "mirror69", "filter69"],
    ),
    (
        ("signal69 packet69 router69 cluster69 mirror69 filter69", 10),
        ["signal69", "packet69", "router69", "cluster69", "mirror69", "filter69"],
    ),
    (
        ("signal69 packet69 router69 cluster69 mirror69 filter69", 18),
        ["signal69 packet69", "router69 cluster69", "mirror69 filter69"],
    ),
    (
        ("signal69 packet69 router69 cluster69 mirror69 filter69", 28),
        ["signal69 packet69 router69", "cluster69 mirror69 filter69"],
    ),
    (
        ("packet69 router69 cluster69 mirror69 filter69 ranking69", 6),
        ["packet69", "router69", "cluster69", "mirror69", "filter69", "ranking69"],
    ),
    (
        ("packet69 router69 cluster69 mirror69 filter69 ranking69", 10),
        ["packet69", "router69", "cluster69", "mirror69", "filter69", "ranking69"],
    ),
    (
        ("packet69 router69 cluster69 mirror69 filter69 ranking69", 18),
        ["packet69 router69", "cluster69 mirror69", "filter69 ranking69"],
    ),
    (
        ("packet69 router69 cluster69 mirror69 filter69 ranking69", 28),
        ["packet69 router69 cluster69", "mirror69 filter69 ranking69"],
    ),
    (
        ("router69 cluster69 mirror69 filter69 ranking69 encoding69", 6),
        ["router69", "cluster69", "mirror69", "filter69", "ranking69", "encoding69"],
    ),
    (
        ("router69 cluster69 mirror69 filter69 ranking69 encoding69", 10),
        ["router69", "cluster69", "mirror69", "filter69", "ranking69", "encoding69"],
    ),
    (
        ("router69 cluster69 mirror69 filter69 ranking69 encoding69", 18),
        ["router69 cluster69", "mirror69 filter69", "ranking69", "encoding69"],
    ),
    (
        ("router69 cluster69 mirror69 filter69 ranking69 encoding69", 28),
        ["router69 cluster69 mirror69", "filter69 ranking69", "encoding69"],
    ),
    (
        ("cluster69 mirror69 filter69 ranking69 encoding69 mapping69", 6),
        ["cluster69", "mirror69", "filter69", "ranking69", "encoding69", "mapping69"],
    ),
    (
        ("cluster69 mirror69 filter69 ranking69 encoding69 mapping69", 10),
        ["cluster69", "mirror69", "filter69", "ranking69", "encoding69", "mapping69"],
    ),
    (
        ("cluster69 mirror69 filter69 ranking69 encoding69 mapping69", 18),
        ["cluster69 mirror69", "filter69 ranking69", "encoding69", "mapping69"],
    ),
    (
        ("cluster69 mirror69 filter69 ranking69 encoding69 mapping69", 28),
        ["cluster69 mirror69 filter69", "ranking69 encoding69", "mapping69"],
    ),
    (
        ("mirror69 filter69 ranking69 encoding69 mapping69 record69", 6),
        ["mirror69", "filter69", "ranking69", "encoding69", "mapping69", "record69"],
    ),
    (
        ("mirror69 filter69 ranking69 encoding69 mapping69 record69", 10),
        ["mirror69", "filter69", "ranking69", "encoding69", "mapping69", "record69"],
    ),
    (
        ("mirror69 filter69 ranking69 encoding69 mapping69 record69", 18),
        ["mirror69 filter69", "ranking69", "encoding69", "mapping69 record69"],
    ),
    (
        ("mirror69 filter69 ranking69 encoding69 mapping69 record69", 28),
        ["mirror69 filter69 ranking69", "encoding69 mapping69", "record69"],
    ),
    (
        ("filter69 ranking69 encoding69 mapping69 record69 candle69", 6),
        ["filter69", "ranking69", "encoding69", "mapping69", "record69", "candle69"],
    ),
    (
        ("filter69 ranking69 encoding69 mapping69 record69 candle69", 10),
        ["filter69", "ranking69", "encoding69", "mapping69", "record69", "candle69"],
    ),
    (
        ("filter69 ranking69 encoding69 mapping69 record69 candle69", 18),
        ["filter69 ranking69", "encoding69", "mapping69 record69", "candle69"],
    ),
    (
        ("filter69 ranking69 encoding69 mapping69 record69 candle69", 28),
        ["filter69 ranking69", "encoding69 mapping69", "record69 candle69"],
    ),
    (
        ("ranking69 encoding69 mapping69 record69 candle69 thread69", 6),
        ["ranking69", "encoding69", "mapping69", "record69", "candle69", "thread69"],
    ),
    (
        ("ranking69 encoding69 mapping69 record69 candle69 thread69", 10),
        ["ranking69", "encoding69", "mapping69", "record69", "candle69", "thread69"],
    ),
    (
        ("ranking69 encoding69 mapping69 record69 candle69 thread69", 18),
        ["ranking69", "encoding69", "mapping69 record69", "candle69 thread69"],
    ),
    (
        ("ranking69 encoding69 mapping69 record69 candle69 thread69", 28),
        ["ranking69 encoding69", "mapping69 record69 candle69", "thread69"],
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
