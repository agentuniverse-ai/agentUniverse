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
        ("round 198: the quick brown fox jumps over the lazy dog", 4),
        ["round", "198:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", 8),
        ["round", "198: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", 12),
        ["round 198:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", 16),
        ["round 198: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", 24),
        ["round 198: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 198: the quick brown fox jumps over the lazy dog", 32),
        ["round 198: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", 4),
        ["round", "198:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", 8),
        ["round", "198:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", 12),
        ["round 198:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", 16),
        ["round 198:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", 24),
        ["round 198: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 198: agentuniverse is a framework for multi agents", 32),
        ["round 198: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", 4),
        ["round", "198:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", 8),
        ["round", "198:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", 12),
        ["round 198:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", 16),
        ["round 198:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", 24),
        ["round 198: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 198: knowledge stored as vectors enables retrieval", 32),
        ["round 198: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 198: the processor reads the record then stops", 4),
        ["round", "198:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 198: the processor reads the record then stops", 8),
        ["round", "198: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 198: the processor reads the record then stops", 12),
        ["round 198:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 198: the processor reads the record then stops", 16),
        ["round 198: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 198: the processor reads the record then stops", 24),
        ["round 198: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 198: the processor reads the record then stops", 32),
        ["round 198: the processor reads", "the record then stops"],
    ),
    (
        ("round 198: a worker pulls the next task from the queue", 4),
        ["round", "198:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 198: a worker pulls the next task from the queue", 8),
        ["round", "198: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 198: a worker pulls the next task from the queue", 12),
        ["round 198: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 198: a worker pulls the next task from the queue", 16),
        ["round 198: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 198: a worker pulls the next task from the queue", 24),
        ["round 198: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 198: a worker pulls the next task from the queue", 32),
        ["round 198: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 198: signals travel through the network layer", 4),
        ["round", "198:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 198: signals travel through the network layer", 8),
        ["round", "198:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 198: signals travel through the network layer", 12),
        ["round 198:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 198: signals travel through the network layer", 16),
        ["round 198:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 198: signals travel through the network layer", 24),
        ["round 198: signals", "travel through the", "network layer"],
    ),
    (
        ("round 198: signals travel through the network layer", 32),
        ["round 198: signals travel", "through the network layer"],
    ),
    (
        ("round 198: the gateway routes each request by policy", 4),
        ["round", "198:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 198: the gateway routes each request by policy", 8),
        ["round", "198: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 198: the gateway routes each request by policy", 12),
        ["round 198:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 198: the gateway routes each request by policy", 16),
        ["round 198: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 198: the gateway routes each request by policy", 24),
        ["round 198: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 198: the gateway routes each request by policy", 32),
        ["round 198: the gateway routes", "each request by policy"],
    ),
    (
        ("round 198: memory grows until the buffer is full", 4),
        ["round", "198:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 198: memory grows until the buffer is full", 8),
        ["round", "198:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 198: memory grows until the buffer is full", 12),
        ["round 198:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 198: memory grows until the buffer is full", 16),
        ["round 198:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 198: memory grows until the buffer is full", 24), ["round 198: memory grows", "until the buffer is full"]),
    (("round 198: memory grows until the buffer is full", 32), ["round 198: memory grows until", "the buffer is full"]),
    (
        ("round 198: the cluster mirrors every packet twice", 4),
        ["round", "198:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 198: the cluster mirrors every packet twice", 8),
        ["round", "198: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 198: the cluster mirrors every packet twice", 12),
        ["round 198:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 198: the cluster mirrors every packet twice", 16),
        ["round 198: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 198: the cluster mirrors every packet twice", 24),
        ["round 198: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 198: the cluster mirrors every packet twice", 32),
        ["round 198: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", 4),
        ["round", "198:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", 8),
        ["round", "198:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", 12),
        ["round 198:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", 16),
        ["round 198:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", 24),
        ["round 198: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 198: ranking uses tokens learned from the corpus", 32),
        ["round 198: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 198: a long session ends when the candle dies", 4),
        ["round", "198:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 198: a long session ends when the candle dies", 8),
        ["round", "198: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 198: a long session ends when the candle dies", 12),
        ["round 198: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 198: a long session ends when the candle dies", 16),
        ["round 198: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 198: a long session ends when the candle dies", 24),
        ["round 198: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 198: a long session ends when the candle dies", 32),
        ["round 198: a long session ends", "when the candle dies"],
    ),
    (
        ("round 198: encode the prompt then map the result", 4),
        ["round", "198:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 198: encode the prompt then map the result", 8),
        ["round", "198:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 198: encode the prompt then map the result", 12),
        ["round 198:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 198: encode the prompt then map the result", 16),
        ["round 198:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 198: encode the prompt then map the result", 24),
        ["round 198: encode the", "prompt then map the", "result"],
    ),
    (("round 198: encode the prompt then map the result", 32), ["round 198: encode the prompt", "then map the result"]),
    (
        ("round 198: the kernel wakes the worker at dawn", 4),
        ["round", "198:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 198: the kernel wakes the worker at dawn", 8),
        ["round", "198: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 198: the kernel wakes the worker at dawn", 12),
        ["round 198:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 198: the kernel wakes the worker at dawn", 16), ["round 198: the", "kernel wakes the", "worker at dawn"]),
    (("round 198: the kernel wakes the worker at dawn", 24), ["round 198: the kernel", "wakes the worker at dawn"]),
    (("round 198: the kernel wakes the worker at dawn", 32), ["round 198: the kernel wakes the", "worker at dawn"]),
    (
        ("round 198: service latency drops after the patch", 4),
        ["round", "198:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 198: service latency drops after the patch", 8),
        ["round", "198:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 198: service latency drops after the patch", 12),
        ["round 198:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 198: service latency drops after the patch", 16),
        ["round 198:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 198: service latency drops after the patch", 24),
        ["round 198: service", "latency drops after the", "patch"],
    ),
    (("round 198: service latency drops after the patch", 32), ["round 198: service latency drops", "after the patch"]),
    (
        ("round 198: the library caches every vector it sees", 4),
        ["round", "198:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 198: the library caches every vector it sees", 8),
        ["round", "198: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 198: the library caches every vector it sees", 12),
        ["round 198:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 198: the library caches every vector it sees", 16),
        ["round 198: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 198: the library caches every vector it sees", 24),
        ["round 198: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 198: the library caches every vector it sees", 32),
        ["round 198: the library caches", "every vector it sees"],
    ),
    (
        ("round 198: agents argue then the debate resolves", 4),
        ["round", "198:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 198: agents argue then the debate resolves", 8),
        ["round", "198:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 198: agents argue then the debate resolves", 12),
        ["round 198:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 198: agents argue then the debate resolves", 16),
        ["round 198:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 198: agents argue then the debate resolves", 24), ["round 198: agents argue", "then the debate resolves"]),
    (("round 198: agents argue then the debate resolves", 32), ["round 198: agents argue then the", "debate resolves"]),
    (
        ("round 198: the filter keeps only strong matches", 4),
        ["round", "198:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 198: the filter keeps only strong matches", 8),
        ["round", "198: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 198: the filter keeps only strong matches", 12),
        ["round 198:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 198: the filter keeps only strong matches", 16),
        ["round 198: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 198: the filter keeps only strong matches", 24),
        ["round 198: the filter", "keeps only strong", "matches"],
    ),
    (("round 198: the filter keeps only strong matches", 32), ["round 198: the filter keeps only", "strong matches"]),
    (
        ("round 198: the model answers with a short reply", 4),
        ["round", "198:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 198: the model answers with a short reply", 8),
        ["round", "198: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 198: the model answers with a short reply", 12),
        ["round 198:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 198: the model answers with a short reply", 16),
        ["round 198: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 198: the model answers with a short reply", 24),
        ["round 198: the model", "answers with a short", "reply"],
    ),
    (("round 198: the model answers with a short reply", 32), ["round 198: the model answers", "with a short reply"]),
    (
        ("round 198: the recorder stores the reasoning trace", 4),
        ["round", "198:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 198: the recorder stores the reasoning trace", 8),
        ["round", "198: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 198: the recorder stores the reasoning trace", 12),
        ["round 198:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 198: the recorder stores the reasoning trace", 16),
        ["round 198: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 198: the recorder stores the reasoning trace", 24),
        ["round 198: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 198: the recorder stores the reasoning trace", 32),
        ["round 198: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 198: the angel watches the processor run", 4),
        ["round", "198:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 198: the angel watches the processor run", 8),
        ["round", "198: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 198: the angel watches the processor run", 12),
        ["round 198:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 198: the angel watches the processor run", 16),
        ["round 198: the", "angel watches", "the processor", "run"],
    ),
    (("round 198: the angel watches the processor run", 24), ["round 198: the angel", "watches the processor", "run"]),
    (("round 198: the angel watches the processor run", 32), ["round 198: the angel watches the", "processor run"]),
    (
        ("round 198: angle of the vector decides the match", 4),
        ["round", "198:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 198: angle of the vector decides the match", 8),
        ["round", "198:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 198: angle of the vector decides the match", 12),
        ["round 198:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 198: angle of the vector decides the match", 16),
        ["round 198: angle", "of the vector", "decides the", "match"],
    ),
    (("round 198: angle of the vector decides the match", 24), ["round 198: angle of the", "vector decides the match"]),
    (("round 198: angle of the vector decides the match", 32), ["round 198: angle of the vector", "decides the match"]),
    (
        ("round 198: the candle burns twice as long at night", 4),
        ["round", "198:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 198: the candle burns twice as long at night", 8),
        ["round", "198: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 198: the candle burns twice as long at night", 12),
        ["round 198:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 198: the candle burns twice as long at night", 16),
        ["round 198: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 198: the candle burns twice as long at night", 24),
        ["round 198: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 198: the candle burns twice as long at night", 32),
        ["round 198: the candle burns", "twice as long at night"],
    ),
    (
        ("round 198: a mirror of the universe in one line", 4),
        ["round", "198:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 198: a mirror of the universe in one line", 8),
        ["round", "198: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 198: a mirror of the universe in one line", 12),
        ["round 198: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 198: a mirror of the universe in one line", 16),
        ["round 198: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 198: a mirror of the universe in one line", 24), ["round 198: a mirror of", "the universe in one line"]),
    (("round 198: a mirror of the universe in one line", 32), ["round 198: a mirror of the", "universe in one line"]),
    (
        ("round 198: the queue drains before the storm", 4),
        ["round", "198:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 198: the queue drains before the storm", 8),
        ["round", "198: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 198: the queue drains before the storm", 12),
        ["round 198:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 198: the queue drains before the storm", 16), ["round 198: the", "queue drains", "before the storm"]),
    (("round 198: the queue drains before the storm", 24), ["round 198: the queue", "drains before the storm"]),
    (("round 198: the queue drains before the storm", 32), ["round 198: the queue drains", "before the storm"]),
    (
        ("kitten198 sitting198 agent198 angle198 universe198 memory198", 6),
        ["kitten198", "sitting198", "agent198", "angle198", "universe198", "memory198"],
    ),
    (
        ("kitten198 sitting198 agent198 angle198 universe198 memory198", 10),
        ["kitten198", "sitting198", "agent198", "angle198", "universe198", "memory198"],
    ),
    (
        ("kitten198 sitting198 agent198 angle198 universe198 memory198", 18),
        ["kitten198", "sitting198", "agent198 angle198", "universe198", "memory198"],
    ),
    (
        ("kitten198 sitting198 agent198 angle198 universe198 memory198", 28),
        ["kitten198 sitting198", "agent198 angle198", "universe198 memory198"],
    ),
    (
        ("sitting198 agent198 angle198 universe198 memory198 stream198", 6),
        ["sitting198", "agent198", "angle198", "universe198", "memory198", "stream198"],
    ),
    (
        ("sitting198 agent198 angle198 universe198 memory198 stream198", 10),
        ["sitting198", "agent198", "angle198", "universe198", "memory198", "stream198"],
    ),
    (
        ("sitting198 agent198 angle198 universe198 memory198 stream198", 18),
        ["sitting198", "agent198 angle198", "universe198", "memory198", "stream198"],
    ),
    (
        ("sitting198 agent198 angle198 universe198 memory198 stream198", 28),
        ["sitting198 agent198 angle198", "universe198 memory198", "stream198"],
    ),
    (
        ("agent198 angle198 universe198 memory198 stream198 context198", 6),
        ["agent198", "angle198", "universe198", "memory198", "stream198", "context198"],
    ),
    (
        ("agent198 angle198 universe198 memory198 stream198 context198", 10),
        ["agent198", "angle198", "universe198", "memory198", "stream198", "context198"],
    ),
    (
        ("agent198 angle198 universe198 memory198 stream198 context198", 18),
        ["agent198 angle198", "universe198", "memory198", "stream198", "context198"],
    ),
    (
        ("agent198 angle198 universe198 memory198 stream198 context198", 28),
        ["agent198 angle198", "universe198 memory198", "stream198 context198"],
    ),
    (
        ("angle198 universe198 memory198 stream198 context198 knowledge198", 6),
        ["angle198", "universe198", "memory198", "stream198", "context198", "knowledge198"],
    ),
    (
        ("angle198 universe198 memory198 stream198 context198 knowledge198", 10),
        ["angle198", "universe198", "memory198", "stream198", "context198", "knowledge198"],
    ),
    (
        ("angle198 universe198 memory198 stream198 context198 knowledge198", 18),
        ["angle198", "universe198", "memory198", "stream198", "context198", "knowledge198"],
    ),
    (
        ("angle198 universe198 memory198 stream198 context198 knowledge198", 28),
        ["angle198 universe198", "memory198 stream198", "context198 knowledge198"],
    ),
    (
        ("universe198 memory198 stream198 context198 knowledge198 vector198", 6),
        ["universe198", "memory198", "stream198", "context198", "knowledge198", "vector198"],
    ),
    (
        ("universe198 memory198 stream198 context198 knowledge198 vector198", 10),
        ["universe198", "memory198", "stream198", "context198", "knowledge198", "vector198"],
    ),
    (
        ("universe198 memory198 stream198 context198 knowledge198 vector198", 18),
        ["universe198", "memory198", "stream198", "context198", "knowledge198", "vector198"],
    ),
    (
        ("universe198 memory198 stream198 context198 knowledge198 vector198", 28),
        ["universe198 memory198", "stream198 context198", "knowledge198 vector198"],
    ),
    (
        ("memory198 stream198 context198 knowledge198 vector198 processor198", 6),
        ["memory198", "stream198", "context198", "knowledge198", "vector198", "processor198"],
    ),
    (
        ("memory198 stream198 context198 knowledge198 vector198 processor198", 10),
        ["memory198", "stream198", "context198", "knowledge198", "vector198", "processor198"],
    ),
    (
        ("memory198 stream198 context198 knowledge198 vector198 processor198", 18),
        ["memory198", "stream198", "context198", "knowledge198", "vector198", "processor198"],
    ),
    (
        ("memory198 stream198 context198 knowledge198 vector198 processor198", 28),
        ["memory198 stream198", "context198 knowledge198", "vector198 processor198"],
    ),
    (
        ("stream198 context198 knowledge198 vector198 processor198 reasoning198", 6),
        ["stream198", "context198", "knowledge198", "vector198", "processor198", "reasoning198"],
    ),
    (
        ("stream198 context198 knowledge198 vector198 processor198 reasoning198", 10),
        ["stream198", "context198", "knowledge198", "vector198", "processor198", "reasoning198"],
    ),
    (
        ("stream198 context198 knowledge198 vector198 processor198 reasoning198", 18),
        ["stream198", "context198", "knowledge198", "vector198", "processor198", "reasoning198"],
    ),
    (
        ("stream198 context198 knowledge198 vector198 processor198 reasoning198", 28),
        ["stream198 context198", "knowledge198 vector198", "processor198 reasoning198"],
    ),
    (
        ("context198 knowledge198 vector198 processor198 reasoning198 machine198", 6),
        ["context198", "knowledge198", "vector198", "processor198", "reasoning198", "machine198"],
    ),
    (
        ("context198 knowledge198 vector198 processor198 reasoning198 machine198", 10),
        ["context198", "knowledge198", "vector198", "processor198", "reasoning198", "machine198"],
    ),
    (
        ("context198 knowledge198 vector198 processor198 reasoning198 machine198", 18),
        ["context198", "knowledge198", "vector198", "processor198", "reasoning198", "machine198"],
    ),
    (
        ("context198 knowledge198 vector198 processor198 reasoning198 machine198", 28),
        ["context198 knowledge198", "vector198 processor198", "reasoning198 machine198"],
    ),
    (
        ("knowledge198 vector198 processor198 reasoning198 machine198 learning198", 6),
        ["knowledge198", "vector198", "processor198", "reasoning198", "machine198", "learning198"],
    ),
    (
        ("knowledge198 vector198 processor198 reasoning198 machine198 learning198", 10),
        ["knowledge198", "vector198", "processor198", "reasoning198", "machine198", "learning198"],
    ),
    (
        ("knowledge198 vector198 processor198 reasoning198 machine198 learning198", 18),
        ["knowledge198", "vector198", "processor198", "reasoning198", "machine198", "learning198"],
    ),
    (
        ("knowledge198 vector198 processor198 reasoning198 machine198 learning198", 28),
        ["knowledge198 vector198", "processor198 reasoning198", "machine198 learning198"],
    ),
    (
        ("vector198 processor198 reasoning198 machine198 learning198 model198", 6),
        ["vector198", "processor198", "reasoning198", "machine198", "learning198", "model198"],
    ),
    (
        ("vector198 processor198 reasoning198 machine198 learning198 model198", 10),
        ["vector198", "processor198", "reasoning198", "machine198", "learning198", "model198"],
    ),
    (
        ("vector198 processor198 reasoning198 machine198 learning198 model198", 18),
        ["vector198", "processor198", "reasoning198", "machine198", "learning198", "model198"],
    ),
    (
        ("vector198 processor198 reasoning198 machine198 learning198 model198", 28),
        ["vector198 processor198", "reasoning198 machine198", "learning198 model198"],
    ),
    (
        ("processor198 reasoning198 machine198 learning198 model198 token198", 6),
        ["processor198", "reasoning198", "machine198", "learning198", "model198", "token198"],
    ),
    (
        ("processor198 reasoning198 machine198 learning198 model198 token198", 10),
        ["processor198", "reasoning198", "machine198", "learning198", "model198", "token198"],
    ),
    (
        ("processor198 reasoning198 machine198 learning198 model198 token198", 18),
        ["processor198", "reasoning198", "machine198", "learning198", "model198 token198"],
    ),
    (
        ("processor198 reasoning198 machine198 learning198 model198 token198", 28),
        ["processor198 reasoning198", "machine198 learning198", "model198 token198"],
    ),
    (
        ("reasoning198 machine198 learning198 model198 token198 prompt198", 6),
        ["reasoning198", "machine198", "learning198", "model198", "token198", "prompt198"],
    ),
    (
        ("reasoning198 machine198 learning198 model198 token198 prompt198", 10),
        ["reasoning198", "machine198", "learning198", "model198", "token198", "prompt198"],
    ),
    (
        ("reasoning198 machine198 learning198 model198 token198 prompt198", 18),
        ["reasoning198", "machine198", "learning198", "model198 token198", "prompt198"],
    ),
    (
        ("reasoning198 machine198 learning198 model198 token198 prompt198", 28),
        ["reasoning198 machine198", "learning198 model198", "token198 prompt198"],
    ),
    (
        ("machine198 learning198 model198 token198 prompt198 session198", 6),
        ["machine198", "learning198", "model198", "token198", "prompt198", "session198"],
    ),
    (
        ("machine198 learning198 model198 token198 prompt198 session198", 10),
        ["machine198", "learning198", "model198", "token198", "prompt198", "session198"],
    ),
    (
        ("machine198 learning198 model198 token198 prompt198 session198", 18),
        ["machine198", "learning198", "model198 token198", "prompt198", "session198"],
    ),
    (
        ("machine198 learning198 model198 token198 prompt198 session198", 28),
        ["machine198 learning198", "model198 token198 prompt198", "session198"],
    ),
    (
        ("learning198 model198 token198 prompt198 session198 library198", 6),
        ["learning198", "model198", "token198", "prompt198", "session198", "library198"],
    ),
    (
        ("learning198 model198 token198 prompt198 session198 library198", 10),
        ["learning198", "model198", "token198", "prompt198", "session198", "library198"],
    ),
    (
        ("learning198 model198 token198 prompt198 session198 library198", 18),
        ["learning198", "model198 token198", "prompt198", "session198", "library198"],
    ),
    (
        ("learning198 model198 token198 prompt198 session198 library198", 28),
        ["learning198 model198", "token198 prompt198", "session198 library198"],
    ),
    (
        ("model198 token198 prompt198 session198 library198 service198", 6),
        ["model198", "token198", "prompt198", "session198", "library198", "service198"],
    ),
    (
        ("model198 token198 prompt198 session198 library198 service198", 10),
        ["model198", "token198", "prompt198", "session198", "library198", "service198"],
    ),
    (
        ("model198 token198 prompt198 session198 library198 service198", 18),
        ["model198 token198", "prompt198", "session198", "library198", "service198"],
    ),
    (
        ("model198 token198 prompt198 session198 library198 service198", 28),
        ["model198 token198 prompt198", "session198 library198", "service198"],
    ),
    (
        ("token198 prompt198 session198 library198 service198 gateway198", 6),
        ["token198", "prompt198", "session198", "library198", "service198", "gateway198"],
    ),
    (
        ("token198 prompt198 session198 library198 service198 gateway198", 10),
        ["token198", "prompt198", "session198", "library198", "service198", "gateway198"],
    ),
    (
        ("token198 prompt198 session198 library198 service198 gateway198", 18),
        ["token198 prompt198", "session198", "library198", "service198", "gateway198"],
    ),
    (
        ("token198 prompt198 session198 library198 service198 gateway198", 28),
        ["token198 prompt198", "session198 library198", "service198 gateway198"],
    ),
    (
        ("prompt198 session198 library198 service198 gateway198 storage198", 6),
        ["prompt198", "session198", "library198", "service198", "gateway198", "storage198"],
    ),
    (
        ("prompt198 session198 library198 service198 gateway198 storage198", 10),
        ["prompt198", "session198", "library198", "service198", "gateway198", "storage198"],
    ),
    (
        ("prompt198 session198 library198 service198 gateway198 storage198", 18),
        ["prompt198", "session198", "library198", "service198", "gateway198", "storage198"],
    ),
    (
        ("prompt198 session198 library198 service198 gateway198 storage198", 28),
        ["prompt198 session198", "library198 service198", "gateway198 storage198"],
    ),
    (
        ("session198 library198 service198 gateway198 storage198 network198", 6),
        ["session198", "library198", "service198", "gateway198", "storage198", "network198"],
    ),
    (
        ("session198 library198 service198 gateway198 storage198 network198", 10),
        ["session198", "library198", "service198", "gateway198", "storage198", "network198"],
    ),
    (
        ("session198 library198 service198 gateway198 storage198 network198", 18),
        ["session198", "library198", "service198", "gateway198", "storage198", "network198"],
    ),
    (
        ("session198 library198 service198 gateway198 storage198 network198", 28),
        ["session198 library198", "service198 gateway198", "storage198 network198"],
    ),
    (
        ("library198 service198 gateway198 storage198 network198 latency198", 6),
        ["library198", "service198", "gateway198", "storage198", "network198", "latency198"],
    ),
    (
        ("library198 service198 gateway198 storage198 network198 latency198", 10),
        ["library198", "service198", "gateway198", "storage198", "network198", "latency198"],
    ),
    (
        ("library198 service198 gateway198 storage198 network198 latency198", 18),
        ["library198", "service198", "gateway198", "storage198", "network198", "latency198"],
    ),
    (
        ("library198 service198 gateway198 storage198 network198 latency198", 28),
        ["library198 service198", "gateway198 storage198", "network198 latency198"],
    ),
    (
        ("service198 gateway198 storage198 network198 latency198 buffer198", 6),
        ["service198", "gateway198", "storage198", "network198", "latency198", "buffer198"],
    ),
    (
        ("service198 gateway198 storage198 network198 latency198 buffer198", 10),
        ["service198", "gateway198", "storage198", "network198", "latency198", "buffer198"],
    ),
    (
        ("service198 gateway198 storage198 network198 latency198 buffer198", 18),
        ["service198", "gateway198", "storage198", "network198", "latency198", "buffer198"],
    ),
    (
        ("service198 gateway198 storage198 network198 latency198 buffer198", 28),
        ["service198 gateway198", "storage198 network198", "latency198 buffer198"],
    ),
    (
        ("gateway198 storage198 network198 latency198 buffer198 queue198", 6),
        ["gateway198", "storage198", "network198", "latency198", "buffer198", "queue198"],
    ),
    (
        ("gateway198 storage198 network198 latency198 buffer198 queue198", 10),
        ["gateway198", "storage198", "network198", "latency198", "buffer198", "queue198"],
    ),
    (
        ("gateway198 storage198 network198 latency198 buffer198 queue198", 18),
        ["gateway198", "storage198", "network198", "latency198", "buffer198 queue198"],
    ),
    (
        ("gateway198 storage198 network198 latency198 buffer198 queue198", 28),
        ["gateway198 storage198", "network198 latency198", "buffer198 queue198"],
    ),
    (
        ("storage198 network198 latency198 buffer198 queue198 worker198", 6),
        ["storage198", "network198", "latency198", "buffer198", "queue198", "worker198"],
    ),
    (
        ("storage198 network198 latency198 buffer198 queue198 worker198", 10),
        ["storage198", "network198", "latency198", "buffer198", "queue198", "worker198"],
    ),
    (
        ("storage198 network198 latency198 buffer198 queue198 worker198", 18),
        ["storage198", "network198", "latency198", "buffer198 queue198", "worker198"],
    ),
    (
        ("storage198 network198 latency198 buffer198 queue198 worker198", 28),
        ["storage198 network198", "latency198 buffer198", "queue198 worker198"],
    ),
    (
        ("network198 latency198 buffer198 queue198 worker198 kernel198", 6),
        ["network198", "latency198", "buffer198", "queue198", "worker198", "kernel198"],
    ),
    (
        ("network198 latency198 buffer198 queue198 worker198 kernel198", 10),
        ["network198", "latency198", "buffer198", "queue198", "worker198", "kernel198"],
    ),
    (
        ("network198 latency198 buffer198 queue198 worker198 kernel198", 18),
        ["network198", "latency198", "buffer198 queue198", "worker198", "kernel198"],
    ),
    (
        ("network198 latency198 buffer198 queue198 worker198 kernel198", 28),
        ["network198 latency198", "buffer198 queue198 worker198", "kernel198"],
    ),
    (
        ("latency198 buffer198 queue198 worker198 kernel198 signal198", 6),
        ["latency198", "buffer198", "queue198", "worker198", "kernel198", "signal198"],
    ),
    (
        ("latency198 buffer198 queue198 worker198 kernel198 signal198", 10),
        ["latency198", "buffer198", "queue198", "worker198", "kernel198", "signal198"],
    ),
    (
        ("latency198 buffer198 queue198 worker198 kernel198 signal198", 18),
        ["latency198", "buffer198 queue198", "worker198", "kernel198", "signal198"],
    ),
    (
        ("latency198 buffer198 queue198 worker198 kernel198 signal198", 28),
        ["latency198 buffer198", "queue198 worker198 kernel198", "signal198"],
    ),
    (
        ("buffer198 queue198 worker198 kernel198 signal198 packet198", 6),
        ["buffer198", "queue198", "worker198", "kernel198", "signal198", "packet198"],
    ),
    (
        ("buffer198 queue198 worker198 kernel198 signal198 packet198", 10),
        ["buffer198", "queue198", "worker198", "kernel198", "signal198", "packet198"],
    ),
    (
        ("buffer198 queue198 worker198 kernel198 signal198 packet198", 18),
        ["buffer198 queue198", "worker198", "kernel198", "signal198", "packet198"],
    ),
    (
        ("buffer198 queue198 worker198 kernel198 signal198 packet198", 28),
        ["buffer198 queue198 worker198", "kernel198 signal198", "packet198"],
    ),
    (
        ("queue198 worker198 kernel198 signal198 packet198 router198", 6),
        ["queue198", "worker198", "kernel198", "signal198", "packet198", "router198"],
    ),
    (
        ("queue198 worker198 kernel198 signal198 packet198 router198", 10),
        ["queue198", "worker198", "kernel198", "signal198", "packet198", "router198"],
    ),
    (
        ("queue198 worker198 kernel198 signal198 packet198 router198", 18),
        ["queue198 worker198", "kernel198", "signal198", "packet198", "router198"],
    ),
    (
        ("queue198 worker198 kernel198 signal198 packet198 router198", 28),
        ["queue198 worker198 kernel198", "signal198 packet198", "router198"],
    ),
    (
        ("worker198 kernel198 signal198 packet198 router198 cluster198", 6),
        ["worker198", "kernel198", "signal198", "packet198", "router198", "cluster198"],
    ),
    (
        ("worker198 kernel198 signal198 packet198 router198 cluster198", 10),
        ["worker198", "kernel198", "signal198", "packet198", "router198", "cluster198"],
    ),
    (
        ("worker198 kernel198 signal198 packet198 router198 cluster198", 18),
        ["worker198", "kernel198", "signal198", "packet198", "router198", "cluster198"],
    ),
    (
        ("worker198 kernel198 signal198 packet198 router198 cluster198", 28),
        ["worker198 kernel198", "signal198 packet198", "router198 cluster198"],
    ),
    (
        ("kernel198 signal198 packet198 router198 cluster198 mirror198", 6),
        ["kernel198", "signal198", "packet198", "router198", "cluster198", "mirror198"],
    ),
    (
        ("kernel198 signal198 packet198 router198 cluster198 mirror198", 10),
        ["kernel198", "signal198", "packet198", "router198", "cluster198", "mirror198"],
    ),
    (
        ("kernel198 signal198 packet198 router198 cluster198 mirror198", 18),
        ["kernel198", "signal198", "packet198", "router198", "cluster198", "mirror198"],
    ),
    (
        ("kernel198 signal198 packet198 router198 cluster198 mirror198", 28),
        ["kernel198 signal198", "packet198 router198", "cluster198 mirror198"],
    ),
    (
        ("signal198 packet198 router198 cluster198 mirror198 filter198", 6),
        ["signal198", "packet198", "router198", "cluster198", "mirror198", "filter198"],
    ),
    (
        ("signal198 packet198 router198 cluster198 mirror198 filter198", 10),
        ["signal198", "packet198", "router198", "cluster198", "mirror198", "filter198"],
    ),
    (
        ("signal198 packet198 router198 cluster198 mirror198 filter198", 18),
        ["signal198", "packet198", "router198", "cluster198", "mirror198", "filter198"],
    ),
    (
        ("signal198 packet198 router198 cluster198 mirror198 filter198", 28),
        ["signal198 packet198", "router198 cluster198", "mirror198 filter198"],
    ),
    (
        ("packet198 router198 cluster198 mirror198 filter198 ranking198", 6),
        ["packet198", "router198", "cluster198", "mirror198", "filter198", "ranking198"],
    ),
    (
        ("packet198 router198 cluster198 mirror198 filter198 ranking198", 10),
        ["packet198", "router198", "cluster198", "mirror198", "filter198", "ranking198"],
    ),
    (
        ("packet198 router198 cluster198 mirror198 filter198 ranking198", 18),
        ["packet198", "router198", "cluster198", "mirror198", "filter198", "ranking198"],
    ),
    (
        ("packet198 router198 cluster198 mirror198 filter198 ranking198", 28),
        ["packet198 router198", "cluster198 mirror198", "filter198 ranking198"],
    ),
    (
        ("router198 cluster198 mirror198 filter198 ranking198 encoding198", 6),
        ["router198", "cluster198", "mirror198", "filter198", "ranking198", "encoding198"],
    ),
    (
        ("router198 cluster198 mirror198 filter198 ranking198 encoding198", 10),
        ["router198", "cluster198", "mirror198", "filter198", "ranking198", "encoding198"],
    ),
    (
        ("router198 cluster198 mirror198 filter198 ranking198 encoding198", 18),
        ["router198", "cluster198", "mirror198", "filter198", "ranking198", "encoding198"],
    ),
    (
        ("router198 cluster198 mirror198 filter198 ranking198 encoding198", 28),
        ["router198 cluster198", "mirror198 filter198", "ranking198 encoding198"],
    ),
    (
        ("cluster198 mirror198 filter198 ranking198 encoding198 mapping198", 6),
        ["cluster198", "mirror198", "filter198", "ranking198", "encoding198", "mapping198"],
    ),
    (
        ("cluster198 mirror198 filter198 ranking198 encoding198 mapping198", 10),
        ["cluster198", "mirror198", "filter198", "ranking198", "encoding198", "mapping198"],
    ),
    (
        ("cluster198 mirror198 filter198 ranking198 encoding198 mapping198", 18),
        ["cluster198", "mirror198", "filter198", "ranking198", "encoding198", "mapping198"],
    ),
    (
        ("cluster198 mirror198 filter198 ranking198 encoding198 mapping198", 28),
        ["cluster198 mirror198", "filter198 ranking198", "encoding198 mapping198"],
    ),
    (
        ("mirror198 filter198 ranking198 encoding198 mapping198 record198", 6),
        ["mirror198", "filter198", "ranking198", "encoding198", "mapping198", "record198"],
    ),
    (
        ("mirror198 filter198 ranking198 encoding198 mapping198 record198", 10),
        ["mirror198", "filter198", "ranking198", "encoding198", "mapping198", "record198"],
    ),
    (
        ("mirror198 filter198 ranking198 encoding198 mapping198 record198", 18),
        ["mirror198", "filter198", "ranking198", "encoding198", "mapping198", "record198"],
    ),
    (
        ("mirror198 filter198 ranking198 encoding198 mapping198 record198", 28),
        ["mirror198 filter198", "ranking198 encoding198", "mapping198 record198"],
    ),
    (
        ("filter198 ranking198 encoding198 mapping198 record198 candle198", 6),
        ["filter198", "ranking198", "encoding198", "mapping198", "record198", "candle198"],
    ),
    (
        ("filter198 ranking198 encoding198 mapping198 record198 candle198", 10),
        ["filter198", "ranking198", "encoding198", "mapping198", "record198", "candle198"],
    ),
    (
        ("filter198 ranking198 encoding198 mapping198 record198 candle198", 18),
        ["filter198", "ranking198", "encoding198", "mapping198", "record198", "candle198"],
    ),
    (
        ("filter198 ranking198 encoding198 mapping198 record198 candle198", 28),
        ["filter198 ranking198", "encoding198 mapping198", "record198 candle198"],
    ),
    (
        ("ranking198 encoding198 mapping198 record198 candle198 thread198", 6),
        ["ranking198", "encoding198", "mapping198", "record198", "candle198", "thread198"],
    ),
    (
        ("ranking198 encoding198 mapping198 record198 candle198 thread198", 10),
        ["ranking198", "encoding198", "mapping198", "record198", "candle198", "thread198"],
    ),
    (
        ("ranking198 encoding198 mapping198 record198 candle198 thread198", 18),
        ["ranking198", "encoding198", "mapping198", "record198", "candle198", "thread198"],
    ),
    (
        ("ranking198 encoding198 mapping198 record198 candle198 thread198", 28),
        ["ranking198 encoding198", "mapping198 record198", "candle198 thread198"],
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
