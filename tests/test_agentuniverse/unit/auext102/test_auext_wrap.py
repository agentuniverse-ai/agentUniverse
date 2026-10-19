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
        ("round 102: the quick brown fox jumps over the lazy dog", 4),
        ["round", "102:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", 8),
        ["round", "102: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", 12),
        ["round 102:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", 16),
        ["round 102: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", 24),
        ["round 102: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 102: the quick brown fox jumps over the lazy dog", 32),
        ["round 102: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", 4),
        ["round", "102:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", 8),
        ["round", "102:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", 12),
        ["round 102:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", 16),
        ["round 102:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", 24),
        ["round 102: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 102: agentuniverse is a framework for multi agents", 32),
        ["round 102: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", 4),
        ["round", "102:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", 8),
        ["round", "102:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", 12),
        ["round 102:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", 16),
        ["round 102:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", 24),
        ["round 102: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 102: knowledge stored as vectors enables retrieval", 32),
        ["round 102: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 102: the processor reads the record then stops", 4),
        ["round", "102:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 102: the processor reads the record then stops", 8),
        ["round", "102: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 102: the processor reads the record then stops", 12),
        ["round 102:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 102: the processor reads the record then stops", 16),
        ["round 102: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 102: the processor reads the record then stops", 24),
        ["round 102: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 102: the processor reads the record then stops", 32),
        ["round 102: the processor reads", "the record then stops"],
    ),
    (
        ("round 102: a worker pulls the next task from the queue", 4),
        ["round", "102:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 102: a worker pulls the next task from the queue", 8),
        ["round", "102: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 102: a worker pulls the next task from the queue", 12),
        ["round 102: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 102: a worker pulls the next task from the queue", 16),
        ["round 102: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 102: a worker pulls the next task from the queue", 24),
        ["round 102: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 102: a worker pulls the next task from the queue", 32),
        ["round 102: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 102: signals travel through the network layer", 4),
        ["round", "102:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 102: signals travel through the network layer", 8),
        ["round", "102:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 102: signals travel through the network layer", 12),
        ["round 102:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 102: signals travel through the network layer", 16),
        ["round 102:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 102: signals travel through the network layer", 24),
        ["round 102: signals", "travel through the", "network layer"],
    ),
    (
        ("round 102: signals travel through the network layer", 32),
        ["round 102: signals travel", "through the network layer"],
    ),
    (
        ("round 102: the gateway routes each request by policy", 4),
        ["round", "102:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 102: the gateway routes each request by policy", 8),
        ["round", "102: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 102: the gateway routes each request by policy", 12),
        ["round 102:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 102: the gateway routes each request by policy", 16),
        ["round 102: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 102: the gateway routes each request by policy", 24),
        ["round 102: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 102: the gateway routes each request by policy", 32),
        ["round 102: the gateway routes", "each request by policy"],
    ),
    (
        ("round 102: memory grows until the buffer is full", 4),
        ["round", "102:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 102: memory grows until the buffer is full", 8),
        ["round", "102:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 102: memory grows until the buffer is full", 12),
        ["round 102:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 102: memory grows until the buffer is full", 16),
        ["round 102:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 102: memory grows until the buffer is full", 24), ["round 102: memory grows", "until the buffer is full"]),
    (("round 102: memory grows until the buffer is full", 32), ["round 102: memory grows until", "the buffer is full"]),
    (
        ("round 102: the cluster mirrors every packet twice", 4),
        ["round", "102:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 102: the cluster mirrors every packet twice", 8),
        ["round", "102: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 102: the cluster mirrors every packet twice", 12),
        ["round 102:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 102: the cluster mirrors every packet twice", 16),
        ["round 102: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 102: the cluster mirrors every packet twice", 24),
        ["round 102: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 102: the cluster mirrors every packet twice", 32),
        ["round 102: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", 4),
        ["round", "102:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", 8),
        ["round", "102:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", 12),
        ["round 102:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", 16),
        ["round 102:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", 24),
        ["round 102: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 102: ranking uses tokens learned from the corpus", 32),
        ["round 102: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 102: a long session ends when the candle dies", 4),
        ["round", "102:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 102: a long session ends when the candle dies", 8),
        ["round", "102: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 102: a long session ends when the candle dies", 12),
        ["round 102: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 102: a long session ends when the candle dies", 16),
        ["round 102: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 102: a long session ends when the candle dies", 24),
        ["round 102: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 102: a long session ends when the candle dies", 32),
        ["round 102: a long session ends", "when the candle dies"],
    ),
    (
        ("round 102: encode the prompt then map the result", 4),
        ["round", "102:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 102: encode the prompt then map the result", 8),
        ["round", "102:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 102: encode the prompt then map the result", 12),
        ["round 102:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 102: encode the prompt then map the result", 16),
        ["round 102:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 102: encode the prompt then map the result", 24),
        ["round 102: encode the", "prompt then map the", "result"],
    ),
    (("round 102: encode the prompt then map the result", 32), ["round 102: encode the prompt", "then map the result"]),
    (
        ("round 102: the kernel wakes the worker at dawn", 4),
        ["round", "102:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 102: the kernel wakes the worker at dawn", 8),
        ["round", "102: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 102: the kernel wakes the worker at dawn", 12),
        ["round 102:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 102: the kernel wakes the worker at dawn", 16), ["round 102: the", "kernel wakes the", "worker at dawn"]),
    (("round 102: the kernel wakes the worker at dawn", 24), ["round 102: the kernel", "wakes the worker at dawn"]),
    (("round 102: the kernel wakes the worker at dawn", 32), ["round 102: the kernel wakes the", "worker at dawn"]),
    (
        ("round 102: service latency drops after the patch", 4),
        ["round", "102:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 102: service latency drops after the patch", 8),
        ["round", "102:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 102: service latency drops after the patch", 12),
        ["round 102:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 102: service latency drops after the patch", 16),
        ["round 102:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 102: service latency drops after the patch", 24),
        ["round 102: service", "latency drops after the", "patch"],
    ),
    (("round 102: service latency drops after the patch", 32), ["round 102: service latency drops", "after the patch"]),
    (
        ("round 102: the library caches every vector it sees", 4),
        ["round", "102:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 102: the library caches every vector it sees", 8),
        ["round", "102: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 102: the library caches every vector it sees", 12),
        ["round 102:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 102: the library caches every vector it sees", 16),
        ["round 102: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 102: the library caches every vector it sees", 24),
        ["round 102: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 102: the library caches every vector it sees", 32),
        ["round 102: the library caches", "every vector it sees"],
    ),
    (
        ("round 102: agents argue then the debate resolves", 4),
        ["round", "102:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 102: agents argue then the debate resolves", 8),
        ["round", "102:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 102: agents argue then the debate resolves", 12),
        ["round 102:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 102: agents argue then the debate resolves", 16),
        ["round 102:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 102: agents argue then the debate resolves", 24), ["round 102: agents argue", "then the debate resolves"]),
    (("round 102: agents argue then the debate resolves", 32), ["round 102: agents argue then the", "debate resolves"]),
    (
        ("round 102: the filter keeps only strong matches", 4),
        ["round", "102:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 102: the filter keeps only strong matches", 8),
        ["round", "102: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 102: the filter keeps only strong matches", 12),
        ["round 102:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 102: the filter keeps only strong matches", 16),
        ["round 102: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 102: the filter keeps only strong matches", 24),
        ["round 102: the filter", "keeps only strong", "matches"],
    ),
    (("round 102: the filter keeps only strong matches", 32), ["round 102: the filter keeps only", "strong matches"]),
    (
        ("round 102: the model answers with a short reply", 4),
        ["round", "102:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 102: the model answers with a short reply", 8),
        ["round", "102: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 102: the model answers with a short reply", 12),
        ["round 102:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 102: the model answers with a short reply", 16),
        ["round 102: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 102: the model answers with a short reply", 24),
        ["round 102: the model", "answers with a short", "reply"],
    ),
    (("round 102: the model answers with a short reply", 32), ["round 102: the model answers", "with a short reply"]),
    (
        ("round 102: the recorder stores the reasoning trace", 4),
        ["round", "102:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 102: the recorder stores the reasoning trace", 8),
        ["round", "102: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 102: the recorder stores the reasoning trace", 12),
        ["round 102:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 102: the recorder stores the reasoning trace", 16),
        ["round 102: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 102: the recorder stores the reasoning trace", 24),
        ["round 102: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 102: the recorder stores the reasoning trace", 32),
        ["round 102: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 102: the angel watches the processor run", 4),
        ["round", "102:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 102: the angel watches the processor run", 8),
        ["round", "102: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 102: the angel watches the processor run", 12),
        ["round 102:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 102: the angel watches the processor run", 16),
        ["round 102: the", "angel watches", "the processor", "run"],
    ),
    (("round 102: the angel watches the processor run", 24), ["round 102: the angel", "watches the processor", "run"]),
    (("round 102: the angel watches the processor run", 32), ["round 102: the angel watches the", "processor run"]),
    (
        ("round 102: angle of the vector decides the match", 4),
        ["round", "102:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 102: angle of the vector decides the match", 8),
        ["round", "102:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 102: angle of the vector decides the match", 12),
        ["round 102:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 102: angle of the vector decides the match", 16),
        ["round 102: angle", "of the vector", "decides the", "match"],
    ),
    (("round 102: angle of the vector decides the match", 24), ["round 102: angle of the", "vector decides the match"]),
    (("round 102: angle of the vector decides the match", 32), ["round 102: angle of the vector", "decides the match"]),
    (
        ("round 102: the candle burns twice as long at night", 4),
        ["round", "102:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 102: the candle burns twice as long at night", 8),
        ["round", "102: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 102: the candle burns twice as long at night", 12),
        ["round 102:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 102: the candle burns twice as long at night", 16),
        ["round 102: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 102: the candle burns twice as long at night", 24),
        ["round 102: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 102: the candle burns twice as long at night", 32),
        ["round 102: the candle burns", "twice as long at night"],
    ),
    (
        ("round 102: a mirror of the universe in one line", 4),
        ["round", "102:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 102: a mirror of the universe in one line", 8),
        ["round", "102: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 102: a mirror of the universe in one line", 12),
        ["round 102: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 102: a mirror of the universe in one line", 16),
        ["round 102: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 102: a mirror of the universe in one line", 24), ["round 102: a mirror of", "the universe in one line"]),
    (("round 102: a mirror of the universe in one line", 32), ["round 102: a mirror of the", "universe in one line"]),
    (
        ("round 102: the queue drains before the storm", 4),
        ["round", "102:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 102: the queue drains before the storm", 8),
        ["round", "102: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 102: the queue drains before the storm", 12),
        ["round 102:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 102: the queue drains before the storm", 16), ["round 102: the", "queue drains", "before the storm"]),
    (("round 102: the queue drains before the storm", 24), ["round 102: the queue", "drains before the storm"]),
    (("round 102: the queue drains before the storm", 32), ["round 102: the queue drains", "before the storm"]),
    (
        ("kitten102 sitting102 agent102 angle102 universe102 memory102", 6),
        ["kitten102", "sitting102", "agent102", "angle102", "universe102", "memory102"],
    ),
    (
        ("kitten102 sitting102 agent102 angle102 universe102 memory102", 10),
        ["kitten102", "sitting102", "agent102", "angle102", "universe102", "memory102"],
    ),
    (
        ("kitten102 sitting102 agent102 angle102 universe102 memory102", 18),
        ["kitten102", "sitting102", "agent102 angle102", "universe102", "memory102"],
    ),
    (
        ("kitten102 sitting102 agent102 angle102 universe102 memory102", 28),
        ["kitten102 sitting102", "agent102 angle102", "universe102 memory102"],
    ),
    (
        ("sitting102 agent102 angle102 universe102 memory102 stream102", 6),
        ["sitting102", "agent102", "angle102", "universe102", "memory102", "stream102"],
    ),
    (
        ("sitting102 agent102 angle102 universe102 memory102 stream102", 10),
        ["sitting102", "agent102", "angle102", "universe102", "memory102", "stream102"],
    ),
    (
        ("sitting102 agent102 angle102 universe102 memory102 stream102", 18),
        ["sitting102", "agent102 angle102", "universe102", "memory102", "stream102"],
    ),
    (
        ("sitting102 agent102 angle102 universe102 memory102 stream102", 28),
        ["sitting102 agent102 angle102", "universe102 memory102", "stream102"],
    ),
    (
        ("agent102 angle102 universe102 memory102 stream102 context102", 6),
        ["agent102", "angle102", "universe102", "memory102", "stream102", "context102"],
    ),
    (
        ("agent102 angle102 universe102 memory102 stream102 context102", 10),
        ["agent102", "angle102", "universe102", "memory102", "stream102", "context102"],
    ),
    (
        ("agent102 angle102 universe102 memory102 stream102 context102", 18),
        ["agent102 angle102", "universe102", "memory102", "stream102", "context102"],
    ),
    (
        ("agent102 angle102 universe102 memory102 stream102 context102", 28),
        ["agent102 angle102", "universe102 memory102", "stream102 context102"],
    ),
    (
        ("angle102 universe102 memory102 stream102 context102 knowledge102", 6),
        ["angle102", "universe102", "memory102", "stream102", "context102", "knowledge102"],
    ),
    (
        ("angle102 universe102 memory102 stream102 context102 knowledge102", 10),
        ["angle102", "universe102", "memory102", "stream102", "context102", "knowledge102"],
    ),
    (
        ("angle102 universe102 memory102 stream102 context102 knowledge102", 18),
        ["angle102", "universe102", "memory102", "stream102", "context102", "knowledge102"],
    ),
    (
        ("angle102 universe102 memory102 stream102 context102 knowledge102", 28),
        ["angle102 universe102", "memory102 stream102", "context102 knowledge102"],
    ),
    (
        ("universe102 memory102 stream102 context102 knowledge102 vector102", 6),
        ["universe102", "memory102", "stream102", "context102", "knowledge102", "vector102"],
    ),
    (
        ("universe102 memory102 stream102 context102 knowledge102 vector102", 10),
        ["universe102", "memory102", "stream102", "context102", "knowledge102", "vector102"],
    ),
    (
        ("universe102 memory102 stream102 context102 knowledge102 vector102", 18),
        ["universe102", "memory102", "stream102", "context102", "knowledge102", "vector102"],
    ),
    (
        ("universe102 memory102 stream102 context102 knowledge102 vector102", 28),
        ["universe102 memory102", "stream102 context102", "knowledge102 vector102"],
    ),
    (
        ("memory102 stream102 context102 knowledge102 vector102 processor102", 6),
        ["memory102", "stream102", "context102", "knowledge102", "vector102", "processor102"],
    ),
    (
        ("memory102 stream102 context102 knowledge102 vector102 processor102", 10),
        ["memory102", "stream102", "context102", "knowledge102", "vector102", "processor102"],
    ),
    (
        ("memory102 stream102 context102 knowledge102 vector102 processor102", 18),
        ["memory102", "stream102", "context102", "knowledge102", "vector102", "processor102"],
    ),
    (
        ("memory102 stream102 context102 knowledge102 vector102 processor102", 28),
        ["memory102 stream102", "context102 knowledge102", "vector102 processor102"],
    ),
    (
        ("stream102 context102 knowledge102 vector102 processor102 reasoning102", 6),
        ["stream102", "context102", "knowledge102", "vector102", "processor102", "reasoning102"],
    ),
    (
        ("stream102 context102 knowledge102 vector102 processor102 reasoning102", 10),
        ["stream102", "context102", "knowledge102", "vector102", "processor102", "reasoning102"],
    ),
    (
        ("stream102 context102 knowledge102 vector102 processor102 reasoning102", 18),
        ["stream102", "context102", "knowledge102", "vector102", "processor102", "reasoning102"],
    ),
    (
        ("stream102 context102 knowledge102 vector102 processor102 reasoning102", 28),
        ["stream102 context102", "knowledge102 vector102", "processor102 reasoning102"],
    ),
    (
        ("context102 knowledge102 vector102 processor102 reasoning102 machine102", 6),
        ["context102", "knowledge102", "vector102", "processor102", "reasoning102", "machine102"],
    ),
    (
        ("context102 knowledge102 vector102 processor102 reasoning102 machine102", 10),
        ["context102", "knowledge102", "vector102", "processor102", "reasoning102", "machine102"],
    ),
    (
        ("context102 knowledge102 vector102 processor102 reasoning102 machine102", 18),
        ["context102", "knowledge102", "vector102", "processor102", "reasoning102", "machine102"],
    ),
    (
        ("context102 knowledge102 vector102 processor102 reasoning102 machine102", 28),
        ["context102 knowledge102", "vector102 processor102", "reasoning102 machine102"],
    ),
    (
        ("knowledge102 vector102 processor102 reasoning102 machine102 learning102", 6),
        ["knowledge102", "vector102", "processor102", "reasoning102", "machine102", "learning102"],
    ),
    (
        ("knowledge102 vector102 processor102 reasoning102 machine102 learning102", 10),
        ["knowledge102", "vector102", "processor102", "reasoning102", "machine102", "learning102"],
    ),
    (
        ("knowledge102 vector102 processor102 reasoning102 machine102 learning102", 18),
        ["knowledge102", "vector102", "processor102", "reasoning102", "machine102", "learning102"],
    ),
    (
        ("knowledge102 vector102 processor102 reasoning102 machine102 learning102", 28),
        ["knowledge102 vector102", "processor102 reasoning102", "machine102 learning102"],
    ),
    (
        ("vector102 processor102 reasoning102 machine102 learning102 model102", 6),
        ["vector102", "processor102", "reasoning102", "machine102", "learning102", "model102"],
    ),
    (
        ("vector102 processor102 reasoning102 machine102 learning102 model102", 10),
        ["vector102", "processor102", "reasoning102", "machine102", "learning102", "model102"],
    ),
    (
        ("vector102 processor102 reasoning102 machine102 learning102 model102", 18),
        ["vector102", "processor102", "reasoning102", "machine102", "learning102", "model102"],
    ),
    (
        ("vector102 processor102 reasoning102 machine102 learning102 model102", 28),
        ["vector102 processor102", "reasoning102 machine102", "learning102 model102"],
    ),
    (
        ("processor102 reasoning102 machine102 learning102 model102 token102", 6),
        ["processor102", "reasoning102", "machine102", "learning102", "model102", "token102"],
    ),
    (
        ("processor102 reasoning102 machine102 learning102 model102 token102", 10),
        ["processor102", "reasoning102", "machine102", "learning102", "model102", "token102"],
    ),
    (
        ("processor102 reasoning102 machine102 learning102 model102 token102", 18),
        ["processor102", "reasoning102", "machine102", "learning102", "model102 token102"],
    ),
    (
        ("processor102 reasoning102 machine102 learning102 model102 token102", 28),
        ["processor102 reasoning102", "machine102 learning102", "model102 token102"],
    ),
    (
        ("reasoning102 machine102 learning102 model102 token102 prompt102", 6),
        ["reasoning102", "machine102", "learning102", "model102", "token102", "prompt102"],
    ),
    (
        ("reasoning102 machine102 learning102 model102 token102 prompt102", 10),
        ["reasoning102", "machine102", "learning102", "model102", "token102", "prompt102"],
    ),
    (
        ("reasoning102 machine102 learning102 model102 token102 prompt102", 18),
        ["reasoning102", "machine102", "learning102", "model102 token102", "prompt102"],
    ),
    (
        ("reasoning102 machine102 learning102 model102 token102 prompt102", 28),
        ["reasoning102 machine102", "learning102 model102", "token102 prompt102"],
    ),
    (
        ("machine102 learning102 model102 token102 prompt102 session102", 6),
        ["machine102", "learning102", "model102", "token102", "prompt102", "session102"],
    ),
    (
        ("machine102 learning102 model102 token102 prompt102 session102", 10),
        ["machine102", "learning102", "model102", "token102", "prompt102", "session102"],
    ),
    (
        ("machine102 learning102 model102 token102 prompt102 session102", 18),
        ["machine102", "learning102", "model102 token102", "prompt102", "session102"],
    ),
    (
        ("machine102 learning102 model102 token102 prompt102 session102", 28),
        ["machine102 learning102", "model102 token102 prompt102", "session102"],
    ),
    (
        ("learning102 model102 token102 prompt102 session102 library102", 6),
        ["learning102", "model102", "token102", "prompt102", "session102", "library102"],
    ),
    (
        ("learning102 model102 token102 prompt102 session102 library102", 10),
        ["learning102", "model102", "token102", "prompt102", "session102", "library102"],
    ),
    (
        ("learning102 model102 token102 prompt102 session102 library102", 18),
        ["learning102", "model102 token102", "prompt102", "session102", "library102"],
    ),
    (
        ("learning102 model102 token102 prompt102 session102 library102", 28),
        ["learning102 model102", "token102 prompt102", "session102 library102"],
    ),
    (
        ("model102 token102 prompt102 session102 library102 service102", 6),
        ["model102", "token102", "prompt102", "session102", "library102", "service102"],
    ),
    (
        ("model102 token102 prompt102 session102 library102 service102", 10),
        ["model102", "token102", "prompt102", "session102", "library102", "service102"],
    ),
    (
        ("model102 token102 prompt102 session102 library102 service102", 18),
        ["model102 token102", "prompt102", "session102", "library102", "service102"],
    ),
    (
        ("model102 token102 prompt102 session102 library102 service102", 28),
        ["model102 token102 prompt102", "session102 library102", "service102"],
    ),
    (
        ("token102 prompt102 session102 library102 service102 gateway102", 6),
        ["token102", "prompt102", "session102", "library102", "service102", "gateway102"],
    ),
    (
        ("token102 prompt102 session102 library102 service102 gateway102", 10),
        ["token102", "prompt102", "session102", "library102", "service102", "gateway102"],
    ),
    (
        ("token102 prompt102 session102 library102 service102 gateway102", 18),
        ["token102 prompt102", "session102", "library102", "service102", "gateway102"],
    ),
    (
        ("token102 prompt102 session102 library102 service102 gateway102", 28),
        ["token102 prompt102", "session102 library102", "service102 gateway102"],
    ),
    (
        ("prompt102 session102 library102 service102 gateway102 storage102", 6),
        ["prompt102", "session102", "library102", "service102", "gateway102", "storage102"],
    ),
    (
        ("prompt102 session102 library102 service102 gateway102 storage102", 10),
        ["prompt102", "session102", "library102", "service102", "gateway102", "storage102"],
    ),
    (
        ("prompt102 session102 library102 service102 gateway102 storage102", 18),
        ["prompt102", "session102", "library102", "service102", "gateway102", "storage102"],
    ),
    (
        ("prompt102 session102 library102 service102 gateway102 storage102", 28),
        ["prompt102 session102", "library102 service102", "gateway102 storage102"],
    ),
    (
        ("session102 library102 service102 gateway102 storage102 network102", 6),
        ["session102", "library102", "service102", "gateway102", "storage102", "network102"],
    ),
    (
        ("session102 library102 service102 gateway102 storage102 network102", 10),
        ["session102", "library102", "service102", "gateway102", "storage102", "network102"],
    ),
    (
        ("session102 library102 service102 gateway102 storage102 network102", 18),
        ["session102", "library102", "service102", "gateway102", "storage102", "network102"],
    ),
    (
        ("session102 library102 service102 gateway102 storage102 network102", 28),
        ["session102 library102", "service102 gateway102", "storage102 network102"],
    ),
    (
        ("library102 service102 gateway102 storage102 network102 latency102", 6),
        ["library102", "service102", "gateway102", "storage102", "network102", "latency102"],
    ),
    (
        ("library102 service102 gateway102 storage102 network102 latency102", 10),
        ["library102", "service102", "gateway102", "storage102", "network102", "latency102"],
    ),
    (
        ("library102 service102 gateway102 storage102 network102 latency102", 18),
        ["library102", "service102", "gateway102", "storage102", "network102", "latency102"],
    ),
    (
        ("library102 service102 gateway102 storage102 network102 latency102", 28),
        ["library102 service102", "gateway102 storage102", "network102 latency102"],
    ),
    (
        ("service102 gateway102 storage102 network102 latency102 buffer102", 6),
        ["service102", "gateway102", "storage102", "network102", "latency102", "buffer102"],
    ),
    (
        ("service102 gateway102 storage102 network102 latency102 buffer102", 10),
        ["service102", "gateway102", "storage102", "network102", "latency102", "buffer102"],
    ),
    (
        ("service102 gateway102 storage102 network102 latency102 buffer102", 18),
        ["service102", "gateway102", "storage102", "network102", "latency102", "buffer102"],
    ),
    (
        ("service102 gateway102 storage102 network102 latency102 buffer102", 28),
        ["service102 gateway102", "storage102 network102", "latency102 buffer102"],
    ),
    (
        ("gateway102 storage102 network102 latency102 buffer102 queue102", 6),
        ["gateway102", "storage102", "network102", "latency102", "buffer102", "queue102"],
    ),
    (
        ("gateway102 storage102 network102 latency102 buffer102 queue102", 10),
        ["gateway102", "storage102", "network102", "latency102", "buffer102", "queue102"],
    ),
    (
        ("gateway102 storage102 network102 latency102 buffer102 queue102", 18),
        ["gateway102", "storage102", "network102", "latency102", "buffer102 queue102"],
    ),
    (
        ("gateway102 storage102 network102 latency102 buffer102 queue102", 28),
        ["gateway102 storage102", "network102 latency102", "buffer102 queue102"],
    ),
    (
        ("storage102 network102 latency102 buffer102 queue102 worker102", 6),
        ["storage102", "network102", "latency102", "buffer102", "queue102", "worker102"],
    ),
    (
        ("storage102 network102 latency102 buffer102 queue102 worker102", 10),
        ["storage102", "network102", "latency102", "buffer102", "queue102", "worker102"],
    ),
    (
        ("storage102 network102 latency102 buffer102 queue102 worker102", 18),
        ["storage102", "network102", "latency102", "buffer102 queue102", "worker102"],
    ),
    (
        ("storage102 network102 latency102 buffer102 queue102 worker102", 28),
        ["storage102 network102", "latency102 buffer102", "queue102 worker102"],
    ),
    (
        ("network102 latency102 buffer102 queue102 worker102 kernel102", 6),
        ["network102", "latency102", "buffer102", "queue102", "worker102", "kernel102"],
    ),
    (
        ("network102 latency102 buffer102 queue102 worker102 kernel102", 10),
        ["network102", "latency102", "buffer102", "queue102", "worker102", "kernel102"],
    ),
    (
        ("network102 latency102 buffer102 queue102 worker102 kernel102", 18),
        ["network102", "latency102", "buffer102 queue102", "worker102", "kernel102"],
    ),
    (
        ("network102 latency102 buffer102 queue102 worker102 kernel102", 28),
        ["network102 latency102", "buffer102 queue102 worker102", "kernel102"],
    ),
    (
        ("latency102 buffer102 queue102 worker102 kernel102 signal102", 6),
        ["latency102", "buffer102", "queue102", "worker102", "kernel102", "signal102"],
    ),
    (
        ("latency102 buffer102 queue102 worker102 kernel102 signal102", 10),
        ["latency102", "buffer102", "queue102", "worker102", "kernel102", "signal102"],
    ),
    (
        ("latency102 buffer102 queue102 worker102 kernel102 signal102", 18),
        ["latency102", "buffer102 queue102", "worker102", "kernel102", "signal102"],
    ),
    (
        ("latency102 buffer102 queue102 worker102 kernel102 signal102", 28),
        ["latency102 buffer102", "queue102 worker102 kernel102", "signal102"],
    ),
    (
        ("buffer102 queue102 worker102 kernel102 signal102 packet102", 6),
        ["buffer102", "queue102", "worker102", "kernel102", "signal102", "packet102"],
    ),
    (
        ("buffer102 queue102 worker102 kernel102 signal102 packet102", 10),
        ["buffer102", "queue102", "worker102", "kernel102", "signal102", "packet102"],
    ),
    (
        ("buffer102 queue102 worker102 kernel102 signal102 packet102", 18),
        ["buffer102 queue102", "worker102", "kernel102", "signal102", "packet102"],
    ),
    (
        ("buffer102 queue102 worker102 kernel102 signal102 packet102", 28),
        ["buffer102 queue102 worker102", "kernel102 signal102", "packet102"],
    ),
    (
        ("queue102 worker102 kernel102 signal102 packet102 router102", 6),
        ["queue102", "worker102", "kernel102", "signal102", "packet102", "router102"],
    ),
    (
        ("queue102 worker102 kernel102 signal102 packet102 router102", 10),
        ["queue102", "worker102", "kernel102", "signal102", "packet102", "router102"],
    ),
    (
        ("queue102 worker102 kernel102 signal102 packet102 router102", 18),
        ["queue102 worker102", "kernel102", "signal102", "packet102", "router102"],
    ),
    (
        ("queue102 worker102 kernel102 signal102 packet102 router102", 28),
        ["queue102 worker102 kernel102", "signal102 packet102", "router102"],
    ),
    (
        ("worker102 kernel102 signal102 packet102 router102 cluster102", 6),
        ["worker102", "kernel102", "signal102", "packet102", "router102", "cluster102"],
    ),
    (
        ("worker102 kernel102 signal102 packet102 router102 cluster102", 10),
        ["worker102", "kernel102", "signal102", "packet102", "router102", "cluster102"],
    ),
    (
        ("worker102 kernel102 signal102 packet102 router102 cluster102", 18),
        ["worker102", "kernel102", "signal102", "packet102", "router102", "cluster102"],
    ),
    (
        ("worker102 kernel102 signal102 packet102 router102 cluster102", 28),
        ["worker102 kernel102", "signal102 packet102", "router102 cluster102"],
    ),
    (
        ("kernel102 signal102 packet102 router102 cluster102 mirror102", 6),
        ["kernel102", "signal102", "packet102", "router102", "cluster102", "mirror102"],
    ),
    (
        ("kernel102 signal102 packet102 router102 cluster102 mirror102", 10),
        ["kernel102", "signal102", "packet102", "router102", "cluster102", "mirror102"],
    ),
    (
        ("kernel102 signal102 packet102 router102 cluster102 mirror102", 18),
        ["kernel102", "signal102", "packet102", "router102", "cluster102", "mirror102"],
    ),
    (
        ("kernel102 signal102 packet102 router102 cluster102 mirror102", 28),
        ["kernel102 signal102", "packet102 router102", "cluster102 mirror102"],
    ),
    (
        ("signal102 packet102 router102 cluster102 mirror102 filter102", 6),
        ["signal102", "packet102", "router102", "cluster102", "mirror102", "filter102"],
    ),
    (
        ("signal102 packet102 router102 cluster102 mirror102 filter102", 10),
        ["signal102", "packet102", "router102", "cluster102", "mirror102", "filter102"],
    ),
    (
        ("signal102 packet102 router102 cluster102 mirror102 filter102", 18),
        ["signal102", "packet102", "router102", "cluster102", "mirror102", "filter102"],
    ),
    (
        ("signal102 packet102 router102 cluster102 mirror102 filter102", 28),
        ["signal102 packet102", "router102 cluster102", "mirror102 filter102"],
    ),
    (
        ("packet102 router102 cluster102 mirror102 filter102 ranking102", 6),
        ["packet102", "router102", "cluster102", "mirror102", "filter102", "ranking102"],
    ),
    (
        ("packet102 router102 cluster102 mirror102 filter102 ranking102", 10),
        ["packet102", "router102", "cluster102", "mirror102", "filter102", "ranking102"],
    ),
    (
        ("packet102 router102 cluster102 mirror102 filter102 ranking102", 18),
        ["packet102", "router102", "cluster102", "mirror102", "filter102", "ranking102"],
    ),
    (
        ("packet102 router102 cluster102 mirror102 filter102 ranking102", 28),
        ["packet102 router102", "cluster102 mirror102", "filter102 ranking102"],
    ),
    (
        ("router102 cluster102 mirror102 filter102 ranking102 encoding102", 6),
        ["router102", "cluster102", "mirror102", "filter102", "ranking102", "encoding102"],
    ),
    (
        ("router102 cluster102 mirror102 filter102 ranking102 encoding102", 10),
        ["router102", "cluster102", "mirror102", "filter102", "ranking102", "encoding102"],
    ),
    (
        ("router102 cluster102 mirror102 filter102 ranking102 encoding102", 18),
        ["router102", "cluster102", "mirror102", "filter102", "ranking102", "encoding102"],
    ),
    (
        ("router102 cluster102 mirror102 filter102 ranking102 encoding102", 28),
        ["router102 cluster102", "mirror102 filter102", "ranking102 encoding102"],
    ),
    (
        ("cluster102 mirror102 filter102 ranking102 encoding102 mapping102", 6),
        ["cluster102", "mirror102", "filter102", "ranking102", "encoding102", "mapping102"],
    ),
    (
        ("cluster102 mirror102 filter102 ranking102 encoding102 mapping102", 10),
        ["cluster102", "mirror102", "filter102", "ranking102", "encoding102", "mapping102"],
    ),
    (
        ("cluster102 mirror102 filter102 ranking102 encoding102 mapping102", 18),
        ["cluster102", "mirror102", "filter102", "ranking102", "encoding102", "mapping102"],
    ),
    (
        ("cluster102 mirror102 filter102 ranking102 encoding102 mapping102", 28),
        ["cluster102 mirror102", "filter102 ranking102", "encoding102 mapping102"],
    ),
    (
        ("mirror102 filter102 ranking102 encoding102 mapping102 record102", 6),
        ["mirror102", "filter102", "ranking102", "encoding102", "mapping102", "record102"],
    ),
    (
        ("mirror102 filter102 ranking102 encoding102 mapping102 record102", 10),
        ["mirror102", "filter102", "ranking102", "encoding102", "mapping102", "record102"],
    ),
    (
        ("mirror102 filter102 ranking102 encoding102 mapping102 record102", 18),
        ["mirror102", "filter102", "ranking102", "encoding102", "mapping102", "record102"],
    ),
    (
        ("mirror102 filter102 ranking102 encoding102 mapping102 record102", 28),
        ["mirror102 filter102", "ranking102 encoding102", "mapping102 record102"],
    ),
    (
        ("filter102 ranking102 encoding102 mapping102 record102 candle102", 6),
        ["filter102", "ranking102", "encoding102", "mapping102", "record102", "candle102"],
    ),
    (
        ("filter102 ranking102 encoding102 mapping102 record102 candle102", 10),
        ["filter102", "ranking102", "encoding102", "mapping102", "record102", "candle102"],
    ),
    (
        ("filter102 ranking102 encoding102 mapping102 record102 candle102", 18),
        ["filter102", "ranking102", "encoding102", "mapping102", "record102", "candle102"],
    ),
    (
        ("filter102 ranking102 encoding102 mapping102 record102 candle102", 28),
        ["filter102 ranking102", "encoding102 mapping102", "record102 candle102"],
    ),
    (
        ("ranking102 encoding102 mapping102 record102 candle102 thread102", 6),
        ["ranking102", "encoding102", "mapping102", "record102", "candle102", "thread102"],
    ),
    (
        ("ranking102 encoding102 mapping102 record102 candle102 thread102", 10),
        ["ranking102", "encoding102", "mapping102", "record102", "candle102", "thread102"],
    ),
    (
        ("ranking102 encoding102 mapping102 record102 candle102 thread102", 18),
        ["ranking102", "encoding102", "mapping102", "record102", "candle102", "thread102"],
    ),
    (
        ("ranking102 encoding102 mapping102 record102 candle102 thread102", 28),
        ["ranking102 encoding102", "mapping102 record102", "candle102 thread102"],
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
