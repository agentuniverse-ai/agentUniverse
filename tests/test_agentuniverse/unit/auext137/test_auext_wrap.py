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
        ("round 137: the quick brown fox jumps over the lazy dog", 4),
        ["round", "137:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", 8),
        ["round", "137: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", 12),
        ["round 137:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", 16),
        ["round 137: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", 24),
        ["round 137: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 137: the quick brown fox jumps over the lazy dog", 32),
        ["round 137: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", 4),
        ["round", "137:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", 8),
        ["round", "137:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", 12),
        ["round 137:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", 16),
        ["round 137:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", 24),
        ["round 137: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 137: agentuniverse is a framework for multi agents", 32),
        ["round 137: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", 4),
        ["round", "137:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", 8),
        ["round", "137:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", 12),
        ["round 137:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", 16),
        ["round 137:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", 24),
        ["round 137: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 137: knowledge stored as vectors enables retrieval", 32),
        ["round 137: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 137: the processor reads the record then stops", 4),
        ["round", "137:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 137: the processor reads the record then stops", 8),
        ["round", "137: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 137: the processor reads the record then stops", 12),
        ["round 137:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 137: the processor reads the record then stops", 16),
        ["round 137: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 137: the processor reads the record then stops", 24),
        ["round 137: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 137: the processor reads the record then stops", 32),
        ["round 137: the processor reads", "the record then stops"],
    ),
    (
        ("round 137: a worker pulls the next task from the queue", 4),
        ["round", "137:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 137: a worker pulls the next task from the queue", 8),
        ["round", "137: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 137: a worker pulls the next task from the queue", 12),
        ["round 137: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 137: a worker pulls the next task from the queue", 16),
        ["round 137: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 137: a worker pulls the next task from the queue", 24),
        ["round 137: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 137: a worker pulls the next task from the queue", 32),
        ["round 137: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 137: signals travel through the network layer", 4),
        ["round", "137:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 137: signals travel through the network layer", 8),
        ["round", "137:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 137: signals travel through the network layer", 12),
        ["round 137:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 137: signals travel through the network layer", 16),
        ["round 137:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 137: signals travel through the network layer", 24),
        ["round 137: signals", "travel through the", "network layer"],
    ),
    (
        ("round 137: signals travel through the network layer", 32),
        ["round 137: signals travel", "through the network layer"],
    ),
    (
        ("round 137: the gateway routes each request by policy", 4),
        ["round", "137:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 137: the gateway routes each request by policy", 8),
        ["round", "137: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 137: the gateway routes each request by policy", 12),
        ["round 137:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 137: the gateway routes each request by policy", 16),
        ["round 137: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 137: the gateway routes each request by policy", 24),
        ["round 137: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 137: the gateway routes each request by policy", 32),
        ["round 137: the gateway routes", "each request by policy"],
    ),
    (
        ("round 137: memory grows until the buffer is full", 4),
        ["round", "137:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 137: memory grows until the buffer is full", 8),
        ["round", "137:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 137: memory grows until the buffer is full", 12),
        ["round 137:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 137: memory grows until the buffer is full", 16),
        ["round 137:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 137: memory grows until the buffer is full", 24), ["round 137: memory grows", "until the buffer is full"]),
    (("round 137: memory grows until the buffer is full", 32), ["round 137: memory grows until", "the buffer is full"]),
    (
        ("round 137: the cluster mirrors every packet twice", 4),
        ["round", "137:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 137: the cluster mirrors every packet twice", 8),
        ["round", "137: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 137: the cluster mirrors every packet twice", 12),
        ["round 137:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 137: the cluster mirrors every packet twice", 16),
        ["round 137: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 137: the cluster mirrors every packet twice", 24),
        ["round 137: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 137: the cluster mirrors every packet twice", 32),
        ["round 137: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", 4),
        ["round", "137:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", 8),
        ["round", "137:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", 12),
        ["round 137:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", 16),
        ["round 137:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", 24),
        ["round 137: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 137: ranking uses tokens learned from the corpus", 32),
        ["round 137: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 137: a long session ends when the candle dies", 4),
        ["round", "137:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 137: a long session ends when the candle dies", 8),
        ["round", "137: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 137: a long session ends when the candle dies", 12),
        ["round 137: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 137: a long session ends when the candle dies", 16),
        ["round 137: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 137: a long session ends when the candle dies", 24),
        ["round 137: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 137: a long session ends when the candle dies", 32),
        ["round 137: a long session ends", "when the candle dies"],
    ),
    (
        ("round 137: encode the prompt then map the result", 4),
        ["round", "137:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 137: encode the prompt then map the result", 8),
        ["round", "137:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 137: encode the prompt then map the result", 12),
        ["round 137:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 137: encode the prompt then map the result", 16),
        ["round 137:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 137: encode the prompt then map the result", 24),
        ["round 137: encode the", "prompt then map the", "result"],
    ),
    (("round 137: encode the prompt then map the result", 32), ["round 137: encode the prompt", "then map the result"]),
    (
        ("round 137: the kernel wakes the worker at dawn", 4),
        ["round", "137:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 137: the kernel wakes the worker at dawn", 8),
        ["round", "137: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 137: the kernel wakes the worker at dawn", 12),
        ["round 137:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 137: the kernel wakes the worker at dawn", 16), ["round 137: the", "kernel wakes the", "worker at dawn"]),
    (("round 137: the kernel wakes the worker at dawn", 24), ["round 137: the kernel", "wakes the worker at dawn"]),
    (("round 137: the kernel wakes the worker at dawn", 32), ["round 137: the kernel wakes the", "worker at dawn"]),
    (
        ("round 137: service latency drops after the patch", 4),
        ["round", "137:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 137: service latency drops after the patch", 8),
        ["round", "137:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 137: service latency drops after the patch", 12),
        ["round 137:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 137: service latency drops after the patch", 16),
        ["round 137:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 137: service latency drops after the patch", 24),
        ["round 137: service", "latency drops after the", "patch"],
    ),
    (("round 137: service latency drops after the patch", 32), ["round 137: service latency drops", "after the patch"]),
    (
        ("round 137: the library caches every vector it sees", 4),
        ["round", "137:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 137: the library caches every vector it sees", 8),
        ["round", "137: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 137: the library caches every vector it sees", 12),
        ["round 137:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 137: the library caches every vector it sees", 16),
        ["round 137: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 137: the library caches every vector it sees", 24),
        ["round 137: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 137: the library caches every vector it sees", 32),
        ["round 137: the library caches", "every vector it sees"],
    ),
    (
        ("round 137: agents argue then the debate resolves", 4),
        ["round", "137:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 137: agents argue then the debate resolves", 8),
        ["round", "137:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 137: agents argue then the debate resolves", 12),
        ["round 137:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 137: agents argue then the debate resolves", 16),
        ["round 137:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 137: agents argue then the debate resolves", 24), ["round 137: agents argue", "then the debate resolves"]),
    (("round 137: agents argue then the debate resolves", 32), ["round 137: agents argue then the", "debate resolves"]),
    (
        ("round 137: the filter keeps only strong matches", 4),
        ["round", "137:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 137: the filter keeps only strong matches", 8),
        ["round", "137: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 137: the filter keeps only strong matches", 12),
        ["round 137:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 137: the filter keeps only strong matches", 16),
        ["round 137: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 137: the filter keeps only strong matches", 24),
        ["round 137: the filter", "keeps only strong", "matches"],
    ),
    (("round 137: the filter keeps only strong matches", 32), ["round 137: the filter keeps only", "strong matches"]),
    (
        ("round 137: the model answers with a short reply", 4),
        ["round", "137:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 137: the model answers with a short reply", 8),
        ["round", "137: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 137: the model answers with a short reply", 12),
        ["round 137:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 137: the model answers with a short reply", 16),
        ["round 137: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 137: the model answers with a short reply", 24),
        ["round 137: the model", "answers with a short", "reply"],
    ),
    (("round 137: the model answers with a short reply", 32), ["round 137: the model answers", "with a short reply"]),
    (
        ("round 137: the recorder stores the reasoning trace", 4),
        ["round", "137:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 137: the recorder stores the reasoning trace", 8),
        ["round", "137: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 137: the recorder stores the reasoning trace", 12),
        ["round 137:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 137: the recorder stores the reasoning trace", 16),
        ["round 137: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 137: the recorder stores the reasoning trace", 24),
        ["round 137: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 137: the recorder stores the reasoning trace", 32),
        ["round 137: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 137: the angel watches the processor run", 4),
        ["round", "137:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 137: the angel watches the processor run", 8),
        ["round", "137: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 137: the angel watches the processor run", 12),
        ["round 137:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 137: the angel watches the processor run", 16),
        ["round 137: the", "angel watches", "the processor", "run"],
    ),
    (("round 137: the angel watches the processor run", 24), ["round 137: the angel", "watches the processor", "run"]),
    (("round 137: the angel watches the processor run", 32), ["round 137: the angel watches the", "processor run"]),
    (
        ("round 137: angle of the vector decides the match", 4),
        ["round", "137:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 137: angle of the vector decides the match", 8),
        ["round", "137:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 137: angle of the vector decides the match", 12),
        ["round 137:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 137: angle of the vector decides the match", 16),
        ["round 137: angle", "of the vector", "decides the", "match"],
    ),
    (("round 137: angle of the vector decides the match", 24), ["round 137: angle of the", "vector decides the match"]),
    (("round 137: angle of the vector decides the match", 32), ["round 137: angle of the vector", "decides the match"]),
    (
        ("round 137: the candle burns twice as long at night", 4),
        ["round", "137:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 137: the candle burns twice as long at night", 8),
        ["round", "137: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 137: the candle burns twice as long at night", 12),
        ["round 137:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 137: the candle burns twice as long at night", 16),
        ["round 137: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 137: the candle burns twice as long at night", 24),
        ["round 137: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 137: the candle burns twice as long at night", 32),
        ["round 137: the candle burns", "twice as long at night"],
    ),
    (
        ("round 137: a mirror of the universe in one line", 4),
        ["round", "137:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 137: a mirror of the universe in one line", 8),
        ["round", "137: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 137: a mirror of the universe in one line", 12),
        ["round 137: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 137: a mirror of the universe in one line", 16),
        ["round 137: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 137: a mirror of the universe in one line", 24), ["round 137: a mirror of", "the universe in one line"]),
    (("round 137: a mirror of the universe in one line", 32), ["round 137: a mirror of the", "universe in one line"]),
    (
        ("round 137: the queue drains before the storm", 4),
        ["round", "137:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 137: the queue drains before the storm", 8),
        ["round", "137: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 137: the queue drains before the storm", 12),
        ["round 137:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 137: the queue drains before the storm", 16), ["round 137: the", "queue drains", "before the storm"]),
    (("round 137: the queue drains before the storm", 24), ["round 137: the queue", "drains before the storm"]),
    (("round 137: the queue drains before the storm", 32), ["round 137: the queue drains", "before the storm"]),
    (
        ("kitten137 sitting137 agent137 angle137 universe137 memory137", 6),
        ["kitten137", "sitting137", "agent137", "angle137", "universe137", "memory137"],
    ),
    (
        ("kitten137 sitting137 agent137 angle137 universe137 memory137", 10),
        ["kitten137", "sitting137", "agent137", "angle137", "universe137", "memory137"],
    ),
    (
        ("kitten137 sitting137 agent137 angle137 universe137 memory137", 18),
        ["kitten137", "sitting137", "agent137 angle137", "universe137", "memory137"],
    ),
    (
        ("kitten137 sitting137 agent137 angle137 universe137 memory137", 28),
        ["kitten137 sitting137", "agent137 angle137", "universe137 memory137"],
    ),
    (
        ("sitting137 agent137 angle137 universe137 memory137 stream137", 6),
        ["sitting137", "agent137", "angle137", "universe137", "memory137", "stream137"],
    ),
    (
        ("sitting137 agent137 angle137 universe137 memory137 stream137", 10),
        ["sitting137", "agent137", "angle137", "universe137", "memory137", "stream137"],
    ),
    (
        ("sitting137 agent137 angle137 universe137 memory137 stream137", 18),
        ["sitting137", "agent137 angle137", "universe137", "memory137", "stream137"],
    ),
    (
        ("sitting137 agent137 angle137 universe137 memory137 stream137", 28),
        ["sitting137 agent137 angle137", "universe137 memory137", "stream137"],
    ),
    (
        ("agent137 angle137 universe137 memory137 stream137 context137", 6),
        ["agent137", "angle137", "universe137", "memory137", "stream137", "context137"],
    ),
    (
        ("agent137 angle137 universe137 memory137 stream137 context137", 10),
        ["agent137", "angle137", "universe137", "memory137", "stream137", "context137"],
    ),
    (
        ("agent137 angle137 universe137 memory137 stream137 context137", 18),
        ["agent137 angle137", "universe137", "memory137", "stream137", "context137"],
    ),
    (
        ("agent137 angle137 universe137 memory137 stream137 context137", 28),
        ["agent137 angle137", "universe137 memory137", "stream137 context137"],
    ),
    (
        ("angle137 universe137 memory137 stream137 context137 knowledge137", 6),
        ["angle137", "universe137", "memory137", "stream137", "context137", "knowledge137"],
    ),
    (
        ("angle137 universe137 memory137 stream137 context137 knowledge137", 10),
        ["angle137", "universe137", "memory137", "stream137", "context137", "knowledge137"],
    ),
    (
        ("angle137 universe137 memory137 stream137 context137 knowledge137", 18),
        ["angle137", "universe137", "memory137", "stream137", "context137", "knowledge137"],
    ),
    (
        ("angle137 universe137 memory137 stream137 context137 knowledge137", 28),
        ["angle137 universe137", "memory137 stream137", "context137 knowledge137"],
    ),
    (
        ("universe137 memory137 stream137 context137 knowledge137 vector137", 6),
        ["universe137", "memory137", "stream137", "context137", "knowledge137", "vector137"],
    ),
    (
        ("universe137 memory137 stream137 context137 knowledge137 vector137", 10),
        ["universe137", "memory137", "stream137", "context137", "knowledge137", "vector137"],
    ),
    (
        ("universe137 memory137 stream137 context137 knowledge137 vector137", 18),
        ["universe137", "memory137", "stream137", "context137", "knowledge137", "vector137"],
    ),
    (
        ("universe137 memory137 stream137 context137 knowledge137 vector137", 28),
        ["universe137 memory137", "stream137 context137", "knowledge137 vector137"],
    ),
    (
        ("memory137 stream137 context137 knowledge137 vector137 processor137", 6),
        ["memory137", "stream137", "context137", "knowledge137", "vector137", "processor137"],
    ),
    (
        ("memory137 stream137 context137 knowledge137 vector137 processor137", 10),
        ["memory137", "stream137", "context137", "knowledge137", "vector137", "processor137"],
    ),
    (
        ("memory137 stream137 context137 knowledge137 vector137 processor137", 18),
        ["memory137", "stream137", "context137", "knowledge137", "vector137", "processor137"],
    ),
    (
        ("memory137 stream137 context137 knowledge137 vector137 processor137", 28),
        ["memory137 stream137", "context137 knowledge137", "vector137 processor137"],
    ),
    (
        ("stream137 context137 knowledge137 vector137 processor137 reasoning137", 6),
        ["stream137", "context137", "knowledge137", "vector137", "processor137", "reasoning137"],
    ),
    (
        ("stream137 context137 knowledge137 vector137 processor137 reasoning137", 10),
        ["stream137", "context137", "knowledge137", "vector137", "processor137", "reasoning137"],
    ),
    (
        ("stream137 context137 knowledge137 vector137 processor137 reasoning137", 18),
        ["stream137", "context137", "knowledge137", "vector137", "processor137", "reasoning137"],
    ),
    (
        ("stream137 context137 knowledge137 vector137 processor137 reasoning137", 28),
        ["stream137 context137", "knowledge137 vector137", "processor137 reasoning137"],
    ),
    (
        ("context137 knowledge137 vector137 processor137 reasoning137 machine137", 6),
        ["context137", "knowledge137", "vector137", "processor137", "reasoning137", "machine137"],
    ),
    (
        ("context137 knowledge137 vector137 processor137 reasoning137 machine137", 10),
        ["context137", "knowledge137", "vector137", "processor137", "reasoning137", "machine137"],
    ),
    (
        ("context137 knowledge137 vector137 processor137 reasoning137 machine137", 18),
        ["context137", "knowledge137", "vector137", "processor137", "reasoning137", "machine137"],
    ),
    (
        ("context137 knowledge137 vector137 processor137 reasoning137 machine137", 28),
        ["context137 knowledge137", "vector137 processor137", "reasoning137 machine137"],
    ),
    (
        ("knowledge137 vector137 processor137 reasoning137 machine137 learning137", 6),
        ["knowledge137", "vector137", "processor137", "reasoning137", "machine137", "learning137"],
    ),
    (
        ("knowledge137 vector137 processor137 reasoning137 machine137 learning137", 10),
        ["knowledge137", "vector137", "processor137", "reasoning137", "machine137", "learning137"],
    ),
    (
        ("knowledge137 vector137 processor137 reasoning137 machine137 learning137", 18),
        ["knowledge137", "vector137", "processor137", "reasoning137", "machine137", "learning137"],
    ),
    (
        ("knowledge137 vector137 processor137 reasoning137 machine137 learning137", 28),
        ["knowledge137 vector137", "processor137 reasoning137", "machine137 learning137"],
    ),
    (
        ("vector137 processor137 reasoning137 machine137 learning137 model137", 6),
        ["vector137", "processor137", "reasoning137", "machine137", "learning137", "model137"],
    ),
    (
        ("vector137 processor137 reasoning137 machine137 learning137 model137", 10),
        ["vector137", "processor137", "reasoning137", "machine137", "learning137", "model137"],
    ),
    (
        ("vector137 processor137 reasoning137 machine137 learning137 model137", 18),
        ["vector137", "processor137", "reasoning137", "machine137", "learning137", "model137"],
    ),
    (
        ("vector137 processor137 reasoning137 machine137 learning137 model137", 28),
        ["vector137 processor137", "reasoning137 machine137", "learning137 model137"],
    ),
    (
        ("processor137 reasoning137 machine137 learning137 model137 token137", 6),
        ["processor137", "reasoning137", "machine137", "learning137", "model137", "token137"],
    ),
    (
        ("processor137 reasoning137 machine137 learning137 model137 token137", 10),
        ["processor137", "reasoning137", "machine137", "learning137", "model137", "token137"],
    ),
    (
        ("processor137 reasoning137 machine137 learning137 model137 token137", 18),
        ["processor137", "reasoning137", "machine137", "learning137", "model137 token137"],
    ),
    (
        ("processor137 reasoning137 machine137 learning137 model137 token137", 28),
        ["processor137 reasoning137", "machine137 learning137", "model137 token137"],
    ),
    (
        ("reasoning137 machine137 learning137 model137 token137 prompt137", 6),
        ["reasoning137", "machine137", "learning137", "model137", "token137", "prompt137"],
    ),
    (
        ("reasoning137 machine137 learning137 model137 token137 prompt137", 10),
        ["reasoning137", "machine137", "learning137", "model137", "token137", "prompt137"],
    ),
    (
        ("reasoning137 machine137 learning137 model137 token137 prompt137", 18),
        ["reasoning137", "machine137", "learning137", "model137 token137", "prompt137"],
    ),
    (
        ("reasoning137 machine137 learning137 model137 token137 prompt137", 28),
        ["reasoning137 machine137", "learning137 model137", "token137 prompt137"],
    ),
    (
        ("machine137 learning137 model137 token137 prompt137 session137", 6),
        ["machine137", "learning137", "model137", "token137", "prompt137", "session137"],
    ),
    (
        ("machine137 learning137 model137 token137 prompt137 session137", 10),
        ["machine137", "learning137", "model137", "token137", "prompt137", "session137"],
    ),
    (
        ("machine137 learning137 model137 token137 prompt137 session137", 18),
        ["machine137", "learning137", "model137 token137", "prompt137", "session137"],
    ),
    (
        ("machine137 learning137 model137 token137 prompt137 session137", 28),
        ["machine137 learning137", "model137 token137 prompt137", "session137"],
    ),
    (
        ("learning137 model137 token137 prompt137 session137 library137", 6),
        ["learning137", "model137", "token137", "prompt137", "session137", "library137"],
    ),
    (
        ("learning137 model137 token137 prompt137 session137 library137", 10),
        ["learning137", "model137", "token137", "prompt137", "session137", "library137"],
    ),
    (
        ("learning137 model137 token137 prompt137 session137 library137", 18),
        ["learning137", "model137 token137", "prompt137", "session137", "library137"],
    ),
    (
        ("learning137 model137 token137 prompt137 session137 library137", 28),
        ["learning137 model137", "token137 prompt137", "session137 library137"],
    ),
    (
        ("model137 token137 prompt137 session137 library137 service137", 6),
        ["model137", "token137", "prompt137", "session137", "library137", "service137"],
    ),
    (
        ("model137 token137 prompt137 session137 library137 service137", 10),
        ["model137", "token137", "prompt137", "session137", "library137", "service137"],
    ),
    (
        ("model137 token137 prompt137 session137 library137 service137", 18),
        ["model137 token137", "prompt137", "session137", "library137", "service137"],
    ),
    (
        ("model137 token137 prompt137 session137 library137 service137", 28),
        ["model137 token137 prompt137", "session137 library137", "service137"],
    ),
    (
        ("token137 prompt137 session137 library137 service137 gateway137", 6),
        ["token137", "prompt137", "session137", "library137", "service137", "gateway137"],
    ),
    (
        ("token137 prompt137 session137 library137 service137 gateway137", 10),
        ["token137", "prompt137", "session137", "library137", "service137", "gateway137"],
    ),
    (
        ("token137 prompt137 session137 library137 service137 gateway137", 18),
        ["token137 prompt137", "session137", "library137", "service137", "gateway137"],
    ),
    (
        ("token137 prompt137 session137 library137 service137 gateway137", 28),
        ["token137 prompt137", "session137 library137", "service137 gateway137"],
    ),
    (
        ("prompt137 session137 library137 service137 gateway137 storage137", 6),
        ["prompt137", "session137", "library137", "service137", "gateway137", "storage137"],
    ),
    (
        ("prompt137 session137 library137 service137 gateway137 storage137", 10),
        ["prompt137", "session137", "library137", "service137", "gateway137", "storage137"],
    ),
    (
        ("prompt137 session137 library137 service137 gateway137 storage137", 18),
        ["prompt137", "session137", "library137", "service137", "gateway137", "storage137"],
    ),
    (
        ("prompt137 session137 library137 service137 gateway137 storage137", 28),
        ["prompt137 session137", "library137 service137", "gateway137 storage137"],
    ),
    (
        ("session137 library137 service137 gateway137 storage137 network137", 6),
        ["session137", "library137", "service137", "gateway137", "storage137", "network137"],
    ),
    (
        ("session137 library137 service137 gateway137 storage137 network137", 10),
        ["session137", "library137", "service137", "gateway137", "storage137", "network137"],
    ),
    (
        ("session137 library137 service137 gateway137 storage137 network137", 18),
        ["session137", "library137", "service137", "gateway137", "storage137", "network137"],
    ),
    (
        ("session137 library137 service137 gateway137 storage137 network137", 28),
        ["session137 library137", "service137 gateway137", "storage137 network137"],
    ),
    (
        ("library137 service137 gateway137 storage137 network137 latency137", 6),
        ["library137", "service137", "gateway137", "storage137", "network137", "latency137"],
    ),
    (
        ("library137 service137 gateway137 storage137 network137 latency137", 10),
        ["library137", "service137", "gateway137", "storage137", "network137", "latency137"],
    ),
    (
        ("library137 service137 gateway137 storage137 network137 latency137", 18),
        ["library137", "service137", "gateway137", "storage137", "network137", "latency137"],
    ),
    (
        ("library137 service137 gateway137 storage137 network137 latency137", 28),
        ["library137 service137", "gateway137 storage137", "network137 latency137"],
    ),
    (
        ("service137 gateway137 storage137 network137 latency137 buffer137", 6),
        ["service137", "gateway137", "storage137", "network137", "latency137", "buffer137"],
    ),
    (
        ("service137 gateway137 storage137 network137 latency137 buffer137", 10),
        ["service137", "gateway137", "storage137", "network137", "latency137", "buffer137"],
    ),
    (
        ("service137 gateway137 storage137 network137 latency137 buffer137", 18),
        ["service137", "gateway137", "storage137", "network137", "latency137", "buffer137"],
    ),
    (
        ("service137 gateway137 storage137 network137 latency137 buffer137", 28),
        ["service137 gateway137", "storage137 network137", "latency137 buffer137"],
    ),
    (
        ("gateway137 storage137 network137 latency137 buffer137 queue137", 6),
        ["gateway137", "storage137", "network137", "latency137", "buffer137", "queue137"],
    ),
    (
        ("gateway137 storage137 network137 latency137 buffer137 queue137", 10),
        ["gateway137", "storage137", "network137", "latency137", "buffer137", "queue137"],
    ),
    (
        ("gateway137 storage137 network137 latency137 buffer137 queue137", 18),
        ["gateway137", "storage137", "network137", "latency137", "buffer137 queue137"],
    ),
    (
        ("gateway137 storage137 network137 latency137 buffer137 queue137", 28),
        ["gateway137 storage137", "network137 latency137", "buffer137 queue137"],
    ),
    (
        ("storage137 network137 latency137 buffer137 queue137 worker137", 6),
        ["storage137", "network137", "latency137", "buffer137", "queue137", "worker137"],
    ),
    (
        ("storage137 network137 latency137 buffer137 queue137 worker137", 10),
        ["storage137", "network137", "latency137", "buffer137", "queue137", "worker137"],
    ),
    (
        ("storage137 network137 latency137 buffer137 queue137 worker137", 18),
        ["storage137", "network137", "latency137", "buffer137 queue137", "worker137"],
    ),
    (
        ("storage137 network137 latency137 buffer137 queue137 worker137", 28),
        ["storage137 network137", "latency137 buffer137", "queue137 worker137"],
    ),
    (
        ("network137 latency137 buffer137 queue137 worker137 kernel137", 6),
        ["network137", "latency137", "buffer137", "queue137", "worker137", "kernel137"],
    ),
    (
        ("network137 latency137 buffer137 queue137 worker137 kernel137", 10),
        ["network137", "latency137", "buffer137", "queue137", "worker137", "kernel137"],
    ),
    (
        ("network137 latency137 buffer137 queue137 worker137 kernel137", 18),
        ["network137", "latency137", "buffer137 queue137", "worker137", "kernel137"],
    ),
    (
        ("network137 latency137 buffer137 queue137 worker137 kernel137", 28),
        ["network137 latency137", "buffer137 queue137 worker137", "kernel137"],
    ),
    (
        ("latency137 buffer137 queue137 worker137 kernel137 signal137", 6),
        ["latency137", "buffer137", "queue137", "worker137", "kernel137", "signal137"],
    ),
    (
        ("latency137 buffer137 queue137 worker137 kernel137 signal137", 10),
        ["latency137", "buffer137", "queue137", "worker137", "kernel137", "signal137"],
    ),
    (
        ("latency137 buffer137 queue137 worker137 kernel137 signal137", 18),
        ["latency137", "buffer137 queue137", "worker137", "kernel137", "signal137"],
    ),
    (
        ("latency137 buffer137 queue137 worker137 kernel137 signal137", 28),
        ["latency137 buffer137", "queue137 worker137 kernel137", "signal137"],
    ),
    (
        ("buffer137 queue137 worker137 kernel137 signal137 packet137", 6),
        ["buffer137", "queue137", "worker137", "kernel137", "signal137", "packet137"],
    ),
    (
        ("buffer137 queue137 worker137 kernel137 signal137 packet137", 10),
        ["buffer137", "queue137", "worker137", "kernel137", "signal137", "packet137"],
    ),
    (
        ("buffer137 queue137 worker137 kernel137 signal137 packet137", 18),
        ["buffer137 queue137", "worker137", "kernel137", "signal137", "packet137"],
    ),
    (
        ("buffer137 queue137 worker137 kernel137 signal137 packet137", 28),
        ["buffer137 queue137 worker137", "kernel137 signal137", "packet137"],
    ),
    (
        ("queue137 worker137 kernel137 signal137 packet137 router137", 6),
        ["queue137", "worker137", "kernel137", "signal137", "packet137", "router137"],
    ),
    (
        ("queue137 worker137 kernel137 signal137 packet137 router137", 10),
        ["queue137", "worker137", "kernel137", "signal137", "packet137", "router137"],
    ),
    (
        ("queue137 worker137 kernel137 signal137 packet137 router137", 18),
        ["queue137 worker137", "kernel137", "signal137", "packet137", "router137"],
    ),
    (
        ("queue137 worker137 kernel137 signal137 packet137 router137", 28),
        ["queue137 worker137 kernel137", "signal137 packet137", "router137"],
    ),
    (
        ("worker137 kernel137 signal137 packet137 router137 cluster137", 6),
        ["worker137", "kernel137", "signal137", "packet137", "router137", "cluster137"],
    ),
    (
        ("worker137 kernel137 signal137 packet137 router137 cluster137", 10),
        ["worker137", "kernel137", "signal137", "packet137", "router137", "cluster137"],
    ),
    (
        ("worker137 kernel137 signal137 packet137 router137 cluster137", 18),
        ["worker137", "kernel137", "signal137", "packet137", "router137", "cluster137"],
    ),
    (
        ("worker137 kernel137 signal137 packet137 router137 cluster137", 28),
        ["worker137 kernel137", "signal137 packet137", "router137 cluster137"],
    ),
    (
        ("kernel137 signal137 packet137 router137 cluster137 mirror137", 6),
        ["kernel137", "signal137", "packet137", "router137", "cluster137", "mirror137"],
    ),
    (
        ("kernel137 signal137 packet137 router137 cluster137 mirror137", 10),
        ["kernel137", "signal137", "packet137", "router137", "cluster137", "mirror137"],
    ),
    (
        ("kernel137 signal137 packet137 router137 cluster137 mirror137", 18),
        ["kernel137", "signal137", "packet137", "router137", "cluster137", "mirror137"],
    ),
    (
        ("kernel137 signal137 packet137 router137 cluster137 mirror137", 28),
        ["kernel137 signal137", "packet137 router137", "cluster137 mirror137"],
    ),
    (
        ("signal137 packet137 router137 cluster137 mirror137 filter137", 6),
        ["signal137", "packet137", "router137", "cluster137", "mirror137", "filter137"],
    ),
    (
        ("signal137 packet137 router137 cluster137 mirror137 filter137", 10),
        ["signal137", "packet137", "router137", "cluster137", "mirror137", "filter137"],
    ),
    (
        ("signal137 packet137 router137 cluster137 mirror137 filter137", 18),
        ["signal137", "packet137", "router137", "cluster137", "mirror137", "filter137"],
    ),
    (
        ("signal137 packet137 router137 cluster137 mirror137 filter137", 28),
        ["signal137 packet137", "router137 cluster137", "mirror137 filter137"],
    ),
    (
        ("packet137 router137 cluster137 mirror137 filter137 ranking137", 6),
        ["packet137", "router137", "cluster137", "mirror137", "filter137", "ranking137"],
    ),
    (
        ("packet137 router137 cluster137 mirror137 filter137 ranking137", 10),
        ["packet137", "router137", "cluster137", "mirror137", "filter137", "ranking137"],
    ),
    (
        ("packet137 router137 cluster137 mirror137 filter137 ranking137", 18),
        ["packet137", "router137", "cluster137", "mirror137", "filter137", "ranking137"],
    ),
    (
        ("packet137 router137 cluster137 mirror137 filter137 ranking137", 28),
        ["packet137 router137", "cluster137 mirror137", "filter137 ranking137"],
    ),
    (
        ("router137 cluster137 mirror137 filter137 ranking137 encoding137", 6),
        ["router137", "cluster137", "mirror137", "filter137", "ranking137", "encoding137"],
    ),
    (
        ("router137 cluster137 mirror137 filter137 ranking137 encoding137", 10),
        ["router137", "cluster137", "mirror137", "filter137", "ranking137", "encoding137"],
    ),
    (
        ("router137 cluster137 mirror137 filter137 ranking137 encoding137", 18),
        ["router137", "cluster137", "mirror137", "filter137", "ranking137", "encoding137"],
    ),
    (
        ("router137 cluster137 mirror137 filter137 ranking137 encoding137", 28),
        ["router137 cluster137", "mirror137 filter137", "ranking137 encoding137"],
    ),
    (
        ("cluster137 mirror137 filter137 ranking137 encoding137 mapping137", 6),
        ["cluster137", "mirror137", "filter137", "ranking137", "encoding137", "mapping137"],
    ),
    (
        ("cluster137 mirror137 filter137 ranking137 encoding137 mapping137", 10),
        ["cluster137", "mirror137", "filter137", "ranking137", "encoding137", "mapping137"],
    ),
    (
        ("cluster137 mirror137 filter137 ranking137 encoding137 mapping137", 18),
        ["cluster137", "mirror137", "filter137", "ranking137", "encoding137", "mapping137"],
    ),
    (
        ("cluster137 mirror137 filter137 ranking137 encoding137 mapping137", 28),
        ["cluster137 mirror137", "filter137 ranking137", "encoding137 mapping137"],
    ),
    (
        ("mirror137 filter137 ranking137 encoding137 mapping137 record137", 6),
        ["mirror137", "filter137", "ranking137", "encoding137", "mapping137", "record137"],
    ),
    (
        ("mirror137 filter137 ranking137 encoding137 mapping137 record137", 10),
        ["mirror137", "filter137", "ranking137", "encoding137", "mapping137", "record137"],
    ),
    (
        ("mirror137 filter137 ranking137 encoding137 mapping137 record137", 18),
        ["mirror137", "filter137", "ranking137", "encoding137", "mapping137", "record137"],
    ),
    (
        ("mirror137 filter137 ranking137 encoding137 mapping137 record137", 28),
        ["mirror137 filter137", "ranking137 encoding137", "mapping137 record137"],
    ),
    (
        ("filter137 ranking137 encoding137 mapping137 record137 candle137", 6),
        ["filter137", "ranking137", "encoding137", "mapping137", "record137", "candle137"],
    ),
    (
        ("filter137 ranking137 encoding137 mapping137 record137 candle137", 10),
        ["filter137", "ranking137", "encoding137", "mapping137", "record137", "candle137"],
    ),
    (
        ("filter137 ranking137 encoding137 mapping137 record137 candle137", 18),
        ["filter137", "ranking137", "encoding137", "mapping137", "record137", "candle137"],
    ),
    (
        ("filter137 ranking137 encoding137 mapping137 record137 candle137", 28),
        ["filter137 ranking137", "encoding137 mapping137", "record137 candle137"],
    ),
    (
        ("ranking137 encoding137 mapping137 record137 candle137 thread137", 6),
        ["ranking137", "encoding137", "mapping137", "record137", "candle137", "thread137"],
    ),
    (
        ("ranking137 encoding137 mapping137 record137 candle137 thread137", 10),
        ["ranking137", "encoding137", "mapping137", "record137", "candle137", "thread137"],
    ),
    (
        ("ranking137 encoding137 mapping137 record137 candle137 thread137", 18),
        ["ranking137", "encoding137", "mapping137", "record137", "candle137", "thread137"],
    ),
    (
        ("ranking137 encoding137 mapping137 record137 candle137 thread137", 28),
        ["ranking137 encoding137", "mapping137 record137", "candle137 thread137"],
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
