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
        ("round 136: the quick brown fox jumps over the lazy dog", 4),
        ["round", "136:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", 8),
        ["round", "136: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", 12),
        ["round 136:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", 16),
        ["round 136: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", 24),
        ["round 136: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 136: the quick brown fox jumps over the lazy dog", 32),
        ["round 136: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", 4),
        ["round", "136:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", 8),
        ["round", "136:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", 12),
        ["round 136:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", 16),
        ["round 136:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", 24),
        ["round 136: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 136: agentuniverse is a framework for multi agents", 32),
        ["round 136: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", 4),
        ["round", "136:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", 8),
        ["round", "136:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", 12),
        ["round 136:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", 16),
        ["round 136:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", 24),
        ["round 136: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 136: knowledge stored as vectors enables retrieval", 32),
        ["round 136: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 136: the processor reads the record then stops", 4),
        ["round", "136:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 136: the processor reads the record then stops", 8),
        ["round", "136: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 136: the processor reads the record then stops", 12),
        ["round 136:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 136: the processor reads the record then stops", 16),
        ["round 136: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 136: the processor reads the record then stops", 24),
        ["round 136: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 136: the processor reads the record then stops", 32),
        ["round 136: the processor reads", "the record then stops"],
    ),
    (
        ("round 136: a worker pulls the next task from the queue", 4),
        ["round", "136:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 136: a worker pulls the next task from the queue", 8),
        ["round", "136: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 136: a worker pulls the next task from the queue", 12),
        ["round 136: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 136: a worker pulls the next task from the queue", 16),
        ["round 136: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 136: a worker pulls the next task from the queue", 24),
        ["round 136: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 136: a worker pulls the next task from the queue", 32),
        ["round 136: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 136: signals travel through the network layer", 4),
        ["round", "136:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 136: signals travel through the network layer", 8),
        ["round", "136:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 136: signals travel through the network layer", 12),
        ["round 136:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 136: signals travel through the network layer", 16),
        ["round 136:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 136: signals travel through the network layer", 24),
        ["round 136: signals", "travel through the", "network layer"],
    ),
    (
        ("round 136: signals travel through the network layer", 32),
        ["round 136: signals travel", "through the network layer"],
    ),
    (
        ("round 136: the gateway routes each request by policy", 4),
        ["round", "136:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 136: the gateway routes each request by policy", 8),
        ["round", "136: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 136: the gateway routes each request by policy", 12),
        ["round 136:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 136: the gateway routes each request by policy", 16),
        ["round 136: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 136: the gateway routes each request by policy", 24),
        ["round 136: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 136: the gateway routes each request by policy", 32),
        ["round 136: the gateway routes", "each request by policy"],
    ),
    (
        ("round 136: memory grows until the buffer is full", 4),
        ["round", "136:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 136: memory grows until the buffer is full", 8),
        ["round", "136:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 136: memory grows until the buffer is full", 12),
        ["round 136:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 136: memory grows until the buffer is full", 16),
        ["round 136:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 136: memory grows until the buffer is full", 24), ["round 136: memory grows", "until the buffer is full"]),
    (("round 136: memory grows until the buffer is full", 32), ["round 136: memory grows until", "the buffer is full"]),
    (
        ("round 136: the cluster mirrors every packet twice", 4),
        ["round", "136:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 136: the cluster mirrors every packet twice", 8),
        ["round", "136: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 136: the cluster mirrors every packet twice", 12),
        ["round 136:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 136: the cluster mirrors every packet twice", 16),
        ["round 136: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 136: the cluster mirrors every packet twice", 24),
        ["round 136: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 136: the cluster mirrors every packet twice", 32),
        ["round 136: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", 4),
        ["round", "136:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", 8),
        ["round", "136:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", 12),
        ["round 136:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", 16),
        ["round 136:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", 24),
        ["round 136: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 136: ranking uses tokens learned from the corpus", 32),
        ["round 136: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 136: a long session ends when the candle dies", 4),
        ["round", "136:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 136: a long session ends when the candle dies", 8),
        ["round", "136: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 136: a long session ends when the candle dies", 12),
        ["round 136: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 136: a long session ends when the candle dies", 16),
        ["round 136: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 136: a long session ends when the candle dies", 24),
        ["round 136: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 136: a long session ends when the candle dies", 32),
        ["round 136: a long session ends", "when the candle dies"],
    ),
    (
        ("round 136: encode the prompt then map the result", 4),
        ["round", "136:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 136: encode the prompt then map the result", 8),
        ["round", "136:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 136: encode the prompt then map the result", 12),
        ["round 136:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 136: encode the prompt then map the result", 16),
        ["round 136:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 136: encode the prompt then map the result", 24),
        ["round 136: encode the", "prompt then map the", "result"],
    ),
    (("round 136: encode the prompt then map the result", 32), ["round 136: encode the prompt", "then map the result"]),
    (
        ("round 136: the kernel wakes the worker at dawn", 4),
        ["round", "136:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 136: the kernel wakes the worker at dawn", 8),
        ["round", "136: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 136: the kernel wakes the worker at dawn", 12),
        ["round 136:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 136: the kernel wakes the worker at dawn", 16), ["round 136: the", "kernel wakes the", "worker at dawn"]),
    (("round 136: the kernel wakes the worker at dawn", 24), ["round 136: the kernel", "wakes the worker at dawn"]),
    (("round 136: the kernel wakes the worker at dawn", 32), ["round 136: the kernel wakes the", "worker at dawn"]),
    (
        ("round 136: service latency drops after the patch", 4),
        ["round", "136:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 136: service latency drops after the patch", 8),
        ["round", "136:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 136: service latency drops after the patch", 12),
        ["round 136:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 136: service latency drops after the patch", 16),
        ["round 136:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 136: service latency drops after the patch", 24),
        ["round 136: service", "latency drops after the", "patch"],
    ),
    (("round 136: service latency drops after the patch", 32), ["round 136: service latency drops", "after the patch"]),
    (
        ("round 136: the library caches every vector it sees", 4),
        ["round", "136:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 136: the library caches every vector it sees", 8),
        ["round", "136: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 136: the library caches every vector it sees", 12),
        ["round 136:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 136: the library caches every vector it sees", 16),
        ["round 136: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 136: the library caches every vector it sees", 24),
        ["round 136: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 136: the library caches every vector it sees", 32),
        ["round 136: the library caches", "every vector it sees"],
    ),
    (
        ("round 136: agents argue then the debate resolves", 4),
        ["round", "136:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 136: agents argue then the debate resolves", 8),
        ["round", "136:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 136: agents argue then the debate resolves", 12),
        ["round 136:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 136: agents argue then the debate resolves", 16),
        ["round 136:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 136: agents argue then the debate resolves", 24), ["round 136: agents argue", "then the debate resolves"]),
    (("round 136: agents argue then the debate resolves", 32), ["round 136: agents argue then the", "debate resolves"]),
    (
        ("round 136: the filter keeps only strong matches", 4),
        ["round", "136:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 136: the filter keeps only strong matches", 8),
        ["round", "136: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 136: the filter keeps only strong matches", 12),
        ["round 136:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 136: the filter keeps only strong matches", 16),
        ["round 136: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 136: the filter keeps only strong matches", 24),
        ["round 136: the filter", "keeps only strong", "matches"],
    ),
    (("round 136: the filter keeps only strong matches", 32), ["round 136: the filter keeps only", "strong matches"]),
    (
        ("round 136: the model answers with a short reply", 4),
        ["round", "136:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 136: the model answers with a short reply", 8),
        ["round", "136: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 136: the model answers with a short reply", 12),
        ["round 136:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 136: the model answers with a short reply", 16),
        ["round 136: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 136: the model answers with a short reply", 24),
        ["round 136: the model", "answers with a short", "reply"],
    ),
    (("round 136: the model answers with a short reply", 32), ["round 136: the model answers", "with a short reply"]),
    (
        ("round 136: the recorder stores the reasoning trace", 4),
        ["round", "136:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 136: the recorder stores the reasoning trace", 8),
        ["round", "136: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 136: the recorder stores the reasoning trace", 12),
        ["round 136:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 136: the recorder stores the reasoning trace", 16),
        ["round 136: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 136: the recorder stores the reasoning trace", 24),
        ["round 136: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 136: the recorder stores the reasoning trace", 32),
        ["round 136: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 136: the angel watches the processor run", 4),
        ["round", "136:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 136: the angel watches the processor run", 8),
        ["round", "136: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 136: the angel watches the processor run", 12),
        ["round 136:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 136: the angel watches the processor run", 16),
        ["round 136: the", "angel watches", "the processor", "run"],
    ),
    (("round 136: the angel watches the processor run", 24), ["round 136: the angel", "watches the processor", "run"]),
    (("round 136: the angel watches the processor run", 32), ["round 136: the angel watches the", "processor run"]),
    (
        ("round 136: angle of the vector decides the match", 4),
        ["round", "136:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 136: angle of the vector decides the match", 8),
        ["round", "136:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 136: angle of the vector decides the match", 12),
        ["round 136:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 136: angle of the vector decides the match", 16),
        ["round 136: angle", "of the vector", "decides the", "match"],
    ),
    (("round 136: angle of the vector decides the match", 24), ["round 136: angle of the", "vector decides the match"]),
    (("round 136: angle of the vector decides the match", 32), ["round 136: angle of the vector", "decides the match"]),
    (
        ("round 136: the candle burns twice as long at night", 4),
        ["round", "136:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 136: the candle burns twice as long at night", 8),
        ["round", "136: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 136: the candle burns twice as long at night", 12),
        ["round 136:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 136: the candle burns twice as long at night", 16),
        ["round 136: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 136: the candle burns twice as long at night", 24),
        ["round 136: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 136: the candle burns twice as long at night", 32),
        ["round 136: the candle burns", "twice as long at night"],
    ),
    (
        ("round 136: a mirror of the universe in one line", 4),
        ["round", "136:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 136: a mirror of the universe in one line", 8),
        ["round", "136: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 136: a mirror of the universe in one line", 12),
        ["round 136: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 136: a mirror of the universe in one line", 16),
        ["round 136: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 136: a mirror of the universe in one line", 24), ["round 136: a mirror of", "the universe in one line"]),
    (("round 136: a mirror of the universe in one line", 32), ["round 136: a mirror of the", "universe in one line"]),
    (
        ("round 136: the queue drains before the storm", 4),
        ["round", "136:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 136: the queue drains before the storm", 8),
        ["round", "136: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 136: the queue drains before the storm", 12),
        ["round 136:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 136: the queue drains before the storm", 16), ["round 136: the", "queue drains", "before the storm"]),
    (("round 136: the queue drains before the storm", 24), ["round 136: the queue", "drains before the storm"]),
    (("round 136: the queue drains before the storm", 32), ["round 136: the queue drains", "before the storm"]),
    (
        ("kitten136 sitting136 agent136 angle136 universe136 memory136", 6),
        ["kitten136", "sitting136", "agent136", "angle136", "universe136", "memory136"],
    ),
    (
        ("kitten136 sitting136 agent136 angle136 universe136 memory136", 10),
        ["kitten136", "sitting136", "agent136", "angle136", "universe136", "memory136"],
    ),
    (
        ("kitten136 sitting136 agent136 angle136 universe136 memory136", 18),
        ["kitten136", "sitting136", "agent136 angle136", "universe136", "memory136"],
    ),
    (
        ("kitten136 sitting136 agent136 angle136 universe136 memory136", 28),
        ["kitten136 sitting136", "agent136 angle136", "universe136 memory136"],
    ),
    (
        ("sitting136 agent136 angle136 universe136 memory136 stream136", 6),
        ["sitting136", "agent136", "angle136", "universe136", "memory136", "stream136"],
    ),
    (
        ("sitting136 agent136 angle136 universe136 memory136 stream136", 10),
        ["sitting136", "agent136", "angle136", "universe136", "memory136", "stream136"],
    ),
    (
        ("sitting136 agent136 angle136 universe136 memory136 stream136", 18),
        ["sitting136", "agent136 angle136", "universe136", "memory136", "stream136"],
    ),
    (
        ("sitting136 agent136 angle136 universe136 memory136 stream136", 28),
        ["sitting136 agent136 angle136", "universe136 memory136", "stream136"],
    ),
    (
        ("agent136 angle136 universe136 memory136 stream136 context136", 6),
        ["agent136", "angle136", "universe136", "memory136", "stream136", "context136"],
    ),
    (
        ("agent136 angle136 universe136 memory136 stream136 context136", 10),
        ["agent136", "angle136", "universe136", "memory136", "stream136", "context136"],
    ),
    (
        ("agent136 angle136 universe136 memory136 stream136 context136", 18),
        ["agent136 angle136", "universe136", "memory136", "stream136", "context136"],
    ),
    (
        ("agent136 angle136 universe136 memory136 stream136 context136", 28),
        ["agent136 angle136", "universe136 memory136", "stream136 context136"],
    ),
    (
        ("angle136 universe136 memory136 stream136 context136 knowledge136", 6),
        ["angle136", "universe136", "memory136", "stream136", "context136", "knowledge136"],
    ),
    (
        ("angle136 universe136 memory136 stream136 context136 knowledge136", 10),
        ["angle136", "universe136", "memory136", "stream136", "context136", "knowledge136"],
    ),
    (
        ("angle136 universe136 memory136 stream136 context136 knowledge136", 18),
        ["angle136", "universe136", "memory136", "stream136", "context136", "knowledge136"],
    ),
    (
        ("angle136 universe136 memory136 stream136 context136 knowledge136", 28),
        ["angle136 universe136", "memory136 stream136", "context136 knowledge136"],
    ),
    (
        ("universe136 memory136 stream136 context136 knowledge136 vector136", 6),
        ["universe136", "memory136", "stream136", "context136", "knowledge136", "vector136"],
    ),
    (
        ("universe136 memory136 stream136 context136 knowledge136 vector136", 10),
        ["universe136", "memory136", "stream136", "context136", "knowledge136", "vector136"],
    ),
    (
        ("universe136 memory136 stream136 context136 knowledge136 vector136", 18),
        ["universe136", "memory136", "stream136", "context136", "knowledge136", "vector136"],
    ),
    (
        ("universe136 memory136 stream136 context136 knowledge136 vector136", 28),
        ["universe136 memory136", "stream136 context136", "knowledge136 vector136"],
    ),
    (
        ("memory136 stream136 context136 knowledge136 vector136 processor136", 6),
        ["memory136", "stream136", "context136", "knowledge136", "vector136", "processor136"],
    ),
    (
        ("memory136 stream136 context136 knowledge136 vector136 processor136", 10),
        ["memory136", "stream136", "context136", "knowledge136", "vector136", "processor136"],
    ),
    (
        ("memory136 stream136 context136 knowledge136 vector136 processor136", 18),
        ["memory136", "stream136", "context136", "knowledge136", "vector136", "processor136"],
    ),
    (
        ("memory136 stream136 context136 knowledge136 vector136 processor136", 28),
        ["memory136 stream136", "context136 knowledge136", "vector136 processor136"],
    ),
    (
        ("stream136 context136 knowledge136 vector136 processor136 reasoning136", 6),
        ["stream136", "context136", "knowledge136", "vector136", "processor136", "reasoning136"],
    ),
    (
        ("stream136 context136 knowledge136 vector136 processor136 reasoning136", 10),
        ["stream136", "context136", "knowledge136", "vector136", "processor136", "reasoning136"],
    ),
    (
        ("stream136 context136 knowledge136 vector136 processor136 reasoning136", 18),
        ["stream136", "context136", "knowledge136", "vector136", "processor136", "reasoning136"],
    ),
    (
        ("stream136 context136 knowledge136 vector136 processor136 reasoning136", 28),
        ["stream136 context136", "knowledge136 vector136", "processor136 reasoning136"],
    ),
    (
        ("context136 knowledge136 vector136 processor136 reasoning136 machine136", 6),
        ["context136", "knowledge136", "vector136", "processor136", "reasoning136", "machine136"],
    ),
    (
        ("context136 knowledge136 vector136 processor136 reasoning136 machine136", 10),
        ["context136", "knowledge136", "vector136", "processor136", "reasoning136", "machine136"],
    ),
    (
        ("context136 knowledge136 vector136 processor136 reasoning136 machine136", 18),
        ["context136", "knowledge136", "vector136", "processor136", "reasoning136", "machine136"],
    ),
    (
        ("context136 knowledge136 vector136 processor136 reasoning136 machine136", 28),
        ["context136 knowledge136", "vector136 processor136", "reasoning136 machine136"],
    ),
    (
        ("knowledge136 vector136 processor136 reasoning136 machine136 learning136", 6),
        ["knowledge136", "vector136", "processor136", "reasoning136", "machine136", "learning136"],
    ),
    (
        ("knowledge136 vector136 processor136 reasoning136 machine136 learning136", 10),
        ["knowledge136", "vector136", "processor136", "reasoning136", "machine136", "learning136"],
    ),
    (
        ("knowledge136 vector136 processor136 reasoning136 machine136 learning136", 18),
        ["knowledge136", "vector136", "processor136", "reasoning136", "machine136", "learning136"],
    ),
    (
        ("knowledge136 vector136 processor136 reasoning136 machine136 learning136", 28),
        ["knowledge136 vector136", "processor136 reasoning136", "machine136 learning136"],
    ),
    (
        ("vector136 processor136 reasoning136 machine136 learning136 model136", 6),
        ["vector136", "processor136", "reasoning136", "machine136", "learning136", "model136"],
    ),
    (
        ("vector136 processor136 reasoning136 machine136 learning136 model136", 10),
        ["vector136", "processor136", "reasoning136", "machine136", "learning136", "model136"],
    ),
    (
        ("vector136 processor136 reasoning136 machine136 learning136 model136", 18),
        ["vector136", "processor136", "reasoning136", "machine136", "learning136", "model136"],
    ),
    (
        ("vector136 processor136 reasoning136 machine136 learning136 model136", 28),
        ["vector136 processor136", "reasoning136 machine136", "learning136 model136"],
    ),
    (
        ("processor136 reasoning136 machine136 learning136 model136 token136", 6),
        ["processor136", "reasoning136", "machine136", "learning136", "model136", "token136"],
    ),
    (
        ("processor136 reasoning136 machine136 learning136 model136 token136", 10),
        ["processor136", "reasoning136", "machine136", "learning136", "model136", "token136"],
    ),
    (
        ("processor136 reasoning136 machine136 learning136 model136 token136", 18),
        ["processor136", "reasoning136", "machine136", "learning136", "model136 token136"],
    ),
    (
        ("processor136 reasoning136 machine136 learning136 model136 token136", 28),
        ["processor136 reasoning136", "machine136 learning136", "model136 token136"],
    ),
    (
        ("reasoning136 machine136 learning136 model136 token136 prompt136", 6),
        ["reasoning136", "machine136", "learning136", "model136", "token136", "prompt136"],
    ),
    (
        ("reasoning136 machine136 learning136 model136 token136 prompt136", 10),
        ["reasoning136", "machine136", "learning136", "model136", "token136", "prompt136"],
    ),
    (
        ("reasoning136 machine136 learning136 model136 token136 prompt136", 18),
        ["reasoning136", "machine136", "learning136", "model136 token136", "prompt136"],
    ),
    (
        ("reasoning136 machine136 learning136 model136 token136 prompt136", 28),
        ["reasoning136 machine136", "learning136 model136", "token136 prompt136"],
    ),
    (
        ("machine136 learning136 model136 token136 prompt136 session136", 6),
        ["machine136", "learning136", "model136", "token136", "prompt136", "session136"],
    ),
    (
        ("machine136 learning136 model136 token136 prompt136 session136", 10),
        ["machine136", "learning136", "model136", "token136", "prompt136", "session136"],
    ),
    (
        ("machine136 learning136 model136 token136 prompt136 session136", 18),
        ["machine136", "learning136", "model136 token136", "prompt136", "session136"],
    ),
    (
        ("machine136 learning136 model136 token136 prompt136 session136", 28),
        ["machine136 learning136", "model136 token136 prompt136", "session136"],
    ),
    (
        ("learning136 model136 token136 prompt136 session136 library136", 6),
        ["learning136", "model136", "token136", "prompt136", "session136", "library136"],
    ),
    (
        ("learning136 model136 token136 prompt136 session136 library136", 10),
        ["learning136", "model136", "token136", "prompt136", "session136", "library136"],
    ),
    (
        ("learning136 model136 token136 prompt136 session136 library136", 18),
        ["learning136", "model136 token136", "prompt136", "session136", "library136"],
    ),
    (
        ("learning136 model136 token136 prompt136 session136 library136", 28),
        ["learning136 model136", "token136 prompt136", "session136 library136"],
    ),
    (
        ("model136 token136 prompt136 session136 library136 service136", 6),
        ["model136", "token136", "prompt136", "session136", "library136", "service136"],
    ),
    (
        ("model136 token136 prompt136 session136 library136 service136", 10),
        ["model136", "token136", "prompt136", "session136", "library136", "service136"],
    ),
    (
        ("model136 token136 prompt136 session136 library136 service136", 18),
        ["model136 token136", "prompt136", "session136", "library136", "service136"],
    ),
    (
        ("model136 token136 prompt136 session136 library136 service136", 28),
        ["model136 token136 prompt136", "session136 library136", "service136"],
    ),
    (
        ("token136 prompt136 session136 library136 service136 gateway136", 6),
        ["token136", "prompt136", "session136", "library136", "service136", "gateway136"],
    ),
    (
        ("token136 prompt136 session136 library136 service136 gateway136", 10),
        ["token136", "prompt136", "session136", "library136", "service136", "gateway136"],
    ),
    (
        ("token136 prompt136 session136 library136 service136 gateway136", 18),
        ["token136 prompt136", "session136", "library136", "service136", "gateway136"],
    ),
    (
        ("token136 prompt136 session136 library136 service136 gateway136", 28),
        ["token136 prompt136", "session136 library136", "service136 gateway136"],
    ),
    (
        ("prompt136 session136 library136 service136 gateway136 storage136", 6),
        ["prompt136", "session136", "library136", "service136", "gateway136", "storage136"],
    ),
    (
        ("prompt136 session136 library136 service136 gateway136 storage136", 10),
        ["prompt136", "session136", "library136", "service136", "gateway136", "storage136"],
    ),
    (
        ("prompt136 session136 library136 service136 gateway136 storage136", 18),
        ["prompt136", "session136", "library136", "service136", "gateway136", "storage136"],
    ),
    (
        ("prompt136 session136 library136 service136 gateway136 storage136", 28),
        ["prompt136 session136", "library136 service136", "gateway136 storage136"],
    ),
    (
        ("session136 library136 service136 gateway136 storage136 network136", 6),
        ["session136", "library136", "service136", "gateway136", "storage136", "network136"],
    ),
    (
        ("session136 library136 service136 gateway136 storage136 network136", 10),
        ["session136", "library136", "service136", "gateway136", "storage136", "network136"],
    ),
    (
        ("session136 library136 service136 gateway136 storage136 network136", 18),
        ["session136", "library136", "service136", "gateway136", "storage136", "network136"],
    ),
    (
        ("session136 library136 service136 gateway136 storage136 network136", 28),
        ["session136 library136", "service136 gateway136", "storage136 network136"],
    ),
    (
        ("library136 service136 gateway136 storage136 network136 latency136", 6),
        ["library136", "service136", "gateway136", "storage136", "network136", "latency136"],
    ),
    (
        ("library136 service136 gateway136 storage136 network136 latency136", 10),
        ["library136", "service136", "gateway136", "storage136", "network136", "latency136"],
    ),
    (
        ("library136 service136 gateway136 storage136 network136 latency136", 18),
        ["library136", "service136", "gateway136", "storage136", "network136", "latency136"],
    ),
    (
        ("library136 service136 gateway136 storage136 network136 latency136", 28),
        ["library136 service136", "gateway136 storage136", "network136 latency136"],
    ),
    (
        ("service136 gateway136 storage136 network136 latency136 buffer136", 6),
        ["service136", "gateway136", "storage136", "network136", "latency136", "buffer136"],
    ),
    (
        ("service136 gateway136 storage136 network136 latency136 buffer136", 10),
        ["service136", "gateway136", "storage136", "network136", "latency136", "buffer136"],
    ),
    (
        ("service136 gateway136 storage136 network136 latency136 buffer136", 18),
        ["service136", "gateway136", "storage136", "network136", "latency136", "buffer136"],
    ),
    (
        ("service136 gateway136 storage136 network136 latency136 buffer136", 28),
        ["service136 gateway136", "storage136 network136", "latency136 buffer136"],
    ),
    (
        ("gateway136 storage136 network136 latency136 buffer136 queue136", 6),
        ["gateway136", "storage136", "network136", "latency136", "buffer136", "queue136"],
    ),
    (
        ("gateway136 storage136 network136 latency136 buffer136 queue136", 10),
        ["gateway136", "storage136", "network136", "latency136", "buffer136", "queue136"],
    ),
    (
        ("gateway136 storage136 network136 latency136 buffer136 queue136", 18),
        ["gateway136", "storage136", "network136", "latency136", "buffer136 queue136"],
    ),
    (
        ("gateway136 storage136 network136 latency136 buffer136 queue136", 28),
        ["gateway136 storage136", "network136 latency136", "buffer136 queue136"],
    ),
    (
        ("storage136 network136 latency136 buffer136 queue136 worker136", 6),
        ["storage136", "network136", "latency136", "buffer136", "queue136", "worker136"],
    ),
    (
        ("storage136 network136 latency136 buffer136 queue136 worker136", 10),
        ["storage136", "network136", "latency136", "buffer136", "queue136", "worker136"],
    ),
    (
        ("storage136 network136 latency136 buffer136 queue136 worker136", 18),
        ["storage136", "network136", "latency136", "buffer136 queue136", "worker136"],
    ),
    (
        ("storage136 network136 latency136 buffer136 queue136 worker136", 28),
        ["storage136 network136", "latency136 buffer136", "queue136 worker136"],
    ),
    (
        ("network136 latency136 buffer136 queue136 worker136 kernel136", 6),
        ["network136", "latency136", "buffer136", "queue136", "worker136", "kernel136"],
    ),
    (
        ("network136 latency136 buffer136 queue136 worker136 kernel136", 10),
        ["network136", "latency136", "buffer136", "queue136", "worker136", "kernel136"],
    ),
    (
        ("network136 latency136 buffer136 queue136 worker136 kernel136", 18),
        ["network136", "latency136", "buffer136 queue136", "worker136", "kernel136"],
    ),
    (
        ("network136 latency136 buffer136 queue136 worker136 kernel136", 28),
        ["network136 latency136", "buffer136 queue136 worker136", "kernel136"],
    ),
    (
        ("latency136 buffer136 queue136 worker136 kernel136 signal136", 6),
        ["latency136", "buffer136", "queue136", "worker136", "kernel136", "signal136"],
    ),
    (
        ("latency136 buffer136 queue136 worker136 kernel136 signal136", 10),
        ["latency136", "buffer136", "queue136", "worker136", "kernel136", "signal136"],
    ),
    (
        ("latency136 buffer136 queue136 worker136 kernel136 signal136", 18),
        ["latency136", "buffer136 queue136", "worker136", "kernel136", "signal136"],
    ),
    (
        ("latency136 buffer136 queue136 worker136 kernel136 signal136", 28),
        ["latency136 buffer136", "queue136 worker136 kernel136", "signal136"],
    ),
    (
        ("buffer136 queue136 worker136 kernel136 signal136 packet136", 6),
        ["buffer136", "queue136", "worker136", "kernel136", "signal136", "packet136"],
    ),
    (
        ("buffer136 queue136 worker136 kernel136 signal136 packet136", 10),
        ["buffer136", "queue136", "worker136", "kernel136", "signal136", "packet136"],
    ),
    (
        ("buffer136 queue136 worker136 kernel136 signal136 packet136", 18),
        ["buffer136 queue136", "worker136", "kernel136", "signal136", "packet136"],
    ),
    (
        ("buffer136 queue136 worker136 kernel136 signal136 packet136", 28),
        ["buffer136 queue136 worker136", "kernel136 signal136", "packet136"],
    ),
    (
        ("queue136 worker136 kernel136 signal136 packet136 router136", 6),
        ["queue136", "worker136", "kernel136", "signal136", "packet136", "router136"],
    ),
    (
        ("queue136 worker136 kernel136 signal136 packet136 router136", 10),
        ["queue136", "worker136", "kernel136", "signal136", "packet136", "router136"],
    ),
    (
        ("queue136 worker136 kernel136 signal136 packet136 router136", 18),
        ["queue136 worker136", "kernel136", "signal136", "packet136", "router136"],
    ),
    (
        ("queue136 worker136 kernel136 signal136 packet136 router136", 28),
        ["queue136 worker136 kernel136", "signal136 packet136", "router136"],
    ),
    (
        ("worker136 kernel136 signal136 packet136 router136 cluster136", 6),
        ["worker136", "kernel136", "signal136", "packet136", "router136", "cluster136"],
    ),
    (
        ("worker136 kernel136 signal136 packet136 router136 cluster136", 10),
        ["worker136", "kernel136", "signal136", "packet136", "router136", "cluster136"],
    ),
    (
        ("worker136 kernel136 signal136 packet136 router136 cluster136", 18),
        ["worker136", "kernel136", "signal136", "packet136", "router136", "cluster136"],
    ),
    (
        ("worker136 kernel136 signal136 packet136 router136 cluster136", 28),
        ["worker136 kernel136", "signal136 packet136", "router136 cluster136"],
    ),
    (
        ("kernel136 signal136 packet136 router136 cluster136 mirror136", 6),
        ["kernel136", "signal136", "packet136", "router136", "cluster136", "mirror136"],
    ),
    (
        ("kernel136 signal136 packet136 router136 cluster136 mirror136", 10),
        ["kernel136", "signal136", "packet136", "router136", "cluster136", "mirror136"],
    ),
    (
        ("kernel136 signal136 packet136 router136 cluster136 mirror136", 18),
        ["kernel136", "signal136", "packet136", "router136", "cluster136", "mirror136"],
    ),
    (
        ("kernel136 signal136 packet136 router136 cluster136 mirror136", 28),
        ["kernel136 signal136", "packet136 router136", "cluster136 mirror136"],
    ),
    (
        ("signal136 packet136 router136 cluster136 mirror136 filter136", 6),
        ["signal136", "packet136", "router136", "cluster136", "mirror136", "filter136"],
    ),
    (
        ("signal136 packet136 router136 cluster136 mirror136 filter136", 10),
        ["signal136", "packet136", "router136", "cluster136", "mirror136", "filter136"],
    ),
    (
        ("signal136 packet136 router136 cluster136 mirror136 filter136", 18),
        ["signal136", "packet136", "router136", "cluster136", "mirror136", "filter136"],
    ),
    (
        ("signal136 packet136 router136 cluster136 mirror136 filter136", 28),
        ["signal136 packet136", "router136 cluster136", "mirror136 filter136"],
    ),
    (
        ("packet136 router136 cluster136 mirror136 filter136 ranking136", 6),
        ["packet136", "router136", "cluster136", "mirror136", "filter136", "ranking136"],
    ),
    (
        ("packet136 router136 cluster136 mirror136 filter136 ranking136", 10),
        ["packet136", "router136", "cluster136", "mirror136", "filter136", "ranking136"],
    ),
    (
        ("packet136 router136 cluster136 mirror136 filter136 ranking136", 18),
        ["packet136", "router136", "cluster136", "mirror136", "filter136", "ranking136"],
    ),
    (
        ("packet136 router136 cluster136 mirror136 filter136 ranking136", 28),
        ["packet136 router136", "cluster136 mirror136", "filter136 ranking136"],
    ),
    (
        ("router136 cluster136 mirror136 filter136 ranking136 encoding136", 6),
        ["router136", "cluster136", "mirror136", "filter136", "ranking136", "encoding136"],
    ),
    (
        ("router136 cluster136 mirror136 filter136 ranking136 encoding136", 10),
        ["router136", "cluster136", "mirror136", "filter136", "ranking136", "encoding136"],
    ),
    (
        ("router136 cluster136 mirror136 filter136 ranking136 encoding136", 18),
        ["router136", "cluster136", "mirror136", "filter136", "ranking136", "encoding136"],
    ),
    (
        ("router136 cluster136 mirror136 filter136 ranking136 encoding136", 28),
        ["router136 cluster136", "mirror136 filter136", "ranking136 encoding136"],
    ),
    (
        ("cluster136 mirror136 filter136 ranking136 encoding136 mapping136", 6),
        ["cluster136", "mirror136", "filter136", "ranking136", "encoding136", "mapping136"],
    ),
    (
        ("cluster136 mirror136 filter136 ranking136 encoding136 mapping136", 10),
        ["cluster136", "mirror136", "filter136", "ranking136", "encoding136", "mapping136"],
    ),
    (
        ("cluster136 mirror136 filter136 ranking136 encoding136 mapping136", 18),
        ["cluster136", "mirror136", "filter136", "ranking136", "encoding136", "mapping136"],
    ),
    (
        ("cluster136 mirror136 filter136 ranking136 encoding136 mapping136", 28),
        ["cluster136 mirror136", "filter136 ranking136", "encoding136 mapping136"],
    ),
    (
        ("mirror136 filter136 ranking136 encoding136 mapping136 record136", 6),
        ["mirror136", "filter136", "ranking136", "encoding136", "mapping136", "record136"],
    ),
    (
        ("mirror136 filter136 ranking136 encoding136 mapping136 record136", 10),
        ["mirror136", "filter136", "ranking136", "encoding136", "mapping136", "record136"],
    ),
    (
        ("mirror136 filter136 ranking136 encoding136 mapping136 record136", 18),
        ["mirror136", "filter136", "ranking136", "encoding136", "mapping136", "record136"],
    ),
    (
        ("mirror136 filter136 ranking136 encoding136 mapping136 record136", 28),
        ["mirror136 filter136", "ranking136 encoding136", "mapping136 record136"],
    ),
    (
        ("filter136 ranking136 encoding136 mapping136 record136 candle136", 6),
        ["filter136", "ranking136", "encoding136", "mapping136", "record136", "candle136"],
    ),
    (
        ("filter136 ranking136 encoding136 mapping136 record136 candle136", 10),
        ["filter136", "ranking136", "encoding136", "mapping136", "record136", "candle136"],
    ),
    (
        ("filter136 ranking136 encoding136 mapping136 record136 candle136", 18),
        ["filter136", "ranking136", "encoding136", "mapping136", "record136", "candle136"],
    ),
    (
        ("filter136 ranking136 encoding136 mapping136 record136 candle136", 28),
        ["filter136 ranking136", "encoding136 mapping136", "record136 candle136"],
    ),
    (
        ("ranking136 encoding136 mapping136 record136 candle136 thread136", 6),
        ["ranking136", "encoding136", "mapping136", "record136", "candle136", "thread136"],
    ),
    (
        ("ranking136 encoding136 mapping136 record136 candle136 thread136", 10),
        ["ranking136", "encoding136", "mapping136", "record136", "candle136", "thread136"],
    ),
    (
        ("ranking136 encoding136 mapping136 record136 candle136 thread136", 18),
        ["ranking136", "encoding136", "mapping136", "record136", "candle136", "thread136"],
    ),
    (
        ("ranking136 encoding136 mapping136 record136 candle136 thread136", 28),
        ["ranking136 encoding136", "mapping136 record136", "candle136 thread136"],
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
