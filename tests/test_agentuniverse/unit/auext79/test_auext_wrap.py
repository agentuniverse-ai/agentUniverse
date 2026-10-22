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
        ("round 79: the quick brown fox jumps over the lazy dog", 4),
        ["round", "79:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 79: the quick brown fox jumps over the lazy dog", 8),
        ["round", "79: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 79: the quick brown fox jumps over the lazy dog", 12),
        ["round 79:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 79: the quick brown fox jumps over the lazy dog", 16),
        ["round 79: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 79: the quick brown fox jumps over the lazy dog", 24),
        ["round 79: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 79: the quick brown fox jumps over the lazy dog", 32),
        ["round 79: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 79: agentuniverse is a framework for multi agents", 4),
        ["round", "79:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 79: agentuniverse is a framework for multi agents", 8),
        ["round", "79:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 79: agentuniverse is a framework for multi agents", 12),
        ["round 79:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 79: agentuniverse is a framework for multi agents", 16),
        ["round 79:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 79: agentuniverse is a framework for multi agents", 24),
        ["round 79: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 79: agentuniverse is a framework for multi agents", 32),
        ["round 79: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 79: knowledge stored as vectors enables retrieval", 4),
        ["round", "79:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 79: knowledge stored as vectors enables retrieval", 8),
        ["round", "79:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 79: knowledge stored as vectors enables retrieval", 12),
        ["round 79:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 79: knowledge stored as vectors enables retrieval", 16),
        ["round 79:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 79: knowledge stored as vectors enables retrieval", 24),
        ["round 79: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 79: knowledge stored as vectors enables retrieval", 32),
        ["round 79: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 79: the processor reads the record then stops", 4),
        ["round", "79:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 79: the processor reads the record then stops", 8),
        ["round", "79: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 79: the processor reads the record then stops", 12),
        ["round 79:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 79: the processor reads the record then stops", 16),
        ["round 79: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 79: the processor reads the record then stops", 24),
        ["round 79: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 79: the processor reads the record then stops", 32),
        ["round 79: the processor reads", "the record then stops"],
    ),
    (
        ("round 79: a worker pulls the next task from the queue", 4),
        ["round", "79:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 79: a worker pulls the next task from the queue", 8),
        ["round", "79: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 79: a worker pulls the next task from the queue", 12),
        ["round 79: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 79: a worker pulls the next task from the queue", 16),
        ["round 79: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 79: a worker pulls the next task from the queue", 24),
        ["round 79: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 79: a worker pulls the next task from the queue", 32),
        ["round 79: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 79: signals travel through the network layer", 4),
        ["round", "79:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 79: signals travel through the network layer", 8),
        ["round", "79:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 79: signals travel through the network layer", 12),
        ["round 79:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 79: signals travel through the network layer", 16),
        ["round 79:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 79: signals travel through the network layer", 24),
        ["round 79: signals travel", "through the network", "layer"],
    ),
    (
        ("round 79: signals travel through the network layer", 32),
        ["round 79: signals travel through", "the network layer"],
    ),
    (
        ("round 79: the gateway routes each request by policy", 4),
        ["round", "79:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 79: the gateway routes each request by policy", 8),
        ["round", "79: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 79: the gateway routes each request by policy", 12),
        ["round 79:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 79: the gateway routes each request by policy", 16),
        ["round 79: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 79: the gateway routes each request by policy", 24),
        ["round 79: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 79: the gateway routes each request by policy", 32),
        ["round 79: the gateway routes", "each request by policy"],
    ),
    (
        ("round 79: memory grows until the buffer is full", 4),
        ["round", "79:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 79: memory grows until the buffer is full", 8),
        ["round", "79:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 79: memory grows until the buffer is full", 12),
        ["round 79:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 79: memory grows until the buffer is full", 16),
        ["round 79: memory", "grows until the", "buffer is full"],
    ),
    (("round 79: memory grows until the buffer is full", 24), ["round 79: memory grows", "until the buffer is full"]),
    (("round 79: memory grows until the buffer is full", 32), ["round 79: memory grows until the", "buffer is full"]),
    (
        ("round 79: the cluster mirrors every packet twice", 4),
        ["round", "79:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 79: the cluster mirrors every packet twice", 8),
        ["round", "79: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 79: the cluster mirrors every packet twice", 12),
        ["round 79:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 79: the cluster mirrors every packet twice", 16),
        ["round 79: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 79: the cluster mirrors every packet twice", 24),
        ["round 79: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 79: the cluster mirrors every packet twice", 32), ["round 79: the cluster mirrors", "every packet twice"]),
    (
        ("round 79: ranking uses tokens learned from the corpus", 4),
        ["round", "79:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 79: ranking uses tokens learned from the corpus", 8),
        ["round", "79:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 79: ranking uses tokens learned from the corpus", 12),
        ["round 79:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 79: ranking uses tokens learned from the corpus", 16),
        ["round 79:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 79: ranking uses tokens learned from the corpus", 24),
        ["round 79: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 79: ranking uses tokens learned from the corpus", 32),
        ["round 79: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 79: a long session ends when the candle dies", 4),
        ["round", "79:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 79: a long session ends when the candle dies", 8),
        ["round", "79: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 79: a long session ends when the candle dies", 12),
        ["round 79: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 79: a long session ends when the candle dies", 16),
        ["round 79: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 79: a long session ends when the candle dies", 24),
        ["round 79: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 79: a long session ends when the candle dies", 32),
        ["round 79: a long session ends", "when the candle dies"],
    ),
    (
        ("round 79: encode the prompt then map the result", 4),
        ["round", "79:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 79: encode the prompt then map the result", 8),
        ["round", "79:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 79: encode the prompt then map the result", 12),
        ["round 79:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 79: encode the prompt then map the result", 16),
        ["round 79: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 79: encode the prompt then map the result", 24),
        ["round 79: encode the", "prompt then map the", "result"],
    ),
    (("round 79: encode the prompt then map the result", 32), ["round 79: encode the prompt then", "map the result"]),
    (
        ("round 79: the kernel wakes the worker at dawn", 4),
        ["round", "79:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 79: the kernel wakes the worker at dawn", 8),
        ["round", "79: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 79: the kernel wakes the worker at dawn", 12),
        ["round 79:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 79: the kernel wakes the worker at dawn", 16), ["round 79: the", "kernel wakes the", "worker at dawn"]),
    (("round 79: the kernel wakes the worker at dawn", 24), ["round 79: the kernel", "wakes the worker at dawn"]),
    (("round 79: the kernel wakes the worker at dawn", 32), ["round 79: the kernel wakes the", "worker at dawn"]),
    (
        ("round 79: service latency drops after the patch", 4),
        ["round", "79:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 79: service latency drops after the patch", 8),
        ["round", "79:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 79: service latency drops after the patch", 12),
        ["round 79:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 79: service latency drops after the patch", 16),
        ["round 79:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 79: service latency drops after the patch", 24),
        ["round 79: service", "latency drops after the", "patch"],
    ),
    (("round 79: service latency drops after the patch", 32), ["round 79: service latency drops", "after the patch"]),
    (
        ("round 79: the library caches every vector it sees", 4),
        ["round", "79:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 79: the library caches every vector it sees", 8),
        ["round", "79: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 79: the library caches every vector it sees", 12),
        ["round 79:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 79: the library caches every vector it sees", 16),
        ["round 79: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 79: the library caches every vector it sees", 24),
        ["round 79: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 79: the library caches every vector it sees", 32),
        ["round 79: the library caches", "every vector it sees"],
    ),
    (
        ("round 79: agents argue then the debate resolves", 4),
        ["round", "79:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 79: agents argue then the debate resolves", 8),
        ["round", "79:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 79: agents argue then the debate resolves", 12),
        ["round 79:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 79: agents argue then the debate resolves", 16),
        ["round 79: agents", "argue then the", "debate resolves"],
    ),
    (("round 79: agents argue then the debate resolves", 24), ["round 79: agents argue", "then the debate resolves"]),
    (("round 79: agents argue then the debate resolves", 32), ["round 79: agents argue then the", "debate resolves"]),
    (
        ("round 79: the filter keeps only strong matches", 4),
        ["round", "79:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 79: the filter keeps only strong matches", 8),
        ["round", "79: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 79: the filter keeps only strong matches", 12),
        ["round 79:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 79: the filter keeps only strong matches", 16),
        ["round 79: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 79: the filter keeps only strong matches", 24), ["round 79: the filter", "keeps only strong", "matches"]),
    (("round 79: the filter keeps only strong matches", 32), ["round 79: the filter keeps only", "strong matches"]),
    (
        ("round 79: the model answers with a short reply", 4),
        ["round", "79:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 79: the model answers with a short reply", 8),
        ["round", "79: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 79: the model answers with a short reply", 12),
        ["round 79:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 79: the model answers with a short reply", 16),
        ["round 79: the", "model answers", "with a short", "reply"],
    ),
    (("round 79: the model answers with a short reply", 24), ["round 79: the model", "answers with a short", "reply"]),
    (("round 79: the model answers with a short reply", 32), ["round 79: the model answers with", "a short reply"]),
    (
        ("round 79: the recorder stores the reasoning trace", 4),
        ["round", "79:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 79: the recorder stores the reasoning trace", 8),
        ["round", "79: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 79: the recorder stores the reasoning trace", 12),
        ["round 79:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 79: the recorder stores the reasoning trace", 16),
        ["round 79: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 79: the recorder stores the reasoning trace", 24),
        ["round 79: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 79: the recorder stores the reasoning trace", 32),
        ["round 79: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 79: the angel watches the processor run", 4),
        ["round", "79:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 79: the angel watches the processor run", 8),
        ["round", "79: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 79: the angel watches the processor run", 12),
        ["round 79:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 79: the angel watches the processor run", 16), ["round 79: the", "angel watches", "the processor", "run"]),
    (("round 79: the angel watches the processor run", 24), ["round 79: the angel", "watches the processor", "run"]),
    (("round 79: the angel watches the processor run", 32), ["round 79: the angel watches the", "processor run"]),
    (
        ("round 79: angle of the vector decides the match", 4),
        ["round", "79:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 79: angle of the vector decides the match", 8),
        ["round", "79:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 79: angle of the vector decides the match", 12),
        ["round 79:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 79: angle of the vector decides the match", 16),
        ["round 79: angle", "of the vector", "decides the", "match"],
    ),
    (("round 79: angle of the vector decides the match", 24), ["round 79: angle of the", "vector decides the match"]),
    (("round 79: angle of the vector decides the match", 32), ["round 79: angle of the vector", "decides the match"]),
    (
        ("round 79: the candle burns twice as long at night", 4),
        ["round", "79:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 79: the candle burns twice as long at night", 8),
        ["round", "79: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 79: the candle burns twice as long at night", 12),
        ["round 79:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 79: the candle burns twice as long at night", 16),
        ["round 79: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 79: the candle burns twice as long at night", 24),
        ["round 79: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 79: the candle burns twice as long at night", 32),
        ["round 79: the candle burns twice", "as long at night"],
    ),
    (
        ("round 79: a mirror of the universe in one line", 4),
        ["round", "79:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 79: a mirror of the universe in one line", 8),
        ["round", "79: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 79: a mirror of the universe in one line", 12),
        ["round 79: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 79: a mirror of the universe in one line", 16),
        ["round 79: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 79: a mirror of the universe in one line", 24), ["round 79: a mirror of", "the universe in one line"]),
    (("round 79: a mirror of the universe in one line", 32), ["round 79: a mirror of the", "universe in one line"]),
    (
        ("round 79: the queue drains before the storm", 4),
        ["round", "79:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 79: the queue drains before the storm", 8),
        ["round", "79: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 79: the queue drains before the storm", 12), ["round 79:", "the queue", "drains", "before the", "storm"]),
    (("round 79: the queue drains before the storm", 16), ["round 79: the", "queue drains", "before the storm"]),
    (("round 79: the queue drains before the storm", 24), ["round 79: the queue", "drains before the storm"]),
    (("round 79: the queue drains before the storm", 32), ["round 79: the queue drains", "before the storm"]),
    (
        ("kitten79 sitting79 agent79 angle79 universe79 memory79", 6),
        ["kitten79", "sitting79", "agent79", "angle79", "universe79", "memory79"],
    ),
    (
        ("kitten79 sitting79 agent79 angle79 universe79 memory79", 10),
        ["kitten79", "sitting79", "agent79", "angle79", "universe79", "memory79"],
    ),
    (
        ("kitten79 sitting79 agent79 angle79 universe79 memory79", 18),
        ["kitten79 sitting79", "agent79 angle79", "universe79", "memory79"],
    ),
    (
        ("kitten79 sitting79 agent79 angle79 universe79 memory79", 28),
        ["kitten79 sitting79 agent79", "angle79 universe79 memory79"],
    ),
    (
        ("sitting79 agent79 angle79 universe79 memory79 stream79", 6),
        ["sitting79", "agent79", "angle79", "universe79", "memory79", "stream79"],
    ),
    (
        ("sitting79 agent79 angle79 universe79 memory79 stream79", 10),
        ["sitting79", "agent79", "angle79", "universe79", "memory79", "stream79"],
    ),
    (
        ("sitting79 agent79 angle79 universe79 memory79 stream79", 18),
        ["sitting79 agent79", "angle79 universe79", "memory79 stream79"],
    ),
    (
        ("sitting79 agent79 angle79 universe79 memory79 stream79", 28),
        ["sitting79 agent79 angle79", "universe79 memory79 stream79"],
    ),
    (
        ("agent79 angle79 universe79 memory79 stream79 context79", 6),
        ["agent79", "angle79", "universe79", "memory79", "stream79", "context79"],
    ),
    (
        ("agent79 angle79 universe79 memory79 stream79 context79", 10),
        ["agent79", "angle79", "universe79", "memory79", "stream79", "context79"],
    ),
    (
        ("agent79 angle79 universe79 memory79 stream79 context79", 18),
        ["agent79 angle79", "universe79", "memory79 stream79", "context79"],
    ),
    (
        ("agent79 angle79 universe79 memory79 stream79 context79", 28),
        ["agent79 angle79 universe79", "memory79 stream79 context79"],
    ),
    (
        ("angle79 universe79 memory79 stream79 context79 knowledge79", 6),
        ["angle79", "universe79", "memory79", "stream79", "context79", "knowledge79"],
    ),
    (
        ("angle79 universe79 memory79 stream79 context79 knowledge79", 10),
        ["angle79", "universe79", "memory79", "stream79", "context79", "knowledge79"],
    ),
    (
        ("angle79 universe79 memory79 stream79 context79 knowledge79", 18),
        ["angle79 universe79", "memory79 stream79", "context79", "knowledge79"],
    ),
    (
        ("angle79 universe79 memory79 stream79 context79 knowledge79", 28),
        ["angle79 universe79 memory79", "stream79 context79", "knowledge79"],
    ),
    (
        ("universe79 memory79 stream79 context79 knowledge79 vector79", 6),
        ["universe79", "memory79", "stream79", "context79", "knowledge79", "vector79"],
    ),
    (
        ("universe79 memory79 stream79 context79 knowledge79 vector79", 10),
        ["universe79", "memory79", "stream79", "context79", "knowledge79", "vector79"],
    ),
    (
        ("universe79 memory79 stream79 context79 knowledge79 vector79", 18),
        ["universe79", "memory79 stream79", "context79", "knowledge79", "vector79"],
    ),
    (
        ("universe79 memory79 stream79 context79 knowledge79 vector79", 28),
        ["universe79 memory79 stream79", "context79 knowledge79", "vector79"],
    ),
    (
        ("memory79 stream79 context79 knowledge79 vector79 processor79", 6),
        ["memory79", "stream79", "context79", "knowledge79", "vector79", "processor79"],
    ),
    (
        ("memory79 stream79 context79 knowledge79 vector79 processor79", 10),
        ["memory79", "stream79", "context79", "knowledge79", "vector79", "processor79"],
    ),
    (
        ("memory79 stream79 context79 knowledge79 vector79 processor79", 18),
        ["memory79 stream79", "context79", "knowledge79", "vector79", "processor79"],
    ),
    (
        ("memory79 stream79 context79 knowledge79 vector79 processor79", 28),
        ["memory79 stream79 context79", "knowledge79 vector79", "processor79"],
    ),
    (
        ("stream79 context79 knowledge79 vector79 processor79 reasoning79", 6),
        ["stream79", "context79", "knowledge79", "vector79", "processor79", "reasoning79"],
    ),
    (
        ("stream79 context79 knowledge79 vector79 processor79 reasoning79", 10),
        ["stream79", "context79", "knowledge79", "vector79", "processor79", "reasoning79"],
    ),
    (
        ("stream79 context79 knowledge79 vector79 processor79 reasoning79", 18),
        ["stream79 context79", "knowledge79", "vector79", "processor79", "reasoning79"],
    ),
    (
        ("stream79 context79 knowledge79 vector79 processor79 reasoning79", 28),
        ["stream79 context79", "knowledge79 vector79", "processor79 reasoning79"],
    ),
    (
        ("context79 knowledge79 vector79 processor79 reasoning79 machine79", 6),
        ["context79", "knowledge79", "vector79", "processor79", "reasoning79", "machine79"],
    ),
    (
        ("context79 knowledge79 vector79 processor79 reasoning79 machine79", 10),
        ["context79", "knowledge79", "vector79", "processor79", "reasoning79", "machine79"],
    ),
    (
        ("context79 knowledge79 vector79 processor79 reasoning79 machine79", 18),
        ["context79", "knowledge79", "vector79", "processor79", "reasoning79", "machine79"],
    ),
    (
        ("context79 knowledge79 vector79 processor79 reasoning79 machine79", 28),
        ["context79 knowledge79", "vector79 processor79", "reasoning79 machine79"],
    ),
    (
        ("knowledge79 vector79 processor79 reasoning79 machine79 learning79", 6),
        ["knowledge79", "vector79", "processor79", "reasoning79", "machine79", "learning79"],
    ),
    (
        ("knowledge79 vector79 processor79 reasoning79 machine79 learning79", 10),
        ["knowledge79", "vector79", "processor79", "reasoning79", "machine79", "learning79"],
    ),
    (
        ("knowledge79 vector79 processor79 reasoning79 machine79 learning79", 18),
        ["knowledge79", "vector79", "processor79", "reasoning79", "machine79", "learning79"],
    ),
    (
        ("knowledge79 vector79 processor79 reasoning79 machine79 learning79", 28),
        ["knowledge79 vector79", "processor79 reasoning79", "machine79 learning79"],
    ),
    (
        ("vector79 processor79 reasoning79 machine79 learning79 model79", 6),
        ["vector79", "processor79", "reasoning79", "machine79", "learning79", "model79"],
    ),
    (
        ("vector79 processor79 reasoning79 machine79 learning79 model79", 10),
        ["vector79", "processor79", "reasoning79", "machine79", "learning79", "model79"],
    ),
    (
        ("vector79 processor79 reasoning79 machine79 learning79 model79", 18),
        ["vector79", "processor79", "reasoning79", "machine79", "learning79 model79"],
    ),
    (
        ("vector79 processor79 reasoning79 machine79 learning79 model79", 28),
        ["vector79 processor79", "reasoning79 machine79", "learning79 model79"],
    ),
    (
        ("processor79 reasoning79 machine79 learning79 model79 token79", 6),
        ["processor79", "reasoning79", "machine79", "learning79", "model79", "token79"],
    ),
    (
        ("processor79 reasoning79 machine79 learning79 model79 token79", 10),
        ["processor79", "reasoning79", "machine79", "learning79", "model79", "token79"],
    ),
    (
        ("processor79 reasoning79 machine79 learning79 model79 token79", 18),
        ["processor79", "reasoning79", "machine79", "learning79 model79", "token79"],
    ),
    (
        ("processor79 reasoning79 machine79 learning79 model79 token79", 28),
        ["processor79 reasoning79", "machine79 learning79 model79", "token79"],
    ),
    (
        ("reasoning79 machine79 learning79 model79 token79 prompt79", 6),
        ["reasoning79", "machine79", "learning79", "model79", "token79", "prompt79"],
    ),
    (
        ("reasoning79 machine79 learning79 model79 token79 prompt79", 10),
        ["reasoning79", "machine79", "learning79", "model79", "token79", "prompt79"],
    ),
    (
        ("reasoning79 machine79 learning79 model79 token79 prompt79", 18),
        ["reasoning79", "machine79", "learning79 model79", "token79 prompt79"],
    ),
    (
        ("reasoning79 machine79 learning79 model79 token79 prompt79", 28),
        ["reasoning79 machine79", "learning79 model79 token79", "prompt79"],
    ),
    (
        ("machine79 learning79 model79 token79 prompt79 session79", 6),
        ["machine79", "learning79", "model79", "token79", "prompt79", "session79"],
    ),
    (
        ("machine79 learning79 model79 token79 prompt79 session79", 10),
        ["machine79", "learning79", "model79", "token79", "prompt79", "session79"],
    ),
    (
        ("machine79 learning79 model79 token79 prompt79 session79", 18),
        ["machine79", "learning79 model79", "token79 prompt79", "session79"],
    ),
    (
        ("machine79 learning79 model79 token79 prompt79 session79", 28),
        ["machine79 learning79 model79", "token79 prompt79 session79"],
    ),
    (
        ("learning79 model79 token79 prompt79 session79 library79", 6),
        ["learning79", "model79", "token79", "prompt79", "session79", "library79"],
    ),
    (
        ("learning79 model79 token79 prompt79 session79 library79", 10),
        ["learning79", "model79", "token79", "prompt79", "session79", "library79"],
    ),
    (
        ("learning79 model79 token79 prompt79 session79 library79", 18),
        ["learning79 model79", "token79 prompt79", "session79", "library79"],
    ),
    (
        ("learning79 model79 token79 prompt79 session79 library79", 28),
        ["learning79 model79 token79", "prompt79 session79 library79"],
    ),
    (
        ("model79 token79 prompt79 session79 library79 service79", 6),
        ["model79", "token79", "prompt79", "session79", "library79", "service79"],
    ),
    (
        ("model79 token79 prompt79 session79 library79 service79", 10),
        ["model79", "token79", "prompt79", "session79", "library79", "service79"],
    ),
    (
        ("model79 token79 prompt79 session79 library79 service79", 18),
        ["model79 token79", "prompt79 session79", "library79", "service79"],
    ),
    (
        ("model79 token79 prompt79 session79 library79 service79", 28),
        ["model79 token79 prompt79", "session79 library79", "service79"],
    ),
    (
        ("token79 prompt79 session79 library79 service79 gateway79", 6),
        ["token79", "prompt79", "session79", "library79", "service79", "gateway79"],
    ),
    (
        ("token79 prompt79 session79 library79 service79 gateway79", 10),
        ["token79", "prompt79", "session79", "library79", "service79", "gateway79"],
    ),
    (
        ("token79 prompt79 session79 library79 service79 gateway79", 18),
        ["token79 prompt79", "session79", "library79", "service79", "gateway79"],
    ),
    (
        ("token79 prompt79 session79 library79 service79 gateway79", 28),
        ["token79 prompt79 session79", "library79 service79", "gateway79"],
    ),
    (
        ("prompt79 session79 library79 service79 gateway79 storage79", 6),
        ["prompt79", "session79", "library79", "service79", "gateway79", "storage79"],
    ),
    (
        ("prompt79 session79 library79 service79 gateway79 storage79", 10),
        ["prompt79", "session79", "library79", "service79", "gateway79", "storage79"],
    ),
    (
        ("prompt79 session79 library79 service79 gateway79 storage79", 18),
        ["prompt79 session79", "library79", "service79", "gateway79", "storage79"],
    ),
    (
        ("prompt79 session79 library79 service79 gateway79 storage79", 28),
        ["prompt79 session79 library79", "service79 gateway79", "storage79"],
    ),
    (
        ("session79 library79 service79 gateway79 storage79 network79", 6),
        ["session79", "library79", "service79", "gateway79", "storage79", "network79"],
    ),
    (
        ("session79 library79 service79 gateway79 storage79 network79", 10),
        ["session79", "library79", "service79", "gateway79", "storage79", "network79"],
    ),
    (
        ("session79 library79 service79 gateway79 storage79 network79", 18),
        ["session79", "library79", "service79", "gateway79", "storage79", "network79"],
    ),
    (
        ("session79 library79 service79 gateway79 storage79 network79", 28),
        ["session79 library79", "service79 gateway79", "storage79 network79"],
    ),
    (
        ("library79 service79 gateway79 storage79 network79 latency79", 6),
        ["library79", "service79", "gateway79", "storage79", "network79", "latency79"],
    ),
    (
        ("library79 service79 gateway79 storage79 network79 latency79", 10),
        ["library79", "service79", "gateway79", "storage79", "network79", "latency79"],
    ),
    (
        ("library79 service79 gateway79 storage79 network79 latency79", 18),
        ["library79", "service79", "gateway79", "storage79", "network79", "latency79"],
    ),
    (
        ("library79 service79 gateway79 storage79 network79 latency79", 28),
        ["library79 service79", "gateway79 storage79", "network79 latency79"],
    ),
    (
        ("service79 gateway79 storage79 network79 latency79 buffer79", 6),
        ["service79", "gateway79", "storage79", "network79", "latency79", "buffer79"],
    ),
    (
        ("service79 gateway79 storage79 network79 latency79 buffer79", 10),
        ["service79", "gateway79", "storage79", "network79", "latency79", "buffer79"],
    ),
    (
        ("service79 gateway79 storage79 network79 latency79 buffer79", 18),
        ["service79", "gateway79", "storage79", "network79", "latency79 buffer79"],
    ),
    (
        ("service79 gateway79 storage79 network79 latency79 buffer79", 28),
        ["service79 gateway79", "storage79 network79", "latency79 buffer79"],
    ),
    (
        ("gateway79 storage79 network79 latency79 buffer79 queue79", 6),
        ["gateway79", "storage79", "network79", "latency79", "buffer79", "queue79"],
    ),
    (
        ("gateway79 storage79 network79 latency79 buffer79 queue79", 10),
        ["gateway79", "storage79", "network79", "latency79", "buffer79", "queue79"],
    ),
    (
        ("gateway79 storage79 network79 latency79 buffer79 queue79", 18),
        ["gateway79", "storage79", "network79", "latency79 buffer79", "queue79"],
    ),
    (
        ("gateway79 storage79 network79 latency79 buffer79 queue79", 28),
        ["gateway79 storage79", "network79 latency79 buffer79", "queue79"],
    ),
    (
        ("storage79 network79 latency79 buffer79 queue79 worker79", 6),
        ["storage79", "network79", "latency79", "buffer79", "queue79", "worker79"],
    ),
    (
        ("storage79 network79 latency79 buffer79 queue79 worker79", 10),
        ["storage79", "network79", "latency79", "buffer79", "queue79", "worker79"],
    ),
    (
        ("storage79 network79 latency79 buffer79 queue79 worker79", 18),
        ["storage79", "network79", "latency79 buffer79", "queue79 worker79"],
    ),
    (
        ("storage79 network79 latency79 buffer79 queue79 worker79", 28),
        ["storage79 network79", "latency79 buffer79 queue79", "worker79"],
    ),
    (
        ("network79 latency79 buffer79 queue79 worker79 kernel79", 6),
        ["network79", "latency79", "buffer79", "queue79", "worker79", "kernel79"],
    ),
    (
        ("network79 latency79 buffer79 queue79 worker79 kernel79", 10),
        ["network79", "latency79", "buffer79", "queue79", "worker79", "kernel79"],
    ),
    (
        ("network79 latency79 buffer79 queue79 worker79 kernel79", 18),
        ["network79", "latency79 buffer79", "queue79 worker79", "kernel79"],
    ),
    (
        ("network79 latency79 buffer79 queue79 worker79 kernel79", 28),
        ["network79 latency79 buffer79", "queue79 worker79 kernel79"],
    ),
    (
        ("latency79 buffer79 queue79 worker79 kernel79 signal79", 6),
        ["latency79", "buffer79", "queue79", "worker79", "kernel79", "signal79"],
    ),
    (
        ("latency79 buffer79 queue79 worker79 kernel79 signal79", 10),
        ["latency79", "buffer79", "queue79", "worker79", "kernel79", "signal79"],
    ),
    (
        ("latency79 buffer79 queue79 worker79 kernel79 signal79", 18),
        ["latency79 buffer79", "queue79 worker79", "kernel79 signal79"],
    ),
    (
        ("latency79 buffer79 queue79 worker79 kernel79 signal79", 28),
        ["latency79 buffer79 queue79", "worker79 kernel79 signal79"],
    ),
    (
        ("buffer79 queue79 worker79 kernel79 signal79 packet79", 6),
        ["buffer79", "queue79", "worker79", "kernel79", "signal79", "packet79"],
    ),
    (
        ("buffer79 queue79 worker79 kernel79 signal79 packet79", 10),
        ["buffer79", "queue79", "worker79", "kernel79", "signal79", "packet79"],
    ),
    (
        ("buffer79 queue79 worker79 kernel79 signal79 packet79", 18),
        ["buffer79 queue79", "worker79 kernel79", "signal79 packet79"],
    ),
    (
        ("buffer79 queue79 worker79 kernel79 signal79 packet79", 28),
        ["buffer79 queue79 worker79", "kernel79 signal79 packet79"],
    ),
    (
        ("queue79 worker79 kernel79 signal79 packet79 router79", 6),
        ["queue79", "worker79", "kernel79", "signal79", "packet79", "router79"],
    ),
    (
        ("queue79 worker79 kernel79 signal79 packet79 router79", 10),
        ["queue79", "worker79", "kernel79", "signal79", "packet79", "router79"],
    ),
    (
        ("queue79 worker79 kernel79 signal79 packet79 router79", 18),
        ["queue79 worker79", "kernel79 signal79", "packet79 router79"],
    ),
    (
        ("queue79 worker79 kernel79 signal79 packet79 router79", 28),
        ["queue79 worker79 kernel79", "signal79 packet79 router79"],
    ),
    (
        ("worker79 kernel79 signal79 packet79 router79 cluster79", 6),
        ["worker79", "kernel79", "signal79", "packet79", "router79", "cluster79"],
    ),
    (
        ("worker79 kernel79 signal79 packet79 router79 cluster79", 10),
        ["worker79", "kernel79", "signal79", "packet79", "router79", "cluster79"],
    ),
    (
        ("worker79 kernel79 signal79 packet79 router79 cluster79", 18),
        ["worker79 kernel79", "signal79 packet79", "router79 cluster79"],
    ),
    (
        ("worker79 kernel79 signal79 packet79 router79 cluster79", 28),
        ["worker79 kernel79 signal79", "packet79 router79 cluster79"],
    ),
    (
        ("kernel79 signal79 packet79 router79 cluster79 mirror79", 6),
        ["kernel79", "signal79", "packet79", "router79", "cluster79", "mirror79"],
    ),
    (
        ("kernel79 signal79 packet79 router79 cluster79 mirror79", 10),
        ["kernel79", "signal79", "packet79", "router79", "cluster79", "mirror79"],
    ),
    (
        ("kernel79 signal79 packet79 router79 cluster79 mirror79", 18),
        ["kernel79 signal79", "packet79 router79", "cluster79 mirror79"],
    ),
    (
        ("kernel79 signal79 packet79 router79 cluster79 mirror79", 28),
        ["kernel79 signal79 packet79", "router79 cluster79 mirror79"],
    ),
    (
        ("signal79 packet79 router79 cluster79 mirror79 filter79", 6),
        ["signal79", "packet79", "router79", "cluster79", "mirror79", "filter79"],
    ),
    (
        ("signal79 packet79 router79 cluster79 mirror79 filter79", 10),
        ["signal79", "packet79", "router79", "cluster79", "mirror79", "filter79"],
    ),
    (
        ("signal79 packet79 router79 cluster79 mirror79 filter79", 18),
        ["signal79 packet79", "router79 cluster79", "mirror79 filter79"],
    ),
    (
        ("signal79 packet79 router79 cluster79 mirror79 filter79", 28),
        ["signal79 packet79 router79", "cluster79 mirror79 filter79"],
    ),
    (
        ("packet79 router79 cluster79 mirror79 filter79 ranking79", 6),
        ["packet79", "router79", "cluster79", "mirror79", "filter79", "ranking79"],
    ),
    (
        ("packet79 router79 cluster79 mirror79 filter79 ranking79", 10),
        ["packet79", "router79", "cluster79", "mirror79", "filter79", "ranking79"],
    ),
    (
        ("packet79 router79 cluster79 mirror79 filter79 ranking79", 18),
        ["packet79 router79", "cluster79 mirror79", "filter79 ranking79"],
    ),
    (
        ("packet79 router79 cluster79 mirror79 filter79 ranking79", 28),
        ["packet79 router79 cluster79", "mirror79 filter79 ranking79"],
    ),
    (
        ("router79 cluster79 mirror79 filter79 ranking79 encoding79", 6),
        ["router79", "cluster79", "mirror79", "filter79", "ranking79", "encoding79"],
    ),
    (
        ("router79 cluster79 mirror79 filter79 ranking79 encoding79", 10),
        ["router79", "cluster79", "mirror79", "filter79", "ranking79", "encoding79"],
    ),
    (
        ("router79 cluster79 mirror79 filter79 ranking79 encoding79", 18),
        ["router79 cluster79", "mirror79 filter79", "ranking79", "encoding79"],
    ),
    (
        ("router79 cluster79 mirror79 filter79 ranking79 encoding79", 28),
        ["router79 cluster79 mirror79", "filter79 ranking79", "encoding79"],
    ),
    (
        ("cluster79 mirror79 filter79 ranking79 encoding79 mapping79", 6),
        ["cluster79", "mirror79", "filter79", "ranking79", "encoding79", "mapping79"],
    ),
    (
        ("cluster79 mirror79 filter79 ranking79 encoding79 mapping79", 10),
        ["cluster79", "mirror79", "filter79", "ranking79", "encoding79", "mapping79"],
    ),
    (
        ("cluster79 mirror79 filter79 ranking79 encoding79 mapping79", 18),
        ["cluster79 mirror79", "filter79 ranking79", "encoding79", "mapping79"],
    ),
    (
        ("cluster79 mirror79 filter79 ranking79 encoding79 mapping79", 28),
        ["cluster79 mirror79 filter79", "ranking79 encoding79", "mapping79"],
    ),
    (
        ("mirror79 filter79 ranking79 encoding79 mapping79 record79", 6),
        ["mirror79", "filter79", "ranking79", "encoding79", "mapping79", "record79"],
    ),
    (
        ("mirror79 filter79 ranking79 encoding79 mapping79 record79", 10),
        ["mirror79", "filter79", "ranking79", "encoding79", "mapping79", "record79"],
    ),
    (
        ("mirror79 filter79 ranking79 encoding79 mapping79 record79", 18),
        ["mirror79 filter79", "ranking79", "encoding79", "mapping79 record79"],
    ),
    (
        ("mirror79 filter79 ranking79 encoding79 mapping79 record79", 28),
        ["mirror79 filter79 ranking79", "encoding79 mapping79", "record79"],
    ),
    (
        ("filter79 ranking79 encoding79 mapping79 record79 candle79", 6),
        ["filter79", "ranking79", "encoding79", "mapping79", "record79", "candle79"],
    ),
    (
        ("filter79 ranking79 encoding79 mapping79 record79 candle79", 10),
        ["filter79", "ranking79", "encoding79", "mapping79", "record79", "candle79"],
    ),
    (
        ("filter79 ranking79 encoding79 mapping79 record79 candle79", 18),
        ["filter79 ranking79", "encoding79", "mapping79 record79", "candle79"],
    ),
    (
        ("filter79 ranking79 encoding79 mapping79 record79 candle79", 28),
        ["filter79 ranking79", "encoding79 mapping79", "record79 candle79"],
    ),
    (
        ("ranking79 encoding79 mapping79 record79 candle79 thread79", 6),
        ["ranking79", "encoding79", "mapping79", "record79", "candle79", "thread79"],
    ),
    (
        ("ranking79 encoding79 mapping79 record79 candle79 thread79", 10),
        ["ranking79", "encoding79", "mapping79", "record79", "candle79", "thread79"],
    ),
    (
        ("ranking79 encoding79 mapping79 record79 candle79 thread79", 18),
        ["ranking79", "encoding79", "mapping79 record79", "candle79 thread79"],
    ),
    (
        ("ranking79 encoding79 mapping79 record79 candle79 thread79", 28),
        ["ranking79 encoding79", "mapping79 record79 candle79", "thread79"],
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
