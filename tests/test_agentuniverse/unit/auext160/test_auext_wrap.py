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
        ("round 160: the quick brown fox jumps over the lazy dog", 4),
        ["round", "160:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", 8),
        ["round", "160: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", 12),
        ["round 160:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", 16),
        ["round 160: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", 24),
        ["round 160: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 160: the quick brown fox jumps over the lazy dog", 32),
        ["round 160: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", 4),
        ["round", "160:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", 8),
        ["round", "160:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", 12),
        ["round 160:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", 16),
        ["round 160:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", 24),
        ["round 160: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 160: agentuniverse is a framework for multi agents", 32),
        ["round 160: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", 4),
        ["round", "160:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", 8),
        ["round", "160:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", 12),
        ["round 160:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", 16),
        ["round 160:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", 24),
        ["round 160: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 160: knowledge stored as vectors enables retrieval", 32),
        ["round 160: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 160: the processor reads the record then stops", 4),
        ["round", "160:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 160: the processor reads the record then stops", 8),
        ["round", "160: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 160: the processor reads the record then stops", 12),
        ["round 160:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 160: the processor reads the record then stops", 16),
        ["round 160: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 160: the processor reads the record then stops", 24),
        ["round 160: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 160: the processor reads the record then stops", 32),
        ["round 160: the processor reads", "the record then stops"],
    ),
    (
        ("round 160: a worker pulls the next task from the queue", 4),
        ["round", "160:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 160: a worker pulls the next task from the queue", 8),
        ["round", "160: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 160: a worker pulls the next task from the queue", 12),
        ["round 160: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 160: a worker pulls the next task from the queue", 16),
        ["round 160: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 160: a worker pulls the next task from the queue", 24),
        ["round 160: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 160: a worker pulls the next task from the queue", 32),
        ["round 160: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 160: signals travel through the network layer", 4),
        ["round", "160:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 160: signals travel through the network layer", 8),
        ["round", "160:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 160: signals travel through the network layer", 12),
        ["round 160:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 160: signals travel through the network layer", 16),
        ["round 160:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 160: signals travel through the network layer", 24),
        ["round 160: signals", "travel through the", "network layer"],
    ),
    (
        ("round 160: signals travel through the network layer", 32),
        ["round 160: signals travel", "through the network layer"],
    ),
    (
        ("round 160: the gateway routes each request by policy", 4),
        ["round", "160:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 160: the gateway routes each request by policy", 8),
        ["round", "160: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 160: the gateway routes each request by policy", 12),
        ["round 160:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 160: the gateway routes each request by policy", 16),
        ["round 160: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 160: the gateway routes each request by policy", 24),
        ["round 160: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 160: the gateway routes each request by policy", 32),
        ["round 160: the gateway routes", "each request by policy"],
    ),
    (
        ("round 160: memory grows until the buffer is full", 4),
        ["round", "160:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 160: memory grows until the buffer is full", 8),
        ["round", "160:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 160: memory grows until the buffer is full", 12),
        ["round 160:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 160: memory grows until the buffer is full", 16),
        ["round 160:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 160: memory grows until the buffer is full", 24), ["round 160: memory grows", "until the buffer is full"]),
    (("round 160: memory grows until the buffer is full", 32), ["round 160: memory grows until", "the buffer is full"]),
    (
        ("round 160: the cluster mirrors every packet twice", 4),
        ["round", "160:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 160: the cluster mirrors every packet twice", 8),
        ["round", "160: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 160: the cluster mirrors every packet twice", 12),
        ["round 160:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 160: the cluster mirrors every packet twice", 16),
        ["round 160: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 160: the cluster mirrors every packet twice", 24),
        ["round 160: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 160: the cluster mirrors every packet twice", 32),
        ["round 160: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", 4),
        ["round", "160:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", 8),
        ["round", "160:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", 12),
        ["round 160:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", 16),
        ["round 160:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", 24),
        ["round 160: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 160: ranking uses tokens learned from the corpus", 32),
        ["round 160: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 160: a long session ends when the candle dies", 4),
        ["round", "160:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 160: a long session ends when the candle dies", 8),
        ["round", "160: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 160: a long session ends when the candle dies", 12),
        ["round 160: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 160: a long session ends when the candle dies", 16),
        ["round 160: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 160: a long session ends when the candle dies", 24),
        ["round 160: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 160: a long session ends when the candle dies", 32),
        ["round 160: a long session ends", "when the candle dies"],
    ),
    (
        ("round 160: encode the prompt then map the result", 4),
        ["round", "160:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 160: encode the prompt then map the result", 8),
        ["round", "160:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 160: encode the prompt then map the result", 12),
        ["round 160:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 160: encode the prompt then map the result", 16),
        ["round 160:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 160: encode the prompt then map the result", 24),
        ["round 160: encode the", "prompt then map the", "result"],
    ),
    (("round 160: encode the prompt then map the result", 32), ["round 160: encode the prompt", "then map the result"]),
    (
        ("round 160: the kernel wakes the worker at dawn", 4),
        ["round", "160:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 160: the kernel wakes the worker at dawn", 8),
        ["round", "160: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 160: the kernel wakes the worker at dawn", 12),
        ["round 160:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 160: the kernel wakes the worker at dawn", 16), ["round 160: the", "kernel wakes the", "worker at dawn"]),
    (("round 160: the kernel wakes the worker at dawn", 24), ["round 160: the kernel", "wakes the worker at dawn"]),
    (("round 160: the kernel wakes the worker at dawn", 32), ["round 160: the kernel wakes the", "worker at dawn"]),
    (
        ("round 160: service latency drops after the patch", 4),
        ["round", "160:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 160: service latency drops after the patch", 8),
        ["round", "160:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 160: service latency drops after the patch", 12),
        ["round 160:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 160: service latency drops after the patch", 16),
        ["round 160:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 160: service latency drops after the patch", 24),
        ["round 160: service", "latency drops after the", "patch"],
    ),
    (("round 160: service latency drops after the patch", 32), ["round 160: service latency drops", "after the patch"]),
    (
        ("round 160: the library caches every vector it sees", 4),
        ["round", "160:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 160: the library caches every vector it sees", 8),
        ["round", "160: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 160: the library caches every vector it sees", 12),
        ["round 160:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 160: the library caches every vector it sees", 16),
        ["round 160: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 160: the library caches every vector it sees", 24),
        ["round 160: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 160: the library caches every vector it sees", 32),
        ["round 160: the library caches", "every vector it sees"],
    ),
    (
        ("round 160: agents argue then the debate resolves", 4),
        ["round", "160:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 160: agents argue then the debate resolves", 8),
        ["round", "160:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 160: agents argue then the debate resolves", 12),
        ["round 160:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 160: agents argue then the debate resolves", 16),
        ["round 160:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 160: agents argue then the debate resolves", 24), ["round 160: agents argue", "then the debate resolves"]),
    (("round 160: agents argue then the debate resolves", 32), ["round 160: agents argue then the", "debate resolves"]),
    (
        ("round 160: the filter keeps only strong matches", 4),
        ["round", "160:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 160: the filter keeps only strong matches", 8),
        ["round", "160: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 160: the filter keeps only strong matches", 12),
        ["round 160:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 160: the filter keeps only strong matches", 16),
        ["round 160: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 160: the filter keeps only strong matches", 24),
        ["round 160: the filter", "keeps only strong", "matches"],
    ),
    (("round 160: the filter keeps only strong matches", 32), ["round 160: the filter keeps only", "strong matches"]),
    (
        ("round 160: the model answers with a short reply", 4),
        ["round", "160:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 160: the model answers with a short reply", 8),
        ["round", "160: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 160: the model answers with a short reply", 12),
        ["round 160:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 160: the model answers with a short reply", 16),
        ["round 160: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 160: the model answers with a short reply", 24),
        ["round 160: the model", "answers with a short", "reply"],
    ),
    (("round 160: the model answers with a short reply", 32), ["round 160: the model answers", "with a short reply"]),
    (
        ("round 160: the recorder stores the reasoning trace", 4),
        ["round", "160:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 160: the recorder stores the reasoning trace", 8),
        ["round", "160: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 160: the recorder stores the reasoning trace", 12),
        ["round 160:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 160: the recorder stores the reasoning trace", 16),
        ["round 160: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 160: the recorder stores the reasoning trace", 24),
        ["round 160: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 160: the recorder stores the reasoning trace", 32),
        ["round 160: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 160: the angel watches the processor run", 4),
        ["round", "160:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 160: the angel watches the processor run", 8),
        ["round", "160: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 160: the angel watches the processor run", 12),
        ["round 160:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 160: the angel watches the processor run", 16),
        ["round 160: the", "angel watches", "the processor", "run"],
    ),
    (("round 160: the angel watches the processor run", 24), ["round 160: the angel", "watches the processor", "run"]),
    (("round 160: the angel watches the processor run", 32), ["round 160: the angel watches the", "processor run"]),
    (
        ("round 160: angle of the vector decides the match", 4),
        ["round", "160:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 160: angle of the vector decides the match", 8),
        ["round", "160:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 160: angle of the vector decides the match", 12),
        ["round 160:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 160: angle of the vector decides the match", 16),
        ["round 160: angle", "of the vector", "decides the", "match"],
    ),
    (("round 160: angle of the vector decides the match", 24), ["round 160: angle of the", "vector decides the match"]),
    (("round 160: angle of the vector decides the match", 32), ["round 160: angle of the vector", "decides the match"]),
    (
        ("round 160: the candle burns twice as long at night", 4),
        ["round", "160:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 160: the candle burns twice as long at night", 8),
        ["round", "160: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 160: the candle burns twice as long at night", 12),
        ["round 160:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 160: the candle burns twice as long at night", 16),
        ["round 160: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 160: the candle burns twice as long at night", 24),
        ["round 160: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 160: the candle burns twice as long at night", 32),
        ["round 160: the candle burns", "twice as long at night"],
    ),
    (
        ("round 160: a mirror of the universe in one line", 4),
        ["round", "160:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 160: a mirror of the universe in one line", 8),
        ["round", "160: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 160: a mirror of the universe in one line", 12),
        ["round 160: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 160: a mirror of the universe in one line", 16),
        ["round 160: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 160: a mirror of the universe in one line", 24), ["round 160: a mirror of", "the universe in one line"]),
    (("round 160: a mirror of the universe in one line", 32), ["round 160: a mirror of the", "universe in one line"]),
    (
        ("round 160: the queue drains before the storm", 4),
        ["round", "160:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 160: the queue drains before the storm", 8),
        ["round", "160: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 160: the queue drains before the storm", 12),
        ["round 160:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 160: the queue drains before the storm", 16), ["round 160: the", "queue drains", "before the storm"]),
    (("round 160: the queue drains before the storm", 24), ["round 160: the queue", "drains before the storm"]),
    (("round 160: the queue drains before the storm", 32), ["round 160: the queue drains", "before the storm"]),
    (
        ("kitten160 sitting160 agent160 angle160 universe160 memory160", 6),
        ["kitten160", "sitting160", "agent160", "angle160", "universe160", "memory160"],
    ),
    (
        ("kitten160 sitting160 agent160 angle160 universe160 memory160", 10),
        ["kitten160", "sitting160", "agent160", "angle160", "universe160", "memory160"],
    ),
    (
        ("kitten160 sitting160 agent160 angle160 universe160 memory160", 18),
        ["kitten160", "sitting160", "agent160 angle160", "universe160", "memory160"],
    ),
    (
        ("kitten160 sitting160 agent160 angle160 universe160 memory160", 28),
        ["kitten160 sitting160", "agent160 angle160", "universe160 memory160"],
    ),
    (
        ("sitting160 agent160 angle160 universe160 memory160 stream160", 6),
        ["sitting160", "agent160", "angle160", "universe160", "memory160", "stream160"],
    ),
    (
        ("sitting160 agent160 angle160 universe160 memory160 stream160", 10),
        ["sitting160", "agent160", "angle160", "universe160", "memory160", "stream160"],
    ),
    (
        ("sitting160 agent160 angle160 universe160 memory160 stream160", 18),
        ["sitting160", "agent160 angle160", "universe160", "memory160", "stream160"],
    ),
    (
        ("sitting160 agent160 angle160 universe160 memory160 stream160", 28),
        ["sitting160 agent160 angle160", "universe160 memory160", "stream160"],
    ),
    (
        ("agent160 angle160 universe160 memory160 stream160 context160", 6),
        ["agent160", "angle160", "universe160", "memory160", "stream160", "context160"],
    ),
    (
        ("agent160 angle160 universe160 memory160 stream160 context160", 10),
        ["agent160", "angle160", "universe160", "memory160", "stream160", "context160"],
    ),
    (
        ("agent160 angle160 universe160 memory160 stream160 context160", 18),
        ["agent160 angle160", "universe160", "memory160", "stream160", "context160"],
    ),
    (
        ("agent160 angle160 universe160 memory160 stream160 context160", 28),
        ["agent160 angle160", "universe160 memory160", "stream160 context160"],
    ),
    (
        ("angle160 universe160 memory160 stream160 context160 knowledge160", 6),
        ["angle160", "universe160", "memory160", "stream160", "context160", "knowledge160"],
    ),
    (
        ("angle160 universe160 memory160 stream160 context160 knowledge160", 10),
        ["angle160", "universe160", "memory160", "stream160", "context160", "knowledge160"],
    ),
    (
        ("angle160 universe160 memory160 stream160 context160 knowledge160", 18),
        ["angle160", "universe160", "memory160", "stream160", "context160", "knowledge160"],
    ),
    (
        ("angle160 universe160 memory160 stream160 context160 knowledge160", 28),
        ["angle160 universe160", "memory160 stream160", "context160 knowledge160"],
    ),
    (
        ("universe160 memory160 stream160 context160 knowledge160 vector160", 6),
        ["universe160", "memory160", "stream160", "context160", "knowledge160", "vector160"],
    ),
    (
        ("universe160 memory160 stream160 context160 knowledge160 vector160", 10),
        ["universe160", "memory160", "stream160", "context160", "knowledge160", "vector160"],
    ),
    (
        ("universe160 memory160 stream160 context160 knowledge160 vector160", 18),
        ["universe160", "memory160", "stream160", "context160", "knowledge160", "vector160"],
    ),
    (
        ("universe160 memory160 stream160 context160 knowledge160 vector160", 28),
        ["universe160 memory160", "stream160 context160", "knowledge160 vector160"],
    ),
    (
        ("memory160 stream160 context160 knowledge160 vector160 processor160", 6),
        ["memory160", "stream160", "context160", "knowledge160", "vector160", "processor160"],
    ),
    (
        ("memory160 stream160 context160 knowledge160 vector160 processor160", 10),
        ["memory160", "stream160", "context160", "knowledge160", "vector160", "processor160"],
    ),
    (
        ("memory160 stream160 context160 knowledge160 vector160 processor160", 18),
        ["memory160", "stream160", "context160", "knowledge160", "vector160", "processor160"],
    ),
    (
        ("memory160 stream160 context160 knowledge160 vector160 processor160", 28),
        ["memory160 stream160", "context160 knowledge160", "vector160 processor160"],
    ),
    (
        ("stream160 context160 knowledge160 vector160 processor160 reasoning160", 6),
        ["stream160", "context160", "knowledge160", "vector160", "processor160", "reasoning160"],
    ),
    (
        ("stream160 context160 knowledge160 vector160 processor160 reasoning160", 10),
        ["stream160", "context160", "knowledge160", "vector160", "processor160", "reasoning160"],
    ),
    (
        ("stream160 context160 knowledge160 vector160 processor160 reasoning160", 18),
        ["stream160", "context160", "knowledge160", "vector160", "processor160", "reasoning160"],
    ),
    (
        ("stream160 context160 knowledge160 vector160 processor160 reasoning160", 28),
        ["stream160 context160", "knowledge160 vector160", "processor160 reasoning160"],
    ),
    (
        ("context160 knowledge160 vector160 processor160 reasoning160 machine160", 6),
        ["context160", "knowledge160", "vector160", "processor160", "reasoning160", "machine160"],
    ),
    (
        ("context160 knowledge160 vector160 processor160 reasoning160 machine160", 10),
        ["context160", "knowledge160", "vector160", "processor160", "reasoning160", "machine160"],
    ),
    (
        ("context160 knowledge160 vector160 processor160 reasoning160 machine160", 18),
        ["context160", "knowledge160", "vector160", "processor160", "reasoning160", "machine160"],
    ),
    (
        ("context160 knowledge160 vector160 processor160 reasoning160 machine160", 28),
        ["context160 knowledge160", "vector160 processor160", "reasoning160 machine160"],
    ),
    (
        ("knowledge160 vector160 processor160 reasoning160 machine160 learning160", 6),
        ["knowledge160", "vector160", "processor160", "reasoning160", "machine160", "learning160"],
    ),
    (
        ("knowledge160 vector160 processor160 reasoning160 machine160 learning160", 10),
        ["knowledge160", "vector160", "processor160", "reasoning160", "machine160", "learning160"],
    ),
    (
        ("knowledge160 vector160 processor160 reasoning160 machine160 learning160", 18),
        ["knowledge160", "vector160", "processor160", "reasoning160", "machine160", "learning160"],
    ),
    (
        ("knowledge160 vector160 processor160 reasoning160 machine160 learning160", 28),
        ["knowledge160 vector160", "processor160 reasoning160", "machine160 learning160"],
    ),
    (
        ("vector160 processor160 reasoning160 machine160 learning160 model160", 6),
        ["vector160", "processor160", "reasoning160", "machine160", "learning160", "model160"],
    ),
    (
        ("vector160 processor160 reasoning160 machine160 learning160 model160", 10),
        ["vector160", "processor160", "reasoning160", "machine160", "learning160", "model160"],
    ),
    (
        ("vector160 processor160 reasoning160 machine160 learning160 model160", 18),
        ["vector160", "processor160", "reasoning160", "machine160", "learning160", "model160"],
    ),
    (
        ("vector160 processor160 reasoning160 machine160 learning160 model160", 28),
        ["vector160 processor160", "reasoning160 machine160", "learning160 model160"],
    ),
    (
        ("processor160 reasoning160 machine160 learning160 model160 token160", 6),
        ["processor160", "reasoning160", "machine160", "learning160", "model160", "token160"],
    ),
    (
        ("processor160 reasoning160 machine160 learning160 model160 token160", 10),
        ["processor160", "reasoning160", "machine160", "learning160", "model160", "token160"],
    ),
    (
        ("processor160 reasoning160 machine160 learning160 model160 token160", 18),
        ["processor160", "reasoning160", "machine160", "learning160", "model160 token160"],
    ),
    (
        ("processor160 reasoning160 machine160 learning160 model160 token160", 28),
        ["processor160 reasoning160", "machine160 learning160", "model160 token160"],
    ),
    (
        ("reasoning160 machine160 learning160 model160 token160 prompt160", 6),
        ["reasoning160", "machine160", "learning160", "model160", "token160", "prompt160"],
    ),
    (
        ("reasoning160 machine160 learning160 model160 token160 prompt160", 10),
        ["reasoning160", "machine160", "learning160", "model160", "token160", "prompt160"],
    ),
    (
        ("reasoning160 machine160 learning160 model160 token160 prompt160", 18),
        ["reasoning160", "machine160", "learning160", "model160 token160", "prompt160"],
    ),
    (
        ("reasoning160 machine160 learning160 model160 token160 prompt160", 28),
        ["reasoning160 machine160", "learning160 model160", "token160 prompt160"],
    ),
    (
        ("machine160 learning160 model160 token160 prompt160 session160", 6),
        ["machine160", "learning160", "model160", "token160", "prompt160", "session160"],
    ),
    (
        ("machine160 learning160 model160 token160 prompt160 session160", 10),
        ["machine160", "learning160", "model160", "token160", "prompt160", "session160"],
    ),
    (
        ("machine160 learning160 model160 token160 prompt160 session160", 18),
        ["machine160", "learning160", "model160 token160", "prompt160", "session160"],
    ),
    (
        ("machine160 learning160 model160 token160 prompt160 session160", 28),
        ["machine160 learning160", "model160 token160 prompt160", "session160"],
    ),
    (
        ("learning160 model160 token160 prompt160 session160 library160", 6),
        ["learning160", "model160", "token160", "prompt160", "session160", "library160"],
    ),
    (
        ("learning160 model160 token160 prompt160 session160 library160", 10),
        ["learning160", "model160", "token160", "prompt160", "session160", "library160"],
    ),
    (
        ("learning160 model160 token160 prompt160 session160 library160", 18),
        ["learning160", "model160 token160", "prompt160", "session160", "library160"],
    ),
    (
        ("learning160 model160 token160 prompt160 session160 library160", 28),
        ["learning160 model160", "token160 prompt160", "session160 library160"],
    ),
    (
        ("model160 token160 prompt160 session160 library160 service160", 6),
        ["model160", "token160", "prompt160", "session160", "library160", "service160"],
    ),
    (
        ("model160 token160 prompt160 session160 library160 service160", 10),
        ["model160", "token160", "prompt160", "session160", "library160", "service160"],
    ),
    (
        ("model160 token160 prompt160 session160 library160 service160", 18),
        ["model160 token160", "prompt160", "session160", "library160", "service160"],
    ),
    (
        ("model160 token160 prompt160 session160 library160 service160", 28),
        ["model160 token160 prompt160", "session160 library160", "service160"],
    ),
    (
        ("token160 prompt160 session160 library160 service160 gateway160", 6),
        ["token160", "prompt160", "session160", "library160", "service160", "gateway160"],
    ),
    (
        ("token160 prompt160 session160 library160 service160 gateway160", 10),
        ["token160", "prompt160", "session160", "library160", "service160", "gateway160"],
    ),
    (
        ("token160 prompt160 session160 library160 service160 gateway160", 18),
        ["token160 prompt160", "session160", "library160", "service160", "gateway160"],
    ),
    (
        ("token160 prompt160 session160 library160 service160 gateway160", 28),
        ["token160 prompt160", "session160 library160", "service160 gateway160"],
    ),
    (
        ("prompt160 session160 library160 service160 gateway160 storage160", 6),
        ["prompt160", "session160", "library160", "service160", "gateway160", "storage160"],
    ),
    (
        ("prompt160 session160 library160 service160 gateway160 storage160", 10),
        ["prompt160", "session160", "library160", "service160", "gateway160", "storage160"],
    ),
    (
        ("prompt160 session160 library160 service160 gateway160 storage160", 18),
        ["prompt160", "session160", "library160", "service160", "gateway160", "storage160"],
    ),
    (
        ("prompt160 session160 library160 service160 gateway160 storage160", 28),
        ["prompt160 session160", "library160 service160", "gateway160 storage160"],
    ),
    (
        ("session160 library160 service160 gateway160 storage160 network160", 6),
        ["session160", "library160", "service160", "gateway160", "storage160", "network160"],
    ),
    (
        ("session160 library160 service160 gateway160 storage160 network160", 10),
        ["session160", "library160", "service160", "gateway160", "storage160", "network160"],
    ),
    (
        ("session160 library160 service160 gateway160 storage160 network160", 18),
        ["session160", "library160", "service160", "gateway160", "storage160", "network160"],
    ),
    (
        ("session160 library160 service160 gateway160 storage160 network160", 28),
        ["session160 library160", "service160 gateway160", "storage160 network160"],
    ),
    (
        ("library160 service160 gateway160 storage160 network160 latency160", 6),
        ["library160", "service160", "gateway160", "storage160", "network160", "latency160"],
    ),
    (
        ("library160 service160 gateway160 storage160 network160 latency160", 10),
        ["library160", "service160", "gateway160", "storage160", "network160", "latency160"],
    ),
    (
        ("library160 service160 gateway160 storage160 network160 latency160", 18),
        ["library160", "service160", "gateway160", "storage160", "network160", "latency160"],
    ),
    (
        ("library160 service160 gateway160 storage160 network160 latency160", 28),
        ["library160 service160", "gateway160 storage160", "network160 latency160"],
    ),
    (
        ("service160 gateway160 storage160 network160 latency160 buffer160", 6),
        ["service160", "gateway160", "storage160", "network160", "latency160", "buffer160"],
    ),
    (
        ("service160 gateway160 storage160 network160 latency160 buffer160", 10),
        ["service160", "gateway160", "storage160", "network160", "latency160", "buffer160"],
    ),
    (
        ("service160 gateway160 storage160 network160 latency160 buffer160", 18),
        ["service160", "gateway160", "storage160", "network160", "latency160", "buffer160"],
    ),
    (
        ("service160 gateway160 storage160 network160 latency160 buffer160", 28),
        ["service160 gateway160", "storage160 network160", "latency160 buffer160"],
    ),
    (
        ("gateway160 storage160 network160 latency160 buffer160 queue160", 6),
        ["gateway160", "storage160", "network160", "latency160", "buffer160", "queue160"],
    ),
    (
        ("gateway160 storage160 network160 latency160 buffer160 queue160", 10),
        ["gateway160", "storage160", "network160", "latency160", "buffer160", "queue160"],
    ),
    (
        ("gateway160 storage160 network160 latency160 buffer160 queue160", 18),
        ["gateway160", "storage160", "network160", "latency160", "buffer160 queue160"],
    ),
    (
        ("gateway160 storage160 network160 latency160 buffer160 queue160", 28),
        ["gateway160 storage160", "network160 latency160", "buffer160 queue160"],
    ),
    (
        ("storage160 network160 latency160 buffer160 queue160 worker160", 6),
        ["storage160", "network160", "latency160", "buffer160", "queue160", "worker160"],
    ),
    (
        ("storage160 network160 latency160 buffer160 queue160 worker160", 10),
        ["storage160", "network160", "latency160", "buffer160", "queue160", "worker160"],
    ),
    (
        ("storage160 network160 latency160 buffer160 queue160 worker160", 18),
        ["storage160", "network160", "latency160", "buffer160 queue160", "worker160"],
    ),
    (
        ("storage160 network160 latency160 buffer160 queue160 worker160", 28),
        ["storage160 network160", "latency160 buffer160", "queue160 worker160"],
    ),
    (
        ("network160 latency160 buffer160 queue160 worker160 kernel160", 6),
        ["network160", "latency160", "buffer160", "queue160", "worker160", "kernel160"],
    ),
    (
        ("network160 latency160 buffer160 queue160 worker160 kernel160", 10),
        ["network160", "latency160", "buffer160", "queue160", "worker160", "kernel160"],
    ),
    (
        ("network160 latency160 buffer160 queue160 worker160 kernel160", 18),
        ["network160", "latency160", "buffer160 queue160", "worker160", "kernel160"],
    ),
    (
        ("network160 latency160 buffer160 queue160 worker160 kernel160", 28),
        ["network160 latency160", "buffer160 queue160 worker160", "kernel160"],
    ),
    (
        ("latency160 buffer160 queue160 worker160 kernel160 signal160", 6),
        ["latency160", "buffer160", "queue160", "worker160", "kernel160", "signal160"],
    ),
    (
        ("latency160 buffer160 queue160 worker160 kernel160 signal160", 10),
        ["latency160", "buffer160", "queue160", "worker160", "kernel160", "signal160"],
    ),
    (
        ("latency160 buffer160 queue160 worker160 kernel160 signal160", 18),
        ["latency160", "buffer160 queue160", "worker160", "kernel160", "signal160"],
    ),
    (
        ("latency160 buffer160 queue160 worker160 kernel160 signal160", 28),
        ["latency160 buffer160", "queue160 worker160 kernel160", "signal160"],
    ),
    (
        ("buffer160 queue160 worker160 kernel160 signal160 packet160", 6),
        ["buffer160", "queue160", "worker160", "kernel160", "signal160", "packet160"],
    ),
    (
        ("buffer160 queue160 worker160 kernel160 signal160 packet160", 10),
        ["buffer160", "queue160", "worker160", "kernel160", "signal160", "packet160"],
    ),
    (
        ("buffer160 queue160 worker160 kernel160 signal160 packet160", 18),
        ["buffer160 queue160", "worker160", "kernel160", "signal160", "packet160"],
    ),
    (
        ("buffer160 queue160 worker160 kernel160 signal160 packet160", 28),
        ["buffer160 queue160 worker160", "kernel160 signal160", "packet160"],
    ),
    (
        ("queue160 worker160 kernel160 signal160 packet160 router160", 6),
        ["queue160", "worker160", "kernel160", "signal160", "packet160", "router160"],
    ),
    (
        ("queue160 worker160 kernel160 signal160 packet160 router160", 10),
        ["queue160", "worker160", "kernel160", "signal160", "packet160", "router160"],
    ),
    (
        ("queue160 worker160 kernel160 signal160 packet160 router160", 18),
        ["queue160 worker160", "kernel160", "signal160", "packet160", "router160"],
    ),
    (
        ("queue160 worker160 kernel160 signal160 packet160 router160", 28),
        ["queue160 worker160 kernel160", "signal160 packet160", "router160"],
    ),
    (
        ("worker160 kernel160 signal160 packet160 router160 cluster160", 6),
        ["worker160", "kernel160", "signal160", "packet160", "router160", "cluster160"],
    ),
    (
        ("worker160 kernel160 signal160 packet160 router160 cluster160", 10),
        ["worker160", "kernel160", "signal160", "packet160", "router160", "cluster160"],
    ),
    (
        ("worker160 kernel160 signal160 packet160 router160 cluster160", 18),
        ["worker160", "kernel160", "signal160", "packet160", "router160", "cluster160"],
    ),
    (
        ("worker160 kernel160 signal160 packet160 router160 cluster160", 28),
        ["worker160 kernel160", "signal160 packet160", "router160 cluster160"],
    ),
    (
        ("kernel160 signal160 packet160 router160 cluster160 mirror160", 6),
        ["kernel160", "signal160", "packet160", "router160", "cluster160", "mirror160"],
    ),
    (
        ("kernel160 signal160 packet160 router160 cluster160 mirror160", 10),
        ["kernel160", "signal160", "packet160", "router160", "cluster160", "mirror160"],
    ),
    (
        ("kernel160 signal160 packet160 router160 cluster160 mirror160", 18),
        ["kernel160", "signal160", "packet160", "router160", "cluster160", "mirror160"],
    ),
    (
        ("kernel160 signal160 packet160 router160 cluster160 mirror160", 28),
        ["kernel160 signal160", "packet160 router160", "cluster160 mirror160"],
    ),
    (
        ("signal160 packet160 router160 cluster160 mirror160 filter160", 6),
        ["signal160", "packet160", "router160", "cluster160", "mirror160", "filter160"],
    ),
    (
        ("signal160 packet160 router160 cluster160 mirror160 filter160", 10),
        ["signal160", "packet160", "router160", "cluster160", "mirror160", "filter160"],
    ),
    (
        ("signal160 packet160 router160 cluster160 mirror160 filter160", 18),
        ["signal160", "packet160", "router160", "cluster160", "mirror160", "filter160"],
    ),
    (
        ("signal160 packet160 router160 cluster160 mirror160 filter160", 28),
        ["signal160 packet160", "router160 cluster160", "mirror160 filter160"],
    ),
    (
        ("packet160 router160 cluster160 mirror160 filter160 ranking160", 6),
        ["packet160", "router160", "cluster160", "mirror160", "filter160", "ranking160"],
    ),
    (
        ("packet160 router160 cluster160 mirror160 filter160 ranking160", 10),
        ["packet160", "router160", "cluster160", "mirror160", "filter160", "ranking160"],
    ),
    (
        ("packet160 router160 cluster160 mirror160 filter160 ranking160", 18),
        ["packet160", "router160", "cluster160", "mirror160", "filter160", "ranking160"],
    ),
    (
        ("packet160 router160 cluster160 mirror160 filter160 ranking160", 28),
        ["packet160 router160", "cluster160 mirror160", "filter160 ranking160"],
    ),
    (
        ("router160 cluster160 mirror160 filter160 ranking160 encoding160", 6),
        ["router160", "cluster160", "mirror160", "filter160", "ranking160", "encoding160"],
    ),
    (
        ("router160 cluster160 mirror160 filter160 ranking160 encoding160", 10),
        ["router160", "cluster160", "mirror160", "filter160", "ranking160", "encoding160"],
    ),
    (
        ("router160 cluster160 mirror160 filter160 ranking160 encoding160", 18),
        ["router160", "cluster160", "mirror160", "filter160", "ranking160", "encoding160"],
    ),
    (
        ("router160 cluster160 mirror160 filter160 ranking160 encoding160", 28),
        ["router160 cluster160", "mirror160 filter160", "ranking160 encoding160"],
    ),
    (
        ("cluster160 mirror160 filter160 ranking160 encoding160 mapping160", 6),
        ["cluster160", "mirror160", "filter160", "ranking160", "encoding160", "mapping160"],
    ),
    (
        ("cluster160 mirror160 filter160 ranking160 encoding160 mapping160", 10),
        ["cluster160", "mirror160", "filter160", "ranking160", "encoding160", "mapping160"],
    ),
    (
        ("cluster160 mirror160 filter160 ranking160 encoding160 mapping160", 18),
        ["cluster160", "mirror160", "filter160", "ranking160", "encoding160", "mapping160"],
    ),
    (
        ("cluster160 mirror160 filter160 ranking160 encoding160 mapping160", 28),
        ["cluster160 mirror160", "filter160 ranking160", "encoding160 mapping160"],
    ),
    (
        ("mirror160 filter160 ranking160 encoding160 mapping160 record160", 6),
        ["mirror160", "filter160", "ranking160", "encoding160", "mapping160", "record160"],
    ),
    (
        ("mirror160 filter160 ranking160 encoding160 mapping160 record160", 10),
        ["mirror160", "filter160", "ranking160", "encoding160", "mapping160", "record160"],
    ),
    (
        ("mirror160 filter160 ranking160 encoding160 mapping160 record160", 18),
        ["mirror160", "filter160", "ranking160", "encoding160", "mapping160", "record160"],
    ),
    (
        ("mirror160 filter160 ranking160 encoding160 mapping160 record160", 28),
        ["mirror160 filter160", "ranking160 encoding160", "mapping160 record160"],
    ),
    (
        ("filter160 ranking160 encoding160 mapping160 record160 candle160", 6),
        ["filter160", "ranking160", "encoding160", "mapping160", "record160", "candle160"],
    ),
    (
        ("filter160 ranking160 encoding160 mapping160 record160 candle160", 10),
        ["filter160", "ranking160", "encoding160", "mapping160", "record160", "candle160"],
    ),
    (
        ("filter160 ranking160 encoding160 mapping160 record160 candle160", 18),
        ["filter160", "ranking160", "encoding160", "mapping160", "record160", "candle160"],
    ),
    (
        ("filter160 ranking160 encoding160 mapping160 record160 candle160", 28),
        ["filter160 ranking160", "encoding160 mapping160", "record160 candle160"],
    ),
    (
        ("ranking160 encoding160 mapping160 record160 candle160 thread160", 6),
        ["ranking160", "encoding160", "mapping160", "record160", "candle160", "thread160"],
    ),
    (
        ("ranking160 encoding160 mapping160 record160 candle160 thread160", 10),
        ["ranking160", "encoding160", "mapping160", "record160", "candle160", "thread160"],
    ),
    (
        ("ranking160 encoding160 mapping160 record160 candle160 thread160", 18),
        ["ranking160", "encoding160", "mapping160", "record160", "candle160", "thread160"],
    ),
    (
        ("ranking160 encoding160 mapping160 record160 candle160 thread160", 28),
        ["ranking160 encoding160", "mapping160 record160", "candle160 thread160"],
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
