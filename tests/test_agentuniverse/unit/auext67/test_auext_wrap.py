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
        ("round 67: the quick brown fox jumps over the lazy dog", 4),
        ["round", "67:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 67: the quick brown fox jumps over the lazy dog", 8),
        ["round", "67: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 67: the quick brown fox jumps over the lazy dog", 12),
        ["round 67:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 67: the quick brown fox jumps over the lazy dog", 16),
        ["round 67: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 67: the quick brown fox jumps over the lazy dog", 24),
        ["round 67: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 67: the quick brown fox jumps over the lazy dog", 32),
        ["round 67: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 67: agentuniverse is a framework for multi agents", 4),
        ["round", "67:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 67: agentuniverse is a framework for multi agents", 8),
        ["round", "67:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 67: agentuniverse is a framework for multi agents", 12),
        ["round 67:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 67: agentuniverse is a framework for multi agents", 16),
        ["round 67:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 67: agentuniverse is a framework for multi agents", 24),
        ["round 67: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 67: agentuniverse is a framework for multi agents", 32),
        ["round 67: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 67: knowledge stored as vectors enables retrieval", 4),
        ["round", "67:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 67: knowledge stored as vectors enables retrieval", 8),
        ["round", "67:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 67: knowledge stored as vectors enables retrieval", 12),
        ["round 67:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 67: knowledge stored as vectors enables retrieval", 16),
        ["round 67:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 67: knowledge stored as vectors enables retrieval", 24),
        ["round 67: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 67: knowledge stored as vectors enables retrieval", 32),
        ["round 67: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 67: the processor reads the record then stops", 4),
        ["round", "67:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 67: the processor reads the record then stops", 8),
        ["round", "67: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 67: the processor reads the record then stops", 12),
        ["round 67:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 67: the processor reads the record then stops", 16),
        ["round 67: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 67: the processor reads the record then stops", 24),
        ["round 67: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 67: the processor reads the record then stops", 32),
        ["round 67: the processor reads", "the record then stops"],
    ),
    (
        ("round 67: a worker pulls the next task from the queue", 4),
        ["round", "67:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 67: a worker pulls the next task from the queue", 8),
        ["round", "67: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 67: a worker pulls the next task from the queue", 12),
        ["round 67: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 67: a worker pulls the next task from the queue", 16),
        ["round 67: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 67: a worker pulls the next task from the queue", 24),
        ["round 67: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 67: a worker pulls the next task from the queue", 32),
        ["round 67: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 67: signals travel through the network layer", 4),
        ["round", "67:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 67: signals travel through the network layer", 8),
        ["round", "67:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 67: signals travel through the network layer", 12),
        ["round 67:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 67: signals travel through the network layer", 16),
        ["round 67:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 67: signals travel through the network layer", 24),
        ["round 67: signals travel", "through the network", "layer"],
    ),
    (
        ("round 67: signals travel through the network layer", 32),
        ["round 67: signals travel through", "the network layer"],
    ),
    (
        ("round 67: the gateway routes each request by policy", 4),
        ["round", "67:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 67: the gateway routes each request by policy", 8),
        ["round", "67: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 67: the gateway routes each request by policy", 12),
        ["round 67:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 67: the gateway routes each request by policy", 16),
        ["round 67: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 67: the gateway routes each request by policy", 24),
        ["round 67: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 67: the gateway routes each request by policy", 32),
        ["round 67: the gateway routes", "each request by policy"],
    ),
    (
        ("round 67: memory grows until the buffer is full", 4),
        ["round", "67:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 67: memory grows until the buffer is full", 8),
        ["round", "67:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 67: memory grows until the buffer is full", 12),
        ["round 67:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 67: memory grows until the buffer is full", 16),
        ["round 67: memory", "grows until the", "buffer is full"],
    ),
    (("round 67: memory grows until the buffer is full", 24), ["round 67: memory grows", "until the buffer is full"]),
    (("round 67: memory grows until the buffer is full", 32), ["round 67: memory grows until the", "buffer is full"]),
    (
        ("round 67: the cluster mirrors every packet twice", 4),
        ["round", "67:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 67: the cluster mirrors every packet twice", 8),
        ["round", "67: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 67: the cluster mirrors every packet twice", 12),
        ["round 67:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 67: the cluster mirrors every packet twice", 16),
        ["round 67: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 67: the cluster mirrors every packet twice", 24),
        ["round 67: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 67: the cluster mirrors every packet twice", 32), ["round 67: the cluster mirrors", "every packet twice"]),
    (
        ("round 67: ranking uses tokens learned from the corpus", 4),
        ["round", "67:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 67: ranking uses tokens learned from the corpus", 8),
        ["round", "67:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 67: ranking uses tokens learned from the corpus", 12),
        ["round 67:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 67: ranking uses tokens learned from the corpus", 16),
        ["round 67:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 67: ranking uses tokens learned from the corpus", 24),
        ["round 67: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 67: ranking uses tokens learned from the corpus", 32),
        ["round 67: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 67: a long session ends when the candle dies", 4),
        ["round", "67:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 67: a long session ends when the candle dies", 8),
        ["round", "67: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 67: a long session ends when the candle dies", 12),
        ["round 67: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 67: a long session ends when the candle dies", 16),
        ["round 67: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 67: a long session ends when the candle dies", 24),
        ["round 67: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 67: a long session ends when the candle dies", 32),
        ["round 67: a long session ends", "when the candle dies"],
    ),
    (
        ("round 67: encode the prompt then map the result", 4),
        ["round", "67:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 67: encode the prompt then map the result", 8),
        ["round", "67:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 67: encode the prompt then map the result", 12),
        ["round 67:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 67: encode the prompt then map the result", 16),
        ["round 67: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 67: encode the prompt then map the result", 24),
        ["round 67: encode the", "prompt then map the", "result"],
    ),
    (("round 67: encode the prompt then map the result", 32), ["round 67: encode the prompt then", "map the result"]),
    (
        ("round 67: the kernel wakes the worker at dawn", 4),
        ["round", "67:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 67: the kernel wakes the worker at dawn", 8),
        ["round", "67: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 67: the kernel wakes the worker at dawn", 12),
        ["round 67:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 67: the kernel wakes the worker at dawn", 16), ["round 67: the", "kernel wakes the", "worker at dawn"]),
    (("round 67: the kernel wakes the worker at dawn", 24), ["round 67: the kernel", "wakes the worker at dawn"]),
    (("round 67: the kernel wakes the worker at dawn", 32), ["round 67: the kernel wakes the", "worker at dawn"]),
    (
        ("round 67: service latency drops after the patch", 4),
        ["round", "67:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 67: service latency drops after the patch", 8),
        ["round", "67:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 67: service latency drops after the patch", 12),
        ["round 67:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 67: service latency drops after the patch", 16),
        ["round 67:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 67: service latency drops after the patch", 24),
        ["round 67: service", "latency drops after the", "patch"],
    ),
    (("round 67: service latency drops after the patch", 32), ["round 67: service latency drops", "after the patch"]),
    (
        ("round 67: the library caches every vector it sees", 4),
        ["round", "67:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 67: the library caches every vector it sees", 8),
        ["round", "67: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 67: the library caches every vector it sees", 12),
        ["round 67:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 67: the library caches every vector it sees", 16),
        ["round 67: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 67: the library caches every vector it sees", 24),
        ["round 67: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 67: the library caches every vector it sees", 32),
        ["round 67: the library caches", "every vector it sees"],
    ),
    (
        ("round 67: agents argue then the debate resolves", 4),
        ["round", "67:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 67: agents argue then the debate resolves", 8),
        ["round", "67:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 67: agents argue then the debate resolves", 12),
        ["round 67:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 67: agents argue then the debate resolves", 16),
        ["round 67: agents", "argue then the", "debate resolves"],
    ),
    (("round 67: agents argue then the debate resolves", 24), ["round 67: agents argue", "then the debate resolves"]),
    (("round 67: agents argue then the debate resolves", 32), ["round 67: agents argue then the", "debate resolves"]),
    (
        ("round 67: the filter keeps only strong matches", 4),
        ["round", "67:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 67: the filter keeps only strong matches", 8),
        ["round", "67: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 67: the filter keeps only strong matches", 12),
        ["round 67:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 67: the filter keeps only strong matches", 16),
        ["round 67: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 67: the filter keeps only strong matches", 24), ["round 67: the filter", "keeps only strong", "matches"]),
    (("round 67: the filter keeps only strong matches", 32), ["round 67: the filter keeps only", "strong matches"]),
    (
        ("round 67: the model answers with a short reply", 4),
        ["round", "67:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 67: the model answers with a short reply", 8),
        ["round", "67: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 67: the model answers with a short reply", 12),
        ["round 67:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 67: the model answers with a short reply", 16),
        ["round 67: the", "model answers", "with a short", "reply"],
    ),
    (("round 67: the model answers with a short reply", 24), ["round 67: the model", "answers with a short", "reply"]),
    (("round 67: the model answers with a short reply", 32), ["round 67: the model answers with", "a short reply"]),
    (
        ("round 67: the recorder stores the reasoning trace", 4),
        ["round", "67:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 67: the recorder stores the reasoning trace", 8),
        ["round", "67: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 67: the recorder stores the reasoning trace", 12),
        ["round 67:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 67: the recorder stores the reasoning trace", 16),
        ["round 67: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 67: the recorder stores the reasoning trace", 24),
        ["round 67: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 67: the recorder stores the reasoning trace", 32),
        ["round 67: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 67: the angel watches the processor run", 4),
        ["round", "67:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 67: the angel watches the processor run", 8),
        ["round", "67: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 67: the angel watches the processor run", 12),
        ["round 67:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 67: the angel watches the processor run", 16), ["round 67: the", "angel watches", "the processor", "run"]),
    (("round 67: the angel watches the processor run", 24), ["round 67: the angel", "watches the processor", "run"]),
    (("round 67: the angel watches the processor run", 32), ["round 67: the angel watches the", "processor run"]),
    (
        ("round 67: angle of the vector decides the match", 4),
        ["round", "67:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 67: angle of the vector decides the match", 8),
        ["round", "67:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 67: angle of the vector decides the match", 12),
        ["round 67:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 67: angle of the vector decides the match", 16),
        ["round 67: angle", "of the vector", "decides the", "match"],
    ),
    (("round 67: angle of the vector decides the match", 24), ["round 67: angle of the", "vector decides the match"]),
    (("round 67: angle of the vector decides the match", 32), ["round 67: angle of the vector", "decides the match"]),
    (
        ("round 67: the candle burns twice as long at night", 4),
        ["round", "67:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 67: the candle burns twice as long at night", 8),
        ["round", "67: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 67: the candle burns twice as long at night", 12),
        ["round 67:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 67: the candle burns twice as long at night", 16),
        ["round 67: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 67: the candle burns twice as long at night", 24),
        ["round 67: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 67: the candle burns twice as long at night", 32),
        ["round 67: the candle burns twice", "as long at night"],
    ),
    (
        ("round 67: a mirror of the universe in one line", 4),
        ["round", "67:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 67: a mirror of the universe in one line", 8),
        ["round", "67: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 67: a mirror of the universe in one line", 12),
        ["round 67: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 67: a mirror of the universe in one line", 16),
        ["round 67: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 67: a mirror of the universe in one line", 24), ["round 67: a mirror of", "the universe in one line"]),
    (("round 67: a mirror of the universe in one line", 32), ["round 67: a mirror of the", "universe in one line"]),
    (
        ("round 67: the queue drains before the storm", 4),
        ["round", "67:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 67: the queue drains before the storm", 8),
        ["round", "67: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 67: the queue drains before the storm", 12), ["round 67:", "the queue", "drains", "before the", "storm"]),
    (("round 67: the queue drains before the storm", 16), ["round 67: the", "queue drains", "before the storm"]),
    (("round 67: the queue drains before the storm", 24), ["round 67: the queue", "drains before the storm"]),
    (("round 67: the queue drains before the storm", 32), ["round 67: the queue drains", "before the storm"]),
    (
        ("kitten67 sitting67 agent67 angle67 universe67 memory67", 6),
        ["kitten67", "sitting67", "agent67", "angle67", "universe67", "memory67"],
    ),
    (
        ("kitten67 sitting67 agent67 angle67 universe67 memory67", 10),
        ["kitten67", "sitting67", "agent67", "angle67", "universe67", "memory67"],
    ),
    (
        ("kitten67 sitting67 agent67 angle67 universe67 memory67", 18),
        ["kitten67 sitting67", "agent67 angle67", "universe67", "memory67"],
    ),
    (
        ("kitten67 sitting67 agent67 angle67 universe67 memory67", 28),
        ["kitten67 sitting67 agent67", "angle67 universe67 memory67"],
    ),
    (
        ("sitting67 agent67 angle67 universe67 memory67 stream67", 6),
        ["sitting67", "agent67", "angle67", "universe67", "memory67", "stream67"],
    ),
    (
        ("sitting67 agent67 angle67 universe67 memory67 stream67", 10),
        ["sitting67", "agent67", "angle67", "universe67", "memory67", "stream67"],
    ),
    (
        ("sitting67 agent67 angle67 universe67 memory67 stream67", 18),
        ["sitting67 agent67", "angle67 universe67", "memory67 stream67"],
    ),
    (
        ("sitting67 agent67 angle67 universe67 memory67 stream67", 28),
        ["sitting67 agent67 angle67", "universe67 memory67 stream67"],
    ),
    (
        ("agent67 angle67 universe67 memory67 stream67 context67", 6),
        ["agent67", "angle67", "universe67", "memory67", "stream67", "context67"],
    ),
    (
        ("agent67 angle67 universe67 memory67 stream67 context67", 10),
        ["agent67", "angle67", "universe67", "memory67", "stream67", "context67"],
    ),
    (
        ("agent67 angle67 universe67 memory67 stream67 context67", 18),
        ["agent67 angle67", "universe67", "memory67 stream67", "context67"],
    ),
    (
        ("agent67 angle67 universe67 memory67 stream67 context67", 28),
        ["agent67 angle67 universe67", "memory67 stream67 context67"],
    ),
    (
        ("angle67 universe67 memory67 stream67 context67 knowledge67", 6),
        ["angle67", "universe67", "memory67", "stream67", "context67", "knowledge67"],
    ),
    (
        ("angle67 universe67 memory67 stream67 context67 knowledge67", 10),
        ["angle67", "universe67", "memory67", "stream67", "context67", "knowledge67"],
    ),
    (
        ("angle67 universe67 memory67 stream67 context67 knowledge67", 18),
        ["angle67 universe67", "memory67 stream67", "context67", "knowledge67"],
    ),
    (
        ("angle67 universe67 memory67 stream67 context67 knowledge67", 28),
        ["angle67 universe67 memory67", "stream67 context67", "knowledge67"],
    ),
    (
        ("universe67 memory67 stream67 context67 knowledge67 vector67", 6),
        ["universe67", "memory67", "stream67", "context67", "knowledge67", "vector67"],
    ),
    (
        ("universe67 memory67 stream67 context67 knowledge67 vector67", 10),
        ["universe67", "memory67", "stream67", "context67", "knowledge67", "vector67"],
    ),
    (
        ("universe67 memory67 stream67 context67 knowledge67 vector67", 18),
        ["universe67", "memory67 stream67", "context67", "knowledge67", "vector67"],
    ),
    (
        ("universe67 memory67 stream67 context67 knowledge67 vector67", 28),
        ["universe67 memory67 stream67", "context67 knowledge67", "vector67"],
    ),
    (
        ("memory67 stream67 context67 knowledge67 vector67 processor67", 6),
        ["memory67", "stream67", "context67", "knowledge67", "vector67", "processor67"],
    ),
    (
        ("memory67 stream67 context67 knowledge67 vector67 processor67", 10),
        ["memory67", "stream67", "context67", "knowledge67", "vector67", "processor67"],
    ),
    (
        ("memory67 stream67 context67 knowledge67 vector67 processor67", 18),
        ["memory67 stream67", "context67", "knowledge67", "vector67", "processor67"],
    ),
    (
        ("memory67 stream67 context67 knowledge67 vector67 processor67", 28),
        ["memory67 stream67 context67", "knowledge67 vector67", "processor67"],
    ),
    (
        ("stream67 context67 knowledge67 vector67 processor67 reasoning67", 6),
        ["stream67", "context67", "knowledge67", "vector67", "processor67", "reasoning67"],
    ),
    (
        ("stream67 context67 knowledge67 vector67 processor67 reasoning67", 10),
        ["stream67", "context67", "knowledge67", "vector67", "processor67", "reasoning67"],
    ),
    (
        ("stream67 context67 knowledge67 vector67 processor67 reasoning67", 18),
        ["stream67 context67", "knowledge67", "vector67", "processor67", "reasoning67"],
    ),
    (
        ("stream67 context67 knowledge67 vector67 processor67 reasoning67", 28),
        ["stream67 context67", "knowledge67 vector67", "processor67 reasoning67"],
    ),
    (
        ("context67 knowledge67 vector67 processor67 reasoning67 machine67", 6),
        ["context67", "knowledge67", "vector67", "processor67", "reasoning67", "machine67"],
    ),
    (
        ("context67 knowledge67 vector67 processor67 reasoning67 machine67", 10),
        ["context67", "knowledge67", "vector67", "processor67", "reasoning67", "machine67"],
    ),
    (
        ("context67 knowledge67 vector67 processor67 reasoning67 machine67", 18),
        ["context67", "knowledge67", "vector67", "processor67", "reasoning67", "machine67"],
    ),
    (
        ("context67 knowledge67 vector67 processor67 reasoning67 machine67", 28),
        ["context67 knowledge67", "vector67 processor67", "reasoning67 machine67"],
    ),
    (
        ("knowledge67 vector67 processor67 reasoning67 machine67 learning67", 6),
        ["knowledge67", "vector67", "processor67", "reasoning67", "machine67", "learning67"],
    ),
    (
        ("knowledge67 vector67 processor67 reasoning67 machine67 learning67", 10),
        ["knowledge67", "vector67", "processor67", "reasoning67", "machine67", "learning67"],
    ),
    (
        ("knowledge67 vector67 processor67 reasoning67 machine67 learning67", 18),
        ["knowledge67", "vector67", "processor67", "reasoning67", "machine67", "learning67"],
    ),
    (
        ("knowledge67 vector67 processor67 reasoning67 machine67 learning67", 28),
        ["knowledge67 vector67", "processor67 reasoning67", "machine67 learning67"],
    ),
    (
        ("vector67 processor67 reasoning67 machine67 learning67 model67", 6),
        ["vector67", "processor67", "reasoning67", "machine67", "learning67", "model67"],
    ),
    (
        ("vector67 processor67 reasoning67 machine67 learning67 model67", 10),
        ["vector67", "processor67", "reasoning67", "machine67", "learning67", "model67"],
    ),
    (
        ("vector67 processor67 reasoning67 machine67 learning67 model67", 18),
        ["vector67", "processor67", "reasoning67", "machine67", "learning67 model67"],
    ),
    (
        ("vector67 processor67 reasoning67 machine67 learning67 model67", 28),
        ["vector67 processor67", "reasoning67 machine67", "learning67 model67"],
    ),
    (
        ("processor67 reasoning67 machine67 learning67 model67 token67", 6),
        ["processor67", "reasoning67", "machine67", "learning67", "model67", "token67"],
    ),
    (
        ("processor67 reasoning67 machine67 learning67 model67 token67", 10),
        ["processor67", "reasoning67", "machine67", "learning67", "model67", "token67"],
    ),
    (
        ("processor67 reasoning67 machine67 learning67 model67 token67", 18),
        ["processor67", "reasoning67", "machine67", "learning67 model67", "token67"],
    ),
    (
        ("processor67 reasoning67 machine67 learning67 model67 token67", 28),
        ["processor67 reasoning67", "machine67 learning67 model67", "token67"],
    ),
    (
        ("reasoning67 machine67 learning67 model67 token67 prompt67", 6),
        ["reasoning67", "machine67", "learning67", "model67", "token67", "prompt67"],
    ),
    (
        ("reasoning67 machine67 learning67 model67 token67 prompt67", 10),
        ["reasoning67", "machine67", "learning67", "model67", "token67", "prompt67"],
    ),
    (
        ("reasoning67 machine67 learning67 model67 token67 prompt67", 18),
        ["reasoning67", "machine67", "learning67 model67", "token67 prompt67"],
    ),
    (
        ("reasoning67 machine67 learning67 model67 token67 prompt67", 28),
        ["reasoning67 machine67", "learning67 model67 token67", "prompt67"],
    ),
    (
        ("machine67 learning67 model67 token67 prompt67 session67", 6),
        ["machine67", "learning67", "model67", "token67", "prompt67", "session67"],
    ),
    (
        ("machine67 learning67 model67 token67 prompt67 session67", 10),
        ["machine67", "learning67", "model67", "token67", "prompt67", "session67"],
    ),
    (
        ("machine67 learning67 model67 token67 prompt67 session67", 18),
        ["machine67", "learning67 model67", "token67 prompt67", "session67"],
    ),
    (
        ("machine67 learning67 model67 token67 prompt67 session67", 28),
        ["machine67 learning67 model67", "token67 prompt67 session67"],
    ),
    (
        ("learning67 model67 token67 prompt67 session67 library67", 6),
        ["learning67", "model67", "token67", "prompt67", "session67", "library67"],
    ),
    (
        ("learning67 model67 token67 prompt67 session67 library67", 10),
        ["learning67", "model67", "token67", "prompt67", "session67", "library67"],
    ),
    (
        ("learning67 model67 token67 prompt67 session67 library67", 18),
        ["learning67 model67", "token67 prompt67", "session67", "library67"],
    ),
    (
        ("learning67 model67 token67 prompt67 session67 library67", 28),
        ["learning67 model67 token67", "prompt67 session67 library67"],
    ),
    (
        ("model67 token67 prompt67 session67 library67 service67", 6),
        ["model67", "token67", "prompt67", "session67", "library67", "service67"],
    ),
    (
        ("model67 token67 prompt67 session67 library67 service67", 10),
        ["model67", "token67", "prompt67", "session67", "library67", "service67"],
    ),
    (
        ("model67 token67 prompt67 session67 library67 service67", 18),
        ["model67 token67", "prompt67 session67", "library67", "service67"],
    ),
    (
        ("model67 token67 prompt67 session67 library67 service67", 28),
        ["model67 token67 prompt67", "session67 library67", "service67"],
    ),
    (
        ("token67 prompt67 session67 library67 service67 gateway67", 6),
        ["token67", "prompt67", "session67", "library67", "service67", "gateway67"],
    ),
    (
        ("token67 prompt67 session67 library67 service67 gateway67", 10),
        ["token67", "prompt67", "session67", "library67", "service67", "gateway67"],
    ),
    (
        ("token67 prompt67 session67 library67 service67 gateway67", 18),
        ["token67 prompt67", "session67", "library67", "service67", "gateway67"],
    ),
    (
        ("token67 prompt67 session67 library67 service67 gateway67", 28),
        ["token67 prompt67 session67", "library67 service67", "gateway67"],
    ),
    (
        ("prompt67 session67 library67 service67 gateway67 storage67", 6),
        ["prompt67", "session67", "library67", "service67", "gateway67", "storage67"],
    ),
    (
        ("prompt67 session67 library67 service67 gateway67 storage67", 10),
        ["prompt67", "session67", "library67", "service67", "gateway67", "storage67"],
    ),
    (
        ("prompt67 session67 library67 service67 gateway67 storage67", 18),
        ["prompt67 session67", "library67", "service67", "gateway67", "storage67"],
    ),
    (
        ("prompt67 session67 library67 service67 gateway67 storage67", 28),
        ["prompt67 session67 library67", "service67 gateway67", "storage67"],
    ),
    (
        ("session67 library67 service67 gateway67 storage67 network67", 6),
        ["session67", "library67", "service67", "gateway67", "storage67", "network67"],
    ),
    (
        ("session67 library67 service67 gateway67 storage67 network67", 10),
        ["session67", "library67", "service67", "gateway67", "storage67", "network67"],
    ),
    (
        ("session67 library67 service67 gateway67 storage67 network67", 18),
        ["session67", "library67", "service67", "gateway67", "storage67", "network67"],
    ),
    (
        ("session67 library67 service67 gateway67 storage67 network67", 28),
        ["session67 library67", "service67 gateway67", "storage67 network67"],
    ),
    (
        ("library67 service67 gateway67 storage67 network67 latency67", 6),
        ["library67", "service67", "gateway67", "storage67", "network67", "latency67"],
    ),
    (
        ("library67 service67 gateway67 storage67 network67 latency67", 10),
        ["library67", "service67", "gateway67", "storage67", "network67", "latency67"],
    ),
    (
        ("library67 service67 gateway67 storage67 network67 latency67", 18),
        ["library67", "service67", "gateway67", "storage67", "network67", "latency67"],
    ),
    (
        ("library67 service67 gateway67 storage67 network67 latency67", 28),
        ["library67 service67", "gateway67 storage67", "network67 latency67"],
    ),
    (
        ("service67 gateway67 storage67 network67 latency67 buffer67", 6),
        ["service67", "gateway67", "storage67", "network67", "latency67", "buffer67"],
    ),
    (
        ("service67 gateway67 storage67 network67 latency67 buffer67", 10),
        ["service67", "gateway67", "storage67", "network67", "latency67", "buffer67"],
    ),
    (
        ("service67 gateway67 storage67 network67 latency67 buffer67", 18),
        ["service67", "gateway67", "storage67", "network67", "latency67 buffer67"],
    ),
    (
        ("service67 gateway67 storage67 network67 latency67 buffer67", 28),
        ["service67 gateway67", "storage67 network67", "latency67 buffer67"],
    ),
    (
        ("gateway67 storage67 network67 latency67 buffer67 queue67", 6),
        ["gateway67", "storage67", "network67", "latency67", "buffer67", "queue67"],
    ),
    (
        ("gateway67 storage67 network67 latency67 buffer67 queue67", 10),
        ["gateway67", "storage67", "network67", "latency67", "buffer67", "queue67"],
    ),
    (
        ("gateway67 storage67 network67 latency67 buffer67 queue67", 18),
        ["gateway67", "storage67", "network67", "latency67 buffer67", "queue67"],
    ),
    (
        ("gateway67 storage67 network67 latency67 buffer67 queue67", 28),
        ["gateway67 storage67", "network67 latency67 buffer67", "queue67"],
    ),
    (
        ("storage67 network67 latency67 buffer67 queue67 worker67", 6),
        ["storage67", "network67", "latency67", "buffer67", "queue67", "worker67"],
    ),
    (
        ("storage67 network67 latency67 buffer67 queue67 worker67", 10),
        ["storage67", "network67", "latency67", "buffer67", "queue67", "worker67"],
    ),
    (
        ("storage67 network67 latency67 buffer67 queue67 worker67", 18),
        ["storage67", "network67", "latency67 buffer67", "queue67 worker67"],
    ),
    (
        ("storage67 network67 latency67 buffer67 queue67 worker67", 28),
        ["storage67 network67", "latency67 buffer67 queue67", "worker67"],
    ),
    (
        ("network67 latency67 buffer67 queue67 worker67 kernel67", 6),
        ["network67", "latency67", "buffer67", "queue67", "worker67", "kernel67"],
    ),
    (
        ("network67 latency67 buffer67 queue67 worker67 kernel67", 10),
        ["network67", "latency67", "buffer67", "queue67", "worker67", "kernel67"],
    ),
    (
        ("network67 latency67 buffer67 queue67 worker67 kernel67", 18),
        ["network67", "latency67 buffer67", "queue67 worker67", "kernel67"],
    ),
    (
        ("network67 latency67 buffer67 queue67 worker67 kernel67", 28),
        ["network67 latency67 buffer67", "queue67 worker67 kernel67"],
    ),
    (
        ("latency67 buffer67 queue67 worker67 kernel67 signal67", 6),
        ["latency67", "buffer67", "queue67", "worker67", "kernel67", "signal67"],
    ),
    (
        ("latency67 buffer67 queue67 worker67 kernel67 signal67", 10),
        ["latency67", "buffer67", "queue67", "worker67", "kernel67", "signal67"],
    ),
    (
        ("latency67 buffer67 queue67 worker67 kernel67 signal67", 18),
        ["latency67 buffer67", "queue67 worker67", "kernel67 signal67"],
    ),
    (
        ("latency67 buffer67 queue67 worker67 kernel67 signal67", 28),
        ["latency67 buffer67 queue67", "worker67 kernel67 signal67"],
    ),
    (
        ("buffer67 queue67 worker67 kernel67 signal67 packet67", 6),
        ["buffer67", "queue67", "worker67", "kernel67", "signal67", "packet67"],
    ),
    (
        ("buffer67 queue67 worker67 kernel67 signal67 packet67", 10),
        ["buffer67", "queue67", "worker67", "kernel67", "signal67", "packet67"],
    ),
    (
        ("buffer67 queue67 worker67 kernel67 signal67 packet67", 18),
        ["buffer67 queue67", "worker67 kernel67", "signal67 packet67"],
    ),
    (
        ("buffer67 queue67 worker67 kernel67 signal67 packet67", 28),
        ["buffer67 queue67 worker67", "kernel67 signal67 packet67"],
    ),
    (
        ("queue67 worker67 kernel67 signal67 packet67 router67", 6),
        ["queue67", "worker67", "kernel67", "signal67", "packet67", "router67"],
    ),
    (
        ("queue67 worker67 kernel67 signal67 packet67 router67", 10),
        ["queue67", "worker67", "kernel67", "signal67", "packet67", "router67"],
    ),
    (
        ("queue67 worker67 kernel67 signal67 packet67 router67", 18),
        ["queue67 worker67", "kernel67 signal67", "packet67 router67"],
    ),
    (
        ("queue67 worker67 kernel67 signal67 packet67 router67", 28),
        ["queue67 worker67 kernel67", "signal67 packet67 router67"],
    ),
    (
        ("worker67 kernel67 signal67 packet67 router67 cluster67", 6),
        ["worker67", "kernel67", "signal67", "packet67", "router67", "cluster67"],
    ),
    (
        ("worker67 kernel67 signal67 packet67 router67 cluster67", 10),
        ["worker67", "kernel67", "signal67", "packet67", "router67", "cluster67"],
    ),
    (
        ("worker67 kernel67 signal67 packet67 router67 cluster67", 18),
        ["worker67 kernel67", "signal67 packet67", "router67 cluster67"],
    ),
    (
        ("worker67 kernel67 signal67 packet67 router67 cluster67", 28),
        ["worker67 kernel67 signal67", "packet67 router67 cluster67"],
    ),
    (
        ("kernel67 signal67 packet67 router67 cluster67 mirror67", 6),
        ["kernel67", "signal67", "packet67", "router67", "cluster67", "mirror67"],
    ),
    (
        ("kernel67 signal67 packet67 router67 cluster67 mirror67", 10),
        ["kernel67", "signal67", "packet67", "router67", "cluster67", "mirror67"],
    ),
    (
        ("kernel67 signal67 packet67 router67 cluster67 mirror67", 18),
        ["kernel67 signal67", "packet67 router67", "cluster67 mirror67"],
    ),
    (
        ("kernel67 signal67 packet67 router67 cluster67 mirror67", 28),
        ["kernel67 signal67 packet67", "router67 cluster67 mirror67"],
    ),
    (
        ("signal67 packet67 router67 cluster67 mirror67 filter67", 6),
        ["signal67", "packet67", "router67", "cluster67", "mirror67", "filter67"],
    ),
    (
        ("signal67 packet67 router67 cluster67 mirror67 filter67", 10),
        ["signal67", "packet67", "router67", "cluster67", "mirror67", "filter67"],
    ),
    (
        ("signal67 packet67 router67 cluster67 mirror67 filter67", 18),
        ["signal67 packet67", "router67 cluster67", "mirror67 filter67"],
    ),
    (
        ("signal67 packet67 router67 cluster67 mirror67 filter67", 28),
        ["signal67 packet67 router67", "cluster67 mirror67 filter67"],
    ),
    (
        ("packet67 router67 cluster67 mirror67 filter67 ranking67", 6),
        ["packet67", "router67", "cluster67", "mirror67", "filter67", "ranking67"],
    ),
    (
        ("packet67 router67 cluster67 mirror67 filter67 ranking67", 10),
        ["packet67", "router67", "cluster67", "mirror67", "filter67", "ranking67"],
    ),
    (
        ("packet67 router67 cluster67 mirror67 filter67 ranking67", 18),
        ["packet67 router67", "cluster67 mirror67", "filter67 ranking67"],
    ),
    (
        ("packet67 router67 cluster67 mirror67 filter67 ranking67", 28),
        ["packet67 router67 cluster67", "mirror67 filter67 ranking67"],
    ),
    (
        ("router67 cluster67 mirror67 filter67 ranking67 encoding67", 6),
        ["router67", "cluster67", "mirror67", "filter67", "ranking67", "encoding67"],
    ),
    (
        ("router67 cluster67 mirror67 filter67 ranking67 encoding67", 10),
        ["router67", "cluster67", "mirror67", "filter67", "ranking67", "encoding67"],
    ),
    (
        ("router67 cluster67 mirror67 filter67 ranking67 encoding67", 18),
        ["router67 cluster67", "mirror67 filter67", "ranking67", "encoding67"],
    ),
    (
        ("router67 cluster67 mirror67 filter67 ranking67 encoding67", 28),
        ["router67 cluster67 mirror67", "filter67 ranking67", "encoding67"],
    ),
    (
        ("cluster67 mirror67 filter67 ranking67 encoding67 mapping67", 6),
        ["cluster67", "mirror67", "filter67", "ranking67", "encoding67", "mapping67"],
    ),
    (
        ("cluster67 mirror67 filter67 ranking67 encoding67 mapping67", 10),
        ["cluster67", "mirror67", "filter67", "ranking67", "encoding67", "mapping67"],
    ),
    (
        ("cluster67 mirror67 filter67 ranking67 encoding67 mapping67", 18),
        ["cluster67 mirror67", "filter67 ranking67", "encoding67", "mapping67"],
    ),
    (
        ("cluster67 mirror67 filter67 ranking67 encoding67 mapping67", 28),
        ["cluster67 mirror67 filter67", "ranking67 encoding67", "mapping67"],
    ),
    (
        ("mirror67 filter67 ranking67 encoding67 mapping67 record67", 6),
        ["mirror67", "filter67", "ranking67", "encoding67", "mapping67", "record67"],
    ),
    (
        ("mirror67 filter67 ranking67 encoding67 mapping67 record67", 10),
        ["mirror67", "filter67", "ranking67", "encoding67", "mapping67", "record67"],
    ),
    (
        ("mirror67 filter67 ranking67 encoding67 mapping67 record67", 18),
        ["mirror67 filter67", "ranking67", "encoding67", "mapping67 record67"],
    ),
    (
        ("mirror67 filter67 ranking67 encoding67 mapping67 record67", 28),
        ["mirror67 filter67 ranking67", "encoding67 mapping67", "record67"],
    ),
    (
        ("filter67 ranking67 encoding67 mapping67 record67 candle67", 6),
        ["filter67", "ranking67", "encoding67", "mapping67", "record67", "candle67"],
    ),
    (
        ("filter67 ranking67 encoding67 mapping67 record67 candle67", 10),
        ["filter67", "ranking67", "encoding67", "mapping67", "record67", "candle67"],
    ),
    (
        ("filter67 ranking67 encoding67 mapping67 record67 candle67", 18),
        ["filter67 ranking67", "encoding67", "mapping67 record67", "candle67"],
    ),
    (
        ("filter67 ranking67 encoding67 mapping67 record67 candle67", 28),
        ["filter67 ranking67", "encoding67 mapping67", "record67 candle67"],
    ),
    (
        ("ranking67 encoding67 mapping67 record67 candle67 thread67", 6),
        ["ranking67", "encoding67", "mapping67", "record67", "candle67", "thread67"],
    ),
    (
        ("ranking67 encoding67 mapping67 record67 candle67 thread67", 10),
        ["ranking67", "encoding67", "mapping67", "record67", "candle67", "thread67"],
    ),
    (
        ("ranking67 encoding67 mapping67 record67 candle67 thread67", 18),
        ["ranking67", "encoding67", "mapping67 record67", "candle67 thread67"],
    ),
    (
        ("ranking67 encoding67 mapping67 record67 candle67 thread67", 28),
        ["ranking67 encoding67", "mapping67 record67 candle67", "thread67"],
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
