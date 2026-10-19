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
        ("round 121: the quick brown fox jumps over the lazy dog", 4),
        ["round", "121:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", 8),
        ["round", "121: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", 12),
        ["round 121:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", 16),
        ["round 121: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", 24),
        ["round 121: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 121: the quick brown fox jumps over the lazy dog", 32),
        ["round 121: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", 4),
        ["round", "121:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", 8),
        ["round", "121:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", 12),
        ["round 121:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", 16),
        ["round 121:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", 24),
        ["round 121: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 121: agentuniverse is a framework for multi agents", 32),
        ["round 121: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", 4),
        ["round", "121:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", 8),
        ["round", "121:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", 12),
        ["round 121:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", 16),
        ["round 121:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", 24),
        ["round 121: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 121: knowledge stored as vectors enables retrieval", 32),
        ["round 121: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 121: the processor reads the record then stops", 4),
        ["round", "121:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 121: the processor reads the record then stops", 8),
        ["round", "121: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 121: the processor reads the record then stops", 12),
        ["round 121:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 121: the processor reads the record then stops", 16),
        ["round 121: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 121: the processor reads the record then stops", 24),
        ["round 121: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 121: the processor reads the record then stops", 32),
        ["round 121: the processor reads", "the record then stops"],
    ),
    (
        ("round 121: a worker pulls the next task from the queue", 4),
        ["round", "121:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 121: a worker pulls the next task from the queue", 8),
        ["round", "121: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 121: a worker pulls the next task from the queue", 12),
        ["round 121: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 121: a worker pulls the next task from the queue", 16),
        ["round 121: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 121: a worker pulls the next task from the queue", 24),
        ["round 121: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 121: a worker pulls the next task from the queue", 32),
        ["round 121: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 121: signals travel through the network layer", 4),
        ["round", "121:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 121: signals travel through the network layer", 8),
        ["round", "121:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 121: signals travel through the network layer", 12),
        ["round 121:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 121: signals travel through the network layer", 16),
        ["round 121:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 121: signals travel through the network layer", 24),
        ["round 121: signals", "travel through the", "network layer"],
    ),
    (
        ("round 121: signals travel through the network layer", 32),
        ["round 121: signals travel", "through the network layer"],
    ),
    (
        ("round 121: the gateway routes each request by policy", 4),
        ["round", "121:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 121: the gateway routes each request by policy", 8),
        ["round", "121: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 121: the gateway routes each request by policy", 12),
        ["round 121:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 121: the gateway routes each request by policy", 16),
        ["round 121: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 121: the gateway routes each request by policy", 24),
        ["round 121: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 121: the gateway routes each request by policy", 32),
        ["round 121: the gateway routes", "each request by policy"],
    ),
    (
        ("round 121: memory grows until the buffer is full", 4),
        ["round", "121:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 121: memory grows until the buffer is full", 8),
        ["round", "121:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 121: memory grows until the buffer is full", 12),
        ["round 121:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 121: memory grows until the buffer is full", 16),
        ["round 121:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 121: memory grows until the buffer is full", 24), ["round 121: memory grows", "until the buffer is full"]),
    (("round 121: memory grows until the buffer is full", 32), ["round 121: memory grows until", "the buffer is full"]),
    (
        ("round 121: the cluster mirrors every packet twice", 4),
        ["round", "121:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 121: the cluster mirrors every packet twice", 8),
        ["round", "121: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 121: the cluster mirrors every packet twice", 12),
        ["round 121:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 121: the cluster mirrors every packet twice", 16),
        ["round 121: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 121: the cluster mirrors every packet twice", 24),
        ["round 121: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 121: the cluster mirrors every packet twice", 32),
        ["round 121: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", 4),
        ["round", "121:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", 8),
        ["round", "121:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", 12),
        ["round 121:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", 16),
        ["round 121:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", 24),
        ["round 121: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 121: ranking uses tokens learned from the corpus", 32),
        ["round 121: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 121: a long session ends when the candle dies", 4),
        ["round", "121:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 121: a long session ends when the candle dies", 8),
        ["round", "121: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 121: a long session ends when the candle dies", 12),
        ["round 121: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 121: a long session ends when the candle dies", 16),
        ["round 121: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 121: a long session ends when the candle dies", 24),
        ["round 121: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 121: a long session ends when the candle dies", 32),
        ["round 121: a long session ends", "when the candle dies"],
    ),
    (
        ("round 121: encode the prompt then map the result", 4),
        ["round", "121:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 121: encode the prompt then map the result", 8),
        ["round", "121:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 121: encode the prompt then map the result", 12),
        ["round 121:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 121: encode the prompt then map the result", 16),
        ["round 121:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 121: encode the prompt then map the result", 24),
        ["round 121: encode the", "prompt then map the", "result"],
    ),
    (("round 121: encode the prompt then map the result", 32), ["round 121: encode the prompt", "then map the result"]),
    (
        ("round 121: the kernel wakes the worker at dawn", 4),
        ["round", "121:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 121: the kernel wakes the worker at dawn", 8),
        ["round", "121: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 121: the kernel wakes the worker at dawn", 12),
        ["round 121:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 121: the kernel wakes the worker at dawn", 16), ["round 121: the", "kernel wakes the", "worker at dawn"]),
    (("round 121: the kernel wakes the worker at dawn", 24), ["round 121: the kernel", "wakes the worker at dawn"]),
    (("round 121: the kernel wakes the worker at dawn", 32), ["round 121: the kernel wakes the", "worker at dawn"]),
    (
        ("round 121: service latency drops after the patch", 4),
        ["round", "121:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 121: service latency drops after the patch", 8),
        ["round", "121:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 121: service latency drops after the patch", 12),
        ["round 121:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 121: service latency drops after the patch", 16),
        ["round 121:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 121: service latency drops after the patch", 24),
        ["round 121: service", "latency drops after the", "patch"],
    ),
    (("round 121: service latency drops after the patch", 32), ["round 121: service latency drops", "after the patch"]),
    (
        ("round 121: the library caches every vector it sees", 4),
        ["round", "121:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 121: the library caches every vector it sees", 8),
        ["round", "121: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 121: the library caches every vector it sees", 12),
        ["round 121:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 121: the library caches every vector it sees", 16),
        ["round 121: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 121: the library caches every vector it sees", 24),
        ["round 121: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 121: the library caches every vector it sees", 32),
        ["round 121: the library caches", "every vector it sees"],
    ),
    (
        ("round 121: agents argue then the debate resolves", 4),
        ["round", "121:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 121: agents argue then the debate resolves", 8),
        ["round", "121:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 121: agents argue then the debate resolves", 12),
        ["round 121:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 121: agents argue then the debate resolves", 16),
        ["round 121:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 121: agents argue then the debate resolves", 24), ["round 121: agents argue", "then the debate resolves"]),
    (("round 121: agents argue then the debate resolves", 32), ["round 121: agents argue then the", "debate resolves"]),
    (
        ("round 121: the filter keeps only strong matches", 4),
        ["round", "121:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 121: the filter keeps only strong matches", 8),
        ["round", "121: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 121: the filter keeps only strong matches", 12),
        ["round 121:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 121: the filter keeps only strong matches", 16),
        ["round 121: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 121: the filter keeps only strong matches", 24),
        ["round 121: the filter", "keeps only strong", "matches"],
    ),
    (("round 121: the filter keeps only strong matches", 32), ["round 121: the filter keeps only", "strong matches"]),
    (
        ("round 121: the model answers with a short reply", 4),
        ["round", "121:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 121: the model answers with a short reply", 8),
        ["round", "121: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 121: the model answers with a short reply", 12),
        ["round 121:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 121: the model answers with a short reply", 16),
        ["round 121: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 121: the model answers with a short reply", 24),
        ["round 121: the model", "answers with a short", "reply"],
    ),
    (("round 121: the model answers with a short reply", 32), ["round 121: the model answers", "with a short reply"]),
    (
        ("round 121: the recorder stores the reasoning trace", 4),
        ["round", "121:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 121: the recorder stores the reasoning trace", 8),
        ["round", "121: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 121: the recorder stores the reasoning trace", 12),
        ["round 121:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 121: the recorder stores the reasoning trace", 16),
        ["round 121: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 121: the recorder stores the reasoning trace", 24),
        ["round 121: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 121: the recorder stores the reasoning trace", 32),
        ["round 121: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 121: the angel watches the processor run", 4),
        ["round", "121:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 121: the angel watches the processor run", 8),
        ["round", "121: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 121: the angel watches the processor run", 12),
        ["round 121:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 121: the angel watches the processor run", 16),
        ["round 121: the", "angel watches", "the processor", "run"],
    ),
    (("round 121: the angel watches the processor run", 24), ["round 121: the angel", "watches the processor", "run"]),
    (("round 121: the angel watches the processor run", 32), ["round 121: the angel watches the", "processor run"]),
    (
        ("round 121: angle of the vector decides the match", 4),
        ["round", "121:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 121: angle of the vector decides the match", 8),
        ["round", "121:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 121: angle of the vector decides the match", 12),
        ["round 121:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 121: angle of the vector decides the match", 16),
        ["round 121: angle", "of the vector", "decides the", "match"],
    ),
    (("round 121: angle of the vector decides the match", 24), ["round 121: angle of the", "vector decides the match"]),
    (("round 121: angle of the vector decides the match", 32), ["round 121: angle of the vector", "decides the match"]),
    (
        ("round 121: the candle burns twice as long at night", 4),
        ["round", "121:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 121: the candle burns twice as long at night", 8),
        ["round", "121: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 121: the candle burns twice as long at night", 12),
        ["round 121:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 121: the candle burns twice as long at night", 16),
        ["round 121: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 121: the candle burns twice as long at night", 24),
        ["round 121: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 121: the candle burns twice as long at night", 32),
        ["round 121: the candle burns", "twice as long at night"],
    ),
    (
        ("round 121: a mirror of the universe in one line", 4),
        ["round", "121:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 121: a mirror of the universe in one line", 8),
        ["round", "121: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 121: a mirror of the universe in one line", 12),
        ["round 121: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 121: a mirror of the universe in one line", 16),
        ["round 121: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 121: a mirror of the universe in one line", 24), ["round 121: a mirror of", "the universe in one line"]),
    (("round 121: a mirror of the universe in one line", 32), ["round 121: a mirror of the", "universe in one line"]),
    (
        ("round 121: the queue drains before the storm", 4),
        ["round", "121:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 121: the queue drains before the storm", 8),
        ["round", "121: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 121: the queue drains before the storm", 12),
        ["round 121:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 121: the queue drains before the storm", 16), ["round 121: the", "queue drains", "before the storm"]),
    (("round 121: the queue drains before the storm", 24), ["round 121: the queue", "drains before the storm"]),
    (("round 121: the queue drains before the storm", 32), ["round 121: the queue drains", "before the storm"]),
    (
        ("kitten121 sitting121 agent121 angle121 universe121 memory121", 6),
        ["kitten121", "sitting121", "agent121", "angle121", "universe121", "memory121"],
    ),
    (
        ("kitten121 sitting121 agent121 angle121 universe121 memory121", 10),
        ["kitten121", "sitting121", "agent121", "angle121", "universe121", "memory121"],
    ),
    (
        ("kitten121 sitting121 agent121 angle121 universe121 memory121", 18),
        ["kitten121", "sitting121", "agent121 angle121", "universe121", "memory121"],
    ),
    (
        ("kitten121 sitting121 agent121 angle121 universe121 memory121", 28),
        ["kitten121 sitting121", "agent121 angle121", "universe121 memory121"],
    ),
    (
        ("sitting121 agent121 angle121 universe121 memory121 stream121", 6),
        ["sitting121", "agent121", "angle121", "universe121", "memory121", "stream121"],
    ),
    (
        ("sitting121 agent121 angle121 universe121 memory121 stream121", 10),
        ["sitting121", "agent121", "angle121", "universe121", "memory121", "stream121"],
    ),
    (
        ("sitting121 agent121 angle121 universe121 memory121 stream121", 18),
        ["sitting121", "agent121 angle121", "universe121", "memory121", "stream121"],
    ),
    (
        ("sitting121 agent121 angle121 universe121 memory121 stream121", 28),
        ["sitting121 agent121 angle121", "universe121 memory121", "stream121"],
    ),
    (
        ("agent121 angle121 universe121 memory121 stream121 context121", 6),
        ["agent121", "angle121", "universe121", "memory121", "stream121", "context121"],
    ),
    (
        ("agent121 angle121 universe121 memory121 stream121 context121", 10),
        ["agent121", "angle121", "universe121", "memory121", "stream121", "context121"],
    ),
    (
        ("agent121 angle121 universe121 memory121 stream121 context121", 18),
        ["agent121 angle121", "universe121", "memory121", "stream121", "context121"],
    ),
    (
        ("agent121 angle121 universe121 memory121 stream121 context121", 28),
        ["agent121 angle121", "universe121 memory121", "stream121 context121"],
    ),
    (
        ("angle121 universe121 memory121 stream121 context121 knowledge121", 6),
        ["angle121", "universe121", "memory121", "stream121", "context121", "knowledge121"],
    ),
    (
        ("angle121 universe121 memory121 stream121 context121 knowledge121", 10),
        ["angle121", "universe121", "memory121", "stream121", "context121", "knowledge121"],
    ),
    (
        ("angle121 universe121 memory121 stream121 context121 knowledge121", 18),
        ["angle121", "universe121", "memory121", "stream121", "context121", "knowledge121"],
    ),
    (
        ("angle121 universe121 memory121 stream121 context121 knowledge121", 28),
        ["angle121 universe121", "memory121 stream121", "context121 knowledge121"],
    ),
    (
        ("universe121 memory121 stream121 context121 knowledge121 vector121", 6),
        ["universe121", "memory121", "stream121", "context121", "knowledge121", "vector121"],
    ),
    (
        ("universe121 memory121 stream121 context121 knowledge121 vector121", 10),
        ["universe121", "memory121", "stream121", "context121", "knowledge121", "vector121"],
    ),
    (
        ("universe121 memory121 stream121 context121 knowledge121 vector121", 18),
        ["universe121", "memory121", "stream121", "context121", "knowledge121", "vector121"],
    ),
    (
        ("universe121 memory121 stream121 context121 knowledge121 vector121", 28),
        ["universe121 memory121", "stream121 context121", "knowledge121 vector121"],
    ),
    (
        ("memory121 stream121 context121 knowledge121 vector121 processor121", 6),
        ["memory121", "stream121", "context121", "knowledge121", "vector121", "processor121"],
    ),
    (
        ("memory121 stream121 context121 knowledge121 vector121 processor121", 10),
        ["memory121", "stream121", "context121", "knowledge121", "vector121", "processor121"],
    ),
    (
        ("memory121 stream121 context121 knowledge121 vector121 processor121", 18),
        ["memory121", "stream121", "context121", "knowledge121", "vector121", "processor121"],
    ),
    (
        ("memory121 stream121 context121 knowledge121 vector121 processor121", 28),
        ["memory121 stream121", "context121 knowledge121", "vector121 processor121"],
    ),
    (
        ("stream121 context121 knowledge121 vector121 processor121 reasoning121", 6),
        ["stream121", "context121", "knowledge121", "vector121", "processor121", "reasoning121"],
    ),
    (
        ("stream121 context121 knowledge121 vector121 processor121 reasoning121", 10),
        ["stream121", "context121", "knowledge121", "vector121", "processor121", "reasoning121"],
    ),
    (
        ("stream121 context121 knowledge121 vector121 processor121 reasoning121", 18),
        ["stream121", "context121", "knowledge121", "vector121", "processor121", "reasoning121"],
    ),
    (
        ("stream121 context121 knowledge121 vector121 processor121 reasoning121", 28),
        ["stream121 context121", "knowledge121 vector121", "processor121 reasoning121"],
    ),
    (
        ("context121 knowledge121 vector121 processor121 reasoning121 machine121", 6),
        ["context121", "knowledge121", "vector121", "processor121", "reasoning121", "machine121"],
    ),
    (
        ("context121 knowledge121 vector121 processor121 reasoning121 machine121", 10),
        ["context121", "knowledge121", "vector121", "processor121", "reasoning121", "machine121"],
    ),
    (
        ("context121 knowledge121 vector121 processor121 reasoning121 machine121", 18),
        ["context121", "knowledge121", "vector121", "processor121", "reasoning121", "machine121"],
    ),
    (
        ("context121 knowledge121 vector121 processor121 reasoning121 machine121", 28),
        ["context121 knowledge121", "vector121 processor121", "reasoning121 machine121"],
    ),
    (
        ("knowledge121 vector121 processor121 reasoning121 machine121 learning121", 6),
        ["knowledge121", "vector121", "processor121", "reasoning121", "machine121", "learning121"],
    ),
    (
        ("knowledge121 vector121 processor121 reasoning121 machine121 learning121", 10),
        ["knowledge121", "vector121", "processor121", "reasoning121", "machine121", "learning121"],
    ),
    (
        ("knowledge121 vector121 processor121 reasoning121 machine121 learning121", 18),
        ["knowledge121", "vector121", "processor121", "reasoning121", "machine121", "learning121"],
    ),
    (
        ("knowledge121 vector121 processor121 reasoning121 machine121 learning121", 28),
        ["knowledge121 vector121", "processor121 reasoning121", "machine121 learning121"],
    ),
    (
        ("vector121 processor121 reasoning121 machine121 learning121 model121", 6),
        ["vector121", "processor121", "reasoning121", "machine121", "learning121", "model121"],
    ),
    (
        ("vector121 processor121 reasoning121 machine121 learning121 model121", 10),
        ["vector121", "processor121", "reasoning121", "machine121", "learning121", "model121"],
    ),
    (
        ("vector121 processor121 reasoning121 machine121 learning121 model121", 18),
        ["vector121", "processor121", "reasoning121", "machine121", "learning121", "model121"],
    ),
    (
        ("vector121 processor121 reasoning121 machine121 learning121 model121", 28),
        ["vector121 processor121", "reasoning121 machine121", "learning121 model121"],
    ),
    (
        ("processor121 reasoning121 machine121 learning121 model121 token121", 6),
        ["processor121", "reasoning121", "machine121", "learning121", "model121", "token121"],
    ),
    (
        ("processor121 reasoning121 machine121 learning121 model121 token121", 10),
        ["processor121", "reasoning121", "machine121", "learning121", "model121", "token121"],
    ),
    (
        ("processor121 reasoning121 machine121 learning121 model121 token121", 18),
        ["processor121", "reasoning121", "machine121", "learning121", "model121 token121"],
    ),
    (
        ("processor121 reasoning121 machine121 learning121 model121 token121", 28),
        ["processor121 reasoning121", "machine121 learning121", "model121 token121"],
    ),
    (
        ("reasoning121 machine121 learning121 model121 token121 prompt121", 6),
        ["reasoning121", "machine121", "learning121", "model121", "token121", "prompt121"],
    ),
    (
        ("reasoning121 machine121 learning121 model121 token121 prompt121", 10),
        ["reasoning121", "machine121", "learning121", "model121", "token121", "prompt121"],
    ),
    (
        ("reasoning121 machine121 learning121 model121 token121 prompt121", 18),
        ["reasoning121", "machine121", "learning121", "model121 token121", "prompt121"],
    ),
    (
        ("reasoning121 machine121 learning121 model121 token121 prompt121", 28),
        ["reasoning121 machine121", "learning121 model121", "token121 prompt121"],
    ),
    (
        ("machine121 learning121 model121 token121 prompt121 session121", 6),
        ["machine121", "learning121", "model121", "token121", "prompt121", "session121"],
    ),
    (
        ("machine121 learning121 model121 token121 prompt121 session121", 10),
        ["machine121", "learning121", "model121", "token121", "prompt121", "session121"],
    ),
    (
        ("machine121 learning121 model121 token121 prompt121 session121", 18),
        ["machine121", "learning121", "model121 token121", "prompt121", "session121"],
    ),
    (
        ("machine121 learning121 model121 token121 prompt121 session121", 28),
        ["machine121 learning121", "model121 token121 prompt121", "session121"],
    ),
    (
        ("learning121 model121 token121 prompt121 session121 library121", 6),
        ["learning121", "model121", "token121", "prompt121", "session121", "library121"],
    ),
    (
        ("learning121 model121 token121 prompt121 session121 library121", 10),
        ["learning121", "model121", "token121", "prompt121", "session121", "library121"],
    ),
    (
        ("learning121 model121 token121 prompt121 session121 library121", 18),
        ["learning121", "model121 token121", "prompt121", "session121", "library121"],
    ),
    (
        ("learning121 model121 token121 prompt121 session121 library121", 28),
        ["learning121 model121", "token121 prompt121", "session121 library121"],
    ),
    (
        ("model121 token121 prompt121 session121 library121 service121", 6),
        ["model121", "token121", "prompt121", "session121", "library121", "service121"],
    ),
    (
        ("model121 token121 prompt121 session121 library121 service121", 10),
        ["model121", "token121", "prompt121", "session121", "library121", "service121"],
    ),
    (
        ("model121 token121 prompt121 session121 library121 service121", 18),
        ["model121 token121", "prompt121", "session121", "library121", "service121"],
    ),
    (
        ("model121 token121 prompt121 session121 library121 service121", 28),
        ["model121 token121 prompt121", "session121 library121", "service121"],
    ),
    (
        ("token121 prompt121 session121 library121 service121 gateway121", 6),
        ["token121", "prompt121", "session121", "library121", "service121", "gateway121"],
    ),
    (
        ("token121 prompt121 session121 library121 service121 gateway121", 10),
        ["token121", "prompt121", "session121", "library121", "service121", "gateway121"],
    ),
    (
        ("token121 prompt121 session121 library121 service121 gateway121", 18),
        ["token121 prompt121", "session121", "library121", "service121", "gateway121"],
    ),
    (
        ("token121 prompt121 session121 library121 service121 gateway121", 28),
        ["token121 prompt121", "session121 library121", "service121 gateway121"],
    ),
    (
        ("prompt121 session121 library121 service121 gateway121 storage121", 6),
        ["prompt121", "session121", "library121", "service121", "gateway121", "storage121"],
    ),
    (
        ("prompt121 session121 library121 service121 gateway121 storage121", 10),
        ["prompt121", "session121", "library121", "service121", "gateway121", "storage121"],
    ),
    (
        ("prompt121 session121 library121 service121 gateway121 storage121", 18),
        ["prompt121", "session121", "library121", "service121", "gateway121", "storage121"],
    ),
    (
        ("prompt121 session121 library121 service121 gateway121 storage121", 28),
        ["prompt121 session121", "library121 service121", "gateway121 storage121"],
    ),
    (
        ("session121 library121 service121 gateway121 storage121 network121", 6),
        ["session121", "library121", "service121", "gateway121", "storage121", "network121"],
    ),
    (
        ("session121 library121 service121 gateway121 storage121 network121", 10),
        ["session121", "library121", "service121", "gateway121", "storage121", "network121"],
    ),
    (
        ("session121 library121 service121 gateway121 storage121 network121", 18),
        ["session121", "library121", "service121", "gateway121", "storage121", "network121"],
    ),
    (
        ("session121 library121 service121 gateway121 storage121 network121", 28),
        ["session121 library121", "service121 gateway121", "storage121 network121"],
    ),
    (
        ("library121 service121 gateway121 storage121 network121 latency121", 6),
        ["library121", "service121", "gateway121", "storage121", "network121", "latency121"],
    ),
    (
        ("library121 service121 gateway121 storage121 network121 latency121", 10),
        ["library121", "service121", "gateway121", "storage121", "network121", "latency121"],
    ),
    (
        ("library121 service121 gateway121 storage121 network121 latency121", 18),
        ["library121", "service121", "gateway121", "storage121", "network121", "latency121"],
    ),
    (
        ("library121 service121 gateway121 storage121 network121 latency121", 28),
        ["library121 service121", "gateway121 storage121", "network121 latency121"],
    ),
    (
        ("service121 gateway121 storage121 network121 latency121 buffer121", 6),
        ["service121", "gateway121", "storage121", "network121", "latency121", "buffer121"],
    ),
    (
        ("service121 gateway121 storage121 network121 latency121 buffer121", 10),
        ["service121", "gateway121", "storage121", "network121", "latency121", "buffer121"],
    ),
    (
        ("service121 gateway121 storage121 network121 latency121 buffer121", 18),
        ["service121", "gateway121", "storage121", "network121", "latency121", "buffer121"],
    ),
    (
        ("service121 gateway121 storage121 network121 latency121 buffer121", 28),
        ["service121 gateway121", "storage121 network121", "latency121 buffer121"],
    ),
    (
        ("gateway121 storage121 network121 latency121 buffer121 queue121", 6),
        ["gateway121", "storage121", "network121", "latency121", "buffer121", "queue121"],
    ),
    (
        ("gateway121 storage121 network121 latency121 buffer121 queue121", 10),
        ["gateway121", "storage121", "network121", "latency121", "buffer121", "queue121"],
    ),
    (
        ("gateway121 storage121 network121 latency121 buffer121 queue121", 18),
        ["gateway121", "storage121", "network121", "latency121", "buffer121 queue121"],
    ),
    (
        ("gateway121 storage121 network121 latency121 buffer121 queue121", 28),
        ["gateway121 storage121", "network121 latency121", "buffer121 queue121"],
    ),
    (
        ("storage121 network121 latency121 buffer121 queue121 worker121", 6),
        ["storage121", "network121", "latency121", "buffer121", "queue121", "worker121"],
    ),
    (
        ("storage121 network121 latency121 buffer121 queue121 worker121", 10),
        ["storage121", "network121", "latency121", "buffer121", "queue121", "worker121"],
    ),
    (
        ("storage121 network121 latency121 buffer121 queue121 worker121", 18),
        ["storage121", "network121", "latency121", "buffer121 queue121", "worker121"],
    ),
    (
        ("storage121 network121 latency121 buffer121 queue121 worker121", 28),
        ["storage121 network121", "latency121 buffer121", "queue121 worker121"],
    ),
    (
        ("network121 latency121 buffer121 queue121 worker121 kernel121", 6),
        ["network121", "latency121", "buffer121", "queue121", "worker121", "kernel121"],
    ),
    (
        ("network121 latency121 buffer121 queue121 worker121 kernel121", 10),
        ["network121", "latency121", "buffer121", "queue121", "worker121", "kernel121"],
    ),
    (
        ("network121 latency121 buffer121 queue121 worker121 kernel121", 18),
        ["network121", "latency121", "buffer121 queue121", "worker121", "kernel121"],
    ),
    (
        ("network121 latency121 buffer121 queue121 worker121 kernel121", 28),
        ["network121 latency121", "buffer121 queue121 worker121", "kernel121"],
    ),
    (
        ("latency121 buffer121 queue121 worker121 kernel121 signal121", 6),
        ["latency121", "buffer121", "queue121", "worker121", "kernel121", "signal121"],
    ),
    (
        ("latency121 buffer121 queue121 worker121 kernel121 signal121", 10),
        ["latency121", "buffer121", "queue121", "worker121", "kernel121", "signal121"],
    ),
    (
        ("latency121 buffer121 queue121 worker121 kernel121 signal121", 18),
        ["latency121", "buffer121 queue121", "worker121", "kernel121", "signal121"],
    ),
    (
        ("latency121 buffer121 queue121 worker121 kernel121 signal121", 28),
        ["latency121 buffer121", "queue121 worker121 kernel121", "signal121"],
    ),
    (
        ("buffer121 queue121 worker121 kernel121 signal121 packet121", 6),
        ["buffer121", "queue121", "worker121", "kernel121", "signal121", "packet121"],
    ),
    (
        ("buffer121 queue121 worker121 kernel121 signal121 packet121", 10),
        ["buffer121", "queue121", "worker121", "kernel121", "signal121", "packet121"],
    ),
    (
        ("buffer121 queue121 worker121 kernel121 signal121 packet121", 18),
        ["buffer121 queue121", "worker121", "kernel121", "signal121", "packet121"],
    ),
    (
        ("buffer121 queue121 worker121 kernel121 signal121 packet121", 28),
        ["buffer121 queue121 worker121", "kernel121 signal121", "packet121"],
    ),
    (
        ("queue121 worker121 kernel121 signal121 packet121 router121", 6),
        ["queue121", "worker121", "kernel121", "signal121", "packet121", "router121"],
    ),
    (
        ("queue121 worker121 kernel121 signal121 packet121 router121", 10),
        ["queue121", "worker121", "kernel121", "signal121", "packet121", "router121"],
    ),
    (
        ("queue121 worker121 kernel121 signal121 packet121 router121", 18),
        ["queue121 worker121", "kernel121", "signal121", "packet121", "router121"],
    ),
    (
        ("queue121 worker121 kernel121 signal121 packet121 router121", 28),
        ["queue121 worker121 kernel121", "signal121 packet121", "router121"],
    ),
    (
        ("worker121 kernel121 signal121 packet121 router121 cluster121", 6),
        ["worker121", "kernel121", "signal121", "packet121", "router121", "cluster121"],
    ),
    (
        ("worker121 kernel121 signal121 packet121 router121 cluster121", 10),
        ["worker121", "kernel121", "signal121", "packet121", "router121", "cluster121"],
    ),
    (
        ("worker121 kernel121 signal121 packet121 router121 cluster121", 18),
        ["worker121", "kernel121", "signal121", "packet121", "router121", "cluster121"],
    ),
    (
        ("worker121 kernel121 signal121 packet121 router121 cluster121", 28),
        ["worker121 kernel121", "signal121 packet121", "router121 cluster121"],
    ),
    (
        ("kernel121 signal121 packet121 router121 cluster121 mirror121", 6),
        ["kernel121", "signal121", "packet121", "router121", "cluster121", "mirror121"],
    ),
    (
        ("kernel121 signal121 packet121 router121 cluster121 mirror121", 10),
        ["kernel121", "signal121", "packet121", "router121", "cluster121", "mirror121"],
    ),
    (
        ("kernel121 signal121 packet121 router121 cluster121 mirror121", 18),
        ["kernel121", "signal121", "packet121", "router121", "cluster121", "mirror121"],
    ),
    (
        ("kernel121 signal121 packet121 router121 cluster121 mirror121", 28),
        ["kernel121 signal121", "packet121 router121", "cluster121 mirror121"],
    ),
    (
        ("signal121 packet121 router121 cluster121 mirror121 filter121", 6),
        ["signal121", "packet121", "router121", "cluster121", "mirror121", "filter121"],
    ),
    (
        ("signal121 packet121 router121 cluster121 mirror121 filter121", 10),
        ["signal121", "packet121", "router121", "cluster121", "mirror121", "filter121"],
    ),
    (
        ("signal121 packet121 router121 cluster121 mirror121 filter121", 18),
        ["signal121", "packet121", "router121", "cluster121", "mirror121", "filter121"],
    ),
    (
        ("signal121 packet121 router121 cluster121 mirror121 filter121", 28),
        ["signal121 packet121", "router121 cluster121", "mirror121 filter121"],
    ),
    (
        ("packet121 router121 cluster121 mirror121 filter121 ranking121", 6),
        ["packet121", "router121", "cluster121", "mirror121", "filter121", "ranking121"],
    ),
    (
        ("packet121 router121 cluster121 mirror121 filter121 ranking121", 10),
        ["packet121", "router121", "cluster121", "mirror121", "filter121", "ranking121"],
    ),
    (
        ("packet121 router121 cluster121 mirror121 filter121 ranking121", 18),
        ["packet121", "router121", "cluster121", "mirror121", "filter121", "ranking121"],
    ),
    (
        ("packet121 router121 cluster121 mirror121 filter121 ranking121", 28),
        ["packet121 router121", "cluster121 mirror121", "filter121 ranking121"],
    ),
    (
        ("router121 cluster121 mirror121 filter121 ranking121 encoding121", 6),
        ["router121", "cluster121", "mirror121", "filter121", "ranking121", "encoding121"],
    ),
    (
        ("router121 cluster121 mirror121 filter121 ranking121 encoding121", 10),
        ["router121", "cluster121", "mirror121", "filter121", "ranking121", "encoding121"],
    ),
    (
        ("router121 cluster121 mirror121 filter121 ranking121 encoding121", 18),
        ["router121", "cluster121", "mirror121", "filter121", "ranking121", "encoding121"],
    ),
    (
        ("router121 cluster121 mirror121 filter121 ranking121 encoding121", 28),
        ["router121 cluster121", "mirror121 filter121", "ranking121 encoding121"],
    ),
    (
        ("cluster121 mirror121 filter121 ranking121 encoding121 mapping121", 6),
        ["cluster121", "mirror121", "filter121", "ranking121", "encoding121", "mapping121"],
    ),
    (
        ("cluster121 mirror121 filter121 ranking121 encoding121 mapping121", 10),
        ["cluster121", "mirror121", "filter121", "ranking121", "encoding121", "mapping121"],
    ),
    (
        ("cluster121 mirror121 filter121 ranking121 encoding121 mapping121", 18),
        ["cluster121", "mirror121", "filter121", "ranking121", "encoding121", "mapping121"],
    ),
    (
        ("cluster121 mirror121 filter121 ranking121 encoding121 mapping121", 28),
        ["cluster121 mirror121", "filter121 ranking121", "encoding121 mapping121"],
    ),
    (
        ("mirror121 filter121 ranking121 encoding121 mapping121 record121", 6),
        ["mirror121", "filter121", "ranking121", "encoding121", "mapping121", "record121"],
    ),
    (
        ("mirror121 filter121 ranking121 encoding121 mapping121 record121", 10),
        ["mirror121", "filter121", "ranking121", "encoding121", "mapping121", "record121"],
    ),
    (
        ("mirror121 filter121 ranking121 encoding121 mapping121 record121", 18),
        ["mirror121", "filter121", "ranking121", "encoding121", "mapping121", "record121"],
    ),
    (
        ("mirror121 filter121 ranking121 encoding121 mapping121 record121", 28),
        ["mirror121 filter121", "ranking121 encoding121", "mapping121 record121"],
    ),
    (
        ("filter121 ranking121 encoding121 mapping121 record121 candle121", 6),
        ["filter121", "ranking121", "encoding121", "mapping121", "record121", "candle121"],
    ),
    (
        ("filter121 ranking121 encoding121 mapping121 record121 candle121", 10),
        ["filter121", "ranking121", "encoding121", "mapping121", "record121", "candle121"],
    ),
    (
        ("filter121 ranking121 encoding121 mapping121 record121 candle121", 18),
        ["filter121", "ranking121", "encoding121", "mapping121", "record121", "candle121"],
    ),
    (
        ("filter121 ranking121 encoding121 mapping121 record121 candle121", 28),
        ["filter121 ranking121", "encoding121 mapping121", "record121 candle121"],
    ),
    (
        ("ranking121 encoding121 mapping121 record121 candle121 thread121", 6),
        ["ranking121", "encoding121", "mapping121", "record121", "candle121", "thread121"],
    ),
    (
        ("ranking121 encoding121 mapping121 record121 candle121 thread121", 10),
        ["ranking121", "encoding121", "mapping121", "record121", "candle121", "thread121"],
    ),
    (
        ("ranking121 encoding121 mapping121 record121 candle121 thread121", 18),
        ["ranking121", "encoding121", "mapping121", "record121", "candle121", "thread121"],
    ),
    (
        ("ranking121 encoding121 mapping121 record121 candle121 thread121", 28),
        ["ranking121 encoding121", "mapping121 record121", "candle121 thread121"],
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
