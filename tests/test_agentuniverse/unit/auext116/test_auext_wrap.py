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
        ("round 116: the quick brown fox jumps over the lazy dog", 4),
        ["round", "116:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", 8),
        ["round", "116: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", 12),
        ["round 116:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", 16),
        ["round 116: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", 24),
        ["round 116: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 116: the quick brown fox jumps over the lazy dog", 32),
        ["round 116: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", 4),
        ["round", "116:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", 8),
        ["round", "116:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", 12),
        ["round 116:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", 16),
        ["round 116:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", 24),
        ["round 116: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 116: agentuniverse is a framework for multi agents", 32),
        ["round 116: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", 4),
        ["round", "116:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", 8),
        ["round", "116:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", 12),
        ["round 116:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", 16),
        ["round 116:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", 24),
        ["round 116: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 116: knowledge stored as vectors enables retrieval", 32),
        ["round 116: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 116: the processor reads the record then stops", 4),
        ["round", "116:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 116: the processor reads the record then stops", 8),
        ["round", "116: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 116: the processor reads the record then stops", 12),
        ["round 116:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 116: the processor reads the record then stops", 16),
        ["round 116: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 116: the processor reads the record then stops", 24),
        ["round 116: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 116: the processor reads the record then stops", 32),
        ["round 116: the processor reads", "the record then stops"],
    ),
    (
        ("round 116: a worker pulls the next task from the queue", 4),
        ["round", "116:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 116: a worker pulls the next task from the queue", 8),
        ["round", "116: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 116: a worker pulls the next task from the queue", 12),
        ["round 116: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 116: a worker pulls the next task from the queue", 16),
        ["round 116: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 116: a worker pulls the next task from the queue", 24),
        ["round 116: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 116: a worker pulls the next task from the queue", 32),
        ["round 116: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 116: signals travel through the network layer", 4),
        ["round", "116:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 116: signals travel through the network layer", 8),
        ["round", "116:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 116: signals travel through the network layer", 12),
        ["round 116:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 116: signals travel through the network layer", 16),
        ["round 116:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 116: signals travel through the network layer", 24),
        ["round 116: signals", "travel through the", "network layer"],
    ),
    (
        ("round 116: signals travel through the network layer", 32),
        ["round 116: signals travel", "through the network layer"],
    ),
    (
        ("round 116: the gateway routes each request by policy", 4),
        ["round", "116:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 116: the gateway routes each request by policy", 8),
        ["round", "116: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 116: the gateway routes each request by policy", 12),
        ["round 116:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 116: the gateway routes each request by policy", 16),
        ["round 116: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 116: the gateway routes each request by policy", 24),
        ["round 116: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 116: the gateway routes each request by policy", 32),
        ["round 116: the gateway routes", "each request by policy"],
    ),
    (
        ("round 116: memory grows until the buffer is full", 4),
        ["round", "116:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 116: memory grows until the buffer is full", 8),
        ["round", "116:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 116: memory grows until the buffer is full", 12),
        ["round 116:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 116: memory grows until the buffer is full", 16),
        ["round 116:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 116: memory grows until the buffer is full", 24), ["round 116: memory grows", "until the buffer is full"]),
    (("round 116: memory grows until the buffer is full", 32), ["round 116: memory grows until", "the buffer is full"]),
    (
        ("round 116: the cluster mirrors every packet twice", 4),
        ["round", "116:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 116: the cluster mirrors every packet twice", 8),
        ["round", "116: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 116: the cluster mirrors every packet twice", 12),
        ["round 116:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 116: the cluster mirrors every packet twice", 16),
        ["round 116: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 116: the cluster mirrors every packet twice", 24),
        ["round 116: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 116: the cluster mirrors every packet twice", 32),
        ["round 116: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", 4),
        ["round", "116:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", 8),
        ["round", "116:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", 12),
        ["round 116:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", 16),
        ["round 116:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", 24),
        ["round 116: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 116: ranking uses tokens learned from the corpus", 32),
        ["round 116: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 116: a long session ends when the candle dies", 4),
        ["round", "116:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 116: a long session ends when the candle dies", 8),
        ["round", "116: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 116: a long session ends when the candle dies", 12),
        ["round 116: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 116: a long session ends when the candle dies", 16),
        ["round 116: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 116: a long session ends when the candle dies", 24),
        ["round 116: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 116: a long session ends when the candle dies", 32),
        ["round 116: a long session ends", "when the candle dies"],
    ),
    (
        ("round 116: encode the prompt then map the result", 4),
        ["round", "116:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 116: encode the prompt then map the result", 8),
        ["round", "116:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 116: encode the prompt then map the result", 12),
        ["round 116:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 116: encode the prompt then map the result", 16),
        ["round 116:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 116: encode the prompt then map the result", 24),
        ["round 116: encode the", "prompt then map the", "result"],
    ),
    (("round 116: encode the prompt then map the result", 32), ["round 116: encode the prompt", "then map the result"]),
    (
        ("round 116: the kernel wakes the worker at dawn", 4),
        ["round", "116:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 116: the kernel wakes the worker at dawn", 8),
        ["round", "116: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 116: the kernel wakes the worker at dawn", 12),
        ["round 116:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 116: the kernel wakes the worker at dawn", 16), ["round 116: the", "kernel wakes the", "worker at dawn"]),
    (("round 116: the kernel wakes the worker at dawn", 24), ["round 116: the kernel", "wakes the worker at dawn"]),
    (("round 116: the kernel wakes the worker at dawn", 32), ["round 116: the kernel wakes the", "worker at dawn"]),
    (
        ("round 116: service latency drops after the patch", 4),
        ["round", "116:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 116: service latency drops after the patch", 8),
        ["round", "116:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 116: service latency drops after the patch", 12),
        ["round 116:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 116: service latency drops after the patch", 16),
        ["round 116:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 116: service latency drops after the patch", 24),
        ["round 116: service", "latency drops after the", "patch"],
    ),
    (("round 116: service latency drops after the patch", 32), ["round 116: service latency drops", "after the patch"]),
    (
        ("round 116: the library caches every vector it sees", 4),
        ["round", "116:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 116: the library caches every vector it sees", 8),
        ["round", "116: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 116: the library caches every vector it sees", 12),
        ["round 116:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 116: the library caches every vector it sees", 16),
        ["round 116: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 116: the library caches every vector it sees", 24),
        ["round 116: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 116: the library caches every vector it sees", 32),
        ["round 116: the library caches", "every vector it sees"],
    ),
    (
        ("round 116: agents argue then the debate resolves", 4),
        ["round", "116:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 116: agents argue then the debate resolves", 8),
        ["round", "116:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 116: agents argue then the debate resolves", 12),
        ["round 116:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 116: agents argue then the debate resolves", 16),
        ["round 116:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 116: agents argue then the debate resolves", 24), ["round 116: agents argue", "then the debate resolves"]),
    (("round 116: agents argue then the debate resolves", 32), ["round 116: agents argue then the", "debate resolves"]),
    (
        ("round 116: the filter keeps only strong matches", 4),
        ["round", "116:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 116: the filter keeps only strong matches", 8),
        ["round", "116: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 116: the filter keeps only strong matches", 12),
        ["round 116:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 116: the filter keeps only strong matches", 16),
        ["round 116: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 116: the filter keeps only strong matches", 24),
        ["round 116: the filter", "keeps only strong", "matches"],
    ),
    (("round 116: the filter keeps only strong matches", 32), ["round 116: the filter keeps only", "strong matches"]),
    (
        ("round 116: the model answers with a short reply", 4),
        ["round", "116:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 116: the model answers with a short reply", 8),
        ["round", "116: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 116: the model answers with a short reply", 12),
        ["round 116:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 116: the model answers with a short reply", 16),
        ["round 116: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 116: the model answers with a short reply", 24),
        ["round 116: the model", "answers with a short", "reply"],
    ),
    (("round 116: the model answers with a short reply", 32), ["round 116: the model answers", "with a short reply"]),
    (
        ("round 116: the recorder stores the reasoning trace", 4),
        ["round", "116:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 116: the recorder stores the reasoning trace", 8),
        ["round", "116: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 116: the recorder stores the reasoning trace", 12),
        ["round 116:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 116: the recorder stores the reasoning trace", 16),
        ["round 116: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 116: the recorder stores the reasoning trace", 24),
        ["round 116: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 116: the recorder stores the reasoning trace", 32),
        ["round 116: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 116: the angel watches the processor run", 4),
        ["round", "116:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 116: the angel watches the processor run", 8),
        ["round", "116: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 116: the angel watches the processor run", 12),
        ["round 116:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 116: the angel watches the processor run", 16),
        ["round 116: the", "angel watches", "the processor", "run"],
    ),
    (("round 116: the angel watches the processor run", 24), ["round 116: the angel", "watches the processor", "run"]),
    (("round 116: the angel watches the processor run", 32), ["round 116: the angel watches the", "processor run"]),
    (
        ("round 116: angle of the vector decides the match", 4),
        ["round", "116:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 116: angle of the vector decides the match", 8),
        ["round", "116:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 116: angle of the vector decides the match", 12),
        ["round 116:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 116: angle of the vector decides the match", 16),
        ["round 116: angle", "of the vector", "decides the", "match"],
    ),
    (("round 116: angle of the vector decides the match", 24), ["round 116: angle of the", "vector decides the match"]),
    (("round 116: angle of the vector decides the match", 32), ["round 116: angle of the vector", "decides the match"]),
    (
        ("round 116: the candle burns twice as long at night", 4),
        ["round", "116:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 116: the candle burns twice as long at night", 8),
        ["round", "116: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 116: the candle burns twice as long at night", 12),
        ["round 116:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 116: the candle burns twice as long at night", 16),
        ["round 116: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 116: the candle burns twice as long at night", 24),
        ["round 116: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 116: the candle burns twice as long at night", 32),
        ["round 116: the candle burns", "twice as long at night"],
    ),
    (
        ("round 116: a mirror of the universe in one line", 4),
        ["round", "116:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 116: a mirror of the universe in one line", 8),
        ["round", "116: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 116: a mirror of the universe in one line", 12),
        ["round 116: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 116: a mirror of the universe in one line", 16),
        ["round 116: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 116: a mirror of the universe in one line", 24), ["round 116: a mirror of", "the universe in one line"]),
    (("round 116: a mirror of the universe in one line", 32), ["round 116: a mirror of the", "universe in one line"]),
    (
        ("round 116: the queue drains before the storm", 4),
        ["round", "116:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 116: the queue drains before the storm", 8),
        ["round", "116: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 116: the queue drains before the storm", 12),
        ["round 116:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 116: the queue drains before the storm", 16), ["round 116: the", "queue drains", "before the storm"]),
    (("round 116: the queue drains before the storm", 24), ["round 116: the queue", "drains before the storm"]),
    (("round 116: the queue drains before the storm", 32), ["round 116: the queue drains", "before the storm"]),
    (
        ("kitten116 sitting116 agent116 angle116 universe116 memory116", 6),
        ["kitten116", "sitting116", "agent116", "angle116", "universe116", "memory116"],
    ),
    (
        ("kitten116 sitting116 agent116 angle116 universe116 memory116", 10),
        ["kitten116", "sitting116", "agent116", "angle116", "universe116", "memory116"],
    ),
    (
        ("kitten116 sitting116 agent116 angle116 universe116 memory116", 18),
        ["kitten116", "sitting116", "agent116 angle116", "universe116", "memory116"],
    ),
    (
        ("kitten116 sitting116 agent116 angle116 universe116 memory116", 28),
        ["kitten116 sitting116", "agent116 angle116", "universe116 memory116"],
    ),
    (
        ("sitting116 agent116 angle116 universe116 memory116 stream116", 6),
        ["sitting116", "agent116", "angle116", "universe116", "memory116", "stream116"],
    ),
    (
        ("sitting116 agent116 angle116 universe116 memory116 stream116", 10),
        ["sitting116", "agent116", "angle116", "universe116", "memory116", "stream116"],
    ),
    (
        ("sitting116 agent116 angle116 universe116 memory116 stream116", 18),
        ["sitting116", "agent116 angle116", "universe116", "memory116", "stream116"],
    ),
    (
        ("sitting116 agent116 angle116 universe116 memory116 stream116", 28),
        ["sitting116 agent116 angle116", "universe116 memory116", "stream116"],
    ),
    (
        ("agent116 angle116 universe116 memory116 stream116 context116", 6),
        ["agent116", "angle116", "universe116", "memory116", "stream116", "context116"],
    ),
    (
        ("agent116 angle116 universe116 memory116 stream116 context116", 10),
        ["agent116", "angle116", "universe116", "memory116", "stream116", "context116"],
    ),
    (
        ("agent116 angle116 universe116 memory116 stream116 context116", 18),
        ["agent116 angle116", "universe116", "memory116", "stream116", "context116"],
    ),
    (
        ("agent116 angle116 universe116 memory116 stream116 context116", 28),
        ["agent116 angle116", "universe116 memory116", "stream116 context116"],
    ),
    (
        ("angle116 universe116 memory116 stream116 context116 knowledge116", 6),
        ["angle116", "universe116", "memory116", "stream116", "context116", "knowledge116"],
    ),
    (
        ("angle116 universe116 memory116 stream116 context116 knowledge116", 10),
        ["angle116", "universe116", "memory116", "stream116", "context116", "knowledge116"],
    ),
    (
        ("angle116 universe116 memory116 stream116 context116 knowledge116", 18),
        ["angle116", "universe116", "memory116", "stream116", "context116", "knowledge116"],
    ),
    (
        ("angle116 universe116 memory116 stream116 context116 knowledge116", 28),
        ["angle116 universe116", "memory116 stream116", "context116 knowledge116"],
    ),
    (
        ("universe116 memory116 stream116 context116 knowledge116 vector116", 6),
        ["universe116", "memory116", "stream116", "context116", "knowledge116", "vector116"],
    ),
    (
        ("universe116 memory116 stream116 context116 knowledge116 vector116", 10),
        ["universe116", "memory116", "stream116", "context116", "knowledge116", "vector116"],
    ),
    (
        ("universe116 memory116 stream116 context116 knowledge116 vector116", 18),
        ["universe116", "memory116", "stream116", "context116", "knowledge116", "vector116"],
    ),
    (
        ("universe116 memory116 stream116 context116 knowledge116 vector116", 28),
        ["universe116 memory116", "stream116 context116", "knowledge116 vector116"],
    ),
    (
        ("memory116 stream116 context116 knowledge116 vector116 processor116", 6),
        ["memory116", "stream116", "context116", "knowledge116", "vector116", "processor116"],
    ),
    (
        ("memory116 stream116 context116 knowledge116 vector116 processor116", 10),
        ["memory116", "stream116", "context116", "knowledge116", "vector116", "processor116"],
    ),
    (
        ("memory116 stream116 context116 knowledge116 vector116 processor116", 18),
        ["memory116", "stream116", "context116", "knowledge116", "vector116", "processor116"],
    ),
    (
        ("memory116 stream116 context116 knowledge116 vector116 processor116", 28),
        ["memory116 stream116", "context116 knowledge116", "vector116 processor116"],
    ),
    (
        ("stream116 context116 knowledge116 vector116 processor116 reasoning116", 6),
        ["stream116", "context116", "knowledge116", "vector116", "processor116", "reasoning116"],
    ),
    (
        ("stream116 context116 knowledge116 vector116 processor116 reasoning116", 10),
        ["stream116", "context116", "knowledge116", "vector116", "processor116", "reasoning116"],
    ),
    (
        ("stream116 context116 knowledge116 vector116 processor116 reasoning116", 18),
        ["stream116", "context116", "knowledge116", "vector116", "processor116", "reasoning116"],
    ),
    (
        ("stream116 context116 knowledge116 vector116 processor116 reasoning116", 28),
        ["stream116 context116", "knowledge116 vector116", "processor116 reasoning116"],
    ),
    (
        ("context116 knowledge116 vector116 processor116 reasoning116 machine116", 6),
        ["context116", "knowledge116", "vector116", "processor116", "reasoning116", "machine116"],
    ),
    (
        ("context116 knowledge116 vector116 processor116 reasoning116 machine116", 10),
        ["context116", "knowledge116", "vector116", "processor116", "reasoning116", "machine116"],
    ),
    (
        ("context116 knowledge116 vector116 processor116 reasoning116 machine116", 18),
        ["context116", "knowledge116", "vector116", "processor116", "reasoning116", "machine116"],
    ),
    (
        ("context116 knowledge116 vector116 processor116 reasoning116 machine116", 28),
        ["context116 knowledge116", "vector116 processor116", "reasoning116 machine116"],
    ),
    (
        ("knowledge116 vector116 processor116 reasoning116 machine116 learning116", 6),
        ["knowledge116", "vector116", "processor116", "reasoning116", "machine116", "learning116"],
    ),
    (
        ("knowledge116 vector116 processor116 reasoning116 machine116 learning116", 10),
        ["knowledge116", "vector116", "processor116", "reasoning116", "machine116", "learning116"],
    ),
    (
        ("knowledge116 vector116 processor116 reasoning116 machine116 learning116", 18),
        ["knowledge116", "vector116", "processor116", "reasoning116", "machine116", "learning116"],
    ),
    (
        ("knowledge116 vector116 processor116 reasoning116 machine116 learning116", 28),
        ["knowledge116 vector116", "processor116 reasoning116", "machine116 learning116"],
    ),
    (
        ("vector116 processor116 reasoning116 machine116 learning116 model116", 6),
        ["vector116", "processor116", "reasoning116", "machine116", "learning116", "model116"],
    ),
    (
        ("vector116 processor116 reasoning116 machine116 learning116 model116", 10),
        ["vector116", "processor116", "reasoning116", "machine116", "learning116", "model116"],
    ),
    (
        ("vector116 processor116 reasoning116 machine116 learning116 model116", 18),
        ["vector116", "processor116", "reasoning116", "machine116", "learning116", "model116"],
    ),
    (
        ("vector116 processor116 reasoning116 machine116 learning116 model116", 28),
        ["vector116 processor116", "reasoning116 machine116", "learning116 model116"],
    ),
    (
        ("processor116 reasoning116 machine116 learning116 model116 token116", 6),
        ["processor116", "reasoning116", "machine116", "learning116", "model116", "token116"],
    ),
    (
        ("processor116 reasoning116 machine116 learning116 model116 token116", 10),
        ["processor116", "reasoning116", "machine116", "learning116", "model116", "token116"],
    ),
    (
        ("processor116 reasoning116 machine116 learning116 model116 token116", 18),
        ["processor116", "reasoning116", "machine116", "learning116", "model116 token116"],
    ),
    (
        ("processor116 reasoning116 machine116 learning116 model116 token116", 28),
        ["processor116 reasoning116", "machine116 learning116", "model116 token116"],
    ),
    (
        ("reasoning116 machine116 learning116 model116 token116 prompt116", 6),
        ["reasoning116", "machine116", "learning116", "model116", "token116", "prompt116"],
    ),
    (
        ("reasoning116 machine116 learning116 model116 token116 prompt116", 10),
        ["reasoning116", "machine116", "learning116", "model116", "token116", "prompt116"],
    ),
    (
        ("reasoning116 machine116 learning116 model116 token116 prompt116", 18),
        ["reasoning116", "machine116", "learning116", "model116 token116", "prompt116"],
    ),
    (
        ("reasoning116 machine116 learning116 model116 token116 prompt116", 28),
        ["reasoning116 machine116", "learning116 model116", "token116 prompt116"],
    ),
    (
        ("machine116 learning116 model116 token116 prompt116 session116", 6),
        ["machine116", "learning116", "model116", "token116", "prompt116", "session116"],
    ),
    (
        ("machine116 learning116 model116 token116 prompt116 session116", 10),
        ["machine116", "learning116", "model116", "token116", "prompt116", "session116"],
    ),
    (
        ("machine116 learning116 model116 token116 prompt116 session116", 18),
        ["machine116", "learning116", "model116 token116", "prompt116", "session116"],
    ),
    (
        ("machine116 learning116 model116 token116 prompt116 session116", 28),
        ["machine116 learning116", "model116 token116 prompt116", "session116"],
    ),
    (
        ("learning116 model116 token116 prompt116 session116 library116", 6),
        ["learning116", "model116", "token116", "prompt116", "session116", "library116"],
    ),
    (
        ("learning116 model116 token116 prompt116 session116 library116", 10),
        ["learning116", "model116", "token116", "prompt116", "session116", "library116"],
    ),
    (
        ("learning116 model116 token116 prompt116 session116 library116", 18),
        ["learning116", "model116 token116", "prompt116", "session116", "library116"],
    ),
    (
        ("learning116 model116 token116 prompt116 session116 library116", 28),
        ["learning116 model116", "token116 prompt116", "session116 library116"],
    ),
    (
        ("model116 token116 prompt116 session116 library116 service116", 6),
        ["model116", "token116", "prompt116", "session116", "library116", "service116"],
    ),
    (
        ("model116 token116 prompt116 session116 library116 service116", 10),
        ["model116", "token116", "prompt116", "session116", "library116", "service116"],
    ),
    (
        ("model116 token116 prompt116 session116 library116 service116", 18),
        ["model116 token116", "prompt116", "session116", "library116", "service116"],
    ),
    (
        ("model116 token116 prompt116 session116 library116 service116", 28),
        ["model116 token116 prompt116", "session116 library116", "service116"],
    ),
    (
        ("token116 prompt116 session116 library116 service116 gateway116", 6),
        ["token116", "prompt116", "session116", "library116", "service116", "gateway116"],
    ),
    (
        ("token116 prompt116 session116 library116 service116 gateway116", 10),
        ["token116", "prompt116", "session116", "library116", "service116", "gateway116"],
    ),
    (
        ("token116 prompt116 session116 library116 service116 gateway116", 18),
        ["token116 prompt116", "session116", "library116", "service116", "gateway116"],
    ),
    (
        ("token116 prompt116 session116 library116 service116 gateway116", 28),
        ["token116 prompt116", "session116 library116", "service116 gateway116"],
    ),
    (
        ("prompt116 session116 library116 service116 gateway116 storage116", 6),
        ["prompt116", "session116", "library116", "service116", "gateway116", "storage116"],
    ),
    (
        ("prompt116 session116 library116 service116 gateway116 storage116", 10),
        ["prompt116", "session116", "library116", "service116", "gateway116", "storage116"],
    ),
    (
        ("prompt116 session116 library116 service116 gateway116 storage116", 18),
        ["prompt116", "session116", "library116", "service116", "gateway116", "storage116"],
    ),
    (
        ("prompt116 session116 library116 service116 gateway116 storage116", 28),
        ["prompt116 session116", "library116 service116", "gateway116 storage116"],
    ),
    (
        ("session116 library116 service116 gateway116 storage116 network116", 6),
        ["session116", "library116", "service116", "gateway116", "storage116", "network116"],
    ),
    (
        ("session116 library116 service116 gateway116 storage116 network116", 10),
        ["session116", "library116", "service116", "gateway116", "storage116", "network116"],
    ),
    (
        ("session116 library116 service116 gateway116 storage116 network116", 18),
        ["session116", "library116", "service116", "gateway116", "storage116", "network116"],
    ),
    (
        ("session116 library116 service116 gateway116 storage116 network116", 28),
        ["session116 library116", "service116 gateway116", "storage116 network116"],
    ),
    (
        ("library116 service116 gateway116 storage116 network116 latency116", 6),
        ["library116", "service116", "gateway116", "storage116", "network116", "latency116"],
    ),
    (
        ("library116 service116 gateway116 storage116 network116 latency116", 10),
        ["library116", "service116", "gateway116", "storage116", "network116", "latency116"],
    ),
    (
        ("library116 service116 gateway116 storage116 network116 latency116", 18),
        ["library116", "service116", "gateway116", "storage116", "network116", "latency116"],
    ),
    (
        ("library116 service116 gateway116 storage116 network116 latency116", 28),
        ["library116 service116", "gateway116 storage116", "network116 latency116"],
    ),
    (
        ("service116 gateway116 storage116 network116 latency116 buffer116", 6),
        ["service116", "gateway116", "storage116", "network116", "latency116", "buffer116"],
    ),
    (
        ("service116 gateway116 storage116 network116 latency116 buffer116", 10),
        ["service116", "gateway116", "storage116", "network116", "latency116", "buffer116"],
    ),
    (
        ("service116 gateway116 storage116 network116 latency116 buffer116", 18),
        ["service116", "gateway116", "storage116", "network116", "latency116", "buffer116"],
    ),
    (
        ("service116 gateway116 storage116 network116 latency116 buffer116", 28),
        ["service116 gateway116", "storage116 network116", "latency116 buffer116"],
    ),
    (
        ("gateway116 storage116 network116 latency116 buffer116 queue116", 6),
        ["gateway116", "storage116", "network116", "latency116", "buffer116", "queue116"],
    ),
    (
        ("gateway116 storage116 network116 latency116 buffer116 queue116", 10),
        ["gateway116", "storage116", "network116", "latency116", "buffer116", "queue116"],
    ),
    (
        ("gateway116 storage116 network116 latency116 buffer116 queue116", 18),
        ["gateway116", "storage116", "network116", "latency116", "buffer116 queue116"],
    ),
    (
        ("gateway116 storage116 network116 latency116 buffer116 queue116", 28),
        ["gateway116 storage116", "network116 latency116", "buffer116 queue116"],
    ),
    (
        ("storage116 network116 latency116 buffer116 queue116 worker116", 6),
        ["storage116", "network116", "latency116", "buffer116", "queue116", "worker116"],
    ),
    (
        ("storage116 network116 latency116 buffer116 queue116 worker116", 10),
        ["storage116", "network116", "latency116", "buffer116", "queue116", "worker116"],
    ),
    (
        ("storage116 network116 latency116 buffer116 queue116 worker116", 18),
        ["storage116", "network116", "latency116", "buffer116 queue116", "worker116"],
    ),
    (
        ("storage116 network116 latency116 buffer116 queue116 worker116", 28),
        ["storage116 network116", "latency116 buffer116", "queue116 worker116"],
    ),
    (
        ("network116 latency116 buffer116 queue116 worker116 kernel116", 6),
        ["network116", "latency116", "buffer116", "queue116", "worker116", "kernel116"],
    ),
    (
        ("network116 latency116 buffer116 queue116 worker116 kernel116", 10),
        ["network116", "latency116", "buffer116", "queue116", "worker116", "kernel116"],
    ),
    (
        ("network116 latency116 buffer116 queue116 worker116 kernel116", 18),
        ["network116", "latency116", "buffer116 queue116", "worker116", "kernel116"],
    ),
    (
        ("network116 latency116 buffer116 queue116 worker116 kernel116", 28),
        ["network116 latency116", "buffer116 queue116 worker116", "kernel116"],
    ),
    (
        ("latency116 buffer116 queue116 worker116 kernel116 signal116", 6),
        ["latency116", "buffer116", "queue116", "worker116", "kernel116", "signal116"],
    ),
    (
        ("latency116 buffer116 queue116 worker116 kernel116 signal116", 10),
        ["latency116", "buffer116", "queue116", "worker116", "kernel116", "signal116"],
    ),
    (
        ("latency116 buffer116 queue116 worker116 kernel116 signal116", 18),
        ["latency116", "buffer116 queue116", "worker116", "kernel116", "signal116"],
    ),
    (
        ("latency116 buffer116 queue116 worker116 kernel116 signal116", 28),
        ["latency116 buffer116", "queue116 worker116 kernel116", "signal116"],
    ),
    (
        ("buffer116 queue116 worker116 kernel116 signal116 packet116", 6),
        ["buffer116", "queue116", "worker116", "kernel116", "signal116", "packet116"],
    ),
    (
        ("buffer116 queue116 worker116 kernel116 signal116 packet116", 10),
        ["buffer116", "queue116", "worker116", "kernel116", "signal116", "packet116"],
    ),
    (
        ("buffer116 queue116 worker116 kernel116 signal116 packet116", 18),
        ["buffer116 queue116", "worker116", "kernel116", "signal116", "packet116"],
    ),
    (
        ("buffer116 queue116 worker116 kernel116 signal116 packet116", 28),
        ["buffer116 queue116 worker116", "kernel116 signal116", "packet116"],
    ),
    (
        ("queue116 worker116 kernel116 signal116 packet116 router116", 6),
        ["queue116", "worker116", "kernel116", "signal116", "packet116", "router116"],
    ),
    (
        ("queue116 worker116 kernel116 signal116 packet116 router116", 10),
        ["queue116", "worker116", "kernel116", "signal116", "packet116", "router116"],
    ),
    (
        ("queue116 worker116 kernel116 signal116 packet116 router116", 18),
        ["queue116 worker116", "kernel116", "signal116", "packet116", "router116"],
    ),
    (
        ("queue116 worker116 kernel116 signal116 packet116 router116", 28),
        ["queue116 worker116 kernel116", "signal116 packet116", "router116"],
    ),
    (
        ("worker116 kernel116 signal116 packet116 router116 cluster116", 6),
        ["worker116", "kernel116", "signal116", "packet116", "router116", "cluster116"],
    ),
    (
        ("worker116 kernel116 signal116 packet116 router116 cluster116", 10),
        ["worker116", "kernel116", "signal116", "packet116", "router116", "cluster116"],
    ),
    (
        ("worker116 kernel116 signal116 packet116 router116 cluster116", 18),
        ["worker116", "kernel116", "signal116", "packet116", "router116", "cluster116"],
    ),
    (
        ("worker116 kernel116 signal116 packet116 router116 cluster116", 28),
        ["worker116 kernel116", "signal116 packet116", "router116 cluster116"],
    ),
    (
        ("kernel116 signal116 packet116 router116 cluster116 mirror116", 6),
        ["kernel116", "signal116", "packet116", "router116", "cluster116", "mirror116"],
    ),
    (
        ("kernel116 signal116 packet116 router116 cluster116 mirror116", 10),
        ["kernel116", "signal116", "packet116", "router116", "cluster116", "mirror116"],
    ),
    (
        ("kernel116 signal116 packet116 router116 cluster116 mirror116", 18),
        ["kernel116", "signal116", "packet116", "router116", "cluster116", "mirror116"],
    ),
    (
        ("kernel116 signal116 packet116 router116 cluster116 mirror116", 28),
        ["kernel116 signal116", "packet116 router116", "cluster116 mirror116"],
    ),
    (
        ("signal116 packet116 router116 cluster116 mirror116 filter116", 6),
        ["signal116", "packet116", "router116", "cluster116", "mirror116", "filter116"],
    ),
    (
        ("signal116 packet116 router116 cluster116 mirror116 filter116", 10),
        ["signal116", "packet116", "router116", "cluster116", "mirror116", "filter116"],
    ),
    (
        ("signal116 packet116 router116 cluster116 mirror116 filter116", 18),
        ["signal116", "packet116", "router116", "cluster116", "mirror116", "filter116"],
    ),
    (
        ("signal116 packet116 router116 cluster116 mirror116 filter116", 28),
        ["signal116 packet116", "router116 cluster116", "mirror116 filter116"],
    ),
    (
        ("packet116 router116 cluster116 mirror116 filter116 ranking116", 6),
        ["packet116", "router116", "cluster116", "mirror116", "filter116", "ranking116"],
    ),
    (
        ("packet116 router116 cluster116 mirror116 filter116 ranking116", 10),
        ["packet116", "router116", "cluster116", "mirror116", "filter116", "ranking116"],
    ),
    (
        ("packet116 router116 cluster116 mirror116 filter116 ranking116", 18),
        ["packet116", "router116", "cluster116", "mirror116", "filter116", "ranking116"],
    ),
    (
        ("packet116 router116 cluster116 mirror116 filter116 ranking116", 28),
        ["packet116 router116", "cluster116 mirror116", "filter116 ranking116"],
    ),
    (
        ("router116 cluster116 mirror116 filter116 ranking116 encoding116", 6),
        ["router116", "cluster116", "mirror116", "filter116", "ranking116", "encoding116"],
    ),
    (
        ("router116 cluster116 mirror116 filter116 ranking116 encoding116", 10),
        ["router116", "cluster116", "mirror116", "filter116", "ranking116", "encoding116"],
    ),
    (
        ("router116 cluster116 mirror116 filter116 ranking116 encoding116", 18),
        ["router116", "cluster116", "mirror116", "filter116", "ranking116", "encoding116"],
    ),
    (
        ("router116 cluster116 mirror116 filter116 ranking116 encoding116", 28),
        ["router116 cluster116", "mirror116 filter116", "ranking116 encoding116"],
    ),
    (
        ("cluster116 mirror116 filter116 ranking116 encoding116 mapping116", 6),
        ["cluster116", "mirror116", "filter116", "ranking116", "encoding116", "mapping116"],
    ),
    (
        ("cluster116 mirror116 filter116 ranking116 encoding116 mapping116", 10),
        ["cluster116", "mirror116", "filter116", "ranking116", "encoding116", "mapping116"],
    ),
    (
        ("cluster116 mirror116 filter116 ranking116 encoding116 mapping116", 18),
        ["cluster116", "mirror116", "filter116", "ranking116", "encoding116", "mapping116"],
    ),
    (
        ("cluster116 mirror116 filter116 ranking116 encoding116 mapping116", 28),
        ["cluster116 mirror116", "filter116 ranking116", "encoding116 mapping116"],
    ),
    (
        ("mirror116 filter116 ranking116 encoding116 mapping116 record116", 6),
        ["mirror116", "filter116", "ranking116", "encoding116", "mapping116", "record116"],
    ),
    (
        ("mirror116 filter116 ranking116 encoding116 mapping116 record116", 10),
        ["mirror116", "filter116", "ranking116", "encoding116", "mapping116", "record116"],
    ),
    (
        ("mirror116 filter116 ranking116 encoding116 mapping116 record116", 18),
        ["mirror116", "filter116", "ranking116", "encoding116", "mapping116", "record116"],
    ),
    (
        ("mirror116 filter116 ranking116 encoding116 mapping116 record116", 28),
        ["mirror116 filter116", "ranking116 encoding116", "mapping116 record116"],
    ),
    (
        ("filter116 ranking116 encoding116 mapping116 record116 candle116", 6),
        ["filter116", "ranking116", "encoding116", "mapping116", "record116", "candle116"],
    ),
    (
        ("filter116 ranking116 encoding116 mapping116 record116 candle116", 10),
        ["filter116", "ranking116", "encoding116", "mapping116", "record116", "candle116"],
    ),
    (
        ("filter116 ranking116 encoding116 mapping116 record116 candle116", 18),
        ["filter116", "ranking116", "encoding116", "mapping116", "record116", "candle116"],
    ),
    (
        ("filter116 ranking116 encoding116 mapping116 record116 candle116", 28),
        ["filter116 ranking116", "encoding116 mapping116", "record116 candle116"],
    ),
    (
        ("ranking116 encoding116 mapping116 record116 candle116 thread116", 6),
        ["ranking116", "encoding116", "mapping116", "record116", "candle116", "thread116"],
    ),
    (
        ("ranking116 encoding116 mapping116 record116 candle116 thread116", 10),
        ["ranking116", "encoding116", "mapping116", "record116", "candle116", "thread116"],
    ),
    (
        ("ranking116 encoding116 mapping116 record116 candle116 thread116", 18),
        ["ranking116", "encoding116", "mapping116", "record116", "candle116", "thread116"],
    ),
    (
        ("ranking116 encoding116 mapping116 record116 candle116 thread116", 28),
        ["ranking116 encoding116", "mapping116 record116", "candle116 thread116"],
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
