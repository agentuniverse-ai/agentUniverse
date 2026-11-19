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
        ("round 35: the quick brown fox jumps over the lazy dog", 4),
        ["round", "35:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 35: the quick brown fox jumps over the lazy dog", 8),
        ["round", "35: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 35: the quick brown fox jumps over the lazy dog", 12),
        ["round 35:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 35: the quick brown fox jumps over the lazy dog", 16),
        ["round 35: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 35: the quick brown fox jumps over the lazy dog", 24),
        ["round 35: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 35: the quick brown fox jumps over the lazy dog", 32),
        ["round 35: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 35: agentuniverse is a framework for multi agents", 4),
        ["round", "35:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 35: agentuniverse is a framework for multi agents", 8),
        ["round", "35:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 35: agentuniverse is a framework for multi agents", 12),
        ["round 35:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 35: agentuniverse is a framework for multi agents", 16),
        ["round 35:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 35: agentuniverse is a framework for multi agents", 24),
        ["round 35: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 35: agentuniverse is a framework for multi agents", 32),
        ["round 35: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 35: knowledge stored as vectors enables retrieval", 4),
        ["round", "35:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 35: knowledge stored as vectors enables retrieval", 8),
        ["round", "35:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 35: knowledge stored as vectors enables retrieval", 12),
        ["round 35:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 35: knowledge stored as vectors enables retrieval", 16),
        ["round 35:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 35: knowledge stored as vectors enables retrieval", 24),
        ["round 35: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 35: knowledge stored as vectors enables retrieval", 32),
        ["round 35: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 35: the processor reads the record then stops", 4),
        ["round", "35:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 35: the processor reads the record then stops", 8),
        ["round", "35: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 35: the processor reads the record then stops", 12),
        ["round 35:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 35: the processor reads the record then stops", 16),
        ["round 35: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 35: the processor reads the record then stops", 24),
        ["round 35: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 35: the processor reads the record then stops", 32),
        ["round 35: the processor reads", "the record then stops"],
    ),
    (
        ("round 35: a worker pulls the next task from the queue", 4),
        ["round", "35:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 35: a worker pulls the next task from the queue", 8),
        ["round", "35: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 35: a worker pulls the next task from the queue", 12),
        ["round 35: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 35: a worker pulls the next task from the queue", 16),
        ["round 35: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 35: a worker pulls the next task from the queue", 24),
        ["round 35: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 35: a worker pulls the next task from the queue", 32),
        ["round 35: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 35: signals travel through the network layer", 4),
        ["round", "35:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 35: signals travel through the network layer", 8),
        ["round", "35:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 35: signals travel through the network layer", 12),
        ["round 35:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 35: signals travel through the network layer", 16),
        ["round 35:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 35: signals travel through the network layer", 24),
        ["round 35: signals travel", "through the network", "layer"],
    ),
    (
        ("round 35: signals travel through the network layer", 32),
        ["round 35: signals travel through", "the network layer"],
    ),
    (
        ("round 35: the gateway routes each request by policy", 4),
        ["round", "35:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 35: the gateway routes each request by policy", 8),
        ["round", "35: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 35: the gateway routes each request by policy", 12),
        ["round 35:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 35: the gateway routes each request by policy", 16),
        ["round 35: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 35: the gateway routes each request by policy", 24),
        ["round 35: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 35: the gateway routes each request by policy", 32),
        ["round 35: the gateway routes", "each request by policy"],
    ),
    (
        ("round 35: memory grows until the buffer is full", 4),
        ["round", "35:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 35: memory grows until the buffer is full", 8),
        ["round", "35:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 35: memory grows until the buffer is full", 12),
        ["round 35:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 35: memory grows until the buffer is full", 16),
        ["round 35: memory", "grows until the", "buffer is full"],
    ),
    (("round 35: memory grows until the buffer is full", 24), ["round 35: memory grows", "until the buffer is full"]),
    (("round 35: memory grows until the buffer is full", 32), ["round 35: memory grows until the", "buffer is full"]),
    (
        ("round 35: the cluster mirrors every packet twice", 4),
        ["round", "35:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 35: the cluster mirrors every packet twice", 8),
        ["round", "35: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 35: the cluster mirrors every packet twice", 12),
        ["round 35:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 35: the cluster mirrors every packet twice", 16),
        ["round 35: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 35: the cluster mirrors every packet twice", 24),
        ["round 35: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 35: the cluster mirrors every packet twice", 32), ["round 35: the cluster mirrors", "every packet twice"]),
    (
        ("round 35: ranking uses tokens learned from the corpus", 4),
        ["round", "35:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 35: ranking uses tokens learned from the corpus", 8),
        ["round", "35:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 35: ranking uses tokens learned from the corpus", 12),
        ["round 35:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 35: ranking uses tokens learned from the corpus", 16),
        ["round 35:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 35: ranking uses tokens learned from the corpus", 24),
        ["round 35: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 35: ranking uses tokens learned from the corpus", 32),
        ["round 35: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 35: a long session ends when the candle dies", 4),
        ["round", "35:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 35: a long session ends when the candle dies", 8),
        ["round", "35: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 35: a long session ends when the candle dies", 12),
        ["round 35: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 35: a long session ends when the candle dies", 16),
        ["round 35: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 35: a long session ends when the candle dies", 24),
        ["round 35: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 35: a long session ends when the candle dies", 32),
        ["round 35: a long session ends", "when the candle dies"],
    ),
    (
        ("round 35: encode the prompt then map the result", 4),
        ["round", "35:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 35: encode the prompt then map the result", 8),
        ["round", "35:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 35: encode the prompt then map the result", 12),
        ["round 35:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 35: encode the prompt then map the result", 16),
        ["round 35: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 35: encode the prompt then map the result", 24),
        ["round 35: encode the", "prompt then map the", "result"],
    ),
    (("round 35: encode the prompt then map the result", 32), ["round 35: encode the prompt then", "map the result"]),
    (
        ("round 35: the kernel wakes the worker at dawn", 4),
        ["round", "35:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 35: the kernel wakes the worker at dawn", 8),
        ["round", "35: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 35: the kernel wakes the worker at dawn", 12),
        ["round 35:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 35: the kernel wakes the worker at dawn", 16), ["round 35: the", "kernel wakes the", "worker at dawn"]),
    (("round 35: the kernel wakes the worker at dawn", 24), ["round 35: the kernel", "wakes the worker at dawn"]),
    (("round 35: the kernel wakes the worker at dawn", 32), ["round 35: the kernel wakes the", "worker at dawn"]),
    (
        ("round 35: service latency drops after the patch", 4),
        ["round", "35:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 35: service latency drops after the patch", 8),
        ["round", "35:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 35: service latency drops after the patch", 12),
        ["round 35:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 35: service latency drops after the patch", 16),
        ["round 35:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 35: service latency drops after the patch", 24),
        ["round 35: service", "latency drops after the", "patch"],
    ),
    (("round 35: service latency drops after the patch", 32), ["round 35: service latency drops", "after the patch"]),
    (
        ("round 35: the library caches every vector it sees", 4),
        ["round", "35:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 35: the library caches every vector it sees", 8),
        ["round", "35: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 35: the library caches every vector it sees", 12),
        ["round 35:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 35: the library caches every vector it sees", 16),
        ["round 35: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 35: the library caches every vector it sees", 24),
        ["round 35: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 35: the library caches every vector it sees", 32),
        ["round 35: the library caches", "every vector it sees"],
    ),
    (
        ("round 35: agents argue then the debate resolves", 4),
        ["round", "35:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 35: agents argue then the debate resolves", 8),
        ["round", "35:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 35: agents argue then the debate resolves", 12),
        ["round 35:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 35: agents argue then the debate resolves", 16),
        ["round 35: agents", "argue then the", "debate resolves"],
    ),
    (("round 35: agents argue then the debate resolves", 24), ["round 35: agents argue", "then the debate resolves"]),
    (("round 35: agents argue then the debate resolves", 32), ["round 35: agents argue then the", "debate resolves"]),
    (
        ("round 35: the filter keeps only strong matches", 4),
        ["round", "35:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 35: the filter keeps only strong matches", 8),
        ["round", "35: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 35: the filter keeps only strong matches", 12),
        ["round 35:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 35: the filter keeps only strong matches", 16),
        ["round 35: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 35: the filter keeps only strong matches", 24), ["round 35: the filter", "keeps only strong", "matches"]),
    (("round 35: the filter keeps only strong matches", 32), ["round 35: the filter keeps only", "strong matches"]),
    (
        ("round 35: the model answers with a short reply", 4),
        ["round", "35:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 35: the model answers with a short reply", 8),
        ["round", "35: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 35: the model answers with a short reply", 12),
        ["round 35:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 35: the model answers with a short reply", 16),
        ["round 35: the", "model answers", "with a short", "reply"],
    ),
    (("round 35: the model answers with a short reply", 24), ["round 35: the model", "answers with a short", "reply"]),
    (("round 35: the model answers with a short reply", 32), ["round 35: the model answers with", "a short reply"]),
    (
        ("round 35: the recorder stores the reasoning trace", 4),
        ["round", "35:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 35: the recorder stores the reasoning trace", 8),
        ["round", "35: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 35: the recorder stores the reasoning trace", 12),
        ["round 35:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 35: the recorder stores the reasoning trace", 16),
        ["round 35: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 35: the recorder stores the reasoning trace", 24),
        ["round 35: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 35: the recorder stores the reasoning trace", 32),
        ["round 35: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 35: the angel watches the processor run", 4),
        ["round", "35:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 35: the angel watches the processor run", 8),
        ["round", "35: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 35: the angel watches the processor run", 12),
        ["round 35:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 35: the angel watches the processor run", 16), ["round 35: the", "angel watches", "the processor", "run"]),
    (("round 35: the angel watches the processor run", 24), ["round 35: the angel", "watches the processor", "run"]),
    (("round 35: the angel watches the processor run", 32), ["round 35: the angel watches the", "processor run"]),
    (
        ("round 35: angle of the vector decides the match", 4),
        ["round", "35:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 35: angle of the vector decides the match", 8),
        ["round", "35:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 35: angle of the vector decides the match", 12),
        ["round 35:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 35: angle of the vector decides the match", 16),
        ["round 35: angle", "of the vector", "decides the", "match"],
    ),
    (("round 35: angle of the vector decides the match", 24), ["round 35: angle of the", "vector decides the match"]),
    (("round 35: angle of the vector decides the match", 32), ["round 35: angle of the vector", "decides the match"]),
    (
        ("round 35: the candle burns twice as long at night", 4),
        ["round", "35:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 35: the candle burns twice as long at night", 8),
        ["round", "35: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 35: the candle burns twice as long at night", 12),
        ["round 35:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 35: the candle burns twice as long at night", 16),
        ["round 35: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 35: the candle burns twice as long at night", 24),
        ["round 35: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 35: the candle burns twice as long at night", 32),
        ["round 35: the candle burns twice", "as long at night"],
    ),
    (
        ("round 35: a mirror of the universe in one line", 4),
        ["round", "35:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 35: a mirror of the universe in one line", 8),
        ["round", "35: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 35: a mirror of the universe in one line", 12),
        ["round 35: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 35: a mirror of the universe in one line", 16),
        ["round 35: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 35: a mirror of the universe in one line", 24), ["round 35: a mirror of", "the universe in one line"]),
    (("round 35: a mirror of the universe in one line", 32), ["round 35: a mirror of the", "universe in one line"]),
    (
        ("round 35: the queue drains before the storm", 4),
        ["round", "35:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 35: the queue drains before the storm", 8),
        ["round", "35: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 35: the queue drains before the storm", 12), ["round 35:", "the queue", "drains", "before the", "storm"]),
    (("round 35: the queue drains before the storm", 16), ["round 35: the", "queue drains", "before the storm"]),
    (("round 35: the queue drains before the storm", 24), ["round 35: the queue", "drains before the storm"]),
    (("round 35: the queue drains before the storm", 32), ["round 35: the queue drains", "before the storm"]),
    (
        ("kitten35 sitting35 agent35 angle35 universe35 memory35", 6),
        ["kitten35", "sitting35", "agent35", "angle35", "universe35", "memory35"],
    ),
    (
        ("kitten35 sitting35 agent35 angle35 universe35 memory35", 10),
        ["kitten35", "sitting35", "agent35", "angle35", "universe35", "memory35"],
    ),
    (
        ("kitten35 sitting35 agent35 angle35 universe35 memory35", 18),
        ["kitten35 sitting35", "agent35 angle35", "universe35", "memory35"],
    ),
    (
        ("kitten35 sitting35 agent35 angle35 universe35 memory35", 28),
        ["kitten35 sitting35 agent35", "angle35 universe35 memory35"],
    ),
    (
        ("sitting35 agent35 angle35 universe35 memory35 stream35", 6),
        ["sitting35", "agent35", "angle35", "universe35", "memory35", "stream35"],
    ),
    (
        ("sitting35 agent35 angle35 universe35 memory35 stream35", 10),
        ["sitting35", "agent35", "angle35", "universe35", "memory35", "stream35"],
    ),
    (
        ("sitting35 agent35 angle35 universe35 memory35 stream35", 18),
        ["sitting35 agent35", "angle35 universe35", "memory35 stream35"],
    ),
    (
        ("sitting35 agent35 angle35 universe35 memory35 stream35", 28),
        ["sitting35 agent35 angle35", "universe35 memory35 stream35"],
    ),
    (
        ("agent35 angle35 universe35 memory35 stream35 context35", 6),
        ["agent35", "angle35", "universe35", "memory35", "stream35", "context35"],
    ),
    (
        ("agent35 angle35 universe35 memory35 stream35 context35", 10),
        ["agent35", "angle35", "universe35", "memory35", "stream35", "context35"],
    ),
    (
        ("agent35 angle35 universe35 memory35 stream35 context35", 18),
        ["agent35 angle35", "universe35", "memory35 stream35", "context35"],
    ),
    (
        ("agent35 angle35 universe35 memory35 stream35 context35", 28),
        ["agent35 angle35 universe35", "memory35 stream35 context35"],
    ),
    (
        ("angle35 universe35 memory35 stream35 context35 knowledge35", 6),
        ["angle35", "universe35", "memory35", "stream35", "context35", "knowledge35"],
    ),
    (
        ("angle35 universe35 memory35 stream35 context35 knowledge35", 10),
        ["angle35", "universe35", "memory35", "stream35", "context35", "knowledge35"],
    ),
    (
        ("angle35 universe35 memory35 stream35 context35 knowledge35", 18),
        ["angle35 universe35", "memory35 stream35", "context35", "knowledge35"],
    ),
    (
        ("angle35 universe35 memory35 stream35 context35 knowledge35", 28),
        ["angle35 universe35 memory35", "stream35 context35", "knowledge35"],
    ),
    (
        ("universe35 memory35 stream35 context35 knowledge35 vector35", 6),
        ["universe35", "memory35", "stream35", "context35", "knowledge35", "vector35"],
    ),
    (
        ("universe35 memory35 stream35 context35 knowledge35 vector35", 10),
        ["universe35", "memory35", "stream35", "context35", "knowledge35", "vector35"],
    ),
    (
        ("universe35 memory35 stream35 context35 knowledge35 vector35", 18),
        ["universe35", "memory35 stream35", "context35", "knowledge35", "vector35"],
    ),
    (
        ("universe35 memory35 stream35 context35 knowledge35 vector35", 28),
        ["universe35 memory35 stream35", "context35 knowledge35", "vector35"],
    ),
    (
        ("memory35 stream35 context35 knowledge35 vector35 processor35", 6),
        ["memory35", "stream35", "context35", "knowledge35", "vector35", "processor35"],
    ),
    (
        ("memory35 stream35 context35 knowledge35 vector35 processor35", 10),
        ["memory35", "stream35", "context35", "knowledge35", "vector35", "processor35"],
    ),
    (
        ("memory35 stream35 context35 knowledge35 vector35 processor35", 18),
        ["memory35 stream35", "context35", "knowledge35", "vector35", "processor35"],
    ),
    (
        ("memory35 stream35 context35 knowledge35 vector35 processor35", 28),
        ["memory35 stream35 context35", "knowledge35 vector35", "processor35"],
    ),
    (
        ("stream35 context35 knowledge35 vector35 processor35 reasoning35", 6),
        ["stream35", "context35", "knowledge35", "vector35", "processor35", "reasoning35"],
    ),
    (
        ("stream35 context35 knowledge35 vector35 processor35 reasoning35", 10),
        ["stream35", "context35", "knowledge35", "vector35", "processor35", "reasoning35"],
    ),
    (
        ("stream35 context35 knowledge35 vector35 processor35 reasoning35", 18),
        ["stream35 context35", "knowledge35", "vector35", "processor35", "reasoning35"],
    ),
    (
        ("stream35 context35 knowledge35 vector35 processor35 reasoning35", 28),
        ["stream35 context35", "knowledge35 vector35", "processor35 reasoning35"],
    ),
    (
        ("context35 knowledge35 vector35 processor35 reasoning35 machine35", 6),
        ["context35", "knowledge35", "vector35", "processor35", "reasoning35", "machine35"],
    ),
    (
        ("context35 knowledge35 vector35 processor35 reasoning35 machine35", 10),
        ["context35", "knowledge35", "vector35", "processor35", "reasoning35", "machine35"],
    ),
    (
        ("context35 knowledge35 vector35 processor35 reasoning35 machine35", 18),
        ["context35", "knowledge35", "vector35", "processor35", "reasoning35", "machine35"],
    ),
    (
        ("context35 knowledge35 vector35 processor35 reasoning35 machine35", 28),
        ["context35 knowledge35", "vector35 processor35", "reasoning35 machine35"],
    ),
    (
        ("knowledge35 vector35 processor35 reasoning35 machine35 learning35", 6),
        ["knowledge35", "vector35", "processor35", "reasoning35", "machine35", "learning35"],
    ),
    (
        ("knowledge35 vector35 processor35 reasoning35 machine35 learning35", 10),
        ["knowledge35", "vector35", "processor35", "reasoning35", "machine35", "learning35"],
    ),
    (
        ("knowledge35 vector35 processor35 reasoning35 machine35 learning35", 18),
        ["knowledge35", "vector35", "processor35", "reasoning35", "machine35", "learning35"],
    ),
    (
        ("knowledge35 vector35 processor35 reasoning35 machine35 learning35", 28),
        ["knowledge35 vector35", "processor35 reasoning35", "machine35 learning35"],
    ),
    (
        ("vector35 processor35 reasoning35 machine35 learning35 model35", 6),
        ["vector35", "processor35", "reasoning35", "machine35", "learning35", "model35"],
    ),
    (
        ("vector35 processor35 reasoning35 machine35 learning35 model35", 10),
        ["vector35", "processor35", "reasoning35", "machine35", "learning35", "model35"],
    ),
    (
        ("vector35 processor35 reasoning35 machine35 learning35 model35", 18),
        ["vector35", "processor35", "reasoning35", "machine35", "learning35 model35"],
    ),
    (
        ("vector35 processor35 reasoning35 machine35 learning35 model35", 28),
        ["vector35 processor35", "reasoning35 machine35", "learning35 model35"],
    ),
    (
        ("processor35 reasoning35 machine35 learning35 model35 token35", 6),
        ["processor35", "reasoning35", "machine35", "learning35", "model35", "token35"],
    ),
    (
        ("processor35 reasoning35 machine35 learning35 model35 token35", 10),
        ["processor35", "reasoning35", "machine35", "learning35", "model35", "token35"],
    ),
    (
        ("processor35 reasoning35 machine35 learning35 model35 token35", 18),
        ["processor35", "reasoning35", "machine35", "learning35 model35", "token35"],
    ),
    (
        ("processor35 reasoning35 machine35 learning35 model35 token35", 28),
        ["processor35 reasoning35", "machine35 learning35 model35", "token35"],
    ),
    (
        ("reasoning35 machine35 learning35 model35 token35 prompt35", 6),
        ["reasoning35", "machine35", "learning35", "model35", "token35", "prompt35"],
    ),
    (
        ("reasoning35 machine35 learning35 model35 token35 prompt35", 10),
        ["reasoning35", "machine35", "learning35", "model35", "token35", "prompt35"],
    ),
    (
        ("reasoning35 machine35 learning35 model35 token35 prompt35", 18),
        ["reasoning35", "machine35", "learning35 model35", "token35 prompt35"],
    ),
    (
        ("reasoning35 machine35 learning35 model35 token35 prompt35", 28),
        ["reasoning35 machine35", "learning35 model35 token35", "prompt35"],
    ),
    (
        ("machine35 learning35 model35 token35 prompt35 session35", 6),
        ["machine35", "learning35", "model35", "token35", "prompt35", "session35"],
    ),
    (
        ("machine35 learning35 model35 token35 prompt35 session35", 10),
        ["machine35", "learning35", "model35", "token35", "prompt35", "session35"],
    ),
    (
        ("machine35 learning35 model35 token35 prompt35 session35", 18),
        ["machine35", "learning35 model35", "token35 prompt35", "session35"],
    ),
    (
        ("machine35 learning35 model35 token35 prompt35 session35", 28),
        ["machine35 learning35 model35", "token35 prompt35 session35"],
    ),
    (
        ("learning35 model35 token35 prompt35 session35 library35", 6),
        ["learning35", "model35", "token35", "prompt35", "session35", "library35"],
    ),
    (
        ("learning35 model35 token35 prompt35 session35 library35", 10),
        ["learning35", "model35", "token35", "prompt35", "session35", "library35"],
    ),
    (
        ("learning35 model35 token35 prompt35 session35 library35", 18),
        ["learning35 model35", "token35 prompt35", "session35", "library35"],
    ),
    (
        ("learning35 model35 token35 prompt35 session35 library35", 28),
        ["learning35 model35 token35", "prompt35 session35 library35"],
    ),
    (
        ("model35 token35 prompt35 session35 library35 service35", 6),
        ["model35", "token35", "prompt35", "session35", "library35", "service35"],
    ),
    (
        ("model35 token35 prompt35 session35 library35 service35", 10),
        ["model35", "token35", "prompt35", "session35", "library35", "service35"],
    ),
    (
        ("model35 token35 prompt35 session35 library35 service35", 18),
        ["model35 token35", "prompt35 session35", "library35", "service35"],
    ),
    (
        ("model35 token35 prompt35 session35 library35 service35", 28),
        ["model35 token35 prompt35", "session35 library35", "service35"],
    ),
    (
        ("token35 prompt35 session35 library35 service35 gateway35", 6),
        ["token35", "prompt35", "session35", "library35", "service35", "gateway35"],
    ),
    (
        ("token35 prompt35 session35 library35 service35 gateway35", 10),
        ["token35", "prompt35", "session35", "library35", "service35", "gateway35"],
    ),
    (
        ("token35 prompt35 session35 library35 service35 gateway35", 18),
        ["token35 prompt35", "session35", "library35", "service35", "gateway35"],
    ),
    (
        ("token35 prompt35 session35 library35 service35 gateway35", 28),
        ["token35 prompt35 session35", "library35 service35", "gateway35"],
    ),
    (
        ("prompt35 session35 library35 service35 gateway35 storage35", 6),
        ["prompt35", "session35", "library35", "service35", "gateway35", "storage35"],
    ),
    (
        ("prompt35 session35 library35 service35 gateway35 storage35", 10),
        ["prompt35", "session35", "library35", "service35", "gateway35", "storage35"],
    ),
    (
        ("prompt35 session35 library35 service35 gateway35 storage35", 18),
        ["prompt35 session35", "library35", "service35", "gateway35", "storage35"],
    ),
    (
        ("prompt35 session35 library35 service35 gateway35 storage35", 28),
        ["prompt35 session35 library35", "service35 gateway35", "storage35"],
    ),
    (
        ("session35 library35 service35 gateway35 storage35 network35", 6),
        ["session35", "library35", "service35", "gateway35", "storage35", "network35"],
    ),
    (
        ("session35 library35 service35 gateway35 storage35 network35", 10),
        ["session35", "library35", "service35", "gateway35", "storage35", "network35"],
    ),
    (
        ("session35 library35 service35 gateway35 storage35 network35", 18),
        ["session35", "library35", "service35", "gateway35", "storage35", "network35"],
    ),
    (
        ("session35 library35 service35 gateway35 storage35 network35", 28),
        ["session35 library35", "service35 gateway35", "storage35 network35"],
    ),
    (
        ("library35 service35 gateway35 storage35 network35 latency35", 6),
        ["library35", "service35", "gateway35", "storage35", "network35", "latency35"],
    ),
    (
        ("library35 service35 gateway35 storage35 network35 latency35", 10),
        ["library35", "service35", "gateway35", "storage35", "network35", "latency35"],
    ),
    (
        ("library35 service35 gateway35 storage35 network35 latency35", 18),
        ["library35", "service35", "gateway35", "storage35", "network35", "latency35"],
    ),
    (
        ("library35 service35 gateway35 storage35 network35 latency35", 28),
        ["library35 service35", "gateway35 storage35", "network35 latency35"],
    ),
    (
        ("service35 gateway35 storage35 network35 latency35 buffer35", 6),
        ["service35", "gateway35", "storage35", "network35", "latency35", "buffer35"],
    ),
    (
        ("service35 gateway35 storage35 network35 latency35 buffer35", 10),
        ["service35", "gateway35", "storage35", "network35", "latency35", "buffer35"],
    ),
    (
        ("service35 gateway35 storage35 network35 latency35 buffer35", 18),
        ["service35", "gateway35", "storage35", "network35", "latency35 buffer35"],
    ),
    (
        ("service35 gateway35 storage35 network35 latency35 buffer35", 28),
        ["service35 gateway35", "storage35 network35", "latency35 buffer35"],
    ),
    (
        ("gateway35 storage35 network35 latency35 buffer35 queue35", 6),
        ["gateway35", "storage35", "network35", "latency35", "buffer35", "queue35"],
    ),
    (
        ("gateway35 storage35 network35 latency35 buffer35 queue35", 10),
        ["gateway35", "storage35", "network35", "latency35", "buffer35", "queue35"],
    ),
    (
        ("gateway35 storage35 network35 latency35 buffer35 queue35", 18),
        ["gateway35", "storage35", "network35", "latency35 buffer35", "queue35"],
    ),
    (
        ("gateway35 storage35 network35 latency35 buffer35 queue35", 28),
        ["gateway35 storage35", "network35 latency35 buffer35", "queue35"],
    ),
    (
        ("storage35 network35 latency35 buffer35 queue35 worker35", 6),
        ["storage35", "network35", "latency35", "buffer35", "queue35", "worker35"],
    ),
    (
        ("storage35 network35 latency35 buffer35 queue35 worker35", 10),
        ["storage35", "network35", "latency35", "buffer35", "queue35", "worker35"],
    ),
    (
        ("storage35 network35 latency35 buffer35 queue35 worker35", 18),
        ["storage35", "network35", "latency35 buffer35", "queue35 worker35"],
    ),
    (
        ("storage35 network35 latency35 buffer35 queue35 worker35", 28),
        ["storage35 network35", "latency35 buffer35 queue35", "worker35"],
    ),
    (
        ("network35 latency35 buffer35 queue35 worker35 kernel35", 6),
        ["network35", "latency35", "buffer35", "queue35", "worker35", "kernel35"],
    ),
    (
        ("network35 latency35 buffer35 queue35 worker35 kernel35", 10),
        ["network35", "latency35", "buffer35", "queue35", "worker35", "kernel35"],
    ),
    (
        ("network35 latency35 buffer35 queue35 worker35 kernel35", 18),
        ["network35", "latency35 buffer35", "queue35 worker35", "kernel35"],
    ),
    (
        ("network35 latency35 buffer35 queue35 worker35 kernel35", 28),
        ["network35 latency35 buffer35", "queue35 worker35 kernel35"],
    ),
    (
        ("latency35 buffer35 queue35 worker35 kernel35 signal35", 6),
        ["latency35", "buffer35", "queue35", "worker35", "kernel35", "signal35"],
    ),
    (
        ("latency35 buffer35 queue35 worker35 kernel35 signal35", 10),
        ["latency35", "buffer35", "queue35", "worker35", "kernel35", "signal35"],
    ),
    (
        ("latency35 buffer35 queue35 worker35 kernel35 signal35", 18),
        ["latency35 buffer35", "queue35 worker35", "kernel35 signal35"],
    ),
    (
        ("latency35 buffer35 queue35 worker35 kernel35 signal35", 28),
        ["latency35 buffer35 queue35", "worker35 kernel35 signal35"],
    ),
    (
        ("buffer35 queue35 worker35 kernel35 signal35 packet35", 6),
        ["buffer35", "queue35", "worker35", "kernel35", "signal35", "packet35"],
    ),
    (
        ("buffer35 queue35 worker35 kernel35 signal35 packet35", 10),
        ["buffer35", "queue35", "worker35", "kernel35", "signal35", "packet35"],
    ),
    (
        ("buffer35 queue35 worker35 kernel35 signal35 packet35", 18),
        ["buffer35 queue35", "worker35 kernel35", "signal35 packet35"],
    ),
    (
        ("buffer35 queue35 worker35 kernel35 signal35 packet35", 28),
        ["buffer35 queue35 worker35", "kernel35 signal35 packet35"],
    ),
    (
        ("queue35 worker35 kernel35 signal35 packet35 router35", 6),
        ["queue35", "worker35", "kernel35", "signal35", "packet35", "router35"],
    ),
    (
        ("queue35 worker35 kernel35 signal35 packet35 router35", 10),
        ["queue35", "worker35", "kernel35", "signal35", "packet35", "router35"],
    ),
    (
        ("queue35 worker35 kernel35 signal35 packet35 router35", 18),
        ["queue35 worker35", "kernel35 signal35", "packet35 router35"],
    ),
    (
        ("queue35 worker35 kernel35 signal35 packet35 router35", 28),
        ["queue35 worker35 kernel35", "signal35 packet35 router35"],
    ),
    (
        ("worker35 kernel35 signal35 packet35 router35 cluster35", 6),
        ["worker35", "kernel35", "signal35", "packet35", "router35", "cluster35"],
    ),
    (
        ("worker35 kernel35 signal35 packet35 router35 cluster35", 10),
        ["worker35", "kernel35", "signal35", "packet35", "router35", "cluster35"],
    ),
    (
        ("worker35 kernel35 signal35 packet35 router35 cluster35", 18),
        ["worker35 kernel35", "signal35 packet35", "router35 cluster35"],
    ),
    (
        ("worker35 kernel35 signal35 packet35 router35 cluster35", 28),
        ["worker35 kernel35 signal35", "packet35 router35 cluster35"],
    ),
    (
        ("kernel35 signal35 packet35 router35 cluster35 mirror35", 6),
        ["kernel35", "signal35", "packet35", "router35", "cluster35", "mirror35"],
    ),
    (
        ("kernel35 signal35 packet35 router35 cluster35 mirror35", 10),
        ["kernel35", "signal35", "packet35", "router35", "cluster35", "mirror35"],
    ),
    (
        ("kernel35 signal35 packet35 router35 cluster35 mirror35", 18),
        ["kernel35 signal35", "packet35 router35", "cluster35 mirror35"],
    ),
    (
        ("kernel35 signal35 packet35 router35 cluster35 mirror35", 28),
        ["kernel35 signal35 packet35", "router35 cluster35 mirror35"],
    ),
    (
        ("signal35 packet35 router35 cluster35 mirror35 filter35", 6),
        ["signal35", "packet35", "router35", "cluster35", "mirror35", "filter35"],
    ),
    (
        ("signal35 packet35 router35 cluster35 mirror35 filter35", 10),
        ["signal35", "packet35", "router35", "cluster35", "mirror35", "filter35"],
    ),
    (
        ("signal35 packet35 router35 cluster35 mirror35 filter35", 18),
        ["signal35 packet35", "router35 cluster35", "mirror35 filter35"],
    ),
    (
        ("signal35 packet35 router35 cluster35 mirror35 filter35", 28),
        ["signal35 packet35 router35", "cluster35 mirror35 filter35"],
    ),
    (
        ("packet35 router35 cluster35 mirror35 filter35 ranking35", 6),
        ["packet35", "router35", "cluster35", "mirror35", "filter35", "ranking35"],
    ),
    (
        ("packet35 router35 cluster35 mirror35 filter35 ranking35", 10),
        ["packet35", "router35", "cluster35", "mirror35", "filter35", "ranking35"],
    ),
    (
        ("packet35 router35 cluster35 mirror35 filter35 ranking35", 18),
        ["packet35 router35", "cluster35 mirror35", "filter35 ranking35"],
    ),
    (
        ("packet35 router35 cluster35 mirror35 filter35 ranking35", 28),
        ["packet35 router35 cluster35", "mirror35 filter35 ranking35"],
    ),
    (
        ("router35 cluster35 mirror35 filter35 ranking35 encoding35", 6),
        ["router35", "cluster35", "mirror35", "filter35", "ranking35", "encoding35"],
    ),
    (
        ("router35 cluster35 mirror35 filter35 ranking35 encoding35", 10),
        ["router35", "cluster35", "mirror35", "filter35", "ranking35", "encoding35"],
    ),
    (
        ("router35 cluster35 mirror35 filter35 ranking35 encoding35", 18),
        ["router35 cluster35", "mirror35 filter35", "ranking35", "encoding35"],
    ),
    (
        ("router35 cluster35 mirror35 filter35 ranking35 encoding35", 28),
        ["router35 cluster35 mirror35", "filter35 ranking35", "encoding35"],
    ),
    (
        ("cluster35 mirror35 filter35 ranking35 encoding35 mapping35", 6),
        ["cluster35", "mirror35", "filter35", "ranking35", "encoding35", "mapping35"],
    ),
    (
        ("cluster35 mirror35 filter35 ranking35 encoding35 mapping35", 10),
        ["cluster35", "mirror35", "filter35", "ranking35", "encoding35", "mapping35"],
    ),
    (
        ("cluster35 mirror35 filter35 ranking35 encoding35 mapping35", 18),
        ["cluster35 mirror35", "filter35 ranking35", "encoding35", "mapping35"],
    ),
    (
        ("cluster35 mirror35 filter35 ranking35 encoding35 mapping35", 28),
        ["cluster35 mirror35 filter35", "ranking35 encoding35", "mapping35"],
    ),
    (
        ("mirror35 filter35 ranking35 encoding35 mapping35 record35", 6),
        ["mirror35", "filter35", "ranking35", "encoding35", "mapping35", "record35"],
    ),
    (
        ("mirror35 filter35 ranking35 encoding35 mapping35 record35", 10),
        ["mirror35", "filter35", "ranking35", "encoding35", "mapping35", "record35"],
    ),
    (
        ("mirror35 filter35 ranking35 encoding35 mapping35 record35", 18),
        ["mirror35 filter35", "ranking35", "encoding35", "mapping35 record35"],
    ),
    (
        ("mirror35 filter35 ranking35 encoding35 mapping35 record35", 28),
        ["mirror35 filter35 ranking35", "encoding35 mapping35", "record35"],
    ),
    (
        ("filter35 ranking35 encoding35 mapping35 record35 candle35", 6),
        ["filter35", "ranking35", "encoding35", "mapping35", "record35", "candle35"],
    ),
    (
        ("filter35 ranking35 encoding35 mapping35 record35 candle35", 10),
        ["filter35", "ranking35", "encoding35", "mapping35", "record35", "candle35"],
    ),
    (
        ("filter35 ranking35 encoding35 mapping35 record35 candle35", 18),
        ["filter35 ranking35", "encoding35", "mapping35 record35", "candle35"],
    ),
    (
        ("filter35 ranking35 encoding35 mapping35 record35 candle35", 28),
        ["filter35 ranking35", "encoding35 mapping35", "record35 candle35"],
    ),
    (
        ("ranking35 encoding35 mapping35 record35 candle35 thread35", 6),
        ["ranking35", "encoding35", "mapping35", "record35", "candle35", "thread35"],
    ),
    (
        ("ranking35 encoding35 mapping35 record35 candle35 thread35", 10),
        ["ranking35", "encoding35", "mapping35", "record35", "candle35", "thread35"],
    ),
    (
        ("ranking35 encoding35 mapping35 record35 candle35 thread35", 18),
        ["ranking35", "encoding35", "mapping35 record35", "candle35 thread35"],
    ),
    (
        ("ranking35 encoding35 mapping35 record35 candle35 thread35", 28),
        ["ranking35 encoding35", "mapping35 record35 candle35", "thread35"],
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
