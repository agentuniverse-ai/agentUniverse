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
        ("round 129: the quick brown fox jumps over the lazy dog", 4),
        ["round", "129:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", 8),
        ["round", "129: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", 12),
        ["round 129:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", 16),
        ["round 129: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", 24),
        ["round 129: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 129: the quick brown fox jumps over the lazy dog", 32),
        ["round 129: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", 4),
        ["round", "129:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", 8),
        ["round", "129:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", 12),
        ["round 129:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", 16),
        ["round 129:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", 24),
        ["round 129: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 129: agentuniverse is a framework for multi agents", 32),
        ["round 129: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", 4),
        ["round", "129:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", 8),
        ["round", "129:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", 12),
        ["round 129:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", 16),
        ["round 129:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", 24),
        ["round 129: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 129: knowledge stored as vectors enables retrieval", 32),
        ["round 129: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 129: the processor reads the record then stops", 4),
        ["round", "129:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 129: the processor reads the record then stops", 8),
        ["round", "129: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 129: the processor reads the record then stops", 12),
        ["round 129:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 129: the processor reads the record then stops", 16),
        ["round 129: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 129: the processor reads the record then stops", 24),
        ["round 129: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 129: the processor reads the record then stops", 32),
        ["round 129: the processor reads", "the record then stops"],
    ),
    (
        ("round 129: a worker pulls the next task from the queue", 4),
        ["round", "129:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 129: a worker pulls the next task from the queue", 8),
        ["round", "129: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 129: a worker pulls the next task from the queue", 12),
        ["round 129: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 129: a worker pulls the next task from the queue", 16),
        ["round 129: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 129: a worker pulls the next task from the queue", 24),
        ["round 129: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 129: a worker pulls the next task from the queue", 32),
        ["round 129: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 129: signals travel through the network layer", 4),
        ["round", "129:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 129: signals travel through the network layer", 8),
        ["round", "129:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 129: signals travel through the network layer", 12),
        ["round 129:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 129: signals travel through the network layer", 16),
        ["round 129:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 129: signals travel through the network layer", 24),
        ["round 129: signals", "travel through the", "network layer"],
    ),
    (
        ("round 129: signals travel through the network layer", 32),
        ["round 129: signals travel", "through the network layer"],
    ),
    (
        ("round 129: the gateway routes each request by policy", 4),
        ["round", "129:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 129: the gateway routes each request by policy", 8),
        ["round", "129: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 129: the gateway routes each request by policy", 12),
        ["round 129:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 129: the gateway routes each request by policy", 16),
        ["round 129: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 129: the gateway routes each request by policy", 24),
        ["round 129: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 129: the gateway routes each request by policy", 32),
        ["round 129: the gateway routes", "each request by policy"],
    ),
    (
        ("round 129: memory grows until the buffer is full", 4),
        ["round", "129:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 129: memory grows until the buffer is full", 8),
        ["round", "129:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 129: memory grows until the buffer is full", 12),
        ["round 129:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 129: memory grows until the buffer is full", 16),
        ["round 129:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 129: memory grows until the buffer is full", 24), ["round 129: memory grows", "until the buffer is full"]),
    (("round 129: memory grows until the buffer is full", 32), ["round 129: memory grows until", "the buffer is full"]),
    (
        ("round 129: the cluster mirrors every packet twice", 4),
        ["round", "129:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 129: the cluster mirrors every packet twice", 8),
        ["round", "129: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 129: the cluster mirrors every packet twice", 12),
        ["round 129:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 129: the cluster mirrors every packet twice", 16),
        ["round 129: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 129: the cluster mirrors every packet twice", 24),
        ["round 129: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 129: the cluster mirrors every packet twice", 32),
        ["round 129: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", 4),
        ["round", "129:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", 8),
        ["round", "129:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", 12),
        ["round 129:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", 16),
        ["round 129:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", 24),
        ["round 129: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 129: ranking uses tokens learned from the corpus", 32),
        ["round 129: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 129: a long session ends when the candle dies", 4),
        ["round", "129:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 129: a long session ends when the candle dies", 8),
        ["round", "129: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 129: a long session ends when the candle dies", 12),
        ["round 129: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 129: a long session ends when the candle dies", 16),
        ["round 129: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 129: a long session ends when the candle dies", 24),
        ["round 129: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 129: a long session ends when the candle dies", 32),
        ["round 129: a long session ends", "when the candle dies"],
    ),
    (
        ("round 129: encode the prompt then map the result", 4),
        ["round", "129:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 129: encode the prompt then map the result", 8),
        ["round", "129:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 129: encode the prompt then map the result", 12),
        ["round 129:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 129: encode the prompt then map the result", 16),
        ["round 129:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 129: encode the prompt then map the result", 24),
        ["round 129: encode the", "prompt then map the", "result"],
    ),
    (("round 129: encode the prompt then map the result", 32), ["round 129: encode the prompt", "then map the result"]),
    (
        ("round 129: the kernel wakes the worker at dawn", 4),
        ["round", "129:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 129: the kernel wakes the worker at dawn", 8),
        ["round", "129: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 129: the kernel wakes the worker at dawn", 12),
        ["round 129:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 129: the kernel wakes the worker at dawn", 16), ["round 129: the", "kernel wakes the", "worker at dawn"]),
    (("round 129: the kernel wakes the worker at dawn", 24), ["round 129: the kernel", "wakes the worker at dawn"]),
    (("round 129: the kernel wakes the worker at dawn", 32), ["round 129: the kernel wakes the", "worker at dawn"]),
    (
        ("round 129: service latency drops after the patch", 4),
        ["round", "129:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 129: service latency drops after the patch", 8),
        ["round", "129:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 129: service latency drops after the patch", 12),
        ["round 129:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 129: service latency drops after the patch", 16),
        ["round 129:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 129: service latency drops after the patch", 24),
        ["round 129: service", "latency drops after the", "patch"],
    ),
    (("round 129: service latency drops after the patch", 32), ["round 129: service latency drops", "after the patch"]),
    (
        ("round 129: the library caches every vector it sees", 4),
        ["round", "129:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 129: the library caches every vector it sees", 8),
        ["round", "129: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 129: the library caches every vector it sees", 12),
        ["round 129:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 129: the library caches every vector it sees", 16),
        ["round 129: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 129: the library caches every vector it sees", 24),
        ["round 129: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 129: the library caches every vector it sees", 32),
        ["round 129: the library caches", "every vector it sees"],
    ),
    (
        ("round 129: agents argue then the debate resolves", 4),
        ["round", "129:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 129: agents argue then the debate resolves", 8),
        ["round", "129:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 129: agents argue then the debate resolves", 12),
        ["round 129:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 129: agents argue then the debate resolves", 16),
        ["round 129:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 129: agents argue then the debate resolves", 24), ["round 129: agents argue", "then the debate resolves"]),
    (("round 129: agents argue then the debate resolves", 32), ["round 129: agents argue then the", "debate resolves"]),
    (
        ("round 129: the filter keeps only strong matches", 4),
        ["round", "129:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 129: the filter keeps only strong matches", 8),
        ["round", "129: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 129: the filter keeps only strong matches", 12),
        ["round 129:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 129: the filter keeps only strong matches", 16),
        ["round 129: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 129: the filter keeps only strong matches", 24),
        ["round 129: the filter", "keeps only strong", "matches"],
    ),
    (("round 129: the filter keeps only strong matches", 32), ["round 129: the filter keeps only", "strong matches"]),
    (
        ("round 129: the model answers with a short reply", 4),
        ["round", "129:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 129: the model answers with a short reply", 8),
        ["round", "129: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 129: the model answers with a short reply", 12),
        ["round 129:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 129: the model answers with a short reply", 16),
        ["round 129: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 129: the model answers with a short reply", 24),
        ["round 129: the model", "answers with a short", "reply"],
    ),
    (("round 129: the model answers with a short reply", 32), ["round 129: the model answers", "with a short reply"]),
    (
        ("round 129: the recorder stores the reasoning trace", 4),
        ["round", "129:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 129: the recorder stores the reasoning trace", 8),
        ["round", "129: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 129: the recorder stores the reasoning trace", 12),
        ["round 129:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 129: the recorder stores the reasoning trace", 16),
        ["round 129: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 129: the recorder stores the reasoning trace", 24),
        ["round 129: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 129: the recorder stores the reasoning trace", 32),
        ["round 129: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 129: the angel watches the processor run", 4),
        ["round", "129:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 129: the angel watches the processor run", 8),
        ["round", "129: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 129: the angel watches the processor run", 12),
        ["round 129:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 129: the angel watches the processor run", 16),
        ["round 129: the", "angel watches", "the processor", "run"],
    ),
    (("round 129: the angel watches the processor run", 24), ["round 129: the angel", "watches the processor", "run"]),
    (("round 129: the angel watches the processor run", 32), ["round 129: the angel watches the", "processor run"]),
    (
        ("round 129: angle of the vector decides the match", 4),
        ["round", "129:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 129: angle of the vector decides the match", 8),
        ["round", "129:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 129: angle of the vector decides the match", 12),
        ["round 129:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 129: angle of the vector decides the match", 16),
        ["round 129: angle", "of the vector", "decides the", "match"],
    ),
    (("round 129: angle of the vector decides the match", 24), ["round 129: angle of the", "vector decides the match"]),
    (("round 129: angle of the vector decides the match", 32), ["round 129: angle of the vector", "decides the match"]),
    (
        ("round 129: the candle burns twice as long at night", 4),
        ["round", "129:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 129: the candle burns twice as long at night", 8),
        ["round", "129: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 129: the candle burns twice as long at night", 12),
        ["round 129:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 129: the candle burns twice as long at night", 16),
        ["round 129: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 129: the candle burns twice as long at night", 24),
        ["round 129: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 129: the candle burns twice as long at night", 32),
        ["round 129: the candle burns", "twice as long at night"],
    ),
    (
        ("round 129: a mirror of the universe in one line", 4),
        ["round", "129:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 129: a mirror of the universe in one line", 8),
        ["round", "129: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 129: a mirror of the universe in one line", 12),
        ["round 129: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 129: a mirror of the universe in one line", 16),
        ["round 129: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 129: a mirror of the universe in one line", 24), ["round 129: a mirror of", "the universe in one line"]),
    (("round 129: a mirror of the universe in one line", 32), ["round 129: a mirror of the", "universe in one line"]),
    (
        ("round 129: the queue drains before the storm", 4),
        ["round", "129:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 129: the queue drains before the storm", 8),
        ["round", "129: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 129: the queue drains before the storm", 12),
        ["round 129:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 129: the queue drains before the storm", 16), ["round 129: the", "queue drains", "before the storm"]),
    (("round 129: the queue drains before the storm", 24), ["round 129: the queue", "drains before the storm"]),
    (("round 129: the queue drains before the storm", 32), ["round 129: the queue drains", "before the storm"]),
    (
        ("kitten129 sitting129 agent129 angle129 universe129 memory129", 6),
        ["kitten129", "sitting129", "agent129", "angle129", "universe129", "memory129"],
    ),
    (
        ("kitten129 sitting129 agent129 angle129 universe129 memory129", 10),
        ["kitten129", "sitting129", "agent129", "angle129", "universe129", "memory129"],
    ),
    (
        ("kitten129 sitting129 agent129 angle129 universe129 memory129", 18),
        ["kitten129", "sitting129", "agent129 angle129", "universe129", "memory129"],
    ),
    (
        ("kitten129 sitting129 agent129 angle129 universe129 memory129", 28),
        ["kitten129 sitting129", "agent129 angle129", "universe129 memory129"],
    ),
    (
        ("sitting129 agent129 angle129 universe129 memory129 stream129", 6),
        ["sitting129", "agent129", "angle129", "universe129", "memory129", "stream129"],
    ),
    (
        ("sitting129 agent129 angle129 universe129 memory129 stream129", 10),
        ["sitting129", "agent129", "angle129", "universe129", "memory129", "stream129"],
    ),
    (
        ("sitting129 agent129 angle129 universe129 memory129 stream129", 18),
        ["sitting129", "agent129 angle129", "universe129", "memory129", "stream129"],
    ),
    (
        ("sitting129 agent129 angle129 universe129 memory129 stream129", 28),
        ["sitting129 agent129 angle129", "universe129 memory129", "stream129"],
    ),
    (
        ("agent129 angle129 universe129 memory129 stream129 context129", 6),
        ["agent129", "angle129", "universe129", "memory129", "stream129", "context129"],
    ),
    (
        ("agent129 angle129 universe129 memory129 stream129 context129", 10),
        ["agent129", "angle129", "universe129", "memory129", "stream129", "context129"],
    ),
    (
        ("agent129 angle129 universe129 memory129 stream129 context129", 18),
        ["agent129 angle129", "universe129", "memory129", "stream129", "context129"],
    ),
    (
        ("agent129 angle129 universe129 memory129 stream129 context129", 28),
        ["agent129 angle129", "universe129 memory129", "stream129 context129"],
    ),
    (
        ("angle129 universe129 memory129 stream129 context129 knowledge129", 6),
        ["angle129", "universe129", "memory129", "stream129", "context129", "knowledge129"],
    ),
    (
        ("angle129 universe129 memory129 stream129 context129 knowledge129", 10),
        ["angle129", "universe129", "memory129", "stream129", "context129", "knowledge129"],
    ),
    (
        ("angle129 universe129 memory129 stream129 context129 knowledge129", 18),
        ["angle129", "universe129", "memory129", "stream129", "context129", "knowledge129"],
    ),
    (
        ("angle129 universe129 memory129 stream129 context129 knowledge129", 28),
        ["angle129 universe129", "memory129 stream129", "context129 knowledge129"],
    ),
    (
        ("universe129 memory129 stream129 context129 knowledge129 vector129", 6),
        ["universe129", "memory129", "stream129", "context129", "knowledge129", "vector129"],
    ),
    (
        ("universe129 memory129 stream129 context129 knowledge129 vector129", 10),
        ["universe129", "memory129", "stream129", "context129", "knowledge129", "vector129"],
    ),
    (
        ("universe129 memory129 stream129 context129 knowledge129 vector129", 18),
        ["universe129", "memory129", "stream129", "context129", "knowledge129", "vector129"],
    ),
    (
        ("universe129 memory129 stream129 context129 knowledge129 vector129", 28),
        ["universe129 memory129", "stream129 context129", "knowledge129 vector129"],
    ),
    (
        ("memory129 stream129 context129 knowledge129 vector129 processor129", 6),
        ["memory129", "stream129", "context129", "knowledge129", "vector129", "processor129"],
    ),
    (
        ("memory129 stream129 context129 knowledge129 vector129 processor129", 10),
        ["memory129", "stream129", "context129", "knowledge129", "vector129", "processor129"],
    ),
    (
        ("memory129 stream129 context129 knowledge129 vector129 processor129", 18),
        ["memory129", "stream129", "context129", "knowledge129", "vector129", "processor129"],
    ),
    (
        ("memory129 stream129 context129 knowledge129 vector129 processor129", 28),
        ["memory129 stream129", "context129 knowledge129", "vector129 processor129"],
    ),
    (
        ("stream129 context129 knowledge129 vector129 processor129 reasoning129", 6),
        ["stream129", "context129", "knowledge129", "vector129", "processor129", "reasoning129"],
    ),
    (
        ("stream129 context129 knowledge129 vector129 processor129 reasoning129", 10),
        ["stream129", "context129", "knowledge129", "vector129", "processor129", "reasoning129"],
    ),
    (
        ("stream129 context129 knowledge129 vector129 processor129 reasoning129", 18),
        ["stream129", "context129", "knowledge129", "vector129", "processor129", "reasoning129"],
    ),
    (
        ("stream129 context129 knowledge129 vector129 processor129 reasoning129", 28),
        ["stream129 context129", "knowledge129 vector129", "processor129 reasoning129"],
    ),
    (
        ("context129 knowledge129 vector129 processor129 reasoning129 machine129", 6),
        ["context129", "knowledge129", "vector129", "processor129", "reasoning129", "machine129"],
    ),
    (
        ("context129 knowledge129 vector129 processor129 reasoning129 machine129", 10),
        ["context129", "knowledge129", "vector129", "processor129", "reasoning129", "machine129"],
    ),
    (
        ("context129 knowledge129 vector129 processor129 reasoning129 machine129", 18),
        ["context129", "knowledge129", "vector129", "processor129", "reasoning129", "machine129"],
    ),
    (
        ("context129 knowledge129 vector129 processor129 reasoning129 machine129", 28),
        ["context129 knowledge129", "vector129 processor129", "reasoning129 machine129"],
    ),
    (
        ("knowledge129 vector129 processor129 reasoning129 machine129 learning129", 6),
        ["knowledge129", "vector129", "processor129", "reasoning129", "machine129", "learning129"],
    ),
    (
        ("knowledge129 vector129 processor129 reasoning129 machine129 learning129", 10),
        ["knowledge129", "vector129", "processor129", "reasoning129", "machine129", "learning129"],
    ),
    (
        ("knowledge129 vector129 processor129 reasoning129 machine129 learning129", 18),
        ["knowledge129", "vector129", "processor129", "reasoning129", "machine129", "learning129"],
    ),
    (
        ("knowledge129 vector129 processor129 reasoning129 machine129 learning129", 28),
        ["knowledge129 vector129", "processor129 reasoning129", "machine129 learning129"],
    ),
    (
        ("vector129 processor129 reasoning129 machine129 learning129 model129", 6),
        ["vector129", "processor129", "reasoning129", "machine129", "learning129", "model129"],
    ),
    (
        ("vector129 processor129 reasoning129 machine129 learning129 model129", 10),
        ["vector129", "processor129", "reasoning129", "machine129", "learning129", "model129"],
    ),
    (
        ("vector129 processor129 reasoning129 machine129 learning129 model129", 18),
        ["vector129", "processor129", "reasoning129", "machine129", "learning129", "model129"],
    ),
    (
        ("vector129 processor129 reasoning129 machine129 learning129 model129", 28),
        ["vector129 processor129", "reasoning129 machine129", "learning129 model129"],
    ),
    (
        ("processor129 reasoning129 machine129 learning129 model129 token129", 6),
        ["processor129", "reasoning129", "machine129", "learning129", "model129", "token129"],
    ),
    (
        ("processor129 reasoning129 machine129 learning129 model129 token129", 10),
        ["processor129", "reasoning129", "machine129", "learning129", "model129", "token129"],
    ),
    (
        ("processor129 reasoning129 machine129 learning129 model129 token129", 18),
        ["processor129", "reasoning129", "machine129", "learning129", "model129 token129"],
    ),
    (
        ("processor129 reasoning129 machine129 learning129 model129 token129", 28),
        ["processor129 reasoning129", "machine129 learning129", "model129 token129"],
    ),
    (
        ("reasoning129 machine129 learning129 model129 token129 prompt129", 6),
        ["reasoning129", "machine129", "learning129", "model129", "token129", "prompt129"],
    ),
    (
        ("reasoning129 machine129 learning129 model129 token129 prompt129", 10),
        ["reasoning129", "machine129", "learning129", "model129", "token129", "prompt129"],
    ),
    (
        ("reasoning129 machine129 learning129 model129 token129 prompt129", 18),
        ["reasoning129", "machine129", "learning129", "model129 token129", "prompt129"],
    ),
    (
        ("reasoning129 machine129 learning129 model129 token129 prompt129", 28),
        ["reasoning129 machine129", "learning129 model129", "token129 prompt129"],
    ),
    (
        ("machine129 learning129 model129 token129 prompt129 session129", 6),
        ["machine129", "learning129", "model129", "token129", "prompt129", "session129"],
    ),
    (
        ("machine129 learning129 model129 token129 prompt129 session129", 10),
        ["machine129", "learning129", "model129", "token129", "prompt129", "session129"],
    ),
    (
        ("machine129 learning129 model129 token129 prompt129 session129", 18),
        ["machine129", "learning129", "model129 token129", "prompt129", "session129"],
    ),
    (
        ("machine129 learning129 model129 token129 prompt129 session129", 28),
        ["machine129 learning129", "model129 token129 prompt129", "session129"],
    ),
    (
        ("learning129 model129 token129 prompt129 session129 library129", 6),
        ["learning129", "model129", "token129", "prompt129", "session129", "library129"],
    ),
    (
        ("learning129 model129 token129 prompt129 session129 library129", 10),
        ["learning129", "model129", "token129", "prompt129", "session129", "library129"],
    ),
    (
        ("learning129 model129 token129 prompt129 session129 library129", 18),
        ["learning129", "model129 token129", "prompt129", "session129", "library129"],
    ),
    (
        ("learning129 model129 token129 prompt129 session129 library129", 28),
        ["learning129 model129", "token129 prompt129", "session129 library129"],
    ),
    (
        ("model129 token129 prompt129 session129 library129 service129", 6),
        ["model129", "token129", "prompt129", "session129", "library129", "service129"],
    ),
    (
        ("model129 token129 prompt129 session129 library129 service129", 10),
        ["model129", "token129", "prompt129", "session129", "library129", "service129"],
    ),
    (
        ("model129 token129 prompt129 session129 library129 service129", 18),
        ["model129 token129", "prompt129", "session129", "library129", "service129"],
    ),
    (
        ("model129 token129 prompt129 session129 library129 service129", 28),
        ["model129 token129 prompt129", "session129 library129", "service129"],
    ),
    (
        ("token129 prompt129 session129 library129 service129 gateway129", 6),
        ["token129", "prompt129", "session129", "library129", "service129", "gateway129"],
    ),
    (
        ("token129 prompt129 session129 library129 service129 gateway129", 10),
        ["token129", "prompt129", "session129", "library129", "service129", "gateway129"],
    ),
    (
        ("token129 prompt129 session129 library129 service129 gateway129", 18),
        ["token129 prompt129", "session129", "library129", "service129", "gateway129"],
    ),
    (
        ("token129 prompt129 session129 library129 service129 gateway129", 28),
        ["token129 prompt129", "session129 library129", "service129 gateway129"],
    ),
    (
        ("prompt129 session129 library129 service129 gateway129 storage129", 6),
        ["prompt129", "session129", "library129", "service129", "gateway129", "storage129"],
    ),
    (
        ("prompt129 session129 library129 service129 gateway129 storage129", 10),
        ["prompt129", "session129", "library129", "service129", "gateway129", "storage129"],
    ),
    (
        ("prompt129 session129 library129 service129 gateway129 storage129", 18),
        ["prompt129", "session129", "library129", "service129", "gateway129", "storage129"],
    ),
    (
        ("prompt129 session129 library129 service129 gateway129 storage129", 28),
        ["prompt129 session129", "library129 service129", "gateway129 storage129"],
    ),
    (
        ("session129 library129 service129 gateway129 storage129 network129", 6),
        ["session129", "library129", "service129", "gateway129", "storage129", "network129"],
    ),
    (
        ("session129 library129 service129 gateway129 storage129 network129", 10),
        ["session129", "library129", "service129", "gateway129", "storage129", "network129"],
    ),
    (
        ("session129 library129 service129 gateway129 storage129 network129", 18),
        ["session129", "library129", "service129", "gateway129", "storage129", "network129"],
    ),
    (
        ("session129 library129 service129 gateway129 storage129 network129", 28),
        ["session129 library129", "service129 gateway129", "storage129 network129"],
    ),
    (
        ("library129 service129 gateway129 storage129 network129 latency129", 6),
        ["library129", "service129", "gateway129", "storage129", "network129", "latency129"],
    ),
    (
        ("library129 service129 gateway129 storage129 network129 latency129", 10),
        ["library129", "service129", "gateway129", "storage129", "network129", "latency129"],
    ),
    (
        ("library129 service129 gateway129 storage129 network129 latency129", 18),
        ["library129", "service129", "gateway129", "storage129", "network129", "latency129"],
    ),
    (
        ("library129 service129 gateway129 storage129 network129 latency129", 28),
        ["library129 service129", "gateway129 storage129", "network129 latency129"],
    ),
    (
        ("service129 gateway129 storage129 network129 latency129 buffer129", 6),
        ["service129", "gateway129", "storage129", "network129", "latency129", "buffer129"],
    ),
    (
        ("service129 gateway129 storage129 network129 latency129 buffer129", 10),
        ["service129", "gateway129", "storage129", "network129", "latency129", "buffer129"],
    ),
    (
        ("service129 gateway129 storage129 network129 latency129 buffer129", 18),
        ["service129", "gateway129", "storage129", "network129", "latency129", "buffer129"],
    ),
    (
        ("service129 gateway129 storage129 network129 latency129 buffer129", 28),
        ["service129 gateway129", "storage129 network129", "latency129 buffer129"],
    ),
    (
        ("gateway129 storage129 network129 latency129 buffer129 queue129", 6),
        ["gateway129", "storage129", "network129", "latency129", "buffer129", "queue129"],
    ),
    (
        ("gateway129 storage129 network129 latency129 buffer129 queue129", 10),
        ["gateway129", "storage129", "network129", "latency129", "buffer129", "queue129"],
    ),
    (
        ("gateway129 storage129 network129 latency129 buffer129 queue129", 18),
        ["gateway129", "storage129", "network129", "latency129", "buffer129 queue129"],
    ),
    (
        ("gateway129 storage129 network129 latency129 buffer129 queue129", 28),
        ["gateway129 storage129", "network129 latency129", "buffer129 queue129"],
    ),
    (
        ("storage129 network129 latency129 buffer129 queue129 worker129", 6),
        ["storage129", "network129", "latency129", "buffer129", "queue129", "worker129"],
    ),
    (
        ("storage129 network129 latency129 buffer129 queue129 worker129", 10),
        ["storage129", "network129", "latency129", "buffer129", "queue129", "worker129"],
    ),
    (
        ("storage129 network129 latency129 buffer129 queue129 worker129", 18),
        ["storage129", "network129", "latency129", "buffer129 queue129", "worker129"],
    ),
    (
        ("storage129 network129 latency129 buffer129 queue129 worker129", 28),
        ["storage129 network129", "latency129 buffer129", "queue129 worker129"],
    ),
    (
        ("network129 latency129 buffer129 queue129 worker129 kernel129", 6),
        ["network129", "latency129", "buffer129", "queue129", "worker129", "kernel129"],
    ),
    (
        ("network129 latency129 buffer129 queue129 worker129 kernel129", 10),
        ["network129", "latency129", "buffer129", "queue129", "worker129", "kernel129"],
    ),
    (
        ("network129 latency129 buffer129 queue129 worker129 kernel129", 18),
        ["network129", "latency129", "buffer129 queue129", "worker129", "kernel129"],
    ),
    (
        ("network129 latency129 buffer129 queue129 worker129 kernel129", 28),
        ["network129 latency129", "buffer129 queue129 worker129", "kernel129"],
    ),
    (
        ("latency129 buffer129 queue129 worker129 kernel129 signal129", 6),
        ["latency129", "buffer129", "queue129", "worker129", "kernel129", "signal129"],
    ),
    (
        ("latency129 buffer129 queue129 worker129 kernel129 signal129", 10),
        ["latency129", "buffer129", "queue129", "worker129", "kernel129", "signal129"],
    ),
    (
        ("latency129 buffer129 queue129 worker129 kernel129 signal129", 18),
        ["latency129", "buffer129 queue129", "worker129", "kernel129", "signal129"],
    ),
    (
        ("latency129 buffer129 queue129 worker129 kernel129 signal129", 28),
        ["latency129 buffer129", "queue129 worker129 kernel129", "signal129"],
    ),
    (
        ("buffer129 queue129 worker129 kernel129 signal129 packet129", 6),
        ["buffer129", "queue129", "worker129", "kernel129", "signal129", "packet129"],
    ),
    (
        ("buffer129 queue129 worker129 kernel129 signal129 packet129", 10),
        ["buffer129", "queue129", "worker129", "kernel129", "signal129", "packet129"],
    ),
    (
        ("buffer129 queue129 worker129 kernel129 signal129 packet129", 18),
        ["buffer129 queue129", "worker129", "kernel129", "signal129", "packet129"],
    ),
    (
        ("buffer129 queue129 worker129 kernel129 signal129 packet129", 28),
        ["buffer129 queue129 worker129", "kernel129 signal129", "packet129"],
    ),
    (
        ("queue129 worker129 kernel129 signal129 packet129 router129", 6),
        ["queue129", "worker129", "kernel129", "signal129", "packet129", "router129"],
    ),
    (
        ("queue129 worker129 kernel129 signal129 packet129 router129", 10),
        ["queue129", "worker129", "kernel129", "signal129", "packet129", "router129"],
    ),
    (
        ("queue129 worker129 kernel129 signal129 packet129 router129", 18),
        ["queue129 worker129", "kernel129", "signal129", "packet129", "router129"],
    ),
    (
        ("queue129 worker129 kernel129 signal129 packet129 router129", 28),
        ["queue129 worker129 kernel129", "signal129 packet129", "router129"],
    ),
    (
        ("worker129 kernel129 signal129 packet129 router129 cluster129", 6),
        ["worker129", "kernel129", "signal129", "packet129", "router129", "cluster129"],
    ),
    (
        ("worker129 kernel129 signal129 packet129 router129 cluster129", 10),
        ["worker129", "kernel129", "signal129", "packet129", "router129", "cluster129"],
    ),
    (
        ("worker129 kernel129 signal129 packet129 router129 cluster129", 18),
        ["worker129", "kernel129", "signal129", "packet129", "router129", "cluster129"],
    ),
    (
        ("worker129 kernel129 signal129 packet129 router129 cluster129", 28),
        ["worker129 kernel129", "signal129 packet129", "router129 cluster129"],
    ),
    (
        ("kernel129 signal129 packet129 router129 cluster129 mirror129", 6),
        ["kernel129", "signal129", "packet129", "router129", "cluster129", "mirror129"],
    ),
    (
        ("kernel129 signal129 packet129 router129 cluster129 mirror129", 10),
        ["kernel129", "signal129", "packet129", "router129", "cluster129", "mirror129"],
    ),
    (
        ("kernel129 signal129 packet129 router129 cluster129 mirror129", 18),
        ["kernel129", "signal129", "packet129", "router129", "cluster129", "mirror129"],
    ),
    (
        ("kernel129 signal129 packet129 router129 cluster129 mirror129", 28),
        ["kernel129 signal129", "packet129 router129", "cluster129 mirror129"],
    ),
    (
        ("signal129 packet129 router129 cluster129 mirror129 filter129", 6),
        ["signal129", "packet129", "router129", "cluster129", "mirror129", "filter129"],
    ),
    (
        ("signal129 packet129 router129 cluster129 mirror129 filter129", 10),
        ["signal129", "packet129", "router129", "cluster129", "mirror129", "filter129"],
    ),
    (
        ("signal129 packet129 router129 cluster129 mirror129 filter129", 18),
        ["signal129", "packet129", "router129", "cluster129", "mirror129", "filter129"],
    ),
    (
        ("signal129 packet129 router129 cluster129 mirror129 filter129", 28),
        ["signal129 packet129", "router129 cluster129", "mirror129 filter129"],
    ),
    (
        ("packet129 router129 cluster129 mirror129 filter129 ranking129", 6),
        ["packet129", "router129", "cluster129", "mirror129", "filter129", "ranking129"],
    ),
    (
        ("packet129 router129 cluster129 mirror129 filter129 ranking129", 10),
        ["packet129", "router129", "cluster129", "mirror129", "filter129", "ranking129"],
    ),
    (
        ("packet129 router129 cluster129 mirror129 filter129 ranking129", 18),
        ["packet129", "router129", "cluster129", "mirror129", "filter129", "ranking129"],
    ),
    (
        ("packet129 router129 cluster129 mirror129 filter129 ranking129", 28),
        ["packet129 router129", "cluster129 mirror129", "filter129 ranking129"],
    ),
    (
        ("router129 cluster129 mirror129 filter129 ranking129 encoding129", 6),
        ["router129", "cluster129", "mirror129", "filter129", "ranking129", "encoding129"],
    ),
    (
        ("router129 cluster129 mirror129 filter129 ranking129 encoding129", 10),
        ["router129", "cluster129", "mirror129", "filter129", "ranking129", "encoding129"],
    ),
    (
        ("router129 cluster129 mirror129 filter129 ranking129 encoding129", 18),
        ["router129", "cluster129", "mirror129", "filter129", "ranking129", "encoding129"],
    ),
    (
        ("router129 cluster129 mirror129 filter129 ranking129 encoding129", 28),
        ["router129 cluster129", "mirror129 filter129", "ranking129 encoding129"],
    ),
    (
        ("cluster129 mirror129 filter129 ranking129 encoding129 mapping129", 6),
        ["cluster129", "mirror129", "filter129", "ranking129", "encoding129", "mapping129"],
    ),
    (
        ("cluster129 mirror129 filter129 ranking129 encoding129 mapping129", 10),
        ["cluster129", "mirror129", "filter129", "ranking129", "encoding129", "mapping129"],
    ),
    (
        ("cluster129 mirror129 filter129 ranking129 encoding129 mapping129", 18),
        ["cluster129", "mirror129", "filter129", "ranking129", "encoding129", "mapping129"],
    ),
    (
        ("cluster129 mirror129 filter129 ranking129 encoding129 mapping129", 28),
        ["cluster129 mirror129", "filter129 ranking129", "encoding129 mapping129"],
    ),
    (
        ("mirror129 filter129 ranking129 encoding129 mapping129 record129", 6),
        ["mirror129", "filter129", "ranking129", "encoding129", "mapping129", "record129"],
    ),
    (
        ("mirror129 filter129 ranking129 encoding129 mapping129 record129", 10),
        ["mirror129", "filter129", "ranking129", "encoding129", "mapping129", "record129"],
    ),
    (
        ("mirror129 filter129 ranking129 encoding129 mapping129 record129", 18),
        ["mirror129", "filter129", "ranking129", "encoding129", "mapping129", "record129"],
    ),
    (
        ("mirror129 filter129 ranking129 encoding129 mapping129 record129", 28),
        ["mirror129 filter129", "ranking129 encoding129", "mapping129 record129"],
    ),
    (
        ("filter129 ranking129 encoding129 mapping129 record129 candle129", 6),
        ["filter129", "ranking129", "encoding129", "mapping129", "record129", "candle129"],
    ),
    (
        ("filter129 ranking129 encoding129 mapping129 record129 candle129", 10),
        ["filter129", "ranking129", "encoding129", "mapping129", "record129", "candle129"],
    ),
    (
        ("filter129 ranking129 encoding129 mapping129 record129 candle129", 18),
        ["filter129", "ranking129", "encoding129", "mapping129", "record129", "candle129"],
    ),
    (
        ("filter129 ranking129 encoding129 mapping129 record129 candle129", 28),
        ["filter129 ranking129", "encoding129 mapping129", "record129 candle129"],
    ),
    (
        ("ranking129 encoding129 mapping129 record129 candle129 thread129", 6),
        ["ranking129", "encoding129", "mapping129", "record129", "candle129", "thread129"],
    ),
    (
        ("ranking129 encoding129 mapping129 record129 candle129 thread129", 10),
        ["ranking129", "encoding129", "mapping129", "record129", "candle129", "thread129"],
    ),
    (
        ("ranking129 encoding129 mapping129 record129 candle129 thread129", 18),
        ["ranking129", "encoding129", "mapping129", "record129", "candle129", "thread129"],
    ),
    (
        ("ranking129 encoding129 mapping129 record129 candle129 thread129", 28),
        ["ranking129 encoding129", "mapping129 record129", "candle129 thread129"],
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
