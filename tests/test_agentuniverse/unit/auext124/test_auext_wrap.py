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
        ("round 124: the quick brown fox jumps over the lazy dog", 4),
        ["round", "124:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", 8),
        ["round", "124: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", 12),
        ["round 124:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", 16),
        ["round 124: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", 24),
        ["round 124: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 124: the quick brown fox jumps over the lazy dog", 32),
        ["round 124: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", 4),
        ["round", "124:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", 8),
        ["round", "124:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", 12),
        ["round 124:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", 16),
        ["round 124:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", 24),
        ["round 124: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 124: agentuniverse is a framework for multi agents", 32),
        ["round 124: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", 4),
        ["round", "124:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", 8),
        ["round", "124:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", 12),
        ["round 124:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", 16),
        ["round 124:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", 24),
        ["round 124: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 124: knowledge stored as vectors enables retrieval", 32),
        ["round 124: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 124: the processor reads the record then stops", 4),
        ["round", "124:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 124: the processor reads the record then stops", 8),
        ["round", "124: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 124: the processor reads the record then stops", 12),
        ["round 124:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 124: the processor reads the record then stops", 16),
        ["round 124: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 124: the processor reads the record then stops", 24),
        ["round 124: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 124: the processor reads the record then stops", 32),
        ["round 124: the processor reads", "the record then stops"],
    ),
    (
        ("round 124: a worker pulls the next task from the queue", 4),
        ["round", "124:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 124: a worker pulls the next task from the queue", 8),
        ["round", "124: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 124: a worker pulls the next task from the queue", 12),
        ["round 124: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 124: a worker pulls the next task from the queue", 16),
        ["round 124: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 124: a worker pulls the next task from the queue", 24),
        ["round 124: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 124: a worker pulls the next task from the queue", 32),
        ["round 124: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 124: signals travel through the network layer", 4),
        ["round", "124:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 124: signals travel through the network layer", 8),
        ["round", "124:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 124: signals travel through the network layer", 12),
        ["round 124:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 124: signals travel through the network layer", 16),
        ["round 124:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 124: signals travel through the network layer", 24),
        ["round 124: signals", "travel through the", "network layer"],
    ),
    (
        ("round 124: signals travel through the network layer", 32),
        ["round 124: signals travel", "through the network layer"],
    ),
    (
        ("round 124: the gateway routes each request by policy", 4),
        ["round", "124:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 124: the gateway routes each request by policy", 8),
        ["round", "124: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 124: the gateway routes each request by policy", 12),
        ["round 124:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 124: the gateway routes each request by policy", 16),
        ["round 124: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 124: the gateway routes each request by policy", 24),
        ["round 124: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 124: the gateway routes each request by policy", 32),
        ["round 124: the gateway routes", "each request by policy"],
    ),
    (
        ("round 124: memory grows until the buffer is full", 4),
        ["round", "124:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 124: memory grows until the buffer is full", 8),
        ["round", "124:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 124: memory grows until the buffer is full", 12),
        ["round 124:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 124: memory grows until the buffer is full", 16),
        ["round 124:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 124: memory grows until the buffer is full", 24), ["round 124: memory grows", "until the buffer is full"]),
    (("round 124: memory grows until the buffer is full", 32), ["round 124: memory grows until", "the buffer is full"]),
    (
        ("round 124: the cluster mirrors every packet twice", 4),
        ["round", "124:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 124: the cluster mirrors every packet twice", 8),
        ["round", "124: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 124: the cluster mirrors every packet twice", 12),
        ["round 124:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 124: the cluster mirrors every packet twice", 16),
        ["round 124: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 124: the cluster mirrors every packet twice", 24),
        ["round 124: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 124: the cluster mirrors every packet twice", 32),
        ["round 124: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", 4),
        ["round", "124:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", 8),
        ["round", "124:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", 12),
        ["round 124:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", 16),
        ["round 124:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", 24),
        ["round 124: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 124: ranking uses tokens learned from the corpus", 32),
        ["round 124: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 124: a long session ends when the candle dies", 4),
        ["round", "124:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 124: a long session ends when the candle dies", 8),
        ["round", "124: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 124: a long session ends when the candle dies", 12),
        ["round 124: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 124: a long session ends when the candle dies", 16),
        ["round 124: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 124: a long session ends when the candle dies", 24),
        ["round 124: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 124: a long session ends when the candle dies", 32),
        ["round 124: a long session ends", "when the candle dies"],
    ),
    (
        ("round 124: encode the prompt then map the result", 4),
        ["round", "124:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 124: encode the prompt then map the result", 8),
        ["round", "124:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 124: encode the prompt then map the result", 12),
        ["round 124:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 124: encode the prompt then map the result", 16),
        ["round 124:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 124: encode the prompt then map the result", 24),
        ["round 124: encode the", "prompt then map the", "result"],
    ),
    (("round 124: encode the prompt then map the result", 32), ["round 124: encode the prompt", "then map the result"]),
    (
        ("round 124: the kernel wakes the worker at dawn", 4),
        ["round", "124:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 124: the kernel wakes the worker at dawn", 8),
        ["round", "124: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 124: the kernel wakes the worker at dawn", 12),
        ["round 124:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 124: the kernel wakes the worker at dawn", 16), ["round 124: the", "kernel wakes the", "worker at dawn"]),
    (("round 124: the kernel wakes the worker at dawn", 24), ["round 124: the kernel", "wakes the worker at dawn"]),
    (("round 124: the kernel wakes the worker at dawn", 32), ["round 124: the kernel wakes the", "worker at dawn"]),
    (
        ("round 124: service latency drops after the patch", 4),
        ["round", "124:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 124: service latency drops after the patch", 8),
        ["round", "124:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 124: service latency drops after the patch", 12),
        ["round 124:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 124: service latency drops after the patch", 16),
        ["round 124:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 124: service latency drops after the patch", 24),
        ["round 124: service", "latency drops after the", "patch"],
    ),
    (("round 124: service latency drops after the patch", 32), ["round 124: service latency drops", "after the patch"]),
    (
        ("round 124: the library caches every vector it sees", 4),
        ["round", "124:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 124: the library caches every vector it sees", 8),
        ["round", "124: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 124: the library caches every vector it sees", 12),
        ["round 124:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 124: the library caches every vector it sees", 16),
        ["round 124: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 124: the library caches every vector it sees", 24),
        ["round 124: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 124: the library caches every vector it sees", 32),
        ["round 124: the library caches", "every vector it sees"],
    ),
    (
        ("round 124: agents argue then the debate resolves", 4),
        ["round", "124:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 124: agents argue then the debate resolves", 8),
        ["round", "124:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 124: agents argue then the debate resolves", 12),
        ["round 124:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 124: agents argue then the debate resolves", 16),
        ["round 124:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 124: agents argue then the debate resolves", 24), ["round 124: agents argue", "then the debate resolves"]),
    (("round 124: agents argue then the debate resolves", 32), ["round 124: agents argue then the", "debate resolves"]),
    (
        ("round 124: the filter keeps only strong matches", 4),
        ["round", "124:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 124: the filter keeps only strong matches", 8),
        ["round", "124: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 124: the filter keeps only strong matches", 12),
        ["round 124:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 124: the filter keeps only strong matches", 16),
        ["round 124: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 124: the filter keeps only strong matches", 24),
        ["round 124: the filter", "keeps only strong", "matches"],
    ),
    (("round 124: the filter keeps only strong matches", 32), ["round 124: the filter keeps only", "strong matches"]),
    (
        ("round 124: the model answers with a short reply", 4),
        ["round", "124:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 124: the model answers with a short reply", 8),
        ["round", "124: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 124: the model answers with a short reply", 12),
        ["round 124:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 124: the model answers with a short reply", 16),
        ["round 124: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 124: the model answers with a short reply", 24),
        ["round 124: the model", "answers with a short", "reply"],
    ),
    (("round 124: the model answers with a short reply", 32), ["round 124: the model answers", "with a short reply"]),
    (
        ("round 124: the recorder stores the reasoning trace", 4),
        ["round", "124:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 124: the recorder stores the reasoning trace", 8),
        ["round", "124: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 124: the recorder stores the reasoning trace", 12),
        ["round 124:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 124: the recorder stores the reasoning trace", 16),
        ["round 124: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 124: the recorder stores the reasoning trace", 24),
        ["round 124: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 124: the recorder stores the reasoning trace", 32),
        ["round 124: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 124: the angel watches the processor run", 4),
        ["round", "124:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 124: the angel watches the processor run", 8),
        ["round", "124: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 124: the angel watches the processor run", 12),
        ["round 124:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 124: the angel watches the processor run", 16),
        ["round 124: the", "angel watches", "the processor", "run"],
    ),
    (("round 124: the angel watches the processor run", 24), ["round 124: the angel", "watches the processor", "run"]),
    (("round 124: the angel watches the processor run", 32), ["round 124: the angel watches the", "processor run"]),
    (
        ("round 124: angle of the vector decides the match", 4),
        ["round", "124:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 124: angle of the vector decides the match", 8),
        ["round", "124:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 124: angle of the vector decides the match", 12),
        ["round 124:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 124: angle of the vector decides the match", 16),
        ["round 124: angle", "of the vector", "decides the", "match"],
    ),
    (("round 124: angle of the vector decides the match", 24), ["round 124: angle of the", "vector decides the match"]),
    (("round 124: angle of the vector decides the match", 32), ["round 124: angle of the vector", "decides the match"]),
    (
        ("round 124: the candle burns twice as long at night", 4),
        ["round", "124:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 124: the candle burns twice as long at night", 8),
        ["round", "124: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 124: the candle burns twice as long at night", 12),
        ["round 124:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 124: the candle burns twice as long at night", 16),
        ["round 124: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 124: the candle burns twice as long at night", 24),
        ["round 124: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 124: the candle burns twice as long at night", 32),
        ["round 124: the candle burns", "twice as long at night"],
    ),
    (
        ("round 124: a mirror of the universe in one line", 4),
        ["round", "124:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 124: a mirror of the universe in one line", 8),
        ["round", "124: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 124: a mirror of the universe in one line", 12),
        ["round 124: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 124: a mirror of the universe in one line", 16),
        ["round 124: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 124: a mirror of the universe in one line", 24), ["round 124: a mirror of", "the universe in one line"]),
    (("round 124: a mirror of the universe in one line", 32), ["round 124: a mirror of the", "universe in one line"]),
    (
        ("round 124: the queue drains before the storm", 4),
        ["round", "124:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 124: the queue drains before the storm", 8),
        ["round", "124: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 124: the queue drains before the storm", 12),
        ["round 124:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 124: the queue drains before the storm", 16), ["round 124: the", "queue drains", "before the storm"]),
    (("round 124: the queue drains before the storm", 24), ["round 124: the queue", "drains before the storm"]),
    (("round 124: the queue drains before the storm", 32), ["round 124: the queue drains", "before the storm"]),
    (
        ("kitten124 sitting124 agent124 angle124 universe124 memory124", 6),
        ["kitten124", "sitting124", "agent124", "angle124", "universe124", "memory124"],
    ),
    (
        ("kitten124 sitting124 agent124 angle124 universe124 memory124", 10),
        ["kitten124", "sitting124", "agent124", "angle124", "universe124", "memory124"],
    ),
    (
        ("kitten124 sitting124 agent124 angle124 universe124 memory124", 18),
        ["kitten124", "sitting124", "agent124 angle124", "universe124", "memory124"],
    ),
    (
        ("kitten124 sitting124 agent124 angle124 universe124 memory124", 28),
        ["kitten124 sitting124", "agent124 angle124", "universe124 memory124"],
    ),
    (
        ("sitting124 agent124 angle124 universe124 memory124 stream124", 6),
        ["sitting124", "agent124", "angle124", "universe124", "memory124", "stream124"],
    ),
    (
        ("sitting124 agent124 angle124 universe124 memory124 stream124", 10),
        ["sitting124", "agent124", "angle124", "universe124", "memory124", "stream124"],
    ),
    (
        ("sitting124 agent124 angle124 universe124 memory124 stream124", 18),
        ["sitting124", "agent124 angle124", "universe124", "memory124", "stream124"],
    ),
    (
        ("sitting124 agent124 angle124 universe124 memory124 stream124", 28),
        ["sitting124 agent124 angle124", "universe124 memory124", "stream124"],
    ),
    (
        ("agent124 angle124 universe124 memory124 stream124 context124", 6),
        ["agent124", "angle124", "universe124", "memory124", "stream124", "context124"],
    ),
    (
        ("agent124 angle124 universe124 memory124 stream124 context124", 10),
        ["agent124", "angle124", "universe124", "memory124", "stream124", "context124"],
    ),
    (
        ("agent124 angle124 universe124 memory124 stream124 context124", 18),
        ["agent124 angle124", "universe124", "memory124", "stream124", "context124"],
    ),
    (
        ("agent124 angle124 universe124 memory124 stream124 context124", 28),
        ["agent124 angle124", "universe124 memory124", "stream124 context124"],
    ),
    (
        ("angle124 universe124 memory124 stream124 context124 knowledge124", 6),
        ["angle124", "universe124", "memory124", "stream124", "context124", "knowledge124"],
    ),
    (
        ("angle124 universe124 memory124 stream124 context124 knowledge124", 10),
        ["angle124", "universe124", "memory124", "stream124", "context124", "knowledge124"],
    ),
    (
        ("angle124 universe124 memory124 stream124 context124 knowledge124", 18),
        ["angle124", "universe124", "memory124", "stream124", "context124", "knowledge124"],
    ),
    (
        ("angle124 universe124 memory124 stream124 context124 knowledge124", 28),
        ["angle124 universe124", "memory124 stream124", "context124 knowledge124"],
    ),
    (
        ("universe124 memory124 stream124 context124 knowledge124 vector124", 6),
        ["universe124", "memory124", "stream124", "context124", "knowledge124", "vector124"],
    ),
    (
        ("universe124 memory124 stream124 context124 knowledge124 vector124", 10),
        ["universe124", "memory124", "stream124", "context124", "knowledge124", "vector124"],
    ),
    (
        ("universe124 memory124 stream124 context124 knowledge124 vector124", 18),
        ["universe124", "memory124", "stream124", "context124", "knowledge124", "vector124"],
    ),
    (
        ("universe124 memory124 stream124 context124 knowledge124 vector124", 28),
        ["universe124 memory124", "stream124 context124", "knowledge124 vector124"],
    ),
    (
        ("memory124 stream124 context124 knowledge124 vector124 processor124", 6),
        ["memory124", "stream124", "context124", "knowledge124", "vector124", "processor124"],
    ),
    (
        ("memory124 stream124 context124 knowledge124 vector124 processor124", 10),
        ["memory124", "stream124", "context124", "knowledge124", "vector124", "processor124"],
    ),
    (
        ("memory124 stream124 context124 knowledge124 vector124 processor124", 18),
        ["memory124", "stream124", "context124", "knowledge124", "vector124", "processor124"],
    ),
    (
        ("memory124 stream124 context124 knowledge124 vector124 processor124", 28),
        ["memory124 stream124", "context124 knowledge124", "vector124 processor124"],
    ),
    (
        ("stream124 context124 knowledge124 vector124 processor124 reasoning124", 6),
        ["stream124", "context124", "knowledge124", "vector124", "processor124", "reasoning124"],
    ),
    (
        ("stream124 context124 knowledge124 vector124 processor124 reasoning124", 10),
        ["stream124", "context124", "knowledge124", "vector124", "processor124", "reasoning124"],
    ),
    (
        ("stream124 context124 knowledge124 vector124 processor124 reasoning124", 18),
        ["stream124", "context124", "knowledge124", "vector124", "processor124", "reasoning124"],
    ),
    (
        ("stream124 context124 knowledge124 vector124 processor124 reasoning124", 28),
        ["stream124 context124", "knowledge124 vector124", "processor124 reasoning124"],
    ),
    (
        ("context124 knowledge124 vector124 processor124 reasoning124 machine124", 6),
        ["context124", "knowledge124", "vector124", "processor124", "reasoning124", "machine124"],
    ),
    (
        ("context124 knowledge124 vector124 processor124 reasoning124 machine124", 10),
        ["context124", "knowledge124", "vector124", "processor124", "reasoning124", "machine124"],
    ),
    (
        ("context124 knowledge124 vector124 processor124 reasoning124 machine124", 18),
        ["context124", "knowledge124", "vector124", "processor124", "reasoning124", "machine124"],
    ),
    (
        ("context124 knowledge124 vector124 processor124 reasoning124 machine124", 28),
        ["context124 knowledge124", "vector124 processor124", "reasoning124 machine124"],
    ),
    (
        ("knowledge124 vector124 processor124 reasoning124 machine124 learning124", 6),
        ["knowledge124", "vector124", "processor124", "reasoning124", "machine124", "learning124"],
    ),
    (
        ("knowledge124 vector124 processor124 reasoning124 machine124 learning124", 10),
        ["knowledge124", "vector124", "processor124", "reasoning124", "machine124", "learning124"],
    ),
    (
        ("knowledge124 vector124 processor124 reasoning124 machine124 learning124", 18),
        ["knowledge124", "vector124", "processor124", "reasoning124", "machine124", "learning124"],
    ),
    (
        ("knowledge124 vector124 processor124 reasoning124 machine124 learning124", 28),
        ["knowledge124 vector124", "processor124 reasoning124", "machine124 learning124"],
    ),
    (
        ("vector124 processor124 reasoning124 machine124 learning124 model124", 6),
        ["vector124", "processor124", "reasoning124", "machine124", "learning124", "model124"],
    ),
    (
        ("vector124 processor124 reasoning124 machine124 learning124 model124", 10),
        ["vector124", "processor124", "reasoning124", "machine124", "learning124", "model124"],
    ),
    (
        ("vector124 processor124 reasoning124 machine124 learning124 model124", 18),
        ["vector124", "processor124", "reasoning124", "machine124", "learning124", "model124"],
    ),
    (
        ("vector124 processor124 reasoning124 machine124 learning124 model124", 28),
        ["vector124 processor124", "reasoning124 machine124", "learning124 model124"],
    ),
    (
        ("processor124 reasoning124 machine124 learning124 model124 token124", 6),
        ["processor124", "reasoning124", "machine124", "learning124", "model124", "token124"],
    ),
    (
        ("processor124 reasoning124 machine124 learning124 model124 token124", 10),
        ["processor124", "reasoning124", "machine124", "learning124", "model124", "token124"],
    ),
    (
        ("processor124 reasoning124 machine124 learning124 model124 token124", 18),
        ["processor124", "reasoning124", "machine124", "learning124", "model124 token124"],
    ),
    (
        ("processor124 reasoning124 machine124 learning124 model124 token124", 28),
        ["processor124 reasoning124", "machine124 learning124", "model124 token124"],
    ),
    (
        ("reasoning124 machine124 learning124 model124 token124 prompt124", 6),
        ["reasoning124", "machine124", "learning124", "model124", "token124", "prompt124"],
    ),
    (
        ("reasoning124 machine124 learning124 model124 token124 prompt124", 10),
        ["reasoning124", "machine124", "learning124", "model124", "token124", "prompt124"],
    ),
    (
        ("reasoning124 machine124 learning124 model124 token124 prompt124", 18),
        ["reasoning124", "machine124", "learning124", "model124 token124", "prompt124"],
    ),
    (
        ("reasoning124 machine124 learning124 model124 token124 prompt124", 28),
        ["reasoning124 machine124", "learning124 model124", "token124 prompt124"],
    ),
    (
        ("machine124 learning124 model124 token124 prompt124 session124", 6),
        ["machine124", "learning124", "model124", "token124", "prompt124", "session124"],
    ),
    (
        ("machine124 learning124 model124 token124 prompt124 session124", 10),
        ["machine124", "learning124", "model124", "token124", "prompt124", "session124"],
    ),
    (
        ("machine124 learning124 model124 token124 prompt124 session124", 18),
        ["machine124", "learning124", "model124 token124", "prompt124", "session124"],
    ),
    (
        ("machine124 learning124 model124 token124 prompt124 session124", 28),
        ["machine124 learning124", "model124 token124 prompt124", "session124"],
    ),
    (
        ("learning124 model124 token124 prompt124 session124 library124", 6),
        ["learning124", "model124", "token124", "prompt124", "session124", "library124"],
    ),
    (
        ("learning124 model124 token124 prompt124 session124 library124", 10),
        ["learning124", "model124", "token124", "prompt124", "session124", "library124"],
    ),
    (
        ("learning124 model124 token124 prompt124 session124 library124", 18),
        ["learning124", "model124 token124", "prompt124", "session124", "library124"],
    ),
    (
        ("learning124 model124 token124 prompt124 session124 library124", 28),
        ["learning124 model124", "token124 prompt124", "session124 library124"],
    ),
    (
        ("model124 token124 prompt124 session124 library124 service124", 6),
        ["model124", "token124", "prompt124", "session124", "library124", "service124"],
    ),
    (
        ("model124 token124 prompt124 session124 library124 service124", 10),
        ["model124", "token124", "prompt124", "session124", "library124", "service124"],
    ),
    (
        ("model124 token124 prompt124 session124 library124 service124", 18),
        ["model124 token124", "prompt124", "session124", "library124", "service124"],
    ),
    (
        ("model124 token124 prompt124 session124 library124 service124", 28),
        ["model124 token124 prompt124", "session124 library124", "service124"],
    ),
    (
        ("token124 prompt124 session124 library124 service124 gateway124", 6),
        ["token124", "prompt124", "session124", "library124", "service124", "gateway124"],
    ),
    (
        ("token124 prompt124 session124 library124 service124 gateway124", 10),
        ["token124", "prompt124", "session124", "library124", "service124", "gateway124"],
    ),
    (
        ("token124 prompt124 session124 library124 service124 gateway124", 18),
        ["token124 prompt124", "session124", "library124", "service124", "gateway124"],
    ),
    (
        ("token124 prompt124 session124 library124 service124 gateway124", 28),
        ["token124 prompt124", "session124 library124", "service124 gateway124"],
    ),
    (
        ("prompt124 session124 library124 service124 gateway124 storage124", 6),
        ["prompt124", "session124", "library124", "service124", "gateway124", "storage124"],
    ),
    (
        ("prompt124 session124 library124 service124 gateway124 storage124", 10),
        ["prompt124", "session124", "library124", "service124", "gateway124", "storage124"],
    ),
    (
        ("prompt124 session124 library124 service124 gateway124 storage124", 18),
        ["prompt124", "session124", "library124", "service124", "gateway124", "storage124"],
    ),
    (
        ("prompt124 session124 library124 service124 gateway124 storage124", 28),
        ["prompt124 session124", "library124 service124", "gateway124 storage124"],
    ),
    (
        ("session124 library124 service124 gateway124 storage124 network124", 6),
        ["session124", "library124", "service124", "gateway124", "storage124", "network124"],
    ),
    (
        ("session124 library124 service124 gateway124 storage124 network124", 10),
        ["session124", "library124", "service124", "gateway124", "storage124", "network124"],
    ),
    (
        ("session124 library124 service124 gateway124 storage124 network124", 18),
        ["session124", "library124", "service124", "gateway124", "storage124", "network124"],
    ),
    (
        ("session124 library124 service124 gateway124 storage124 network124", 28),
        ["session124 library124", "service124 gateway124", "storage124 network124"],
    ),
    (
        ("library124 service124 gateway124 storage124 network124 latency124", 6),
        ["library124", "service124", "gateway124", "storage124", "network124", "latency124"],
    ),
    (
        ("library124 service124 gateway124 storage124 network124 latency124", 10),
        ["library124", "service124", "gateway124", "storage124", "network124", "latency124"],
    ),
    (
        ("library124 service124 gateway124 storage124 network124 latency124", 18),
        ["library124", "service124", "gateway124", "storage124", "network124", "latency124"],
    ),
    (
        ("library124 service124 gateway124 storage124 network124 latency124", 28),
        ["library124 service124", "gateway124 storage124", "network124 latency124"],
    ),
    (
        ("service124 gateway124 storage124 network124 latency124 buffer124", 6),
        ["service124", "gateway124", "storage124", "network124", "latency124", "buffer124"],
    ),
    (
        ("service124 gateway124 storage124 network124 latency124 buffer124", 10),
        ["service124", "gateway124", "storage124", "network124", "latency124", "buffer124"],
    ),
    (
        ("service124 gateway124 storage124 network124 latency124 buffer124", 18),
        ["service124", "gateway124", "storage124", "network124", "latency124", "buffer124"],
    ),
    (
        ("service124 gateway124 storage124 network124 latency124 buffer124", 28),
        ["service124 gateway124", "storage124 network124", "latency124 buffer124"],
    ),
    (
        ("gateway124 storage124 network124 latency124 buffer124 queue124", 6),
        ["gateway124", "storage124", "network124", "latency124", "buffer124", "queue124"],
    ),
    (
        ("gateway124 storage124 network124 latency124 buffer124 queue124", 10),
        ["gateway124", "storage124", "network124", "latency124", "buffer124", "queue124"],
    ),
    (
        ("gateway124 storage124 network124 latency124 buffer124 queue124", 18),
        ["gateway124", "storage124", "network124", "latency124", "buffer124 queue124"],
    ),
    (
        ("gateway124 storage124 network124 latency124 buffer124 queue124", 28),
        ["gateway124 storage124", "network124 latency124", "buffer124 queue124"],
    ),
    (
        ("storage124 network124 latency124 buffer124 queue124 worker124", 6),
        ["storage124", "network124", "latency124", "buffer124", "queue124", "worker124"],
    ),
    (
        ("storage124 network124 latency124 buffer124 queue124 worker124", 10),
        ["storage124", "network124", "latency124", "buffer124", "queue124", "worker124"],
    ),
    (
        ("storage124 network124 latency124 buffer124 queue124 worker124", 18),
        ["storage124", "network124", "latency124", "buffer124 queue124", "worker124"],
    ),
    (
        ("storage124 network124 latency124 buffer124 queue124 worker124", 28),
        ["storage124 network124", "latency124 buffer124", "queue124 worker124"],
    ),
    (
        ("network124 latency124 buffer124 queue124 worker124 kernel124", 6),
        ["network124", "latency124", "buffer124", "queue124", "worker124", "kernel124"],
    ),
    (
        ("network124 latency124 buffer124 queue124 worker124 kernel124", 10),
        ["network124", "latency124", "buffer124", "queue124", "worker124", "kernel124"],
    ),
    (
        ("network124 latency124 buffer124 queue124 worker124 kernel124", 18),
        ["network124", "latency124", "buffer124 queue124", "worker124", "kernel124"],
    ),
    (
        ("network124 latency124 buffer124 queue124 worker124 kernel124", 28),
        ["network124 latency124", "buffer124 queue124 worker124", "kernel124"],
    ),
    (
        ("latency124 buffer124 queue124 worker124 kernel124 signal124", 6),
        ["latency124", "buffer124", "queue124", "worker124", "kernel124", "signal124"],
    ),
    (
        ("latency124 buffer124 queue124 worker124 kernel124 signal124", 10),
        ["latency124", "buffer124", "queue124", "worker124", "kernel124", "signal124"],
    ),
    (
        ("latency124 buffer124 queue124 worker124 kernel124 signal124", 18),
        ["latency124", "buffer124 queue124", "worker124", "kernel124", "signal124"],
    ),
    (
        ("latency124 buffer124 queue124 worker124 kernel124 signal124", 28),
        ["latency124 buffer124", "queue124 worker124 kernel124", "signal124"],
    ),
    (
        ("buffer124 queue124 worker124 kernel124 signal124 packet124", 6),
        ["buffer124", "queue124", "worker124", "kernel124", "signal124", "packet124"],
    ),
    (
        ("buffer124 queue124 worker124 kernel124 signal124 packet124", 10),
        ["buffer124", "queue124", "worker124", "kernel124", "signal124", "packet124"],
    ),
    (
        ("buffer124 queue124 worker124 kernel124 signal124 packet124", 18),
        ["buffer124 queue124", "worker124", "kernel124", "signal124", "packet124"],
    ),
    (
        ("buffer124 queue124 worker124 kernel124 signal124 packet124", 28),
        ["buffer124 queue124 worker124", "kernel124 signal124", "packet124"],
    ),
    (
        ("queue124 worker124 kernel124 signal124 packet124 router124", 6),
        ["queue124", "worker124", "kernel124", "signal124", "packet124", "router124"],
    ),
    (
        ("queue124 worker124 kernel124 signal124 packet124 router124", 10),
        ["queue124", "worker124", "kernel124", "signal124", "packet124", "router124"],
    ),
    (
        ("queue124 worker124 kernel124 signal124 packet124 router124", 18),
        ["queue124 worker124", "kernel124", "signal124", "packet124", "router124"],
    ),
    (
        ("queue124 worker124 kernel124 signal124 packet124 router124", 28),
        ["queue124 worker124 kernel124", "signal124 packet124", "router124"],
    ),
    (
        ("worker124 kernel124 signal124 packet124 router124 cluster124", 6),
        ["worker124", "kernel124", "signal124", "packet124", "router124", "cluster124"],
    ),
    (
        ("worker124 kernel124 signal124 packet124 router124 cluster124", 10),
        ["worker124", "kernel124", "signal124", "packet124", "router124", "cluster124"],
    ),
    (
        ("worker124 kernel124 signal124 packet124 router124 cluster124", 18),
        ["worker124", "kernel124", "signal124", "packet124", "router124", "cluster124"],
    ),
    (
        ("worker124 kernel124 signal124 packet124 router124 cluster124", 28),
        ["worker124 kernel124", "signal124 packet124", "router124 cluster124"],
    ),
    (
        ("kernel124 signal124 packet124 router124 cluster124 mirror124", 6),
        ["kernel124", "signal124", "packet124", "router124", "cluster124", "mirror124"],
    ),
    (
        ("kernel124 signal124 packet124 router124 cluster124 mirror124", 10),
        ["kernel124", "signal124", "packet124", "router124", "cluster124", "mirror124"],
    ),
    (
        ("kernel124 signal124 packet124 router124 cluster124 mirror124", 18),
        ["kernel124", "signal124", "packet124", "router124", "cluster124", "mirror124"],
    ),
    (
        ("kernel124 signal124 packet124 router124 cluster124 mirror124", 28),
        ["kernel124 signal124", "packet124 router124", "cluster124 mirror124"],
    ),
    (
        ("signal124 packet124 router124 cluster124 mirror124 filter124", 6),
        ["signal124", "packet124", "router124", "cluster124", "mirror124", "filter124"],
    ),
    (
        ("signal124 packet124 router124 cluster124 mirror124 filter124", 10),
        ["signal124", "packet124", "router124", "cluster124", "mirror124", "filter124"],
    ),
    (
        ("signal124 packet124 router124 cluster124 mirror124 filter124", 18),
        ["signal124", "packet124", "router124", "cluster124", "mirror124", "filter124"],
    ),
    (
        ("signal124 packet124 router124 cluster124 mirror124 filter124", 28),
        ["signal124 packet124", "router124 cluster124", "mirror124 filter124"],
    ),
    (
        ("packet124 router124 cluster124 mirror124 filter124 ranking124", 6),
        ["packet124", "router124", "cluster124", "mirror124", "filter124", "ranking124"],
    ),
    (
        ("packet124 router124 cluster124 mirror124 filter124 ranking124", 10),
        ["packet124", "router124", "cluster124", "mirror124", "filter124", "ranking124"],
    ),
    (
        ("packet124 router124 cluster124 mirror124 filter124 ranking124", 18),
        ["packet124", "router124", "cluster124", "mirror124", "filter124", "ranking124"],
    ),
    (
        ("packet124 router124 cluster124 mirror124 filter124 ranking124", 28),
        ["packet124 router124", "cluster124 mirror124", "filter124 ranking124"],
    ),
    (
        ("router124 cluster124 mirror124 filter124 ranking124 encoding124", 6),
        ["router124", "cluster124", "mirror124", "filter124", "ranking124", "encoding124"],
    ),
    (
        ("router124 cluster124 mirror124 filter124 ranking124 encoding124", 10),
        ["router124", "cluster124", "mirror124", "filter124", "ranking124", "encoding124"],
    ),
    (
        ("router124 cluster124 mirror124 filter124 ranking124 encoding124", 18),
        ["router124", "cluster124", "mirror124", "filter124", "ranking124", "encoding124"],
    ),
    (
        ("router124 cluster124 mirror124 filter124 ranking124 encoding124", 28),
        ["router124 cluster124", "mirror124 filter124", "ranking124 encoding124"],
    ),
    (
        ("cluster124 mirror124 filter124 ranking124 encoding124 mapping124", 6),
        ["cluster124", "mirror124", "filter124", "ranking124", "encoding124", "mapping124"],
    ),
    (
        ("cluster124 mirror124 filter124 ranking124 encoding124 mapping124", 10),
        ["cluster124", "mirror124", "filter124", "ranking124", "encoding124", "mapping124"],
    ),
    (
        ("cluster124 mirror124 filter124 ranking124 encoding124 mapping124", 18),
        ["cluster124", "mirror124", "filter124", "ranking124", "encoding124", "mapping124"],
    ),
    (
        ("cluster124 mirror124 filter124 ranking124 encoding124 mapping124", 28),
        ["cluster124 mirror124", "filter124 ranking124", "encoding124 mapping124"],
    ),
    (
        ("mirror124 filter124 ranking124 encoding124 mapping124 record124", 6),
        ["mirror124", "filter124", "ranking124", "encoding124", "mapping124", "record124"],
    ),
    (
        ("mirror124 filter124 ranking124 encoding124 mapping124 record124", 10),
        ["mirror124", "filter124", "ranking124", "encoding124", "mapping124", "record124"],
    ),
    (
        ("mirror124 filter124 ranking124 encoding124 mapping124 record124", 18),
        ["mirror124", "filter124", "ranking124", "encoding124", "mapping124", "record124"],
    ),
    (
        ("mirror124 filter124 ranking124 encoding124 mapping124 record124", 28),
        ["mirror124 filter124", "ranking124 encoding124", "mapping124 record124"],
    ),
    (
        ("filter124 ranking124 encoding124 mapping124 record124 candle124", 6),
        ["filter124", "ranking124", "encoding124", "mapping124", "record124", "candle124"],
    ),
    (
        ("filter124 ranking124 encoding124 mapping124 record124 candle124", 10),
        ["filter124", "ranking124", "encoding124", "mapping124", "record124", "candle124"],
    ),
    (
        ("filter124 ranking124 encoding124 mapping124 record124 candle124", 18),
        ["filter124", "ranking124", "encoding124", "mapping124", "record124", "candle124"],
    ),
    (
        ("filter124 ranking124 encoding124 mapping124 record124 candle124", 28),
        ["filter124 ranking124", "encoding124 mapping124", "record124 candle124"],
    ),
    (
        ("ranking124 encoding124 mapping124 record124 candle124 thread124", 6),
        ["ranking124", "encoding124", "mapping124", "record124", "candle124", "thread124"],
    ),
    (
        ("ranking124 encoding124 mapping124 record124 candle124 thread124", 10),
        ["ranking124", "encoding124", "mapping124", "record124", "candle124", "thread124"],
    ),
    (
        ("ranking124 encoding124 mapping124 record124 candle124 thread124", 18),
        ["ranking124", "encoding124", "mapping124", "record124", "candle124", "thread124"],
    ),
    (
        ("ranking124 encoding124 mapping124 record124 candle124 thread124", 28),
        ["ranking124 encoding124", "mapping124 record124", "candle124 thread124"],
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
