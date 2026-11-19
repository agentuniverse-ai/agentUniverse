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
        ("round 49: the quick brown fox jumps over the lazy dog", 4),
        ["round", "49:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 49: the quick brown fox jumps over the lazy dog", 8),
        ["round", "49: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 49: the quick brown fox jumps over the lazy dog", 12),
        ["round 49:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 49: the quick brown fox jumps over the lazy dog", 16),
        ["round 49: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 49: the quick brown fox jumps over the lazy dog", 24),
        ["round 49: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 49: the quick brown fox jumps over the lazy dog", 32),
        ["round 49: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 49: agentuniverse is a framework for multi agents", 4),
        ["round", "49:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 49: agentuniverse is a framework for multi agents", 8),
        ["round", "49:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 49: agentuniverse is a framework for multi agents", 12),
        ["round 49:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 49: agentuniverse is a framework for multi agents", 16),
        ["round 49:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 49: agentuniverse is a framework for multi agents", 24),
        ["round 49: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 49: agentuniverse is a framework for multi agents", 32),
        ["round 49: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 49: knowledge stored as vectors enables retrieval", 4),
        ["round", "49:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 49: knowledge stored as vectors enables retrieval", 8),
        ["round", "49:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 49: knowledge stored as vectors enables retrieval", 12),
        ["round 49:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 49: knowledge stored as vectors enables retrieval", 16),
        ["round 49:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 49: knowledge stored as vectors enables retrieval", 24),
        ["round 49: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 49: knowledge stored as vectors enables retrieval", 32),
        ["round 49: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 49: the processor reads the record then stops", 4),
        ["round", "49:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 49: the processor reads the record then stops", 8),
        ["round", "49: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 49: the processor reads the record then stops", 12),
        ["round 49:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 49: the processor reads the record then stops", 16),
        ["round 49: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 49: the processor reads the record then stops", 24),
        ["round 49: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 49: the processor reads the record then stops", 32),
        ["round 49: the processor reads", "the record then stops"],
    ),
    (
        ("round 49: a worker pulls the next task from the queue", 4),
        ["round", "49:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 49: a worker pulls the next task from the queue", 8),
        ["round", "49: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 49: a worker pulls the next task from the queue", 12),
        ["round 49: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 49: a worker pulls the next task from the queue", 16),
        ["round 49: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 49: a worker pulls the next task from the queue", 24),
        ["round 49: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 49: a worker pulls the next task from the queue", 32),
        ["round 49: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 49: signals travel through the network layer", 4),
        ["round", "49:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 49: signals travel through the network layer", 8),
        ["round", "49:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 49: signals travel through the network layer", 12),
        ["round 49:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 49: signals travel through the network layer", 16),
        ["round 49:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 49: signals travel through the network layer", 24),
        ["round 49: signals travel", "through the network", "layer"],
    ),
    (
        ("round 49: signals travel through the network layer", 32),
        ["round 49: signals travel through", "the network layer"],
    ),
    (
        ("round 49: the gateway routes each request by policy", 4),
        ["round", "49:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 49: the gateway routes each request by policy", 8),
        ["round", "49: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 49: the gateway routes each request by policy", 12),
        ["round 49:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 49: the gateway routes each request by policy", 16),
        ["round 49: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 49: the gateway routes each request by policy", 24),
        ["round 49: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 49: the gateway routes each request by policy", 32),
        ["round 49: the gateway routes", "each request by policy"],
    ),
    (
        ("round 49: memory grows until the buffer is full", 4),
        ["round", "49:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 49: memory grows until the buffer is full", 8),
        ["round", "49:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 49: memory grows until the buffer is full", 12),
        ["round 49:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 49: memory grows until the buffer is full", 16),
        ["round 49: memory", "grows until the", "buffer is full"],
    ),
    (("round 49: memory grows until the buffer is full", 24), ["round 49: memory grows", "until the buffer is full"]),
    (("round 49: memory grows until the buffer is full", 32), ["round 49: memory grows until the", "buffer is full"]),
    (
        ("round 49: the cluster mirrors every packet twice", 4),
        ["round", "49:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 49: the cluster mirrors every packet twice", 8),
        ["round", "49: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 49: the cluster mirrors every packet twice", 12),
        ["round 49:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 49: the cluster mirrors every packet twice", 16),
        ["round 49: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 49: the cluster mirrors every packet twice", 24),
        ["round 49: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 49: the cluster mirrors every packet twice", 32), ["round 49: the cluster mirrors", "every packet twice"]),
    (
        ("round 49: ranking uses tokens learned from the corpus", 4),
        ["round", "49:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 49: ranking uses tokens learned from the corpus", 8),
        ["round", "49:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 49: ranking uses tokens learned from the corpus", 12),
        ["round 49:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 49: ranking uses tokens learned from the corpus", 16),
        ["round 49:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 49: ranking uses tokens learned from the corpus", 24),
        ["round 49: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 49: ranking uses tokens learned from the corpus", 32),
        ["round 49: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 49: a long session ends when the candle dies", 4),
        ["round", "49:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 49: a long session ends when the candle dies", 8),
        ["round", "49: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 49: a long session ends when the candle dies", 12),
        ["round 49: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 49: a long session ends when the candle dies", 16),
        ["round 49: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 49: a long session ends when the candle dies", 24),
        ["round 49: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 49: a long session ends when the candle dies", 32),
        ["round 49: a long session ends", "when the candle dies"],
    ),
    (
        ("round 49: encode the prompt then map the result", 4),
        ["round", "49:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 49: encode the prompt then map the result", 8),
        ["round", "49:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 49: encode the prompt then map the result", 12),
        ["round 49:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 49: encode the prompt then map the result", 16),
        ["round 49: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 49: encode the prompt then map the result", 24),
        ["round 49: encode the", "prompt then map the", "result"],
    ),
    (("round 49: encode the prompt then map the result", 32), ["round 49: encode the prompt then", "map the result"]),
    (
        ("round 49: the kernel wakes the worker at dawn", 4),
        ["round", "49:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 49: the kernel wakes the worker at dawn", 8),
        ["round", "49: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 49: the kernel wakes the worker at dawn", 12),
        ["round 49:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 49: the kernel wakes the worker at dawn", 16), ["round 49: the", "kernel wakes the", "worker at dawn"]),
    (("round 49: the kernel wakes the worker at dawn", 24), ["round 49: the kernel", "wakes the worker at dawn"]),
    (("round 49: the kernel wakes the worker at dawn", 32), ["round 49: the kernel wakes the", "worker at dawn"]),
    (
        ("round 49: service latency drops after the patch", 4),
        ["round", "49:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 49: service latency drops after the patch", 8),
        ["round", "49:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 49: service latency drops after the patch", 12),
        ["round 49:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 49: service latency drops after the patch", 16),
        ["round 49:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 49: service latency drops after the patch", 24),
        ["round 49: service", "latency drops after the", "patch"],
    ),
    (("round 49: service latency drops after the patch", 32), ["round 49: service latency drops", "after the patch"]),
    (
        ("round 49: the library caches every vector it sees", 4),
        ["round", "49:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 49: the library caches every vector it sees", 8),
        ["round", "49: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 49: the library caches every vector it sees", 12),
        ["round 49:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 49: the library caches every vector it sees", 16),
        ["round 49: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 49: the library caches every vector it sees", 24),
        ["round 49: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 49: the library caches every vector it sees", 32),
        ["round 49: the library caches", "every vector it sees"],
    ),
    (
        ("round 49: agents argue then the debate resolves", 4),
        ["round", "49:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 49: agents argue then the debate resolves", 8),
        ["round", "49:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 49: agents argue then the debate resolves", 12),
        ["round 49:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 49: agents argue then the debate resolves", 16),
        ["round 49: agents", "argue then the", "debate resolves"],
    ),
    (("round 49: agents argue then the debate resolves", 24), ["round 49: agents argue", "then the debate resolves"]),
    (("round 49: agents argue then the debate resolves", 32), ["round 49: agents argue then the", "debate resolves"]),
    (
        ("round 49: the filter keeps only strong matches", 4),
        ["round", "49:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 49: the filter keeps only strong matches", 8),
        ["round", "49: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 49: the filter keeps only strong matches", 12),
        ["round 49:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 49: the filter keeps only strong matches", 16),
        ["round 49: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 49: the filter keeps only strong matches", 24), ["round 49: the filter", "keeps only strong", "matches"]),
    (("round 49: the filter keeps only strong matches", 32), ["round 49: the filter keeps only", "strong matches"]),
    (
        ("round 49: the model answers with a short reply", 4),
        ["round", "49:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 49: the model answers with a short reply", 8),
        ["round", "49: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 49: the model answers with a short reply", 12),
        ["round 49:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 49: the model answers with a short reply", 16),
        ["round 49: the", "model answers", "with a short", "reply"],
    ),
    (("round 49: the model answers with a short reply", 24), ["round 49: the model", "answers with a short", "reply"]),
    (("round 49: the model answers with a short reply", 32), ["round 49: the model answers with", "a short reply"]),
    (
        ("round 49: the recorder stores the reasoning trace", 4),
        ["round", "49:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 49: the recorder stores the reasoning trace", 8),
        ["round", "49: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 49: the recorder stores the reasoning trace", 12),
        ["round 49:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 49: the recorder stores the reasoning trace", 16),
        ["round 49: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 49: the recorder stores the reasoning trace", 24),
        ["round 49: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 49: the recorder stores the reasoning trace", 32),
        ["round 49: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 49: the angel watches the processor run", 4),
        ["round", "49:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 49: the angel watches the processor run", 8),
        ["round", "49: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 49: the angel watches the processor run", 12),
        ["round 49:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 49: the angel watches the processor run", 16), ["round 49: the", "angel watches", "the processor", "run"]),
    (("round 49: the angel watches the processor run", 24), ["round 49: the angel", "watches the processor", "run"]),
    (("round 49: the angel watches the processor run", 32), ["round 49: the angel watches the", "processor run"]),
    (
        ("round 49: angle of the vector decides the match", 4),
        ["round", "49:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 49: angle of the vector decides the match", 8),
        ["round", "49:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 49: angle of the vector decides the match", 12),
        ["round 49:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 49: angle of the vector decides the match", 16),
        ["round 49: angle", "of the vector", "decides the", "match"],
    ),
    (("round 49: angle of the vector decides the match", 24), ["round 49: angle of the", "vector decides the match"]),
    (("round 49: angle of the vector decides the match", 32), ["round 49: angle of the vector", "decides the match"]),
    (
        ("round 49: the candle burns twice as long at night", 4),
        ["round", "49:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 49: the candle burns twice as long at night", 8),
        ["round", "49: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 49: the candle burns twice as long at night", 12),
        ["round 49:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 49: the candle burns twice as long at night", 16),
        ["round 49: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 49: the candle burns twice as long at night", 24),
        ["round 49: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 49: the candle burns twice as long at night", 32),
        ["round 49: the candle burns twice", "as long at night"],
    ),
    (
        ("round 49: a mirror of the universe in one line", 4),
        ["round", "49:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 49: a mirror of the universe in one line", 8),
        ["round", "49: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 49: a mirror of the universe in one line", 12),
        ["round 49: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 49: a mirror of the universe in one line", 16),
        ["round 49: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 49: a mirror of the universe in one line", 24), ["round 49: a mirror of", "the universe in one line"]),
    (("round 49: a mirror of the universe in one line", 32), ["round 49: a mirror of the", "universe in one line"]),
    (
        ("round 49: the queue drains before the storm", 4),
        ["round", "49:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 49: the queue drains before the storm", 8),
        ["round", "49: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 49: the queue drains before the storm", 12), ["round 49:", "the queue", "drains", "before the", "storm"]),
    (("round 49: the queue drains before the storm", 16), ["round 49: the", "queue drains", "before the storm"]),
    (("round 49: the queue drains before the storm", 24), ["round 49: the queue", "drains before the storm"]),
    (("round 49: the queue drains before the storm", 32), ["round 49: the queue drains", "before the storm"]),
    (
        ("kitten49 sitting49 agent49 angle49 universe49 memory49", 6),
        ["kitten49", "sitting49", "agent49", "angle49", "universe49", "memory49"],
    ),
    (
        ("kitten49 sitting49 agent49 angle49 universe49 memory49", 10),
        ["kitten49", "sitting49", "agent49", "angle49", "universe49", "memory49"],
    ),
    (
        ("kitten49 sitting49 agent49 angle49 universe49 memory49", 18),
        ["kitten49 sitting49", "agent49 angle49", "universe49", "memory49"],
    ),
    (
        ("kitten49 sitting49 agent49 angle49 universe49 memory49", 28),
        ["kitten49 sitting49 agent49", "angle49 universe49 memory49"],
    ),
    (
        ("sitting49 agent49 angle49 universe49 memory49 stream49", 6),
        ["sitting49", "agent49", "angle49", "universe49", "memory49", "stream49"],
    ),
    (
        ("sitting49 agent49 angle49 universe49 memory49 stream49", 10),
        ["sitting49", "agent49", "angle49", "universe49", "memory49", "stream49"],
    ),
    (
        ("sitting49 agent49 angle49 universe49 memory49 stream49", 18),
        ["sitting49 agent49", "angle49 universe49", "memory49 stream49"],
    ),
    (
        ("sitting49 agent49 angle49 universe49 memory49 stream49", 28),
        ["sitting49 agent49 angle49", "universe49 memory49 stream49"],
    ),
    (
        ("agent49 angle49 universe49 memory49 stream49 context49", 6),
        ["agent49", "angle49", "universe49", "memory49", "stream49", "context49"],
    ),
    (
        ("agent49 angle49 universe49 memory49 stream49 context49", 10),
        ["agent49", "angle49", "universe49", "memory49", "stream49", "context49"],
    ),
    (
        ("agent49 angle49 universe49 memory49 stream49 context49", 18),
        ["agent49 angle49", "universe49", "memory49 stream49", "context49"],
    ),
    (
        ("agent49 angle49 universe49 memory49 stream49 context49", 28),
        ["agent49 angle49 universe49", "memory49 stream49 context49"],
    ),
    (
        ("angle49 universe49 memory49 stream49 context49 knowledge49", 6),
        ["angle49", "universe49", "memory49", "stream49", "context49", "knowledge49"],
    ),
    (
        ("angle49 universe49 memory49 stream49 context49 knowledge49", 10),
        ["angle49", "universe49", "memory49", "stream49", "context49", "knowledge49"],
    ),
    (
        ("angle49 universe49 memory49 stream49 context49 knowledge49", 18),
        ["angle49 universe49", "memory49 stream49", "context49", "knowledge49"],
    ),
    (
        ("angle49 universe49 memory49 stream49 context49 knowledge49", 28),
        ["angle49 universe49 memory49", "stream49 context49", "knowledge49"],
    ),
    (
        ("universe49 memory49 stream49 context49 knowledge49 vector49", 6),
        ["universe49", "memory49", "stream49", "context49", "knowledge49", "vector49"],
    ),
    (
        ("universe49 memory49 stream49 context49 knowledge49 vector49", 10),
        ["universe49", "memory49", "stream49", "context49", "knowledge49", "vector49"],
    ),
    (
        ("universe49 memory49 stream49 context49 knowledge49 vector49", 18),
        ["universe49", "memory49 stream49", "context49", "knowledge49", "vector49"],
    ),
    (
        ("universe49 memory49 stream49 context49 knowledge49 vector49", 28),
        ["universe49 memory49 stream49", "context49 knowledge49", "vector49"],
    ),
    (
        ("memory49 stream49 context49 knowledge49 vector49 processor49", 6),
        ["memory49", "stream49", "context49", "knowledge49", "vector49", "processor49"],
    ),
    (
        ("memory49 stream49 context49 knowledge49 vector49 processor49", 10),
        ["memory49", "stream49", "context49", "knowledge49", "vector49", "processor49"],
    ),
    (
        ("memory49 stream49 context49 knowledge49 vector49 processor49", 18),
        ["memory49 stream49", "context49", "knowledge49", "vector49", "processor49"],
    ),
    (
        ("memory49 stream49 context49 knowledge49 vector49 processor49", 28),
        ["memory49 stream49 context49", "knowledge49 vector49", "processor49"],
    ),
    (
        ("stream49 context49 knowledge49 vector49 processor49 reasoning49", 6),
        ["stream49", "context49", "knowledge49", "vector49", "processor49", "reasoning49"],
    ),
    (
        ("stream49 context49 knowledge49 vector49 processor49 reasoning49", 10),
        ["stream49", "context49", "knowledge49", "vector49", "processor49", "reasoning49"],
    ),
    (
        ("stream49 context49 knowledge49 vector49 processor49 reasoning49", 18),
        ["stream49 context49", "knowledge49", "vector49", "processor49", "reasoning49"],
    ),
    (
        ("stream49 context49 knowledge49 vector49 processor49 reasoning49", 28),
        ["stream49 context49", "knowledge49 vector49", "processor49 reasoning49"],
    ),
    (
        ("context49 knowledge49 vector49 processor49 reasoning49 machine49", 6),
        ["context49", "knowledge49", "vector49", "processor49", "reasoning49", "machine49"],
    ),
    (
        ("context49 knowledge49 vector49 processor49 reasoning49 machine49", 10),
        ["context49", "knowledge49", "vector49", "processor49", "reasoning49", "machine49"],
    ),
    (
        ("context49 knowledge49 vector49 processor49 reasoning49 machine49", 18),
        ["context49", "knowledge49", "vector49", "processor49", "reasoning49", "machine49"],
    ),
    (
        ("context49 knowledge49 vector49 processor49 reasoning49 machine49", 28),
        ["context49 knowledge49", "vector49 processor49", "reasoning49 machine49"],
    ),
    (
        ("knowledge49 vector49 processor49 reasoning49 machine49 learning49", 6),
        ["knowledge49", "vector49", "processor49", "reasoning49", "machine49", "learning49"],
    ),
    (
        ("knowledge49 vector49 processor49 reasoning49 machine49 learning49", 10),
        ["knowledge49", "vector49", "processor49", "reasoning49", "machine49", "learning49"],
    ),
    (
        ("knowledge49 vector49 processor49 reasoning49 machine49 learning49", 18),
        ["knowledge49", "vector49", "processor49", "reasoning49", "machine49", "learning49"],
    ),
    (
        ("knowledge49 vector49 processor49 reasoning49 machine49 learning49", 28),
        ["knowledge49 vector49", "processor49 reasoning49", "machine49 learning49"],
    ),
    (
        ("vector49 processor49 reasoning49 machine49 learning49 model49", 6),
        ["vector49", "processor49", "reasoning49", "machine49", "learning49", "model49"],
    ),
    (
        ("vector49 processor49 reasoning49 machine49 learning49 model49", 10),
        ["vector49", "processor49", "reasoning49", "machine49", "learning49", "model49"],
    ),
    (
        ("vector49 processor49 reasoning49 machine49 learning49 model49", 18),
        ["vector49", "processor49", "reasoning49", "machine49", "learning49 model49"],
    ),
    (
        ("vector49 processor49 reasoning49 machine49 learning49 model49", 28),
        ["vector49 processor49", "reasoning49 machine49", "learning49 model49"],
    ),
    (
        ("processor49 reasoning49 machine49 learning49 model49 token49", 6),
        ["processor49", "reasoning49", "machine49", "learning49", "model49", "token49"],
    ),
    (
        ("processor49 reasoning49 machine49 learning49 model49 token49", 10),
        ["processor49", "reasoning49", "machine49", "learning49", "model49", "token49"],
    ),
    (
        ("processor49 reasoning49 machine49 learning49 model49 token49", 18),
        ["processor49", "reasoning49", "machine49", "learning49 model49", "token49"],
    ),
    (
        ("processor49 reasoning49 machine49 learning49 model49 token49", 28),
        ["processor49 reasoning49", "machine49 learning49 model49", "token49"],
    ),
    (
        ("reasoning49 machine49 learning49 model49 token49 prompt49", 6),
        ["reasoning49", "machine49", "learning49", "model49", "token49", "prompt49"],
    ),
    (
        ("reasoning49 machine49 learning49 model49 token49 prompt49", 10),
        ["reasoning49", "machine49", "learning49", "model49", "token49", "prompt49"],
    ),
    (
        ("reasoning49 machine49 learning49 model49 token49 prompt49", 18),
        ["reasoning49", "machine49", "learning49 model49", "token49 prompt49"],
    ),
    (
        ("reasoning49 machine49 learning49 model49 token49 prompt49", 28),
        ["reasoning49 machine49", "learning49 model49 token49", "prompt49"],
    ),
    (
        ("machine49 learning49 model49 token49 prompt49 session49", 6),
        ["machine49", "learning49", "model49", "token49", "prompt49", "session49"],
    ),
    (
        ("machine49 learning49 model49 token49 prompt49 session49", 10),
        ["machine49", "learning49", "model49", "token49", "prompt49", "session49"],
    ),
    (
        ("machine49 learning49 model49 token49 prompt49 session49", 18),
        ["machine49", "learning49 model49", "token49 prompt49", "session49"],
    ),
    (
        ("machine49 learning49 model49 token49 prompt49 session49", 28),
        ["machine49 learning49 model49", "token49 prompt49 session49"],
    ),
    (
        ("learning49 model49 token49 prompt49 session49 library49", 6),
        ["learning49", "model49", "token49", "prompt49", "session49", "library49"],
    ),
    (
        ("learning49 model49 token49 prompt49 session49 library49", 10),
        ["learning49", "model49", "token49", "prompt49", "session49", "library49"],
    ),
    (
        ("learning49 model49 token49 prompt49 session49 library49", 18),
        ["learning49 model49", "token49 prompt49", "session49", "library49"],
    ),
    (
        ("learning49 model49 token49 prompt49 session49 library49", 28),
        ["learning49 model49 token49", "prompt49 session49 library49"],
    ),
    (
        ("model49 token49 prompt49 session49 library49 service49", 6),
        ["model49", "token49", "prompt49", "session49", "library49", "service49"],
    ),
    (
        ("model49 token49 prompt49 session49 library49 service49", 10),
        ["model49", "token49", "prompt49", "session49", "library49", "service49"],
    ),
    (
        ("model49 token49 prompt49 session49 library49 service49", 18),
        ["model49 token49", "prompt49 session49", "library49", "service49"],
    ),
    (
        ("model49 token49 prompt49 session49 library49 service49", 28),
        ["model49 token49 prompt49", "session49 library49", "service49"],
    ),
    (
        ("token49 prompt49 session49 library49 service49 gateway49", 6),
        ["token49", "prompt49", "session49", "library49", "service49", "gateway49"],
    ),
    (
        ("token49 prompt49 session49 library49 service49 gateway49", 10),
        ["token49", "prompt49", "session49", "library49", "service49", "gateway49"],
    ),
    (
        ("token49 prompt49 session49 library49 service49 gateway49", 18),
        ["token49 prompt49", "session49", "library49", "service49", "gateway49"],
    ),
    (
        ("token49 prompt49 session49 library49 service49 gateway49", 28),
        ["token49 prompt49 session49", "library49 service49", "gateway49"],
    ),
    (
        ("prompt49 session49 library49 service49 gateway49 storage49", 6),
        ["prompt49", "session49", "library49", "service49", "gateway49", "storage49"],
    ),
    (
        ("prompt49 session49 library49 service49 gateway49 storage49", 10),
        ["prompt49", "session49", "library49", "service49", "gateway49", "storage49"],
    ),
    (
        ("prompt49 session49 library49 service49 gateway49 storage49", 18),
        ["prompt49 session49", "library49", "service49", "gateway49", "storage49"],
    ),
    (
        ("prompt49 session49 library49 service49 gateway49 storage49", 28),
        ["prompt49 session49 library49", "service49 gateway49", "storage49"],
    ),
    (
        ("session49 library49 service49 gateway49 storage49 network49", 6),
        ["session49", "library49", "service49", "gateway49", "storage49", "network49"],
    ),
    (
        ("session49 library49 service49 gateway49 storage49 network49", 10),
        ["session49", "library49", "service49", "gateway49", "storage49", "network49"],
    ),
    (
        ("session49 library49 service49 gateway49 storage49 network49", 18),
        ["session49", "library49", "service49", "gateway49", "storage49", "network49"],
    ),
    (
        ("session49 library49 service49 gateway49 storage49 network49", 28),
        ["session49 library49", "service49 gateway49", "storage49 network49"],
    ),
    (
        ("library49 service49 gateway49 storage49 network49 latency49", 6),
        ["library49", "service49", "gateway49", "storage49", "network49", "latency49"],
    ),
    (
        ("library49 service49 gateway49 storage49 network49 latency49", 10),
        ["library49", "service49", "gateway49", "storage49", "network49", "latency49"],
    ),
    (
        ("library49 service49 gateway49 storage49 network49 latency49", 18),
        ["library49", "service49", "gateway49", "storage49", "network49", "latency49"],
    ),
    (
        ("library49 service49 gateway49 storage49 network49 latency49", 28),
        ["library49 service49", "gateway49 storage49", "network49 latency49"],
    ),
    (
        ("service49 gateway49 storage49 network49 latency49 buffer49", 6),
        ["service49", "gateway49", "storage49", "network49", "latency49", "buffer49"],
    ),
    (
        ("service49 gateway49 storage49 network49 latency49 buffer49", 10),
        ["service49", "gateway49", "storage49", "network49", "latency49", "buffer49"],
    ),
    (
        ("service49 gateway49 storage49 network49 latency49 buffer49", 18),
        ["service49", "gateway49", "storage49", "network49", "latency49 buffer49"],
    ),
    (
        ("service49 gateway49 storage49 network49 latency49 buffer49", 28),
        ["service49 gateway49", "storage49 network49", "latency49 buffer49"],
    ),
    (
        ("gateway49 storage49 network49 latency49 buffer49 queue49", 6),
        ["gateway49", "storage49", "network49", "latency49", "buffer49", "queue49"],
    ),
    (
        ("gateway49 storage49 network49 latency49 buffer49 queue49", 10),
        ["gateway49", "storage49", "network49", "latency49", "buffer49", "queue49"],
    ),
    (
        ("gateway49 storage49 network49 latency49 buffer49 queue49", 18),
        ["gateway49", "storage49", "network49", "latency49 buffer49", "queue49"],
    ),
    (
        ("gateway49 storage49 network49 latency49 buffer49 queue49", 28),
        ["gateway49 storage49", "network49 latency49 buffer49", "queue49"],
    ),
    (
        ("storage49 network49 latency49 buffer49 queue49 worker49", 6),
        ["storage49", "network49", "latency49", "buffer49", "queue49", "worker49"],
    ),
    (
        ("storage49 network49 latency49 buffer49 queue49 worker49", 10),
        ["storage49", "network49", "latency49", "buffer49", "queue49", "worker49"],
    ),
    (
        ("storage49 network49 latency49 buffer49 queue49 worker49", 18),
        ["storage49", "network49", "latency49 buffer49", "queue49 worker49"],
    ),
    (
        ("storage49 network49 latency49 buffer49 queue49 worker49", 28),
        ["storage49 network49", "latency49 buffer49 queue49", "worker49"],
    ),
    (
        ("network49 latency49 buffer49 queue49 worker49 kernel49", 6),
        ["network49", "latency49", "buffer49", "queue49", "worker49", "kernel49"],
    ),
    (
        ("network49 latency49 buffer49 queue49 worker49 kernel49", 10),
        ["network49", "latency49", "buffer49", "queue49", "worker49", "kernel49"],
    ),
    (
        ("network49 latency49 buffer49 queue49 worker49 kernel49", 18),
        ["network49", "latency49 buffer49", "queue49 worker49", "kernel49"],
    ),
    (
        ("network49 latency49 buffer49 queue49 worker49 kernel49", 28),
        ["network49 latency49 buffer49", "queue49 worker49 kernel49"],
    ),
    (
        ("latency49 buffer49 queue49 worker49 kernel49 signal49", 6),
        ["latency49", "buffer49", "queue49", "worker49", "kernel49", "signal49"],
    ),
    (
        ("latency49 buffer49 queue49 worker49 kernel49 signal49", 10),
        ["latency49", "buffer49", "queue49", "worker49", "kernel49", "signal49"],
    ),
    (
        ("latency49 buffer49 queue49 worker49 kernel49 signal49", 18),
        ["latency49 buffer49", "queue49 worker49", "kernel49 signal49"],
    ),
    (
        ("latency49 buffer49 queue49 worker49 kernel49 signal49", 28),
        ["latency49 buffer49 queue49", "worker49 kernel49 signal49"],
    ),
    (
        ("buffer49 queue49 worker49 kernel49 signal49 packet49", 6),
        ["buffer49", "queue49", "worker49", "kernel49", "signal49", "packet49"],
    ),
    (
        ("buffer49 queue49 worker49 kernel49 signal49 packet49", 10),
        ["buffer49", "queue49", "worker49", "kernel49", "signal49", "packet49"],
    ),
    (
        ("buffer49 queue49 worker49 kernel49 signal49 packet49", 18),
        ["buffer49 queue49", "worker49 kernel49", "signal49 packet49"],
    ),
    (
        ("buffer49 queue49 worker49 kernel49 signal49 packet49", 28),
        ["buffer49 queue49 worker49", "kernel49 signal49 packet49"],
    ),
    (
        ("queue49 worker49 kernel49 signal49 packet49 router49", 6),
        ["queue49", "worker49", "kernel49", "signal49", "packet49", "router49"],
    ),
    (
        ("queue49 worker49 kernel49 signal49 packet49 router49", 10),
        ["queue49", "worker49", "kernel49", "signal49", "packet49", "router49"],
    ),
    (
        ("queue49 worker49 kernel49 signal49 packet49 router49", 18),
        ["queue49 worker49", "kernel49 signal49", "packet49 router49"],
    ),
    (
        ("queue49 worker49 kernel49 signal49 packet49 router49", 28),
        ["queue49 worker49 kernel49", "signal49 packet49 router49"],
    ),
    (
        ("worker49 kernel49 signal49 packet49 router49 cluster49", 6),
        ["worker49", "kernel49", "signal49", "packet49", "router49", "cluster49"],
    ),
    (
        ("worker49 kernel49 signal49 packet49 router49 cluster49", 10),
        ["worker49", "kernel49", "signal49", "packet49", "router49", "cluster49"],
    ),
    (
        ("worker49 kernel49 signal49 packet49 router49 cluster49", 18),
        ["worker49 kernel49", "signal49 packet49", "router49 cluster49"],
    ),
    (
        ("worker49 kernel49 signal49 packet49 router49 cluster49", 28),
        ["worker49 kernel49 signal49", "packet49 router49 cluster49"],
    ),
    (
        ("kernel49 signal49 packet49 router49 cluster49 mirror49", 6),
        ["kernel49", "signal49", "packet49", "router49", "cluster49", "mirror49"],
    ),
    (
        ("kernel49 signal49 packet49 router49 cluster49 mirror49", 10),
        ["kernel49", "signal49", "packet49", "router49", "cluster49", "mirror49"],
    ),
    (
        ("kernel49 signal49 packet49 router49 cluster49 mirror49", 18),
        ["kernel49 signal49", "packet49 router49", "cluster49 mirror49"],
    ),
    (
        ("kernel49 signal49 packet49 router49 cluster49 mirror49", 28),
        ["kernel49 signal49 packet49", "router49 cluster49 mirror49"],
    ),
    (
        ("signal49 packet49 router49 cluster49 mirror49 filter49", 6),
        ["signal49", "packet49", "router49", "cluster49", "mirror49", "filter49"],
    ),
    (
        ("signal49 packet49 router49 cluster49 mirror49 filter49", 10),
        ["signal49", "packet49", "router49", "cluster49", "mirror49", "filter49"],
    ),
    (
        ("signal49 packet49 router49 cluster49 mirror49 filter49", 18),
        ["signal49 packet49", "router49 cluster49", "mirror49 filter49"],
    ),
    (
        ("signal49 packet49 router49 cluster49 mirror49 filter49", 28),
        ["signal49 packet49 router49", "cluster49 mirror49 filter49"],
    ),
    (
        ("packet49 router49 cluster49 mirror49 filter49 ranking49", 6),
        ["packet49", "router49", "cluster49", "mirror49", "filter49", "ranking49"],
    ),
    (
        ("packet49 router49 cluster49 mirror49 filter49 ranking49", 10),
        ["packet49", "router49", "cluster49", "mirror49", "filter49", "ranking49"],
    ),
    (
        ("packet49 router49 cluster49 mirror49 filter49 ranking49", 18),
        ["packet49 router49", "cluster49 mirror49", "filter49 ranking49"],
    ),
    (
        ("packet49 router49 cluster49 mirror49 filter49 ranking49", 28),
        ["packet49 router49 cluster49", "mirror49 filter49 ranking49"],
    ),
    (
        ("router49 cluster49 mirror49 filter49 ranking49 encoding49", 6),
        ["router49", "cluster49", "mirror49", "filter49", "ranking49", "encoding49"],
    ),
    (
        ("router49 cluster49 mirror49 filter49 ranking49 encoding49", 10),
        ["router49", "cluster49", "mirror49", "filter49", "ranking49", "encoding49"],
    ),
    (
        ("router49 cluster49 mirror49 filter49 ranking49 encoding49", 18),
        ["router49 cluster49", "mirror49 filter49", "ranking49", "encoding49"],
    ),
    (
        ("router49 cluster49 mirror49 filter49 ranking49 encoding49", 28),
        ["router49 cluster49 mirror49", "filter49 ranking49", "encoding49"],
    ),
    (
        ("cluster49 mirror49 filter49 ranking49 encoding49 mapping49", 6),
        ["cluster49", "mirror49", "filter49", "ranking49", "encoding49", "mapping49"],
    ),
    (
        ("cluster49 mirror49 filter49 ranking49 encoding49 mapping49", 10),
        ["cluster49", "mirror49", "filter49", "ranking49", "encoding49", "mapping49"],
    ),
    (
        ("cluster49 mirror49 filter49 ranking49 encoding49 mapping49", 18),
        ["cluster49 mirror49", "filter49 ranking49", "encoding49", "mapping49"],
    ),
    (
        ("cluster49 mirror49 filter49 ranking49 encoding49 mapping49", 28),
        ["cluster49 mirror49 filter49", "ranking49 encoding49", "mapping49"],
    ),
    (
        ("mirror49 filter49 ranking49 encoding49 mapping49 record49", 6),
        ["mirror49", "filter49", "ranking49", "encoding49", "mapping49", "record49"],
    ),
    (
        ("mirror49 filter49 ranking49 encoding49 mapping49 record49", 10),
        ["mirror49", "filter49", "ranking49", "encoding49", "mapping49", "record49"],
    ),
    (
        ("mirror49 filter49 ranking49 encoding49 mapping49 record49", 18),
        ["mirror49 filter49", "ranking49", "encoding49", "mapping49 record49"],
    ),
    (
        ("mirror49 filter49 ranking49 encoding49 mapping49 record49", 28),
        ["mirror49 filter49 ranking49", "encoding49 mapping49", "record49"],
    ),
    (
        ("filter49 ranking49 encoding49 mapping49 record49 candle49", 6),
        ["filter49", "ranking49", "encoding49", "mapping49", "record49", "candle49"],
    ),
    (
        ("filter49 ranking49 encoding49 mapping49 record49 candle49", 10),
        ["filter49", "ranking49", "encoding49", "mapping49", "record49", "candle49"],
    ),
    (
        ("filter49 ranking49 encoding49 mapping49 record49 candle49", 18),
        ["filter49 ranking49", "encoding49", "mapping49 record49", "candle49"],
    ),
    (
        ("filter49 ranking49 encoding49 mapping49 record49 candle49", 28),
        ["filter49 ranking49", "encoding49 mapping49", "record49 candle49"],
    ),
    (
        ("ranking49 encoding49 mapping49 record49 candle49 thread49", 6),
        ["ranking49", "encoding49", "mapping49", "record49", "candle49", "thread49"],
    ),
    (
        ("ranking49 encoding49 mapping49 record49 candle49 thread49", 10),
        ["ranking49", "encoding49", "mapping49", "record49", "candle49", "thread49"],
    ),
    (
        ("ranking49 encoding49 mapping49 record49 candle49 thread49", 18),
        ["ranking49", "encoding49", "mapping49 record49", "candle49 thread49"],
    ),
    (
        ("ranking49 encoding49 mapping49 record49 candle49 thread49", 28),
        ["ranking49 encoding49", "mapping49 record49 candle49", "thread49"],
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
