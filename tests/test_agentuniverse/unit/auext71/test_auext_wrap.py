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
        ("round 71: the quick brown fox jumps over the lazy dog", 4),
        ["round", "71:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 71: the quick brown fox jumps over the lazy dog", 8),
        ["round", "71: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 71: the quick brown fox jumps over the lazy dog", 12),
        ["round 71:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 71: the quick brown fox jumps over the lazy dog", 16),
        ["round 71: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 71: the quick brown fox jumps over the lazy dog", 24),
        ["round 71: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 71: the quick brown fox jumps over the lazy dog", 32),
        ["round 71: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 71: agentuniverse is a framework for multi agents", 4),
        ["round", "71:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 71: agentuniverse is a framework for multi agents", 8),
        ["round", "71:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 71: agentuniverse is a framework for multi agents", 12),
        ["round 71:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 71: agentuniverse is a framework for multi agents", 16),
        ["round 71:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 71: agentuniverse is a framework for multi agents", 24),
        ["round 71: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 71: agentuniverse is a framework for multi agents", 32),
        ["round 71: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 71: knowledge stored as vectors enables retrieval", 4),
        ["round", "71:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 71: knowledge stored as vectors enables retrieval", 8),
        ["round", "71:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 71: knowledge stored as vectors enables retrieval", 12),
        ["round 71:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 71: knowledge stored as vectors enables retrieval", 16),
        ["round 71:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 71: knowledge stored as vectors enables retrieval", 24),
        ["round 71: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 71: knowledge stored as vectors enables retrieval", 32),
        ["round 71: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 71: the processor reads the record then stops", 4),
        ["round", "71:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 71: the processor reads the record then stops", 8),
        ["round", "71: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 71: the processor reads the record then stops", 12),
        ["round 71:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 71: the processor reads the record then stops", 16),
        ["round 71: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 71: the processor reads the record then stops", 24),
        ["round 71: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 71: the processor reads the record then stops", 32),
        ["round 71: the processor reads", "the record then stops"],
    ),
    (
        ("round 71: a worker pulls the next task from the queue", 4),
        ["round", "71:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 71: a worker pulls the next task from the queue", 8),
        ["round", "71: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 71: a worker pulls the next task from the queue", 12),
        ["round 71: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 71: a worker pulls the next task from the queue", 16),
        ["round 71: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 71: a worker pulls the next task from the queue", 24),
        ["round 71: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 71: a worker pulls the next task from the queue", 32),
        ["round 71: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 71: signals travel through the network layer", 4),
        ["round", "71:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 71: signals travel through the network layer", 8),
        ["round", "71:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 71: signals travel through the network layer", 12),
        ["round 71:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 71: signals travel through the network layer", 16),
        ["round 71:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 71: signals travel through the network layer", 24),
        ["round 71: signals travel", "through the network", "layer"],
    ),
    (
        ("round 71: signals travel through the network layer", 32),
        ["round 71: signals travel through", "the network layer"],
    ),
    (
        ("round 71: the gateway routes each request by policy", 4),
        ["round", "71:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 71: the gateway routes each request by policy", 8),
        ["round", "71: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 71: the gateway routes each request by policy", 12),
        ["round 71:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 71: the gateway routes each request by policy", 16),
        ["round 71: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 71: the gateway routes each request by policy", 24),
        ["round 71: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 71: the gateway routes each request by policy", 32),
        ["round 71: the gateway routes", "each request by policy"],
    ),
    (
        ("round 71: memory grows until the buffer is full", 4),
        ["round", "71:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 71: memory grows until the buffer is full", 8),
        ["round", "71:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 71: memory grows until the buffer is full", 12),
        ["round 71:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 71: memory grows until the buffer is full", 16),
        ["round 71: memory", "grows until the", "buffer is full"],
    ),
    (("round 71: memory grows until the buffer is full", 24), ["round 71: memory grows", "until the buffer is full"]),
    (("round 71: memory grows until the buffer is full", 32), ["round 71: memory grows until the", "buffer is full"]),
    (
        ("round 71: the cluster mirrors every packet twice", 4),
        ["round", "71:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 71: the cluster mirrors every packet twice", 8),
        ["round", "71: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 71: the cluster mirrors every packet twice", 12),
        ["round 71:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 71: the cluster mirrors every packet twice", 16),
        ["round 71: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 71: the cluster mirrors every packet twice", 24),
        ["round 71: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 71: the cluster mirrors every packet twice", 32), ["round 71: the cluster mirrors", "every packet twice"]),
    (
        ("round 71: ranking uses tokens learned from the corpus", 4),
        ["round", "71:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 71: ranking uses tokens learned from the corpus", 8),
        ["round", "71:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 71: ranking uses tokens learned from the corpus", 12),
        ["round 71:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 71: ranking uses tokens learned from the corpus", 16),
        ["round 71:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 71: ranking uses tokens learned from the corpus", 24),
        ["round 71: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 71: ranking uses tokens learned from the corpus", 32),
        ["round 71: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 71: a long session ends when the candle dies", 4),
        ["round", "71:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 71: a long session ends when the candle dies", 8),
        ["round", "71: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 71: a long session ends when the candle dies", 12),
        ["round 71: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 71: a long session ends when the candle dies", 16),
        ["round 71: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 71: a long session ends when the candle dies", 24),
        ["round 71: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 71: a long session ends when the candle dies", 32),
        ["round 71: a long session ends", "when the candle dies"],
    ),
    (
        ("round 71: encode the prompt then map the result", 4),
        ["round", "71:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 71: encode the prompt then map the result", 8),
        ["round", "71:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 71: encode the prompt then map the result", 12),
        ["round 71:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 71: encode the prompt then map the result", 16),
        ["round 71: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 71: encode the prompt then map the result", 24),
        ["round 71: encode the", "prompt then map the", "result"],
    ),
    (("round 71: encode the prompt then map the result", 32), ["round 71: encode the prompt then", "map the result"]),
    (
        ("round 71: the kernel wakes the worker at dawn", 4),
        ["round", "71:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 71: the kernel wakes the worker at dawn", 8),
        ["round", "71: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 71: the kernel wakes the worker at dawn", 12),
        ["round 71:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 71: the kernel wakes the worker at dawn", 16), ["round 71: the", "kernel wakes the", "worker at dawn"]),
    (("round 71: the kernel wakes the worker at dawn", 24), ["round 71: the kernel", "wakes the worker at dawn"]),
    (("round 71: the kernel wakes the worker at dawn", 32), ["round 71: the kernel wakes the", "worker at dawn"]),
    (
        ("round 71: service latency drops after the patch", 4),
        ["round", "71:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 71: service latency drops after the patch", 8),
        ["round", "71:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 71: service latency drops after the patch", 12),
        ["round 71:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 71: service latency drops after the patch", 16),
        ["round 71:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 71: service latency drops after the patch", 24),
        ["round 71: service", "latency drops after the", "patch"],
    ),
    (("round 71: service latency drops after the patch", 32), ["round 71: service latency drops", "after the patch"]),
    (
        ("round 71: the library caches every vector it sees", 4),
        ["round", "71:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 71: the library caches every vector it sees", 8),
        ["round", "71: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 71: the library caches every vector it sees", 12),
        ["round 71:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 71: the library caches every vector it sees", 16),
        ["round 71: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 71: the library caches every vector it sees", 24),
        ["round 71: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 71: the library caches every vector it sees", 32),
        ["round 71: the library caches", "every vector it sees"],
    ),
    (
        ("round 71: agents argue then the debate resolves", 4),
        ["round", "71:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 71: agents argue then the debate resolves", 8),
        ["round", "71:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 71: agents argue then the debate resolves", 12),
        ["round 71:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 71: agents argue then the debate resolves", 16),
        ["round 71: agents", "argue then the", "debate resolves"],
    ),
    (("round 71: agents argue then the debate resolves", 24), ["round 71: agents argue", "then the debate resolves"]),
    (("round 71: agents argue then the debate resolves", 32), ["round 71: agents argue then the", "debate resolves"]),
    (
        ("round 71: the filter keeps only strong matches", 4),
        ["round", "71:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 71: the filter keeps only strong matches", 8),
        ["round", "71: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 71: the filter keeps only strong matches", 12),
        ["round 71:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 71: the filter keeps only strong matches", 16),
        ["round 71: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 71: the filter keeps only strong matches", 24), ["round 71: the filter", "keeps only strong", "matches"]),
    (("round 71: the filter keeps only strong matches", 32), ["round 71: the filter keeps only", "strong matches"]),
    (
        ("round 71: the model answers with a short reply", 4),
        ["round", "71:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 71: the model answers with a short reply", 8),
        ["round", "71: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 71: the model answers with a short reply", 12),
        ["round 71:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 71: the model answers with a short reply", 16),
        ["round 71: the", "model answers", "with a short", "reply"],
    ),
    (("round 71: the model answers with a short reply", 24), ["round 71: the model", "answers with a short", "reply"]),
    (("round 71: the model answers with a short reply", 32), ["round 71: the model answers with", "a short reply"]),
    (
        ("round 71: the recorder stores the reasoning trace", 4),
        ["round", "71:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 71: the recorder stores the reasoning trace", 8),
        ["round", "71: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 71: the recorder stores the reasoning trace", 12),
        ["round 71:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 71: the recorder stores the reasoning trace", 16),
        ["round 71: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 71: the recorder stores the reasoning trace", 24),
        ["round 71: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 71: the recorder stores the reasoning trace", 32),
        ["round 71: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 71: the angel watches the processor run", 4),
        ["round", "71:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 71: the angel watches the processor run", 8),
        ["round", "71: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 71: the angel watches the processor run", 12),
        ["round 71:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 71: the angel watches the processor run", 16), ["round 71: the", "angel watches", "the processor", "run"]),
    (("round 71: the angel watches the processor run", 24), ["round 71: the angel", "watches the processor", "run"]),
    (("round 71: the angel watches the processor run", 32), ["round 71: the angel watches the", "processor run"]),
    (
        ("round 71: angle of the vector decides the match", 4),
        ["round", "71:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 71: angle of the vector decides the match", 8),
        ["round", "71:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 71: angle of the vector decides the match", 12),
        ["round 71:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 71: angle of the vector decides the match", 16),
        ["round 71: angle", "of the vector", "decides the", "match"],
    ),
    (("round 71: angle of the vector decides the match", 24), ["round 71: angle of the", "vector decides the match"]),
    (("round 71: angle of the vector decides the match", 32), ["round 71: angle of the vector", "decides the match"]),
    (
        ("round 71: the candle burns twice as long at night", 4),
        ["round", "71:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 71: the candle burns twice as long at night", 8),
        ["round", "71: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 71: the candle burns twice as long at night", 12),
        ["round 71:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 71: the candle burns twice as long at night", 16),
        ["round 71: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 71: the candle burns twice as long at night", 24),
        ["round 71: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 71: the candle burns twice as long at night", 32),
        ["round 71: the candle burns twice", "as long at night"],
    ),
    (
        ("round 71: a mirror of the universe in one line", 4),
        ["round", "71:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 71: a mirror of the universe in one line", 8),
        ["round", "71: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 71: a mirror of the universe in one line", 12),
        ["round 71: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 71: a mirror of the universe in one line", 16),
        ["round 71: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 71: a mirror of the universe in one line", 24), ["round 71: a mirror of", "the universe in one line"]),
    (("round 71: a mirror of the universe in one line", 32), ["round 71: a mirror of the", "universe in one line"]),
    (
        ("round 71: the queue drains before the storm", 4),
        ["round", "71:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 71: the queue drains before the storm", 8),
        ["round", "71: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 71: the queue drains before the storm", 12), ["round 71:", "the queue", "drains", "before the", "storm"]),
    (("round 71: the queue drains before the storm", 16), ["round 71: the", "queue drains", "before the storm"]),
    (("round 71: the queue drains before the storm", 24), ["round 71: the queue", "drains before the storm"]),
    (("round 71: the queue drains before the storm", 32), ["round 71: the queue drains", "before the storm"]),
    (
        ("kitten71 sitting71 agent71 angle71 universe71 memory71", 6),
        ["kitten71", "sitting71", "agent71", "angle71", "universe71", "memory71"],
    ),
    (
        ("kitten71 sitting71 agent71 angle71 universe71 memory71", 10),
        ["kitten71", "sitting71", "agent71", "angle71", "universe71", "memory71"],
    ),
    (
        ("kitten71 sitting71 agent71 angle71 universe71 memory71", 18),
        ["kitten71 sitting71", "agent71 angle71", "universe71", "memory71"],
    ),
    (
        ("kitten71 sitting71 agent71 angle71 universe71 memory71", 28),
        ["kitten71 sitting71 agent71", "angle71 universe71 memory71"],
    ),
    (
        ("sitting71 agent71 angle71 universe71 memory71 stream71", 6),
        ["sitting71", "agent71", "angle71", "universe71", "memory71", "stream71"],
    ),
    (
        ("sitting71 agent71 angle71 universe71 memory71 stream71", 10),
        ["sitting71", "agent71", "angle71", "universe71", "memory71", "stream71"],
    ),
    (
        ("sitting71 agent71 angle71 universe71 memory71 stream71", 18),
        ["sitting71 agent71", "angle71 universe71", "memory71 stream71"],
    ),
    (
        ("sitting71 agent71 angle71 universe71 memory71 stream71", 28),
        ["sitting71 agent71 angle71", "universe71 memory71 stream71"],
    ),
    (
        ("agent71 angle71 universe71 memory71 stream71 context71", 6),
        ["agent71", "angle71", "universe71", "memory71", "stream71", "context71"],
    ),
    (
        ("agent71 angle71 universe71 memory71 stream71 context71", 10),
        ["agent71", "angle71", "universe71", "memory71", "stream71", "context71"],
    ),
    (
        ("agent71 angle71 universe71 memory71 stream71 context71", 18),
        ["agent71 angle71", "universe71", "memory71 stream71", "context71"],
    ),
    (
        ("agent71 angle71 universe71 memory71 stream71 context71", 28),
        ["agent71 angle71 universe71", "memory71 stream71 context71"],
    ),
    (
        ("angle71 universe71 memory71 stream71 context71 knowledge71", 6),
        ["angle71", "universe71", "memory71", "stream71", "context71", "knowledge71"],
    ),
    (
        ("angle71 universe71 memory71 stream71 context71 knowledge71", 10),
        ["angle71", "universe71", "memory71", "stream71", "context71", "knowledge71"],
    ),
    (
        ("angle71 universe71 memory71 stream71 context71 knowledge71", 18),
        ["angle71 universe71", "memory71 stream71", "context71", "knowledge71"],
    ),
    (
        ("angle71 universe71 memory71 stream71 context71 knowledge71", 28),
        ["angle71 universe71 memory71", "stream71 context71", "knowledge71"],
    ),
    (
        ("universe71 memory71 stream71 context71 knowledge71 vector71", 6),
        ["universe71", "memory71", "stream71", "context71", "knowledge71", "vector71"],
    ),
    (
        ("universe71 memory71 stream71 context71 knowledge71 vector71", 10),
        ["universe71", "memory71", "stream71", "context71", "knowledge71", "vector71"],
    ),
    (
        ("universe71 memory71 stream71 context71 knowledge71 vector71", 18),
        ["universe71", "memory71 stream71", "context71", "knowledge71", "vector71"],
    ),
    (
        ("universe71 memory71 stream71 context71 knowledge71 vector71", 28),
        ["universe71 memory71 stream71", "context71 knowledge71", "vector71"],
    ),
    (
        ("memory71 stream71 context71 knowledge71 vector71 processor71", 6),
        ["memory71", "stream71", "context71", "knowledge71", "vector71", "processor71"],
    ),
    (
        ("memory71 stream71 context71 knowledge71 vector71 processor71", 10),
        ["memory71", "stream71", "context71", "knowledge71", "vector71", "processor71"],
    ),
    (
        ("memory71 stream71 context71 knowledge71 vector71 processor71", 18),
        ["memory71 stream71", "context71", "knowledge71", "vector71", "processor71"],
    ),
    (
        ("memory71 stream71 context71 knowledge71 vector71 processor71", 28),
        ["memory71 stream71 context71", "knowledge71 vector71", "processor71"],
    ),
    (
        ("stream71 context71 knowledge71 vector71 processor71 reasoning71", 6),
        ["stream71", "context71", "knowledge71", "vector71", "processor71", "reasoning71"],
    ),
    (
        ("stream71 context71 knowledge71 vector71 processor71 reasoning71", 10),
        ["stream71", "context71", "knowledge71", "vector71", "processor71", "reasoning71"],
    ),
    (
        ("stream71 context71 knowledge71 vector71 processor71 reasoning71", 18),
        ["stream71 context71", "knowledge71", "vector71", "processor71", "reasoning71"],
    ),
    (
        ("stream71 context71 knowledge71 vector71 processor71 reasoning71", 28),
        ["stream71 context71", "knowledge71 vector71", "processor71 reasoning71"],
    ),
    (
        ("context71 knowledge71 vector71 processor71 reasoning71 machine71", 6),
        ["context71", "knowledge71", "vector71", "processor71", "reasoning71", "machine71"],
    ),
    (
        ("context71 knowledge71 vector71 processor71 reasoning71 machine71", 10),
        ["context71", "knowledge71", "vector71", "processor71", "reasoning71", "machine71"],
    ),
    (
        ("context71 knowledge71 vector71 processor71 reasoning71 machine71", 18),
        ["context71", "knowledge71", "vector71", "processor71", "reasoning71", "machine71"],
    ),
    (
        ("context71 knowledge71 vector71 processor71 reasoning71 machine71", 28),
        ["context71 knowledge71", "vector71 processor71", "reasoning71 machine71"],
    ),
    (
        ("knowledge71 vector71 processor71 reasoning71 machine71 learning71", 6),
        ["knowledge71", "vector71", "processor71", "reasoning71", "machine71", "learning71"],
    ),
    (
        ("knowledge71 vector71 processor71 reasoning71 machine71 learning71", 10),
        ["knowledge71", "vector71", "processor71", "reasoning71", "machine71", "learning71"],
    ),
    (
        ("knowledge71 vector71 processor71 reasoning71 machine71 learning71", 18),
        ["knowledge71", "vector71", "processor71", "reasoning71", "machine71", "learning71"],
    ),
    (
        ("knowledge71 vector71 processor71 reasoning71 machine71 learning71", 28),
        ["knowledge71 vector71", "processor71 reasoning71", "machine71 learning71"],
    ),
    (
        ("vector71 processor71 reasoning71 machine71 learning71 model71", 6),
        ["vector71", "processor71", "reasoning71", "machine71", "learning71", "model71"],
    ),
    (
        ("vector71 processor71 reasoning71 machine71 learning71 model71", 10),
        ["vector71", "processor71", "reasoning71", "machine71", "learning71", "model71"],
    ),
    (
        ("vector71 processor71 reasoning71 machine71 learning71 model71", 18),
        ["vector71", "processor71", "reasoning71", "machine71", "learning71 model71"],
    ),
    (
        ("vector71 processor71 reasoning71 machine71 learning71 model71", 28),
        ["vector71 processor71", "reasoning71 machine71", "learning71 model71"],
    ),
    (
        ("processor71 reasoning71 machine71 learning71 model71 token71", 6),
        ["processor71", "reasoning71", "machine71", "learning71", "model71", "token71"],
    ),
    (
        ("processor71 reasoning71 machine71 learning71 model71 token71", 10),
        ["processor71", "reasoning71", "machine71", "learning71", "model71", "token71"],
    ),
    (
        ("processor71 reasoning71 machine71 learning71 model71 token71", 18),
        ["processor71", "reasoning71", "machine71", "learning71 model71", "token71"],
    ),
    (
        ("processor71 reasoning71 machine71 learning71 model71 token71", 28),
        ["processor71 reasoning71", "machine71 learning71 model71", "token71"],
    ),
    (
        ("reasoning71 machine71 learning71 model71 token71 prompt71", 6),
        ["reasoning71", "machine71", "learning71", "model71", "token71", "prompt71"],
    ),
    (
        ("reasoning71 machine71 learning71 model71 token71 prompt71", 10),
        ["reasoning71", "machine71", "learning71", "model71", "token71", "prompt71"],
    ),
    (
        ("reasoning71 machine71 learning71 model71 token71 prompt71", 18),
        ["reasoning71", "machine71", "learning71 model71", "token71 prompt71"],
    ),
    (
        ("reasoning71 machine71 learning71 model71 token71 prompt71", 28),
        ["reasoning71 machine71", "learning71 model71 token71", "prompt71"],
    ),
    (
        ("machine71 learning71 model71 token71 prompt71 session71", 6),
        ["machine71", "learning71", "model71", "token71", "prompt71", "session71"],
    ),
    (
        ("machine71 learning71 model71 token71 prompt71 session71", 10),
        ["machine71", "learning71", "model71", "token71", "prompt71", "session71"],
    ),
    (
        ("machine71 learning71 model71 token71 prompt71 session71", 18),
        ["machine71", "learning71 model71", "token71 prompt71", "session71"],
    ),
    (
        ("machine71 learning71 model71 token71 prompt71 session71", 28),
        ["machine71 learning71 model71", "token71 prompt71 session71"],
    ),
    (
        ("learning71 model71 token71 prompt71 session71 library71", 6),
        ["learning71", "model71", "token71", "prompt71", "session71", "library71"],
    ),
    (
        ("learning71 model71 token71 prompt71 session71 library71", 10),
        ["learning71", "model71", "token71", "prompt71", "session71", "library71"],
    ),
    (
        ("learning71 model71 token71 prompt71 session71 library71", 18),
        ["learning71 model71", "token71 prompt71", "session71", "library71"],
    ),
    (
        ("learning71 model71 token71 prompt71 session71 library71", 28),
        ["learning71 model71 token71", "prompt71 session71 library71"],
    ),
    (
        ("model71 token71 prompt71 session71 library71 service71", 6),
        ["model71", "token71", "prompt71", "session71", "library71", "service71"],
    ),
    (
        ("model71 token71 prompt71 session71 library71 service71", 10),
        ["model71", "token71", "prompt71", "session71", "library71", "service71"],
    ),
    (
        ("model71 token71 prompt71 session71 library71 service71", 18),
        ["model71 token71", "prompt71 session71", "library71", "service71"],
    ),
    (
        ("model71 token71 prompt71 session71 library71 service71", 28),
        ["model71 token71 prompt71", "session71 library71", "service71"],
    ),
    (
        ("token71 prompt71 session71 library71 service71 gateway71", 6),
        ["token71", "prompt71", "session71", "library71", "service71", "gateway71"],
    ),
    (
        ("token71 prompt71 session71 library71 service71 gateway71", 10),
        ["token71", "prompt71", "session71", "library71", "service71", "gateway71"],
    ),
    (
        ("token71 prompt71 session71 library71 service71 gateway71", 18),
        ["token71 prompt71", "session71", "library71", "service71", "gateway71"],
    ),
    (
        ("token71 prompt71 session71 library71 service71 gateway71", 28),
        ["token71 prompt71 session71", "library71 service71", "gateway71"],
    ),
    (
        ("prompt71 session71 library71 service71 gateway71 storage71", 6),
        ["prompt71", "session71", "library71", "service71", "gateway71", "storage71"],
    ),
    (
        ("prompt71 session71 library71 service71 gateway71 storage71", 10),
        ["prompt71", "session71", "library71", "service71", "gateway71", "storage71"],
    ),
    (
        ("prompt71 session71 library71 service71 gateway71 storage71", 18),
        ["prompt71 session71", "library71", "service71", "gateway71", "storage71"],
    ),
    (
        ("prompt71 session71 library71 service71 gateway71 storage71", 28),
        ["prompt71 session71 library71", "service71 gateway71", "storage71"],
    ),
    (
        ("session71 library71 service71 gateway71 storage71 network71", 6),
        ["session71", "library71", "service71", "gateway71", "storage71", "network71"],
    ),
    (
        ("session71 library71 service71 gateway71 storage71 network71", 10),
        ["session71", "library71", "service71", "gateway71", "storage71", "network71"],
    ),
    (
        ("session71 library71 service71 gateway71 storage71 network71", 18),
        ["session71", "library71", "service71", "gateway71", "storage71", "network71"],
    ),
    (
        ("session71 library71 service71 gateway71 storage71 network71", 28),
        ["session71 library71", "service71 gateway71", "storage71 network71"],
    ),
    (
        ("library71 service71 gateway71 storage71 network71 latency71", 6),
        ["library71", "service71", "gateway71", "storage71", "network71", "latency71"],
    ),
    (
        ("library71 service71 gateway71 storage71 network71 latency71", 10),
        ["library71", "service71", "gateway71", "storage71", "network71", "latency71"],
    ),
    (
        ("library71 service71 gateway71 storage71 network71 latency71", 18),
        ["library71", "service71", "gateway71", "storage71", "network71", "latency71"],
    ),
    (
        ("library71 service71 gateway71 storage71 network71 latency71", 28),
        ["library71 service71", "gateway71 storage71", "network71 latency71"],
    ),
    (
        ("service71 gateway71 storage71 network71 latency71 buffer71", 6),
        ["service71", "gateway71", "storage71", "network71", "latency71", "buffer71"],
    ),
    (
        ("service71 gateway71 storage71 network71 latency71 buffer71", 10),
        ["service71", "gateway71", "storage71", "network71", "latency71", "buffer71"],
    ),
    (
        ("service71 gateway71 storage71 network71 latency71 buffer71", 18),
        ["service71", "gateway71", "storage71", "network71", "latency71 buffer71"],
    ),
    (
        ("service71 gateway71 storage71 network71 latency71 buffer71", 28),
        ["service71 gateway71", "storage71 network71", "latency71 buffer71"],
    ),
    (
        ("gateway71 storage71 network71 latency71 buffer71 queue71", 6),
        ["gateway71", "storage71", "network71", "latency71", "buffer71", "queue71"],
    ),
    (
        ("gateway71 storage71 network71 latency71 buffer71 queue71", 10),
        ["gateway71", "storage71", "network71", "latency71", "buffer71", "queue71"],
    ),
    (
        ("gateway71 storage71 network71 latency71 buffer71 queue71", 18),
        ["gateway71", "storage71", "network71", "latency71 buffer71", "queue71"],
    ),
    (
        ("gateway71 storage71 network71 latency71 buffer71 queue71", 28),
        ["gateway71 storage71", "network71 latency71 buffer71", "queue71"],
    ),
    (
        ("storage71 network71 latency71 buffer71 queue71 worker71", 6),
        ["storage71", "network71", "latency71", "buffer71", "queue71", "worker71"],
    ),
    (
        ("storage71 network71 latency71 buffer71 queue71 worker71", 10),
        ["storage71", "network71", "latency71", "buffer71", "queue71", "worker71"],
    ),
    (
        ("storage71 network71 latency71 buffer71 queue71 worker71", 18),
        ["storage71", "network71", "latency71 buffer71", "queue71 worker71"],
    ),
    (
        ("storage71 network71 latency71 buffer71 queue71 worker71", 28),
        ["storage71 network71", "latency71 buffer71 queue71", "worker71"],
    ),
    (
        ("network71 latency71 buffer71 queue71 worker71 kernel71", 6),
        ["network71", "latency71", "buffer71", "queue71", "worker71", "kernel71"],
    ),
    (
        ("network71 latency71 buffer71 queue71 worker71 kernel71", 10),
        ["network71", "latency71", "buffer71", "queue71", "worker71", "kernel71"],
    ),
    (
        ("network71 latency71 buffer71 queue71 worker71 kernel71", 18),
        ["network71", "latency71 buffer71", "queue71 worker71", "kernel71"],
    ),
    (
        ("network71 latency71 buffer71 queue71 worker71 kernel71", 28),
        ["network71 latency71 buffer71", "queue71 worker71 kernel71"],
    ),
    (
        ("latency71 buffer71 queue71 worker71 kernel71 signal71", 6),
        ["latency71", "buffer71", "queue71", "worker71", "kernel71", "signal71"],
    ),
    (
        ("latency71 buffer71 queue71 worker71 kernel71 signal71", 10),
        ["latency71", "buffer71", "queue71", "worker71", "kernel71", "signal71"],
    ),
    (
        ("latency71 buffer71 queue71 worker71 kernel71 signal71", 18),
        ["latency71 buffer71", "queue71 worker71", "kernel71 signal71"],
    ),
    (
        ("latency71 buffer71 queue71 worker71 kernel71 signal71", 28),
        ["latency71 buffer71 queue71", "worker71 kernel71 signal71"],
    ),
    (
        ("buffer71 queue71 worker71 kernel71 signal71 packet71", 6),
        ["buffer71", "queue71", "worker71", "kernel71", "signal71", "packet71"],
    ),
    (
        ("buffer71 queue71 worker71 kernel71 signal71 packet71", 10),
        ["buffer71", "queue71", "worker71", "kernel71", "signal71", "packet71"],
    ),
    (
        ("buffer71 queue71 worker71 kernel71 signal71 packet71", 18),
        ["buffer71 queue71", "worker71 kernel71", "signal71 packet71"],
    ),
    (
        ("buffer71 queue71 worker71 kernel71 signal71 packet71", 28),
        ["buffer71 queue71 worker71", "kernel71 signal71 packet71"],
    ),
    (
        ("queue71 worker71 kernel71 signal71 packet71 router71", 6),
        ["queue71", "worker71", "kernel71", "signal71", "packet71", "router71"],
    ),
    (
        ("queue71 worker71 kernel71 signal71 packet71 router71", 10),
        ["queue71", "worker71", "kernel71", "signal71", "packet71", "router71"],
    ),
    (
        ("queue71 worker71 kernel71 signal71 packet71 router71", 18),
        ["queue71 worker71", "kernel71 signal71", "packet71 router71"],
    ),
    (
        ("queue71 worker71 kernel71 signal71 packet71 router71", 28),
        ["queue71 worker71 kernel71", "signal71 packet71 router71"],
    ),
    (
        ("worker71 kernel71 signal71 packet71 router71 cluster71", 6),
        ["worker71", "kernel71", "signal71", "packet71", "router71", "cluster71"],
    ),
    (
        ("worker71 kernel71 signal71 packet71 router71 cluster71", 10),
        ["worker71", "kernel71", "signal71", "packet71", "router71", "cluster71"],
    ),
    (
        ("worker71 kernel71 signal71 packet71 router71 cluster71", 18),
        ["worker71 kernel71", "signal71 packet71", "router71 cluster71"],
    ),
    (
        ("worker71 kernel71 signal71 packet71 router71 cluster71", 28),
        ["worker71 kernel71 signal71", "packet71 router71 cluster71"],
    ),
    (
        ("kernel71 signal71 packet71 router71 cluster71 mirror71", 6),
        ["kernel71", "signal71", "packet71", "router71", "cluster71", "mirror71"],
    ),
    (
        ("kernel71 signal71 packet71 router71 cluster71 mirror71", 10),
        ["kernel71", "signal71", "packet71", "router71", "cluster71", "mirror71"],
    ),
    (
        ("kernel71 signal71 packet71 router71 cluster71 mirror71", 18),
        ["kernel71 signal71", "packet71 router71", "cluster71 mirror71"],
    ),
    (
        ("kernel71 signal71 packet71 router71 cluster71 mirror71", 28),
        ["kernel71 signal71 packet71", "router71 cluster71 mirror71"],
    ),
    (
        ("signal71 packet71 router71 cluster71 mirror71 filter71", 6),
        ["signal71", "packet71", "router71", "cluster71", "mirror71", "filter71"],
    ),
    (
        ("signal71 packet71 router71 cluster71 mirror71 filter71", 10),
        ["signal71", "packet71", "router71", "cluster71", "mirror71", "filter71"],
    ),
    (
        ("signal71 packet71 router71 cluster71 mirror71 filter71", 18),
        ["signal71 packet71", "router71 cluster71", "mirror71 filter71"],
    ),
    (
        ("signal71 packet71 router71 cluster71 mirror71 filter71", 28),
        ["signal71 packet71 router71", "cluster71 mirror71 filter71"],
    ),
    (
        ("packet71 router71 cluster71 mirror71 filter71 ranking71", 6),
        ["packet71", "router71", "cluster71", "mirror71", "filter71", "ranking71"],
    ),
    (
        ("packet71 router71 cluster71 mirror71 filter71 ranking71", 10),
        ["packet71", "router71", "cluster71", "mirror71", "filter71", "ranking71"],
    ),
    (
        ("packet71 router71 cluster71 mirror71 filter71 ranking71", 18),
        ["packet71 router71", "cluster71 mirror71", "filter71 ranking71"],
    ),
    (
        ("packet71 router71 cluster71 mirror71 filter71 ranking71", 28),
        ["packet71 router71 cluster71", "mirror71 filter71 ranking71"],
    ),
    (
        ("router71 cluster71 mirror71 filter71 ranking71 encoding71", 6),
        ["router71", "cluster71", "mirror71", "filter71", "ranking71", "encoding71"],
    ),
    (
        ("router71 cluster71 mirror71 filter71 ranking71 encoding71", 10),
        ["router71", "cluster71", "mirror71", "filter71", "ranking71", "encoding71"],
    ),
    (
        ("router71 cluster71 mirror71 filter71 ranking71 encoding71", 18),
        ["router71 cluster71", "mirror71 filter71", "ranking71", "encoding71"],
    ),
    (
        ("router71 cluster71 mirror71 filter71 ranking71 encoding71", 28),
        ["router71 cluster71 mirror71", "filter71 ranking71", "encoding71"],
    ),
    (
        ("cluster71 mirror71 filter71 ranking71 encoding71 mapping71", 6),
        ["cluster71", "mirror71", "filter71", "ranking71", "encoding71", "mapping71"],
    ),
    (
        ("cluster71 mirror71 filter71 ranking71 encoding71 mapping71", 10),
        ["cluster71", "mirror71", "filter71", "ranking71", "encoding71", "mapping71"],
    ),
    (
        ("cluster71 mirror71 filter71 ranking71 encoding71 mapping71", 18),
        ["cluster71 mirror71", "filter71 ranking71", "encoding71", "mapping71"],
    ),
    (
        ("cluster71 mirror71 filter71 ranking71 encoding71 mapping71", 28),
        ["cluster71 mirror71 filter71", "ranking71 encoding71", "mapping71"],
    ),
    (
        ("mirror71 filter71 ranking71 encoding71 mapping71 record71", 6),
        ["mirror71", "filter71", "ranking71", "encoding71", "mapping71", "record71"],
    ),
    (
        ("mirror71 filter71 ranking71 encoding71 mapping71 record71", 10),
        ["mirror71", "filter71", "ranking71", "encoding71", "mapping71", "record71"],
    ),
    (
        ("mirror71 filter71 ranking71 encoding71 mapping71 record71", 18),
        ["mirror71 filter71", "ranking71", "encoding71", "mapping71 record71"],
    ),
    (
        ("mirror71 filter71 ranking71 encoding71 mapping71 record71", 28),
        ["mirror71 filter71 ranking71", "encoding71 mapping71", "record71"],
    ),
    (
        ("filter71 ranking71 encoding71 mapping71 record71 candle71", 6),
        ["filter71", "ranking71", "encoding71", "mapping71", "record71", "candle71"],
    ),
    (
        ("filter71 ranking71 encoding71 mapping71 record71 candle71", 10),
        ["filter71", "ranking71", "encoding71", "mapping71", "record71", "candle71"],
    ),
    (
        ("filter71 ranking71 encoding71 mapping71 record71 candle71", 18),
        ["filter71 ranking71", "encoding71", "mapping71 record71", "candle71"],
    ),
    (
        ("filter71 ranking71 encoding71 mapping71 record71 candle71", 28),
        ["filter71 ranking71", "encoding71 mapping71", "record71 candle71"],
    ),
    (
        ("ranking71 encoding71 mapping71 record71 candle71 thread71", 6),
        ["ranking71", "encoding71", "mapping71", "record71", "candle71", "thread71"],
    ),
    (
        ("ranking71 encoding71 mapping71 record71 candle71 thread71", 10),
        ["ranking71", "encoding71", "mapping71", "record71", "candle71", "thread71"],
    ),
    (
        ("ranking71 encoding71 mapping71 record71 candle71 thread71", 18),
        ["ranking71", "encoding71", "mapping71 record71", "candle71 thread71"],
    ),
    (
        ("ranking71 encoding71 mapping71 record71 candle71 thread71", 28),
        ["ranking71 encoding71", "mapping71 record71 candle71", "thread71"],
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
