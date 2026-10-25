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
        ("round 8: the quick brown fox jumps over the lazy dog", 4),
        ["round", "8:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 8: the quick brown fox jumps over the lazy dog", 8),
        ["round 8:", "the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 8: the quick brown fox jumps over the lazy dog", 12),
        ["round 8: the", "quick brown", "fox jumps", "over the", "lazy dog"],
    ),
    (
        ("round 8: the quick brown fox jumps over the lazy dog", 16),
        ["round 8: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 8: the quick brown fox jumps over the lazy dog", 24),
        ["round 8: the quick brown", "fox jumps over the lazy", "dog"],
    ),
    (
        ("round 8: the quick brown fox jumps over the lazy dog", 32),
        ["round 8: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 8: agentuniverse is a framework for multi agents", 4),
        ["round", "8:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 8: agentuniverse is a framework for multi agents", 8),
        ["round 8:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 8: agentuniverse is a framework for multi agents", 12),
        ["round 8:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 8: agentuniverse is a framework for multi agents", 16),
        ["round 8:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 8: agentuniverse is a framework for multi agents", 24),
        ["round 8: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 8: agentuniverse is a framework for multi agents", 32),
        ["round 8: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 8: knowledge stored as vectors enables retrieval", 4),
        ["round", "8:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 8: knowledge stored as vectors enables retrieval", 8),
        ["round 8:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 8: knowledge stored as vectors enables retrieval", 12),
        ["round 8:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 8: knowledge stored as vectors enables retrieval", 16),
        ["round 8:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 8: knowledge stored as vectors enables retrieval", 24),
        ["round 8: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 8: knowledge stored as vectors enables retrieval", 32),
        ["round 8: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 8: the processor reads the record then stops", 4),
        ["round", "8:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 8: the processor reads the record then stops", 8),
        ["round 8:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 8: the processor reads the record then stops", 12),
        ["round 8: the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 8: the processor reads the record then stops", 16),
        ["round 8: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 8: the processor reads the record then stops", 24),
        ["round 8: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 8: the processor reads the record then stops", 32),
        ["round 8: the processor reads the", "record then stops"],
    ),
    (
        ("round 8: a worker pulls the next task from the queue", 4),
        ["round", "8: a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 8: a worker pulls the next task from the queue", 8),
        ["round 8:", "a worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 8: a worker pulls the next task from the queue", 12),
        ["round 8: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 8: a worker pulls the next task from the queue", 16),
        ["round 8: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 8: a worker pulls the next task from the queue", 24),
        ["round 8: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 8: a worker pulls the next task from the queue", 32),
        ["round 8: a worker pulls the next", "task from the queue"],
    ),
    (
        ("round 8: signals travel through the network layer", 4),
        ["round", "8:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 8: signals travel through the network layer", 8),
        ["round 8:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 8: signals travel through the network layer", 12),
        ["round 8:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 8: signals travel through the network layer", 16),
        ["round 8: signals", "travel through", "the network", "layer"],
    ),
    (
        ("round 8: signals travel through the network layer", 24),
        ["round 8: signals travel", "through the network", "layer"],
    ),
    (
        ("round 8: signals travel through the network layer", 32),
        ["round 8: signals travel through", "the network layer"],
    ),
    (
        ("round 8: the gateway routes each request by policy", 4),
        ["round", "8:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 8: the gateway routes each request by policy", 8),
        ["round 8:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 8: the gateway routes each request by policy", 12),
        ["round 8: the", "gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 8: the gateway routes each request by policy", 16),
        ["round 8: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 8: the gateway routes each request by policy", 24),
        ["round 8: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 8: the gateway routes each request by policy", 32),
        ["round 8: the gateway routes each", "request by policy"],
    ),
    (
        ("round 8: memory grows until the buffer is full", 4),
        ["round", "8:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 8: memory grows until the buffer is full", 8),
        ["round 8:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 8: memory grows until the buffer is full", 12),
        ["round 8:", "memory grows", "until the", "buffer is", "full"],
    ),
    (("round 8: memory grows until the buffer is full", 16), ["round 8: memory", "grows until the", "buffer is full"]),
    (("round 8: memory grows until the buffer is full", 24), ["round 8: memory grows", "until the buffer is full"]),
    (("round 8: memory grows until the buffer is full", 32), ["round 8: memory grows until the", "buffer is full"]),
    (
        ("round 8: the cluster mirrors every packet twice", 4),
        ["round", "8:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 8: the cluster mirrors every packet twice", 8),
        ["round 8:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 8: the cluster mirrors every packet twice", 12),
        ["round 8: the", "cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 8: the cluster mirrors every packet twice", 16),
        ["round 8: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 8: the cluster mirrors every packet twice", 24),
        ["round 8: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 8: the cluster mirrors every packet twice", 32), ["round 8: the cluster mirrors", "every packet twice"]),
    (
        ("round 8: ranking uses tokens learned from the corpus", 4),
        ["round", "8:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 8: ranking uses tokens learned from the corpus", 8),
        ["round 8:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 8: ranking uses tokens learned from the corpus", 12),
        ["round 8:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 8: ranking uses tokens learned from the corpus", 16),
        ["round 8: ranking", "uses tokens", "learned from the", "corpus"],
    ),
    (
        ("round 8: ranking uses tokens learned from the corpus", 24),
        ["round 8: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 8: ranking uses tokens learned from the corpus", 32),
        ["round 8: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 8: a long session ends when the candle dies", 4),
        ["round", "8: a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 8: a long session ends when the candle dies", 8),
        ["round 8:", "a long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 8: a long session ends when the candle dies", 12),
        ["round 8: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 8: a long session ends when the candle dies", 16),
        ["round 8: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 8: a long session ends when the candle dies", 24),
        ["round 8: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 8: a long session ends when the candle dies", 32),
        ["round 8: a long session ends", "when the candle dies"],
    ),
    (
        ("round 8: encode the prompt then map the result", 4),
        ["round", "8:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 8: encode the prompt then map the result", 8),
        ["round 8:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 8: encode the prompt then map the result", 12),
        ["round 8:", "encode the", "prompt then", "map the", "result"],
    ),
    (("round 8: encode the prompt then map the result", 16), ["round 8: encode", "the prompt then", "map the result"]),
    (("round 8: encode the prompt then map the result", 24), ["round 8: encode the", "prompt then map the", "result"]),
    (("round 8: encode the prompt then map the result", 32), ["round 8: encode the prompt then", "map the result"]),
    (
        ("round 8: the kernel wakes the worker at dawn", 4),
        ["round", "8:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 8: the kernel wakes the worker at dawn", 8),
        ["round 8:", "the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (("round 8: the kernel wakes the worker at dawn", 12), ["round 8: the", "kernel wakes", "the worker", "at dawn"]),
    (("round 8: the kernel wakes the worker at dawn", 16), ["round 8: the", "kernel wakes the", "worker at dawn"]),
    (("round 8: the kernel wakes the worker at dawn", 24), ["round 8: the kernel", "wakes the worker at dawn"]),
    (("round 8: the kernel wakes the worker at dawn", 32), ["round 8: the kernel wakes the", "worker at dawn"]),
    (
        ("round 8: service latency drops after the patch", 4),
        ["round", "8:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 8: service latency drops after the patch", 8),
        ["round 8:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 8: service latency drops after the patch", 12),
        ["round 8:", "service", "latency", "drops after", "the patch"],
    ),
    (("round 8: service latency drops after the patch", 16), ["round 8: service", "latency drops", "after the patch"]),
    (("round 8: service latency drops after the patch", 24), ["round 8: service latency", "drops after the patch"]),
    (("round 8: service latency drops after the patch", 32), ["round 8: service latency drops", "after the patch"]),
    (
        ("round 8: the library caches every vector it sees", 4),
        ["round", "8:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 8: the library caches every vector it sees", 8),
        ["round 8:", "the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 8: the library caches every vector it sees", 12),
        ["round 8: the", "library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 8: the library caches every vector it sees", 16),
        ["round 8: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 8: the library caches every vector it sees", 24),
        ["round 8: the library", "caches every vector it", "sees"],
    ),
    (("round 8: the library caches every vector it sees", 32), ["round 8: the library caches", "every vector it sees"]),
    (
        ("round 8: agents argue then the debate resolves", 4),
        ["round", "8:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 8: agents argue then the debate resolves", 8),
        ["round 8:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 8: agents argue then the debate resolves", 12),
        ["round 8:", "agents argue", "then the", "debate", "resolves"],
    ),
    (("round 8: agents argue then the debate resolves", 16), ["round 8: agents", "argue then the", "debate resolves"]),
    (("round 8: agents argue then the debate resolves", 24), ["round 8: agents argue", "then the debate resolves"]),
    (("round 8: agents argue then the debate resolves", 32), ["round 8: agents argue then the", "debate resolves"]),
    (
        ("round 8: the filter keeps only strong matches", 4),
        ["round", "8:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 8: the filter keeps only strong matches", 8),
        ["round 8:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (("round 8: the filter keeps only strong matches", 12), ["round 8: the", "filter keeps", "only strong", "matches"]),
    (("round 8: the filter keeps only strong matches", 16), ["round 8: the", "filter keeps", "only strong", "matches"]),
    (("round 8: the filter keeps only strong matches", 24), ["round 8: the filter", "keeps only strong", "matches"]),
    (("round 8: the filter keeps only strong matches", 32), ["round 8: the filter keeps only", "strong matches"]),
    (
        ("round 8: the model answers with a short reply", 4),
        ["round", "8:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 8: the model answers with a short reply", 8),
        ["round 8:", "the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 8: the model answers with a short reply", 12),
        ["round 8: the", "model", "answers with", "a short", "reply"],
    ),
    (("round 8: the model answers with a short reply", 16), ["round 8: the", "model answers", "with a short", "reply"]),
    (("round 8: the model answers with a short reply", 24), ["round 8: the model", "answers with a short", "reply"]),
    (("round 8: the model answers with a short reply", 32), ["round 8: the model answers with", "a short reply"]),
    (
        ("round 8: the recorder stores the reasoning trace", 4),
        ["round", "8:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 8: the recorder stores the reasoning trace", 8),
        ["round 8:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 8: the recorder stores the reasoning trace", 12),
        ["round 8: the", "recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 8: the recorder stores the reasoning trace", 16),
        ["round 8: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 8: the recorder stores the reasoning trace", 24),
        ["round 8: the recorder", "stores the reasoning", "trace"],
    ),
    (("round 8: the recorder stores the reasoning trace", 32), ["round 8: the recorder stores the", "reasoning trace"]),
    (
        ("round 8: the angel watches the processor run", 4),
        ["round", "8:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 8: the angel watches the processor run", 8),
        ["round 8:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 8: the angel watches the processor run", 12),
        ["round 8: the", "angel", "watches the", "processor", "run"],
    ),
    (("round 8: the angel watches the processor run", 16), ["round 8: the", "angel watches", "the processor", "run"]),
    (("round 8: the angel watches the processor run", 24), ["round 8: the angel", "watches the processor", "run"]),
    (("round 8: the angel watches the processor run", 32), ["round 8: the angel watches the", "processor run"]),
    (
        ("round 8: angle of the vector decides the match", 4),
        ["round", "8:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 8: angle of the vector decides the match", 8),
        ["round 8:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 8: angle of the vector decides the match", 12),
        ["round 8:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 8: angle of the vector decides the match", 16),
        ["round 8: angle", "of the vector", "decides the", "match"],
    ),
    (("round 8: angle of the vector decides the match", 24), ["round 8: angle of the", "vector decides the match"]),
    (("round 8: angle of the vector decides the match", 32), ["round 8: angle of the vector", "decides the match"]),
    (
        ("round 8: the candle burns twice as long at night", 4),
        ["round", "8:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 8: the candle burns twice as long at night", 8),
        ["round 8:", "the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 8: the candle burns twice as long at night", 12),
        ["round 8: the", "candle burns", "twice as", "long at", "night"],
    ),
    (
        ("round 8: the candle burns twice as long at night", 16),
        ["round 8: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 8: the candle burns twice as long at night", 24),
        ["round 8: the candle", "burns twice as long at", "night"],
    ),
    (("round 8: the candle burns twice as long at night", 32), ["round 8: the candle burns twice", "as long at night"]),
    (
        ("round 8: a mirror of the universe in one line", 4),
        ["round", "8: a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 8: a mirror of the universe in one line", 8),
        ["round 8:", "a mirror", "of the", "universe", "in one", "line"],
    ),
    (("round 8: a mirror of the universe in one line", 12), ["round 8: a", "mirror of", "the universe", "in one line"]),
    (("round 8: a mirror of the universe in one line", 16), ["round 8: a", "mirror of the", "universe in one", "line"]),
    (("round 8: a mirror of the universe in one line", 24), ["round 8: a mirror of the", "universe in one line"]),
    (("round 8: a mirror of the universe in one line", 32), ["round 8: a mirror of the", "universe in one line"]),
    (
        ("round 8: the queue drains before the storm", 4),
        ["round", "8:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 8: the queue drains before the storm", 8),
        ["round 8:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 8: the queue drains before the storm", 12), ["round 8: the", "queue drains", "before the", "storm"]),
    (("round 8: the queue drains before the storm", 16), ["round 8: the", "queue drains", "before the storm"]),
    (("round 8: the queue drains before the storm", 24), ["round 8: the queue", "drains before the storm"]),
    (("round 8: the queue drains before the storm", 32), ["round 8: the queue drains before", "the storm"]),
    (
        ("kitten8 sitting8 agent8 angle8 universe8 memory8", 6),
        ["kitten8", "sitting8", "agent8", "angle8", "universe8", "memory8"],
    ),
    (
        ("kitten8 sitting8 agent8 angle8 universe8 memory8", 10),
        ["kitten8", "sitting8", "agent8", "angle8", "universe8", "memory8"],
    ),
    (
        ("kitten8 sitting8 agent8 angle8 universe8 memory8", 18),
        ["kitten8 sitting8", "agent8 angle8", "universe8 memory8"],
    ),
    (("kitten8 sitting8 agent8 angle8 universe8 memory8", 28), ["kitten8 sitting8 agent8", "angle8 universe8 memory8"]),
    (
        ("sitting8 agent8 angle8 universe8 memory8 stream8", 6),
        ["sitting8", "agent8", "angle8", "universe8", "memory8", "stream8"],
    ),
    (
        ("sitting8 agent8 angle8 universe8 memory8 stream8", 10),
        ["sitting8", "agent8", "angle8", "universe8", "memory8", "stream8"],
    ),
    (
        ("sitting8 agent8 angle8 universe8 memory8 stream8", 18),
        ["sitting8 agent8", "angle8 universe8", "memory8 stream8"],
    ),
    (("sitting8 agent8 angle8 universe8 memory8 stream8", 28), ["sitting8 agent8 angle8", "universe8 memory8 stream8"]),
    (
        ("agent8 angle8 universe8 memory8 stream8 context8", 6),
        ["agent8", "angle8", "universe8", "memory8", "stream8", "context8"],
    ),
    (
        ("agent8 angle8 universe8 memory8 stream8 context8", 10),
        ["agent8", "angle8", "universe8", "memory8", "stream8", "context8"],
    ),
    (
        ("agent8 angle8 universe8 memory8 stream8 context8", 18),
        ["agent8 angle8", "universe8 memory8", "stream8 context8"],
    ),
    (("agent8 angle8 universe8 memory8 stream8 context8", 28), ["agent8 angle8 universe8", "memory8 stream8 context8"]),
    (
        ("angle8 universe8 memory8 stream8 context8 knowledge8", 6),
        ["angle8", "universe8", "memory8", "stream8", "context8", "knowledge8"],
    ),
    (
        ("angle8 universe8 memory8 stream8 context8 knowledge8", 10),
        ["angle8", "universe8", "memory8", "stream8", "context8", "knowledge8"],
    ),
    (
        ("angle8 universe8 memory8 stream8 context8 knowledge8", 18),
        ["angle8 universe8", "memory8 stream8", "context8", "knowledge8"],
    ),
    (
        ("angle8 universe8 memory8 stream8 context8 knowledge8", 28),
        ["angle8 universe8 memory8", "stream8 context8 knowledge8"],
    ),
    (
        ("universe8 memory8 stream8 context8 knowledge8 vector8", 6),
        ["universe8", "memory8", "stream8", "context8", "knowledge8", "vector8"],
    ),
    (
        ("universe8 memory8 stream8 context8 knowledge8 vector8", 10),
        ["universe8", "memory8", "stream8", "context8", "knowledge8", "vector8"],
    ),
    (
        ("universe8 memory8 stream8 context8 knowledge8 vector8", 18),
        ["universe8 memory8", "stream8 context8", "knowledge8 vector8"],
    ),
    (
        ("universe8 memory8 stream8 context8 knowledge8 vector8", 28),
        ["universe8 memory8 stream8", "context8 knowledge8 vector8"],
    ),
    (
        ("memory8 stream8 context8 knowledge8 vector8 processor8", 6),
        ["memory8", "stream8", "context8", "knowledge8", "vector8", "processor8"],
    ),
    (
        ("memory8 stream8 context8 knowledge8 vector8 processor8", 10),
        ["memory8", "stream8", "context8", "knowledge8", "vector8", "processor8"],
    ),
    (
        ("memory8 stream8 context8 knowledge8 vector8 processor8", 18),
        ["memory8 stream8", "context8", "knowledge8 vector8", "processor8"],
    ),
    (
        ("memory8 stream8 context8 knowledge8 vector8 processor8", 28),
        ["memory8 stream8 context8", "knowledge8 vector8", "processor8"],
    ),
    (
        ("stream8 context8 knowledge8 vector8 processor8 reasoning8", 6),
        ["stream8", "context8", "knowledge8", "vector8", "processor8", "reasoning8"],
    ),
    (
        ("stream8 context8 knowledge8 vector8 processor8 reasoning8", 10),
        ["stream8", "context8", "knowledge8", "vector8", "processor8", "reasoning8"],
    ),
    (
        ("stream8 context8 knowledge8 vector8 processor8 reasoning8", 18),
        ["stream8 context8", "knowledge8 vector8", "processor8", "reasoning8"],
    ),
    (
        ("stream8 context8 knowledge8 vector8 processor8 reasoning8", 28),
        ["stream8 context8 knowledge8", "vector8 processor8", "reasoning8"],
    ),
    (
        ("context8 knowledge8 vector8 processor8 reasoning8 machine8", 6),
        ["context8", "knowledge8", "vector8", "processor8", "reasoning8", "machine8"],
    ),
    (
        ("context8 knowledge8 vector8 processor8 reasoning8 machine8", 10),
        ["context8", "knowledge8", "vector8", "processor8", "reasoning8", "machine8"],
    ),
    (
        ("context8 knowledge8 vector8 processor8 reasoning8 machine8", 18),
        ["context8", "knowledge8 vector8", "processor8", "reasoning8", "machine8"],
    ),
    (
        ("context8 knowledge8 vector8 processor8 reasoning8 machine8", 28),
        ["context8 knowledge8 vector8", "processor8 reasoning8", "machine8"],
    ),
    (
        ("knowledge8 vector8 processor8 reasoning8 machine8 learning8", 6),
        ["knowledge8", "vector8", "processor8", "reasoning8", "machine8", "learning8"],
    ),
    (
        ("knowledge8 vector8 processor8 reasoning8 machine8 learning8", 10),
        ["knowledge8", "vector8", "processor8", "reasoning8", "machine8", "learning8"],
    ),
    (
        ("knowledge8 vector8 processor8 reasoning8 machine8 learning8", 18),
        ["knowledge8 vector8", "processor8", "reasoning8", "machine8 learning8"],
    ),
    (
        ("knowledge8 vector8 processor8 reasoning8 machine8 learning8", 28),
        ["knowledge8 vector8", "processor8 reasoning8", "machine8 learning8"],
    ),
    (
        ("vector8 processor8 reasoning8 machine8 learning8 model8", 6),
        ["vector8", "processor8", "reasoning8", "machine8", "learning8", "model8"],
    ),
    (
        ("vector8 processor8 reasoning8 machine8 learning8 model8", 10),
        ["vector8", "processor8", "reasoning8", "machine8", "learning8", "model8"],
    ),
    (
        ("vector8 processor8 reasoning8 machine8 learning8 model8", 18),
        ["vector8 processor8", "reasoning8", "machine8 learning8", "model8"],
    ),
    (
        ("vector8 processor8 reasoning8 machine8 learning8 model8", 28),
        ["vector8 processor8", "reasoning8 machine8", "learning8 model8"],
    ),
    (
        ("processor8 reasoning8 machine8 learning8 model8 token8", 6),
        ["processor8", "reasoning8", "machine8", "learning8", "model8", "token8"],
    ),
    (
        ("processor8 reasoning8 machine8 learning8 model8 token8", 10),
        ["processor8", "reasoning8", "machine8", "learning8", "model8", "token8"],
    ),
    (
        ("processor8 reasoning8 machine8 learning8 model8 token8", 18),
        ["processor8", "reasoning8", "machine8 learning8", "model8 token8"],
    ),
    (
        ("processor8 reasoning8 machine8 learning8 model8 token8", 28),
        ["processor8 reasoning8", "machine8 learning8 model8", "token8"],
    ),
    (
        ("reasoning8 machine8 learning8 model8 token8 prompt8", 6),
        ["reasoning8", "machine8", "learning8", "model8", "token8", "prompt8"],
    ),
    (
        ("reasoning8 machine8 learning8 model8 token8 prompt8", 10),
        ["reasoning8", "machine8", "learning8", "model8", "token8", "prompt8"],
    ),
    (
        ("reasoning8 machine8 learning8 model8 token8 prompt8", 18),
        ["reasoning8", "machine8 learning8", "model8 token8", "prompt8"],
    ),
    (
        ("reasoning8 machine8 learning8 model8 token8 prompt8", 28),
        ["reasoning8 machine8", "learning8 model8 token8", "prompt8"],
    ),
    (
        ("machine8 learning8 model8 token8 prompt8 session8", 6),
        ["machine8", "learning8", "model8", "token8", "prompt8", "session8"],
    ),
    (
        ("machine8 learning8 model8 token8 prompt8 session8", 10),
        ["machine8", "learning8", "model8", "token8", "prompt8", "session8"],
    ),
    (
        ("machine8 learning8 model8 token8 prompt8 session8", 18),
        ["machine8 learning8", "model8 token8", "prompt8 session8"],
    ),
    (
        ("machine8 learning8 model8 token8 prompt8 session8", 28),
        ["machine8 learning8 model8", "token8 prompt8 session8"],
    ),
    (
        ("learning8 model8 token8 prompt8 session8 library8", 6),
        ["learning8", "model8", "token8", "prompt8", "session8", "library8"],
    ),
    (
        ("learning8 model8 token8 prompt8 session8 library8", 10),
        ["learning8", "model8", "token8", "prompt8", "session8", "library8"],
    ),
    (
        ("learning8 model8 token8 prompt8 session8 library8", 18),
        ["learning8 model8", "token8 prompt8", "session8 library8"],
    ),
    (
        ("learning8 model8 token8 prompt8 session8 library8", 28),
        ["learning8 model8 token8", "prompt8 session8 library8"],
    ),
    (
        ("model8 token8 prompt8 session8 library8 service8", 6),
        ["model8", "token8", "prompt8", "session8", "library8", "service8"],
    ),
    (
        ("model8 token8 prompt8 session8 library8 service8", 10),
        ["model8", "token8", "prompt8", "session8", "library8", "service8"],
    ),
    (
        ("model8 token8 prompt8 session8 library8 service8", 18),
        ["model8 token8", "prompt8 session8", "library8 service8"],
    ),
    (("model8 token8 prompt8 session8 library8 service8", 28), ["model8 token8 prompt8", "session8 library8 service8"]),
    (
        ("token8 prompt8 session8 library8 service8 gateway8", 6),
        ["token8", "prompt8", "session8", "library8", "service8", "gateway8"],
    ),
    (
        ("token8 prompt8 session8 library8 service8 gateway8", 10),
        ["token8", "prompt8", "session8", "library8", "service8", "gateway8"],
    ),
    (
        ("token8 prompt8 session8 library8 service8 gateway8", 18),
        ["token8 prompt8", "session8 library8", "service8 gateway8"],
    ),
    (
        ("token8 prompt8 session8 library8 service8 gateway8", 28),
        ["token8 prompt8 session8", "library8 service8 gateway8"],
    ),
    (
        ("prompt8 session8 library8 service8 gateway8 storage8", 6),
        ["prompt8", "session8", "library8", "service8", "gateway8", "storage8"],
    ),
    (
        ("prompt8 session8 library8 service8 gateway8 storage8", 10),
        ["prompt8", "session8", "library8", "service8", "gateway8", "storage8"],
    ),
    (
        ("prompt8 session8 library8 service8 gateway8 storage8", 18),
        ["prompt8 session8", "library8 service8", "gateway8 storage8"],
    ),
    (
        ("prompt8 session8 library8 service8 gateway8 storage8", 28),
        ["prompt8 session8 library8", "service8 gateway8 storage8"],
    ),
    (
        ("session8 library8 service8 gateway8 storage8 network8", 6),
        ["session8", "library8", "service8", "gateway8", "storage8", "network8"],
    ),
    (
        ("session8 library8 service8 gateway8 storage8 network8", 10),
        ["session8", "library8", "service8", "gateway8", "storage8", "network8"],
    ),
    (
        ("session8 library8 service8 gateway8 storage8 network8", 18),
        ["session8 library8", "service8 gateway8", "storage8 network8"],
    ),
    (
        ("session8 library8 service8 gateway8 storage8 network8", 28),
        ["session8 library8 service8", "gateway8 storage8 network8"],
    ),
    (
        ("library8 service8 gateway8 storage8 network8 latency8", 6),
        ["library8", "service8", "gateway8", "storage8", "network8", "latency8"],
    ),
    (
        ("library8 service8 gateway8 storage8 network8 latency8", 10),
        ["library8", "service8", "gateway8", "storage8", "network8", "latency8"],
    ),
    (
        ("library8 service8 gateway8 storage8 network8 latency8", 18),
        ["library8 service8", "gateway8 storage8", "network8 latency8"],
    ),
    (
        ("library8 service8 gateway8 storage8 network8 latency8", 28),
        ["library8 service8 gateway8", "storage8 network8 latency8"],
    ),
    (
        ("service8 gateway8 storage8 network8 latency8 buffer8", 6),
        ["service8", "gateway8", "storage8", "network8", "latency8", "buffer8"],
    ),
    (
        ("service8 gateway8 storage8 network8 latency8 buffer8", 10),
        ["service8", "gateway8", "storage8", "network8", "latency8", "buffer8"],
    ),
    (
        ("service8 gateway8 storage8 network8 latency8 buffer8", 18),
        ["service8 gateway8", "storage8 network8", "latency8 buffer8"],
    ),
    (
        ("service8 gateway8 storage8 network8 latency8 buffer8", 28),
        ["service8 gateway8 storage8", "network8 latency8 buffer8"],
    ),
    (
        ("gateway8 storage8 network8 latency8 buffer8 queue8", 6),
        ["gateway8", "storage8", "network8", "latency8", "buffer8", "queue8"],
    ),
    (
        ("gateway8 storage8 network8 latency8 buffer8 queue8", 10),
        ["gateway8", "storage8", "network8", "latency8", "buffer8", "queue8"],
    ),
    (
        ("gateway8 storage8 network8 latency8 buffer8 queue8", 18),
        ["gateway8 storage8", "network8 latency8", "buffer8 queue8"],
    ),
    (
        ("gateway8 storage8 network8 latency8 buffer8 queue8", 28),
        ["gateway8 storage8 network8", "latency8 buffer8 queue8"],
    ),
    (
        ("storage8 network8 latency8 buffer8 queue8 worker8", 6),
        ["storage8", "network8", "latency8", "buffer8", "queue8", "worker8"],
    ),
    (
        ("storage8 network8 latency8 buffer8 queue8 worker8", 10),
        ["storage8", "network8", "latency8", "buffer8", "queue8", "worker8"],
    ),
    (
        ("storage8 network8 latency8 buffer8 queue8 worker8", 18),
        ["storage8 network8", "latency8 buffer8", "queue8 worker8"],
    ),
    (
        ("storage8 network8 latency8 buffer8 queue8 worker8", 28),
        ["storage8 network8 latency8", "buffer8 queue8 worker8"],
    ),
    (
        ("network8 latency8 buffer8 queue8 worker8 kernel8", 6),
        ["network8", "latency8", "buffer8", "queue8", "worker8", "kernel8"],
    ),
    (
        ("network8 latency8 buffer8 queue8 worker8 kernel8", 10),
        ["network8", "latency8", "buffer8", "queue8", "worker8", "kernel8"],
    ),
    (
        ("network8 latency8 buffer8 queue8 worker8 kernel8", 18),
        ["network8 latency8", "buffer8 queue8", "worker8 kernel8"],
    ),
    (("network8 latency8 buffer8 queue8 worker8 kernel8", 28), ["network8 latency8 buffer8", "queue8 worker8 kernel8"]),
    (
        ("latency8 buffer8 queue8 worker8 kernel8 signal8", 6),
        ["latency8", "buffer8", "queue8", "worker8", "kernel8", "signal8"],
    ),
    (
        ("latency8 buffer8 queue8 worker8 kernel8 signal8", 10),
        ["latency8", "buffer8", "queue8", "worker8", "kernel8", "signal8"],
    ),
    (
        ("latency8 buffer8 queue8 worker8 kernel8 signal8", 18),
        ["latency8 buffer8", "queue8 worker8", "kernel8 signal8"],
    ),
    (("latency8 buffer8 queue8 worker8 kernel8 signal8", 28), ["latency8 buffer8 queue8", "worker8 kernel8 signal8"]),
    (
        ("buffer8 queue8 worker8 kernel8 signal8 packet8", 6),
        ["buffer8", "queue8", "worker8", "kernel8", "signal8", "packet8"],
    ),
    (
        ("buffer8 queue8 worker8 kernel8 signal8 packet8", 10),
        ["buffer8", "queue8", "worker8", "kernel8", "signal8", "packet8"],
    ),
    (("buffer8 queue8 worker8 kernel8 signal8 packet8", 18), ["buffer8 queue8", "worker8 kernel8", "signal8 packet8"]),
    (("buffer8 queue8 worker8 kernel8 signal8 packet8", 28), ["buffer8 queue8 worker8", "kernel8 signal8 packet8"]),
    (
        ("queue8 worker8 kernel8 signal8 packet8 router8", 6),
        ["queue8", "worker8", "kernel8", "signal8", "packet8", "router8"],
    ),
    (
        ("queue8 worker8 kernel8 signal8 packet8 router8", 10),
        ["queue8", "worker8", "kernel8", "signal8", "packet8", "router8"],
    ),
    (("queue8 worker8 kernel8 signal8 packet8 router8", 18), ["queue8 worker8", "kernel8 signal8", "packet8 router8"]),
    (("queue8 worker8 kernel8 signal8 packet8 router8", 28), ["queue8 worker8 kernel8", "signal8 packet8 router8"]),
    (
        ("worker8 kernel8 signal8 packet8 router8 cluster8", 6),
        ["worker8", "kernel8", "signal8", "packet8", "router8", "cluster8"],
    ),
    (
        ("worker8 kernel8 signal8 packet8 router8 cluster8", 10),
        ["worker8", "kernel8", "signal8", "packet8", "router8", "cluster8"],
    ),
    (
        ("worker8 kernel8 signal8 packet8 router8 cluster8", 18),
        ["worker8 kernel8", "signal8 packet8", "router8 cluster8"],
    ),
    (("worker8 kernel8 signal8 packet8 router8 cluster8", 28), ["worker8 kernel8 signal8", "packet8 router8 cluster8"]),
    (
        ("kernel8 signal8 packet8 router8 cluster8 mirror8", 6),
        ["kernel8", "signal8", "packet8", "router8", "cluster8", "mirror8"],
    ),
    (
        ("kernel8 signal8 packet8 router8 cluster8 mirror8", 10),
        ["kernel8", "signal8", "packet8", "router8", "cluster8", "mirror8"],
    ),
    (
        ("kernel8 signal8 packet8 router8 cluster8 mirror8", 18),
        ["kernel8 signal8", "packet8 router8", "cluster8 mirror8"],
    ),
    (("kernel8 signal8 packet8 router8 cluster8 mirror8", 28), ["kernel8 signal8 packet8", "router8 cluster8 mirror8"]),
    (
        ("signal8 packet8 router8 cluster8 mirror8 filter8", 6),
        ["signal8", "packet8", "router8", "cluster8", "mirror8", "filter8"],
    ),
    (
        ("signal8 packet8 router8 cluster8 mirror8 filter8", 10),
        ["signal8", "packet8", "router8", "cluster8", "mirror8", "filter8"],
    ),
    (
        ("signal8 packet8 router8 cluster8 mirror8 filter8", 18),
        ["signal8 packet8", "router8 cluster8", "mirror8 filter8"],
    ),
    (("signal8 packet8 router8 cluster8 mirror8 filter8", 28), ["signal8 packet8 router8", "cluster8 mirror8 filter8"]),
    (
        ("packet8 router8 cluster8 mirror8 filter8 ranking8", 6),
        ["packet8", "router8", "cluster8", "mirror8", "filter8", "ranking8"],
    ),
    (
        ("packet8 router8 cluster8 mirror8 filter8 ranking8", 10),
        ["packet8", "router8", "cluster8", "mirror8", "filter8", "ranking8"],
    ),
    (
        ("packet8 router8 cluster8 mirror8 filter8 ranking8", 18),
        ["packet8 router8", "cluster8 mirror8", "filter8 ranking8"],
    ),
    (
        ("packet8 router8 cluster8 mirror8 filter8 ranking8", 28),
        ["packet8 router8 cluster8", "mirror8 filter8 ranking8"],
    ),
    (
        ("router8 cluster8 mirror8 filter8 ranking8 encoding8", 6),
        ["router8", "cluster8", "mirror8", "filter8", "ranking8", "encoding8"],
    ),
    (
        ("router8 cluster8 mirror8 filter8 ranking8 encoding8", 10),
        ["router8", "cluster8", "mirror8", "filter8", "ranking8", "encoding8"],
    ),
    (
        ("router8 cluster8 mirror8 filter8 ranking8 encoding8", 18),
        ["router8 cluster8", "mirror8 filter8", "ranking8 encoding8"],
    ),
    (
        ("router8 cluster8 mirror8 filter8 ranking8 encoding8", 28),
        ["router8 cluster8 mirror8", "filter8 ranking8 encoding8"],
    ),
    (
        ("cluster8 mirror8 filter8 ranking8 encoding8 mapping8", 6),
        ["cluster8", "mirror8", "filter8", "ranking8", "encoding8", "mapping8"],
    ),
    (
        ("cluster8 mirror8 filter8 ranking8 encoding8 mapping8", 10),
        ["cluster8", "mirror8", "filter8", "ranking8", "encoding8", "mapping8"],
    ),
    (
        ("cluster8 mirror8 filter8 ranking8 encoding8 mapping8", 18),
        ["cluster8 mirror8", "filter8 ranking8", "encoding8 mapping8"],
    ),
    (
        ("cluster8 mirror8 filter8 ranking8 encoding8 mapping8", 28),
        ["cluster8 mirror8 filter8", "ranking8 encoding8 mapping8"],
    ),
    (
        ("mirror8 filter8 ranking8 encoding8 mapping8 record8", 6),
        ["mirror8", "filter8", "ranking8", "encoding8", "mapping8", "record8"],
    ),
    (
        ("mirror8 filter8 ranking8 encoding8 mapping8 record8", 10),
        ["mirror8", "filter8", "ranking8", "encoding8", "mapping8", "record8"],
    ),
    (
        ("mirror8 filter8 ranking8 encoding8 mapping8 record8", 18),
        ["mirror8 filter8", "ranking8 encoding8", "mapping8 record8"],
    ),
    (
        ("mirror8 filter8 ranking8 encoding8 mapping8 record8", 28),
        ["mirror8 filter8 ranking8", "encoding8 mapping8 record8"],
    ),
    (
        ("filter8 ranking8 encoding8 mapping8 record8 candle8", 6),
        ["filter8", "ranking8", "encoding8", "mapping8", "record8", "candle8"],
    ),
    (
        ("filter8 ranking8 encoding8 mapping8 record8 candle8", 10),
        ["filter8", "ranking8", "encoding8", "mapping8", "record8", "candle8"],
    ),
    (
        ("filter8 ranking8 encoding8 mapping8 record8 candle8", 18),
        ["filter8 ranking8", "encoding8 mapping8", "record8 candle8"],
    ),
    (
        ("filter8 ranking8 encoding8 mapping8 record8 candle8", 28),
        ["filter8 ranking8 encoding8", "mapping8 record8 candle8"],
    ),
    (
        ("ranking8 encoding8 mapping8 record8 candle8 thread8", 6),
        ["ranking8", "encoding8", "mapping8", "record8", "candle8", "thread8"],
    ),
    (
        ("ranking8 encoding8 mapping8 record8 candle8 thread8", 10),
        ["ranking8", "encoding8", "mapping8", "record8", "candle8", "thread8"],
    ),
    (
        ("ranking8 encoding8 mapping8 record8 candle8 thread8", 18),
        ["ranking8 encoding8", "mapping8 record8", "candle8 thread8"],
    ),
    (
        ("ranking8 encoding8 mapping8 record8 candle8 thread8", 28),
        ["ranking8 encoding8 mapping8", "record8 candle8 thread8"],
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
