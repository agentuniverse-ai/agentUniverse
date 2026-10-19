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
        ("round 75: the quick brown fox jumps over the lazy dog", 4),
        ["round", "75:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 75: the quick brown fox jumps over the lazy dog", 8),
        ["round", "75: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 75: the quick brown fox jumps over the lazy dog", 12),
        ["round 75:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 75: the quick brown fox jumps over the lazy dog", 16),
        ["round 75: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 75: the quick brown fox jumps over the lazy dog", 24),
        ["round 75: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 75: the quick brown fox jumps over the lazy dog", 32),
        ["round 75: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 75: agentuniverse is a framework for multi agents", 4),
        ["round", "75:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 75: agentuniverse is a framework for multi agents", 8),
        ["round", "75:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 75: agentuniverse is a framework for multi agents", 12),
        ["round 75:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 75: agentuniverse is a framework for multi agents", 16),
        ["round 75:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 75: agentuniverse is a framework for multi agents", 24),
        ["round 75: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 75: agentuniverse is a framework for multi agents", 32),
        ["round 75: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 75: knowledge stored as vectors enables retrieval", 4),
        ["round", "75:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 75: knowledge stored as vectors enables retrieval", 8),
        ["round", "75:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 75: knowledge stored as vectors enables retrieval", 12),
        ["round 75:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 75: knowledge stored as vectors enables retrieval", 16),
        ["round 75:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 75: knowledge stored as vectors enables retrieval", 24),
        ["round 75: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 75: knowledge stored as vectors enables retrieval", 32),
        ["round 75: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 75: the processor reads the record then stops", 4),
        ["round", "75:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 75: the processor reads the record then stops", 8),
        ["round", "75: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 75: the processor reads the record then stops", 12),
        ["round 75:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 75: the processor reads the record then stops", 16),
        ["round 75: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 75: the processor reads the record then stops", 24),
        ["round 75: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 75: the processor reads the record then stops", 32),
        ["round 75: the processor reads", "the record then stops"],
    ),
    (
        ("round 75: a worker pulls the next task from the queue", 4),
        ["round", "75:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 75: a worker pulls the next task from the queue", 8),
        ["round", "75: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 75: a worker pulls the next task from the queue", 12),
        ["round 75: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 75: a worker pulls the next task from the queue", 16),
        ["round 75: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 75: a worker pulls the next task from the queue", 24),
        ["round 75: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 75: a worker pulls the next task from the queue", 32),
        ["round 75: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 75: signals travel through the network layer", 4),
        ["round", "75:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 75: signals travel through the network layer", 8),
        ["round", "75:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 75: signals travel through the network layer", 12),
        ["round 75:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 75: signals travel through the network layer", 16),
        ["round 75:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 75: signals travel through the network layer", 24),
        ["round 75: signals travel", "through the network", "layer"],
    ),
    (
        ("round 75: signals travel through the network layer", 32),
        ["round 75: signals travel through", "the network layer"],
    ),
    (
        ("round 75: the gateway routes each request by policy", 4),
        ["round", "75:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 75: the gateway routes each request by policy", 8),
        ["round", "75: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 75: the gateway routes each request by policy", 12),
        ["round 75:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 75: the gateway routes each request by policy", 16),
        ["round 75: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 75: the gateway routes each request by policy", 24),
        ["round 75: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 75: the gateway routes each request by policy", 32),
        ["round 75: the gateway routes", "each request by policy"],
    ),
    (
        ("round 75: memory grows until the buffer is full", 4),
        ["round", "75:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 75: memory grows until the buffer is full", 8),
        ["round", "75:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 75: memory grows until the buffer is full", 12),
        ["round 75:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 75: memory grows until the buffer is full", 16),
        ["round 75: memory", "grows until the", "buffer is full"],
    ),
    (("round 75: memory grows until the buffer is full", 24), ["round 75: memory grows", "until the buffer is full"]),
    (("round 75: memory grows until the buffer is full", 32), ["round 75: memory grows until the", "buffer is full"]),
    (
        ("round 75: the cluster mirrors every packet twice", 4),
        ["round", "75:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 75: the cluster mirrors every packet twice", 8),
        ["round", "75: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 75: the cluster mirrors every packet twice", 12),
        ["round 75:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 75: the cluster mirrors every packet twice", 16),
        ["round 75: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 75: the cluster mirrors every packet twice", 24),
        ["round 75: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 75: the cluster mirrors every packet twice", 32), ["round 75: the cluster mirrors", "every packet twice"]),
    (
        ("round 75: ranking uses tokens learned from the corpus", 4),
        ["round", "75:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 75: ranking uses tokens learned from the corpus", 8),
        ["round", "75:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 75: ranking uses tokens learned from the corpus", 12),
        ["round 75:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 75: ranking uses tokens learned from the corpus", 16),
        ["round 75:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 75: ranking uses tokens learned from the corpus", 24),
        ["round 75: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 75: ranking uses tokens learned from the corpus", 32),
        ["round 75: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 75: a long session ends when the candle dies", 4),
        ["round", "75:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 75: a long session ends when the candle dies", 8),
        ["round", "75: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 75: a long session ends when the candle dies", 12),
        ["round 75: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 75: a long session ends when the candle dies", 16),
        ["round 75: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 75: a long session ends when the candle dies", 24),
        ["round 75: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 75: a long session ends when the candle dies", 32),
        ["round 75: a long session ends", "when the candle dies"],
    ),
    (
        ("round 75: encode the prompt then map the result", 4),
        ["round", "75:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 75: encode the prompt then map the result", 8),
        ["round", "75:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 75: encode the prompt then map the result", 12),
        ["round 75:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 75: encode the prompt then map the result", 16),
        ["round 75: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 75: encode the prompt then map the result", 24),
        ["round 75: encode the", "prompt then map the", "result"],
    ),
    (("round 75: encode the prompt then map the result", 32), ["round 75: encode the prompt then", "map the result"]),
    (
        ("round 75: the kernel wakes the worker at dawn", 4),
        ["round", "75:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 75: the kernel wakes the worker at dawn", 8),
        ["round", "75: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 75: the kernel wakes the worker at dawn", 12),
        ["round 75:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 75: the kernel wakes the worker at dawn", 16), ["round 75: the", "kernel wakes the", "worker at dawn"]),
    (("round 75: the kernel wakes the worker at dawn", 24), ["round 75: the kernel", "wakes the worker at dawn"]),
    (("round 75: the kernel wakes the worker at dawn", 32), ["round 75: the kernel wakes the", "worker at dawn"]),
    (
        ("round 75: service latency drops after the patch", 4),
        ["round", "75:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 75: service latency drops after the patch", 8),
        ["round", "75:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 75: service latency drops after the patch", 12),
        ["round 75:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 75: service latency drops after the patch", 16),
        ["round 75:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 75: service latency drops after the patch", 24),
        ["round 75: service", "latency drops after the", "patch"],
    ),
    (("round 75: service latency drops after the patch", 32), ["round 75: service latency drops", "after the patch"]),
    (
        ("round 75: the library caches every vector it sees", 4),
        ["round", "75:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 75: the library caches every vector it sees", 8),
        ["round", "75: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 75: the library caches every vector it sees", 12),
        ["round 75:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 75: the library caches every vector it sees", 16),
        ["round 75: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 75: the library caches every vector it sees", 24),
        ["round 75: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 75: the library caches every vector it sees", 32),
        ["round 75: the library caches", "every vector it sees"],
    ),
    (
        ("round 75: agents argue then the debate resolves", 4),
        ["round", "75:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 75: agents argue then the debate resolves", 8),
        ["round", "75:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 75: agents argue then the debate resolves", 12),
        ["round 75:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 75: agents argue then the debate resolves", 16),
        ["round 75: agents", "argue then the", "debate resolves"],
    ),
    (("round 75: agents argue then the debate resolves", 24), ["round 75: agents argue", "then the debate resolves"]),
    (("round 75: agents argue then the debate resolves", 32), ["round 75: agents argue then the", "debate resolves"]),
    (
        ("round 75: the filter keeps only strong matches", 4),
        ["round", "75:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 75: the filter keeps only strong matches", 8),
        ["round", "75: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 75: the filter keeps only strong matches", 12),
        ["round 75:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 75: the filter keeps only strong matches", 16),
        ["round 75: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 75: the filter keeps only strong matches", 24), ["round 75: the filter", "keeps only strong", "matches"]),
    (("round 75: the filter keeps only strong matches", 32), ["round 75: the filter keeps only", "strong matches"]),
    (
        ("round 75: the model answers with a short reply", 4),
        ["round", "75:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 75: the model answers with a short reply", 8),
        ["round", "75: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 75: the model answers with a short reply", 12),
        ["round 75:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 75: the model answers with a short reply", 16),
        ["round 75: the", "model answers", "with a short", "reply"],
    ),
    (("round 75: the model answers with a short reply", 24), ["round 75: the model", "answers with a short", "reply"]),
    (("round 75: the model answers with a short reply", 32), ["round 75: the model answers with", "a short reply"]),
    (
        ("round 75: the recorder stores the reasoning trace", 4),
        ["round", "75:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 75: the recorder stores the reasoning trace", 8),
        ["round", "75: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 75: the recorder stores the reasoning trace", 12),
        ["round 75:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 75: the recorder stores the reasoning trace", 16),
        ["round 75: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 75: the recorder stores the reasoning trace", 24),
        ["round 75: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 75: the recorder stores the reasoning trace", 32),
        ["round 75: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 75: the angel watches the processor run", 4),
        ["round", "75:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 75: the angel watches the processor run", 8),
        ["round", "75: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 75: the angel watches the processor run", 12),
        ["round 75:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 75: the angel watches the processor run", 16), ["round 75: the", "angel watches", "the processor", "run"]),
    (("round 75: the angel watches the processor run", 24), ["round 75: the angel", "watches the processor", "run"]),
    (("round 75: the angel watches the processor run", 32), ["round 75: the angel watches the", "processor run"]),
    (
        ("round 75: angle of the vector decides the match", 4),
        ["round", "75:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 75: angle of the vector decides the match", 8),
        ["round", "75:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 75: angle of the vector decides the match", 12),
        ["round 75:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 75: angle of the vector decides the match", 16),
        ["round 75: angle", "of the vector", "decides the", "match"],
    ),
    (("round 75: angle of the vector decides the match", 24), ["round 75: angle of the", "vector decides the match"]),
    (("round 75: angle of the vector decides the match", 32), ["round 75: angle of the vector", "decides the match"]),
    (
        ("round 75: the candle burns twice as long at night", 4),
        ["round", "75:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 75: the candle burns twice as long at night", 8),
        ["round", "75: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 75: the candle burns twice as long at night", 12),
        ["round 75:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 75: the candle burns twice as long at night", 16),
        ["round 75: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 75: the candle burns twice as long at night", 24),
        ["round 75: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 75: the candle burns twice as long at night", 32),
        ["round 75: the candle burns twice", "as long at night"],
    ),
    (
        ("round 75: a mirror of the universe in one line", 4),
        ["round", "75:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 75: a mirror of the universe in one line", 8),
        ["round", "75: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 75: a mirror of the universe in one line", 12),
        ["round 75: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 75: a mirror of the universe in one line", 16),
        ["round 75: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 75: a mirror of the universe in one line", 24), ["round 75: a mirror of", "the universe in one line"]),
    (("round 75: a mirror of the universe in one line", 32), ["round 75: a mirror of the", "universe in one line"]),
    (
        ("round 75: the queue drains before the storm", 4),
        ["round", "75:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 75: the queue drains before the storm", 8),
        ["round", "75: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 75: the queue drains before the storm", 12), ["round 75:", "the queue", "drains", "before the", "storm"]),
    (("round 75: the queue drains before the storm", 16), ["round 75: the", "queue drains", "before the storm"]),
    (("round 75: the queue drains before the storm", 24), ["round 75: the queue", "drains before the storm"]),
    (("round 75: the queue drains before the storm", 32), ["round 75: the queue drains", "before the storm"]),
    (
        ("kitten75 sitting75 agent75 angle75 universe75 memory75", 6),
        ["kitten75", "sitting75", "agent75", "angle75", "universe75", "memory75"],
    ),
    (
        ("kitten75 sitting75 agent75 angle75 universe75 memory75", 10),
        ["kitten75", "sitting75", "agent75", "angle75", "universe75", "memory75"],
    ),
    (
        ("kitten75 sitting75 agent75 angle75 universe75 memory75", 18),
        ["kitten75 sitting75", "agent75 angle75", "universe75", "memory75"],
    ),
    (
        ("kitten75 sitting75 agent75 angle75 universe75 memory75", 28),
        ["kitten75 sitting75 agent75", "angle75 universe75 memory75"],
    ),
    (
        ("sitting75 agent75 angle75 universe75 memory75 stream75", 6),
        ["sitting75", "agent75", "angle75", "universe75", "memory75", "stream75"],
    ),
    (
        ("sitting75 agent75 angle75 universe75 memory75 stream75", 10),
        ["sitting75", "agent75", "angle75", "universe75", "memory75", "stream75"],
    ),
    (
        ("sitting75 agent75 angle75 universe75 memory75 stream75", 18),
        ["sitting75 agent75", "angle75 universe75", "memory75 stream75"],
    ),
    (
        ("sitting75 agent75 angle75 universe75 memory75 stream75", 28),
        ["sitting75 agent75 angle75", "universe75 memory75 stream75"],
    ),
    (
        ("agent75 angle75 universe75 memory75 stream75 context75", 6),
        ["agent75", "angle75", "universe75", "memory75", "stream75", "context75"],
    ),
    (
        ("agent75 angle75 universe75 memory75 stream75 context75", 10),
        ["agent75", "angle75", "universe75", "memory75", "stream75", "context75"],
    ),
    (
        ("agent75 angle75 universe75 memory75 stream75 context75", 18),
        ["agent75 angle75", "universe75", "memory75 stream75", "context75"],
    ),
    (
        ("agent75 angle75 universe75 memory75 stream75 context75", 28),
        ["agent75 angle75 universe75", "memory75 stream75 context75"],
    ),
    (
        ("angle75 universe75 memory75 stream75 context75 knowledge75", 6),
        ["angle75", "universe75", "memory75", "stream75", "context75", "knowledge75"],
    ),
    (
        ("angle75 universe75 memory75 stream75 context75 knowledge75", 10),
        ["angle75", "universe75", "memory75", "stream75", "context75", "knowledge75"],
    ),
    (
        ("angle75 universe75 memory75 stream75 context75 knowledge75", 18),
        ["angle75 universe75", "memory75 stream75", "context75", "knowledge75"],
    ),
    (
        ("angle75 universe75 memory75 stream75 context75 knowledge75", 28),
        ["angle75 universe75 memory75", "stream75 context75", "knowledge75"],
    ),
    (
        ("universe75 memory75 stream75 context75 knowledge75 vector75", 6),
        ["universe75", "memory75", "stream75", "context75", "knowledge75", "vector75"],
    ),
    (
        ("universe75 memory75 stream75 context75 knowledge75 vector75", 10),
        ["universe75", "memory75", "stream75", "context75", "knowledge75", "vector75"],
    ),
    (
        ("universe75 memory75 stream75 context75 knowledge75 vector75", 18),
        ["universe75", "memory75 stream75", "context75", "knowledge75", "vector75"],
    ),
    (
        ("universe75 memory75 stream75 context75 knowledge75 vector75", 28),
        ["universe75 memory75 stream75", "context75 knowledge75", "vector75"],
    ),
    (
        ("memory75 stream75 context75 knowledge75 vector75 processor75", 6),
        ["memory75", "stream75", "context75", "knowledge75", "vector75", "processor75"],
    ),
    (
        ("memory75 stream75 context75 knowledge75 vector75 processor75", 10),
        ["memory75", "stream75", "context75", "knowledge75", "vector75", "processor75"],
    ),
    (
        ("memory75 stream75 context75 knowledge75 vector75 processor75", 18),
        ["memory75 stream75", "context75", "knowledge75", "vector75", "processor75"],
    ),
    (
        ("memory75 stream75 context75 knowledge75 vector75 processor75", 28),
        ["memory75 stream75 context75", "knowledge75 vector75", "processor75"],
    ),
    (
        ("stream75 context75 knowledge75 vector75 processor75 reasoning75", 6),
        ["stream75", "context75", "knowledge75", "vector75", "processor75", "reasoning75"],
    ),
    (
        ("stream75 context75 knowledge75 vector75 processor75 reasoning75", 10),
        ["stream75", "context75", "knowledge75", "vector75", "processor75", "reasoning75"],
    ),
    (
        ("stream75 context75 knowledge75 vector75 processor75 reasoning75", 18),
        ["stream75 context75", "knowledge75", "vector75", "processor75", "reasoning75"],
    ),
    (
        ("stream75 context75 knowledge75 vector75 processor75 reasoning75", 28),
        ["stream75 context75", "knowledge75 vector75", "processor75 reasoning75"],
    ),
    (
        ("context75 knowledge75 vector75 processor75 reasoning75 machine75", 6),
        ["context75", "knowledge75", "vector75", "processor75", "reasoning75", "machine75"],
    ),
    (
        ("context75 knowledge75 vector75 processor75 reasoning75 machine75", 10),
        ["context75", "knowledge75", "vector75", "processor75", "reasoning75", "machine75"],
    ),
    (
        ("context75 knowledge75 vector75 processor75 reasoning75 machine75", 18),
        ["context75", "knowledge75", "vector75", "processor75", "reasoning75", "machine75"],
    ),
    (
        ("context75 knowledge75 vector75 processor75 reasoning75 machine75", 28),
        ["context75 knowledge75", "vector75 processor75", "reasoning75 machine75"],
    ),
    (
        ("knowledge75 vector75 processor75 reasoning75 machine75 learning75", 6),
        ["knowledge75", "vector75", "processor75", "reasoning75", "machine75", "learning75"],
    ),
    (
        ("knowledge75 vector75 processor75 reasoning75 machine75 learning75", 10),
        ["knowledge75", "vector75", "processor75", "reasoning75", "machine75", "learning75"],
    ),
    (
        ("knowledge75 vector75 processor75 reasoning75 machine75 learning75", 18),
        ["knowledge75", "vector75", "processor75", "reasoning75", "machine75", "learning75"],
    ),
    (
        ("knowledge75 vector75 processor75 reasoning75 machine75 learning75", 28),
        ["knowledge75 vector75", "processor75 reasoning75", "machine75 learning75"],
    ),
    (
        ("vector75 processor75 reasoning75 machine75 learning75 model75", 6),
        ["vector75", "processor75", "reasoning75", "machine75", "learning75", "model75"],
    ),
    (
        ("vector75 processor75 reasoning75 machine75 learning75 model75", 10),
        ["vector75", "processor75", "reasoning75", "machine75", "learning75", "model75"],
    ),
    (
        ("vector75 processor75 reasoning75 machine75 learning75 model75", 18),
        ["vector75", "processor75", "reasoning75", "machine75", "learning75 model75"],
    ),
    (
        ("vector75 processor75 reasoning75 machine75 learning75 model75", 28),
        ["vector75 processor75", "reasoning75 machine75", "learning75 model75"],
    ),
    (
        ("processor75 reasoning75 machine75 learning75 model75 token75", 6),
        ["processor75", "reasoning75", "machine75", "learning75", "model75", "token75"],
    ),
    (
        ("processor75 reasoning75 machine75 learning75 model75 token75", 10),
        ["processor75", "reasoning75", "machine75", "learning75", "model75", "token75"],
    ),
    (
        ("processor75 reasoning75 machine75 learning75 model75 token75", 18),
        ["processor75", "reasoning75", "machine75", "learning75 model75", "token75"],
    ),
    (
        ("processor75 reasoning75 machine75 learning75 model75 token75", 28),
        ["processor75 reasoning75", "machine75 learning75 model75", "token75"],
    ),
    (
        ("reasoning75 machine75 learning75 model75 token75 prompt75", 6),
        ["reasoning75", "machine75", "learning75", "model75", "token75", "prompt75"],
    ),
    (
        ("reasoning75 machine75 learning75 model75 token75 prompt75", 10),
        ["reasoning75", "machine75", "learning75", "model75", "token75", "prompt75"],
    ),
    (
        ("reasoning75 machine75 learning75 model75 token75 prompt75", 18),
        ["reasoning75", "machine75", "learning75 model75", "token75 prompt75"],
    ),
    (
        ("reasoning75 machine75 learning75 model75 token75 prompt75", 28),
        ["reasoning75 machine75", "learning75 model75 token75", "prompt75"],
    ),
    (
        ("machine75 learning75 model75 token75 prompt75 session75", 6),
        ["machine75", "learning75", "model75", "token75", "prompt75", "session75"],
    ),
    (
        ("machine75 learning75 model75 token75 prompt75 session75", 10),
        ["machine75", "learning75", "model75", "token75", "prompt75", "session75"],
    ),
    (
        ("machine75 learning75 model75 token75 prompt75 session75", 18),
        ["machine75", "learning75 model75", "token75 prompt75", "session75"],
    ),
    (
        ("machine75 learning75 model75 token75 prompt75 session75", 28),
        ["machine75 learning75 model75", "token75 prompt75 session75"],
    ),
    (
        ("learning75 model75 token75 prompt75 session75 library75", 6),
        ["learning75", "model75", "token75", "prompt75", "session75", "library75"],
    ),
    (
        ("learning75 model75 token75 prompt75 session75 library75", 10),
        ["learning75", "model75", "token75", "prompt75", "session75", "library75"],
    ),
    (
        ("learning75 model75 token75 prompt75 session75 library75", 18),
        ["learning75 model75", "token75 prompt75", "session75", "library75"],
    ),
    (
        ("learning75 model75 token75 prompt75 session75 library75", 28),
        ["learning75 model75 token75", "prompt75 session75 library75"],
    ),
    (
        ("model75 token75 prompt75 session75 library75 service75", 6),
        ["model75", "token75", "prompt75", "session75", "library75", "service75"],
    ),
    (
        ("model75 token75 prompt75 session75 library75 service75", 10),
        ["model75", "token75", "prompt75", "session75", "library75", "service75"],
    ),
    (
        ("model75 token75 prompt75 session75 library75 service75", 18),
        ["model75 token75", "prompt75 session75", "library75", "service75"],
    ),
    (
        ("model75 token75 prompt75 session75 library75 service75", 28),
        ["model75 token75 prompt75", "session75 library75", "service75"],
    ),
    (
        ("token75 prompt75 session75 library75 service75 gateway75", 6),
        ["token75", "prompt75", "session75", "library75", "service75", "gateway75"],
    ),
    (
        ("token75 prompt75 session75 library75 service75 gateway75", 10),
        ["token75", "prompt75", "session75", "library75", "service75", "gateway75"],
    ),
    (
        ("token75 prompt75 session75 library75 service75 gateway75", 18),
        ["token75 prompt75", "session75", "library75", "service75", "gateway75"],
    ),
    (
        ("token75 prompt75 session75 library75 service75 gateway75", 28),
        ["token75 prompt75 session75", "library75 service75", "gateway75"],
    ),
    (
        ("prompt75 session75 library75 service75 gateway75 storage75", 6),
        ["prompt75", "session75", "library75", "service75", "gateway75", "storage75"],
    ),
    (
        ("prompt75 session75 library75 service75 gateway75 storage75", 10),
        ["prompt75", "session75", "library75", "service75", "gateway75", "storage75"],
    ),
    (
        ("prompt75 session75 library75 service75 gateway75 storage75", 18),
        ["prompt75 session75", "library75", "service75", "gateway75", "storage75"],
    ),
    (
        ("prompt75 session75 library75 service75 gateway75 storage75", 28),
        ["prompt75 session75 library75", "service75 gateway75", "storage75"],
    ),
    (
        ("session75 library75 service75 gateway75 storage75 network75", 6),
        ["session75", "library75", "service75", "gateway75", "storage75", "network75"],
    ),
    (
        ("session75 library75 service75 gateway75 storage75 network75", 10),
        ["session75", "library75", "service75", "gateway75", "storage75", "network75"],
    ),
    (
        ("session75 library75 service75 gateway75 storage75 network75", 18),
        ["session75", "library75", "service75", "gateway75", "storage75", "network75"],
    ),
    (
        ("session75 library75 service75 gateway75 storage75 network75", 28),
        ["session75 library75", "service75 gateway75", "storage75 network75"],
    ),
    (
        ("library75 service75 gateway75 storage75 network75 latency75", 6),
        ["library75", "service75", "gateway75", "storage75", "network75", "latency75"],
    ),
    (
        ("library75 service75 gateway75 storage75 network75 latency75", 10),
        ["library75", "service75", "gateway75", "storage75", "network75", "latency75"],
    ),
    (
        ("library75 service75 gateway75 storage75 network75 latency75", 18),
        ["library75", "service75", "gateway75", "storage75", "network75", "latency75"],
    ),
    (
        ("library75 service75 gateway75 storage75 network75 latency75", 28),
        ["library75 service75", "gateway75 storage75", "network75 latency75"],
    ),
    (
        ("service75 gateway75 storage75 network75 latency75 buffer75", 6),
        ["service75", "gateway75", "storage75", "network75", "latency75", "buffer75"],
    ),
    (
        ("service75 gateway75 storage75 network75 latency75 buffer75", 10),
        ["service75", "gateway75", "storage75", "network75", "latency75", "buffer75"],
    ),
    (
        ("service75 gateway75 storage75 network75 latency75 buffer75", 18),
        ["service75", "gateway75", "storage75", "network75", "latency75 buffer75"],
    ),
    (
        ("service75 gateway75 storage75 network75 latency75 buffer75", 28),
        ["service75 gateway75", "storage75 network75", "latency75 buffer75"],
    ),
    (
        ("gateway75 storage75 network75 latency75 buffer75 queue75", 6),
        ["gateway75", "storage75", "network75", "latency75", "buffer75", "queue75"],
    ),
    (
        ("gateway75 storage75 network75 latency75 buffer75 queue75", 10),
        ["gateway75", "storage75", "network75", "latency75", "buffer75", "queue75"],
    ),
    (
        ("gateway75 storage75 network75 latency75 buffer75 queue75", 18),
        ["gateway75", "storage75", "network75", "latency75 buffer75", "queue75"],
    ),
    (
        ("gateway75 storage75 network75 latency75 buffer75 queue75", 28),
        ["gateway75 storage75", "network75 latency75 buffer75", "queue75"],
    ),
    (
        ("storage75 network75 latency75 buffer75 queue75 worker75", 6),
        ["storage75", "network75", "latency75", "buffer75", "queue75", "worker75"],
    ),
    (
        ("storage75 network75 latency75 buffer75 queue75 worker75", 10),
        ["storage75", "network75", "latency75", "buffer75", "queue75", "worker75"],
    ),
    (
        ("storage75 network75 latency75 buffer75 queue75 worker75", 18),
        ["storage75", "network75", "latency75 buffer75", "queue75 worker75"],
    ),
    (
        ("storage75 network75 latency75 buffer75 queue75 worker75", 28),
        ["storage75 network75", "latency75 buffer75 queue75", "worker75"],
    ),
    (
        ("network75 latency75 buffer75 queue75 worker75 kernel75", 6),
        ["network75", "latency75", "buffer75", "queue75", "worker75", "kernel75"],
    ),
    (
        ("network75 latency75 buffer75 queue75 worker75 kernel75", 10),
        ["network75", "latency75", "buffer75", "queue75", "worker75", "kernel75"],
    ),
    (
        ("network75 latency75 buffer75 queue75 worker75 kernel75", 18),
        ["network75", "latency75 buffer75", "queue75 worker75", "kernel75"],
    ),
    (
        ("network75 latency75 buffer75 queue75 worker75 kernel75", 28),
        ["network75 latency75 buffer75", "queue75 worker75 kernel75"],
    ),
    (
        ("latency75 buffer75 queue75 worker75 kernel75 signal75", 6),
        ["latency75", "buffer75", "queue75", "worker75", "kernel75", "signal75"],
    ),
    (
        ("latency75 buffer75 queue75 worker75 kernel75 signal75", 10),
        ["latency75", "buffer75", "queue75", "worker75", "kernel75", "signal75"],
    ),
    (
        ("latency75 buffer75 queue75 worker75 kernel75 signal75", 18),
        ["latency75 buffer75", "queue75 worker75", "kernel75 signal75"],
    ),
    (
        ("latency75 buffer75 queue75 worker75 kernel75 signal75", 28),
        ["latency75 buffer75 queue75", "worker75 kernel75 signal75"],
    ),
    (
        ("buffer75 queue75 worker75 kernel75 signal75 packet75", 6),
        ["buffer75", "queue75", "worker75", "kernel75", "signal75", "packet75"],
    ),
    (
        ("buffer75 queue75 worker75 kernel75 signal75 packet75", 10),
        ["buffer75", "queue75", "worker75", "kernel75", "signal75", "packet75"],
    ),
    (
        ("buffer75 queue75 worker75 kernel75 signal75 packet75", 18),
        ["buffer75 queue75", "worker75 kernel75", "signal75 packet75"],
    ),
    (
        ("buffer75 queue75 worker75 kernel75 signal75 packet75", 28),
        ["buffer75 queue75 worker75", "kernel75 signal75 packet75"],
    ),
    (
        ("queue75 worker75 kernel75 signal75 packet75 router75", 6),
        ["queue75", "worker75", "kernel75", "signal75", "packet75", "router75"],
    ),
    (
        ("queue75 worker75 kernel75 signal75 packet75 router75", 10),
        ["queue75", "worker75", "kernel75", "signal75", "packet75", "router75"],
    ),
    (
        ("queue75 worker75 kernel75 signal75 packet75 router75", 18),
        ["queue75 worker75", "kernel75 signal75", "packet75 router75"],
    ),
    (
        ("queue75 worker75 kernel75 signal75 packet75 router75", 28),
        ["queue75 worker75 kernel75", "signal75 packet75 router75"],
    ),
    (
        ("worker75 kernel75 signal75 packet75 router75 cluster75", 6),
        ["worker75", "kernel75", "signal75", "packet75", "router75", "cluster75"],
    ),
    (
        ("worker75 kernel75 signal75 packet75 router75 cluster75", 10),
        ["worker75", "kernel75", "signal75", "packet75", "router75", "cluster75"],
    ),
    (
        ("worker75 kernel75 signal75 packet75 router75 cluster75", 18),
        ["worker75 kernel75", "signal75 packet75", "router75 cluster75"],
    ),
    (
        ("worker75 kernel75 signal75 packet75 router75 cluster75", 28),
        ["worker75 kernel75 signal75", "packet75 router75 cluster75"],
    ),
    (
        ("kernel75 signal75 packet75 router75 cluster75 mirror75", 6),
        ["kernel75", "signal75", "packet75", "router75", "cluster75", "mirror75"],
    ),
    (
        ("kernel75 signal75 packet75 router75 cluster75 mirror75", 10),
        ["kernel75", "signal75", "packet75", "router75", "cluster75", "mirror75"],
    ),
    (
        ("kernel75 signal75 packet75 router75 cluster75 mirror75", 18),
        ["kernel75 signal75", "packet75 router75", "cluster75 mirror75"],
    ),
    (
        ("kernel75 signal75 packet75 router75 cluster75 mirror75", 28),
        ["kernel75 signal75 packet75", "router75 cluster75 mirror75"],
    ),
    (
        ("signal75 packet75 router75 cluster75 mirror75 filter75", 6),
        ["signal75", "packet75", "router75", "cluster75", "mirror75", "filter75"],
    ),
    (
        ("signal75 packet75 router75 cluster75 mirror75 filter75", 10),
        ["signal75", "packet75", "router75", "cluster75", "mirror75", "filter75"],
    ),
    (
        ("signal75 packet75 router75 cluster75 mirror75 filter75", 18),
        ["signal75 packet75", "router75 cluster75", "mirror75 filter75"],
    ),
    (
        ("signal75 packet75 router75 cluster75 mirror75 filter75", 28),
        ["signal75 packet75 router75", "cluster75 mirror75 filter75"],
    ),
    (
        ("packet75 router75 cluster75 mirror75 filter75 ranking75", 6),
        ["packet75", "router75", "cluster75", "mirror75", "filter75", "ranking75"],
    ),
    (
        ("packet75 router75 cluster75 mirror75 filter75 ranking75", 10),
        ["packet75", "router75", "cluster75", "mirror75", "filter75", "ranking75"],
    ),
    (
        ("packet75 router75 cluster75 mirror75 filter75 ranking75", 18),
        ["packet75 router75", "cluster75 mirror75", "filter75 ranking75"],
    ),
    (
        ("packet75 router75 cluster75 mirror75 filter75 ranking75", 28),
        ["packet75 router75 cluster75", "mirror75 filter75 ranking75"],
    ),
    (
        ("router75 cluster75 mirror75 filter75 ranking75 encoding75", 6),
        ["router75", "cluster75", "mirror75", "filter75", "ranking75", "encoding75"],
    ),
    (
        ("router75 cluster75 mirror75 filter75 ranking75 encoding75", 10),
        ["router75", "cluster75", "mirror75", "filter75", "ranking75", "encoding75"],
    ),
    (
        ("router75 cluster75 mirror75 filter75 ranking75 encoding75", 18),
        ["router75 cluster75", "mirror75 filter75", "ranking75", "encoding75"],
    ),
    (
        ("router75 cluster75 mirror75 filter75 ranking75 encoding75", 28),
        ["router75 cluster75 mirror75", "filter75 ranking75", "encoding75"],
    ),
    (
        ("cluster75 mirror75 filter75 ranking75 encoding75 mapping75", 6),
        ["cluster75", "mirror75", "filter75", "ranking75", "encoding75", "mapping75"],
    ),
    (
        ("cluster75 mirror75 filter75 ranking75 encoding75 mapping75", 10),
        ["cluster75", "mirror75", "filter75", "ranking75", "encoding75", "mapping75"],
    ),
    (
        ("cluster75 mirror75 filter75 ranking75 encoding75 mapping75", 18),
        ["cluster75 mirror75", "filter75 ranking75", "encoding75", "mapping75"],
    ),
    (
        ("cluster75 mirror75 filter75 ranking75 encoding75 mapping75", 28),
        ["cluster75 mirror75 filter75", "ranking75 encoding75", "mapping75"],
    ),
    (
        ("mirror75 filter75 ranking75 encoding75 mapping75 record75", 6),
        ["mirror75", "filter75", "ranking75", "encoding75", "mapping75", "record75"],
    ),
    (
        ("mirror75 filter75 ranking75 encoding75 mapping75 record75", 10),
        ["mirror75", "filter75", "ranking75", "encoding75", "mapping75", "record75"],
    ),
    (
        ("mirror75 filter75 ranking75 encoding75 mapping75 record75", 18),
        ["mirror75 filter75", "ranking75", "encoding75", "mapping75 record75"],
    ),
    (
        ("mirror75 filter75 ranking75 encoding75 mapping75 record75", 28),
        ["mirror75 filter75 ranking75", "encoding75 mapping75", "record75"],
    ),
    (
        ("filter75 ranking75 encoding75 mapping75 record75 candle75", 6),
        ["filter75", "ranking75", "encoding75", "mapping75", "record75", "candle75"],
    ),
    (
        ("filter75 ranking75 encoding75 mapping75 record75 candle75", 10),
        ["filter75", "ranking75", "encoding75", "mapping75", "record75", "candle75"],
    ),
    (
        ("filter75 ranking75 encoding75 mapping75 record75 candle75", 18),
        ["filter75 ranking75", "encoding75", "mapping75 record75", "candle75"],
    ),
    (
        ("filter75 ranking75 encoding75 mapping75 record75 candle75", 28),
        ["filter75 ranking75", "encoding75 mapping75", "record75 candle75"],
    ),
    (
        ("ranking75 encoding75 mapping75 record75 candle75 thread75", 6),
        ["ranking75", "encoding75", "mapping75", "record75", "candle75", "thread75"],
    ),
    (
        ("ranking75 encoding75 mapping75 record75 candle75 thread75", 10),
        ["ranking75", "encoding75", "mapping75", "record75", "candle75", "thread75"],
    ),
    (
        ("ranking75 encoding75 mapping75 record75 candle75 thread75", 18),
        ["ranking75", "encoding75", "mapping75 record75", "candle75 thread75"],
    ),
    (
        ("ranking75 encoding75 mapping75 record75 candle75 thread75", 28),
        ["ranking75 encoding75", "mapping75 record75 candle75", "thread75"],
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
