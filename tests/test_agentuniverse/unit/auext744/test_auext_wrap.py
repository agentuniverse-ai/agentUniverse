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
        ("round 744: the quick brown fox jumps over the lazy dog", 4),
        ["round", "744:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", 8),
        ["round", "744: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", 12),
        ["round 744:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", 16),
        ["round 744: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", 24),
        ["round 744: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 744: the quick brown fox jumps over the lazy dog", 32),
        ["round 744: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", 4),
        ["round", "744:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", 8),
        ["round", "744:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", 12),
        ["round 744:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", 16),
        ["round 744:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", 24),
        ["round 744: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 744: agentuniverse is a framework for multi agents", 32),
        ["round 744: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", 4),
        ["round", "744:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", 8),
        ["round", "744:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", 12),
        ["round 744:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", 16),
        ["round 744:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", 24),
        ["round 744: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 744: knowledge stored as vectors enables retrieval", 32),
        ["round 744: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 744: the processor reads the record then stops", 4),
        ["round", "744:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 744: the processor reads the record then stops", 8),
        ["round", "744: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 744: the processor reads the record then stops", 12),
        ["round 744:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 744: the processor reads the record then stops", 16),
        ["round 744: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 744: the processor reads the record then stops", 24),
        ["round 744: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 744: the processor reads the record then stops", 32),
        ["round 744: the processor reads", "the record then stops"],
    ),
    (
        ("round 744: a worker pulls the next task from the queue", 4),
        ["round", "744:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 744: a worker pulls the next task from the queue", 8),
        ["round", "744: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 744: a worker pulls the next task from the queue", 12),
        ["round 744: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 744: a worker pulls the next task from the queue", 16),
        ["round 744: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 744: a worker pulls the next task from the queue", 24),
        ["round 744: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 744: a worker pulls the next task from the queue", 32),
        ["round 744: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 744: signals travel through the network layer", 4),
        ["round", "744:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 744: signals travel through the network layer", 8),
        ["round", "744:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 744: signals travel through the network layer", 12),
        ["round 744:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 744: signals travel through the network layer", 16),
        ["round 744:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 744: signals travel through the network layer", 24),
        ["round 744: signals", "travel through the", "network layer"],
    ),
    (
        ("round 744: signals travel through the network layer", 32),
        ["round 744: signals travel", "through the network layer"],
    ),
    (
        ("round 744: the gateway routes each request by policy", 4),
        ["round", "744:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 744: the gateway routes each request by policy", 8),
        ["round", "744: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 744: the gateway routes each request by policy", 12),
        ["round 744:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 744: the gateway routes each request by policy", 16),
        ["round 744: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 744: the gateway routes each request by policy", 24),
        ["round 744: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 744: the gateway routes each request by policy", 32),
        ["round 744: the gateway routes", "each request by policy"],
    ),
    (
        ("round 744: memory grows until the buffer is full", 4),
        ["round", "744:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 744: memory grows until the buffer is full", 8),
        ["round", "744:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 744: memory grows until the buffer is full", 12),
        ["round 744:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 744: memory grows until the buffer is full", 16),
        ["round 744:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 744: memory grows until the buffer is full", 24), ["round 744: memory grows", "until the buffer is full"]),
    (("round 744: memory grows until the buffer is full", 32), ["round 744: memory grows until", "the buffer is full"]),
    (
        ("round 744: the cluster mirrors every packet twice", 4),
        ["round", "744:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 744: the cluster mirrors every packet twice", 8),
        ["round", "744: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 744: the cluster mirrors every packet twice", 12),
        ["round 744:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 744: the cluster mirrors every packet twice", 16),
        ["round 744: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 744: the cluster mirrors every packet twice", 24),
        ["round 744: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 744: the cluster mirrors every packet twice", 32),
        ["round 744: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", 4),
        ["round", "744:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", 8),
        ["round", "744:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", 12),
        ["round 744:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", 16),
        ["round 744:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", 24),
        ["round 744: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 744: ranking uses tokens learned from the corpus", 32),
        ["round 744: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 744: a long session ends when the candle dies", 4),
        ["round", "744:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 744: a long session ends when the candle dies", 8),
        ["round", "744: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 744: a long session ends when the candle dies", 12),
        ["round 744: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 744: a long session ends when the candle dies", 16),
        ["round 744: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 744: a long session ends when the candle dies", 24),
        ["round 744: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 744: a long session ends when the candle dies", 32),
        ["round 744: a long session ends", "when the candle dies"],
    ),
    (
        ("round 744: encode the prompt then map the result", 4),
        ["round", "744:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 744: encode the prompt then map the result", 8),
        ["round", "744:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 744: encode the prompt then map the result", 12),
        ["round 744:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 744: encode the prompt then map the result", 16),
        ["round 744:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 744: encode the prompt then map the result", 24),
        ["round 744: encode the", "prompt then map the", "result"],
    ),
    (("round 744: encode the prompt then map the result", 32), ["round 744: encode the prompt", "then map the result"]),
    (
        ("round 744: the kernel wakes the worker at dawn", 4),
        ["round", "744:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 744: the kernel wakes the worker at dawn", 8),
        ["round", "744: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 744: the kernel wakes the worker at dawn", 12),
        ["round 744:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 744: the kernel wakes the worker at dawn", 16), ["round 744: the", "kernel wakes the", "worker at dawn"]),
    (("round 744: the kernel wakes the worker at dawn", 24), ["round 744: the kernel", "wakes the worker at dawn"]),
    (("round 744: the kernel wakes the worker at dawn", 32), ["round 744: the kernel wakes the", "worker at dawn"]),
    (
        ("round 744: service latency drops after the patch", 4),
        ["round", "744:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 744: service latency drops after the patch", 8),
        ["round", "744:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 744: service latency drops after the patch", 12),
        ["round 744:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 744: service latency drops after the patch", 16),
        ["round 744:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 744: service latency drops after the patch", 24),
        ["round 744: service", "latency drops after the", "patch"],
    ),
    (("round 744: service latency drops after the patch", 32), ["round 744: service latency drops", "after the patch"]),
    (
        ("round 744: the library caches every vector it sees", 4),
        ["round", "744:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 744: the library caches every vector it sees", 8),
        ["round", "744: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 744: the library caches every vector it sees", 12),
        ["round 744:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 744: the library caches every vector it sees", 16),
        ["round 744: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 744: the library caches every vector it sees", 24),
        ["round 744: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 744: the library caches every vector it sees", 32),
        ["round 744: the library caches", "every vector it sees"],
    ),
    (
        ("round 744: agents argue then the debate resolves", 4),
        ["round", "744:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 744: agents argue then the debate resolves", 8),
        ["round", "744:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 744: agents argue then the debate resolves", 12),
        ["round 744:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 744: agents argue then the debate resolves", 16),
        ["round 744:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 744: agents argue then the debate resolves", 24), ["round 744: agents argue", "then the debate resolves"]),
    (("round 744: agents argue then the debate resolves", 32), ["round 744: agents argue then the", "debate resolves"]),
    (
        ("round 744: the filter keeps only strong matches", 4),
        ["round", "744:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 744: the filter keeps only strong matches", 8),
        ["round", "744: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 744: the filter keeps only strong matches", 12),
        ["round 744:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 744: the filter keeps only strong matches", 16),
        ["round 744: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 744: the filter keeps only strong matches", 24),
        ["round 744: the filter", "keeps only strong", "matches"],
    ),
    (("round 744: the filter keeps only strong matches", 32), ["round 744: the filter keeps only", "strong matches"]),
    (
        ("round 744: the model answers with a short reply", 4),
        ["round", "744:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 744: the model answers with a short reply", 8),
        ["round", "744: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 744: the model answers with a short reply", 12),
        ["round 744:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 744: the model answers with a short reply", 16),
        ["round 744: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 744: the model answers with a short reply", 24),
        ["round 744: the model", "answers with a short", "reply"],
    ),
    (("round 744: the model answers with a short reply", 32), ["round 744: the model answers", "with a short reply"]),
    (
        ("round 744: the recorder stores the reasoning trace", 4),
        ["round", "744:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 744: the recorder stores the reasoning trace", 8),
        ["round", "744: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 744: the recorder stores the reasoning trace", 12),
        ["round 744:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 744: the recorder stores the reasoning trace", 16),
        ["round 744: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 744: the recorder stores the reasoning trace", 24),
        ["round 744: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 744: the recorder stores the reasoning trace", 32),
        ["round 744: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 744: the angel watches the processor run", 4),
        ["round", "744:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 744: the angel watches the processor run", 8),
        ["round", "744: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 744: the angel watches the processor run", 12),
        ["round 744:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 744: the angel watches the processor run", 16),
        ["round 744: the", "angel watches", "the processor", "run"],
    ),
    (("round 744: the angel watches the processor run", 24), ["round 744: the angel", "watches the processor", "run"]),
    (("round 744: the angel watches the processor run", 32), ["round 744: the angel watches the", "processor run"]),
    (
        ("round 744: angle of the vector decides the match", 4),
        ["round", "744:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 744: angle of the vector decides the match", 8),
        ["round", "744:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 744: angle of the vector decides the match", 12),
        ["round 744:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 744: angle of the vector decides the match", 16),
        ["round 744: angle", "of the vector", "decides the", "match"],
    ),
    (("round 744: angle of the vector decides the match", 24), ["round 744: angle of the", "vector decides the match"]),
    (("round 744: angle of the vector decides the match", 32), ["round 744: angle of the vector", "decides the match"]),
    (
        ("round 744: the candle burns twice as long at night", 4),
        ["round", "744:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 744: the candle burns twice as long at night", 8),
        ["round", "744: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 744: the candle burns twice as long at night", 12),
        ["round 744:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 744: the candle burns twice as long at night", 16),
        ["round 744: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 744: the candle burns twice as long at night", 24),
        ["round 744: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 744: the candle burns twice as long at night", 32),
        ["round 744: the candle burns", "twice as long at night"],
    ),
    (
        ("round 744: a mirror of the universe in one line", 4),
        ["round", "744:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 744: a mirror of the universe in one line", 8),
        ["round", "744: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 744: a mirror of the universe in one line", 12),
        ["round 744: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 744: a mirror of the universe in one line", 16),
        ["round 744: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 744: a mirror of the universe in one line", 24), ["round 744: a mirror of", "the universe in one line"]),
    (("round 744: a mirror of the universe in one line", 32), ["round 744: a mirror of the", "universe in one line"]),
    (
        ("round 744: the queue drains before the storm", 4),
        ["round", "744:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 744: the queue drains before the storm", 8),
        ["round", "744: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 744: the queue drains before the storm", 12),
        ["round 744:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 744: the queue drains before the storm", 16), ["round 744: the", "queue drains", "before the storm"]),
    (("round 744: the queue drains before the storm", 24), ["round 744: the queue", "drains before the storm"]),
    (("round 744: the queue drains before the storm", 32), ["round 744: the queue drains", "before the storm"]),
    (
        ("kitten744 sitting744 agent744 angle744 universe744 memory744", 6),
        ["kitten744", "sitting744", "agent744", "angle744", "universe744", "memory744"],
    ),
    (
        ("kitten744 sitting744 agent744 angle744 universe744 memory744", 10),
        ["kitten744", "sitting744", "agent744", "angle744", "universe744", "memory744"],
    ),
    (
        ("kitten744 sitting744 agent744 angle744 universe744 memory744", 18),
        ["kitten744", "sitting744", "agent744 angle744", "universe744", "memory744"],
    ),
    (
        ("kitten744 sitting744 agent744 angle744 universe744 memory744", 28),
        ["kitten744 sitting744", "agent744 angle744", "universe744 memory744"],
    ),
    (
        ("sitting744 agent744 angle744 universe744 memory744 stream744", 6),
        ["sitting744", "agent744", "angle744", "universe744", "memory744", "stream744"],
    ),
    (
        ("sitting744 agent744 angle744 universe744 memory744 stream744", 10),
        ["sitting744", "agent744", "angle744", "universe744", "memory744", "stream744"],
    ),
    (
        ("sitting744 agent744 angle744 universe744 memory744 stream744", 18),
        ["sitting744", "agent744 angle744", "universe744", "memory744", "stream744"],
    ),
    (
        ("sitting744 agent744 angle744 universe744 memory744 stream744", 28),
        ["sitting744 agent744 angle744", "universe744 memory744", "stream744"],
    ),
    (
        ("agent744 angle744 universe744 memory744 stream744 context744", 6),
        ["agent744", "angle744", "universe744", "memory744", "stream744", "context744"],
    ),
    (
        ("agent744 angle744 universe744 memory744 stream744 context744", 10),
        ["agent744", "angle744", "universe744", "memory744", "stream744", "context744"],
    ),
    (
        ("agent744 angle744 universe744 memory744 stream744 context744", 18),
        ["agent744 angle744", "universe744", "memory744", "stream744", "context744"],
    ),
    (
        ("agent744 angle744 universe744 memory744 stream744 context744", 28),
        ["agent744 angle744", "universe744 memory744", "stream744 context744"],
    ),
    (
        ("angle744 universe744 memory744 stream744 context744 knowledge744", 6),
        ["angle744", "universe744", "memory744", "stream744", "context744", "knowledge744"],
    ),
    (
        ("angle744 universe744 memory744 stream744 context744 knowledge744", 10),
        ["angle744", "universe744", "memory744", "stream744", "context744", "knowledge744"],
    ),
    (
        ("angle744 universe744 memory744 stream744 context744 knowledge744", 18),
        ["angle744", "universe744", "memory744", "stream744", "context744", "knowledge744"],
    ),
    (
        ("angle744 universe744 memory744 stream744 context744 knowledge744", 28),
        ["angle744 universe744", "memory744 stream744", "context744 knowledge744"],
    ),
    (
        ("universe744 memory744 stream744 context744 knowledge744 vector744", 6),
        ["universe744", "memory744", "stream744", "context744", "knowledge744", "vector744"],
    ),
    (
        ("universe744 memory744 stream744 context744 knowledge744 vector744", 10),
        ["universe744", "memory744", "stream744", "context744", "knowledge744", "vector744"],
    ),
    (
        ("universe744 memory744 stream744 context744 knowledge744 vector744", 18),
        ["universe744", "memory744", "stream744", "context744", "knowledge744", "vector744"],
    ),
    (
        ("universe744 memory744 stream744 context744 knowledge744 vector744", 28),
        ["universe744 memory744", "stream744 context744", "knowledge744 vector744"],
    ),
    (
        ("memory744 stream744 context744 knowledge744 vector744 processor744", 6),
        ["memory744", "stream744", "context744", "knowledge744", "vector744", "processor744"],
    ),
    (
        ("memory744 stream744 context744 knowledge744 vector744 processor744", 10),
        ["memory744", "stream744", "context744", "knowledge744", "vector744", "processor744"],
    ),
    (
        ("memory744 stream744 context744 knowledge744 vector744 processor744", 18),
        ["memory744", "stream744", "context744", "knowledge744", "vector744", "processor744"],
    ),
    (
        ("memory744 stream744 context744 knowledge744 vector744 processor744", 28),
        ["memory744 stream744", "context744 knowledge744", "vector744 processor744"],
    ),
    (
        ("stream744 context744 knowledge744 vector744 processor744 reasoning744", 6),
        ["stream744", "context744", "knowledge744", "vector744", "processor744", "reasoning744"],
    ),
    (
        ("stream744 context744 knowledge744 vector744 processor744 reasoning744", 10),
        ["stream744", "context744", "knowledge744", "vector744", "processor744", "reasoning744"],
    ),
    (
        ("stream744 context744 knowledge744 vector744 processor744 reasoning744", 18),
        ["stream744", "context744", "knowledge744", "vector744", "processor744", "reasoning744"],
    ),
    (
        ("stream744 context744 knowledge744 vector744 processor744 reasoning744", 28),
        ["stream744 context744", "knowledge744 vector744", "processor744 reasoning744"],
    ),
    (
        ("context744 knowledge744 vector744 processor744 reasoning744 machine744", 6),
        ["context744", "knowledge744", "vector744", "processor744", "reasoning744", "machine744"],
    ),
    (
        ("context744 knowledge744 vector744 processor744 reasoning744 machine744", 10),
        ["context744", "knowledge744", "vector744", "processor744", "reasoning744", "machine744"],
    ),
    (
        ("context744 knowledge744 vector744 processor744 reasoning744 machine744", 18),
        ["context744", "knowledge744", "vector744", "processor744", "reasoning744", "machine744"],
    ),
    (
        ("context744 knowledge744 vector744 processor744 reasoning744 machine744", 28),
        ["context744 knowledge744", "vector744 processor744", "reasoning744 machine744"],
    ),
    (
        ("knowledge744 vector744 processor744 reasoning744 machine744 learning744", 6),
        ["knowledge744", "vector744", "processor744", "reasoning744", "machine744", "learning744"],
    ),
    (
        ("knowledge744 vector744 processor744 reasoning744 machine744 learning744", 10),
        ["knowledge744", "vector744", "processor744", "reasoning744", "machine744", "learning744"],
    ),
    (
        ("knowledge744 vector744 processor744 reasoning744 machine744 learning744", 18),
        ["knowledge744", "vector744", "processor744", "reasoning744", "machine744", "learning744"],
    ),
    (
        ("knowledge744 vector744 processor744 reasoning744 machine744 learning744", 28),
        ["knowledge744 vector744", "processor744 reasoning744", "machine744 learning744"],
    ),
    (
        ("vector744 processor744 reasoning744 machine744 learning744 model744", 6),
        ["vector744", "processor744", "reasoning744", "machine744", "learning744", "model744"],
    ),
    (
        ("vector744 processor744 reasoning744 machine744 learning744 model744", 10),
        ["vector744", "processor744", "reasoning744", "machine744", "learning744", "model744"],
    ),
    (
        ("vector744 processor744 reasoning744 machine744 learning744 model744", 18),
        ["vector744", "processor744", "reasoning744", "machine744", "learning744", "model744"],
    ),
    (
        ("vector744 processor744 reasoning744 machine744 learning744 model744", 28),
        ["vector744 processor744", "reasoning744 machine744", "learning744 model744"],
    ),
    (
        ("processor744 reasoning744 machine744 learning744 model744 token744", 6),
        ["processor744", "reasoning744", "machine744", "learning744", "model744", "token744"],
    ),
    (
        ("processor744 reasoning744 machine744 learning744 model744 token744", 10),
        ["processor744", "reasoning744", "machine744", "learning744", "model744", "token744"],
    ),
    (
        ("processor744 reasoning744 machine744 learning744 model744 token744", 18),
        ["processor744", "reasoning744", "machine744", "learning744", "model744 token744"],
    ),
    (
        ("processor744 reasoning744 machine744 learning744 model744 token744", 28),
        ["processor744 reasoning744", "machine744 learning744", "model744 token744"],
    ),
    (
        ("reasoning744 machine744 learning744 model744 token744 prompt744", 6),
        ["reasoning744", "machine744", "learning744", "model744", "token744", "prompt744"],
    ),
    (
        ("reasoning744 machine744 learning744 model744 token744 prompt744", 10),
        ["reasoning744", "machine744", "learning744", "model744", "token744", "prompt744"],
    ),
    (
        ("reasoning744 machine744 learning744 model744 token744 prompt744", 18),
        ["reasoning744", "machine744", "learning744", "model744 token744", "prompt744"],
    ),
    (
        ("reasoning744 machine744 learning744 model744 token744 prompt744", 28),
        ["reasoning744 machine744", "learning744 model744", "token744 prompt744"],
    ),
    (
        ("machine744 learning744 model744 token744 prompt744 session744", 6),
        ["machine744", "learning744", "model744", "token744", "prompt744", "session744"],
    ),
    (
        ("machine744 learning744 model744 token744 prompt744 session744", 10),
        ["machine744", "learning744", "model744", "token744", "prompt744", "session744"],
    ),
    (
        ("machine744 learning744 model744 token744 prompt744 session744", 18),
        ["machine744", "learning744", "model744 token744", "prompt744", "session744"],
    ),
    (
        ("machine744 learning744 model744 token744 prompt744 session744", 28),
        ["machine744 learning744", "model744 token744 prompt744", "session744"],
    ),
    (
        ("learning744 model744 token744 prompt744 session744 library744", 6),
        ["learning744", "model744", "token744", "prompt744", "session744", "library744"],
    ),
    (
        ("learning744 model744 token744 prompt744 session744 library744", 10),
        ["learning744", "model744", "token744", "prompt744", "session744", "library744"],
    ),
    (
        ("learning744 model744 token744 prompt744 session744 library744", 18),
        ["learning744", "model744 token744", "prompt744", "session744", "library744"],
    ),
    (
        ("learning744 model744 token744 prompt744 session744 library744", 28),
        ["learning744 model744", "token744 prompt744", "session744 library744"],
    ),
    (
        ("model744 token744 prompt744 session744 library744 service744", 6),
        ["model744", "token744", "prompt744", "session744", "library744", "service744"],
    ),
    (
        ("model744 token744 prompt744 session744 library744 service744", 10),
        ["model744", "token744", "prompt744", "session744", "library744", "service744"],
    ),
    (
        ("model744 token744 prompt744 session744 library744 service744", 18),
        ["model744 token744", "prompt744", "session744", "library744", "service744"],
    ),
    (
        ("model744 token744 prompt744 session744 library744 service744", 28),
        ["model744 token744 prompt744", "session744 library744", "service744"],
    ),
    (
        ("token744 prompt744 session744 library744 service744 gateway744", 6),
        ["token744", "prompt744", "session744", "library744", "service744", "gateway744"],
    ),
    (
        ("token744 prompt744 session744 library744 service744 gateway744", 10),
        ["token744", "prompt744", "session744", "library744", "service744", "gateway744"],
    ),
    (
        ("token744 prompt744 session744 library744 service744 gateway744", 18),
        ["token744 prompt744", "session744", "library744", "service744", "gateway744"],
    ),
    (
        ("token744 prompt744 session744 library744 service744 gateway744", 28),
        ["token744 prompt744", "session744 library744", "service744 gateway744"],
    ),
    (
        ("prompt744 session744 library744 service744 gateway744 storage744", 6),
        ["prompt744", "session744", "library744", "service744", "gateway744", "storage744"],
    ),
    (
        ("prompt744 session744 library744 service744 gateway744 storage744", 10),
        ["prompt744", "session744", "library744", "service744", "gateway744", "storage744"],
    ),
    (
        ("prompt744 session744 library744 service744 gateway744 storage744", 18),
        ["prompt744", "session744", "library744", "service744", "gateway744", "storage744"],
    ),
    (
        ("prompt744 session744 library744 service744 gateway744 storage744", 28),
        ["prompt744 session744", "library744 service744", "gateway744 storage744"],
    ),
    (
        ("session744 library744 service744 gateway744 storage744 network744", 6),
        ["session744", "library744", "service744", "gateway744", "storage744", "network744"],
    ),
    (
        ("session744 library744 service744 gateway744 storage744 network744", 10),
        ["session744", "library744", "service744", "gateway744", "storage744", "network744"],
    ),
    (
        ("session744 library744 service744 gateway744 storage744 network744", 18),
        ["session744", "library744", "service744", "gateway744", "storage744", "network744"],
    ),
    (
        ("session744 library744 service744 gateway744 storage744 network744", 28),
        ["session744 library744", "service744 gateway744", "storage744 network744"],
    ),
    (
        ("library744 service744 gateway744 storage744 network744 latency744", 6),
        ["library744", "service744", "gateway744", "storage744", "network744", "latency744"],
    ),
    (
        ("library744 service744 gateway744 storage744 network744 latency744", 10),
        ["library744", "service744", "gateway744", "storage744", "network744", "latency744"],
    ),
    (
        ("library744 service744 gateway744 storage744 network744 latency744", 18),
        ["library744", "service744", "gateway744", "storage744", "network744", "latency744"],
    ),
    (
        ("library744 service744 gateway744 storage744 network744 latency744", 28),
        ["library744 service744", "gateway744 storage744", "network744 latency744"],
    ),
    (
        ("service744 gateway744 storage744 network744 latency744 buffer744", 6),
        ["service744", "gateway744", "storage744", "network744", "latency744", "buffer744"],
    ),
    (
        ("service744 gateway744 storage744 network744 latency744 buffer744", 10),
        ["service744", "gateway744", "storage744", "network744", "latency744", "buffer744"],
    ),
    (
        ("service744 gateway744 storage744 network744 latency744 buffer744", 18),
        ["service744", "gateway744", "storage744", "network744", "latency744", "buffer744"],
    ),
    (
        ("service744 gateway744 storage744 network744 latency744 buffer744", 28),
        ["service744 gateway744", "storage744 network744", "latency744 buffer744"],
    ),
    (
        ("gateway744 storage744 network744 latency744 buffer744 queue744", 6),
        ["gateway744", "storage744", "network744", "latency744", "buffer744", "queue744"],
    ),
    (
        ("gateway744 storage744 network744 latency744 buffer744 queue744", 10),
        ["gateway744", "storage744", "network744", "latency744", "buffer744", "queue744"],
    ),
    (
        ("gateway744 storage744 network744 latency744 buffer744 queue744", 18),
        ["gateway744", "storage744", "network744", "latency744", "buffer744 queue744"],
    ),
    (
        ("gateway744 storage744 network744 latency744 buffer744 queue744", 28),
        ["gateway744 storage744", "network744 latency744", "buffer744 queue744"],
    ),
    (
        ("storage744 network744 latency744 buffer744 queue744 worker744", 6),
        ["storage744", "network744", "latency744", "buffer744", "queue744", "worker744"],
    ),
    (
        ("storage744 network744 latency744 buffer744 queue744 worker744", 10),
        ["storage744", "network744", "latency744", "buffer744", "queue744", "worker744"],
    ),
    (
        ("storage744 network744 latency744 buffer744 queue744 worker744", 18),
        ["storage744", "network744", "latency744", "buffer744 queue744", "worker744"],
    ),
    (
        ("storage744 network744 latency744 buffer744 queue744 worker744", 28),
        ["storage744 network744", "latency744 buffer744", "queue744 worker744"],
    ),
    (
        ("network744 latency744 buffer744 queue744 worker744 kernel744", 6),
        ["network744", "latency744", "buffer744", "queue744", "worker744", "kernel744"],
    ),
    (
        ("network744 latency744 buffer744 queue744 worker744 kernel744", 10),
        ["network744", "latency744", "buffer744", "queue744", "worker744", "kernel744"],
    ),
    (
        ("network744 latency744 buffer744 queue744 worker744 kernel744", 18),
        ["network744", "latency744", "buffer744 queue744", "worker744", "kernel744"],
    ),
    (
        ("network744 latency744 buffer744 queue744 worker744 kernel744", 28),
        ["network744 latency744", "buffer744 queue744 worker744", "kernel744"],
    ),
    (
        ("latency744 buffer744 queue744 worker744 kernel744 signal744", 6),
        ["latency744", "buffer744", "queue744", "worker744", "kernel744", "signal744"],
    ),
    (
        ("latency744 buffer744 queue744 worker744 kernel744 signal744", 10),
        ["latency744", "buffer744", "queue744", "worker744", "kernel744", "signal744"],
    ),
    (
        ("latency744 buffer744 queue744 worker744 kernel744 signal744", 18),
        ["latency744", "buffer744 queue744", "worker744", "kernel744", "signal744"],
    ),
    (
        ("latency744 buffer744 queue744 worker744 kernel744 signal744", 28),
        ["latency744 buffer744", "queue744 worker744 kernel744", "signal744"],
    ),
    (
        ("buffer744 queue744 worker744 kernel744 signal744 packet744", 6),
        ["buffer744", "queue744", "worker744", "kernel744", "signal744", "packet744"],
    ),
    (
        ("buffer744 queue744 worker744 kernel744 signal744 packet744", 10),
        ["buffer744", "queue744", "worker744", "kernel744", "signal744", "packet744"],
    ),
    (
        ("buffer744 queue744 worker744 kernel744 signal744 packet744", 18),
        ["buffer744 queue744", "worker744", "kernel744", "signal744", "packet744"],
    ),
    (
        ("buffer744 queue744 worker744 kernel744 signal744 packet744", 28),
        ["buffer744 queue744 worker744", "kernel744 signal744", "packet744"],
    ),
    (
        ("queue744 worker744 kernel744 signal744 packet744 router744", 6),
        ["queue744", "worker744", "kernel744", "signal744", "packet744", "router744"],
    ),
    (
        ("queue744 worker744 kernel744 signal744 packet744 router744", 10),
        ["queue744", "worker744", "kernel744", "signal744", "packet744", "router744"],
    ),
    (
        ("queue744 worker744 kernel744 signal744 packet744 router744", 18),
        ["queue744 worker744", "kernel744", "signal744", "packet744", "router744"],
    ),
    (
        ("queue744 worker744 kernel744 signal744 packet744 router744", 28),
        ["queue744 worker744 kernel744", "signal744 packet744", "router744"],
    ),
    (
        ("worker744 kernel744 signal744 packet744 router744 cluster744", 6),
        ["worker744", "kernel744", "signal744", "packet744", "router744", "cluster744"],
    ),
    (
        ("worker744 kernel744 signal744 packet744 router744 cluster744", 10),
        ["worker744", "kernel744", "signal744", "packet744", "router744", "cluster744"],
    ),
    (
        ("worker744 kernel744 signal744 packet744 router744 cluster744", 18),
        ["worker744", "kernel744", "signal744", "packet744", "router744", "cluster744"],
    ),
    (
        ("worker744 kernel744 signal744 packet744 router744 cluster744", 28),
        ["worker744 kernel744", "signal744 packet744", "router744 cluster744"],
    ),
    (
        ("kernel744 signal744 packet744 router744 cluster744 mirror744", 6),
        ["kernel744", "signal744", "packet744", "router744", "cluster744", "mirror744"],
    ),
    (
        ("kernel744 signal744 packet744 router744 cluster744 mirror744", 10),
        ["kernel744", "signal744", "packet744", "router744", "cluster744", "mirror744"],
    ),
    (
        ("kernel744 signal744 packet744 router744 cluster744 mirror744", 18),
        ["kernel744", "signal744", "packet744", "router744", "cluster744", "mirror744"],
    ),
    (
        ("kernel744 signal744 packet744 router744 cluster744 mirror744", 28),
        ["kernel744 signal744", "packet744 router744", "cluster744 mirror744"],
    ),
    (
        ("signal744 packet744 router744 cluster744 mirror744 filter744", 6),
        ["signal744", "packet744", "router744", "cluster744", "mirror744", "filter744"],
    ),
    (
        ("signal744 packet744 router744 cluster744 mirror744 filter744", 10),
        ["signal744", "packet744", "router744", "cluster744", "mirror744", "filter744"],
    ),
    (
        ("signal744 packet744 router744 cluster744 mirror744 filter744", 18),
        ["signal744", "packet744", "router744", "cluster744", "mirror744", "filter744"],
    ),
    (
        ("signal744 packet744 router744 cluster744 mirror744 filter744", 28),
        ["signal744 packet744", "router744 cluster744", "mirror744 filter744"],
    ),
    (
        ("packet744 router744 cluster744 mirror744 filter744 ranking744", 6),
        ["packet744", "router744", "cluster744", "mirror744", "filter744", "ranking744"],
    ),
    (
        ("packet744 router744 cluster744 mirror744 filter744 ranking744", 10),
        ["packet744", "router744", "cluster744", "mirror744", "filter744", "ranking744"],
    ),
    (
        ("packet744 router744 cluster744 mirror744 filter744 ranking744", 18),
        ["packet744", "router744", "cluster744", "mirror744", "filter744", "ranking744"],
    ),
    (
        ("packet744 router744 cluster744 mirror744 filter744 ranking744", 28),
        ["packet744 router744", "cluster744 mirror744", "filter744 ranking744"],
    ),
    (
        ("router744 cluster744 mirror744 filter744 ranking744 encoding744", 6),
        ["router744", "cluster744", "mirror744", "filter744", "ranking744", "encoding744"],
    ),
    (
        ("router744 cluster744 mirror744 filter744 ranking744 encoding744", 10),
        ["router744", "cluster744", "mirror744", "filter744", "ranking744", "encoding744"],
    ),
    (
        ("router744 cluster744 mirror744 filter744 ranking744 encoding744", 18),
        ["router744", "cluster744", "mirror744", "filter744", "ranking744", "encoding744"],
    ),
    (
        ("router744 cluster744 mirror744 filter744 ranking744 encoding744", 28),
        ["router744 cluster744", "mirror744 filter744", "ranking744 encoding744"],
    ),
    (
        ("cluster744 mirror744 filter744 ranking744 encoding744 mapping744", 6),
        ["cluster744", "mirror744", "filter744", "ranking744", "encoding744", "mapping744"],
    ),
    (
        ("cluster744 mirror744 filter744 ranking744 encoding744 mapping744", 10),
        ["cluster744", "mirror744", "filter744", "ranking744", "encoding744", "mapping744"],
    ),
    (
        ("cluster744 mirror744 filter744 ranking744 encoding744 mapping744", 18),
        ["cluster744", "mirror744", "filter744", "ranking744", "encoding744", "mapping744"],
    ),
    (
        ("cluster744 mirror744 filter744 ranking744 encoding744 mapping744", 28),
        ["cluster744 mirror744", "filter744 ranking744", "encoding744 mapping744"],
    ),
    (
        ("mirror744 filter744 ranking744 encoding744 mapping744 record744", 6),
        ["mirror744", "filter744", "ranking744", "encoding744", "mapping744", "record744"],
    ),
    (
        ("mirror744 filter744 ranking744 encoding744 mapping744 record744", 10),
        ["mirror744", "filter744", "ranking744", "encoding744", "mapping744", "record744"],
    ),
    (
        ("mirror744 filter744 ranking744 encoding744 mapping744 record744", 18),
        ["mirror744", "filter744", "ranking744", "encoding744", "mapping744", "record744"],
    ),
    (
        ("mirror744 filter744 ranking744 encoding744 mapping744 record744", 28),
        ["mirror744 filter744", "ranking744 encoding744", "mapping744 record744"],
    ),
    (
        ("filter744 ranking744 encoding744 mapping744 record744 candle744", 6),
        ["filter744", "ranking744", "encoding744", "mapping744", "record744", "candle744"],
    ),
    (
        ("filter744 ranking744 encoding744 mapping744 record744 candle744", 10),
        ["filter744", "ranking744", "encoding744", "mapping744", "record744", "candle744"],
    ),
    (
        ("filter744 ranking744 encoding744 mapping744 record744 candle744", 18),
        ["filter744", "ranking744", "encoding744", "mapping744", "record744", "candle744"],
    ),
    (
        ("filter744 ranking744 encoding744 mapping744 record744 candle744", 28),
        ["filter744 ranking744", "encoding744 mapping744", "record744 candle744"],
    ),
    (
        ("ranking744 encoding744 mapping744 record744 candle744 thread744", 6),
        ["ranking744", "encoding744", "mapping744", "record744", "candle744", "thread744"],
    ),
    (
        ("ranking744 encoding744 mapping744 record744 candle744 thread744", 10),
        ["ranking744", "encoding744", "mapping744", "record744", "candle744", "thread744"],
    ),
    (
        ("ranking744 encoding744 mapping744 record744 candle744 thread744", 18),
        ["ranking744", "encoding744", "mapping744", "record744", "candle744", "thread744"],
    ),
    (
        ("ranking744 encoding744 mapping744 record744 candle744 thread744", 28),
        ["ranking744 encoding744", "mapping744 record744", "candle744 thread744"],
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
