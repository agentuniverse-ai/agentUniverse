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
        ("round 59: the quick brown fox jumps over the lazy dog", 4),
        ["round", "59:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 59: the quick brown fox jumps over the lazy dog", 8),
        ["round", "59: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 59: the quick brown fox jumps over the lazy dog", 12),
        ["round 59:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 59: the quick brown fox jumps over the lazy dog", 16),
        ["round 59: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 59: the quick brown fox jumps over the lazy dog", 24),
        ["round 59: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 59: the quick brown fox jumps over the lazy dog", 32),
        ["round 59: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 59: agentuniverse is a framework for multi agents", 4),
        ["round", "59:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 59: agentuniverse is a framework for multi agents", 8),
        ["round", "59:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 59: agentuniverse is a framework for multi agents", 12),
        ["round 59:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 59: agentuniverse is a framework for multi agents", 16),
        ["round 59:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 59: agentuniverse is a framework for multi agents", 24),
        ["round 59: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 59: agentuniverse is a framework for multi agents", 32),
        ["round 59: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 59: knowledge stored as vectors enables retrieval", 4),
        ["round", "59:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 59: knowledge stored as vectors enables retrieval", 8),
        ["round", "59:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 59: knowledge stored as vectors enables retrieval", 12),
        ["round 59:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 59: knowledge stored as vectors enables retrieval", 16),
        ["round 59:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 59: knowledge stored as vectors enables retrieval", 24),
        ["round 59: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 59: knowledge stored as vectors enables retrieval", 32),
        ["round 59: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 59: the processor reads the record then stops", 4),
        ["round", "59:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 59: the processor reads the record then stops", 8),
        ["round", "59: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 59: the processor reads the record then stops", 12),
        ["round 59:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 59: the processor reads the record then stops", 16),
        ["round 59: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 59: the processor reads the record then stops", 24),
        ["round 59: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 59: the processor reads the record then stops", 32),
        ["round 59: the processor reads", "the record then stops"],
    ),
    (
        ("round 59: a worker pulls the next task from the queue", 4),
        ["round", "59:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 59: a worker pulls the next task from the queue", 8),
        ["round", "59: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 59: a worker pulls the next task from the queue", 12),
        ["round 59: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 59: a worker pulls the next task from the queue", 16),
        ["round 59: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 59: a worker pulls the next task from the queue", 24),
        ["round 59: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 59: a worker pulls the next task from the queue", 32),
        ["round 59: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 59: signals travel through the network layer", 4),
        ["round", "59:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 59: signals travel through the network layer", 8),
        ["round", "59:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 59: signals travel through the network layer", 12),
        ["round 59:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 59: signals travel through the network layer", 16),
        ["round 59:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 59: signals travel through the network layer", 24),
        ["round 59: signals travel", "through the network", "layer"],
    ),
    (
        ("round 59: signals travel through the network layer", 32),
        ["round 59: signals travel through", "the network layer"],
    ),
    (
        ("round 59: the gateway routes each request by policy", 4),
        ["round", "59:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 59: the gateway routes each request by policy", 8),
        ["round", "59: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 59: the gateway routes each request by policy", 12),
        ["round 59:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 59: the gateway routes each request by policy", 16),
        ["round 59: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 59: the gateway routes each request by policy", 24),
        ["round 59: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 59: the gateway routes each request by policy", 32),
        ["round 59: the gateway routes", "each request by policy"],
    ),
    (
        ("round 59: memory grows until the buffer is full", 4),
        ["round", "59:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 59: memory grows until the buffer is full", 8),
        ["round", "59:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 59: memory grows until the buffer is full", 12),
        ["round 59:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 59: memory grows until the buffer is full", 16),
        ["round 59: memory", "grows until the", "buffer is full"],
    ),
    (("round 59: memory grows until the buffer is full", 24), ["round 59: memory grows", "until the buffer is full"]),
    (("round 59: memory grows until the buffer is full", 32), ["round 59: memory grows until the", "buffer is full"]),
    (
        ("round 59: the cluster mirrors every packet twice", 4),
        ["round", "59:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 59: the cluster mirrors every packet twice", 8),
        ["round", "59: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 59: the cluster mirrors every packet twice", 12),
        ["round 59:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 59: the cluster mirrors every packet twice", 16),
        ["round 59: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 59: the cluster mirrors every packet twice", 24),
        ["round 59: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 59: the cluster mirrors every packet twice", 32), ["round 59: the cluster mirrors", "every packet twice"]),
    (
        ("round 59: ranking uses tokens learned from the corpus", 4),
        ["round", "59:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 59: ranking uses tokens learned from the corpus", 8),
        ["round", "59:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 59: ranking uses tokens learned from the corpus", 12),
        ["round 59:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 59: ranking uses tokens learned from the corpus", 16),
        ["round 59:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 59: ranking uses tokens learned from the corpus", 24),
        ["round 59: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 59: ranking uses tokens learned from the corpus", 32),
        ["round 59: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 59: a long session ends when the candle dies", 4),
        ["round", "59:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 59: a long session ends when the candle dies", 8),
        ["round", "59: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 59: a long session ends when the candle dies", 12),
        ["round 59: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 59: a long session ends when the candle dies", 16),
        ["round 59: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 59: a long session ends when the candle dies", 24),
        ["round 59: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 59: a long session ends when the candle dies", 32),
        ["round 59: a long session ends", "when the candle dies"],
    ),
    (
        ("round 59: encode the prompt then map the result", 4),
        ["round", "59:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 59: encode the prompt then map the result", 8),
        ["round", "59:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 59: encode the prompt then map the result", 12),
        ["round 59:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 59: encode the prompt then map the result", 16),
        ["round 59: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 59: encode the prompt then map the result", 24),
        ["round 59: encode the", "prompt then map the", "result"],
    ),
    (("round 59: encode the prompt then map the result", 32), ["round 59: encode the prompt then", "map the result"]),
    (
        ("round 59: the kernel wakes the worker at dawn", 4),
        ["round", "59:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 59: the kernel wakes the worker at dawn", 8),
        ["round", "59: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 59: the kernel wakes the worker at dawn", 12),
        ["round 59:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 59: the kernel wakes the worker at dawn", 16), ["round 59: the", "kernel wakes the", "worker at dawn"]),
    (("round 59: the kernel wakes the worker at dawn", 24), ["round 59: the kernel", "wakes the worker at dawn"]),
    (("round 59: the kernel wakes the worker at dawn", 32), ["round 59: the kernel wakes the", "worker at dawn"]),
    (
        ("round 59: service latency drops after the patch", 4),
        ["round", "59:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 59: service latency drops after the patch", 8),
        ["round", "59:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 59: service latency drops after the patch", 12),
        ["round 59:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 59: service latency drops after the patch", 16),
        ["round 59:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 59: service latency drops after the patch", 24),
        ["round 59: service", "latency drops after the", "patch"],
    ),
    (("round 59: service latency drops after the patch", 32), ["round 59: service latency drops", "after the patch"]),
    (
        ("round 59: the library caches every vector it sees", 4),
        ["round", "59:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 59: the library caches every vector it sees", 8),
        ["round", "59: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 59: the library caches every vector it sees", 12),
        ["round 59:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 59: the library caches every vector it sees", 16),
        ["round 59: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 59: the library caches every vector it sees", 24),
        ["round 59: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 59: the library caches every vector it sees", 32),
        ["round 59: the library caches", "every vector it sees"],
    ),
    (
        ("round 59: agents argue then the debate resolves", 4),
        ["round", "59:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 59: agents argue then the debate resolves", 8),
        ["round", "59:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 59: agents argue then the debate resolves", 12),
        ["round 59:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 59: agents argue then the debate resolves", 16),
        ["round 59: agents", "argue then the", "debate resolves"],
    ),
    (("round 59: agents argue then the debate resolves", 24), ["round 59: agents argue", "then the debate resolves"]),
    (("round 59: agents argue then the debate resolves", 32), ["round 59: agents argue then the", "debate resolves"]),
    (
        ("round 59: the filter keeps only strong matches", 4),
        ["round", "59:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 59: the filter keeps only strong matches", 8),
        ["round", "59: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 59: the filter keeps only strong matches", 12),
        ["round 59:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 59: the filter keeps only strong matches", 16),
        ["round 59: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 59: the filter keeps only strong matches", 24), ["round 59: the filter", "keeps only strong", "matches"]),
    (("round 59: the filter keeps only strong matches", 32), ["round 59: the filter keeps only", "strong matches"]),
    (
        ("round 59: the model answers with a short reply", 4),
        ["round", "59:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 59: the model answers with a short reply", 8),
        ["round", "59: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 59: the model answers with a short reply", 12),
        ["round 59:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 59: the model answers with a short reply", 16),
        ["round 59: the", "model answers", "with a short", "reply"],
    ),
    (("round 59: the model answers with a short reply", 24), ["round 59: the model", "answers with a short", "reply"]),
    (("round 59: the model answers with a short reply", 32), ["round 59: the model answers with", "a short reply"]),
    (
        ("round 59: the recorder stores the reasoning trace", 4),
        ["round", "59:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 59: the recorder stores the reasoning trace", 8),
        ["round", "59: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 59: the recorder stores the reasoning trace", 12),
        ["round 59:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 59: the recorder stores the reasoning trace", 16),
        ["round 59: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 59: the recorder stores the reasoning trace", 24),
        ["round 59: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 59: the recorder stores the reasoning trace", 32),
        ["round 59: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 59: the angel watches the processor run", 4),
        ["round", "59:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 59: the angel watches the processor run", 8),
        ["round", "59: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 59: the angel watches the processor run", 12),
        ["round 59:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 59: the angel watches the processor run", 16), ["round 59: the", "angel watches", "the processor", "run"]),
    (("round 59: the angel watches the processor run", 24), ["round 59: the angel", "watches the processor", "run"]),
    (("round 59: the angel watches the processor run", 32), ["round 59: the angel watches the", "processor run"]),
    (
        ("round 59: angle of the vector decides the match", 4),
        ["round", "59:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 59: angle of the vector decides the match", 8),
        ["round", "59:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 59: angle of the vector decides the match", 12),
        ["round 59:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 59: angle of the vector decides the match", 16),
        ["round 59: angle", "of the vector", "decides the", "match"],
    ),
    (("round 59: angle of the vector decides the match", 24), ["round 59: angle of the", "vector decides the match"]),
    (("round 59: angle of the vector decides the match", 32), ["round 59: angle of the vector", "decides the match"]),
    (
        ("round 59: the candle burns twice as long at night", 4),
        ["round", "59:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 59: the candle burns twice as long at night", 8),
        ["round", "59: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 59: the candle burns twice as long at night", 12),
        ["round 59:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 59: the candle burns twice as long at night", 16),
        ["round 59: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 59: the candle burns twice as long at night", 24),
        ["round 59: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 59: the candle burns twice as long at night", 32),
        ["round 59: the candle burns twice", "as long at night"],
    ),
    (
        ("round 59: a mirror of the universe in one line", 4),
        ["round", "59:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 59: a mirror of the universe in one line", 8),
        ["round", "59: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 59: a mirror of the universe in one line", 12),
        ["round 59: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 59: a mirror of the universe in one line", 16),
        ["round 59: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 59: a mirror of the universe in one line", 24), ["round 59: a mirror of", "the universe in one line"]),
    (("round 59: a mirror of the universe in one line", 32), ["round 59: a mirror of the", "universe in one line"]),
    (
        ("round 59: the queue drains before the storm", 4),
        ["round", "59:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 59: the queue drains before the storm", 8),
        ["round", "59: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 59: the queue drains before the storm", 12), ["round 59:", "the queue", "drains", "before the", "storm"]),
    (("round 59: the queue drains before the storm", 16), ["round 59: the", "queue drains", "before the storm"]),
    (("round 59: the queue drains before the storm", 24), ["round 59: the queue", "drains before the storm"]),
    (("round 59: the queue drains before the storm", 32), ["round 59: the queue drains", "before the storm"]),
    (
        ("kitten59 sitting59 agent59 angle59 universe59 memory59", 6),
        ["kitten59", "sitting59", "agent59", "angle59", "universe59", "memory59"],
    ),
    (
        ("kitten59 sitting59 agent59 angle59 universe59 memory59", 10),
        ["kitten59", "sitting59", "agent59", "angle59", "universe59", "memory59"],
    ),
    (
        ("kitten59 sitting59 agent59 angle59 universe59 memory59", 18),
        ["kitten59 sitting59", "agent59 angle59", "universe59", "memory59"],
    ),
    (
        ("kitten59 sitting59 agent59 angle59 universe59 memory59", 28),
        ["kitten59 sitting59 agent59", "angle59 universe59 memory59"],
    ),
    (
        ("sitting59 agent59 angle59 universe59 memory59 stream59", 6),
        ["sitting59", "agent59", "angle59", "universe59", "memory59", "stream59"],
    ),
    (
        ("sitting59 agent59 angle59 universe59 memory59 stream59", 10),
        ["sitting59", "agent59", "angle59", "universe59", "memory59", "stream59"],
    ),
    (
        ("sitting59 agent59 angle59 universe59 memory59 stream59", 18),
        ["sitting59 agent59", "angle59 universe59", "memory59 stream59"],
    ),
    (
        ("sitting59 agent59 angle59 universe59 memory59 stream59", 28),
        ["sitting59 agent59 angle59", "universe59 memory59 stream59"],
    ),
    (
        ("agent59 angle59 universe59 memory59 stream59 context59", 6),
        ["agent59", "angle59", "universe59", "memory59", "stream59", "context59"],
    ),
    (
        ("agent59 angle59 universe59 memory59 stream59 context59", 10),
        ["agent59", "angle59", "universe59", "memory59", "stream59", "context59"],
    ),
    (
        ("agent59 angle59 universe59 memory59 stream59 context59", 18),
        ["agent59 angle59", "universe59", "memory59 stream59", "context59"],
    ),
    (
        ("agent59 angle59 universe59 memory59 stream59 context59", 28),
        ["agent59 angle59 universe59", "memory59 stream59 context59"],
    ),
    (
        ("angle59 universe59 memory59 stream59 context59 knowledge59", 6),
        ["angle59", "universe59", "memory59", "stream59", "context59", "knowledge59"],
    ),
    (
        ("angle59 universe59 memory59 stream59 context59 knowledge59", 10),
        ["angle59", "universe59", "memory59", "stream59", "context59", "knowledge59"],
    ),
    (
        ("angle59 universe59 memory59 stream59 context59 knowledge59", 18),
        ["angle59 universe59", "memory59 stream59", "context59", "knowledge59"],
    ),
    (
        ("angle59 universe59 memory59 stream59 context59 knowledge59", 28),
        ["angle59 universe59 memory59", "stream59 context59", "knowledge59"],
    ),
    (
        ("universe59 memory59 stream59 context59 knowledge59 vector59", 6),
        ["universe59", "memory59", "stream59", "context59", "knowledge59", "vector59"],
    ),
    (
        ("universe59 memory59 stream59 context59 knowledge59 vector59", 10),
        ["universe59", "memory59", "stream59", "context59", "knowledge59", "vector59"],
    ),
    (
        ("universe59 memory59 stream59 context59 knowledge59 vector59", 18),
        ["universe59", "memory59 stream59", "context59", "knowledge59", "vector59"],
    ),
    (
        ("universe59 memory59 stream59 context59 knowledge59 vector59", 28),
        ["universe59 memory59 stream59", "context59 knowledge59", "vector59"],
    ),
    (
        ("memory59 stream59 context59 knowledge59 vector59 processor59", 6),
        ["memory59", "stream59", "context59", "knowledge59", "vector59", "processor59"],
    ),
    (
        ("memory59 stream59 context59 knowledge59 vector59 processor59", 10),
        ["memory59", "stream59", "context59", "knowledge59", "vector59", "processor59"],
    ),
    (
        ("memory59 stream59 context59 knowledge59 vector59 processor59", 18),
        ["memory59 stream59", "context59", "knowledge59", "vector59", "processor59"],
    ),
    (
        ("memory59 stream59 context59 knowledge59 vector59 processor59", 28),
        ["memory59 stream59 context59", "knowledge59 vector59", "processor59"],
    ),
    (
        ("stream59 context59 knowledge59 vector59 processor59 reasoning59", 6),
        ["stream59", "context59", "knowledge59", "vector59", "processor59", "reasoning59"],
    ),
    (
        ("stream59 context59 knowledge59 vector59 processor59 reasoning59", 10),
        ["stream59", "context59", "knowledge59", "vector59", "processor59", "reasoning59"],
    ),
    (
        ("stream59 context59 knowledge59 vector59 processor59 reasoning59", 18),
        ["stream59 context59", "knowledge59", "vector59", "processor59", "reasoning59"],
    ),
    (
        ("stream59 context59 knowledge59 vector59 processor59 reasoning59", 28),
        ["stream59 context59", "knowledge59 vector59", "processor59 reasoning59"],
    ),
    (
        ("context59 knowledge59 vector59 processor59 reasoning59 machine59", 6),
        ["context59", "knowledge59", "vector59", "processor59", "reasoning59", "machine59"],
    ),
    (
        ("context59 knowledge59 vector59 processor59 reasoning59 machine59", 10),
        ["context59", "knowledge59", "vector59", "processor59", "reasoning59", "machine59"],
    ),
    (
        ("context59 knowledge59 vector59 processor59 reasoning59 machine59", 18),
        ["context59", "knowledge59", "vector59", "processor59", "reasoning59", "machine59"],
    ),
    (
        ("context59 knowledge59 vector59 processor59 reasoning59 machine59", 28),
        ["context59 knowledge59", "vector59 processor59", "reasoning59 machine59"],
    ),
    (
        ("knowledge59 vector59 processor59 reasoning59 machine59 learning59", 6),
        ["knowledge59", "vector59", "processor59", "reasoning59", "machine59", "learning59"],
    ),
    (
        ("knowledge59 vector59 processor59 reasoning59 machine59 learning59", 10),
        ["knowledge59", "vector59", "processor59", "reasoning59", "machine59", "learning59"],
    ),
    (
        ("knowledge59 vector59 processor59 reasoning59 machine59 learning59", 18),
        ["knowledge59", "vector59", "processor59", "reasoning59", "machine59", "learning59"],
    ),
    (
        ("knowledge59 vector59 processor59 reasoning59 machine59 learning59", 28),
        ["knowledge59 vector59", "processor59 reasoning59", "machine59 learning59"],
    ),
    (
        ("vector59 processor59 reasoning59 machine59 learning59 model59", 6),
        ["vector59", "processor59", "reasoning59", "machine59", "learning59", "model59"],
    ),
    (
        ("vector59 processor59 reasoning59 machine59 learning59 model59", 10),
        ["vector59", "processor59", "reasoning59", "machine59", "learning59", "model59"],
    ),
    (
        ("vector59 processor59 reasoning59 machine59 learning59 model59", 18),
        ["vector59", "processor59", "reasoning59", "machine59", "learning59 model59"],
    ),
    (
        ("vector59 processor59 reasoning59 machine59 learning59 model59", 28),
        ["vector59 processor59", "reasoning59 machine59", "learning59 model59"],
    ),
    (
        ("processor59 reasoning59 machine59 learning59 model59 token59", 6),
        ["processor59", "reasoning59", "machine59", "learning59", "model59", "token59"],
    ),
    (
        ("processor59 reasoning59 machine59 learning59 model59 token59", 10),
        ["processor59", "reasoning59", "machine59", "learning59", "model59", "token59"],
    ),
    (
        ("processor59 reasoning59 machine59 learning59 model59 token59", 18),
        ["processor59", "reasoning59", "machine59", "learning59 model59", "token59"],
    ),
    (
        ("processor59 reasoning59 machine59 learning59 model59 token59", 28),
        ["processor59 reasoning59", "machine59 learning59 model59", "token59"],
    ),
    (
        ("reasoning59 machine59 learning59 model59 token59 prompt59", 6),
        ["reasoning59", "machine59", "learning59", "model59", "token59", "prompt59"],
    ),
    (
        ("reasoning59 machine59 learning59 model59 token59 prompt59", 10),
        ["reasoning59", "machine59", "learning59", "model59", "token59", "prompt59"],
    ),
    (
        ("reasoning59 machine59 learning59 model59 token59 prompt59", 18),
        ["reasoning59", "machine59", "learning59 model59", "token59 prompt59"],
    ),
    (
        ("reasoning59 machine59 learning59 model59 token59 prompt59", 28),
        ["reasoning59 machine59", "learning59 model59 token59", "prompt59"],
    ),
    (
        ("machine59 learning59 model59 token59 prompt59 session59", 6),
        ["machine59", "learning59", "model59", "token59", "prompt59", "session59"],
    ),
    (
        ("machine59 learning59 model59 token59 prompt59 session59", 10),
        ["machine59", "learning59", "model59", "token59", "prompt59", "session59"],
    ),
    (
        ("machine59 learning59 model59 token59 prompt59 session59", 18),
        ["machine59", "learning59 model59", "token59 prompt59", "session59"],
    ),
    (
        ("machine59 learning59 model59 token59 prompt59 session59", 28),
        ["machine59 learning59 model59", "token59 prompt59 session59"],
    ),
    (
        ("learning59 model59 token59 prompt59 session59 library59", 6),
        ["learning59", "model59", "token59", "prompt59", "session59", "library59"],
    ),
    (
        ("learning59 model59 token59 prompt59 session59 library59", 10),
        ["learning59", "model59", "token59", "prompt59", "session59", "library59"],
    ),
    (
        ("learning59 model59 token59 prompt59 session59 library59", 18),
        ["learning59 model59", "token59 prompt59", "session59", "library59"],
    ),
    (
        ("learning59 model59 token59 prompt59 session59 library59", 28),
        ["learning59 model59 token59", "prompt59 session59 library59"],
    ),
    (
        ("model59 token59 prompt59 session59 library59 service59", 6),
        ["model59", "token59", "prompt59", "session59", "library59", "service59"],
    ),
    (
        ("model59 token59 prompt59 session59 library59 service59", 10),
        ["model59", "token59", "prompt59", "session59", "library59", "service59"],
    ),
    (
        ("model59 token59 prompt59 session59 library59 service59", 18),
        ["model59 token59", "prompt59 session59", "library59", "service59"],
    ),
    (
        ("model59 token59 prompt59 session59 library59 service59", 28),
        ["model59 token59 prompt59", "session59 library59", "service59"],
    ),
    (
        ("token59 prompt59 session59 library59 service59 gateway59", 6),
        ["token59", "prompt59", "session59", "library59", "service59", "gateway59"],
    ),
    (
        ("token59 prompt59 session59 library59 service59 gateway59", 10),
        ["token59", "prompt59", "session59", "library59", "service59", "gateway59"],
    ),
    (
        ("token59 prompt59 session59 library59 service59 gateway59", 18),
        ["token59 prompt59", "session59", "library59", "service59", "gateway59"],
    ),
    (
        ("token59 prompt59 session59 library59 service59 gateway59", 28),
        ["token59 prompt59 session59", "library59 service59", "gateway59"],
    ),
    (
        ("prompt59 session59 library59 service59 gateway59 storage59", 6),
        ["prompt59", "session59", "library59", "service59", "gateway59", "storage59"],
    ),
    (
        ("prompt59 session59 library59 service59 gateway59 storage59", 10),
        ["prompt59", "session59", "library59", "service59", "gateway59", "storage59"],
    ),
    (
        ("prompt59 session59 library59 service59 gateway59 storage59", 18),
        ["prompt59 session59", "library59", "service59", "gateway59", "storage59"],
    ),
    (
        ("prompt59 session59 library59 service59 gateway59 storage59", 28),
        ["prompt59 session59 library59", "service59 gateway59", "storage59"],
    ),
    (
        ("session59 library59 service59 gateway59 storage59 network59", 6),
        ["session59", "library59", "service59", "gateway59", "storage59", "network59"],
    ),
    (
        ("session59 library59 service59 gateway59 storage59 network59", 10),
        ["session59", "library59", "service59", "gateway59", "storage59", "network59"],
    ),
    (
        ("session59 library59 service59 gateway59 storage59 network59", 18),
        ["session59", "library59", "service59", "gateway59", "storage59", "network59"],
    ),
    (
        ("session59 library59 service59 gateway59 storage59 network59", 28),
        ["session59 library59", "service59 gateway59", "storage59 network59"],
    ),
    (
        ("library59 service59 gateway59 storage59 network59 latency59", 6),
        ["library59", "service59", "gateway59", "storage59", "network59", "latency59"],
    ),
    (
        ("library59 service59 gateway59 storage59 network59 latency59", 10),
        ["library59", "service59", "gateway59", "storage59", "network59", "latency59"],
    ),
    (
        ("library59 service59 gateway59 storage59 network59 latency59", 18),
        ["library59", "service59", "gateway59", "storage59", "network59", "latency59"],
    ),
    (
        ("library59 service59 gateway59 storage59 network59 latency59", 28),
        ["library59 service59", "gateway59 storage59", "network59 latency59"],
    ),
    (
        ("service59 gateway59 storage59 network59 latency59 buffer59", 6),
        ["service59", "gateway59", "storage59", "network59", "latency59", "buffer59"],
    ),
    (
        ("service59 gateway59 storage59 network59 latency59 buffer59", 10),
        ["service59", "gateway59", "storage59", "network59", "latency59", "buffer59"],
    ),
    (
        ("service59 gateway59 storage59 network59 latency59 buffer59", 18),
        ["service59", "gateway59", "storage59", "network59", "latency59 buffer59"],
    ),
    (
        ("service59 gateway59 storage59 network59 latency59 buffer59", 28),
        ["service59 gateway59", "storage59 network59", "latency59 buffer59"],
    ),
    (
        ("gateway59 storage59 network59 latency59 buffer59 queue59", 6),
        ["gateway59", "storage59", "network59", "latency59", "buffer59", "queue59"],
    ),
    (
        ("gateway59 storage59 network59 latency59 buffer59 queue59", 10),
        ["gateway59", "storage59", "network59", "latency59", "buffer59", "queue59"],
    ),
    (
        ("gateway59 storage59 network59 latency59 buffer59 queue59", 18),
        ["gateway59", "storage59", "network59", "latency59 buffer59", "queue59"],
    ),
    (
        ("gateway59 storage59 network59 latency59 buffer59 queue59", 28),
        ["gateway59 storage59", "network59 latency59 buffer59", "queue59"],
    ),
    (
        ("storage59 network59 latency59 buffer59 queue59 worker59", 6),
        ["storage59", "network59", "latency59", "buffer59", "queue59", "worker59"],
    ),
    (
        ("storage59 network59 latency59 buffer59 queue59 worker59", 10),
        ["storage59", "network59", "latency59", "buffer59", "queue59", "worker59"],
    ),
    (
        ("storage59 network59 latency59 buffer59 queue59 worker59", 18),
        ["storage59", "network59", "latency59 buffer59", "queue59 worker59"],
    ),
    (
        ("storage59 network59 latency59 buffer59 queue59 worker59", 28),
        ["storage59 network59", "latency59 buffer59 queue59", "worker59"],
    ),
    (
        ("network59 latency59 buffer59 queue59 worker59 kernel59", 6),
        ["network59", "latency59", "buffer59", "queue59", "worker59", "kernel59"],
    ),
    (
        ("network59 latency59 buffer59 queue59 worker59 kernel59", 10),
        ["network59", "latency59", "buffer59", "queue59", "worker59", "kernel59"],
    ),
    (
        ("network59 latency59 buffer59 queue59 worker59 kernel59", 18),
        ["network59", "latency59 buffer59", "queue59 worker59", "kernel59"],
    ),
    (
        ("network59 latency59 buffer59 queue59 worker59 kernel59", 28),
        ["network59 latency59 buffer59", "queue59 worker59 kernel59"],
    ),
    (
        ("latency59 buffer59 queue59 worker59 kernel59 signal59", 6),
        ["latency59", "buffer59", "queue59", "worker59", "kernel59", "signal59"],
    ),
    (
        ("latency59 buffer59 queue59 worker59 kernel59 signal59", 10),
        ["latency59", "buffer59", "queue59", "worker59", "kernel59", "signal59"],
    ),
    (
        ("latency59 buffer59 queue59 worker59 kernel59 signal59", 18),
        ["latency59 buffer59", "queue59 worker59", "kernel59 signal59"],
    ),
    (
        ("latency59 buffer59 queue59 worker59 kernel59 signal59", 28),
        ["latency59 buffer59 queue59", "worker59 kernel59 signal59"],
    ),
    (
        ("buffer59 queue59 worker59 kernel59 signal59 packet59", 6),
        ["buffer59", "queue59", "worker59", "kernel59", "signal59", "packet59"],
    ),
    (
        ("buffer59 queue59 worker59 kernel59 signal59 packet59", 10),
        ["buffer59", "queue59", "worker59", "kernel59", "signal59", "packet59"],
    ),
    (
        ("buffer59 queue59 worker59 kernel59 signal59 packet59", 18),
        ["buffer59 queue59", "worker59 kernel59", "signal59 packet59"],
    ),
    (
        ("buffer59 queue59 worker59 kernel59 signal59 packet59", 28),
        ["buffer59 queue59 worker59", "kernel59 signal59 packet59"],
    ),
    (
        ("queue59 worker59 kernel59 signal59 packet59 router59", 6),
        ["queue59", "worker59", "kernel59", "signal59", "packet59", "router59"],
    ),
    (
        ("queue59 worker59 kernel59 signal59 packet59 router59", 10),
        ["queue59", "worker59", "kernel59", "signal59", "packet59", "router59"],
    ),
    (
        ("queue59 worker59 kernel59 signal59 packet59 router59", 18),
        ["queue59 worker59", "kernel59 signal59", "packet59 router59"],
    ),
    (
        ("queue59 worker59 kernel59 signal59 packet59 router59", 28),
        ["queue59 worker59 kernel59", "signal59 packet59 router59"],
    ),
    (
        ("worker59 kernel59 signal59 packet59 router59 cluster59", 6),
        ["worker59", "kernel59", "signal59", "packet59", "router59", "cluster59"],
    ),
    (
        ("worker59 kernel59 signal59 packet59 router59 cluster59", 10),
        ["worker59", "kernel59", "signal59", "packet59", "router59", "cluster59"],
    ),
    (
        ("worker59 kernel59 signal59 packet59 router59 cluster59", 18),
        ["worker59 kernel59", "signal59 packet59", "router59 cluster59"],
    ),
    (
        ("worker59 kernel59 signal59 packet59 router59 cluster59", 28),
        ["worker59 kernel59 signal59", "packet59 router59 cluster59"],
    ),
    (
        ("kernel59 signal59 packet59 router59 cluster59 mirror59", 6),
        ["kernel59", "signal59", "packet59", "router59", "cluster59", "mirror59"],
    ),
    (
        ("kernel59 signal59 packet59 router59 cluster59 mirror59", 10),
        ["kernel59", "signal59", "packet59", "router59", "cluster59", "mirror59"],
    ),
    (
        ("kernel59 signal59 packet59 router59 cluster59 mirror59", 18),
        ["kernel59 signal59", "packet59 router59", "cluster59 mirror59"],
    ),
    (
        ("kernel59 signal59 packet59 router59 cluster59 mirror59", 28),
        ["kernel59 signal59 packet59", "router59 cluster59 mirror59"],
    ),
    (
        ("signal59 packet59 router59 cluster59 mirror59 filter59", 6),
        ["signal59", "packet59", "router59", "cluster59", "mirror59", "filter59"],
    ),
    (
        ("signal59 packet59 router59 cluster59 mirror59 filter59", 10),
        ["signal59", "packet59", "router59", "cluster59", "mirror59", "filter59"],
    ),
    (
        ("signal59 packet59 router59 cluster59 mirror59 filter59", 18),
        ["signal59 packet59", "router59 cluster59", "mirror59 filter59"],
    ),
    (
        ("signal59 packet59 router59 cluster59 mirror59 filter59", 28),
        ["signal59 packet59 router59", "cluster59 mirror59 filter59"],
    ),
    (
        ("packet59 router59 cluster59 mirror59 filter59 ranking59", 6),
        ["packet59", "router59", "cluster59", "mirror59", "filter59", "ranking59"],
    ),
    (
        ("packet59 router59 cluster59 mirror59 filter59 ranking59", 10),
        ["packet59", "router59", "cluster59", "mirror59", "filter59", "ranking59"],
    ),
    (
        ("packet59 router59 cluster59 mirror59 filter59 ranking59", 18),
        ["packet59 router59", "cluster59 mirror59", "filter59 ranking59"],
    ),
    (
        ("packet59 router59 cluster59 mirror59 filter59 ranking59", 28),
        ["packet59 router59 cluster59", "mirror59 filter59 ranking59"],
    ),
    (
        ("router59 cluster59 mirror59 filter59 ranking59 encoding59", 6),
        ["router59", "cluster59", "mirror59", "filter59", "ranking59", "encoding59"],
    ),
    (
        ("router59 cluster59 mirror59 filter59 ranking59 encoding59", 10),
        ["router59", "cluster59", "mirror59", "filter59", "ranking59", "encoding59"],
    ),
    (
        ("router59 cluster59 mirror59 filter59 ranking59 encoding59", 18),
        ["router59 cluster59", "mirror59 filter59", "ranking59", "encoding59"],
    ),
    (
        ("router59 cluster59 mirror59 filter59 ranking59 encoding59", 28),
        ["router59 cluster59 mirror59", "filter59 ranking59", "encoding59"],
    ),
    (
        ("cluster59 mirror59 filter59 ranking59 encoding59 mapping59", 6),
        ["cluster59", "mirror59", "filter59", "ranking59", "encoding59", "mapping59"],
    ),
    (
        ("cluster59 mirror59 filter59 ranking59 encoding59 mapping59", 10),
        ["cluster59", "mirror59", "filter59", "ranking59", "encoding59", "mapping59"],
    ),
    (
        ("cluster59 mirror59 filter59 ranking59 encoding59 mapping59", 18),
        ["cluster59 mirror59", "filter59 ranking59", "encoding59", "mapping59"],
    ),
    (
        ("cluster59 mirror59 filter59 ranking59 encoding59 mapping59", 28),
        ["cluster59 mirror59 filter59", "ranking59 encoding59", "mapping59"],
    ),
    (
        ("mirror59 filter59 ranking59 encoding59 mapping59 record59", 6),
        ["mirror59", "filter59", "ranking59", "encoding59", "mapping59", "record59"],
    ),
    (
        ("mirror59 filter59 ranking59 encoding59 mapping59 record59", 10),
        ["mirror59", "filter59", "ranking59", "encoding59", "mapping59", "record59"],
    ),
    (
        ("mirror59 filter59 ranking59 encoding59 mapping59 record59", 18),
        ["mirror59 filter59", "ranking59", "encoding59", "mapping59 record59"],
    ),
    (
        ("mirror59 filter59 ranking59 encoding59 mapping59 record59", 28),
        ["mirror59 filter59 ranking59", "encoding59 mapping59", "record59"],
    ),
    (
        ("filter59 ranking59 encoding59 mapping59 record59 candle59", 6),
        ["filter59", "ranking59", "encoding59", "mapping59", "record59", "candle59"],
    ),
    (
        ("filter59 ranking59 encoding59 mapping59 record59 candle59", 10),
        ["filter59", "ranking59", "encoding59", "mapping59", "record59", "candle59"],
    ),
    (
        ("filter59 ranking59 encoding59 mapping59 record59 candle59", 18),
        ["filter59 ranking59", "encoding59", "mapping59 record59", "candle59"],
    ),
    (
        ("filter59 ranking59 encoding59 mapping59 record59 candle59", 28),
        ["filter59 ranking59", "encoding59 mapping59", "record59 candle59"],
    ),
    (
        ("ranking59 encoding59 mapping59 record59 candle59 thread59", 6),
        ["ranking59", "encoding59", "mapping59", "record59", "candle59", "thread59"],
    ),
    (
        ("ranking59 encoding59 mapping59 record59 candle59 thread59", 10),
        ["ranking59", "encoding59", "mapping59", "record59", "candle59", "thread59"],
    ),
    (
        ("ranking59 encoding59 mapping59 record59 candle59 thread59", 18),
        ["ranking59", "encoding59", "mapping59 record59", "candle59 thread59"],
    ),
    (
        ("ranking59 encoding59 mapping59 record59 candle59 thread59", 28),
        ["ranking59 encoding59", "mapping59 record59 candle59", "thread59"],
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
