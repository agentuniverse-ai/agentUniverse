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
        ("round 174: the quick brown fox jumps over the lazy dog", 4),
        ["round", "174:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", 8),
        ["round", "174: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", 12),
        ["round 174:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", 16),
        ["round 174: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", 24),
        ["round 174: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 174: the quick brown fox jumps over the lazy dog", 32),
        ["round 174: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", 4),
        ["round", "174:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", 8),
        ["round", "174:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", 12),
        ["round 174:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", 16),
        ["round 174:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", 24),
        ["round 174: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 174: agentuniverse is a framework for multi agents", 32),
        ["round 174: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", 4),
        ["round", "174:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", 8),
        ["round", "174:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", 12),
        ["round 174:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", 16),
        ["round 174:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", 24),
        ["round 174: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 174: knowledge stored as vectors enables retrieval", 32),
        ["round 174: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 174: the processor reads the record then stops", 4),
        ["round", "174:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 174: the processor reads the record then stops", 8),
        ["round", "174: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 174: the processor reads the record then stops", 12),
        ["round 174:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 174: the processor reads the record then stops", 16),
        ["round 174: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 174: the processor reads the record then stops", 24),
        ["round 174: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 174: the processor reads the record then stops", 32),
        ["round 174: the processor reads", "the record then stops"],
    ),
    (
        ("round 174: a worker pulls the next task from the queue", 4),
        ["round", "174:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 174: a worker pulls the next task from the queue", 8),
        ["round", "174: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 174: a worker pulls the next task from the queue", 12),
        ["round 174: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 174: a worker pulls the next task from the queue", 16),
        ["round 174: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 174: a worker pulls the next task from the queue", 24),
        ["round 174: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 174: a worker pulls the next task from the queue", 32),
        ["round 174: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 174: signals travel through the network layer", 4),
        ["round", "174:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 174: signals travel through the network layer", 8),
        ["round", "174:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 174: signals travel through the network layer", 12),
        ["round 174:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 174: signals travel through the network layer", 16),
        ["round 174:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 174: signals travel through the network layer", 24),
        ["round 174: signals", "travel through the", "network layer"],
    ),
    (
        ("round 174: signals travel through the network layer", 32),
        ["round 174: signals travel", "through the network layer"],
    ),
    (
        ("round 174: the gateway routes each request by policy", 4),
        ["round", "174:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 174: the gateway routes each request by policy", 8),
        ["round", "174: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 174: the gateway routes each request by policy", 12),
        ["round 174:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 174: the gateway routes each request by policy", 16),
        ["round 174: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 174: the gateway routes each request by policy", 24),
        ["round 174: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 174: the gateway routes each request by policy", 32),
        ["round 174: the gateway routes", "each request by policy"],
    ),
    (
        ("round 174: memory grows until the buffer is full", 4),
        ["round", "174:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 174: memory grows until the buffer is full", 8),
        ["round", "174:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 174: memory grows until the buffer is full", 12),
        ["round 174:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 174: memory grows until the buffer is full", 16),
        ["round 174:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 174: memory grows until the buffer is full", 24), ["round 174: memory grows", "until the buffer is full"]),
    (("round 174: memory grows until the buffer is full", 32), ["round 174: memory grows until", "the buffer is full"]),
    (
        ("round 174: the cluster mirrors every packet twice", 4),
        ["round", "174:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 174: the cluster mirrors every packet twice", 8),
        ["round", "174: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 174: the cluster mirrors every packet twice", 12),
        ["round 174:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 174: the cluster mirrors every packet twice", 16),
        ["round 174: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 174: the cluster mirrors every packet twice", 24),
        ["round 174: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 174: the cluster mirrors every packet twice", 32),
        ["round 174: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", 4),
        ["round", "174:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", 8),
        ["round", "174:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", 12),
        ["round 174:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", 16),
        ["round 174:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", 24),
        ["round 174: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 174: ranking uses tokens learned from the corpus", 32),
        ["round 174: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 174: a long session ends when the candle dies", 4),
        ["round", "174:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 174: a long session ends when the candle dies", 8),
        ["round", "174: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 174: a long session ends when the candle dies", 12),
        ["round 174: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 174: a long session ends when the candle dies", 16),
        ["round 174: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 174: a long session ends when the candle dies", 24),
        ["round 174: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 174: a long session ends when the candle dies", 32),
        ["round 174: a long session ends", "when the candle dies"],
    ),
    (
        ("round 174: encode the prompt then map the result", 4),
        ["round", "174:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 174: encode the prompt then map the result", 8),
        ["round", "174:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 174: encode the prompt then map the result", 12),
        ["round 174:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 174: encode the prompt then map the result", 16),
        ["round 174:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 174: encode the prompt then map the result", 24),
        ["round 174: encode the", "prompt then map the", "result"],
    ),
    (("round 174: encode the prompt then map the result", 32), ["round 174: encode the prompt", "then map the result"]),
    (
        ("round 174: the kernel wakes the worker at dawn", 4),
        ["round", "174:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 174: the kernel wakes the worker at dawn", 8),
        ["round", "174: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 174: the kernel wakes the worker at dawn", 12),
        ["round 174:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 174: the kernel wakes the worker at dawn", 16), ["round 174: the", "kernel wakes the", "worker at dawn"]),
    (("round 174: the kernel wakes the worker at dawn", 24), ["round 174: the kernel", "wakes the worker at dawn"]),
    (("round 174: the kernel wakes the worker at dawn", 32), ["round 174: the kernel wakes the", "worker at dawn"]),
    (
        ("round 174: service latency drops after the patch", 4),
        ["round", "174:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 174: service latency drops after the patch", 8),
        ["round", "174:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 174: service latency drops after the patch", 12),
        ["round 174:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 174: service latency drops after the patch", 16),
        ["round 174:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 174: service latency drops after the patch", 24),
        ["round 174: service", "latency drops after the", "patch"],
    ),
    (("round 174: service latency drops after the patch", 32), ["round 174: service latency drops", "after the patch"]),
    (
        ("round 174: the library caches every vector it sees", 4),
        ["round", "174:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 174: the library caches every vector it sees", 8),
        ["round", "174: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 174: the library caches every vector it sees", 12),
        ["round 174:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 174: the library caches every vector it sees", 16),
        ["round 174: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 174: the library caches every vector it sees", 24),
        ["round 174: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 174: the library caches every vector it sees", 32),
        ["round 174: the library caches", "every vector it sees"],
    ),
    (
        ("round 174: agents argue then the debate resolves", 4),
        ["round", "174:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 174: agents argue then the debate resolves", 8),
        ["round", "174:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 174: agents argue then the debate resolves", 12),
        ["round 174:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 174: agents argue then the debate resolves", 16),
        ["round 174:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 174: agents argue then the debate resolves", 24), ["round 174: agents argue", "then the debate resolves"]),
    (("round 174: agents argue then the debate resolves", 32), ["round 174: agents argue then the", "debate resolves"]),
    (
        ("round 174: the filter keeps only strong matches", 4),
        ["round", "174:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 174: the filter keeps only strong matches", 8),
        ["round", "174: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 174: the filter keeps only strong matches", 12),
        ["round 174:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 174: the filter keeps only strong matches", 16),
        ["round 174: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 174: the filter keeps only strong matches", 24),
        ["round 174: the filter", "keeps only strong", "matches"],
    ),
    (("round 174: the filter keeps only strong matches", 32), ["round 174: the filter keeps only", "strong matches"]),
    (
        ("round 174: the model answers with a short reply", 4),
        ["round", "174:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 174: the model answers with a short reply", 8),
        ["round", "174: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 174: the model answers with a short reply", 12),
        ["round 174:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 174: the model answers with a short reply", 16),
        ["round 174: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 174: the model answers with a short reply", 24),
        ["round 174: the model", "answers with a short", "reply"],
    ),
    (("round 174: the model answers with a short reply", 32), ["round 174: the model answers", "with a short reply"]),
    (
        ("round 174: the recorder stores the reasoning trace", 4),
        ["round", "174:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 174: the recorder stores the reasoning trace", 8),
        ["round", "174: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 174: the recorder stores the reasoning trace", 12),
        ["round 174:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 174: the recorder stores the reasoning trace", 16),
        ["round 174: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 174: the recorder stores the reasoning trace", 24),
        ["round 174: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 174: the recorder stores the reasoning trace", 32),
        ["round 174: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 174: the angel watches the processor run", 4),
        ["round", "174:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 174: the angel watches the processor run", 8),
        ["round", "174: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 174: the angel watches the processor run", 12),
        ["round 174:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 174: the angel watches the processor run", 16),
        ["round 174: the", "angel watches", "the processor", "run"],
    ),
    (("round 174: the angel watches the processor run", 24), ["round 174: the angel", "watches the processor", "run"]),
    (("round 174: the angel watches the processor run", 32), ["round 174: the angel watches the", "processor run"]),
    (
        ("round 174: angle of the vector decides the match", 4),
        ["round", "174:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 174: angle of the vector decides the match", 8),
        ["round", "174:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 174: angle of the vector decides the match", 12),
        ["round 174:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 174: angle of the vector decides the match", 16),
        ["round 174: angle", "of the vector", "decides the", "match"],
    ),
    (("round 174: angle of the vector decides the match", 24), ["round 174: angle of the", "vector decides the match"]),
    (("round 174: angle of the vector decides the match", 32), ["round 174: angle of the vector", "decides the match"]),
    (
        ("round 174: the candle burns twice as long at night", 4),
        ["round", "174:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 174: the candle burns twice as long at night", 8),
        ["round", "174: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 174: the candle burns twice as long at night", 12),
        ["round 174:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 174: the candle burns twice as long at night", 16),
        ["round 174: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 174: the candle burns twice as long at night", 24),
        ["round 174: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 174: the candle burns twice as long at night", 32),
        ["round 174: the candle burns", "twice as long at night"],
    ),
    (
        ("round 174: a mirror of the universe in one line", 4),
        ["round", "174:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 174: a mirror of the universe in one line", 8),
        ["round", "174: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 174: a mirror of the universe in one line", 12),
        ["round 174: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 174: a mirror of the universe in one line", 16),
        ["round 174: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 174: a mirror of the universe in one line", 24), ["round 174: a mirror of", "the universe in one line"]),
    (("round 174: a mirror of the universe in one line", 32), ["round 174: a mirror of the", "universe in one line"]),
    (
        ("round 174: the queue drains before the storm", 4),
        ["round", "174:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 174: the queue drains before the storm", 8),
        ["round", "174: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 174: the queue drains before the storm", 12),
        ["round 174:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 174: the queue drains before the storm", 16), ["round 174: the", "queue drains", "before the storm"]),
    (("round 174: the queue drains before the storm", 24), ["round 174: the queue", "drains before the storm"]),
    (("round 174: the queue drains before the storm", 32), ["round 174: the queue drains", "before the storm"]),
    (
        ("kitten174 sitting174 agent174 angle174 universe174 memory174", 6),
        ["kitten174", "sitting174", "agent174", "angle174", "universe174", "memory174"],
    ),
    (
        ("kitten174 sitting174 agent174 angle174 universe174 memory174", 10),
        ["kitten174", "sitting174", "agent174", "angle174", "universe174", "memory174"],
    ),
    (
        ("kitten174 sitting174 agent174 angle174 universe174 memory174", 18),
        ["kitten174", "sitting174", "agent174 angle174", "universe174", "memory174"],
    ),
    (
        ("kitten174 sitting174 agent174 angle174 universe174 memory174", 28),
        ["kitten174 sitting174", "agent174 angle174", "universe174 memory174"],
    ),
    (
        ("sitting174 agent174 angle174 universe174 memory174 stream174", 6),
        ["sitting174", "agent174", "angle174", "universe174", "memory174", "stream174"],
    ),
    (
        ("sitting174 agent174 angle174 universe174 memory174 stream174", 10),
        ["sitting174", "agent174", "angle174", "universe174", "memory174", "stream174"],
    ),
    (
        ("sitting174 agent174 angle174 universe174 memory174 stream174", 18),
        ["sitting174", "agent174 angle174", "universe174", "memory174", "stream174"],
    ),
    (
        ("sitting174 agent174 angle174 universe174 memory174 stream174", 28),
        ["sitting174 agent174 angle174", "universe174 memory174", "stream174"],
    ),
    (
        ("agent174 angle174 universe174 memory174 stream174 context174", 6),
        ["agent174", "angle174", "universe174", "memory174", "stream174", "context174"],
    ),
    (
        ("agent174 angle174 universe174 memory174 stream174 context174", 10),
        ["agent174", "angle174", "universe174", "memory174", "stream174", "context174"],
    ),
    (
        ("agent174 angle174 universe174 memory174 stream174 context174", 18),
        ["agent174 angle174", "universe174", "memory174", "stream174", "context174"],
    ),
    (
        ("agent174 angle174 universe174 memory174 stream174 context174", 28),
        ["agent174 angle174", "universe174 memory174", "stream174 context174"],
    ),
    (
        ("angle174 universe174 memory174 stream174 context174 knowledge174", 6),
        ["angle174", "universe174", "memory174", "stream174", "context174", "knowledge174"],
    ),
    (
        ("angle174 universe174 memory174 stream174 context174 knowledge174", 10),
        ["angle174", "universe174", "memory174", "stream174", "context174", "knowledge174"],
    ),
    (
        ("angle174 universe174 memory174 stream174 context174 knowledge174", 18),
        ["angle174", "universe174", "memory174", "stream174", "context174", "knowledge174"],
    ),
    (
        ("angle174 universe174 memory174 stream174 context174 knowledge174", 28),
        ["angle174 universe174", "memory174 stream174", "context174 knowledge174"],
    ),
    (
        ("universe174 memory174 stream174 context174 knowledge174 vector174", 6),
        ["universe174", "memory174", "stream174", "context174", "knowledge174", "vector174"],
    ),
    (
        ("universe174 memory174 stream174 context174 knowledge174 vector174", 10),
        ["universe174", "memory174", "stream174", "context174", "knowledge174", "vector174"],
    ),
    (
        ("universe174 memory174 stream174 context174 knowledge174 vector174", 18),
        ["universe174", "memory174", "stream174", "context174", "knowledge174", "vector174"],
    ),
    (
        ("universe174 memory174 stream174 context174 knowledge174 vector174", 28),
        ["universe174 memory174", "stream174 context174", "knowledge174 vector174"],
    ),
    (
        ("memory174 stream174 context174 knowledge174 vector174 processor174", 6),
        ["memory174", "stream174", "context174", "knowledge174", "vector174", "processor174"],
    ),
    (
        ("memory174 stream174 context174 knowledge174 vector174 processor174", 10),
        ["memory174", "stream174", "context174", "knowledge174", "vector174", "processor174"],
    ),
    (
        ("memory174 stream174 context174 knowledge174 vector174 processor174", 18),
        ["memory174", "stream174", "context174", "knowledge174", "vector174", "processor174"],
    ),
    (
        ("memory174 stream174 context174 knowledge174 vector174 processor174", 28),
        ["memory174 stream174", "context174 knowledge174", "vector174 processor174"],
    ),
    (
        ("stream174 context174 knowledge174 vector174 processor174 reasoning174", 6),
        ["stream174", "context174", "knowledge174", "vector174", "processor174", "reasoning174"],
    ),
    (
        ("stream174 context174 knowledge174 vector174 processor174 reasoning174", 10),
        ["stream174", "context174", "knowledge174", "vector174", "processor174", "reasoning174"],
    ),
    (
        ("stream174 context174 knowledge174 vector174 processor174 reasoning174", 18),
        ["stream174", "context174", "knowledge174", "vector174", "processor174", "reasoning174"],
    ),
    (
        ("stream174 context174 knowledge174 vector174 processor174 reasoning174", 28),
        ["stream174 context174", "knowledge174 vector174", "processor174 reasoning174"],
    ),
    (
        ("context174 knowledge174 vector174 processor174 reasoning174 machine174", 6),
        ["context174", "knowledge174", "vector174", "processor174", "reasoning174", "machine174"],
    ),
    (
        ("context174 knowledge174 vector174 processor174 reasoning174 machine174", 10),
        ["context174", "knowledge174", "vector174", "processor174", "reasoning174", "machine174"],
    ),
    (
        ("context174 knowledge174 vector174 processor174 reasoning174 machine174", 18),
        ["context174", "knowledge174", "vector174", "processor174", "reasoning174", "machine174"],
    ),
    (
        ("context174 knowledge174 vector174 processor174 reasoning174 machine174", 28),
        ["context174 knowledge174", "vector174 processor174", "reasoning174 machine174"],
    ),
    (
        ("knowledge174 vector174 processor174 reasoning174 machine174 learning174", 6),
        ["knowledge174", "vector174", "processor174", "reasoning174", "machine174", "learning174"],
    ),
    (
        ("knowledge174 vector174 processor174 reasoning174 machine174 learning174", 10),
        ["knowledge174", "vector174", "processor174", "reasoning174", "machine174", "learning174"],
    ),
    (
        ("knowledge174 vector174 processor174 reasoning174 machine174 learning174", 18),
        ["knowledge174", "vector174", "processor174", "reasoning174", "machine174", "learning174"],
    ),
    (
        ("knowledge174 vector174 processor174 reasoning174 machine174 learning174", 28),
        ["knowledge174 vector174", "processor174 reasoning174", "machine174 learning174"],
    ),
    (
        ("vector174 processor174 reasoning174 machine174 learning174 model174", 6),
        ["vector174", "processor174", "reasoning174", "machine174", "learning174", "model174"],
    ),
    (
        ("vector174 processor174 reasoning174 machine174 learning174 model174", 10),
        ["vector174", "processor174", "reasoning174", "machine174", "learning174", "model174"],
    ),
    (
        ("vector174 processor174 reasoning174 machine174 learning174 model174", 18),
        ["vector174", "processor174", "reasoning174", "machine174", "learning174", "model174"],
    ),
    (
        ("vector174 processor174 reasoning174 machine174 learning174 model174", 28),
        ["vector174 processor174", "reasoning174 machine174", "learning174 model174"],
    ),
    (
        ("processor174 reasoning174 machine174 learning174 model174 token174", 6),
        ["processor174", "reasoning174", "machine174", "learning174", "model174", "token174"],
    ),
    (
        ("processor174 reasoning174 machine174 learning174 model174 token174", 10),
        ["processor174", "reasoning174", "machine174", "learning174", "model174", "token174"],
    ),
    (
        ("processor174 reasoning174 machine174 learning174 model174 token174", 18),
        ["processor174", "reasoning174", "machine174", "learning174", "model174 token174"],
    ),
    (
        ("processor174 reasoning174 machine174 learning174 model174 token174", 28),
        ["processor174 reasoning174", "machine174 learning174", "model174 token174"],
    ),
    (
        ("reasoning174 machine174 learning174 model174 token174 prompt174", 6),
        ["reasoning174", "machine174", "learning174", "model174", "token174", "prompt174"],
    ),
    (
        ("reasoning174 machine174 learning174 model174 token174 prompt174", 10),
        ["reasoning174", "machine174", "learning174", "model174", "token174", "prompt174"],
    ),
    (
        ("reasoning174 machine174 learning174 model174 token174 prompt174", 18),
        ["reasoning174", "machine174", "learning174", "model174 token174", "prompt174"],
    ),
    (
        ("reasoning174 machine174 learning174 model174 token174 prompt174", 28),
        ["reasoning174 machine174", "learning174 model174", "token174 prompt174"],
    ),
    (
        ("machine174 learning174 model174 token174 prompt174 session174", 6),
        ["machine174", "learning174", "model174", "token174", "prompt174", "session174"],
    ),
    (
        ("machine174 learning174 model174 token174 prompt174 session174", 10),
        ["machine174", "learning174", "model174", "token174", "prompt174", "session174"],
    ),
    (
        ("machine174 learning174 model174 token174 prompt174 session174", 18),
        ["machine174", "learning174", "model174 token174", "prompt174", "session174"],
    ),
    (
        ("machine174 learning174 model174 token174 prompt174 session174", 28),
        ["machine174 learning174", "model174 token174 prompt174", "session174"],
    ),
    (
        ("learning174 model174 token174 prompt174 session174 library174", 6),
        ["learning174", "model174", "token174", "prompt174", "session174", "library174"],
    ),
    (
        ("learning174 model174 token174 prompt174 session174 library174", 10),
        ["learning174", "model174", "token174", "prompt174", "session174", "library174"],
    ),
    (
        ("learning174 model174 token174 prompt174 session174 library174", 18),
        ["learning174", "model174 token174", "prompt174", "session174", "library174"],
    ),
    (
        ("learning174 model174 token174 prompt174 session174 library174", 28),
        ["learning174 model174", "token174 prompt174", "session174 library174"],
    ),
    (
        ("model174 token174 prompt174 session174 library174 service174", 6),
        ["model174", "token174", "prompt174", "session174", "library174", "service174"],
    ),
    (
        ("model174 token174 prompt174 session174 library174 service174", 10),
        ["model174", "token174", "prompt174", "session174", "library174", "service174"],
    ),
    (
        ("model174 token174 prompt174 session174 library174 service174", 18),
        ["model174 token174", "prompt174", "session174", "library174", "service174"],
    ),
    (
        ("model174 token174 prompt174 session174 library174 service174", 28),
        ["model174 token174 prompt174", "session174 library174", "service174"],
    ),
    (
        ("token174 prompt174 session174 library174 service174 gateway174", 6),
        ["token174", "prompt174", "session174", "library174", "service174", "gateway174"],
    ),
    (
        ("token174 prompt174 session174 library174 service174 gateway174", 10),
        ["token174", "prompt174", "session174", "library174", "service174", "gateway174"],
    ),
    (
        ("token174 prompt174 session174 library174 service174 gateway174", 18),
        ["token174 prompt174", "session174", "library174", "service174", "gateway174"],
    ),
    (
        ("token174 prompt174 session174 library174 service174 gateway174", 28),
        ["token174 prompt174", "session174 library174", "service174 gateway174"],
    ),
    (
        ("prompt174 session174 library174 service174 gateway174 storage174", 6),
        ["prompt174", "session174", "library174", "service174", "gateway174", "storage174"],
    ),
    (
        ("prompt174 session174 library174 service174 gateway174 storage174", 10),
        ["prompt174", "session174", "library174", "service174", "gateway174", "storage174"],
    ),
    (
        ("prompt174 session174 library174 service174 gateway174 storage174", 18),
        ["prompt174", "session174", "library174", "service174", "gateway174", "storage174"],
    ),
    (
        ("prompt174 session174 library174 service174 gateway174 storage174", 28),
        ["prompt174 session174", "library174 service174", "gateway174 storage174"],
    ),
    (
        ("session174 library174 service174 gateway174 storage174 network174", 6),
        ["session174", "library174", "service174", "gateway174", "storage174", "network174"],
    ),
    (
        ("session174 library174 service174 gateway174 storage174 network174", 10),
        ["session174", "library174", "service174", "gateway174", "storage174", "network174"],
    ),
    (
        ("session174 library174 service174 gateway174 storage174 network174", 18),
        ["session174", "library174", "service174", "gateway174", "storage174", "network174"],
    ),
    (
        ("session174 library174 service174 gateway174 storage174 network174", 28),
        ["session174 library174", "service174 gateway174", "storage174 network174"],
    ),
    (
        ("library174 service174 gateway174 storage174 network174 latency174", 6),
        ["library174", "service174", "gateway174", "storage174", "network174", "latency174"],
    ),
    (
        ("library174 service174 gateway174 storage174 network174 latency174", 10),
        ["library174", "service174", "gateway174", "storage174", "network174", "latency174"],
    ),
    (
        ("library174 service174 gateway174 storage174 network174 latency174", 18),
        ["library174", "service174", "gateway174", "storage174", "network174", "latency174"],
    ),
    (
        ("library174 service174 gateway174 storage174 network174 latency174", 28),
        ["library174 service174", "gateway174 storage174", "network174 latency174"],
    ),
    (
        ("service174 gateway174 storage174 network174 latency174 buffer174", 6),
        ["service174", "gateway174", "storage174", "network174", "latency174", "buffer174"],
    ),
    (
        ("service174 gateway174 storage174 network174 latency174 buffer174", 10),
        ["service174", "gateway174", "storage174", "network174", "latency174", "buffer174"],
    ),
    (
        ("service174 gateway174 storage174 network174 latency174 buffer174", 18),
        ["service174", "gateway174", "storage174", "network174", "latency174", "buffer174"],
    ),
    (
        ("service174 gateway174 storage174 network174 latency174 buffer174", 28),
        ["service174 gateway174", "storage174 network174", "latency174 buffer174"],
    ),
    (
        ("gateway174 storage174 network174 latency174 buffer174 queue174", 6),
        ["gateway174", "storage174", "network174", "latency174", "buffer174", "queue174"],
    ),
    (
        ("gateway174 storage174 network174 latency174 buffer174 queue174", 10),
        ["gateway174", "storage174", "network174", "latency174", "buffer174", "queue174"],
    ),
    (
        ("gateway174 storage174 network174 latency174 buffer174 queue174", 18),
        ["gateway174", "storage174", "network174", "latency174", "buffer174 queue174"],
    ),
    (
        ("gateway174 storage174 network174 latency174 buffer174 queue174", 28),
        ["gateway174 storage174", "network174 latency174", "buffer174 queue174"],
    ),
    (
        ("storage174 network174 latency174 buffer174 queue174 worker174", 6),
        ["storage174", "network174", "latency174", "buffer174", "queue174", "worker174"],
    ),
    (
        ("storage174 network174 latency174 buffer174 queue174 worker174", 10),
        ["storage174", "network174", "latency174", "buffer174", "queue174", "worker174"],
    ),
    (
        ("storage174 network174 latency174 buffer174 queue174 worker174", 18),
        ["storage174", "network174", "latency174", "buffer174 queue174", "worker174"],
    ),
    (
        ("storage174 network174 latency174 buffer174 queue174 worker174", 28),
        ["storage174 network174", "latency174 buffer174", "queue174 worker174"],
    ),
    (
        ("network174 latency174 buffer174 queue174 worker174 kernel174", 6),
        ["network174", "latency174", "buffer174", "queue174", "worker174", "kernel174"],
    ),
    (
        ("network174 latency174 buffer174 queue174 worker174 kernel174", 10),
        ["network174", "latency174", "buffer174", "queue174", "worker174", "kernel174"],
    ),
    (
        ("network174 latency174 buffer174 queue174 worker174 kernel174", 18),
        ["network174", "latency174", "buffer174 queue174", "worker174", "kernel174"],
    ),
    (
        ("network174 latency174 buffer174 queue174 worker174 kernel174", 28),
        ["network174 latency174", "buffer174 queue174 worker174", "kernel174"],
    ),
    (
        ("latency174 buffer174 queue174 worker174 kernel174 signal174", 6),
        ["latency174", "buffer174", "queue174", "worker174", "kernel174", "signal174"],
    ),
    (
        ("latency174 buffer174 queue174 worker174 kernel174 signal174", 10),
        ["latency174", "buffer174", "queue174", "worker174", "kernel174", "signal174"],
    ),
    (
        ("latency174 buffer174 queue174 worker174 kernel174 signal174", 18),
        ["latency174", "buffer174 queue174", "worker174", "kernel174", "signal174"],
    ),
    (
        ("latency174 buffer174 queue174 worker174 kernel174 signal174", 28),
        ["latency174 buffer174", "queue174 worker174 kernel174", "signal174"],
    ),
    (
        ("buffer174 queue174 worker174 kernel174 signal174 packet174", 6),
        ["buffer174", "queue174", "worker174", "kernel174", "signal174", "packet174"],
    ),
    (
        ("buffer174 queue174 worker174 kernel174 signal174 packet174", 10),
        ["buffer174", "queue174", "worker174", "kernel174", "signal174", "packet174"],
    ),
    (
        ("buffer174 queue174 worker174 kernel174 signal174 packet174", 18),
        ["buffer174 queue174", "worker174", "kernel174", "signal174", "packet174"],
    ),
    (
        ("buffer174 queue174 worker174 kernel174 signal174 packet174", 28),
        ["buffer174 queue174 worker174", "kernel174 signal174", "packet174"],
    ),
    (
        ("queue174 worker174 kernel174 signal174 packet174 router174", 6),
        ["queue174", "worker174", "kernel174", "signal174", "packet174", "router174"],
    ),
    (
        ("queue174 worker174 kernel174 signal174 packet174 router174", 10),
        ["queue174", "worker174", "kernel174", "signal174", "packet174", "router174"],
    ),
    (
        ("queue174 worker174 kernel174 signal174 packet174 router174", 18),
        ["queue174 worker174", "kernel174", "signal174", "packet174", "router174"],
    ),
    (
        ("queue174 worker174 kernel174 signal174 packet174 router174", 28),
        ["queue174 worker174 kernel174", "signal174 packet174", "router174"],
    ),
    (
        ("worker174 kernel174 signal174 packet174 router174 cluster174", 6),
        ["worker174", "kernel174", "signal174", "packet174", "router174", "cluster174"],
    ),
    (
        ("worker174 kernel174 signal174 packet174 router174 cluster174", 10),
        ["worker174", "kernel174", "signal174", "packet174", "router174", "cluster174"],
    ),
    (
        ("worker174 kernel174 signal174 packet174 router174 cluster174", 18),
        ["worker174", "kernel174", "signal174", "packet174", "router174", "cluster174"],
    ),
    (
        ("worker174 kernel174 signal174 packet174 router174 cluster174", 28),
        ["worker174 kernel174", "signal174 packet174", "router174 cluster174"],
    ),
    (
        ("kernel174 signal174 packet174 router174 cluster174 mirror174", 6),
        ["kernel174", "signal174", "packet174", "router174", "cluster174", "mirror174"],
    ),
    (
        ("kernel174 signal174 packet174 router174 cluster174 mirror174", 10),
        ["kernel174", "signal174", "packet174", "router174", "cluster174", "mirror174"],
    ),
    (
        ("kernel174 signal174 packet174 router174 cluster174 mirror174", 18),
        ["kernel174", "signal174", "packet174", "router174", "cluster174", "mirror174"],
    ),
    (
        ("kernel174 signal174 packet174 router174 cluster174 mirror174", 28),
        ["kernel174 signal174", "packet174 router174", "cluster174 mirror174"],
    ),
    (
        ("signal174 packet174 router174 cluster174 mirror174 filter174", 6),
        ["signal174", "packet174", "router174", "cluster174", "mirror174", "filter174"],
    ),
    (
        ("signal174 packet174 router174 cluster174 mirror174 filter174", 10),
        ["signal174", "packet174", "router174", "cluster174", "mirror174", "filter174"],
    ),
    (
        ("signal174 packet174 router174 cluster174 mirror174 filter174", 18),
        ["signal174", "packet174", "router174", "cluster174", "mirror174", "filter174"],
    ),
    (
        ("signal174 packet174 router174 cluster174 mirror174 filter174", 28),
        ["signal174 packet174", "router174 cluster174", "mirror174 filter174"],
    ),
    (
        ("packet174 router174 cluster174 mirror174 filter174 ranking174", 6),
        ["packet174", "router174", "cluster174", "mirror174", "filter174", "ranking174"],
    ),
    (
        ("packet174 router174 cluster174 mirror174 filter174 ranking174", 10),
        ["packet174", "router174", "cluster174", "mirror174", "filter174", "ranking174"],
    ),
    (
        ("packet174 router174 cluster174 mirror174 filter174 ranking174", 18),
        ["packet174", "router174", "cluster174", "mirror174", "filter174", "ranking174"],
    ),
    (
        ("packet174 router174 cluster174 mirror174 filter174 ranking174", 28),
        ["packet174 router174", "cluster174 mirror174", "filter174 ranking174"],
    ),
    (
        ("router174 cluster174 mirror174 filter174 ranking174 encoding174", 6),
        ["router174", "cluster174", "mirror174", "filter174", "ranking174", "encoding174"],
    ),
    (
        ("router174 cluster174 mirror174 filter174 ranking174 encoding174", 10),
        ["router174", "cluster174", "mirror174", "filter174", "ranking174", "encoding174"],
    ),
    (
        ("router174 cluster174 mirror174 filter174 ranking174 encoding174", 18),
        ["router174", "cluster174", "mirror174", "filter174", "ranking174", "encoding174"],
    ),
    (
        ("router174 cluster174 mirror174 filter174 ranking174 encoding174", 28),
        ["router174 cluster174", "mirror174 filter174", "ranking174 encoding174"],
    ),
    (
        ("cluster174 mirror174 filter174 ranking174 encoding174 mapping174", 6),
        ["cluster174", "mirror174", "filter174", "ranking174", "encoding174", "mapping174"],
    ),
    (
        ("cluster174 mirror174 filter174 ranking174 encoding174 mapping174", 10),
        ["cluster174", "mirror174", "filter174", "ranking174", "encoding174", "mapping174"],
    ),
    (
        ("cluster174 mirror174 filter174 ranking174 encoding174 mapping174", 18),
        ["cluster174", "mirror174", "filter174", "ranking174", "encoding174", "mapping174"],
    ),
    (
        ("cluster174 mirror174 filter174 ranking174 encoding174 mapping174", 28),
        ["cluster174 mirror174", "filter174 ranking174", "encoding174 mapping174"],
    ),
    (
        ("mirror174 filter174 ranking174 encoding174 mapping174 record174", 6),
        ["mirror174", "filter174", "ranking174", "encoding174", "mapping174", "record174"],
    ),
    (
        ("mirror174 filter174 ranking174 encoding174 mapping174 record174", 10),
        ["mirror174", "filter174", "ranking174", "encoding174", "mapping174", "record174"],
    ),
    (
        ("mirror174 filter174 ranking174 encoding174 mapping174 record174", 18),
        ["mirror174", "filter174", "ranking174", "encoding174", "mapping174", "record174"],
    ),
    (
        ("mirror174 filter174 ranking174 encoding174 mapping174 record174", 28),
        ["mirror174 filter174", "ranking174 encoding174", "mapping174 record174"],
    ),
    (
        ("filter174 ranking174 encoding174 mapping174 record174 candle174", 6),
        ["filter174", "ranking174", "encoding174", "mapping174", "record174", "candle174"],
    ),
    (
        ("filter174 ranking174 encoding174 mapping174 record174 candle174", 10),
        ["filter174", "ranking174", "encoding174", "mapping174", "record174", "candle174"],
    ),
    (
        ("filter174 ranking174 encoding174 mapping174 record174 candle174", 18),
        ["filter174", "ranking174", "encoding174", "mapping174", "record174", "candle174"],
    ),
    (
        ("filter174 ranking174 encoding174 mapping174 record174 candle174", 28),
        ["filter174 ranking174", "encoding174 mapping174", "record174 candle174"],
    ),
    (
        ("ranking174 encoding174 mapping174 record174 candle174 thread174", 6),
        ["ranking174", "encoding174", "mapping174", "record174", "candle174", "thread174"],
    ),
    (
        ("ranking174 encoding174 mapping174 record174 candle174 thread174", 10),
        ["ranking174", "encoding174", "mapping174", "record174", "candle174", "thread174"],
    ),
    (
        ("ranking174 encoding174 mapping174 record174 candle174 thread174", 18),
        ["ranking174", "encoding174", "mapping174", "record174", "candle174", "thread174"],
    ),
    (
        ("ranking174 encoding174 mapping174 record174 candle174 thread174", 28),
        ["ranking174 encoding174", "mapping174 record174", "candle174 thread174"],
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
