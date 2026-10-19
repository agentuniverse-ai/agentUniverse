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
        ("round 167: the quick brown fox jumps over the lazy dog", 4),
        ["round", "167:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", 8),
        ["round", "167: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", 12),
        ["round 167:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", 16),
        ["round 167: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", 24),
        ["round 167: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 167: the quick brown fox jumps over the lazy dog", 32),
        ["round 167: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", 4),
        ["round", "167:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", 8),
        ["round", "167:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", 12),
        ["round 167:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", 16),
        ["round 167:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", 24),
        ["round 167: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 167: agentuniverse is a framework for multi agents", 32),
        ["round 167: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", 4),
        ["round", "167:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", 8),
        ["round", "167:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", 12),
        ["round 167:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", 16),
        ["round 167:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", 24),
        ["round 167: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 167: knowledge stored as vectors enables retrieval", 32),
        ["round 167: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 167: the processor reads the record then stops", 4),
        ["round", "167:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 167: the processor reads the record then stops", 8),
        ["round", "167: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 167: the processor reads the record then stops", 12),
        ["round 167:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 167: the processor reads the record then stops", 16),
        ["round 167: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 167: the processor reads the record then stops", 24),
        ["round 167: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 167: the processor reads the record then stops", 32),
        ["round 167: the processor reads", "the record then stops"],
    ),
    (
        ("round 167: a worker pulls the next task from the queue", 4),
        ["round", "167:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 167: a worker pulls the next task from the queue", 8),
        ["round", "167: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 167: a worker pulls the next task from the queue", 12),
        ["round 167: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 167: a worker pulls the next task from the queue", 16),
        ["round 167: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 167: a worker pulls the next task from the queue", 24),
        ["round 167: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 167: a worker pulls the next task from the queue", 32),
        ["round 167: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 167: signals travel through the network layer", 4),
        ["round", "167:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 167: signals travel through the network layer", 8),
        ["round", "167:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 167: signals travel through the network layer", 12),
        ["round 167:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 167: signals travel through the network layer", 16),
        ["round 167:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 167: signals travel through the network layer", 24),
        ["round 167: signals", "travel through the", "network layer"],
    ),
    (
        ("round 167: signals travel through the network layer", 32),
        ["round 167: signals travel", "through the network layer"],
    ),
    (
        ("round 167: the gateway routes each request by policy", 4),
        ["round", "167:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 167: the gateway routes each request by policy", 8),
        ["round", "167: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 167: the gateway routes each request by policy", 12),
        ["round 167:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 167: the gateway routes each request by policy", 16),
        ["round 167: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 167: the gateway routes each request by policy", 24),
        ["round 167: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 167: the gateway routes each request by policy", 32),
        ["round 167: the gateway routes", "each request by policy"],
    ),
    (
        ("round 167: memory grows until the buffer is full", 4),
        ["round", "167:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 167: memory grows until the buffer is full", 8),
        ["round", "167:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 167: memory grows until the buffer is full", 12),
        ["round 167:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 167: memory grows until the buffer is full", 16),
        ["round 167:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 167: memory grows until the buffer is full", 24), ["round 167: memory grows", "until the buffer is full"]),
    (("round 167: memory grows until the buffer is full", 32), ["round 167: memory grows until", "the buffer is full"]),
    (
        ("round 167: the cluster mirrors every packet twice", 4),
        ["round", "167:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 167: the cluster mirrors every packet twice", 8),
        ["round", "167: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 167: the cluster mirrors every packet twice", 12),
        ["round 167:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 167: the cluster mirrors every packet twice", 16),
        ["round 167: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 167: the cluster mirrors every packet twice", 24),
        ["round 167: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 167: the cluster mirrors every packet twice", 32),
        ["round 167: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", 4),
        ["round", "167:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", 8),
        ["round", "167:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", 12),
        ["round 167:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", 16),
        ["round 167:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", 24),
        ["round 167: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 167: ranking uses tokens learned from the corpus", 32),
        ["round 167: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 167: a long session ends when the candle dies", 4),
        ["round", "167:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 167: a long session ends when the candle dies", 8),
        ["round", "167: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 167: a long session ends when the candle dies", 12),
        ["round 167: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 167: a long session ends when the candle dies", 16),
        ["round 167: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 167: a long session ends when the candle dies", 24),
        ["round 167: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 167: a long session ends when the candle dies", 32),
        ["round 167: a long session ends", "when the candle dies"],
    ),
    (
        ("round 167: encode the prompt then map the result", 4),
        ["round", "167:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 167: encode the prompt then map the result", 8),
        ["round", "167:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 167: encode the prompt then map the result", 12),
        ["round 167:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 167: encode the prompt then map the result", 16),
        ["round 167:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 167: encode the prompt then map the result", 24),
        ["round 167: encode the", "prompt then map the", "result"],
    ),
    (("round 167: encode the prompt then map the result", 32), ["round 167: encode the prompt", "then map the result"]),
    (
        ("round 167: the kernel wakes the worker at dawn", 4),
        ["round", "167:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 167: the kernel wakes the worker at dawn", 8),
        ["round", "167: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 167: the kernel wakes the worker at dawn", 12),
        ["round 167:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 167: the kernel wakes the worker at dawn", 16), ["round 167: the", "kernel wakes the", "worker at dawn"]),
    (("round 167: the kernel wakes the worker at dawn", 24), ["round 167: the kernel", "wakes the worker at dawn"]),
    (("round 167: the kernel wakes the worker at dawn", 32), ["round 167: the kernel wakes the", "worker at dawn"]),
    (
        ("round 167: service latency drops after the patch", 4),
        ["round", "167:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 167: service latency drops after the patch", 8),
        ["round", "167:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 167: service latency drops after the patch", 12),
        ["round 167:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 167: service latency drops after the patch", 16),
        ["round 167:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 167: service latency drops after the patch", 24),
        ["round 167: service", "latency drops after the", "patch"],
    ),
    (("round 167: service latency drops after the patch", 32), ["round 167: service latency drops", "after the patch"]),
    (
        ("round 167: the library caches every vector it sees", 4),
        ["round", "167:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 167: the library caches every vector it sees", 8),
        ["round", "167: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 167: the library caches every vector it sees", 12),
        ["round 167:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 167: the library caches every vector it sees", 16),
        ["round 167: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 167: the library caches every vector it sees", 24),
        ["round 167: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 167: the library caches every vector it sees", 32),
        ["round 167: the library caches", "every vector it sees"],
    ),
    (
        ("round 167: agents argue then the debate resolves", 4),
        ["round", "167:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 167: agents argue then the debate resolves", 8),
        ["round", "167:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 167: agents argue then the debate resolves", 12),
        ["round 167:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 167: agents argue then the debate resolves", 16),
        ["round 167:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 167: agents argue then the debate resolves", 24), ["round 167: agents argue", "then the debate resolves"]),
    (("round 167: agents argue then the debate resolves", 32), ["round 167: agents argue then the", "debate resolves"]),
    (
        ("round 167: the filter keeps only strong matches", 4),
        ["round", "167:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 167: the filter keeps only strong matches", 8),
        ["round", "167: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 167: the filter keeps only strong matches", 12),
        ["round 167:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 167: the filter keeps only strong matches", 16),
        ["round 167: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 167: the filter keeps only strong matches", 24),
        ["round 167: the filter", "keeps only strong", "matches"],
    ),
    (("round 167: the filter keeps only strong matches", 32), ["round 167: the filter keeps only", "strong matches"]),
    (
        ("round 167: the model answers with a short reply", 4),
        ["round", "167:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 167: the model answers with a short reply", 8),
        ["round", "167: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 167: the model answers with a short reply", 12),
        ["round 167:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 167: the model answers with a short reply", 16),
        ["round 167: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 167: the model answers with a short reply", 24),
        ["round 167: the model", "answers with a short", "reply"],
    ),
    (("round 167: the model answers with a short reply", 32), ["round 167: the model answers", "with a short reply"]),
    (
        ("round 167: the recorder stores the reasoning trace", 4),
        ["round", "167:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 167: the recorder stores the reasoning trace", 8),
        ["round", "167: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 167: the recorder stores the reasoning trace", 12),
        ["round 167:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 167: the recorder stores the reasoning trace", 16),
        ["round 167: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 167: the recorder stores the reasoning trace", 24),
        ["round 167: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 167: the recorder stores the reasoning trace", 32),
        ["round 167: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 167: the angel watches the processor run", 4),
        ["round", "167:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 167: the angel watches the processor run", 8),
        ["round", "167: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 167: the angel watches the processor run", 12),
        ["round 167:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 167: the angel watches the processor run", 16),
        ["round 167: the", "angel watches", "the processor", "run"],
    ),
    (("round 167: the angel watches the processor run", 24), ["round 167: the angel", "watches the processor", "run"]),
    (("round 167: the angel watches the processor run", 32), ["round 167: the angel watches the", "processor run"]),
    (
        ("round 167: angle of the vector decides the match", 4),
        ["round", "167:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 167: angle of the vector decides the match", 8),
        ["round", "167:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 167: angle of the vector decides the match", 12),
        ["round 167:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 167: angle of the vector decides the match", 16),
        ["round 167: angle", "of the vector", "decides the", "match"],
    ),
    (("round 167: angle of the vector decides the match", 24), ["round 167: angle of the", "vector decides the match"]),
    (("round 167: angle of the vector decides the match", 32), ["round 167: angle of the vector", "decides the match"]),
    (
        ("round 167: the candle burns twice as long at night", 4),
        ["round", "167:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 167: the candle burns twice as long at night", 8),
        ["round", "167: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 167: the candle burns twice as long at night", 12),
        ["round 167:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 167: the candle burns twice as long at night", 16),
        ["round 167: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 167: the candle burns twice as long at night", 24),
        ["round 167: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 167: the candle burns twice as long at night", 32),
        ["round 167: the candle burns", "twice as long at night"],
    ),
    (
        ("round 167: a mirror of the universe in one line", 4),
        ["round", "167:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 167: a mirror of the universe in one line", 8),
        ["round", "167: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 167: a mirror of the universe in one line", 12),
        ["round 167: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 167: a mirror of the universe in one line", 16),
        ["round 167: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 167: a mirror of the universe in one line", 24), ["round 167: a mirror of", "the universe in one line"]),
    (("round 167: a mirror of the universe in one line", 32), ["round 167: a mirror of the", "universe in one line"]),
    (
        ("round 167: the queue drains before the storm", 4),
        ["round", "167:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 167: the queue drains before the storm", 8),
        ["round", "167: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 167: the queue drains before the storm", 12),
        ["round 167:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 167: the queue drains before the storm", 16), ["round 167: the", "queue drains", "before the storm"]),
    (("round 167: the queue drains before the storm", 24), ["round 167: the queue", "drains before the storm"]),
    (("round 167: the queue drains before the storm", 32), ["round 167: the queue drains", "before the storm"]),
    (
        ("kitten167 sitting167 agent167 angle167 universe167 memory167", 6),
        ["kitten167", "sitting167", "agent167", "angle167", "universe167", "memory167"],
    ),
    (
        ("kitten167 sitting167 agent167 angle167 universe167 memory167", 10),
        ["kitten167", "sitting167", "agent167", "angle167", "universe167", "memory167"],
    ),
    (
        ("kitten167 sitting167 agent167 angle167 universe167 memory167", 18),
        ["kitten167", "sitting167", "agent167 angle167", "universe167", "memory167"],
    ),
    (
        ("kitten167 sitting167 agent167 angle167 universe167 memory167", 28),
        ["kitten167 sitting167", "agent167 angle167", "universe167 memory167"],
    ),
    (
        ("sitting167 agent167 angle167 universe167 memory167 stream167", 6),
        ["sitting167", "agent167", "angle167", "universe167", "memory167", "stream167"],
    ),
    (
        ("sitting167 agent167 angle167 universe167 memory167 stream167", 10),
        ["sitting167", "agent167", "angle167", "universe167", "memory167", "stream167"],
    ),
    (
        ("sitting167 agent167 angle167 universe167 memory167 stream167", 18),
        ["sitting167", "agent167 angle167", "universe167", "memory167", "stream167"],
    ),
    (
        ("sitting167 agent167 angle167 universe167 memory167 stream167", 28),
        ["sitting167 agent167 angle167", "universe167 memory167", "stream167"],
    ),
    (
        ("agent167 angle167 universe167 memory167 stream167 context167", 6),
        ["agent167", "angle167", "universe167", "memory167", "stream167", "context167"],
    ),
    (
        ("agent167 angle167 universe167 memory167 stream167 context167", 10),
        ["agent167", "angle167", "universe167", "memory167", "stream167", "context167"],
    ),
    (
        ("agent167 angle167 universe167 memory167 stream167 context167", 18),
        ["agent167 angle167", "universe167", "memory167", "stream167", "context167"],
    ),
    (
        ("agent167 angle167 universe167 memory167 stream167 context167", 28),
        ["agent167 angle167", "universe167 memory167", "stream167 context167"],
    ),
    (
        ("angle167 universe167 memory167 stream167 context167 knowledge167", 6),
        ["angle167", "universe167", "memory167", "stream167", "context167", "knowledge167"],
    ),
    (
        ("angle167 universe167 memory167 stream167 context167 knowledge167", 10),
        ["angle167", "universe167", "memory167", "stream167", "context167", "knowledge167"],
    ),
    (
        ("angle167 universe167 memory167 stream167 context167 knowledge167", 18),
        ["angle167", "universe167", "memory167", "stream167", "context167", "knowledge167"],
    ),
    (
        ("angle167 universe167 memory167 stream167 context167 knowledge167", 28),
        ["angle167 universe167", "memory167 stream167", "context167 knowledge167"],
    ),
    (
        ("universe167 memory167 stream167 context167 knowledge167 vector167", 6),
        ["universe167", "memory167", "stream167", "context167", "knowledge167", "vector167"],
    ),
    (
        ("universe167 memory167 stream167 context167 knowledge167 vector167", 10),
        ["universe167", "memory167", "stream167", "context167", "knowledge167", "vector167"],
    ),
    (
        ("universe167 memory167 stream167 context167 knowledge167 vector167", 18),
        ["universe167", "memory167", "stream167", "context167", "knowledge167", "vector167"],
    ),
    (
        ("universe167 memory167 stream167 context167 knowledge167 vector167", 28),
        ["universe167 memory167", "stream167 context167", "knowledge167 vector167"],
    ),
    (
        ("memory167 stream167 context167 knowledge167 vector167 processor167", 6),
        ["memory167", "stream167", "context167", "knowledge167", "vector167", "processor167"],
    ),
    (
        ("memory167 stream167 context167 knowledge167 vector167 processor167", 10),
        ["memory167", "stream167", "context167", "knowledge167", "vector167", "processor167"],
    ),
    (
        ("memory167 stream167 context167 knowledge167 vector167 processor167", 18),
        ["memory167", "stream167", "context167", "knowledge167", "vector167", "processor167"],
    ),
    (
        ("memory167 stream167 context167 knowledge167 vector167 processor167", 28),
        ["memory167 stream167", "context167 knowledge167", "vector167 processor167"],
    ),
    (
        ("stream167 context167 knowledge167 vector167 processor167 reasoning167", 6),
        ["stream167", "context167", "knowledge167", "vector167", "processor167", "reasoning167"],
    ),
    (
        ("stream167 context167 knowledge167 vector167 processor167 reasoning167", 10),
        ["stream167", "context167", "knowledge167", "vector167", "processor167", "reasoning167"],
    ),
    (
        ("stream167 context167 knowledge167 vector167 processor167 reasoning167", 18),
        ["stream167", "context167", "knowledge167", "vector167", "processor167", "reasoning167"],
    ),
    (
        ("stream167 context167 knowledge167 vector167 processor167 reasoning167", 28),
        ["stream167 context167", "knowledge167 vector167", "processor167 reasoning167"],
    ),
    (
        ("context167 knowledge167 vector167 processor167 reasoning167 machine167", 6),
        ["context167", "knowledge167", "vector167", "processor167", "reasoning167", "machine167"],
    ),
    (
        ("context167 knowledge167 vector167 processor167 reasoning167 machine167", 10),
        ["context167", "knowledge167", "vector167", "processor167", "reasoning167", "machine167"],
    ),
    (
        ("context167 knowledge167 vector167 processor167 reasoning167 machine167", 18),
        ["context167", "knowledge167", "vector167", "processor167", "reasoning167", "machine167"],
    ),
    (
        ("context167 knowledge167 vector167 processor167 reasoning167 machine167", 28),
        ["context167 knowledge167", "vector167 processor167", "reasoning167 machine167"],
    ),
    (
        ("knowledge167 vector167 processor167 reasoning167 machine167 learning167", 6),
        ["knowledge167", "vector167", "processor167", "reasoning167", "machine167", "learning167"],
    ),
    (
        ("knowledge167 vector167 processor167 reasoning167 machine167 learning167", 10),
        ["knowledge167", "vector167", "processor167", "reasoning167", "machine167", "learning167"],
    ),
    (
        ("knowledge167 vector167 processor167 reasoning167 machine167 learning167", 18),
        ["knowledge167", "vector167", "processor167", "reasoning167", "machine167", "learning167"],
    ),
    (
        ("knowledge167 vector167 processor167 reasoning167 machine167 learning167", 28),
        ["knowledge167 vector167", "processor167 reasoning167", "machine167 learning167"],
    ),
    (
        ("vector167 processor167 reasoning167 machine167 learning167 model167", 6),
        ["vector167", "processor167", "reasoning167", "machine167", "learning167", "model167"],
    ),
    (
        ("vector167 processor167 reasoning167 machine167 learning167 model167", 10),
        ["vector167", "processor167", "reasoning167", "machine167", "learning167", "model167"],
    ),
    (
        ("vector167 processor167 reasoning167 machine167 learning167 model167", 18),
        ["vector167", "processor167", "reasoning167", "machine167", "learning167", "model167"],
    ),
    (
        ("vector167 processor167 reasoning167 machine167 learning167 model167", 28),
        ["vector167 processor167", "reasoning167 machine167", "learning167 model167"],
    ),
    (
        ("processor167 reasoning167 machine167 learning167 model167 token167", 6),
        ["processor167", "reasoning167", "machine167", "learning167", "model167", "token167"],
    ),
    (
        ("processor167 reasoning167 machine167 learning167 model167 token167", 10),
        ["processor167", "reasoning167", "machine167", "learning167", "model167", "token167"],
    ),
    (
        ("processor167 reasoning167 machine167 learning167 model167 token167", 18),
        ["processor167", "reasoning167", "machine167", "learning167", "model167 token167"],
    ),
    (
        ("processor167 reasoning167 machine167 learning167 model167 token167", 28),
        ["processor167 reasoning167", "machine167 learning167", "model167 token167"],
    ),
    (
        ("reasoning167 machine167 learning167 model167 token167 prompt167", 6),
        ["reasoning167", "machine167", "learning167", "model167", "token167", "prompt167"],
    ),
    (
        ("reasoning167 machine167 learning167 model167 token167 prompt167", 10),
        ["reasoning167", "machine167", "learning167", "model167", "token167", "prompt167"],
    ),
    (
        ("reasoning167 machine167 learning167 model167 token167 prompt167", 18),
        ["reasoning167", "machine167", "learning167", "model167 token167", "prompt167"],
    ),
    (
        ("reasoning167 machine167 learning167 model167 token167 prompt167", 28),
        ["reasoning167 machine167", "learning167 model167", "token167 prompt167"],
    ),
    (
        ("machine167 learning167 model167 token167 prompt167 session167", 6),
        ["machine167", "learning167", "model167", "token167", "prompt167", "session167"],
    ),
    (
        ("machine167 learning167 model167 token167 prompt167 session167", 10),
        ["machine167", "learning167", "model167", "token167", "prompt167", "session167"],
    ),
    (
        ("machine167 learning167 model167 token167 prompt167 session167", 18),
        ["machine167", "learning167", "model167 token167", "prompt167", "session167"],
    ),
    (
        ("machine167 learning167 model167 token167 prompt167 session167", 28),
        ["machine167 learning167", "model167 token167 prompt167", "session167"],
    ),
    (
        ("learning167 model167 token167 prompt167 session167 library167", 6),
        ["learning167", "model167", "token167", "prompt167", "session167", "library167"],
    ),
    (
        ("learning167 model167 token167 prompt167 session167 library167", 10),
        ["learning167", "model167", "token167", "prompt167", "session167", "library167"],
    ),
    (
        ("learning167 model167 token167 prompt167 session167 library167", 18),
        ["learning167", "model167 token167", "prompt167", "session167", "library167"],
    ),
    (
        ("learning167 model167 token167 prompt167 session167 library167", 28),
        ["learning167 model167", "token167 prompt167", "session167 library167"],
    ),
    (
        ("model167 token167 prompt167 session167 library167 service167", 6),
        ["model167", "token167", "prompt167", "session167", "library167", "service167"],
    ),
    (
        ("model167 token167 prompt167 session167 library167 service167", 10),
        ["model167", "token167", "prompt167", "session167", "library167", "service167"],
    ),
    (
        ("model167 token167 prompt167 session167 library167 service167", 18),
        ["model167 token167", "prompt167", "session167", "library167", "service167"],
    ),
    (
        ("model167 token167 prompt167 session167 library167 service167", 28),
        ["model167 token167 prompt167", "session167 library167", "service167"],
    ),
    (
        ("token167 prompt167 session167 library167 service167 gateway167", 6),
        ["token167", "prompt167", "session167", "library167", "service167", "gateway167"],
    ),
    (
        ("token167 prompt167 session167 library167 service167 gateway167", 10),
        ["token167", "prompt167", "session167", "library167", "service167", "gateway167"],
    ),
    (
        ("token167 prompt167 session167 library167 service167 gateway167", 18),
        ["token167 prompt167", "session167", "library167", "service167", "gateway167"],
    ),
    (
        ("token167 prompt167 session167 library167 service167 gateway167", 28),
        ["token167 prompt167", "session167 library167", "service167 gateway167"],
    ),
    (
        ("prompt167 session167 library167 service167 gateway167 storage167", 6),
        ["prompt167", "session167", "library167", "service167", "gateway167", "storage167"],
    ),
    (
        ("prompt167 session167 library167 service167 gateway167 storage167", 10),
        ["prompt167", "session167", "library167", "service167", "gateway167", "storage167"],
    ),
    (
        ("prompt167 session167 library167 service167 gateway167 storage167", 18),
        ["prompt167", "session167", "library167", "service167", "gateway167", "storage167"],
    ),
    (
        ("prompt167 session167 library167 service167 gateway167 storage167", 28),
        ["prompt167 session167", "library167 service167", "gateway167 storage167"],
    ),
    (
        ("session167 library167 service167 gateway167 storage167 network167", 6),
        ["session167", "library167", "service167", "gateway167", "storage167", "network167"],
    ),
    (
        ("session167 library167 service167 gateway167 storage167 network167", 10),
        ["session167", "library167", "service167", "gateway167", "storage167", "network167"],
    ),
    (
        ("session167 library167 service167 gateway167 storage167 network167", 18),
        ["session167", "library167", "service167", "gateway167", "storage167", "network167"],
    ),
    (
        ("session167 library167 service167 gateway167 storage167 network167", 28),
        ["session167 library167", "service167 gateway167", "storage167 network167"],
    ),
    (
        ("library167 service167 gateway167 storage167 network167 latency167", 6),
        ["library167", "service167", "gateway167", "storage167", "network167", "latency167"],
    ),
    (
        ("library167 service167 gateway167 storage167 network167 latency167", 10),
        ["library167", "service167", "gateway167", "storage167", "network167", "latency167"],
    ),
    (
        ("library167 service167 gateway167 storage167 network167 latency167", 18),
        ["library167", "service167", "gateway167", "storage167", "network167", "latency167"],
    ),
    (
        ("library167 service167 gateway167 storage167 network167 latency167", 28),
        ["library167 service167", "gateway167 storage167", "network167 latency167"],
    ),
    (
        ("service167 gateway167 storage167 network167 latency167 buffer167", 6),
        ["service167", "gateway167", "storage167", "network167", "latency167", "buffer167"],
    ),
    (
        ("service167 gateway167 storage167 network167 latency167 buffer167", 10),
        ["service167", "gateway167", "storage167", "network167", "latency167", "buffer167"],
    ),
    (
        ("service167 gateway167 storage167 network167 latency167 buffer167", 18),
        ["service167", "gateway167", "storage167", "network167", "latency167", "buffer167"],
    ),
    (
        ("service167 gateway167 storage167 network167 latency167 buffer167", 28),
        ["service167 gateway167", "storage167 network167", "latency167 buffer167"],
    ),
    (
        ("gateway167 storage167 network167 latency167 buffer167 queue167", 6),
        ["gateway167", "storage167", "network167", "latency167", "buffer167", "queue167"],
    ),
    (
        ("gateway167 storage167 network167 latency167 buffer167 queue167", 10),
        ["gateway167", "storage167", "network167", "latency167", "buffer167", "queue167"],
    ),
    (
        ("gateway167 storage167 network167 latency167 buffer167 queue167", 18),
        ["gateway167", "storage167", "network167", "latency167", "buffer167 queue167"],
    ),
    (
        ("gateway167 storage167 network167 latency167 buffer167 queue167", 28),
        ["gateway167 storage167", "network167 latency167", "buffer167 queue167"],
    ),
    (
        ("storage167 network167 latency167 buffer167 queue167 worker167", 6),
        ["storage167", "network167", "latency167", "buffer167", "queue167", "worker167"],
    ),
    (
        ("storage167 network167 latency167 buffer167 queue167 worker167", 10),
        ["storage167", "network167", "latency167", "buffer167", "queue167", "worker167"],
    ),
    (
        ("storage167 network167 latency167 buffer167 queue167 worker167", 18),
        ["storage167", "network167", "latency167", "buffer167 queue167", "worker167"],
    ),
    (
        ("storage167 network167 latency167 buffer167 queue167 worker167", 28),
        ["storage167 network167", "latency167 buffer167", "queue167 worker167"],
    ),
    (
        ("network167 latency167 buffer167 queue167 worker167 kernel167", 6),
        ["network167", "latency167", "buffer167", "queue167", "worker167", "kernel167"],
    ),
    (
        ("network167 latency167 buffer167 queue167 worker167 kernel167", 10),
        ["network167", "latency167", "buffer167", "queue167", "worker167", "kernel167"],
    ),
    (
        ("network167 latency167 buffer167 queue167 worker167 kernel167", 18),
        ["network167", "latency167", "buffer167 queue167", "worker167", "kernel167"],
    ),
    (
        ("network167 latency167 buffer167 queue167 worker167 kernel167", 28),
        ["network167 latency167", "buffer167 queue167 worker167", "kernel167"],
    ),
    (
        ("latency167 buffer167 queue167 worker167 kernel167 signal167", 6),
        ["latency167", "buffer167", "queue167", "worker167", "kernel167", "signal167"],
    ),
    (
        ("latency167 buffer167 queue167 worker167 kernel167 signal167", 10),
        ["latency167", "buffer167", "queue167", "worker167", "kernel167", "signal167"],
    ),
    (
        ("latency167 buffer167 queue167 worker167 kernel167 signal167", 18),
        ["latency167", "buffer167 queue167", "worker167", "kernel167", "signal167"],
    ),
    (
        ("latency167 buffer167 queue167 worker167 kernel167 signal167", 28),
        ["latency167 buffer167", "queue167 worker167 kernel167", "signal167"],
    ),
    (
        ("buffer167 queue167 worker167 kernel167 signal167 packet167", 6),
        ["buffer167", "queue167", "worker167", "kernel167", "signal167", "packet167"],
    ),
    (
        ("buffer167 queue167 worker167 kernel167 signal167 packet167", 10),
        ["buffer167", "queue167", "worker167", "kernel167", "signal167", "packet167"],
    ),
    (
        ("buffer167 queue167 worker167 kernel167 signal167 packet167", 18),
        ["buffer167 queue167", "worker167", "kernel167", "signal167", "packet167"],
    ),
    (
        ("buffer167 queue167 worker167 kernel167 signal167 packet167", 28),
        ["buffer167 queue167 worker167", "kernel167 signal167", "packet167"],
    ),
    (
        ("queue167 worker167 kernel167 signal167 packet167 router167", 6),
        ["queue167", "worker167", "kernel167", "signal167", "packet167", "router167"],
    ),
    (
        ("queue167 worker167 kernel167 signal167 packet167 router167", 10),
        ["queue167", "worker167", "kernel167", "signal167", "packet167", "router167"],
    ),
    (
        ("queue167 worker167 kernel167 signal167 packet167 router167", 18),
        ["queue167 worker167", "kernel167", "signal167", "packet167", "router167"],
    ),
    (
        ("queue167 worker167 kernel167 signal167 packet167 router167", 28),
        ["queue167 worker167 kernel167", "signal167 packet167", "router167"],
    ),
    (
        ("worker167 kernel167 signal167 packet167 router167 cluster167", 6),
        ["worker167", "kernel167", "signal167", "packet167", "router167", "cluster167"],
    ),
    (
        ("worker167 kernel167 signal167 packet167 router167 cluster167", 10),
        ["worker167", "kernel167", "signal167", "packet167", "router167", "cluster167"],
    ),
    (
        ("worker167 kernel167 signal167 packet167 router167 cluster167", 18),
        ["worker167", "kernel167", "signal167", "packet167", "router167", "cluster167"],
    ),
    (
        ("worker167 kernel167 signal167 packet167 router167 cluster167", 28),
        ["worker167 kernel167", "signal167 packet167", "router167 cluster167"],
    ),
    (
        ("kernel167 signal167 packet167 router167 cluster167 mirror167", 6),
        ["kernel167", "signal167", "packet167", "router167", "cluster167", "mirror167"],
    ),
    (
        ("kernel167 signal167 packet167 router167 cluster167 mirror167", 10),
        ["kernel167", "signal167", "packet167", "router167", "cluster167", "mirror167"],
    ),
    (
        ("kernel167 signal167 packet167 router167 cluster167 mirror167", 18),
        ["kernel167", "signal167", "packet167", "router167", "cluster167", "mirror167"],
    ),
    (
        ("kernel167 signal167 packet167 router167 cluster167 mirror167", 28),
        ["kernel167 signal167", "packet167 router167", "cluster167 mirror167"],
    ),
    (
        ("signal167 packet167 router167 cluster167 mirror167 filter167", 6),
        ["signal167", "packet167", "router167", "cluster167", "mirror167", "filter167"],
    ),
    (
        ("signal167 packet167 router167 cluster167 mirror167 filter167", 10),
        ["signal167", "packet167", "router167", "cluster167", "mirror167", "filter167"],
    ),
    (
        ("signal167 packet167 router167 cluster167 mirror167 filter167", 18),
        ["signal167", "packet167", "router167", "cluster167", "mirror167", "filter167"],
    ),
    (
        ("signal167 packet167 router167 cluster167 mirror167 filter167", 28),
        ["signal167 packet167", "router167 cluster167", "mirror167 filter167"],
    ),
    (
        ("packet167 router167 cluster167 mirror167 filter167 ranking167", 6),
        ["packet167", "router167", "cluster167", "mirror167", "filter167", "ranking167"],
    ),
    (
        ("packet167 router167 cluster167 mirror167 filter167 ranking167", 10),
        ["packet167", "router167", "cluster167", "mirror167", "filter167", "ranking167"],
    ),
    (
        ("packet167 router167 cluster167 mirror167 filter167 ranking167", 18),
        ["packet167", "router167", "cluster167", "mirror167", "filter167", "ranking167"],
    ),
    (
        ("packet167 router167 cluster167 mirror167 filter167 ranking167", 28),
        ["packet167 router167", "cluster167 mirror167", "filter167 ranking167"],
    ),
    (
        ("router167 cluster167 mirror167 filter167 ranking167 encoding167", 6),
        ["router167", "cluster167", "mirror167", "filter167", "ranking167", "encoding167"],
    ),
    (
        ("router167 cluster167 mirror167 filter167 ranking167 encoding167", 10),
        ["router167", "cluster167", "mirror167", "filter167", "ranking167", "encoding167"],
    ),
    (
        ("router167 cluster167 mirror167 filter167 ranking167 encoding167", 18),
        ["router167", "cluster167", "mirror167", "filter167", "ranking167", "encoding167"],
    ),
    (
        ("router167 cluster167 mirror167 filter167 ranking167 encoding167", 28),
        ["router167 cluster167", "mirror167 filter167", "ranking167 encoding167"],
    ),
    (
        ("cluster167 mirror167 filter167 ranking167 encoding167 mapping167", 6),
        ["cluster167", "mirror167", "filter167", "ranking167", "encoding167", "mapping167"],
    ),
    (
        ("cluster167 mirror167 filter167 ranking167 encoding167 mapping167", 10),
        ["cluster167", "mirror167", "filter167", "ranking167", "encoding167", "mapping167"],
    ),
    (
        ("cluster167 mirror167 filter167 ranking167 encoding167 mapping167", 18),
        ["cluster167", "mirror167", "filter167", "ranking167", "encoding167", "mapping167"],
    ),
    (
        ("cluster167 mirror167 filter167 ranking167 encoding167 mapping167", 28),
        ["cluster167 mirror167", "filter167 ranking167", "encoding167 mapping167"],
    ),
    (
        ("mirror167 filter167 ranking167 encoding167 mapping167 record167", 6),
        ["mirror167", "filter167", "ranking167", "encoding167", "mapping167", "record167"],
    ),
    (
        ("mirror167 filter167 ranking167 encoding167 mapping167 record167", 10),
        ["mirror167", "filter167", "ranking167", "encoding167", "mapping167", "record167"],
    ),
    (
        ("mirror167 filter167 ranking167 encoding167 mapping167 record167", 18),
        ["mirror167", "filter167", "ranking167", "encoding167", "mapping167", "record167"],
    ),
    (
        ("mirror167 filter167 ranking167 encoding167 mapping167 record167", 28),
        ["mirror167 filter167", "ranking167 encoding167", "mapping167 record167"],
    ),
    (
        ("filter167 ranking167 encoding167 mapping167 record167 candle167", 6),
        ["filter167", "ranking167", "encoding167", "mapping167", "record167", "candle167"],
    ),
    (
        ("filter167 ranking167 encoding167 mapping167 record167 candle167", 10),
        ["filter167", "ranking167", "encoding167", "mapping167", "record167", "candle167"],
    ),
    (
        ("filter167 ranking167 encoding167 mapping167 record167 candle167", 18),
        ["filter167", "ranking167", "encoding167", "mapping167", "record167", "candle167"],
    ),
    (
        ("filter167 ranking167 encoding167 mapping167 record167 candle167", 28),
        ["filter167 ranking167", "encoding167 mapping167", "record167 candle167"],
    ),
    (
        ("ranking167 encoding167 mapping167 record167 candle167 thread167", 6),
        ["ranking167", "encoding167", "mapping167", "record167", "candle167", "thread167"],
    ),
    (
        ("ranking167 encoding167 mapping167 record167 candle167 thread167", 10),
        ["ranking167", "encoding167", "mapping167", "record167", "candle167", "thread167"],
    ),
    (
        ("ranking167 encoding167 mapping167 record167 candle167 thread167", 18),
        ["ranking167", "encoding167", "mapping167", "record167", "candle167", "thread167"],
    ),
    (
        ("ranking167 encoding167 mapping167 record167 candle167 thread167", 28),
        ["ranking167 encoding167", "mapping167 record167", "candle167 thread167"],
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
