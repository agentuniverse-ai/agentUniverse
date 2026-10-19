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
        ("round 114: the quick brown fox jumps over the lazy dog", 4),
        ["round", "114:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", 8),
        ["round", "114: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", 12),
        ["round 114:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", 16),
        ["round 114: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", 24),
        ["round 114: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 114: the quick brown fox jumps over the lazy dog", 32),
        ["round 114: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", 4),
        ["round", "114:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", 8),
        ["round", "114:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", 12),
        ["round 114:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", 16),
        ["round 114:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", 24),
        ["round 114: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 114: agentuniverse is a framework for multi agents", 32),
        ["round 114: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", 4),
        ["round", "114:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", 8),
        ["round", "114:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", 12),
        ["round 114:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", 16),
        ["round 114:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", 24),
        ["round 114: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 114: knowledge stored as vectors enables retrieval", 32),
        ["round 114: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 114: the processor reads the record then stops", 4),
        ["round", "114:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 114: the processor reads the record then stops", 8),
        ["round", "114: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 114: the processor reads the record then stops", 12),
        ["round 114:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 114: the processor reads the record then stops", 16),
        ["round 114: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 114: the processor reads the record then stops", 24),
        ["round 114: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 114: the processor reads the record then stops", 32),
        ["round 114: the processor reads", "the record then stops"],
    ),
    (
        ("round 114: a worker pulls the next task from the queue", 4),
        ["round", "114:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 114: a worker pulls the next task from the queue", 8),
        ["round", "114: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 114: a worker pulls the next task from the queue", 12),
        ["round 114: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 114: a worker pulls the next task from the queue", 16),
        ["round 114: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 114: a worker pulls the next task from the queue", 24),
        ["round 114: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 114: a worker pulls the next task from the queue", 32),
        ["round 114: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 114: signals travel through the network layer", 4),
        ["round", "114:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 114: signals travel through the network layer", 8),
        ["round", "114:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 114: signals travel through the network layer", 12),
        ["round 114:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 114: signals travel through the network layer", 16),
        ["round 114:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 114: signals travel through the network layer", 24),
        ["round 114: signals", "travel through the", "network layer"],
    ),
    (
        ("round 114: signals travel through the network layer", 32),
        ["round 114: signals travel", "through the network layer"],
    ),
    (
        ("round 114: the gateway routes each request by policy", 4),
        ["round", "114:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 114: the gateway routes each request by policy", 8),
        ["round", "114: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 114: the gateway routes each request by policy", 12),
        ["round 114:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 114: the gateway routes each request by policy", 16),
        ["round 114: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 114: the gateway routes each request by policy", 24),
        ["round 114: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 114: the gateway routes each request by policy", 32),
        ["round 114: the gateway routes", "each request by policy"],
    ),
    (
        ("round 114: memory grows until the buffer is full", 4),
        ["round", "114:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 114: memory grows until the buffer is full", 8),
        ["round", "114:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 114: memory grows until the buffer is full", 12),
        ["round 114:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 114: memory grows until the buffer is full", 16),
        ["round 114:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 114: memory grows until the buffer is full", 24), ["round 114: memory grows", "until the buffer is full"]),
    (("round 114: memory grows until the buffer is full", 32), ["round 114: memory grows until", "the buffer is full"]),
    (
        ("round 114: the cluster mirrors every packet twice", 4),
        ["round", "114:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 114: the cluster mirrors every packet twice", 8),
        ["round", "114: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 114: the cluster mirrors every packet twice", 12),
        ["round 114:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 114: the cluster mirrors every packet twice", 16),
        ["round 114: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 114: the cluster mirrors every packet twice", 24),
        ["round 114: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 114: the cluster mirrors every packet twice", 32),
        ["round 114: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", 4),
        ["round", "114:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", 8),
        ["round", "114:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", 12),
        ["round 114:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", 16),
        ["round 114:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", 24),
        ["round 114: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 114: ranking uses tokens learned from the corpus", 32),
        ["round 114: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 114: a long session ends when the candle dies", 4),
        ["round", "114:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 114: a long session ends when the candle dies", 8),
        ["round", "114: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 114: a long session ends when the candle dies", 12),
        ["round 114: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 114: a long session ends when the candle dies", 16),
        ["round 114: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 114: a long session ends when the candle dies", 24),
        ["round 114: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 114: a long session ends when the candle dies", 32),
        ["round 114: a long session ends", "when the candle dies"],
    ),
    (
        ("round 114: encode the prompt then map the result", 4),
        ["round", "114:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 114: encode the prompt then map the result", 8),
        ["round", "114:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 114: encode the prompt then map the result", 12),
        ["round 114:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 114: encode the prompt then map the result", 16),
        ["round 114:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 114: encode the prompt then map the result", 24),
        ["round 114: encode the", "prompt then map the", "result"],
    ),
    (("round 114: encode the prompt then map the result", 32), ["round 114: encode the prompt", "then map the result"]),
    (
        ("round 114: the kernel wakes the worker at dawn", 4),
        ["round", "114:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 114: the kernel wakes the worker at dawn", 8),
        ["round", "114: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 114: the kernel wakes the worker at dawn", 12),
        ["round 114:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 114: the kernel wakes the worker at dawn", 16), ["round 114: the", "kernel wakes the", "worker at dawn"]),
    (("round 114: the kernel wakes the worker at dawn", 24), ["round 114: the kernel", "wakes the worker at dawn"]),
    (("round 114: the kernel wakes the worker at dawn", 32), ["round 114: the kernel wakes the", "worker at dawn"]),
    (
        ("round 114: service latency drops after the patch", 4),
        ["round", "114:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 114: service latency drops after the patch", 8),
        ["round", "114:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 114: service latency drops after the patch", 12),
        ["round 114:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 114: service latency drops after the patch", 16),
        ["round 114:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 114: service latency drops after the patch", 24),
        ["round 114: service", "latency drops after the", "patch"],
    ),
    (("round 114: service latency drops after the patch", 32), ["round 114: service latency drops", "after the patch"]),
    (
        ("round 114: the library caches every vector it sees", 4),
        ["round", "114:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 114: the library caches every vector it sees", 8),
        ["round", "114: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 114: the library caches every vector it sees", 12),
        ["round 114:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 114: the library caches every vector it sees", 16),
        ["round 114: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 114: the library caches every vector it sees", 24),
        ["round 114: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 114: the library caches every vector it sees", 32),
        ["round 114: the library caches", "every vector it sees"],
    ),
    (
        ("round 114: agents argue then the debate resolves", 4),
        ["round", "114:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 114: agents argue then the debate resolves", 8),
        ["round", "114:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 114: agents argue then the debate resolves", 12),
        ["round 114:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 114: agents argue then the debate resolves", 16),
        ["round 114:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 114: agents argue then the debate resolves", 24), ["round 114: agents argue", "then the debate resolves"]),
    (("round 114: agents argue then the debate resolves", 32), ["round 114: agents argue then the", "debate resolves"]),
    (
        ("round 114: the filter keeps only strong matches", 4),
        ["round", "114:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 114: the filter keeps only strong matches", 8),
        ["round", "114: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 114: the filter keeps only strong matches", 12),
        ["round 114:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 114: the filter keeps only strong matches", 16),
        ["round 114: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 114: the filter keeps only strong matches", 24),
        ["round 114: the filter", "keeps only strong", "matches"],
    ),
    (("round 114: the filter keeps only strong matches", 32), ["round 114: the filter keeps only", "strong matches"]),
    (
        ("round 114: the model answers with a short reply", 4),
        ["round", "114:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 114: the model answers with a short reply", 8),
        ["round", "114: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 114: the model answers with a short reply", 12),
        ["round 114:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 114: the model answers with a short reply", 16),
        ["round 114: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 114: the model answers with a short reply", 24),
        ["round 114: the model", "answers with a short", "reply"],
    ),
    (("round 114: the model answers with a short reply", 32), ["round 114: the model answers", "with a short reply"]),
    (
        ("round 114: the recorder stores the reasoning trace", 4),
        ["round", "114:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 114: the recorder stores the reasoning trace", 8),
        ["round", "114: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 114: the recorder stores the reasoning trace", 12),
        ["round 114:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 114: the recorder stores the reasoning trace", 16),
        ["round 114: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 114: the recorder stores the reasoning trace", 24),
        ["round 114: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 114: the recorder stores the reasoning trace", 32),
        ["round 114: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 114: the angel watches the processor run", 4),
        ["round", "114:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 114: the angel watches the processor run", 8),
        ["round", "114: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 114: the angel watches the processor run", 12),
        ["round 114:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 114: the angel watches the processor run", 16),
        ["round 114: the", "angel watches", "the processor", "run"],
    ),
    (("round 114: the angel watches the processor run", 24), ["round 114: the angel", "watches the processor", "run"]),
    (("round 114: the angel watches the processor run", 32), ["round 114: the angel watches the", "processor run"]),
    (
        ("round 114: angle of the vector decides the match", 4),
        ["round", "114:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 114: angle of the vector decides the match", 8),
        ["round", "114:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 114: angle of the vector decides the match", 12),
        ["round 114:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 114: angle of the vector decides the match", 16),
        ["round 114: angle", "of the vector", "decides the", "match"],
    ),
    (("round 114: angle of the vector decides the match", 24), ["round 114: angle of the", "vector decides the match"]),
    (("round 114: angle of the vector decides the match", 32), ["round 114: angle of the vector", "decides the match"]),
    (
        ("round 114: the candle burns twice as long at night", 4),
        ["round", "114:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 114: the candle burns twice as long at night", 8),
        ["round", "114: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 114: the candle burns twice as long at night", 12),
        ["round 114:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 114: the candle burns twice as long at night", 16),
        ["round 114: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 114: the candle burns twice as long at night", 24),
        ["round 114: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 114: the candle burns twice as long at night", 32),
        ["round 114: the candle burns", "twice as long at night"],
    ),
    (
        ("round 114: a mirror of the universe in one line", 4),
        ["round", "114:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 114: a mirror of the universe in one line", 8),
        ["round", "114: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 114: a mirror of the universe in one line", 12),
        ["round 114: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 114: a mirror of the universe in one line", 16),
        ["round 114: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 114: a mirror of the universe in one line", 24), ["round 114: a mirror of", "the universe in one line"]),
    (("round 114: a mirror of the universe in one line", 32), ["round 114: a mirror of the", "universe in one line"]),
    (
        ("round 114: the queue drains before the storm", 4),
        ["round", "114:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 114: the queue drains before the storm", 8),
        ["round", "114: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 114: the queue drains before the storm", 12),
        ["round 114:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 114: the queue drains before the storm", 16), ["round 114: the", "queue drains", "before the storm"]),
    (("round 114: the queue drains before the storm", 24), ["round 114: the queue", "drains before the storm"]),
    (("round 114: the queue drains before the storm", 32), ["round 114: the queue drains", "before the storm"]),
    (
        ("kitten114 sitting114 agent114 angle114 universe114 memory114", 6),
        ["kitten114", "sitting114", "agent114", "angle114", "universe114", "memory114"],
    ),
    (
        ("kitten114 sitting114 agent114 angle114 universe114 memory114", 10),
        ["kitten114", "sitting114", "agent114", "angle114", "universe114", "memory114"],
    ),
    (
        ("kitten114 sitting114 agent114 angle114 universe114 memory114", 18),
        ["kitten114", "sitting114", "agent114 angle114", "universe114", "memory114"],
    ),
    (
        ("kitten114 sitting114 agent114 angle114 universe114 memory114", 28),
        ["kitten114 sitting114", "agent114 angle114", "universe114 memory114"],
    ),
    (
        ("sitting114 agent114 angle114 universe114 memory114 stream114", 6),
        ["sitting114", "agent114", "angle114", "universe114", "memory114", "stream114"],
    ),
    (
        ("sitting114 agent114 angle114 universe114 memory114 stream114", 10),
        ["sitting114", "agent114", "angle114", "universe114", "memory114", "stream114"],
    ),
    (
        ("sitting114 agent114 angle114 universe114 memory114 stream114", 18),
        ["sitting114", "agent114 angle114", "universe114", "memory114", "stream114"],
    ),
    (
        ("sitting114 agent114 angle114 universe114 memory114 stream114", 28),
        ["sitting114 agent114 angle114", "universe114 memory114", "stream114"],
    ),
    (
        ("agent114 angle114 universe114 memory114 stream114 context114", 6),
        ["agent114", "angle114", "universe114", "memory114", "stream114", "context114"],
    ),
    (
        ("agent114 angle114 universe114 memory114 stream114 context114", 10),
        ["agent114", "angle114", "universe114", "memory114", "stream114", "context114"],
    ),
    (
        ("agent114 angle114 universe114 memory114 stream114 context114", 18),
        ["agent114 angle114", "universe114", "memory114", "stream114", "context114"],
    ),
    (
        ("agent114 angle114 universe114 memory114 stream114 context114", 28),
        ["agent114 angle114", "universe114 memory114", "stream114 context114"],
    ),
    (
        ("angle114 universe114 memory114 stream114 context114 knowledge114", 6),
        ["angle114", "universe114", "memory114", "stream114", "context114", "knowledge114"],
    ),
    (
        ("angle114 universe114 memory114 stream114 context114 knowledge114", 10),
        ["angle114", "universe114", "memory114", "stream114", "context114", "knowledge114"],
    ),
    (
        ("angle114 universe114 memory114 stream114 context114 knowledge114", 18),
        ["angle114", "universe114", "memory114", "stream114", "context114", "knowledge114"],
    ),
    (
        ("angle114 universe114 memory114 stream114 context114 knowledge114", 28),
        ["angle114 universe114", "memory114 stream114", "context114 knowledge114"],
    ),
    (
        ("universe114 memory114 stream114 context114 knowledge114 vector114", 6),
        ["universe114", "memory114", "stream114", "context114", "knowledge114", "vector114"],
    ),
    (
        ("universe114 memory114 stream114 context114 knowledge114 vector114", 10),
        ["universe114", "memory114", "stream114", "context114", "knowledge114", "vector114"],
    ),
    (
        ("universe114 memory114 stream114 context114 knowledge114 vector114", 18),
        ["universe114", "memory114", "stream114", "context114", "knowledge114", "vector114"],
    ),
    (
        ("universe114 memory114 stream114 context114 knowledge114 vector114", 28),
        ["universe114 memory114", "stream114 context114", "knowledge114 vector114"],
    ),
    (
        ("memory114 stream114 context114 knowledge114 vector114 processor114", 6),
        ["memory114", "stream114", "context114", "knowledge114", "vector114", "processor114"],
    ),
    (
        ("memory114 stream114 context114 knowledge114 vector114 processor114", 10),
        ["memory114", "stream114", "context114", "knowledge114", "vector114", "processor114"],
    ),
    (
        ("memory114 stream114 context114 knowledge114 vector114 processor114", 18),
        ["memory114", "stream114", "context114", "knowledge114", "vector114", "processor114"],
    ),
    (
        ("memory114 stream114 context114 knowledge114 vector114 processor114", 28),
        ["memory114 stream114", "context114 knowledge114", "vector114 processor114"],
    ),
    (
        ("stream114 context114 knowledge114 vector114 processor114 reasoning114", 6),
        ["stream114", "context114", "knowledge114", "vector114", "processor114", "reasoning114"],
    ),
    (
        ("stream114 context114 knowledge114 vector114 processor114 reasoning114", 10),
        ["stream114", "context114", "knowledge114", "vector114", "processor114", "reasoning114"],
    ),
    (
        ("stream114 context114 knowledge114 vector114 processor114 reasoning114", 18),
        ["stream114", "context114", "knowledge114", "vector114", "processor114", "reasoning114"],
    ),
    (
        ("stream114 context114 knowledge114 vector114 processor114 reasoning114", 28),
        ["stream114 context114", "knowledge114 vector114", "processor114 reasoning114"],
    ),
    (
        ("context114 knowledge114 vector114 processor114 reasoning114 machine114", 6),
        ["context114", "knowledge114", "vector114", "processor114", "reasoning114", "machine114"],
    ),
    (
        ("context114 knowledge114 vector114 processor114 reasoning114 machine114", 10),
        ["context114", "knowledge114", "vector114", "processor114", "reasoning114", "machine114"],
    ),
    (
        ("context114 knowledge114 vector114 processor114 reasoning114 machine114", 18),
        ["context114", "knowledge114", "vector114", "processor114", "reasoning114", "machine114"],
    ),
    (
        ("context114 knowledge114 vector114 processor114 reasoning114 machine114", 28),
        ["context114 knowledge114", "vector114 processor114", "reasoning114 machine114"],
    ),
    (
        ("knowledge114 vector114 processor114 reasoning114 machine114 learning114", 6),
        ["knowledge114", "vector114", "processor114", "reasoning114", "machine114", "learning114"],
    ),
    (
        ("knowledge114 vector114 processor114 reasoning114 machine114 learning114", 10),
        ["knowledge114", "vector114", "processor114", "reasoning114", "machine114", "learning114"],
    ),
    (
        ("knowledge114 vector114 processor114 reasoning114 machine114 learning114", 18),
        ["knowledge114", "vector114", "processor114", "reasoning114", "machine114", "learning114"],
    ),
    (
        ("knowledge114 vector114 processor114 reasoning114 machine114 learning114", 28),
        ["knowledge114 vector114", "processor114 reasoning114", "machine114 learning114"],
    ),
    (
        ("vector114 processor114 reasoning114 machine114 learning114 model114", 6),
        ["vector114", "processor114", "reasoning114", "machine114", "learning114", "model114"],
    ),
    (
        ("vector114 processor114 reasoning114 machine114 learning114 model114", 10),
        ["vector114", "processor114", "reasoning114", "machine114", "learning114", "model114"],
    ),
    (
        ("vector114 processor114 reasoning114 machine114 learning114 model114", 18),
        ["vector114", "processor114", "reasoning114", "machine114", "learning114", "model114"],
    ),
    (
        ("vector114 processor114 reasoning114 machine114 learning114 model114", 28),
        ["vector114 processor114", "reasoning114 machine114", "learning114 model114"],
    ),
    (
        ("processor114 reasoning114 machine114 learning114 model114 token114", 6),
        ["processor114", "reasoning114", "machine114", "learning114", "model114", "token114"],
    ),
    (
        ("processor114 reasoning114 machine114 learning114 model114 token114", 10),
        ["processor114", "reasoning114", "machine114", "learning114", "model114", "token114"],
    ),
    (
        ("processor114 reasoning114 machine114 learning114 model114 token114", 18),
        ["processor114", "reasoning114", "machine114", "learning114", "model114 token114"],
    ),
    (
        ("processor114 reasoning114 machine114 learning114 model114 token114", 28),
        ["processor114 reasoning114", "machine114 learning114", "model114 token114"],
    ),
    (
        ("reasoning114 machine114 learning114 model114 token114 prompt114", 6),
        ["reasoning114", "machine114", "learning114", "model114", "token114", "prompt114"],
    ),
    (
        ("reasoning114 machine114 learning114 model114 token114 prompt114", 10),
        ["reasoning114", "machine114", "learning114", "model114", "token114", "prompt114"],
    ),
    (
        ("reasoning114 machine114 learning114 model114 token114 prompt114", 18),
        ["reasoning114", "machine114", "learning114", "model114 token114", "prompt114"],
    ),
    (
        ("reasoning114 machine114 learning114 model114 token114 prompt114", 28),
        ["reasoning114 machine114", "learning114 model114", "token114 prompt114"],
    ),
    (
        ("machine114 learning114 model114 token114 prompt114 session114", 6),
        ["machine114", "learning114", "model114", "token114", "prompt114", "session114"],
    ),
    (
        ("machine114 learning114 model114 token114 prompt114 session114", 10),
        ["machine114", "learning114", "model114", "token114", "prompt114", "session114"],
    ),
    (
        ("machine114 learning114 model114 token114 prompt114 session114", 18),
        ["machine114", "learning114", "model114 token114", "prompt114", "session114"],
    ),
    (
        ("machine114 learning114 model114 token114 prompt114 session114", 28),
        ["machine114 learning114", "model114 token114 prompt114", "session114"],
    ),
    (
        ("learning114 model114 token114 prompt114 session114 library114", 6),
        ["learning114", "model114", "token114", "prompt114", "session114", "library114"],
    ),
    (
        ("learning114 model114 token114 prompt114 session114 library114", 10),
        ["learning114", "model114", "token114", "prompt114", "session114", "library114"],
    ),
    (
        ("learning114 model114 token114 prompt114 session114 library114", 18),
        ["learning114", "model114 token114", "prompt114", "session114", "library114"],
    ),
    (
        ("learning114 model114 token114 prompt114 session114 library114", 28),
        ["learning114 model114", "token114 prompt114", "session114 library114"],
    ),
    (
        ("model114 token114 prompt114 session114 library114 service114", 6),
        ["model114", "token114", "prompt114", "session114", "library114", "service114"],
    ),
    (
        ("model114 token114 prompt114 session114 library114 service114", 10),
        ["model114", "token114", "prompt114", "session114", "library114", "service114"],
    ),
    (
        ("model114 token114 prompt114 session114 library114 service114", 18),
        ["model114 token114", "prompt114", "session114", "library114", "service114"],
    ),
    (
        ("model114 token114 prompt114 session114 library114 service114", 28),
        ["model114 token114 prompt114", "session114 library114", "service114"],
    ),
    (
        ("token114 prompt114 session114 library114 service114 gateway114", 6),
        ["token114", "prompt114", "session114", "library114", "service114", "gateway114"],
    ),
    (
        ("token114 prompt114 session114 library114 service114 gateway114", 10),
        ["token114", "prompt114", "session114", "library114", "service114", "gateway114"],
    ),
    (
        ("token114 prompt114 session114 library114 service114 gateway114", 18),
        ["token114 prompt114", "session114", "library114", "service114", "gateway114"],
    ),
    (
        ("token114 prompt114 session114 library114 service114 gateway114", 28),
        ["token114 prompt114", "session114 library114", "service114 gateway114"],
    ),
    (
        ("prompt114 session114 library114 service114 gateway114 storage114", 6),
        ["prompt114", "session114", "library114", "service114", "gateway114", "storage114"],
    ),
    (
        ("prompt114 session114 library114 service114 gateway114 storage114", 10),
        ["prompt114", "session114", "library114", "service114", "gateway114", "storage114"],
    ),
    (
        ("prompt114 session114 library114 service114 gateway114 storage114", 18),
        ["prompt114", "session114", "library114", "service114", "gateway114", "storage114"],
    ),
    (
        ("prompt114 session114 library114 service114 gateway114 storage114", 28),
        ["prompt114 session114", "library114 service114", "gateway114 storage114"],
    ),
    (
        ("session114 library114 service114 gateway114 storage114 network114", 6),
        ["session114", "library114", "service114", "gateway114", "storage114", "network114"],
    ),
    (
        ("session114 library114 service114 gateway114 storage114 network114", 10),
        ["session114", "library114", "service114", "gateway114", "storage114", "network114"],
    ),
    (
        ("session114 library114 service114 gateway114 storage114 network114", 18),
        ["session114", "library114", "service114", "gateway114", "storage114", "network114"],
    ),
    (
        ("session114 library114 service114 gateway114 storage114 network114", 28),
        ["session114 library114", "service114 gateway114", "storage114 network114"],
    ),
    (
        ("library114 service114 gateway114 storage114 network114 latency114", 6),
        ["library114", "service114", "gateway114", "storage114", "network114", "latency114"],
    ),
    (
        ("library114 service114 gateway114 storage114 network114 latency114", 10),
        ["library114", "service114", "gateway114", "storage114", "network114", "latency114"],
    ),
    (
        ("library114 service114 gateway114 storage114 network114 latency114", 18),
        ["library114", "service114", "gateway114", "storage114", "network114", "latency114"],
    ),
    (
        ("library114 service114 gateway114 storage114 network114 latency114", 28),
        ["library114 service114", "gateway114 storage114", "network114 latency114"],
    ),
    (
        ("service114 gateway114 storage114 network114 latency114 buffer114", 6),
        ["service114", "gateway114", "storage114", "network114", "latency114", "buffer114"],
    ),
    (
        ("service114 gateway114 storage114 network114 latency114 buffer114", 10),
        ["service114", "gateway114", "storage114", "network114", "latency114", "buffer114"],
    ),
    (
        ("service114 gateway114 storage114 network114 latency114 buffer114", 18),
        ["service114", "gateway114", "storage114", "network114", "latency114", "buffer114"],
    ),
    (
        ("service114 gateway114 storage114 network114 latency114 buffer114", 28),
        ["service114 gateway114", "storage114 network114", "latency114 buffer114"],
    ),
    (
        ("gateway114 storage114 network114 latency114 buffer114 queue114", 6),
        ["gateway114", "storage114", "network114", "latency114", "buffer114", "queue114"],
    ),
    (
        ("gateway114 storage114 network114 latency114 buffer114 queue114", 10),
        ["gateway114", "storage114", "network114", "latency114", "buffer114", "queue114"],
    ),
    (
        ("gateway114 storage114 network114 latency114 buffer114 queue114", 18),
        ["gateway114", "storage114", "network114", "latency114", "buffer114 queue114"],
    ),
    (
        ("gateway114 storage114 network114 latency114 buffer114 queue114", 28),
        ["gateway114 storage114", "network114 latency114", "buffer114 queue114"],
    ),
    (
        ("storage114 network114 latency114 buffer114 queue114 worker114", 6),
        ["storage114", "network114", "latency114", "buffer114", "queue114", "worker114"],
    ),
    (
        ("storage114 network114 latency114 buffer114 queue114 worker114", 10),
        ["storage114", "network114", "latency114", "buffer114", "queue114", "worker114"],
    ),
    (
        ("storage114 network114 latency114 buffer114 queue114 worker114", 18),
        ["storage114", "network114", "latency114", "buffer114 queue114", "worker114"],
    ),
    (
        ("storage114 network114 latency114 buffer114 queue114 worker114", 28),
        ["storage114 network114", "latency114 buffer114", "queue114 worker114"],
    ),
    (
        ("network114 latency114 buffer114 queue114 worker114 kernel114", 6),
        ["network114", "latency114", "buffer114", "queue114", "worker114", "kernel114"],
    ),
    (
        ("network114 latency114 buffer114 queue114 worker114 kernel114", 10),
        ["network114", "latency114", "buffer114", "queue114", "worker114", "kernel114"],
    ),
    (
        ("network114 latency114 buffer114 queue114 worker114 kernel114", 18),
        ["network114", "latency114", "buffer114 queue114", "worker114", "kernel114"],
    ),
    (
        ("network114 latency114 buffer114 queue114 worker114 kernel114", 28),
        ["network114 latency114", "buffer114 queue114 worker114", "kernel114"],
    ),
    (
        ("latency114 buffer114 queue114 worker114 kernel114 signal114", 6),
        ["latency114", "buffer114", "queue114", "worker114", "kernel114", "signal114"],
    ),
    (
        ("latency114 buffer114 queue114 worker114 kernel114 signal114", 10),
        ["latency114", "buffer114", "queue114", "worker114", "kernel114", "signal114"],
    ),
    (
        ("latency114 buffer114 queue114 worker114 kernel114 signal114", 18),
        ["latency114", "buffer114 queue114", "worker114", "kernel114", "signal114"],
    ),
    (
        ("latency114 buffer114 queue114 worker114 kernel114 signal114", 28),
        ["latency114 buffer114", "queue114 worker114 kernel114", "signal114"],
    ),
    (
        ("buffer114 queue114 worker114 kernel114 signal114 packet114", 6),
        ["buffer114", "queue114", "worker114", "kernel114", "signal114", "packet114"],
    ),
    (
        ("buffer114 queue114 worker114 kernel114 signal114 packet114", 10),
        ["buffer114", "queue114", "worker114", "kernel114", "signal114", "packet114"],
    ),
    (
        ("buffer114 queue114 worker114 kernel114 signal114 packet114", 18),
        ["buffer114 queue114", "worker114", "kernel114", "signal114", "packet114"],
    ),
    (
        ("buffer114 queue114 worker114 kernel114 signal114 packet114", 28),
        ["buffer114 queue114 worker114", "kernel114 signal114", "packet114"],
    ),
    (
        ("queue114 worker114 kernel114 signal114 packet114 router114", 6),
        ["queue114", "worker114", "kernel114", "signal114", "packet114", "router114"],
    ),
    (
        ("queue114 worker114 kernel114 signal114 packet114 router114", 10),
        ["queue114", "worker114", "kernel114", "signal114", "packet114", "router114"],
    ),
    (
        ("queue114 worker114 kernel114 signal114 packet114 router114", 18),
        ["queue114 worker114", "kernel114", "signal114", "packet114", "router114"],
    ),
    (
        ("queue114 worker114 kernel114 signal114 packet114 router114", 28),
        ["queue114 worker114 kernel114", "signal114 packet114", "router114"],
    ),
    (
        ("worker114 kernel114 signal114 packet114 router114 cluster114", 6),
        ["worker114", "kernel114", "signal114", "packet114", "router114", "cluster114"],
    ),
    (
        ("worker114 kernel114 signal114 packet114 router114 cluster114", 10),
        ["worker114", "kernel114", "signal114", "packet114", "router114", "cluster114"],
    ),
    (
        ("worker114 kernel114 signal114 packet114 router114 cluster114", 18),
        ["worker114", "kernel114", "signal114", "packet114", "router114", "cluster114"],
    ),
    (
        ("worker114 kernel114 signal114 packet114 router114 cluster114", 28),
        ["worker114 kernel114", "signal114 packet114", "router114 cluster114"],
    ),
    (
        ("kernel114 signal114 packet114 router114 cluster114 mirror114", 6),
        ["kernel114", "signal114", "packet114", "router114", "cluster114", "mirror114"],
    ),
    (
        ("kernel114 signal114 packet114 router114 cluster114 mirror114", 10),
        ["kernel114", "signal114", "packet114", "router114", "cluster114", "mirror114"],
    ),
    (
        ("kernel114 signal114 packet114 router114 cluster114 mirror114", 18),
        ["kernel114", "signal114", "packet114", "router114", "cluster114", "mirror114"],
    ),
    (
        ("kernel114 signal114 packet114 router114 cluster114 mirror114", 28),
        ["kernel114 signal114", "packet114 router114", "cluster114 mirror114"],
    ),
    (
        ("signal114 packet114 router114 cluster114 mirror114 filter114", 6),
        ["signal114", "packet114", "router114", "cluster114", "mirror114", "filter114"],
    ),
    (
        ("signal114 packet114 router114 cluster114 mirror114 filter114", 10),
        ["signal114", "packet114", "router114", "cluster114", "mirror114", "filter114"],
    ),
    (
        ("signal114 packet114 router114 cluster114 mirror114 filter114", 18),
        ["signal114", "packet114", "router114", "cluster114", "mirror114", "filter114"],
    ),
    (
        ("signal114 packet114 router114 cluster114 mirror114 filter114", 28),
        ["signal114 packet114", "router114 cluster114", "mirror114 filter114"],
    ),
    (
        ("packet114 router114 cluster114 mirror114 filter114 ranking114", 6),
        ["packet114", "router114", "cluster114", "mirror114", "filter114", "ranking114"],
    ),
    (
        ("packet114 router114 cluster114 mirror114 filter114 ranking114", 10),
        ["packet114", "router114", "cluster114", "mirror114", "filter114", "ranking114"],
    ),
    (
        ("packet114 router114 cluster114 mirror114 filter114 ranking114", 18),
        ["packet114", "router114", "cluster114", "mirror114", "filter114", "ranking114"],
    ),
    (
        ("packet114 router114 cluster114 mirror114 filter114 ranking114", 28),
        ["packet114 router114", "cluster114 mirror114", "filter114 ranking114"],
    ),
    (
        ("router114 cluster114 mirror114 filter114 ranking114 encoding114", 6),
        ["router114", "cluster114", "mirror114", "filter114", "ranking114", "encoding114"],
    ),
    (
        ("router114 cluster114 mirror114 filter114 ranking114 encoding114", 10),
        ["router114", "cluster114", "mirror114", "filter114", "ranking114", "encoding114"],
    ),
    (
        ("router114 cluster114 mirror114 filter114 ranking114 encoding114", 18),
        ["router114", "cluster114", "mirror114", "filter114", "ranking114", "encoding114"],
    ),
    (
        ("router114 cluster114 mirror114 filter114 ranking114 encoding114", 28),
        ["router114 cluster114", "mirror114 filter114", "ranking114 encoding114"],
    ),
    (
        ("cluster114 mirror114 filter114 ranking114 encoding114 mapping114", 6),
        ["cluster114", "mirror114", "filter114", "ranking114", "encoding114", "mapping114"],
    ),
    (
        ("cluster114 mirror114 filter114 ranking114 encoding114 mapping114", 10),
        ["cluster114", "mirror114", "filter114", "ranking114", "encoding114", "mapping114"],
    ),
    (
        ("cluster114 mirror114 filter114 ranking114 encoding114 mapping114", 18),
        ["cluster114", "mirror114", "filter114", "ranking114", "encoding114", "mapping114"],
    ),
    (
        ("cluster114 mirror114 filter114 ranking114 encoding114 mapping114", 28),
        ["cluster114 mirror114", "filter114 ranking114", "encoding114 mapping114"],
    ),
    (
        ("mirror114 filter114 ranking114 encoding114 mapping114 record114", 6),
        ["mirror114", "filter114", "ranking114", "encoding114", "mapping114", "record114"],
    ),
    (
        ("mirror114 filter114 ranking114 encoding114 mapping114 record114", 10),
        ["mirror114", "filter114", "ranking114", "encoding114", "mapping114", "record114"],
    ),
    (
        ("mirror114 filter114 ranking114 encoding114 mapping114 record114", 18),
        ["mirror114", "filter114", "ranking114", "encoding114", "mapping114", "record114"],
    ),
    (
        ("mirror114 filter114 ranking114 encoding114 mapping114 record114", 28),
        ["mirror114 filter114", "ranking114 encoding114", "mapping114 record114"],
    ),
    (
        ("filter114 ranking114 encoding114 mapping114 record114 candle114", 6),
        ["filter114", "ranking114", "encoding114", "mapping114", "record114", "candle114"],
    ),
    (
        ("filter114 ranking114 encoding114 mapping114 record114 candle114", 10),
        ["filter114", "ranking114", "encoding114", "mapping114", "record114", "candle114"],
    ),
    (
        ("filter114 ranking114 encoding114 mapping114 record114 candle114", 18),
        ["filter114", "ranking114", "encoding114", "mapping114", "record114", "candle114"],
    ),
    (
        ("filter114 ranking114 encoding114 mapping114 record114 candle114", 28),
        ["filter114 ranking114", "encoding114 mapping114", "record114 candle114"],
    ),
    (
        ("ranking114 encoding114 mapping114 record114 candle114 thread114", 6),
        ["ranking114", "encoding114", "mapping114", "record114", "candle114", "thread114"],
    ),
    (
        ("ranking114 encoding114 mapping114 record114 candle114 thread114", 10),
        ["ranking114", "encoding114", "mapping114", "record114", "candle114", "thread114"],
    ),
    (
        ("ranking114 encoding114 mapping114 record114 candle114 thread114", 18),
        ["ranking114", "encoding114", "mapping114", "record114", "candle114", "thread114"],
    ),
    (
        ("ranking114 encoding114 mapping114 record114 candle114 thread114", 28),
        ["ranking114 encoding114", "mapping114 record114", "candle114 thread114"],
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
