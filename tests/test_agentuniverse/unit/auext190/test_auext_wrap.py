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
        ("round 190: the quick brown fox jumps over the lazy dog", 4),
        ["round", "190:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", 8),
        ["round", "190: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", 12),
        ["round 190:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", 16),
        ["round 190: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", 24),
        ["round 190: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 190: the quick brown fox jumps over the lazy dog", 32),
        ["round 190: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", 4),
        ["round", "190:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", 8),
        ["round", "190:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", 12),
        ["round 190:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", 16),
        ["round 190:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", 24),
        ["round 190: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 190: agentuniverse is a framework for multi agents", 32),
        ["round 190: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", 4),
        ["round", "190:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", 8),
        ["round", "190:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", 12),
        ["round 190:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", 16),
        ["round 190:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", 24),
        ["round 190: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 190: knowledge stored as vectors enables retrieval", 32),
        ["round 190: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 190: the processor reads the record then stops", 4),
        ["round", "190:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 190: the processor reads the record then stops", 8),
        ["round", "190: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 190: the processor reads the record then stops", 12),
        ["round 190:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 190: the processor reads the record then stops", 16),
        ["round 190: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 190: the processor reads the record then stops", 24),
        ["round 190: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 190: the processor reads the record then stops", 32),
        ["round 190: the processor reads", "the record then stops"],
    ),
    (
        ("round 190: a worker pulls the next task from the queue", 4),
        ["round", "190:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 190: a worker pulls the next task from the queue", 8),
        ["round", "190: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 190: a worker pulls the next task from the queue", 12),
        ["round 190: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 190: a worker pulls the next task from the queue", 16),
        ["round 190: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 190: a worker pulls the next task from the queue", 24),
        ["round 190: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 190: a worker pulls the next task from the queue", 32),
        ["round 190: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 190: signals travel through the network layer", 4),
        ["round", "190:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 190: signals travel through the network layer", 8),
        ["round", "190:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 190: signals travel through the network layer", 12),
        ["round 190:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 190: signals travel through the network layer", 16),
        ["round 190:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 190: signals travel through the network layer", 24),
        ["round 190: signals", "travel through the", "network layer"],
    ),
    (
        ("round 190: signals travel through the network layer", 32),
        ["round 190: signals travel", "through the network layer"],
    ),
    (
        ("round 190: the gateway routes each request by policy", 4),
        ["round", "190:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 190: the gateway routes each request by policy", 8),
        ["round", "190: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 190: the gateway routes each request by policy", 12),
        ["round 190:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 190: the gateway routes each request by policy", 16),
        ["round 190: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 190: the gateway routes each request by policy", 24),
        ["round 190: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 190: the gateway routes each request by policy", 32),
        ["round 190: the gateway routes", "each request by policy"],
    ),
    (
        ("round 190: memory grows until the buffer is full", 4),
        ["round", "190:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 190: memory grows until the buffer is full", 8),
        ["round", "190:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 190: memory grows until the buffer is full", 12),
        ["round 190:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 190: memory grows until the buffer is full", 16),
        ["round 190:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 190: memory grows until the buffer is full", 24), ["round 190: memory grows", "until the buffer is full"]),
    (("round 190: memory grows until the buffer is full", 32), ["round 190: memory grows until", "the buffer is full"]),
    (
        ("round 190: the cluster mirrors every packet twice", 4),
        ["round", "190:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 190: the cluster mirrors every packet twice", 8),
        ["round", "190: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 190: the cluster mirrors every packet twice", 12),
        ["round 190:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 190: the cluster mirrors every packet twice", 16),
        ["round 190: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 190: the cluster mirrors every packet twice", 24),
        ["round 190: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 190: the cluster mirrors every packet twice", 32),
        ["round 190: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", 4),
        ["round", "190:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", 8),
        ["round", "190:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", 12),
        ["round 190:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", 16),
        ["round 190:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", 24),
        ["round 190: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 190: ranking uses tokens learned from the corpus", 32),
        ["round 190: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 190: a long session ends when the candle dies", 4),
        ["round", "190:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 190: a long session ends when the candle dies", 8),
        ["round", "190: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 190: a long session ends when the candle dies", 12),
        ["round 190: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 190: a long session ends when the candle dies", 16),
        ["round 190: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 190: a long session ends when the candle dies", 24),
        ["round 190: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 190: a long session ends when the candle dies", 32),
        ["round 190: a long session ends", "when the candle dies"],
    ),
    (
        ("round 190: encode the prompt then map the result", 4),
        ["round", "190:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 190: encode the prompt then map the result", 8),
        ["round", "190:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 190: encode the prompt then map the result", 12),
        ["round 190:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 190: encode the prompt then map the result", 16),
        ["round 190:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 190: encode the prompt then map the result", 24),
        ["round 190: encode the", "prompt then map the", "result"],
    ),
    (("round 190: encode the prompt then map the result", 32), ["round 190: encode the prompt", "then map the result"]),
    (
        ("round 190: the kernel wakes the worker at dawn", 4),
        ["round", "190:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 190: the kernel wakes the worker at dawn", 8),
        ["round", "190: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 190: the kernel wakes the worker at dawn", 12),
        ["round 190:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 190: the kernel wakes the worker at dawn", 16), ["round 190: the", "kernel wakes the", "worker at dawn"]),
    (("round 190: the kernel wakes the worker at dawn", 24), ["round 190: the kernel", "wakes the worker at dawn"]),
    (("round 190: the kernel wakes the worker at dawn", 32), ["round 190: the kernel wakes the", "worker at dawn"]),
    (
        ("round 190: service latency drops after the patch", 4),
        ["round", "190:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 190: service latency drops after the patch", 8),
        ["round", "190:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 190: service latency drops after the patch", 12),
        ["round 190:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 190: service latency drops after the patch", 16),
        ["round 190:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 190: service latency drops after the patch", 24),
        ["round 190: service", "latency drops after the", "patch"],
    ),
    (("round 190: service latency drops after the patch", 32), ["round 190: service latency drops", "after the patch"]),
    (
        ("round 190: the library caches every vector it sees", 4),
        ["round", "190:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 190: the library caches every vector it sees", 8),
        ["round", "190: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 190: the library caches every vector it sees", 12),
        ["round 190:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 190: the library caches every vector it sees", 16),
        ["round 190: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 190: the library caches every vector it sees", 24),
        ["round 190: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 190: the library caches every vector it sees", 32),
        ["round 190: the library caches", "every vector it sees"],
    ),
    (
        ("round 190: agents argue then the debate resolves", 4),
        ["round", "190:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 190: agents argue then the debate resolves", 8),
        ["round", "190:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 190: agents argue then the debate resolves", 12),
        ["round 190:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 190: agents argue then the debate resolves", 16),
        ["round 190:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 190: agents argue then the debate resolves", 24), ["round 190: agents argue", "then the debate resolves"]),
    (("round 190: agents argue then the debate resolves", 32), ["round 190: agents argue then the", "debate resolves"]),
    (
        ("round 190: the filter keeps only strong matches", 4),
        ["round", "190:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 190: the filter keeps only strong matches", 8),
        ["round", "190: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 190: the filter keeps only strong matches", 12),
        ["round 190:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 190: the filter keeps only strong matches", 16),
        ["round 190: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 190: the filter keeps only strong matches", 24),
        ["round 190: the filter", "keeps only strong", "matches"],
    ),
    (("round 190: the filter keeps only strong matches", 32), ["round 190: the filter keeps only", "strong matches"]),
    (
        ("round 190: the model answers with a short reply", 4),
        ["round", "190:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 190: the model answers with a short reply", 8),
        ["round", "190: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 190: the model answers with a short reply", 12),
        ["round 190:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 190: the model answers with a short reply", 16),
        ["round 190: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 190: the model answers with a short reply", 24),
        ["round 190: the model", "answers with a short", "reply"],
    ),
    (("round 190: the model answers with a short reply", 32), ["round 190: the model answers", "with a short reply"]),
    (
        ("round 190: the recorder stores the reasoning trace", 4),
        ["round", "190:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 190: the recorder stores the reasoning trace", 8),
        ["round", "190: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 190: the recorder stores the reasoning trace", 12),
        ["round 190:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 190: the recorder stores the reasoning trace", 16),
        ["round 190: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 190: the recorder stores the reasoning trace", 24),
        ["round 190: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 190: the recorder stores the reasoning trace", 32),
        ["round 190: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 190: the angel watches the processor run", 4),
        ["round", "190:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 190: the angel watches the processor run", 8),
        ["round", "190: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 190: the angel watches the processor run", 12),
        ["round 190:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 190: the angel watches the processor run", 16),
        ["round 190: the", "angel watches", "the processor", "run"],
    ),
    (("round 190: the angel watches the processor run", 24), ["round 190: the angel", "watches the processor", "run"]),
    (("round 190: the angel watches the processor run", 32), ["round 190: the angel watches the", "processor run"]),
    (
        ("round 190: angle of the vector decides the match", 4),
        ["round", "190:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 190: angle of the vector decides the match", 8),
        ["round", "190:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 190: angle of the vector decides the match", 12),
        ["round 190:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 190: angle of the vector decides the match", 16),
        ["round 190: angle", "of the vector", "decides the", "match"],
    ),
    (("round 190: angle of the vector decides the match", 24), ["round 190: angle of the", "vector decides the match"]),
    (("round 190: angle of the vector decides the match", 32), ["round 190: angle of the vector", "decides the match"]),
    (
        ("round 190: the candle burns twice as long at night", 4),
        ["round", "190:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 190: the candle burns twice as long at night", 8),
        ["round", "190: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 190: the candle burns twice as long at night", 12),
        ["round 190:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 190: the candle burns twice as long at night", 16),
        ["round 190: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 190: the candle burns twice as long at night", 24),
        ["round 190: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 190: the candle burns twice as long at night", 32),
        ["round 190: the candle burns", "twice as long at night"],
    ),
    (
        ("round 190: a mirror of the universe in one line", 4),
        ["round", "190:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 190: a mirror of the universe in one line", 8),
        ["round", "190: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 190: a mirror of the universe in one line", 12),
        ["round 190: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 190: a mirror of the universe in one line", 16),
        ["round 190: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 190: a mirror of the universe in one line", 24), ["round 190: a mirror of", "the universe in one line"]),
    (("round 190: a mirror of the universe in one line", 32), ["round 190: a mirror of the", "universe in one line"]),
    (
        ("round 190: the queue drains before the storm", 4),
        ["round", "190:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 190: the queue drains before the storm", 8),
        ["round", "190: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 190: the queue drains before the storm", 12),
        ["round 190:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 190: the queue drains before the storm", 16), ["round 190: the", "queue drains", "before the storm"]),
    (("round 190: the queue drains before the storm", 24), ["round 190: the queue", "drains before the storm"]),
    (("round 190: the queue drains before the storm", 32), ["round 190: the queue drains", "before the storm"]),
    (
        ("kitten190 sitting190 agent190 angle190 universe190 memory190", 6),
        ["kitten190", "sitting190", "agent190", "angle190", "universe190", "memory190"],
    ),
    (
        ("kitten190 sitting190 agent190 angle190 universe190 memory190", 10),
        ["kitten190", "sitting190", "agent190", "angle190", "universe190", "memory190"],
    ),
    (
        ("kitten190 sitting190 agent190 angle190 universe190 memory190", 18),
        ["kitten190", "sitting190", "agent190 angle190", "universe190", "memory190"],
    ),
    (
        ("kitten190 sitting190 agent190 angle190 universe190 memory190", 28),
        ["kitten190 sitting190", "agent190 angle190", "universe190 memory190"],
    ),
    (
        ("sitting190 agent190 angle190 universe190 memory190 stream190", 6),
        ["sitting190", "agent190", "angle190", "universe190", "memory190", "stream190"],
    ),
    (
        ("sitting190 agent190 angle190 universe190 memory190 stream190", 10),
        ["sitting190", "agent190", "angle190", "universe190", "memory190", "stream190"],
    ),
    (
        ("sitting190 agent190 angle190 universe190 memory190 stream190", 18),
        ["sitting190", "agent190 angle190", "universe190", "memory190", "stream190"],
    ),
    (
        ("sitting190 agent190 angle190 universe190 memory190 stream190", 28),
        ["sitting190 agent190 angle190", "universe190 memory190", "stream190"],
    ),
    (
        ("agent190 angle190 universe190 memory190 stream190 context190", 6),
        ["agent190", "angle190", "universe190", "memory190", "stream190", "context190"],
    ),
    (
        ("agent190 angle190 universe190 memory190 stream190 context190", 10),
        ["agent190", "angle190", "universe190", "memory190", "stream190", "context190"],
    ),
    (
        ("agent190 angle190 universe190 memory190 stream190 context190", 18),
        ["agent190 angle190", "universe190", "memory190", "stream190", "context190"],
    ),
    (
        ("agent190 angle190 universe190 memory190 stream190 context190", 28),
        ["agent190 angle190", "universe190 memory190", "stream190 context190"],
    ),
    (
        ("angle190 universe190 memory190 stream190 context190 knowledge190", 6),
        ["angle190", "universe190", "memory190", "stream190", "context190", "knowledge190"],
    ),
    (
        ("angle190 universe190 memory190 stream190 context190 knowledge190", 10),
        ["angle190", "universe190", "memory190", "stream190", "context190", "knowledge190"],
    ),
    (
        ("angle190 universe190 memory190 stream190 context190 knowledge190", 18),
        ["angle190", "universe190", "memory190", "stream190", "context190", "knowledge190"],
    ),
    (
        ("angle190 universe190 memory190 stream190 context190 knowledge190", 28),
        ["angle190 universe190", "memory190 stream190", "context190 knowledge190"],
    ),
    (
        ("universe190 memory190 stream190 context190 knowledge190 vector190", 6),
        ["universe190", "memory190", "stream190", "context190", "knowledge190", "vector190"],
    ),
    (
        ("universe190 memory190 stream190 context190 knowledge190 vector190", 10),
        ["universe190", "memory190", "stream190", "context190", "knowledge190", "vector190"],
    ),
    (
        ("universe190 memory190 stream190 context190 knowledge190 vector190", 18),
        ["universe190", "memory190", "stream190", "context190", "knowledge190", "vector190"],
    ),
    (
        ("universe190 memory190 stream190 context190 knowledge190 vector190", 28),
        ["universe190 memory190", "stream190 context190", "knowledge190 vector190"],
    ),
    (
        ("memory190 stream190 context190 knowledge190 vector190 processor190", 6),
        ["memory190", "stream190", "context190", "knowledge190", "vector190", "processor190"],
    ),
    (
        ("memory190 stream190 context190 knowledge190 vector190 processor190", 10),
        ["memory190", "stream190", "context190", "knowledge190", "vector190", "processor190"],
    ),
    (
        ("memory190 stream190 context190 knowledge190 vector190 processor190", 18),
        ["memory190", "stream190", "context190", "knowledge190", "vector190", "processor190"],
    ),
    (
        ("memory190 stream190 context190 knowledge190 vector190 processor190", 28),
        ["memory190 stream190", "context190 knowledge190", "vector190 processor190"],
    ),
    (
        ("stream190 context190 knowledge190 vector190 processor190 reasoning190", 6),
        ["stream190", "context190", "knowledge190", "vector190", "processor190", "reasoning190"],
    ),
    (
        ("stream190 context190 knowledge190 vector190 processor190 reasoning190", 10),
        ["stream190", "context190", "knowledge190", "vector190", "processor190", "reasoning190"],
    ),
    (
        ("stream190 context190 knowledge190 vector190 processor190 reasoning190", 18),
        ["stream190", "context190", "knowledge190", "vector190", "processor190", "reasoning190"],
    ),
    (
        ("stream190 context190 knowledge190 vector190 processor190 reasoning190", 28),
        ["stream190 context190", "knowledge190 vector190", "processor190 reasoning190"],
    ),
    (
        ("context190 knowledge190 vector190 processor190 reasoning190 machine190", 6),
        ["context190", "knowledge190", "vector190", "processor190", "reasoning190", "machine190"],
    ),
    (
        ("context190 knowledge190 vector190 processor190 reasoning190 machine190", 10),
        ["context190", "knowledge190", "vector190", "processor190", "reasoning190", "machine190"],
    ),
    (
        ("context190 knowledge190 vector190 processor190 reasoning190 machine190", 18),
        ["context190", "knowledge190", "vector190", "processor190", "reasoning190", "machine190"],
    ),
    (
        ("context190 knowledge190 vector190 processor190 reasoning190 machine190", 28),
        ["context190 knowledge190", "vector190 processor190", "reasoning190 machine190"],
    ),
    (
        ("knowledge190 vector190 processor190 reasoning190 machine190 learning190", 6),
        ["knowledge190", "vector190", "processor190", "reasoning190", "machine190", "learning190"],
    ),
    (
        ("knowledge190 vector190 processor190 reasoning190 machine190 learning190", 10),
        ["knowledge190", "vector190", "processor190", "reasoning190", "machine190", "learning190"],
    ),
    (
        ("knowledge190 vector190 processor190 reasoning190 machine190 learning190", 18),
        ["knowledge190", "vector190", "processor190", "reasoning190", "machine190", "learning190"],
    ),
    (
        ("knowledge190 vector190 processor190 reasoning190 machine190 learning190", 28),
        ["knowledge190 vector190", "processor190 reasoning190", "machine190 learning190"],
    ),
    (
        ("vector190 processor190 reasoning190 machine190 learning190 model190", 6),
        ["vector190", "processor190", "reasoning190", "machine190", "learning190", "model190"],
    ),
    (
        ("vector190 processor190 reasoning190 machine190 learning190 model190", 10),
        ["vector190", "processor190", "reasoning190", "machine190", "learning190", "model190"],
    ),
    (
        ("vector190 processor190 reasoning190 machine190 learning190 model190", 18),
        ["vector190", "processor190", "reasoning190", "machine190", "learning190", "model190"],
    ),
    (
        ("vector190 processor190 reasoning190 machine190 learning190 model190", 28),
        ["vector190 processor190", "reasoning190 machine190", "learning190 model190"],
    ),
    (
        ("processor190 reasoning190 machine190 learning190 model190 token190", 6),
        ["processor190", "reasoning190", "machine190", "learning190", "model190", "token190"],
    ),
    (
        ("processor190 reasoning190 machine190 learning190 model190 token190", 10),
        ["processor190", "reasoning190", "machine190", "learning190", "model190", "token190"],
    ),
    (
        ("processor190 reasoning190 machine190 learning190 model190 token190", 18),
        ["processor190", "reasoning190", "machine190", "learning190", "model190 token190"],
    ),
    (
        ("processor190 reasoning190 machine190 learning190 model190 token190", 28),
        ["processor190 reasoning190", "machine190 learning190", "model190 token190"],
    ),
    (
        ("reasoning190 machine190 learning190 model190 token190 prompt190", 6),
        ["reasoning190", "machine190", "learning190", "model190", "token190", "prompt190"],
    ),
    (
        ("reasoning190 machine190 learning190 model190 token190 prompt190", 10),
        ["reasoning190", "machine190", "learning190", "model190", "token190", "prompt190"],
    ),
    (
        ("reasoning190 machine190 learning190 model190 token190 prompt190", 18),
        ["reasoning190", "machine190", "learning190", "model190 token190", "prompt190"],
    ),
    (
        ("reasoning190 machine190 learning190 model190 token190 prompt190", 28),
        ["reasoning190 machine190", "learning190 model190", "token190 prompt190"],
    ),
    (
        ("machine190 learning190 model190 token190 prompt190 session190", 6),
        ["machine190", "learning190", "model190", "token190", "prompt190", "session190"],
    ),
    (
        ("machine190 learning190 model190 token190 prompt190 session190", 10),
        ["machine190", "learning190", "model190", "token190", "prompt190", "session190"],
    ),
    (
        ("machine190 learning190 model190 token190 prompt190 session190", 18),
        ["machine190", "learning190", "model190 token190", "prompt190", "session190"],
    ),
    (
        ("machine190 learning190 model190 token190 prompt190 session190", 28),
        ["machine190 learning190", "model190 token190 prompt190", "session190"],
    ),
    (
        ("learning190 model190 token190 prompt190 session190 library190", 6),
        ["learning190", "model190", "token190", "prompt190", "session190", "library190"],
    ),
    (
        ("learning190 model190 token190 prompt190 session190 library190", 10),
        ["learning190", "model190", "token190", "prompt190", "session190", "library190"],
    ),
    (
        ("learning190 model190 token190 prompt190 session190 library190", 18),
        ["learning190", "model190 token190", "prompt190", "session190", "library190"],
    ),
    (
        ("learning190 model190 token190 prompt190 session190 library190", 28),
        ["learning190 model190", "token190 prompt190", "session190 library190"],
    ),
    (
        ("model190 token190 prompt190 session190 library190 service190", 6),
        ["model190", "token190", "prompt190", "session190", "library190", "service190"],
    ),
    (
        ("model190 token190 prompt190 session190 library190 service190", 10),
        ["model190", "token190", "prompt190", "session190", "library190", "service190"],
    ),
    (
        ("model190 token190 prompt190 session190 library190 service190", 18),
        ["model190 token190", "prompt190", "session190", "library190", "service190"],
    ),
    (
        ("model190 token190 prompt190 session190 library190 service190", 28),
        ["model190 token190 prompt190", "session190 library190", "service190"],
    ),
    (
        ("token190 prompt190 session190 library190 service190 gateway190", 6),
        ["token190", "prompt190", "session190", "library190", "service190", "gateway190"],
    ),
    (
        ("token190 prompt190 session190 library190 service190 gateway190", 10),
        ["token190", "prompt190", "session190", "library190", "service190", "gateway190"],
    ),
    (
        ("token190 prompt190 session190 library190 service190 gateway190", 18),
        ["token190 prompt190", "session190", "library190", "service190", "gateway190"],
    ),
    (
        ("token190 prompt190 session190 library190 service190 gateway190", 28),
        ["token190 prompt190", "session190 library190", "service190 gateway190"],
    ),
    (
        ("prompt190 session190 library190 service190 gateway190 storage190", 6),
        ["prompt190", "session190", "library190", "service190", "gateway190", "storage190"],
    ),
    (
        ("prompt190 session190 library190 service190 gateway190 storage190", 10),
        ["prompt190", "session190", "library190", "service190", "gateway190", "storage190"],
    ),
    (
        ("prompt190 session190 library190 service190 gateway190 storage190", 18),
        ["prompt190", "session190", "library190", "service190", "gateway190", "storage190"],
    ),
    (
        ("prompt190 session190 library190 service190 gateway190 storage190", 28),
        ["prompt190 session190", "library190 service190", "gateway190 storage190"],
    ),
    (
        ("session190 library190 service190 gateway190 storage190 network190", 6),
        ["session190", "library190", "service190", "gateway190", "storage190", "network190"],
    ),
    (
        ("session190 library190 service190 gateway190 storage190 network190", 10),
        ["session190", "library190", "service190", "gateway190", "storage190", "network190"],
    ),
    (
        ("session190 library190 service190 gateway190 storage190 network190", 18),
        ["session190", "library190", "service190", "gateway190", "storage190", "network190"],
    ),
    (
        ("session190 library190 service190 gateway190 storage190 network190", 28),
        ["session190 library190", "service190 gateway190", "storage190 network190"],
    ),
    (
        ("library190 service190 gateway190 storage190 network190 latency190", 6),
        ["library190", "service190", "gateway190", "storage190", "network190", "latency190"],
    ),
    (
        ("library190 service190 gateway190 storage190 network190 latency190", 10),
        ["library190", "service190", "gateway190", "storage190", "network190", "latency190"],
    ),
    (
        ("library190 service190 gateway190 storage190 network190 latency190", 18),
        ["library190", "service190", "gateway190", "storage190", "network190", "latency190"],
    ),
    (
        ("library190 service190 gateway190 storage190 network190 latency190", 28),
        ["library190 service190", "gateway190 storage190", "network190 latency190"],
    ),
    (
        ("service190 gateway190 storage190 network190 latency190 buffer190", 6),
        ["service190", "gateway190", "storage190", "network190", "latency190", "buffer190"],
    ),
    (
        ("service190 gateway190 storage190 network190 latency190 buffer190", 10),
        ["service190", "gateway190", "storage190", "network190", "latency190", "buffer190"],
    ),
    (
        ("service190 gateway190 storage190 network190 latency190 buffer190", 18),
        ["service190", "gateway190", "storage190", "network190", "latency190", "buffer190"],
    ),
    (
        ("service190 gateway190 storage190 network190 latency190 buffer190", 28),
        ["service190 gateway190", "storage190 network190", "latency190 buffer190"],
    ),
    (
        ("gateway190 storage190 network190 latency190 buffer190 queue190", 6),
        ["gateway190", "storage190", "network190", "latency190", "buffer190", "queue190"],
    ),
    (
        ("gateway190 storage190 network190 latency190 buffer190 queue190", 10),
        ["gateway190", "storage190", "network190", "latency190", "buffer190", "queue190"],
    ),
    (
        ("gateway190 storage190 network190 latency190 buffer190 queue190", 18),
        ["gateway190", "storage190", "network190", "latency190", "buffer190 queue190"],
    ),
    (
        ("gateway190 storage190 network190 latency190 buffer190 queue190", 28),
        ["gateway190 storage190", "network190 latency190", "buffer190 queue190"],
    ),
    (
        ("storage190 network190 latency190 buffer190 queue190 worker190", 6),
        ["storage190", "network190", "latency190", "buffer190", "queue190", "worker190"],
    ),
    (
        ("storage190 network190 latency190 buffer190 queue190 worker190", 10),
        ["storage190", "network190", "latency190", "buffer190", "queue190", "worker190"],
    ),
    (
        ("storage190 network190 latency190 buffer190 queue190 worker190", 18),
        ["storage190", "network190", "latency190", "buffer190 queue190", "worker190"],
    ),
    (
        ("storage190 network190 latency190 buffer190 queue190 worker190", 28),
        ["storage190 network190", "latency190 buffer190", "queue190 worker190"],
    ),
    (
        ("network190 latency190 buffer190 queue190 worker190 kernel190", 6),
        ["network190", "latency190", "buffer190", "queue190", "worker190", "kernel190"],
    ),
    (
        ("network190 latency190 buffer190 queue190 worker190 kernel190", 10),
        ["network190", "latency190", "buffer190", "queue190", "worker190", "kernel190"],
    ),
    (
        ("network190 latency190 buffer190 queue190 worker190 kernel190", 18),
        ["network190", "latency190", "buffer190 queue190", "worker190", "kernel190"],
    ),
    (
        ("network190 latency190 buffer190 queue190 worker190 kernel190", 28),
        ["network190 latency190", "buffer190 queue190 worker190", "kernel190"],
    ),
    (
        ("latency190 buffer190 queue190 worker190 kernel190 signal190", 6),
        ["latency190", "buffer190", "queue190", "worker190", "kernel190", "signal190"],
    ),
    (
        ("latency190 buffer190 queue190 worker190 kernel190 signal190", 10),
        ["latency190", "buffer190", "queue190", "worker190", "kernel190", "signal190"],
    ),
    (
        ("latency190 buffer190 queue190 worker190 kernel190 signal190", 18),
        ["latency190", "buffer190 queue190", "worker190", "kernel190", "signal190"],
    ),
    (
        ("latency190 buffer190 queue190 worker190 kernel190 signal190", 28),
        ["latency190 buffer190", "queue190 worker190 kernel190", "signal190"],
    ),
    (
        ("buffer190 queue190 worker190 kernel190 signal190 packet190", 6),
        ["buffer190", "queue190", "worker190", "kernel190", "signal190", "packet190"],
    ),
    (
        ("buffer190 queue190 worker190 kernel190 signal190 packet190", 10),
        ["buffer190", "queue190", "worker190", "kernel190", "signal190", "packet190"],
    ),
    (
        ("buffer190 queue190 worker190 kernel190 signal190 packet190", 18),
        ["buffer190 queue190", "worker190", "kernel190", "signal190", "packet190"],
    ),
    (
        ("buffer190 queue190 worker190 kernel190 signal190 packet190", 28),
        ["buffer190 queue190 worker190", "kernel190 signal190", "packet190"],
    ),
    (
        ("queue190 worker190 kernel190 signal190 packet190 router190", 6),
        ["queue190", "worker190", "kernel190", "signal190", "packet190", "router190"],
    ),
    (
        ("queue190 worker190 kernel190 signal190 packet190 router190", 10),
        ["queue190", "worker190", "kernel190", "signal190", "packet190", "router190"],
    ),
    (
        ("queue190 worker190 kernel190 signal190 packet190 router190", 18),
        ["queue190 worker190", "kernel190", "signal190", "packet190", "router190"],
    ),
    (
        ("queue190 worker190 kernel190 signal190 packet190 router190", 28),
        ["queue190 worker190 kernel190", "signal190 packet190", "router190"],
    ),
    (
        ("worker190 kernel190 signal190 packet190 router190 cluster190", 6),
        ["worker190", "kernel190", "signal190", "packet190", "router190", "cluster190"],
    ),
    (
        ("worker190 kernel190 signal190 packet190 router190 cluster190", 10),
        ["worker190", "kernel190", "signal190", "packet190", "router190", "cluster190"],
    ),
    (
        ("worker190 kernel190 signal190 packet190 router190 cluster190", 18),
        ["worker190", "kernel190", "signal190", "packet190", "router190", "cluster190"],
    ),
    (
        ("worker190 kernel190 signal190 packet190 router190 cluster190", 28),
        ["worker190 kernel190", "signal190 packet190", "router190 cluster190"],
    ),
    (
        ("kernel190 signal190 packet190 router190 cluster190 mirror190", 6),
        ["kernel190", "signal190", "packet190", "router190", "cluster190", "mirror190"],
    ),
    (
        ("kernel190 signal190 packet190 router190 cluster190 mirror190", 10),
        ["kernel190", "signal190", "packet190", "router190", "cluster190", "mirror190"],
    ),
    (
        ("kernel190 signal190 packet190 router190 cluster190 mirror190", 18),
        ["kernel190", "signal190", "packet190", "router190", "cluster190", "mirror190"],
    ),
    (
        ("kernel190 signal190 packet190 router190 cluster190 mirror190", 28),
        ["kernel190 signal190", "packet190 router190", "cluster190 mirror190"],
    ),
    (
        ("signal190 packet190 router190 cluster190 mirror190 filter190", 6),
        ["signal190", "packet190", "router190", "cluster190", "mirror190", "filter190"],
    ),
    (
        ("signal190 packet190 router190 cluster190 mirror190 filter190", 10),
        ["signal190", "packet190", "router190", "cluster190", "mirror190", "filter190"],
    ),
    (
        ("signal190 packet190 router190 cluster190 mirror190 filter190", 18),
        ["signal190", "packet190", "router190", "cluster190", "mirror190", "filter190"],
    ),
    (
        ("signal190 packet190 router190 cluster190 mirror190 filter190", 28),
        ["signal190 packet190", "router190 cluster190", "mirror190 filter190"],
    ),
    (
        ("packet190 router190 cluster190 mirror190 filter190 ranking190", 6),
        ["packet190", "router190", "cluster190", "mirror190", "filter190", "ranking190"],
    ),
    (
        ("packet190 router190 cluster190 mirror190 filter190 ranking190", 10),
        ["packet190", "router190", "cluster190", "mirror190", "filter190", "ranking190"],
    ),
    (
        ("packet190 router190 cluster190 mirror190 filter190 ranking190", 18),
        ["packet190", "router190", "cluster190", "mirror190", "filter190", "ranking190"],
    ),
    (
        ("packet190 router190 cluster190 mirror190 filter190 ranking190", 28),
        ["packet190 router190", "cluster190 mirror190", "filter190 ranking190"],
    ),
    (
        ("router190 cluster190 mirror190 filter190 ranking190 encoding190", 6),
        ["router190", "cluster190", "mirror190", "filter190", "ranking190", "encoding190"],
    ),
    (
        ("router190 cluster190 mirror190 filter190 ranking190 encoding190", 10),
        ["router190", "cluster190", "mirror190", "filter190", "ranking190", "encoding190"],
    ),
    (
        ("router190 cluster190 mirror190 filter190 ranking190 encoding190", 18),
        ["router190", "cluster190", "mirror190", "filter190", "ranking190", "encoding190"],
    ),
    (
        ("router190 cluster190 mirror190 filter190 ranking190 encoding190", 28),
        ["router190 cluster190", "mirror190 filter190", "ranking190 encoding190"],
    ),
    (
        ("cluster190 mirror190 filter190 ranking190 encoding190 mapping190", 6),
        ["cluster190", "mirror190", "filter190", "ranking190", "encoding190", "mapping190"],
    ),
    (
        ("cluster190 mirror190 filter190 ranking190 encoding190 mapping190", 10),
        ["cluster190", "mirror190", "filter190", "ranking190", "encoding190", "mapping190"],
    ),
    (
        ("cluster190 mirror190 filter190 ranking190 encoding190 mapping190", 18),
        ["cluster190", "mirror190", "filter190", "ranking190", "encoding190", "mapping190"],
    ),
    (
        ("cluster190 mirror190 filter190 ranking190 encoding190 mapping190", 28),
        ["cluster190 mirror190", "filter190 ranking190", "encoding190 mapping190"],
    ),
    (
        ("mirror190 filter190 ranking190 encoding190 mapping190 record190", 6),
        ["mirror190", "filter190", "ranking190", "encoding190", "mapping190", "record190"],
    ),
    (
        ("mirror190 filter190 ranking190 encoding190 mapping190 record190", 10),
        ["mirror190", "filter190", "ranking190", "encoding190", "mapping190", "record190"],
    ),
    (
        ("mirror190 filter190 ranking190 encoding190 mapping190 record190", 18),
        ["mirror190", "filter190", "ranking190", "encoding190", "mapping190", "record190"],
    ),
    (
        ("mirror190 filter190 ranking190 encoding190 mapping190 record190", 28),
        ["mirror190 filter190", "ranking190 encoding190", "mapping190 record190"],
    ),
    (
        ("filter190 ranking190 encoding190 mapping190 record190 candle190", 6),
        ["filter190", "ranking190", "encoding190", "mapping190", "record190", "candle190"],
    ),
    (
        ("filter190 ranking190 encoding190 mapping190 record190 candle190", 10),
        ["filter190", "ranking190", "encoding190", "mapping190", "record190", "candle190"],
    ),
    (
        ("filter190 ranking190 encoding190 mapping190 record190 candle190", 18),
        ["filter190", "ranking190", "encoding190", "mapping190", "record190", "candle190"],
    ),
    (
        ("filter190 ranking190 encoding190 mapping190 record190 candle190", 28),
        ["filter190 ranking190", "encoding190 mapping190", "record190 candle190"],
    ),
    (
        ("ranking190 encoding190 mapping190 record190 candle190 thread190", 6),
        ["ranking190", "encoding190", "mapping190", "record190", "candle190", "thread190"],
    ),
    (
        ("ranking190 encoding190 mapping190 record190 candle190 thread190", 10),
        ["ranking190", "encoding190", "mapping190", "record190", "candle190", "thread190"],
    ),
    (
        ("ranking190 encoding190 mapping190 record190 candle190 thread190", 18),
        ["ranking190", "encoding190", "mapping190", "record190", "candle190", "thread190"],
    ),
    (
        ("ranking190 encoding190 mapping190 record190 candle190 thread190", 28),
        ["ranking190 encoding190", "mapping190 record190", "candle190 thread190"],
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
