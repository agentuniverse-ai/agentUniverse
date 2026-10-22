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
        ("round 94: the quick brown fox jumps over the lazy dog", 4),
        ["round", "94:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 94: the quick brown fox jumps over the lazy dog", 8),
        ["round", "94: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 94: the quick brown fox jumps over the lazy dog", 12),
        ["round 94:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 94: the quick brown fox jumps over the lazy dog", 16),
        ["round 94: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 94: the quick brown fox jumps over the lazy dog", 24),
        ["round 94: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 94: the quick brown fox jumps over the lazy dog", 32),
        ["round 94: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 94: agentuniverse is a framework for multi agents", 4),
        ["round", "94:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 94: agentuniverse is a framework for multi agents", 8),
        ["round", "94:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 94: agentuniverse is a framework for multi agents", 12),
        ["round 94:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 94: agentuniverse is a framework for multi agents", 16),
        ["round 94:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 94: agentuniverse is a framework for multi agents", 24),
        ["round 94: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 94: agentuniverse is a framework for multi agents", 32),
        ["round 94: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 94: knowledge stored as vectors enables retrieval", 4),
        ["round", "94:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 94: knowledge stored as vectors enables retrieval", 8),
        ["round", "94:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 94: knowledge stored as vectors enables retrieval", 12),
        ["round 94:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 94: knowledge stored as vectors enables retrieval", 16),
        ["round 94:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 94: knowledge stored as vectors enables retrieval", 24),
        ["round 94: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 94: knowledge stored as vectors enables retrieval", 32),
        ["round 94: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 94: the processor reads the record then stops", 4),
        ["round", "94:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 94: the processor reads the record then stops", 8),
        ["round", "94: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 94: the processor reads the record then stops", 12),
        ["round 94:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 94: the processor reads the record then stops", 16),
        ["round 94: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 94: the processor reads the record then stops", 24),
        ["round 94: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 94: the processor reads the record then stops", 32),
        ["round 94: the processor reads", "the record then stops"],
    ),
    (
        ("round 94: a worker pulls the next task from the queue", 4),
        ["round", "94:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 94: a worker pulls the next task from the queue", 8),
        ["round", "94: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 94: a worker pulls the next task from the queue", 12),
        ["round 94: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 94: a worker pulls the next task from the queue", 16),
        ["round 94: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 94: a worker pulls the next task from the queue", 24),
        ["round 94: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 94: a worker pulls the next task from the queue", 32),
        ["round 94: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 94: signals travel through the network layer", 4),
        ["round", "94:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 94: signals travel through the network layer", 8),
        ["round", "94:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 94: signals travel through the network layer", 12),
        ["round 94:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 94: signals travel through the network layer", 16),
        ["round 94:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 94: signals travel through the network layer", 24),
        ["round 94: signals travel", "through the network", "layer"],
    ),
    (
        ("round 94: signals travel through the network layer", 32),
        ["round 94: signals travel through", "the network layer"],
    ),
    (
        ("round 94: the gateway routes each request by policy", 4),
        ["round", "94:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 94: the gateway routes each request by policy", 8),
        ["round", "94: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 94: the gateway routes each request by policy", 12),
        ["round 94:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 94: the gateway routes each request by policy", 16),
        ["round 94: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 94: the gateway routes each request by policy", 24),
        ["round 94: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 94: the gateway routes each request by policy", 32),
        ["round 94: the gateway routes", "each request by policy"],
    ),
    (
        ("round 94: memory grows until the buffer is full", 4),
        ["round", "94:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 94: memory grows until the buffer is full", 8),
        ["round", "94:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 94: memory grows until the buffer is full", 12),
        ["round 94:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 94: memory grows until the buffer is full", 16),
        ["round 94: memory", "grows until the", "buffer is full"],
    ),
    (("round 94: memory grows until the buffer is full", 24), ["round 94: memory grows", "until the buffer is full"]),
    (("round 94: memory grows until the buffer is full", 32), ["round 94: memory grows until the", "buffer is full"]),
    (
        ("round 94: the cluster mirrors every packet twice", 4),
        ["round", "94:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 94: the cluster mirrors every packet twice", 8),
        ["round", "94: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 94: the cluster mirrors every packet twice", 12),
        ["round 94:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 94: the cluster mirrors every packet twice", 16),
        ["round 94: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 94: the cluster mirrors every packet twice", 24),
        ["round 94: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 94: the cluster mirrors every packet twice", 32), ["round 94: the cluster mirrors", "every packet twice"]),
    (
        ("round 94: ranking uses tokens learned from the corpus", 4),
        ["round", "94:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 94: ranking uses tokens learned from the corpus", 8),
        ["round", "94:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 94: ranking uses tokens learned from the corpus", 12),
        ["round 94:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 94: ranking uses tokens learned from the corpus", 16),
        ["round 94:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 94: ranking uses tokens learned from the corpus", 24),
        ["round 94: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 94: ranking uses tokens learned from the corpus", 32),
        ["round 94: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 94: a long session ends when the candle dies", 4),
        ["round", "94:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 94: a long session ends when the candle dies", 8),
        ["round", "94: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 94: a long session ends when the candle dies", 12),
        ["round 94: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 94: a long session ends when the candle dies", 16),
        ["round 94: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 94: a long session ends when the candle dies", 24),
        ["round 94: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 94: a long session ends when the candle dies", 32),
        ["round 94: a long session ends", "when the candle dies"],
    ),
    (
        ("round 94: encode the prompt then map the result", 4),
        ["round", "94:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 94: encode the prompt then map the result", 8),
        ["round", "94:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 94: encode the prompt then map the result", 12),
        ["round 94:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 94: encode the prompt then map the result", 16),
        ["round 94: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 94: encode the prompt then map the result", 24),
        ["round 94: encode the", "prompt then map the", "result"],
    ),
    (("round 94: encode the prompt then map the result", 32), ["round 94: encode the prompt then", "map the result"]),
    (
        ("round 94: the kernel wakes the worker at dawn", 4),
        ["round", "94:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 94: the kernel wakes the worker at dawn", 8),
        ["round", "94: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 94: the kernel wakes the worker at dawn", 12),
        ["round 94:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 94: the kernel wakes the worker at dawn", 16), ["round 94: the", "kernel wakes the", "worker at dawn"]),
    (("round 94: the kernel wakes the worker at dawn", 24), ["round 94: the kernel", "wakes the worker at dawn"]),
    (("round 94: the kernel wakes the worker at dawn", 32), ["round 94: the kernel wakes the", "worker at dawn"]),
    (
        ("round 94: service latency drops after the patch", 4),
        ["round", "94:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 94: service latency drops after the patch", 8),
        ["round", "94:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 94: service latency drops after the patch", 12),
        ["round 94:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 94: service latency drops after the patch", 16),
        ["round 94:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 94: service latency drops after the patch", 24),
        ["round 94: service", "latency drops after the", "patch"],
    ),
    (("round 94: service latency drops after the patch", 32), ["round 94: service latency drops", "after the patch"]),
    (
        ("round 94: the library caches every vector it sees", 4),
        ["round", "94:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 94: the library caches every vector it sees", 8),
        ["round", "94: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 94: the library caches every vector it sees", 12),
        ["round 94:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 94: the library caches every vector it sees", 16),
        ["round 94: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 94: the library caches every vector it sees", 24),
        ["round 94: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 94: the library caches every vector it sees", 32),
        ["round 94: the library caches", "every vector it sees"],
    ),
    (
        ("round 94: agents argue then the debate resolves", 4),
        ["round", "94:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 94: agents argue then the debate resolves", 8),
        ["round", "94:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 94: agents argue then the debate resolves", 12),
        ["round 94:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 94: agents argue then the debate resolves", 16),
        ["round 94: agents", "argue then the", "debate resolves"],
    ),
    (("round 94: agents argue then the debate resolves", 24), ["round 94: agents argue", "then the debate resolves"]),
    (("round 94: agents argue then the debate resolves", 32), ["round 94: agents argue then the", "debate resolves"]),
    (
        ("round 94: the filter keeps only strong matches", 4),
        ["round", "94:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 94: the filter keeps only strong matches", 8),
        ["round", "94: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 94: the filter keeps only strong matches", 12),
        ["round 94:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 94: the filter keeps only strong matches", 16),
        ["round 94: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 94: the filter keeps only strong matches", 24), ["round 94: the filter", "keeps only strong", "matches"]),
    (("round 94: the filter keeps only strong matches", 32), ["round 94: the filter keeps only", "strong matches"]),
    (
        ("round 94: the model answers with a short reply", 4),
        ["round", "94:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 94: the model answers with a short reply", 8),
        ["round", "94: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 94: the model answers with a short reply", 12),
        ["round 94:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 94: the model answers with a short reply", 16),
        ["round 94: the", "model answers", "with a short", "reply"],
    ),
    (("round 94: the model answers with a short reply", 24), ["round 94: the model", "answers with a short", "reply"]),
    (("round 94: the model answers with a short reply", 32), ["round 94: the model answers with", "a short reply"]),
    (
        ("round 94: the recorder stores the reasoning trace", 4),
        ["round", "94:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 94: the recorder stores the reasoning trace", 8),
        ["round", "94: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 94: the recorder stores the reasoning trace", 12),
        ["round 94:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 94: the recorder stores the reasoning trace", 16),
        ["round 94: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 94: the recorder stores the reasoning trace", 24),
        ["round 94: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 94: the recorder stores the reasoning trace", 32),
        ["round 94: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 94: the angel watches the processor run", 4),
        ["round", "94:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 94: the angel watches the processor run", 8),
        ["round", "94: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 94: the angel watches the processor run", 12),
        ["round 94:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 94: the angel watches the processor run", 16), ["round 94: the", "angel watches", "the processor", "run"]),
    (("round 94: the angel watches the processor run", 24), ["round 94: the angel", "watches the processor", "run"]),
    (("round 94: the angel watches the processor run", 32), ["round 94: the angel watches the", "processor run"]),
    (
        ("round 94: angle of the vector decides the match", 4),
        ["round", "94:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 94: angle of the vector decides the match", 8),
        ["round", "94:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 94: angle of the vector decides the match", 12),
        ["round 94:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 94: angle of the vector decides the match", 16),
        ["round 94: angle", "of the vector", "decides the", "match"],
    ),
    (("round 94: angle of the vector decides the match", 24), ["round 94: angle of the", "vector decides the match"]),
    (("round 94: angle of the vector decides the match", 32), ["round 94: angle of the vector", "decides the match"]),
    (
        ("round 94: the candle burns twice as long at night", 4),
        ["round", "94:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 94: the candle burns twice as long at night", 8),
        ["round", "94: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 94: the candle burns twice as long at night", 12),
        ["round 94:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 94: the candle burns twice as long at night", 16),
        ["round 94: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 94: the candle burns twice as long at night", 24),
        ["round 94: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 94: the candle burns twice as long at night", 32),
        ["round 94: the candle burns twice", "as long at night"],
    ),
    (
        ("round 94: a mirror of the universe in one line", 4),
        ["round", "94:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 94: a mirror of the universe in one line", 8),
        ["round", "94: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 94: a mirror of the universe in one line", 12),
        ["round 94: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 94: a mirror of the universe in one line", 16),
        ["round 94: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 94: a mirror of the universe in one line", 24), ["round 94: a mirror of", "the universe in one line"]),
    (("round 94: a mirror of the universe in one line", 32), ["round 94: a mirror of the", "universe in one line"]),
    (
        ("round 94: the queue drains before the storm", 4),
        ["round", "94:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 94: the queue drains before the storm", 8),
        ["round", "94: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 94: the queue drains before the storm", 12), ["round 94:", "the queue", "drains", "before the", "storm"]),
    (("round 94: the queue drains before the storm", 16), ["round 94: the", "queue drains", "before the storm"]),
    (("round 94: the queue drains before the storm", 24), ["round 94: the queue", "drains before the storm"]),
    (("round 94: the queue drains before the storm", 32), ["round 94: the queue drains", "before the storm"]),
    (
        ("kitten94 sitting94 agent94 angle94 universe94 memory94", 6),
        ["kitten94", "sitting94", "agent94", "angle94", "universe94", "memory94"],
    ),
    (
        ("kitten94 sitting94 agent94 angle94 universe94 memory94", 10),
        ["kitten94", "sitting94", "agent94", "angle94", "universe94", "memory94"],
    ),
    (
        ("kitten94 sitting94 agent94 angle94 universe94 memory94", 18),
        ["kitten94 sitting94", "agent94 angle94", "universe94", "memory94"],
    ),
    (
        ("kitten94 sitting94 agent94 angle94 universe94 memory94", 28),
        ["kitten94 sitting94 agent94", "angle94 universe94 memory94"],
    ),
    (
        ("sitting94 agent94 angle94 universe94 memory94 stream94", 6),
        ["sitting94", "agent94", "angle94", "universe94", "memory94", "stream94"],
    ),
    (
        ("sitting94 agent94 angle94 universe94 memory94 stream94", 10),
        ["sitting94", "agent94", "angle94", "universe94", "memory94", "stream94"],
    ),
    (
        ("sitting94 agent94 angle94 universe94 memory94 stream94", 18),
        ["sitting94 agent94", "angle94 universe94", "memory94 stream94"],
    ),
    (
        ("sitting94 agent94 angle94 universe94 memory94 stream94", 28),
        ["sitting94 agent94 angle94", "universe94 memory94 stream94"],
    ),
    (
        ("agent94 angle94 universe94 memory94 stream94 context94", 6),
        ["agent94", "angle94", "universe94", "memory94", "stream94", "context94"],
    ),
    (
        ("agent94 angle94 universe94 memory94 stream94 context94", 10),
        ["agent94", "angle94", "universe94", "memory94", "stream94", "context94"],
    ),
    (
        ("agent94 angle94 universe94 memory94 stream94 context94", 18),
        ["agent94 angle94", "universe94", "memory94 stream94", "context94"],
    ),
    (
        ("agent94 angle94 universe94 memory94 stream94 context94", 28),
        ["agent94 angle94 universe94", "memory94 stream94 context94"],
    ),
    (
        ("angle94 universe94 memory94 stream94 context94 knowledge94", 6),
        ["angle94", "universe94", "memory94", "stream94", "context94", "knowledge94"],
    ),
    (
        ("angle94 universe94 memory94 stream94 context94 knowledge94", 10),
        ["angle94", "universe94", "memory94", "stream94", "context94", "knowledge94"],
    ),
    (
        ("angle94 universe94 memory94 stream94 context94 knowledge94", 18),
        ["angle94 universe94", "memory94 stream94", "context94", "knowledge94"],
    ),
    (
        ("angle94 universe94 memory94 stream94 context94 knowledge94", 28),
        ["angle94 universe94 memory94", "stream94 context94", "knowledge94"],
    ),
    (
        ("universe94 memory94 stream94 context94 knowledge94 vector94", 6),
        ["universe94", "memory94", "stream94", "context94", "knowledge94", "vector94"],
    ),
    (
        ("universe94 memory94 stream94 context94 knowledge94 vector94", 10),
        ["universe94", "memory94", "stream94", "context94", "knowledge94", "vector94"],
    ),
    (
        ("universe94 memory94 stream94 context94 knowledge94 vector94", 18),
        ["universe94", "memory94 stream94", "context94", "knowledge94", "vector94"],
    ),
    (
        ("universe94 memory94 stream94 context94 knowledge94 vector94", 28),
        ["universe94 memory94 stream94", "context94 knowledge94", "vector94"],
    ),
    (
        ("memory94 stream94 context94 knowledge94 vector94 processor94", 6),
        ["memory94", "stream94", "context94", "knowledge94", "vector94", "processor94"],
    ),
    (
        ("memory94 stream94 context94 knowledge94 vector94 processor94", 10),
        ["memory94", "stream94", "context94", "knowledge94", "vector94", "processor94"],
    ),
    (
        ("memory94 stream94 context94 knowledge94 vector94 processor94", 18),
        ["memory94 stream94", "context94", "knowledge94", "vector94", "processor94"],
    ),
    (
        ("memory94 stream94 context94 knowledge94 vector94 processor94", 28),
        ["memory94 stream94 context94", "knowledge94 vector94", "processor94"],
    ),
    (
        ("stream94 context94 knowledge94 vector94 processor94 reasoning94", 6),
        ["stream94", "context94", "knowledge94", "vector94", "processor94", "reasoning94"],
    ),
    (
        ("stream94 context94 knowledge94 vector94 processor94 reasoning94", 10),
        ["stream94", "context94", "knowledge94", "vector94", "processor94", "reasoning94"],
    ),
    (
        ("stream94 context94 knowledge94 vector94 processor94 reasoning94", 18),
        ["stream94 context94", "knowledge94", "vector94", "processor94", "reasoning94"],
    ),
    (
        ("stream94 context94 knowledge94 vector94 processor94 reasoning94", 28),
        ["stream94 context94", "knowledge94 vector94", "processor94 reasoning94"],
    ),
    (
        ("context94 knowledge94 vector94 processor94 reasoning94 machine94", 6),
        ["context94", "knowledge94", "vector94", "processor94", "reasoning94", "machine94"],
    ),
    (
        ("context94 knowledge94 vector94 processor94 reasoning94 machine94", 10),
        ["context94", "knowledge94", "vector94", "processor94", "reasoning94", "machine94"],
    ),
    (
        ("context94 knowledge94 vector94 processor94 reasoning94 machine94", 18),
        ["context94", "knowledge94", "vector94", "processor94", "reasoning94", "machine94"],
    ),
    (
        ("context94 knowledge94 vector94 processor94 reasoning94 machine94", 28),
        ["context94 knowledge94", "vector94 processor94", "reasoning94 machine94"],
    ),
    (
        ("knowledge94 vector94 processor94 reasoning94 machine94 learning94", 6),
        ["knowledge94", "vector94", "processor94", "reasoning94", "machine94", "learning94"],
    ),
    (
        ("knowledge94 vector94 processor94 reasoning94 machine94 learning94", 10),
        ["knowledge94", "vector94", "processor94", "reasoning94", "machine94", "learning94"],
    ),
    (
        ("knowledge94 vector94 processor94 reasoning94 machine94 learning94", 18),
        ["knowledge94", "vector94", "processor94", "reasoning94", "machine94", "learning94"],
    ),
    (
        ("knowledge94 vector94 processor94 reasoning94 machine94 learning94", 28),
        ["knowledge94 vector94", "processor94 reasoning94", "machine94 learning94"],
    ),
    (
        ("vector94 processor94 reasoning94 machine94 learning94 model94", 6),
        ["vector94", "processor94", "reasoning94", "machine94", "learning94", "model94"],
    ),
    (
        ("vector94 processor94 reasoning94 machine94 learning94 model94", 10),
        ["vector94", "processor94", "reasoning94", "machine94", "learning94", "model94"],
    ),
    (
        ("vector94 processor94 reasoning94 machine94 learning94 model94", 18),
        ["vector94", "processor94", "reasoning94", "machine94", "learning94 model94"],
    ),
    (
        ("vector94 processor94 reasoning94 machine94 learning94 model94", 28),
        ["vector94 processor94", "reasoning94 machine94", "learning94 model94"],
    ),
    (
        ("processor94 reasoning94 machine94 learning94 model94 token94", 6),
        ["processor94", "reasoning94", "machine94", "learning94", "model94", "token94"],
    ),
    (
        ("processor94 reasoning94 machine94 learning94 model94 token94", 10),
        ["processor94", "reasoning94", "machine94", "learning94", "model94", "token94"],
    ),
    (
        ("processor94 reasoning94 machine94 learning94 model94 token94", 18),
        ["processor94", "reasoning94", "machine94", "learning94 model94", "token94"],
    ),
    (
        ("processor94 reasoning94 machine94 learning94 model94 token94", 28),
        ["processor94 reasoning94", "machine94 learning94 model94", "token94"],
    ),
    (
        ("reasoning94 machine94 learning94 model94 token94 prompt94", 6),
        ["reasoning94", "machine94", "learning94", "model94", "token94", "prompt94"],
    ),
    (
        ("reasoning94 machine94 learning94 model94 token94 prompt94", 10),
        ["reasoning94", "machine94", "learning94", "model94", "token94", "prompt94"],
    ),
    (
        ("reasoning94 machine94 learning94 model94 token94 prompt94", 18),
        ["reasoning94", "machine94", "learning94 model94", "token94 prompt94"],
    ),
    (
        ("reasoning94 machine94 learning94 model94 token94 prompt94", 28),
        ["reasoning94 machine94", "learning94 model94 token94", "prompt94"],
    ),
    (
        ("machine94 learning94 model94 token94 prompt94 session94", 6),
        ["machine94", "learning94", "model94", "token94", "prompt94", "session94"],
    ),
    (
        ("machine94 learning94 model94 token94 prompt94 session94", 10),
        ["machine94", "learning94", "model94", "token94", "prompt94", "session94"],
    ),
    (
        ("machine94 learning94 model94 token94 prompt94 session94", 18),
        ["machine94", "learning94 model94", "token94 prompt94", "session94"],
    ),
    (
        ("machine94 learning94 model94 token94 prompt94 session94", 28),
        ["machine94 learning94 model94", "token94 prompt94 session94"],
    ),
    (
        ("learning94 model94 token94 prompt94 session94 library94", 6),
        ["learning94", "model94", "token94", "prompt94", "session94", "library94"],
    ),
    (
        ("learning94 model94 token94 prompt94 session94 library94", 10),
        ["learning94", "model94", "token94", "prompt94", "session94", "library94"],
    ),
    (
        ("learning94 model94 token94 prompt94 session94 library94", 18),
        ["learning94 model94", "token94 prompt94", "session94", "library94"],
    ),
    (
        ("learning94 model94 token94 prompt94 session94 library94", 28),
        ["learning94 model94 token94", "prompt94 session94 library94"],
    ),
    (
        ("model94 token94 prompt94 session94 library94 service94", 6),
        ["model94", "token94", "prompt94", "session94", "library94", "service94"],
    ),
    (
        ("model94 token94 prompt94 session94 library94 service94", 10),
        ["model94", "token94", "prompt94", "session94", "library94", "service94"],
    ),
    (
        ("model94 token94 prompt94 session94 library94 service94", 18),
        ["model94 token94", "prompt94 session94", "library94", "service94"],
    ),
    (
        ("model94 token94 prompt94 session94 library94 service94", 28),
        ["model94 token94 prompt94", "session94 library94", "service94"],
    ),
    (
        ("token94 prompt94 session94 library94 service94 gateway94", 6),
        ["token94", "prompt94", "session94", "library94", "service94", "gateway94"],
    ),
    (
        ("token94 prompt94 session94 library94 service94 gateway94", 10),
        ["token94", "prompt94", "session94", "library94", "service94", "gateway94"],
    ),
    (
        ("token94 prompt94 session94 library94 service94 gateway94", 18),
        ["token94 prompt94", "session94", "library94", "service94", "gateway94"],
    ),
    (
        ("token94 prompt94 session94 library94 service94 gateway94", 28),
        ["token94 prompt94 session94", "library94 service94", "gateway94"],
    ),
    (
        ("prompt94 session94 library94 service94 gateway94 storage94", 6),
        ["prompt94", "session94", "library94", "service94", "gateway94", "storage94"],
    ),
    (
        ("prompt94 session94 library94 service94 gateway94 storage94", 10),
        ["prompt94", "session94", "library94", "service94", "gateway94", "storage94"],
    ),
    (
        ("prompt94 session94 library94 service94 gateway94 storage94", 18),
        ["prompt94 session94", "library94", "service94", "gateway94", "storage94"],
    ),
    (
        ("prompt94 session94 library94 service94 gateway94 storage94", 28),
        ["prompt94 session94 library94", "service94 gateway94", "storage94"],
    ),
    (
        ("session94 library94 service94 gateway94 storage94 network94", 6),
        ["session94", "library94", "service94", "gateway94", "storage94", "network94"],
    ),
    (
        ("session94 library94 service94 gateway94 storage94 network94", 10),
        ["session94", "library94", "service94", "gateway94", "storage94", "network94"],
    ),
    (
        ("session94 library94 service94 gateway94 storage94 network94", 18),
        ["session94", "library94", "service94", "gateway94", "storage94", "network94"],
    ),
    (
        ("session94 library94 service94 gateway94 storage94 network94", 28),
        ["session94 library94", "service94 gateway94", "storage94 network94"],
    ),
    (
        ("library94 service94 gateway94 storage94 network94 latency94", 6),
        ["library94", "service94", "gateway94", "storage94", "network94", "latency94"],
    ),
    (
        ("library94 service94 gateway94 storage94 network94 latency94", 10),
        ["library94", "service94", "gateway94", "storage94", "network94", "latency94"],
    ),
    (
        ("library94 service94 gateway94 storage94 network94 latency94", 18),
        ["library94", "service94", "gateway94", "storage94", "network94", "latency94"],
    ),
    (
        ("library94 service94 gateway94 storage94 network94 latency94", 28),
        ["library94 service94", "gateway94 storage94", "network94 latency94"],
    ),
    (
        ("service94 gateway94 storage94 network94 latency94 buffer94", 6),
        ["service94", "gateway94", "storage94", "network94", "latency94", "buffer94"],
    ),
    (
        ("service94 gateway94 storage94 network94 latency94 buffer94", 10),
        ["service94", "gateway94", "storage94", "network94", "latency94", "buffer94"],
    ),
    (
        ("service94 gateway94 storage94 network94 latency94 buffer94", 18),
        ["service94", "gateway94", "storage94", "network94", "latency94 buffer94"],
    ),
    (
        ("service94 gateway94 storage94 network94 latency94 buffer94", 28),
        ["service94 gateway94", "storage94 network94", "latency94 buffer94"],
    ),
    (
        ("gateway94 storage94 network94 latency94 buffer94 queue94", 6),
        ["gateway94", "storage94", "network94", "latency94", "buffer94", "queue94"],
    ),
    (
        ("gateway94 storage94 network94 latency94 buffer94 queue94", 10),
        ["gateway94", "storage94", "network94", "latency94", "buffer94", "queue94"],
    ),
    (
        ("gateway94 storage94 network94 latency94 buffer94 queue94", 18),
        ["gateway94", "storage94", "network94", "latency94 buffer94", "queue94"],
    ),
    (
        ("gateway94 storage94 network94 latency94 buffer94 queue94", 28),
        ["gateway94 storage94", "network94 latency94 buffer94", "queue94"],
    ),
    (
        ("storage94 network94 latency94 buffer94 queue94 worker94", 6),
        ["storage94", "network94", "latency94", "buffer94", "queue94", "worker94"],
    ),
    (
        ("storage94 network94 latency94 buffer94 queue94 worker94", 10),
        ["storage94", "network94", "latency94", "buffer94", "queue94", "worker94"],
    ),
    (
        ("storage94 network94 latency94 buffer94 queue94 worker94", 18),
        ["storage94", "network94", "latency94 buffer94", "queue94 worker94"],
    ),
    (
        ("storage94 network94 latency94 buffer94 queue94 worker94", 28),
        ["storage94 network94", "latency94 buffer94 queue94", "worker94"],
    ),
    (
        ("network94 latency94 buffer94 queue94 worker94 kernel94", 6),
        ["network94", "latency94", "buffer94", "queue94", "worker94", "kernel94"],
    ),
    (
        ("network94 latency94 buffer94 queue94 worker94 kernel94", 10),
        ["network94", "latency94", "buffer94", "queue94", "worker94", "kernel94"],
    ),
    (
        ("network94 latency94 buffer94 queue94 worker94 kernel94", 18),
        ["network94", "latency94 buffer94", "queue94 worker94", "kernel94"],
    ),
    (
        ("network94 latency94 buffer94 queue94 worker94 kernel94", 28),
        ["network94 latency94 buffer94", "queue94 worker94 kernel94"],
    ),
    (
        ("latency94 buffer94 queue94 worker94 kernel94 signal94", 6),
        ["latency94", "buffer94", "queue94", "worker94", "kernel94", "signal94"],
    ),
    (
        ("latency94 buffer94 queue94 worker94 kernel94 signal94", 10),
        ["latency94", "buffer94", "queue94", "worker94", "kernel94", "signal94"],
    ),
    (
        ("latency94 buffer94 queue94 worker94 kernel94 signal94", 18),
        ["latency94 buffer94", "queue94 worker94", "kernel94 signal94"],
    ),
    (
        ("latency94 buffer94 queue94 worker94 kernel94 signal94", 28),
        ["latency94 buffer94 queue94", "worker94 kernel94 signal94"],
    ),
    (
        ("buffer94 queue94 worker94 kernel94 signal94 packet94", 6),
        ["buffer94", "queue94", "worker94", "kernel94", "signal94", "packet94"],
    ),
    (
        ("buffer94 queue94 worker94 kernel94 signal94 packet94", 10),
        ["buffer94", "queue94", "worker94", "kernel94", "signal94", "packet94"],
    ),
    (
        ("buffer94 queue94 worker94 kernel94 signal94 packet94", 18),
        ["buffer94 queue94", "worker94 kernel94", "signal94 packet94"],
    ),
    (
        ("buffer94 queue94 worker94 kernel94 signal94 packet94", 28),
        ["buffer94 queue94 worker94", "kernel94 signal94 packet94"],
    ),
    (
        ("queue94 worker94 kernel94 signal94 packet94 router94", 6),
        ["queue94", "worker94", "kernel94", "signal94", "packet94", "router94"],
    ),
    (
        ("queue94 worker94 kernel94 signal94 packet94 router94", 10),
        ["queue94", "worker94", "kernel94", "signal94", "packet94", "router94"],
    ),
    (
        ("queue94 worker94 kernel94 signal94 packet94 router94", 18),
        ["queue94 worker94", "kernel94 signal94", "packet94 router94"],
    ),
    (
        ("queue94 worker94 kernel94 signal94 packet94 router94", 28),
        ["queue94 worker94 kernel94", "signal94 packet94 router94"],
    ),
    (
        ("worker94 kernel94 signal94 packet94 router94 cluster94", 6),
        ["worker94", "kernel94", "signal94", "packet94", "router94", "cluster94"],
    ),
    (
        ("worker94 kernel94 signal94 packet94 router94 cluster94", 10),
        ["worker94", "kernel94", "signal94", "packet94", "router94", "cluster94"],
    ),
    (
        ("worker94 kernel94 signal94 packet94 router94 cluster94", 18),
        ["worker94 kernel94", "signal94 packet94", "router94 cluster94"],
    ),
    (
        ("worker94 kernel94 signal94 packet94 router94 cluster94", 28),
        ["worker94 kernel94 signal94", "packet94 router94 cluster94"],
    ),
    (
        ("kernel94 signal94 packet94 router94 cluster94 mirror94", 6),
        ["kernel94", "signal94", "packet94", "router94", "cluster94", "mirror94"],
    ),
    (
        ("kernel94 signal94 packet94 router94 cluster94 mirror94", 10),
        ["kernel94", "signal94", "packet94", "router94", "cluster94", "mirror94"],
    ),
    (
        ("kernel94 signal94 packet94 router94 cluster94 mirror94", 18),
        ["kernel94 signal94", "packet94 router94", "cluster94 mirror94"],
    ),
    (
        ("kernel94 signal94 packet94 router94 cluster94 mirror94", 28),
        ["kernel94 signal94 packet94", "router94 cluster94 mirror94"],
    ),
    (
        ("signal94 packet94 router94 cluster94 mirror94 filter94", 6),
        ["signal94", "packet94", "router94", "cluster94", "mirror94", "filter94"],
    ),
    (
        ("signal94 packet94 router94 cluster94 mirror94 filter94", 10),
        ["signal94", "packet94", "router94", "cluster94", "mirror94", "filter94"],
    ),
    (
        ("signal94 packet94 router94 cluster94 mirror94 filter94", 18),
        ["signal94 packet94", "router94 cluster94", "mirror94 filter94"],
    ),
    (
        ("signal94 packet94 router94 cluster94 mirror94 filter94", 28),
        ["signal94 packet94 router94", "cluster94 mirror94 filter94"],
    ),
    (
        ("packet94 router94 cluster94 mirror94 filter94 ranking94", 6),
        ["packet94", "router94", "cluster94", "mirror94", "filter94", "ranking94"],
    ),
    (
        ("packet94 router94 cluster94 mirror94 filter94 ranking94", 10),
        ["packet94", "router94", "cluster94", "mirror94", "filter94", "ranking94"],
    ),
    (
        ("packet94 router94 cluster94 mirror94 filter94 ranking94", 18),
        ["packet94 router94", "cluster94 mirror94", "filter94 ranking94"],
    ),
    (
        ("packet94 router94 cluster94 mirror94 filter94 ranking94", 28),
        ["packet94 router94 cluster94", "mirror94 filter94 ranking94"],
    ),
    (
        ("router94 cluster94 mirror94 filter94 ranking94 encoding94", 6),
        ["router94", "cluster94", "mirror94", "filter94", "ranking94", "encoding94"],
    ),
    (
        ("router94 cluster94 mirror94 filter94 ranking94 encoding94", 10),
        ["router94", "cluster94", "mirror94", "filter94", "ranking94", "encoding94"],
    ),
    (
        ("router94 cluster94 mirror94 filter94 ranking94 encoding94", 18),
        ["router94 cluster94", "mirror94 filter94", "ranking94", "encoding94"],
    ),
    (
        ("router94 cluster94 mirror94 filter94 ranking94 encoding94", 28),
        ["router94 cluster94 mirror94", "filter94 ranking94", "encoding94"],
    ),
    (
        ("cluster94 mirror94 filter94 ranking94 encoding94 mapping94", 6),
        ["cluster94", "mirror94", "filter94", "ranking94", "encoding94", "mapping94"],
    ),
    (
        ("cluster94 mirror94 filter94 ranking94 encoding94 mapping94", 10),
        ["cluster94", "mirror94", "filter94", "ranking94", "encoding94", "mapping94"],
    ),
    (
        ("cluster94 mirror94 filter94 ranking94 encoding94 mapping94", 18),
        ["cluster94 mirror94", "filter94 ranking94", "encoding94", "mapping94"],
    ),
    (
        ("cluster94 mirror94 filter94 ranking94 encoding94 mapping94", 28),
        ["cluster94 mirror94 filter94", "ranking94 encoding94", "mapping94"],
    ),
    (
        ("mirror94 filter94 ranking94 encoding94 mapping94 record94", 6),
        ["mirror94", "filter94", "ranking94", "encoding94", "mapping94", "record94"],
    ),
    (
        ("mirror94 filter94 ranking94 encoding94 mapping94 record94", 10),
        ["mirror94", "filter94", "ranking94", "encoding94", "mapping94", "record94"],
    ),
    (
        ("mirror94 filter94 ranking94 encoding94 mapping94 record94", 18),
        ["mirror94 filter94", "ranking94", "encoding94", "mapping94 record94"],
    ),
    (
        ("mirror94 filter94 ranking94 encoding94 mapping94 record94", 28),
        ["mirror94 filter94 ranking94", "encoding94 mapping94", "record94"],
    ),
    (
        ("filter94 ranking94 encoding94 mapping94 record94 candle94", 6),
        ["filter94", "ranking94", "encoding94", "mapping94", "record94", "candle94"],
    ),
    (
        ("filter94 ranking94 encoding94 mapping94 record94 candle94", 10),
        ["filter94", "ranking94", "encoding94", "mapping94", "record94", "candle94"],
    ),
    (
        ("filter94 ranking94 encoding94 mapping94 record94 candle94", 18),
        ["filter94 ranking94", "encoding94", "mapping94 record94", "candle94"],
    ),
    (
        ("filter94 ranking94 encoding94 mapping94 record94 candle94", 28),
        ["filter94 ranking94", "encoding94 mapping94", "record94 candle94"],
    ),
    (
        ("ranking94 encoding94 mapping94 record94 candle94 thread94", 6),
        ["ranking94", "encoding94", "mapping94", "record94", "candle94", "thread94"],
    ),
    (
        ("ranking94 encoding94 mapping94 record94 candle94 thread94", 10),
        ["ranking94", "encoding94", "mapping94", "record94", "candle94", "thread94"],
    ),
    (
        ("ranking94 encoding94 mapping94 record94 candle94 thread94", 18),
        ["ranking94", "encoding94", "mapping94 record94", "candle94 thread94"],
    ),
    (
        ("ranking94 encoding94 mapping94 record94 candle94 thread94", 28),
        ["ranking94 encoding94", "mapping94 record94 candle94", "thread94"],
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
