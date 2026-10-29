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
        ("round 131: the quick brown fox jumps over the lazy dog", 4),
        ["round", "131:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", 8),
        ["round", "131: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", 12),
        ["round 131:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", 16),
        ["round 131: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", 24),
        ["round 131: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 131: the quick brown fox jumps over the lazy dog", 32),
        ["round 131: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", 4),
        ["round", "131:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", 8),
        ["round", "131:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", 12),
        ["round 131:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", 16),
        ["round 131:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", 24),
        ["round 131: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 131: agentuniverse is a framework for multi agents", 32),
        ["round 131: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", 4),
        ["round", "131:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", 8),
        ["round", "131:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", 12),
        ["round 131:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", 16),
        ["round 131:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", 24),
        ["round 131: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 131: knowledge stored as vectors enables retrieval", 32),
        ["round 131: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 131: the processor reads the record then stops", 4),
        ["round", "131:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 131: the processor reads the record then stops", 8),
        ["round", "131: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 131: the processor reads the record then stops", 12),
        ["round 131:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 131: the processor reads the record then stops", 16),
        ["round 131: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 131: the processor reads the record then stops", 24),
        ["round 131: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 131: the processor reads the record then stops", 32),
        ["round 131: the processor reads", "the record then stops"],
    ),
    (
        ("round 131: a worker pulls the next task from the queue", 4),
        ["round", "131:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 131: a worker pulls the next task from the queue", 8),
        ["round", "131: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 131: a worker pulls the next task from the queue", 12),
        ["round 131: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 131: a worker pulls the next task from the queue", 16),
        ["round 131: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 131: a worker pulls the next task from the queue", 24),
        ["round 131: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 131: a worker pulls the next task from the queue", 32),
        ["round 131: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 131: signals travel through the network layer", 4),
        ["round", "131:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 131: signals travel through the network layer", 8),
        ["round", "131:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 131: signals travel through the network layer", 12),
        ["round 131:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 131: signals travel through the network layer", 16),
        ["round 131:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 131: signals travel through the network layer", 24),
        ["round 131: signals", "travel through the", "network layer"],
    ),
    (
        ("round 131: signals travel through the network layer", 32),
        ["round 131: signals travel", "through the network layer"],
    ),
    (
        ("round 131: the gateway routes each request by policy", 4),
        ["round", "131:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 131: the gateway routes each request by policy", 8),
        ["round", "131: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 131: the gateway routes each request by policy", 12),
        ["round 131:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 131: the gateway routes each request by policy", 16),
        ["round 131: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 131: the gateway routes each request by policy", 24),
        ["round 131: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 131: the gateway routes each request by policy", 32),
        ["round 131: the gateway routes", "each request by policy"],
    ),
    (
        ("round 131: memory grows until the buffer is full", 4),
        ["round", "131:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 131: memory grows until the buffer is full", 8),
        ["round", "131:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 131: memory grows until the buffer is full", 12),
        ["round 131:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 131: memory grows until the buffer is full", 16),
        ["round 131:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 131: memory grows until the buffer is full", 24), ["round 131: memory grows", "until the buffer is full"]),
    (("round 131: memory grows until the buffer is full", 32), ["round 131: memory grows until", "the buffer is full"]),
    (
        ("round 131: the cluster mirrors every packet twice", 4),
        ["round", "131:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 131: the cluster mirrors every packet twice", 8),
        ["round", "131: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 131: the cluster mirrors every packet twice", 12),
        ["round 131:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 131: the cluster mirrors every packet twice", 16),
        ["round 131: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 131: the cluster mirrors every packet twice", 24),
        ["round 131: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 131: the cluster mirrors every packet twice", 32),
        ["round 131: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", 4),
        ["round", "131:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", 8),
        ["round", "131:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", 12),
        ["round 131:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", 16),
        ["round 131:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", 24),
        ["round 131: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 131: ranking uses tokens learned from the corpus", 32),
        ["round 131: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 131: a long session ends when the candle dies", 4),
        ["round", "131:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 131: a long session ends when the candle dies", 8),
        ["round", "131: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 131: a long session ends when the candle dies", 12),
        ["round 131: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 131: a long session ends when the candle dies", 16),
        ["round 131: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 131: a long session ends when the candle dies", 24),
        ["round 131: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 131: a long session ends when the candle dies", 32),
        ["round 131: a long session ends", "when the candle dies"],
    ),
    (
        ("round 131: encode the prompt then map the result", 4),
        ["round", "131:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 131: encode the prompt then map the result", 8),
        ["round", "131:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 131: encode the prompt then map the result", 12),
        ["round 131:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 131: encode the prompt then map the result", 16),
        ["round 131:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 131: encode the prompt then map the result", 24),
        ["round 131: encode the", "prompt then map the", "result"],
    ),
    (("round 131: encode the prompt then map the result", 32), ["round 131: encode the prompt", "then map the result"]),
    (
        ("round 131: the kernel wakes the worker at dawn", 4),
        ["round", "131:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 131: the kernel wakes the worker at dawn", 8),
        ["round", "131: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 131: the kernel wakes the worker at dawn", 12),
        ["round 131:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 131: the kernel wakes the worker at dawn", 16), ["round 131: the", "kernel wakes the", "worker at dawn"]),
    (("round 131: the kernel wakes the worker at dawn", 24), ["round 131: the kernel", "wakes the worker at dawn"]),
    (("round 131: the kernel wakes the worker at dawn", 32), ["round 131: the kernel wakes the", "worker at dawn"]),
    (
        ("round 131: service latency drops after the patch", 4),
        ["round", "131:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 131: service latency drops after the patch", 8),
        ["round", "131:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 131: service latency drops after the patch", 12),
        ["round 131:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 131: service latency drops after the patch", 16),
        ["round 131:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 131: service latency drops after the patch", 24),
        ["round 131: service", "latency drops after the", "patch"],
    ),
    (("round 131: service latency drops after the patch", 32), ["round 131: service latency drops", "after the patch"]),
    (
        ("round 131: the library caches every vector it sees", 4),
        ["round", "131:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 131: the library caches every vector it sees", 8),
        ["round", "131: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 131: the library caches every vector it sees", 12),
        ["round 131:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 131: the library caches every vector it sees", 16),
        ["round 131: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 131: the library caches every vector it sees", 24),
        ["round 131: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 131: the library caches every vector it sees", 32),
        ["round 131: the library caches", "every vector it sees"],
    ),
    (
        ("round 131: agents argue then the debate resolves", 4),
        ["round", "131:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 131: agents argue then the debate resolves", 8),
        ["round", "131:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 131: agents argue then the debate resolves", 12),
        ["round 131:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 131: agents argue then the debate resolves", 16),
        ["round 131:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 131: agents argue then the debate resolves", 24), ["round 131: agents argue", "then the debate resolves"]),
    (("round 131: agents argue then the debate resolves", 32), ["round 131: agents argue then the", "debate resolves"]),
    (
        ("round 131: the filter keeps only strong matches", 4),
        ["round", "131:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 131: the filter keeps only strong matches", 8),
        ["round", "131: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 131: the filter keeps only strong matches", 12),
        ["round 131:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 131: the filter keeps only strong matches", 16),
        ["round 131: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 131: the filter keeps only strong matches", 24),
        ["round 131: the filter", "keeps only strong", "matches"],
    ),
    (("round 131: the filter keeps only strong matches", 32), ["round 131: the filter keeps only", "strong matches"]),
    (
        ("round 131: the model answers with a short reply", 4),
        ["round", "131:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 131: the model answers with a short reply", 8),
        ["round", "131: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 131: the model answers with a short reply", 12),
        ["round 131:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 131: the model answers with a short reply", 16),
        ["round 131: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 131: the model answers with a short reply", 24),
        ["round 131: the model", "answers with a short", "reply"],
    ),
    (("round 131: the model answers with a short reply", 32), ["round 131: the model answers", "with a short reply"]),
    (
        ("round 131: the recorder stores the reasoning trace", 4),
        ["round", "131:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 131: the recorder stores the reasoning trace", 8),
        ["round", "131: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 131: the recorder stores the reasoning trace", 12),
        ["round 131:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 131: the recorder stores the reasoning trace", 16),
        ["round 131: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 131: the recorder stores the reasoning trace", 24),
        ["round 131: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 131: the recorder stores the reasoning trace", 32),
        ["round 131: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 131: the angel watches the processor run", 4),
        ["round", "131:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 131: the angel watches the processor run", 8),
        ["round", "131: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 131: the angel watches the processor run", 12),
        ["round 131:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 131: the angel watches the processor run", 16),
        ["round 131: the", "angel watches", "the processor", "run"],
    ),
    (("round 131: the angel watches the processor run", 24), ["round 131: the angel", "watches the processor", "run"]),
    (("round 131: the angel watches the processor run", 32), ["round 131: the angel watches the", "processor run"]),
    (
        ("round 131: angle of the vector decides the match", 4),
        ["round", "131:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 131: angle of the vector decides the match", 8),
        ["round", "131:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 131: angle of the vector decides the match", 12),
        ["round 131:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 131: angle of the vector decides the match", 16),
        ["round 131: angle", "of the vector", "decides the", "match"],
    ),
    (("round 131: angle of the vector decides the match", 24), ["round 131: angle of the", "vector decides the match"]),
    (("round 131: angle of the vector decides the match", 32), ["round 131: angle of the vector", "decides the match"]),
    (
        ("round 131: the candle burns twice as long at night", 4),
        ["round", "131:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 131: the candle burns twice as long at night", 8),
        ["round", "131: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 131: the candle burns twice as long at night", 12),
        ["round 131:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 131: the candle burns twice as long at night", 16),
        ["round 131: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 131: the candle burns twice as long at night", 24),
        ["round 131: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 131: the candle burns twice as long at night", 32),
        ["round 131: the candle burns", "twice as long at night"],
    ),
    (
        ("round 131: a mirror of the universe in one line", 4),
        ["round", "131:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 131: a mirror of the universe in one line", 8),
        ["round", "131: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 131: a mirror of the universe in one line", 12),
        ["round 131: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 131: a mirror of the universe in one line", 16),
        ["round 131: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 131: a mirror of the universe in one line", 24), ["round 131: a mirror of", "the universe in one line"]),
    (("round 131: a mirror of the universe in one line", 32), ["round 131: a mirror of the", "universe in one line"]),
    (
        ("round 131: the queue drains before the storm", 4),
        ["round", "131:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 131: the queue drains before the storm", 8),
        ["round", "131: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 131: the queue drains before the storm", 12),
        ["round 131:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 131: the queue drains before the storm", 16), ["round 131: the", "queue drains", "before the storm"]),
    (("round 131: the queue drains before the storm", 24), ["round 131: the queue", "drains before the storm"]),
    (("round 131: the queue drains before the storm", 32), ["round 131: the queue drains", "before the storm"]),
    (
        ("kitten131 sitting131 agent131 angle131 universe131 memory131", 6),
        ["kitten131", "sitting131", "agent131", "angle131", "universe131", "memory131"],
    ),
    (
        ("kitten131 sitting131 agent131 angle131 universe131 memory131", 10),
        ["kitten131", "sitting131", "agent131", "angle131", "universe131", "memory131"],
    ),
    (
        ("kitten131 sitting131 agent131 angle131 universe131 memory131", 18),
        ["kitten131", "sitting131", "agent131 angle131", "universe131", "memory131"],
    ),
    (
        ("kitten131 sitting131 agent131 angle131 universe131 memory131", 28),
        ["kitten131 sitting131", "agent131 angle131", "universe131 memory131"],
    ),
    (
        ("sitting131 agent131 angle131 universe131 memory131 stream131", 6),
        ["sitting131", "agent131", "angle131", "universe131", "memory131", "stream131"],
    ),
    (
        ("sitting131 agent131 angle131 universe131 memory131 stream131", 10),
        ["sitting131", "agent131", "angle131", "universe131", "memory131", "stream131"],
    ),
    (
        ("sitting131 agent131 angle131 universe131 memory131 stream131", 18),
        ["sitting131", "agent131 angle131", "universe131", "memory131", "stream131"],
    ),
    (
        ("sitting131 agent131 angle131 universe131 memory131 stream131", 28),
        ["sitting131 agent131 angle131", "universe131 memory131", "stream131"],
    ),
    (
        ("agent131 angle131 universe131 memory131 stream131 context131", 6),
        ["agent131", "angle131", "universe131", "memory131", "stream131", "context131"],
    ),
    (
        ("agent131 angle131 universe131 memory131 stream131 context131", 10),
        ["agent131", "angle131", "universe131", "memory131", "stream131", "context131"],
    ),
    (
        ("agent131 angle131 universe131 memory131 stream131 context131", 18),
        ["agent131 angle131", "universe131", "memory131", "stream131", "context131"],
    ),
    (
        ("agent131 angle131 universe131 memory131 stream131 context131", 28),
        ["agent131 angle131", "universe131 memory131", "stream131 context131"],
    ),
    (
        ("angle131 universe131 memory131 stream131 context131 knowledge131", 6),
        ["angle131", "universe131", "memory131", "stream131", "context131", "knowledge131"],
    ),
    (
        ("angle131 universe131 memory131 stream131 context131 knowledge131", 10),
        ["angle131", "universe131", "memory131", "stream131", "context131", "knowledge131"],
    ),
    (
        ("angle131 universe131 memory131 stream131 context131 knowledge131", 18),
        ["angle131", "universe131", "memory131", "stream131", "context131", "knowledge131"],
    ),
    (
        ("angle131 universe131 memory131 stream131 context131 knowledge131", 28),
        ["angle131 universe131", "memory131 stream131", "context131 knowledge131"],
    ),
    (
        ("universe131 memory131 stream131 context131 knowledge131 vector131", 6),
        ["universe131", "memory131", "stream131", "context131", "knowledge131", "vector131"],
    ),
    (
        ("universe131 memory131 stream131 context131 knowledge131 vector131", 10),
        ["universe131", "memory131", "stream131", "context131", "knowledge131", "vector131"],
    ),
    (
        ("universe131 memory131 stream131 context131 knowledge131 vector131", 18),
        ["universe131", "memory131", "stream131", "context131", "knowledge131", "vector131"],
    ),
    (
        ("universe131 memory131 stream131 context131 knowledge131 vector131", 28),
        ["universe131 memory131", "stream131 context131", "knowledge131 vector131"],
    ),
    (
        ("memory131 stream131 context131 knowledge131 vector131 processor131", 6),
        ["memory131", "stream131", "context131", "knowledge131", "vector131", "processor131"],
    ),
    (
        ("memory131 stream131 context131 knowledge131 vector131 processor131", 10),
        ["memory131", "stream131", "context131", "knowledge131", "vector131", "processor131"],
    ),
    (
        ("memory131 stream131 context131 knowledge131 vector131 processor131", 18),
        ["memory131", "stream131", "context131", "knowledge131", "vector131", "processor131"],
    ),
    (
        ("memory131 stream131 context131 knowledge131 vector131 processor131", 28),
        ["memory131 stream131", "context131 knowledge131", "vector131 processor131"],
    ),
    (
        ("stream131 context131 knowledge131 vector131 processor131 reasoning131", 6),
        ["stream131", "context131", "knowledge131", "vector131", "processor131", "reasoning131"],
    ),
    (
        ("stream131 context131 knowledge131 vector131 processor131 reasoning131", 10),
        ["stream131", "context131", "knowledge131", "vector131", "processor131", "reasoning131"],
    ),
    (
        ("stream131 context131 knowledge131 vector131 processor131 reasoning131", 18),
        ["stream131", "context131", "knowledge131", "vector131", "processor131", "reasoning131"],
    ),
    (
        ("stream131 context131 knowledge131 vector131 processor131 reasoning131", 28),
        ["stream131 context131", "knowledge131 vector131", "processor131 reasoning131"],
    ),
    (
        ("context131 knowledge131 vector131 processor131 reasoning131 machine131", 6),
        ["context131", "knowledge131", "vector131", "processor131", "reasoning131", "machine131"],
    ),
    (
        ("context131 knowledge131 vector131 processor131 reasoning131 machine131", 10),
        ["context131", "knowledge131", "vector131", "processor131", "reasoning131", "machine131"],
    ),
    (
        ("context131 knowledge131 vector131 processor131 reasoning131 machine131", 18),
        ["context131", "knowledge131", "vector131", "processor131", "reasoning131", "machine131"],
    ),
    (
        ("context131 knowledge131 vector131 processor131 reasoning131 machine131", 28),
        ["context131 knowledge131", "vector131 processor131", "reasoning131 machine131"],
    ),
    (
        ("knowledge131 vector131 processor131 reasoning131 machine131 learning131", 6),
        ["knowledge131", "vector131", "processor131", "reasoning131", "machine131", "learning131"],
    ),
    (
        ("knowledge131 vector131 processor131 reasoning131 machine131 learning131", 10),
        ["knowledge131", "vector131", "processor131", "reasoning131", "machine131", "learning131"],
    ),
    (
        ("knowledge131 vector131 processor131 reasoning131 machine131 learning131", 18),
        ["knowledge131", "vector131", "processor131", "reasoning131", "machine131", "learning131"],
    ),
    (
        ("knowledge131 vector131 processor131 reasoning131 machine131 learning131", 28),
        ["knowledge131 vector131", "processor131 reasoning131", "machine131 learning131"],
    ),
    (
        ("vector131 processor131 reasoning131 machine131 learning131 model131", 6),
        ["vector131", "processor131", "reasoning131", "machine131", "learning131", "model131"],
    ),
    (
        ("vector131 processor131 reasoning131 machine131 learning131 model131", 10),
        ["vector131", "processor131", "reasoning131", "machine131", "learning131", "model131"],
    ),
    (
        ("vector131 processor131 reasoning131 machine131 learning131 model131", 18),
        ["vector131", "processor131", "reasoning131", "machine131", "learning131", "model131"],
    ),
    (
        ("vector131 processor131 reasoning131 machine131 learning131 model131", 28),
        ["vector131 processor131", "reasoning131 machine131", "learning131 model131"],
    ),
    (
        ("processor131 reasoning131 machine131 learning131 model131 token131", 6),
        ["processor131", "reasoning131", "machine131", "learning131", "model131", "token131"],
    ),
    (
        ("processor131 reasoning131 machine131 learning131 model131 token131", 10),
        ["processor131", "reasoning131", "machine131", "learning131", "model131", "token131"],
    ),
    (
        ("processor131 reasoning131 machine131 learning131 model131 token131", 18),
        ["processor131", "reasoning131", "machine131", "learning131", "model131 token131"],
    ),
    (
        ("processor131 reasoning131 machine131 learning131 model131 token131", 28),
        ["processor131 reasoning131", "machine131 learning131", "model131 token131"],
    ),
    (
        ("reasoning131 machine131 learning131 model131 token131 prompt131", 6),
        ["reasoning131", "machine131", "learning131", "model131", "token131", "prompt131"],
    ),
    (
        ("reasoning131 machine131 learning131 model131 token131 prompt131", 10),
        ["reasoning131", "machine131", "learning131", "model131", "token131", "prompt131"],
    ),
    (
        ("reasoning131 machine131 learning131 model131 token131 prompt131", 18),
        ["reasoning131", "machine131", "learning131", "model131 token131", "prompt131"],
    ),
    (
        ("reasoning131 machine131 learning131 model131 token131 prompt131", 28),
        ["reasoning131 machine131", "learning131 model131", "token131 prompt131"],
    ),
    (
        ("machine131 learning131 model131 token131 prompt131 session131", 6),
        ["machine131", "learning131", "model131", "token131", "prompt131", "session131"],
    ),
    (
        ("machine131 learning131 model131 token131 prompt131 session131", 10),
        ["machine131", "learning131", "model131", "token131", "prompt131", "session131"],
    ),
    (
        ("machine131 learning131 model131 token131 prompt131 session131", 18),
        ["machine131", "learning131", "model131 token131", "prompt131", "session131"],
    ),
    (
        ("machine131 learning131 model131 token131 prompt131 session131", 28),
        ["machine131 learning131", "model131 token131 prompt131", "session131"],
    ),
    (
        ("learning131 model131 token131 prompt131 session131 library131", 6),
        ["learning131", "model131", "token131", "prompt131", "session131", "library131"],
    ),
    (
        ("learning131 model131 token131 prompt131 session131 library131", 10),
        ["learning131", "model131", "token131", "prompt131", "session131", "library131"],
    ),
    (
        ("learning131 model131 token131 prompt131 session131 library131", 18),
        ["learning131", "model131 token131", "prompt131", "session131", "library131"],
    ),
    (
        ("learning131 model131 token131 prompt131 session131 library131", 28),
        ["learning131 model131", "token131 prompt131", "session131 library131"],
    ),
    (
        ("model131 token131 prompt131 session131 library131 service131", 6),
        ["model131", "token131", "prompt131", "session131", "library131", "service131"],
    ),
    (
        ("model131 token131 prompt131 session131 library131 service131", 10),
        ["model131", "token131", "prompt131", "session131", "library131", "service131"],
    ),
    (
        ("model131 token131 prompt131 session131 library131 service131", 18),
        ["model131 token131", "prompt131", "session131", "library131", "service131"],
    ),
    (
        ("model131 token131 prompt131 session131 library131 service131", 28),
        ["model131 token131 prompt131", "session131 library131", "service131"],
    ),
    (
        ("token131 prompt131 session131 library131 service131 gateway131", 6),
        ["token131", "prompt131", "session131", "library131", "service131", "gateway131"],
    ),
    (
        ("token131 prompt131 session131 library131 service131 gateway131", 10),
        ["token131", "prompt131", "session131", "library131", "service131", "gateway131"],
    ),
    (
        ("token131 prompt131 session131 library131 service131 gateway131", 18),
        ["token131 prompt131", "session131", "library131", "service131", "gateway131"],
    ),
    (
        ("token131 prompt131 session131 library131 service131 gateway131", 28),
        ["token131 prompt131", "session131 library131", "service131 gateway131"],
    ),
    (
        ("prompt131 session131 library131 service131 gateway131 storage131", 6),
        ["prompt131", "session131", "library131", "service131", "gateway131", "storage131"],
    ),
    (
        ("prompt131 session131 library131 service131 gateway131 storage131", 10),
        ["prompt131", "session131", "library131", "service131", "gateway131", "storage131"],
    ),
    (
        ("prompt131 session131 library131 service131 gateway131 storage131", 18),
        ["prompt131", "session131", "library131", "service131", "gateway131", "storage131"],
    ),
    (
        ("prompt131 session131 library131 service131 gateway131 storage131", 28),
        ["prompt131 session131", "library131 service131", "gateway131 storage131"],
    ),
    (
        ("session131 library131 service131 gateway131 storage131 network131", 6),
        ["session131", "library131", "service131", "gateway131", "storage131", "network131"],
    ),
    (
        ("session131 library131 service131 gateway131 storage131 network131", 10),
        ["session131", "library131", "service131", "gateway131", "storage131", "network131"],
    ),
    (
        ("session131 library131 service131 gateway131 storage131 network131", 18),
        ["session131", "library131", "service131", "gateway131", "storage131", "network131"],
    ),
    (
        ("session131 library131 service131 gateway131 storage131 network131", 28),
        ["session131 library131", "service131 gateway131", "storage131 network131"],
    ),
    (
        ("library131 service131 gateway131 storage131 network131 latency131", 6),
        ["library131", "service131", "gateway131", "storage131", "network131", "latency131"],
    ),
    (
        ("library131 service131 gateway131 storage131 network131 latency131", 10),
        ["library131", "service131", "gateway131", "storage131", "network131", "latency131"],
    ),
    (
        ("library131 service131 gateway131 storage131 network131 latency131", 18),
        ["library131", "service131", "gateway131", "storage131", "network131", "latency131"],
    ),
    (
        ("library131 service131 gateway131 storage131 network131 latency131", 28),
        ["library131 service131", "gateway131 storage131", "network131 latency131"],
    ),
    (
        ("service131 gateway131 storage131 network131 latency131 buffer131", 6),
        ["service131", "gateway131", "storage131", "network131", "latency131", "buffer131"],
    ),
    (
        ("service131 gateway131 storage131 network131 latency131 buffer131", 10),
        ["service131", "gateway131", "storage131", "network131", "latency131", "buffer131"],
    ),
    (
        ("service131 gateway131 storage131 network131 latency131 buffer131", 18),
        ["service131", "gateway131", "storage131", "network131", "latency131", "buffer131"],
    ),
    (
        ("service131 gateway131 storage131 network131 latency131 buffer131", 28),
        ["service131 gateway131", "storage131 network131", "latency131 buffer131"],
    ),
    (
        ("gateway131 storage131 network131 latency131 buffer131 queue131", 6),
        ["gateway131", "storage131", "network131", "latency131", "buffer131", "queue131"],
    ),
    (
        ("gateway131 storage131 network131 latency131 buffer131 queue131", 10),
        ["gateway131", "storage131", "network131", "latency131", "buffer131", "queue131"],
    ),
    (
        ("gateway131 storage131 network131 latency131 buffer131 queue131", 18),
        ["gateway131", "storage131", "network131", "latency131", "buffer131 queue131"],
    ),
    (
        ("gateway131 storage131 network131 latency131 buffer131 queue131", 28),
        ["gateway131 storage131", "network131 latency131", "buffer131 queue131"],
    ),
    (
        ("storage131 network131 latency131 buffer131 queue131 worker131", 6),
        ["storage131", "network131", "latency131", "buffer131", "queue131", "worker131"],
    ),
    (
        ("storage131 network131 latency131 buffer131 queue131 worker131", 10),
        ["storage131", "network131", "latency131", "buffer131", "queue131", "worker131"],
    ),
    (
        ("storage131 network131 latency131 buffer131 queue131 worker131", 18),
        ["storage131", "network131", "latency131", "buffer131 queue131", "worker131"],
    ),
    (
        ("storage131 network131 latency131 buffer131 queue131 worker131", 28),
        ["storage131 network131", "latency131 buffer131", "queue131 worker131"],
    ),
    (
        ("network131 latency131 buffer131 queue131 worker131 kernel131", 6),
        ["network131", "latency131", "buffer131", "queue131", "worker131", "kernel131"],
    ),
    (
        ("network131 latency131 buffer131 queue131 worker131 kernel131", 10),
        ["network131", "latency131", "buffer131", "queue131", "worker131", "kernel131"],
    ),
    (
        ("network131 latency131 buffer131 queue131 worker131 kernel131", 18),
        ["network131", "latency131", "buffer131 queue131", "worker131", "kernel131"],
    ),
    (
        ("network131 latency131 buffer131 queue131 worker131 kernel131", 28),
        ["network131 latency131", "buffer131 queue131 worker131", "kernel131"],
    ),
    (
        ("latency131 buffer131 queue131 worker131 kernel131 signal131", 6),
        ["latency131", "buffer131", "queue131", "worker131", "kernel131", "signal131"],
    ),
    (
        ("latency131 buffer131 queue131 worker131 kernel131 signal131", 10),
        ["latency131", "buffer131", "queue131", "worker131", "kernel131", "signal131"],
    ),
    (
        ("latency131 buffer131 queue131 worker131 kernel131 signal131", 18),
        ["latency131", "buffer131 queue131", "worker131", "kernel131", "signal131"],
    ),
    (
        ("latency131 buffer131 queue131 worker131 kernel131 signal131", 28),
        ["latency131 buffer131", "queue131 worker131 kernel131", "signal131"],
    ),
    (
        ("buffer131 queue131 worker131 kernel131 signal131 packet131", 6),
        ["buffer131", "queue131", "worker131", "kernel131", "signal131", "packet131"],
    ),
    (
        ("buffer131 queue131 worker131 kernel131 signal131 packet131", 10),
        ["buffer131", "queue131", "worker131", "kernel131", "signal131", "packet131"],
    ),
    (
        ("buffer131 queue131 worker131 kernel131 signal131 packet131", 18),
        ["buffer131 queue131", "worker131", "kernel131", "signal131", "packet131"],
    ),
    (
        ("buffer131 queue131 worker131 kernel131 signal131 packet131", 28),
        ["buffer131 queue131 worker131", "kernel131 signal131", "packet131"],
    ),
    (
        ("queue131 worker131 kernel131 signal131 packet131 router131", 6),
        ["queue131", "worker131", "kernel131", "signal131", "packet131", "router131"],
    ),
    (
        ("queue131 worker131 kernel131 signal131 packet131 router131", 10),
        ["queue131", "worker131", "kernel131", "signal131", "packet131", "router131"],
    ),
    (
        ("queue131 worker131 kernel131 signal131 packet131 router131", 18),
        ["queue131 worker131", "kernel131", "signal131", "packet131", "router131"],
    ),
    (
        ("queue131 worker131 kernel131 signal131 packet131 router131", 28),
        ["queue131 worker131 kernel131", "signal131 packet131", "router131"],
    ),
    (
        ("worker131 kernel131 signal131 packet131 router131 cluster131", 6),
        ["worker131", "kernel131", "signal131", "packet131", "router131", "cluster131"],
    ),
    (
        ("worker131 kernel131 signal131 packet131 router131 cluster131", 10),
        ["worker131", "kernel131", "signal131", "packet131", "router131", "cluster131"],
    ),
    (
        ("worker131 kernel131 signal131 packet131 router131 cluster131", 18),
        ["worker131", "kernel131", "signal131", "packet131", "router131", "cluster131"],
    ),
    (
        ("worker131 kernel131 signal131 packet131 router131 cluster131", 28),
        ["worker131 kernel131", "signal131 packet131", "router131 cluster131"],
    ),
    (
        ("kernel131 signal131 packet131 router131 cluster131 mirror131", 6),
        ["kernel131", "signal131", "packet131", "router131", "cluster131", "mirror131"],
    ),
    (
        ("kernel131 signal131 packet131 router131 cluster131 mirror131", 10),
        ["kernel131", "signal131", "packet131", "router131", "cluster131", "mirror131"],
    ),
    (
        ("kernel131 signal131 packet131 router131 cluster131 mirror131", 18),
        ["kernel131", "signal131", "packet131", "router131", "cluster131", "mirror131"],
    ),
    (
        ("kernel131 signal131 packet131 router131 cluster131 mirror131", 28),
        ["kernel131 signal131", "packet131 router131", "cluster131 mirror131"],
    ),
    (
        ("signal131 packet131 router131 cluster131 mirror131 filter131", 6),
        ["signal131", "packet131", "router131", "cluster131", "mirror131", "filter131"],
    ),
    (
        ("signal131 packet131 router131 cluster131 mirror131 filter131", 10),
        ["signal131", "packet131", "router131", "cluster131", "mirror131", "filter131"],
    ),
    (
        ("signal131 packet131 router131 cluster131 mirror131 filter131", 18),
        ["signal131", "packet131", "router131", "cluster131", "mirror131", "filter131"],
    ),
    (
        ("signal131 packet131 router131 cluster131 mirror131 filter131", 28),
        ["signal131 packet131", "router131 cluster131", "mirror131 filter131"],
    ),
    (
        ("packet131 router131 cluster131 mirror131 filter131 ranking131", 6),
        ["packet131", "router131", "cluster131", "mirror131", "filter131", "ranking131"],
    ),
    (
        ("packet131 router131 cluster131 mirror131 filter131 ranking131", 10),
        ["packet131", "router131", "cluster131", "mirror131", "filter131", "ranking131"],
    ),
    (
        ("packet131 router131 cluster131 mirror131 filter131 ranking131", 18),
        ["packet131", "router131", "cluster131", "mirror131", "filter131", "ranking131"],
    ),
    (
        ("packet131 router131 cluster131 mirror131 filter131 ranking131", 28),
        ["packet131 router131", "cluster131 mirror131", "filter131 ranking131"],
    ),
    (
        ("router131 cluster131 mirror131 filter131 ranking131 encoding131", 6),
        ["router131", "cluster131", "mirror131", "filter131", "ranking131", "encoding131"],
    ),
    (
        ("router131 cluster131 mirror131 filter131 ranking131 encoding131", 10),
        ["router131", "cluster131", "mirror131", "filter131", "ranking131", "encoding131"],
    ),
    (
        ("router131 cluster131 mirror131 filter131 ranking131 encoding131", 18),
        ["router131", "cluster131", "mirror131", "filter131", "ranking131", "encoding131"],
    ),
    (
        ("router131 cluster131 mirror131 filter131 ranking131 encoding131", 28),
        ["router131 cluster131", "mirror131 filter131", "ranking131 encoding131"],
    ),
    (
        ("cluster131 mirror131 filter131 ranking131 encoding131 mapping131", 6),
        ["cluster131", "mirror131", "filter131", "ranking131", "encoding131", "mapping131"],
    ),
    (
        ("cluster131 mirror131 filter131 ranking131 encoding131 mapping131", 10),
        ["cluster131", "mirror131", "filter131", "ranking131", "encoding131", "mapping131"],
    ),
    (
        ("cluster131 mirror131 filter131 ranking131 encoding131 mapping131", 18),
        ["cluster131", "mirror131", "filter131", "ranking131", "encoding131", "mapping131"],
    ),
    (
        ("cluster131 mirror131 filter131 ranking131 encoding131 mapping131", 28),
        ["cluster131 mirror131", "filter131 ranking131", "encoding131 mapping131"],
    ),
    (
        ("mirror131 filter131 ranking131 encoding131 mapping131 record131", 6),
        ["mirror131", "filter131", "ranking131", "encoding131", "mapping131", "record131"],
    ),
    (
        ("mirror131 filter131 ranking131 encoding131 mapping131 record131", 10),
        ["mirror131", "filter131", "ranking131", "encoding131", "mapping131", "record131"],
    ),
    (
        ("mirror131 filter131 ranking131 encoding131 mapping131 record131", 18),
        ["mirror131", "filter131", "ranking131", "encoding131", "mapping131", "record131"],
    ),
    (
        ("mirror131 filter131 ranking131 encoding131 mapping131 record131", 28),
        ["mirror131 filter131", "ranking131 encoding131", "mapping131 record131"],
    ),
    (
        ("filter131 ranking131 encoding131 mapping131 record131 candle131", 6),
        ["filter131", "ranking131", "encoding131", "mapping131", "record131", "candle131"],
    ),
    (
        ("filter131 ranking131 encoding131 mapping131 record131 candle131", 10),
        ["filter131", "ranking131", "encoding131", "mapping131", "record131", "candle131"],
    ),
    (
        ("filter131 ranking131 encoding131 mapping131 record131 candle131", 18),
        ["filter131", "ranking131", "encoding131", "mapping131", "record131", "candle131"],
    ),
    (
        ("filter131 ranking131 encoding131 mapping131 record131 candle131", 28),
        ["filter131 ranking131", "encoding131 mapping131", "record131 candle131"],
    ),
    (
        ("ranking131 encoding131 mapping131 record131 candle131 thread131", 6),
        ["ranking131", "encoding131", "mapping131", "record131", "candle131", "thread131"],
    ),
    (
        ("ranking131 encoding131 mapping131 record131 candle131 thread131", 10),
        ["ranking131", "encoding131", "mapping131", "record131", "candle131", "thread131"],
    ),
    (
        ("ranking131 encoding131 mapping131 record131 candle131 thread131", 18),
        ["ranking131", "encoding131", "mapping131", "record131", "candle131", "thread131"],
    ),
    (
        ("ranking131 encoding131 mapping131 record131 candle131 thread131", 28),
        ["ranking131 encoding131", "mapping131 record131", "candle131 thread131"],
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
