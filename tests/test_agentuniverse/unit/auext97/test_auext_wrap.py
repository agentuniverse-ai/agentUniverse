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
        ("round 97: the quick brown fox jumps over the lazy dog", 4),
        ["round", "97:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 97: the quick brown fox jumps over the lazy dog", 8),
        ["round", "97: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 97: the quick brown fox jumps over the lazy dog", 12),
        ["round 97:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 97: the quick brown fox jumps over the lazy dog", 16),
        ["round 97: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 97: the quick brown fox jumps over the lazy dog", 24),
        ["round 97: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 97: the quick brown fox jumps over the lazy dog", 32),
        ["round 97: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 97: agentuniverse is a framework for multi agents", 4),
        ["round", "97:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 97: agentuniverse is a framework for multi agents", 8),
        ["round", "97:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 97: agentuniverse is a framework for multi agents", 12),
        ["round 97:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 97: agentuniverse is a framework for multi agents", 16),
        ["round 97:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 97: agentuniverse is a framework for multi agents", 24),
        ["round 97: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 97: agentuniverse is a framework for multi agents", 32),
        ["round 97: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 97: knowledge stored as vectors enables retrieval", 4),
        ["round", "97:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 97: knowledge stored as vectors enables retrieval", 8),
        ["round", "97:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 97: knowledge stored as vectors enables retrieval", 12),
        ["round 97:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 97: knowledge stored as vectors enables retrieval", 16),
        ["round 97:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 97: knowledge stored as vectors enables retrieval", 24),
        ["round 97: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 97: knowledge stored as vectors enables retrieval", 32),
        ["round 97: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 97: the processor reads the record then stops", 4),
        ["round", "97:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 97: the processor reads the record then stops", 8),
        ["round", "97: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 97: the processor reads the record then stops", 12),
        ["round 97:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 97: the processor reads the record then stops", 16),
        ["round 97: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 97: the processor reads the record then stops", 24),
        ["round 97: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 97: the processor reads the record then stops", 32),
        ["round 97: the processor reads", "the record then stops"],
    ),
    (
        ("round 97: a worker pulls the next task from the queue", 4),
        ["round", "97:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 97: a worker pulls the next task from the queue", 8),
        ["round", "97: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 97: a worker pulls the next task from the queue", 12),
        ["round 97: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 97: a worker pulls the next task from the queue", 16),
        ["round 97: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 97: a worker pulls the next task from the queue", 24),
        ["round 97: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 97: a worker pulls the next task from the queue", 32),
        ["round 97: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 97: signals travel through the network layer", 4),
        ["round", "97:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 97: signals travel through the network layer", 8),
        ["round", "97:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 97: signals travel through the network layer", 12),
        ["round 97:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 97: signals travel through the network layer", 16),
        ["round 97:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 97: signals travel through the network layer", 24),
        ["round 97: signals travel", "through the network", "layer"],
    ),
    (
        ("round 97: signals travel through the network layer", 32),
        ["round 97: signals travel through", "the network layer"],
    ),
    (
        ("round 97: the gateway routes each request by policy", 4),
        ["round", "97:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 97: the gateway routes each request by policy", 8),
        ["round", "97: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 97: the gateway routes each request by policy", 12),
        ["round 97:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 97: the gateway routes each request by policy", 16),
        ["round 97: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 97: the gateway routes each request by policy", 24),
        ["round 97: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 97: the gateway routes each request by policy", 32),
        ["round 97: the gateway routes", "each request by policy"],
    ),
    (
        ("round 97: memory grows until the buffer is full", 4),
        ["round", "97:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 97: memory grows until the buffer is full", 8),
        ["round", "97:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 97: memory grows until the buffer is full", 12),
        ["round 97:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 97: memory grows until the buffer is full", 16),
        ["round 97: memory", "grows until the", "buffer is full"],
    ),
    (("round 97: memory grows until the buffer is full", 24), ["round 97: memory grows", "until the buffer is full"]),
    (("round 97: memory grows until the buffer is full", 32), ["round 97: memory grows until the", "buffer is full"]),
    (
        ("round 97: the cluster mirrors every packet twice", 4),
        ["round", "97:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 97: the cluster mirrors every packet twice", 8),
        ["round", "97: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 97: the cluster mirrors every packet twice", 12),
        ["round 97:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 97: the cluster mirrors every packet twice", 16),
        ["round 97: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 97: the cluster mirrors every packet twice", 24),
        ["round 97: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 97: the cluster mirrors every packet twice", 32), ["round 97: the cluster mirrors", "every packet twice"]),
    (
        ("round 97: ranking uses tokens learned from the corpus", 4),
        ["round", "97:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 97: ranking uses tokens learned from the corpus", 8),
        ["round", "97:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 97: ranking uses tokens learned from the corpus", 12),
        ["round 97:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 97: ranking uses tokens learned from the corpus", 16),
        ["round 97:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 97: ranking uses tokens learned from the corpus", 24),
        ["round 97: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 97: ranking uses tokens learned from the corpus", 32),
        ["round 97: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 97: a long session ends when the candle dies", 4),
        ["round", "97:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 97: a long session ends when the candle dies", 8),
        ["round", "97: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 97: a long session ends when the candle dies", 12),
        ["round 97: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 97: a long session ends when the candle dies", 16),
        ["round 97: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 97: a long session ends when the candle dies", 24),
        ["round 97: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 97: a long session ends when the candle dies", 32),
        ["round 97: a long session ends", "when the candle dies"],
    ),
    (
        ("round 97: encode the prompt then map the result", 4),
        ["round", "97:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 97: encode the prompt then map the result", 8),
        ["round", "97:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 97: encode the prompt then map the result", 12),
        ["round 97:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 97: encode the prompt then map the result", 16),
        ["round 97: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 97: encode the prompt then map the result", 24),
        ["round 97: encode the", "prompt then map the", "result"],
    ),
    (("round 97: encode the prompt then map the result", 32), ["round 97: encode the prompt then", "map the result"]),
    (
        ("round 97: the kernel wakes the worker at dawn", 4),
        ["round", "97:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 97: the kernel wakes the worker at dawn", 8),
        ["round", "97: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 97: the kernel wakes the worker at dawn", 12),
        ["round 97:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 97: the kernel wakes the worker at dawn", 16), ["round 97: the", "kernel wakes the", "worker at dawn"]),
    (("round 97: the kernel wakes the worker at dawn", 24), ["round 97: the kernel", "wakes the worker at dawn"]),
    (("round 97: the kernel wakes the worker at dawn", 32), ["round 97: the kernel wakes the", "worker at dawn"]),
    (
        ("round 97: service latency drops after the patch", 4),
        ["round", "97:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 97: service latency drops after the patch", 8),
        ["round", "97:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 97: service latency drops after the patch", 12),
        ["round 97:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 97: service latency drops after the patch", 16),
        ["round 97:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 97: service latency drops after the patch", 24),
        ["round 97: service", "latency drops after the", "patch"],
    ),
    (("round 97: service latency drops after the patch", 32), ["round 97: service latency drops", "after the patch"]),
    (
        ("round 97: the library caches every vector it sees", 4),
        ["round", "97:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 97: the library caches every vector it sees", 8),
        ["round", "97: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 97: the library caches every vector it sees", 12),
        ["round 97:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 97: the library caches every vector it sees", 16),
        ["round 97: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 97: the library caches every vector it sees", 24),
        ["round 97: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 97: the library caches every vector it sees", 32),
        ["round 97: the library caches", "every vector it sees"],
    ),
    (
        ("round 97: agents argue then the debate resolves", 4),
        ["round", "97:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 97: agents argue then the debate resolves", 8),
        ["round", "97:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 97: agents argue then the debate resolves", 12),
        ["round 97:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 97: agents argue then the debate resolves", 16),
        ["round 97: agents", "argue then the", "debate resolves"],
    ),
    (("round 97: agents argue then the debate resolves", 24), ["round 97: agents argue", "then the debate resolves"]),
    (("round 97: agents argue then the debate resolves", 32), ["round 97: agents argue then the", "debate resolves"]),
    (
        ("round 97: the filter keeps only strong matches", 4),
        ["round", "97:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 97: the filter keeps only strong matches", 8),
        ["round", "97: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 97: the filter keeps only strong matches", 12),
        ["round 97:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 97: the filter keeps only strong matches", 16),
        ["round 97: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 97: the filter keeps only strong matches", 24), ["round 97: the filter", "keeps only strong", "matches"]),
    (("round 97: the filter keeps only strong matches", 32), ["round 97: the filter keeps only", "strong matches"]),
    (
        ("round 97: the model answers with a short reply", 4),
        ["round", "97:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 97: the model answers with a short reply", 8),
        ["round", "97: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 97: the model answers with a short reply", 12),
        ["round 97:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 97: the model answers with a short reply", 16),
        ["round 97: the", "model answers", "with a short", "reply"],
    ),
    (("round 97: the model answers with a short reply", 24), ["round 97: the model", "answers with a short", "reply"]),
    (("round 97: the model answers with a short reply", 32), ["round 97: the model answers with", "a short reply"]),
    (
        ("round 97: the recorder stores the reasoning trace", 4),
        ["round", "97:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 97: the recorder stores the reasoning trace", 8),
        ["round", "97: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 97: the recorder stores the reasoning trace", 12),
        ["round 97:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 97: the recorder stores the reasoning trace", 16),
        ["round 97: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 97: the recorder stores the reasoning trace", 24),
        ["round 97: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 97: the recorder stores the reasoning trace", 32),
        ["round 97: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 97: the angel watches the processor run", 4),
        ["round", "97:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 97: the angel watches the processor run", 8),
        ["round", "97: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 97: the angel watches the processor run", 12),
        ["round 97:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 97: the angel watches the processor run", 16), ["round 97: the", "angel watches", "the processor", "run"]),
    (("round 97: the angel watches the processor run", 24), ["round 97: the angel", "watches the processor", "run"]),
    (("round 97: the angel watches the processor run", 32), ["round 97: the angel watches the", "processor run"]),
    (
        ("round 97: angle of the vector decides the match", 4),
        ["round", "97:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 97: angle of the vector decides the match", 8),
        ["round", "97:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 97: angle of the vector decides the match", 12),
        ["round 97:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 97: angle of the vector decides the match", 16),
        ["round 97: angle", "of the vector", "decides the", "match"],
    ),
    (("round 97: angle of the vector decides the match", 24), ["round 97: angle of the", "vector decides the match"]),
    (("round 97: angle of the vector decides the match", 32), ["round 97: angle of the vector", "decides the match"]),
    (
        ("round 97: the candle burns twice as long at night", 4),
        ["round", "97:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 97: the candle burns twice as long at night", 8),
        ["round", "97: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 97: the candle burns twice as long at night", 12),
        ["round 97:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 97: the candle burns twice as long at night", 16),
        ["round 97: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 97: the candle burns twice as long at night", 24),
        ["round 97: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 97: the candle burns twice as long at night", 32),
        ["round 97: the candle burns twice", "as long at night"],
    ),
    (
        ("round 97: a mirror of the universe in one line", 4),
        ["round", "97:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 97: a mirror of the universe in one line", 8),
        ["round", "97: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 97: a mirror of the universe in one line", 12),
        ["round 97: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 97: a mirror of the universe in one line", 16),
        ["round 97: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 97: a mirror of the universe in one line", 24), ["round 97: a mirror of", "the universe in one line"]),
    (("round 97: a mirror of the universe in one line", 32), ["round 97: a mirror of the", "universe in one line"]),
    (
        ("round 97: the queue drains before the storm", 4),
        ["round", "97:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 97: the queue drains before the storm", 8),
        ["round", "97: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 97: the queue drains before the storm", 12), ["round 97:", "the queue", "drains", "before the", "storm"]),
    (("round 97: the queue drains before the storm", 16), ["round 97: the", "queue drains", "before the storm"]),
    (("round 97: the queue drains before the storm", 24), ["round 97: the queue", "drains before the storm"]),
    (("round 97: the queue drains before the storm", 32), ["round 97: the queue drains", "before the storm"]),
    (
        ("kitten97 sitting97 agent97 angle97 universe97 memory97", 6),
        ["kitten97", "sitting97", "agent97", "angle97", "universe97", "memory97"],
    ),
    (
        ("kitten97 sitting97 agent97 angle97 universe97 memory97", 10),
        ["kitten97", "sitting97", "agent97", "angle97", "universe97", "memory97"],
    ),
    (
        ("kitten97 sitting97 agent97 angle97 universe97 memory97", 18),
        ["kitten97 sitting97", "agent97 angle97", "universe97", "memory97"],
    ),
    (
        ("kitten97 sitting97 agent97 angle97 universe97 memory97", 28),
        ["kitten97 sitting97 agent97", "angle97 universe97 memory97"],
    ),
    (
        ("sitting97 agent97 angle97 universe97 memory97 stream97", 6),
        ["sitting97", "agent97", "angle97", "universe97", "memory97", "stream97"],
    ),
    (
        ("sitting97 agent97 angle97 universe97 memory97 stream97", 10),
        ["sitting97", "agent97", "angle97", "universe97", "memory97", "stream97"],
    ),
    (
        ("sitting97 agent97 angle97 universe97 memory97 stream97", 18),
        ["sitting97 agent97", "angle97 universe97", "memory97 stream97"],
    ),
    (
        ("sitting97 agent97 angle97 universe97 memory97 stream97", 28),
        ["sitting97 agent97 angle97", "universe97 memory97 stream97"],
    ),
    (
        ("agent97 angle97 universe97 memory97 stream97 context97", 6),
        ["agent97", "angle97", "universe97", "memory97", "stream97", "context97"],
    ),
    (
        ("agent97 angle97 universe97 memory97 stream97 context97", 10),
        ["agent97", "angle97", "universe97", "memory97", "stream97", "context97"],
    ),
    (
        ("agent97 angle97 universe97 memory97 stream97 context97", 18),
        ["agent97 angle97", "universe97", "memory97 stream97", "context97"],
    ),
    (
        ("agent97 angle97 universe97 memory97 stream97 context97", 28),
        ["agent97 angle97 universe97", "memory97 stream97 context97"],
    ),
    (
        ("angle97 universe97 memory97 stream97 context97 knowledge97", 6),
        ["angle97", "universe97", "memory97", "stream97", "context97", "knowledge97"],
    ),
    (
        ("angle97 universe97 memory97 stream97 context97 knowledge97", 10),
        ["angle97", "universe97", "memory97", "stream97", "context97", "knowledge97"],
    ),
    (
        ("angle97 universe97 memory97 stream97 context97 knowledge97", 18),
        ["angle97 universe97", "memory97 stream97", "context97", "knowledge97"],
    ),
    (
        ("angle97 universe97 memory97 stream97 context97 knowledge97", 28),
        ["angle97 universe97 memory97", "stream97 context97", "knowledge97"],
    ),
    (
        ("universe97 memory97 stream97 context97 knowledge97 vector97", 6),
        ["universe97", "memory97", "stream97", "context97", "knowledge97", "vector97"],
    ),
    (
        ("universe97 memory97 stream97 context97 knowledge97 vector97", 10),
        ["universe97", "memory97", "stream97", "context97", "knowledge97", "vector97"],
    ),
    (
        ("universe97 memory97 stream97 context97 knowledge97 vector97", 18),
        ["universe97", "memory97 stream97", "context97", "knowledge97", "vector97"],
    ),
    (
        ("universe97 memory97 stream97 context97 knowledge97 vector97", 28),
        ["universe97 memory97 stream97", "context97 knowledge97", "vector97"],
    ),
    (
        ("memory97 stream97 context97 knowledge97 vector97 processor97", 6),
        ["memory97", "stream97", "context97", "knowledge97", "vector97", "processor97"],
    ),
    (
        ("memory97 stream97 context97 knowledge97 vector97 processor97", 10),
        ["memory97", "stream97", "context97", "knowledge97", "vector97", "processor97"],
    ),
    (
        ("memory97 stream97 context97 knowledge97 vector97 processor97", 18),
        ["memory97 stream97", "context97", "knowledge97", "vector97", "processor97"],
    ),
    (
        ("memory97 stream97 context97 knowledge97 vector97 processor97", 28),
        ["memory97 stream97 context97", "knowledge97 vector97", "processor97"],
    ),
    (
        ("stream97 context97 knowledge97 vector97 processor97 reasoning97", 6),
        ["stream97", "context97", "knowledge97", "vector97", "processor97", "reasoning97"],
    ),
    (
        ("stream97 context97 knowledge97 vector97 processor97 reasoning97", 10),
        ["stream97", "context97", "knowledge97", "vector97", "processor97", "reasoning97"],
    ),
    (
        ("stream97 context97 knowledge97 vector97 processor97 reasoning97", 18),
        ["stream97 context97", "knowledge97", "vector97", "processor97", "reasoning97"],
    ),
    (
        ("stream97 context97 knowledge97 vector97 processor97 reasoning97", 28),
        ["stream97 context97", "knowledge97 vector97", "processor97 reasoning97"],
    ),
    (
        ("context97 knowledge97 vector97 processor97 reasoning97 machine97", 6),
        ["context97", "knowledge97", "vector97", "processor97", "reasoning97", "machine97"],
    ),
    (
        ("context97 knowledge97 vector97 processor97 reasoning97 machine97", 10),
        ["context97", "knowledge97", "vector97", "processor97", "reasoning97", "machine97"],
    ),
    (
        ("context97 knowledge97 vector97 processor97 reasoning97 machine97", 18),
        ["context97", "knowledge97", "vector97", "processor97", "reasoning97", "machine97"],
    ),
    (
        ("context97 knowledge97 vector97 processor97 reasoning97 machine97", 28),
        ["context97 knowledge97", "vector97 processor97", "reasoning97 machine97"],
    ),
    (
        ("knowledge97 vector97 processor97 reasoning97 machine97 learning97", 6),
        ["knowledge97", "vector97", "processor97", "reasoning97", "machine97", "learning97"],
    ),
    (
        ("knowledge97 vector97 processor97 reasoning97 machine97 learning97", 10),
        ["knowledge97", "vector97", "processor97", "reasoning97", "machine97", "learning97"],
    ),
    (
        ("knowledge97 vector97 processor97 reasoning97 machine97 learning97", 18),
        ["knowledge97", "vector97", "processor97", "reasoning97", "machine97", "learning97"],
    ),
    (
        ("knowledge97 vector97 processor97 reasoning97 machine97 learning97", 28),
        ["knowledge97 vector97", "processor97 reasoning97", "machine97 learning97"],
    ),
    (
        ("vector97 processor97 reasoning97 machine97 learning97 model97", 6),
        ["vector97", "processor97", "reasoning97", "machine97", "learning97", "model97"],
    ),
    (
        ("vector97 processor97 reasoning97 machine97 learning97 model97", 10),
        ["vector97", "processor97", "reasoning97", "machine97", "learning97", "model97"],
    ),
    (
        ("vector97 processor97 reasoning97 machine97 learning97 model97", 18),
        ["vector97", "processor97", "reasoning97", "machine97", "learning97 model97"],
    ),
    (
        ("vector97 processor97 reasoning97 machine97 learning97 model97", 28),
        ["vector97 processor97", "reasoning97 machine97", "learning97 model97"],
    ),
    (
        ("processor97 reasoning97 machine97 learning97 model97 token97", 6),
        ["processor97", "reasoning97", "machine97", "learning97", "model97", "token97"],
    ),
    (
        ("processor97 reasoning97 machine97 learning97 model97 token97", 10),
        ["processor97", "reasoning97", "machine97", "learning97", "model97", "token97"],
    ),
    (
        ("processor97 reasoning97 machine97 learning97 model97 token97", 18),
        ["processor97", "reasoning97", "machine97", "learning97 model97", "token97"],
    ),
    (
        ("processor97 reasoning97 machine97 learning97 model97 token97", 28),
        ["processor97 reasoning97", "machine97 learning97 model97", "token97"],
    ),
    (
        ("reasoning97 machine97 learning97 model97 token97 prompt97", 6),
        ["reasoning97", "machine97", "learning97", "model97", "token97", "prompt97"],
    ),
    (
        ("reasoning97 machine97 learning97 model97 token97 prompt97", 10),
        ["reasoning97", "machine97", "learning97", "model97", "token97", "prompt97"],
    ),
    (
        ("reasoning97 machine97 learning97 model97 token97 prompt97", 18),
        ["reasoning97", "machine97", "learning97 model97", "token97 prompt97"],
    ),
    (
        ("reasoning97 machine97 learning97 model97 token97 prompt97", 28),
        ["reasoning97 machine97", "learning97 model97 token97", "prompt97"],
    ),
    (
        ("machine97 learning97 model97 token97 prompt97 session97", 6),
        ["machine97", "learning97", "model97", "token97", "prompt97", "session97"],
    ),
    (
        ("machine97 learning97 model97 token97 prompt97 session97", 10),
        ["machine97", "learning97", "model97", "token97", "prompt97", "session97"],
    ),
    (
        ("machine97 learning97 model97 token97 prompt97 session97", 18),
        ["machine97", "learning97 model97", "token97 prompt97", "session97"],
    ),
    (
        ("machine97 learning97 model97 token97 prompt97 session97", 28),
        ["machine97 learning97 model97", "token97 prompt97 session97"],
    ),
    (
        ("learning97 model97 token97 prompt97 session97 library97", 6),
        ["learning97", "model97", "token97", "prompt97", "session97", "library97"],
    ),
    (
        ("learning97 model97 token97 prompt97 session97 library97", 10),
        ["learning97", "model97", "token97", "prompt97", "session97", "library97"],
    ),
    (
        ("learning97 model97 token97 prompt97 session97 library97", 18),
        ["learning97 model97", "token97 prompt97", "session97", "library97"],
    ),
    (
        ("learning97 model97 token97 prompt97 session97 library97", 28),
        ["learning97 model97 token97", "prompt97 session97 library97"],
    ),
    (
        ("model97 token97 prompt97 session97 library97 service97", 6),
        ["model97", "token97", "prompt97", "session97", "library97", "service97"],
    ),
    (
        ("model97 token97 prompt97 session97 library97 service97", 10),
        ["model97", "token97", "prompt97", "session97", "library97", "service97"],
    ),
    (
        ("model97 token97 prompt97 session97 library97 service97", 18),
        ["model97 token97", "prompt97 session97", "library97", "service97"],
    ),
    (
        ("model97 token97 prompt97 session97 library97 service97", 28),
        ["model97 token97 prompt97", "session97 library97", "service97"],
    ),
    (
        ("token97 prompt97 session97 library97 service97 gateway97", 6),
        ["token97", "prompt97", "session97", "library97", "service97", "gateway97"],
    ),
    (
        ("token97 prompt97 session97 library97 service97 gateway97", 10),
        ["token97", "prompt97", "session97", "library97", "service97", "gateway97"],
    ),
    (
        ("token97 prompt97 session97 library97 service97 gateway97", 18),
        ["token97 prompt97", "session97", "library97", "service97", "gateway97"],
    ),
    (
        ("token97 prompt97 session97 library97 service97 gateway97", 28),
        ["token97 prompt97 session97", "library97 service97", "gateway97"],
    ),
    (
        ("prompt97 session97 library97 service97 gateway97 storage97", 6),
        ["prompt97", "session97", "library97", "service97", "gateway97", "storage97"],
    ),
    (
        ("prompt97 session97 library97 service97 gateway97 storage97", 10),
        ["prompt97", "session97", "library97", "service97", "gateway97", "storage97"],
    ),
    (
        ("prompt97 session97 library97 service97 gateway97 storage97", 18),
        ["prompt97 session97", "library97", "service97", "gateway97", "storage97"],
    ),
    (
        ("prompt97 session97 library97 service97 gateway97 storage97", 28),
        ["prompt97 session97 library97", "service97 gateway97", "storage97"],
    ),
    (
        ("session97 library97 service97 gateway97 storage97 network97", 6),
        ["session97", "library97", "service97", "gateway97", "storage97", "network97"],
    ),
    (
        ("session97 library97 service97 gateway97 storage97 network97", 10),
        ["session97", "library97", "service97", "gateway97", "storage97", "network97"],
    ),
    (
        ("session97 library97 service97 gateway97 storage97 network97", 18),
        ["session97", "library97", "service97", "gateway97", "storage97", "network97"],
    ),
    (
        ("session97 library97 service97 gateway97 storage97 network97", 28),
        ["session97 library97", "service97 gateway97", "storage97 network97"],
    ),
    (
        ("library97 service97 gateway97 storage97 network97 latency97", 6),
        ["library97", "service97", "gateway97", "storage97", "network97", "latency97"],
    ),
    (
        ("library97 service97 gateway97 storage97 network97 latency97", 10),
        ["library97", "service97", "gateway97", "storage97", "network97", "latency97"],
    ),
    (
        ("library97 service97 gateway97 storage97 network97 latency97", 18),
        ["library97", "service97", "gateway97", "storage97", "network97", "latency97"],
    ),
    (
        ("library97 service97 gateway97 storage97 network97 latency97", 28),
        ["library97 service97", "gateway97 storage97", "network97 latency97"],
    ),
    (
        ("service97 gateway97 storage97 network97 latency97 buffer97", 6),
        ["service97", "gateway97", "storage97", "network97", "latency97", "buffer97"],
    ),
    (
        ("service97 gateway97 storage97 network97 latency97 buffer97", 10),
        ["service97", "gateway97", "storage97", "network97", "latency97", "buffer97"],
    ),
    (
        ("service97 gateway97 storage97 network97 latency97 buffer97", 18),
        ["service97", "gateway97", "storage97", "network97", "latency97 buffer97"],
    ),
    (
        ("service97 gateway97 storage97 network97 latency97 buffer97", 28),
        ["service97 gateway97", "storage97 network97", "latency97 buffer97"],
    ),
    (
        ("gateway97 storage97 network97 latency97 buffer97 queue97", 6),
        ["gateway97", "storage97", "network97", "latency97", "buffer97", "queue97"],
    ),
    (
        ("gateway97 storage97 network97 latency97 buffer97 queue97", 10),
        ["gateway97", "storage97", "network97", "latency97", "buffer97", "queue97"],
    ),
    (
        ("gateway97 storage97 network97 latency97 buffer97 queue97", 18),
        ["gateway97", "storage97", "network97", "latency97 buffer97", "queue97"],
    ),
    (
        ("gateway97 storage97 network97 latency97 buffer97 queue97", 28),
        ["gateway97 storage97", "network97 latency97 buffer97", "queue97"],
    ),
    (
        ("storage97 network97 latency97 buffer97 queue97 worker97", 6),
        ["storage97", "network97", "latency97", "buffer97", "queue97", "worker97"],
    ),
    (
        ("storage97 network97 latency97 buffer97 queue97 worker97", 10),
        ["storage97", "network97", "latency97", "buffer97", "queue97", "worker97"],
    ),
    (
        ("storage97 network97 latency97 buffer97 queue97 worker97", 18),
        ["storage97", "network97", "latency97 buffer97", "queue97 worker97"],
    ),
    (
        ("storage97 network97 latency97 buffer97 queue97 worker97", 28),
        ["storage97 network97", "latency97 buffer97 queue97", "worker97"],
    ),
    (
        ("network97 latency97 buffer97 queue97 worker97 kernel97", 6),
        ["network97", "latency97", "buffer97", "queue97", "worker97", "kernel97"],
    ),
    (
        ("network97 latency97 buffer97 queue97 worker97 kernel97", 10),
        ["network97", "latency97", "buffer97", "queue97", "worker97", "kernel97"],
    ),
    (
        ("network97 latency97 buffer97 queue97 worker97 kernel97", 18),
        ["network97", "latency97 buffer97", "queue97 worker97", "kernel97"],
    ),
    (
        ("network97 latency97 buffer97 queue97 worker97 kernel97", 28),
        ["network97 latency97 buffer97", "queue97 worker97 kernel97"],
    ),
    (
        ("latency97 buffer97 queue97 worker97 kernel97 signal97", 6),
        ["latency97", "buffer97", "queue97", "worker97", "kernel97", "signal97"],
    ),
    (
        ("latency97 buffer97 queue97 worker97 kernel97 signal97", 10),
        ["latency97", "buffer97", "queue97", "worker97", "kernel97", "signal97"],
    ),
    (
        ("latency97 buffer97 queue97 worker97 kernel97 signal97", 18),
        ["latency97 buffer97", "queue97 worker97", "kernel97 signal97"],
    ),
    (
        ("latency97 buffer97 queue97 worker97 kernel97 signal97", 28),
        ["latency97 buffer97 queue97", "worker97 kernel97 signal97"],
    ),
    (
        ("buffer97 queue97 worker97 kernel97 signal97 packet97", 6),
        ["buffer97", "queue97", "worker97", "kernel97", "signal97", "packet97"],
    ),
    (
        ("buffer97 queue97 worker97 kernel97 signal97 packet97", 10),
        ["buffer97", "queue97", "worker97", "kernel97", "signal97", "packet97"],
    ),
    (
        ("buffer97 queue97 worker97 kernel97 signal97 packet97", 18),
        ["buffer97 queue97", "worker97 kernel97", "signal97 packet97"],
    ),
    (
        ("buffer97 queue97 worker97 kernel97 signal97 packet97", 28),
        ["buffer97 queue97 worker97", "kernel97 signal97 packet97"],
    ),
    (
        ("queue97 worker97 kernel97 signal97 packet97 router97", 6),
        ["queue97", "worker97", "kernel97", "signal97", "packet97", "router97"],
    ),
    (
        ("queue97 worker97 kernel97 signal97 packet97 router97", 10),
        ["queue97", "worker97", "kernel97", "signal97", "packet97", "router97"],
    ),
    (
        ("queue97 worker97 kernel97 signal97 packet97 router97", 18),
        ["queue97 worker97", "kernel97 signal97", "packet97 router97"],
    ),
    (
        ("queue97 worker97 kernel97 signal97 packet97 router97", 28),
        ["queue97 worker97 kernel97", "signal97 packet97 router97"],
    ),
    (
        ("worker97 kernel97 signal97 packet97 router97 cluster97", 6),
        ["worker97", "kernel97", "signal97", "packet97", "router97", "cluster97"],
    ),
    (
        ("worker97 kernel97 signal97 packet97 router97 cluster97", 10),
        ["worker97", "kernel97", "signal97", "packet97", "router97", "cluster97"],
    ),
    (
        ("worker97 kernel97 signal97 packet97 router97 cluster97", 18),
        ["worker97 kernel97", "signal97 packet97", "router97 cluster97"],
    ),
    (
        ("worker97 kernel97 signal97 packet97 router97 cluster97", 28),
        ["worker97 kernel97 signal97", "packet97 router97 cluster97"],
    ),
    (
        ("kernel97 signal97 packet97 router97 cluster97 mirror97", 6),
        ["kernel97", "signal97", "packet97", "router97", "cluster97", "mirror97"],
    ),
    (
        ("kernel97 signal97 packet97 router97 cluster97 mirror97", 10),
        ["kernel97", "signal97", "packet97", "router97", "cluster97", "mirror97"],
    ),
    (
        ("kernel97 signal97 packet97 router97 cluster97 mirror97", 18),
        ["kernel97 signal97", "packet97 router97", "cluster97 mirror97"],
    ),
    (
        ("kernel97 signal97 packet97 router97 cluster97 mirror97", 28),
        ["kernel97 signal97 packet97", "router97 cluster97 mirror97"],
    ),
    (
        ("signal97 packet97 router97 cluster97 mirror97 filter97", 6),
        ["signal97", "packet97", "router97", "cluster97", "mirror97", "filter97"],
    ),
    (
        ("signal97 packet97 router97 cluster97 mirror97 filter97", 10),
        ["signal97", "packet97", "router97", "cluster97", "mirror97", "filter97"],
    ),
    (
        ("signal97 packet97 router97 cluster97 mirror97 filter97", 18),
        ["signal97 packet97", "router97 cluster97", "mirror97 filter97"],
    ),
    (
        ("signal97 packet97 router97 cluster97 mirror97 filter97", 28),
        ["signal97 packet97 router97", "cluster97 mirror97 filter97"],
    ),
    (
        ("packet97 router97 cluster97 mirror97 filter97 ranking97", 6),
        ["packet97", "router97", "cluster97", "mirror97", "filter97", "ranking97"],
    ),
    (
        ("packet97 router97 cluster97 mirror97 filter97 ranking97", 10),
        ["packet97", "router97", "cluster97", "mirror97", "filter97", "ranking97"],
    ),
    (
        ("packet97 router97 cluster97 mirror97 filter97 ranking97", 18),
        ["packet97 router97", "cluster97 mirror97", "filter97 ranking97"],
    ),
    (
        ("packet97 router97 cluster97 mirror97 filter97 ranking97", 28),
        ["packet97 router97 cluster97", "mirror97 filter97 ranking97"],
    ),
    (
        ("router97 cluster97 mirror97 filter97 ranking97 encoding97", 6),
        ["router97", "cluster97", "mirror97", "filter97", "ranking97", "encoding97"],
    ),
    (
        ("router97 cluster97 mirror97 filter97 ranking97 encoding97", 10),
        ["router97", "cluster97", "mirror97", "filter97", "ranking97", "encoding97"],
    ),
    (
        ("router97 cluster97 mirror97 filter97 ranking97 encoding97", 18),
        ["router97 cluster97", "mirror97 filter97", "ranking97", "encoding97"],
    ),
    (
        ("router97 cluster97 mirror97 filter97 ranking97 encoding97", 28),
        ["router97 cluster97 mirror97", "filter97 ranking97", "encoding97"],
    ),
    (
        ("cluster97 mirror97 filter97 ranking97 encoding97 mapping97", 6),
        ["cluster97", "mirror97", "filter97", "ranking97", "encoding97", "mapping97"],
    ),
    (
        ("cluster97 mirror97 filter97 ranking97 encoding97 mapping97", 10),
        ["cluster97", "mirror97", "filter97", "ranking97", "encoding97", "mapping97"],
    ),
    (
        ("cluster97 mirror97 filter97 ranking97 encoding97 mapping97", 18),
        ["cluster97 mirror97", "filter97 ranking97", "encoding97", "mapping97"],
    ),
    (
        ("cluster97 mirror97 filter97 ranking97 encoding97 mapping97", 28),
        ["cluster97 mirror97 filter97", "ranking97 encoding97", "mapping97"],
    ),
    (
        ("mirror97 filter97 ranking97 encoding97 mapping97 record97", 6),
        ["mirror97", "filter97", "ranking97", "encoding97", "mapping97", "record97"],
    ),
    (
        ("mirror97 filter97 ranking97 encoding97 mapping97 record97", 10),
        ["mirror97", "filter97", "ranking97", "encoding97", "mapping97", "record97"],
    ),
    (
        ("mirror97 filter97 ranking97 encoding97 mapping97 record97", 18),
        ["mirror97 filter97", "ranking97", "encoding97", "mapping97 record97"],
    ),
    (
        ("mirror97 filter97 ranking97 encoding97 mapping97 record97", 28),
        ["mirror97 filter97 ranking97", "encoding97 mapping97", "record97"],
    ),
    (
        ("filter97 ranking97 encoding97 mapping97 record97 candle97", 6),
        ["filter97", "ranking97", "encoding97", "mapping97", "record97", "candle97"],
    ),
    (
        ("filter97 ranking97 encoding97 mapping97 record97 candle97", 10),
        ["filter97", "ranking97", "encoding97", "mapping97", "record97", "candle97"],
    ),
    (
        ("filter97 ranking97 encoding97 mapping97 record97 candle97", 18),
        ["filter97 ranking97", "encoding97", "mapping97 record97", "candle97"],
    ),
    (
        ("filter97 ranking97 encoding97 mapping97 record97 candle97", 28),
        ["filter97 ranking97", "encoding97 mapping97", "record97 candle97"],
    ),
    (
        ("ranking97 encoding97 mapping97 record97 candle97 thread97", 6),
        ["ranking97", "encoding97", "mapping97", "record97", "candle97", "thread97"],
    ),
    (
        ("ranking97 encoding97 mapping97 record97 candle97 thread97", 10),
        ["ranking97", "encoding97", "mapping97", "record97", "candle97", "thread97"],
    ),
    (
        ("ranking97 encoding97 mapping97 record97 candle97 thread97", 18),
        ["ranking97", "encoding97", "mapping97 record97", "candle97 thread97"],
    ),
    (
        ("ranking97 encoding97 mapping97 record97 candle97 thread97", 28),
        ["ranking97 encoding97", "mapping97 record97 candle97", "thread97"],
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
