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
        ("round 133: the quick brown fox jumps over the lazy dog", 4),
        ["round", "133:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", 8),
        ["round", "133: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", 12),
        ["round 133:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", 16),
        ["round 133: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", 24),
        ["round 133: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 133: the quick brown fox jumps over the lazy dog", 32),
        ["round 133: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", 4),
        ["round", "133:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", 8),
        ["round", "133:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", 12),
        ["round 133:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", 16),
        ["round 133:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", 24),
        ["round 133: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 133: agentuniverse is a framework for multi agents", 32),
        ["round 133: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", 4),
        ["round", "133:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", 8),
        ["round", "133:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", 12),
        ["round 133:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", 16),
        ["round 133:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", 24),
        ["round 133: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 133: knowledge stored as vectors enables retrieval", 32),
        ["round 133: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 133: the processor reads the record then stops", 4),
        ["round", "133:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 133: the processor reads the record then stops", 8),
        ["round", "133: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 133: the processor reads the record then stops", 12),
        ["round 133:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 133: the processor reads the record then stops", 16),
        ["round 133: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 133: the processor reads the record then stops", 24),
        ["round 133: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 133: the processor reads the record then stops", 32),
        ["round 133: the processor reads", "the record then stops"],
    ),
    (
        ("round 133: a worker pulls the next task from the queue", 4),
        ["round", "133:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 133: a worker pulls the next task from the queue", 8),
        ["round", "133: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 133: a worker pulls the next task from the queue", 12),
        ["round 133: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 133: a worker pulls the next task from the queue", 16),
        ["round 133: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 133: a worker pulls the next task from the queue", 24),
        ["round 133: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 133: a worker pulls the next task from the queue", 32),
        ["round 133: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 133: signals travel through the network layer", 4),
        ["round", "133:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 133: signals travel through the network layer", 8),
        ["round", "133:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 133: signals travel through the network layer", 12),
        ["round 133:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 133: signals travel through the network layer", 16),
        ["round 133:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 133: signals travel through the network layer", 24),
        ["round 133: signals", "travel through the", "network layer"],
    ),
    (
        ("round 133: signals travel through the network layer", 32),
        ["round 133: signals travel", "through the network layer"],
    ),
    (
        ("round 133: the gateway routes each request by policy", 4),
        ["round", "133:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 133: the gateway routes each request by policy", 8),
        ["round", "133: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 133: the gateway routes each request by policy", 12),
        ["round 133:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 133: the gateway routes each request by policy", 16),
        ["round 133: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 133: the gateway routes each request by policy", 24),
        ["round 133: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 133: the gateway routes each request by policy", 32),
        ["round 133: the gateway routes", "each request by policy"],
    ),
    (
        ("round 133: memory grows until the buffer is full", 4),
        ["round", "133:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 133: memory grows until the buffer is full", 8),
        ["round", "133:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 133: memory grows until the buffer is full", 12),
        ["round 133:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 133: memory grows until the buffer is full", 16),
        ["round 133:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 133: memory grows until the buffer is full", 24), ["round 133: memory grows", "until the buffer is full"]),
    (("round 133: memory grows until the buffer is full", 32), ["round 133: memory grows until", "the buffer is full"]),
    (
        ("round 133: the cluster mirrors every packet twice", 4),
        ["round", "133:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 133: the cluster mirrors every packet twice", 8),
        ["round", "133: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 133: the cluster mirrors every packet twice", 12),
        ["round 133:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 133: the cluster mirrors every packet twice", 16),
        ["round 133: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 133: the cluster mirrors every packet twice", 24),
        ["round 133: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 133: the cluster mirrors every packet twice", 32),
        ["round 133: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", 4),
        ["round", "133:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", 8),
        ["round", "133:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", 12),
        ["round 133:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", 16),
        ["round 133:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", 24),
        ["round 133: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 133: ranking uses tokens learned from the corpus", 32),
        ["round 133: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 133: a long session ends when the candle dies", 4),
        ["round", "133:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 133: a long session ends when the candle dies", 8),
        ["round", "133: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 133: a long session ends when the candle dies", 12),
        ["round 133: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 133: a long session ends when the candle dies", 16),
        ["round 133: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 133: a long session ends when the candle dies", 24),
        ["round 133: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 133: a long session ends when the candle dies", 32),
        ["round 133: a long session ends", "when the candle dies"],
    ),
    (
        ("round 133: encode the prompt then map the result", 4),
        ["round", "133:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 133: encode the prompt then map the result", 8),
        ["round", "133:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 133: encode the prompt then map the result", 12),
        ["round 133:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 133: encode the prompt then map the result", 16),
        ["round 133:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 133: encode the prompt then map the result", 24),
        ["round 133: encode the", "prompt then map the", "result"],
    ),
    (("round 133: encode the prompt then map the result", 32), ["round 133: encode the prompt", "then map the result"]),
    (
        ("round 133: the kernel wakes the worker at dawn", 4),
        ["round", "133:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 133: the kernel wakes the worker at dawn", 8),
        ["round", "133: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 133: the kernel wakes the worker at dawn", 12),
        ["round 133:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 133: the kernel wakes the worker at dawn", 16), ["round 133: the", "kernel wakes the", "worker at dawn"]),
    (("round 133: the kernel wakes the worker at dawn", 24), ["round 133: the kernel", "wakes the worker at dawn"]),
    (("round 133: the kernel wakes the worker at dawn", 32), ["round 133: the kernel wakes the", "worker at dawn"]),
    (
        ("round 133: service latency drops after the patch", 4),
        ["round", "133:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 133: service latency drops after the patch", 8),
        ["round", "133:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 133: service latency drops after the patch", 12),
        ["round 133:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 133: service latency drops after the patch", 16),
        ["round 133:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 133: service latency drops after the patch", 24),
        ["round 133: service", "latency drops after the", "patch"],
    ),
    (("round 133: service latency drops after the patch", 32), ["round 133: service latency drops", "after the patch"]),
    (
        ("round 133: the library caches every vector it sees", 4),
        ["round", "133:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 133: the library caches every vector it sees", 8),
        ["round", "133: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 133: the library caches every vector it sees", 12),
        ["round 133:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 133: the library caches every vector it sees", 16),
        ["round 133: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 133: the library caches every vector it sees", 24),
        ["round 133: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 133: the library caches every vector it sees", 32),
        ["round 133: the library caches", "every vector it sees"],
    ),
    (
        ("round 133: agents argue then the debate resolves", 4),
        ["round", "133:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 133: agents argue then the debate resolves", 8),
        ["round", "133:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 133: agents argue then the debate resolves", 12),
        ["round 133:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 133: agents argue then the debate resolves", 16),
        ["round 133:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 133: agents argue then the debate resolves", 24), ["round 133: agents argue", "then the debate resolves"]),
    (("round 133: agents argue then the debate resolves", 32), ["round 133: agents argue then the", "debate resolves"]),
    (
        ("round 133: the filter keeps only strong matches", 4),
        ["round", "133:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 133: the filter keeps only strong matches", 8),
        ["round", "133: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 133: the filter keeps only strong matches", 12),
        ["round 133:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 133: the filter keeps only strong matches", 16),
        ["round 133: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 133: the filter keeps only strong matches", 24),
        ["round 133: the filter", "keeps only strong", "matches"],
    ),
    (("round 133: the filter keeps only strong matches", 32), ["round 133: the filter keeps only", "strong matches"]),
    (
        ("round 133: the model answers with a short reply", 4),
        ["round", "133:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 133: the model answers with a short reply", 8),
        ["round", "133: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 133: the model answers with a short reply", 12),
        ["round 133:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 133: the model answers with a short reply", 16),
        ["round 133: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 133: the model answers with a short reply", 24),
        ["round 133: the model", "answers with a short", "reply"],
    ),
    (("round 133: the model answers with a short reply", 32), ["round 133: the model answers", "with a short reply"]),
    (
        ("round 133: the recorder stores the reasoning trace", 4),
        ["round", "133:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 133: the recorder stores the reasoning trace", 8),
        ["round", "133: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 133: the recorder stores the reasoning trace", 12),
        ["round 133:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 133: the recorder stores the reasoning trace", 16),
        ["round 133: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 133: the recorder stores the reasoning trace", 24),
        ["round 133: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 133: the recorder stores the reasoning trace", 32),
        ["round 133: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 133: the angel watches the processor run", 4),
        ["round", "133:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 133: the angel watches the processor run", 8),
        ["round", "133: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 133: the angel watches the processor run", 12),
        ["round 133:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 133: the angel watches the processor run", 16),
        ["round 133: the", "angel watches", "the processor", "run"],
    ),
    (("round 133: the angel watches the processor run", 24), ["round 133: the angel", "watches the processor", "run"]),
    (("round 133: the angel watches the processor run", 32), ["round 133: the angel watches the", "processor run"]),
    (
        ("round 133: angle of the vector decides the match", 4),
        ["round", "133:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 133: angle of the vector decides the match", 8),
        ["round", "133:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 133: angle of the vector decides the match", 12),
        ["round 133:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 133: angle of the vector decides the match", 16),
        ["round 133: angle", "of the vector", "decides the", "match"],
    ),
    (("round 133: angle of the vector decides the match", 24), ["round 133: angle of the", "vector decides the match"]),
    (("round 133: angle of the vector decides the match", 32), ["round 133: angle of the vector", "decides the match"]),
    (
        ("round 133: the candle burns twice as long at night", 4),
        ["round", "133:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 133: the candle burns twice as long at night", 8),
        ["round", "133: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 133: the candle burns twice as long at night", 12),
        ["round 133:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 133: the candle burns twice as long at night", 16),
        ["round 133: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 133: the candle burns twice as long at night", 24),
        ["round 133: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 133: the candle burns twice as long at night", 32),
        ["round 133: the candle burns", "twice as long at night"],
    ),
    (
        ("round 133: a mirror of the universe in one line", 4),
        ["round", "133:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 133: a mirror of the universe in one line", 8),
        ["round", "133: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 133: a mirror of the universe in one line", 12),
        ["round 133: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 133: a mirror of the universe in one line", 16),
        ["round 133: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 133: a mirror of the universe in one line", 24), ["round 133: a mirror of", "the universe in one line"]),
    (("round 133: a mirror of the universe in one line", 32), ["round 133: a mirror of the", "universe in one line"]),
    (
        ("round 133: the queue drains before the storm", 4),
        ["round", "133:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 133: the queue drains before the storm", 8),
        ["round", "133: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 133: the queue drains before the storm", 12),
        ["round 133:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 133: the queue drains before the storm", 16), ["round 133: the", "queue drains", "before the storm"]),
    (("round 133: the queue drains before the storm", 24), ["round 133: the queue", "drains before the storm"]),
    (("round 133: the queue drains before the storm", 32), ["round 133: the queue drains", "before the storm"]),
    (
        ("kitten133 sitting133 agent133 angle133 universe133 memory133", 6),
        ["kitten133", "sitting133", "agent133", "angle133", "universe133", "memory133"],
    ),
    (
        ("kitten133 sitting133 agent133 angle133 universe133 memory133", 10),
        ["kitten133", "sitting133", "agent133", "angle133", "universe133", "memory133"],
    ),
    (
        ("kitten133 sitting133 agent133 angle133 universe133 memory133", 18),
        ["kitten133", "sitting133", "agent133 angle133", "universe133", "memory133"],
    ),
    (
        ("kitten133 sitting133 agent133 angle133 universe133 memory133", 28),
        ["kitten133 sitting133", "agent133 angle133", "universe133 memory133"],
    ),
    (
        ("sitting133 agent133 angle133 universe133 memory133 stream133", 6),
        ["sitting133", "agent133", "angle133", "universe133", "memory133", "stream133"],
    ),
    (
        ("sitting133 agent133 angle133 universe133 memory133 stream133", 10),
        ["sitting133", "agent133", "angle133", "universe133", "memory133", "stream133"],
    ),
    (
        ("sitting133 agent133 angle133 universe133 memory133 stream133", 18),
        ["sitting133", "agent133 angle133", "universe133", "memory133", "stream133"],
    ),
    (
        ("sitting133 agent133 angle133 universe133 memory133 stream133", 28),
        ["sitting133 agent133 angle133", "universe133 memory133", "stream133"],
    ),
    (
        ("agent133 angle133 universe133 memory133 stream133 context133", 6),
        ["agent133", "angle133", "universe133", "memory133", "stream133", "context133"],
    ),
    (
        ("agent133 angle133 universe133 memory133 stream133 context133", 10),
        ["agent133", "angle133", "universe133", "memory133", "stream133", "context133"],
    ),
    (
        ("agent133 angle133 universe133 memory133 stream133 context133", 18),
        ["agent133 angle133", "universe133", "memory133", "stream133", "context133"],
    ),
    (
        ("agent133 angle133 universe133 memory133 stream133 context133", 28),
        ["agent133 angle133", "universe133 memory133", "stream133 context133"],
    ),
    (
        ("angle133 universe133 memory133 stream133 context133 knowledge133", 6),
        ["angle133", "universe133", "memory133", "stream133", "context133", "knowledge133"],
    ),
    (
        ("angle133 universe133 memory133 stream133 context133 knowledge133", 10),
        ["angle133", "universe133", "memory133", "stream133", "context133", "knowledge133"],
    ),
    (
        ("angle133 universe133 memory133 stream133 context133 knowledge133", 18),
        ["angle133", "universe133", "memory133", "stream133", "context133", "knowledge133"],
    ),
    (
        ("angle133 universe133 memory133 stream133 context133 knowledge133", 28),
        ["angle133 universe133", "memory133 stream133", "context133 knowledge133"],
    ),
    (
        ("universe133 memory133 stream133 context133 knowledge133 vector133", 6),
        ["universe133", "memory133", "stream133", "context133", "knowledge133", "vector133"],
    ),
    (
        ("universe133 memory133 stream133 context133 knowledge133 vector133", 10),
        ["universe133", "memory133", "stream133", "context133", "knowledge133", "vector133"],
    ),
    (
        ("universe133 memory133 stream133 context133 knowledge133 vector133", 18),
        ["universe133", "memory133", "stream133", "context133", "knowledge133", "vector133"],
    ),
    (
        ("universe133 memory133 stream133 context133 knowledge133 vector133", 28),
        ["universe133 memory133", "stream133 context133", "knowledge133 vector133"],
    ),
    (
        ("memory133 stream133 context133 knowledge133 vector133 processor133", 6),
        ["memory133", "stream133", "context133", "knowledge133", "vector133", "processor133"],
    ),
    (
        ("memory133 stream133 context133 knowledge133 vector133 processor133", 10),
        ["memory133", "stream133", "context133", "knowledge133", "vector133", "processor133"],
    ),
    (
        ("memory133 stream133 context133 knowledge133 vector133 processor133", 18),
        ["memory133", "stream133", "context133", "knowledge133", "vector133", "processor133"],
    ),
    (
        ("memory133 stream133 context133 knowledge133 vector133 processor133", 28),
        ["memory133 stream133", "context133 knowledge133", "vector133 processor133"],
    ),
    (
        ("stream133 context133 knowledge133 vector133 processor133 reasoning133", 6),
        ["stream133", "context133", "knowledge133", "vector133", "processor133", "reasoning133"],
    ),
    (
        ("stream133 context133 knowledge133 vector133 processor133 reasoning133", 10),
        ["stream133", "context133", "knowledge133", "vector133", "processor133", "reasoning133"],
    ),
    (
        ("stream133 context133 knowledge133 vector133 processor133 reasoning133", 18),
        ["stream133", "context133", "knowledge133", "vector133", "processor133", "reasoning133"],
    ),
    (
        ("stream133 context133 knowledge133 vector133 processor133 reasoning133", 28),
        ["stream133 context133", "knowledge133 vector133", "processor133 reasoning133"],
    ),
    (
        ("context133 knowledge133 vector133 processor133 reasoning133 machine133", 6),
        ["context133", "knowledge133", "vector133", "processor133", "reasoning133", "machine133"],
    ),
    (
        ("context133 knowledge133 vector133 processor133 reasoning133 machine133", 10),
        ["context133", "knowledge133", "vector133", "processor133", "reasoning133", "machine133"],
    ),
    (
        ("context133 knowledge133 vector133 processor133 reasoning133 machine133", 18),
        ["context133", "knowledge133", "vector133", "processor133", "reasoning133", "machine133"],
    ),
    (
        ("context133 knowledge133 vector133 processor133 reasoning133 machine133", 28),
        ["context133 knowledge133", "vector133 processor133", "reasoning133 machine133"],
    ),
    (
        ("knowledge133 vector133 processor133 reasoning133 machine133 learning133", 6),
        ["knowledge133", "vector133", "processor133", "reasoning133", "machine133", "learning133"],
    ),
    (
        ("knowledge133 vector133 processor133 reasoning133 machine133 learning133", 10),
        ["knowledge133", "vector133", "processor133", "reasoning133", "machine133", "learning133"],
    ),
    (
        ("knowledge133 vector133 processor133 reasoning133 machine133 learning133", 18),
        ["knowledge133", "vector133", "processor133", "reasoning133", "machine133", "learning133"],
    ),
    (
        ("knowledge133 vector133 processor133 reasoning133 machine133 learning133", 28),
        ["knowledge133 vector133", "processor133 reasoning133", "machine133 learning133"],
    ),
    (
        ("vector133 processor133 reasoning133 machine133 learning133 model133", 6),
        ["vector133", "processor133", "reasoning133", "machine133", "learning133", "model133"],
    ),
    (
        ("vector133 processor133 reasoning133 machine133 learning133 model133", 10),
        ["vector133", "processor133", "reasoning133", "machine133", "learning133", "model133"],
    ),
    (
        ("vector133 processor133 reasoning133 machine133 learning133 model133", 18),
        ["vector133", "processor133", "reasoning133", "machine133", "learning133", "model133"],
    ),
    (
        ("vector133 processor133 reasoning133 machine133 learning133 model133", 28),
        ["vector133 processor133", "reasoning133 machine133", "learning133 model133"],
    ),
    (
        ("processor133 reasoning133 machine133 learning133 model133 token133", 6),
        ["processor133", "reasoning133", "machine133", "learning133", "model133", "token133"],
    ),
    (
        ("processor133 reasoning133 machine133 learning133 model133 token133", 10),
        ["processor133", "reasoning133", "machine133", "learning133", "model133", "token133"],
    ),
    (
        ("processor133 reasoning133 machine133 learning133 model133 token133", 18),
        ["processor133", "reasoning133", "machine133", "learning133", "model133 token133"],
    ),
    (
        ("processor133 reasoning133 machine133 learning133 model133 token133", 28),
        ["processor133 reasoning133", "machine133 learning133", "model133 token133"],
    ),
    (
        ("reasoning133 machine133 learning133 model133 token133 prompt133", 6),
        ["reasoning133", "machine133", "learning133", "model133", "token133", "prompt133"],
    ),
    (
        ("reasoning133 machine133 learning133 model133 token133 prompt133", 10),
        ["reasoning133", "machine133", "learning133", "model133", "token133", "prompt133"],
    ),
    (
        ("reasoning133 machine133 learning133 model133 token133 prompt133", 18),
        ["reasoning133", "machine133", "learning133", "model133 token133", "prompt133"],
    ),
    (
        ("reasoning133 machine133 learning133 model133 token133 prompt133", 28),
        ["reasoning133 machine133", "learning133 model133", "token133 prompt133"],
    ),
    (
        ("machine133 learning133 model133 token133 prompt133 session133", 6),
        ["machine133", "learning133", "model133", "token133", "prompt133", "session133"],
    ),
    (
        ("machine133 learning133 model133 token133 prompt133 session133", 10),
        ["machine133", "learning133", "model133", "token133", "prompt133", "session133"],
    ),
    (
        ("machine133 learning133 model133 token133 prompt133 session133", 18),
        ["machine133", "learning133", "model133 token133", "prompt133", "session133"],
    ),
    (
        ("machine133 learning133 model133 token133 prompt133 session133", 28),
        ["machine133 learning133", "model133 token133 prompt133", "session133"],
    ),
    (
        ("learning133 model133 token133 prompt133 session133 library133", 6),
        ["learning133", "model133", "token133", "prompt133", "session133", "library133"],
    ),
    (
        ("learning133 model133 token133 prompt133 session133 library133", 10),
        ["learning133", "model133", "token133", "prompt133", "session133", "library133"],
    ),
    (
        ("learning133 model133 token133 prompt133 session133 library133", 18),
        ["learning133", "model133 token133", "prompt133", "session133", "library133"],
    ),
    (
        ("learning133 model133 token133 prompt133 session133 library133", 28),
        ["learning133 model133", "token133 prompt133", "session133 library133"],
    ),
    (
        ("model133 token133 prompt133 session133 library133 service133", 6),
        ["model133", "token133", "prompt133", "session133", "library133", "service133"],
    ),
    (
        ("model133 token133 prompt133 session133 library133 service133", 10),
        ["model133", "token133", "prompt133", "session133", "library133", "service133"],
    ),
    (
        ("model133 token133 prompt133 session133 library133 service133", 18),
        ["model133 token133", "prompt133", "session133", "library133", "service133"],
    ),
    (
        ("model133 token133 prompt133 session133 library133 service133", 28),
        ["model133 token133 prompt133", "session133 library133", "service133"],
    ),
    (
        ("token133 prompt133 session133 library133 service133 gateway133", 6),
        ["token133", "prompt133", "session133", "library133", "service133", "gateway133"],
    ),
    (
        ("token133 prompt133 session133 library133 service133 gateway133", 10),
        ["token133", "prompt133", "session133", "library133", "service133", "gateway133"],
    ),
    (
        ("token133 prompt133 session133 library133 service133 gateway133", 18),
        ["token133 prompt133", "session133", "library133", "service133", "gateway133"],
    ),
    (
        ("token133 prompt133 session133 library133 service133 gateway133", 28),
        ["token133 prompt133", "session133 library133", "service133 gateway133"],
    ),
    (
        ("prompt133 session133 library133 service133 gateway133 storage133", 6),
        ["prompt133", "session133", "library133", "service133", "gateway133", "storage133"],
    ),
    (
        ("prompt133 session133 library133 service133 gateway133 storage133", 10),
        ["prompt133", "session133", "library133", "service133", "gateway133", "storage133"],
    ),
    (
        ("prompt133 session133 library133 service133 gateway133 storage133", 18),
        ["prompt133", "session133", "library133", "service133", "gateway133", "storage133"],
    ),
    (
        ("prompt133 session133 library133 service133 gateway133 storage133", 28),
        ["prompt133 session133", "library133 service133", "gateway133 storage133"],
    ),
    (
        ("session133 library133 service133 gateway133 storage133 network133", 6),
        ["session133", "library133", "service133", "gateway133", "storage133", "network133"],
    ),
    (
        ("session133 library133 service133 gateway133 storage133 network133", 10),
        ["session133", "library133", "service133", "gateway133", "storage133", "network133"],
    ),
    (
        ("session133 library133 service133 gateway133 storage133 network133", 18),
        ["session133", "library133", "service133", "gateway133", "storage133", "network133"],
    ),
    (
        ("session133 library133 service133 gateway133 storage133 network133", 28),
        ["session133 library133", "service133 gateway133", "storage133 network133"],
    ),
    (
        ("library133 service133 gateway133 storage133 network133 latency133", 6),
        ["library133", "service133", "gateway133", "storage133", "network133", "latency133"],
    ),
    (
        ("library133 service133 gateway133 storage133 network133 latency133", 10),
        ["library133", "service133", "gateway133", "storage133", "network133", "latency133"],
    ),
    (
        ("library133 service133 gateway133 storage133 network133 latency133", 18),
        ["library133", "service133", "gateway133", "storage133", "network133", "latency133"],
    ),
    (
        ("library133 service133 gateway133 storage133 network133 latency133", 28),
        ["library133 service133", "gateway133 storage133", "network133 latency133"],
    ),
    (
        ("service133 gateway133 storage133 network133 latency133 buffer133", 6),
        ["service133", "gateway133", "storage133", "network133", "latency133", "buffer133"],
    ),
    (
        ("service133 gateway133 storage133 network133 latency133 buffer133", 10),
        ["service133", "gateway133", "storage133", "network133", "latency133", "buffer133"],
    ),
    (
        ("service133 gateway133 storage133 network133 latency133 buffer133", 18),
        ["service133", "gateway133", "storage133", "network133", "latency133", "buffer133"],
    ),
    (
        ("service133 gateway133 storage133 network133 latency133 buffer133", 28),
        ["service133 gateway133", "storage133 network133", "latency133 buffer133"],
    ),
    (
        ("gateway133 storage133 network133 latency133 buffer133 queue133", 6),
        ["gateway133", "storage133", "network133", "latency133", "buffer133", "queue133"],
    ),
    (
        ("gateway133 storage133 network133 latency133 buffer133 queue133", 10),
        ["gateway133", "storage133", "network133", "latency133", "buffer133", "queue133"],
    ),
    (
        ("gateway133 storage133 network133 latency133 buffer133 queue133", 18),
        ["gateway133", "storage133", "network133", "latency133", "buffer133 queue133"],
    ),
    (
        ("gateway133 storage133 network133 latency133 buffer133 queue133", 28),
        ["gateway133 storage133", "network133 latency133", "buffer133 queue133"],
    ),
    (
        ("storage133 network133 latency133 buffer133 queue133 worker133", 6),
        ["storage133", "network133", "latency133", "buffer133", "queue133", "worker133"],
    ),
    (
        ("storage133 network133 latency133 buffer133 queue133 worker133", 10),
        ["storage133", "network133", "latency133", "buffer133", "queue133", "worker133"],
    ),
    (
        ("storage133 network133 latency133 buffer133 queue133 worker133", 18),
        ["storage133", "network133", "latency133", "buffer133 queue133", "worker133"],
    ),
    (
        ("storage133 network133 latency133 buffer133 queue133 worker133", 28),
        ["storage133 network133", "latency133 buffer133", "queue133 worker133"],
    ),
    (
        ("network133 latency133 buffer133 queue133 worker133 kernel133", 6),
        ["network133", "latency133", "buffer133", "queue133", "worker133", "kernel133"],
    ),
    (
        ("network133 latency133 buffer133 queue133 worker133 kernel133", 10),
        ["network133", "latency133", "buffer133", "queue133", "worker133", "kernel133"],
    ),
    (
        ("network133 latency133 buffer133 queue133 worker133 kernel133", 18),
        ["network133", "latency133", "buffer133 queue133", "worker133", "kernel133"],
    ),
    (
        ("network133 latency133 buffer133 queue133 worker133 kernel133", 28),
        ["network133 latency133", "buffer133 queue133 worker133", "kernel133"],
    ),
    (
        ("latency133 buffer133 queue133 worker133 kernel133 signal133", 6),
        ["latency133", "buffer133", "queue133", "worker133", "kernel133", "signal133"],
    ),
    (
        ("latency133 buffer133 queue133 worker133 kernel133 signal133", 10),
        ["latency133", "buffer133", "queue133", "worker133", "kernel133", "signal133"],
    ),
    (
        ("latency133 buffer133 queue133 worker133 kernel133 signal133", 18),
        ["latency133", "buffer133 queue133", "worker133", "kernel133", "signal133"],
    ),
    (
        ("latency133 buffer133 queue133 worker133 kernel133 signal133", 28),
        ["latency133 buffer133", "queue133 worker133 kernel133", "signal133"],
    ),
    (
        ("buffer133 queue133 worker133 kernel133 signal133 packet133", 6),
        ["buffer133", "queue133", "worker133", "kernel133", "signal133", "packet133"],
    ),
    (
        ("buffer133 queue133 worker133 kernel133 signal133 packet133", 10),
        ["buffer133", "queue133", "worker133", "kernel133", "signal133", "packet133"],
    ),
    (
        ("buffer133 queue133 worker133 kernel133 signal133 packet133", 18),
        ["buffer133 queue133", "worker133", "kernel133", "signal133", "packet133"],
    ),
    (
        ("buffer133 queue133 worker133 kernel133 signal133 packet133", 28),
        ["buffer133 queue133 worker133", "kernel133 signal133", "packet133"],
    ),
    (
        ("queue133 worker133 kernel133 signal133 packet133 router133", 6),
        ["queue133", "worker133", "kernel133", "signal133", "packet133", "router133"],
    ),
    (
        ("queue133 worker133 kernel133 signal133 packet133 router133", 10),
        ["queue133", "worker133", "kernel133", "signal133", "packet133", "router133"],
    ),
    (
        ("queue133 worker133 kernel133 signal133 packet133 router133", 18),
        ["queue133 worker133", "kernel133", "signal133", "packet133", "router133"],
    ),
    (
        ("queue133 worker133 kernel133 signal133 packet133 router133", 28),
        ["queue133 worker133 kernel133", "signal133 packet133", "router133"],
    ),
    (
        ("worker133 kernel133 signal133 packet133 router133 cluster133", 6),
        ["worker133", "kernel133", "signal133", "packet133", "router133", "cluster133"],
    ),
    (
        ("worker133 kernel133 signal133 packet133 router133 cluster133", 10),
        ["worker133", "kernel133", "signal133", "packet133", "router133", "cluster133"],
    ),
    (
        ("worker133 kernel133 signal133 packet133 router133 cluster133", 18),
        ["worker133", "kernel133", "signal133", "packet133", "router133", "cluster133"],
    ),
    (
        ("worker133 kernel133 signal133 packet133 router133 cluster133", 28),
        ["worker133 kernel133", "signal133 packet133", "router133 cluster133"],
    ),
    (
        ("kernel133 signal133 packet133 router133 cluster133 mirror133", 6),
        ["kernel133", "signal133", "packet133", "router133", "cluster133", "mirror133"],
    ),
    (
        ("kernel133 signal133 packet133 router133 cluster133 mirror133", 10),
        ["kernel133", "signal133", "packet133", "router133", "cluster133", "mirror133"],
    ),
    (
        ("kernel133 signal133 packet133 router133 cluster133 mirror133", 18),
        ["kernel133", "signal133", "packet133", "router133", "cluster133", "mirror133"],
    ),
    (
        ("kernel133 signal133 packet133 router133 cluster133 mirror133", 28),
        ["kernel133 signal133", "packet133 router133", "cluster133 mirror133"],
    ),
    (
        ("signal133 packet133 router133 cluster133 mirror133 filter133", 6),
        ["signal133", "packet133", "router133", "cluster133", "mirror133", "filter133"],
    ),
    (
        ("signal133 packet133 router133 cluster133 mirror133 filter133", 10),
        ["signal133", "packet133", "router133", "cluster133", "mirror133", "filter133"],
    ),
    (
        ("signal133 packet133 router133 cluster133 mirror133 filter133", 18),
        ["signal133", "packet133", "router133", "cluster133", "mirror133", "filter133"],
    ),
    (
        ("signal133 packet133 router133 cluster133 mirror133 filter133", 28),
        ["signal133 packet133", "router133 cluster133", "mirror133 filter133"],
    ),
    (
        ("packet133 router133 cluster133 mirror133 filter133 ranking133", 6),
        ["packet133", "router133", "cluster133", "mirror133", "filter133", "ranking133"],
    ),
    (
        ("packet133 router133 cluster133 mirror133 filter133 ranking133", 10),
        ["packet133", "router133", "cluster133", "mirror133", "filter133", "ranking133"],
    ),
    (
        ("packet133 router133 cluster133 mirror133 filter133 ranking133", 18),
        ["packet133", "router133", "cluster133", "mirror133", "filter133", "ranking133"],
    ),
    (
        ("packet133 router133 cluster133 mirror133 filter133 ranking133", 28),
        ["packet133 router133", "cluster133 mirror133", "filter133 ranking133"],
    ),
    (
        ("router133 cluster133 mirror133 filter133 ranking133 encoding133", 6),
        ["router133", "cluster133", "mirror133", "filter133", "ranking133", "encoding133"],
    ),
    (
        ("router133 cluster133 mirror133 filter133 ranking133 encoding133", 10),
        ["router133", "cluster133", "mirror133", "filter133", "ranking133", "encoding133"],
    ),
    (
        ("router133 cluster133 mirror133 filter133 ranking133 encoding133", 18),
        ["router133", "cluster133", "mirror133", "filter133", "ranking133", "encoding133"],
    ),
    (
        ("router133 cluster133 mirror133 filter133 ranking133 encoding133", 28),
        ["router133 cluster133", "mirror133 filter133", "ranking133 encoding133"],
    ),
    (
        ("cluster133 mirror133 filter133 ranking133 encoding133 mapping133", 6),
        ["cluster133", "mirror133", "filter133", "ranking133", "encoding133", "mapping133"],
    ),
    (
        ("cluster133 mirror133 filter133 ranking133 encoding133 mapping133", 10),
        ["cluster133", "mirror133", "filter133", "ranking133", "encoding133", "mapping133"],
    ),
    (
        ("cluster133 mirror133 filter133 ranking133 encoding133 mapping133", 18),
        ["cluster133", "mirror133", "filter133", "ranking133", "encoding133", "mapping133"],
    ),
    (
        ("cluster133 mirror133 filter133 ranking133 encoding133 mapping133", 28),
        ["cluster133 mirror133", "filter133 ranking133", "encoding133 mapping133"],
    ),
    (
        ("mirror133 filter133 ranking133 encoding133 mapping133 record133", 6),
        ["mirror133", "filter133", "ranking133", "encoding133", "mapping133", "record133"],
    ),
    (
        ("mirror133 filter133 ranking133 encoding133 mapping133 record133", 10),
        ["mirror133", "filter133", "ranking133", "encoding133", "mapping133", "record133"],
    ),
    (
        ("mirror133 filter133 ranking133 encoding133 mapping133 record133", 18),
        ["mirror133", "filter133", "ranking133", "encoding133", "mapping133", "record133"],
    ),
    (
        ("mirror133 filter133 ranking133 encoding133 mapping133 record133", 28),
        ["mirror133 filter133", "ranking133 encoding133", "mapping133 record133"],
    ),
    (
        ("filter133 ranking133 encoding133 mapping133 record133 candle133", 6),
        ["filter133", "ranking133", "encoding133", "mapping133", "record133", "candle133"],
    ),
    (
        ("filter133 ranking133 encoding133 mapping133 record133 candle133", 10),
        ["filter133", "ranking133", "encoding133", "mapping133", "record133", "candle133"],
    ),
    (
        ("filter133 ranking133 encoding133 mapping133 record133 candle133", 18),
        ["filter133", "ranking133", "encoding133", "mapping133", "record133", "candle133"],
    ),
    (
        ("filter133 ranking133 encoding133 mapping133 record133 candle133", 28),
        ["filter133 ranking133", "encoding133 mapping133", "record133 candle133"],
    ),
    (
        ("ranking133 encoding133 mapping133 record133 candle133 thread133", 6),
        ["ranking133", "encoding133", "mapping133", "record133", "candle133", "thread133"],
    ),
    (
        ("ranking133 encoding133 mapping133 record133 candle133 thread133", 10),
        ["ranking133", "encoding133", "mapping133", "record133", "candle133", "thread133"],
    ),
    (
        ("ranking133 encoding133 mapping133 record133 candle133 thread133", 18),
        ["ranking133", "encoding133", "mapping133", "record133", "candle133", "thread133"],
    ),
    (
        ("ranking133 encoding133 mapping133 record133 candle133 thread133", 28),
        ["ranking133 encoding133", "mapping133 record133", "candle133 thread133"],
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
