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
        ("round 65: the quick brown fox jumps over the lazy dog", 4),
        ["round", "65:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 65: the quick brown fox jumps over the lazy dog", 8),
        ["round", "65: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 65: the quick brown fox jumps over the lazy dog", 12),
        ["round 65:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 65: the quick brown fox jumps over the lazy dog", 16),
        ["round 65: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 65: the quick brown fox jumps over the lazy dog", 24),
        ["round 65: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 65: the quick brown fox jumps over the lazy dog", 32),
        ["round 65: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 65: agentuniverse is a framework for multi agents", 4),
        ["round", "65:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 65: agentuniverse is a framework for multi agents", 8),
        ["round", "65:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 65: agentuniverse is a framework for multi agents", 12),
        ["round 65:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 65: agentuniverse is a framework for multi agents", 16),
        ["round 65:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 65: agentuniverse is a framework for multi agents", 24),
        ["round 65: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 65: agentuniverse is a framework for multi agents", 32),
        ["round 65: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 65: knowledge stored as vectors enables retrieval", 4),
        ["round", "65:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 65: knowledge stored as vectors enables retrieval", 8),
        ["round", "65:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 65: knowledge stored as vectors enables retrieval", 12),
        ["round 65:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 65: knowledge stored as vectors enables retrieval", 16),
        ["round 65:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 65: knowledge stored as vectors enables retrieval", 24),
        ["round 65: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 65: knowledge stored as vectors enables retrieval", 32),
        ["round 65: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 65: the processor reads the record then stops", 4),
        ["round", "65:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 65: the processor reads the record then stops", 8),
        ["round", "65: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 65: the processor reads the record then stops", 12),
        ["round 65:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 65: the processor reads the record then stops", 16),
        ["round 65: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 65: the processor reads the record then stops", 24),
        ["round 65: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 65: the processor reads the record then stops", 32),
        ["round 65: the processor reads", "the record then stops"],
    ),
    (
        ("round 65: a worker pulls the next task from the queue", 4),
        ["round", "65:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 65: a worker pulls the next task from the queue", 8),
        ["round", "65: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 65: a worker pulls the next task from the queue", 12),
        ["round 65: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 65: a worker pulls the next task from the queue", 16),
        ["round 65: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 65: a worker pulls the next task from the queue", 24),
        ["round 65: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 65: a worker pulls the next task from the queue", 32),
        ["round 65: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 65: signals travel through the network layer", 4),
        ["round", "65:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 65: signals travel through the network layer", 8),
        ["round", "65:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 65: signals travel through the network layer", 12),
        ["round 65:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 65: signals travel through the network layer", 16),
        ["round 65:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 65: signals travel through the network layer", 24),
        ["round 65: signals travel", "through the network", "layer"],
    ),
    (
        ("round 65: signals travel through the network layer", 32),
        ["round 65: signals travel through", "the network layer"],
    ),
    (
        ("round 65: the gateway routes each request by policy", 4),
        ["round", "65:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 65: the gateway routes each request by policy", 8),
        ["round", "65: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 65: the gateway routes each request by policy", 12),
        ["round 65:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 65: the gateway routes each request by policy", 16),
        ["round 65: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 65: the gateway routes each request by policy", 24),
        ["round 65: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 65: the gateway routes each request by policy", 32),
        ["round 65: the gateway routes", "each request by policy"],
    ),
    (
        ("round 65: memory grows until the buffer is full", 4),
        ["round", "65:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 65: memory grows until the buffer is full", 8),
        ["round", "65:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 65: memory grows until the buffer is full", 12),
        ["round 65:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 65: memory grows until the buffer is full", 16),
        ["round 65: memory", "grows until the", "buffer is full"],
    ),
    (("round 65: memory grows until the buffer is full", 24), ["round 65: memory grows", "until the buffer is full"]),
    (("round 65: memory grows until the buffer is full", 32), ["round 65: memory grows until the", "buffer is full"]),
    (
        ("round 65: the cluster mirrors every packet twice", 4),
        ["round", "65:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 65: the cluster mirrors every packet twice", 8),
        ["round", "65: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 65: the cluster mirrors every packet twice", 12),
        ["round 65:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 65: the cluster mirrors every packet twice", 16),
        ["round 65: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 65: the cluster mirrors every packet twice", 24),
        ["round 65: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 65: the cluster mirrors every packet twice", 32), ["round 65: the cluster mirrors", "every packet twice"]),
    (
        ("round 65: ranking uses tokens learned from the corpus", 4),
        ["round", "65:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 65: ranking uses tokens learned from the corpus", 8),
        ["round", "65:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 65: ranking uses tokens learned from the corpus", 12),
        ["round 65:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 65: ranking uses tokens learned from the corpus", 16),
        ["round 65:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 65: ranking uses tokens learned from the corpus", 24),
        ["round 65: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 65: ranking uses tokens learned from the corpus", 32),
        ["round 65: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 65: a long session ends when the candle dies", 4),
        ["round", "65:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 65: a long session ends when the candle dies", 8),
        ["round", "65: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 65: a long session ends when the candle dies", 12),
        ["round 65: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 65: a long session ends when the candle dies", 16),
        ["round 65: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 65: a long session ends when the candle dies", 24),
        ["round 65: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 65: a long session ends when the candle dies", 32),
        ["round 65: a long session ends", "when the candle dies"],
    ),
    (
        ("round 65: encode the prompt then map the result", 4),
        ["round", "65:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 65: encode the prompt then map the result", 8),
        ["round", "65:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 65: encode the prompt then map the result", 12),
        ["round 65:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 65: encode the prompt then map the result", 16),
        ["round 65: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 65: encode the prompt then map the result", 24),
        ["round 65: encode the", "prompt then map the", "result"],
    ),
    (("round 65: encode the prompt then map the result", 32), ["round 65: encode the prompt then", "map the result"]),
    (
        ("round 65: the kernel wakes the worker at dawn", 4),
        ["round", "65:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 65: the kernel wakes the worker at dawn", 8),
        ["round", "65: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 65: the kernel wakes the worker at dawn", 12),
        ["round 65:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 65: the kernel wakes the worker at dawn", 16), ["round 65: the", "kernel wakes the", "worker at dawn"]),
    (("round 65: the kernel wakes the worker at dawn", 24), ["round 65: the kernel", "wakes the worker at dawn"]),
    (("round 65: the kernel wakes the worker at dawn", 32), ["round 65: the kernel wakes the", "worker at dawn"]),
    (
        ("round 65: service latency drops after the patch", 4),
        ["round", "65:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 65: service latency drops after the patch", 8),
        ["round", "65:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 65: service latency drops after the patch", 12),
        ["round 65:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 65: service latency drops after the patch", 16),
        ["round 65:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 65: service latency drops after the patch", 24),
        ["round 65: service", "latency drops after the", "patch"],
    ),
    (("round 65: service latency drops after the patch", 32), ["round 65: service latency drops", "after the patch"]),
    (
        ("round 65: the library caches every vector it sees", 4),
        ["round", "65:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 65: the library caches every vector it sees", 8),
        ["round", "65: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 65: the library caches every vector it sees", 12),
        ["round 65:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 65: the library caches every vector it sees", 16),
        ["round 65: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 65: the library caches every vector it sees", 24),
        ["round 65: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 65: the library caches every vector it sees", 32),
        ["round 65: the library caches", "every vector it sees"],
    ),
    (
        ("round 65: agents argue then the debate resolves", 4),
        ["round", "65:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 65: agents argue then the debate resolves", 8),
        ["round", "65:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 65: agents argue then the debate resolves", 12),
        ["round 65:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 65: agents argue then the debate resolves", 16),
        ["round 65: agents", "argue then the", "debate resolves"],
    ),
    (("round 65: agents argue then the debate resolves", 24), ["round 65: agents argue", "then the debate resolves"]),
    (("round 65: agents argue then the debate resolves", 32), ["round 65: agents argue then the", "debate resolves"]),
    (
        ("round 65: the filter keeps only strong matches", 4),
        ["round", "65:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 65: the filter keeps only strong matches", 8),
        ["round", "65: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 65: the filter keeps only strong matches", 12),
        ["round 65:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 65: the filter keeps only strong matches", 16),
        ["round 65: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 65: the filter keeps only strong matches", 24), ["round 65: the filter", "keeps only strong", "matches"]),
    (("round 65: the filter keeps only strong matches", 32), ["round 65: the filter keeps only", "strong matches"]),
    (
        ("round 65: the model answers with a short reply", 4),
        ["round", "65:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 65: the model answers with a short reply", 8),
        ["round", "65: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 65: the model answers with a short reply", 12),
        ["round 65:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 65: the model answers with a short reply", 16),
        ["round 65: the", "model answers", "with a short", "reply"],
    ),
    (("round 65: the model answers with a short reply", 24), ["round 65: the model", "answers with a short", "reply"]),
    (("round 65: the model answers with a short reply", 32), ["round 65: the model answers with", "a short reply"]),
    (
        ("round 65: the recorder stores the reasoning trace", 4),
        ["round", "65:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 65: the recorder stores the reasoning trace", 8),
        ["round", "65: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 65: the recorder stores the reasoning trace", 12),
        ["round 65:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 65: the recorder stores the reasoning trace", 16),
        ["round 65: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 65: the recorder stores the reasoning trace", 24),
        ["round 65: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 65: the recorder stores the reasoning trace", 32),
        ["round 65: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 65: the angel watches the processor run", 4),
        ["round", "65:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 65: the angel watches the processor run", 8),
        ["round", "65: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 65: the angel watches the processor run", 12),
        ["round 65:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 65: the angel watches the processor run", 16), ["round 65: the", "angel watches", "the processor", "run"]),
    (("round 65: the angel watches the processor run", 24), ["round 65: the angel", "watches the processor", "run"]),
    (("round 65: the angel watches the processor run", 32), ["round 65: the angel watches the", "processor run"]),
    (
        ("round 65: angle of the vector decides the match", 4),
        ["round", "65:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 65: angle of the vector decides the match", 8),
        ["round", "65:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 65: angle of the vector decides the match", 12),
        ["round 65:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 65: angle of the vector decides the match", 16),
        ["round 65: angle", "of the vector", "decides the", "match"],
    ),
    (("round 65: angle of the vector decides the match", 24), ["round 65: angle of the", "vector decides the match"]),
    (("round 65: angle of the vector decides the match", 32), ["round 65: angle of the vector", "decides the match"]),
    (
        ("round 65: the candle burns twice as long at night", 4),
        ["round", "65:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 65: the candle burns twice as long at night", 8),
        ["round", "65: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 65: the candle burns twice as long at night", 12),
        ["round 65:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 65: the candle burns twice as long at night", 16),
        ["round 65: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 65: the candle burns twice as long at night", 24),
        ["round 65: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 65: the candle burns twice as long at night", 32),
        ["round 65: the candle burns twice", "as long at night"],
    ),
    (
        ("round 65: a mirror of the universe in one line", 4),
        ["round", "65:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 65: a mirror of the universe in one line", 8),
        ["round", "65: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 65: a mirror of the universe in one line", 12),
        ["round 65: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 65: a mirror of the universe in one line", 16),
        ["round 65: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 65: a mirror of the universe in one line", 24), ["round 65: a mirror of", "the universe in one line"]),
    (("round 65: a mirror of the universe in one line", 32), ["round 65: a mirror of the", "universe in one line"]),
    (
        ("round 65: the queue drains before the storm", 4),
        ["round", "65:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 65: the queue drains before the storm", 8),
        ["round", "65: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 65: the queue drains before the storm", 12), ["round 65:", "the queue", "drains", "before the", "storm"]),
    (("round 65: the queue drains before the storm", 16), ["round 65: the", "queue drains", "before the storm"]),
    (("round 65: the queue drains before the storm", 24), ["round 65: the queue", "drains before the storm"]),
    (("round 65: the queue drains before the storm", 32), ["round 65: the queue drains", "before the storm"]),
    (
        ("kitten65 sitting65 agent65 angle65 universe65 memory65", 6),
        ["kitten65", "sitting65", "agent65", "angle65", "universe65", "memory65"],
    ),
    (
        ("kitten65 sitting65 agent65 angle65 universe65 memory65", 10),
        ["kitten65", "sitting65", "agent65", "angle65", "universe65", "memory65"],
    ),
    (
        ("kitten65 sitting65 agent65 angle65 universe65 memory65", 18),
        ["kitten65 sitting65", "agent65 angle65", "universe65", "memory65"],
    ),
    (
        ("kitten65 sitting65 agent65 angle65 universe65 memory65", 28),
        ["kitten65 sitting65 agent65", "angle65 universe65 memory65"],
    ),
    (
        ("sitting65 agent65 angle65 universe65 memory65 stream65", 6),
        ["sitting65", "agent65", "angle65", "universe65", "memory65", "stream65"],
    ),
    (
        ("sitting65 agent65 angle65 universe65 memory65 stream65", 10),
        ["sitting65", "agent65", "angle65", "universe65", "memory65", "stream65"],
    ),
    (
        ("sitting65 agent65 angle65 universe65 memory65 stream65", 18),
        ["sitting65 agent65", "angle65 universe65", "memory65 stream65"],
    ),
    (
        ("sitting65 agent65 angle65 universe65 memory65 stream65", 28),
        ["sitting65 agent65 angle65", "universe65 memory65 stream65"],
    ),
    (
        ("agent65 angle65 universe65 memory65 stream65 context65", 6),
        ["agent65", "angle65", "universe65", "memory65", "stream65", "context65"],
    ),
    (
        ("agent65 angle65 universe65 memory65 stream65 context65", 10),
        ["agent65", "angle65", "universe65", "memory65", "stream65", "context65"],
    ),
    (
        ("agent65 angle65 universe65 memory65 stream65 context65", 18),
        ["agent65 angle65", "universe65", "memory65 stream65", "context65"],
    ),
    (
        ("agent65 angle65 universe65 memory65 stream65 context65", 28),
        ["agent65 angle65 universe65", "memory65 stream65 context65"],
    ),
    (
        ("angle65 universe65 memory65 stream65 context65 knowledge65", 6),
        ["angle65", "universe65", "memory65", "stream65", "context65", "knowledge65"],
    ),
    (
        ("angle65 universe65 memory65 stream65 context65 knowledge65", 10),
        ["angle65", "universe65", "memory65", "stream65", "context65", "knowledge65"],
    ),
    (
        ("angle65 universe65 memory65 stream65 context65 knowledge65", 18),
        ["angle65 universe65", "memory65 stream65", "context65", "knowledge65"],
    ),
    (
        ("angle65 universe65 memory65 stream65 context65 knowledge65", 28),
        ["angle65 universe65 memory65", "stream65 context65", "knowledge65"],
    ),
    (
        ("universe65 memory65 stream65 context65 knowledge65 vector65", 6),
        ["universe65", "memory65", "stream65", "context65", "knowledge65", "vector65"],
    ),
    (
        ("universe65 memory65 stream65 context65 knowledge65 vector65", 10),
        ["universe65", "memory65", "stream65", "context65", "knowledge65", "vector65"],
    ),
    (
        ("universe65 memory65 stream65 context65 knowledge65 vector65", 18),
        ["universe65", "memory65 stream65", "context65", "knowledge65", "vector65"],
    ),
    (
        ("universe65 memory65 stream65 context65 knowledge65 vector65", 28),
        ["universe65 memory65 stream65", "context65 knowledge65", "vector65"],
    ),
    (
        ("memory65 stream65 context65 knowledge65 vector65 processor65", 6),
        ["memory65", "stream65", "context65", "knowledge65", "vector65", "processor65"],
    ),
    (
        ("memory65 stream65 context65 knowledge65 vector65 processor65", 10),
        ["memory65", "stream65", "context65", "knowledge65", "vector65", "processor65"],
    ),
    (
        ("memory65 stream65 context65 knowledge65 vector65 processor65", 18),
        ["memory65 stream65", "context65", "knowledge65", "vector65", "processor65"],
    ),
    (
        ("memory65 stream65 context65 knowledge65 vector65 processor65", 28),
        ["memory65 stream65 context65", "knowledge65 vector65", "processor65"],
    ),
    (
        ("stream65 context65 knowledge65 vector65 processor65 reasoning65", 6),
        ["stream65", "context65", "knowledge65", "vector65", "processor65", "reasoning65"],
    ),
    (
        ("stream65 context65 knowledge65 vector65 processor65 reasoning65", 10),
        ["stream65", "context65", "knowledge65", "vector65", "processor65", "reasoning65"],
    ),
    (
        ("stream65 context65 knowledge65 vector65 processor65 reasoning65", 18),
        ["stream65 context65", "knowledge65", "vector65", "processor65", "reasoning65"],
    ),
    (
        ("stream65 context65 knowledge65 vector65 processor65 reasoning65", 28),
        ["stream65 context65", "knowledge65 vector65", "processor65 reasoning65"],
    ),
    (
        ("context65 knowledge65 vector65 processor65 reasoning65 machine65", 6),
        ["context65", "knowledge65", "vector65", "processor65", "reasoning65", "machine65"],
    ),
    (
        ("context65 knowledge65 vector65 processor65 reasoning65 machine65", 10),
        ["context65", "knowledge65", "vector65", "processor65", "reasoning65", "machine65"],
    ),
    (
        ("context65 knowledge65 vector65 processor65 reasoning65 machine65", 18),
        ["context65", "knowledge65", "vector65", "processor65", "reasoning65", "machine65"],
    ),
    (
        ("context65 knowledge65 vector65 processor65 reasoning65 machine65", 28),
        ["context65 knowledge65", "vector65 processor65", "reasoning65 machine65"],
    ),
    (
        ("knowledge65 vector65 processor65 reasoning65 machine65 learning65", 6),
        ["knowledge65", "vector65", "processor65", "reasoning65", "machine65", "learning65"],
    ),
    (
        ("knowledge65 vector65 processor65 reasoning65 machine65 learning65", 10),
        ["knowledge65", "vector65", "processor65", "reasoning65", "machine65", "learning65"],
    ),
    (
        ("knowledge65 vector65 processor65 reasoning65 machine65 learning65", 18),
        ["knowledge65", "vector65", "processor65", "reasoning65", "machine65", "learning65"],
    ),
    (
        ("knowledge65 vector65 processor65 reasoning65 machine65 learning65", 28),
        ["knowledge65 vector65", "processor65 reasoning65", "machine65 learning65"],
    ),
    (
        ("vector65 processor65 reasoning65 machine65 learning65 model65", 6),
        ["vector65", "processor65", "reasoning65", "machine65", "learning65", "model65"],
    ),
    (
        ("vector65 processor65 reasoning65 machine65 learning65 model65", 10),
        ["vector65", "processor65", "reasoning65", "machine65", "learning65", "model65"],
    ),
    (
        ("vector65 processor65 reasoning65 machine65 learning65 model65", 18),
        ["vector65", "processor65", "reasoning65", "machine65", "learning65 model65"],
    ),
    (
        ("vector65 processor65 reasoning65 machine65 learning65 model65", 28),
        ["vector65 processor65", "reasoning65 machine65", "learning65 model65"],
    ),
    (
        ("processor65 reasoning65 machine65 learning65 model65 token65", 6),
        ["processor65", "reasoning65", "machine65", "learning65", "model65", "token65"],
    ),
    (
        ("processor65 reasoning65 machine65 learning65 model65 token65", 10),
        ["processor65", "reasoning65", "machine65", "learning65", "model65", "token65"],
    ),
    (
        ("processor65 reasoning65 machine65 learning65 model65 token65", 18),
        ["processor65", "reasoning65", "machine65", "learning65 model65", "token65"],
    ),
    (
        ("processor65 reasoning65 machine65 learning65 model65 token65", 28),
        ["processor65 reasoning65", "machine65 learning65 model65", "token65"],
    ),
    (
        ("reasoning65 machine65 learning65 model65 token65 prompt65", 6),
        ["reasoning65", "machine65", "learning65", "model65", "token65", "prompt65"],
    ),
    (
        ("reasoning65 machine65 learning65 model65 token65 prompt65", 10),
        ["reasoning65", "machine65", "learning65", "model65", "token65", "prompt65"],
    ),
    (
        ("reasoning65 machine65 learning65 model65 token65 prompt65", 18),
        ["reasoning65", "machine65", "learning65 model65", "token65 prompt65"],
    ),
    (
        ("reasoning65 machine65 learning65 model65 token65 prompt65", 28),
        ["reasoning65 machine65", "learning65 model65 token65", "prompt65"],
    ),
    (
        ("machine65 learning65 model65 token65 prompt65 session65", 6),
        ["machine65", "learning65", "model65", "token65", "prompt65", "session65"],
    ),
    (
        ("machine65 learning65 model65 token65 prompt65 session65", 10),
        ["machine65", "learning65", "model65", "token65", "prompt65", "session65"],
    ),
    (
        ("machine65 learning65 model65 token65 prompt65 session65", 18),
        ["machine65", "learning65 model65", "token65 prompt65", "session65"],
    ),
    (
        ("machine65 learning65 model65 token65 prompt65 session65", 28),
        ["machine65 learning65 model65", "token65 prompt65 session65"],
    ),
    (
        ("learning65 model65 token65 prompt65 session65 library65", 6),
        ["learning65", "model65", "token65", "prompt65", "session65", "library65"],
    ),
    (
        ("learning65 model65 token65 prompt65 session65 library65", 10),
        ["learning65", "model65", "token65", "prompt65", "session65", "library65"],
    ),
    (
        ("learning65 model65 token65 prompt65 session65 library65", 18),
        ["learning65 model65", "token65 prompt65", "session65", "library65"],
    ),
    (
        ("learning65 model65 token65 prompt65 session65 library65", 28),
        ["learning65 model65 token65", "prompt65 session65 library65"],
    ),
    (
        ("model65 token65 prompt65 session65 library65 service65", 6),
        ["model65", "token65", "prompt65", "session65", "library65", "service65"],
    ),
    (
        ("model65 token65 prompt65 session65 library65 service65", 10),
        ["model65", "token65", "prompt65", "session65", "library65", "service65"],
    ),
    (
        ("model65 token65 prompt65 session65 library65 service65", 18),
        ["model65 token65", "prompt65 session65", "library65", "service65"],
    ),
    (
        ("model65 token65 prompt65 session65 library65 service65", 28),
        ["model65 token65 prompt65", "session65 library65", "service65"],
    ),
    (
        ("token65 prompt65 session65 library65 service65 gateway65", 6),
        ["token65", "prompt65", "session65", "library65", "service65", "gateway65"],
    ),
    (
        ("token65 prompt65 session65 library65 service65 gateway65", 10),
        ["token65", "prompt65", "session65", "library65", "service65", "gateway65"],
    ),
    (
        ("token65 prompt65 session65 library65 service65 gateway65", 18),
        ["token65 prompt65", "session65", "library65", "service65", "gateway65"],
    ),
    (
        ("token65 prompt65 session65 library65 service65 gateway65", 28),
        ["token65 prompt65 session65", "library65 service65", "gateway65"],
    ),
    (
        ("prompt65 session65 library65 service65 gateway65 storage65", 6),
        ["prompt65", "session65", "library65", "service65", "gateway65", "storage65"],
    ),
    (
        ("prompt65 session65 library65 service65 gateway65 storage65", 10),
        ["prompt65", "session65", "library65", "service65", "gateway65", "storage65"],
    ),
    (
        ("prompt65 session65 library65 service65 gateway65 storage65", 18),
        ["prompt65 session65", "library65", "service65", "gateway65", "storage65"],
    ),
    (
        ("prompt65 session65 library65 service65 gateway65 storage65", 28),
        ["prompt65 session65 library65", "service65 gateway65", "storage65"],
    ),
    (
        ("session65 library65 service65 gateway65 storage65 network65", 6),
        ["session65", "library65", "service65", "gateway65", "storage65", "network65"],
    ),
    (
        ("session65 library65 service65 gateway65 storage65 network65", 10),
        ["session65", "library65", "service65", "gateway65", "storage65", "network65"],
    ),
    (
        ("session65 library65 service65 gateway65 storage65 network65", 18),
        ["session65", "library65", "service65", "gateway65", "storage65", "network65"],
    ),
    (
        ("session65 library65 service65 gateway65 storage65 network65", 28),
        ["session65 library65", "service65 gateway65", "storage65 network65"],
    ),
    (
        ("library65 service65 gateway65 storage65 network65 latency65", 6),
        ["library65", "service65", "gateway65", "storage65", "network65", "latency65"],
    ),
    (
        ("library65 service65 gateway65 storage65 network65 latency65", 10),
        ["library65", "service65", "gateway65", "storage65", "network65", "latency65"],
    ),
    (
        ("library65 service65 gateway65 storage65 network65 latency65", 18),
        ["library65", "service65", "gateway65", "storage65", "network65", "latency65"],
    ),
    (
        ("library65 service65 gateway65 storage65 network65 latency65", 28),
        ["library65 service65", "gateway65 storage65", "network65 latency65"],
    ),
    (
        ("service65 gateway65 storage65 network65 latency65 buffer65", 6),
        ["service65", "gateway65", "storage65", "network65", "latency65", "buffer65"],
    ),
    (
        ("service65 gateway65 storage65 network65 latency65 buffer65", 10),
        ["service65", "gateway65", "storage65", "network65", "latency65", "buffer65"],
    ),
    (
        ("service65 gateway65 storage65 network65 latency65 buffer65", 18),
        ["service65", "gateway65", "storage65", "network65", "latency65 buffer65"],
    ),
    (
        ("service65 gateway65 storage65 network65 latency65 buffer65", 28),
        ["service65 gateway65", "storage65 network65", "latency65 buffer65"],
    ),
    (
        ("gateway65 storage65 network65 latency65 buffer65 queue65", 6),
        ["gateway65", "storage65", "network65", "latency65", "buffer65", "queue65"],
    ),
    (
        ("gateway65 storage65 network65 latency65 buffer65 queue65", 10),
        ["gateway65", "storage65", "network65", "latency65", "buffer65", "queue65"],
    ),
    (
        ("gateway65 storage65 network65 latency65 buffer65 queue65", 18),
        ["gateway65", "storage65", "network65", "latency65 buffer65", "queue65"],
    ),
    (
        ("gateway65 storage65 network65 latency65 buffer65 queue65", 28),
        ["gateway65 storage65", "network65 latency65 buffer65", "queue65"],
    ),
    (
        ("storage65 network65 latency65 buffer65 queue65 worker65", 6),
        ["storage65", "network65", "latency65", "buffer65", "queue65", "worker65"],
    ),
    (
        ("storage65 network65 latency65 buffer65 queue65 worker65", 10),
        ["storage65", "network65", "latency65", "buffer65", "queue65", "worker65"],
    ),
    (
        ("storage65 network65 latency65 buffer65 queue65 worker65", 18),
        ["storage65", "network65", "latency65 buffer65", "queue65 worker65"],
    ),
    (
        ("storage65 network65 latency65 buffer65 queue65 worker65", 28),
        ["storage65 network65", "latency65 buffer65 queue65", "worker65"],
    ),
    (
        ("network65 latency65 buffer65 queue65 worker65 kernel65", 6),
        ["network65", "latency65", "buffer65", "queue65", "worker65", "kernel65"],
    ),
    (
        ("network65 latency65 buffer65 queue65 worker65 kernel65", 10),
        ["network65", "latency65", "buffer65", "queue65", "worker65", "kernel65"],
    ),
    (
        ("network65 latency65 buffer65 queue65 worker65 kernel65", 18),
        ["network65", "latency65 buffer65", "queue65 worker65", "kernel65"],
    ),
    (
        ("network65 latency65 buffer65 queue65 worker65 kernel65", 28),
        ["network65 latency65 buffer65", "queue65 worker65 kernel65"],
    ),
    (
        ("latency65 buffer65 queue65 worker65 kernel65 signal65", 6),
        ["latency65", "buffer65", "queue65", "worker65", "kernel65", "signal65"],
    ),
    (
        ("latency65 buffer65 queue65 worker65 kernel65 signal65", 10),
        ["latency65", "buffer65", "queue65", "worker65", "kernel65", "signal65"],
    ),
    (
        ("latency65 buffer65 queue65 worker65 kernel65 signal65", 18),
        ["latency65 buffer65", "queue65 worker65", "kernel65 signal65"],
    ),
    (
        ("latency65 buffer65 queue65 worker65 kernel65 signal65", 28),
        ["latency65 buffer65 queue65", "worker65 kernel65 signal65"],
    ),
    (
        ("buffer65 queue65 worker65 kernel65 signal65 packet65", 6),
        ["buffer65", "queue65", "worker65", "kernel65", "signal65", "packet65"],
    ),
    (
        ("buffer65 queue65 worker65 kernel65 signal65 packet65", 10),
        ["buffer65", "queue65", "worker65", "kernel65", "signal65", "packet65"],
    ),
    (
        ("buffer65 queue65 worker65 kernel65 signal65 packet65", 18),
        ["buffer65 queue65", "worker65 kernel65", "signal65 packet65"],
    ),
    (
        ("buffer65 queue65 worker65 kernel65 signal65 packet65", 28),
        ["buffer65 queue65 worker65", "kernel65 signal65 packet65"],
    ),
    (
        ("queue65 worker65 kernel65 signal65 packet65 router65", 6),
        ["queue65", "worker65", "kernel65", "signal65", "packet65", "router65"],
    ),
    (
        ("queue65 worker65 kernel65 signal65 packet65 router65", 10),
        ["queue65", "worker65", "kernel65", "signal65", "packet65", "router65"],
    ),
    (
        ("queue65 worker65 kernel65 signal65 packet65 router65", 18),
        ["queue65 worker65", "kernel65 signal65", "packet65 router65"],
    ),
    (
        ("queue65 worker65 kernel65 signal65 packet65 router65", 28),
        ["queue65 worker65 kernel65", "signal65 packet65 router65"],
    ),
    (
        ("worker65 kernel65 signal65 packet65 router65 cluster65", 6),
        ["worker65", "kernel65", "signal65", "packet65", "router65", "cluster65"],
    ),
    (
        ("worker65 kernel65 signal65 packet65 router65 cluster65", 10),
        ["worker65", "kernel65", "signal65", "packet65", "router65", "cluster65"],
    ),
    (
        ("worker65 kernel65 signal65 packet65 router65 cluster65", 18),
        ["worker65 kernel65", "signal65 packet65", "router65 cluster65"],
    ),
    (
        ("worker65 kernel65 signal65 packet65 router65 cluster65", 28),
        ["worker65 kernel65 signal65", "packet65 router65 cluster65"],
    ),
    (
        ("kernel65 signal65 packet65 router65 cluster65 mirror65", 6),
        ["kernel65", "signal65", "packet65", "router65", "cluster65", "mirror65"],
    ),
    (
        ("kernel65 signal65 packet65 router65 cluster65 mirror65", 10),
        ["kernel65", "signal65", "packet65", "router65", "cluster65", "mirror65"],
    ),
    (
        ("kernel65 signal65 packet65 router65 cluster65 mirror65", 18),
        ["kernel65 signal65", "packet65 router65", "cluster65 mirror65"],
    ),
    (
        ("kernel65 signal65 packet65 router65 cluster65 mirror65", 28),
        ["kernel65 signal65 packet65", "router65 cluster65 mirror65"],
    ),
    (
        ("signal65 packet65 router65 cluster65 mirror65 filter65", 6),
        ["signal65", "packet65", "router65", "cluster65", "mirror65", "filter65"],
    ),
    (
        ("signal65 packet65 router65 cluster65 mirror65 filter65", 10),
        ["signal65", "packet65", "router65", "cluster65", "mirror65", "filter65"],
    ),
    (
        ("signal65 packet65 router65 cluster65 mirror65 filter65", 18),
        ["signal65 packet65", "router65 cluster65", "mirror65 filter65"],
    ),
    (
        ("signal65 packet65 router65 cluster65 mirror65 filter65", 28),
        ["signal65 packet65 router65", "cluster65 mirror65 filter65"],
    ),
    (
        ("packet65 router65 cluster65 mirror65 filter65 ranking65", 6),
        ["packet65", "router65", "cluster65", "mirror65", "filter65", "ranking65"],
    ),
    (
        ("packet65 router65 cluster65 mirror65 filter65 ranking65", 10),
        ["packet65", "router65", "cluster65", "mirror65", "filter65", "ranking65"],
    ),
    (
        ("packet65 router65 cluster65 mirror65 filter65 ranking65", 18),
        ["packet65 router65", "cluster65 mirror65", "filter65 ranking65"],
    ),
    (
        ("packet65 router65 cluster65 mirror65 filter65 ranking65", 28),
        ["packet65 router65 cluster65", "mirror65 filter65 ranking65"],
    ),
    (
        ("router65 cluster65 mirror65 filter65 ranking65 encoding65", 6),
        ["router65", "cluster65", "mirror65", "filter65", "ranking65", "encoding65"],
    ),
    (
        ("router65 cluster65 mirror65 filter65 ranking65 encoding65", 10),
        ["router65", "cluster65", "mirror65", "filter65", "ranking65", "encoding65"],
    ),
    (
        ("router65 cluster65 mirror65 filter65 ranking65 encoding65", 18),
        ["router65 cluster65", "mirror65 filter65", "ranking65", "encoding65"],
    ),
    (
        ("router65 cluster65 mirror65 filter65 ranking65 encoding65", 28),
        ["router65 cluster65 mirror65", "filter65 ranking65", "encoding65"],
    ),
    (
        ("cluster65 mirror65 filter65 ranking65 encoding65 mapping65", 6),
        ["cluster65", "mirror65", "filter65", "ranking65", "encoding65", "mapping65"],
    ),
    (
        ("cluster65 mirror65 filter65 ranking65 encoding65 mapping65", 10),
        ["cluster65", "mirror65", "filter65", "ranking65", "encoding65", "mapping65"],
    ),
    (
        ("cluster65 mirror65 filter65 ranking65 encoding65 mapping65", 18),
        ["cluster65 mirror65", "filter65 ranking65", "encoding65", "mapping65"],
    ),
    (
        ("cluster65 mirror65 filter65 ranking65 encoding65 mapping65", 28),
        ["cluster65 mirror65 filter65", "ranking65 encoding65", "mapping65"],
    ),
    (
        ("mirror65 filter65 ranking65 encoding65 mapping65 record65", 6),
        ["mirror65", "filter65", "ranking65", "encoding65", "mapping65", "record65"],
    ),
    (
        ("mirror65 filter65 ranking65 encoding65 mapping65 record65", 10),
        ["mirror65", "filter65", "ranking65", "encoding65", "mapping65", "record65"],
    ),
    (
        ("mirror65 filter65 ranking65 encoding65 mapping65 record65", 18),
        ["mirror65 filter65", "ranking65", "encoding65", "mapping65 record65"],
    ),
    (
        ("mirror65 filter65 ranking65 encoding65 mapping65 record65", 28),
        ["mirror65 filter65 ranking65", "encoding65 mapping65", "record65"],
    ),
    (
        ("filter65 ranking65 encoding65 mapping65 record65 candle65", 6),
        ["filter65", "ranking65", "encoding65", "mapping65", "record65", "candle65"],
    ),
    (
        ("filter65 ranking65 encoding65 mapping65 record65 candle65", 10),
        ["filter65", "ranking65", "encoding65", "mapping65", "record65", "candle65"],
    ),
    (
        ("filter65 ranking65 encoding65 mapping65 record65 candle65", 18),
        ["filter65 ranking65", "encoding65", "mapping65 record65", "candle65"],
    ),
    (
        ("filter65 ranking65 encoding65 mapping65 record65 candle65", 28),
        ["filter65 ranking65", "encoding65 mapping65", "record65 candle65"],
    ),
    (
        ("ranking65 encoding65 mapping65 record65 candle65 thread65", 6),
        ["ranking65", "encoding65", "mapping65", "record65", "candle65", "thread65"],
    ),
    (
        ("ranking65 encoding65 mapping65 record65 candle65 thread65", 10),
        ["ranking65", "encoding65", "mapping65", "record65", "candle65", "thread65"],
    ),
    (
        ("ranking65 encoding65 mapping65 record65 candle65 thread65", 18),
        ["ranking65", "encoding65", "mapping65 record65", "candle65 thread65"],
    ),
    (
        ("ranking65 encoding65 mapping65 record65 candle65 thread65", 28),
        ["ranking65 encoding65", "mapping65 record65 candle65", "thread65"],
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
