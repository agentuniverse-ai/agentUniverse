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
        ("round 141: the quick brown fox jumps over the lazy dog", 4),
        ["round", "141:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", 8),
        ["round", "141: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", 12),
        ["round 141:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", 16),
        ["round 141: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", 24),
        ["round 141: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 141: the quick brown fox jumps over the lazy dog", 32),
        ["round 141: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", 4),
        ["round", "141:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", 8),
        ["round", "141:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", 12),
        ["round 141:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", 16),
        ["round 141:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", 24),
        ["round 141: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 141: agentuniverse is a framework for multi agents", 32),
        ["round 141: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", 4),
        ["round", "141:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", 8),
        ["round", "141:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", 12),
        ["round 141:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", 16),
        ["round 141:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", 24),
        ["round 141: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 141: knowledge stored as vectors enables retrieval", 32),
        ["round 141: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 141: the processor reads the record then stops", 4),
        ["round", "141:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 141: the processor reads the record then stops", 8),
        ["round", "141: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 141: the processor reads the record then stops", 12),
        ["round 141:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 141: the processor reads the record then stops", 16),
        ["round 141: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 141: the processor reads the record then stops", 24),
        ["round 141: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 141: the processor reads the record then stops", 32),
        ["round 141: the processor reads", "the record then stops"],
    ),
    (
        ("round 141: a worker pulls the next task from the queue", 4),
        ["round", "141:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 141: a worker pulls the next task from the queue", 8),
        ["round", "141: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 141: a worker pulls the next task from the queue", 12),
        ["round 141: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 141: a worker pulls the next task from the queue", 16),
        ["round 141: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 141: a worker pulls the next task from the queue", 24),
        ["round 141: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 141: a worker pulls the next task from the queue", 32),
        ["round 141: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 141: signals travel through the network layer", 4),
        ["round", "141:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 141: signals travel through the network layer", 8),
        ["round", "141:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 141: signals travel through the network layer", 12),
        ["round 141:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 141: signals travel through the network layer", 16),
        ["round 141:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 141: signals travel through the network layer", 24),
        ["round 141: signals", "travel through the", "network layer"],
    ),
    (
        ("round 141: signals travel through the network layer", 32),
        ["round 141: signals travel", "through the network layer"],
    ),
    (
        ("round 141: the gateway routes each request by policy", 4),
        ["round", "141:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 141: the gateway routes each request by policy", 8),
        ["round", "141: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 141: the gateway routes each request by policy", 12),
        ["round 141:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 141: the gateway routes each request by policy", 16),
        ["round 141: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 141: the gateway routes each request by policy", 24),
        ["round 141: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 141: the gateway routes each request by policy", 32),
        ["round 141: the gateway routes", "each request by policy"],
    ),
    (
        ("round 141: memory grows until the buffer is full", 4),
        ["round", "141:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 141: memory grows until the buffer is full", 8),
        ["round", "141:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 141: memory grows until the buffer is full", 12),
        ["round 141:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 141: memory grows until the buffer is full", 16),
        ["round 141:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 141: memory grows until the buffer is full", 24), ["round 141: memory grows", "until the buffer is full"]),
    (("round 141: memory grows until the buffer is full", 32), ["round 141: memory grows until", "the buffer is full"]),
    (
        ("round 141: the cluster mirrors every packet twice", 4),
        ["round", "141:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 141: the cluster mirrors every packet twice", 8),
        ["round", "141: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 141: the cluster mirrors every packet twice", 12),
        ["round 141:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 141: the cluster mirrors every packet twice", 16),
        ["round 141: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 141: the cluster mirrors every packet twice", 24),
        ["round 141: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 141: the cluster mirrors every packet twice", 32),
        ["round 141: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", 4),
        ["round", "141:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", 8),
        ["round", "141:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", 12),
        ["round 141:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", 16),
        ["round 141:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", 24),
        ["round 141: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 141: ranking uses tokens learned from the corpus", 32),
        ["round 141: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 141: a long session ends when the candle dies", 4),
        ["round", "141:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 141: a long session ends when the candle dies", 8),
        ["round", "141: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 141: a long session ends when the candle dies", 12),
        ["round 141: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 141: a long session ends when the candle dies", 16),
        ["round 141: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 141: a long session ends when the candle dies", 24),
        ["round 141: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 141: a long session ends when the candle dies", 32),
        ["round 141: a long session ends", "when the candle dies"],
    ),
    (
        ("round 141: encode the prompt then map the result", 4),
        ["round", "141:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 141: encode the prompt then map the result", 8),
        ["round", "141:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 141: encode the prompt then map the result", 12),
        ["round 141:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 141: encode the prompt then map the result", 16),
        ["round 141:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 141: encode the prompt then map the result", 24),
        ["round 141: encode the", "prompt then map the", "result"],
    ),
    (("round 141: encode the prompt then map the result", 32), ["round 141: encode the prompt", "then map the result"]),
    (
        ("round 141: the kernel wakes the worker at dawn", 4),
        ["round", "141:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 141: the kernel wakes the worker at dawn", 8),
        ["round", "141: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 141: the kernel wakes the worker at dawn", 12),
        ["round 141:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 141: the kernel wakes the worker at dawn", 16), ["round 141: the", "kernel wakes the", "worker at dawn"]),
    (("round 141: the kernel wakes the worker at dawn", 24), ["round 141: the kernel", "wakes the worker at dawn"]),
    (("round 141: the kernel wakes the worker at dawn", 32), ["round 141: the kernel wakes the", "worker at dawn"]),
    (
        ("round 141: service latency drops after the patch", 4),
        ["round", "141:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 141: service latency drops after the patch", 8),
        ["round", "141:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 141: service latency drops after the patch", 12),
        ["round 141:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 141: service latency drops after the patch", 16),
        ["round 141:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 141: service latency drops after the patch", 24),
        ["round 141: service", "latency drops after the", "patch"],
    ),
    (("round 141: service latency drops after the patch", 32), ["round 141: service latency drops", "after the patch"]),
    (
        ("round 141: the library caches every vector it sees", 4),
        ["round", "141:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 141: the library caches every vector it sees", 8),
        ["round", "141: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 141: the library caches every vector it sees", 12),
        ["round 141:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 141: the library caches every vector it sees", 16),
        ["round 141: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 141: the library caches every vector it sees", 24),
        ["round 141: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 141: the library caches every vector it sees", 32),
        ["round 141: the library caches", "every vector it sees"],
    ),
    (
        ("round 141: agents argue then the debate resolves", 4),
        ["round", "141:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 141: agents argue then the debate resolves", 8),
        ["round", "141:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 141: agents argue then the debate resolves", 12),
        ["round 141:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 141: agents argue then the debate resolves", 16),
        ["round 141:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 141: agents argue then the debate resolves", 24), ["round 141: agents argue", "then the debate resolves"]),
    (("round 141: agents argue then the debate resolves", 32), ["round 141: agents argue then the", "debate resolves"]),
    (
        ("round 141: the filter keeps only strong matches", 4),
        ["round", "141:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 141: the filter keeps only strong matches", 8),
        ["round", "141: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 141: the filter keeps only strong matches", 12),
        ["round 141:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 141: the filter keeps only strong matches", 16),
        ["round 141: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 141: the filter keeps only strong matches", 24),
        ["round 141: the filter", "keeps only strong", "matches"],
    ),
    (("round 141: the filter keeps only strong matches", 32), ["round 141: the filter keeps only", "strong matches"]),
    (
        ("round 141: the model answers with a short reply", 4),
        ["round", "141:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 141: the model answers with a short reply", 8),
        ["round", "141: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 141: the model answers with a short reply", 12),
        ["round 141:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 141: the model answers with a short reply", 16),
        ["round 141: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 141: the model answers with a short reply", 24),
        ["round 141: the model", "answers with a short", "reply"],
    ),
    (("round 141: the model answers with a short reply", 32), ["round 141: the model answers", "with a short reply"]),
    (
        ("round 141: the recorder stores the reasoning trace", 4),
        ["round", "141:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 141: the recorder stores the reasoning trace", 8),
        ["round", "141: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 141: the recorder stores the reasoning trace", 12),
        ["round 141:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 141: the recorder stores the reasoning trace", 16),
        ["round 141: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 141: the recorder stores the reasoning trace", 24),
        ["round 141: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 141: the recorder stores the reasoning trace", 32),
        ["round 141: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 141: the angel watches the processor run", 4),
        ["round", "141:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 141: the angel watches the processor run", 8),
        ["round", "141: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 141: the angel watches the processor run", 12),
        ["round 141:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 141: the angel watches the processor run", 16),
        ["round 141: the", "angel watches", "the processor", "run"],
    ),
    (("round 141: the angel watches the processor run", 24), ["round 141: the angel", "watches the processor", "run"]),
    (("round 141: the angel watches the processor run", 32), ["round 141: the angel watches the", "processor run"]),
    (
        ("round 141: angle of the vector decides the match", 4),
        ["round", "141:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 141: angle of the vector decides the match", 8),
        ["round", "141:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 141: angle of the vector decides the match", 12),
        ["round 141:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 141: angle of the vector decides the match", 16),
        ["round 141: angle", "of the vector", "decides the", "match"],
    ),
    (("round 141: angle of the vector decides the match", 24), ["round 141: angle of the", "vector decides the match"]),
    (("round 141: angle of the vector decides the match", 32), ["round 141: angle of the vector", "decides the match"]),
    (
        ("round 141: the candle burns twice as long at night", 4),
        ["round", "141:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 141: the candle burns twice as long at night", 8),
        ["round", "141: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 141: the candle burns twice as long at night", 12),
        ["round 141:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 141: the candle burns twice as long at night", 16),
        ["round 141: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 141: the candle burns twice as long at night", 24),
        ["round 141: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 141: the candle burns twice as long at night", 32),
        ["round 141: the candle burns", "twice as long at night"],
    ),
    (
        ("round 141: a mirror of the universe in one line", 4),
        ["round", "141:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 141: a mirror of the universe in one line", 8),
        ["round", "141: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 141: a mirror of the universe in one line", 12),
        ["round 141: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 141: a mirror of the universe in one line", 16),
        ["round 141: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 141: a mirror of the universe in one line", 24), ["round 141: a mirror of", "the universe in one line"]),
    (("round 141: a mirror of the universe in one line", 32), ["round 141: a mirror of the", "universe in one line"]),
    (
        ("round 141: the queue drains before the storm", 4),
        ["round", "141:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 141: the queue drains before the storm", 8),
        ["round", "141: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 141: the queue drains before the storm", 12),
        ["round 141:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 141: the queue drains before the storm", 16), ["round 141: the", "queue drains", "before the storm"]),
    (("round 141: the queue drains before the storm", 24), ["round 141: the queue", "drains before the storm"]),
    (("round 141: the queue drains before the storm", 32), ["round 141: the queue drains", "before the storm"]),
    (
        ("kitten141 sitting141 agent141 angle141 universe141 memory141", 6),
        ["kitten141", "sitting141", "agent141", "angle141", "universe141", "memory141"],
    ),
    (
        ("kitten141 sitting141 agent141 angle141 universe141 memory141", 10),
        ["kitten141", "sitting141", "agent141", "angle141", "universe141", "memory141"],
    ),
    (
        ("kitten141 sitting141 agent141 angle141 universe141 memory141", 18),
        ["kitten141", "sitting141", "agent141 angle141", "universe141", "memory141"],
    ),
    (
        ("kitten141 sitting141 agent141 angle141 universe141 memory141", 28),
        ["kitten141 sitting141", "agent141 angle141", "universe141 memory141"],
    ),
    (
        ("sitting141 agent141 angle141 universe141 memory141 stream141", 6),
        ["sitting141", "agent141", "angle141", "universe141", "memory141", "stream141"],
    ),
    (
        ("sitting141 agent141 angle141 universe141 memory141 stream141", 10),
        ["sitting141", "agent141", "angle141", "universe141", "memory141", "stream141"],
    ),
    (
        ("sitting141 agent141 angle141 universe141 memory141 stream141", 18),
        ["sitting141", "agent141 angle141", "universe141", "memory141", "stream141"],
    ),
    (
        ("sitting141 agent141 angle141 universe141 memory141 stream141", 28),
        ["sitting141 agent141 angle141", "universe141 memory141", "stream141"],
    ),
    (
        ("agent141 angle141 universe141 memory141 stream141 context141", 6),
        ["agent141", "angle141", "universe141", "memory141", "stream141", "context141"],
    ),
    (
        ("agent141 angle141 universe141 memory141 stream141 context141", 10),
        ["agent141", "angle141", "universe141", "memory141", "stream141", "context141"],
    ),
    (
        ("agent141 angle141 universe141 memory141 stream141 context141", 18),
        ["agent141 angle141", "universe141", "memory141", "stream141", "context141"],
    ),
    (
        ("agent141 angle141 universe141 memory141 stream141 context141", 28),
        ["agent141 angle141", "universe141 memory141", "stream141 context141"],
    ),
    (
        ("angle141 universe141 memory141 stream141 context141 knowledge141", 6),
        ["angle141", "universe141", "memory141", "stream141", "context141", "knowledge141"],
    ),
    (
        ("angle141 universe141 memory141 stream141 context141 knowledge141", 10),
        ["angle141", "universe141", "memory141", "stream141", "context141", "knowledge141"],
    ),
    (
        ("angle141 universe141 memory141 stream141 context141 knowledge141", 18),
        ["angle141", "universe141", "memory141", "stream141", "context141", "knowledge141"],
    ),
    (
        ("angle141 universe141 memory141 stream141 context141 knowledge141", 28),
        ["angle141 universe141", "memory141 stream141", "context141 knowledge141"],
    ),
    (
        ("universe141 memory141 stream141 context141 knowledge141 vector141", 6),
        ["universe141", "memory141", "stream141", "context141", "knowledge141", "vector141"],
    ),
    (
        ("universe141 memory141 stream141 context141 knowledge141 vector141", 10),
        ["universe141", "memory141", "stream141", "context141", "knowledge141", "vector141"],
    ),
    (
        ("universe141 memory141 stream141 context141 knowledge141 vector141", 18),
        ["universe141", "memory141", "stream141", "context141", "knowledge141", "vector141"],
    ),
    (
        ("universe141 memory141 stream141 context141 knowledge141 vector141", 28),
        ["universe141 memory141", "stream141 context141", "knowledge141 vector141"],
    ),
    (
        ("memory141 stream141 context141 knowledge141 vector141 processor141", 6),
        ["memory141", "stream141", "context141", "knowledge141", "vector141", "processor141"],
    ),
    (
        ("memory141 stream141 context141 knowledge141 vector141 processor141", 10),
        ["memory141", "stream141", "context141", "knowledge141", "vector141", "processor141"],
    ),
    (
        ("memory141 stream141 context141 knowledge141 vector141 processor141", 18),
        ["memory141", "stream141", "context141", "knowledge141", "vector141", "processor141"],
    ),
    (
        ("memory141 stream141 context141 knowledge141 vector141 processor141", 28),
        ["memory141 stream141", "context141 knowledge141", "vector141 processor141"],
    ),
    (
        ("stream141 context141 knowledge141 vector141 processor141 reasoning141", 6),
        ["stream141", "context141", "knowledge141", "vector141", "processor141", "reasoning141"],
    ),
    (
        ("stream141 context141 knowledge141 vector141 processor141 reasoning141", 10),
        ["stream141", "context141", "knowledge141", "vector141", "processor141", "reasoning141"],
    ),
    (
        ("stream141 context141 knowledge141 vector141 processor141 reasoning141", 18),
        ["stream141", "context141", "knowledge141", "vector141", "processor141", "reasoning141"],
    ),
    (
        ("stream141 context141 knowledge141 vector141 processor141 reasoning141", 28),
        ["stream141 context141", "knowledge141 vector141", "processor141 reasoning141"],
    ),
    (
        ("context141 knowledge141 vector141 processor141 reasoning141 machine141", 6),
        ["context141", "knowledge141", "vector141", "processor141", "reasoning141", "machine141"],
    ),
    (
        ("context141 knowledge141 vector141 processor141 reasoning141 machine141", 10),
        ["context141", "knowledge141", "vector141", "processor141", "reasoning141", "machine141"],
    ),
    (
        ("context141 knowledge141 vector141 processor141 reasoning141 machine141", 18),
        ["context141", "knowledge141", "vector141", "processor141", "reasoning141", "machine141"],
    ),
    (
        ("context141 knowledge141 vector141 processor141 reasoning141 machine141", 28),
        ["context141 knowledge141", "vector141 processor141", "reasoning141 machine141"],
    ),
    (
        ("knowledge141 vector141 processor141 reasoning141 machine141 learning141", 6),
        ["knowledge141", "vector141", "processor141", "reasoning141", "machine141", "learning141"],
    ),
    (
        ("knowledge141 vector141 processor141 reasoning141 machine141 learning141", 10),
        ["knowledge141", "vector141", "processor141", "reasoning141", "machine141", "learning141"],
    ),
    (
        ("knowledge141 vector141 processor141 reasoning141 machine141 learning141", 18),
        ["knowledge141", "vector141", "processor141", "reasoning141", "machine141", "learning141"],
    ),
    (
        ("knowledge141 vector141 processor141 reasoning141 machine141 learning141", 28),
        ["knowledge141 vector141", "processor141 reasoning141", "machine141 learning141"],
    ),
    (
        ("vector141 processor141 reasoning141 machine141 learning141 model141", 6),
        ["vector141", "processor141", "reasoning141", "machine141", "learning141", "model141"],
    ),
    (
        ("vector141 processor141 reasoning141 machine141 learning141 model141", 10),
        ["vector141", "processor141", "reasoning141", "machine141", "learning141", "model141"],
    ),
    (
        ("vector141 processor141 reasoning141 machine141 learning141 model141", 18),
        ["vector141", "processor141", "reasoning141", "machine141", "learning141", "model141"],
    ),
    (
        ("vector141 processor141 reasoning141 machine141 learning141 model141", 28),
        ["vector141 processor141", "reasoning141 machine141", "learning141 model141"],
    ),
    (
        ("processor141 reasoning141 machine141 learning141 model141 token141", 6),
        ["processor141", "reasoning141", "machine141", "learning141", "model141", "token141"],
    ),
    (
        ("processor141 reasoning141 machine141 learning141 model141 token141", 10),
        ["processor141", "reasoning141", "machine141", "learning141", "model141", "token141"],
    ),
    (
        ("processor141 reasoning141 machine141 learning141 model141 token141", 18),
        ["processor141", "reasoning141", "machine141", "learning141", "model141 token141"],
    ),
    (
        ("processor141 reasoning141 machine141 learning141 model141 token141", 28),
        ["processor141 reasoning141", "machine141 learning141", "model141 token141"],
    ),
    (
        ("reasoning141 machine141 learning141 model141 token141 prompt141", 6),
        ["reasoning141", "machine141", "learning141", "model141", "token141", "prompt141"],
    ),
    (
        ("reasoning141 machine141 learning141 model141 token141 prompt141", 10),
        ["reasoning141", "machine141", "learning141", "model141", "token141", "prompt141"],
    ),
    (
        ("reasoning141 machine141 learning141 model141 token141 prompt141", 18),
        ["reasoning141", "machine141", "learning141", "model141 token141", "prompt141"],
    ),
    (
        ("reasoning141 machine141 learning141 model141 token141 prompt141", 28),
        ["reasoning141 machine141", "learning141 model141", "token141 prompt141"],
    ),
    (
        ("machine141 learning141 model141 token141 prompt141 session141", 6),
        ["machine141", "learning141", "model141", "token141", "prompt141", "session141"],
    ),
    (
        ("machine141 learning141 model141 token141 prompt141 session141", 10),
        ["machine141", "learning141", "model141", "token141", "prompt141", "session141"],
    ),
    (
        ("machine141 learning141 model141 token141 prompt141 session141", 18),
        ["machine141", "learning141", "model141 token141", "prompt141", "session141"],
    ),
    (
        ("machine141 learning141 model141 token141 prompt141 session141", 28),
        ["machine141 learning141", "model141 token141 prompt141", "session141"],
    ),
    (
        ("learning141 model141 token141 prompt141 session141 library141", 6),
        ["learning141", "model141", "token141", "prompt141", "session141", "library141"],
    ),
    (
        ("learning141 model141 token141 prompt141 session141 library141", 10),
        ["learning141", "model141", "token141", "prompt141", "session141", "library141"],
    ),
    (
        ("learning141 model141 token141 prompt141 session141 library141", 18),
        ["learning141", "model141 token141", "prompt141", "session141", "library141"],
    ),
    (
        ("learning141 model141 token141 prompt141 session141 library141", 28),
        ["learning141 model141", "token141 prompt141", "session141 library141"],
    ),
    (
        ("model141 token141 prompt141 session141 library141 service141", 6),
        ["model141", "token141", "prompt141", "session141", "library141", "service141"],
    ),
    (
        ("model141 token141 prompt141 session141 library141 service141", 10),
        ["model141", "token141", "prompt141", "session141", "library141", "service141"],
    ),
    (
        ("model141 token141 prompt141 session141 library141 service141", 18),
        ["model141 token141", "prompt141", "session141", "library141", "service141"],
    ),
    (
        ("model141 token141 prompt141 session141 library141 service141", 28),
        ["model141 token141 prompt141", "session141 library141", "service141"],
    ),
    (
        ("token141 prompt141 session141 library141 service141 gateway141", 6),
        ["token141", "prompt141", "session141", "library141", "service141", "gateway141"],
    ),
    (
        ("token141 prompt141 session141 library141 service141 gateway141", 10),
        ["token141", "prompt141", "session141", "library141", "service141", "gateway141"],
    ),
    (
        ("token141 prompt141 session141 library141 service141 gateway141", 18),
        ["token141 prompt141", "session141", "library141", "service141", "gateway141"],
    ),
    (
        ("token141 prompt141 session141 library141 service141 gateway141", 28),
        ["token141 prompt141", "session141 library141", "service141 gateway141"],
    ),
    (
        ("prompt141 session141 library141 service141 gateway141 storage141", 6),
        ["prompt141", "session141", "library141", "service141", "gateway141", "storage141"],
    ),
    (
        ("prompt141 session141 library141 service141 gateway141 storage141", 10),
        ["prompt141", "session141", "library141", "service141", "gateway141", "storage141"],
    ),
    (
        ("prompt141 session141 library141 service141 gateway141 storage141", 18),
        ["prompt141", "session141", "library141", "service141", "gateway141", "storage141"],
    ),
    (
        ("prompt141 session141 library141 service141 gateway141 storage141", 28),
        ["prompt141 session141", "library141 service141", "gateway141 storage141"],
    ),
    (
        ("session141 library141 service141 gateway141 storage141 network141", 6),
        ["session141", "library141", "service141", "gateway141", "storage141", "network141"],
    ),
    (
        ("session141 library141 service141 gateway141 storage141 network141", 10),
        ["session141", "library141", "service141", "gateway141", "storage141", "network141"],
    ),
    (
        ("session141 library141 service141 gateway141 storage141 network141", 18),
        ["session141", "library141", "service141", "gateway141", "storage141", "network141"],
    ),
    (
        ("session141 library141 service141 gateway141 storage141 network141", 28),
        ["session141 library141", "service141 gateway141", "storage141 network141"],
    ),
    (
        ("library141 service141 gateway141 storage141 network141 latency141", 6),
        ["library141", "service141", "gateway141", "storage141", "network141", "latency141"],
    ),
    (
        ("library141 service141 gateway141 storage141 network141 latency141", 10),
        ["library141", "service141", "gateway141", "storage141", "network141", "latency141"],
    ),
    (
        ("library141 service141 gateway141 storage141 network141 latency141", 18),
        ["library141", "service141", "gateway141", "storage141", "network141", "latency141"],
    ),
    (
        ("library141 service141 gateway141 storage141 network141 latency141", 28),
        ["library141 service141", "gateway141 storage141", "network141 latency141"],
    ),
    (
        ("service141 gateway141 storage141 network141 latency141 buffer141", 6),
        ["service141", "gateway141", "storage141", "network141", "latency141", "buffer141"],
    ),
    (
        ("service141 gateway141 storage141 network141 latency141 buffer141", 10),
        ["service141", "gateway141", "storage141", "network141", "latency141", "buffer141"],
    ),
    (
        ("service141 gateway141 storage141 network141 latency141 buffer141", 18),
        ["service141", "gateway141", "storage141", "network141", "latency141", "buffer141"],
    ),
    (
        ("service141 gateway141 storage141 network141 latency141 buffer141", 28),
        ["service141 gateway141", "storage141 network141", "latency141 buffer141"],
    ),
    (
        ("gateway141 storage141 network141 latency141 buffer141 queue141", 6),
        ["gateway141", "storage141", "network141", "latency141", "buffer141", "queue141"],
    ),
    (
        ("gateway141 storage141 network141 latency141 buffer141 queue141", 10),
        ["gateway141", "storage141", "network141", "latency141", "buffer141", "queue141"],
    ),
    (
        ("gateway141 storage141 network141 latency141 buffer141 queue141", 18),
        ["gateway141", "storage141", "network141", "latency141", "buffer141 queue141"],
    ),
    (
        ("gateway141 storage141 network141 latency141 buffer141 queue141", 28),
        ["gateway141 storage141", "network141 latency141", "buffer141 queue141"],
    ),
    (
        ("storage141 network141 latency141 buffer141 queue141 worker141", 6),
        ["storage141", "network141", "latency141", "buffer141", "queue141", "worker141"],
    ),
    (
        ("storage141 network141 latency141 buffer141 queue141 worker141", 10),
        ["storage141", "network141", "latency141", "buffer141", "queue141", "worker141"],
    ),
    (
        ("storage141 network141 latency141 buffer141 queue141 worker141", 18),
        ["storage141", "network141", "latency141", "buffer141 queue141", "worker141"],
    ),
    (
        ("storage141 network141 latency141 buffer141 queue141 worker141", 28),
        ["storage141 network141", "latency141 buffer141", "queue141 worker141"],
    ),
    (
        ("network141 latency141 buffer141 queue141 worker141 kernel141", 6),
        ["network141", "latency141", "buffer141", "queue141", "worker141", "kernel141"],
    ),
    (
        ("network141 latency141 buffer141 queue141 worker141 kernel141", 10),
        ["network141", "latency141", "buffer141", "queue141", "worker141", "kernel141"],
    ),
    (
        ("network141 latency141 buffer141 queue141 worker141 kernel141", 18),
        ["network141", "latency141", "buffer141 queue141", "worker141", "kernel141"],
    ),
    (
        ("network141 latency141 buffer141 queue141 worker141 kernel141", 28),
        ["network141 latency141", "buffer141 queue141 worker141", "kernel141"],
    ),
    (
        ("latency141 buffer141 queue141 worker141 kernel141 signal141", 6),
        ["latency141", "buffer141", "queue141", "worker141", "kernel141", "signal141"],
    ),
    (
        ("latency141 buffer141 queue141 worker141 kernel141 signal141", 10),
        ["latency141", "buffer141", "queue141", "worker141", "kernel141", "signal141"],
    ),
    (
        ("latency141 buffer141 queue141 worker141 kernel141 signal141", 18),
        ["latency141", "buffer141 queue141", "worker141", "kernel141", "signal141"],
    ),
    (
        ("latency141 buffer141 queue141 worker141 kernel141 signal141", 28),
        ["latency141 buffer141", "queue141 worker141 kernel141", "signal141"],
    ),
    (
        ("buffer141 queue141 worker141 kernel141 signal141 packet141", 6),
        ["buffer141", "queue141", "worker141", "kernel141", "signal141", "packet141"],
    ),
    (
        ("buffer141 queue141 worker141 kernel141 signal141 packet141", 10),
        ["buffer141", "queue141", "worker141", "kernel141", "signal141", "packet141"],
    ),
    (
        ("buffer141 queue141 worker141 kernel141 signal141 packet141", 18),
        ["buffer141 queue141", "worker141", "kernel141", "signal141", "packet141"],
    ),
    (
        ("buffer141 queue141 worker141 kernel141 signal141 packet141", 28),
        ["buffer141 queue141 worker141", "kernel141 signal141", "packet141"],
    ),
    (
        ("queue141 worker141 kernel141 signal141 packet141 router141", 6),
        ["queue141", "worker141", "kernel141", "signal141", "packet141", "router141"],
    ),
    (
        ("queue141 worker141 kernel141 signal141 packet141 router141", 10),
        ["queue141", "worker141", "kernel141", "signal141", "packet141", "router141"],
    ),
    (
        ("queue141 worker141 kernel141 signal141 packet141 router141", 18),
        ["queue141 worker141", "kernel141", "signal141", "packet141", "router141"],
    ),
    (
        ("queue141 worker141 kernel141 signal141 packet141 router141", 28),
        ["queue141 worker141 kernel141", "signal141 packet141", "router141"],
    ),
    (
        ("worker141 kernel141 signal141 packet141 router141 cluster141", 6),
        ["worker141", "kernel141", "signal141", "packet141", "router141", "cluster141"],
    ),
    (
        ("worker141 kernel141 signal141 packet141 router141 cluster141", 10),
        ["worker141", "kernel141", "signal141", "packet141", "router141", "cluster141"],
    ),
    (
        ("worker141 kernel141 signal141 packet141 router141 cluster141", 18),
        ["worker141", "kernel141", "signal141", "packet141", "router141", "cluster141"],
    ),
    (
        ("worker141 kernel141 signal141 packet141 router141 cluster141", 28),
        ["worker141 kernel141", "signal141 packet141", "router141 cluster141"],
    ),
    (
        ("kernel141 signal141 packet141 router141 cluster141 mirror141", 6),
        ["kernel141", "signal141", "packet141", "router141", "cluster141", "mirror141"],
    ),
    (
        ("kernel141 signal141 packet141 router141 cluster141 mirror141", 10),
        ["kernel141", "signal141", "packet141", "router141", "cluster141", "mirror141"],
    ),
    (
        ("kernel141 signal141 packet141 router141 cluster141 mirror141", 18),
        ["kernel141", "signal141", "packet141", "router141", "cluster141", "mirror141"],
    ),
    (
        ("kernel141 signal141 packet141 router141 cluster141 mirror141", 28),
        ["kernel141 signal141", "packet141 router141", "cluster141 mirror141"],
    ),
    (
        ("signal141 packet141 router141 cluster141 mirror141 filter141", 6),
        ["signal141", "packet141", "router141", "cluster141", "mirror141", "filter141"],
    ),
    (
        ("signal141 packet141 router141 cluster141 mirror141 filter141", 10),
        ["signal141", "packet141", "router141", "cluster141", "mirror141", "filter141"],
    ),
    (
        ("signal141 packet141 router141 cluster141 mirror141 filter141", 18),
        ["signal141", "packet141", "router141", "cluster141", "mirror141", "filter141"],
    ),
    (
        ("signal141 packet141 router141 cluster141 mirror141 filter141", 28),
        ["signal141 packet141", "router141 cluster141", "mirror141 filter141"],
    ),
    (
        ("packet141 router141 cluster141 mirror141 filter141 ranking141", 6),
        ["packet141", "router141", "cluster141", "mirror141", "filter141", "ranking141"],
    ),
    (
        ("packet141 router141 cluster141 mirror141 filter141 ranking141", 10),
        ["packet141", "router141", "cluster141", "mirror141", "filter141", "ranking141"],
    ),
    (
        ("packet141 router141 cluster141 mirror141 filter141 ranking141", 18),
        ["packet141", "router141", "cluster141", "mirror141", "filter141", "ranking141"],
    ),
    (
        ("packet141 router141 cluster141 mirror141 filter141 ranking141", 28),
        ["packet141 router141", "cluster141 mirror141", "filter141 ranking141"],
    ),
    (
        ("router141 cluster141 mirror141 filter141 ranking141 encoding141", 6),
        ["router141", "cluster141", "mirror141", "filter141", "ranking141", "encoding141"],
    ),
    (
        ("router141 cluster141 mirror141 filter141 ranking141 encoding141", 10),
        ["router141", "cluster141", "mirror141", "filter141", "ranking141", "encoding141"],
    ),
    (
        ("router141 cluster141 mirror141 filter141 ranking141 encoding141", 18),
        ["router141", "cluster141", "mirror141", "filter141", "ranking141", "encoding141"],
    ),
    (
        ("router141 cluster141 mirror141 filter141 ranking141 encoding141", 28),
        ["router141 cluster141", "mirror141 filter141", "ranking141 encoding141"],
    ),
    (
        ("cluster141 mirror141 filter141 ranking141 encoding141 mapping141", 6),
        ["cluster141", "mirror141", "filter141", "ranking141", "encoding141", "mapping141"],
    ),
    (
        ("cluster141 mirror141 filter141 ranking141 encoding141 mapping141", 10),
        ["cluster141", "mirror141", "filter141", "ranking141", "encoding141", "mapping141"],
    ),
    (
        ("cluster141 mirror141 filter141 ranking141 encoding141 mapping141", 18),
        ["cluster141", "mirror141", "filter141", "ranking141", "encoding141", "mapping141"],
    ),
    (
        ("cluster141 mirror141 filter141 ranking141 encoding141 mapping141", 28),
        ["cluster141 mirror141", "filter141 ranking141", "encoding141 mapping141"],
    ),
    (
        ("mirror141 filter141 ranking141 encoding141 mapping141 record141", 6),
        ["mirror141", "filter141", "ranking141", "encoding141", "mapping141", "record141"],
    ),
    (
        ("mirror141 filter141 ranking141 encoding141 mapping141 record141", 10),
        ["mirror141", "filter141", "ranking141", "encoding141", "mapping141", "record141"],
    ),
    (
        ("mirror141 filter141 ranking141 encoding141 mapping141 record141", 18),
        ["mirror141", "filter141", "ranking141", "encoding141", "mapping141", "record141"],
    ),
    (
        ("mirror141 filter141 ranking141 encoding141 mapping141 record141", 28),
        ["mirror141 filter141", "ranking141 encoding141", "mapping141 record141"],
    ),
    (
        ("filter141 ranking141 encoding141 mapping141 record141 candle141", 6),
        ["filter141", "ranking141", "encoding141", "mapping141", "record141", "candle141"],
    ),
    (
        ("filter141 ranking141 encoding141 mapping141 record141 candle141", 10),
        ["filter141", "ranking141", "encoding141", "mapping141", "record141", "candle141"],
    ),
    (
        ("filter141 ranking141 encoding141 mapping141 record141 candle141", 18),
        ["filter141", "ranking141", "encoding141", "mapping141", "record141", "candle141"],
    ),
    (
        ("filter141 ranking141 encoding141 mapping141 record141 candle141", 28),
        ["filter141 ranking141", "encoding141 mapping141", "record141 candle141"],
    ),
    (
        ("ranking141 encoding141 mapping141 record141 candle141 thread141", 6),
        ["ranking141", "encoding141", "mapping141", "record141", "candle141", "thread141"],
    ),
    (
        ("ranking141 encoding141 mapping141 record141 candle141 thread141", 10),
        ["ranking141", "encoding141", "mapping141", "record141", "candle141", "thread141"],
    ),
    (
        ("ranking141 encoding141 mapping141 record141 candle141 thread141", 18),
        ["ranking141", "encoding141", "mapping141", "record141", "candle141", "thread141"],
    ),
    (
        ("ranking141 encoding141 mapping141 record141 candle141 thread141", 28),
        ["ranking141 encoding141", "mapping141 record141", "candle141 thread141"],
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
