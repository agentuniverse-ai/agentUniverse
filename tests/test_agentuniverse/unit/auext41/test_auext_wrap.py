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
        ("round 41: the quick brown fox jumps over the lazy dog", 4),
        ["round", "41:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 41: the quick brown fox jumps over the lazy dog", 8),
        ["round", "41: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 41: the quick brown fox jumps over the lazy dog", 12),
        ["round 41:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 41: the quick brown fox jumps over the lazy dog", 16),
        ["round 41: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 41: the quick brown fox jumps over the lazy dog", 24),
        ["round 41: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 41: the quick brown fox jumps over the lazy dog", 32),
        ["round 41: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 41: agentuniverse is a framework for multi agents", 4),
        ["round", "41:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 41: agentuniverse is a framework for multi agents", 8),
        ["round", "41:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 41: agentuniverse is a framework for multi agents", 12),
        ["round 41:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 41: agentuniverse is a framework for multi agents", 16),
        ["round 41:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 41: agentuniverse is a framework for multi agents", 24),
        ["round 41: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 41: agentuniverse is a framework for multi agents", 32),
        ["round 41: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 41: knowledge stored as vectors enables retrieval", 4),
        ["round", "41:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 41: knowledge stored as vectors enables retrieval", 8),
        ["round", "41:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 41: knowledge stored as vectors enables retrieval", 12),
        ["round 41:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 41: knowledge stored as vectors enables retrieval", 16),
        ["round 41:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 41: knowledge stored as vectors enables retrieval", 24),
        ["round 41: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 41: knowledge stored as vectors enables retrieval", 32),
        ["round 41: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 41: the processor reads the record then stops", 4),
        ["round", "41:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 41: the processor reads the record then stops", 8),
        ["round", "41: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 41: the processor reads the record then stops", 12),
        ["round 41:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 41: the processor reads the record then stops", 16),
        ["round 41: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 41: the processor reads the record then stops", 24),
        ["round 41: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 41: the processor reads the record then stops", 32),
        ["round 41: the processor reads", "the record then stops"],
    ),
    (
        ("round 41: a worker pulls the next task from the queue", 4),
        ["round", "41:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 41: a worker pulls the next task from the queue", 8),
        ["round", "41: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 41: a worker pulls the next task from the queue", 12),
        ["round 41: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 41: a worker pulls the next task from the queue", 16),
        ["round 41: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 41: a worker pulls the next task from the queue", 24),
        ["round 41: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 41: a worker pulls the next task from the queue", 32),
        ["round 41: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 41: signals travel through the network layer", 4),
        ["round", "41:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 41: signals travel through the network layer", 8),
        ["round", "41:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 41: signals travel through the network layer", 12),
        ["round 41:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 41: signals travel through the network layer", 16),
        ["round 41:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 41: signals travel through the network layer", 24),
        ["round 41: signals travel", "through the network", "layer"],
    ),
    (
        ("round 41: signals travel through the network layer", 32),
        ["round 41: signals travel through", "the network layer"],
    ),
    (
        ("round 41: the gateway routes each request by policy", 4),
        ["round", "41:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 41: the gateway routes each request by policy", 8),
        ["round", "41: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 41: the gateway routes each request by policy", 12),
        ["round 41:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 41: the gateway routes each request by policy", 16),
        ["round 41: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 41: the gateway routes each request by policy", 24),
        ["round 41: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 41: the gateway routes each request by policy", 32),
        ["round 41: the gateway routes", "each request by policy"],
    ),
    (
        ("round 41: memory grows until the buffer is full", 4),
        ["round", "41:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 41: memory grows until the buffer is full", 8),
        ["round", "41:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 41: memory grows until the buffer is full", 12),
        ["round 41:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 41: memory grows until the buffer is full", 16),
        ["round 41: memory", "grows until the", "buffer is full"],
    ),
    (("round 41: memory grows until the buffer is full", 24), ["round 41: memory grows", "until the buffer is full"]),
    (("round 41: memory grows until the buffer is full", 32), ["round 41: memory grows until the", "buffer is full"]),
    (
        ("round 41: the cluster mirrors every packet twice", 4),
        ["round", "41:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 41: the cluster mirrors every packet twice", 8),
        ["round", "41: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 41: the cluster mirrors every packet twice", 12),
        ["round 41:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 41: the cluster mirrors every packet twice", 16),
        ["round 41: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 41: the cluster mirrors every packet twice", 24),
        ["round 41: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 41: the cluster mirrors every packet twice", 32), ["round 41: the cluster mirrors", "every packet twice"]),
    (
        ("round 41: ranking uses tokens learned from the corpus", 4),
        ["round", "41:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 41: ranking uses tokens learned from the corpus", 8),
        ["round", "41:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 41: ranking uses tokens learned from the corpus", 12),
        ["round 41:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 41: ranking uses tokens learned from the corpus", 16),
        ["round 41:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 41: ranking uses tokens learned from the corpus", 24),
        ["round 41: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 41: ranking uses tokens learned from the corpus", 32),
        ["round 41: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 41: a long session ends when the candle dies", 4),
        ["round", "41:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 41: a long session ends when the candle dies", 8),
        ["round", "41: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 41: a long session ends when the candle dies", 12),
        ["round 41: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 41: a long session ends when the candle dies", 16),
        ["round 41: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 41: a long session ends when the candle dies", 24),
        ["round 41: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 41: a long session ends when the candle dies", 32),
        ["round 41: a long session ends", "when the candle dies"],
    ),
    (
        ("round 41: encode the prompt then map the result", 4),
        ["round", "41:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 41: encode the prompt then map the result", 8),
        ["round", "41:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 41: encode the prompt then map the result", 12),
        ["round 41:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 41: encode the prompt then map the result", 16),
        ["round 41: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 41: encode the prompt then map the result", 24),
        ["round 41: encode the", "prompt then map the", "result"],
    ),
    (("round 41: encode the prompt then map the result", 32), ["round 41: encode the prompt then", "map the result"]),
    (
        ("round 41: the kernel wakes the worker at dawn", 4),
        ["round", "41:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 41: the kernel wakes the worker at dawn", 8),
        ["round", "41: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 41: the kernel wakes the worker at dawn", 12),
        ["round 41:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 41: the kernel wakes the worker at dawn", 16), ["round 41: the", "kernel wakes the", "worker at dawn"]),
    (("round 41: the kernel wakes the worker at dawn", 24), ["round 41: the kernel", "wakes the worker at dawn"]),
    (("round 41: the kernel wakes the worker at dawn", 32), ["round 41: the kernel wakes the", "worker at dawn"]),
    (
        ("round 41: service latency drops after the patch", 4),
        ["round", "41:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 41: service latency drops after the patch", 8),
        ["round", "41:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 41: service latency drops after the patch", 12),
        ["round 41:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 41: service latency drops after the patch", 16),
        ["round 41:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 41: service latency drops after the patch", 24),
        ["round 41: service", "latency drops after the", "patch"],
    ),
    (("round 41: service latency drops after the patch", 32), ["round 41: service latency drops", "after the patch"]),
    (
        ("round 41: the library caches every vector it sees", 4),
        ["round", "41:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 41: the library caches every vector it sees", 8),
        ["round", "41: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 41: the library caches every vector it sees", 12),
        ["round 41:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 41: the library caches every vector it sees", 16),
        ["round 41: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 41: the library caches every vector it sees", 24),
        ["round 41: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 41: the library caches every vector it sees", 32),
        ["round 41: the library caches", "every vector it sees"],
    ),
    (
        ("round 41: agents argue then the debate resolves", 4),
        ["round", "41:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 41: agents argue then the debate resolves", 8),
        ["round", "41:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 41: agents argue then the debate resolves", 12),
        ["round 41:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 41: agents argue then the debate resolves", 16),
        ["round 41: agents", "argue then the", "debate resolves"],
    ),
    (("round 41: agents argue then the debate resolves", 24), ["round 41: agents argue", "then the debate resolves"]),
    (("round 41: agents argue then the debate resolves", 32), ["round 41: agents argue then the", "debate resolves"]),
    (
        ("round 41: the filter keeps only strong matches", 4),
        ["round", "41:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 41: the filter keeps only strong matches", 8),
        ["round", "41: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 41: the filter keeps only strong matches", 12),
        ["round 41:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 41: the filter keeps only strong matches", 16),
        ["round 41: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 41: the filter keeps only strong matches", 24), ["round 41: the filter", "keeps only strong", "matches"]),
    (("round 41: the filter keeps only strong matches", 32), ["round 41: the filter keeps only", "strong matches"]),
    (
        ("round 41: the model answers with a short reply", 4),
        ["round", "41:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 41: the model answers with a short reply", 8),
        ["round", "41: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 41: the model answers with a short reply", 12),
        ["round 41:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 41: the model answers with a short reply", 16),
        ["round 41: the", "model answers", "with a short", "reply"],
    ),
    (("round 41: the model answers with a short reply", 24), ["round 41: the model", "answers with a short", "reply"]),
    (("round 41: the model answers with a short reply", 32), ["round 41: the model answers with", "a short reply"]),
    (
        ("round 41: the recorder stores the reasoning trace", 4),
        ["round", "41:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 41: the recorder stores the reasoning trace", 8),
        ["round", "41: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 41: the recorder stores the reasoning trace", 12),
        ["round 41:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 41: the recorder stores the reasoning trace", 16),
        ["round 41: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 41: the recorder stores the reasoning trace", 24),
        ["round 41: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 41: the recorder stores the reasoning trace", 32),
        ["round 41: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 41: the angel watches the processor run", 4),
        ["round", "41:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 41: the angel watches the processor run", 8),
        ["round", "41: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 41: the angel watches the processor run", 12),
        ["round 41:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 41: the angel watches the processor run", 16), ["round 41: the", "angel watches", "the processor", "run"]),
    (("round 41: the angel watches the processor run", 24), ["round 41: the angel", "watches the processor", "run"]),
    (("round 41: the angel watches the processor run", 32), ["round 41: the angel watches the", "processor run"]),
    (
        ("round 41: angle of the vector decides the match", 4),
        ["round", "41:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 41: angle of the vector decides the match", 8),
        ["round", "41:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 41: angle of the vector decides the match", 12),
        ["round 41:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 41: angle of the vector decides the match", 16),
        ["round 41: angle", "of the vector", "decides the", "match"],
    ),
    (("round 41: angle of the vector decides the match", 24), ["round 41: angle of the", "vector decides the match"]),
    (("round 41: angle of the vector decides the match", 32), ["round 41: angle of the vector", "decides the match"]),
    (
        ("round 41: the candle burns twice as long at night", 4),
        ["round", "41:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 41: the candle burns twice as long at night", 8),
        ["round", "41: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 41: the candle burns twice as long at night", 12),
        ["round 41:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 41: the candle burns twice as long at night", 16),
        ["round 41: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 41: the candle burns twice as long at night", 24),
        ["round 41: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 41: the candle burns twice as long at night", 32),
        ["round 41: the candle burns twice", "as long at night"],
    ),
    (
        ("round 41: a mirror of the universe in one line", 4),
        ["round", "41:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 41: a mirror of the universe in one line", 8),
        ["round", "41: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 41: a mirror of the universe in one line", 12),
        ["round 41: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 41: a mirror of the universe in one line", 16),
        ["round 41: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 41: a mirror of the universe in one line", 24), ["round 41: a mirror of", "the universe in one line"]),
    (("round 41: a mirror of the universe in one line", 32), ["round 41: a mirror of the", "universe in one line"]),
    (
        ("round 41: the queue drains before the storm", 4),
        ["round", "41:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 41: the queue drains before the storm", 8),
        ["round", "41: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 41: the queue drains before the storm", 12), ["round 41:", "the queue", "drains", "before the", "storm"]),
    (("round 41: the queue drains before the storm", 16), ["round 41: the", "queue drains", "before the storm"]),
    (("round 41: the queue drains before the storm", 24), ["round 41: the queue", "drains before the storm"]),
    (("round 41: the queue drains before the storm", 32), ["round 41: the queue drains", "before the storm"]),
    (
        ("kitten41 sitting41 agent41 angle41 universe41 memory41", 6),
        ["kitten41", "sitting41", "agent41", "angle41", "universe41", "memory41"],
    ),
    (
        ("kitten41 sitting41 agent41 angle41 universe41 memory41", 10),
        ["kitten41", "sitting41", "agent41", "angle41", "universe41", "memory41"],
    ),
    (
        ("kitten41 sitting41 agent41 angle41 universe41 memory41", 18),
        ["kitten41 sitting41", "agent41 angle41", "universe41", "memory41"],
    ),
    (
        ("kitten41 sitting41 agent41 angle41 universe41 memory41", 28),
        ["kitten41 sitting41 agent41", "angle41 universe41 memory41"],
    ),
    (
        ("sitting41 agent41 angle41 universe41 memory41 stream41", 6),
        ["sitting41", "agent41", "angle41", "universe41", "memory41", "stream41"],
    ),
    (
        ("sitting41 agent41 angle41 universe41 memory41 stream41", 10),
        ["sitting41", "agent41", "angle41", "universe41", "memory41", "stream41"],
    ),
    (
        ("sitting41 agent41 angle41 universe41 memory41 stream41", 18),
        ["sitting41 agent41", "angle41 universe41", "memory41 stream41"],
    ),
    (
        ("sitting41 agent41 angle41 universe41 memory41 stream41", 28),
        ["sitting41 agent41 angle41", "universe41 memory41 stream41"],
    ),
    (
        ("agent41 angle41 universe41 memory41 stream41 context41", 6),
        ["agent41", "angle41", "universe41", "memory41", "stream41", "context41"],
    ),
    (
        ("agent41 angle41 universe41 memory41 stream41 context41", 10),
        ["agent41", "angle41", "universe41", "memory41", "stream41", "context41"],
    ),
    (
        ("agent41 angle41 universe41 memory41 stream41 context41", 18),
        ["agent41 angle41", "universe41", "memory41 stream41", "context41"],
    ),
    (
        ("agent41 angle41 universe41 memory41 stream41 context41", 28),
        ["agent41 angle41 universe41", "memory41 stream41 context41"],
    ),
    (
        ("angle41 universe41 memory41 stream41 context41 knowledge41", 6),
        ["angle41", "universe41", "memory41", "stream41", "context41", "knowledge41"],
    ),
    (
        ("angle41 universe41 memory41 stream41 context41 knowledge41", 10),
        ["angle41", "universe41", "memory41", "stream41", "context41", "knowledge41"],
    ),
    (
        ("angle41 universe41 memory41 stream41 context41 knowledge41", 18),
        ["angle41 universe41", "memory41 stream41", "context41", "knowledge41"],
    ),
    (
        ("angle41 universe41 memory41 stream41 context41 knowledge41", 28),
        ["angle41 universe41 memory41", "stream41 context41", "knowledge41"],
    ),
    (
        ("universe41 memory41 stream41 context41 knowledge41 vector41", 6),
        ["universe41", "memory41", "stream41", "context41", "knowledge41", "vector41"],
    ),
    (
        ("universe41 memory41 stream41 context41 knowledge41 vector41", 10),
        ["universe41", "memory41", "stream41", "context41", "knowledge41", "vector41"],
    ),
    (
        ("universe41 memory41 stream41 context41 knowledge41 vector41", 18),
        ["universe41", "memory41 stream41", "context41", "knowledge41", "vector41"],
    ),
    (
        ("universe41 memory41 stream41 context41 knowledge41 vector41", 28),
        ["universe41 memory41 stream41", "context41 knowledge41", "vector41"],
    ),
    (
        ("memory41 stream41 context41 knowledge41 vector41 processor41", 6),
        ["memory41", "stream41", "context41", "knowledge41", "vector41", "processor41"],
    ),
    (
        ("memory41 stream41 context41 knowledge41 vector41 processor41", 10),
        ["memory41", "stream41", "context41", "knowledge41", "vector41", "processor41"],
    ),
    (
        ("memory41 stream41 context41 knowledge41 vector41 processor41", 18),
        ["memory41 stream41", "context41", "knowledge41", "vector41", "processor41"],
    ),
    (
        ("memory41 stream41 context41 knowledge41 vector41 processor41", 28),
        ["memory41 stream41 context41", "knowledge41 vector41", "processor41"],
    ),
    (
        ("stream41 context41 knowledge41 vector41 processor41 reasoning41", 6),
        ["stream41", "context41", "knowledge41", "vector41", "processor41", "reasoning41"],
    ),
    (
        ("stream41 context41 knowledge41 vector41 processor41 reasoning41", 10),
        ["stream41", "context41", "knowledge41", "vector41", "processor41", "reasoning41"],
    ),
    (
        ("stream41 context41 knowledge41 vector41 processor41 reasoning41", 18),
        ["stream41 context41", "knowledge41", "vector41", "processor41", "reasoning41"],
    ),
    (
        ("stream41 context41 knowledge41 vector41 processor41 reasoning41", 28),
        ["stream41 context41", "knowledge41 vector41", "processor41 reasoning41"],
    ),
    (
        ("context41 knowledge41 vector41 processor41 reasoning41 machine41", 6),
        ["context41", "knowledge41", "vector41", "processor41", "reasoning41", "machine41"],
    ),
    (
        ("context41 knowledge41 vector41 processor41 reasoning41 machine41", 10),
        ["context41", "knowledge41", "vector41", "processor41", "reasoning41", "machine41"],
    ),
    (
        ("context41 knowledge41 vector41 processor41 reasoning41 machine41", 18),
        ["context41", "knowledge41", "vector41", "processor41", "reasoning41", "machine41"],
    ),
    (
        ("context41 knowledge41 vector41 processor41 reasoning41 machine41", 28),
        ["context41 knowledge41", "vector41 processor41", "reasoning41 machine41"],
    ),
    (
        ("knowledge41 vector41 processor41 reasoning41 machine41 learning41", 6),
        ["knowledge41", "vector41", "processor41", "reasoning41", "machine41", "learning41"],
    ),
    (
        ("knowledge41 vector41 processor41 reasoning41 machine41 learning41", 10),
        ["knowledge41", "vector41", "processor41", "reasoning41", "machine41", "learning41"],
    ),
    (
        ("knowledge41 vector41 processor41 reasoning41 machine41 learning41", 18),
        ["knowledge41", "vector41", "processor41", "reasoning41", "machine41", "learning41"],
    ),
    (
        ("knowledge41 vector41 processor41 reasoning41 machine41 learning41", 28),
        ["knowledge41 vector41", "processor41 reasoning41", "machine41 learning41"],
    ),
    (
        ("vector41 processor41 reasoning41 machine41 learning41 model41", 6),
        ["vector41", "processor41", "reasoning41", "machine41", "learning41", "model41"],
    ),
    (
        ("vector41 processor41 reasoning41 machine41 learning41 model41", 10),
        ["vector41", "processor41", "reasoning41", "machine41", "learning41", "model41"],
    ),
    (
        ("vector41 processor41 reasoning41 machine41 learning41 model41", 18),
        ["vector41", "processor41", "reasoning41", "machine41", "learning41 model41"],
    ),
    (
        ("vector41 processor41 reasoning41 machine41 learning41 model41", 28),
        ["vector41 processor41", "reasoning41 machine41", "learning41 model41"],
    ),
    (
        ("processor41 reasoning41 machine41 learning41 model41 token41", 6),
        ["processor41", "reasoning41", "machine41", "learning41", "model41", "token41"],
    ),
    (
        ("processor41 reasoning41 machine41 learning41 model41 token41", 10),
        ["processor41", "reasoning41", "machine41", "learning41", "model41", "token41"],
    ),
    (
        ("processor41 reasoning41 machine41 learning41 model41 token41", 18),
        ["processor41", "reasoning41", "machine41", "learning41 model41", "token41"],
    ),
    (
        ("processor41 reasoning41 machine41 learning41 model41 token41", 28),
        ["processor41 reasoning41", "machine41 learning41 model41", "token41"],
    ),
    (
        ("reasoning41 machine41 learning41 model41 token41 prompt41", 6),
        ["reasoning41", "machine41", "learning41", "model41", "token41", "prompt41"],
    ),
    (
        ("reasoning41 machine41 learning41 model41 token41 prompt41", 10),
        ["reasoning41", "machine41", "learning41", "model41", "token41", "prompt41"],
    ),
    (
        ("reasoning41 machine41 learning41 model41 token41 prompt41", 18),
        ["reasoning41", "machine41", "learning41 model41", "token41 prompt41"],
    ),
    (
        ("reasoning41 machine41 learning41 model41 token41 prompt41", 28),
        ["reasoning41 machine41", "learning41 model41 token41", "prompt41"],
    ),
    (
        ("machine41 learning41 model41 token41 prompt41 session41", 6),
        ["machine41", "learning41", "model41", "token41", "prompt41", "session41"],
    ),
    (
        ("machine41 learning41 model41 token41 prompt41 session41", 10),
        ["machine41", "learning41", "model41", "token41", "prompt41", "session41"],
    ),
    (
        ("machine41 learning41 model41 token41 prompt41 session41", 18),
        ["machine41", "learning41 model41", "token41 prompt41", "session41"],
    ),
    (
        ("machine41 learning41 model41 token41 prompt41 session41", 28),
        ["machine41 learning41 model41", "token41 prompt41 session41"],
    ),
    (
        ("learning41 model41 token41 prompt41 session41 library41", 6),
        ["learning41", "model41", "token41", "prompt41", "session41", "library41"],
    ),
    (
        ("learning41 model41 token41 prompt41 session41 library41", 10),
        ["learning41", "model41", "token41", "prompt41", "session41", "library41"],
    ),
    (
        ("learning41 model41 token41 prompt41 session41 library41", 18),
        ["learning41 model41", "token41 prompt41", "session41", "library41"],
    ),
    (
        ("learning41 model41 token41 prompt41 session41 library41", 28),
        ["learning41 model41 token41", "prompt41 session41 library41"],
    ),
    (
        ("model41 token41 prompt41 session41 library41 service41", 6),
        ["model41", "token41", "prompt41", "session41", "library41", "service41"],
    ),
    (
        ("model41 token41 prompt41 session41 library41 service41", 10),
        ["model41", "token41", "prompt41", "session41", "library41", "service41"],
    ),
    (
        ("model41 token41 prompt41 session41 library41 service41", 18),
        ["model41 token41", "prompt41 session41", "library41", "service41"],
    ),
    (
        ("model41 token41 prompt41 session41 library41 service41", 28),
        ["model41 token41 prompt41", "session41 library41", "service41"],
    ),
    (
        ("token41 prompt41 session41 library41 service41 gateway41", 6),
        ["token41", "prompt41", "session41", "library41", "service41", "gateway41"],
    ),
    (
        ("token41 prompt41 session41 library41 service41 gateway41", 10),
        ["token41", "prompt41", "session41", "library41", "service41", "gateway41"],
    ),
    (
        ("token41 prompt41 session41 library41 service41 gateway41", 18),
        ["token41 prompt41", "session41", "library41", "service41", "gateway41"],
    ),
    (
        ("token41 prompt41 session41 library41 service41 gateway41", 28),
        ["token41 prompt41 session41", "library41 service41", "gateway41"],
    ),
    (
        ("prompt41 session41 library41 service41 gateway41 storage41", 6),
        ["prompt41", "session41", "library41", "service41", "gateway41", "storage41"],
    ),
    (
        ("prompt41 session41 library41 service41 gateway41 storage41", 10),
        ["prompt41", "session41", "library41", "service41", "gateway41", "storage41"],
    ),
    (
        ("prompt41 session41 library41 service41 gateway41 storage41", 18),
        ["prompt41 session41", "library41", "service41", "gateway41", "storage41"],
    ),
    (
        ("prompt41 session41 library41 service41 gateway41 storage41", 28),
        ["prompt41 session41 library41", "service41 gateway41", "storage41"],
    ),
    (
        ("session41 library41 service41 gateway41 storage41 network41", 6),
        ["session41", "library41", "service41", "gateway41", "storage41", "network41"],
    ),
    (
        ("session41 library41 service41 gateway41 storage41 network41", 10),
        ["session41", "library41", "service41", "gateway41", "storage41", "network41"],
    ),
    (
        ("session41 library41 service41 gateway41 storage41 network41", 18),
        ["session41", "library41", "service41", "gateway41", "storage41", "network41"],
    ),
    (
        ("session41 library41 service41 gateway41 storage41 network41", 28),
        ["session41 library41", "service41 gateway41", "storage41 network41"],
    ),
    (
        ("library41 service41 gateway41 storage41 network41 latency41", 6),
        ["library41", "service41", "gateway41", "storage41", "network41", "latency41"],
    ),
    (
        ("library41 service41 gateway41 storage41 network41 latency41", 10),
        ["library41", "service41", "gateway41", "storage41", "network41", "latency41"],
    ),
    (
        ("library41 service41 gateway41 storage41 network41 latency41", 18),
        ["library41", "service41", "gateway41", "storage41", "network41", "latency41"],
    ),
    (
        ("library41 service41 gateway41 storage41 network41 latency41", 28),
        ["library41 service41", "gateway41 storage41", "network41 latency41"],
    ),
    (
        ("service41 gateway41 storage41 network41 latency41 buffer41", 6),
        ["service41", "gateway41", "storage41", "network41", "latency41", "buffer41"],
    ),
    (
        ("service41 gateway41 storage41 network41 latency41 buffer41", 10),
        ["service41", "gateway41", "storage41", "network41", "latency41", "buffer41"],
    ),
    (
        ("service41 gateway41 storage41 network41 latency41 buffer41", 18),
        ["service41", "gateway41", "storage41", "network41", "latency41 buffer41"],
    ),
    (
        ("service41 gateway41 storage41 network41 latency41 buffer41", 28),
        ["service41 gateway41", "storage41 network41", "latency41 buffer41"],
    ),
    (
        ("gateway41 storage41 network41 latency41 buffer41 queue41", 6),
        ["gateway41", "storage41", "network41", "latency41", "buffer41", "queue41"],
    ),
    (
        ("gateway41 storage41 network41 latency41 buffer41 queue41", 10),
        ["gateway41", "storage41", "network41", "latency41", "buffer41", "queue41"],
    ),
    (
        ("gateway41 storage41 network41 latency41 buffer41 queue41", 18),
        ["gateway41", "storage41", "network41", "latency41 buffer41", "queue41"],
    ),
    (
        ("gateway41 storage41 network41 latency41 buffer41 queue41", 28),
        ["gateway41 storage41", "network41 latency41 buffer41", "queue41"],
    ),
    (
        ("storage41 network41 latency41 buffer41 queue41 worker41", 6),
        ["storage41", "network41", "latency41", "buffer41", "queue41", "worker41"],
    ),
    (
        ("storage41 network41 latency41 buffer41 queue41 worker41", 10),
        ["storage41", "network41", "latency41", "buffer41", "queue41", "worker41"],
    ),
    (
        ("storage41 network41 latency41 buffer41 queue41 worker41", 18),
        ["storage41", "network41", "latency41 buffer41", "queue41 worker41"],
    ),
    (
        ("storage41 network41 latency41 buffer41 queue41 worker41", 28),
        ["storage41 network41", "latency41 buffer41 queue41", "worker41"],
    ),
    (
        ("network41 latency41 buffer41 queue41 worker41 kernel41", 6),
        ["network41", "latency41", "buffer41", "queue41", "worker41", "kernel41"],
    ),
    (
        ("network41 latency41 buffer41 queue41 worker41 kernel41", 10),
        ["network41", "latency41", "buffer41", "queue41", "worker41", "kernel41"],
    ),
    (
        ("network41 latency41 buffer41 queue41 worker41 kernel41", 18),
        ["network41", "latency41 buffer41", "queue41 worker41", "kernel41"],
    ),
    (
        ("network41 latency41 buffer41 queue41 worker41 kernel41", 28),
        ["network41 latency41 buffer41", "queue41 worker41 kernel41"],
    ),
    (
        ("latency41 buffer41 queue41 worker41 kernel41 signal41", 6),
        ["latency41", "buffer41", "queue41", "worker41", "kernel41", "signal41"],
    ),
    (
        ("latency41 buffer41 queue41 worker41 kernel41 signal41", 10),
        ["latency41", "buffer41", "queue41", "worker41", "kernel41", "signal41"],
    ),
    (
        ("latency41 buffer41 queue41 worker41 kernel41 signal41", 18),
        ["latency41 buffer41", "queue41 worker41", "kernel41 signal41"],
    ),
    (
        ("latency41 buffer41 queue41 worker41 kernel41 signal41", 28),
        ["latency41 buffer41 queue41", "worker41 kernel41 signal41"],
    ),
    (
        ("buffer41 queue41 worker41 kernel41 signal41 packet41", 6),
        ["buffer41", "queue41", "worker41", "kernel41", "signal41", "packet41"],
    ),
    (
        ("buffer41 queue41 worker41 kernel41 signal41 packet41", 10),
        ["buffer41", "queue41", "worker41", "kernel41", "signal41", "packet41"],
    ),
    (
        ("buffer41 queue41 worker41 kernel41 signal41 packet41", 18),
        ["buffer41 queue41", "worker41 kernel41", "signal41 packet41"],
    ),
    (
        ("buffer41 queue41 worker41 kernel41 signal41 packet41", 28),
        ["buffer41 queue41 worker41", "kernel41 signal41 packet41"],
    ),
    (
        ("queue41 worker41 kernel41 signal41 packet41 router41", 6),
        ["queue41", "worker41", "kernel41", "signal41", "packet41", "router41"],
    ),
    (
        ("queue41 worker41 kernel41 signal41 packet41 router41", 10),
        ["queue41", "worker41", "kernel41", "signal41", "packet41", "router41"],
    ),
    (
        ("queue41 worker41 kernel41 signal41 packet41 router41", 18),
        ["queue41 worker41", "kernel41 signal41", "packet41 router41"],
    ),
    (
        ("queue41 worker41 kernel41 signal41 packet41 router41", 28),
        ["queue41 worker41 kernel41", "signal41 packet41 router41"],
    ),
    (
        ("worker41 kernel41 signal41 packet41 router41 cluster41", 6),
        ["worker41", "kernel41", "signal41", "packet41", "router41", "cluster41"],
    ),
    (
        ("worker41 kernel41 signal41 packet41 router41 cluster41", 10),
        ["worker41", "kernel41", "signal41", "packet41", "router41", "cluster41"],
    ),
    (
        ("worker41 kernel41 signal41 packet41 router41 cluster41", 18),
        ["worker41 kernel41", "signal41 packet41", "router41 cluster41"],
    ),
    (
        ("worker41 kernel41 signal41 packet41 router41 cluster41", 28),
        ["worker41 kernel41 signal41", "packet41 router41 cluster41"],
    ),
    (
        ("kernel41 signal41 packet41 router41 cluster41 mirror41", 6),
        ["kernel41", "signal41", "packet41", "router41", "cluster41", "mirror41"],
    ),
    (
        ("kernel41 signal41 packet41 router41 cluster41 mirror41", 10),
        ["kernel41", "signal41", "packet41", "router41", "cluster41", "mirror41"],
    ),
    (
        ("kernel41 signal41 packet41 router41 cluster41 mirror41", 18),
        ["kernel41 signal41", "packet41 router41", "cluster41 mirror41"],
    ),
    (
        ("kernel41 signal41 packet41 router41 cluster41 mirror41", 28),
        ["kernel41 signal41 packet41", "router41 cluster41 mirror41"],
    ),
    (
        ("signal41 packet41 router41 cluster41 mirror41 filter41", 6),
        ["signal41", "packet41", "router41", "cluster41", "mirror41", "filter41"],
    ),
    (
        ("signal41 packet41 router41 cluster41 mirror41 filter41", 10),
        ["signal41", "packet41", "router41", "cluster41", "mirror41", "filter41"],
    ),
    (
        ("signal41 packet41 router41 cluster41 mirror41 filter41", 18),
        ["signal41 packet41", "router41 cluster41", "mirror41 filter41"],
    ),
    (
        ("signal41 packet41 router41 cluster41 mirror41 filter41", 28),
        ["signal41 packet41 router41", "cluster41 mirror41 filter41"],
    ),
    (
        ("packet41 router41 cluster41 mirror41 filter41 ranking41", 6),
        ["packet41", "router41", "cluster41", "mirror41", "filter41", "ranking41"],
    ),
    (
        ("packet41 router41 cluster41 mirror41 filter41 ranking41", 10),
        ["packet41", "router41", "cluster41", "mirror41", "filter41", "ranking41"],
    ),
    (
        ("packet41 router41 cluster41 mirror41 filter41 ranking41", 18),
        ["packet41 router41", "cluster41 mirror41", "filter41 ranking41"],
    ),
    (
        ("packet41 router41 cluster41 mirror41 filter41 ranking41", 28),
        ["packet41 router41 cluster41", "mirror41 filter41 ranking41"],
    ),
    (
        ("router41 cluster41 mirror41 filter41 ranking41 encoding41", 6),
        ["router41", "cluster41", "mirror41", "filter41", "ranking41", "encoding41"],
    ),
    (
        ("router41 cluster41 mirror41 filter41 ranking41 encoding41", 10),
        ["router41", "cluster41", "mirror41", "filter41", "ranking41", "encoding41"],
    ),
    (
        ("router41 cluster41 mirror41 filter41 ranking41 encoding41", 18),
        ["router41 cluster41", "mirror41 filter41", "ranking41", "encoding41"],
    ),
    (
        ("router41 cluster41 mirror41 filter41 ranking41 encoding41", 28),
        ["router41 cluster41 mirror41", "filter41 ranking41", "encoding41"],
    ),
    (
        ("cluster41 mirror41 filter41 ranking41 encoding41 mapping41", 6),
        ["cluster41", "mirror41", "filter41", "ranking41", "encoding41", "mapping41"],
    ),
    (
        ("cluster41 mirror41 filter41 ranking41 encoding41 mapping41", 10),
        ["cluster41", "mirror41", "filter41", "ranking41", "encoding41", "mapping41"],
    ),
    (
        ("cluster41 mirror41 filter41 ranking41 encoding41 mapping41", 18),
        ["cluster41 mirror41", "filter41 ranking41", "encoding41", "mapping41"],
    ),
    (
        ("cluster41 mirror41 filter41 ranking41 encoding41 mapping41", 28),
        ["cluster41 mirror41 filter41", "ranking41 encoding41", "mapping41"],
    ),
    (
        ("mirror41 filter41 ranking41 encoding41 mapping41 record41", 6),
        ["mirror41", "filter41", "ranking41", "encoding41", "mapping41", "record41"],
    ),
    (
        ("mirror41 filter41 ranking41 encoding41 mapping41 record41", 10),
        ["mirror41", "filter41", "ranking41", "encoding41", "mapping41", "record41"],
    ),
    (
        ("mirror41 filter41 ranking41 encoding41 mapping41 record41", 18),
        ["mirror41 filter41", "ranking41", "encoding41", "mapping41 record41"],
    ),
    (
        ("mirror41 filter41 ranking41 encoding41 mapping41 record41", 28),
        ["mirror41 filter41 ranking41", "encoding41 mapping41", "record41"],
    ),
    (
        ("filter41 ranking41 encoding41 mapping41 record41 candle41", 6),
        ["filter41", "ranking41", "encoding41", "mapping41", "record41", "candle41"],
    ),
    (
        ("filter41 ranking41 encoding41 mapping41 record41 candle41", 10),
        ["filter41", "ranking41", "encoding41", "mapping41", "record41", "candle41"],
    ),
    (
        ("filter41 ranking41 encoding41 mapping41 record41 candle41", 18),
        ["filter41 ranking41", "encoding41", "mapping41 record41", "candle41"],
    ),
    (
        ("filter41 ranking41 encoding41 mapping41 record41 candle41", 28),
        ["filter41 ranking41", "encoding41 mapping41", "record41 candle41"],
    ),
    (
        ("ranking41 encoding41 mapping41 record41 candle41 thread41", 6),
        ["ranking41", "encoding41", "mapping41", "record41", "candle41", "thread41"],
    ),
    (
        ("ranking41 encoding41 mapping41 record41 candle41 thread41", 10),
        ["ranking41", "encoding41", "mapping41", "record41", "candle41", "thread41"],
    ),
    (
        ("ranking41 encoding41 mapping41 record41 candle41 thread41", 18),
        ["ranking41", "encoding41", "mapping41 record41", "candle41 thread41"],
    ),
    (
        ("ranking41 encoding41 mapping41 record41 candle41 thread41", 28),
        ["ranking41 encoding41", "mapping41 record41 candle41", "thread41"],
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
