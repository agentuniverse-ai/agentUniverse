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
        ("round 195: the quick brown fox jumps over the lazy dog", 4),
        ["round", "195:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", 8),
        ["round", "195: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", 12),
        ["round 195:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", 16),
        ["round 195: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", 24),
        ["round 195: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 195: the quick brown fox jumps over the lazy dog", 32),
        ["round 195: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", 4),
        ["round", "195:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", 8),
        ["round", "195:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", 12),
        ["round 195:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", 16),
        ["round 195:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", 24),
        ["round 195: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 195: agentuniverse is a framework for multi agents", 32),
        ["round 195: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", 4),
        ["round", "195:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", 8),
        ["round", "195:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", 12),
        ["round 195:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", 16),
        ["round 195:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", 24),
        ["round 195: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 195: knowledge stored as vectors enables retrieval", 32),
        ["round 195: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 195: the processor reads the record then stops", 4),
        ["round", "195:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 195: the processor reads the record then stops", 8),
        ["round", "195: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 195: the processor reads the record then stops", 12),
        ["round 195:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 195: the processor reads the record then stops", 16),
        ["round 195: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 195: the processor reads the record then stops", 24),
        ["round 195: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 195: the processor reads the record then stops", 32),
        ["round 195: the processor reads", "the record then stops"],
    ),
    (
        ("round 195: a worker pulls the next task from the queue", 4),
        ["round", "195:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 195: a worker pulls the next task from the queue", 8),
        ["round", "195: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 195: a worker pulls the next task from the queue", 12),
        ["round 195: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 195: a worker pulls the next task from the queue", 16),
        ["round 195: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 195: a worker pulls the next task from the queue", 24),
        ["round 195: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 195: a worker pulls the next task from the queue", 32),
        ["round 195: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 195: signals travel through the network layer", 4),
        ["round", "195:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 195: signals travel through the network layer", 8),
        ["round", "195:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 195: signals travel through the network layer", 12),
        ["round 195:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 195: signals travel through the network layer", 16),
        ["round 195:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 195: signals travel through the network layer", 24),
        ["round 195: signals", "travel through the", "network layer"],
    ),
    (
        ("round 195: signals travel through the network layer", 32),
        ["round 195: signals travel", "through the network layer"],
    ),
    (
        ("round 195: the gateway routes each request by policy", 4),
        ["round", "195:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 195: the gateway routes each request by policy", 8),
        ["round", "195: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 195: the gateway routes each request by policy", 12),
        ["round 195:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 195: the gateway routes each request by policy", 16),
        ["round 195: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 195: the gateway routes each request by policy", 24),
        ["round 195: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 195: the gateway routes each request by policy", 32),
        ["round 195: the gateway routes", "each request by policy"],
    ),
    (
        ("round 195: memory grows until the buffer is full", 4),
        ["round", "195:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 195: memory grows until the buffer is full", 8),
        ["round", "195:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 195: memory grows until the buffer is full", 12),
        ["round 195:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 195: memory grows until the buffer is full", 16),
        ["round 195:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 195: memory grows until the buffer is full", 24), ["round 195: memory grows", "until the buffer is full"]),
    (("round 195: memory grows until the buffer is full", 32), ["round 195: memory grows until", "the buffer is full"]),
    (
        ("round 195: the cluster mirrors every packet twice", 4),
        ["round", "195:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 195: the cluster mirrors every packet twice", 8),
        ["round", "195: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 195: the cluster mirrors every packet twice", 12),
        ["round 195:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 195: the cluster mirrors every packet twice", 16),
        ["round 195: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 195: the cluster mirrors every packet twice", 24),
        ["round 195: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 195: the cluster mirrors every packet twice", 32),
        ["round 195: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", 4),
        ["round", "195:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", 8),
        ["round", "195:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", 12),
        ["round 195:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", 16),
        ["round 195:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", 24),
        ["round 195: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 195: ranking uses tokens learned from the corpus", 32),
        ["round 195: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 195: a long session ends when the candle dies", 4),
        ["round", "195:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 195: a long session ends when the candle dies", 8),
        ["round", "195: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 195: a long session ends when the candle dies", 12),
        ["round 195: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 195: a long session ends when the candle dies", 16),
        ["round 195: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 195: a long session ends when the candle dies", 24),
        ["round 195: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 195: a long session ends when the candle dies", 32),
        ["round 195: a long session ends", "when the candle dies"],
    ),
    (
        ("round 195: encode the prompt then map the result", 4),
        ["round", "195:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 195: encode the prompt then map the result", 8),
        ["round", "195:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 195: encode the prompt then map the result", 12),
        ["round 195:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 195: encode the prompt then map the result", 16),
        ["round 195:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 195: encode the prompt then map the result", 24),
        ["round 195: encode the", "prompt then map the", "result"],
    ),
    (("round 195: encode the prompt then map the result", 32), ["round 195: encode the prompt", "then map the result"]),
    (
        ("round 195: the kernel wakes the worker at dawn", 4),
        ["round", "195:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 195: the kernel wakes the worker at dawn", 8),
        ["round", "195: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 195: the kernel wakes the worker at dawn", 12),
        ["round 195:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 195: the kernel wakes the worker at dawn", 16), ["round 195: the", "kernel wakes the", "worker at dawn"]),
    (("round 195: the kernel wakes the worker at dawn", 24), ["round 195: the kernel", "wakes the worker at dawn"]),
    (("round 195: the kernel wakes the worker at dawn", 32), ["round 195: the kernel wakes the", "worker at dawn"]),
    (
        ("round 195: service latency drops after the patch", 4),
        ["round", "195:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 195: service latency drops after the patch", 8),
        ["round", "195:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 195: service latency drops after the patch", 12),
        ["round 195:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 195: service latency drops after the patch", 16),
        ["round 195:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 195: service latency drops after the patch", 24),
        ["round 195: service", "latency drops after the", "patch"],
    ),
    (("round 195: service latency drops after the patch", 32), ["round 195: service latency drops", "after the patch"]),
    (
        ("round 195: the library caches every vector it sees", 4),
        ["round", "195:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 195: the library caches every vector it sees", 8),
        ["round", "195: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 195: the library caches every vector it sees", 12),
        ["round 195:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 195: the library caches every vector it sees", 16),
        ["round 195: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 195: the library caches every vector it sees", 24),
        ["round 195: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 195: the library caches every vector it sees", 32),
        ["round 195: the library caches", "every vector it sees"],
    ),
    (
        ("round 195: agents argue then the debate resolves", 4),
        ["round", "195:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 195: agents argue then the debate resolves", 8),
        ["round", "195:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 195: agents argue then the debate resolves", 12),
        ["round 195:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 195: agents argue then the debate resolves", 16),
        ["round 195:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 195: agents argue then the debate resolves", 24), ["round 195: agents argue", "then the debate resolves"]),
    (("round 195: agents argue then the debate resolves", 32), ["round 195: agents argue then the", "debate resolves"]),
    (
        ("round 195: the filter keeps only strong matches", 4),
        ["round", "195:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 195: the filter keeps only strong matches", 8),
        ["round", "195: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 195: the filter keeps only strong matches", 12),
        ["round 195:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 195: the filter keeps only strong matches", 16),
        ["round 195: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 195: the filter keeps only strong matches", 24),
        ["round 195: the filter", "keeps only strong", "matches"],
    ),
    (("round 195: the filter keeps only strong matches", 32), ["round 195: the filter keeps only", "strong matches"]),
    (
        ("round 195: the model answers with a short reply", 4),
        ["round", "195:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 195: the model answers with a short reply", 8),
        ["round", "195: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 195: the model answers with a short reply", 12),
        ["round 195:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 195: the model answers with a short reply", 16),
        ["round 195: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 195: the model answers with a short reply", 24),
        ["round 195: the model", "answers with a short", "reply"],
    ),
    (("round 195: the model answers with a short reply", 32), ["round 195: the model answers", "with a short reply"]),
    (
        ("round 195: the recorder stores the reasoning trace", 4),
        ["round", "195:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 195: the recorder stores the reasoning trace", 8),
        ["round", "195: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 195: the recorder stores the reasoning trace", 12),
        ["round 195:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 195: the recorder stores the reasoning trace", 16),
        ["round 195: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 195: the recorder stores the reasoning trace", 24),
        ["round 195: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 195: the recorder stores the reasoning trace", 32),
        ["round 195: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 195: the angel watches the processor run", 4),
        ["round", "195:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 195: the angel watches the processor run", 8),
        ["round", "195: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 195: the angel watches the processor run", 12),
        ["round 195:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 195: the angel watches the processor run", 16),
        ["round 195: the", "angel watches", "the processor", "run"],
    ),
    (("round 195: the angel watches the processor run", 24), ["round 195: the angel", "watches the processor", "run"]),
    (("round 195: the angel watches the processor run", 32), ["round 195: the angel watches the", "processor run"]),
    (
        ("round 195: angle of the vector decides the match", 4),
        ["round", "195:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 195: angle of the vector decides the match", 8),
        ["round", "195:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 195: angle of the vector decides the match", 12),
        ["round 195:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 195: angle of the vector decides the match", 16),
        ["round 195: angle", "of the vector", "decides the", "match"],
    ),
    (("round 195: angle of the vector decides the match", 24), ["round 195: angle of the", "vector decides the match"]),
    (("round 195: angle of the vector decides the match", 32), ["round 195: angle of the vector", "decides the match"]),
    (
        ("round 195: the candle burns twice as long at night", 4),
        ["round", "195:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 195: the candle burns twice as long at night", 8),
        ["round", "195: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 195: the candle burns twice as long at night", 12),
        ["round 195:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 195: the candle burns twice as long at night", 16),
        ["round 195: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 195: the candle burns twice as long at night", 24),
        ["round 195: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 195: the candle burns twice as long at night", 32),
        ["round 195: the candle burns", "twice as long at night"],
    ),
    (
        ("round 195: a mirror of the universe in one line", 4),
        ["round", "195:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 195: a mirror of the universe in one line", 8),
        ["round", "195: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 195: a mirror of the universe in one line", 12),
        ["round 195: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 195: a mirror of the universe in one line", 16),
        ["round 195: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 195: a mirror of the universe in one line", 24), ["round 195: a mirror of", "the universe in one line"]),
    (("round 195: a mirror of the universe in one line", 32), ["round 195: a mirror of the", "universe in one line"]),
    (
        ("round 195: the queue drains before the storm", 4),
        ["round", "195:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 195: the queue drains before the storm", 8),
        ["round", "195: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 195: the queue drains before the storm", 12),
        ["round 195:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 195: the queue drains before the storm", 16), ["round 195: the", "queue drains", "before the storm"]),
    (("round 195: the queue drains before the storm", 24), ["round 195: the queue", "drains before the storm"]),
    (("round 195: the queue drains before the storm", 32), ["round 195: the queue drains", "before the storm"]),
    (
        ("kitten195 sitting195 agent195 angle195 universe195 memory195", 6),
        ["kitten195", "sitting195", "agent195", "angle195", "universe195", "memory195"],
    ),
    (
        ("kitten195 sitting195 agent195 angle195 universe195 memory195", 10),
        ["kitten195", "sitting195", "agent195", "angle195", "universe195", "memory195"],
    ),
    (
        ("kitten195 sitting195 agent195 angle195 universe195 memory195", 18),
        ["kitten195", "sitting195", "agent195 angle195", "universe195", "memory195"],
    ),
    (
        ("kitten195 sitting195 agent195 angle195 universe195 memory195", 28),
        ["kitten195 sitting195", "agent195 angle195", "universe195 memory195"],
    ),
    (
        ("sitting195 agent195 angle195 universe195 memory195 stream195", 6),
        ["sitting195", "agent195", "angle195", "universe195", "memory195", "stream195"],
    ),
    (
        ("sitting195 agent195 angle195 universe195 memory195 stream195", 10),
        ["sitting195", "agent195", "angle195", "universe195", "memory195", "stream195"],
    ),
    (
        ("sitting195 agent195 angle195 universe195 memory195 stream195", 18),
        ["sitting195", "agent195 angle195", "universe195", "memory195", "stream195"],
    ),
    (
        ("sitting195 agent195 angle195 universe195 memory195 stream195", 28),
        ["sitting195 agent195 angle195", "universe195 memory195", "stream195"],
    ),
    (
        ("agent195 angle195 universe195 memory195 stream195 context195", 6),
        ["agent195", "angle195", "universe195", "memory195", "stream195", "context195"],
    ),
    (
        ("agent195 angle195 universe195 memory195 stream195 context195", 10),
        ["agent195", "angle195", "universe195", "memory195", "stream195", "context195"],
    ),
    (
        ("agent195 angle195 universe195 memory195 stream195 context195", 18),
        ["agent195 angle195", "universe195", "memory195", "stream195", "context195"],
    ),
    (
        ("agent195 angle195 universe195 memory195 stream195 context195", 28),
        ["agent195 angle195", "universe195 memory195", "stream195 context195"],
    ),
    (
        ("angle195 universe195 memory195 stream195 context195 knowledge195", 6),
        ["angle195", "universe195", "memory195", "stream195", "context195", "knowledge195"],
    ),
    (
        ("angle195 universe195 memory195 stream195 context195 knowledge195", 10),
        ["angle195", "universe195", "memory195", "stream195", "context195", "knowledge195"],
    ),
    (
        ("angle195 universe195 memory195 stream195 context195 knowledge195", 18),
        ["angle195", "universe195", "memory195", "stream195", "context195", "knowledge195"],
    ),
    (
        ("angle195 universe195 memory195 stream195 context195 knowledge195", 28),
        ["angle195 universe195", "memory195 stream195", "context195 knowledge195"],
    ),
    (
        ("universe195 memory195 stream195 context195 knowledge195 vector195", 6),
        ["universe195", "memory195", "stream195", "context195", "knowledge195", "vector195"],
    ),
    (
        ("universe195 memory195 stream195 context195 knowledge195 vector195", 10),
        ["universe195", "memory195", "stream195", "context195", "knowledge195", "vector195"],
    ),
    (
        ("universe195 memory195 stream195 context195 knowledge195 vector195", 18),
        ["universe195", "memory195", "stream195", "context195", "knowledge195", "vector195"],
    ),
    (
        ("universe195 memory195 stream195 context195 knowledge195 vector195", 28),
        ["universe195 memory195", "stream195 context195", "knowledge195 vector195"],
    ),
    (
        ("memory195 stream195 context195 knowledge195 vector195 processor195", 6),
        ["memory195", "stream195", "context195", "knowledge195", "vector195", "processor195"],
    ),
    (
        ("memory195 stream195 context195 knowledge195 vector195 processor195", 10),
        ["memory195", "stream195", "context195", "knowledge195", "vector195", "processor195"],
    ),
    (
        ("memory195 stream195 context195 knowledge195 vector195 processor195", 18),
        ["memory195", "stream195", "context195", "knowledge195", "vector195", "processor195"],
    ),
    (
        ("memory195 stream195 context195 knowledge195 vector195 processor195", 28),
        ["memory195 stream195", "context195 knowledge195", "vector195 processor195"],
    ),
    (
        ("stream195 context195 knowledge195 vector195 processor195 reasoning195", 6),
        ["stream195", "context195", "knowledge195", "vector195", "processor195", "reasoning195"],
    ),
    (
        ("stream195 context195 knowledge195 vector195 processor195 reasoning195", 10),
        ["stream195", "context195", "knowledge195", "vector195", "processor195", "reasoning195"],
    ),
    (
        ("stream195 context195 knowledge195 vector195 processor195 reasoning195", 18),
        ["stream195", "context195", "knowledge195", "vector195", "processor195", "reasoning195"],
    ),
    (
        ("stream195 context195 knowledge195 vector195 processor195 reasoning195", 28),
        ["stream195 context195", "knowledge195 vector195", "processor195 reasoning195"],
    ),
    (
        ("context195 knowledge195 vector195 processor195 reasoning195 machine195", 6),
        ["context195", "knowledge195", "vector195", "processor195", "reasoning195", "machine195"],
    ),
    (
        ("context195 knowledge195 vector195 processor195 reasoning195 machine195", 10),
        ["context195", "knowledge195", "vector195", "processor195", "reasoning195", "machine195"],
    ),
    (
        ("context195 knowledge195 vector195 processor195 reasoning195 machine195", 18),
        ["context195", "knowledge195", "vector195", "processor195", "reasoning195", "machine195"],
    ),
    (
        ("context195 knowledge195 vector195 processor195 reasoning195 machine195", 28),
        ["context195 knowledge195", "vector195 processor195", "reasoning195 machine195"],
    ),
    (
        ("knowledge195 vector195 processor195 reasoning195 machine195 learning195", 6),
        ["knowledge195", "vector195", "processor195", "reasoning195", "machine195", "learning195"],
    ),
    (
        ("knowledge195 vector195 processor195 reasoning195 machine195 learning195", 10),
        ["knowledge195", "vector195", "processor195", "reasoning195", "machine195", "learning195"],
    ),
    (
        ("knowledge195 vector195 processor195 reasoning195 machine195 learning195", 18),
        ["knowledge195", "vector195", "processor195", "reasoning195", "machine195", "learning195"],
    ),
    (
        ("knowledge195 vector195 processor195 reasoning195 machine195 learning195", 28),
        ["knowledge195 vector195", "processor195 reasoning195", "machine195 learning195"],
    ),
    (
        ("vector195 processor195 reasoning195 machine195 learning195 model195", 6),
        ["vector195", "processor195", "reasoning195", "machine195", "learning195", "model195"],
    ),
    (
        ("vector195 processor195 reasoning195 machine195 learning195 model195", 10),
        ["vector195", "processor195", "reasoning195", "machine195", "learning195", "model195"],
    ),
    (
        ("vector195 processor195 reasoning195 machine195 learning195 model195", 18),
        ["vector195", "processor195", "reasoning195", "machine195", "learning195", "model195"],
    ),
    (
        ("vector195 processor195 reasoning195 machine195 learning195 model195", 28),
        ["vector195 processor195", "reasoning195 machine195", "learning195 model195"],
    ),
    (
        ("processor195 reasoning195 machine195 learning195 model195 token195", 6),
        ["processor195", "reasoning195", "machine195", "learning195", "model195", "token195"],
    ),
    (
        ("processor195 reasoning195 machine195 learning195 model195 token195", 10),
        ["processor195", "reasoning195", "machine195", "learning195", "model195", "token195"],
    ),
    (
        ("processor195 reasoning195 machine195 learning195 model195 token195", 18),
        ["processor195", "reasoning195", "machine195", "learning195", "model195 token195"],
    ),
    (
        ("processor195 reasoning195 machine195 learning195 model195 token195", 28),
        ["processor195 reasoning195", "machine195 learning195", "model195 token195"],
    ),
    (
        ("reasoning195 machine195 learning195 model195 token195 prompt195", 6),
        ["reasoning195", "machine195", "learning195", "model195", "token195", "prompt195"],
    ),
    (
        ("reasoning195 machine195 learning195 model195 token195 prompt195", 10),
        ["reasoning195", "machine195", "learning195", "model195", "token195", "prompt195"],
    ),
    (
        ("reasoning195 machine195 learning195 model195 token195 prompt195", 18),
        ["reasoning195", "machine195", "learning195", "model195 token195", "prompt195"],
    ),
    (
        ("reasoning195 machine195 learning195 model195 token195 prompt195", 28),
        ["reasoning195 machine195", "learning195 model195", "token195 prompt195"],
    ),
    (
        ("machine195 learning195 model195 token195 prompt195 session195", 6),
        ["machine195", "learning195", "model195", "token195", "prompt195", "session195"],
    ),
    (
        ("machine195 learning195 model195 token195 prompt195 session195", 10),
        ["machine195", "learning195", "model195", "token195", "prompt195", "session195"],
    ),
    (
        ("machine195 learning195 model195 token195 prompt195 session195", 18),
        ["machine195", "learning195", "model195 token195", "prompt195", "session195"],
    ),
    (
        ("machine195 learning195 model195 token195 prompt195 session195", 28),
        ["machine195 learning195", "model195 token195 prompt195", "session195"],
    ),
    (
        ("learning195 model195 token195 prompt195 session195 library195", 6),
        ["learning195", "model195", "token195", "prompt195", "session195", "library195"],
    ),
    (
        ("learning195 model195 token195 prompt195 session195 library195", 10),
        ["learning195", "model195", "token195", "prompt195", "session195", "library195"],
    ),
    (
        ("learning195 model195 token195 prompt195 session195 library195", 18),
        ["learning195", "model195 token195", "prompt195", "session195", "library195"],
    ),
    (
        ("learning195 model195 token195 prompt195 session195 library195", 28),
        ["learning195 model195", "token195 prompt195", "session195 library195"],
    ),
    (
        ("model195 token195 prompt195 session195 library195 service195", 6),
        ["model195", "token195", "prompt195", "session195", "library195", "service195"],
    ),
    (
        ("model195 token195 prompt195 session195 library195 service195", 10),
        ["model195", "token195", "prompt195", "session195", "library195", "service195"],
    ),
    (
        ("model195 token195 prompt195 session195 library195 service195", 18),
        ["model195 token195", "prompt195", "session195", "library195", "service195"],
    ),
    (
        ("model195 token195 prompt195 session195 library195 service195", 28),
        ["model195 token195 prompt195", "session195 library195", "service195"],
    ),
    (
        ("token195 prompt195 session195 library195 service195 gateway195", 6),
        ["token195", "prompt195", "session195", "library195", "service195", "gateway195"],
    ),
    (
        ("token195 prompt195 session195 library195 service195 gateway195", 10),
        ["token195", "prompt195", "session195", "library195", "service195", "gateway195"],
    ),
    (
        ("token195 prompt195 session195 library195 service195 gateway195", 18),
        ["token195 prompt195", "session195", "library195", "service195", "gateway195"],
    ),
    (
        ("token195 prompt195 session195 library195 service195 gateway195", 28),
        ["token195 prompt195", "session195 library195", "service195 gateway195"],
    ),
    (
        ("prompt195 session195 library195 service195 gateway195 storage195", 6),
        ["prompt195", "session195", "library195", "service195", "gateway195", "storage195"],
    ),
    (
        ("prompt195 session195 library195 service195 gateway195 storage195", 10),
        ["prompt195", "session195", "library195", "service195", "gateway195", "storage195"],
    ),
    (
        ("prompt195 session195 library195 service195 gateway195 storage195", 18),
        ["prompt195", "session195", "library195", "service195", "gateway195", "storage195"],
    ),
    (
        ("prompt195 session195 library195 service195 gateway195 storage195", 28),
        ["prompt195 session195", "library195 service195", "gateway195 storage195"],
    ),
    (
        ("session195 library195 service195 gateway195 storage195 network195", 6),
        ["session195", "library195", "service195", "gateway195", "storage195", "network195"],
    ),
    (
        ("session195 library195 service195 gateway195 storage195 network195", 10),
        ["session195", "library195", "service195", "gateway195", "storage195", "network195"],
    ),
    (
        ("session195 library195 service195 gateway195 storage195 network195", 18),
        ["session195", "library195", "service195", "gateway195", "storage195", "network195"],
    ),
    (
        ("session195 library195 service195 gateway195 storage195 network195", 28),
        ["session195 library195", "service195 gateway195", "storage195 network195"],
    ),
    (
        ("library195 service195 gateway195 storage195 network195 latency195", 6),
        ["library195", "service195", "gateway195", "storage195", "network195", "latency195"],
    ),
    (
        ("library195 service195 gateway195 storage195 network195 latency195", 10),
        ["library195", "service195", "gateway195", "storage195", "network195", "latency195"],
    ),
    (
        ("library195 service195 gateway195 storage195 network195 latency195", 18),
        ["library195", "service195", "gateway195", "storage195", "network195", "latency195"],
    ),
    (
        ("library195 service195 gateway195 storage195 network195 latency195", 28),
        ["library195 service195", "gateway195 storage195", "network195 latency195"],
    ),
    (
        ("service195 gateway195 storage195 network195 latency195 buffer195", 6),
        ["service195", "gateway195", "storage195", "network195", "latency195", "buffer195"],
    ),
    (
        ("service195 gateway195 storage195 network195 latency195 buffer195", 10),
        ["service195", "gateway195", "storage195", "network195", "latency195", "buffer195"],
    ),
    (
        ("service195 gateway195 storage195 network195 latency195 buffer195", 18),
        ["service195", "gateway195", "storage195", "network195", "latency195", "buffer195"],
    ),
    (
        ("service195 gateway195 storage195 network195 latency195 buffer195", 28),
        ["service195 gateway195", "storage195 network195", "latency195 buffer195"],
    ),
    (
        ("gateway195 storage195 network195 latency195 buffer195 queue195", 6),
        ["gateway195", "storage195", "network195", "latency195", "buffer195", "queue195"],
    ),
    (
        ("gateway195 storage195 network195 latency195 buffer195 queue195", 10),
        ["gateway195", "storage195", "network195", "latency195", "buffer195", "queue195"],
    ),
    (
        ("gateway195 storage195 network195 latency195 buffer195 queue195", 18),
        ["gateway195", "storage195", "network195", "latency195", "buffer195 queue195"],
    ),
    (
        ("gateway195 storage195 network195 latency195 buffer195 queue195", 28),
        ["gateway195 storage195", "network195 latency195", "buffer195 queue195"],
    ),
    (
        ("storage195 network195 latency195 buffer195 queue195 worker195", 6),
        ["storage195", "network195", "latency195", "buffer195", "queue195", "worker195"],
    ),
    (
        ("storage195 network195 latency195 buffer195 queue195 worker195", 10),
        ["storage195", "network195", "latency195", "buffer195", "queue195", "worker195"],
    ),
    (
        ("storage195 network195 latency195 buffer195 queue195 worker195", 18),
        ["storage195", "network195", "latency195", "buffer195 queue195", "worker195"],
    ),
    (
        ("storage195 network195 latency195 buffer195 queue195 worker195", 28),
        ["storage195 network195", "latency195 buffer195", "queue195 worker195"],
    ),
    (
        ("network195 latency195 buffer195 queue195 worker195 kernel195", 6),
        ["network195", "latency195", "buffer195", "queue195", "worker195", "kernel195"],
    ),
    (
        ("network195 latency195 buffer195 queue195 worker195 kernel195", 10),
        ["network195", "latency195", "buffer195", "queue195", "worker195", "kernel195"],
    ),
    (
        ("network195 latency195 buffer195 queue195 worker195 kernel195", 18),
        ["network195", "latency195", "buffer195 queue195", "worker195", "kernel195"],
    ),
    (
        ("network195 latency195 buffer195 queue195 worker195 kernel195", 28),
        ["network195 latency195", "buffer195 queue195 worker195", "kernel195"],
    ),
    (
        ("latency195 buffer195 queue195 worker195 kernel195 signal195", 6),
        ["latency195", "buffer195", "queue195", "worker195", "kernel195", "signal195"],
    ),
    (
        ("latency195 buffer195 queue195 worker195 kernel195 signal195", 10),
        ["latency195", "buffer195", "queue195", "worker195", "kernel195", "signal195"],
    ),
    (
        ("latency195 buffer195 queue195 worker195 kernel195 signal195", 18),
        ["latency195", "buffer195 queue195", "worker195", "kernel195", "signal195"],
    ),
    (
        ("latency195 buffer195 queue195 worker195 kernel195 signal195", 28),
        ["latency195 buffer195", "queue195 worker195 kernel195", "signal195"],
    ),
    (
        ("buffer195 queue195 worker195 kernel195 signal195 packet195", 6),
        ["buffer195", "queue195", "worker195", "kernel195", "signal195", "packet195"],
    ),
    (
        ("buffer195 queue195 worker195 kernel195 signal195 packet195", 10),
        ["buffer195", "queue195", "worker195", "kernel195", "signal195", "packet195"],
    ),
    (
        ("buffer195 queue195 worker195 kernel195 signal195 packet195", 18),
        ["buffer195 queue195", "worker195", "kernel195", "signal195", "packet195"],
    ),
    (
        ("buffer195 queue195 worker195 kernel195 signal195 packet195", 28),
        ["buffer195 queue195 worker195", "kernel195 signal195", "packet195"],
    ),
    (
        ("queue195 worker195 kernel195 signal195 packet195 router195", 6),
        ["queue195", "worker195", "kernel195", "signal195", "packet195", "router195"],
    ),
    (
        ("queue195 worker195 kernel195 signal195 packet195 router195", 10),
        ["queue195", "worker195", "kernel195", "signal195", "packet195", "router195"],
    ),
    (
        ("queue195 worker195 kernel195 signal195 packet195 router195", 18),
        ["queue195 worker195", "kernel195", "signal195", "packet195", "router195"],
    ),
    (
        ("queue195 worker195 kernel195 signal195 packet195 router195", 28),
        ["queue195 worker195 kernel195", "signal195 packet195", "router195"],
    ),
    (
        ("worker195 kernel195 signal195 packet195 router195 cluster195", 6),
        ["worker195", "kernel195", "signal195", "packet195", "router195", "cluster195"],
    ),
    (
        ("worker195 kernel195 signal195 packet195 router195 cluster195", 10),
        ["worker195", "kernel195", "signal195", "packet195", "router195", "cluster195"],
    ),
    (
        ("worker195 kernel195 signal195 packet195 router195 cluster195", 18),
        ["worker195", "kernel195", "signal195", "packet195", "router195", "cluster195"],
    ),
    (
        ("worker195 kernel195 signal195 packet195 router195 cluster195", 28),
        ["worker195 kernel195", "signal195 packet195", "router195 cluster195"],
    ),
    (
        ("kernel195 signal195 packet195 router195 cluster195 mirror195", 6),
        ["kernel195", "signal195", "packet195", "router195", "cluster195", "mirror195"],
    ),
    (
        ("kernel195 signal195 packet195 router195 cluster195 mirror195", 10),
        ["kernel195", "signal195", "packet195", "router195", "cluster195", "mirror195"],
    ),
    (
        ("kernel195 signal195 packet195 router195 cluster195 mirror195", 18),
        ["kernel195", "signal195", "packet195", "router195", "cluster195", "mirror195"],
    ),
    (
        ("kernel195 signal195 packet195 router195 cluster195 mirror195", 28),
        ["kernel195 signal195", "packet195 router195", "cluster195 mirror195"],
    ),
    (
        ("signal195 packet195 router195 cluster195 mirror195 filter195", 6),
        ["signal195", "packet195", "router195", "cluster195", "mirror195", "filter195"],
    ),
    (
        ("signal195 packet195 router195 cluster195 mirror195 filter195", 10),
        ["signal195", "packet195", "router195", "cluster195", "mirror195", "filter195"],
    ),
    (
        ("signal195 packet195 router195 cluster195 mirror195 filter195", 18),
        ["signal195", "packet195", "router195", "cluster195", "mirror195", "filter195"],
    ),
    (
        ("signal195 packet195 router195 cluster195 mirror195 filter195", 28),
        ["signal195 packet195", "router195 cluster195", "mirror195 filter195"],
    ),
    (
        ("packet195 router195 cluster195 mirror195 filter195 ranking195", 6),
        ["packet195", "router195", "cluster195", "mirror195", "filter195", "ranking195"],
    ),
    (
        ("packet195 router195 cluster195 mirror195 filter195 ranking195", 10),
        ["packet195", "router195", "cluster195", "mirror195", "filter195", "ranking195"],
    ),
    (
        ("packet195 router195 cluster195 mirror195 filter195 ranking195", 18),
        ["packet195", "router195", "cluster195", "mirror195", "filter195", "ranking195"],
    ),
    (
        ("packet195 router195 cluster195 mirror195 filter195 ranking195", 28),
        ["packet195 router195", "cluster195 mirror195", "filter195 ranking195"],
    ),
    (
        ("router195 cluster195 mirror195 filter195 ranking195 encoding195", 6),
        ["router195", "cluster195", "mirror195", "filter195", "ranking195", "encoding195"],
    ),
    (
        ("router195 cluster195 mirror195 filter195 ranking195 encoding195", 10),
        ["router195", "cluster195", "mirror195", "filter195", "ranking195", "encoding195"],
    ),
    (
        ("router195 cluster195 mirror195 filter195 ranking195 encoding195", 18),
        ["router195", "cluster195", "mirror195", "filter195", "ranking195", "encoding195"],
    ),
    (
        ("router195 cluster195 mirror195 filter195 ranking195 encoding195", 28),
        ["router195 cluster195", "mirror195 filter195", "ranking195 encoding195"],
    ),
    (
        ("cluster195 mirror195 filter195 ranking195 encoding195 mapping195", 6),
        ["cluster195", "mirror195", "filter195", "ranking195", "encoding195", "mapping195"],
    ),
    (
        ("cluster195 mirror195 filter195 ranking195 encoding195 mapping195", 10),
        ["cluster195", "mirror195", "filter195", "ranking195", "encoding195", "mapping195"],
    ),
    (
        ("cluster195 mirror195 filter195 ranking195 encoding195 mapping195", 18),
        ["cluster195", "mirror195", "filter195", "ranking195", "encoding195", "mapping195"],
    ),
    (
        ("cluster195 mirror195 filter195 ranking195 encoding195 mapping195", 28),
        ["cluster195 mirror195", "filter195 ranking195", "encoding195 mapping195"],
    ),
    (
        ("mirror195 filter195 ranking195 encoding195 mapping195 record195", 6),
        ["mirror195", "filter195", "ranking195", "encoding195", "mapping195", "record195"],
    ),
    (
        ("mirror195 filter195 ranking195 encoding195 mapping195 record195", 10),
        ["mirror195", "filter195", "ranking195", "encoding195", "mapping195", "record195"],
    ),
    (
        ("mirror195 filter195 ranking195 encoding195 mapping195 record195", 18),
        ["mirror195", "filter195", "ranking195", "encoding195", "mapping195", "record195"],
    ),
    (
        ("mirror195 filter195 ranking195 encoding195 mapping195 record195", 28),
        ["mirror195 filter195", "ranking195 encoding195", "mapping195 record195"],
    ),
    (
        ("filter195 ranking195 encoding195 mapping195 record195 candle195", 6),
        ["filter195", "ranking195", "encoding195", "mapping195", "record195", "candle195"],
    ),
    (
        ("filter195 ranking195 encoding195 mapping195 record195 candle195", 10),
        ["filter195", "ranking195", "encoding195", "mapping195", "record195", "candle195"],
    ),
    (
        ("filter195 ranking195 encoding195 mapping195 record195 candle195", 18),
        ["filter195", "ranking195", "encoding195", "mapping195", "record195", "candle195"],
    ),
    (
        ("filter195 ranking195 encoding195 mapping195 record195 candle195", 28),
        ["filter195 ranking195", "encoding195 mapping195", "record195 candle195"],
    ),
    (
        ("ranking195 encoding195 mapping195 record195 candle195 thread195", 6),
        ["ranking195", "encoding195", "mapping195", "record195", "candle195", "thread195"],
    ),
    (
        ("ranking195 encoding195 mapping195 record195 candle195 thread195", 10),
        ["ranking195", "encoding195", "mapping195", "record195", "candle195", "thread195"],
    ),
    (
        ("ranking195 encoding195 mapping195 record195 candle195 thread195", 18),
        ["ranking195", "encoding195", "mapping195", "record195", "candle195", "thread195"],
    ),
    (
        ("ranking195 encoding195 mapping195 record195 candle195 thread195", 28),
        ["ranking195 encoding195", "mapping195 record195", "candle195 thread195"],
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
