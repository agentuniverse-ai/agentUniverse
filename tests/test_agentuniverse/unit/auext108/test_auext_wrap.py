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
        ("round 108: the quick brown fox jumps over the lazy dog", 4),
        ["round", "108:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", 8),
        ["round", "108: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", 12),
        ["round 108:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", 16),
        ["round 108: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", 24),
        ["round 108: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 108: the quick brown fox jumps over the lazy dog", 32),
        ["round 108: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", 4),
        ["round", "108:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", 8),
        ["round", "108:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", 12),
        ["round 108:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", 16),
        ["round 108:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", 24),
        ["round 108: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 108: agentuniverse is a framework for multi agents", 32),
        ["round 108: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", 4),
        ["round", "108:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", 8),
        ["round", "108:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", 12),
        ["round 108:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", 16),
        ["round 108:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", 24),
        ["round 108: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 108: knowledge stored as vectors enables retrieval", 32),
        ["round 108: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 108: the processor reads the record then stops", 4),
        ["round", "108:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 108: the processor reads the record then stops", 8),
        ["round", "108: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 108: the processor reads the record then stops", 12),
        ["round 108:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 108: the processor reads the record then stops", 16),
        ["round 108: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 108: the processor reads the record then stops", 24),
        ["round 108: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 108: the processor reads the record then stops", 32),
        ["round 108: the processor reads", "the record then stops"],
    ),
    (
        ("round 108: a worker pulls the next task from the queue", 4),
        ["round", "108:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 108: a worker pulls the next task from the queue", 8),
        ["round", "108: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 108: a worker pulls the next task from the queue", 12),
        ["round 108: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 108: a worker pulls the next task from the queue", 16),
        ["round 108: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 108: a worker pulls the next task from the queue", 24),
        ["round 108: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 108: a worker pulls the next task from the queue", 32),
        ["round 108: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 108: signals travel through the network layer", 4),
        ["round", "108:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 108: signals travel through the network layer", 8),
        ["round", "108:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 108: signals travel through the network layer", 12),
        ["round 108:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 108: signals travel through the network layer", 16),
        ["round 108:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 108: signals travel through the network layer", 24),
        ["round 108: signals", "travel through the", "network layer"],
    ),
    (
        ("round 108: signals travel through the network layer", 32),
        ["round 108: signals travel", "through the network layer"],
    ),
    (
        ("round 108: the gateway routes each request by policy", 4),
        ["round", "108:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 108: the gateway routes each request by policy", 8),
        ["round", "108: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 108: the gateway routes each request by policy", 12),
        ["round 108:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 108: the gateway routes each request by policy", 16),
        ["round 108: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 108: the gateway routes each request by policy", 24),
        ["round 108: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 108: the gateway routes each request by policy", 32),
        ["round 108: the gateway routes", "each request by policy"],
    ),
    (
        ("round 108: memory grows until the buffer is full", 4),
        ["round", "108:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 108: memory grows until the buffer is full", 8),
        ["round", "108:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 108: memory grows until the buffer is full", 12),
        ["round 108:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 108: memory grows until the buffer is full", 16),
        ["round 108:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 108: memory grows until the buffer is full", 24), ["round 108: memory grows", "until the buffer is full"]),
    (("round 108: memory grows until the buffer is full", 32), ["round 108: memory grows until", "the buffer is full"]),
    (
        ("round 108: the cluster mirrors every packet twice", 4),
        ["round", "108:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 108: the cluster mirrors every packet twice", 8),
        ["round", "108: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 108: the cluster mirrors every packet twice", 12),
        ["round 108:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 108: the cluster mirrors every packet twice", 16),
        ["round 108: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 108: the cluster mirrors every packet twice", 24),
        ["round 108: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 108: the cluster mirrors every packet twice", 32),
        ["round 108: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", 4),
        ["round", "108:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", 8),
        ["round", "108:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", 12),
        ["round 108:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", 16),
        ["round 108:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", 24),
        ["round 108: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 108: ranking uses tokens learned from the corpus", 32),
        ["round 108: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 108: a long session ends when the candle dies", 4),
        ["round", "108:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 108: a long session ends when the candle dies", 8),
        ["round", "108: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 108: a long session ends when the candle dies", 12),
        ["round 108: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 108: a long session ends when the candle dies", 16),
        ["round 108: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 108: a long session ends when the candle dies", 24),
        ["round 108: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 108: a long session ends when the candle dies", 32),
        ["round 108: a long session ends", "when the candle dies"],
    ),
    (
        ("round 108: encode the prompt then map the result", 4),
        ["round", "108:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 108: encode the prompt then map the result", 8),
        ["round", "108:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 108: encode the prompt then map the result", 12),
        ["round 108:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 108: encode the prompt then map the result", 16),
        ["round 108:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 108: encode the prompt then map the result", 24),
        ["round 108: encode the", "prompt then map the", "result"],
    ),
    (("round 108: encode the prompt then map the result", 32), ["round 108: encode the prompt", "then map the result"]),
    (
        ("round 108: the kernel wakes the worker at dawn", 4),
        ["round", "108:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 108: the kernel wakes the worker at dawn", 8),
        ["round", "108: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 108: the kernel wakes the worker at dawn", 12),
        ["round 108:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 108: the kernel wakes the worker at dawn", 16), ["round 108: the", "kernel wakes the", "worker at dawn"]),
    (("round 108: the kernel wakes the worker at dawn", 24), ["round 108: the kernel", "wakes the worker at dawn"]),
    (("round 108: the kernel wakes the worker at dawn", 32), ["round 108: the kernel wakes the", "worker at dawn"]),
    (
        ("round 108: service latency drops after the patch", 4),
        ["round", "108:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 108: service latency drops after the patch", 8),
        ["round", "108:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 108: service latency drops after the patch", 12),
        ["round 108:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 108: service latency drops after the patch", 16),
        ["round 108:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 108: service latency drops after the patch", 24),
        ["round 108: service", "latency drops after the", "patch"],
    ),
    (("round 108: service latency drops after the patch", 32), ["round 108: service latency drops", "after the patch"]),
    (
        ("round 108: the library caches every vector it sees", 4),
        ["round", "108:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 108: the library caches every vector it sees", 8),
        ["round", "108: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 108: the library caches every vector it sees", 12),
        ["round 108:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 108: the library caches every vector it sees", 16),
        ["round 108: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 108: the library caches every vector it sees", 24),
        ["round 108: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 108: the library caches every vector it sees", 32),
        ["round 108: the library caches", "every vector it sees"],
    ),
    (
        ("round 108: agents argue then the debate resolves", 4),
        ["round", "108:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 108: agents argue then the debate resolves", 8),
        ["round", "108:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 108: agents argue then the debate resolves", 12),
        ["round 108:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 108: agents argue then the debate resolves", 16),
        ["round 108:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 108: agents argue then the debate resolves", 24), ["round 108: agents argue", "then the debate resolves"]),
    (("round 108: agents argue then the debate resolves", 32), ["round 108: agents argue then the", "debate resolves"]),
    (
        ("round 108: the filter keeps only strong matches", 4),
        ["round", "108:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 108: the filter keeps only strong matches", 8),
        ["round", "108: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 108: the filter keeps only strong matches", 12),
        ["round 108:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 108: the filter keeps only strong matches", 16),
        ["round 108: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 108: the filter keeps only strong matches", 24),
        ["round 108: the filter", "keeps only strong", "matches"],
    ),
    (("round 108: the filter keeps only strong matches", 32), ["round 108: the filter keeps only", "strong matches"]),
    (
        ("round 108: the model answers with a short reply", 4),
        ["round", "108:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 108: the model answers with a short reply", 8),
        ["round", "108: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 108: the model answers with a short reply", 12),
        ["round 108:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 108: the model answers with a short reply", 16),
        ["round 108: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 108: the model answers with a short reply", 24),
        ["round 108: the model", "answers with a short", "reply"],
    ),
    (("round 108: the model answers with a short reply", 32), ["round 108: the model answers", "with a short reply"]),
    (
        ("round 108: the recorder stores the reasoning trace", 4),
        ["round", "108:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 108: the recorder stores the reasoning trace", 8),
        ["round", "108: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 108: the recorder stores the reasoning trace", 12),
        ["round 108:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 108: the recorder stores the reasoning trace", 16),
        ["round 108: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 108: the recorder stores the reasoning trace", 24),
        ["round 108: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 108: the recorder stores the reasoning trace", 32),
        ["round 108: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 108: the angel watches the processor run", 4),
        ["round", "108:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 108: the angel watches the processor run", 8),
        ["round", "108: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 108: the angel watches the processor run", 12),
        ["round 108:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 108: the angel watches the processor run", 16),
        ["round 108: the", "angel watches", "the processor", "run"],
    ),
    (("round 108: the angel watches the processor run", 24), ["round 108: the angel", "watches the processor", "run"]),
    (("round 108: the angel watches the processor run", 32), ["round 108: the angel watches the", "processor run"]),
    (
        ("round 108: angle of the vector decides the match", 4),
        ["round", "108:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 108: angle of the vector decides the match", 8),
        ["round", "108:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 108: angle of the vector decides the match", 12),
        ["round 108:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 108: angle of the vector decides the match", 16),
        ["round 108: angle", "of the vector", "decides the", "match"],
    ),
    (("round 108: angle of the vector decides the match", 24), ["round 108: angle of the", "vector decides the match"]),
    (("round 108: angle of the vector decides the match", 32), ["round 108: angle of the vector", "decides the match"]),
    (
        ("round 108: the candle burns twice as long at night", 4),
        ["round", "108:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 108: the candle burns twice as long at night", 8),
        ["round", "108: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 108: the candle burns twice as long at night", 12),
        ["round 108:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 108: the candle burns twice as long at night", 16),
        ["round 108: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 108: the candle burns twice as long at night", 24),
        ["round 108: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 108: the candle burns twice as long at night", 32),
        ["round 108: the candle burns", "twice as long at night"],
    ),
    (
        ("round 108: a mirror of the universe in one line", 4),
        ["round", "108:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 108: a mirror of the universe in one line", 8),
        ["round", "108: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 108: a mirror of the universe in one line", 12),
        ["round 108: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 108: a mirror of the universe in one line", 16),
        ["round 108: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 108: a mirror of the universe in one line", 24), ["round 108: a mirror of", "the universe in one line"]),
    (("round 108: a mirror of the universe in one line", 32), ["round 108: a mirror of the", "universe in one line"]),
    (
        ("round 108: the queue drains before the storm", 4),
        ["round", "108:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 108: the queue drains before the storm", 8),
        ["round", "108: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 108: the queue drains before the storm", 12),
        ["round 108:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 108: the queue drains before the storm", 16), ["round 108: the", "queue drains", "before the storm"]),
    (("round 108: the queue drains before the storm", 24), ["round 108: the queue", "drains before the storm"]),
    (("round 108: the queue drains before the storm", 32), ["round 108: the queue drains", "before the storm"]),
    (
        ("kitten108 sitting108 agent108 angle108 universe108 memory108", 6),
        ["kitten108", "sitting108", "agent108", "angle108", "universe108", "memory108"],
    ),
    (
        ("kitten108 sitting108 agent108 angle108 universe108 memory108", 10),
        ["kitten108", "sitting108", "agent108", "angle108", "universe108", "memory108"],
    ),
    (
        ("kitten108 sitting108 agent108 angle108 universe108 memory108", 18),
        ["kitten108", "sitting108", "agent108 angle108", "universe108", "memory108"],
    ),
    (
        ("kitten108 sitting108 agent108 angle108 universe108 memory108", 28),
        ["kitten108 sitting108", "agent108 angle108", "universe108 memory108"],
    ),
    (
        ("sitting108 agent108 angle108 universe108 memory108 stream108", 6),
        ["sitting108", "agent108", "angle108", "universe108", "memory108", "stream108"],
    ),
    (
        ("sitting108 agent108 angle108 universe108 memory108 stream108", 10),
        ["sitting108", "agent108", "angle108", "universe108", "memory108", "stream108"],
    ),
    (
        ("sitting108 agent108 angle108 universe108 memory108 stream108", 18),
        ["sitting108", "agent108 angle108", "universe108", "memory108", "stream108"],
    ),
    (
        ("sitting108 agent108 angle108 universe108 memory108 stream108", 28),
        ["sitting108 agent108 angle108", "universe108 memory108", "stream108"],
    ),
    (
        ("agent108 angle108 universe108 memory108 stream108 context108", 6),
        ["agent108", "angle108", "universe108", "memory108", "stream108", "context108"],
    ),
    (
        ("agent108 angle108 universe108 memory108 stream108 context108", 10),
        ["agent108", "angle108", "universe108", "memory108", "stream108", "context108"],
    ),
    (
        ("agent108 angle108 universe108 memory108 stream108 context108", 18),
        ["agent108 angle108", "universe108", "memory108", "stream108", "context108"],
    ),
    (
        ("agent108 angle108 universe108 memory108 stream108 context108", 28),
        ["agent108 angle108", "universe108 memory108", "stream108 context108"],
    ),
    (
        ("angle108 universe108 memory108 stream108 context108 knowledge108", 6),
        ["angle108", "universe108", "memory108", "stream108", "context108", "knowledge108"],
    ),
    (
        ("angle108 universe108 memory108 stream108 context108 knowledge108", 10),
        ["angle108", "universe108", "memory108", "stream108", "context108", "knowledge108"],
    ),
    (
        ("angle108 universe108 memory108 stream108 context108 knowledge108", 18),
        ["angle108", "universe108", "memory108", "stream108", "context108", "knowledge108"],
    ),
    (
        ("angle108 universe108 memory108 stream108 context108 knowledge108", 28),
        ["angle108 universe108", "memory108 stream108", "context108 knowledge108"],
    ),
    (
        ("universe108 memory108 stream108 context108 knowledge108 vector108", 6),
        ["universe108", "memory108", "stream108", "context108", "knowledge108", "vector108"],
    ),
    (
        ("universe108 memory108 stream108 context108 knowledge108 vector108", 10),
        ["universe108", "memory108", "stream108", "context108", "knowledge108", "vector108"],
    ),
    (
        ("universe108 memory108 stream108 context108 knowledge108 vector108", 18),
        ["universe108", "memory108", "stream108", "context108", "knowledge108", "vector108"],
    ),
    (
        ("universe108 memory108 stream108 context108 knowledge108 vector108", 28),
        ["universe108 memory108", "stream108 context108", "knowledge108 vector108"],
    ),
    (
        ("memory108 stream108 context108 knowledge108 vector108 processor108", 6),
        ["memory108", "stream108", "context108", "knowledge108", "vector108", "processor108"],
    ),
    (
        ("memory108 stream108 context108 knowledge108 vector108 processor108", 10),
        ["memory108", "stream108", "context108", "knowledge108", "vector108", "processor108"],
    ),
    (
        ("memory108 stream108 context108 knowledge108 vector108 processor108", 18),
        ["memory108", "stream108", "context108", "knowledge108", "vector108", "processor108"],
    ),
    (
        ("memory108 stream108 context108 knowledge108 vector108 processor108", 28),
        ["memory108 stream108", "context108 knowledge108", "vector108 processor108"],
    ),
    (
        ("stream108 context108 knowledge108 vector108 processor108 reasoning108", 6),
        ["stream108", "context108", "knowledge108", "vector108", "processor108", "reasoning108"],
    ),
    (
        ("stream108 context108 knowledge108 vector108 processor108 reasoning108", 10),
        ["stream108", "context108", "knowledge108", "vector108", "processor108", "reasoning108"],
    ),
    (
        ("stream108 context108 knowledge108 vector108 processor108 reasoning108", 18),
        ["stream108", "context108", "knowledge108", "vector108", "processor108", "reasoning108"],
    ),
    (
        ("stream108 context108 knowledge108 vector108 processor108 reasoning108", 28),
        ["stream108 context108", "knowledge108 vector108", "processor108 reasoning108"],
    ),
    (
        ("context108 knowledge108 vector108 processor108 reasoning108 machine108", 6),
        ["context108", "knowledge108", "vector108", "processor108", "reasoning108", "machine108"],
    ),
    (
        ("context108 knowledge108 vector108 processor108 reasoning108 machine108", 10),
        ["context108", "knowledge108", "vector108", "processor108", "reasoning108", "machine108"],
    ),
    (
        ("context108 knowledge108 vector108 processor108 reasoning108 machine108", 18),
        ["context108", "knowledge108", "vector108", "processor108", "reasoning108", "machine108"],
    ),
    (
        ("context108 knowledge108 vector108 processor108 reasoning108 machine108", 28),
        ["context108 knowledge108", "vector108 processor108", "reasoning108 machine108"],
    ),
    (
        ("knowledge108 vector108 processor108 reasoning108 machine108 learning108", 6),
        ["knowledge108", "vector108", "processor108", "reasoning108", "machine108", "learning108"],
    ),
    (
        ("knowledge108 vector108 processor108 reasoning108 machine108 learning108", 10),
        ["knowledge108", "vector108", "processor108", "reasoning108", "machine108", "learning108"],
    ),
    (
        ("knowledge108 vector108 processor108 reasoning108 machine108 learning108", 18),
        ["knowledge108", "vector108", "processor108", "reasoning108", "machine108", "learning108"],
    ),
    (
        ("knowledge108 vector108 processor108 reasoning108 machine108 learning108", 28),
        ["knowledge108 vector108", "processor108 reasoning108", "machine108 learning108"],
    ),
    (
        ("vector108 processor108 reasoning108 machine108 learning108 model108", 6),
        ["vector108", "processor108", "reasoning108", "machine108", "learning108", "model108"],
    ),
    (
        ("vector108 processor108 reasoning108 machine108 learning108 model108", 10),
        ["vector108", "processor108", "reasoning108", "machine108", "learning108", "model108"],
    ),
    (
        ("vector108 processor108 reasoning108 machine108 learning108 model108", 18),
        ["vector108", "processor108", "reasoning108", "machine108", "learning108", "model108"],
    ),
    (
        ("vector108 processor108 reasoning108 machine108 learning108 model108", 28),
        ["vector108 processor108", "reasoning108 machine108", "learning108 model108"],
    ),
    (
        ("processor108 reasoning108 machine108 learning108 model108 token108", 6),
        ["processor108", "reasoning108", "machine108", "learning108", "model108", "token108"],
    ),
    (
        ("processor108 reasoning108 machine108 learning108 model108 token108", 10),
        ["processor108", "reasoning108", "machine108", "learning108", "model108", "token108"],
    ),
    (
        ("processor108 reasoning108 machine108 learning108 model108 token108", 18),
        ["processor108", "reasoning108", "machine108", "learning108", "model108 token108"],
    ),
    (
        ("processor108 reasoning108 machine108 learning108 model108 token108", 28),
        ["processor108 reasoning108", "machine108 learning108", "model108 token108"],
    ),
    (
        ("reasoning108 machine108 learning108 model108 token108 prompt108", 6),
        ["reasoning108", "machine108", "learning108", "model108", "token108", "prompt108"],
    ),
    (
        ("reasoning108 machine108 learning108 model108 token108 prompt108", 10),
        ["reasoning108", "machine108", "learning108", "model108", "token108", "prompt108"],
    ),
    (
        ("reasoning108 machine108 learning108 model108 token108 prompt108", 18),
        ["reasoning108", "machine108", "learning108", "model108 token108", "prompt108"],
    ),
    (
        ("reasoning108 machine108 learning108 model108 token108 prompt108", 28),
        ["reasoning108 machine108", "learning108 model108", "token108 prompt108"],
    ),
    (
        ("machine108 learning108 model108 token108 prompt108 session108", 6),
        ["machine108", "learning108", "model108", "token108", "prompt108", "session108"],
    ),
    (
        ("machine108 learning108 model108 token108 prompt108 session108", 10),
        ["machine108", "learning108", "model108", "token108", "prompt108", "session108"],
    ),
    (
        ("machine108 learning108 model108 token108 prompt108 session108", 18),
        ["machine108", "learning108", "model108 token108", "prompt108", "session108"],
    ),
    (
        ("machine108 learning108 model108 token108 prompt108 session108", 28),
        ["machine108 learning108", "model108 token108 prompt108", "session108"],
    ),
    (
        ("learning108 model108 token108 prompt108 session108 library108", 6),
        ["learning108", "model108", "token108", "prompt108", "session108", "library108"],
    ),
    (
        ("learning108 model108 token108 prompt108 session108 library108", 10),
        ["learning108", "model108", "token108", "prompt108", "session108", "library108"],
    ),
    (
        ("learning108 model108 token108 prompt108 session108 library108", 18),
        ["learning108", "model108 token108", "prompt108", "session108", "library108"],
    ),
    (
        ("learning108 model108 token108 prompt108 session108 library108", 28),
        ["learning108 model108", "token108 prompt108", "session108 library108"],
    ),
    (
        ("model108 token108 prompt108 session108 library108 service108", 6),
        ["model108", "token108", "prompt108", "session108", "library108", "service108"],
    ),
    (
        ("model108 token108 prompt108 session108 library108 service108", 10),
        ["model108", "token108", "prompt108", "session108", "library108", "service108"],
    ),
    (
        ("model108 token108 prompt108 session108 library108 service108", 18),
        ["model108 token108", "prompt108", "session108", "library108", "service108"],
    ),
    (
        ("model108 token108 prompt108 session108 library108 service108", 28),
        ["model108 token108 prompt108", "session108 library108", "service108"],
    ),
    (
        ("token108 prompt108 session108 library108 service108 gateway108", 6),
        ["token108", "prompt108", "session108", "library108", "service108", "gateway108"],
    ),
    (
        ("token108 prompt108 session108 library108 service108 gateway108", 10),
        ["token108", "prompt108", "session108", "library108", "service108", "gateway108"],
    ),
    (
        ("token108 prompt108 session108 library108 service108 gateway108", 18),
        ["token108 prompt108", "session108", "library108", "service108", "gateway108"],
    ),
    (
        ("token108 prompt108 session108 library108 service108 gateway108", 28),
        ["token108 prompt108", "session108 library108", "service108 gateway108"],
    ),
    (
        ("prompt108 session108 library108 service108 gateway108 storage108", 6),
        ["prompt108", "session108", "library108", "service108", "gateway108", "storage108"],
    ),
    (
        ("prompt108 session108 library108 service108 gateway108 storage108", 10),
        ["prompt108", "session108", "library108", "service108", "gateway108", "storage108"],
    ),
    (
        ("prompt108 session108 library108 service108 gateway108 storage108", 18),
        ["prompt108", "session108", "library108", "service108", "gateway108", "storage108"],
    ),
    (
        ("prompt108 session108 library108 service108 gateway108 storage108", 28),
        ["prompt108 session108", "library108 service108", "gateway108 storage108"],
    ),
    (
        ("session108 library108 service108 gateway108 storage108 network108", 6),
        ["session108", "library108", "service108", "gateway108", "storage108", "network108"],
    ),
    (
        ("session108 library108 service108 gateway108 storage108 network108", 10),
        ["session108", "library108", "service108", "gateway108", "storage108", "network108"],
    ),
    (
        ("session108 library108 service108 gateway108 storage108 network108", 18),
        ["session108", "library108", "service108", "gateway108", "storage108", "network108"],
    ),
    (
        ("session108 library108 service108 gateway108 storage108 network108", 28),
        ["session108 library108", "service108 gateway108", "storage108 network108"],
    ),
    (
        ("library108 service108 gateway108 storage108 network108 latency108", 6),
        ["library108", "service108", "gateway108", "storage108", "network108", "latency108"],
    ),
    (
        ("library108 service108 gateway108 storage108 network108 latency108", 10),
        ["library108", "service108", "gateway108", "storage108", "network108", "latency108"],
    ),
    (
        ("library108 service108 gateway108 storage108 network108 latency108", 18),
        ["library108", "service108", "gateway108", "storage108", "network108", "latency108"],
    ),
    (
        ("library108 service108 gateway108 storage108 network108 latency108", 28),
        ["library108 service108", "gateway108 storage108", "network108 latency108"],
    ),
    (
        ("service108 gateway108 storage108 network108 latency108 buffer108", 6),
        ["service108", "gateway108", "storage108", "network108", "latency108", "buffer108"],
    ),
    (
        ("service108 gateway108 storage108 network108 latency108 buffer108", 10),
        ["service108", "gateway108", "storage108", "network108", "latency108", "buffer108"],
    ),
    (
        ("service108 gateway108 storage108 network108 latency108 buffer108", 18),
        ["service108", "gateway108", "storage108", "network108", "latency108", "buffer108"],
    ),
    (
        ("service108 gateway108 storage108 network108 latency108 buffer108", 28),
        ["service108 gateway108", "storage108 network108", "latency108 buffer108"],
    ),
    (
        ("gateway108 storage108 network108 latency108 buffer108 queue108", 6),
        ["gateway108", "storage108", "network108", "latency108", "buffer108", "queue108"],
    ),
    (
        ("gateway108 storage108 network108 latency108 buffer108 queue108", 10),
        ["gateway108", "storage108", "network108", "latency108", "buffer108", "queue108"],
    ),
    (
        ("gateway108 storage108 network108 latency108 buffer108 queue108", 18),
        ["gateway108", "storage108", "network108", "latency108", "buffer108 queue108"],
    ),
    (
        ("gateway108 storage108 network108 latency108 buffer108 queue108", 28),
        ["gateway108 storage108", "network108 latency108", "buffer108 queue108"],
    ),
    (
        ("storage108 network108 latency108 buffer108 queue108 worker108", 6),
        ["storage108", "network108", "latency108", "buffer108", "queue108", "worker108"],
    ),
    (
        ("storage108 network108 latency108 buffer108 queue108 worker108", 10),
        ["storage108", "network108", "latency108", "buffer108", "queue108", "worker108"],
    ),
    (
        ("storage108 network108 latency108 buffer108 queue108 worker108", 18),
        ["storage108", "network108", "latency108", "buffer108 queue108", "worker108"],
    ),
    (
        ("storage108 network108 latency108 buffer108 queue108 worker108", 28),
        ["storage108 network108", "latency108 buffer108", "queue108 worker108"],
    ),
    (
        ("network108 latency108 buffer108 queue108 worker108 kernel108", 6),
        ["network108", "latency108", "buffer108", "queue108", "worker108", "kernel108"],
    ),
    (
        ("network108 latency108 buffer108 queue108 worker108 kernel108", 10),
        ["network108", "latency108", "buffer108", "queue108", "worker108", "kernel108"],
    ),
    (
        ("network108 latency108 buffer108 queue108 worker108 kernel108", 18),
        ["network108", "latency108", "buffer108 queue108", "worker108", "kernel108"],
    ),
    (
        ("network108 latency108 buffer108 queue108 worker108 kernel108", 28),
        ["network108 latency108", "buffer108 queue108 worker108", "kernel108"],
    ),
    (
        ("latency108 buffer108 queue108 worker108 kernel108 signal108", 6),
        ["latency108", "buffer108", "queue108", "worker108", "kernel108", "signal108"],
    ),
    (
        ("latency108 buffer108 queue108 worker108 kernel108 signal108", 10),
        ["latency108", "buffer108", "queue108", "worker108", "kernel108", "signal108"],
    ),
    (
        ("latency108 buffer108 queue108 worker108 kernel108 signal108", 18),
        ["latency108", "buffer108 queue108", "worker108", "kernel108", "signal108"],
    ),
    (
        ("latency108 buffer108 queue108 worker108 kernel108 signal108", 28),
        ["latency108 buffer108", "queue108 worker108 kernel108", "signal108"],
    ),
    (
        ("buffer108 queue108 worker108 kernel108 signal108 packet108", 6),
        ["buffer108", "queue108", "worker108", "kernel108", "signal108", "packet108"],
    ),
    (
        ("buffer108 queue108 worker108 kernel108 signal108 packet108", 10),
        ["buffer108", "queue108", "worker108", "kernel108", "signal108", "packet108"],
    ),
    (
        ("buffer108 queue108 worker108 kernel108 signal108 packet108", 18),
        ["buffer108 queue108", "worker108", "kernel108", "signal108", "packet108"],
    ),
    (
        ("buffer108 queue108 worker108 kernel108 signal108 packet108", 28),
        ["buffer108 queue108 worker108", "kernel108 signal108", "packet108"],
    ),
    (
        ("queue108 worker108 kernel108 signal108 packet108 router108", 6),
        ["queue108", "worker108", "kernel108", "signal108", "packet108", "router108"],
    ),
    (
        ("queue108 worker108 kernel108 signal108 packet108 router108", 10),
        ["queue108", "worker108", "kernel108", "signal108", "packet108", "router108"],
    ),
    (
        ("queue108 worker108 kernel108 signal108 packet108 router108", 18),
        ["queue108 worker108", "kernel108", "signal108", "packet108", "router108"],
    ),
    (
        ("queue108 worker108 kernel108 signal108 packet108 router108", 28),
        ["queue108 worker108 kernel108", "signal108 packet108", "router108"],
    ),
    (
        ("worker108 kernel108 signal108 packet108 router108 cluster108", 6),
        ["worker108", "kernel108", "signal108", "packet108", "router108", "cluster108"],
    ),
    (
        ("worker108 kernel108 signal108 packet108 router108 cluster108", 10),
        ["worker108", "kernel108", "signal108", "packet108", "router108", "cluster108"],
    ),
    (
        ("worker108 kernel108 signal108 packet108 router108 cluster108", 18),
        ["worker108", "kernel108", "signal108", "packet108", "router108", "cluster108"],
    ),
    (
        ("worker108 kernel108 signal108 packet108 router108 cluster108", 28),
        ["worker108 kernel108", "signal108 packet108", "router108 cluster108"],
    ),
    (
        ("kernel108 signal108 packet108 router108 cluster108 mirror108", 6),
        ["kernel108", "signal108", "packet108", "router108", "cluster108", "mirror108"],
    ),
    (
        ("kernel108 signal108 packet108 router108 cluster108 mirror108", 10),
        ["kernel108", "signal108", "packet108", "router108", "cluster108", "mirror108"],
    ),
    (
        ("kernel108 signal108 packet108 router108 cluster108 mirror108", 18),
        ["kernel108", "signal108", "packet108", "router108", "cluster108", "mirror108"],
    ),
    (
        ("kernel108 signal108 packet108 router108 cluster108 mirror108", 28),
        ["kernel108 signal108", "packet108 router108", "cluster108 mirror108"],
    ),
    (
        ("signal108 packet108 router108 cluster108 mirror108 filter108", 6),
        ["signal108", "packet108", "router108", "cluster108", "mirror108", "filter108"],
    ),
    (
        ("signal108 packet108 router108 cluster108 mirror108 filter108", 10),
        ["signal108", "packet108", "router108", "cluster108", "mirror108", "filter108"],
    ),
    (
        ("signal108 packet108 router108 cluster108 mirror108 filter108", 18),
        ["signal108", "packet108", "router108", "cluster108", "mirror108", "filter108"],
    ),
    (
        ("signal108 packet108 router108 cluster108 mirror108 filter108", 28),
        ["signal108 packet108", "router108 cluster108", "mirror108 filter108"],
    ),
    (
        ("packet108 router108 cluster108 mirror108 filter108 ranking108", 6),
        ["packet108", "router108", "cluster108", "mirror108", "filter108", "ranking108"],
    ),
    (
        ("packet108 router108 cluster108 mirror108 filter108 ranking108", 10),
        ["packet108", "router108", "cluster108", "mirror108", "filter108", "ranking108"],
    ),
    (
        ("packet108 router108 cluster108 mirror108 filter108 ranking108", 18),
        ["packet108", "router108", "cluster108", "mirror108", "filter108", "ranking108"],
    ),
    (
        ("packet108 router108 cluster108 mirror108 filter108 ranking108", 28),
        ["packet108 router108", "cluster108 mirror108", "filter108 ranking108"],
    ),
    (
        ("router108 cluster108 mirror108 filter108 ranking108 encoding108", 6),
        ["router108", "cluster108", "mirror108", "filter108", "ranking108", "encoding108"],
    ),
    (
        ("router108 cluster108 mirror108 filter108 ranking108 encoding108", 10),
        ["router108", "cluster108", "mirror108", "filter108", "ranking108", "encoding108"],
    ),
    (
        ("router108 cluster108 mirror108 filter108 ranking108 encoding108", 18),
        ["router108", "cluster108", "mirror108", "filter108", "ranking108", "encoding108"],
    ),
    (
        ("router108 cluster108 mirror108 filter108 ranking108 encoding108", 28),
        ["router108 cluster108", "mirror108 filter108", "ranking108 encoding108"],
    ),
    (
        ("cluster108 mirror108 filter108 ranking108 encoding108 mapping108", 6),
        ["cluster108", "mirror108", "filter108", "ranking108", "encoding108", "mapping108"],
    ),
    (
        ("cluster108 mirror108 filter108 ranking108 encoding108 mapping108", 10),
        ["cluster108", "mirror108", "filter108", "ranking108", "encoding108", "mapping108"],
    ),
    (
        ("cluster108 mirror108 filter108 ranking108 encoding108 mapping108", 18),
        ["cluster108", "mirror108", "filter108", "ranking108", "encoding108", "mapping108"],
    ),
    (
        ("cluster108 mirror108 filter108 ranking108 encoding108 mapping108", 28),
        ["cluster108 mirror108", "filter108 ranking108", "encoding108 mapping108"],
    ),
    (
        ("mirror108 filter108 ranking108 encoding108 mapping108 record108", 6),
        ["mirror108", "filter108", "ranking108", "encoding108", "mapping108", "record108"],
    ),
    (
        ("mirror108 filter108 ranking108 encoding108 mapping108 record108", 10),
        ["mirror108", "filter108", "ranking108", "encoding108", "mapping108", "record108"],
    ),
    (
        ("mirror108 filter108 ranking108 encoding108 mapping108 record108", 18),
        ["mirror108", "filter108", "ranking108", "encoding108", "mapping108", "record108"],
    ),
    (
        ("mirror108 filter108 ranking108 encoding108 mapping108 record108", 28),
        ["mirror108 filter108", "ranking108 encoding108", "mapping108 record108"],
    ),
    (
        ("filter108 ranking108 encoding108 mapping108 record108 candle108", 6),
        ["filter108", "ranking108", "encoding108", "mapping108", "record108", "candle108"],
    ),
    (
        ("filter108 ranking108 encoding108 mapping108 record108 candle108", 10),
        ["filter108", "ranking108", "encoding108", "mapping108", "record108", "candle108"],
    ),
    (
        ("filter108 ranking108 encoding108 mapping108 record108 candle108", 18),
        ["filter108", "ranking108", "encoding108", "mapping108", "record108", "candle108"],
    ),
    (
        ("filter108 ranking108 encoding108 mapping108 record108 candle108", 28),
        ["filter108 ranking108", "encoding108 mapping108", "record108 candle108"],
    ),
    (
        ("ranking108 encoding108 mapping108 record108 candle108 thread108", 6),
        ["ranking108", "encoding108", "mapping108", "record108", "candle108", "thread108"],
    ),
    (
        ("ranking108 encoding108 mapping108 record108 candle108 thread108", 10),
        ["ranking108", "encoding108", "mapping108", "record108", "candle108", "thread108"],
    ),
    (
        ("ranking108 encoding108 mapping108 record108 candle108 thread108", 18),
        ["ranking108", "encoding108", "mapping108", "record108", "candle108", "thread108"],
    ),
    (
        ("ranking108 encoding108 mapping108 record108 candle108 thread108", 28),
        ["ranking108 encoding108", "mapping108 record108", "candle108 thread108"],
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
