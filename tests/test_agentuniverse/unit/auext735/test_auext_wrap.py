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
        ("round 735: the quick brown fox jumps over the lazy dog", 4),
        ["round", "735:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", 8),
        ["round", "735: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", 12),
        ["round 735:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", 16),
        ["round 735: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", 24),
        ["round 735: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 735: the quick brown fox jumps over the lazy dog", 32),
        ["round 735: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", 4),
        ["round", "735:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", 8),
        ["round", "735:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", 12),
        ["round 735:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", 16),
        ["round 735:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", 24),
        ["round 735: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 735: agentuniverse is a framework for multi agents", 32),
        ["round 735: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", 4),
        ["round", "735:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", 8),
        ["round", "735:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", 12),
        ["round 735:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", 16),
        ["round 735:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", 24),
        ["round 735: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 735: knowledge stored as vectors enables retrieval", 32),
        ["round 735: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 735: the processor reads the record then stops", 4),
        ["round", "735:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 735: the processor reads the record then stops", 8),
        ["round", "735: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 735: the processor reads the record then stops", 12),
        ["round 735:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 735: the processor reads the record then stops", 16),
        ["round 735: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 735: the processor reads the record then stops", 24),
        ["round 735: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 735: the processor reads the record then stops", 32),
        ["round 735: the processor reads", "the record then stops"],
    ),
    (
        ("round 735: a worker pulls the next task from the queue", 4),
        ["round", "735:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 735: a worker pulls the next task from the queue", 8),
        ["round", "735: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 735: a worker pulls the next task from the queue", 12),
        ["round 735: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 735: a worker pulls the next task from the queue", 16),
        ["round 735: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 735: a worker pulls the next task from the queue", 24),
        ["round 735: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 735: a worker pulls the next task from the queue", 32),
        ["round 735: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 735: signals travel through the network layer", 4),
        ["round", "735:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 735: signals travel through the network layer", 8),
        ["round", "735:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 735: signals travel through the network layer", 12),
        ["round 735:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 735: signals travel through the network layer", 16),
        ["round 735:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 735: signals travel through the network layer", 24),
        ["round 735: signals", "travel through the", "network layer"],
    ),
    (
        ("round 735: signals travel through the network layer", 32),
        ["round 735: signals travel", "through the network layer"],
    ),
    (
        ("round 735: the gateway routes each request by policy", 4),
        ["round", "735:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 735: the gateway routes each request by policy", 8),
        ["round", "735: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 735: the gateway routes each request by policy", 12),
        ["round 735:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 735: the gateway routes each request by policy", 16),
        ["round 735: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 735: the gateway routes each request by policy", 24),
        ["round 735: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 735: the gateway routes each request by policy", 32),
        ["round 735: the gateway routes", "each request by policy"],
    ),
    (
        ("round 735: memory grows until the buffer is full", 4),
        ["round", "735:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 735: memory grows until the buffer is full", 8),
        ["round", "735:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 735: memory grows until the buffer is full", 12),
        ["round 735:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 735: memory grows until the buffer is full", 16),
        ["round 735:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 735: memory grows until the buffer is full", 24), ["round 735: memory grows", "until the buffer is full"]),
    (("round 735: memory grows until the buffer is full", 32), ["round 735: memory grows until", "the buffer is full"]),
    (
        ("round 735: the cluster mirrors every packet twice", 4),
        ["round", "735:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 735: the cluster mirrors every packet twice", 8),
        ["round", "735: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 735: the cluster mirrors every packet twice", 12),
        ["round 735:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 735: the cluster mirrors every packet twice", 16),
        ["round 735: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 735: the cluster mirrors every packet twice", 24),
        ["round 735: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 735: the cluster mirrors every packet twice", 32),
        ["round 735: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", 4),
        ["round", "735:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", 8),
        ["round", "735:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", 12),
        ["round 735:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", 16),
        ["round 735:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", 24),
        ["round 735: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 735: ranking uses tokens learned from the corpus", 32),
        ["round 735: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 735: a long session ends when the candle dies", 4),
        ["round", "735:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 735: a long session ends when the candle dies", 8),
        ["round", "735: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 735: a long session ends when the candle dies", 12),
        ["round 735: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 735: a long session ends when the candle dies", 16),
        ["round 735: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 735: a long session ends when the candle dies", 24),
        ["round 735: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 735: a long session ends when the candle dies", 32),
        ["round 735: a long session ends", "when the candle dies"],
    ),
    (
        ("round 735: encode the prompt then map the result", 4),
        ["round", "735:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 735: encode the prompt then map the result", 8),
        ["round", "735:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 735: encode the prompt then map the result", 12),
        ["round 735:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 735: encode the prompt then map the result", 16),
        ["round 735:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 735: encode the prompt then map the result", 24),
        ["round 735: encode the", "prompt then map the", "result"],
    ),
    (("round 735: encode the prompt then map the result", 32), ["round 735: encode the prompt", "then map the result"]),
    (
        ("round 735: the kernel wakes the worker at dawn", 4),
        ["round", "735:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 735: the kernel wakes the worker at dawn", 8),
        ["round", "735: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 735: the kernel wakes the worker at dawn", 12),
        ["round 735:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 735: the kernel wakes the worker at dawn", 16), ["round 735: the", "kernel wakes the", "worker at dawn"]),
    (("round 735: the kernel wakes the worker at dawn", 24), ["round 735: the kernel", "wakes the worker at dawn"]),
    (("round 735: the kernel wakes the worker at dawn", 32), ["round 735: the kernel wakes the", "worker at dawn"]),
    (
        ("round 735: service latency drops after the patch", 4),
        ["round", "735:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 735: service latency drops after the patch", 8),
        ["round", "735:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 735: service latency drops after the patch", 12),
        ["round 735:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 735: service latency drops after the patch", 16),
        ["round 735:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 735: service latency drops after the patch", 24),
        ["round 735: service", "latency drops after the", "patch"],
    ),
    (("round 735: service latency drops after the patch", 32), ["round 735: service latency drops", "after the patch"]),
    (
        ("round 735: the library caches every vector it sees", 4),
        ["round", "735:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 735: the library caches every vector it sees", 8),
        ["round", "735: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 735: the library caches every vector it sees", 12),
        ["round 735:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 735: the library caches every vector it sees", 16),
        ["round 735: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 735: the library caches every vector it sees", 24),
        ["round 735: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 735: the library caches every vector it sees", 32),
        ["round 735: the library caches", "every vector it sees"],
    ),
    (
        ("round 735: agents argue then the debate resolves", 4),
        ["round", "735:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 735: agents argue then the debate resolves", 8),
        ["round", "735:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 735: agents argue then the debate resolves", 12),
        ["round 735:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 735: agents argue then the debate resolves", 16),
        ["round 735:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 735: agents argue then the debate resolves", 24), ["round 735: agents argue", "then the debate resolves"]),
    (("round 735: agents argue then the debate resolves", 32), ["round 735: agents argue then the", "debate resolves"]),
    (
        ("round 735: the filter keeps only strong matches", 4),
        ["round", "735:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 735: the filter keeps only strong matches", 8),
        ["round", "735: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 735: the filter keeps only strong matches", 12),
        ["round 735:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 735: the filter keeps only strong matches", 16),
        ["round 735: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 735: the filter keeps only strong matches", 24),
        ["round 735: the filter", "keeps only strong", "matches"],
    ),
    (("round 735: the filter keeps only strong matches", 32), ["round 735: the filter keeps only", "strong matches"]),
    (
        ("round 735: the model answers with a short reply", 4),
        ["round", "735:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 735: the model answers with a short reply", 8),
        ["round", "735: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 735: the model answers with a short reply", 12),
        ["round 735:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 735: the model answers with a short reply", 16),
        ["round 735: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 735: the model answers with a short reply", 24),
        ["round 735: the model", "answers with a short", "reply"],
    ),
    (("round 735: the model answers with a short reply", 32), ["round 735: the model answers", "with a short reply"]),
    (
        ("round 735: the recorder stores the reasoning trace", 4),
        ["round", "735:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 735: the recorder stores the reasoning trace", 8),
        ["round", "735: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 735: the recorder stores the reasoning trace", 12),
        ["round 735:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 735: the recorder stores the reasoning trace", 16),
        ["round 735: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 735: the recorder stores the reasoning trace", 24),
        ["round 735: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 735: the recorder stores the reasoning trace", 32),
        ["round 735: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 735: the angel watches the processor run", 4),
        ["round", "735:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 735: the angel watches the processor run", 8),
        ["round", "735: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 735: the angel watches the processor run", 12),
        ["round 735:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 735: the angel watches the processor run", 16),
        ["round 735: the", "angel watches", "the processor", "run"],
    ),
    (("round 735: the angel watches the processor run", 24), ["round 735: the angel", "watches the processor", "run"]),
    (("round 735: the angel watches the processor run", 32), ["round 735: the angel watches the", "processor run"]),
    (
        ("round 735: angle of the vector decides the match", 4),
        ["round", "735:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 735: angle of the vector decides the match", 8),
        ["round", "735:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 735: angle of the vector decides the match", 12),
        ["round 735:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 735: angle of the vector decides the match", 16),
        ["round 735: angle", "of the vector", "decides the", "match"],
    ),
    (("round 735: angle of the vector decides the match", 24), ["round 735: angle of the", "vector decides the match"]),
    (("round 735: angle of the vector decides the match", 32), ["round 735: angle of the vector", "decides the match"]),
    (
        ("round 735: the candle burns twice as long at night", 4),
        ["round", "735:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 735: the candle burns twice as long at night", 8),
        ["round", "735: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 735: the candle burns twice as long at night", 12),
        ["round 735:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 735: the candle burns twice as long at night", 16),
        ["round 735: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 735: the candle burns twice as long at night", 24),
        ["round 735: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 735: the candle burns twice as long at night", 32),
        ["round 735: the candle burns", "twice as long at night"],
    ),
    (
        ("round 735: a mirror of the universe in one line", 4),
        ["round", "735:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 735: a mirror of the universe in one line", 8),
        ["round", "735: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 735: a mirror of the universe in one line", 12),
        ["round 735: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 735: a mirror of the universe in one line", 16),
        ["round 735: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 735: a mirror of the universe in one line", 24), ["round 735: a mirror of", "the universe in one line"]),
    (("round 735: a mirror of the universe in one line", 32), ["round 735: a mirror of the", "universe in one line"]),
    (
        ("round 735: the queue drains before the storm", 4),
        ["round", "735:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 735: the queue drains before the storm", 8),
        ["round", "735: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 735: the queue drains before the storm", 12),
        ["round 735:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 735: the queue drains before the storm", 16), ["round 735: the", "queue drains", "before the storm"]),
    (("round 735: the queue drains before the storm", 24), ["round 735: the queue", "drains before the storm"]),
    (("round 735: the queue drains before the storm", 32), ["round 735: the queue drains", "before the storm"]),
    (
        ("kitten735 sitting735 agent735 angle735 universe735 memory735", 6),
        ["kitten735", "sitting735", "agent735", "angle735", "universe735", "memory735"],
    ),
    (
        ("kitten735 sitting735 agent735 angle735 universe735 memory735", 10),
        ["kitten735", "sitting735", "agent735", "angle735", "universe735", "memory735"],
    ),
    (
        ("kitten735 sitting735 agent735 angle735 universe735 memory735", 18),
        ["kitten735", "sitting735", "agent735 angle735", "universe735", "memory735"],
    ),
    (
        ("kitten735 sitting735 agent735 angle735 universe735 memory735", 28),
        ["kitten735 sitting735", "agent735 angle735", "universe735 memory735"],
    ),
    (
        ("sitting735 agent735 angle735 universe735 memory735 stream735", 6),
        ["sitting735", "agent735", "angle735", "universe735", "memory735", "stream735"],
    ),
    (
        ("sitting735 agent735 angle735 universe735 memory735 stream735", 10),
        ["sitting735", "agent735", "angle735", "universe735", "memory735", "stream735"],
    ),
    (
        ("sitting735 agent735 angle735 universe735 memory735 stream735", 18),
        ["sitting735", "agent735 angle735", "universe735", "memory735", "stream735"],
    ),
    (
        ("sitting735 agent735 angle735 universe735 memory735 stream735", 28),
        ["sitting735 agent735 angle735", "universe735 memory735", "stream735"],
    ),
    (
        ("agent735 angle735 universe735 memory735 stream735 context735", 6),
        ["agent735", "angle735", "universe735", "memory735", "stream735", "context735"],
    ),
    (
        ("agent735 angle735 universe735 memory735 stream735 context735", 10),
        ["agent735", "angle735", "universe735", "memory735", "stream735", "context735"],
    ),
    (
        ("agent735 angle735 universe735 memory735 stream735 context735", 18),
        ["agent735 angle735", "universe735", "memory735", "stream735", "context735"],
    ),
    (
        ("agent735 angle735 universe735 memory735 stream735 context735", 28),
        ["agent735 angle735", "universe735 memory735", "stream735 context735"],
    ),
    (
        ("angle735 universe735 memory735 stream735 context735 knowledge735", 6),
        ["angle735", "universe735", "memory735", "stream735", "context735", "knowledge735"],
    ),
    (
        ("angle735 universe735 memory735 stream735 context735 knowledge735", 10),
        ["angle735", "universe735", "memory735", "stream735", "context735", "knowledge735"],
    ),
    (
        ("angle735 universe735 memory735 stream735 context735 knowledge735", 18),
        ["angle735", "universe735", "memory735", "stream735", "context735", "knowledge735"],
    ),
    (
        ("angle735 universe735 memory735 stream735 context735 knowledge735", 28),
        ["angle735 universe735", "memory735 stream735", "context735 knowledge735"],
    ),
    (
        ("universe735 memory735 stream735 context735 knowledge735 vector735", 6),
        ["universe735", "memory735", "stream735", "context735", "knowledge735", "vector735"],
    ),
    (
        ("universe735 memory735 stream735 context735 knowledge735 vector735", 10),
        ["universe735", "memory735", "stream735", "context735", "knowledge735", "vector735"],
    ),
    (
        ("universe735 memory735 stream735 context735 knowledge735 vector735", 18),
        ["universe735", "memory735", "stream735", "context735", "knowledge735", "vector735"],
    ),
    (
        ("universe735 memory735 stream735 context735 knowledge735 vector735", 28),
        ["universe735 memory735", "stream735 context735", "knowledge735 vector735"],
    ),
    (
        ("memory735 stream735 context735 knowledge735 vector735 processor735", 6),
        ["memory735", "stream735", "context735", "knowledge735", "vector735", "processor735"],
    ),
    (
        ("memory735 stream735 context735 knowledge735 vector735 processor735", 10),
        ["memory735", "stream735", "context735", "knowledge735", "vector735", "processor735"],
    ),
    (
        ("memory735 stream735 context735 knowledge735 vector735 processor735", 18),
        ["memory735", "stream735", "context735", "knowledge735", "vector735", "processor735"],
    ),
    (
        ("memory735 stream735 context735 knowledge735 vector735 processor735", 28),
        ["memory735 stream735", "context735 knowledge735", "vector735 processor735"],
    ),
    (
        ("stream735 context735 knowledge735 vector735 processor735 reasoning735", 6),
        ["stream735", "context735", "knowledge735", "vector735", "processor735", "reasoning735"],
    ),
    (
        ("stream735 context735 knowledge735 vector735 processor735 reasoning735", 10),
        ["stream735", "context735", "knowledge735", "vector735", "processor735", "reasoning735"],
    ),
    (
        ("stream735 context735 knowledge735 vector735 processor735 reasoning735", 18),
        ["stream735", "context735", "knowledge735", "vector735", "processor735", "reasoning735"],
    ),
    (
        ("stream735 context735 knowledge735 vector735 processor735 reasoning735", 28),
        ["stream735 context735", "knowledge735 vector735", "processor735 reasoning735"],
    ),
    (
        ("context735 knowledge735 vector735 processor735 reasoning735 machine735", 6),
        ["context735", "knowledge735", "vector735", "processor735", "reasoning735", "machine735"],
    ),
    (
        ("context735 knowledge735 vector735 processor735 reasoning735 machine735", 10),
        ["context735", "knowledge735", "vector735", "processor735", "reasoning735", "machine735"],
    ),
    (
        ("context735 knowledge735 vector735 processor735 reasoning735 machine735", 18),
        ["context735", "knowledge735", "vector735", "processor735", "reasoning735", "machine735"],
    ),
    (
        ("context735 knowledge735 vector735 processor735 reasoning735 machine735", 28),
        ["context735 knowledge735", "vector735 processor735", "reasoning735 machine735"],
    ),
    (
        ("knowledge735 vector735 processor735 reasoning735 machine735 learning735", 6),
        ["knowledge735", "vector735", "processor735", "reasoning735", "machine735", "learning735"],
    ),
    (
        ("knowledge735 vector735 processor735 reasoning735 machine735 learning735", 10),
        ["knowledge735", "vector735", "processor735", "reasoning735", "machine735", "learning735"],
    ),
    (
        ("knowledge735 vector735 processor735 reasoning735 machine735 learning735", 18),
        ["knowledge735", "vector735", "processor735", "reasoning735", "machine735", "learning735"],
    ),
    (
        ("knowledge735 vector735 processor735 reasoning735 machine735 learning735", 28),
        ["knowledge735 vector735", "processor735 reasoning735", "machine735 learning735"],
    ),
    (
        ("vector735 processor735 reasoning735 machine735 learning735 model735", 6),
        ["vector735", "processor735", "reasoning735", "machine735", "learning735", "model735"],
    ),
    (
        ("vector735 processor735 reasoning735 machine735 learning735 model735", 10),
        ["vector735", "processor735", "reasoning735", "machine735", "learning735", "model735"],
    ),
    (
        ("vector735 processor735 reasoning735 machine735 learning735 model735", 18),
        ["vector735", "processor735", "reasoning735", "machine735", "learning735", "model735"],
    ),
    (
        ("vector735 processor735 reasoning735 machine735 learning735 model735", 28),
        ["vector735 processor735", "reasoning735 machine735", "learning735 model735"],
    ),
    (
        ("processor735 reasoning735 machine735 learning735 model735 token735", 6),
        ["processor735", "reasoning735", "machine735", "learning735", "model735", "token735"],
    ),
    (
        ("processor735 reasoning735 machine735 learning735 model735 token735", 10),
        ["processor735", "reasoning735", "machine735", "learning735", "model735", "token735"],
    ),
    (
        ("processor735 reasoning735 machine735 learning735 model735 token735", 18),
        ["processor735", "reasoning735", "machine735", "learning735", "model735 token735"],
    ),
    (
        ("processor735 reasoning735 machine735 learning735 model735 token735", 28),
        ["processor735 reasoning735", "machine735 learning735", "model735 token735"],
    ),
    (
        ("reasoning735 machine735 learning735 model735 token735 prompt735", 6),
        ["reasoning735", "machine735", "learning735", "model735", "token735", "prompt735"],
    ),
    (
        ("reasoning735 machine735 learning735 model735 token735 prompt735", 10),
        ["reasoning735", "machine735", "learning735", "model735", "token735", "prompt735"],
    ),
    (
        ("reasoning735 machine735 learning735 model735 token735 prompt735", 18),
        ["reasoning735", "machine735", "learning735", "model735 token735", "prompt735"],
    ),
    (
        ("reasoning735 machine735 learning735 model735 token735 prompt735", 28),
        ["reasoning735 machine735", "learning735 model735", "token735 prompt735"],
    ),
    (
        ("machine735 learning735 model735 token735 prompt735 session735", 6),
        ["machine735", "learning735", "model735", "token735", "prompt735", "session735"],
    ),
    (
        ("machine735 learning735 model735 token735 prompt735 session735", 10),
        ["machine735", "learning735", "model735", "token735", "prompt735", "session735"],
    ),
    (
        ("machine735 learning735 model735 token735 prompt735 session735", 18),
        ["machine735", "learning735", "model735 token735", "prompt735", "session735"],
    ),
    (
        ("machine735 learning735 model735 token735 prompt735 session735", 28),
        ["machine735 learning735", "model735 token735 prompt735", "session735"],
    ),
    (
        ("learning735 model735 token735 prompt735 session735 library735", 6),
        ["learning735", "model735", "token735", "prompt735", "session735", "library735"],
    ),
    (
        ("learning735 model735 token735 prompt735 session735 library735", 10),
        ["learning735", "model735", "token735", "prompt735", "session735", "library735"],
    ),
    (
        ("learning735 model735 token735 prompt735 session735 library735", 18),
        ["learning735", "model735 token735", "prompt735", "session735", "library735"],
    ),
    (
        ("learning735 model735 token735 prompt735 session735 library735", 28),
        ["learning735 model735", "token735 prompt735", "session735 library735"],
    ),
    (
        ("model735 token735 prompt735 session735 library735 service735", 6),
        ["model735", "token735", "prompt735", "session735", "library735", "service735"],
    ),
    (
        ("model735 token735 prompt735 session735 library735 service735", 10),
        ["model735", "token735", "prompt735", "session735", "library735", "service735"],
    ),
    (
        ("model735 token735 prompt735 session735 library735 service735", 18),
        ["model735 token735", "prompt735", "session735", "library735", "service735"],
    ),
    (
        ("model735 token735 prompt735 session735 library735 service735", 28),
        ["model735 token735 prompt735", "session735 library735", "service735"],
    ),
    (
        ("token735 prompt735 session735 library735 service735 gateway735", 6),
        ["token735", "prompt735", "session735", "library735", "service735", "gateway735"],
    ),
    (
        ("token735 prompt735 session735 library735 service735 gateway735", 10),
        ["token735", "prompt735", "session735", "library735", "service735", "gateway735"],
    ),
    (
        ("token735 prompt735 session735 library735 service735 gateway735", 18),
        ["token735 prompt735", "session735", "library735", "service735", "gateway735"],
    ),
    (
        ("token735 prompt735 session735 library735 service735 gateway735", 28),
        ["token735 prompt735", "session735 library735", "service735 gateway735"],
    ),
    (
        ("prompt735 session735 library735 service735 gateway735 storage735", 6),
        ["prompt735", "session735", "library735", "service735", "gateway735", "storage735"],
    ),
    (
        ("prompt735 session735 library735 service735 gateway735 storage735", 10),
        ["prompt735", "session735", "library735", "service735", "gateway735", "storage735"],
    ),
    (
        ("prompt735 session735 library735 service735 gateway735 storage735", 18),
        ["prompt735", "session735", "library735", "service735", "gateway735", "storage735"],
    ),
    (
        ("prompt735 session735 library735 service735 gateway735 storage735", 28),
        ["prompt735 session735", "library735 service735", "gateway735 storage735"],
    ),
    (
        ("session735 library735 service735 gateway735 storage735 network735", 6),
        ["session735", "library735", "service735", "gateway735", "storage735", "network735"],
    ),
    (
        ("session735 library735 service735 gateway735 storage735 network735", 10),
        ["session735", "library735", "service735", "gateway735", "storage735", "network735"],
    ),
    (
        ("session735 library735 service735 gateway735 storage735 network735", 18),
        ["session735", "library735", "service735", "gateway735", "storage735", "network735"],
    ),
    (
        ("session735 library735 service735 gateway735 storage735 network735", 28),
        ["session735 library735", "service735 gateway735", "storage735 network735"],
    ),
    (
        ("library735 service735 gateway735 storage735 network735 latency735", 6),
        ["library735", "service735", "gateway735", "storage735", "network735", "latency735"],
    ),
    (
        ("library735 service735 gateway735 storage735 network735 latency735", 10),
        ["library735", "service735", "gateway735", "storage735", "network735", "latency735"],
    ),
    (
        ("library735 service735 gateway735 storage735 network735 latency735", 18),
        ["library735", "service735", "gateway735", "storage735", "network735", "latency735"],
    ),
    (
        ("library735 service735 gateway735 storage735 network735 latency735", 28),
        ["library735 service735", "gateway735 storage735", "network735 latency735"],
    ),
    (
        ("service735 gateway735 storage735 network735 latency735 buffer735", 6),
        ["service735", "gateway735", "storage735", "network735", "latency735", "buffer735"],
    ),
    (
        ("service735 gateway735 storage735 network735 latency735 buffer735", 10),
        ["service735", "gateway735", "storage735", "network735", "latency735", "buffer735"],
    ),
    (
        ("service735 gateway735 storage735 network735 latency735 buffer735", 18),
        ["service735", "gateway735", "storage735", "network735", "latency735", "buffer735"],
    ),
    (
        ("service735 gateway735 storage735 network735 latency735 buffer735", 28),
        ["service735 gateway735", "storage735 network735", "latency735 buffer735"],
    ),
    (
        ("gateway735 storage735 network735 latency735 buffer735 queue735", 6),
        ["gateway735", "storage735", "network735", "latency735", "buffer735", "queue735"],
    ),
    (
        ("gateway735 storage735 network735 latency735 buffer735 queue735", 10),
        ["gateway735", "storage735", "network735", "latency735", "buffer735", "queue735"],
    ),
    (
        ("gateway735 storage735 network735 latency735 buffer735 queue735", 18),
        ["gateway735", "storage735", "network735", "latency735", "buffer735 queue735"],
    ),
    (
        ("gateway735 storage735 network735 latency735 buffer735 queue735", 28),
        ["gateway735 storage735", "network735 latency735", "buffer735 queue735"],
    ),
    (
        ("storage735 network735 latency735 buffer735 queue735 worker735", 6),
        ["storage735", "network735", "latency735", "buffer735", "queue735", "worker735"],
    ),
    (
        ("storage735 network735 latency735 buffer735 queue735 worker735", 10),
        ["storage735", "network735", "latency735", "buffer735", "queue735", "worker735"],
    ),
    (
        ("storage735 network735 latency735 buffer735 queue735 worker735", 18),
        ["storage735", "network735", "latency735", "buffer735 queue735", "worker735"],
    ),
    (
        ("storage735 network735 latency735 buffer735 queue735 worker735", 28),
        ["storage735 network735", "latency735 buffer735", "queue735 worker735"],
    ),
    (
        ("network735 latency735 buffer735 queue735 worker735 kernel735", 6),
        ["network735", "latency735", "buffer735", "queue735", "worker735", "kernel735"],
    ),
    (
        ("network735 latency735 buffer735 queue735 worker735 kernel735", 10),
        ["network735", "latency735", "buffer735", "queue735", "worker735", "kernel735"],
    ),
    (
        ("network735 latency735 buffer735 queue735 worker735 kernel735", 18),
        ["network735", "latency735", "buffer735 queue735", "worker735", "kernel735"],
    ),
    (
        ("network735 latency735 buffer735 queue735 worker735 kernel735", 28),
        ["network735 latency735", "buffer735 queue735 worker735", "kernel735"],
    ),
    (
        ("latency735 buffer735 queue735 worker735 kernel735 signal735", 6),
        ["latency735", "buffer735", "queue735", "worker735", "kernel735", "signal735"],
    ),
    (
        ("latency735 buffer735 queue735 worker735 kernel735 signal735", 10),
        ["latency735", "buffer735", "queue735", "worker735", "kernel735", "signal735"],
    ),
    (
        ("latency735 buffer735 queue735 worker735 kernel735 signal735", 18),
        ["latency735", "buffer735 queue735", "worker735", "kernel735", "signal735"],
    ),
    (
        ("latency735 buffer735 queue735 worker735 kernel735 signal735", 28),
        ["latency735 buffer735", "queue735 worker735 kernel735", "signal735"],
    ),
    (
        ("buffer735 queue735 worker735 kernel735 signal735 packet735", 6),
        ["buffer735", "queue735", "worker735", "kernel735", "signal735", "packet735"],
    ),
    (
        ("buffer735 queue735 worker735 kernel735 signal735 packet735", 10),
        ["buffer735", "queue735", "worker735", "kernel735", "signal735", "packet735"],
    ),
    (
        ("buffer735 queue735 worker735 kernel735 signal735 packet735", 18),
        ["buffer735 queue735", "worker735", "kernel735", "signal735", "packet735"],
    ),
    (
        ("buffer735 queue735 worker735 kernel735 signal735 packet735", 28),
        ["buffer735 queue735 worker735", "kernel735 signal735", "packet735"],
    ),
    (
        ("queue735 worker735 kernel735 signal735 packet735 router735", 6),
        ["queue735", "worker735", "kernel735", "signal735", "packet735", "router735"],
    ),
    (
        ("queue735 worker735 kernel735 signal735 packet735 router735", 10),
        ["queue735", "worker735", "kernel735", "signal735", "packet735", "router735"],
    ),
    (
        ("queue735 worker735 kernel735 signal735 packet735 router735", 18),
        ["queue735 worker735", "kernel735", "signal735", "packet735", "router735"],
    ),
    (
        ("queue735 worker735 kernel735 signal735 packet735 router735", 28),
        ["queue735 worker735 kernel735", "signal735 packet735", "router735"],
    ),
    (
        ("worker735 kernel735 signal735 packet735 router735 cluster735", 6),
        ["worker735", "kernel735", "signal735", "packet735", "router735", "cluster735"],
    ),
    (
        ("worker735 kernel735 signal735 packet735 router735 cluster735", 10),
        ["worker735", "kernel735", "signal735", "packet735", "router735", "cluster735"],
    ),
    (
        ("worker735 kernel735 signal735 packet735 router735 cluster735", 18),
        ["worker735", "kernel735", "signal735", "packet735", "router735", "cluster735"],
    ),
    (
        ("worker735 kernel735 signal735 packet735 router735 cluster735", 28),
        ["worker735 kernel735", "signal735 packet735", "router735 cluster735"],
    ),
    (
        ("kernel735 signal735 packet735 router735 cluster735 mirror735", 6),
        ["kernel735", "signal735", "packet735", "router735", "cluster735", "mirror735"],
    ),
    (
        ("kernel735 signal735 packet735 router735 cluster735 mirror735", 10),
        ["kernel735", "signal735", "packet735", "router735", "cluster735", "mirror735"],
    ),
    (
        ("kernel735 signal735 packet735 router735 cluster735 mirror735", 18),
        ["kernel735", "signal735", "packet735", "router735", "cluster735", "mirror735"],
    ),
    (
        ("kernel735 signal735 packet735 router735 cluster735 mirror735", 28),
        ["kernel735 signal735", "packet735 router735", "cluster735 mirror735"],
    ),
    (
        ("signal735 packet735 router735 cluster735 mirror735 filter735", 6),
        ["signal735", "packet735", "router735", "cluster735", "mirror735", "filter735"],
    ),
    (
        ("signal735 packet735 router735 cluster735 mirror735 filter735", 10),
        ["signal735", "packet735", "router735", "cluster735", "mirror735", "filter735"],
    ),
    (
        ("signal735 packet735 router735 cluster735 mirror735 filter735", 18),
        ["signal735", "packet735", "router735", "cluster735", "mirror735", "filter735"],
    ),
    (
        ("signal735 packet735 router735 cluster735 mirror735 filter735", 28),
        ["signal735 packet735", "router735 cluster735", "mirror735 filter735"],
    ),
    (
        ("packet735 router735 cluster735 mirror735 filter735 ranking735", 6),
        ["packet735", "router735", "cluster735", "mirror735", "filter735", "ranking735"],
    ),
    (
        ("packet735 router735 cluster735 mirror735 filter735 ranking735", 10),
        ["packet735", "router735", "cluster735", "mirror735", "filter735", "ranking735"],
    ),
    (
        ("packet735 router735 cluster735 mirror735 filter735 ranking735", 18),
        ["packet735", "router735", "cluster735", "mirror735", "filter735", "ranking735"],
    ),
    (
        ("packet735 router735 cluster735 mirror735 filter735 ranking735", 28),
        ["packet735 router735", "cluster735 mirror735", "filter735 ranking735"],
    ),
    (
        ("router735 cluster735 mirror735 filter735 ranking735 encoding735", 6),
        ["router735", "cluster735", "mirror735", "filter735", "ranking735", "encoding735"],
    ),
    (
        ("router735 cluster735 mirror735 filter735 ranking735 encoding735", 10),
        ["router735", "cluster735", "mirror735", "filter735", "ranking735", "encoding735"],
    ),
    (
        ("router735 cluster735 mirror735 filter735 ranking735 encoding735", 18),
        ["router735", "cluster735", "mirror735", "filter735", "ranking735", "encoding735"],
    ),
    (
        ("router735 cluster735 mirror735 filter735 ranking735 encoding735", 28),
        ["router735 cluster735", "mirror735 filter735", "ranking735 encoding735"],
    ),
    (
        ("cluster735 mirror735 filter735 ranking735 encoding735 mapping735", 6),
        ["cluster735", "mirror735", "filter735", "ranking735", "encoding735", "mapping735"],
    ),
    (
        ("cluster735 mirror735 filter735 ranking735 encoding735 mapping735", 10),
        ["cluster735", "mirror735", "filter735", "ranking735", "encoding735", "mapping735"],
    ),
    (
        ("cluster735 mirror735 filter735 ranking735 encoding735 mapping735", 18),
        ["cluster735", "mirror735", "filter735", "ranking735", "encoding735", "mapping735"],
    ),
    (
        ("cluster735 mirror735 filter735 ranking735 encoding735 mapping735", 28),
        ["cluster735 mirror735", "filter735 ranking735", "encoding735 mapping735"],
    ),
    (
        ("mirror735 filter735 ranking735 encoding735 mapping735 record735", 6),
        ["mirror735", "filter735", "ranking735", "encoding735", "mapping735", "record735"],
    ),
    (
        ("mirror735 filter735 ranking735 encoding735 mapping735 record735", 10),
        ["mirror735", "filter735", "ranking735", "encoding735", "mapping735", "record735"],
    ),
    (
        ("mirror735 filter735 ranking735 encoding735 mapping735 record735", 18),
        ["mirror735", "filter735", "ranking735", "encoding735", "mapping735", "record735"],
    ),
    (
        ("mirror735 filter735 ranking735 encoding735 mapping735 record735", 28),
        ["mirror735 filter735", "ranking735 encoding735", "mapping735 record735"],
    ),
    (
        ("filter735 ranking735 encoding735 mapping735 record735 candle735", 6),
        ["filter735", "ranking735", "encoding735", "mapping735", "record735", "candle735"],
    ),
    (
        ("filter735 ranking735 encoding735 mapping735 record735 candle735", 10),
        ["filter735", "ranking735", "encoding735", "mapping735", "record735", "candle735"],
    ),
    (
        ("filter735 ranking735 encoding735 mapping735 record735 candle735", 18),
        ["filter735", "ranking735", "encoding735", "mapping735", "record735", "candle735"],
    ),
    (
        ("filter735 ranking735 encoding735 mapping735 record735 candle735", 28),
        ["filter735 ranking735", "encoding735 mapping735", "record735 candle735"],
    ),
    (
        ("ranking735 encoding735 mapping735 record735 candle735 thread735", 6),
        ["ranking735", "encoding735", "mapping735", "record735", "candle735", "thread735"],
    ),
    (
        ("ranking735 encoding735 mapping735 record735 candle735 thread735", 10),
        ["ranking735", "encoding735", "mapping735", "record735", "candle735", "thread735"],
    ),
    (
        ("ranking735 encoding735 mapping735 record735 candle735 thread735", 18),
        ["ranking735", "encoding735", "mapping735", "record735", "candle735", "thread735"],
    ),
    (
        ("ranking735 encoding735 mapping735 record735 candle735 thread735", 28),
        ["ranking735 encoding735", "mapping735 record735", "candle735 thread735"],
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
