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
        ("round 86: the quick brown fox jumps over the lazy dog", 4),
        ["round", "86:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 86: the quick brown fox jumps over the lazy dog", 8),
        ["round", "86: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 86: the quick brown fox jumps over the lazy dog", 12),
        ["round 86:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 86: the quick brown fox jumps over the lazy dog", 16),
        ["round 86: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 86: the quick brown fox jumps over the lazy dog", 24),
        ["round 86: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 86: the quick brown fox jumps over the lazy dog", 32),
        ["round 86: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 86: agentuniverse is a framework for multi agents", 4),
        ["round", "86:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 86: agentuniverse is a framework for multi agents", 8),
        ["round", "86:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 86: agentuniverse is a framework for multi agents", 12),
        ["round 86:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 86: agentuniverse is a framework for multi agents", 16),
        ["round 86:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 86: agentuniverse is a framework for multi agents", 24),
        ["round 86: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 86: agentuniverse is a framework for multi agents", 32),
        ["round 86: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 86: knowledge stored as vectors enables retrieval", 4),
        ["round", "86:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 86: knowledge stored as vectors enables retrieval", 8),
        ["round", "86:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 86: knowledge stored as vectors enables retrieval", 12),
        ["round 86:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 86: knowledge stored as vectors enables retrieval", 16),
        ["round 86:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 86: knowledge stored as vectors enables retrieval", 24),
        ["round 86: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 86: knowledge stored as vectors enables retrieval", 32),
        ["round 86: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 86: the processor reads the record then stops", 4),
        ["round", "86:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 86: the processor reads the record then stops", 8),
        ["round", "86: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 86: the processor reads the record then stops", 12),
        ["round 86:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 86: the processor reads the record then stops", 16),
        ["round 86: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 86: the processor reads the record then stops", 24),
        ["round 86: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 86: the processor reads the record then stops", 32),
        ["round 86: the processor reads", "the record then stops"],
    ),
    (
        ("round 86: a worker pulls the next task from the queue", 4),
        ["round", "86:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 86: a worker pulls the next task from the queue", 8),
        ["round", "86: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 86: a worker pulls the next task from the queue", 12),
        ["round 86: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 86: a worker pulls the next task from the queue", 16),
        ["round 86: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 86: a worker pulls the next task from the queue", 24),
        ["round 86: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 86: a worker pulls the next task from the queue", 32),
        ["round 86: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 86: signals travel through the network layer", 4),
        ["round", "86:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 86: signals travel through the network layer", 8),
        ["round", "86:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 86: signals travel through the network layer", 12),
        ["round 86:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 86: signals travel through the network layer", 16),
        ["round 86:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 86: signals travel through the network layer", 24),
        ["round 86: signals travel", "through the network", "layer"],
    ),
    (
        ("round 86: signals travel through the network layer", 32),
        ["round 86: signals travel through", "the network layer"],
    ),
    (
        ("round 86: the gateway routes each request by policy", 4),
        ["round", "86:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 86: the gateway routes each request by policy", 8),
        ["round", "86: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 86: the gateway routes each request by policy", 12),
        ["round 86:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 86: the gateway routes each request by policy", 16),
        ["round 86: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 86: the gateway routes each request by policy", 24),
        ["round 86: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 86: the gateway routes each request by policy", 32),
        ["round 86: the gateway routes", "each request by policy"],
    ),
    (
        ("round 86: memory grows until the buffer is full", 4),
        ["round", "86:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 86: memory grows until the buffer is full", 8),
        ["round", "86:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 86: memory grows until the buffer is full", 12),
        ["round 86:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 86: memory grows until the buffer is full", 16),
        ["round 86: memory", "grows until the", "buffer is full"],
    ),
    (("round 86: memory grows until the buffer is full", 24), ["round 86: memory grows", "until the buffer is full"]),
    (("round 86: memory grows until the buffer is full", 32), ["round 86: memory grows until the", "buffer is full"]),
    (
        ("round 86: the cluster mirrors every packet twice", 4),
        ["round", "86:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 86: the cluster mirrors every packet twice", 8),
        ["round", "86: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 86: the cluster mirrors every packet twice", 12),
        ["round 86:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 86: the cluster mirrors every packet twice", 16),
        ["round 86: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 86: the cluster mirrors every packet twice", 24),
        ["round 86: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 86: the cluster mirrors every packet twice", 32), ["round 86: the cluster mirrors", "every packet twice"]),
    (
        ("round 86: ranking uses tokens learned from the corpus", 4),
        ["round", "86:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 86: ranking uses tokens learned from the corpus", 8),
        ["round", "86:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 86: ranking uses tokens learned from the corpus", 12),
        ["round 86:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 86: ranking uses tokens learned from the corpus", 16),
        ["round 86:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 86: ranking uses tokens learned from the corpus", 24),
        ["round 86: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 86: ranking uses tokens learned from the corpus", 32),
        ["round 86: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 86: a long session ends when the candle dies", 4),
        ["round", "86:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 86: a long session ends when the candle dies", 8),
        ["round", "86: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 86: a long session ends when the candle dies", 12),
        ["round 86: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 86: a long session ends when the candle dies", 16),
        ["round 86: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 86: a long session ends when the candle dies", 24),
        ["round 86: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 86: a long session ends when the candle dies", 32),
        ["round 86: a long session ends", "when the candle dies"],
    ),
    (
        ("round 86: encode the prompt then map the result", 4),
        ["round", "86:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 86: encode the prompt then map the result", 8),
        ["round", "86:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 86: encode the prompt then map the result", 12),
        ["round 86:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 86: encode the prompt then map the result", 16),
        ["round 86: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 86: encode the prompt then map the result", 24),
        ["round 86: encode the", "prompt then map the", "result"],
    ),
    (("round 86: encode the prompt then map the result", 32), ["round 86: encode the prompt then", "map the result"]),
    (
        ("round 86: the kernel wakes the worker at dawn", 4),
        ["round", "86:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 86: the kernel wakes the worker at dawn", 8),
        ["round", "86: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 86: the kernel wakes the worker at dawn", 12),
        ["round 86:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 86: the kernel wakes the worker at dawn", 16), ["round 86: the", "kernel wakes the", "worker at dawn"]),
    (("round 86: the kernel wakes the worker at dawn", 24), ["round 86: the kernel", "wakes the worker at dawn"]),
    (("round 86: the kernel wakes the worker at dawn", 32), ["round 86: the kernel wakes the", "worker at dawn"]),
    (
        ("round 86: service latency drops after the patch", 4),
        ["round", "86:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 86: service latency drops after the patch", 8),
        ["round", "86:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 86: service latency drops after the patch", 12),
        ["round 86:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 86: service latency drops after the patch", 16),
        ["round 86:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 86: service latency drops after the patch", 24),
        ["round 86: service", "latency drops after the", "patch"],
    ),
    (("round 86: service latency drops after the patch", 32), ["round 86: service latency drops", "after the patch"]),
    (
        ("round 86: the library caches every vector it sees", 4),
        ["round", "86:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 86: the library caches every vector it sees", 8),
        ["round", "86: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 86: the library caches every vector it sees", 12),
        ["round 86:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 86: the library caches every vector it sees", 16),
        ["round 86: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 86: the library caches every vector it sees", 24),
        ["round 86: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 86: the library caches every vector it sees", 32),
        ["round 86: the library caches", "every vector it sees"],
    ),
    (
        ("round 86: agents argue then the debate resolves", 4),
        ["round", "86:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 86: agents argue then the debate resolves", 8),
        ["round", "86:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 86: agents argue then the debate resolves", 12),
        ["round 86:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 86: agents argue then the debate resolves", 16),
        ["round 86: agents", "argue then the", "debate resolves"],
    ),
    (("round 86: agents argue then the debate resolves", 24), ["round 86: agents argue", "then the debate resolves"]),
    (("round 86: agents argue then the debate resolves", 32), ["round 86: agents argue then the", "debate resolves"]),
    (
        ("round 86: the filter keeps only strong matches", 4),
        ["round", "86:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 86: the filter keeps only strong matches", 8),
        ["round", "86: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 86: the filter keeps only strong matches", 12),
        ["round 86:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 86: the filter keeps only strong matches", 16),
        ["round 86: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 86: the filter keeps only strong matches", 24), ["round 86: the filter", "keeps only strong", "matches"]),
    (("round 86: the filter keeps only strong matches", 32), ["round 86: the filter keeps only", "strong matches"]),
    (
        ("round 86: the model answers with a short reply", 4),
        ["round", "86:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 86: the model answers with a short reply", 8),
        ["round", "86: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 86: the model answers with a short reply", 12),
        ["round 86:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 86: the model answers with a short reply", 16),
        ["round 86: the", "model answers", "with a short", "reply"],
    ),
    (("round 86: the model answers with a short reply", 24), ["round 86: the model", "answers with a short", "reply"]),
    (("round 86: the model answers with a short reply", 32), ["round 86: the model answers with", "a short reply"]),
    (
        ("round 86: the recorder stores the reasoning trace", 4),
        ["round", "86:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 86: the recorder stores the reasoning trace", 8),
        ["round", "86: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 86: the recorder stores the reasoning trace", 12),
        ["round 86:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 86: the recorder stores the reasoning trace", 16),
        ["round 86: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 86: the recorder stores the reasoning trace", 24),
        ["round 86: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 86: the recorder stores the reasoning trace", 32),
        ["round 86: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 86: the angel watches the processor run", 4),
        ["round", "86:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 86: the angel watches the processor run", 8),
        ["round", "86: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 86: the angel watches the processor run", 12),
        ["round 86:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 86: the angel watches the processor run", 16), ["round 86: the", "angel watches", "the processor", "run"]),
    (("round 86: the angel watches the processor run", 24), ["round 86: the angel", "watches the processor", "run"]),
    (("round 86: the angel watches the processor run", 32), ["round 86: the angel watches the", "processor run"]),
    (
        ("round 86: angle of the vector decides the match", 4),
        ["round", "86:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 86: angle of the vector decides the match", 8),
        ["round", "86:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 86: angle of the vector decides the match", 12),
        ["round 86:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 86: angle of the vector decides the match", 16),
        ["round 86: angle", "of the vector", "decides the", "match"],
    ),
    (("round 86: angle of the vector decides the match", 24), ["round 86: angle of the", "vector decides the match"]),
    (("round 86: angle of the vector decides the match", 32), ["round 86: angle of the vector", "decides the match"]),
    (
        ("round 86: the candle burns twice as long at night", 4),
        ["round", "86:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 86: the candle burns twice as long at night", 8),
        ["round", "86: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 86: the candle burns twice as long at night", 12),
        ["round 86:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 86: the candle burns twice as long at night", 16),
        ["round 86: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 86: the candle burns twice as long at night", 24),
        ["round 86: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 86: the candle burns twice as long at night", 32),
        ["round 86: the candle burns twice", "as long at night"],
    ),
    (
        ("round 86: a mirror of the universe in one line", 4),
        ["round", "86:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 86: a mirror of the universe in one line", 8),
        ["round", "86: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 86: a mirror of the universe in one line", 12),
        ["round 86: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 86: a mirror of the universe in one line", 16),
        ["round 86: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 86: a mirror of the universe in one line", 24), ["round 86: a mirror of", "the universe in one line"]),
    (("round 86: a mirror of the universe in one line", 32), ["round 86: a mirror of the", "universe in one line"]),
    (
        ("round 86: the queue drains before the storm", 4),
        ["round", "86:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 86: the queue drains before the storm", 8),
        ["round", "86: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 86: the queue drains before the storm", 12), ["round 86:", "the queue", "drains", "before the", "storm"]),
    (("round 86: the queue drains before the storm", 16), ["round 86: the", "queue drains", "before the storm"]),
    (("round 86: the queue drains before the storm", 24), ["round 86: the queue", "drains before the storm"]),
    (("round 86: the queue drains before the storm", 32), ["round 86: the queue drains", "before the storm"]),
    (
        ("kitten86 sitting86 agent86 angle86 universe86 memory86", 6),
        ["kitten86", "sitting86", "agent86", "angle86", "universe86", "memory86"],
    ),
    (
        ("kitten86 sitting86 agent86 angle86 universe86 memory86", 10),
        ["kitten86", "sitting86", "agent86", "angle86", "universe86", "memory86"],
    ),
    (
        ("kitten86 sitting86 agent86 angle86 universe86 memory86", 18),
        ["kitten86 sitting86", "agent86 angle86", "universe86", "memory86"],
    ),
    (
        ("kitten86 sitting86 agent86 angle86 universe86 memory86", 28),
        ["kitten86 sitting86 agent86", "angle86 universe86 memory86"],
    ),
    (
        ("sitting86 agent86 angle86 universe86 memory86 stream86", 6),
        ["sitting86", "agent86", "angle86", "universe86", "memory86", "stream86"],
    ),
    (
        ("sitting86 agent86 angle86 universe86 memory86 stream86", 10),
        ["sitting86", "agent86", "angle86", "universe86", "memory86", "stream86"],
    ),
    (
        ("sitting86 agent86 angle86 universe86 memory86 stream86", 18),
        ["sitting86 agent86", "angle86 universe86", "memory86 stream86"],
    ),
    (
        ("sitting86 agent86 angle86 universe86 memory86 stream86", 28),
        ["sitting86 agent86 angle86", "universe86 memory86 stream86"],
    ),
    (
        ("agent86 angle86 universe86 memory86 stream86 context86", 6),
        ["agent86", "angle86", "universe86", "memory86", "stream86", "context86"],
    ),
    (
        ("agent86 angle86 universe86 memory86 stream86 context86", 10),
        ["agent86", "angle86", "universe86", "memory86", "stream86", "context86"],
    ),
    (
        ("agent86 angle86 universe86 memory86 stream86 context86", 18),
        ["agent86 angle86", "universe86", "memory86 stream86", "context86"],
    ),
    (
        ("agent86 angle86 universe86 memory86 stream86 context86", 28),
        ["agent86 angle86 universe86", "memory86 stream86 context86"],
    ),
    (
        ("angle86 universe86 memory86 stream86 context86 knowledge86", 6),
        ["angle86", "universe86", "memory86", "stream86", "context86", "knowledge86"],
    ),
    (
        ("angle86 universe86 memory86 stream86 context86 knowledge86", 10),
        ["angle86", "universe86", "memory86", "stream86", "context86", "knowledge86"],
    ),
    (
        ("angle86 universe86 memory86 stream86 context86 knowledge86", 18),
        ["angle86 universe86", "memory86 stream86", "context86", "knowledge86"],
    ),
    (
        ("angle86 universe86 memory86 stream86 context86 knowledge86", 28),
        ["angle86 universe86 memory86", "stream86 context86", "knowledge86"],
    ),
    (
        ("universe86 memory86 stream86 context86 knowledge86 vector86", 6),
        ["universe86", "memory86", "stream86", "context86", "knowledge86", "vector86"],
    ),
    (
        ("universe86 memory86 stream86 context86 knowledge86 vector86", 10),
        ["universe86", "memory86", "stream86", "context86", "knowledge86", "vector86"],
    ),
    (
        ("universe86 memory86 stream86 context86 knowledge86 vector86", 18),
        ["universe86", "memory86 stream86", "context86", "knowledge86", "vector86"],
    ),
    (
        ("universe86 memory86 stream86 context86 knowledge86 vector86", 28),
        ["universe86 memory86 stream86", "context86 knowledge86", "vector86"],
    ),
    (
        ("memory86 stream86 context86 knowledge86 vector86 processor86", 6),
        ["memory86", "stream86", "context86", "knowledge86", "vector86", "processor86"],
    ),
    (
        ("memory86 stream86 context86 knowledge86 vector86 processor86", 10),
        ["memory86", "stream86", "context86", "knowledge86", "vector86", "processor86"],
    ),
    (
        ("memory86 stream86 context86 knowledge86 vector86 processor86", 18),
        ["memory86 stream86", "context86", "knowledge86", "vector86", "processor86"],
    ),
    (
        ("memory86 stream86 context86 knowledge86 vector86 processor86", 28),
        ["memory86 stream86 context86", "knowledge86 vector86", "processor86"],
    ),
    (
        ("stream86 context86 knowledge86 vector86 processor86 reasoning86", 6),
        ["stream86", "context86", "knowledge86", "vector86", "processor86", "reasoning86"],
    ),
    (
        ("stream86 context86 knowledge86 vector86 processor86 reasoning86", 10),
        ["stream86", "context86", "knowledge86", "vector86", "processor86", "reasoning86"],
    ),
    (
        ("stream86 context86 knowledge86 vector86 processor86 reasoning86", 18),
        ["stream86 context86", "knowledge86", "vector86", "processor86", "reasoning86"],
    ),
    (
        ("stream86 context86 knowledge86 vector86 processor86 reasoning86", 28),
        ["stream86 context86", "knowledge86 vector86", "processor86 reasoning86"],
    ),
    (
        ("context86 knowledge86 vector86 processor86 reasoning86 machine86", 6),
        ["context86", "knowledge86", "vector86", "processor86", "reasoning86", "machine86"],
    ),
    (
        ("context86 knowledge86 vector86 processor86 reasoning86 machine86", 10),
        ["context86", "knowledge86", "vector86", "processor86", "reasoning86", "machine86"],
    ),
    (
        ("context86 knowledge86 vector86 processor86 reasoning86 machine86", 18),
        ["context86", "knowledge86", "vector86", "processor86", "reasoning86", "machine86"],
    ),
    (
        ("context86 knowledge86 vector86 processor86 reasoning86 machine86", 28),
        ["context86 knowledge86", "vector86 processor86", "reasoning86 machine86"],
    ),
    (
        ("knowledge86 vector86 processor86 reasoning86 machine86 learning86", 6),
        ["knowledge86", "vector86", "processor86", "reasoning86", "machine86", "learning86"],
    ),
    (
        ("knowledge86 vector86 processor86 reasoning86 machine86 learning86", 10),
        ["knowledge86", "vector86", "processor86", "reasoning86", "machine86", "learning86"],
    ),
    (
        ("knowledge86 vector86 processor86 reasoning86 machine86 learning86", 18),
        ["knowledge86", "vector86", "processor86", "reasoning86", "machine86", "learning86"],
    ),
    (
        ("knowledge86 vector86 processor86 reasoning86 machine86 learning86", 28),
        ["knowledge86 vector86", "processor86 reasoning86", "machine86 learning86"],
    ),
    (
        ("vector86 processor86 reasoning86 machine86 learning86 model86", 6),
        ["vector86", "processor86", "reasoning86", "machine86", "learning86", "model86"],
    ),
    (
        ("vector86 processor86 reasoning86 machine86 learning86 model86", 10),
        ["vector86", "processor86", "reasoning86", "machine86", "learning86", "model86"],
    ),
    (
        ("vector86 processor86 reasoning86 machine86 learning86 model86", 18),
        ["vector86", "processor86", "reasoning86", "machine86", "learning86 model86"],
    ),
    (
        ("vector86 processor86 reasoning86 machine86 learning86 model86", 28),
        ["vector86 processor86", "reasoning86 machine86", "learning86 model86"],
    ),
    (
        ("processor86 reasoning86 machine86 learning86 model86 token86", 6),
        ["processor86", "reasoning86", "machine86", "learning86", "model86", "token86"],
    ),
    (
        ("processor86 reasoning86 machine86 learning86 model86 token86", 10),
        ["processor86", "reasoning86", "machine86", "learning86", "model86", "token86"],
    ),
    (
        ("processor86 reasoning86 machine86 learning86 model86 token86", 18),
        ["processor86", "reasoning86", "machine86", "learning86 model86", "token86"],
    ),
    (
        ("processor86 reasoning86 machine86 learning86 model86 token86", 28),
        ["processor86 reasoning86", "machine86 learning86 model86", "token86"],
    ),
    (
        ("reasoning86 machine86 learning86 model86 token86 prompt86", 6),
        ["reasoning86", "machine86", "learning86", "model86", "token86", "prompt86"],
    ),
    (
        ("reasoning86 machine86 learning86 model86 token86 prompt86", 10),
        ["reasoning86", "machine86", "learning86", "model86", "token86", "prompt86"],
    ),
    (
        ("reasoning86 machine86 learning86 model86 token86 prompt86", 18),
        ["reasoning86", "machine86", "learning86 model86", "token86 prompt86"],
    ),
    (
        ("reasoning86 machine86 learning86 model86 token86 prompt86", 28),
        ["reasoning86 machine86", "learning86 model86 token86", "prompt86"],
    ),
    (
        ("machine86 learning86 model86 token86 prompt86 session86", 6),
        ["machine86", "learning86", "model86", "token86", "prompt86", "session86"],
    ),
    (
        ("machine86 learning86 model86 token86 prompt86 session86", 10),
        ["machine86", "learning86", "model86", "token86", "prompt86", "session86"],
    ),
    (
        ("machine86 learning86 model86 token86 prompt86 session86", 18),
        ["machine86", "learning86 model86", "token86 prompt86", "session86"],
    ),
    (
        ("machine86 learning86 model86 token86 prompt86 session86", 28),
        ["machine86 learning86 model86", "token86 prompt86 session86"],
    ),
    (
        ("learning86 model86 token86 prompt86 session86 library86", 6),
        ["learning86", "model86", "token86", "prompt86", "session86", "library86"],
    ),
    (
        ("learning86 model86 token86 prompt86 session86 library86", 10),
        ["learning86", "model86", "token86", "prompt86", "session86", "library86"],
    ),
    (
        ("learning86 model86 token86 prompt86 session86 library86", 18),
        ["learning86 model86", "token86 prompt86", "session86", "library86"],
    ),
    (
        ("learning86 model86 token86 prompt86 session86 library86", 28),
        ["learning86 model86 token86", "prompt86 session86 library86"],
    ),
    (
        ("model86 token86 prompt86 session86 library86 service86", 6),
        ["model86", "token86", "prompt86", "session86", "library86", "service86"],
    ),
    (
        ("model86 token86 prompt86 session86 library86 service86", 10),
        ["model86", "token86", "prompt86", "session86", "library86", "service86"],
    ),
    (
        ("model86 token86 prompt86 session86 library86 service86", 18),
        ["model86 token86", "prompt86 session86", "library86", "service86"],
    ),
    (
        ("model86 token86 prompt86 session86 library86 service86", 28),
        ["model86 token86 prompt86", "session86 library86", "service86"],
    ),
    (
        ("token86 prompt86 session86 library86 service86 gateway86", 6),
        ["token86", "prompt86", "session86", "library86", "service86", "gateway86"],
    ),
    (
        ("token86 prompt86 session86 library86 service86 gateway86", 10),
        ["token86", "prompt86", "session86", "library86", "service86", "gateway86"],
    ),
    (
        ("token86 prompt86 session86 library86 service86 gateway86", 18),
        ["token86 prompt86", "session86", "library86", "service86", "gateway86"],
    ),
    (
        ("token86 prompt86 session86 library86 service86 gateway86", 28),
        ["token86 prompt86 session86", "library86 service86", "gateway86"],
    ),
    (
        ("prompt86 session86 library86 service86 gateway86 storage86", 6),
        ["prompt86", "session86", "library86", "service86", "gateway86", "storage86"],
    ),
    (
        ("prompt86 session86 library86 service86 gateway86 storage86", 10),
        ["prompt86", "session86", "library86", "service86", "gateway86", "storage86"],
    ),
    (
        ("prompt86 session86 library86 service86 gateway86 storage86", 18),
        ["prompt86 session86", "library86", "service86", "gateway86", "storage86"],
    ),
    (
        ("prompt86 session86 library86 service86 gateway86 storage86", 28),
        ["prompt86 session86 library86", "service86 gateway86", "storage86"],
    ),
    (
        ("session86 library86 service86 gateway86 storage86 network86", 6),
        ["session86", "library86", "service86", "gateway86", "storage86", "network86"],
    ),
    (
        ("session86 library86 service86 gateway86 storage86 network86", 10),
        ["session86", "library86", "service86", "gateway86", "storage86", "network86"],
    ),
    (
        ("session86 library86 service86 gateway86 storage86 network86", 18),
        ["session86", "library86", "service86", "gateway86", "storage86", "network86"],
    ),
    (
        ("session86 library86 service86 gateway86 storage86 network86", 28),
        ["session86 library86", "service86 gateway86", "storage86 network86"],
    ),
    (
        ("library86 service86 gateway86 storage86 network86 latency86", 6),
        ["library86", "service86", "gateway86", "storage86", "network86", "latency86"],
    ),
    (
        ("library86 service86 gateway86 storage86 network86 latency86", 10),
        ["library86", "service86", "gateway86", "storage86", "network86", "latency86"],
    ),
    (
        ("library86 service86 gateway86 storage86 network86 latency86", 18),
        ["library86", "service86", "gateway86", "storage86", "network86", "latency86"],
    ),
    (
        ("library86 service86 gateway86 storage86 network86 latency86", 28),
        ["library86 service86", "gateway86 storage86", "network86 latency86"],
    ),
    (
        ("service86 gateway86 storage86 network86 latency86 buffer86", 6),
        ["service86", "gateway86", "storage86", "network86", "latency86", "buffer86"],
    ),
    (
        ("service86 gateway86 storage86 network86 latency86 buffer86", 10),
        ["service86", "gateway86", "storage86", "network86", "latency86", "buffer86"],
    ),
    (
        ("service86 gateway86 storage86 network86 latency86 buffer86", 18),
        ["service86", "gateway86", "storage86", "network86", "latency86 buffer86"],
    ),
    (
        ("service86 gateway86 storage86 network86 latency86 buffer86", 28),
        ["service86 gateway86", "storage86 network86", "latency86 buffer86"],
    ),
    (
        ("gateway86 storage86 network86 latency86 buffer86 queue86", 6),
        ["gateway86", "storage86", "network86", "latency86", "buffer86", "queue86"],
    ),
    (
        ("gateway86 storage86 network86 latency86 buffer86 queue86", 10),
        ["gateway86", "storage86", "network86", "latency86", "buffer86", "queue86"],
    ),
    (
        ("gateway86 storage86 network86 latency86 buffer86 queue86", 18),
        ["gateway86", "storage86", "network86", "latency86 buffer86", "queue86"],
    ),
    (
        ("gateway86 storage86 network86 latency86 buffer86 queue86", 28),
        ["gateway86 storage86", "network86 latency86 buffer86", "queue86"],
    ),
    (
        ("storage86 network86 latency86 buffer86 queue86 worker86", 6),
        ["storage86", "network86", "latency86", "buffer86", "queue86", "worker86"],
    ),
    (
        ("storage86 network86 latency86 buffer86 queue86 worker86", 10),
        ["storage86", "network86", "latency86", "buffer86", "queue86", "worker86"],
    ),
    (
        ("storage86 network86 latency86 buffer86 queue86 worker86", 18),
        ["storage86", "network86", "latency86 buffer86", "queue86 worker86"],
    ),
    (
        ("storage86 network86 latency86 buffer86 queue86 worker86", 28),
        ["storage86 network86", "latency86 buffer86 queue86", "worker86"],
    ),
    (
        ("network86 latency86 buffer86 queue86 worker86 kernel86", 6),
        ["network86", "latency86", "buffer86", "queue86", "worker86", "kernel86"],
    ),
    (
        ("network86 latency86 buffer86 queue86 worker86 kernel86", 10),
        ["network86", "latency86", "buffer86", "queue86", "worker86", "kernel86"],
    ),
    (
        ("network86 latency86 buffer86 queue86 worker86 kernel86", 18),
        ["network86", "latency86 buffer86", "queue86 worker86", "kernel86"],
    ),
    (
        ("network86 latency86 buffer86 queue86 worker86 kernel86", 28),
        ["network86 latency86 buffer86", "queue86 worker86 kernel86"],
    ),
    (
        ("latency86 buffer86 queue86 worker86 kernel86 signal86", 6),
        ["latency86", "buffer86", "queue86", "worker86", "kernel86", "signal86"],
    ),
    (
        ("latency86 buffer86 queue86 worker86 kernel86 signal86", 10),
        ["latency86", "buffer86", "queue86", "worker86", "kernel86", "signal86"],
    ),
    (
        ("latency86 buffer86 queue86 worker86 kernel86 signal86", 18),
        ["latency86 buffer86", "queue86 worker86", "kernel86 signal86"],
    ),
    (
        ("latency86 buffer86 queue86 worker86 kernel86 signal86", 28),
        ["latency86 buffer86 queue86", "worker86 kernel86 signal86"],
    ),
    (
        ("buffer86 queue86 worker86 kernel86 signal86 packet86", 6),
        ["buffer86", "queue86", "worker86", "kernel86", "signal86", "packet86"],
    ),
    (
        ("buffer86 queue86 worker86 kernel86 signal86 packet86", 10),
        ["buffer86", "queue86", "worker86", "kernel86", "signal86", "packet86"],
    ),
    (
        ("buffer86 queue86 worker86 kernel86 signal86 packet86", 18),
        ["buffer86 queue86", "worker86 kernel86", "signal86 packet86"],
    ),
    (
        ("buffer86 queue86 worker86 kernel86 signal86 packet86", 28),
        ["buffer86 queue86 worker86", "kernel86 signal86 packet86"],
    ),
    (
        ("queue86 worker86 kernel86 signal86 packet86 router86", 6),
        ["queue86", "worker86", "kernel86", "signal86", "packet86", "router86"],
    ),
    (
        ("queue86 worker86 kernel86 signal86 packet86 router86", 10),
        ["queue86", "worker86", "kernel86", "signal86", "packet86", "router86"],
    ),
    (
        ("queue86 worker86 kernel86 signal86 packet86 router86", 18),
        ["queue86 worker86", "kernel86 signal86", "packet86 router86"],
    ),
    (
        ("queue86 worker86 kernel86 signal86 packet86 router86", 28),
        ["queue86 worker86 kernel86", "signal86 packet86 router86"],
    ),
    (
        ("worker86 kernel86 signal86 packet86 router86 cluster86", 6),
        ["worker86", "kernel86", "signal86", "packet86", "router86", "cluster86"],
    ),
    (
        ("worker86 kernel86 signal86 packet86 router86 cluster86", 10),
        ["worker86", "kernel86", "signal86", "packet86", "router86", "cluster86"],
    ),
    (
        ("worker86 kernel86 signal86 packet86 router86 cluster86", 18),
        ["worker86 kernel86", "signal86 packet86", "router86 cluster86"],
    ),
    (
        ("worker86 kernel86 signal86 packet86 router86 cluster86", 28),
        ["worker86 kernel86 signal86", "packet86 router86 cluster86"],
    ),
    (
        ("kernel86 signal86 packet86 router86 cluster86 mirror86", 6),
        ["kernel86", "signal86", "packet86", "router86", "cluster86", "mirror86"],
    ),
    (
        ("kernel86 signal86 packet86 router86 cluster86 mirror86", 10),
        ["kernel86", "signal86", "packet86", "router86", "cluster86", "mirror86"],
    ),
    (
        ("kernel86 signal86 packet86 router86 cluster86 mirror86", 18),
        ["kernel86 signal86", "packet86 router86", "cluster86 mirror86"],
    ),
    (
        ("kernel86 signal86 packet86 router86 cluster86 mirror86", 28),
        ["kernel86 signal86 packet86", "router86 cluster86 mirror86"],
    ),
    (
        ("signal86 packet86 router86 cluster86 mirror86 filter86", 6),
        ["signal86", "packet86", "router86", "cluster86", "mirror86", "filter86"],
    ),
    (
        ("signal86 packet86 router86 cluster86 mirror86 filter86", 10),
        ["signal86", "packet86", "router86", "cluster86", "mirror86", "filter86"],
    ),
    (
        ("signal86 packet86 router86 cluster86 mirror86 filter86", 18),
        ["signal86 packet86", "router86 cluster86", "mirror86 filter86"],
    ),
    (
        ("signal86 packet86 router86 cluster86 mirror86 filter86", 28),
        ["signal86 packet86 router86", "cluster86 mirror86 filter86"],
    ),
    (
        ("packet86 router86 cluster86 mirror86 filter86 ranking86", 6),
        ["packet86", "router86", "cluster86", "mirror86", "filter86", "ranking86"],
    ),
    (
        ("packet86 router86 cluster86 mirror86 filter86 ranking86", 10),
        ["packet86", "router86", "cluster86", "mirror86", "filter86", "ranking86"],
    ),
    (
        ("packet86 router86 cluster86 mirror86 filter86 ranking86", 18),
        ["packet86 router86", "cluster86 mirror86", "filter86 ranking86"],
    ),
    (
        ("packet86 router86 cluster86 mirror86 filter86 ranking86", 28),
        ["packet86 router86 cluster86", "mirror86 filter86 ranking86"],
    ),
    (
        ("router86 cluster86 mirror86 filter86 ranking86 encoding86", 6),
        ["router86", "cluster86", "mirror86", "filter86", "ranking86", "encoding86"],
    ),
    (
        ("router86 cluster86 mirror86 filter86 ranking86 encoding86", 10),
        ["router86", "cluster86", "mirror86", "filter86", "ranking86", "encoding86"],
    ),
    (
        ("router86 cluster86 mirror86 filter86 ranking86 encoding86", 18),
        ["router86 cluster86", "mirror86 filter86", "ranking86", "encoding86"],
    ),
    (
        ("router86 cluster86 mirror86 filter86 ranking86 encoding86", 28),
        ["router86 cluster86 mirror86", "filter86 ranking86", "encoding86"],
    ),
    (
        ("cluster86 mirror86 filter86 ranking86 encoding86 mapping86", 6),
        ["cluster86", "mirror86", "filter86", "ranking86", "encoding86", "mapping86"],
    ),
    (
        ("cluster86 mirror86 filter86 ranking86 encoding86 mapping86", 10),
        ["cluster86", "mirror86", "filter86", "ranking86", "encoding86", "mapping86"],
    ),
    (
        ("cluster86 mirror86 filter86 ranking86 encoding86 mapping86", 18),
        ["cluster86 mirror86", "filter86 ranking86", "encoding86", "mapping86"],
    ),
    (
        ("cluster86 mirror86 filter86 ranking86 encoding86 mapping86", 28),
        ["cluster86 mirror86 filter86", "ranking86 encoding86", "mapping86"],
    ),
    (
        ("mirror86 filter86 ranking86 encoding86 mapping86 record86", 6),
        ["mirror86", "filter86", "ranking86", "encoding86", "mapping86", "record86"],
    ),
    (
        ("mirror86 filter86 ranking86 encoding86 mapping86 record86", 10),
        ["mirror86", "filter86", "ranking86", "encoding86", "mapping86", "record86"],
    ),
    (
        ("mirror86 filter86 ranking86 encoding86 mapping86 record86", 18),
        ["mirror86 filter86", "ranking86", "encoding86", "mapping86 record86"],
    ),
    (
        ("mirror86 filter86 ranking86 encoding86 mapping86 record86", 28),
        ["mirror86 filter86 ranking86", "encoding86 mapping86", "record86"],
    ),
    (
        ("filter86 ranking86 encoding86 mapping86 record86 candle86", 6),
        ["filter86", "ranking86", "encoding86", "mapping86", "record86", "candle86"],
    ),
    (
        ("filter86 ranking86 encoding86 mapping86 record86 candle86", 10),
        ["filter86", "ranking86", "encoding86", "mapping86", "record86", "candle86"],
    ),
    (
        ("filter86 ranking86 encoding86 mapping86 record86 candle86", 18),
        ["filter86 ranking86", "encoding86", "mapping86 record86", "candle86"],
    ),
    (
        ("filter86 ranking86 encoding86 mapping86 record86 candle86", 28),
        ["filter86 ranking86", "encoding86 mapping86", "record86 candle86"],
    ),
    (
        ("ranking86 encoding86 mapping86 record86 candle86 thread86", 6),
        ["ranking86", "encoding86", "mapping86", "record86", "candle86", "thread86"],
    ),
    (
        ("ranking86 encoding86 mapping86 record86 candle86 thread86", 10),
        ["ranking86", "encoding86", "mapping86", "record86", "candle86", "thread86"],
    ),
    (
        ("ranking86 encoding86 mapping86 record86 candle86 thread86", 18),
        ["ranking86", "encoding86", "mapping86 record86", "candle86 thread86"],
    ),
    (
        ("ranking86 encoding86 mapping86 record86 candle86 thread86", 28),
        ["ranking86 encoding86", "mapping86 record86 candle86", "thread86"],
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
