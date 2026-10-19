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
        ("round 748: the quick brown fox jumps over the lazy dog", 4),
        ["round", "748:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", 8),
        ["round", "748: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", 12),
        ["round 748:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", 16),
        ["round 748: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", 24),
        ["round 748: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 748: the quick brown fox jumps over the lazy dog", 32),
        ["round 748: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", 4),
        ["round", "748:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", 8),
        ["round", "748:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", 12),
        ["round 748:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", 16),
        ["round 748:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", 24),
        ["round 748: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 748: agentuniverse is a framework for multi agents", 32),
        ["round 748: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", 4),
        ["round", "748:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", 8),
        ["round", "748:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", 12),
        ["round 748:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", 16),
        ["round 748:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", 24),
        ["round 748: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 748: knowledge stored as vectors enables retrieval", 32),
        ["round 748: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 748: the processor reads the record then stops", 4),
        ["round", "748:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 748: the processor reads the record then stops", 8),
        ["round", "748: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 748: the processor reads the record then stops", 12),
        ["round 748:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 748: the processor reads the record then stops", 16),
        ["round 748: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 748: the processor reads the record then stops", 24),
        ["round 748: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 748: the processor reads the record then stops", 32),
        ["round 748: the processor reads", "the record then stops"],
    ),
    (
        ("round 748: a worker pulls the next task from the queue", 4),
        ["round", "748:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 748: a worker pulls the next task from the queue", 8),
        ["round", "748: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 748: a worker pulls the next task from the queue", 12),
        ["round 748: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 748: a worker pulls the next task from the queue", 16),
        ["round 748: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 748: a worker pulls the next task from the queue", 24),
        ["round 748: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 748: a worker pulls the next task from the queue", 32),
        ["round 748: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 748: signals travel through the network layer", 4),
        ["round", "748:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 748: signals travel through the network layer", 8),
        ["round", "748:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 748: signals travel through the network layer", 12),
        ["round 748:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 748: signals travel through the network layer", 16),
        ["round 748:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 748: signals travel through the network layer", 24),
        ["round 748: signals", "travel through the", "network layer"],
    ),
    (
        ("round 748: signals travel through the network layer", 32),
        ["round 748: signals travel", "through the network layer"],
    ),
    (
        ("round 748: the gateway routes each request by policy", 4),
        ["round", "748:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 748: the gateway routes each request by policy", 8),
        ["round", "748: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 748: the gateway routes each request by policy", 12),
        ["round 748:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 748: the gateway routes each request by policy", 16),
        ["round 748: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 748: the gateway routes each request by policy", 24),
        ["round 748: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 748: the gateway routes each request by policy", 32),
        ["round 748: the gateway routes", "each request by policy"],
    ),
    (
        ("round 748: memory grows until the buffer is full", 4),
        ["round", "748:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 748: memory grows until the buffer is full", 8),
        ["round", "748:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 748: memory grows until the buffer is full", 12),
        ["round 748:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 748: memory grows until the buffer is full", 16),
        ["round 748:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 748: memory grows until the buffer is full", 24), ["round 748: memory grows", "until the buffer is full"]),
    (("round 748: memory grows until the buffer is full", 32), ["round 748: memory grows until", "the buffer is full"]),
    (
        ("round 748: the cluster mirrors every packet twice", 4),
        ["round", "748:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 748: the cluster mirrors every packet twice", 8),
        ["round", "748: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 748: the cluster mirrors every packet twice", 12),
        ["round 748:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 748: the cluster mirrors every packet twice", 16),
        ["round 748: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 748: the cluster mirrors every packet twice", 24),
        ["round 748: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 748: the cluster mirrors every packet twice", 32),
        ["round 748: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", 4),
        ["round", "748:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", 8),
        ["round", "748:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", 12),
        ["round 748:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", 16),
        ["round 748:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", 24),
        ["round 748: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 748: ranking uses tokens learned from the corpus", 32),
        ["round 748: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 748: a long session ends when the candle dies", 4),
        ["round", "748:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 748: a long session ends when the candle dies", 8),
        ["round", "748: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 748: a long session ends when the candle dies", 12),
        ["round 748: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 748: a long session ends when the candle dies", 16),
        ["round 748: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 748: a long session ends when the candle dies", 24),
        ["round 748: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 748: a long session ends when the candle dies", 32),
        ["round 748: a long session ends", "when the candle dies"],
    ),
    (
        ("round 748: encode the prompt then map the result", 4),
        ["round", "748:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 748: encode the prompt then map the result", 8),
        ["round", "748:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 748: encode the prompt then map the result", 12),
        ["round 748:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 748: encode the prompt then map the result", 16),
        ["round 748:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 748: encode the prompt then map the result", 24),
        ["round 748: encode the", "prompt then map the", "result"],
    ),
    (("round 748: encode the prompt then map the result", 32), ["round 748: encode the prompt", "then map the result"]),
    (
        ("round 748: the kernel wakes the worker at dawn", 4),
        ["round", "748:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 748: the kernel wakes the worker at dawn", 8),
        ["round", "748: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 748: the kernel wakes the worker at dawn", 12),
        ["round 748:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 748: the kernel wakes the worker at dawn", 16), ["round 748: the", "kernel wakes the", "worker at dawn"]),
    (("round 748: the kernel wakes the worker at dawn", 24), ["round 748: the kernel", "wakes the worker at dawn"]),
    (("round 748: the kernel wakes the worker at dawn", 32), ["round 748: the kernel wakes the", "worker at dawn"]),
    (
        ("round 748: service latency drops after the patch", 4),
        ["round", "748:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 748: service latency drops after the patch", 8),
        ["round", "748:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 748: service latency drops after the patch", 12),
        ["round 748:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 748: service latency drops after the patch", 16),
        ["round 748:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 748: service latency drops after the patch", 24),
        ["round 748: service", "latency drops after the", "patch"],
    ),
    (("round 748: service latency drops after the patch", 32), ["round 748: service latency drops", "after the patch"]),
    (
        ("round 748: the library caches every vector it sees", 4),
        ["round", "748:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 748: the library caches every vector it sees", 8),
        ["round", "748: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 748: the library caches every vector it sees", 12),
        ["round 748:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 748: the library caches every vector it sees", 16),
        ["round 748: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 748: the library caches every vector it sees", 24),
        ["round 748: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 748: the library caches every vector it sees", 32),
        ["round 748: the library caches", "every vector it sees"],
    ),
    (
        ("round 748: agents argue then the debate resolves", 4),
        ["round", "748:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 748: agents argue then the debate resolves", 8),
        ["round", "748:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 748: agents argue then the debate resolves", 12),
        ["round 748:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 748: agents argue then the debate resolves", 16),
        ["round 748:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 748: agents argue then the debate resolves", 24), ["round 748: agents argue", "then the debate resolves"]),
    (("round 748: agents argue then the debate resolves", 32), ["round 748: agents argue then the", "debate resolves"]),
    (
        ("round 748: the filter keeps only strong matches", 4),
        ["round", "748:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 748: the filter keeps only strong matches", 8),
        ["round", "748: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 748: the filter keeps only strong matches", 12),
        ["round 748:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 748: the filter keeps only strong matches", 16),
        ["round 748: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 748: the filter keeps only strong matches", 24),
        ["round 748: the filter", "keeps only strong", "matches"],
    ),
    (("round 748: the filter keeps only strong matches", 32), ["round 748: the filter keeps only", "strong matches"]),
    (
        ("round 748: the model answers with a short reply", 4),
        ["round", "748:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 748: the model answers with a short reply", 8),
        ["round", "748: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 748: the model answers with a short reply", 12),
        ["round 748:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 748: the model answers with a short reply", 16),
        ["round 748: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 748: the model answers with a short reply", 24),
        ["round 748: the model", "answers with a short", "reply"],
    ),
    (("round 748: the model answers with a short reply", 32), ["round 748: the model answers", "with a short reply"]),
    (
        ("round 748: the recorder stores the reasoning trace", 4),
        ["round", "748:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 748: the recorder stores the reasoning trace", 8),
        ["round", "748: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 748: the recorder stores the reasoning trace", 12),
        ["round 748:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 748: the recorder stores the reasoning trace", 16),
        ["round 748: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 748: the recorder stores the reasoning trace", 24),
        ["round 748: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 748: the recorder stores the reasoning trace", 32),
        ["round 748: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 748: the angel watches the processor run", 4),
        ["round", "748:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 748: the angel watches the processor run", 8),
        ["round", "748: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 748: the angel watches the processor run", 12),
        ["round 748:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 748: the angel watches the processor run", 16),
        ["round 748: the", "angel watches", "the processor", "run"],
    ),
    (("round 748: the angel watches the processor run", 24), ["round 748: the angel", "watches the processor", "run"]),
    (("round 748: the angel watches the processor run", 32), ["round 748: the angel watches the", "processor run"]),
    (
        ("round 748: angle of the vector decides the match", 4),
        ["round", "748:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 748: angle of the vector decides the match", 8),
        ["round", "748:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 748: angle of the vector decides the match", 12),
        ["round 748:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 748: angle of the vector decides the match", 16),
        ["round 748: angle", "of the vector", "decides the", "match"],
    ),
    (("round 748: angle of the vector decides the match", 24), ["round 748: angle of the", "vector decides the match"]),
    (("round 748: angle of the vector decides the match", 32), ["round 748: angle of the vector", "decides the match"]),
    (
        ("round 748: the candle burns twice as long at night", 4),
        ["round", "748:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 748: the candle burns twice as long at night", 8),
        ["round", "748: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 748: the candle burns twice as long at night", 12),
        ["round 748:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 748: the candle burns twice as long at night", 16),
        ["round 748: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 748: the candle burns twice as long at night", 24),
        ["round 748: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 748: the candle burns twice as long at night", 32),
        ["round 748: the candle burns", "twice as long at night"],
    ),
    (
        ("round 748: a mirror of the universe in one line", 4),
        ["round", "748:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 748: a mirror of the universe in one line", 8),
        ["round", "748: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 748: a mirror of the universe in one line", 12),
        ["round 748: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 748: a mirror of the universe in one line", 16),
        ["round 748: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 748: a mirror of the universe in one line", 24), ["round 748: a mirror of", "the universe in one line"]),
    (("round 748: a mirror of the universe in one line", 32), ["round 748: a mirror of the", "universe in one line"]),
    (
        ("round 748: the queue drains before the storm", 4),
        ["round", "748:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 748: the queue drains before the storm", 8),
        ["round", "748: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 748: the queue drains before the storm", 12),
        ["round 748:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 748: the queue drains before the storm", 16), ["round 748: the", "queue drains", "before the storm"]),
    (("round 748: the queue drains before the storm", 24), ["round 748: the queue", "drains before the storm"]),
    (("round 748: the queue drains before the storm", 32), ["round 748: the queue drains", "before the storm"]),
    (
        ("kitten748 sitting748 agent748 angle748 universe748 memory748", 6),
        ["kitten748", "sitting748", "agent748", "angle748", "universe748", "memory748"],
    ),
    (
        ("kitten748 sitting748 agent748 angle748 universe748 memory748", 10),
        ["kitten748", "sitting748", "agent748", "angle748", "universe748", "memory748"],
    ),
    (
        ("kitten748 sitting748 agent748 angle748 universe748 memory748", 18),
        ["kitten748", "sitting748", "agent748 angle748", "universe748", "memory748"],
    ),
    (
        ("kitten748 sitting748 agent748 angle748 universe748 memory748", 28),
        ["kitten748 sitting748", "agent748 angle748", "universe748 memory748"],
    ),
    (
        ("sitting748 agent748 angle748 universe748 memory748 stream748", 6),
        ["sitting748", "agent748", "angle748", "universe748", "memory748", "stream748"],
    ),
    (
        ("sitting748 agent748 angle748 universe748 memory748 stream748", 10),
        ["sitting748", "agent748", "angle748", "universe748", "memory748", "stream748"],
    ),
    (
        ("sitting748 agent748 angle748 universe748 memory748 stream748", 18),
        ["sitting748", "agent748 angle748", "universe748", "memory748", "stream748"],
    ),
    (
        ("sitting748 agent748 angle748 universe748 memory748 stream748", 28),
        ["sitting748 agent748 angle748", "universe748 memory748", "stream748"],
    ),
    (
        ("agent748 angle748 universe748 memory748 stream748 context748", 6),
        ["agent748", "angle748", "universe748", "memory748", "stream748", "context748"],
    ),
    (
        ("agent748 angle748 universe748 memory748 stream748 context748", 10),
        ["agent748", "angle748", "universe748", "memory748", "stream748", "context748"],
    ),
    (
        ("agent748 angle748 universe748 memory748 stream748 context748", 18),
        ["agent748 angle748", "universe748", "memory748", "stream748", "context748"],
    ),
    (
        ("agent748 angle748 universe748 memory748 stream748 context748", 28),
        ["agent748 angle748", "universe748 memory748", "stream748 context748"],
    ),
    (
        ("angle748 universe748 memory748 stream748 context748 knowledge748", 6),
        ["angle748", "universe748", "memory748", "stream748", "context748", "knowledge748"],
    ),
    (
        ("angle748 universe748 memory748 stream748 context748 knowledge748", 10),
        ["angle748", "universe748", "memory748", "stream748", "context748", "knowledge748"],
    ),
    (
        ("angle748 universe748 memory748 stream748 context748 knowledge748", 18),
        ["angle748", "universe748", "memory748", "stream748", "context748", "knowledge748"],
    ),
    (
        ("angle748 universe748 memory748 stream748 context748 knowledge748", 28),
        ["angle748 universe748", "memory748 stream748", "context748 knowledge748"],
    ),
    (
        ("universe748 memory748 stream748 context748 knowledge748 vector748", 6),
        ["universe748", "memory748", "stream748", "context748", "knowledge748", "vector748"],
    ),
    (
        ("universe748 memory748 stream748 context748 knowledge748 vector748", 10),
        ["universe748", "memory748", "stream748", "context748", "knowledge748", "vector748"],
    ),
    (
        ("universe748 memory748 stream748 context748 knowledge748 vector748", 18),
        ["universe748", "memory748", "stream748", "context748", "knowledge748", "vector748"],
    ),
    (
        ("universe748 memory748 stream748 context748 knowledge748 vector748", 28),
        ["universe748 memory748", "stream748 context748", "knowledge748 vector748"],
    ),
    (
        ("memory748 stream748 context748 knowledge748 vector748 processor748", 6),
        ["memory748", "stream748", "context748", "knowledge748", "vector748", "processor748"],
    ),
    (
        ("memory748 stream748 context748 knowledge748 vector748 processor748", 10),
        ["memory748", "stream748", "context748", "knowledge748", "vector748", "processor748"],
    ),
    (
        ("memory748 stream748 context748 knowledge748 vector748 processor748", 18),
        ["memory748", "stream748", "context748", "knowledge748", "vector748", "processor748"],
    ),
    (
        ("memory748 stream748 context748 knowledge748 vector748 processor748", 28),
        ["memory748 stream748", "context748 knowledge748", "vector748 processor748"],
    ),
    (
        ("stream748 context748 knowledge748 vector748 processor748 reasoning748", 6),
        ["stream748", "context748", "knowledge748", "vector748", "processor748", "reasoning748"],
    ),
    (
        ("stream748 context748 knowledge748 vector748 processor748 reasoning748", 10),
        ["stream748", "context748", "knowledge748", "vector748", "processor748", "reasoning748"],
    ),
    (
        ("stream748 context748 knowledge748 vector748 processor748 reasoning748", 18),
        ["stream748", "context748", "knowledge748", "vector748", "processor748", "reasoning748"],
    ),
    (
        ("stream748 context748 knowledge748 vector748 processor748 reasoning748", 28),
        ["stream748 context748", "knowledge748 vector748", "processor748 reasoning748"],
    ),
    (
        ("context748 knowledge748 vector748 processor748 reasoning748 machine748", 6),
        ["context748", "knowledge748", "vector748", "processor748", "reasoning748", "machine748"],
    ),
    (
        ("context748 knowledge748 vector748 processor748 reasoning748 machine748", 10),
        ["context748", "knowledge748", "vector748", "processor748", "reasoning748", "machine748"],
    ),
    (
        ("context748 knowledge748 vector748 processor748 reasoning748 machine748", 18),
        ["context748", "knowledge748", "vector748", "processor748", "reasoning748", "machine748"],
    ),
    (
        ("context748 knowledge748 vector748 processor748 reasoning748 machine748", 28),
        ["context748 knowledge748", "vector748 processor748", "reasoning748 machine748"],
    ),
    (
        ("knowledge748 vector748 processor748 reasoning748 machine748 learning748", 6),
        ["knowledge748", "vector748", "processor748", "reasoning748", "machine748", "learning748"],
    ),
    (
        ("knowledge748 vector748 processor748 reasoning748 machine748 learning748", 10),
        ["knowledge748", "vector748", "processor748", "reasoning748", "machine748", "learning748"],
    ),
    (
        ("knowledge748 vector748 processor748 reasoning748 machine748 learning748", 18),
        ["knowledge748", "vector748", "processor748", "reasoning748", "machine748", "learning748"],
    ),
    (
        ("knowledge748 vector748 processor748 reasoning748 machine748 learning748", 28),
        ["knowledge748 vector748", "processor748 reasoning748", "machine748 learning748"],
    ),
    (
        ("vector748 processor748 reasoning748 machine748 learning748 model748", 6),
        ["vector748", "processor748", "reasoning748", "machine748", "learning748", "model748"],
    ),
    (
        ("vector748 processor748 reasoning748 machine748 learning748 model748", 10),
        ["vector748", "processor748", "reasoning748", "machine748", "learning748", "model748"],
    ),
    (
        ("vector748 processor748 reasoning748 machine748 learning748 model748", 18),
        ["vector748", "processor748", "reasoning748", "machine748", "learning748", "model748"],
    ),
    (
        ("vector748 processor748 reasoning748 machine748 learning748 model748", 28),
        ["vector748 processor748", "reasoning748 machine748", "learning748 model748"],
    ),
    (
        ("processor748 reasoning748 machine748 learning748 model748 token748", 6),
        ["processor748", "reasoning748", "machine748", "learning748", "model748", "token748"],
    ),
    (
        ("processor748 reasoning748 machine748 learning748 model748 token748", 10),
        ["processor748", "reasoning748", "machine748", "learning748", "model748", "token748"],
    ),
    (
        ("processor748 reasoning748 machine748 learning748 model748 token748", 18),
        ["processor748", "reasoning748", "machine748", "learning748", "model748 token748"],
    ),
    (
        ("processor748 reasoning748 machine748 learning748 model748 token748", 28),
        ["processor748 reasoning748", "machine748 learning748", "model748 token748"],
    ),
    (
        ("reasoning748 machine748 learning748 model748 token748 prompt748", 6),
        ["reasoning748", "machine748", "learning748", "model748", "token748", "prompt748"],
    ),
    (
        ("reasoning748 machine748 learning748 model748 token748 prompt748", 10),
        ["reasoning748", "machine748", "learning748", "model748", "token748", "prompt748"],
    ),
    (
        ("reasoning748 machine748 learning748 model748 token748 prompt748", 18),
        ["reasoning748", "machine748", "learning748", "model748 token748", "prompt748"],
    ),
    (
        ("reasoning748 machine748 learning748 model748 token748 prompt748", 28),
        ["reasoning748 machine748", "learning748 model748", "token748 prompt748"],
    ),
    (
        ("machine748 learning748 model748 token748 prompt748 session748", 6),
        ["machine748", "learning748", "model748", "token748", "prompt748", "session748"],
    ),
    (
        ("machine748 learning748 model748 token748 prompt748 session748", 10),
        ["machine748", "learning748", "model748", "token748", "prompt748", "session748"],
    ),
    (
        ("machine748 learning748 model748 token748 prompt748 session748", 18),
        ["machine748", "learning748", "model748 token748", "prompt748", "session748"],
    ),
    (
        ("machine748 learning748 model748 token748 prompt748 session748", 28),
        ["machine748 learning748", "model748 token748 prompt748", "session748"],
    ),
    (
        ("learning748 model748 token748 prompt748 session748 library748", 6),
        ["learning748", "model748", "token748", "prompt748", "session748", "library748"],
    ),
    (
        ("learning748 model748 token748 prompt748 session748 library748", 10),
        ["learning748", "model748", "token748", "prompt748", "session748", "library748"],
    ),
    (
        ("learning748 model748 token748 prompt748 session748 library748", 18),
        ["learning748", "model748 token748", "prompt748", "session748", "library748"],
    ),
    (
        ("learning748 model748 token748 prompt748 session748 library748", 28),
        ["learning748 model748", "token748 prompt748", "session748 library748"],
    ),
    (
        ("model748 token748 prompt748 session748 library748 service748", 6),
        ["model748", "token748", "prompt748", "session748", "library748", "service748"],
    ),
    (
        ("model748 token748 prompt748 session748 library748 service748", 10),
        ["model748", "token748", "prompt748", "session748", "library748", "service748"],
    ),
    (
        ("model748 token748 prompt748 session748 library748 service748", 18),
        ["model748 token748", "prompt748", "session748", "library748", "service748"],
    ),
    (
        ("model748 token748 prompt748 session748 library748 service748", 28),
        ["model748 token748 prompt748", "session748 library748", "service748"],
    ),
    (
        ("token748 prompt748 session748 library748 service748 gateway748", 6),
        ["token748", "prompt748", "session748", "library748", "service748", "gateway748"],
    ),
    (
        ("token748 prompt748 session748 library748 service748 gateway748", 10),
        ["token748", "prompt748", "session748", "library748", "service748", "gateway748"],
    ),
    (
        ("token748 prompt748 session748 library748 service748 gateway748", 18),
        ["token748 prompt748", "session748", "library748", "service748", "gateway748"],
    ),
    (
        ("token748 prompt748 session748 library748 service748 gateway748", 28),
        ["token748 prompt748", "session748 library748", "service748 gateway748"],
    ),
    (
        ("prompt748 session748 library748 service748 gateway748 storage748", 6),
        ["prompt748", "session748", "library748", "service748", "gateway748", "storage748"],
    ),
    (
        ("prompt748 session748 library748 service748 gateway748 storage748", 10),
        ["prompt748", "session748", "library748", "service748", "gateway748", "storage748"],
    ),
    (
        ("prompt748 session748 library748 service748 gateway748 storage748", 18),
        ["prompt748", "session748", "library748", "service748", "gateway748", "storage748"],
    ),
    (
        ("prompt748 session748 library748 service748 gateway748 storage748", 28),
        ["prompt748 session748", "library748 service748", "gateway748 storage748"],
    ),
    (
        ("session748 library748 service748 gateway748 storage748 network748", 6),
        ["session748", "library748", "service748", "gateway748", "storage748", "network748"],
    ),
    (
        ("session748 library748 service748 gateway748 storage748 network748", 10),
        ["session748", "library748", "service748", "gateway748", "storage748", "network748"],
    ),
    (
        ("session748 library748 service748 gateway748 storage748 network748", 18),
        ["session748", "library748", "service748", "gateway748", "storage748", "network748"],
    ),
    (
        ("session748 library748 service748 gateway748 storage748 network748", 28),
        ["session748 library748", "service748 gateway748", "storage748 network748"],
    ),
    (
        ("library748 service748 gateway748 storage748 network748 latency748", 6),
        ["library748", "service748", "gateway748", "storage748", "network748", "latency748"],
    ),
    (
        ("library748 service748 gateway748 storage748 network748 latency748", 10),
        ["library748", "service748", "gateway748", "storage748", "network748", "latency748"],
    ),
    (
        ("library748 service748 gateway748 storage748 network748 latency748", 18),
        ["library748", "service748", "gateway748", "storage748", "network748", "latency748"],
    ),
    (
        ("library748 service748 gateway748 storage748 network748 latency748", 28),
        ["library748 service748", "gateway748 storage748", "network748 latency748"],
    ),
    (
        ("service748 gateway748 storage748 network748 latency748 buffer748", 6),
        ["service748", "gateway748", "storage748", "network748", "latency748", "buffer748"],
    ),
    (
        ("service748 gateway748 storage748 network748 latency748 buffer748", 10),
        ["service748", "gateway748", "storage748", "network748", "latency748", "buffer748"],
    ),
    (
        ("service748 gateway748 storage748 network748 latency748 buffer748", 18),
        ["service748", "gateway748", "storage748", "network748", "latency748", "buffer748"],
    ),
    (
        ("service748 gateway748 storage748 network748 latency748 buffer748", 28),
        ["service748 gateway748", "storage748 network748", "latency748 buffer748"],
    ),
    (
        ("gateway748 storage748 network748 latency748 buffer748 queue748", 6),
        ["gateway748", "storage748", "network748", "latency748", "buffer748", "queue748"],
    ),
    (
        ("gateway748 storage748 network748 latency748 buffer748 queue748", 10),
        ["gateway748", "storage748", "network748", "latency748", "buffer748", "queue748"],
    ),
    (
        ("gateway748 storage748 network748 latency748 buffer748 queue748", 18),
        ["gateway748", "storage748", "network748", "latency748", "buffer748 queue748"],
    ),
    (
        ("gateway748 storage748 network748 latency748 buffer748 queue748", 28),
        ["gateway748 storage748", "network748 latency748", "buffer748 queue748"],
    ),
    (
        ("storage748 network748 latency748 buffer748 queue748 worker748", 6),
        ["storage748", "network748", "latency748", "buffer748", "queue748", "worker748"],
    ),
    (
        ("storage748 network748 latency748 buffer748 queue748 worker748", 10),
        ["storage748", "network748", "latency748", "buffer748", "queue748", "worker748"],
    ),
    (
        ("storage748 network748 latency748 buffer748 queue748 worker748", 18),
        ["storage748", "network748", "latency748", "buffer748 queue748", "worker748"],
    ),
    (
        ("storage748 network748 latency748 buffer748 queue748 worker748", 28),
        ["storage748 network748", "latency748 buffer748", "queue748 worker748"],
    ),
    (
        ("network748 latency748 buffer748 queue748 worker748 kernel748", 6),
        ["network748", "latency748", "buffer748", "queue748", "worker748", "kernel748"],
    ),
    (
        ("network748 latency748 buffer748 queue748 worker748 kernel748", 10),
        ["network748", "latency748", "buffer748", "queue748", "worker748", "kernel748"],
    ),
    (
        ("network748 latency748 buffer748 queue748 worker748 kernel748", 18),
        ["network748", "latency748", "buffer748 queue748", "worker748", "kernel748"],
    ),
    (
        ("network748 latency748 buffer748 queue748 worker748 kernel748", 28),
        ["network748 latency748", "buffer748 queue748 worker748", "kernel748"],
    ),
    (
        ("latency748 buffer748 queue748 worker748 kernel748 signal748", 6),
        ["latency748", "buffer748", "queue748", "worker748", "kernel748", "signal748"],
    ),
    (
        ("latency748 buffer748 queue748 worker748 kernel748 signal748", 10),
        ["latency748", "buffer748", "queue748", "worker748", "kernel748", "signal748"],
    ),
    (
        ("latency748 buffer748 queue748 worker748 kernel748 signal748", 18),
        ["latency748", "buffer748 queue748", "worker748", "kernel748", "signal748"],
    ),
    (
        ("latency748 buffer748 queue748 worker748 kernel748 signal748", 28),
        ["latency748 buffer748", "queue748 worker748 kernel748", "signal748"],
    ),
    (
        ("buffer748 queue748 worker748 kernel748 signal748 packet748", 6),
        ["buffer748", "queue748", "worker748", "kernel748", "signal748", "packet748"],
    ),
    (
        ("buffer748 queue748 worker748 kernel748 signal748 packet748", 10),
        ["buffer748", "queue748", "worker748", "kernel748", "signal748", "packet748"],
    ),
    (
        ("buffer748 queue748 worker748 kernel748 signal748 packet748", 18),
        ["buffer748 queue748", "worker748", "kernel748", "signal748", "packet748"],
    ),
    (
        ("buffer748 queue748 worker748 kernel748 signal748 packet748", 28),
        ["buffer748 queue748 worker748", "kernel748 signal748", "packet748"],
    ),
    (
        ("queue748 worker748 kernel748 signal748 packet748 router748", 6),
        ["queue748", "worker748", "kernel748", "signal748", "packet748", "router748"],
    ),
    (
        ("queue748 worker748 kernel748 signal748 packet748 router748", 10),
        ["queue748", "worker748", "kernel748", "signal748", "packet748", "router748"],
    ),
    (
        ("queue748 worker748 kernel748 signal748 packet748 router748", 18),
        ["queue748 worker748", "kernel748", "signal748", "packet748", "router748"],
    ),
    (
        ("queue748 worker748 kernel748 signal748 packet748 router748", 28),
        ["queue748 worker748 kernel748", "signal748 packet748", "router748"],
    ),
    (
        ("worker748 kernel748 signal748 packet748 router748 cluster748", 6),
        ["worker748", "kernel748", "signal748", "packet748", "router748", "cluster748"],
    ),
    (
        ("worker748 kernel748 signal748 packet748 router748 cluster748", 10),
        ["worker748", "kernel748", "signal748", "packet748", "router748", "cluster748"],
    ),
    (
        ("worker748 kernel748 signal748 packet748 router748 cluster748", 18),
        ["worker748", "kernel748", "signal748", "packet748", "router748", "cluster748"],
    ),
    (
        ("worker748 kernel748 signal748 packet748 router748 cluster748", 28),
        ["worker748 kernel748", "signal748 packet748", "router748 cluster748"],
    ),
    (
        ("kernel748 signal748 packet748 router748 cluster748 mirror748", 6),
        ["kernel748", "signal748", "packet748", "router748", "cluster748", "mirror748"],
    ),
    (
        ("kernel748 signal748 packet748 router748 cluster748 mirror748", 10),
        ["kernel748", "signal748", "packet748", "router748", "cluster748", "mirror748"],
    ),
    (
        ("kernel748 signal748 packet748 router748 cluster748 mirror748", 18),
        ["kernel748", "signal748", "packet748", "router748", "cluster748", "mirror748"],
    ),
    (
        ("kernel748 signal748 packet748 router748 cluster748 mirror748", 28),
        ["kernel748 signal748", "packet748 router748", "cluster748 mirror748"],
    ),
    (
        ("signal748 packet748 router748 cluster748 mirror748 filter748", 6),
        ["signal748", "packet748", "router748", "cluster748", "mirror748", "filter748"],
    ),
    (
        ("signal748 packet748 router748 cluster748 mirror748 filter748", 10),
        ["signal748", "packet748", "router748", "cluster748", "mirror748", "filter748"],
    ),
    (
        ("signal748 packet748 router748 cluster748 mirror748 filter748", 18),
        ["signal748", "packet748", "router748", "cluster748", "mirror748", "filter748"],
    ),
    (
        ("signal748 packet748 router748 cluster748 mirror748 filter748", 28),
        ["signal748 packet748", "router748 cluster748", "mirror748 filter748"],
    ),
    (
        ("packet748 router748 cluster748 mirror748 filter748 ranking748", 6),
        ["packet748", "router748", "cluster748", "mirror748", "filter748", "ranking748"],
    ),
    (
        ("packet748 router748 cluster748 mirror748 filter748 ranking748", 10),
        ["packet748", "router748", "cluster748", "mirror748", "filter748", "ranking748"],
    ),
    (
        ("packet748 router748 cluster748 mirror748 filter748 ranking748", 18),
        ["packet748", "router748", "cluster748", "mirror748", "filter748", "ranking748"],
    ),
    (
        ("packet748 router748 cluster748 mirror748 filter748 ranking748", 28),
        ["packet748 router748", "cluster748 mirror748", "filter748 ranking748"],
    ),
    (
        ("router748 cluster748 mirror748 filter748 ranking748 encoding748", 6),
        ["router748", "cluster748", "mirror748", "filter748", "ranking748", "encoding748"],
    ),
    (
        ("router748 cluster748 mirror748 filter748 ranking748 encoding748", 10),
        ["router748", "cluster748", "mirror748", "filter748", "ranking748", "encoding748"],
    ),
    (
        ("router748 cluster748 mirror748 filter748 ranking748 encoding748", 18),
        ["router748", "cluster748", "mirror748", "filter748", "ranking748", "encoding748"],
    ),
    (
        ("router748 cluster748 mirror748 filter748 ranking748 encoding748", 28),
        ["router748 cluster748", "mirror748 filter748", "ranking748 encoding748"],
    ),
    (
        ("cluster748 mirror748 filter748 ranking748 encoding748 mapping748", 6),
        ["cluster748", "mirror748", "filter748", "ranking748", "encoding748", "mapping748"],
    ),
    (
        ("cluster748 mirror748 filter748 ranking748 encoding748 mapping748", 10),
        ["cluster748", "mirror748", "filter748", "ranking748", "encoding748", "mapping748"],
    ),
    (
        ("cluster748 mirror748 filter748 ranking748 encoding748 mapping748", 18),
        ["cluster748", "mirror748", "filter748", "ranking748", "encoding748", "mapping748"],
    ),
    (
        ("cluster748 mirror748 filter748 ranking748 encoding748 mapping748", 28),
        ["cluster748 mirror748", "filter748 ranking748", "encoding748 mapping748"],
    ),
    (
        ("mirror748 filter748 ranking748 encoding748 mapping748 record748", 6),
        ["mirror748", "filter748", "ranking748", "encoding748", "mapping748", "record748"],
    ),
    (
        ("mirror748 filter748 ranking748 encoding748 mapping748 record748", 10),
        ["mirror748", "filter748", "ranking748", "encoding748", "mapping748", "record748"],
    ),
    (
        ("mirror748 filter748 ranking748 encoding748 mapping748 record748", 18),
        ["mirror748", "filter748", "ranking748", "encoding748", "mapping748", "record748"],
    ),
    (
        ("mirror748 filter748 ranking748 encoding748 mapping748 record748", 28),
        ["mirror748 filter748", "ranking748 encoding748", "mapping748 record748"],
    ),
    (
        ("filter748 ranking748 encoding748 mapping748 record748 candle748", 6),
        ["filter748", "ranking748", "encoding748", "mapping748", "record748", "candle748"],
    ),
    (
        ("filter748 ranking748 encoding748 mapping748 record748 candle748", 10),
        ["filter748", "ranking748", "encoding748", "mapping748", "record748", "candle748"],
    ),
    (
        ("filter748 ranking748 encoding748 mapping748 record748 candle748", 18),
        ["filter748", "ranking748", "encoding748", "mapping748", "record748", "candle748"],
    ),
    (
        ("filter748 ranking748 encoding748 mapping748 record748 candle748", 28),
        ["filter748 ranking748", "encoding748 mapping748", "record748 candle748"],
    ),
    (
        ("ranking748 encoding748 mapping748 record748 candle748 thread748", 6),
        ["ranking748", "encoding748", "mapping748", "record748", "candle748", "thread748"],
    ),
    (
        ("ranking748 encoding748 mapping748 record748 candle748 thread748", 10),
        ["ranking748", "encoding748", "mapping748", "record748", "candle748", "thread748"],
    ),
    (
        ("ranking748 encoding748 mapping748 record748 candle748 thread748", 18),
        ["ranking748", "encoding748", "mapping748", "record748", "candle748", "thread748"],
    ),
    (
        ("ranking748 encoding748 mapping748 record748 candle748 thread748", 28),
        ["ranking748 encoding748", "mapping748 record748", "candle748 thread748"],
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
