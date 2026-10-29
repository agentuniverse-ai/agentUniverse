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
        ("round 104: the quick brown fox jumps over the lazy dog", 4),
        ["round", "104:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", 8),
        ["round", "104: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", 12),
        ["round 104:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", 16),
        ["round 104: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", 24),
        ["round 104: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 104: the quick brown fox jumps over the lazy dog", 32),
        ["round 104: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", 4),
        ["round", "104:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", 8),
        ["round", "104:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", 12),
        ["round 104:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", 16),
        ["round 104:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", 24),
        ["round 104: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 104: agentuniverse is a framework for multi agents", 32),
        ["round 104: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", 4),
        ["round", "104:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", 8),
        ["round", "104:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", 12),
        ["round 104:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", 16),
        ["round 104:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", 24),
        ["round 104: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 104: knowledge stored as vectors enables retrieval", 32),
        ["round 104: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 104: the processor reads the record then stops", 4),
        ["round", "104:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 104: the processor reads the record then stops", 8),
        ["round", "104: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 104: the processor reads the record then stops", 12),
        ["round 104:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 104: the processor reads the record then stops", 16),
        ["round 104: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 104: the processor reads the record then stops", 24),
        ["round 104: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 104: the processor reads the record then stops", 32),
        ["round 104: the processor reads", "the record then stops"],
    ),
    (
        ("round 104: a worker pulls the next task from the queue", 4),
        ["round", "104:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 104: a worker pulls the next task from the queue", 8),
        ["round", "104: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 104: a worker pulls the next task from the queue", 12),
        ["round 104: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 104: a worker pulls the next task from the queue", 16),
        ["round 104: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 104: a worker pulls the next task from the queue", 24),
        ["round 104: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 104: a worker pulls the next task from the queue", 32),
        ["round 104: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 104: signals travel through the network layer", 4),
        ["round", "104:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 104: signals travel through the network layer", 8),
        ["round", "104:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 104: signals travel through the network layer", 12),
        ["round 104:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 104: signals travel through the network layer", 16),
        ["round 104:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 104: signals travel through the network layer", 24),
        ["round 104: signals", "travel through the", "network layer"],
    ),
    (
        ("round 104: signals travel through the network layer", 32),
        ["round 104: signals travel", "through the network layer"],
    ),
    (
        ("round 104: the gateway routes each request by policy", 4),
        ["round", "104:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 104: the gateway routes each request by policy", 8),
        ["round", "104: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 104: the gateway routes each request by policy", 12),
        ["round 104:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 104: the gateway routes each request by policy", 16),
        ["round 104: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 104: the gateway routes each request by policy", 24),
        ["round 104: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 104: the gateway routes each request by policy", 32),
        ["round 104: the gateway routes", "each request by policy"],
    ),
    (
        ("round 104: memory grows until the buffer is full", 4),
        ["round", "104:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 104: memory grows until the buffer is full", 8),
        ["round", "104:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 104: memory grows until the buffer is full", 12),
        ["round 104:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 104: memory grows until the buffer is full", 16),
        ["round 104:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 104: memory grows until the buffer is full", 24), ["round 104: memory grows", "until the buffer is full"]),
    (("round 104: memory grows until the buffer is full", 32), ["round 104: memory grows until", "the buffer is full"]),
    (
        ("round 104: the cluster mirrors every packet twice", 4),
        ["round", "104:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 104: the cluster mirrors every packet twice", 8),
        ["round", "104: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 104: the cluster mirrors every packet twice", 12),
        ["round 104:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 104: the cluster mirrors every packet twice", 16),
        ["round 104: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 104: the cluster mirrors every packet twice", 24),
        ["round 104: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 104: the cluster mirrors every packet twice", 32),
        ["round 104: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", 4),
        ["round", "104:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", 8),
        ["round", "104:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", 12),
        ["round 104:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", 16),
        ["round 104:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", 24),
        ["round 104: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 104: ranking uses tokens learned from the corpus", 32),
        ["round 104: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 104: a long session ends when the candle dies", 4),
        ["round", "104:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 104: a long session ends when the candle dies", 8),
        ["round", "104: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 104: a long session ends when the candle dies", 12),
        ["round 104: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 104: a long session ends when the candle dies", 16),
        ["round 104: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 104: a long session ends when the candle dies", 24),
        ["round 104: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 104: a long session ends when the candle dies", 32),
        ["round 104: a long session ends", "when the candle dies"],
    ),
    (
        ("round 104: encode the prompt then map the result", 4),
        ["round", "104:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 104: encode the prompt then map the result", 8),
        ["round", "104:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 104: encode the prompt then map the result", 12),
        ["round 104:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 104: encode the prompt then map the result", 16),
        ["round 104:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 104: encode the prompt then map the result", 24),
        ["round 104: encode the", "prompt then map the", "result"],
    ),
    (("round 104: encode the prompt then map the result", 32), ["round 104: encode the prompt", "then map the result"]),
    (
        ("round 104: the kernel wakes the worker at dawn", 4),
        ["round", "104:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 104: the kernel wakes the worker at dawn", 8),
        ["round", "104: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 104: the kernel wakes the worker at dawn", 12),
        ["round 104:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 104: the kernel wakes the worker at dawn", 16), ["round 104: the", "kernel wakes the", "worker at dawn"]),
    (("round 104: the kernel wakes the worker at dawn", 24), ["round 104: the kernel", "wakes the worker at dawn"]),
    (("round 104: the kernel wakes the worker at dawn", 32), ["round 104: the kernel wakes the", "worker at dawn"]),
    (
        ("round 104: service latency drops after the patch", 4),
        ["round", "104:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 104: service latency drops after the patch", 8),
        ["round", "104:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 104: service latency drops after the patch", 12),
        ["round 104:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 104: service latency drops after the patch", 16),
        ["round 104:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 104: service latency drops after the patch", 24),
        ["round 104: service", "latency drops after the", "patch"],
    ),
    (("round 104: service latency drops after the patch", 32), ["round 104: service latency drops", "after the patch"]),
    (
        ("round 104: the library caches every vector it sees", 4),
        ["round", "104:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 104: the library caches every vector it sees", 8),
        ["round", "104: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 104: the library caches every vector it sees", 12),
        ["round 104:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 104: the library caches every vector it sees", 16),
        ["round 104: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 104: the library caches every vector it sees", 24),
        ["round 104: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 104: the library caches every vector it sees", 32),
        ["round 104: the library caches", "every vector it sees"],
    ),
    (
        ("round 104: agents argue then the debate resolves", 4),
        ["round", "104:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 104: agents argue then the debate resolves", 8),
        ["round", "104:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 104: agents argue then the debate resolves", 12),
        ["round 104:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 104: agents argue then the debate resolves", 16),
        ["round 104:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 104: agents argue then the debate resolves", 24), ["round 104: agents argue", "then the debate resolves"]),
    (("round 104: agents argue then the debate resolves", 32), ["round 104: agents argue then the", "debate resolves"]),
    (
        ("round 104: the filter keeps only strong matches", 4),
        ["round", "104:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 104: the filter keeps only strong matches", 8),
        ["round", "104: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 104: the filter keeps only strong matches", 12),
        ["round 104:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 104: the filter keeps only strong matches", 16),
        ["round 104: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 104: the filter keeps only strong matches", 24),
        ["round 104: the filter", "keeps only strong", "matches"],
    ),
    (("round 104: the filter keeps only strong matches", 32), ["round 104: the filter keeps only", "strong matches"]),
    (
        ("round 104: the model answers with a short reply", 4),
        ["round", "104:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 104: the model answers with a short reply", 8),
        ["round", "104: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 104: the model answers with a short reply", 12),
        ["round 104:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 104: the model answers with a short reply", 16),
        ["round 104: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 104: the model answers with a short reply", 24),
        ["round 104: the model", "answers with a short", "reply"],
    ),
    (("round 104: the model answers with a short reply", 32), ["round 104: the model answers", "with a short reply"]),
    (
        ("round 104: the recorder stores the reasoning trace", 4),
        ["round", "104:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 104: the recorder stores the reasoning trace", 8),
        ["round", "104: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 104: the recorder stores the reasoning trace", 12),
        ["round 104:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 104: the recorder stores the reasoning trace", 16),
        ["round 104: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 104: the recorder stores the reasoning trace", 24),
        ["round 104: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 104: the recorder stores the reasoning trace", 32),
        ["round 104: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 104: the angel watches the processor run", 4),
        ["round", "104:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 104: the angel watches the processor run", 8),
        ["round", "104: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 104: the angel watches the processor run", 12),
        ["round 104:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 104: the angel watches the processor run", 16),
        ["round 104: the", "angel watches", "the processor", "run"],
    ),
    (("round 104: the angel watches the processor run", 24), ["round 104: the angel", "watches the processor", "run"]),
    (("round 104: the angel watches the processor run", 32), ["round 104: the angel watches the", "processor run"]),
    (
        ("round 104: angle of the vector decides the match", 4),
        ["round", "104:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 104: angle of the vector decides the match", 8),
        ["round", "104:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 104: angle of the vector decides the match", 12),
        ["round 104:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 104: angle of the vector decides the match", 16),
        ["round 104: angle", "of the vector", "decides the", "match"],
    ),
    (("round 104: angle of the vector decides the match", 24), ["round 104: angle of the", "vector decides the match"]),
    (("round 104: angle of the vector decides the match", 32), ["round 104: angle of the vector", "decides the match"]),
    (
        ("round 104: the candle burns twice as long at night", 4),
        ["round", "104:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 104: the candle burns twice as long at night", 8),
        ["round", "104: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 104: the candle burns twice as long at night", 12),
        ["round 104:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 104: the candle burns twice as long at night", 16),
        ["round 104: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 104: the candle burns twice as long at night", 24),
        ["round 104: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 104: the candle burns twice as long at night", 32),
        ["round 104: the candle burns", "twice as long at night"],
    ),
    (
        ("round 104: a mirror of the universe in one line", 4),
        ["round", "104:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 104: a mirror of the universe in one line", 8),
        ["round", "104: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 104: a mirror of the universe in one line", 12),
        ["round 104: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 104: a mirror of the universe in one line", 16),
        ["round 104: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 104: a mirror of the universe in one line", 24), ["round 104: a mirror of", "the universe in one line"]),
    (("round 104: a mirror of the universe in one line", 32), ["round 104: a mirror of the", "universe in one line"]),
    (
        ("round 104: the queue drains before the storm", 4),
        ["round", "104:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 104: the queue drains before the storm", 8),
        ["round", "104: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 104: the queue drains before the storm", 12),
        ["round 104:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 104: the queue drains before the storm", 16), ["round 104: the", "queue drains", "before the storm"]),
    (("round 104: the queue drains before the storm", 24), ["round 104: the queue", "drains before the storm"]),
    (("round 104: the queue drains before the storm", 32), ["round 104: the queue drains", "before the storm"]),
    (
        ("kitten104 sitting104 agent104 angle104 universe104 memory104", 6),
        ["kitten104", "sitting104", "agent104", "angle104", "universe104", "memory104"],
    ),
    (
        ("kitten104 sitting104 agent104 angle104 universe104 memory104", 10),
        ["kitten104", "sitting104", "agent104", "angle104", "universe104", "memory104"],
    ),
    (
        ("kitten104 sitting104 agent104 angle104 universe104 memory104", 18),
        ["kitten104", "sitting104", "agent104 angle104", "universe104", "memory104"],
    ),
    (
        ("kitten104 sitting104 agent104 angle104 universe104 memory104", 28),
        ["kitten104 sitting104", "agent104 angle104", "universe104 memory104"],
    ),
    (
        ("sitting104 agent104 angle104 universe104 memory104 stream104", 6),
        ["sitting104", "agent104", "angle104", "universe104", "memory104", "stream104"],
    ),
    (
        ("sitting104 agent104 angle104 universe104 memory104 stream104", 10),
        ["sitting104", "agent104", "angle104", "universe104", "memory104", "stream104"],
    ),
    (
        ("sitting104 agent104 angle104 universe104 memory104 stream104", 18),
        ["sitting104", "agent104 angle104", "universe104", "memory104", "stream104"],
    ),
    (
        ("sitting104 agent104 angle104 universe104 memory104 stream104", 28),
        ["sitting104 agent104 angle104", "universe104 memory104", "stream104"],
    ),
    (
        ("agent104 angle104 universe104 memory104 stream104 context104", 6),
        ["agent104", "angle104", "universe104", "memory104", "stream104", "context104"],
    ),
    (
        ("agent104 angle104 universe104 memory104 stream104 context104", 10),
        ["agent104", "angle104", "universe104", "memory104", "stream104", "context104"],
    ),
    (
        ("agent104 angle104 universe104 memory104 stream104 context104", 18),
        ["agent104 angle104", "universe104", "memory104", "stream104", "context104"],
    ),
    (
        ("agent104 angle104 universe104 memory104 stream104 context104", 28),
        ["agent104 angle104", "universe104 memory104", "stream104 context104"],
    ),
    (
        ("angle104 universe104 memory104 stream104 context104 knowledge104", 6),
        ["angle104", "universe104", "memory104", "stream104", "context104", "knowledge104"],
    ),
    (
        ("angle104 universe104 memory104 stream104 context104 knowledge104", 10),
        ["angle104", "universe104", "memory104", "stream104", "context104", "knowledge104"],
    ),
    (
        ("angle104 universe104 memory104 stream104 context104 knowledge104", 18),
        ["angle104", "universe104", "memory104", "stream104", "context104", "knowledge104"],
    ),
    (
        ("angle104 universe104 memory104 stream104 context104 knowledge104", 28),
        ["angle104 universe104", "memory104 stream104", "context104 knowledge104"],
    ),
    (
        ("universe104 memory104 stream104 context104 knowledge104 vector104", 6),
        ["universe104", "memory104", "stream104", "context104", "knowledge104", "vector104"],
    ),
    (
        ("universe104 memory104 stream104 context104 knowledge104 vector104", 10),
        ["universe104", "memory104", "stream104", "context104", "knowledge104", "vector104"],
    ),
    (
        ("universe104 memory104 stream104 context104 knowledge104 vector104", 18),
        ["universe104", "memory104", "stream104", "context104", "knowledge104", "vector104"],
    ),
    (
        ("universe104 memory104 stream104 context104 knowledge104 vector104", 28),
        ["universe104 memory104", "stream104 context104", "knowledge104 vector104"],
    ),
    (
        ("memory104 stream104 context104 knowledge104 vector104 processor104", 6),
        ["memory104", "stream104", "context104", "knowledge104", "vector104", "processor104"],
    ),
    (
        ("memory104 stream104 context104 knowledge104 vector104 processor104", 10),
        ["memory104", "stream104", "context104", "knowledge104", "vector104", "processor104"],
    ),
    (
        ("memory104 stream104 context104 knowledge104 vector104 processor104", 18),
        ["memory104", "stream104", "context104", "knowledge104", "vector104", "processor104"],
    ),
    (
        ("memory104 stream104 context104 knowledge104 vector104 processor104", 28),
        ["memory104 stream104", "context104 knowledge104", "vector104 processor104"],
    ),
    (
        ("stream104 context104 knowledge104 vector104 processor104 reasoning104", 6),
        ["stream104", "context104", "knowledge104", "vector104", "processor104", "reasoning104"],
    ),
    (
        ("stream104 context104 knowledge104 vector104 processor104 reasoning104", 10),
        ["stream104", "context104", "knowledge104", "vector104", "processor104", "reasoning104"],
    ),
    (
        ("stream104 context104 knowledge104 vector104 processor104 reasoning104", 18),
        ["stream104", "context104", "knowledge104", "vector104", "processor104", "reasoning104"],
    ),
    (
        ("stream104 context104 knowledge104 vector104 processor104 reasoning104", 28),
        ["stream104 context104", "knowledge104 vector104", "processor104 reasoning104"],
    ),
    (
        ("context104 knowledge104 vector104 processor104 reasoning104 machine104", 6),
        ["context104", "knowledge104", "vector104", "processor104", "reasoning104", "machine104"],
    ),
    (
        ("context104 knowledge104 vector104 processor104 reasoning104 machine104", 10),
        ["context104", "knowledge104", "vector104", "processor104", "reasoning104", "machine104"],
    ),
    (
        ("context104 knowledge104 vector104 processor104 reasoning104 machine104", 18),
        ["context104", "knowledge104", "vector104", "processor104", "reasoning104", "machine104"],
    ),
    (
        ("context104 knowledge104 vector104 processor104 reasoning104 machine104", 28),
        ["context104 knowledge104", "vector104 processor104", "reasoning104 machine104"],
    ),
    (
        ("knowledge104 vector104 processor104 reasoning104 machine104 learning104", 6),
        ["knowledge104", "vector104", "processor104", "reasoning104", "machine104", "learning104"],
    ),
    (
        ("knowledge104 vector104 processor104 reasoning104 machine104 learning104", 10),
        ["knowledge104", "vector104", "processor104", "reasoning104", "machine104", "learning104"],
    ),
    (
        ("knowledge104 vector104 processor104 reasoning104 machine104 learning104", 18),
        ["knowledge104", "vector104", "processor104", "reasoning104", "machine104", "learning104"],
    ),
    (
        ("knowledge104 vector104 processor104 reasoning104 machine104 learning104", 28),
        ["knowledge104 vector104", "processor104 reasoning104", "machine104 learning104"],
    ),
    (
        ("vector104 processor104 reasoning104 machine104 learning104 model104", 6),
        ["vector104", "processor104", "reasoning104", "machine104", "learning104", "model104"],
    ),
    (
        ("vector104 processor104 reasoning104 machine104 learning104 model104", 10),
        ["vector104", "processor104", "reasoning104", "machine104", "learning104", "model104"],
    ),
    (
        ("vector104 processor104 reasoning104 machine104 learning104 model104", 18),
        ["vector104", "processor104", "reasoning104", "machine104", "learning104", "model104"],
    ),
    (
        ("vector104 processor104 reasoning104 machine104 learning104 model104", 28),
        ["vector104 processor104", "reasoning104 machine104", "learning104 model104"],
    ),
    (
        ("processor104 reasoning104 machine104 learning104 model104 token104", 6),
        ["processor104", "reasoning104", "machine104", "learning104", "model104", "token104"],
    ),
    (
        ("processor104 reasoning104 machine104 learning104 model104 token104", 10),
        ["processor104", "reasoning104", "machine104", "learning104", "model104", "token104"],
    ),
    (
        ("processor104 reasoning104 machine104 learning104 model104 token104", 18),
        ["processor104", "reasoning104", "machine104", "learning104", "model104 token104"],
    ),
    (
        ("processor104 reasoning104 machine104 learning104 model104 token104", 28),
        ["processor104 reasoning104", "machine104 learning104", "model104 token104"],
    ),
    (
        ("reasoning104 machine104 learning104 model104 token104 prompt104", 6),
        ["reasoning104", "machine104", "learning104", "model104", "token104", "prompt104"],
    ),
    (
        ("reasoning104 machine104 learning104 model104 token104 prompt104", 10),
        ["reasoning104", "machine104", "learning104", "model104", "token104", "prompt104"],
    ),
    (
        ("reasoning104 machine104 learning104 model104 token104 prompt104", 18),
        ["reasoning104", "machine104", "learning104", "model104 token104", "prompt104"],
    ),
    (
        ("reasoning104 machine104 learning104 model104 token104 prompt104", 28),
        ["reasoning104 machine104", "learning104 model104", "token104 prompt104"],
    ),
    (
        ("machine104 learning104 model104 token104 prompt104 session104", 6),
        ["machine104", "learning104", "model104", "token104", "prompt104", "session104"],
    ),
    (
        ("machine104 learning104 model104 token104 prompt104 session104", 10),
        ["machine104", "learning104", "model104", "token104", "prompt104", "session104"],
    ),
    (
        ("machine104 learning104 model104 token104 prompt104 session104", 18),
        ["machine104", "learning104", "model104 token104", "prompt104", "session104"],
    ),
    (
        ("machine104 learning104 model104 token104 prompt104 session104", 28),
        ["machine104 learning104", "model104 token104 prompt104", "session104"],
    ),
    (
        ("learning104 model104 token104 prompt104 session104 library104", 6),
        ["learning104", "model104", "token104", "prompt104", "session104", "library104"],
    ),
    (
        ("learning104 model104 token104 prompt104 session104 library104", 10),
        ["learning104", "model104", "token104", "prompt104", "session104", "library104"],
    ),
    (
        ("learning104 model104 token104 prompt104 session104 library104", 18),
        ["learning104", "model104 token104", "prompt104", "session104", "library104"],
    ),
    (
        ("learning104 model104 token104 prompt104 session104 library104", 28),
        ["learning104 model104", "token104 prompt104", "session104 library104"],
    ),
    (
        ("model104 token104 prompt104 session104 library104 service104", 6),
        ["model104", "token104", "prompt104", "session104", "library104", "service104"],
    ),
    (
        ("model104 token104 prompt104 session104 library104 service104", 10),
        ["model104", "token104", "prompt104", "session104", "library104", "service104"],
    ),
    (
        ("model104 token104 prompt104 session104 library104 service104", 18),
        ["model104 token104", "prompt104", "session104", "library104", "service104"],
    ),
    (
        ("model104 token104 prompt104 session104 library104 service104", 28),
        ["model104 token104 prompt104", "session104 library104", "service104"],
    ),
    (
        ("token104 prompt104 session104 library104 service104 gateway104", 6),
        ["token104", "prompt104", "session104", "library104", "service104", "gateway104"],
    ),
    (
        ("token104 prompt104 session104 library104 service104 gateway104", 10),
        ["token104", "prompt104", "session104", "library104", "service104", "gateway104"],
    ),
    (
        ("token104 prompt104 session104 library104 service104 gateway104", 18),
        ["token104 prompt104", "session104", "library104", "service104", "gateway104"],
    ),
    (
        ("token104 prompt104 session104 library104 service104 gateway104", 28),
        ["token104 prompt104", "session104 library104", "service104 gateway104"],
    ),
    (
        ("prompt104 session104 library104 service104 gateway104 storage104", 6),
        ["prompt104", "session104", "library104", "service104", "gateway104", "storage104"],
    ),
    (
        ("prompt104 session104 library104 service104 gateway104 storage104", 10),
        ["prompt104", "session104", "library104", "service104", "gateway104", "storage104"],
    ),
    (
        ("prompt104 session104 library104 service104 gateway104 storage104", 18),
        ["prompt104", "session104", "library104", "service104", "gateway104", "storage104"],
    ),
    (
        ("prompt104 session104 library104 service104 gateway104 storage104", 28),
        ["prompt104 session104", "library104 service104", "gateway104 storage104"],
    ),
    (
        ("session104 library104 service104 gateway104 storage104 network104", 6),
        ["session104", "library104", "service104", "gateway104", "storage104", "network104"],
    ),
    (
        ("session104 library104 service104 gateway104 storage104 network104", 10),
        ["session104", "library104", "service104", "gateway104", "storage104", "network104"],
    ),
    (
        ("session104 library104 service104 gateway104 storage104 network104", 18),
        ["session104", "library104", "service104", "gateway104", "storage104", "network104"],
    ),
    (
        ("session104 library104 service104 gateway104 storage104 network104", 28),
        ["session104 library104", "service104 gateway104", "storage104 network104"],
    ),
    (
        ("library104 service104 gateway104 storage104 network104 latency104", 6),
        ["library104", "service104", "gateway104", "storage104", "network104", "latency104"],
    ),
    (
        ("library104 service104 gateway104 storage104 network104 latency104", 10),
        ["library104", "service104", "gateway104", "storage104", "network104", "latency104"],
    ),
    (
        ("library104 service104 gateway104 storage104 network104 latency104", 18),
        ["library104", "service104", "gateway104", "storage104", "network104", "latency104"],
    ),
    (
        ("library104 service104 gateway104 storage104 network104 latency104", 28),
        ["library104 service104", "gateway104 storage104", "network104 latency104"],
    ),
    (
        ("service104 gateway104 storage104 network104 latency104 buffer104", 6),
        ["service104", "gateway104", "storage104", "network104", "latency104", "buffer104"],
    ),
    (
        ("service104 gateway104 storage104 network104 latency104 buffer104", 10),
        ["service104", "gateway104", "storage104", "network104", "latency104", "buffer104"],
    ),
    (
        ("service104 gateway104 storage104 network104 latency104 buffer104", 18),
        ["service104", "gateway104", "storage104", "network104", "latency104", "buffer104"],
    ),
    (
        ("service104 gateway104 storage104 network104 latency104 buffer104", 28),
        ["service104 gateway104", "storage104 network104", "latency104 buffer104"],
    ),
    (
        ("gateway104 storage104 network104 latency104 buffer104 queue104", 6),
        ["gateway104", "storage104", "network104", "latency104", "buffer104", "queue104"],
    ),
    (
        ("gateway104 storage104 network104 latency104 buffer104 queue104", 10),
        ["gateway104", "storage104", "network104", "latency104", "buffer104", "queue104"],
    ),
    (
        ("gateway104 storage104 network104 latency104 buffer104 queue104", 18),
        ["gateway104", "storage104", "network104", "latency104", "buffer104 queue104"],
    ),
    (
        ("gateway104 storage104 network104 latency104 buffer104 queue104", 28),
        ["gateway104 storage104", "network104 latency104", "buffer104 queue104"],
    ),
    (
        ("storage104 network104 latency104 buffer104 queue104 worker104", 6),
        ["storage104", "network104", "latency104", "buffer104", "queue104", "worker104"],
    ),
    (
        ("storage104 network104 latency104 buffer104 queue104 worker104", 10),
        ["storage104", "network104", "latency104", "buffer104", "queue104", "worker104"],
    ),
    (
        ("storage104 network104 latency104 buffer104 queue104 worker104", 18),
        ["storage104", "network104", "latency104", "buffer104 queue104", "worker104"],
    ),
    (
        ("storage104 network104 latency104 buffer104 queue104 worker104", 28),
        ["storage104 network104", "latency104 buffer104", "queue104 worker104"],
    ),
    (
        ("network104 latency104 buffer104 queue104 worker104 kernel104", 6),
        ["network104", "latency104", "buffer104", "queue104", "worker104", "kernel104"],
    ),
    (
        ("network104 latency104 buffer104 queue104 worker104 kernel104", 10),
        ["network104", "latency104", "buffer104", "queue104", "worker104", "kernel104"],
    ),
    (
        ("network104 latency104 buffer104 queue104 worker104 kernel104", 18),
        ["network104", "latency104", "buffer104 queue104", "worker104", "kernel104"],
    ),
    (
        ("network104 latency104 buffer104 queue104 worker104 kernel104", 28),
        ["network104 latency104", "buffer104 queue104 worker104", "kernel104"],
    ),
    (
        ("latency104 buffer104 queue104 worker104 kernel104 signal104", 6),
        ["latency104", "buffer104", "queue104", "worker104", "kernel104", "signal104"],
    ),
    (
        ("latency104 buffer104 queue104 worker104 kernel104 signal104", 10),
        ["latency104", "buffer104", "queue104", "worker104", "kernel104", "signal104"],
    ),
    (
        ("latency104 buffer104 queue104 worker104 kernel104 signal104", 18),
        ["latency104", "buffer104 queue104", "worker104", "kernel104", "signal104"],
    ),
    (
        ("latency104 buffer104 queue104 worker104 kernel104 signal104", 28),
        ["latency104 buffer104", "queue104 worker104 kernel104", "signal104"],
    ),
    (
        ("buffer104 queue104 worker104 kernel104 signal104 packet104", 6),
        ["buffer104", "queue104", "worker104", "kernel104", "signal104", "packet104"],
    ),
    (
        ("buffer104 queue104 worker104 kernel104 signal104 packet104", 10),
        ["buffer104", "queue104", "worker104", "kernel104", "signal104", "packet104"],
    ),
    (
        ("buffer104 queue104 worker104 kernel104 signal104 packet104", 18),
        ["buffer104 queue104", "worker104", "kernel104", "signal104", "packet104"],
    ),
    (
        ("buffer104 queue104 worker104 kernel104 signal104 packet104", 28),
        ["buffer104 queue104 worker104", "kernel104 signal104", "packet104"],
    ),
    (
        ("queue104 worker104 kernel104 signal104 packet104 router104", 6),
        ["queue104", "worker104", "kernel104", "signal104", "packet104", "router104"],
    ),
    (
        ("queue104 worker104 kernel104 signal104 packet104 router104", 10),
        ["queue104", "worker104", "kernel104", "signal104", "packet104", "router104"],
    ),
    (
        ("queue104 worker104 kernel104 signal104 packet104 router104", 18),
        ["queue104 worker104", "kernel104", "signal104", "packet104", "router104"],
    ),
    (
        ("queue104 worker104 kernel104 signal104 packet104 router104", 28),
        ["queue104 worker104 kernel104", "signal104 packet104", "router104"],
    ),
    (
        ("worker104 kernel104 signal104 packet104 router104 cluster104", 6),
        ["worker104", "kernel104", "signal104", "packet104", "router104", "cluster104"],
    ),
    (
        ("worker104 kernel104 signal104 packet104 router104 cluster104", 10),
        ["worker104", "kernel104", "signal104", "packet104", "router104", "cluster104"],
    ),
    (
        ("worker104 kernel104 signal104 packet104 router104 cluster104", 18),
        ["worker104", "kernel104", "signal104", "packet104", "router104", "cluster104"],
    ),
    (
        ("worker104 kernel104 signal104 packet104 router104 cluster104", 28),
        ["worker104 kernel104", "signal104 packet104", "router104 cluster104"],
    ),
    (
        ("kernel104 signal104 packet104 router104 cluster104 mirror104", 6),
        ["kernel104", "signal104", "packet104", "router104", "cluster104", "mirror104"],
    ),
    (
        ("kernel104 signal104 packet104 router104 cluster104 mirror104", 10),
        ["kernel104", "signal104", "packet104", "router104", "cluster104", "mirror104"],
    ),
    (
        ("kernel104 signal104 packet104 router104 cluster104 mirror104", 18),
        ["kernel104", "signal104", "packet104", "router104", "cluster104", "mirror104"],
    ),
    (
        ("kernel104 signal104 packet104 router104 cluster104 mirror104", 28),
        ["kernel104 signal104", "packet104 router104", "cluster104 mirror104"],
    ),
    (
        ("signal104 packet104 router104 cluster104 mirror104 filter104", 6),
        ["signal104", "packet104", "router104", "cluster104", "mirror104", "filter104"],
    ),
    (
        ("signal104 packet104 router104 cluster104 mirror104 filter104", 10),
        ["signal104", "packet104", "router104", "cluster104", "mirror104", "filter104"],
    ),
    (
        ("signal104 packet104 router104 cluster104 mirror104 filter104", 18),
        ["signal104", "packet104", "router104", "cluster104", "mirror104", "filter104"],
    ),
    (
        ("signal104 packet104 router104 cluster104 mirror104 filter104", 28),
        ["signal104 packet104", "router104 cluster104", "mirror104 filter104"],
    ),
    (
        ("packet104 router104 cluster104 mirror104 filter104 ranking104", 6),
        ["packet104", "router104", "cluster104", "mirror104", "filter104", "ranking104"],
    ),
    (
        ("packet104 router104 cluster104 mirror104 filter104 ranking104", 10),
        ["packet104", "router104", "cluster104", "mirror104", "filter104", "ranking104"],
    ),
    (
        ("packet104 router104 cluster104 mirror104 filter104 ranking104", 18),
        ["packet104", "router104", "cluster104", "mirror104", "filter104", "ranking104"],
    ),
    (
        ("packet104 router104 cluster104 mirror104 filter104 ranking104", 28),
        ["packet104 router104", "cluster104 mirror104", "filter104 ranking104"],
    ),
    (
        ("router104 cluster104 mirror104 filter104 ranking104 encoding104", 6),
        ["router104", "cluster104", "mirror104", "filter104", "ranking104", "encoding104"],
    ),
    (
        ("router104 cluster104 mirror104 filter104 ranking104 encoding104", 10),
        ["router104", "cluster104", "mirror104", "filter104", "ranking104", "encoding104"],
    ),
    (
        ("router104 cluster104 mirror104 filter104 ranking104 encoding104", 18),
        ["router104", "cluster104", "mirror104", "filter104", "ranking104", "encoding104"],
    ),
    (
        ("router104 cluster104 mirror104 filter104 ranking104 encoding104", 28),
        ["router104 cluster104", "mirror104 filter104", "ranking104 encoding104"],
    ),
    (
        ("cluster104 mirror104 filter104 ranking104 encoding104 mapping104", 6),
        ["cluster104", "mirror104", "filter104", "ranking104", "encoding104", "mapping104"],
    ),
    (
        ("cluster104 mirror104 filter104 ranking104 encoding104 mapping104", 10),
        ["cluster104", "mirror104", "filter104", "ranking104", "encoding104", "mapping104"],
    ),
    (
        ("cluster104 mirror104 filter104 ranking104 encoding104 mapping104", 18),
        ["cluster104", "mirror104", "filter104", "ranking104", "encoding104", "mapping104"],
    ),
    (
        ("cluster104 mirror104 filter104 ranking104 encoding104 mapping104", 28),
        ["cluster104 mirror104", "filter104 ranking104", "encoding104 mapping104"],
    ),
    (
        ("mirror104 filter104 ranking104 encoding104 mapping104 record104", 6),
        ["mirror104", "filter104", "ranking104", "encoding104", "mapping104", "record104"],
    ),
    (
        ("mirror104 filter104 ranking104 encoding104 mapping104 record104", 10),
        ["mirror104", "filter104", "ranking104", "encoding104", "mapping104", "record104"],
    ),
    (
        ("mirror104 filter104 ranking104 encoding104 mapping104 record104", 18),
        ["mirror104", "filter104", "ranking104", "encoding104", "mapping104", "record104"],
    ),
    (
        ("mirror104 filter104 ranking104 encoding104 mapping104 record104", 28),
        ["mirror104 filter104", "ranking104 encoding104", "mapping104 record104"],
    ),
    (
        ("filter104 ranking104 encoding104 mapping104 record104 candle104", 6),
        ["filter104", "ranking104", "encoding104", "mapping104", "record104", "candle104"],
    ),
    (
        ("filter104 ranking104 encoding104 mapping104 record104 candle104", 10),
        ["filter104", "ranking104", "encoding104", "mapping104", "record104", "candle104"],
    ),
    (
        ("filter104 ranking104 encoding104 mapping104 record104 candle104", 18),
        ["filter104", "ranking104", "encoding104", "mapping104", "record104", "candle104"],
    ),
    (
        ("filter104 ranking104 encoding104 mapping104 record104 candle104", 28),
        ["filter104 ranking104", "encoding104 mapping104", "record104 candle104"],
    ),
    (
        ("ranking104 encoding104 mapping104 record104 candle104 thread104", 6),
        ["ranking104", "encoding104", "mapping104", "record104", "candle104", "thread104"],
    ),
    (
        ("ranking104 encoding104 mapping104 record104 candle104 thread104", 10),
        ["ranking104", "encoding104", "mapping104", "record104", "candle104", "thread104"],
    ),
    (
        ("ranking104 encoding104 mapping104 record104 candle104 thread104", 18),
        ["ranking104", "encoding104", "mapping104", "record104", "candle104", "thread104"],
    ),
    (
        ("ranking104 encoding104 mapping104 record104 candle104 thread104", 28),
        ["ranking104 encoding104", "mapping104 record104", "candle104 thread104"],
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
