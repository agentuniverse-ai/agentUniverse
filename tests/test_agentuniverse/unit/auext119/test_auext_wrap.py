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
        ("round 119: the quick brown fox jumps over the lazy dog", 4),
        ["round", "119:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", 8),
        ["round", "119: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", 12),
        ["round 119:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", 16),
        ["round 119: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", 24),
        ["round 119: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 119: the quick brown fox jumps over the lazy dog", 32),
        ["round 119: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", 4),
        ["round", "119:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", 8),
        ["round", "119:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", 12),
        ["round 119:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", 16),
        ["round 119:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", 24),
        ["round 119: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 119: agentuniverse is a framework for multi agents", 32),
        ["round 119: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", 4),
        ["round", "119:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", 8),
        ["round", "119:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", 12),
        ["round 119:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", 16),
        ["round 119:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", 24),
        ["round 119: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 119: knowledge stored as vectors enables retrieval", 32),
        ["round 119: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 119: the processor reads the record then stops", 4),
        ["round", "119:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 119: the processor reads the record then stops", 8),
        ["round", "119: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 119: the processor reads the record then stops", 12),
        ["round 119:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 119: the processor reads the record then stops", 16),
        ["round 119: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 119: the processor reads the record then stops", 24),
        ["round 119: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 119: the processor reads the record then stops", 32),
        ["round 119: the processor reads", "the record then stops"],
    ),
    (
        ("round 119: a worker pulls the next task from the queue", 4),
        ["round", "119:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 119: a worker pulls the next task from the queue", 8),
        ["round", "119: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 119: a worker pulls the next task from the queue", 12),
        ["round 119: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 119: a worker pulls the next task from the queue", 16),
        ["round 119: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 119: a worker pulls the next task from the queue", 24),
        ["round 119: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 119: a worker pulls the next task from the queue", 32),
        ["round 119: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 119: signals travel through the network layer", 4),
        ["round", "119:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 119: signals travel through the network layer", 8),
        ["round", "119:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 119: signals travel through the network layer", 12),
        ["round 119:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 119: signals travel through the network layer", 16),
        ["round 119:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 119: signals travel through the network layer", 24),
        ["round 119: signals", "travel through the", "network layer"],
    ),
    (
        ("round 119: signals travel through the network layer", 32),
        ["round 119: signals travel", "through the network layer"],
    ),
    (
        ("round 119: the gateway routes each request by policy", 4),
        ["round", "119:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 119: the gateway routes each request by policy", 8),
        ["round", "119: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 119: the gateway routes each request by policy", 12),
        ["round 119:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 119: the gateway routes each request by policy", 16),
        ["round 119: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 119: the gateway routes each request by policy", 24),
        ["round 119: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 119: the gateway routes each request by policy", 32),
        ["round 119: the gateway routes", "each request by policy"],
    ),
    (
        ("round 119: memory grows until the buffer is full", 4),
        ["round", "119:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 119: memory grows until the buffer is full", 8),
        ["round", "119:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 119: memory grows until the buffer is full", 12),
        ["round 119:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 119: memory grows until the buffer is full", 16),
        ["round 119:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 119: memory grows until the buffer is full", 24), ["round 119: memory grows", "until the buffer is full"]),
    (("round 119: memory grows until the buffer is full", 32), ["round 119: memory grows until", "the buffer is full"]),
    (
        ("round 119: the cluster mirrors every packet twice", 4),
        ["round", "119:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 119: the cluster mirrors every packet twice", 8),
        ["round", "119: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 119: the cluster mirrors every packet twice", 12),
        ["round 119:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 119: the cluster mirrors every packet twice", 16),
        ["round 119: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 119: the cluster mirrors every packet twice", 24),
        ["round 119: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 119: the cluster mirrors every packet twice", 32),
        ["round 119: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", 4),
        ["round", "119:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", 8),
        ["round", "119:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", 12),
        ["round 119:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", 16),
        ["round 119:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", 24),
        ["round 119: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 119: ranking uses tokens learned from the corpus", 32),
        ["round 119: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 119: a long session ends when the candle dies", 4),
        ["round", "119:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 119: a long session ends when the candle dies", 8),
        ["round", "119: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 119: a long session ends when the candle dies", 12),
        ["round 119: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 119: a long session ends when the candle dies", 16),
        ["round 119: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 119: a long session ends when the candle dies", 24),
        ["round 119: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 119: a long session ends when the candle dies", 32),
        ["round 119: a long session ends", "when the candle dies"],
    ),
    (
        ("round 119: encode the prompt then map the result", 4),
        ["round", "119:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 119: encode the prompt then map the result", 8),
        ["round", "119:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 119: encode the prompt then map the result", 12),
        ["round 119:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 119: encode the prompt then map the result", 16),
        ["round 119:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 119: encode the prompt then map the result", 24),
        ["round 119: encode the", "prompt then map the", "result"],
    ),
    (("round 119: encode the prompt then map the result", 32), ["round 119: encode the prompt", "then map the result"]),
    (
        ("round 119: the kernel wakes the worker at dawn", 4),
        ["round", "119:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 119: the kernel wakes the worker at dawn", 8),
        ["round", "119: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 119: the kernel wakes the worker at dawn", 12),
        ["round 119:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 119: the kernel wakes the worker at dawn", 16), ["round 119: the", "kernel wakes the", "worker at dawn"]),
    (("round 119: the kernel wakes the worker at dawn", 24), ["round 119: the kernel", "wakes the worker at dawn"]),
    (("round 119: the kernel wakes the worker at dawn", 32), ["round 119: the kernel wakes the", "worker at dawn"]),
    (
        ("round 119: service latency drops after the patch", 4),
        ["round", "119:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 119: service latency drops after the patch", 8),
        ["round", "119:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 119: service latency drops after the patch", 12),
        ["round 119:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 119: service latency drops after the patch", 16),
        ["round 119:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 119: service latency drops after the patch", 24),
        ["round 119: service", "latency drops after the", "patch"],
    ),
    (("round 119: service latency drops after the patch", 32), ["round 119: service latency drops", "after the patch"]),
    (
        ("round 119: the library caches every vector it sees", 4),
        ["round", "119:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 119: the library caches every vector it sees", 8),
        ["round", "119: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 119: the library caches every vector it sees", 12),
        ["round 119:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 119: the library caches every vector it sees", 16),
        ["round 119: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 119: the library caches every vector it sees", 24),
        ["round 119: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 119: the library caches every vector it sees", 32),
        ["round 119: the library caches", "every vector it sees"],
    ),
    (
        ("round 119: agents argue then the debate resolves", 4),
        ["round", "119:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 119: agents argue then the debate resolves", 8),
        ["round", "119:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 119: agents argue then the debate resolves", 12),
        ["round 119:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 119: agents argue then the debate resolves", 16),
        ["round 119:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 119: agents argue then the debate resolves", 24), ["round 119: agents argue", "then the debate resolves"]),
    (("round 119: agents argue then the debate resolves", 32), ["round 119: agents argue then the", "debate resolves"]),
    (
        ("round 119: the filter keeps only strong matches", 4),
        ["round", "119:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 119: the filter keeps only strong matches", 8),
        ["round", "119: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 119: the filter keeps only strong matches", 12),
        ["round 119:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 119: the filter keeps only strong matches", 16),
        ["round 119: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 119: the filter keeps only strong matches", 24),
        ["round 119: the filter", "keeps only strong", "matches"],
    ),
    (("round 119: the filter keeps only strong matches", 32), ["round 119: the filter keeps only", "strong matches"]),
    (
        ("round 119: the model answers with a short reply", 4),
        ["round", "119:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 119: the model answers with a short reply", 8),
        ["round", "119: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 119: the model answers with a short reply", 12),
        ["round 119:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 119: the model answers with a short reply", 16),
        ["round 119: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 119: the model answers with a short reply", 24),
        ["round 119: the model", "answers with a short", "reply"],
    ),
    (("round 119: the model answers with a short reply", 32), ["round 119: the model answers", "with a short reply"]),
    (
        ("round 119: the recorder stores the reasoning trace", 4),
        ["round", "119:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 119: the recorder stores the reasoning trace", 8),
        ["round", "119: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 119: the recorder stores the reasoning trace", 12),
        ["round 119:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 119: the recorder stores the reasoning trace", 16),
        ["round 119: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 119: the recorder stores the reasoning trace", 24),
        ["round 119: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 119: the recorder stores the reasoning trace", 32),
        ["round 119: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 119: the angel watches the processor run", 4),
        ["round", "119:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 119: the angel watches the processor run", 8),
        ["round", "119: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 119: the angel watches the processor run", 12),
        ["round 119:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 119: the angel watches the processor run", 16),
        ["round 119: the", "angel watches", "the processor", "run"],
    ),
    (("round 119: the angel watches the processor run", 24), ["round 119: the angel", "watches the processor", "run"]),
    (("round 119: the angel watches the processor run", 32), ["round 119: the angel watches the", "processor run"]),
    (
        ("round 119: angle of the vector decides the match", 4),
        ["round", "119:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 119: angle of the vector decides the match", 8),
        ["round", "119:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 119: angle of the vector decides the match", 12),
        ["round 119:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 119: angle of the vector decides the match", 16),
        ["round 119: angle", "of the vector", "decides the", "match"],
    ),
    (("round 119: angle of the vector decides the match", 24), ["round 119: angle of the", "vector decides the match"]),
    (("round 119: angle of the vector decides the match", 32), ["round 119: angle of the vector", "decides the match"]),
    (
        ("round 119: the candle burns twice as long at night", 4),
        ["round", "119:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 119: the candle burns twice as long at night", 8),
        ["round", "119: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 119: the candle burns twice as long at night", 12),
        ["round 119:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 119: the candle burns twice as long at night", 16),
        ["round 119: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 119: the candle burns twice as long at night", 24),
        ["round 119: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 119: the candle burns twice as long at night", 32),
        ["round 119: the candle burns", "twice as long at night"],
    ),
    (
        ("round 119: a mirror of the universe in one line", 4),
        ["round", "119:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 119: a mirror of the universe in one line", 8),
        ["round", "119: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 119: a mirror of the universe in one line", 12),
        ["round 119: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 119: a mirror of the universe in one line", 16),
        ["round 119: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 119: a mirror of the universe in one line", 24), ["round 119: a mirror of", "the universe in one line"]),
    (("round 119: a mirror of the universe in one line", 32), ["round 119: a mirror of the", "universe in one line"]),
    (
        ("round 119: the queue drains before the storm", 4),
        ["round", "119:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 119: the queue drains before the storm", 8),
        ["round", "119: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 119: the queue drains before the storm", 12),
        ["round 119:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 119: the queue drains before the storm", 16), ["round 119: the", "queue drains", "before the storm"]),
    (("round 119: the queue drains before the storm", 24), ["round 119: the queue", "drains before the storm"]),
    (("round 119: the queue drains before the storm", 32), ["round 119: the queue drains", "before the storm"]),
    (
        ("kitten119 sitting119 agent119 angle119 universe119 memory119", 6),
        ["kitten119", "sitting119", "agent119", "angle119", "universe119", "memory119"],
    ),
    (
        ("kitten119 sitting119 agent119 angle119 universe119 memory119", 10),
        ["kitten119", "sitting119", "agent119", "angle119", "universe119", "memory119"],
    ),
    (
        ("kitten119 sitting119 agent119 angle119 universe119 memory119", 18),
        ["kitten119", "sitting119", "agent119 angle119", "universe119", "memory119"],
    ),
    (
        ("kitten119 sitting119 agent119 angle119 universe119 memory119", 28),
        ["kitten119 sitting119", "agent119 angle119", "universe119 memory119"],
    ),
    (
        ("sitting119 agent119 angle119 universe119 memory119 stream119", 6),
        ["sitting119", "agent119", "angle119", "universe119", "memory119", "stream119"],
    ),
    (
        ("sitting119 agent119 angle119 universe119 memory119 stream119", 10),
        ["sitting119", "agent119", "angle119", "universe119", "memory119", "stream119"],
    ),
    (
        ("sitting119 agent119 angle119 universe119 memory119 stream119", 18),
        ["sitting119", "agent119 angle119", "universe119", "memory119", "stream119"],
    ),
    (
        ("sitting119 agent119 angle119 universe119 memory119 stream119", 28),
        ["sitting119 agent119 angle119", "universe119 memory119", "stream119"],
    ),
    (
        ("agent119 angle119 universe119 memory119 stream119 context119", 6),
        ["agent119", "angle119", "universe119", "memory119", "stream119", "context119"],
    ),
    (
        ("agent119 angle119 universe119 memory119 stream119 context119", 10),
        ["agent119", "angle119", "universe119", "memory119", "stream119", "context119"],
    ),
    (
        ("agent119 angle119 universe119 memory119 stream119 context119", 18),
        ["agent119 angle119", "universe119", "memory119", "stream119", "context119"],
    ),
    (
        ("agent119 angle119 universe119 memory119 stream119 context119", 28),
        ["agent119 angle119", "universe119 memory119", "stream119 context119"],
    ),
    (
        ("angle119 universe119 memory119 stream119 context119 knowledge119", 6),
        ["angle119", "universe119", "memory119", "stream119", "context119", "knowledge119"],
    ),
    (
        ("angle119 universe119 memory119 stream119 context119 knowledge119", 10),
        ["angle119", "universe119", "memory119", "stream119", "context119", "knowledge119"],
    ),
    (
        ("angle119 universe119 memory119 stream119 context119 knowledge119", 18),
        ["angle119", "universe119", "memory119", "stream119", "context119", "knowledge119"],
    ),
    (
        ("angle119 universe119 memory119 stream119 context119 knowledge119", 28),
        ["angle119 universe119", "memory119 stream119", "context119 knowledge119"],
    ),
    (
        ("universe119 memory119 stream119 context119 knowledge119 vector119", 6),
        ["universe119", "memory119", "stream119", "context119", "knowledge119", "vector119"],
    ),
    (
        ("universe119 memory119 stream119 context119 knowledge119 vector119", 10),
        ["universe119", "memory119", "stream119", "context119", "knowledge119", "vector119"],
    ),
    (
        ("universe119 memory119 stream119 context119 knowledge119 vector119", 18),
        ["universe119", "memory119", "stream119", "context119", "knowledge119", "vector119"],
    ),
    (
        ("universe119 memory119 stream119 context119 knowledge119 vector119", 28),
        ["universe119 memory119", "stream119 context119", "knowledge119 vector119"],
    ),
    (
        ("memory119 stream119 context119 knowledge119 vector119 processor119", 6),
        ["memory119", "stream119", "context119", "knowledge119", "vector119", "processor119"],
    ),
    (
        ("memory119 stream119 context119 knowledge119 vector119 processor119", 10),
        ["memory119", "stream119", "context119", "knowledge119", "vector119", "processor119"],
    ),
    (
        ("memory119 stream119 context119 knowledge119 vector119 processor119", 18),
        ["memory119", "stream119", "context119", "knowledge119", "vector119", "processor119"],
    ),
    (
        ("memory119 stream119 context119 knowledge119 vector119 processor119", 28),
        ["memory119 stream119", "context119 knowledge119", "vector119 processor119"],
    ),
    (
        ("stream119 context119 knowledge119 vector119 processor119 reasoning119", 6),
        ["stream119", "context119", "knowledge119", "vector119", "processor119", "reasoning119"],
    ),
    (
        ("stream119 context119 knowledge119 vector119 processor119 reasoning119", 10),
        ["stream119", "context119", "knowledge119", "vector119", "processor119", "reasoning119"],
    ),
    (
        ("stream119 context119 knowledge119 vector119 processor119 reasoning119", 18),
        ["stream119", "context119", "knowledge119", "vector119", "processor119", "reasoning119"],
    ),
    (
        ("stream119 context119 knowledge119 vector119 processor119 reasoning119", 28),
        ["stream119 context119", "knowledge119 vector119", "processor119 reasoning119"],
    ),
    (
        ("context119 knowledge119 vector119 processor119 reasoning119 machine119", 6),
        ["context119", "knowledge119", "vector119", "processor119", "reasoning119", "machine119"],
    ),
    (
        ("context119 knowledge119 vector119 processor119 reasoning119 machine119", 10),
        ["context119", "knowledge119", "vector119", "processor119", "reasoning119", "machine119"],
    ),
    (
        ("context119 knowledge119 vector119 processor119 reasoning119 machine119", 18),
        ["context119", "knowledge119", "vector119", "processor119", "reasoning119", "machine119"],
    ),
    (
        ("context119 knowledge119 vector119 processor119 reasoning119 machine119", 28),
        ["context119 knowledge119", "vector119 processor119", "reasoning119 machine119"],
    ),
    (
        ("knowledge119 vector119 processor119 reasoning119 machine119 learning119", 6),
        ["knowledge119", "vector119", "processor119", "reasoning119", "machine119", "learning119"],
    ),
    (
        ("knowledge119 vector119 processor119 reasoning119 machine119 learning119", 10),
        ["knowledge119", "vector119", "processor119", "reasoning119", "machine119", "learning119"],
    ),
    (
        ("knowledge119 vector119 processor119 reasoning119 machine119 learning119", 18),
        ["knowledge119", "vector119", "processor119", "reasoning119", "machine119", "learning119"],
    ),
    (
        ("knowledge119 vector119 processor119 reasoning119 machine119 learning119", 28),
        ["knowledge119 vector119", "processor119 reasoning119", "machine119 learning119"],
    ),
    (
        ("vector119 processor119 reasoning119 machine119 learning119 model119", 6),
        ["vector119", "processor119", "reasoning119", "machine119", "learning119", "model119"],
    ),
    (
        ("vector119 processor119 reasoning119 machine119 learning119 model119", 10),
        ["vector119", "processor119", "reasoning119", "machine119", "learning119", "model119"],
    ),
    (
        ("vector119 processor119 reasoning119 machine119 learning119 model119", 18),
        ["vector119", "processor119", "reasoning119", "machine119", "learning119", "model119"],
    ),
    (
        ("vector119 processor119 reasoning119 machine119 learning119 model119", 28),
        ["vector119 processor119", "reasoning119 machine119", "learning119 model119"],
    ),
    (
        ("processor119 reasoning119 machine119 learning119 model119 token119", 6),
        ["processor119", "reasoning119", "machine119", "learning119", "model119", "token119"],
    ),
    (
        ("processor119 reasoning119 machine119 learning119 model119 token119", 10),
        ["processor119", "reasoning119", "machine119", "learning119", "model119", "token119"],
    ),
    (
        ("processor119 reasoning119 machine119 learning119 model119 token119", 18),
        ["processor119", "reasoning119", "machine119", "learning119", "model119 token119"],
    ),
    (
        ("processor119 reasoning119 machine119 learning119 model119 token119", 28),
        ["processor119 reasoning119", "machine119 learning119", "model119 token119"],
    ),
    (
        ("reasoning119 machine119 learning119 model119 token119 prompt119", 6),
        ["reasoning119", "machine119", "learning119", "model119", "token119", "prompt119"],
    ),
    (
        ("reasoning119 machine119 learning119 model119 token119 prompt119", 10),
        ["reasoning119", "machine119", "learning119", "model119", "token119", "prompt119"],
    ),
    (
        ("reasoning119 machine119 learning119 model119 token119 prompt119", 18),
        ["reasoning119", "machine119", "learning119", "model119 token119", "prompt119"],
    ),
    (
        ("reasoning119 machine119 learning119 model119 token119 prompt119", 28),
        ["reasoning119 machine119", "learning119 model119", "token119 prompt119"],
    ),
    (
        ("machine119 learning119 model119 token119 prompt119 session119", 6),
        ["machine119", "learning119", "model119", "token119", "prompt119", "session119"],
    ),
    (
        ("machine119 learning119 model119 token119 prompt119 session119", 10),
        ["machine119", "learning119", "model119", "token119", "prompt119", "session119"],
    ),
    (
        ("machine119 learning119 model119 token119 prompt119 session119", 18),
        ["machine119", "learning119", "model119 token119", "prompt119", "session119"],
    ),
    (
        ("machine119 learning119 model119 token119 prompt119 session119", 28),
        ["machine119 learning119", "model119 token119 prompt119", "session119"],
    ),
    (
        ("learning119 model119 token119 prompt119 session119 library119", 6),
        ["learning119", "model119", "token119", "prompt119", "session119", "library119"],
    ),
    (
        ("learning119 model119 token119 prompt119 session119 library119", 10),
        ["learning119", "model119", "token119", "prompt119", "session119", "library119"],
    ),
    (
        ("learning119 model119 token119 prompt119 session119 library119", 18),
        ["learning119", "model119 token119", "prompt119", "session119", "library119"],
    ),
    (
        ("learning119 model119 token119 prompt119 session119 library119", 28),
        ["learning119 model119", "token119 prompt119", "session119 library119"],
    ),
    (
        ("model119 token119 prompt119 session119 library119 service119", 6),
        ["model119", "token119", "prompt119", "session119", "library119", "service119"],
    ),
    (
        ("model119 token119 prompt119 session119 library119 service119", 10),
        ["model119", "token119", "prompt119", "session119", "library119", "service119"],
    ),
    (
        ("model119 token119 prompt119 session119 library119 service119", 18),
        ["model119 token119", "prompt119", "session119", "library119", "service119"],
    ),
    (
        ("model119 token119 prompt119 session119 library119 service119", 28),
        ["model119 token119 prompt119", "session119 library119", "service119"],
    ),
    (
        ("token119 prompt119 session119 library119 service119 gateway119", 6),
        ["token119", "prompt119", "session119", "library119", "service119", "gateway119"],
    ),
    (
        ("token119 prompt119 session119 library119 service119 gateway119", 10),
        ["token119", "prompt119", "session119", "library119", "service119", "gateway119"],
    ),
    (
        ("token119 prompt119 session119 library119 service119 gateway119", 18),
        ["token119 prompt119", "session119", "library119", "service119", "gateway119"],
    ),
    (
        ("token119 prompt119 session119 library119 service119 gateway119", 28),
        ["token119 prompt119", "session119 library119", "service119 gateway119"],
    ),
    (
        ("prompt119 session119 library119 service119 gateway119 storage119", 6),
        ["prompt119", "session119", "library119", "service119", "gateway119", "storage119"],
    ),
    (
        ("prompt119 session119 library119 service119 gateway119 storage119", 10),
        ["prompt119", "session119", "library119", "service119", "gateway119", "storage119"],
    ),
    (
        ("prompt119 session119 library119 service119 gateway119 storage119", 18),
        ["prompt119", "session119", "library119", "service119", "gateway119", "storage119"],
    ),
    (
        ("prompt119 session119 library119 service119 gateway119 storage119", 28),
        ["prompt119 session119", "library119 service119", "gateway119 storage119"],
    ),
    (
        ("session119 library119 service119 gateway119 storage119 network119", 6),
        ["session119", "library119", "service119", "gateway119", "storage119", "network119"],
    ),
    (
        ("session119 library119 service119 gateway119 storage119 network119", 10),
        ["session119", "library119", "service119", "gateway119", "storage119", "network119"],
    ),
    (
        ("session119 library119 service119 gateway119 storage119 network119", 18),
        ["session119", "library119", "service119", "gateway119", "storage119", "network119"],
    ),
    (
        ("session119 library119 service119 gateway119 storage119 network119", 28),
        ["session119 library119", "service119 gateway119", "storage119 network119"],
    ),
    (
        ("library119 service119 gateway119 storage119 network119 latency119", 6),
        ["library119", "service119", "gateway119", "storage119", "network119", "latency119"],
    ),
    (
        ("library119 service119 gateway119 storage119 network119 latency119", 10),
        ["library119", "service119", "gateway119", "storage119", "network119", "latency119"],
    ),
    (
        ("library119 service119 gateway119 storage119 network119 latency119", 18),
        ["library119", "service119", "gateway119", "storage119", "network119", "latency119"],
    ),
    (
        ("library119 service119 gateway119 storage119 network119 latency119", 28),
        ["library119 service119", "gateway119 storage119", "network119 latency119"],
    ),
    (
        ("service119 gateway119 storage119 network119 latency119 buffer119", 6),
        ["service119", "gateway119", "storage119", "network119", "latency119", "buffer119"],
    ),
    (
        ("service119 gateway119 storage119 network119 latency119 buffer119", 10),
        ["service119", "gateway119", "storage119", "network119", "latency119", "buffer119"],
    ),
    (
        ("service119 gateway119 storage119 network119 latency119 buffer119", 18),
        ["service119", "gateway119", "storage119", "network119", "latency119", "buffer119"],
    ),
    (
        ("service119 gateway119 storage119 network119 latency119 buffer119", 28),
        ["service119 gateway119", "storage119 network119", "latency119 buffer119"],
    ),
    (
        ("gateway119 storage119 network119 latency119 buffer119 queue119", 6),
        ["gateway119", "storage119", "network119", "latency119", "buffer119", "queue119"],
    ),
    (
        ("gateway119 storage119 network119 latency119 buffer119 queue119", 10),
        ["gateway119", "storage119", "network119", "latency119", "buffer119", "queue119"],
    ),
    (
        ("gateway119 storage119 network119 latency119 buffer119 queue119", 18),
        ["gateway119", "storage119", "network119", "latency119", "buffer119 queue119"],
    ),
    (
        ("gateway119 storage119 network119 latency119 buffer119 queue119", 28),
        ["gateway119 storage119", "network119 latency119", "buffer119 queue119"],
    ),
    (
        ("storage119 network119 latency119 buffer119 queue119 worker119", 6),
        ["storage119", "network119", "latency119", "buffer119", "queue119", "worker119"],
    ),
    (
        ("storage119 network119 latency119 buffer119 queue119 worker119", 10),
        ["storage119", "network119", "latency119", "buffer119", "queue119", "worker119"],
    ),
    (
        ("storage119 network119 latency119 buffer119 queue119 worker119", 18),
        ["storage119", "network119", "latency119", "buffer119 queue119", "worker119"],
    ),
    (
        ("storage119 network119 latency119 buffer119 queue119 worker119", 28),
        ["storage119 network119", "latency119 buffer119", "queue119 worker119"],
    ),
    (
        ("network119 latency119 buffer119 queue119 worker119 kernel119", 6),
        ["network119", "latency119", "buffer119", "queue119", "worker119", "kernel119"],
    ),
    (
        ("network119 latency119 buffer119 queue119 worker119 kernel119", 10),
        ["network119", "latency119", "buffer119", "queue119", "worker119", "kernel119"],
    ),
    (
        ("network119 latency119 buffer119 queue119 worker119 kernel119", 18),
        ["network119", "latency119", "buffer119 queue119", "worker119", "kernel119"],
    ),
    (
        ("network119 latency119 buffer119 queue119 worker119 kernel119", 28),
        ["network119 latency119", "buffer119 queue119 worker119", "kernel119"],
    ),
    (
        ("latency119 buffer119 queue119 worker119 kernel119 signal119", 6),
        ["latency119", "buffer119", "queue119", "worker119", "kernel119", "signal119"],
    ),
    (
        ("latency119 buffer119 queue119 worker119 kernel119 signal119", 10),
        ["latency119", "buffer119", "queue119", "worker119", "kernel119", "signal119"],
    ),
    (
        ("latency119 buffer119 queue119 worker119 kernel119 signal119", 18),
        ["latency119", "buffer119 queue119", "worker119", "kernel119", "signal119"],
    ),
    (
        ("latency119 buffer119 queue119 worker119 kernel119 signal119", 28),
        ["latency119 buffer119", "queue119 worker119 kernel119", "signal119"],
    ),
    (
        ("buffer119 queue119 worker119 kernel119 signal119 packet119", 6),
        ["buffer119", "queue119", "worker119", "kernel119", "signal119", "packet119"],
    ),
    (
        ("buffer119 queue119 worker119 kernel119 signal119 packet119", 10),
        ["buffer119", "queue119", "worker119", "kernel119", "signal119", "packet119"],
    ),
    (
        ("buffer119 queue119 worker119 kernel119 signal119 packet119", 18),
        ["buffer119 queue119", "worker119", "kernel119", "signal119", "packet119"],
    ),
    (
        ("buffer119 queue119 worker119 kernel119 signal119 packet119", 28),
        ["buffer119 queue119 worker119", "kernel119 signal119", "packet119"],
    ),
    (
        ("queue119 worker119 kernel119 signal119 packet119 router119", 6),
        ["queue119", "worker119", "kernel119", "signal119", "packet119", "router119"],
    ),
    (
        ("queue119 worker119 kernel119 signal119 packet119 router119", 10),
        ["queue119", "worker119", "kernel119", "signal119", "packet119", "router119"],
    ),
    (
        ("queue119 worker119 kernel119 signal119 packet119 router119", 18),
        ["queue119 worker119", "kernel119", "signal119", "packet119", "router119"],
    ),
    (
        ("queue119 worker119 kernel119 signal119 packet119 router119", 28),
        ["queue119 worker119 kernel119", "signal119 packet119", "router119"],
    ),
    (
        ("worker119 kernel119 signal119 packet119 router119 cluster119", 6),
        ["worker119", "kernel119", "signal119", "packet119", "router119", "cluster119"],
    ),
    (
        ("worker119 kernel119 signal119 packet119 router119 cluster119", 10),
        ["worker119", "kernel119", "signal119", "packet119", "router119", "cluster119"],
    ),
    (
        ("worker119 kernel119 signal119 packet119 router119 cluster119", 18),
        ["worker119", "kernel119", "signal119", "packet119", "router119", "cluster119"],
    ),
    (
        ("worker119 kernel119 signal119 packet119 router119 cluster119", 28),
        ["worker119 kernel119", "signal119 packet119", "router119 cluster119"],
    ),
    (
        ("kernel119 signal119 packet119 router119 cluster119 mirror119", 6),
        ["kernel119", "signal119", "packet119", "router119", "cluster119", "mirror119"],
    ),
    (
        ("kernel119 signal119 packet119 router119 cluster119 mirror119", 10),
        ["kernel119", "signal119", "packet119", "router119", "cluster119", "mirror119"],
    ),
    (
        ("kernel119 signal119 packet119 router119 cluster119 mirror119", 18),
        ["kernel119", "signal119", "packet119", "router119", "cluster119", "mirror119"],
    ),
    (
        ("kernel119 signal119 packet119 router119 cluster119 mirror119", 28),
        ["kernel119 signal119", "packet119 router119", "cluster119 mirror119"],
    ),
    (
        ("signal119 packet119 router119 cluster119 mirror119 filter119", 6),
        ["signal119", "packet119", "router119", "cluster119", "mirror119", "filter119"],
    ),
    (
        ("signal119 packet119 router119 cluster119 mirror119 filter119", 10),
        ["signal119", "packet119", "router119", "cluster119", "mirror119", "filter119"],
    ),
    (
        ("signal119 packet119 router119 cluster119 mirror119 filter119", 18),
        ["signal119", "packet119", "router119", "cluster119", "mirror119", "filter119"],
    ),
    (
        ("signal119 packet119 router119 cluster119 mirror119 filter119", 28),
        ["signal119 packet119", "router119 cluster119", "mirror119 filter119"],
    ),
    (
        ("packet119 router119 cluster119 mirror119 filter119 ranking119", 6),
        ["packet119", "router119", "cluster119", "mirror119", "filter119", "ranking119"],
    ),
    (
        ("packet119 router119 cluster119 mirror119 filter119 ranking119", 10),
        ["packet119", "router119", "cluster119", "mirror119", "filter119", "ranking119"],
    ),
    (
        ("packet119 router119 cluster119 mirror119 filter119 ranking119", 18),
        ["packet119", "router119", "cluster119", "mirror119", "filter119", "ranking119"],
    ),
    (
        ("packet119 router119 cluster119 mirror119 filter119 ranking119", 28),
        ["packet119 router119", "cluster119 mirror119", "filter119 ranking119"],
    ),
    (
        ("router119 cluster119 mirror119 filter119 ranking119 encoding119", 6),
        ["router119", "cluster119", "mirror119", "filter119", "ranking119", "encoding119"],
    ),
    (
        ("router119 cluster119 mirror119 filter119 ranking119 encoding119", 10),
        ["router119", "cluster119", "mirror119", "filter119", "ranking119", "encoding119"],
    ),
    (
        ("router119 cluster119 mirror119 filter119 ranking119 encoding119", 18),
        ["router119", "cluster119", "mirror119", "filter119", "ranking119", "encoding119"],
    ),
    (
        ("router119 cluster119 mirror119 filter119 ranking119 encoding119", 28),
        ["router119 cluster119", "mirror119 filter119", "ranking119 encoding119"],
    ),
    (
        ("cluster119 mirror119 filter119 ranking119 encoding119 mapping119", 6),
        ["cluster119", "mirror119", "filter119", "ranking119", "encoding119", "mapping119"],
    ),
    (
        ("cluster119 mirror119 filter119 ranking119 encoding119 mapping119", 10),
        ["cluster119", "mirror119", "filter119", "ranking119", "encoding119", "mapping119"],
    ),
    (
        ("cluster119 mirror119 filter119 ranking119 encoding119 mapping119", 18),
        ["cluster119", "mirror119", "filter119", "ranking119", "encoding119", "mapping119"],
    ),
    (
        ("cluster119 mirror119 filter119 ranking119 encoding119 mapping119", 28),
        ["cluster119 mirror119", "filter119 ranking119", "encoding119 mapping119"],
    ),
    (
        ("mirror119 filter119 ranking119 encoding119 mapping119 record119", 6),
        ["mirror119", "filter119", "ranking119", "encoding119", "mapping119", "record119"],
    ),
    (
        ("mirror119 filter119 ranking119 encoding119 mapping119 record119", 10),
        ["mirror119", "filter119", "ranking119", "encoding119", "mapping119", "record119"],
    ),
    (
        ("mirror119 filter119 ranking119 encoding119 mapping119 record119", 18),
        ["mirror119", "filter119", "ranking119", "encoding119", "mapping119", "record119"],
    ),
    (
        ("mirror119 filter119 ranking119 encoding119 mapping119 record119", 28),
        ["mirror119 filter119", "ranking119 encoding119", "mapping119 record119"],
    ),
    (
        ("filter119 ranking119 encoding119 mapping119 record119 candle119", 6),
        ["filter119", "ranking119", "encoding119", "mapping119", "record119", "candle119"],
    ),
    (
        ("filter119 ranking119 encoding119 mapping119 record119 candle119", 10),
        ["filter119", "ranking119", "encoding119", "mapping119", "record119", "candle119"],
    ),
    (
        ("filter119 ranking119 encoding119 mapping119 record119 candle119", 18),
        ["filter119", "ranking119", "encoding119", "mapping119", "record119", "candle119"],
    ),
    (
        ("filter119 ranking119 encoding119 mapping119 record119 candle119", 28),
        ["filter119 ranking119", "encoding119 mapping119", "record119 candle119"],
    ),
    (
        ("ranking119 encoding119 mapping119 record119 candle119 thread119", 6),
        ["ranking119", "encoding119", "mapping119", "record119", "candle119", "thread119"],
    ),
    (
        ("ranking119 encoding119 mapping119 record119 candle119 thread119", 10),
        ["ranking119", "encoding119", "mapping119", "record119", "candle119", "thread119"],
    ),
    (
        ("ranking119 encoding119 mapping119 record119 candle119 thread119", 18),
        ["ranking119", "encoding119", "mapping119", "record119", "candle119", "thread119"],
    ),
    (
        ("ranking119 encoding119 mapping119 record119 candle119 thread119", 28),
        ["ranking119 encoding119", "mapping119 record119", "candle119 thread119"],
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
