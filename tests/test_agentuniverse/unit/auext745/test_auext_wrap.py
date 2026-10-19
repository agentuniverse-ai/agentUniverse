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
        ("round 745: the quick brown fox jumps over the lazy dog", 4),
        ["round", "745:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", 8),
        ["round", "745: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", 12),
        ["round 745:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", 16),
        ["round 745: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", 24),
        ["round 745: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 745: the quick brown fox jumps over the lazy dog", 32),
        ["round 745: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", 4),
        ["round", "745:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", 8),
        ["round", "745:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", 12),
        ["round 745:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", 16),
        ["round 745:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", 24),
        ["round 745: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 745: agentuniverse is a framework for multi agents", 32),
        ["round 745: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", 4),
        ["round", "745:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", 8),
        ["round", "745:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", 12),
        ["round 745:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", 16),
        ["round 745:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", 24),
        ["round 745: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 745: knowledge stored as vectors enables retrieval", 32),
        ["round 745: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 745: the processor reads the record then stops", 4),
        ["round", "745:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 745: the processor reads the record then stops", 8),
        ["round", "745: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 745: the processor reads the record then stops", 12),
        ["round 745:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 745: the processor reads the record then stops", 16),
        ["round 745: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 745: the processor reads the record then stops", 24),
        ["round 745: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 745: the processor reads the record then stops", 32),
        ["round 745: the processor reads", "the record then stops"],
    ),
    (
        ("round 745: a worker pulls the next task from the queue", 4),
        ["round", "745:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 745: a worker pulls the next task from the queue", 8),
        ["round", "745: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 745: a worker pulls the next task from the queue", 12),
        ["round 745: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 745: a worker pulls the next task from the queue", 16),
        ["round 745: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 745: a worker pulls the next task from the queue", 24),
        ["round 745: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 745: a worker pulls the next task from the queue", 32),
        ["round 745: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 745: signals travel through the network layer", 4),
        ["round", "745:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 745: signals travel through the network layer", 8),
        ["round", "745:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 745: signals travel through the network layer", 12),
        ["round 745:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 745: signals travel through the network layer", 16),
        ["round 745:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 745: signals travel through the network layer", 24),
        ["round 745: signals", "travel through the", "network layer"],
    ),
    (
        ("round 745: signals travel through the network layer", 32),
        ["round 745: signals travel", "through the network layer"],
    ),
    (
        ("round 745: the gateway routes each request by policy", 4),
        ["round", "745:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 745: the gateway routes each request by policy", 8),
        ["round", "745: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 745: the gateway routes each request by policy", 12),
        ["round 745:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 745: the gateway routes each request by policy", 16),
        ["round 745: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 745: the gateway routes each request by policy", 24),
        ["round 745: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 745: the gateway routes each request by policy", 32),
        ["round 745: the gateway routes", "each request by policy"],
    ),
    (
        ("round 745: memory grows until the buffer is full", 4),
        ["round", "745:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 745: memory grows until the buffer is full", 8),
        ["round", "745:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 745: memory grows until the buffer is full", 12),
        ["round 745:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 745: memory grows until the buffer is full", 16),
        ["round 745:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 745: memory grows until the buffer is full", 24), ["round 745: memory grows", "until the buffer is full"]),
    (("round 745: memory grows until the buffer is full", 32), ["round 745: memory grows until", "the buffer is full"]),
    (
        ("round 745: the cluster mirrors every packet twice", 4),
        ["round", "745:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 745: the cluster mirrors every packet twice", 8),
        ["round", "745: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 745: the cluster mirrors every packet twice", 12),
        ["round 745:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 745: the cluster mirrors every packet twice", 16),
        ["round 745: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 745: the cluster mirrors every packet twice", 24),
        ["round 745: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 745: the cluster mirrors every packet twice", 32),
        ["round 745: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", 4),
        ["round", "745:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", 8),
        ["round", "745:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", 12),
        ["round 745:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", 16),
        ["round 745:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", 24),
        ["round 745: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 745: ranking uses tokens learned from the corpus", 32),
        ["round 745: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 745: a long session ends when the candle dies", 4),
        ["round", "745:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 745: a long session ends when the candle dies", 8),
        ["round", "745: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 745: a long session ends when the candle dies", 12),
        ["round 745: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 745: a long session ends when the candle dies", 16),
        ["round 745: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 745: a long session ends when the candle dies", 24),
        ["round 745: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 745: a long session ends when the candle dies", 32),
        ["round 745: a long session ends", "when the candle dies"],
    ),
    (
        ("round 745: encode the prompt then map the result", 4),
        ["round", "745:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 745: encode the prompt then map the result", 8),
        ["round", "745:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 745: encode the prompt then map the result", 12),
        ["round 745:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 745: encode the prompt then map the result", 16),
        ["round 745:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 745: encode the prompt then map the result", 24),
        ["round 745: encode the", "prompt then map the", "result"],
    ),
    (("round 745: encode the prompt then map the result", 32), ["round 745: encode the prompt", "then map the result"]),
    (
        ("round 745: the kernel wakes the worker at dawn", 4),
        ["round", "745:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 745: the kernel wakes the worker at dawn", 8),
        ["round", "745: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 745: the kernel wakes the worker at dawn", 12),
        ["round 745:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 745: the kernel wakes the worker at dawn", 16), ["round 745: the", "kernel wakes the", "worker at dawn"]),
    (("round 745: the kernel wakes the worker at dawn", 24), ["round 745: the kernel", "wakes the worker at dawn"]),
    (("round 745: the kernel wakes the worker at dawn", 32), ["round 745: the kernel wakes the", "worker at dawn"]),
    (
        ("round 745: service latency drops after the patch", 4),
        ["round", "745:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 745: service latency drops after the patch", 8),
        ["round", "745:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 745: service latency drops after the patch", 12),
        ["round 745:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 745: service latency drops after the patch", 16),
        ["round 745:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 745: service latency drops after the patch", 24),
        ["round 745: service", "latency drops after the", "patch"],
    ),
    (("round 745: service latency drops after the patch", 32), ["round 745: service latency drops", "after the patch"]),
    (
        ("round 745: the library caches every vector it sees", 4),
        ["round", "745:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 745: the library caches every vector it sees", 8),
        ["round", "745: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 745: the library caches every vector it sees", 12),
        ["round 745:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 745: the library caches every vector it sees", 16),
        ["round 745: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 745: the library caches every vector it sees", 24),
        ["round 745: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 745: the library caches every vector it sees", 32),
        ["round 745: the library caches", "every vector it sees"],
    ),
    (
        ("round 745: agents argue then the debate resolves", 4),
        ["round", "745:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 745: agents argue then the debate resolves", 8),
        ["round", "745:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 745: agents argue then the debate resolves", 12),
        ["round 745:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 745: agents argue then the debate resolves", 16),
        ["round 745:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 745: agents argue then the debate resolves", 24), ["round 745: agents argue", "then the debate resolves"]),
    (("round 745: agents argue then the debate resolves", 32), ["round 745: agents argue then the", "debate resolves"]),
    (
        ("round 745: the filter keeps only strong matches", 4),
        ["round", "745:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 745: the filter keeps only strong matches", 8),
        ["round", "745: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 745: the filter keeps only strong matches", 12),
        ["round 745:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 745: the filter keeps only strong matches", 16),
        ["round 745: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 745: the filter keeps only strong matches", 24),
        ["round 745: the filter", "keeps only strong", "matches"],
    ),
    (("round 745: the filter keeps only strong matches", 32), ["round 745: the filter keeps only", "strong matches"]),
    (
        ("round 745: the model answers with a short reply", 4),
        ["round", "745:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 745: the model answers with a short reply", 8),
        ["round", "745: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 745: the model answers with a short reply", 12),
        ["round 745:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 745: the model answers with a short reply", 16),
        ["round 745: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 745: the model answers with a short reply", 24),
        ["round 745: the model", "answers with a short", "reply"],
    ),
    (("round 745: the model answers with a short reply", 32), ["round 745: the model answers", "with a short reply"]),
    (
        ("round 745: the recorder stores the reasoning trace", 4),
        ["round", "745:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 745: the recorder stores the reasoning trace", 8),
        ["round", "745: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 745: the recorder stores the reasoning trace", 12),
        ["round 745:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 745: the recorder stores the reasoning trace", 16),
        ["round 745: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 745: the recorder stores the reasoning trace", 24),
        ["round 745: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 745: the recorder stores the reasoning trace", 32),
        ["round 745: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 745: the angel watches the processor run", 4),
        ["round", "745:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 745: the angel watches the processor run", 8),
        ["round", "745: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 745: the angel watches the processor run", 12),
        ["round 745:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 745: the angel watches the processor run", 16),
        ["round 745: the", "angel watches", "the processor", "run"],
    ),
    (("round 745: the angel watches the processor run", 24), ["round 745: the angel", "watches the processor", "run"]),
    (("round 745: the angel watches the processor run", 32), ["round 745: the angel watches the", "processor run"]),
    (
        ("round 745: angle of the vector decides the match", 4),
        ["round", "745:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 745: angle of the vector decides the match", 8),
        ["round", "745:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 745: angle of the vector decides the match", 12),
        ["round 745:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 745: angle of the vector decides the match", 16),
        ["round 745: angle", "of the vector", "decides the", "match"],
    ),
    (("round 745: angle of the vector decides the match", 24), ["round 745: angle of the", "vector decides the match"]),
    (("round 745: angle of the vector decides the match", 32), ["round 745: angle of the vector", "decides the match"]),
    (
        ("round 745: the candle burns twice as long at night", 4),
        ["round", "745:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 745: the candle burns twice as long at night", 8),
        ["round", "745: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 745: the candle burns twice as long at night", 12),
        ["round 745:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 745: the candle burns twice as long at night", 16),
        ["round 745: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 745: the candle burns twice as long at night", 24),
        ["round 745: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 745: the candle burns twice as long at night", 32),
        ["round 745: the candle burns", "twice as long at night"],
    ),
    (
        ("round 745: a mirror of the universe in one line", 4),
        ["round", "745:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 745: a mirror of the universe in one line", 8),
        ["round", "745: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 745: a mirror of the universe in one line", 12),
        ["round 745: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 745: a mirror of the universe in one line", 16),
        ["round 745: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 745: a mirror of the universe in one line", 24), ["round 745: a mirror of", "the universe in one line"]),
    (("round 745: a mirror of the universe in one line", 32), ["round 745: a mirror of the", "universe in one line"]),
    (
        ("round 745: the queue drains before the storm", 4),
        ["round", "745:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 745: the queue drains before the storm", 8),
        ["round", "745: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 745: the queue drains before the storm", 12),
        ["round 745:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 745: the queue drains before the storm", 16), ["round 745: the", "queue drains", "before the storm"]),
    (("round 745: the queue drains before the storm", 24), ["round 745: the queue", "drains before the storm"]),
    (("round 745: the queue drains before the storm", 32), ["round 745: the queue drains", "before the storm"]),
    (
        ("kitten745 sitting745 agent745 angle745 universe745 memory745", 6),
        ["kitten745", "sitting745", "agent745", "angle745", "universe745", "memory745"],
    ),
    (
        ("kitten745 sitting745 agent745 angle745 universe745 memory745", 10),
        ["kitten745", "sitting745", "agent745", "angle745", "universe745", "memory745"],
    ),
    (
        ("kitten745 sitting745 agent745 angle745 universe745 memory745", 18),
        ["kitten745", "sitting745", "agent745 angle745", "universe745", "memory745"],
    ),
    (
        ("kitten745 sitting745 agent745 angle745 universe745 memory745", 28),
        ["kitten745 sitting745", "agent745 angle745", "universe745 memory745"],
    ),
    (
        ("sitting745 agent745 angle745 universe745 memory745 stream745", 6),
        ["sitting745", "agent745", "angle745", "universe745", "memory745", "stream745"],
    ),
    (
        ("sitting745 agent745 angle745 universe745 memory745 stream745", 10),
        ["sitting745", "agent745", "angle745", "universe745", "memory745", "stream745"],
    ),
    (
        ("sitting745 agent745 angle745 universe745 memory745 stream745", 18),
        ["sitting745", "agent745 angle745", "universe745", "memory745", "stream745"],
    ),
    (
        ("sitting745 agent745 angle745 universe745 memory745 stream745", 28),
        ["sitting745 agent745 angle745", "universe745 memory745", "stream745"],
    ),
    (
        ("agent745 angle745 universe745 memory745 stream745 context745", 6),
        ["agent745", "angle745", "universe745", "memory745", "stream745", "context745"],
    ),
    (
        ("agent745 angle745 universe745 memory745 stream745 context745", 10),
        ["agent745", "angle745", "universe745", "memory745", "stream745", "context745"],
    ),
    (
        ("agent745 angle745 universe745 memory745 stream745 context745", 18),
        ["agent745 angle745", "universe745", "memory745", "stream745", "context745"],
    ),
    (
        ("agent745 angle745 universe745 memory745 stream745 context745", 28),
        ["agent745 angle745", "universe745 memory745", "stream745 context745"],
    ),
    (
        ("angle745 universe745 memory745 stream745 context745 knowledge745", 6),
        ["angle745", "universe745", "memory745", "stream745", "context745", "knowledge745"],
    ),
    (
        ("angle745 universe745 memory745 stream745 context745 knowledge745", 10),
        ["angle745", "universe745", "memory745", "stream745", "context745", "knowledge745"],
    ),
    (
        ("angle745 universe745 memory745 stream745 context745 knowledge745", 18),
        ["angle745", "universe745", "memory745", "stream745", "context745", "knowledge745"],
    ),
    (
        ("angle745 universe745 memory745 stream745 context745 knowledge745", 28),
        ["angle745 universe745", "memory745 stream745", "context745 knowledge745"],
    ),
    (
        ("universe745 memory745 stream745 context745 knowledge745 vector745", 6),
        ["universe745", "memory745", "stream745", "context745", "knowledge745", "vector745"],
    ),
    (
        ("universe745 memory745 stream745 context745 knowledge745 vector745", 10),
        ["universe745", "memory745", "stream745", "context745", "knowledge745", "vector745"],
    ),
    (
        ("universe745 memory745 stream745 context745 knowledge745 vector745", 18),
        ["universe745", "memory745", "stream745", "context745", "knowledge745", "vector745"],
    ),
    (
        ("universe745 memory745 stream745 context745 knowledge745 vector745", 28),
        ["universe745 memory745", "stream745 context745", "knowledge745 vector745"],
    ),
    (
        ("memory745 stream745 context745 knowledge745 vector745 processor745", 6),
        ["memory745", "stream745", "context745", "knowledge745", "vector745", "processor745"],
    ),
    (
        ("memory745 stream745 context745 knowledge745 vector745 processor745", 10),
        ["memory745", "stream745", "context745", "knowledge745", "vector745", "processor745"],
    ),
    (
        ("memory745 stream745 context745 knowledge745 vector745 processor745", 18),
        ["memory745", "stream745", "context745", "knowledge745", "vector745", "processor745"],
    ),
    (
        ("memory745 stream745 context745 knowledge745 vector745 processor745", 28),
        ["memory745 stream745", "context745 knowledge745", "vector745 processor745"],
    ),
    (
        ("stream745 context745 knowledge745 vector745 processor745 reasoning745", 6),
        ["stream745", "context745", "knowledge745", "vector745", "processor745", "reasoning745"],
    ),
    (
        ("stream745 context745 knowledge745 vector745 processor745 reasoning745", 10),
        ["stream745", "context745", "knowledge745", "vector745", "processor745", "reasoning745"],
    ),
    (
        ("stream745 context745 knowledge745 vector745 processor745 reasoning745", 18),
        ["stream745", "context745", "knowledge745", "vector745", "processor745", "reasoning745"],
    ),
    (
        ("stream745 context745 knowledge745 vector745 processor745 reasoning745", 28),
        ["stream745 context745", "knowledge745 vector745", "processor745 reasoning745"],
    ),
    (
        ("context745 knowledge745 vector745 processor745 reasoning745 machine745", 6),
        ["context745", "knowledge745", "vector745", "processor745", "reasoning745", "machine745"],
    ),
    (
        ("context745 knowledge745 vector745 processor745 reasoning745 machine745", 10),
        ["context745", "knowledge745", "vector745", "processor745", "reasoning745", "machine745"],
    ),
    (
        ("context745 knowledge745 vector745 processor745 reasoning745 machine745", 18),
        ["context745", "knowledge745", "vector745", "processor745", "reasoning745", "machine745"],
    ),
    (
        ("context745 knowledge745 vector745 processor745 reasoning745 machine745", 28),
        ["context745 knowledge745", "vector745 processor745", "reasoning745 machine745"],
    ),
    (
        ("knowledge745 vector745 processor745 reasoning745 machine745 learning745", 6),
        ["knowledge745", "vector745", "processor745", "reasoning745", "machine745", "learning745"],
    ),
    (
        ("knowledge745 vector745 processor745 reasoning745 machine745 learning745", 10),
        ["knowledge745", "vector745", "processor745", "reasoning745", "machine745", "learning745"],
    ),
    (
        ("knowledge745 vector745 processor745 reasoning745 machine745 learning745", 18),
        ["knowledge745", "vector745", "processor745", "reasoning745", "machine745", "learning745"],
    ),
    (
        ("knowledge745 vector745 processor745 reasoning745 machine745 learning745", 28),
        ["knowledge745 vector745", "processor745 reasoning745", "machine745 learning745"],
    ),
    (
        ("vector745 processor745 reasoning745 machine745 learning745 model745", 6),
        ["vector745", "processor745", "reasoning745", "machine745", "learning745", "model745"],
    ),
    (
        ("vector745 processor745 reasoning745 machine745 learning745 model745", 10),
        ["vector745", "processor745", "reasoning745", "machine745", "learning745", "model745"],
    ),
    (
        ("vector745 processor745 reasoning745 machine745 learning745 model745", 18),
        ["vector745", "processor745", "reasoning745", "machine745", "learning745", "model745"],
    ),
    (
        ("vector745 processor745 reasoning745 machine745 learning745 model745", 28),
        ["vector745 processor745", "reasoning745 machine745", "learning745 model745"],
    ),
    (
        ("processor745 reasoning745 machine745 learning745 model745 token745", 6),
        ["processor745", "reasoning745", "machine745", "learning745", "model745", "token745"],
    ),
    (
        ("processor745 reasoning745 machine745 learning745 model745 token745", 10),
        ["processor745", "reasoning745", "machine745", "learning745", "model745", "token745"],
    ),
    (
        ("processor745 reasoning745 machine745 learning745 model745 token745", 18),
        ["processor745", "reasoning745", "machine745", "learning745", "model745 token745"],
    ),
    (
        ("processor745 reasoning745 machine745 learning745 model745 token745", 28),
        ["processor745 reasoning745", "machine745 learning745", "model745 token745"],
    ),
    (
        ("reasoning745 machine745 learning745 model745 token745 prompt745", 6),
        ["reasoning745", "machine745", "learning745", "model745", "token745", "prompt745"],
    ),
    (
        ("reasoning745 machine745 learning745 model745 token745 prompt745", 10),
        ["reasoning745", "machine745", "learning745", "model745", "token745", "prompt745"],
    ),
    (
        ("reasoning745 machine745 learning745 model745 token745 prompt745", 18),
        ["reasoning745", "machine745", "learning745", "model745 token745", "prompt745"],
    ),
    (
        ("reasoning745 machine745 learning745 model745 token745 prompt745", 28),
        ["reasoning745 machine745", "learning745 model745", "token745 prompt745"],
    ),
    (
        ("machine745 learning745 model745 token745 prompt745 session745", 6),
        ["machine745", "learning745", "model745", "token745", "prompt745", "session745"],
    ),
    (
        ("machine745 learning745 model745 token745 prompt745 session745", 10),
        ["machine745", "learning745", "model745", "token745", "prompt745", "session745"],
    ),
    (
        ("machine745 learning745 model745 token745 prompt745 session745", 18),
        ["machine745", "learning745", "model745 token745", "prompt745", "session745"],
    ),
    (
        ("machine745 learning745 model745 token745 prompt745 session745", 28),
        ["machine745 learning745", "model745 token745 prompt745", "session745"],
    ),
    (
        ("learning745 model745 token745 prompt745 session745 library745", 6),
        ["learning745", "model745", "token745", "prompt745", "session745", "library745"],
    ),
    (
        ("learning745 model745 token745 prompt745 session745 library745", 10),
        ["learning745", "model745", "token745", "prompt745", "session745", "library745"],
    ),
    (
        ("learning745 model745 token745 prompt745 session745 library745", 18),
        ["learning745", "model745 token745", "prompt745", "session745", "library745"],
    ),
    (
        ("learning745 model745 token745 prompt745 session745 library745", 28),
        ["learning745 model745", "token745 prompt745", "session745 library745"],
    ),
    (
        ("model745 token745 prompt745 session745 library745 service745", 6),
        ["model745", "token745", "prompt745", "session745", "library745", "service745"],
    ),
    (
        ("model745 token745 prompt745 session745 library745 service745", 10),
        ["model745", "token745", "prompt745", "session745", "library745", "service745"],
    ),
    (
        ("model745 token745 prompt745 session745 library745 service745", 18),
        ["model745 token745", "prompt745", "session745", "library745", "service745"],
    ),
    (
        ("model745 token745 prompt745 session745 library745 service745", 28),
        ["model745 token745 prompt745", "session745 library745", "service745"],
    ),
    (
        ("token745 prompt745 session745 library745 service745 gateway745", 6),
        ["token745", "prompt745", "session745", "library745", "service745", "gateway745"],
    ),
    (
        ("token745 prompt745 session745 library745 service745 gateway745", 10),
        ["token745", "prompt745", "session745", "library745", "service745", "gateway745"],
    ),
    (
        ("token745 prompt745 session745 library745 service745 gateway745", 18),
        ["token745 prompt745", "session745", "library745", "service745", "gateway745"],
    ),
    (
        ("token745 prompt745 session745 library745 service745 gateway745", 28),
        ["token745 prompt745", "session745 library745", "service745 gateway745"],
    ),
    (
        ("prompt745 session745 library745 service745 gateway745 storage745", 6),
        ["prompt745", "session745", "library745", "service745", "gateway745", "storage745"],
    ),
    (
        ("prompt745 session745 library745 service745 gateway745 storage745", 10),
        ["prompt745", "session745", "library745", "service745", "gateway745", "storage745"],
    ),
    (
        ("prompt745 session745 library745 service745 gateway745 storage745", 18),
        ["prompt745", "session745", "library745", "service745", "gateway745", "storage745"],
    ),
    (
        ("prompt745 session745 library745 service745 gateway745 storage745", 28),
        ["prompt745 session745", "library745 service745", "gateway745 storage745"],
    ),
    (
        ("session745 library745 service745 gateway745 storage745 network745", 6),
        ["session745", "library745", "service745", "gateway745", "storage745", "network745"],
    ),
    (
        ("session745 library745 service745 gateway745 storage745 network745", 10),
        ["session745", "library745", "service745", "gateway745", "storage745", "network745"],
    ),
    (
        ("session745 library745 service745 gateway745 storage745 network745", 18),
        ["session745", "library745", "service745", "gateway745", "storage745", "network745"],
    ),
    (
        ("session745 library745 service745 gateway745 storage745 network745", 28),
        ["session745 library745", "service745 gateway745", "storage745 network745"],
    ),
    (
        ("library745 service745 gateway745 storage745 network745 latency745", 6),
        ["library745", "service745", "gateway745", "storage745", "network745", "latency745"],
    ),
    (
        ("library745 service745 gateway745 storage745 network745 latency745", 10),
        ["library745", "service745", "gateway745", "storage745", "network745", "latency745"],
    ),
    (
        ("library745 service745 gateway745 storage745 network745 latency745", 18),
        ["library745", "service745", "gateway745", "storage745", "network745", "latency745"],
    ),
    (
        ("library745 service745 gateway745 storage745 network745 latency745", 28),
        ["library745 service745", "gateway745 storage745", "network745 latency745"],
    ),
    (
        ("service745 gateway745 storage745 network745 latency745 buffer745", 6),
        ["service745", "gateway745", "storage745", "network745", "latency745", "buffer745"],
    ),
    (
        ("service745 gateway745 storage745 network745 latency745 buffer745", 10),
        ["service745", "gateway745", "storage745", "network745", "latency745", "buffer745"],
    ),
    (
        ("service745 gateway745 storage745 network745 latency745 buffer745", 18),
        ["service745", "gateway745", "storage745", "network745", "latency745", "buffer745"],
    ),
    (
        ("service745 gateway745 storage745 network745 latency745 buffer745", 28),
        ["service745 gateway745", "storage745 network745", "latency745 buffer745"],
    ),
    (
        ("gateway745 storage745 network745 latency745 buffer745 queue745", 6),
        ["gateway745", "storage745", "network745", "latency745", "buffer745", "queue745"],
    ),
    (
        ("gateway745 storage745 network745 latency745 buffer745 queue745", 10),
        ["gateway745", "storage745", "network745", "latency745", "buffer745", "queue745"],
    ),
    (
        ("gateway745 storage745 network745 latency745 buffer745 queue745", 18),
        ["gateway745", "storage745", "network745", "latency745", "buffer745 queue745"],
    ),
    (
        ("gateway745 storage745 network745 latency745 buffer745 queue745", 28),
        ["gateway745 storage745", "network745 latency745", "buffer745 queue745"],
    ),
    (
        ("storage745 network745 latency745 buffer745 queue745 worker745", 6),
        ["storage745", "network745", "latency745", "buffer745", "queue745", "worker745"],
    ),
    (
        ("storage745 network745 latency745 buffer745 queue745 worker745", 10),
        ["storage745", "network745", "latency745", "buffer745", "queue745", "worker745"],
    ),
    (
        ("storage745 network745 latency745 buffer745 queue745 worker745", 18),
        ["storage745", "network745", "latency745", "buffer745 queue745", "worker745"],
    ),
    (
        ("storage745 network745 latency745 buffer745 queue745 worker745", 28),
        ["storage745 network745", "latency745 buffer745", "queue745 worker745"],
    ),
    (
        ("network745 latency745 buffer745 queue745 worker745 kernel745", 6),
        ["network745", "latency745", "buffer745", "queue745", "worker745", "kernel745"],
    ),
    (
        ("network745 latency745 buffer745 queue745 worker745 kernel745", 10),
        ["network745", "latency745", "buffer745", "queue745", "worker745", "kernel745"],
    ),
    (
        ("network745 latency745 buffer745 queue745 worker745 kernel745", 18),
        ["network745", "latency745", "buffer745 queue745", "worker745", "kernel745"],
    ),
    (
        ("network745 latency745 buffer745 queue745 worker745 kernel745", 28),
        ["network745 latency745", "buffer745 queue745 worker745", "kernel745"],
    ),
    (
        ("latency745 buffer745 queue745 worker745 kernel745 signal745", 6),
        ["latency745", "buffer745", "queue745", "worker745", "kernel745", "signal745"],
    ),
    (
        ("latency745 buffer745 queue745 worker745 kernel745 signal745", 10),
        ["latency745", "buffer745", "queue745", "worker745", "kernel745", "signal745"],
    ),
    (
        ("latency745 buffer745 queue745 worker745 kernel745 signal745", 18),
        ["latency745", "buffer745 queue745", "worker745", "kernel745", "signal745"],
    ),
    (
        ("latency745 buffer745 queue745 worker745 kernel745 signal745", 28),
        ["latency745 buffer745", "queue745 worker745 kernel745", "signal745"],
    ),
    (
        ("buffer745 queue745 worker745 kernel745 signal745 packet745", 6),
        ["buffer745", "queue745", "worker745", "kernel745", "signal745", "packet745"],
    ),
    (
        ("buffer745 queue745 worker745 kernel745 signal745 packet745", 10),
        ["buffer745", "queue745", "worker745", "kernel745", "signal745", "packet745"],
    ),
    (
        ("buffer745 queue745 worker745 kernel745 signal745 packet745", 18),
        ["buffer745 queue745", "worker745", "kernel745", "signal745", "packet745"],
    ),
    (
        ("buffer745 queue745 worker745 kernel745 signal745 packet745", 28),
        ["buffer745 queue745 worker745", "kernel745 signal745", "packet745"],
    ),
    (
        ("queue745 worker745 kernel745 signal745 packet745 router745", 6),
        ["queue745", "worker745", "kernel745", "signal745", "packet745", "router745"],
    ),
    (
        ("queue745 worker745 kernel745 signal745 packet745 router745", 10),
        ["queue745", "worker745", "kernel745", "signal745", "packet745", "router745"],
    ),
    (
        ("queue745 worker745 kernel745 signal745 packet745 router745", 18),
        ["queue745 worker745", "kernel745", "signal745", "packet745", "router745"],
    ),
    (
        ("queue745 worker745 kernel745 signal745 packet745 router745", 28),
        ["queue745 worker745 kernel745", "signal745 packet745", "router745"],
    ),
    (
        ("worker745 kernel745 signal745 packet745 router745 cluster745", 6),
        ["worker745", "kernel745", "signal745", "packet745", "router745", "cluster745"],
    ),
    (
        ("worker745 kernel745 signal745 packet745 router745 cluster745", 10),
        ["worker745", "kernel745", "signal745", "packet745", "router745", "cluster745"],
    ),
    (
        ("worker745 kernel745 signal745 packet745 router745 cluster745", 18),
        ["worker745", "kernel745", "signal745", "packet745", "router745", "cluster745"],
    ),
    (
        ("worker745 kernel745 signal745 packet745 router745 cluster745", 28),
        ["worker745 kernel745", "signal745 packet745", "router745 cluster745"],
    ),
    (
        ("kernel745 signal745 packet745 router745 cluster745 mirror745", 6),
        ["kernel745", "signal745", "packet745", "router745", "cluster745", "mirror745"],
    ),
    (
        ("kernel745 signal745 packet745 router745 cluster745 mirror745", 10),
        ["kernel745", "signal745", "packet745", "router745", "cluster745", "mirror745"],
    ),
    (
        ("kernel745 signal745 packet745 router745 cluster745 mirror745", 18),
        ["kernel745", "signal745", "packet745", "router745", "cluster745", "mirror745"],
    ),
    (
        ("kernel745 signal745 packet745 router745 cluster745 mirror745", 28),
        ["kernel745 signal745", "packet745 router745", "cluster745 mirror745"],
    ),
    (
        ("signal745 packet745 router745 cluster745 mirror745 filter745", 6),
        ["signal745", "packet745", "router745", "cluster745", "mirror745", "filter745"],
    ),
    (
        ("signal745 packet745 router745 cluster745 mirror745 filter745", 10),
        ["signal745", "packet745", "router745", "cluster745", "mirror745", "filter745"],
    ),
    (
        ("signal745 packet745 router745 cluster745 mirror745 filter745", 18),
        ["signal745", "packet745", "router745", "cluster745", "mirror745", "filter745"],
    ),
    (
        ("signal745 packet745 router745 cluster745 mirror745 filter745", 28),
        ["signal745 packet745", "router745 cluster745", "mirror745 filter745"],
    ),
    (
        ("packet745 router745 cluster745 mirror745 filter745 ranking745", 6),
        ["packet745", "router745", "cluster745", "mirror745", "filter745", "ranking745"],
    ),
    (
        ("packet745 router745 cluster745 mirror745 filter745 ranking745", 10),
        ["packet745", "router745", "cluster745", "mirror745", "filter745", "ranking745"],
    ),
    (
        ("packet745 router745 cluster745 mirror745 filter745 ranking745", 18),
        ["packet745", "router745", "cluster745", "mirror745", "filter745", "ranking745"],
    ),
    (
        ("packet745 router745 cluster745 mirror745 filter745 ranking745", 28),
        ["packet745 router745", "cluster745 mirror745", "filter745 ranking745"],
    ),
    (
        ("router745 cluster745 mirror745 filter745 ranking745 encoding745", 6),
        ["router745", "cluster745", "mirror745", "filter745", "ranking745", "encoding745"],
    ),
    (
        ("router745 cluster745 mirror745 filter745 ranking745 encoding745", 10),
        ["router745", "cluster745", "mirror745", "filter745", "ranking745", "encoding745"],
    ),
    (
        ("router745 cluster745 mirror745 filter745 ranking745 encoding745", 18),
        ["router745", "cluster745", "mirror745", "filter745", "ranking745", "encoding745"],
    ),
    (
        ("router745 cluster745 mirror745 filter745 ranking745 encoding745", 28),
        ["router745 cluster745", "mirror745 filter745", "ranking745 encoding745"],
    ),
    (
        ("cluster745 mirror745 filter745 ranking745 encoding745 mapping745", 6),
        ["cluster745", "mirror745", "filter745", "ranking745", "encoding745", "mapping745"],
    ),
    (
        ("cluster745 mirror745 filter745 ranking745 encoding745 mapping745", 10),
        ["cluster745", "mirror745", "filter745", "ranking745", "encoding745", "mapping745"],
    ),
    (
        ("cluster745 mirror745 filter745 ranking745 encoding745 mapping745", 18),
        ["cluster745", "mirror745", "filter745", "ranking745", "encoding745", "mapping745"],
    ),
    (
        ("cluster745 mirror745 filter745 ranking745 encoding745 mapping745", 28),
        ["cluster745 mirror745", "filter745 ranking745", "encoding745 mapping745"],
    ),
    (
        ("mirror745 filter745 ranking745 encoding745 mapping745 record745", 6),
        ["mirror745", "filter745", "ranking745", "encoding745", "mapping745", "record745"],
    ),
    (
        ("mirror745 filter745 ranking745 encoding745 mapping745 record745", 10),
        ["mirror745", "filter745", "ranking745", "encoding745", "mapping745", "record745"],
    ),
    (
        ("mirror745 filter745 ranking745 encoding745 mapping745 record745", 18),
        ["mirror745", "filter745", "ranking745", "encoding745", "mapping745", "record745"],
    ),
    (
        ("mirror745 filter745 ranking745 encoding745 mapping745 record745", 28),
        ["mirror745 filter745", "ranking745 encoding745", "mapping745 record745"],
    ),
    (
        ("filter745 ranking745 encoding745 mapping745 record745 candle745", 6),
        ["filter745", "ranking745", "encoding745", "mapping745", "record745", "candle745"],
    ),
    (
        ("filter745 ranking745 encoding745 mapping745 record745 candle745", 10),
        ["filter745", "ranking745", "encoding745", "mapping745", "record745", "candle745"],
    ),
    (
        ("filter745 ranking745 encoding745 mapping745 record745 candle745", 18),
        ["filter745", "ranking745", "encoding745", "mapping745", "record745", "candle745"],
    ),
    (
        ("filter745 ranking745 encoding745 mapping745 record745 candle745", 28),
        ["filter745 ranking745", "encoding745 mapping745", "record745 candle745"],
    ),
    (
        ("ranking745 encoding745 mapping745 record745 candle745 thread745", 6),
        ["ranking745", "encoding745", "mapping745", "record745", "candle745", "thread745"],
    ),
    (
        ("ranking745 encoding745 mapping745 record745 candle745 thread745", 10),
        ["ranking745", "encoding745", "mapping745", "record745", "candle745", "thread745"],
    ),
    (
        ("ranking745 encoding745 mapping745 record745 candle745 thread745", 18),
        ["ranking745", "encoding745", "mapping745", "record745", "candle745", "thread745"],
    ),
    (
        ("ranking745 encoding745 mapping745 record745 candle745 thread745", 28),
        ["ranking745 encoding745", "mapping745 record745", "candle745 thread745"],
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
