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
        ("round 166: the quick brown fox jumps over the lazy dog", 4),
        ["round", "166:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", 8),
        ["round", "166: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", 12),
        ["round 166:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", 16),
        ["round 166: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", 24),
        ["round 166: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 166: the quick brown fox jumps over the lazy dog", 32),
        ["round 166: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", 4),
        ["round", "166:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", 8),
        ["round", "166:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", 12),
        ["round 166:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", 16),
        ["round 166:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", 24),
        ["round 166: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 166: agentuniverse is a framework for multi agents", 32),
        ["round 166: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", 4),
        ["round", "166:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", 8),
        ["round", "166:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", 12),
        ["round 166:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", 16),
        ["round 166:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", 24),
        ["round 166: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 166: knowledge stored as vectors enables retrieval", 32),
        ["round 166: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 166: the processor reads the record then stops", 4),
        ["round", "166:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 166: the processor reads the record then stops", 8),
        ["round", "166: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 166: the processor reads the record then stops", 12),
        ["round 166:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 166: the processor reads the record then stops", 16),
        ["round 166: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 166: the processor reads the record then stops", 24),
        ["round 166: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 166: the processor reads the record then stops", 32),
        ["round 166: the processor reads", "the record then stops"],
    ),
    (
        ("round 166: a worker pulls the next task from the queue", 4),
        ["round", "166:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 166: a worker pulls the next task from the queue", 8),
        ["round", "166: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 166: a worker pulls the next task from the queue", 12),
        ["round 166: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 166: a worker pulls the next task from the queue", 16),
        ["round 166: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 166: a worker pulls the next task from the queue", 24),
        ["round 166: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 166: a worker pulls the next task from the queue", 32),
        ["round 166: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 166: signals travel through the network layer", 4),
        ["round", "166:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 166: signals travel through the network layer", 8),
        ["round", "166:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 166: signals travel through the network layer", 12),
        ["round 166:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 166: signals travel through the network layer", 16),
        ["round 166:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 166: signals travel through the network layer", 24),
        ["round 166: signals", "travel through the", "network layer"],
    ),
    (
        ("round 166: signals travel through the network layer", 32),
        ["round 166: signals travel", "through the network layer"],
    ),
    (
        ("round 166: the gateway routes each request by policy", 4),
        ["round", "166:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 166: the gateway routes each request by policy", 8),
        ["round", "166: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 166: the gateway routes each request by policy", 12),
        ["round 166:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 166: the gateway routes each request by policy", 16),
        ["round 166: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 166: the gateway routes each request by policy", 24),
        ["round 166: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 166: the gateway routes each request by policy", 32),
        ["round 166: the gateway routes", "each request by policy"],
    ),
    (
        ("round 166: memory grows until the buffer is full", 4),
        ["round", "166:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 166: memory grows until the buffer is full", 8),
        ["round", "166:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 166: memory grows until the buffer is full", 12),
        ["round 166:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 166: memory grows until the buffer is full", 16),
        ["round 166:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 166: memory grows until the buffer is full", 24), ["round 166: memory grows", "until the buffer is full"]),
    (("round 166: memory grows until the buffer is full", 32), ["round 166: memory grows until", "the buffer is full"]),
    (
        ("round 166: the cluster mirrors every packet twice", 4),
        ["round", "166:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 166: the cluster mirrors every packet twice", 8),
        ["round", "166: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 166: the cluster mirrors every packet twice", 12),
        ["round 166:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 166: the cluster mirrors every packet twice", 16),
        ["round 166: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 166: the cluster mirrors every packet twice", 24),
        ["round 166: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 166: the cluster mirrors every packet twice", 32),
        ["round 166: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", 4),
        ["round", "166:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", 8),
        ["round", "166:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", 12),
        ["round 166:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", 16),
        ["round 166:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", 24),
        ["round 166: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 166: ranking uses tokens learned from the corpus", 32),
        ["round 166: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 166: a long session ends when the candle dies", 4),
        ["round", "166:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 166: a long session ends when the candle dies", 8),
        ["round", "166: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 166: a long session ends when the candle dies", 12),
        ["round 166: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 166: a long session ends when the candle dies", 16),
        ["round 166: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 166: a long session ends when the candle dies", 24),
        ["round 166: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 166: a long session ends when the candle dies", 32),
        ["round 166: a long session ends", "when the candle dies"],
    ),
    (
        ("round 166: encode the prompt then map the result", 4),
        ["round", "166:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 166: encode the prompt then map the result", 8),
        ["round", "166:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 166: encode the prompt then map the result", 12),
        ["round 166:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 166: encode the prompt then map the result", 16),
        ["round 166:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 166: encode the prompt then map the result", 24),
        ["round 166: encode the", "prompt then map the", "result"],
    ),
    (("round 166: encode the prompt then map the result", 32), ["round 166: encode the prompt", "then map the result"]),
    (
        ("round 166: the kernel wakes the worker at dawn", 4),
        ["round", "166:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 166: the kernel wakes the worker at dawn", 8),
        ["round", "166: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 166: the kernel wakes the worker at dawn", 12),
        ["round 166:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 166: the kernel wakes the worker at dawn", 16), ["round 166: the", "kernel wakes the", "worker at dawn"]),
    (("round 166: the kernel wakes the worker at dawn", 24), ["round 166: the kernel", "wakes the worker at dawn"]),
    (("round 166: the kernel wakes the worker at dawn", 32), ["round 166: the kernel wakes the", "worker at dawn"]),
    (
        ("round 166: service latency drops after the patch", 4),
        ["round", "166:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 166: service latency drops after the patch", 8),
        ["round", "166:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 166: service latency drops after the patch", 12),
        ["round 166:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 166: service latency drops after the patch", 16),
        ["round 166:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 166: service latency drops after the patch", 24),
        ["round 166: service", "latency drops after the", "patch"],
    ),
    (("round 166: service latency drops after the patch", 32), ["round 166: service latency drops", "after the patch"]),
    (
        ("round 166: the library caches every vector it sees", 4),
        ["round", "166:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 166: the library caches every vector it sees", 8),
        ["round", "166: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 166: the library caches every vector it sees", 12),
        ["round 166:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 166: the library caches every vector it sees", 16),
        ["round 166: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 166: the library caches every vector it sees", 24),
        ["round 166: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 166: the library caches every vector it sees", 32),
        ["round 166: the library caches", "every vector it sees"],
    ),
    (
        ("round 166: agents argue then the debate resolves", 4),
        ["round", "166:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 166: agents argue then the debate resolves", 8),
        ["round", "166:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 166: agents argue then the debate resolves", 12),
        ["round 166:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 166: agents argue then the debate resolves", 16),
        ["round 166:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 166: agents argue then the debate resolves", 24), ["round 166: agents argue", "then the debate resolves"]),
    (("round 166: agents argue then the debate resolves", 32), ["round 166: agents argue then the", "debate resolves"]),
    (
        ("round 166: the filter keeps only strong matches", 4),
        ["round", "166:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 166: the filter keeps only strong matches", 8),
        ["round", "166: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 166: the filter keeps only strong matches", 12),
        ["round 166:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 166: the filter keeps only strong matches", 16),
        ["round 166: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 166: the filter keeps only strong matches", 24),
        ["round 166: the filter", "keeps only strong", "matches"],
    ),
    (("round 166: the filter keeps only strong matches", 32), ["round 166: the filter keeps only", "strong matches"]),
    (
        ("round 166: the model answers with a short reply", 4),
        ["round", "166:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 166: the model answers with a short reply", 8),
        ["round", "166: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 166: the model answers with a short reply", 12),
        ["round 166:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 166: the model answers with a short reply", 16),
        ["round 166: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 166: the model answers with a short reply", 24),
        ["round 166: the model", "answers with a short", "reply"],
    ),
    (("round 166: the model answers with a short reply", 32), ["round 166: the model answers", "with a short reply"]),
    (
        ("round 166: the recorder stores the reasoning trace", 4),
        ["round", "166:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 166: the recorder stores the reasoning trace", 8),
        ["round", "166: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 166: the recorder stores the reasoning trace", 12),
        ["round 166:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 166: the recorder stores the reasoning trace", 16),
        ["round 166: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 166: the recorder stores the reasoning trace", 24),
        ["round 166: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 166: the recorder stores the reasoning trace", 32),
        ["round 166: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 166: the angel watches the processor run", 4),
        ["round", "166:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 166: the angel watches the processor run", 8),
        ["round", "166: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 166: the angel watches the processor run", 12),
        ["round 166:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 166: the angel watches the processor run", 16),
        ["round 166: the", "angel watches", "the processor", "run"],
    ),
    (("round 166: the angel watches the processor run", 24), ["round 166: the angel", "watches the processor", "run"]),
    (("round 166: the angel watches the processor run", 32), ["round 166: the angel watches the", "processor run"]),
    (
        ("round 166: angle of the vector decides the match", 4),
        ["round", "166:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 166: angle of the vector decides the match", 8),
        ["round", "166:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 166: angle of the vector decides the match", 12),
        ["round 166:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 166: angle of the vector decides the match", 16),
        ["round 166: angle", "of the vector", "decides the", "match"],
    ),
    (("round 166: angle of the vector decides the match", 24), ["round 166: angle of the", "vector decides the match"]),
    (("round 166: angle of the vector decides the match", 32), ["round 166: angle of the vector", "decides the match"]),
    (
        ("round 166: the candle burns twice as long at night", 4),
        ["round", "166:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 166: the candle burns twice as long at night", 8),
        ["round", "166: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 166: the candle burns twice as long at night", 12),
        ["round 166:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 166: the candle burns twice as long at night", 16),
        ["round 166: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 166: the candle burns twice as long at night", 24),
        ["round 166: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 166: the candle burns twice as long at night", 32),
        ["round 166: the candle burns", "twice as long at night"],
    ),
    (
        ("round 166: a mirror of the universe in one line", 4),
        ["round", "166:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 166: a mirror of the universe in one line", 8),
        ["round", "166: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 166: a mirror of the universe in one line", 12),
        ["round 166: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 166: a mirror of the universe in one line", 16),
        ["round 166: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 166: a mirror of the universe in one line", 24), ["round 166: a mirror of", "the universe in one line"]),
    (("round 166: a mirror of the universe in one line", 32), ["round 166: a mirror of the", "universe in one line"]),
    (
        ("round 166: the queue drains before the storm", 4),
        ["round", "166:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 166: the queue drains before the storm", 8),
        ["round", "166: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 166: the queue drains before the storm", 12),
        ["round 166:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 166: the queue drains before the storm", 16), ["round 166: the", "queue drains", "before the storm"]),
    (("round 166: the queue drains before the storm", 24), ["round 166: the queue", "drains before the storm"]),
    (("round 166: the queue drains before the storm", 32), ["round 166: the queue drains", "before the storm"]),
    (
        ("kitten166 sitting166 agent166 angle166 universe166 memory166", 6),
        ["kitten166", "sitting166", "agent166", "angle166", "universe166", "memory166"],
    ),
    (
        ("kitten166 sitting166 agent166 angle166 universe166 memory166", 10),
        ["kitten166", "sitting166", "agent166", "angle166", "universe166", "memory166"],
    ),
    (
        ("kitten166 sitting166 agent166 angle166 universe166 memory166", 18),
        ["kitten166", "sitting166", "agent166 angle166", "universe166", "memory166"],
    ),
    (
        ("kitten166 sitting166 agent166 angle166 universe166 memory166", 28),
        ["kitten166 sitting166", "agent166 angle166", "universe166 memory166"],
    ),
    (
        ("sitting166 agent166 angle166 universe166 memory166 stream166", 6),
        ["sitting166", "agent166", "angle166", "universe166", "memory166", "stream166"],
    ),
    (
        ("sitting166 agent166 angle166 universe166 memory166 stream166", 10),
        ["sitting166", "agent166", "angle166", "universe166", "memory166", "stream166"],
    ),
    (
        ("sitting166 agent166 angle166 universe166 memory166 stream166", 18),
        ["sitting166", "agent166 angle166", "universe166", "memory166", "stream166"],
    ),
    (
        ("sitting166 agent166 angle166 universe166 memory166 stream166", 28),
        ["sitting166 agent166 angle166", "universe166 memory166", "stream166"],
    ),
    (
        ("agent166 angle166 universe166 memory166 stream166 context166", 6),
        ["agent166", "angle166", "universe166", "memory166", "stream166", "context166"],
    ),
    (
        ("agent166 angle166 universe166 memory166 stream166 context166", 10),
        ["agent166", "angle166", "universe166", "memory166", "stream166", "context166"],
    ),
    (
        ("agent166 angle166 universe166 memory166 stream166 context166", 18),
        ["agent166 angle166", "universe166", "memory166", "stream166", "context166"],
    ),
    (
        ("agent166 angle166 universe166 memory166 stream166 context166", 28),
        ["agent166 angle166", "universe166 memory166", "stream166 context166"],
    ),
    (
        ("angle166 universe166 memory166 stream166 context166 knowledge166", 6),
        ["angle166", "universe166", "memory166", "stream166", "context166", "knowledge166"],
    ),
    (
        ("angle166 universe166 memory166 stream166 context166 knowledge166", 10),
        ["angle166", "universe166", "memory166", "stream166", "context166", "knowledge166"],
    ),
    (
        ("angle166 universe166 memory166 stream166 context166 knowledge166", 18),
        ["angle166", "universe166", "memory166", "stream166", "context166", "knowledge166"],
    ),
    (
        ("angle166 universe166 memory166 stream166 context166 knowledge166", 28),
        ["angle166 universe166", "memory166 stream166", "context166 knowledge166"],
    ),
    (
        ("universe166 memory166 stream166 context166 knowledge166 vector166", 6),
        ["universe166", "memory166", "stream166", "context166", "knowledge166", "vector166"],
    ),
    (
        ("universe166 memory166 stream166 context166 knowledge166 vector166", 10),
        ["universe166", "memory166", "stream166", "context166", "knowledge166", "vector166"],
    ),
    (
        ("universe166 memory166 stream166 context166 knowledge166 vector166", 18),
        ["universe166", "memory166", "stream166", "context166", "knowledge166", "vector166"],
    ),
    (
        ("universe166 memory166 stream166 context166 knowledge166 vector166", 28),
        ["universe166 memory166", "stream166 context166", "knowledge166 vector166"],
    ),
    (
        ("memory166 stream166 context166 knowledge166 vector166 processor166", 6),
        ["memory166", "stream166", "context166", "knowledge166", "vector166", "processor166"],
    ),
    (
        ("memory166 stream166 context166 knowledge166 vector166 processor166", 10),
        ["memory166", "stream166", "context166", "knowledge166", "vector166", "processor166"],
    ),
    (
        ("memory166 stream166 context166 knowledge166 vector166 processor166", 18),
        ["memory166", "stream166", "context166", "knowledge166", "vector166", "processor166"],
    ),
    (
        ("memory166 stream166 context166 knowledge166 vector166 processor166", 28),
        ["memory166 stream166", "context166 knowledge166", "vector166 processor166"],
    ),
    (
        ("stream166 context166 knowledge166 vector166 processor166 reasoning166", 6),
        ["stream166", "context166", "knowledge166", "vector166", "processor166", "reasoning166"],
    ),
    (
        ("stream166 context166 knowledge166 vector166 processor166 reasoning166", 10),
        ["stream166", "context166", "knowledge166", "vector166", "processor166", "reasoning166"],
    ),
    (
        ("stream166 context166 knowledge166 vector166 processor166 reasoning166", 18),
        ["stream166", "context166", "knowledge166", "vector166", "processor166", "reasoning166"],
    ),
    (
        ("stream166 context166 knowledge166 vector166 processor166 reasoning166", 28),
        ["stream166 context166", "knowledge166 vector166", "processor166 reasoning166"],
    ),
    (
        ("context166 knowledge166 vector166 processor166 reasoning166 machine166", 6),
        ["context166", "knowledge166", "vector166", "processor166", "reasoning166", "machine166"],
    ),
    (
        ("context166 knowledge166 vector166 processor166 reasoning166 machine166", 10),
        ["context166", "knowledge166", "vector166", "processor166", "reasoning166", "machine166"],
    ),
    (
        ("context166 knowledge166 vector166 processor166 reasoning166 machine166", 18),
        ["context166", "knowledge166", "vector166", "processor166", "reasoning166", "machine166"],
    ),
    (
        ("context166 knowledge166 vector166 processor166 reasoning166 machine166", 28),
        ["context166 knowledge166", "vector166 processor166", "reasoning166 machine166"],
    ),
    (
        ("knowledge166 vector166 processor166 reasoning166 machine166 learning166", 6),
        ["knowledge166", "vector166", "processor166", "reasoning166", "machine166", "learning166"],
    ),
    (
        ("knowledge166 vector166 processor166 reasoning166 machine166 learning166", 10),
        ["knowledge166", "vector166", "processor166", "reasoning166", "machine166", "learning166"],
    ),
    (
        ("knowledge166 vector166 processor166 reasoning166 machine166 learning166", 18),
        ["knowledge166", "vector166", "processor166", "reasoning166", "machine166", "learning166"],
    ),
    (
        ("knowledge166 vector166 processor166 reasoning166 machine166 learning166", 28),
        ["knowledge166 vector166", "processor166 reasoning166", "machine166 learning166"],
    ),
    (
        ("vector166 processor166 reasoning166 machine166 learning166 model166", 6),
        ["vector166", "processor166", "reasoning166", "machine166", "learning166", "model166"],
    ),
    (
        ("vector166 processor166 reasoning166 machine166 learning166 model166", 10),
        ["vector166", "processor166", "reasoning166", "machine166", "learning166", "model166"],
    ),
    (
        ("vector166 processor166 reasoning166 machine166 learning166 model166", 18),
        ["vector166", "processor166", "reasoning166", "machine166", "learning166", "model166"],
    ),
    (
        ("vector166 processor166 reasoning166 machine166 learning166 model166", 28),
        ["vector166 processor166", "reasoning166 machine166", "learning166 model166"],
    ),
    (
        ("processor166 reasoning166 machine166 learning166 model166 token166", 6),
        ["processor166", "reasoning166", "machine166", "learning166", "model166", "token166"],
    ),
    (
        ("processor166 reasoning166 machine166 learning166 model166 token166", 10),
        ["processor166", "reasoning166", "machine166", "learning166", "model166", "token166"],
    ),
    (
        ("processor166 reasoning166 machine166 learning166 model166 token166", 18),
        ["processor166", "reasoning166", "machine166", "learning166", "model166 token166"],
    ),
    (
        ("processor166 reasoning166 machine166 learning166 model166 token166", 28),
        ["processor166 reasoning166", "machine166 learning166", "model166 token166"],
    ),
    (
        ("reasoning166 machine166 learning166 model166 token166 prompt166", 6),
        ["reasoning166", "machine166", "learning166", "model166", "token166", "prompt166"],
    ),
    (
        ("reasoning166 machine166 learning166 model166 token166 prompt166", 10),
        ["reasoning166", "machine166", "learning166", "model166", "token166", "prompt166"],
    ),
    (
        ("reasoning166 machine166 learning166 model166 token166 prompt166", 18),
        ["reasoning166", "machine166", "learning166", "model166 token166", "prompt166"],
    ),
    (
        ("reasoning166 machine166 learning166 model166 token166 prompt166", 28),
        ["reasoning166 machine166", "learning166 model166", "token166 prompt166"],
    ),
    (
        ("machine166 learning166 model166 token166 prompt166 session166", 6),
        ["machine166", "learning166", "model166", "token166", "prompt166", "session166"],
    ),
    (
        ("machine166 learning166 model166 token166 prompt166 session166", 10),
        ["machine166", "learning166", "model166", "token166", "prompt166", "session166"],
    ),
    (
        ("machine166 learning166 model166 token166 prompt166 session166", 18),
        ["machine166", "learning166", "model166 token166", "prompt166", "session166"],
    ),
    (
        ("machine166 learning166 model166 token166 prompt166 session166", 28),
        ["machine166 learning166", "model166 token166 prompt166", "session166"],
    ),
    (
        ("learning166 model166 token166 prompt166 session166 library166", 6),
        ["learning166", "model166", "token166", "prompt166", "session166", "library166"],
    ),
    (
        ("learning166 model166 token166 prompt166 session166 library166", 10),
        ["learning166", "model166", "token166", "prompt166", "session166", "library166"],
    ),
    (
        ("learning166 model166 token166 prompt166 session166 library166", 18),
        ["learning166", "model166 token166", "prompt166", "session166", "library166"],
    ),
    (
        ("learning166 model166 token166 prompt166 session166 library166", 28),
        ["learning166 model166", "token166 prompt166", "session166 library166"],
    ),
    (
        ("model166 token166 prompt166 session166 library166 service166", 6),
        ["model166", "token166", "prompt166", "session166", "library166", "service166"],
    ),
    (
        ("model166 token166 prompt166 session166 library166 service166", 10),
        ["model166", "token166", "prompt166", "session166", "library166", "service166"],
    ),
    (
        ("model166 token166 prompt166 session166 library166 service166", 18),
        ["model166 token166", "prompt166", "session166", "library166", "service166"],
    ),
    (
        ("model166 token166 prompt166 session166 library166 service166", 28),
        ["model166 token166 prompt166", "session166 library166", "service166"],
    ),
    (
        ("token166 prompt166 session166 library166 service166 gateway166", 6),
        ["token166", "prompt166", "session166", "library166", "service166", "gateway166"],
    ),
    (
        ("token166 prompt166 session166 library166 service166 gateway166", 10),
        ["token166", "prompt166", "session166", "library166", "service166", "gateway166"],
    ),
    (
        ("token166 prompt166 session166 library166 service166 gateway166", 18),
        ["token166 prompt166", "session166", "library166", "service166", "gateway166"],
    ),
    (
        ("token166 prompt166 session166 library166 service166 gateway166", 28),
        ["token166 prompt166", "session166 library166", "service166 gateway166"],
    ),
    (
        ("prompt166 session166 library166 service166 gateway166 storage166", 6),
        ["prompt166", "session166", "library166", "service166", "gateway166", "storage166"],
    ),
    (
        ("prompt166 session166 library166 service166 gateway166 storage166", 10),
        ["prompt166", "session166", "library166", "service166", "gateway166", "storage166"],
    ),
    (
        ("prompt166 session166 library166 service166 gateway166 storage166", 18),
        ["prompt166", "session166", "library166", "service166", "gateway166", "storage166"],
    ),
    (
        ("prompt166 session166 library166 service166 gateway166 storage166", 28),
        ["prompt166 session166", "library166 service166", "gateway166 storage166"],
    ),
    (
        ("session166 library166 service166 gateway166 storage166 network166", 6),
        ["session166", "library166", "service166", "gateway166", "storage166", "network166"],
    ),
    (
        ("session166 library166 service166 gateway166 storage166 network166", 10),
        ["session166", "library166", "service166", "gateway166", "storage166", "network166"],
    ),
    (
        ("session166 library166 service166 gateway166 storage166 network166", 18),
        ["session166", "library166", "service166", "gateway166", "storage166", "network166"],
    ),
    (
        ("session166 library166 service166 gateway166 storage166 network166", 28),
        ["session166 library166", "service166 gateway166", "storage166 network166"],
    ),
    (
        ("library166 service166 gateway166 storage166 network166 latency166", 6),
        ["library166", "service166", "gateway166", "storage166", "network166", "latency166"],
    ),
    (
        ("library166 service166 gateway166 storage166 network166 latency166", 10),
        ["library166", "service166", "gateway166", "storage166", "network166", "latency166"],
    ),
    (
        ("library166 service166 gateway166 storage166 network166 latency166", 18),
        ["library166", "service166", "gateway166", "storage166", "network166", "latency166"],
    ),
    (
        ("library166 service166 gateway166 storage166 network166 latency166", 28),
        ["library166 service166", "gateway166 storage166", "network166 latency166"],
    ),
    (
        ("service166 gateway166 storage166 network166 latency166 buffer166", 6),
        ["service166", "gateway166", "storage166", "network166", "latency166", "buffer166"],
    ),
    (
        ("service166 gateway166 storage166 network166 latency166 buffer166", 10),
        ["service166", "gateway166", "storage166", "network166", "latency166", "buffer166"],
    ),
    (
        ("service166 gateway166 storage166 network166 latency166 buffer166", 18),
        ["service166", "gateway166", "storage166", "network166", "latency166", "buffer166"],
    ),
    (
        ("service166 gateway166 storage166 network166 latency166 buffer166", 28),
        ["service166 gateway166", "storage166 network166", "latency166 buffer166"],
    ),
    (
        ("gateway166 storage166 network166 latency166 buffer166 queue166", 6),
        ["gateway166", "storage166", "network166", "latency166", "buffer166", "queue166"],
    ),
    (
        ("gateway166 storage166 network166 latency166 buffer166 queue166", 10),
        ["gateway166", "storage166", "network166", "latency166", "buffer166", "queue166"],
    ),
    (
        ("gateway166 storage166 network166 latency166 buffer166 queue166", 18),
        ["gateway166", "storage166", "network166", "latency166", "buffer166 queue166"],
    ),
    (
        ("gateway166 storage166 network166 latency166 buffer166 queue166", 28),
        ["gateway166 storage166", "network166 latency166", "buffer166 queue166"],
    ),
    (
        ("storage166 network166 latency166 buffer166 queue166 worker166", 6),
        ["storage166", "network166", "latency166", "buffer166", "queue166", "worker166"],
    ),
    (
        ("storage166 network166 latency166 buffer166 queue166 worker166", 10),
        ["storage166", "network166", "latency166", "buffer166", "queue166", "worker166"],
    ),
    (
        ("storage166 network166 latency166 buffer166 queue166 worker166", 18),
        ["storage166", "network166", "latency166", "buffer166 queue166", "worker166"],
    ),
    (
        ("storage166 network166 latency166 buffer166 queue166 worker166", 28),
        ["storage166 network166", "latency166 buffer166", "queue166 worker166"],
    ),
    (
        ("network166 latency166 buffer166 queue166 worker166 kernel166", 6),
        ["network166", "latency166", "buffer166", "queue166", "worker166", "kernel166"],
    ),
    (
        ("network166 latency166 buffer166 queue166 worker166 kernel166", 10),
        ["network166", "latency166", "buffer166", "queue166", "worker166", "kernel166"],
    ),
    (
        ("network166 latency166 buffer166 queue166 worker166 kernel166", 18),
        ["network166", "latency166", "buffer166 queue166", "worker166", "kernel166"],
    ),
    (
        ("network166 latency166 buffer166 queue166 worker166 kernel166", 28),
        ["network166 latency166", "buffer166 queue166 worker166", "kernel166"],
    ),
    (
        ("latency166 buffer166 queue166 worker166 kernel166 signal166", 6),
        ["latency166", "buffer166", "queue166", "worker166", "kernel166", "signal166"],
    ),
    (
        ("latency166 buffer166 queue166 worker166 kernel166 signal166", 10),
        ["latency166", "buffer166", "queue166", "worker166", "kernel166", "signal166"],
    ),
    (
        ("latency166 buffer166 queue166 worker166 kernel166 signal166", 18),
        ["latency166", "buffer166 queue166", "worker166", "kernel166", "signal166"],
    ),
    (
        ("latency166 buffer166 queue166 worker166 kernel166 signal166", 28),
        ["latency166 buffer166", "queue166 worker166 kernel166", "signal166"],
    ),
    (
        ("buffer166 queue166 worker166 kernel166 signal166 packet166", 6),
        ["buffer166", "queue166", "worker166", "kernel166", "signal166", "packet166"],
    ),
    (
        ("buffer166 queue166 worker166 kernel166 signal166 packet166", 10),
        ["buffer166", "queue166", "worker166", "kernel166", "signal166", "packet166"],
    ),
    (
        ("buffer166 queue166 worker166 kernel166 signal166 packet166", 18),
        ["buffer166 queue166", "worker166", "kernel166", "signal166", "packet166"],
    ),
    (
        ("buffer166 queue166 worker166 kernel166 signal166 packet166", 28),
        ["buffer166 queue166 worker166", "kernel166 signal166", "packet166"],
    ),
    (
        ("queue166 worker166 kernel166 signal166 packet166 router166", 6),
        ["queue166", "worker166", "kernel166", "signal166", "packet166", "router166"],
    ),
    (
        ("queue166 worker166 kernel166 signal166 packet166 router166", 10),
        ["queue166", "worker166", "kernel166", "signal166", "packet166", "router166"],
    ),
    (
        ("queue166 worker166 kernel166 signal166 packet166 router166", 18),
        ["queue166 worker166", "kernel166", "signal166", "packet166", "router166"],
    ),
    (
        ("queue166 worker166 kernel166 signal166 packet166 router166", 28),
        ["queue166 worker166 kernel166", "signal166 packet166", "router166"],
    ),
    (
        ("worker166 kernel166 signal166 packet166 router166 cluster166", 6),
        ["worker166", "kernel166", "signal166", "packet166", "router166", "cluster166"],
    ),
    (
        ("worker166 kernel166 signal166 packet166 router166 cluster166", 10),
        ["worker166", "kernel166", "signal166", "packet166", "router166", "cluster166"],
    ),
    (
        ("worker166 kernel166 signal166 packet166 router166 cluster166", 18),
        ["worker166", "kernel166", "signal166", "packet166", "router166", "cluster166"],
    ),
    (
        ("worker166 kernel166 signal166 packet166 router166 cluster166", 28),
        ["worker166 kernel166", "signal166 packet166", "router166 cluster166"],
    ),
    (
        ("kernel166 signal166 packet166 router166 cluster166 mirror166", 6),
        ["kernel166", "signal166", "packet166", "router166", "cluster166", "mirror166"],
    ),
    (
        ("kernel166 signal166 packet166 router166 cluster166 mirror166", 10),
        ["kernel166", "signal166", "packet166", "router166", "cluster166", "mirror166"],
    ),
    (
        ("kernel166 signal166 packet166 router166 cluster166 mirror166", 18),
        ["kernel166", "signal166", "packet166", "router166", "cluster166", "mirror166"],
    ),
    (
        ("kernel166 signal166 packet166 router166 cluster166 mirror166", 28),
        ["kernel166 signal166", "packet166 router166", "cluster166 mirror166"],
    ),
    (
        ("signal166 packet166 router166 cluster166 mirror166 filter166", 6),
        ["signal166", "packet166", "router166", "cluster166", "mirror166", "filter166"],
    ),
    (
        ("signal166 packet166 router166 cluster166 mirror166 filter166", 10),
        ["signal166", "packet166", "router166", "cluster166", "mirror166", "filter166"],
    ),
    (
        ("signal166 packet166 router166 cluster166 mirror166 filter166", 18),
        ["signal166", "packet166", "router166", "cluster166", "mirror166", "filter166"],
    ),
    (
        ("signal166 packet166 router166 cluster166 mirror166 filter166", 28),
        ["signal166 packet166", "router166 cluster166", "mirror166 filter166"],
    ),
    (
        ("packet166 router166 cluster166 mirror166 filter166 ranking166", 6),
        ["packet166", "router166", "cluster166", "mirror166", "filter166", "ranking166"],
    ),
    (
        ("packet166 router166 cluster166 mirror166 filter166 ranking166", 10),
        ["packet166", "router166", "cluster166", "mirror166", "filter166", "ranking166"],
    ),
    (
        ("packet166 router166 cluster166 mirror166 filter166 ranking166", 18),
        ["packet166", "router166", "cluster166", "mirror166", "filter166", "ranking166"],
    ),
    (
        ("packet166 router166 cluster166 mirror166 filter166 ranking166", 28),
        ["packet166 router166", "cluster166 mirror166", "filter166 ranking166"],
    ),
    (
        ("router166 cluster166 mirror166 filter166 ranking166 encoding166", 6),
        ["router166", "cluster166", "mirror166", "filter166", "ranking166", "encoding166"],
    ),
    (
        ("router166 cluster166 mirror166 filter166 ranking166 encoding166", 10),
        ["router166", "cluster166", "mirror166", "filter166", "ranking166", "encoding166"],
    ),
    (
        ("router166 cluster166 mirror166 filter166 ranking166 encoding166", 18),
        ["router166", "cluster166", "mirror166", "filter166", "ranking166", "encoding166"],
    ),
    (
        ("router166 cluster166 mirror166 filter166 ranking166 encoding166", 28),
        ["router166 cluster166", "mirror166 filter166", "ranking166 encoding166"],
    ),
    (
        ("cluster166 mirror166 filter166 ranking166 encoding166 mapping166", 6),
        ["cluster166", "mirror166", "filter166", "ranking166", "encoding166", "mapping166"],
    ),
    (
        ("cluster166 mirror166 filter166 ranking166 encoding166 mapping166", 10),
        ["cluster166", "mirror166", "filter166", "ranking166", "encoding166", "mapping166"],
    ),
    (
        ("cluster166 mirror166 filter166 ranking166 encoding166 mapping166", 18),
        ["cluster166", "mirror166", "filter166", "ranking166", "encoding166", "mapping166"],
    ),
    (
        ("cluster166 mirror166 filter166 ranking166 encoding166 mapping166", 28),
        ["cluster166 mirror166", "filter166 ranking166", "encoding166 mapping166"],
    ),
    (
        ("mirror166 filter166 ranking166 encoding166 mapping166 record166", 6),
        ["mirror166", "filter166", "ranking166", "encoding166", "mapping166", "record166"],
    ),
    (
        ("mirror166 filter166 ranking166 encoding166 mapping166 record166", 10),
        ["mirror166", "filter166", "ranking166", "encoding166", "mapping166", "record166"],
    ),
    (
        ("mirror166 filter166 ranking166 encoding166 mapping166 record166", 18),
        ["mirror166", "filter166", "ranking166", "encoding166", "mapping166", "record166"],
    ),
    (
        ("mirror166 filter166 ranking166 encoding166 mapping166 record166", 28),
        ["mirror166 filter166", "ranking166 encoding166", "mapping166 record166"],
    ),
    (
        ("filter166 ranking166 encoding166 mapping166 record166 candle166", 6),
        ["filter166", "ranking166", "encoding166", "mapping166", "record166", "candle166"],
    ),
    (
        ("filter166 ranking166 encoding166 mapping166 record166 candle166", 10),
        ["filter166", "ranking166", "encoding166", "mapping166", "record166", "candle166"],
    ),
    (
        ("filter166 ranking166 encoding166 mapping166 record166 candle166", 18),
        ["filter166", "ranking166", "encoding166", "mapping166", "record166", "candle166"],
    ),
    (
        ("filter166 ranking166 encoding166 mapping166 record166 candle166", 28),
        ["filter166 ranking166", "encoding166 mapping166", "record166 candle166"],
    ),
    (
        ("ranking166 encoding166 mapping166 record166 candle166 thread166", 6),
        ["ranking166", "encoding166", "mapping166", "record166", "candle166", "thread166"],
    ),
    (
        ("ranking166 encoding166 mapping166 record166 candle166 thread166", 10),
        ["ranking166", "encoding166", "mapping166", "record166", "candle166", "thread166"],
    ),
    (
        ("ranking166 encoding166 mapping166 record166 candle166 thread166", 18),
        ["ranking166", "encoding166", "mapping166", "record166", "candle166", "thread166"],
    ),
    (
        ("ranking166 encoding166 mapping166 record166 candle166 thread166", 28),
        ["ranking166 encoding166", "mapping166 record166", "candle166 thread166"],
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
