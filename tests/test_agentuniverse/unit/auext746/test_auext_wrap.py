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
        ("round 746: the quick brown fox jumps over the lazy dog", 4),
        ["round", "746:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", 8),
        ["round", "746: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", 12),
        ["round 746:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", 16),
        ["round 746: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", 24),
        ["round 746: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 746: the quick brown fox jumps over the lazy dog", 32),
        ["round 746: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", 4),
        ["round", "746:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", 8),
        ["round", "746:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", 12),
        ["round 746:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", 16),
        ["round 746:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", 24),
        ["round 746: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 746: agentuniverse is a framework for multi agents", 32),
        ["round 746: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", 4),
        ["round", "746:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", 8),
        ["round", "746:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", 12),
        ["round 746:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", 16),
        ["round 746:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", 24),
        ["round 746: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 746: knowledge stored as vectors enables retrieval", 32),
        ["round 746: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 746: the processor reads the record then stops", 4),
        ["round", "746:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 746: the processor reads the record then stops", 8),
        ["round", "746: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 746: the processor reads the record then stops", 12),
        ["round 746:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 746: the processor reads the record then stops", 16),
        ["round 746: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 746: the processor reads the record then stops", 24),
        ["round 746: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 746: the processor reads the record then stops", 32),
        ["round 746: the processor reads", "the record then stops"],
    ),
    (
        ("round 746: a worker pulls the next task from the queue", 4),
        ["round", "746:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 746: a worker pulls the next task from the queue", 8),
        ["round", "746: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 746: a worker pulls the next task from the queue", 12),
        ["round 746: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 746: a worker pulls the next task from the queue", 16),
        ["round 746: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 746: a worker pulls the next task from the queue", 24),
        ["round 746: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 746: a worker pulls the next task from the queue", 32),
        ["round 746: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 746: signals travel through the network layer", 4),
        ["round", "746:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 746: signals travel through the network layer", 8),
        ["round", "746:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 746: signals travel through the network layer", 12),
        ["round 746:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 746: signals travel through the network layer", 16),
        ["round 746:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 746: signals travel through the network layer", 24),
        ["round 746: signals", "travel through the", "network layer"],
    ),
    (
        ("round 746: signals travel through the network layer", 32),
        ["round 746: signals travel", "through the network layer"],
    ),
    (
        ("round 746: the gateway routes each request by policy", 4),
        ["round", "746:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 746: the gateway routes each request by policy", 8),
        ["round", "746: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 746: the gateway routes each request by policy", 12),
        ["round 746:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 746: the gateway routes each request by policy", 16),
        ["round 746: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 746: the gateway routes each request by policy", 24),
        ["round 746: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 746: the gateway routes each request by policy", 32),
        ["round 746: the gateway routes", "each request by policy"],
    ),
    (
        ("round 746: memory grows until the buffer is full", 4),
        ["round", "746:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 746: memory grows until the buffer is full", 8),
        ["round", "746:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 746: memory grows until the buffer is full", 12),
        ["round 746:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 746: memory grows until the buffer is full", 16),
        ["round 746:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 746: memory grows until the buffer is full", 24), ["round 746: memory grows", "until the buffer is full"]),
    (("round 746: memory grows until the buffer is full", 32), ["round 746: memory grows until", "the buffer is full"]),
    (
        ("round 746: the cluster mirrors every packet twice", 4),
        ["round", "746:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 746: the cluster mirrors every packet twice", 8),
        ["round", "746: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 746: the cluster mirrors every packet twice", 12),
        ["round 746:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 746: the cluster mirrors every packet twice", 16),
        ["round 746: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 746: the cluster mirrors every packet twice", 24),
        ["round 746: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 746: the cluster mirrors every packet twice", 32),
        ["round 746: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", 4),
        ["round", "746:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", 8),
        ["round", "746:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", 12),
        ["round 746:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", 16),
        ["round 746:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", 24),
        ["round 746: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 746: ranking uses tokens learned from the corpus", 32),
        ["round 746: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 746: a long session ends when the candle dies", 4),
        ["round", "746:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 746: a long session ends when the candle dies", 8),
        ["round", "746: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 746: a long session ends when the candle dies", 12),
        ["round 746: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 746: a long session ends when the candle dies", 16),
        ["round 746: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 746: a long session ends when the candle dies", 24),
        ["round 746: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 746: a long session ends when the candle dies", 32),
        ["round 746: a long session ends", "when the candle dies"],
    ),
    (
        ("round 746: encode the prompt then map the result", 4),
        ["round", "746:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 746: encode the prompt then map the result", 8),
        ["round", "746:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 746: encode the prompt then map the result", 12),
        ["round 746:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 746: encode the prompt then map the result", 16),
        ["round 746:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 746: encode the prompt then map the result", 24),
        ["round 746: encode the", "prompt then map the", "result"],
    ),
    (("round 746: encode the prompt then map the result", 32), ["round 746: encode the prompt", "then map the result"]),
    (
        ("round 746: the kernel wakes the worker at dawn", 4),
        ["round", "746:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 746: the kernel wakes the worker at dawn", 8),
        ["round", "746: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 746: the kernel wakes the worker at dawn", 12),
        ["round 746:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 746: the kernel wakes the worker at dawn", 16), ["round 746: the", "kernel wakes the", "worker at dawn"]),
    (("round 746: the kernel wakes the worker at dawn", 24), ["round 746: the kernel", "wakes the worker at dawn"]),
    (("round 746: the kernel wakes the worker at dawn", 32), ["round 746: the kernel wakes the", "worker at dawn"]),
    (
        ("round 746: service latency drops after the patch", 4),
        ["round", "746:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 746: service latency drops after the patch", 8),
        ["round", "746:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 746: service latency drops after the patch", 12),
        ["round 746:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 746: service latency drops after the patch", 16),
        ["round 746:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 746: service latency drops after the patch", 24),
        ["round 746: service", "latency drops after the", "patch"],
    ),
    (("round 746: service latency drops after the patch", 32), ["round 746: service latency drops", "after the patch"]),
    (
        ("round 746: the library caches every vector it sees", 4),
        ["round", "746:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 746: the library caches every vector it sees", 8),
        ["round", "746: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 746: the library caches every vector it sees", 12),
        ["round 746:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 746: the library caches every vector it sees", 16),
        ["round 746: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 746: the library caches every vector it sees", 24),
        ["round 746: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 746: the library caches every vector it sees", 32),
        ["round 746: the library caches", "every vector it sees"],
    ),
    (
        ("round 746: agents argue then the debate resolves", 4),
        ["round", "746:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 746: agents argue then the debate resolves", 8),
        ["round", "746:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 746: agents argue then the debate resolves", 12),
        ["round 746:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 746: agents argue then the debate resolves", 16),
        ["round 746:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 746: agents argue then the debate resolves", 24), ["round 746: agents argue", "then the debate resolves"]),
    (("round 746: agents argue then the debate resolves", 32), ["round 746: agents argue then the", "debate resolves"]),
    (
        ("round 746: the filter keeps only strong matches", 4),
        ["round", "746:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 746: the filter keeps only strong matches", 8),
        ["round", "746: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 746: the filter keeps only strong matches", 12),
        ["round 746:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 746: the filter keeps only strong matches", 16),
        ["round 746: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 746: the filter keeps only strong matches", 24),
        ["round 746: the filter", "keeps only strong", "matches"],
    ),
    (("round 746: the filter keeps only strong matches", 32), ["round 746: the filter keeps only", "strong matches"]),
    (
        ("round 746: the model answers with a short reply", 4),
        ["round", "746:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 746: the model answers with a short reply", 8),
        ["round", "746: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 746: the model answers with a short reply", 12),
        ["round 746:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 746: the model answers with a short reply", 16),
        ["round 746: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 746: the model answers with a short reply", 24),
        ["round 746: the model", "answers with a short", "reply"],
    ),
    (("round 746: the model answers with a short reply", 32), ["round 746: the model answers", "with a short reply"]),
    (
        ("round 746: the recorder stores the reasoning trace", 4),
        ["round", "746:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 746: the recorder stores the reasoning trace", 8),
        ["round", "746: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 746: the recorder stores the reasoning trace", 12),
        ["round 746:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 746: the recorder stores the reasoning trace", 16),
        ["round 746: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 746: the recorder stores the reasoning trace", 24),
        ["round 746: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 746: the recorder stores the reasoning trace", 32),
        ["round 746: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 746: the angel watches the processor run", 4),
        ["round", "746:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 746: the angel watches the processor run", 8),
        ["round", "746: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 746: the angel watches the processor run", 12),
        ["round 746:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 746: the angel watches the processor run", 16),
        ["round 746: the", "angel watches", "the processor", "run"],
    ),
    (("round 746: the angel watches the processor run", 24), ["round 746: the angel", "watches the processor", "run"]),
    (("round 746: the angel watches the processor run", 32), ["round 746: the angel watches the", "processor run"]),
    (
        ("round 746: angle of the vector decides the match", 4),
        ["round", "746:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 746: angle of the vector decides the match", 8),
        ["round", "746:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 746: angle of the vector decides the match", 12),
        ["round 746:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 746: angle of the vector decides the match", 16),
        ["round 746: angle", "of the vector", "decides the", "match"],
    ),
    (("round 746: angle of the vector decides the match", 24), ["round 746: angle of the", "vector decides the match"]),
    (("round 746: angle of the vector decides the match", 32), ["round 746: angle of the vector", "decides the match"]),
    (
        ("round 746: the candle burns twice as long at night", 4),
        ["round", "746:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 746: the candle burns twice as long at night", 8),
        ["round", "746: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 746: the candle burns twice as long at night", 12),
        ["round 746:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 746: the candle burns twice as long at night", 16),
        ["round 746: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 746: the candle burns twice as long at night", 24),
        ["round 746: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 746: the candle burns twice as long at night", 32),
        ["round 746: the candle burns", "twice as long at night"],
    ),
    (
        ("round 746: a mirror of the universe in one line", 4),
        ["round", "746:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 746: a mirror of the universe in one line", 8),
        ["round", "746: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 746: a mirror of the universe in one line", 12),
        ["round 746: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 746: a mirror of the universe in one line", 16),
        ["round 746: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 746: a mirror of the universe in one line", 24), ["round 746: a mirror of", "the universe in one line"]),
    (("round 746: a mirror of the universe in one line", 32), ["round 746: a mirror of the", "universe in one line"]),
    (
        ("round 746: the queue drains before the storm", 4),
        ["round", "746:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 746: the queue drains before the storm", 8),
        ["round", "746: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 746: the queue drains before the storm", 12),
        ["round 746:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 746: the queue drains before the storm", 16), ["round 746: the", "queue drains", "before the storm"]),
    (("round 746: the queue drains before the storm", 24), ["round 746: the queue", "drains before the storm"]),
    (("round 746: the queue drains before the storm", 32), ["round 746: the queue drains", "before the storm"]),
    (
        ("kitten746 sitting746 agent746 angle746 universe746 memory746", 6),
        ["kitten746", "sitting746", "agent746", "angle746", "universe746", "memory746"],
    ),
    (
        ("kitten746 sitting746 agent746 angle746 universe746 memory746", 10),
        ["kitten746", "sitting746", "agent746", "angle746", "universe746", "memory746"],
    ),
    (
        ("kitten746 sitting746 agent746 angle746 universe746 memory746", 18),
        ["kitten746", "sitting746", "agent746 angle746", "universe746", "memory746"],
    ),
    (
        ("kitten746 sitting746 agent746 angle746 universe746 memory746", 28),
        ["kitten746 sitting746", "agent746 angle746", "universe746 memory746"],
    ),
    (
        ("sitting746 agent746 angle746 universe746 memory746 stream746", 6),
        ["sitting746", "agent746", "angle746", "universe746", "memory746", "stream746"],
    ),
    (
        ("sitting746 agent746 angle746 universe746 memory746 stream746", 10),
        ["sitting746", "agent746", "angle746", "universe746", "memory746", "stream746"],
    ),
    (
        ("sitting746 agent746 angle746 universe746 memory746 stream746", 18),
        ["sitting746", "agent746 angle746", "universe746", "memory746", "stream746"],
    ),
    (
        ("sitting746 agent746 angle746 universe746 memory746 stream746", 28),
        ["sitting746 agent746 angle746", "universe746 memory746", "stream746"],
    ),
    (
        ("agent746 angle746 universe746 memory746 stream746 context746", 6),
        ["agent746", "angle746", "universe746", "memory746", "stream746", "context746"],
    ),
    (
        ("agent746 angle746 universe746 memory746 stream746 context746", 10),
        ["agent746", "angle746", "universe746", "memory746", "stream746", "context746"],
    ),
    (
        ("agent746 angle746 universe746 memory746 stream746 context746", 18),
        ["agent746 angle746", "universe746", "memory746", "stream746", "context746"],
    ),
    (
        ("agent746 angle746 universe746 memory746 stream746 context746", 28),
        ["agent746 angle746", "universe746 memory746", "stream746 context746"],
    ),
    (
        ("angle746 universe746 memory746 stream746 context746 knowledge746", 6),
        ["angle746", "universe746", "memory746", "stream746", "context746", "knowledge746"],
    ),
    (
        ("angle746 universe746 memory746 stream746 context746 knowledge746", 10),
        ["angle746", "universe746", "memory746", "stream746", "context746", "knowledge746"],
    ),
    (
        ("angle746 universe746 memory746 stream746 context746 knowledge746", 18),
        ["angle746", "universe746", "memory746", "stream746", "context746", "knowledge746"],
    ),
    (
        ("angle746 universe746 memory746 stream746 context746 knowledge746", 28),
        ["angle746 universe746", "memory746 stream746", "context746 knowledge746"],
    ),
    (
        ("universe746 memory746 stream746 context746 knowledge746 vector746", 6),
        ["universe746", "memory746", "stream746", "context746", "knowledge746", "vector746"],
    ),
    (
        ("universe746 memory746 stream746 context746 knowledge746 vector746", 10),
        ["universe746", "memory746", "stream746", "context746", "knowledge746", "vector746"],
    ),
    (
        ("universe746 memory746 stream746 context746 knowledge746 vector746", 18),
        ["universe746", "memory746", "stream746", "context746", "knowledge746", "vector746"],
    ),
    (
        ("universe746 memory746 stream746 context746 knowledge746 vector746", 28),
        ["universe746 memory746", "stream746 context746", "knowledge746 vector746"],
    ),
    (
        ("memory746 stream746 context746 knowledge746 vector746 processor746", 6),
        ["memory746", "stream746", "context746", "knowledge746", "vector746", "processor746"],
    ),
    (
        ("memory746 stream746 context746 knowledge746 vector746 processor746", 10),
        ["memory746", "stream746", "context746", "knowledge746", "vector746", "processor746"],
    ),
    (
        ("memory746 stream746 context746 knowledge746 vector746 processor746", 18),
        ["memory746", "stream746", "context746", "knowledge746", "vector746", "processor746"],
    ),
    (
        ("memory746 stream746 context746 knowledge746 vector746 processor746", 28),
        ["memory746 stream746", "context746 knowledge746", "vector746 processor746"],
    ),
    (
        ("stream746 context746 knowledge746 vector746 processor746 reasoning746", 6),
        ["stream746", "context746", "knowledge746", "vector746", "processor746", "reasoning746"],
    ),
    (
        ("stream746 context746 knowledge746 vector746 processor746 reasoning746", 10),
        ["stream746", "context746", "knowledge746", "vector746", "processor746", "reasoning746"],
    ),
    (
        ("stream746 context746 knowledge746 vector746 processor746 reasoning746", 18),
        ["stream746", "context746", "knowledge746", "vector746", "processor746", "reasoning746"],
    ),
    (
        ("stream746 context746 knowledge746 vector746 processor746 reasoning746", 28),
        ["stream746 context746", "knowledge746 vector746", "processor746 reasoning746"],
    ),
    (
        ("context746 knowledge746 vector746 processor746 reasoning746 machine746", 6),
        ["context746", "knowledge746", "vector746", "processor746", "reasoning746", "machine746"],
    ),
    (
        ("context746 knowledge746 vector746 processor746 reasoning746 machine746", 10),
        ["context746", "knowledge746", "vector746", "processor746", "reasoning746", "machine746"],
    ),
    (
        ("context746 knowledge746 vector746 processor746 reasoning746 machine746", 18),
        ["context746", "knowledge746", "vector746", "processor746", "reasoning746", "machine746"],
    ),
    (
        ("context746 knowledge746 vector746 processor746 reasoning746 machine746", 28),
        ["context746 knowledge746", "vector746 processor746", "reasoning746 machine746"],
    ),
    (
        ("knowledge746 vector746 processor746 reasoning746 machine746 learning746", 6),
        ["knowledge746", "vector746", "processor746", "reasoning746", "machine746", "learning746"],
    ),
    (
        ("knowledge746 vector746 processor746 reasoning746 machine746 learning746", 10),
        ["knowledge746", "vector746", "processor746", "reasoning746", "machine746", "learning746"],
    ),
    (
        ("knowledge746 vector746 processor746 reasoning746 machine746 learning746", 18),
        ["knowledge746", "vector746", "processor746", "reasoning746", "machine746", "learning746"],
    ),
    (
        ("knowledge746 vector746 processor746 reasoning746 machine746 learning746", 28),
        ["knowledge746 vector746", "processor746 reasoning746", "machine746 learning746"],
    ),
    (
        ("vector746 processor746 reasoning746 machine746 learning746 model746", 6),
        ["vector746", "processor746", "reasoning746", "machine746", "learning746", "model746"],
    ),
    (
        ("vector746 processor746 reasoning746 machine746 learning746 model746", 10),
        ["vector746", "processor746", "reasoning746", "machine746", "learning746", "model746"],
    ),
    (
        ("vector746 processor746 reasoning746 machine746 learning746 model746", 18),
        ["vector746", "processor746", "reasoning746", "machine746", "learning746", "model746"],
    ),
    (
        ("vector746 processor746 reasoning746 machine746 learning746 model746", 28),
        ["vector746 processor746", "reasoning746 machine746", "learning746 model746"],
    ),
    (
        ("processor746 reasoning746 machine746 learning746 model746 token746", 6),
        ["processor746", "reasoning746", "machine746", "learning746", "model746", "token746"],
    ),
    (
        ("processor746 reasoning746 machine746 learning746 model746 token746", 10),
        ["processor746", "reasoning746", "machine746", "learning746", "model746", "token746"],
    ),
    (
        ("processor746 reasoning746 machine746 learning746 model746 token746", 18),
        ["processor746", "reasoning746", "machine746", "learning746", "model746 token746"],
    ),
    (
        ("processor746 reasoning746 machine746 learning746 model746 token746", 28),
        ["processor746 reasoning746", "machine746 learning746", "model746 token746"],
    ),
    (
        ("reasoning746 machine746 learning746 model746 token746 prompt746", 6),
        ["reasoning746", "machine746", "learning746", "model746", "token746", "prompt746"],
    ),
    (
        ("reasoning746 machine746 learning746 model746 token746 prompt746", 10),
        ["reasoning746", "machine746", "learning746", "model746", "token746", "prompt746"],
    ),
    (
        ("reasoning746 machine746 learning746 model746 token746 prompt746", 18),
        ["reasoning746", "machine746", "learning746", "model746 token746", "prompt746"],
    ),
    (
        ("reasoning746 machine746 learning746 model746 token746 prompt746", 28),
        ["reasoning746 machine746", "learning746 model746", "token746 prompt746"],
    ),
    (
        ("machine746 learning746 model746 token746 prompt746 session746", 6),
        ["machine746", "learning746", "model746", "token746", "prompt746", "session746"],
    ),
    (
        ("machine746 learning746 model746 token746 prompt746 session746", 10),
        ["machine746", "learning746", "model746", "token746", "prompt746", "session746"],
    ),
    (
        ("machine746 learning746 model746 token746 prompt746 session746", 18),
        ["machine746", "learning746", "model746 token746", "prompt746", "session746"],
    ),
    (
        ("machine746 learning746 model746 token746 prompt746 session746", 28),
        ["machine746 learning746", "model746 token746 prompt746", "session746"],
    ),
    (
        ("learning746 model746 token746 prompt746 session746 library746", 6),
        ["learning746", "model746", "token746", "prompt746", "session746", "library746"],
    ),
    (
        ("learning746 model746 token746 prompt746 session746 library746", 10),
        ["learning746", "model746", "token746", "prompt746", "session746", "library746"],
    ),
    (
        ("learning746 model746 token746 prompt746 session746 library746", 18),
        ["learning746", "model746 token746", "prompt746", "session746", "library746"],
    ),
    (
        ("learning746 model746 token746 prompt746 session746 library746", 28),
        ["learning746 model746", "token746 prompt746", "session746 library746"],
    ),
    (
        ("model746 token746 prompt746 session746 library746 service746", 6),
        ["model746", "token746", "prompt746", "session746", "library746", "service746"],
    ),
    (
        ("model746 token746 prompt746 session746 library746 service746", 10),
        ["model746", "token746", "prompt746", "session746", "library746", "service746"],
    ),
    (
        ("model746 token746 prompt746 session746 library746 service746", 18),
        ["model746 token746", "prompt746", "session746", "library746", "service746"],
    ),
    (
        ("model746 token746 prompt746 session746 library746 service746", 28),
        ["model746 token746 prompt746", "session746 library746", "service746"],
    ),
    (
        ("token746 prompt746 session746 library746 service746 gateway746", 6),
        ["token746", "prompt746", "session746", "library746", "service746", "gateway746"],
    ),
    (
        ("token746 prompt746 session746 library746 service746 gateway746", 10),
        ["token746", "prompt746", "session746", "library746", "service746", "gateway746"],
    ),
    (
        ("token746 prompt746 session746 library746 service746 gateway746", 18),
        ["token746 prompt746", "session746", "library746", "service746", "gateway746"],
    ),
    (
        ("token746 prompt746 session746 library746 service746 gateway746", 28),
        ["token746 prompt746", "session746 library746", "service746 gateway746"],
    ),
    (
        ("prompt746 session746 library746 service746 gateway746 storage746", 6),
        ["prompt746", "session746", "library746", "service746", "gateway746", "storage746"],
    ),
    (
        ("prompt746 session746 library746 service746 gateway746 storage746", 10),
        ["prompt746", "session746", "library746", "service746", "gateway746", "storage746"],
    ),
    (
        ("prompt746 session746 library746 service746 gateway746 storage746", 18),
        ["prompt746", "session746", "library746", "service746", "gateway746", "storage746"],
    ),
    (
        ("prompt746 session746 library746 service746 gateway746 storage746", 28),
        ["prompt746 session746", "library746 service746", "gateway746 storage746"],
    ),
    (
        ("session746 library746 service746 gateway746 storage746 network746", 6),
        ["session746", "library746", "service746", "gateway746", "storage746", "network746"],
    ),
    (
        ("session746 library746 service746 gateway746 storage746 network746", 10),
        ["session746", "library746", "service746", "gateway746", "storage746", "network746"],
    ),
    (
        ("session746 library746 service746 gateway746 storage746 network746", 18),
        ["session746", "library746", "service746", "gateway746", "storage746", "network746"],
    ),
    (
        ("session746 library746 service746 gateway746 storage746 network746", 28),
        ["session746 library746", "service746 gateway746", "storage746 network746"],
    ),
    (
        ("library746 service746 gateway746 storage746 network746 latency746", 6),
        ["library746", "service746", "gateway746", "storage746", "network746", "latency746"],
    ),
    (
        ("library746 service746 gateway746 storage746 network746 latency746", 10),
        ["library746", "service746", "gateway746", "storage746", "network746", "latency746"],
    ),
    (
        ("library746 service746 gateway746 storage746 network746 latency746", 18),
        ["library746", "service746", "gateway746", "storage746", "network746", "latency746"],
    ),
    (
        ("library746 service746 gateway746 storage746 network746 latency746", 28),
        ["library746 service746", "gateway746 storage746", "network746 latency746"],
    ),
    (
        ("service746 gateway746 storage746 network746 latency746 buffer746", 6),
        ["service746", "gateway746", "storage746", "network746", "latency746", "buffer746"],
    ),
    (
        ("service746 gateway746 storage746 network746 latency746 buffer746", 10),
        ["service746", "gateway746", "storage746", "network746", "latency746", "buffer746"],
    ),
    (
        ("service746 gateway746 storage746 network746 latency746 buffer746", 18),
        ["service746", "gateway746", "storage746", "network746", "latency746", "buffer746"],
    ),
    (
        ("service746 gateway746 storage746 network746 latency746 buffer746", 28),
        ["service746 gateway746", "storage746 network746", "latency746 buffer746"],
    ),
    (
        ("gateway746 storage746 network746 latency746 buffer746 queue746", 6),
        ["gateway746", "storage746", "network746", "latency746", "buffer746", "queue746"],
    ),
    (
        ("gateway746 storage746 network746 latency746 buffer746 queue746", 10),
        ["gateway746", "storage746", "network746", "latency746", "buffer746", "queue746"],
    ),
    (
        ("gateway746 storage746 network746 latency746 buffer746 queue746", 18),
        ["gateway746", "storage746", "network746", "latency746", "buffer746 queue746"],
    ),
    (
        ("gateway746 storage746 network746 latency746 buffer746 queue746", 28),
        ["gateway746 storage746", "network746 latency746", "buffer746 queue746"],
    ),
    (
        ("storage746 network746 latency746 buffer746 queue746 worker746", 6),
        ["storage746", "network746", "latency746", "buffer746", "queue746", "worker746"],
    ),
    (
        ("storage746 network746 latency746 buffer746 queue746 worker746", 10),
        ["storage746", "network746", "latency746", "buffer746", "queue746", "worker746"],
    ),
    (
        ("storage746 network746 latency746 buffer746 queue746 worker746", 18),
        ["storage746", "network746", "latency746", "buffer746 queue746", "worker746"],
    ),
    (
        ("storage746 network746 latency746 buffer746 queue746 worker746", 28),
        ["storage746 network746", "latency746 buffer746", "queue746 worker746"],
    ),
    (
        ("network746 latency746 buffer746 queue746 worker746 kernel746", 6),
        ["network746", "latency746", "buffer746", "queue746", "worker746", "kernel746"],
    ),
    (
        ("network746 latency746 buffer746 queue746 worker746 kernel746", 10),
        ["network746", "latency746", "buffer746", "queue746", "worker746", "kernel746"],
    ),
    (
        ("network746 latency746 buffer746 queue746 worker746 kernel746", 18),
        ["network746", "latency746", "buffer746 queue746", "worker746", "kernel746"],
    ),
    (
        ("network746 latency746 buffer746 queue746 worker746 kernel746", 28),
        ["network746 latency746", "buffer746 queue746 worker746", "kernel746"],
    ),
    (
        ("latency746 buffer746 queue746 worker746 kernel746 signal746", 6),
        ["latency746", "buffer746", "queue746", "worker746", "kernel746", "signal746"],
    ),
    (
        ("latency746 buffer746 queue746 worker746 kernel746 signal746", 10),
        ["latency746", "buffer746", "queue746", "worker746", "kernel746", "signal746"],
    ),
    (
        ("latency746 buffer746 queue746 worker746 kernel746 signal746", 18),
        ["latency746", "buffer746 queue746", "worker746", "kernel746", "signal746"],
    ),
    (
        ("latency746 buffer746 queue746 worker746 kernel746 signal746", 28),
        ["latency746 buffer746", "queue746 worker746 kernel746", "signal746"],
    ),
    (
        ("buffer746 queue746 worker746 kernel746 signal746 packet746", 6),
        ["buffer746", "queue746", "worker746", "kernel746", "signal746", "packet746"],
    ),
    (
        ("buffer746 queue746 worker746 kernel746 signal746 packet746", 10),
        ["buffer746", "queue746", "worker746", "kernel746", "signal746", "packet746"],
    ),
    (
        ("buffer746 queue746 worker746 kernel746 signal746 packet746", 18),
        ["buffer746 queue746", "worker746", "kernel746", "signal746", "packet746"],
    ),
    (
        ("buffer746 queue746 worker746 kernel746 signal746 packet746", 28),
        ["buffer746 queue746 worker746", "kernel746 signal746", "packet746"],
    ),
    (
        ("queue746 worker746 kernel746 signal746 packet746 router746", 6),
        ["queue746", "worker746", "kernel746", "signal746", "packet746", "router746"],
    ),
    (
        ("queue746 worker746 kernel746 signal746 packet746 router746", 10),
        ["queue746", "worker746", "kernel746", "signal746", "packet746", "router746"],
    ),
    (
        ("queue746 worker746 kernel746 signal746 packet746 router746", 18),
        ["queue746 worker746", "kernel746", "signal746", "packet746", "router746"],
    ),
    (
        ("queue746 worker746 kernel746 signal746 packet746 router746", 28),
        ["queue746 worker746 kernel746", "signal746 packet746", "router746"],
    ),
    (
        ("worker746 kernel746 signal746 packet746 router746 cluster746", 6),
        ["worker746", "kernel746", "signal746", "packet746", "router746", "cluster746"],
    ),
    (
        ("worker746 kernel746 signal746 packet746 router746 cluster746", 10),
        ["worker746", "kernel746", "signal746", "packet746", "router746", "cluster746"],
    ),
    (
        ("worker746 kernel746 signal746 packet746 router746 cluster746", 18),
        ["worker746", "kernel746", "signal746", "packet746", "router746", "cluster746"],
    ),
    (
        ("worker746 kernel746 signal746 packet746 router746 cluster746", 28),
        ["worker746 kernel746", "signal746 packet746", "router746 cluster746"],
    ),
    (
        ("kernel746 signal746 packet746 router746 cluster746 mirror746", 6),
        ["kernel746", "signal746", "packet746", "router746", "cluster746", "mirror746"],
    ),
    (
        ("kernel746 signal746 packet746 router746 cluster746 mirror746", 10),
        ["kernel746", "signal746", "packet746", "router746", "cluster746", "mirror746"],
    ),
    (
        ("kernel746 signal746 packet746 router746 cluster746 mirror746", 18),
        ["kernel746", "signal746", "packet746", "router746", "cluster746", "mirror746"],
    ),
    (
        ("kernel746 signal746 packet746 router746 cluster746 mirror746", 28),
        ["kernel746 signal746", "packet746 router746", "cluster746 mirror746"],
    ),
    (
        ("signal746 packet746 router746 cluster746 mirror746 filter746", 6),
        ["signal746", "packet746", "router746", "cluster746", "mirror746", "filter746"],
    ),
    (
        ("signal746 packet746 router746 cluster746 mirror746 filter746", 10),
        ["signal746", "packet746", "router746", "cluster746", "mirror746", "filter746"],
    ),
    (
        ("signal746 packet746 router746 cluster746 mirror746 filter746", 18),
        ["signal746", "packet746", "router746", "cluster746", "mirror746", "filter746"],
    ),
    (
        ("signal746 packet746 router746 cluster746 mirror746 filter746", 28),
        ["signal746 packet746", "router746 cluster746", "mirror746 filter746"],
    ),
    (
        ("packet746 router746 cluster746 mirror746 filter746 ranking746", 6),
        ["packet746", "router746", "cluster746", "mirror746", "filter746", "ranking746"],
    ),
    (
        ("packet746 router746 cluster746 mirror746 filter746 ranking746", 10),
        ["packet746", "router746", "cluster746", "mirror746", "filter746", "ranking746"],
    ),
    (
        ("packet746 router746 cluster746 mirror746 filter746 ranking746", 18),
        ["packet746", "router746", "cluster746", "mirror746", "filter746", "ranking746"],
    ),
    (
        ("packet746 router746 cluster746 mirror746 filter746 ranking746", 28),
        ["packet746 router746", "cluster746 mirror746", "filter746 ranking746"],
    ),
    (
        ("router746 cluster746 mirror746 filter746 ranking746 encoding746", 6),
        ["router746", "cluster746", "mirror746", "filter746", "ranking746", "encoding746"],
    ),
    (
        ("router746 cluster746 mirror746 filter746 ranking746 encoding746", 10),
        ["router746", "cluster746", "mirror746", "filter746", "ranking746", "encoding746"],
    ),
    (
        ("router746 cluster746 mirror746 filter746 ranking746 encoding746", 18),
        ["router746", "cluster746", "mirror746", "filter746", "ranking746", "encoding746"],
    ),
    (
        ("router746 cluster746 mirror746 filter746 ranking746 encoding746", 28),
        ["router746 cluster746", "mirror746 filter746", "ranking746 encoding746"],
    ),
    (
        ("cluster746 mirror746 filter746 ranking746 encoding746 mapping746", 6),
        ["cluster746", "mirror746", "filter746", "ranking746", "encoding746", "mapping746"],
    ),
    (
        ("cluster746 mirror746 filter746 ranking746 encoding746 mapping746", 10),
        ["cluster746", "mirror746", "filter746", "ranking746", "encoding746", "mapping746"],
    ),
    (
        ("cluster746 mirror746 filter746 ranking746 encoding746 mapping746", 18),
        ["cluster746", "mirror746", "filter746", "ranking746", "encoding746", "mapping746"],
    ),
    (
        ("cluster746 mirror746 filter746 ranking746 encoding746 mapping746", 28),
        ["cluster746 mirror746", "filter746 ranking746", "encoding746 mapping746"],
    ),
    (
        ("mirror746 filter746 ranking746 encoding746 mapping746 record746", 6),
        ["mirror746", "filter746", "ranking746", "encoding746", "mapping746", "record746"],
    ),
    (
        ("mirror746 filter746 ranking746 encoding746 mapping746 record746", 10),
        ["mirror746", "filter746", "ranking746", "encoding746", "mapping746", "record746"],
    ),
    (
        ("mirror746 filter746 ranking746 encoding746 mapping746 record746", 18),
        ["mirror746", "filter746", "ranking746", "encoding746", "mapping746", "record746"],
    ),
    (
        ("mirror746 filter746 ranking746 encoding746 mapping746 record746", 28),
        ["mirror746 filter746", "ranking746 encoding746", "mapping746 record746"],
    ),
    (
        ("filter746 ranking746 encoding746 mapping746 record746 candle746", 6),
        ["filter746", "ranking746", "encoding746", "mapping746", "record746", "candle746"],
    ),
    (
        ("filter746 ranking746 encoding746 mapping746 record746 candle746", 10),
        ["filter746", "ranking746", "encoding746", "mapping746", "record746", "candle746"],
    ),
    (
        ("filter746 ranking746 encoding746 mapping746 record746 candle746", 18),
        ["filter746", "ranking746", "encoding746", "mapping746", "record746", "candle746"],
    ),
    (
        ("filter746 ranking746 encoding746 mapping746 record746 candle746", 28),
        ["filter746 ranking746", "encoding746 mapping746", "record746 candle746"],
    ),
    (
        ("ranking746 encoding746 mapping746 record746 candle746 thread746", 6),
        ["ranking746", "encoding746", "mapping746", "record746", "candle746", "thread746"],
    ),
    (
        ("ranking746 encoding746 mapping746 record746 candle746 thread746", 10),
        ["ranking746", "encoding746", "mapping746", "record746", "candle746", "thread746"],
    ),
    (
        ("ranking746 encoding746 mapping746 record746 candle746 thread746", 18),
        ["ranking746", "encoding746", "mapping746", "record746", "candle746", "thread746"],
    ),
    (
        ("ranking746 encoding746 mapping746 record746 candle746 thread746", 28),
        ["ranking746 encoding746", "mapping746 record746", "candle746 thread746"],
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
