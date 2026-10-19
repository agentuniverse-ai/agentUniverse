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
        ("round 742: the quick brown fox jumps over the lazy dog", 4),
        ["round", "742:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", 8),
        ["round", "742: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", 12),
        ["round 742:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", 16),
        ["round 742: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", 24),
        ["round 742: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 742: the quick brown fox jumps over the lazy dog", 32),
        ["round 742: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", 4),
        ["round", "742:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", 8),
        ["round", "742:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", 12),
        ["round 742:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", 16),
        ["round 742:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", 24),
        ["round 742: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 742: agentuniverse is a framework for multi agents", 32),
        ["round 742: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", 4),
        ["round", "742:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", 8),
        ["round", "742:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", 12),
        ["round 742:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", 16),
        ["round 742:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", 24),
        ["round 742: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 742: knowledge stored as vectors enables retrieval", 32),
        ["round 742: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 742: the processor reads the record then stops", 4),
        ["round", "742:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 742: the processor reads the record then stops", 8),
        ["round", "742: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 742: the processor reads the record then stops", 12),
        ["round 742:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 742: the processor reads the record then stops", 16),
        ["round 742: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 742: the processor reads the record then stops", 24),
        ["round 742: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 742: the processor reads the record then stops", 32),
        ["round 742: the processor reads", "the record then stops"],
    ),
    (
        ("round 742: a worker pulls the next task from the queue", 4),
        ["round", "742:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 742: a worker pulls the next task from the queue", 8),
        ["round", "742: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 742: a worker pulls the next task from the queue", 12),
        ["round 742: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 742: a worker pulls the next task from the queue", 16),
        ["round 742: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 742: a worker pulls the next task from the queue", 24),
        ["round 742: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 742: a worker pulls the next task from the queue", 32),
        ["round 742: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 742: signals travel through the network layer", 4),
        ["round", "742:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 742: signals travel through the network layer", 8),
        ["round", "742:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 742: signals travel through the network layer", 12),
        ["round 742:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 742: signals travel through the network layer", 16),
        ["round 742:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 742: signals travel through the network layer", 24),
        ["round 742: signals", "travel through the", "network layer"],
    ),
    (
        ("round 742: signals travel through the network layer", 32),
        ["round 742: signals travel", "through the network layer"],
    ),
    (
        ("round 742: the gateway routes each request by policy", 4),
        ["round", "742:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 742: the gateway routes each request by policy", 8),
        ["round", "742: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 742: the gateway routes each request by policy", 12),
        ["round 742:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 742: the gateway routes each request by policy", 16),
        ["round 742: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 742: the gateway routes each request by policy", 24),
        ["round 742: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 742: the gateway routes each request by policy", 32),
        ["round 742: the gateway routes", "each request by policy"],
    ),
    (
        ("round 742: memory grows until the buffer is full", 4),
        ["round", "742:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 742: memory grows until the buffer is full", 8),
        ["round", "742:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 742: memory grows until the buffer is full", 12),
        ["round 742:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 742: memory grows until the buffer is full", 16),
        ["round 742:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 742: memory grows until the buffer is full", 24), ["round 742: memory grows", "until the buffer is full"]),
    (("round 742: memory grows until the buffer is full", 32), ["round 742: memory grows until", "the buffer is full"]),
    (
        ("round 742: the cluster mirrors every packet twice", 4),
        ["round", "742:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 742: the cluster mirrors every packet twice", 8),
        ["round", "742: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 742: the cluster mirrors every packet twice", 12),
        ["round 742:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 742: the cluster mirrors every packet twice", 16),
        ["round 742: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 742: the cluster mirrors every packet twice", 24),
        ["round 742: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 742: the cluster mirrors every packet twice", 32),
        ["round 742: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", 4),
        ["round", "742:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", 8),
        ["round", "742:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", 12),
        ["round 742:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", 16),
        ["round 742:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", 24),
        ["round 742: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 742: ranking uses tokens learned from the corpus", 32),
        ["round 742: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 742: a long session ends when the candle dies", 4),
        ["round", "742:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 742: a long session ends when the candle dies", 8),
        ["round", "742: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 742: a long session ends when the candle dies", 12),
        ["round 742: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 742: a long session ends when the candle dies", 16),
        ["round 742: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 742: a long session ends when the candle dies", 24),
        ["round 742: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 742: a long session ends when the candle dies", 32),
        ["round 742: a long session ends", "when the candle dies"],
    ),
    (
        ("round 742: encode the prompt then map the result", 4),
        ["round", "742:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 742: encode the prompt then map the result", 8),
        ["round", "742:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 742: encode the prompt then map the result", 12),
        ["round 742:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 742: encode the prompt then map the result", 16),
        ["round 742:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 742: encode the prompt then map the result", 24),
        ["round 742: encode the", "prompt then map the", "result"],
    ),
    (("round 742: encode the prompt then map the result", 32), ["round 742: encode the prompt", "then map the result"]),
    (
        ("round 742: the kernel wakes the worker at dawn", 4),
        ["round", "742:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 742: the kernel wakes the worker at dawn", 8),
        ["round", "742: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 742: the kernel wakes the worker at dawn", 12),
        ["round 742:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 742: the kernel wakes the worker at dawn", 16), ["round 742: the", "kernel wakes the", "worker at dawn"]),
    (("round 742: the kernel wakes the worker at dawn", 24), ["round 742: the kernel", "wakes the worker at dawn"]),
    (("round 742: the kernel wakes the worker at dawn", 32), ["round 742: the kernel wakes the", "worker at dawn"]),
    (
        ("round 742: service latency drops after the patch", 4),
        ["round", "742:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 742: service latency drops after the patch", 8),
        ["round", "742:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 742: service latency drops after the patch", 12),
        ["round 742:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 742: service latency drops after the patch", 16),
        ["round 742:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 742: service latency drops after the patch", 24),
        ["round 742: service", "latency drops after the", "patch"],
    ),
    (("round 742: service latency drops after the patch", 32), ["round 742: service latency drops", "after the patch"]),
    (
        ("round 742: the library caches every vector it sees", 4),
        ["round", "742:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 742: the library caches every vector it sees", 8),
        ["round", "742: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 742: the library caches every vector it sees", 12),
        ["round 742:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 742: the library caches every vector it sees", 16),
        ["round 742: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 742: the library caches every vector it sees", 24),
        ["round 742: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 742: the library caches every vector it sees", 32),
        ["round 742: the library caches", "every vector it sees"],
    ),
    (
        ("round 742: agents argue then the debate resolves", 4),
        ["round", "742:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 742: agents argue then the debate resolves", 8),
        ["round", "742:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 742: agents argue then the debate resolves", 12),
        ["round 742:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 742: agents argue then the debate resolves", 16),
        ["round 742:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 742: agents argue then the debate resolves", 24), ["round 742: agents argue", "then the debate resolves"]),
    (("round 742: agents argue then the debate resolves", 32), ["round 742: agents argue then the", "debate resolves"]),
    (
        ("round 742: the filter keeps only strong matches", 4),
        ["round", "742:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 742: the filter keeps only strong matches", 8),
        ["round", "742: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 742: the filter keeps only strong matches", 12),
        ["round 742:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 742: the filter keeps only strong matches", 16),
        ["round 742: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 742: the filter keeps only strong matches", 24),
        ["round 742: the filter", "keeps only strong", "matches"],
    ),
    (("round 742: the filter keeps only strong matches", 32), ["round 742: the filter keeps only", "strong matches"]),
    (
        ("round 742: the model answers with a short reply", 4),
        ["round", "742:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 742: the model answers with a short reply", 8),
        ["round", "742: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 742: the model answers with a short reply", 12),
        ["round 742:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 742: the model answers with a short reply", 16),
        ["round 742: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 742: the model answers with a short reply", 24),
        ["round 742: the model", "answers with a short", "reply"],
    ),
    (("round 742: the model answers with a short reply", 32), ["round 742: the model answers", "with a short reply"]),
    (
        ("round 742: the recorder stores the reasoning trace", 4),
        ["round", "742:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 742: the recorder stores the reasoning trace", 8),
        ["round", "742: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 742: the recorder stores the reasoning trace", 12),
        ["round 742:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 742: the recorder stores the reasoning trace", 16),
        ["round 742: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 742: the recorder stores the reasoning trace", 24),
        ["round 742: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 742: the recorder stores the reasoning trace", 32),
        ["round 742: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 742: the angel watches the processor run", 4),
        ["round", "742:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 742: the angel watches the processor run", 8),
        ["round", "742: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 742: the angel watches the processor run", 12),
        ["round 742:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 742: the angel watches the processor run", 16),
        ["round 742: the", "angel watches", "the processor", "run"],
    ),
    (("round 742: the angel watches the processor run", 24), ["round 742: the angel", "watches the processor", "run"]),
    (("round 742: the angel watches the processor run", 32), ["round 742: the angel watches the", "processor run"]),
    (
        ("round 742: angle of the vector decides the match", 4),
        ["round", "742:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 742: angle of the vector decides the match", 8),
        ["round", "742:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 742: angle of the vector decides the match", 12),
        ["round 742:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 742: angle of the vector decides the match", 16),
        ["round 742: angle", "of the vector", "decides the", "match"],
    ),
    (("round 742: angle of the vector decides the match", 24), ["round 742: angle of the", "vector decides the match"]),
    (("round 742: angle of the vector decides the match", 32), ["round 742: angle of the vector", "decides the match"]),
    (
        ("round 742: the candle burns twice as long at night", 4),
        ["round", "742:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 742: the candle burns twice as long at night", 8),
        ["round", "742: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 742: the candle burns twice as long at night", 12),
        ["round 742:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 742: the candle burns twice as long at night", 16),
        ["round 742: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 742: the candle burns twice as long at night", 24),
        ["round 742: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 742: the candle burns twice as long at night", 32),
        ["round 742: the candle burns", "twice as long at night"],
    ),
    (
        ("round 742: a mirror of the universe in one line", 4),
        ["round", "742:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 742: a mirror of the universe in one line", 8),
        ["round", "742: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 742: a mirror of the universe in one line", 12),
        ["round 742: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 742: a mirror of the universe in one line", 16),
        ["round 742: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 742: a mirror of the universe in one line", 24), ["round 742: a mirror of", "the universe in one line"]),
    (("round 742: a mirror of the universe in one line", 32), ["round 742: a mirror of the", "universe in one line"]),
    (
        ("round 742: the queue drains before the storm", 4),
        ["round", "742:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 742: the queue drains before the storm", 8),
        ["round", "742: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 742: the queue drains before the storm", 12),
        ["round 742:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 742: the queue drains before the storm", 16), ["round 742: the", "queue drains", "before the storm"]),
    (("round 742: the queue drains before the storm", 24), ["round 742: the queue", "drains before the storm"]),
    (("round 742: the queue drains before the storm", 32), ["round 742: the queue drains", "before the storm"]),
    (
        ("kitten742 sitting742 agent742 angle742 universe742 memory742", 6),
        ["kitten742", "sitting742", "agent742", "angle742", "universe742", "memory742"],
    ),
    (
        ("kitten742 sitting742 agent742 angle742 universe742 memory742", 10),
        ["kitten742", "sitting742", "agent742", "angle742", "universe742", "memory742"],
    ),
    (
        ("kitten742 sitting742 agent742 angle742 universe742 memory742", 18),
        ["kitten742", "sitting742", "agent742 angle742", "universe742", "memory742"],
    ),
    (
        ("kitten742 sitting742 agent742 angle742 universe742 memory742", 28),
        ["kitten742 sitting742", "agent742 angle742", "universe742 memory742"],
    ),
    (
        ("sitting742 agent742 angle742 universe742 memory742 stream742", 6),
        ["sitting742", "agent742", "angle742", "universe742", "memory742", "stream742"],
    ),
    (
        ("sitting742 agent742 angle742 universe742 memory742 stream742", 10),
        ["sitting742", "agent742", "angle742", "universe742", "memory742", "stream742"],
    ),
    (
        ("sitting742 agent742 angle742 universe742 memory742 stream742", 18),
        ["sitting742", "agent742 angle742", "universe742", "memory742", "stream742"],
    ),
    (
        ("sitting742 agent742 angle742 universe742 memory742 stream742", 28),
        ["sitting742 agent742 angle742", "universe742 memory742", "stream742"],
    ),
    (
        ("agent742 angle742 universe742 memory742 stream742 context742", 6),
        ["agent742", "angle742", "universe742", "memory742", "stream742", "context742"],
    ),
    (
        ("agent742 angle742 universe742 memory742 stream742 context742", 10),
        ["agent742", "angle742", "universe742", "memory742", "stream742", "context742"],
    ),
    (
        ("agent742 angle742 universe742 memory742 stream742 context742", 18),
        ["agent742 angle742", "universe742", "memory742", "stream742", "context742"],
    ),
    (
        ("agent742 angle742 universe742 memory742 stream742 context742", 28),
        ["agent742 angle742", "universe742 memory742", "stream742 context742"],
    ),
    (
        ("angle742 universe742 memory742 stream742 context742 knowledge742", 6),
        ["angle742", "universe742", "memory742", "stream742", "context742", "knowledge742"],
    ),
    (
        ("angle742 universe742 memory742 stream742 context742 knowledge742", 10),
        ["angle742", "universe742", "memory742", "stream742", "context742", "knowledge742"],
    ),
    (
        ("angle742 universe742 memory742 stream742 context742 knowledge742", 18),
        ["angle742", "universe742", "memory742", "stream742", "context742", "knowledge742"],
    ),
    (
        ("angle742 universe742 memory742 stream742 context742 knowledge742", 28),
        ["angle742 universe742", "memory742 stream742", "context742 knowledge742"],
    ),
    (
        ("universe742 memory742 stream742 context742 knowledge742 vector742", 6),
        ["universe742", "memory742", "stream742", "context742", "knowledge742", "vector742"],
    ),
    (
        ("universe742 memory742 stream742 context742 knowledge742 vector742", 10),
        ["universe742", "memory742", "stream742", "context742", "knowledge742", "vector742"],
    ),
    (
        ("universe742 memory742 stream742 context742 knowledge742 vector742", 18),
        ["universe742", "memory742", "stream742", "context742", "knowledge742", "vector742"],
    ),
    (
        ("universe742 memory742 stream742 context742 knowledge742 vector742", 28),
        ["universe742 memory742", "stream742 context742", "knowledge742 vector742"],
    ),
    (
        ("memory742 stream742 context742 knowledge742 vector742 processor742", 6),
        ["memory742", "stream742", "context742", "knowledge742", "vector742", "processor742"],
    ),
    (
        ("memory742 stream742 context742 knowledge742 vector742 processor742", 10),
        ["memory742", "stream742", "context742", "knowledge742", "vector742", "processor742"],
    ),
    (
        ("memory742 stream742 context742 knowledge742 vector742 processor742", 18),
        ["memory742", "stream742", "context742", "knowledge742", "vector742", "processor742"],
    ),
    (
        ("memory742 stream742 context742 knowledge742 vector742 processor742", 28),
        ["memory742 stream742", "context742 knowledge742", "vector742 processor742"],
    ),
    (
        ("stream742 context742 knowledge742 vector742 processor742 reasoning742", 6),
        ["stream742", "context742", "knowledge742", "vector742", "processor742", "reasoning742"],
    ),
    (
        ("stream742 context742 knowledge742 vector742 processor742 reasoning742", 10),
        ["stream742", "context742", "knowledge742", "vector742", "processor742", "reasoning742"],
    ),
    (
        ("stream742 context742 knowledge742 vector742 processor742 reasoning742", 18),
        ["stream742", "context742", "knowledge742", "vector742", "processor742", "reasoning742"],
    ),
    (
        ("stream742 context742 knowledge742 vector742 processor742 reasoning742", 28),
        ["stream742 context742", "knowledge742 vector742", "processor742 reasoning742"],
    ),
    (
        ("context742 knowledge742 vector742 processor742 reasoning742 machine742", 6),
        ["context742", "knowledge742", "vector742", "processor742", "reasoning742", "machine742"],
    ),
    (
        ("context742 knowledge742 vector742 processor742 reasoning742 machine742", 10),
        ["context742", "knowledge742", "vector742", "processor742", "reasoning742", "machine742"],
    ),
    (
        ("context742 knowledge742 vector742 processor742 reasoning742 machine742", 18),
        ["context742", "knowledge742", "vector742", "processor742", "reasoning742", "machine742"],
    ),
    (
        ("context742 knowledge742 vector742 processor742 reasoning742 machine742", 28),
        ["context742 knowledge742", "vector742 processor742", "reasoning742 machine742"],
    ),
    (
        ("knowledge742 vector742 processor742 reasoning742 machine742 learning742", 6),
        ["knowledge742", "vector742", "processor742", "reasoning742", "machine742", "learning742"],
    ),
    (
        ("knowledge742 vector742 processor742 reasoning742 machine742 learning742", 10),
        ["knowledge742", "vector742", "processor742", "reasoning742", "machine742", "learning742"],
    ),
    (
        ("knowledge742 vector742 processor742 reasoning742 machine742 learning742", 18),
        ["knowledge742", "vector742", "processor742", "reasoning742", "machine742", "learning742"],
    ),
    (
        ("knowledge742 vector742 processor742 reasoning742 machine742 learning742", 28),
        ["knowledge742 vector742", "processor742 reasoning742", "machine742 learning742"],
    ),
    (
        ("vector742 processor742 reasoning742 machine742 learning742 model742", 6),
        ["vector742", "processor742", "reasoning742", "machine742", "learning742", "model742"],
    ),
    (
        ("vector742 processor742 reasoning742 machine742 learning742 model742", 10),
        ["vector742", "processor742", "reasoning742", "machine742", "learning742", "model742"],
    ),
    (
        ("vector742 processor742 reasoning742 machine742 learning742 model742", 18),
        ["vector742", "processor742", "reasoning742", "machine742", "learning742", "model742"],
    ),
    (
        ("vector742 processor742 reasoning742 machine742 learning742 model742", 28),
        ["vector742 processor742", "reasoning742 machine742", "learning742 model742"],
    ),
    (
        ("processor742 reasoning742 machine742 learning742 model742 token742", 6),
        ["processor742", "reasoning742", "machine742", "learning742", "model742", "token742"],
    ),
    (
        ("processor742 reasoning742 machine742 learning742 model742 token742", 10),
        ["processor742", "reasoning742", "machine742", "learning742", "model742", "token742"],
    ),
    (
        ("processor742 reasoning742 machine742 learning742 model742 token742", 18),
        ["processor742", "reasoning742", "machine742", "learning742", "model742 token742"],
    ),
    (
        ("processor742 reasoning742 machine742 learning742 model742 token742", 28),
        ["processor742 reasoning742", "machine742 learning742", "model742 token742"],
    ),
    (
        ("reasoning742 machine742 learning742 model742 token742 prompt742", 6),
        ["reasoning742", "machine742", "learning742", "model742", "token742", "prompt742"],
    ),
    (
        ("reasoning742 machine742 learning742 model742 token742 prompt742", 10),
        ["reasoning742", "machine742", "learning742", "model742", "token742", "prompt742"],
    ),
    (
        ("reasoning742 machine742 learning742 model742 token742 prompt742", 18),
        ["reasoning742", "machine742", "learning742", "model742 token742", "prompt742"],
    ),
    (
        ("reasoning742 machine742 learning742 model742 token742 prompt742", 28),
        ["reasoning742 machine742", "learning742 model742", "token742 prompt742"],
    ),
    (
        ("machine742 learning742 model742 token742 prompt742 session742", 6),
        ["machine742", "learning742", "model742", "token742", "prompt742", "session742"],
    ),
    (
        ("machine742 learning742 model742 token742 prompt742 session742", 10),
        ["machine742", "learning742", "model742", "token742", "prompt742", "session742"],
    ),
    (
        ("machine742 learning742 model742 token742 prompt742 session742", 18),
        ["machine742", "learning742", "model742 token742", "prompt742", "session742"],
    ),
    (
        ("machine742 learning742 model742 token742 prompt742 session742", 28),
        ["machine742 learning742", "model742 token742 prompt742", "session742"],
    ),
    (
        ("learning742 model742 token742 prompt742 session742 library742", 6),
        ["learning742", "model742", "token742", "prompt742", "session742", "library742"],
    ),
    (
        ("learning742 model742 token742 prompt742 session742 library742", 10),
        ["learning742", "model742", "token742", "prompt742", "session742", "library742"],
    ),
    (
        ("learning742 model742 token742 prompt742 session742 library742", 18),
        ["learning742", "model742 token742", "prompt742", "session742", "library742"],
    ),
    (
        ("learning742 model742 token742 prompt742 session742 library742", 28),
        ["learning742 model742", "token742 prompt742", "session742 library742"],
    ),
    (
        ("model742 token742 prompt742 session742 library742 service742", 6),
        ["model742", "token742", "prompt742", "session742", "library742", "service742"],
    ),
    (
        ("model742 token742 prompt742 session742 library742 service742", 10),
        ["model742", "token742", "prompt742", "session742", "library742", "service742"],
    ),
    (
        ("model742 token742 prompt742 session742 library742 service742", 18),
        ["model742 token742", "prompt742", "session742", "library742", "service742"],
    ),
    (
        ("model742 token742 prompt742 session742 library742 service742", 28),
        ["model742 token742 prompt742", "session742 library742", "service742"],
    ),
    (
        ("token742 prompt742 session742 library742 service742 gateway742", 6),
        ["token742", "prompt742", "session742", "library742", "service742", "gateway742"],
    ),
    (
        ("token742 prompt742 session742 library742 service742 gateway742", 10),
        ["token742", "prompt742", "session742", "library742", "service742", "gateway742"],
    ),
    (
        ("token742 prompt742 session742 library742 service742 gateway742", 18),
        ["token742 prompt742", "session742", "library742", "service742", "gateway742"],
    ),
    (
        ("token742 prompt742 session742 library742 service742 gateway742", 28),
        ["token742 prompt742", "session742 library742", "service742 gateway742"],
    ),
    (
        ("prompt742 session742 library742 service742 gateway742 storage742", 6),
        ["prompt742", "session742", "library742", "service742", "gateway742", "storage742"],
    ),
    (
        ("prompt742 session742 library742 service742 gateway742 storage742", 10),
        ["prompt742", "session742", "library742", "service742", "gateway742", "storage742"],
    ),
    (
        ("prompt742 session742 library742 service742 gateway742 storage742", 18),
        ["prompt742", "session742", "library742", "service742", "gateway742", "storage742"],
    ),
    (
        ("prompt742 session742 library742 service742 gateway742 storage742", 28),
        ["prompt742 session742", "library742 service742", "gateway742 storage742"],
    ),
    (
        ("session742 library742 service742 gateway742 storage742 network742", 6),
        ["session742", "library742", "service742", "gateway742", "storage742", "network742"],
    ),
    (
        ("session742 library742 service742 gateway742 storage742 network742", 10),
        ["session742", "library742", "service742", "gateway742", "storage742", "network742"],
    ),
    (
        ("session742 library742 service742 gateway742 storage742 network742", 18),
        ["session742", "library742", "service742", "gateway742", "storage742", "network742"],
    ),
    (
        ("session742 library742 service742 gateway742 storage742 network742", 28),
        ["session742 library742", "service742 gateway742", "storage742 network742"],
    ),
    (
        ("library742 service742 gateway742 storage742 network742 latency742", 6),
        ["library742", "service742", "gateway742", "storage742", "network742", "latency742"],
    ),
    (
        ("library742 service742 gateway742 storage742 network742 latency742", 10),
        ["library742", "service742", "gateway742", "storage742", "network742", "latency742"],
    ),
    (
        ("library742 service742 gateway742 storage742 network742 latency742", 18),
        ["library742", "service742", "gateway742", "storage742", "network742", "latency742"],
    ),
    (
        ("library742 service742 gateway742 storage742 network742 latency742", 28),
        ["library742 service742", "gateway742 storage742", "network742 latency742"],
    ),
    (
        ("service742 gateway742 storage742 network742 latency742 buffer742", 6),
        ["service742", "gateway742", "storage742", "network742", "latency742", "buffer742"],
    ),
    (
        ("service742 gateway742 storage742 network742 latency742 buffer742", 10),
        ["service742", "gateway742", "storage742", "network742", "latency742", "buffer742"],
    ),
    (
        ("service742 gateway742 storage742 network742 latency742 buffer742", 18),
        ["service742", "gateway742", "storage742", "network742", "latency742", "buffer742"],
    ),
    (
        ("service742 gateway742 storage742 network742 latency742 buffer742", 28),
        ["service742 gateway742", "storage742 network742", "latency742 buffer742"],
    ),
    (
        ("gateway742 storage742 network742 latency742 buffer742 queue742", 6),
        ["gateway742", "storage742", "network742", "latency742", "buffer742", "queue742"],
    ),
    (
        ("gateway742 storage742 network742 latency742 buffer742 queue742", 10),
        ["gateway742", "storage742", "network742", "latency742", "buffer742", "queue742"],
    ),
    (
        ("gateway742 storage742 network742 latency742 buffer742 queue742", 18),
        ["gateway742", "storage742", "network742", "latency742", "buffer742 queue742"],
    ),
    (
        ("gateway742 storage742 network742 latency742 buffer742 queue742", 28),
        ["gateway742 storage742", "network742 latency742", "buffer742 queue742"],
    ),
    (
        ("storage742 network742 latency742 buffer742 queue742 worker742", 6),
        ["storage742", "network742", "latency742", "buffer742", "queue742", "worker742"],
    ),
    (
        ("storage742 network742 latency742 buffer742 queue742 worker742", 10),
        ["storage742", "network742", "latency742", "buffer742", "queue742", "worker742"],
    ),
    (
        ("storage742 network742 latency742 buffer742 queue742 worker742", 18),
        ["storage742", "network742", "latency742", "buffer742 queue742", "worker742"],
    ),
    (
        ("storage742 network742 latency742 buffer742 queue742 worker742", 28),
        ["storage742 network742", "latency742 buffer742", "queue742 worker742"],
    ),
    (
        ("network742 latency742 buffer742 queue742 worker742 kernel742", 6),
        ["network742", "latency742", "buffer742", "queue742", "worker742", "kernel742"],
    ),
    (
        ("network742 latency742 buffer742 queue742 worker742 kernel742", 10),
        ["network742", "latency742", "buffer742", "queue742", "worker742", "kernel742"],
    ),
    (
        ("network742 latency742 buffer742 queue742 worker742 kernel742", 18),
        ["network742", "latency742", "buffer742 queue742", "worker742", "kernel742"],
    ),
    (
        ("network742 latency742 buffer742 queue742 worker742 kernel742", 28),
        ["network742 latency742", "buffer742 queue742 worker742", "kernel742"],
    ),
    (
        ("latency742 buffer742 queue742 worker742 kernel742 signal742", 6),
        ["latency742", "buffer742", "queue742", "worker742", "kernel742", "signal742"],
    ),
    (
        ("latency742 buffer742 queue742 worker742 kernel742 signal742", 10),
        ["latency742", "buffer742", "queue742", "worker742", "kernel742", "signal742"],
    ),
    (
        ("latency742 buffer742 queue742 worker742 kernel742 signal742", 18),
        ["latency742", "buffer742 queue742", "worker742", "kernel742", "signal742"],
    ),
    (
        ("latency742 buffer742 queue742 worker742 kernel742 signal742", 28),
        ["latency742 buffer742", "queue742 worker742 kernel742", "signal742"],
    ),
    (
        ("buffer742 queue742 worker742 kernel742 signal742 packet742", 6),
        ["buffer742", "queue742", "worker742", "kernel742", "signal742", "packet742"],
    ),
    (
        ("buffer742 queue742 worker742 kernel742 signal742 packet742", 10),
        ["buffer742", "queue742", "worker742", "kernel742", "signal742", "packet742"],
    ),
    (
        ("buffer742 queue742 worker742 kernel742 signal742 packet742", 18),
        ["buffer742 queue742", "worker742", "kernel742", "signal742", "packet742"],
    ),
    (
        ("buffer742 queue742 worker742 kernel742 signal742 packet742", 28),
        ["buffer742 queue742 worker742", "kernel742 signal742", "packet742"],
    ),
    (
        ("queue742 worker742 kernel742 signal742 packet742 router742", 6),
        ["queue742", "worker742", "kernel742", "signal742", "packet742", "router742"],
    ),
    (
        ("queue742 worker742 kernel742 signal742 packet742 router742", 10),
        ["queue742", "worker742", "kernel742", "signal742", "packet742", "router742"],
    ),
    (
        ("queue742 worker742 kernel742 signal742 packet742 router742", 18),
        ["queue742 worker742", "kernel742", "signal742", "packet742", "router742"],
    ),
    (
        ("queue742 worker742 kernel742 signal742 packet742 router742", 28),
        ["queue742 worker742 kernel742", "signal742 packet742", "router742"],
    ),
    (
        ("worker742 kernel742 signal742 packet742 router742 cluster742", 6),
        ["worker742", "kernel742", "signal742", "packet742", "router742", "cluster742"],
    ),
    (
        ("worker742 kernel742 signal742 packet742 router742 cluster742", 10),
        ["worker742", "kernel742", "signal742", "packet742", "router742", "cluster742"],
    ),
    (
        ("worker742 kernel742 signal742 packet742 router742 cluster742", 18),
        ["worker742", "kernel742", "signal742", "packet742", "router742", "cluster742"],
    ),
    (
        ("worker742 kernel742 signal742 packet742 router742 cluster742", 28),
        ["worker742 kernel742", "signal742 packet742", "router742 cluster742"],
    ),
    (
        ("kernel742 signal742 packet742 router742 cluster742 mirror742", 6),
        ["kernel742", "signal742", "packet742", "router742", "cluster742", "mirror742"],
    ),
    (
        ("kernel742 signal742 packet742 router742 cluster742 mirror742", 10),
        ["kernel742", "signal742", "packet742", "router742", "cluster742", "mirror742"],
    ),
    (
        ("kernel742 signal742 packet742 router742 cluster742 mirror742", 18),
        ["kernel742", "signal742", "packet742", "router742", "cluster742", "mirror742"],
    ),
    (
        ("kernel742 signal742 packet742 router742 cluster742 mirror742", 28),
        ["kernel742 signal742", "packet742 router742", "cluster742 mirror742"],
    ),
    (
        ("signal742 packet742 router742 cluster742 mirror742 filter742", 6),
        ["signal742", "packet742", "router742", "cluster742", "mirror742", "filter742"],
    ),
    (
        ("signal742 packet742 router742 cluster742 mirror742 filter742", 10),
        ["signal742", "packet742", "router742", "cluster742", "mirror742", "filter742"],
    ),
    (
        ("signal742 packet742 router742 cluster742 mirror742 filter742", 18),
        ["signal742", "packet742", "router742", "cluster742", "mirror742", "filter742"],
    ),
    (
        ("signal742 packet742 router742 cluster742 mirror742 filter742", 28),
        ["signal742 packet742", "router742 cluster742", "mirror742 filter742"],
    ),
    (
        ("packet742 router742 cluster742 mirror742 filter742 ranking742", 6),
        ["packet742", "router742", "cluster742", "mirror742", "filter742", "ranking742"],
    ),
    (
        ("packet742 router742 cluster742 mirror742 filter742 ranking742", 10),
        ["packet742", "router742", "cluster742", "mirror742", "filter742", "ranking742"],
    ),
    (
        ("packet742 router742 cluster742 mirror742 filter742 ranking742", 18),
        ["packet742", "router742", "cluster742", "mirror742", "filter742", "ranking742"],
    ),
    (
        ("packet742 router742 cluster742 mirror742 filter742 ranking742", 28),
        ["packet742 router742", "cluster742 mirror742", "filter742 ranking742"],
    ),
    (
        ("router742 cluster742 mirror742 filter742 ranking742 encoding742", 6),
        ["router742", "cluster742", "mirror742", "filter742", "ranking742", "encoding742"],
    ),
    (
        ("router742 cluster742 mirror742 filter742 ranking742 encoding742", 10),
        ["router742", "cluster742", "mirror742", "filter742", "ranking742", "encoding742"],
    ),
    (
        ("router742 cluster742 mirror742 filter742 ranking742 encoding742", 18),
        ["router742", "cluster742", "mirror742", "filter742", "ranking742", "encoding742"],
    ),
    (
        ("router742 cluster742 mirror742 filter742 ranking742 encoding742", 28),
        ["router742 cluster742", "mirror742 filter742", "ranking742 encoding742"],
    ),
    (
        ("cluster742 mirror742 filter742 ranking742 encoding742 mapping742", 6),
        ["cluster742", "mirror742", "filter742", "ranking742", "encoding742", "mapping742"],
    ),
    (
        ("cluster742 mirror742 filter742 ranking742 encoding742 mapping742", 10),
        ["cluster742", "mirror742", "filter742", "ranking742", "encoding742", "mapping742"],
    ),
    (
        ("cluster742 mirror742 filter742 ranking742 encoding742 mapping742", 18),
        ["cluster742", "mirror742", "filter742", "ranking742", "encoding742", "mapping742"],
    ),
    (
        ("cluster742 mirror742 filter742 ranking742 encoding742 mapping742", 28),
        ["cluster742 mirror742", "filter742 ranking742", "encoding742 mapping742"],
    ),
    (
        ("mirror742 filter742 ranking742 encoding742 mapping742 record742", 6),
        ["mirror742", "filter742", "ranking742", "encoding742", "mapping742", "record742"],
    ),
    (
        ("mirror742 filter742 ranking742 encoding742 mapping742 record742", 10),
        ["mirror742", "filter742", "ranking742", "encoding742", "mapping742", "record742"],
    ),
    (
        ("mirror742 filter742 ranking742 encoding742 mapping742 record742", 18),
        ["mirror742", "filter742", "ranking742", "encoding742", "mapping742", "record742"],
    ),
    (
        ("mirror742 filter742 ranking742 encoding742 mapping742 record742", 28),
        ["mirror742 filter742", "ranking742 encoding742", "mapping742 record742"],
    ),
    (
        ("filter742 ranking742 encoding742 mapping742 record742 candle742", 6),
        ["filter742", "ranking742", "encoding742", "mapping742", "record742", "candle742"],
    ),
    (
        ("filter742 ranking742 encoding742 mapping742 record742 candle742", 10),
        ["filter742", "ranking742", "encoding742", "mapping742", "record742", "candle742"],
    ),
    (
        ("filter742 ranking742 encoding742 mapping742 record742 candle742", 18),
        ["filter742", "ranking742", "encoding742", "mapping742", "record742", "candle742"],
    ),
    (
        ("filter742 ranking742 encoding742 mapping742 record742 candle742", 28),
        ["filter742 ranking742", "encoding742 mapping742", "record742 candle742"],
    ),
    (
        ("ranking742 encoding742 mapping742 record742 candle742 thread742", 6),
        ["ranking742", "encoding742", "mapping742", "record742", "candle742", "thread742"],
    ),
    (
        ("ranking742 encoding742 mapping742 record742 candle742 thread742", 10),
        ["ranking742", "encoding742", "mapping742", "record742", "candle742", "thread742"],
    ),
    (
        ("ranking742 encoding742 mapping742 record742 candle742 thread742", 18),
        ["ranking742", "encoding742", "mapping742", "record742", "candle742", "thread742"],
    ),
    (
        ("ranking742 encoding742 mapping742 record742 candle742 thread742", 28),
        ["ranking742 encoding742", "mapping742 record742", "candle742 thread742"],
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
