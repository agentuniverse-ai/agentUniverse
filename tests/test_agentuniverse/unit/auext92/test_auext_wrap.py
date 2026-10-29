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
        ("round 92: the quick brown fox jumps over the lazy dog", 4),
        ["round", "92:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 92: the quick brown fox jumps over the lazy dog", 8),
        ["round", "92: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 92: the quick brown fox jumps over the lazy dog", 12),
        ["round 92:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 92: the quick brown fox jumps over the lazy dog", 16),
        ["round 92: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 92: the quick brown fox jumps over the lazy dog", 24),
        ["round 92: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 92: the quick brown fox jumps over the lazy dog", 32),
        ["round 92: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 92: agentuniverse is a framework for multi agents", 4),
        ["round", "92:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 92: agentuniverse is a framework for multi agents", 8),
        ["round", "92:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 92: agentuniverse is a framework for multi agents", 12),
        ["round 92:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 92: agentuniverse is a framework for multi agents", 16),
        ["round 92:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 92: agentuniverse is a framework for multi agents", 24),
        ["round 92: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 92: agentuniverse is a framework for multi agents", 32),
        ["round 92: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 92: knowledge stored as vectors enables retrieval", 4),
        ["round", "92:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 92: knowledge stored as vectors enables retrieval", 8),
        ["round", "92:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 92: knowledge stored as vectors enables retrieval", 12),
        ["round 92:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 92: knowledge stored as vectors enables retrieval", 16),
        ["round 92:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 92: knowledge stored as vectors enables retrieval", 24),
        ["round 92: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 92: knowledge stored as vectors enables retrieval", 32),
        ["round 92: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 92: the processor reads the record then stops", 4),
        ["round", "92:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 92: the processor reads the record then stops", 8),
        ["round", "92: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 92: the processor reads the record then stops", 12),
        ["round 92:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 92: the processor reads the record then stops", 16),
        ["round 92: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 92: the processor reads the record then stops", 24),
        ["round 92: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 92: the processor reads the record then stops", 32),
        ["round 92: the processor reads", "the record then stops"],
    ),
    (
        ("round 92: a worker pulls the next task from the queue", 4),
        ["round", "92:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 92: a worker pulls the next task from the queue", 8),
        ["round", "92: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 92: a worker pulls the next task from the queue", 12),
        ["round 92: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 92: a worker pulls the next task from the queue", 16),
        ["round 92: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 92: a worker pulls the next task from the queue", 24),
        ["round 92: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 92: a worker pulls the next task from the queue", 32),
        ["round 92: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 92: signals travel through the network layer", 4),
        ["round", "92:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 92: signals travel through the network layer", 8),
        ["round", "92:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 92: signals travel through the network layer", 12),
        ["round 92:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 92: signals travel through the network layer", 16),
        ["round 92:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 92: signals travel through the network layer", 24),
        ["round 92: signals travel", "through the network", "layer"],
    ),
    (
        ("round 92: signals travel through the network layer", 32),
        ["round 92: signals travel through", "the network layer"],
    ),
    (
        ("round 92: the gateway routes each request by policy", 4),
        ["round", "92:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 92: the gateway routes each request by policy", 8),
        ["round", "92: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 92: the gateway routes each request by policy", 12),
        ["round 92:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 92: the gateway routes each request by policy", 16),
        ["round 92: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 92: the gateway routes each request by policy", 24),
        ["round 92: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 92: the gateway routes each request by policy", 32),
        ["round 92: the gateway routes", "each request by policy"],
    ),
    (
        ("round 92: memory grows until the buffer is full", 4),
        ["round", "92:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 92: memory grows until the buffer is full", 8),
        ["round", "92:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 92: memory grows until the buffer is full", 12),
        ["round 92:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 92: memory grows until the buffer is full", 16),
        ["round 92: memory", "grows until the", "buffer is full"],
    ),
    (("round 92: memory grows until the buffer is full", 24), ["round 92: memory grows", "until the buffer is full"]),
    (("round 92: memory grows until the buffer is full", 32), ["round 92: memory grows until the", "buffer is full"]),
    (
        ("round 92: the cluster mirrors every packet twice", 4),
        ["round", "92:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 92: the cluster mirrors every packet twice", 8),
        ["round", "92: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 92: the cluster mirrors every packet twice", 12),
        ["round 92:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 92: the cluster mirrors every packet twice", 16),
        ["round 92: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 92: the cluster mirrors every packet twice", 24),
        ["round 92: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 92: the cluster mirrors every packet twice", 32), ["round 92: the cluster mirrors", "every packet twice"]),
    (
        ("round 92: ranking uses tokens learned from the corpus", 4),
        ["round", "92:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 92: ranking uses tokens learned from the corpus", 8),
        ["round", "92:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 92: ranking uses tokens learned from the corpus", 12),
        ["round 92:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 92: ranking uses tokens learned from the corpus", 16),
        ["round 92:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 92: ranking uses tokens learned from the corpus", 24),
        ["round 92: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 92: ranking uses tokens learned from the corpus", 32),
        ["round 92: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 92: a long session ends when the candle dies", 4),
        ["round", "92:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 92: a long session ends when the candle dies", 8),
        ["round", "92: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 92: a long session ends when the candle dies", 12),
        ["round 92: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 92: a long session ends when the candle dies", 16),
        ["round 92: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 92: a long session ends when the candle dies", 24),
        ["round 92: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 92: a long session ends when the candle dies", 32),
        ["round 92: a long session ends", "when the candle dies"],
    ),
    (
        ("round 92: encode the prompt then map the result", 4),
        ["round", "92:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 92: encode the prompt then map the result", 8),
        ["round", "92:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 92: encode the prompt then map the result", 12),
        ["round 92:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 92: encode the prompt then map the result", 16),
        ["round 92: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 92: encode the prompt then map the result", 24),
        ["round 92: encode the", "prompt then map the", "result"],
    ),
    (("round 92: encode the prompt then map the result", 32), ["round 92: encode the prompt then", "map the result"]),
    (
        ("round 92: the kernel wakes the worker at dawn", 4),
        ["round", "92:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 92: the kernel wakes the worker at dawn", 8),
        ["round", "92: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 92: the kernel wakes the worker at dawn", 12),
        ["round 92:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 92: the kernel wakes the worker at dawn", 16), ["round 92: the", "kernel wakes the", "worker at dawn"]),
    (("round 92: the kernel wakes the worker at dawn", 24), ["round 92: the kernel", "wakes the worker at dawn"]),
    (("round 92: the kernel wakes the worker at dawn", 32), ["round 92: the kernel wakes the", "worker at dawn"]),
    (
        ("round 92: service latency drops after the patch", 4),
        ["round", "92:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 92: service latency drops after the patch", 8),
        ["round", "92:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 92: service latency drops after the patch", 12),
        ["round 92:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 92: service latency drops after the patch", 16),
        ["round 92:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 92: service latency drops after the patch", 24),
        ["round 92: service", "latency drops after the", "patch"],
    ),
    (("round 92: service latency drops after the patch", 32), ["round 92: service latency drops", "after the patch"]),
    (
        ("round 92: the library caches every vector it sees", 4),
        ["round", "92:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 92: the library caches every vector it sees", 8),
        ["round", "92: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 92: the library caches every vector it sees", 12),
        ["round 92:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 92: the library caches every vector it sees", 16),
        ["round 92: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 92: the library caches every vector it sees", 24),
        ["round 92: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 92: the library caches every vector it sees", 32),
        ["round 92: the library caches", "every vector it sees"],
    ),
    (
        ("round 92: agents argue then the debate resolves", 4),
        ["round", "92:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 92: agents argue then the debate resolves", 8),
        ["round", "92:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 92: agents argue then the debate resolves", 12),
        ["round 92:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 92: agents argue then the debate resolves", 16),
        ["round 92: agents", "argue then the", "debate resolves"],
    ),
    (("round 92: agents argue then the debate resolves", 24), ["round 92: agents argue", "then the debate resolves"]),
    (("round 92: agents argue then the debate resolves", 32), ["round 92: agents argue then the", "debate resolves"]),
    (
        ("round 92: the filter keeps only strong matches", 4),
        ["round", "92:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 92: the filter keeps only strong matches", 8),
        ["round", "92: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 92: the filter keeps only strong matches", 12),
        ["round 92:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 92: the filter keeps only strong matches", 16),
        ["round 92: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 92: the filter keeps only strong matches", 24), ["round 92: the filter", "keeps only strong", "matches"]),
    (("round 92: the filter keeps only strong matches", 32), ["round 92: the filter keeps only", "strong matches"]),
    (
        ("round 92: the model answers with a short reply", 4),
        ["round", "92:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 92: the model answers with a short reply", 8),
        ["round", "92: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 92: the model answers with a short reply", 12),
        ["round 92:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 92: the model answers with a short reply", 16),
        ["round 92: the", "model answers", "with a short", "reply"],
    ),
    (("round 92: the model answers with a short reply", 24), ["round 92: the model", "answers with a short", "reply"]),
    (("round 92: the model answers with a short reply", 32), ["round 92: the model answers with", "a short reply"]),
    (
        ("round 92: the recorder stores the reasoning trace", 4),
        ["round", "92:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 92: the recorder stores the reasoning trace", 8),
        ["round", "92: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 92: the recorder stores the reasoning trace", 12),
        ["round 92:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 92: the recorder stores the reasoning trace", 16),
        ["round 92: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 92: the recorder stores the reasoning trace", 24),
        ["round 92: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 92: the recorder stores the reasoning trace", 32),
        ["round 92: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 92: the angel watches the processor run", 4),
        ["round", "92:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 92: the angel watches the processor run", 8),
        ["round", "92: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 92: the angel watches the processor run", 12),
        ["round 92:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 92: the angel watches the processor run", 16), ["round 92: the", "angel watches", "the processor", "run"]),
    (("round 92: the angel watches the processor run", 24), ["round 92: the angel", "watches the processor", "run"]),
    (("round 92: the angel watches the processor run", 32), ["round 92: the angel watches the", "processor run"]),
    (
        ("round 92: angle of the vector decides the match", 4),
        ["round", "92:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 92: angle of the vector decides the match", 8),
        ["round", "92:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 92: angle of the vector decides the match", 12),
        ["round 92:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 92: angle of the vector decides the match", 16),
        ["round 92: angle", "of the vector", "decides the", "match"],
    ),
    (("round 92: angle of the vector decides the match", 24), ["round 92: angle of the", "vector decides the match"]),
    (("round 92: angle of the vector decides the match", 32), ["round 92: angle of the vector", "decides the match"]),
    (
        ("round 92: the candle burns twice as long at night", 4),
        ["round", "92:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 92: the candle burns twice as long at night", 8),
        ["round", "92: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 92: the candle burns twice as long at night", 12),
        ["round 92:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 92: the candle burns twice as long at night", 16),
        ["round 92: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 92: the candle burns twice as long at night", 24),
        ["round 92: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 92: the candle burns twice as long at night", 32),
        ["round 92: the candle burns twice", "as long at night"],
    ),
    (
        ("round 92: a mirror of the universe in one line", 4),
        ["round", "92:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 92: a mirror of the universe in one line", 8),
        ["round", "92: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 92: a mirror of the universe in one line", 12),
        ["round 92: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 92: a mirror of the universe in one line", 16),
        ["round 92: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 92: a mirror of the universe in one line", 24), ["round 92: a mirror of", "the universe in one line"]),
    (("round 92: a mirror of the universe in one line", 32), ["round 92: a mirror of the", "universe in one line"]),
    (
        ("round 92: the queue drains before the storm", 4),
        ["round", "92:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 92: the queue drains before the storm", 8),
        ["round", "92: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 92: the queue drains before the storm", 12), ["round 92:", "the queue", "drains", "before the", "storm"]),
    (("round 92: the queue drains before the storm", 16), ["round 92: the", "queue drains", "before the storm"]),
    (("round 92: the queue drains before the storm", 24), ["round 92: the queue", "drains before the storm"]),
    (("round 92: the queue drains before the storm", 32), ["round 92: the queue drains", "before the storm"]),
    (
        ("kitten92 sitting92 agent92 angle92 universe92 memory92", 6),
        ["kitten92", "sitting92", "agent92", "angle92", "universe92", "memory92"],
    ),
    (
        ("kitten92 sitting92 agent92 angle92 universe92 memory92", 10),
        ["kitten92", "sitting92", "agent92", "angle92", "universe92", "memory92"],
    ),
    (
        ("kitten92 sitting92 agent92 angle92 universe92 memory92", 18),
        ["kitten92 sitting92", "agent92 angle92", "universe92", "memory92"],
    ),
    (
        ("kitten92 sitting92 agent92 angle92 universe92 memory92", 28),
        ["kitten92 sitting92 agent92", "angle92 universe92 memory92"],
    ),
    (
        ("sitting92 agent92 angle92 universe92 memory92 stream92", 6),
        ["sitting92", "agent92", "angle92", "universe92", "memory92", "stream92"],
    ),
    (
        ("sitting92 agent92 angle92 universe92 memory92 stream92", 10),
        ["sitting92", "agent92", "angle92", "universe92", "memory92", "stream92"],
    ),
    (
        ("sitting92 agent92 angle92 universe92 memory92 stream92", 18),
        ["sitting92 agent92", "angle92 universe92", "memory92 stream92"],
    ),
    (
        ("sitting92 agent92 angle92 universe92 memory92 stream92", 28),
        ["sitting92 agent92 angle92", "universe92 memory92 stream92"],
    ),
    (
        ("agent92 angle92 universe92 memory92 stream92 context92", 6),
        ["agent92", "angle92", "universe92", "memory92", "stream92", "context92"],
    ),
    (
        ("agent92 angle92 universe92 memory92 stream92 context92", 10),
        ["agent92", "angle92", "universe92", "memory92", "stream92", "context92"],
    ),
    (
        ("agent92 angle92 universe92 memory92 stream92 context92", 18),
        ["agent92 angle92", "universe92", "memory92 stream92", "context92"],
    ),
    (
        ("agent92 angle92 universe92 memory92 stream92 context92", 28),
        ["agent92 angle92 universe92", "memory92 stream92 context92"],
    ),
    (
        ("angle92 universe92 memory92 stream92 context92 knowledge92", 6),
        ["angle92", "universe92", "memory92", "stream92", "context92", "knowledge92"],
    ),
    (
        ("angle92 universe92 memory92 stream92 context92 knowledge92", 10),
        ["angle92", "universe92", "memory92", "stream92", "context92", "knowledge92"],
    ),
    (
        ("angle92 universe92 memory92 stream92 context92 knowledge92", 18),
        ["angle92 universe92", "memory92 stream92", "context92", "knowledge92"],
    ),
    (
        ("angle92 universe92 memory92 stream92 context92 knowledge92", 28),
        ["angle92 universe92 memory92", "stream92 context92", "knowledge92"],
    ),
    (
        ("universe92 memory92 stream92 context92 knowledge92 vector92", 6),
        ["universe92", "memory92", "stream92", "context92", "knowledge92", "vector92"],
    ),
    (
        ("universe92 memory92 stream92 context92 knowledge92 vector92", 10),
        ["universe92", "memory92", "stream92", "context92", "knowledge92", "vector92"],
    ),
    (
        ("universe92 memory92 stream92 context92 knowledge92 vector92", 18),
        ["universe92", "memory92 stream92", "context92", "knowledge92", "vector92"],
    ),
    (
        ("universe92 memory92 stream92 context92 knowledge92 vector92", 28),
        ["universe92 memory92 stream92", "context92 knowledge92", "vector92"],
    ),
    (
        ("memory92 stream92 context92 knowledge92 vector92 processor92", 6),
        ["memory92", "stream92", "context92", "knowledge92", "vector92", "processor92"],
    ),
    (
        ("memory92 stream92 context92 knowledge92 vector92 processor92", 10),
        ["memory92", "stream92", "context92", "knowledge92", "vector92", "processor92"],
    ),
    (
        ("memory92 stream92 context92 knowledge92 vector92 processor92", 18),
        ["memory92 stream92", "context92", "knowledge92", "vector92", "processor92"],
    ),
    (
        ("memory92 stream92 context92 knowledge92 vector92 processor92", 28),
        ["memory92 stream92 context92", "knowledge92 vector92", "processor92"],
    ),
    (
        ("stream92 context92 knowledge92 vector92 processor92 reasoning92", 6),
        ["stream92", "context92", "knowledge92", "vector92", "processor92", "reasoning92"],
    ),
    (
        ("stream92 context92 knowledge92 vector92 processor92 reasoning92", 10),
        ["stream92", "context92", "knowledge92", "vector92", "processor92", "reasoning92"],
    ),
    (
        ("stream92 context92 knowledge92 vector92 processor92 reasoning92", 18),
        ["stream92 context92", "knowledge92", "vector92", "processor92", "reasoning92"],
    ),
    (
        ("stream92 context92 knowledge92 vector92 processor92 reasoning92", 28),
        ["stream92 context92", "knowledge92 vector92", "processor92 reasoning92"],
    ),
    (
        ("context92 knowledge92 vector92 processor92 reasoning92 machine92", 6),
        ["context92", "knowledge92", "vector92", "processor92", "reasoning92", "machine92"],
    ),
    (
        ("context92 knowledge92 vector92 processor92 reasoning92 machine92", 10),
        ["context92", "knowledge92", "vector92", "processor92", "reasoning92", "machine92"],
    ),
    (
        ("context92 knowledge92 vector92 processor92 reasoning92 machine92", 18),
        ["context92", "knowledge92", "vector92", "processor92", "reasoning92", "machine92"],
    ),
    (
        ("context92 knowledge92 vector92 processor92 reasoning92 machine92", 28),
        ["context92 knowledge92", "vector92 processor92", "reasoning92 machine92"],
    ),
    (
        ("knowledge92 vector92 processor92 reasoning92 machine92 learning92", 6),
        ["knowledge92", "vector92", "processor92", "reasoning92", "machine92", "learning92"],
    ),
    (
        ("knowledge92 vector92 processor92 reasoning92 machine92 learning92", 10),
        ["knowledge92", "vector92", "processor92", "reasoning92", "machine92", "learning92"],
    ),
    (
        ("knowledge92 vector92 processor92 reasoning92 machine92 learning92", 18),
        ["knowledge92", "vector92", "processor92", "reasoning92", "machine92", "learning92"],
    ),
    (
        ("knowledge92 vector92 processor92 reasoning92 machine92 learning92", 28),
        ["knowledge92 vector92", "processor92 reasoning92", "machine92 learning92"],
    ),
    (
        ("vector92 processor92 reasoning92 machine92 learning92 model92", 6),
        ["vector92", "processor92", "reasoning92", "machine92", "learning92", "model92"],
    ),
    (
        ("vector92 processor92 reasoning92 machine92 learning92 model92", 10),
        ["vector92", "processor92", "reasoning92", "machine92", "learning92", "model92"],
    ),
    (
        ("vector92 processor92 reasoning92 machine92 learning92 model92", 18),
        ["vector92", "processor92", "reasoning92", "machine92", "learning92 model92"],
    ),
    (
        ("vector92 processor92 reasoning92 machine92 learning92 model92", 28),
        ["vector92 processor92", "reasoning92 machine92", "learning92 model92"],
    ),
    (
        ("processor92 reasoning92 machine92 learning92 model92 token92", 6),
        ["processor92", "reasoning92", "machine92", "learning92", "model92", "token92"],
    ),
    (
        ("processor92 reasoning92 machine92 learning92 model92 token92", 10),
        ["processor92", "reasoning92", "machine92", "learning92", "model92", "token92"],
    ),
    (
        ("processor92 reasoning92 machine92 learning92 model92 token92", 18),
        ["processor92", "reasoning92", "machine92", "learning92 model92", "token92"],
    ),
    (
        ("processor92 reasoning92 machine92 learning92 model92 token92", 28),
        ["processor92 reasoning92", "machine92 learning92 model92", "token92"],
    ),
    (
        ("reasoning92 machine92 learning92 model92 token92 prompt92", 6),
        ["reasoning92", "machine92", "learning92", "model92", "token92", "prompt92"],
    ),
    (
        ("reasoning92 machine92 learning92 model92 token92 prompt92", 10),
        ["reasoning92", "machine92", "learning92", "model92", "token92", "prompt92"],
    ),
    (
        ("reasoning92 machine92 learning92 model92 token92 prompt92", 18),
        ["reasoning92", "machine92", "learning92 model92", "token92 prompt92"],
    ),
    (
        ("reasoning92 machine92 learning92 model92 token92 prompt92", 28),
        ["reasoning92 machine92", "learning92 model92 token92", "prompt92"],
    ),
    (
        ("machine92 learning92 model92 token92 prompt92 session92", 6),
        ["machine92", "learning92", "model92", "token92", "prompt92", "session92"],
    ),
    (
        ("machine92 learning92 model92 token92 prompt92 session92", 10),
        ["machine92", "learning92", "model92", "token92", "prompt92", "session92"],
    ),
    (
        ("machine92 learning92 model92 token92 prompt92 session92", 18),
        ["machine92", "learning92 model92", "token92 prompt92", "session92"],
    ),
    (
        ("machine92 learning92 model92 token92 prompt92 session92", 28),
        ["machine92 learning92 model92", "token92 prompt92 session92"],
    ),
    (
        ("learning92 model92 token92 prompt92 session92 library92", 6),
        ["learning92", "model92", "token92", "prompt92", "session92", "library92"],
    ),
    (
        ("learning92 model92 token92 prompt92 session92 library92", 10),
        ["learning92", "model92", "token92", "prompt92", "session92", "library92"],
    ),
    (
        ("learning92 model92 token92 prompt92 session92 library92", 18),
        ["learning92 model92", "token92 prompt92", "session92", "library92"],
    ),
    (
        ("learning92 model92 token92 prompt92 session92 library92", 28),
        ["learning92 model92 token92", "prompt92 session92 library92"],
    ),
    (
        ("model92 token92 prompt92 session92 library92 service92", 6),
        ["model92", "token92", "prompt92", "session92", "library92", "service92"],
    ),
    (
        ("model92 token92 prompt92 session92 library92 service92", 10),
        ["model92", "token92", "prompt92", "session92", "library92", "service92"],
    ),
    (
        ("model92 token92 prompt92 session92 library92 service92", 18),
        ["model92 token92", "prompt92 session92", "library92", "service92"],
    ),
    (
        ("model92 token92 prompt92 session92 library92 service92", 28),
        ["model92 token92 prompt92", "session92 library92", "service92"],
    ),
    (
        ("token92 prompt92 session92 library92 service92 gateway92", 6),
        ["token92", "prompt92", "session92", "library92", "service92", "gateway92"],
    ),
    (
        ("token92 prompt92 session92 library92 service92 gateway92", 10),
        ["token92", "prompt92", "session92", "library92", "service92", "gateway92"],
    ),
    (
        ("token92 prompt92 session92 library92 service92 gateway92", 18),
        ["token92 prompt92", "session92", "library92", "service92", "gateway92"],
    ),
    (
        ("token92 prompt92 session92 library92 service92 gateway92", 28),
        ["token92 prompt92 session92", "library92 service92", "gateway92"],
    ),
    (
        ("prompt92 session92 library92 service92 gateway92 storage92", 6),
        ["prompt92", "session92", "library92", "service92", "gateway92", "storage92"],
    ),
    (
        ("prompt92 session92 library92 service92 gateway92 storage92", 10),
        ["prompt92", "session92", "library92", "service92", "gateway92", "storage92"],
    ),
    (
        ("prompt92 session92 library92 service92 gateway92 storage92", 18),
        ["prompt92 session92", "library92", "service92", "gateway92", "storage92"],
    ),
    (
        ("prompt92 session92 library92 service92 gateway92 storage92", 28),
        ["prompt92 session92 library92", "service92 gateway92", "storage92"],
    ),
    (
        ("session92 library92 service92 gateway92 storage92 network92", 6),
        ["session92", "library92", "service92", "gateway92", "storage92", "network92"],
    ),
    (
        ("session92 library92 service92 gateway92 storage92 network92", 10),
        ["session92", "library92", "service92", "gateway92", "storage92", "network92"],
    ),
    (
        ("session92 library92 service92 gateway92 storage92 network92", 18),
        ["session92", "library92", "service92", "gateway92", "storage92", "network92"],
    ),
    (
        ("session92 library92 service92 gateway92 storage92 network92", 28),
        ["session92 library92", "service92 gateway92", "storage92 network92"],
    ),
    (
        ("library92 service92 gateway92 storage92 network92 latency92", 6),
        ["library92", "service92", "gateway92", "storage92", "network92", "latency92"],
    ),
    (
        ("library92 service92 gateway92 storage92 network92 latency92", 10),
        ["library92", "service92", "gateway92", "storage92", "network92", "latency92"],
    ),
    (
        ("library92 service92 gateway92 storage92 network92 latency92", 18),
        ["library92", "service92", "gateway92", "storage92", "network92", "latency92"],
    ),
    (
        ("library92 service92 gateway92 storage92 network92 latency92", 28),
        ["library92 service92", "gateway92 storage92", "network92 latency92"],
    ),
    (
        ("service92 gateway92 storage92 network92 latency92 buffer92", 6),
        ["service92", "gateway92", "storage92", "network92", "latency92", "buffer92"],
    ),
    (
        ("service92 gateway92 storage92 network92 latency92 buffer92", 10),
        ["service92", "gateway92", "storage92", "network92", "latency92", "buffer92"],
    ),
    (
        ("service92 gateway92 storage92 network92 latency92 buffer92", 18),
        ["service92", "gateway92", "storage92", "network92", "latency92 buffer92"],
    ),
    (
        ("service92 gateway92 storage92 network92 latency92 buffer92", 28),
        ["service92 gateway92", "storage92 network92", "latency92 buffer92"],
    ),
    (
        ("gateway92 storage92 network92 latency92 buffer92 queue92", 6),
        ["gateway92", "storage92", "network92", "latency92", "buffer92", "queue92"],
    ),
    (
        ("gateway92 storage92 network92 latency92 buffer92 queue92", 10),
        ["gateway92", "storage92", "network92", "latency92", "buffer92", "queue92"],
    ),
    (
        ("gateway92 storage92 network92 latency92 buffer92 queue92", 18),
        ["gateway92", "storage92", "network92", "latency92 buffer92", "queue92"],
    ),
    (
        ("gateway92 storage92 network92 latency92 buffer92 queue92", 28),
        ["gateway92 storage92", "network92 latency92 buffer92", "queue92"],
    ),
    (
        ("storage92 network92 latency92 buffer92 queue92 worker92", 6),
        ["storage92", "network92", "latency92", "buffer92", "queue92", "worker92"],
    ),
    (
        ("storage92 network92 latency92 buffer92 queue92 worker92", 10),
        ["storage92", "network92", "latency92", "buffer92", "queue92", "worker92"],
    ),
    (
        ("storage92 network92 latency92 buffer92 queue92 worker92", 18),
        ["storage92", "network92", "latency92 buffer92", "queue92 worker92"],
    ),
    (
        ("storage92 network92 latency92 buffer92 queue92 worker92", 28),
        ["storage92 network92", "latency92 buffer92 queue92", "worker92"],
    ),
    (
        ("network92 latency92 buffer92 queue92 worker92 kernel92", 6),
        ["network92", "latency92", "buffer92", "queue92", "worker92", "kernel92"],
    ),
    (
        ("network92 latency92 buffer92 queue92 worker92 kernel92", 10),
        ["network92", "latency92", "buffer92", "queue92", "worker92", "kernel92"],
    ),
    (
        ("network92 latency92 buffer92 queue92 worker92 kernel92", 18),
        ["network92", "latency92 buffer92", "queue92 worker92", "kernel92"],
    ),
    (
        ("network92 latency92 buffer92 queue92 worker92 kernel92", 28),
        ["network92 latency92 buffer92", "queue92 worker92 kernel92"],
    ),
    (
        ("latency92 buffer92 queue92 worker92 kernel92 signal92", 6),
        ["latency92", "buffer92", "queue92", "worker92", "kernel92", "signal92"],
    ),
    (
        ("latency92 buffer92 queue92 worker92 kernel92 signal92", 10),
        ["latency92", "buffer92", "queue92", "worker92", "kernel92", "signal92"],
    ),
    (
        ("latency92 buffer92 queue92 worker92 kernel92 signal92", 18),
        ["latency92 buffer92", "queue92 worker92", "kernel92 signal92"],
    ),
    (
        ("latency92 buffer92 queue92 worker92 kernel92 signal92", 28),
        ["latency92 buffer92 queue92", "worker92 kernel92 signal92"],
    ),
    (
        ("buffer92 queue92 worker92 kernel92 signal92 packet92", 6),
        ["buffer92", "queue92", "worker92", "kernel92", "signal92", "packet92"],
    ),
    (
        ("buffer92 queue92 worker92 kernel92 signal92 packet92", 10),
        ["buffer92", "queue92", "worker92", "kernel92", "signal92", "packet92"],
    ),
    (
        ("buffer92 queue92 worker92 kernel92 signal92 packet92", 18),
        ["buffer92 queue92", "worker92 kernel92", "signal92 packet92"],
    ),
    (
        ("buffer92 queue92 worker92 kernel92 signal92 packet92", 28),
        ["buffer92 queue92 worker92", "kernel92 signal92 packet92"],
    ),
    (
        ("queue92 worker92 kernel92 signal92 packet92 router92", 6),
        ["queue92", "worker92", "kernel92", "signal92", "packet92", "router92"],
    ),
    (
        ("queue92 worker92 kernel92 signal92 packet92 router92", 10),
        ["queue92", "worker92", "kernel92", "signal92", "packet92", "router92"],
    ),
    (
        ("queue92 worker92 kernel92 signal92 packet92 router92", 18),
        ["queue92 worker92", "kernel92 signal92", "packet92 router92"],
    ),
    (
        ("queue92 worker92 kernel92 signal92 packet92 router92", 28),
        ["queue92 worker92 kernel92", "signal92 packet92 router92"],
    ),
    (
        ("worker92 kernel92 signal92 packet92 router92 cluster92", 6),
        ["worker92", "kernel92", "signal92", "packet92", "router92", "cluster92"],
    ),
    (
        ("worker92 kernel92 signal92 packet92 router92 cluster92", 10),
        ["worker92", "kernel92", "signal92", "packet92", "router92", "cluster92"],
    ),
    (
        ("worker92 kernel92 signal92 packet92 router92 cluster92", 18),
        ["worker92 kernel92", "signal92 packet92", "router92 cluster92"],
    ),
    (
        ("worker92 kernel92 signal92 packet92 router92 cluster92", 28),
        ["worker92 kernel92 signal92", "packet92 router92 cluster92"],
    ),
    (
        ("kernel92 signal92 packet92 router92 cluster92 mirror92", 6),
        ["kernel92", "signal92", "packet92", "router92", "cluster92", "mirror92"],
    ),
    (
        ("kernel92 signal92 packet92 router92 cluster92 mirror92", 10),
        ["kernel92", "signal92", "packet92", "router92", "cluster92", "mirror92"],
    ),
    (
        ("kernel92 signal92 packet92 router92 cluster92 mirror92", 18),
        ["kernel92 signal92", "packet92 router92", "cluster92 mirror92"],
    ),
    (
        ("kernel92 signal92 packet92 router92 cluster92 mirror92", 28),
        ["kernel92 signal92 packet92", "router92 cluster92 mirror92"],
    ),
    (
        ("signal92 packet92 router92 cluster92 mirror92 filter92", 6),
        ["signal92", "packet92", "router92", "cluster92", "mirror92", "filter92"],
    ),
    (
        ("signal92 packet92 router92 cluster92 mirror92 filter92", 10),
        ["signal92", "packet92", "router92", "cluster92", "mirror92", "filter92"],
    ),
    (
        ("signal92 packet92 router92 cluster92 mirror92 filter92", 18),
        ["signal92 packet92", "router92 cluster92", "mirror92 filter92"],
    ),
    (
        ("signal92 packet92 router92 cluster92 mirror92 filter92", 28),
        ["signal92 packet92 router92", "cluster92 mirror92 filter92"],
    ),
    (
        ("packet92 router92 cluster92 mirror92 filter92 ranking92", 6),
        ["packet92", "router92", "cluster92", "mirror92", "filter92", "ranking92"],
    ),
    (
        ("packet92 router92 cluster92 mirror92 filter92 ranking92", 10),
        ["packet92", "router92", "cluster92", "mirror92", "filter92", "ranking92"],
    ),
    (
        ("packet92 router92 cluster92 mirror92 filter92 ranking92", 18),
        ["packet92 router92", "cluster92 mirror92", "filter92 ranking92"],
    ),
    (
        ("packet92 router92 cluster92 mirror92 filter92 ranking92", 28),
        ["packet92 router92 cluster92", "mirror92 filter92 ranking92"],
    ),
    (
        ("router92 cluster92 mirror92 filter92 ranking92 encoding92", 6),
        ["router92", "cluster92", "mirror92", "filter92", "ranking92", "encoding92"],
    ),
    (
        ("router92 cluster92 mirror92 filter92 ranking92 encoding92", 10),
        ["router92", "cluster92", "mirror92", "filter92", "ranking92", "encoding92"],
    ),
    (
        ("router92 cluster92 mirror92 filter92 ranking92 encoding92", 18),
        ["router92 cluster92", "mirror92 filter92", "ranking92", "encoding92"],
    ),
    (
        ("router92 cluster92 mirror92 filter92 ranking92 encoding92", 28),
        ["router92 cluster92 mirror92", "filter92 ranking92", "encoding92"],
    ),
    (
        ("cluster92 mirror92 filter92 ranking92 encoding92 mapping92", 6),
        ["cluster92", "mirror92", "filter92", "ranking92", "encoding92", "mapping92"],
    ),
    (
        ("cluster92 mirror92 filter92 ranking92 encoding92 mapping92", 10),
        ["cluster92", "mirror92", "filter92", "ranking92", "encoding92", "mapping92"],
    ),
    (
        ("cluster92 mirror92 filter92 ranking92 encoding92 mapping92", 18),
        ["cluster92 mirror92", "filter92 ranking92", "encoding92", "mapping92"],
    ),
    (
        ("cluster92 mirror92 filter92 ranking92 encoding92 mapping92", 28),
        ["cluster92 mirror92 filter92", "ranking92 encoding92", "mapping92"],
    ),
    (
        ("mirror92 filter92 ranking92 encoding92 mapping92 record92", 6),
        ["mirror92", "filter92", "ranking92", "encoding92", "mapping92", "record92"],
    ),
    (
        ("mirror92 filter92 ranking92 encoding92 mapping92 record92", 10),
        ["mirror92", "filter92", "ranking92", "encoding92", "mapping92", "record92"],
    ),
    (
        ("mirror92 filter92 ranking92 encoding92 mapping92 record92", 18),
        ["mirror92 filter92", "ranking92", "encoding92", "mapping92 record92"],
    ),
    (
        ("mirror92 filter92 ranking92 encoding92 mapping92 record92", 28),
        ["mirror92 filter92 ranking92", "encoding92 mapping92", "record92"],
    ),
    (
        ("filter92 ranking92 encoding92 mapping92 record92 candle92", 6),
        ["filter92", "ranking92", "encoding92", "mapping92", "record92", "candle92"],
    ),
    (
        ("filter92 ranking92 encoding92 mapping92 record92 candle92", 10),
        ["filter92", "ranking92", "encoding92", "mapping92", "record92", "candle92"],
    ),
    (
        ("filter92 ranking92 encoding92 mapping92 record92 candle92", 18),
        ["filter92 ranking92", "encoding92", "mapping92 record92", "candle92"],
    ),
    (
        ("filter92 ranking92 encoding92 mapping92 record92 candle92", 28),
        ["filter92 ranking92", "encoding92 mapping92", "record92 candle92"],
    ),
    (
        ("ranking92 encoding92 mapping92 record92 candle92 thread92", 6),
        ["ranking92", "encoding92", "mapping92", "record92", "candle92", "thread92"],
    ),
    (
        ("ranking92 encoding92 mapping92 record92 candle92 thread92", 10),
        ["ranking92", "encoding92", "mapping92", "record92", "candle92", "thread92"],
    ),
    (
        ("ranking92 encoding92 mapping92 record92 candle92 thread92", 18),
        ["ranking92", "encoding92", "mapping92 record92", "candle92 thread92"],
    ),
    (
        ("ranking92 encoding92 mapping92 record92 candle92 thread92", 28),
        ["ranking92 encoding92", "mapping92 record92 candle92", "thread92"],
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
