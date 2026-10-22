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
        ("round 179: the quick brown fox jumps over the lazy dog", 4),
        ["round", "179:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", 8),
        ["round", "179: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", 12),
        ["round 179:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", 16),
        ["round 179: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", 24),
        ["round 179: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 179: the quick brown fox jumps over the lazy dog", 32),
        ["round 179: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", 4),
        ["round", "179:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", 8),
        ["round", "179:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", 12),
        ["round 179:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", 16),
        ["round 179:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", 24),
        ["round 179: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 179: agentuniverse is a framework for multi agents", 32),
        ["round 179: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", 4),
        ["round", "179:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", 8),
        ["round", "179:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", 12),
        ["round 179:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", 16),
        ["round 179:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", 24),
        ["round 179: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 179: knowledge stored as vectors enables retrieval", 32),
        ["round 179: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 179: the processor reads the record then stops", 4),
        ["round", "179:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 179: the processor reads the record then stops", 8),
        ["round", "179: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 179: the processor reads the record then stops", 12),
        ["round 179:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 179: the processor reads the record then stops", 16),
        ["round 179: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 179: the processor reads the record then stops", 24),
        ["round 179: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 179: the processor reads the record then stops", 32),
        ["round 179: the processor reads", "the record then stops"],
    ),
    (
        ("round 179: a worker pulls the next task from the queue", 4),
        ["round", "179:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 179: a worker pulls the next task from the queue", 8),
        ["round", "179: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 179: a worker pulls the next task from the queue", 12),
        ["round 179: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 179: a worker pulls the next task from the queue", 16),
        ["round 179: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 179: a worker pulls the next task from the queue", 24),
        ["round 179: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 179: a worker pulls the next task from the queue", 32),
        ["round 179: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 179: signals travel through the network layer", 4),
        ["round", "179:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 179: signals travel through the network layer", 8),
        ["round", "179:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 179: signals travel through the network layer", 12),
        ["round 179:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 179: signals travel through the network layer", 16),
        ["round 179:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 179: signals travel through the network layer", 24),
        ["round 179: signals", "travel through the", "network layer"],
    ),
    (
        ("round 179: signals travel through the network layer", 32),
        ["round 179: signals travel", "through the network layer"],
    ),
    (
        ("round 179: the gateway routes each request by policy", 4),
        ["round", "179:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 179: the gateway routes each request by policy", 8),
        ["round", "179: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 179: the gateway routes each request by policy", 12),
        ["round 179:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 179: the gateway routes each request by policy", 16),
        ["round 179: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 179: the gateway routes each request by policy", 24),
        ["round 179: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 179: the gateway routes each request by policy", 32),
        ["round 179: the gateway routes", "each request by policy"],
    ),
    (
        ("round 179: memory grows until the buffer is full", 4),
        ["round", "179:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 179: memory grows until the buffer is full", 8),
        ["round", "179:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 179: memory grows until the buffer is full", 12),
        ["round 179:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 179: memory grows until the buffer is full", 16),
        ["round 179:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 179: memory grows until the buffer is full", 24), ["round 179: memory grows", "until the buffer is full"]),
    (("round 179: memory grows until the buffer is full", 32), ["round 179: memory grows until", "the buffer is full"]),
    (
        ("round 179: the cluster mirrors every packet twice", 4),
        ["round", "179:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 179: the cluster mirrors every packet twice", 8),
        ["round", "179: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 179: the cluster mirrors every packet twice", 12),
        ["round 179:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 179: the cluster mirrors every packet twice", 16),
        ["round 179: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 179: the cluster mirrors every packet twice", 24),
        ["round 179: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 179: the cluster mirrors every packet twice", 32),
        ["round 179: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", 4),
        ["round", "179:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", 8),
        ["round", "179:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", 12),
        ["round 179:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", 16),
        ["round 179:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", 24),
        ["round 179: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 179: ranking uses tokens learned from the corpus", 32),
        ["round 179: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 179: a long session ends when the candle dies", 4),
        ["round", "179:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 179: a long session ends when the candle dies", 8),
        ["round", "179: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 179: a long session ends when the candle dies", 12),
        ["round 179: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 179: a long session ends when the candle dies", 16),
        ["round 179: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 179: a long session ends when the candle dies", 24),
        ["round 179: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 179: a long session ends when the candle dies", 32),
        ["round 179: a long session ends", "when the candle dies"],
    ),
    (
        ("round 179: encode the prompt then map the result", 4),
        ["round", "179:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 179: encode the prompt then map the result", 8),
        ["round", "179:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 179: encode the prompt then map the result", 12),
        ["round 179:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 179: encode the prompt then map the result", 16),
        ["round 179:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 179: encode the prompt then map the result", 24),
        ["round 179: encode the", "prompt then map the", "result"],
    ),
    (("round 179: encode the prompt then map the result", 32), ["round 179: encode the prompt", "then map the result"]),
    (
        ("round 179: the kernel wakes the worker at dawn", 4),
        ["round", "179:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 179: the kernel wakes the worker at dawn", 8),
        ["round", "179: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 179: the kernel wakes the worker at dawn", 12),
        ["round 179:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 179: the kernel wakes the worker at dawn", 16), ["round 179: the", "kernel wakes the", "worker at dawn"]),
    (("round 179: the kernel wakes the worker at dawn", 24), ["round 179: the kernel", "wakes the worker at dawn"]),
    (("round 179: the kernel wakes the worker at dawn", 32), ["round 179: the kernel wakes the", "worker at dawn"]),
    (
        ("round 179: service latency drops after the patch", 4),
        ["round", "179:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 179: service latency drops after the patch", 8),
        ["round", "179:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 179: service latency drops after the patch", 12),
        ["round 179:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 179: service latency drops after the patch", 16),
        ["round 179:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 179: service latency drops after the patch", 24),
        ["round 179: service", "latency drops after the", "patch"],
    ),
    (("round 179: service latency drops after the patch", 32), ["round 179: service latency drops", "after the patch"]),
    (
        ("round 179: the library caches every vector it sees", 4),
        ["round", "179:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 179: the library caches every vector it sees", 8),
        ["round", "179: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 179: the library caches every vector it sees", 12),
        ["round 179:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 179: the library caches every vector it sees", 16),
        ["round 179: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 179: the library caches every vector it sees", 24),
        ["round 179: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 179: the library caches every vector it sees", 32),
        ["round 179: the library caches", "every vector it sees"],
    ),
    (
        ("round 179: agents argue then the debate resolves", 4),
        ["round", "179:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 179: agents argue then the debate resolves", 8),
        ["round", "179:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 179: agents argue then the debate resolves", 12),
        ["round 179:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 179: agents argue then the debate resolves", 16),
        ["round 179:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 179: agents argue then the debate resolves", 24), ["round 179: agents argue", "then the debate resolves"]),
    (("round 179: agents argue then the debate resolves", 32), ["round 179: agents argue then the", "debate resolves"]),
    (
        ("round 179: the filter keeps only strong matches", 4),
        ["round", "179:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 179: the filter keeps only strong matches", 8),
        ["round", "179: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 179: the filter keeps only strong matches", 12),
        ["round 179:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 179: the filter keeps only strong matches", 16),
        ["round 179: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 179: the filter keeps only strong matches", 24),
        ["round 179: the filter", "keeps only strong", "matches"],
    ),
    (("round 179: the filter keeps only strong matches", 32), ["round 179: the filter keeps only", "strong matches"]),
    (
        ("round 179: the model answers with a short reply", 4),
        ["round", "179:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 179: the model answers with a short reply", 8),
        ["round", "179: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 179: the model answers with a short reply", 12),
        ["round 179:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 179: the model answers with a short reply", 16),
        ["round 179: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 179: the model answers with a short reply", 24),
        ["round 179: the model", "answers with a short", "reply"],
    ),
    (("round 179: the model answers with a short reply", 32), ["round 179: the model answers", "with a short reply"]),
    (
        ("round 179: the recorder stores the reasoning trace", 4),
        ["round", "179:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 179: the recorder stores the reasoning trace", 8),
        ["round", "179: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 179: the recorder stores the reasoning trace", 12),
        ["round 179:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 179: the recorder stores the reasoning trace", 16),
        ["round 179: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 179: the recorder stores the reasoning trace", 24),
        ["round 179: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 179: the recorder stores the reasoning trace", 32),
        ["round 179: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 179: the angel watches the processor run", 4),
        ["round", "179:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 179: the angel watches the processor run", 8),
        ["round", "179: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 179: the angel watches the processor run", 12),
        ["round 179:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 179: the angel watches the processor run", 16),
        ["round 179: the", "angel watches", "the processor", "run"],
    ),
    (("round 179: the angel watches the processor run", 24), ["round 179: the angel", "watches the processor", "run"]),
    (("round 179: the angel watches the processor run", 32), ["round 179: the angel watches the", "processor run"]),
    (
        ("round 179: angle of the vector decides the match", 4),
        ["round", "179:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 179: angle of the vector decides the match", 8),
        ["round", "179:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 179: angle of the vector decides the match", 12),
        ["round 179:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 179: angle of the vector decides the match", 16),
        ["round 179: angle", "of the vector", "decides the", "match"],
    ),
    (("round 179: angle of the vector decides the match", 24), ["round 179: angle of the", "vector decides the match"]),
    (("round 179: angle of the vector decides the match", 32), ["round 179: angle of the vector", "decides the match"]),
    (
        ("round 179: the candle burns twice as long at night", 4),
        ["round", "179:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 179: the candle burns twice as long at night", 8),
        ["round", "179: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 179: the candle burns twice as long at night", 12),
        ["round 179:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 179: the candle burns twice as long at night", 16),
        ["round 179: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 179: the candle burns twice as long at night", 24),
        ["round 179: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 179: the candle burns twice as long at night", 32),
        ["round 179: the candle burns", "twice as long at night"],
    ),
    (
        ("round 179: a mirror of the universe in one line", 4),
        ["round", "179:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 179: a mirror of the universe in one line", 8),
        ["round", "179: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 179: a mirror of the universe in one line", 12),
        ["round 179: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 179: a mirror of the universe in one line", 16),
        ["round 179: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 179: a mirror of the universe in one line", 24), ["round 179: a mirror of", "the universe in one line"]),
    (("round 179: a mirror of the universe in one line", 32), ["round 179: a mirror of the", "universe in one line"]),
    (
        ("round 179: the queue drains before the storm", 4),
        ["round", "179:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 179: the queue drains before the storm", 8),
        ["round", "179: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 179: the queue drains before the storm", 12),
        ["round 179:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 179: the queue drains before the storm", 16), ["round 179: the", "queue drains", "before the storm"]),
    (("round 179: the queue drains before the storm", 24), ["round 179: the queue", "drains before the storm"]),
    (("round 179: the queue drains before the storm", 32), ["round 179: the queue drains", "before the storm"]),
    (
        ("kitten179 sitting179 agent179 angle179 universe179 memory179", 6),
        ["kitten179", "sitting179", "agent179", "angle179", "universe179", "memory179"],
    ),
    (
        ("kitten179 sitting179 agent179 angle179 universe179 memory179", 10),
        ["kitten179", "sitting179", "agent179", "angle179", "universe179", "memory179"],
    ),
    (
        ("kitten179 sitting179 agent179 angle179 universe179 memory179", 18),
        ["kitten179", "sitting179", "agent179 angle179", "universe179", "memory179"],
    ),
    (
        ("kitten179 sitting179 agent179 angle179 universe179 memory179", 28),
        ["kitten179 sitting179", "agent179 angle179", "universe179 memory179"],
    ),
    (
        ("sitting179 agent179 angle179 universe179 memory179 stream179", 6),
        ["sitting179", "agent179", "angle179", "universe179", "memory179", "stream179"],
    ),
    (
        ("sitting179 agent179 angle179 universe179 memory179 stream179", 10),
        ["sitting179", "agent179", "angle179", "universe179", "memory179", "stream179"],
    ),
    (
        ("sitting179 agent179 angle179 universe179 memory179 stream179", 18),
        ["sitting179", "agent179 angle179", "universe179", "memory179", "stream179"],
    ),
    (
        ("sitting179 agent179 angle179 universe179 memory179 stream179", 28),
        ["sitting179 agent179 angle179", "universe179 memory179", "stream179"],
    ),
    (
        ("agent179 angle179 universe179 memory179 stream179 context179", 6),
        ["agent179", "angle179", "universe179", "memory179", "stream179", "context179"],
    ),
    (
        ("agent179 angle179 universe179 memory179 stream179 context179", 10),
        ["agent179", "angle179", "universe179", "memory179", "stream179", "context179"],
    ),
    (
        ("agent179 angle179 universe179 memory179 stream179 context179", 18),
        ["agent179 angle179", "universe179", "memory179", "stream179", "context179"],
    ),
    (
        ("agent179 angle179 universe179 memory179 stream179 context179", 28),
        ["agent179 angle179", "universe179 memory179", "stream179 context179"],
    ),
    (
        ("angle179 universe179 memory179 stream179 context179 knowledge179", 6),
        ["angle179", "universe179", "memory179", "stream179", "context179", "knowledge179"],
    ),
    (
        ("angle179 universe179 memory179 stream179 context179 knowledge179", 10),
        ["angle179", "universe179", "memory179", "stream179", "context179", "knowledge179"],
    ),
    (
        ("angle179 universe179 memory179 stream179 context179 knowledge179", 18),
        ["angle179", "universe179", "memory179", "stream179", "context179", "knowledge179"],
    ),
    (
        ("angle179 universe179 memory179 stream179 context179 knowledge179", 28),
        ["angle179 universe179", "memory179 stream179", "context179 knowledge179"],
    ),
    (
        ("universe179 memory179 stream179 context179 knowledge179 vector179", 6),
        ["universe179", "memory179", "stream179", "context179", "knowledge179", "vector179"],
    ),
    (
        ("universe179 memory179 stream179 context179 knowledge179 vector179", 10),
        ["universe179", "memory179", "stream179", "context179", "knowledge179", "vector179"],
    ),
    (
        ("universe179 memory179 stream179 context179 knowledge179 vector179", 18),
        ["universe179", "memory179", "stream179", "context179", "knowledge179", "vector179"],
    ),
    (
        ("universe179 memory179 stream179 context179 knowledge179 vector179", 28),
        ["universe179 memory179", "stream179 context179", "knowledge179 vector179"],
    ),
    (
        ("memory179 stream179 context179 knowledge179 vector179 processor179", 6),
        ["memory179", "stream179", "context179", "knowledge179", "vector179", "processor179"],
    ),
    (
        ("memory179 stream179 context179 knowledge179 vector179 processor179", 10),
        ["memory179", "stream179", "context179", "knowledge179", "vector179", "processor179"],
    ),
    (
        ("memory179 stream179 context179 knowledge179 vector179 processor179", 18),
        ["memory179", "stream179", "context179", "knowledge179", "vector179", "processor179"],
    ),
    (
        ("memory179 stream179 context179 knowledge179 vector179 processor179", 28),
        ["memory179 stream179", "context179 knowledge179", "vector179 processor179"],
    ),
    (
        ("stream179 context179 knowledge179 vector179 processor179 reasoning179", 6),
        ["stream179", "context179", "knowledge179", "vector179", "processor179", "reasoning179"],
    ),
    (
        ("stream179 context179 knowledge179 vector179 processor179 reasoning179", 10),
        ["stream179", "context179", "knowledge179", "vector179", "processor179", "reasoning179"],
    ),
    (
        ("stream179 context179 knowledge179 vector179 processor179 reasoning179", 18),
        ["stream179", "context179", "knowledge179", "vector179", "processor179", "reasoning179"],
    ),
    (
        ("stream179 context179 knowledge179 vector179 processor179 reasoning179", 28),
        ["stream179 context179", "knowledge179 vector179", "processor179 reasoning179"],
    ),
    (
        ("context179 knowledge179 vector179 processor179 reasoning179 machine179", 6),
        ["context179", "knowledge179", "vector179", "processor179", "reasoning179", "machine179"],
    ),
    (
        ("context179 knowledge179 vector179 processor179 reasoning179 machine179", 10),
        ["context179", "knowledge179", "vector179", "processor179", "reasoning179", "machine179"],
    ),
    (
        ("context179 knowledge179 vector179 processor179 reasoning179 machine179", 18),
        ["context179", "knowledge179", "vector179", "processor179", "reasoning179", "machine179"],
    ),
    (
        ("context179 knowledge179 vector179 processor179 reasoning179 machine179", 28),
        ["context179 knowledge179", "vector179 processor179", "reasoning179 machine179"],
    ),
    (
        ("knowledge179 vector179 processor179 reasoning179 machine179 learning179", 6),
        ["knowledge179", "vector179", "processor179", "reasoning179", "machine179", "learning179"],
    ),
    (
        ("knowledge179 vector179 processor179 reasoning179 machine179 learning179", 10),
        ["knowledge179", "vector179", "processor179", "reasoning179", "machine179", "learning179"],
    ),
    (
        ("knowledge179 vector179 processor179 reasoning179 machine179 learning179", 18),
        ["knowledge179", "vector179", "processor179", "reasoning179", "machine179", "learning179"],
    ),
    (
        ("knowledge179 vector179 processor179 reasoning179 machine179 learning179", 28),
        ["knowledge179 vector179", "processor179 reasoning179", "machine179 learning179"],
    ),
    (
        ("vector179 processor179 reasoning179 machine179 learning179 model179", 6),
        ["vector179", "processor179", "reasoning179", "machine179", "learning179", "model179"],
    ),
    (
        ("vector179 processor179 reasoning179 machine179 learning179 model179", 10),
        ["vector179", "processor179", "reasoning179", "machine179", "learning179", "model179"],
    ),
    (
        ("vector179 processor179 reasoning179 machine179 learning179 model179", 18),
        ["vector179", "processor179", "reasoning179", "machine179", "learning179", "model179"],
    ),
    (
        ("vector179 processor179 reasoning179 machine179 learning179 model179", 28),
        ["vector179 processor179", "reasoning179 machine179", "learning179 model179"],
    ),
    (
        ("processor179 reasoning179 machine179 learning179 model179 token179", 6),
        ["processor179", "reasoning179", "machine179", "learning179", "model179", "token179"],
    ),
    (
        ("processor179 reasoning179 machine179 learning179 model179 token179", 10),
        ["processor179", "reasoning179", "machine179", "learning179", "model179", "token179"],
    ),
    (
        ("processor179 reasoning179 machine179 learning179 model179 token179", 18),
        ["processor179", "reasoning179", "machine179", "learning179", "model179 token179"],
    ),
    (
        ("processor179 reasoning179 machine179 learning179 model179 token179", 28),
        ["processor179 reasoning179", "machine179 learning179", "model179 token179"],
    ),
    (
        ("reasoning179 machine179 learning179 model179 token179 prompt179", 6),
        ["reasoning179", "machine179", "learning179", "model179", "token179", "prompt179"],
    ),
    (
        ("reasoning179 machine179 learning179 model179 token179 prompt179", 10),
        ["reasoning179", "machine179", "learning179", "model179", "token179", "prompt179"],
    ),
    (
        ("reasoning179 machine179 learning179 model179 token179 prompt179", 18),
        ["reasoning179", "machine179", "learning179", "model179 token179", "prompt179"],
    ),
    (
        ("reasoning179 machine179 learning179 model179 token179 prompt179", 28),
        ["reasoning179 machine179", "learning179 model179", "token179 prompt179"],
    ),
    (
        ("machine179 learning179 model179 token179 prompt179 session179", 6),
        ["machine179", "learning179", "model179", "token179", "prompt179", "session179"],
    ),
    (
        ("machine179 learning179 model179 token179 prompt179 session179", 10),
        ["machine179", "learning179", "model179", "token179", "prompt179", "session179"],
    ),
    (
        ("machine179 learning179 model179 token179 prompt179 session179", 18),
        ["machine179", "learning179", "model179 token179", "prompt179", "session179"],
    ),
    (
        ("machine179 learning179 model179 token179 prompt179 session179", 28),
        ["machine179 learning179", "model179 token179 prompt179", "session179"],
    ),
    (
        ("learning179 model179 token179 prompt179 session179 library179", 6),
        ["learning179", "model179", "token179", "prompt179", "session179", "library179"],
    ),
    (
        ("learning179 model179 token179 prompt179 session179 library179", 10),
        ["learning179", "model179", "token179", "prompt179", "session179", "library179"],
    ),
    (
        ("learning179 model179 token179 prompt179 session179 library179", 18),
        ["learning179", "model179 token179", "prompt179", "session179", "library179"],
    ),
    (
        ("learning179 model179 token179 prompt179 session179 library179", 28),
        ["learning179 model179", "token179 prompt179", "session179 library179"],
    ),
    (
        ("model179 token179 prompt179 session179 library179 service179", 6),
        ["model179", "token179", "prompt179", "session179", "library179", "service179"],
    ),
    (
        ("model179 token179 prompt179 session179 library179 service179", 10),
        ["model179", "token179", "prompt179", "session179", "library179", "service179"],
    ),
    (
        ("model179 token179 prompt179 session179 library179 service179", 18),
        ["model179 token179", "prompt179", "session179", "library179", "service179"],
    ),
    (
        ("model179 token179 prompt179 session179 library179 service179", 28),
        ["model179 token179 prompt179", "session179 library179", "service179"],
    ),
    (
        ("token179 prompt179 session179 library179 service179 gateway179", 6),
        ["token179", "prompt179", "session179", "library179", "service179", "gateway179"],
    ),
    (
        ("token179 prompt179 session179 library179 service179 gateway179", 10),
        ["token179", "prompt179", "session179", "library179", "service179", "gateway179"],
    ),
    (
        ("token179 prompt179 session179 library179 service179 gateway179", 18),
        ["token179 prompt179", "session179", "library179", "service179", "gateway179"],
    ),
    (
        ("token179 prompt179 session179 library179 service179 gateway179", 28),
        ["token179 prompt179", "session179 library179", "service179 gateway179"],
    ),
    (
        ("prompt179 session179 library179 service179 gateway179 storage179", 6),
        ["prompt179", "session179", "library179", "service179", "gateway179", "storage179"],
    ),
    (
        ("prompt179 session179 library179 service179 gateway179 storage179", 10),
        ["prompt179", "session179", "library179", "service179", "gateway179", "storage179"],
    ),
    (
        ("prompt179 session179 library179 service179 gateway179 storage179", 18),
        ["prompt179", "session179", "library179", "service179", "gateway179", "storage179"],
    ),
    (
        ("prompt179 session179 library179 service179 gateway179 storage179", 28),
        ["prompt179 session179", "library179 service179", "gateway179 storage179"],
    ),
    (
        ("session179 library179 service179 gateway179 storage179 network179", 6),
        ["session179", "library179", "service179", "gateway179", "storage179", "network179"],
    ),
    (
        ("session179 library179 service179 gateway179 storage179 network179", 10),
        ["session179", "library179", "service179", "gateway179", "storage179", "network179"],
    ),
    (
        ("session179 library179 service179 gateway179 storage179 network179", 18),
        ["session179", "library179", "service179", "gateway179", "storage179", "network179"],
    ),
    (
        ("session179 library179 service179 gateway179 storage179 network179", 28),
        ["session179 library179", "service179 gateway179", "storage179 network179"],
    ),
    (
        ("library179 service179 gateway179 storage179 network179 latency179", 6),
        ["library179", "service179", "gateway179", "storage179", "network179", "latency179"],
    ),
    (
        ("library179 service179 gateway179 storage179 network179 latency179", 10),
        ["library179", "service179", "gateway179", "storage179", "network179", "latency179"],
    ),
    (
        ("library179 service179 gateway179 storage179 network179 latency179", 18),
        ["library179", "service179", "gateway179", "storage179", "network179", "latency179"],
    ),
    (
        ("library179 service179 gateway179 storage179 network179 latency179", 28),
        ["library179 service179", "gateway179 storage179", "network179 latency179"],
    ),
    (
        ("service179 gateway179 storage179 network179 latency179 buffer179", 6),
        ["service179", "gateway179", "storage179", "network179", "latency179", "buffer179"],
    ),
    (
        ("service179 gateway179 storage179 network179 latency179 buffer179", 10),
        ["service179", "gateway179", "storage179", "network179", "latency179", "buffer179"],
    ),
    (
        ("service179 gateway179 storage179 network179 latency179 buffer179", 18),
        ["service179", "gateway179", "storage179", "network179", "latency179", "buffer179"],
    ),
    (
        ("service179 gateway179 storage179 network179 latency179 buffer179", 28),
        ["service179 gateway179", "storage179 network179", "latency179 buffer179"],
    ),
    (
        ("gateway179 storage179 network179 latency179 buffer179 queue179", 6),
        ["gateway179", "storage179", "network179", "latency179", "buffer179", "queue179"],
    ),
    (
        ("gateway179 storage179 network179 latency179 buffer179 queue179", 10),
        ["gateway179", "storage179", "network179", "latency179", "buffer179", "queue179"],
    ),
    (
        ("gateway179 storage179 network179 latency179 buffer179 queue179", 18),
        ["gateway179", "storage179", "network179", "latency179", "buffer179 queue179"],
    ),
    (
        ("gateway179 storage179 network179 latency179 buffer179 queue179", 28),
        ["gateway179 storage179", "network179 latency179", "buffer179 queue179"],
    ),
    (
        ("storage179 network179 latency179 buffer179 queue179 worker179", 6),
        ["storage179", "network179", "latency179", "buffer179", "queue179", "worker179"],
    ),
    (
        ("storage179 network179 latency179 buffer179 queue179 worker179", 10),
        ["storage179", "network179", "latency179", "buffer179", "queue179", "worker179"],
    ),
    (
        ("storage179 network179 latency179 buffer179 queue179 worker179", 18),
        ["storage179", "network179", "latency179", "buffer179 queue179", "worker179"],
    ),
    (
        ("storage179 network179 latency179 buffer179 queue179 worker179", 28),
        ["storage179 network179", "latency179 buffer179", "queue179 worker179"],
    ),
    (
        ("network179 latency179 buffer179 queue179 worker179 kernel179", 6),
        ["network179", "latency179", "buffer179", "queue179", "worker179", "kernel179"],
    ),
    (
        ("network179 latency179 buffer179 queue179 worker179 kernel179", 10),
        ["network179", "latency179", "buffer179", "queue179", "worker179", "kernel179"],
    ),
    (
        ("network179 latency179 buffer179 queue179 worker179 kernel179", 18),
        ["network179", "latency179", "buffer179 queue179", "worker179", "kernel179"],
    ),
    (
        ("network179 latency179 buffer179 queue179 worker179 kernel179", 28),
        ["network179 latency179", "buffer179 queue179 worker179", "kernel179"],
    ),
    (
        ("latency179 buffer179 queue179 worker179 kernel179 signal179", 6),
        ["latency179", "buffer179", "queue179", "worker179", "kernel179", "signal179"],
    ),
    (
        ("latency179 buffer179 queue179 worker179 kernel179 signal179", 10),
        ["latency179", "buffer179", "queue179", "worker179", "kernel179", "signal179"],
    ),
    (
        ("latency179 buffer179 queue179 worker179 kernel179 signal179", 18),
        ["latency179", "buffer179 queue179", "worker179", "kernel179", "signal179"],
    ),
    (
        ("latency179 buffer179 queue179 worker179 kernel179 signal179", 28),
        ["latency179 buffer179", "queue179 worker179 kernel179", "signal179"],
    ),
    (
        ("buffer179 queue179 worker179 kernel179 signal179 packet179", 6),
        ["buffer179", "queue179", "worker179", "kernel179", "signal179", "packet179"],
    ),
    (
        ("buffer179 queue179 worker179 kernel179 signal179 packet179", 10),
        ["buffer179", "queue179", "worker179", "kernel179", "signal179", "packet179"],
    ),
    (
        ("buffer179 queue179 worker179 kernel179 signal179 packet179", 18),
        ["buffer179 queue179", "worker179", "kernel179", "signal179", "packet179"],
    ),
    (
        ("buffer179 queue179 worker179 kernel179 signal179 packet179", 28),
        ["buffer179 queue179 worker179", "kernel179 signal179", "packet179"],
    ),
    (
        ("queue179 worker179 kernel179 signal179 packet179 router179", 6),
        ["queue179", "worker179", "kernel179", "signal179", "packet179", "router179"],
    ),
    (
        ("queue179 worker179 kernel179 signal179 packet179 router179", 10),
        ["queue179", "worker179", "kernel179", "signal179", "packet179", "router179"],
    ),
    (
        ("queue179 worker179 kernel179 signal179 packet179 router179", 18),
        ["queue179 worker179", "kernel179", "signal179", "packet179", "router179"],
    ),
    (
        ("queue179 worker179 kernel179 signal179 packet179 router179", 28),
        ["queue179 worker179 kernel179", "signal179 packet179", "router179"],
    ),
    (
        ("worker179 kernel179 signal179 packet179 router179 cluster179", 6),
        ["worker179", "kernel179", "signal179", "packet179", "router179", "cluster179"],
    ),
    (
        ("worker179 kernel179 signal179 packet179 router179 cluster179", 10),
        ["worker179", "kernel179", "signal179", "packet179", "router179", "cluster179"],
    ),
    (
        ("worker179 kernel179 signal179 packet179 router179 cluster179", 18),
        ["worker179", "kernel179", "signal179", "packet179", "router179", "cluster179"],
    ),
    (
        ("worker179 kernel179 signal179 packet179 router179 cluster179", 28),
        ["worker179 kernel179", "signal179 packet179", "router179 cluster179"],
    ),
    (
        ("kernel179 signal179 packet179 router179 cluster179 mirror179", 6),
        ["kernel179", "signal179", "packet179", "router179", "cluster179", "mirror179"],
    ),
    (
        ("kernel179 signal179 packet179 router179 cluster179 mirror179", 10),
        ["kernel179", "signal179", "packet179", "router179", "cluster179", "mirror179"],
    ),
    (
        ("kernel179 signal179 packet179 router179 cluster179 mirror179", 18),
        ["kernel179", "signal179", "packet179", "router179", "cluster179", "mirror179"],
    ),
    (
        ("kernel179 signal179 packet179 router179 cluster179 mirror179", 28),
        ["kernel179 signal179", "packet179 router179", "cluster179 mirror179"],
    ),
    (
        ("signal179 packet179 router179 cluster179 mirror179 filter179", 6),
        ["signal179", "packet179", "router179", "cluster179", "mirror179", "filter179"],
    ),
    (
        ("signal179 packet179 router179 cluster179 mirror179 filter179", 10),
        ["signal179", "packet179", "router179", "cluster179", "mirror179", "filter179"],
    ),
    (
        ("signal179 packet179 router179 cluster179 mirror179 filter179", 18),
        ["signal179", "packet179", "router179", "cluster179", "mirror179", "filter179"],
    ),
    (
        ("signal179 packet179 router179 cluster179 mirror179 filter179", 28),
        ["signal179 packet179", "router179 cluster179", "mirror179 filter179"],
    ),
    (
        ("packet179 router179 cluster179 mirror179 filter179 ranking179", 6),
        ["packet179", "router179", "cluster179", "mirror179", "filter179", "ranking179"],
    ),
    (
        ("packet179 router179 cluster179 mirror179 filter179 ranking179", 10),
        ["packet179", "router179", "cluster179", "mirror179", "filter179", "ranking179"],
    ),
    (
        ("packet179 router179 cluster179 mirror179 filter179 ranking179", 18),
        ["packet179", "router179", "cluster179", "mirror179", "filter179", "ranking179"],
    ),
    (
        ("packet179 router179 cluster179 mirror179 filter179 ranking179", 28),
        ["packet179 router179", "cluster179 mirror179", "filter179 ranking179"],
    ),
    (
        ("router179 cluster179 mirror179 filter179 ranking179 encoding179", 6),
        ["router179", "cluster179", "mirror179", "filter179", "ranking179", "encoding179"],
    ),
    (
        ("router179 cluster179 mirror179 filter179 ranking179 encoding179", 10),
        ["router179", "cluster179", "mirror179", "filter179", "ranking179", "encoding179"],
    ),
    (
        ("router179 cluster179 mirror179 filter179 ranking179 encoding179", 18),
        ["router179", "cluster179", "mirror179", "filter179", "ranking179", "encoding179"],
    ),
    (
        ("router179 cluster179 mirror179 filter179 ranking179 encoding179", 28),
        ["router179 cluster179", "mirror179 filter179", "ranking179 encoding179"],
    ),
    (
        ("cluster179 mirror179 filter179 ranking179 encoding179 mapping179", 6),
        ["cluster179", "mirror179", "filter179", "ranking179", "encoding179", "mapping179"],
    ),
    (
        ("cluster179 mirror179 filter179 ranking179 encoding179 mapping179", 10),
        ["cluster179", "mirror179", "filter179", "ranking179", "encoding179", "mapping179"],
    ),
    (
        ("cluster179 mirror179 filter179 ranking179 encoding179 mapping179", 18),
        ["cluster179", "mirror179", "filter179", "ranking179", "encoding179", "mapping179"],
    ),
    (
        ("cluster179 mirror179 filter179 ranking179 encoding179 mapping179", 28),
        ["cluster179 mirror179", "filter179 ranking179", "encoding179 mapping179"],
    ),
    (
        ("mirror179 filter179 ranking179 encoding179 mapping179 record179", 6),
        ["mirror179", "filter179", "ranking179", "encoding179", "mapping179", "record179"],
    ),
    (
        ("mirror179 filter179 ranking179 encoding179 mapping179 record179", 10),
        ["mirror179", "filter179", "ranking179", "encoding179", "mapping179", "record179"],
    ),
    (
        ("mirror179 filter179 ranking179 encoding179 mapping179 record179", 18),
        ["mirror179", "filter179", "ranking179", "encoding179", "mapping179", "record179"],
    ),
    (
        ("mirror179 filter179 ranking179 encoding179 mapping179 record179", 28),
        ["mirror179 filter179", "ranking179 encoding179", "mapping179 record179"],
    ),
    (
        ("filter179 ranking179 encoding179 mapping179 record179 candle179", 6),
        ["filter179", "ranking179", "encoding179", "mapping179", "record179", "candle179"],
    ),
    (
        ("filter179 ranking179 encoding179 mapping179 record179 candle179", 10),
        ["filter179", "ranking179", "encoding179", "mapping179", "record179", "candle179"],
    ),
    (
        ("filter179 ranking179 encoding179 mapping179 record179 candle179", 18),
        ["filter179", "ranking179", "encoding179", "mapping179", "record179", "candle179"],
    ),
    (
        ("filter179 ranking179 encoding179 mapping179 record179 candle179", 28),
        ["filter179 ranking179", "encoding179 mapping179", "record179 candle179"],
    ),
    (
        ("ranking179 encoding179 mapping179 record179 candle179 thread179", 6),
        ["ranking179", "encoding179", "mapping179", "record179", "candle179", "thread179"],
    ),
    (
        ("ranking179 encoding179 mapping179 record179 candle179 thread179", 10),
        ["ranking179", "encoding179", "mapping179", "record179", "candle179", "thread179"],
    ),
    (
        ("ranking179 encoding179 mapping179 record179 candle179 thread179", 18),
        ["ranking179", "encoding179", "mapping179", "record179", "candle179", "thread179"],
    ),
    (
        ("ranking179 encoding179 mapping179 record179 candle179 thread179", 28),
        ["ranking179 encoding179", "mapping179 record179", "candle179 thread179"],
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
