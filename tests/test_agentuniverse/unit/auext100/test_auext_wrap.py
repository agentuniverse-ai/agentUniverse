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
        ("round 100: the quick brown fox jumps over the lazy dog", 4),
        ["round", "100:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", 8),
        ["round", "100: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", 12),
        ["round 100:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", 16),
        ["round 100: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", 24),
        ["round 100: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 100: the quick brown fox jumps over the lazy dog", 32),
        ["round 100: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", 4),
        ["round", "100:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", 8),
        ["round", "100:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", 12),
        ["round 100:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", 16),
        ["round 100:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", 24),
        ["round 100: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 100: agentuniverse is a framework for multi agents", 32),
        ["round 100: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", 4),
        ["round", "100:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", 8),
        ["round", "100:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", 12),
        ["round 100:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", 16),
        ["round 100:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", 24),
        ["round 100: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 100: knowledge stored as vectors enables retrieval", 32),
        ["round 100: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 100: the processor reads the record then stops", 4),
        ["round", "100:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 100: the processor reads the record then stops", 8),
        ["round", "100: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 100: the processor reads the record then stops", 12),
        ["round 100:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 100: the processor reads the record then stops", 16),
        ["round 100: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 100: the processor reads the record then stops", 24),
        ["round 100: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 100: the processor reads the record then stops", 32),
        ["round 100: the processor reads", "the record then stops"],
    ),
    (
        ("round 100: a worker pulls the next task from the queue", 4),
        ["round", "100:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 100: a worker pulls the next task from the queue", 8),
        ["round", "100: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 100: a worker pulls the next task from the queue", 12),
        ["round 100: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 100: a worker pulls the next task from the queue", 16),
        ["round 100: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 100: a worker pulls the next task from the queue", 24),
        ["round 100: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 100: a worker pulls the next task from the queue", 32),
        ["round 100: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 100: signals travel through the network layer", 4),
        ["round", "100:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 100: signals travel through the network layer", 8),
        ["round", "100:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 100: signals travel through the network layer", 12),
        ["round 100:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 100: signals travel through the network layer", 16),
        ["round 100:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 100: signals travel through the network layer", 24),
        ["round 100: signals", "travel through the", "network layer"],
    ),
    (
        ("round 100: signals travel through the network layer", 32),
        ["round 100: signals travel", "through the network layer"],
    ),
    (
        ("round 100: the gateway routes each request by policy", 4),
        ["round", "100:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 100: the gateway routes each request by policy", 8),
        ["round", "100: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 100: the gateway routes each request by policy", 12),
        ["round 100:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 100: the gateway routes each request by policy", 16),
        ["round 100: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 100: the gateway routes each request by policy", 24),
        ["round 100: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 100: the gateway routes each request by policy", 32),
        ["round 100: the gateway routes", "each request by policy"],
    ),
    (
        ("round 100: memory grows until the buffer is full", 4),
        ["round", "100:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 100: memory grows until the buffer is full", 8),
        ["round", "100:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 100: memory grows until the buffer is full", 12),
        ["round 100:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 100: memory grows until the buffer is full", 16),
        ["round 100:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 100: memory grows until the buffer is full", 24), ["round 100: memory grows", "until the buffer is full"]),
    (("round 100: memory grows until the buffer is full", 32), ["round 100: memory grows until", "the buffer is full"]),
    (
        ("round 100: the cluster mirrors every packet twice", 4),
        ["round", "100:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 100: the cluster mirrors every packet twice", 8),
        ["round", "100: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 100: the cluster mirrors every packet twice", 12),
        ["round 100:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 100: the cluster mirrors every packet twice", 16),
        ["round 100: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 100: the cluster mirrors every packet twice", 24),
        ["round 100: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 100: the cluster mirrors every packet twice", 32),
        ["round 100: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", 4),
        ["round", "100:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", 8),
        ["round", "100:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", 12),
        ["round 100:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", 16),
        ["round 100:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", 24),
        ["round 100: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 100: ranking uses tokens learned from the corpus", 32),
        ["round 100: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 100: a long session ends when the candle dies", 4),
        ["round", "100:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 100: a long session ends when the candle dies", 8),
        ["round", "100: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 100: a long session ends when the candle dies", 12),
        ["round 100: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 100: a long session ends when the candle dies", 16),
        ["round 100: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 100: a long session ends when the candle dies", 24),
        ["round 100: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 100: a long session ends when the candle dies", 32),
        ["round 100: a long session ends", "when the candle dies"],
    ),
    (
        ("round 100: encode the prompt then map the result", 4),
        ["round", "100:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 100: encode the prompt then map the result", 8),
        ["round", "100:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 100: encode the prompt then map the result", 12),
        ["round 100:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 100: encode the prompt then map the result", 16),
        ["round 100:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 100: encode the prompt then map the result", 24),
        ["round 100: encode the", "prompt then map the", "result"],
    ),
    (("round 100: encode the prompt then map the result", 32), ["round 100: encode the prompt", "then map the result"]),
    (
        ("round 100: the kernel wakes the worker at dawn", 4),
        ["round", "100:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 100: the kernel wakes the worker at dawn", 8),
        ["round", "100: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 100: the kernel wakes the worker at dawn", 12),
        ["round 100:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 100: the kernel wakes the worker at dawn", 16), ["round 100: the", "kernel wakes the", "worker at dawn"]),
    (("round 100: the kernel wakes the worker at dawn", 24), ["round 100: the kernel", "wakes the worker at dawn"]),
    (("round 100: the kernel wakes the worker at dawn", 32), ["round 100: the kernel wakes the", "worker at dawn"]),
    (
        ("round 100: service latency drops after the patch", 4),
        ["round", "100:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 100: service latency drops after the patch", 8),
        ["round", "100:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 100: service latency drops after the patch", 12),
        ["round 100:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 100: service latency drops after the patch", 16),
        ["round 100:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 100: service latency drops after the patch", 24),
        ["round 100: service", "latency drops after the", "patch"],
    ),
    (("round 100: service latency drops after the patch", 32), ["round 100: service latency drops", "after the patch"]),
    (
        ("round 100: the library caches every vector it sees", 4),
        ["round", "100:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 100: the library caches every vector it sees", 8),
        ["round", "100: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 100: the library caches every vector it sees", 12),
        ["round 100:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 100: the library caches every vector it sees", 16),
        ["round 100: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 100: the library caches every vector it sees", 24),
        ["round 100: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 100: the library caches every vector it sees", 32),
        ["round 100: the library caches", "every vector it sees"],
    ),
    (
        ("round 100: agents argue then the debate resolves", 4),
        ["round", "100:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 100: agents argue then the debate resolves", 8),
        ["round", "100:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 100: agents argue then the debate resolves", 12),
        ["round 100:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 100: agents argue then the debate resolves", 16),
        ["round 100:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 100: agents argue then the debate resolves", 24), ["round 100: agents argue", "then the debate resolves"]),
    (("round 100: agents argue then the debate resolves", 32), ["round 100: agents argue then the", "debate resolves"]),
    (
        ("round 100: the filter keeps only strong matches", 4),
        ["round", "100:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 100: the filter keeps only strong matches", 8),
        ["round", "100: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 100: the filter keeps only strong matches", 12),
        ["round 100:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 100: the filter keeps only strong matches", 16),
        ["round 100: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 100: the filter keeps only strong matches", 24),
        ["round 100: the filter", "keeps only strong", "matches"],
    ),
    (("round 100: the filter keeps only strong matches", 32), ["round 100: the filter keeps only", "strong matches"]),
    (
        ("round 100: the model answers with a short reply", 4),
        ["round", "100:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 100: the model answers with a short reply", 8),
        ["round", "100: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 100: the model answers with a short reply", 12),
        ["round 100:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 100: the model answers with a short reply", 16),
        ["round 100: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 100: the model answers with a short reply", 24),
        ["round 100: the model", "answers with a short", "reply"],
    ),
    (("round 100: the model answers with a short reply", 32), ["round 100: the model answers", "with a short reply"]),
    (
        ("round 100: the recorder stores the reasoning trace", 4),
        ["round", "100:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 100: the recorder stores the reasoning trace", 8),
        ["round", "100: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 100: the recorder stores the reasoning trace", 12),
        ["round 100:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 100: the recorder stores the reasoning trace", 16),
        ["round 100: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 100: the recorder stores the reasoning trace", 24),
        ["round 100: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 100: the recorder stores the reasoning trace", 32),
        ["round 100: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 100: the angel watches the processor run", 4),
        ["round", "100:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 100: the angel watches the processor run", 8),
        ["round", "100: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 100: the angel watches the processor run", 12),
        ["round 100:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 100: the angel watches the processor run", 16),
        ["round 100: the", "angel watches", "the processor", "run"],
    ),
    (("round 100: the angel watches the processor run", 24), ["round 100: the angel", "watches the processor", "run"]),
    (("round 100: the angel watches the processor run", 32), ["round 100: the angel watches the", "processor run"]),
    (
        ("round 100: angle of the vector decides the match", 4),
        ["round", "100:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 100: angle of the vector decides the match", 8),
        ["round", "100:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 100: angle of the vector decides the match", 12),
        ["round 100:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 100: angle of the vector decides the match", 16),
        ["round 100: angle", "of the vector", "decides the", "match"],
    ),
    (("round 100: angle of the vector decides the match", 24), ["round 100: angle of the", "vector decides the match"]),
    (("round 100: angle of the vector decides the match", 32), ["round 100: angle of the vector", "decides the match"]),
    (
        ("round 100: the candle burns twice as long at night", 4),
        ["round", "100:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 100: the candle burns twice as long at night", 8),
        ["round", "100: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 100: the candle burns twice as long at night", 12),
        ["round 100:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 100: the candle burns twice as long at night", 16),
        ["round 100: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 100: the candle burns twice as long at night", 24),
        ["round 100: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 100: the candle burns twice as long at night", 32),
        ["round 100: the candle burns", "twice as long at night"],
    ),
    (
        ("round 100: a mirror of the universe in one line", 4),
        ["round", "100:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 100: a mirror of the universe in one line", 8),
        ["round", "100: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 100: a mirror of the universe in one line", 12),
        ["round 100: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 100: a mirror of the universe in one line", 16),
        ["round 100: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 100: a mirror of the universe in one line", 24), ["round 100: a mirror of", "the universe in one line"]),
    (("round 100: a mirror of the universe in one line", 32), ["round 100: a mirror of the", "universe in one line"]),
    (
        ("round 100: the queue drains before the storm", 4),
        ["round", "100:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 100: the queue drains before the storm", 8),
        ["round", "100: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 100: the queue drains before the storm", 12),
        ["round 100:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 100: the queue drains before the storm", 16), ["round 100: the", "queue drains", "before the storm"]),
    (("round 100: the queue drains before the storm", 24), ["round 100: the queue", "drains before the storm"]),
    (("round 100: the queue drains before the storm", 32), ["round 100: the queue drains", "before the storm"]),
    (
        ("kitten100 sitting100 agent100 angle100 universe100 memory100", 6),
        ["kitten100", "sitting100", "agent100", "angle100", "universe100", "memory100"],
    ),
    (
        ("kitten100 sitting100 agent100 angle100 universe100 memory100", 10),
        ["kitten100", "sitting100", "agent100", "angle100", "universe100", "memory100"],
    ),
    (
        ("kitten100 sitting100 agent100 angle100 universe100 memory100", 18),
        ["kitten100", "sitting100", "agent100 angle100", "universe100", "memory100"],
    ),
    (
        ("kitten100 sitting100 agent100 angle100 universe100 memory100", 28),
        ["kitten100 sitting100", "agent100 angle100", "universe100 memory100"],
    ),
    (
        ("sitting100 agent100 angle100 universe100 memory100 stream100", 6),
        ["sitting100", "agent100", "angle100", "universe100", "memory100", "stream100"],
    ),
    (
        ("sitting100 agent100 angle100 universe100 memory100 stream100", 10),
        ["sitting100", "agent100", "angle100", "universe100", "memory100", "stream100"],
    ),
    (
        ("sitting100 agent100 angle100 universe100 memory100 stream100", 18),
        ["sitting100", "agent100 angle100", "universe100", "memory100", "stream100"],
    ),
    (
        ("sitting100 agent100 angle100 universe100 memory100 stream100", 28),
        ["sitting100 agent100 angle100", "universe100 memory100", "stream100"],
    ),
    (
        ("agent100 angle100 universe100 memory100 stream100 context100", 6),
        ["agent100", "angle100", "universe100", "memory100", "stream100", "context100"],
    ),
    (
        ("agent100 angle100 universe100 memory100 stream100 context100", 10),
        ["agent100", "angle100", "universe100", "memory100", "stream100", "context100"],
    ),
    (
        ("agent100 angle100 universe100 memory100 stream100 context100", 18),
        ["agent100 angle100", "universe100", "memory100", "stream100", "context100"],
    ),
    (
        ("agent100 angle100 universe100 memory100 stream100 context100", 28),
        ["agent100 angle100", "universe100 memory100", "stream100 context100"],
    ),
    (
        ("angle100 universe100 memory100 stream100 context100 knowledge100", 6),
        ["angle100", "universe100", "memory100", "stream100", "context100", "knowledge100"],
    ),
    (
        ("angle100 universe100 memory100 stream100 context100 knowledge100", 10),
        ["angle100", "universe100", "memory100", "stream100", "context100", "knowledge100"],
    ),
    (
        ("angle100 universe100 memory100 stream100 context100 knowledge100", 18),
        ["angle100", "universe100", "memory100", "stream100", "context100", "knowledge100"],
    ),
    (
        ("angle100 universe100 memory100 stream100 context100 knowledge100", 28),
        ["angle100 universe100", "memory100 stream100", "context100 knowledge100"],
    ),
    (
        ("universe100 memory100 stream100 context100 knowledge100 vector100", 6),
        ["universe100", "memory100", "stream100", "context100", "knowledge100", "vector100"],
    ),
    (
        ("universe100 memory100 stream100 context100 knowledge100 vector100", 10),
        ["universe100", "memory100", "stream100", "context100", "knowledge100", "vector100"],
    ),
    (
        ("universe100 memory100 stream100 context100 knowledge100 vector100", 18),
        ["universe100", "memory100", "stream100", "context100", "knowledge100", "vector100"],
    ),
    (
        ("universe100 memory100 stream100 context100 knowledge100 vector100", 28),
        ["universe100 memory100", "stream100 context100", "knowledge100 vector100"],
    ),
    (
        ("memory100 stream100 context100 knowledge100 vector100 processor100", 6),
        ["memory100", "stream100", "context100", "knowledge100", "vector100", "processor100"],
    ),
    (
        ("memory100 stream100 context100 knowledge100 vector100 processor100", 10),
        ["memory100", "stream100", "context100", "knowledge100", "vector100", "processor100"],
    ),
    (
        ("memory100 stream100 context100 knowledge100 vector100 processor100", 18),
        ["memory100", "stream100", "context100", "knowledge100", "vector100", "processor100"],
    ),
    (
        ("memory100 stream100 context100 knowledge100 vector100 processor100", 28),
        ["memory100 stream100", "context100 knowledge100", "vector100 processor100"],
    ),
    (
        ("stream100 context100 knowledge100 vector100 processor100 reasoning100", 6),
        ["stream100", "context100", "knowledge100", "vector100", "processor100", "reasoning100"],
    ),
    (
        ("stream100 context100 knowledge100 vector100 processor100 reasoning100", 10),
        ["stream100", "context100", "knowledge100", "vector100", "processor100", "reasoning100"],
    ),
    (
        ("stream100 context100 knowledge100 vector100 processor100 reasoning100", 18),
        ["stream100", "context100", "knowledge100", "vector100", "processor100", "reasoning100"],
    ),
    (
        ("stream100 context100 knowledge100 vector100 processor100 reasoning100", 28),
        ["stream100 context100", "knowledge100 vector100", "processor100 reasoning100"],
    ),
    (
        ("context100 knowledge100 vector100 processor100 reasoning100 machine100", 6),
        ["context100", "knowledge100", "vector100", "processor100", "reasoning100", "machine100"],
    ),
    (
        ("context100 knowledge100 vector100 processor100 reasoning100 machine100", 10),
        ["context100", "knowledge100", "vector100", "processor100", "reasoning100", "machine100"],
    ),
    (
        ("context100 knowledge100 vector100 processor100 reasoning100 machine100", 18),
        ["context100", "knowledge100", "vector100", "processor100", "reasoning100", "machine100"],
    ),
    (
        ("context100 knowledge100 vector100 processor100 reasoning100 machine100", 28),
        ["context100 knowledge100", "vector100 processor100", "reasoning100 machine100"],
    ),
    (
        ("knowledge100 vector100 processor100 reasoning100 machine100 learning100", 6),
        ["knowledge100", "vector100", "processor100", "reasoning100", "machine100", "learning100"],
    ),
    (
        ("knowledge100 vector100 processor100 reasoning100 machine100 learning100", 10),
        ["knowledge100", "vector100", "processor100", "reasoning100", "machine100", "learning100"],
    ),
    (
        ("knowledge100 vector100 processor100 reasoning100 machine100 learning100", 18),
        ["knowledge100", "vector100", "processor100", "reasoning100", "machine100", "learning100"],
    ),
    (
        ("knowledge100 vector100 processor100 reasoning100 machine100 learning100", 28),
        ["knowledge100 vector100", "processor100 reasoning100", "machine100 learning100"],
    ),
    (
        ("vector100 processor100 reasoning100 machine100 learning100 model100", 6),
        ["vector100", "processor100", "reasoning100", "machine100", "learning100", "model100"],
    ),
    (
        ("vector100 processor100 reasoning100 machine100 learning100 model100", 10),
        ["vector100", "processor100", "reasoning100", "machine100", "learning100", "model100"],
    ),
    (
        ("vector100 processor100 reasoning100 machine100 learning100 model100", 18),
        ["vector100", "processor100", "reasoning100", "machine100", "learning100", "model100"],
    ),
    (
        ("vector100 processor100 reasoning100 machine100 learning100 model100", 28),
        ["vector100 processor100", "reasoning100 machine100", "learning100 model100"],
    ),
    (
        ("processor100 reasoning100 machine100 learning100 model100 token100", 6),
        ["processor100", "reasoning100", "machine100", "learning100", "model100", "token100"],
    ),
    (
        ("processor100 reasoning100 machine100 learning100 model100 token100", 10),
        ["processor100", "reasoning100", "machine100", "learning100", "model100", "token100"],
    ),
    (
        ("processor100 reasoning100 machine100 learning100 model100 token100", 18),
        ["processor100", "reasoning100", "machine100", "learning100", "model100 token100"],
    ),
    (
        ("processor100 reasoning100 machine100 learning100 model100 token100", 28),
        ["processor100 reasoning100", "machine100 learning100", "model100 token100"],
    ),
    (
        ("reasoning100 machine100 learning100 model100 token100 prompt100", 6),
        ["reasoning100", "machine100", "learning100", "model100", "token100", "prompt100"],
    ),
    (
        ("reasoning100 machine100 learning100 model100 token100 prompt100", 10),
        ["reasoning100", "machine100", "learning100", "model100", "token100", "prompt100"],
    ),
    (
        ("reasoning100 machine100 learning100 model100 token100 prompt100", 18),
        ["reasoning100", "machine100", "learning100", "model100 token100", "prompt100"],
    ),
    (
        ("reasoning100 machine100 learning100 model100 token100 prompt100", 28),
        ["reasoning100 machine100", "learning100 model100", "token100 prompt100"],
    ),
    (
        ("machine100 learning100 model100 token100 prompt100 session100", 6),
        ["machine100", "learning100", "model100", "token100", "prompt100", "session100"],
    ),
    (
        ("machine100 learning100 model100 token100 prompt100 session100", 10),
        ["machine100", "learning100", "model100", "token100", "prompt100", "session100"],
    ),
    (
        ("machine100 learning100 model100 token100 prompt100 session100", 18),
        ["machine100", "learning100", "model100 token100", "prompt100", "session100"],
    ),
    (
        ("machine100 learning100 model100 token100 prompt100 session100", 28),
        ["machine100 learning100", "model100 token100 prompt100", "session100"],
    ),
    (
        ("learning100 model100 token100 prompt100 session100 library100", 6),
        ["learning100", "model100", "token100", "prompt100", "session100", "library100"],
    ),
    (
        ("learning100 model100 token100 prompt100 session100 library100", 10),
        ["learning100", "model100", "token100", "prompt100", "session100", "library100"],
    ),
    (
        ("learning100 model100 token100 prompt100 session100 library100", 18),
        ["learning100", "model100 token100", "prompt100", "session100", "library100"],
    ),
    (
        ("learning100 model100 token100 prompt100 session100 library100", 28),
        ["learning100 model100", "token100 prompt100", "session100 library100"],
    ),
    (
        ("model100 token100 prompt100 session100 library100 service100", 6),
        ["model100", "token100", "prompt100", "session100", "library100", "service100"],
    ),
    (
        ("model100 token100 prompt100 session100 library100 service100", 10),
        ["model100", "token100", "prompt100", "session100", "library100", "service100"],
    ),
    (
        ("model100 token100 prompt100 session100 library100 service100", 18),
        ["model100 token100", "prompt100", "session100", "library100", "service100"],
    ),
    (
        ("model100 token100 prompt100 session100 library100 service100", 28),
        ["model100 token100 prompt100", "session100 library100", "service100"],
    ),
    (
        ("token100 prompt100 session100 library100 service100 gateway100", 6),
        ["token100", "prompt100", "session100", "library100", "service100", "gateway100"],
    ),
    (
        ("token100 prompt100 session100 library100 service100 gateway100", 10),
        ["token100", "prompt100", "session100", "library100", "service100", "gateway100"],
    ),
    (
        ("token100 prompt100 session100 library100 service100 gateway100", 18),
        ["token100 prompt100", "session100", "library100", "service100", "gateway100"],
    ),
    (
        ("token100 prompt100 session100 library100 service100 gateway100", 28),
        ["token100 prompt100", "session100 library100", "service100 gateway100"],
    ),
    (
        ("prompt100 session100 library100 service100 gateway100 storage100", 6),
        ["prompt100", "session100", "library100", "service100", "gateway100", "storage100"],
    ),
    (
        ("prompt100 session100 library100 service100 gateway100 storage100", 10),
        ["prompt100", "session100", "library100", "service100", "gateway100", "storage100"],
    ),
    (
        ("prompt100 session100 library100 service100 gateway100 storage100", 18),
        ["prompt100", "session100", "library100", "service100", "gateway100", "storage100"],
    ),
    (
        ("prompt100 session100 library100 service100 gateway100 storage100", 28),
        ["prompt100 session100", "library100 service100", "gateway100 storage100"],
    ),
    (
        ("session100 library100 service100 gateway100 storage100 network100", 6),
        ["session100", "library100", "service100", "gateway100", "storage100", "network100"],
    ),
    (
        ("session100 library100 service100 gateway100 storage100 network100", 10),
        ["session100", "library100", "service100", "gateway100", "storage100", "network100"],
    ),
    (
        ("session100 library100 service100 gateway100 storage100 network100", 18),
        ["session100", "library100", "service100", "gateway100", "storage100", "network100"],
    ),
    (
        ("session100 library100 service100 gateway100 storage100 network100", 28),
        ["session100 library100", "service100 gateway100", "storage100 network100"],
    ),
    (
        ("library100 service100 gateway100 storage100 network100 latency100", 6),
        ["library100", "service100", "gateway100", "storage100", "network100", "latency100"],
    ),
    (
        ("library100 service100 gateway100 storage100 network100 latency100", 10),
        ["library100", "service100", "gateway100", "storage100", "network100", "latency100"],
    ),
    (
        ("library100 service100 gateway100 storage100 network100 latency100", 18),
        ["library100", "service100", "gateway100", "storage100", "network100", "latency100"],
    ),
    (
        ("library100 service100 gateway100 storage100 network100 latency100", 28),
        ["library100 service100", "gateway100 storage100", "network100 latency100"],
    ),
    (
        ("service100 gateway100 storage100 network100 latency100 buffer100", 6),
        ["service100", "gateway100", "storage100", "network100", "latency100", "buffer100"],
    ),
    (
        ("service100 gateway100 storage100 network100 latency100 buffer100", 10),
        ["service100", "gateway100", "storage100", "network100", "latency100", "buffer100"],
    ),
    (
        ("service100 gateway100 storage100 network100 latency100 buffer100", 18),
        ["service100", "gateway100", "storage100", "network100", "latency100", "buffer100"],
    ),
    (
        ("service100 gateway100 storage100 network100 latency100 buffer100", 28),
        ["service100 gateway100", "storage100 network100", "latency100 buffer100"],
    ),
    (
        ("gateway100 storage100 network100 latency100 buffer100 queue100", 6),
        ["gateway100", "storage100", "network100", "latency100", "buffer100", "queue100"],
    ),
    (
        ("gateway100 storage100 network100 latency100 buffer100 queue100", 10),
        ["gateway100", "storage100", "network100", "latency100", "buffer100", "queue100"],
    ),
    (
        ("gateway100 storage100 network100 latency100 buffer100 queue100", 18),
        ["gateway100", "storage100", "network100", "latency100", "buffer100 queue100"],
    ),
    (
        ("gateway100 storage100 network100 latency100 buffer100 queue100", 28),
        ["gateway100 storage100", "network100 latency100", "buffer100 queue100"],
    ),
    (
        ("storage100 network100 latency100 buffer100 queue100 worker100", 6),
        ["storage100", "network100", "latency100", "buffer100", "queue100", "worker100"],
    ),
    (
        ("storage100 network100 latency100 buffer100 queue100 worker100", 10),
        ["storage100", "network100", "latency100", "buffer100", "queue100", "worker100"],
    ),
    (
        ("storage100 network100 latency100 buffer100 queue100 worker100", 18),
        ["storage100", "network100", "latency100", "buffer100 queue100", "worker100"],
    ),
    (
        ("storage100 network100 latency100 buffer100 queue100 worker100", 28),
        ["storage100 network100", "latency100 buffer100", "queue100 worker100"],
    ),
    (
        ("network100 latency100 buffer100 queue100 worker100 kernel100", 6),
        ["network100", "latency100", "buffer100", "queue100", "worker100", "kernel100"],
    ),
    (
        ("network100 latency100 buffer100 queue100 worker100 kernel100", 10),
        ["network100", "latency100", "buffer100", "queue100", "worker100", "kernel100"],
    ),
    (
        ("network100 latency100 buffer100 queue100 worker100 kernel100", 18),
        ["network100", "latency100", "buffer100 queue100", "worker100", "kernel100"],
    ),
    (
        ("network100 latency100 buffer100 queue100 worker100 kernel100", 28),
        ["network100 latency100", "buffer100 queue100 worker100", "kernel100"],
    ),
    (
        ("latency100 buffer100 queue100 worker100 kernel100 signal100", 6),
        ["latency100", "buffer100", "queue100", "worker100", "kernel100", "signal100"],
    ),
    (
        ("latency100 buffer100 queue100 worker100 kernel100 signal100", 10),
        ["latency100", "buffer100", "queue100", "worker100", "kernel100", "signal100"],
    ),
    (
        ("latency100 buffer100 queue100 worker100 kernel100 signal100", 18),
        ["latency100", "buffer100 queue100", "worker100", "kernel100", "signal100"],
    ),
    (
        ("latency100 buffer100 queue100 worker100 kernel100 signal100", 28),
        ["latency100 buffer100", "queue100 worker100 kernel100", "signal100"],
    ),
    (
        ("buffer100 queue100 worker100 kernel100 signal100 packet100", 6),
        ["buffer100", "queue100", "worker100", "kernel100", "signal100", "packet100"],
    ),
    (
        ("buffer100 queue100 worker100 kernel100 signal100 packet100", 10),
        ["buffer100", "queue100", "worker100", "kernel100", "signal100", "packet100"],
    ),
    (
        ("buffer100 queue100 worker100 kernel100 signal100 packet100", 18),
        ["buffer100 queue100", "worker100", "kernel100", "signal100", "packet100"],
    ),
    (
        ("buffer100 queue100 worker100 kernel100 signal100 packet100", 28),
        ["buffer100 queue100 worker100", "kernel100 signal100", "packet100"],
    ),
    (
        ("queue100 worker100 kernel100 signal100 packet100 router100", 6),
        ["queue100", "worker100", "kernel100", "signal100", "packet100", "router100"],
    ),
    (
        ("queue100 worker100 kernel100 signal100 packet100 router100", 10),
        ["queue100", "worker100", "kernel100", "signal100", "packet100", "router100"],
    ),
    (
        ("queue100 worker100 kernel100 signal100 packet100 router100", 18),
        ["queue100 worker100", "kernel100", "signal100", "packet100", "router100"],
    ),
    (
        ("queue100 worker100 kernel100 signal100 packet100 router100", 28),
        ["queue100 worker100 kernel100", "signal100 packet100", "router100"],
    ),
    (
        ("worker100 kernel100 signal100 packet100 router100 cluster100", 6),
        ["worker100", "kernel100", "signal100", "packet100", "router100", "cluster100"],
    ),
    (
        ("worker100 kernel100 signal100 packet100 router100 cluster100", 10),
        ["worker100", "kernel100", "signal100", "packet100", "router100", "cluster100"],
    ),
    (
        ("worker100 kernel100 signal100 packet100 router100 cluster100", 18),
        ["worker100", "kernel100", "signal100", "packet100", "router100", "cluster100"],
    ),
    (
        ("worker100 kernel100 signal100 packet100 router100 cluster100", 28),
        ["worker100 kernel100", "signal100 packet100", "router100 cluster100"],
    ),
    (
        ("kernel100 signal100 packet100 router100 cluster100 mirror100", 6),
        ["kernel100", "signal100", "packet100", "router100", "cluster100", "mirror100"],
    ),
    (
        ("kernel100 signal100 packet100 router100 cluster100 mirror100", 10),
        ["kernel100", "signal100", "packet100", "router100", "cluster100", "mirror100"],
    ),
    (
        ("kernel100 signal100 packet100 router100 cluster100 mirror100", 18),
        ["kernel100", "signal100", "packet100", "router100", "cluster100", "mirror100"],
    ),
    (
        ("kernel100 signal100 packet100 router100 cluster100 mirror100", 28),
        ["kernel100 signal100", "packet100 router100", "cluster100 mirror100"],
    ),
    (
        ("signal100 packet100 router100 cluster100 mirror100 filter100", 6),
        ["signal100", "packet100", "router100", "cluster100", "mirror100", "filter100"],
    ),
    (
        ("signal100 packet100 router100 cluster100 mirror100 filter100", 10),
        ["signal100", "packet100", "router100", "cluster100", "mirror100", "filter100"],
    ),
    (
        ("signal100 packet100 router100 cluster100 mirror100 filter100", 18),
        ["signal100", "packet100", "router100", "cluster100", "mirror100", "filter100"],
    ),
    (
        ("signal100 packet100 router100 cluster100 mirror100 filter100", 28),
        ["signal100 packet100", "router100 cluster100", "mirror100 filter100"],
    ),
    (
        ("packet100 router100 cluster100 mirror100 filter100 ranking100", 6),
        ["packet100", "router100", "cluster100", "mirror100", "filter100", "ranking100"],
    ),
    (
        ("packet100 router100 cluster100 mirror100 filter100 ranking100", 10),
        ["packet100", "router100", "cluster100", "mirror100", "filter100", "ranking100"],
    ),
    (
        ("packet100 router100 cluster100 mirror100 filter100 ranking100", 18),
        ["packet100", "router100", "cluster100", "mirror100", "filter100", "ranking100"],
    ),
    (
        ("packet100 router100 cluster100 mirror100 filter100 ranking100", 28),
        ["packet100 router100", "cluster100 mirror100", "filter100 ranking100"],
    ),
    (
        ("router100 cluster100 mirror100 filter100 ranking100 encoding100", 6),
        ["router100", "cluster100", "mirror100", "filter100", "ranking100", "encoding100"],
    ),
    (
        ("router100 cluster100 mirror100 filter100 ranking100 encoding100", 10),
        ["router100", "cluster100", "mirror100", "filter100", "ranking100", "encoding100"],
    ),
    (
        ("router100 cluster100 mirror100 filter100 ranking100 encoding100", 18),
        ["router100", "cluster100", "mirror100", "filter100", "ranking100", "encoding100"],
    ),
    (
        ("router100 cluster100 mirror100 filter100 ranking100 encoding100", 28),
        ["router100 cluster100", "mirror100 filter100", "ranking100 encoding100"],
    ),
    (
        ("cluster100 mirror100 filter100 ranking100 encoding100 mapping100", 6),
        ["cluster100", "mirror100", "filter100", "ranking100", "encoding100", "mapping100"],
    ),
    (
        ("cluster100 mirror100 filter100 ranking100 encoding100 mapping100", 10),
        ["cluster100", "mirror100", "filter100", "ranking100", "encoding100", "mapping100"],
    ),
    (
        ("cluster100 mirror100 filter100 ranking100 encoding100 mapping100", 18),
        ["cluster100", "mirror100", "filter100", "ranking100", "encoding100", "mapping100"],
    ),
    (
        ("cluster100 mirror100 filter100 ranking100 encoding100 mapping100", 28),
        ["cluster100 mirror100", "filter100 ranking100", "encoding100 mapping100"],
    ),
    (
        ("mirror100 filter100 ranking100 encoding100 mapping100 record100", 6),
        ["mirror100", "filter100", "ranking100", "encoding100", "mapping100", "record100"],
    ),
    (
        ("mirror100 filter100 ranking100 encoding100 mapping100 record100", 10),
        ["mirror100", "filter100", "ranking100", "encoding100", "mapping100", "record100"],
    ),
    (
        ("mirror100 filter100 ranking100 encoding100 mapping100 record100", 18),
        ["mirror100", "filter100", "ranking100", "encoding100", "mapping100", "record100"],
    ),
    (
        ("mirror100 filter100 ranking100 encoding100 mapping100 record100", 28),
        ["mirror100 filter100", "ranking100 encoding100", "mapping100 record100"],
    ),
    (
        ("filter100 ranking100 encoding100 mapping100 record100 candle100", 6),
        ["filter100", "ranking100", "encoding100", "mapping100", "record100", "candle100"],
    ),
    (
        ("filter100 ranking100 encoding100 mapping100 record100 candle100", 10),
        ["filter100", "ranking100", "encoding100", "mapping100", "record100", "candle100"],
    ),
    (
        ("filter100 ranking100 encoding100 mapping100 record100 candle100", 18),
        ["filter100", "ranking100", "encoding100", "mapping100", "record100", "candle100"],
    ),
    (
        ("filter100 ranking100 encoding100 mapping100 record100 candle100", 28),
        ["filter100 ranking100", "encoding100 mapping100", "record100 candle100"],
    ),
    (
        ("ranking100 encoding100 mapping100 record100 candle100 thread100", 6),
        ["ranking100", "encoding100", "mapping100", "record100", "candle100", "thread100"],
    ),
    (
        ("ranking100 encoding100 mapping100 record100 candle100 thread100", 10),
        ["ranking100", "encoding100", "mapping100", "record100", "candle100", "thread100"],
    ),
    (
        ("ranking100 encoding100 mapping100 record100 candle100 thread100", 18),
        ["ranking100", "encoding100", "mapping100", "record100", "candle100", "thread100"],
    ),
    (
        ("ranking100 encoding100 mapping100 record100 candle100 thread100", 28),
        ["ranking100 encoding100", "mapping100 record100", "candle100 thread100"],
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
