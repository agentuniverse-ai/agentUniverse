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
        ("round 103: the quick brown fox jumps over the lazy dog", 4),
        ["round", "103:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", 8),
        ["round", "103: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", 12),
        ["round 103:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", 16),
        ["round 103: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", 24),
        ["round 103: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 103: the quick brown fox jumps over the lazy dog", 32),
        ["round 103: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", 4),
        ["round", "103:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", 8),
        ["round", "103:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", 12),
        ["round 103:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", 16),
        ["round 103:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", 24),
        ["round 103: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 103: agentuniverse is a framework for multi agents", 32),
        ["round 103: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", 4),
        ["round", "103:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", 8),
        ["round", "103:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", 12),
        ["round 103:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", 16),
        ["round 103:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", 24),
        ["round 103: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 103: knowledge stored as vectors enables retrieval", 32),
        ["round 103: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 103: the processor reads the record then stops", 4),
        ["round", "103:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 103: the processor reads the record then stops", 8),
        ["round", "103: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 103: the processor reads the record then stops", 12),
        ["round 103:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 103: the processor reads the record then stops", 16),
        ["round 103: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 103: the processor reads the record then stops", 24),
        ["round 103: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 103: the processor reads the record then stops", 32),
        ["round 103: the processor reads", "the record then stops"],
    ),
    (
        ("round 103: a worker pulls the next task from the queue", 4),
        ["round", "103:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 103: a worker pulls the next task from the queue", 8),
        ["round", "103: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 103: a worker pulls the next task from the queue", 12),
        ["round 103: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 103: a worker pulls the next task from the queue", 16),
        ["round 103: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 103: a worker pulls the next task from the queue", 24),
        ["round 103: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 103: a worker pulls the next task from the queue", 32),
        ["round 103: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 103: signals travel through the network layer", 4),
        ["round", "103:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 103: signals travel through the network layer", 8),
        ["round", "103:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 103: signals travel through the network layer", 12),
        ["round 103:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 103: signals travel through the network layer", 16),
        ["round 103:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 103: signals travel through the network layer", 24),
        ["round 103: signals", "travel through the", "network layer"],
    ),
    (
        ("round 103: signals travel through the network layer", 32),
        ["round 103: signals travel", "through the network layer"],
    ),
    (
        ("round 103: the gateway routes each request by policy", 4),
        ["round", "103:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 103: the gateway routes each request by policy", 8),
        ["round", "103: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 103: the gateway routes each request by policy", 12),
        ["round 103:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 103: the gateway routes each request by policy", 16),
        ["round 103: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 103: the gateway routes each request by policy", 24),
        ["round 103: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 103: the gateway routes each request by policy", 32),
        ["round 103: the gateway routes", "each request by policy"],
    ),
    (
        ("round 103: memory grows until the buffer is full", 4),
        ["round", "103:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 103: memory grows until the buffer is full", 8),
        ["round", "103:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 103: memory grows until the buffer is full", 12),
        ["round 103:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 103: memory grows until the buffer is full", 16),
        ["round 103:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 103: memory grows until the buffer is full", 24), ["round 103: memory grows", "until the buffer is full"]),
    (("round 103: memory grows until the buffer is full", 32), ["round 103: memory grows until", "the buffer is full"]),
    (
        ("round 103: the cluster mirrors every packet twice", 4),
        ["round", "103:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 103: the cluster mirrors every packet twice", 8),
        ["round", "103: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 103: the cluster mirrors every packet twice", 12),
        ["round 103:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 103: the cluster mirrors every packet twice", 16),
        ["round 103: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 103: the cluster mirrors every packet twice", 24),
        ["round 103: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 103: the cluster mirrors every packet twice", 32),
        ["round 103: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", 4),
        ["round", "103:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", 8),
        ["round", "103:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", 12),
        ["round 103:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", 16),
        ["round 103:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", 24),
        ["round 103: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 103: ranking uses tokens learned from the corpus", 32),
        ["round 103: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 103: a long session ends when the candle dies", 4),
        ["round", "103:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 103: a long session ends when the candle dies", 8),
        ["round", "103: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 103: a long session ends when the candle dies", 12),
        ["round 103: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 103: a long session ends when the candle dies", 16),
        ["round 103: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 103: a long session ends when the candle dies", 24),
        ["round 103: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 103: a long session ends when the candle dies", 32),
        ["round 103: a long session ends", "when the candle dies"],
    ),
    (
        ("round 103: encode the prompt then map the result", 4),
        ["round", "103:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 103: encode the prompt then map the result", 8),
        ["round", "103:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 103: encode the prompt then map the result", 12),
        ["round 103:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 103: encode the prompt then map the result", 16),
        ["round 103:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 103: encode the prompt then map the result", 24),
        ["round 103: encode the", "prompt then map the", "result"],
    ),
    (("round 103: encode the prompt then map the result", 32), ["round 103: encode the prompt", "then map the result"]),
    (
        ("round 103: the kernel wakes the worker at dawn", 4),
        ["round", "103:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 103: the kernel wakes the worker at dawn", 8),
        ["round", "103: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 103: the kernel wakes the worker at dawn", 12),
        ["round 103:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 103: the kernel wakes the worker at dawn", 16), ["round 103: the", "kernel wakes the", "worker at dawn"]),
    (("round 103: the kernel wakes the worker at dawn", 24), ["round 103: the kernel", "wakes the worker at dawn"]),
    (("round 103: the kernel wakes the worker at dawn", 32), ["round 103: the kernel wakes the", "worker at dawn"]),
    (
        ("round 103: service latency drops after the patch", 4),
        ["round", "103:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 103: service latency drops after the patch", 8),
        ["round", "103:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 103: service latency drops after the patch", 12),
        ["round 103:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 103: service latency drops after the patch", 16),
        ["round 103:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 103: service latency drops after the patch", 24),
        ["round 103: service", "latency drops after the", "patch"],
    ),
    (("round 103: service latency drops after the patch", 32), ["round 103: service latency drops", "after the patch"]),
    (
        ("round 103: the library caches every vector it sees", 4),
        ["round", "103:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 103: the library caches every vector it sees", 8),
        ["round", "103: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 103: the library caches every vector it sees", 12),
        ["round 103:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 103: the library caches every vector it sees", 16),
        ["round 103: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 103: the library caches every vector it sees", 24),
        ["round 103: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 103: the library caches every vector it sees", 32),
        ["round 103: the library caches", "every vector it sees"],
    ),
    (
        ("round 103: agents argue then the debate resolves", 4),
        ["round", "103:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 103: agents argue then the debate resolves", 8),
        ["round", "103:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 103: agents argue then the debate resolves", 12),
        ["round 103:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 103: agents argue then the debate resolves", 16),
        ["round 103:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 103: agents argue then the debate resolves", 24), ["round 103: agents argue", "then the debate resolves"]),
    (("round 103: agents argue then the debate resolves", 32), ["round 103: agents argue then the", "debate resolves"]),
    (
        ("round 103: the filter keeps only strong matches", 4),
        ["round", "103:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 103: the filter keeps only strong matches", 8),
        ["round", "103: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 103: the filter keeps only strong matches", 12),
        ["round 103:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 103: the filter keeps only strong matches", 16),
        ["round 103: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 103: the filter keeps only strong matches", 24),
        ["round 103: the filter", "keeps only strong", "matches"],
    ),
    (("round 103: the filter keeps only strong matches", 32), ["round 103: the filter keeps only", "strong matches"]),
    (
        ("round 103: the model answers with a short reply", 4),
        ["round", "103:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 103: the model answers with a short reply", 8),
        ["round", "103: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 103: the model answers with a short reply", 12),
        ["round 103:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 103: the model answers with a short reply", 16),
        ["round 103: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 103: the model answers with a short reply", 24),
        ["round 103: the model", "answers with a short", "reply"],
    ),
    (("round 103: the model answers with a short reply", 32), ["round 103: the model answers", "with a short reply"]),
    (
        ("round 103: the recorder stores the reasoning trace", 4),
        ["round", "103:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 103: the recorder stores the reasoning trace", 8),
        ["round", "103: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 103: the recorder stores the reasoning trace", 12),
        ["round 103:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 103: the recorder stores the reasoning trace", 16),
        ["round 103: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 103: the recorder stores the reasoning trace", 24),
        ["round 103: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 103: the recorder stores the reasoning trace", 32),
        ["round 103: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 103: the angel watches the processor run", 4),
        ["round", "103:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 103: the angel watches the processor run", 8),
        ["round", "103: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 103: the angel watches the processor run", 12),
        ["round 103:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 103: the angel watches the processor run", 16),
        ["round 103: the", "angel watches", "the processor", "run"],
    ),
    (("round 103: the angel watches the processor run", 24), ["round 103: the angel", "watches the processor", "run"]),
    (("round 103: the angel watches the processor run", 32), ["round 103: the angel watches the", "processor run"]),
    (
        ("round 103: angle of the vector decides the match", 4),
        ["round", "103:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 103: angle of the vector decides the match", 8),
        ["round", "103:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 103: angle of the vector decides the match", 12),
        ["round 103:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 103: angle of the vector decides the match", 16),
        ["round 103: angle", "of the vector", "decides the", "match"],
    ),
    (("round 103: angle of the vector decides the match", 24), ["round 103: angle of the", "vector decides the match"]),
    (("round 103: angle of the vector decides the match", 32), ["round 103: angle of the vector", "decides the match"]),
    (
        ("round 103: the candle burns twice as long at night", 4),
        ["round", "103:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 103: the candle burns twice as long at night", 8),
        ["round", "103: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 103: the candle burns twice as long at night", 12),
        ["round 103:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 103: the candle burns twice as long at night", 16),
        ["round 103: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 103: the candle burns twice as long at night", 24),
        ["round 103: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 103: the candle burns twice as long at night", 32),
        ["round 103: the candle burns", "twice as long at night"],
    ),
    (
        ("round 103: a mirror of the universe in one line", 4),
        ["round", "103:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 103: a mirror of the universe in one line", 8),
        ["round", "103: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 103: a mirror of the universe in one line", 12),
        ["round 103: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 103: a mirror of the universe in one line", 16),
        ["round 103: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 103: a mirror of the universe in one line", 24), ["round 103: a mirror of", "the universe in one line"]),
    (("round 103: a mirror of the universe in one line", 32), ["round 103: a mirror of the", "universe in one line"]),
    (
        ("round 103: the queue drains before the storm", 4),
        ["round", "103:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 103: the queue drains before the storm", 8),
        ["round", "103: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 103: the queue drains before the storm", 12),
        ["round 103:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 103: the queue drains before the storm", 16), ["round 103: the", "queue drains", "before the storm"]),
    (("round 103: the queue drains before the storm", 24), ["round 103: the queue", "drains before the storm"]),
    (("round 103: the queue drains before the storm", 32), ["round 103: the queue drains", "before the storm"]),
    (
        ("kitten103 sitting103 agent103 angle103 universe103 memory103", 6),
        ["kitten103", "sitting103", "agent103", "angle103", "universe103", "memory103"],
    ),
    (
        ("kitten103 sitting103 agent103 angle103 universe103 memory103", 10),
        ["kitten103", "sitting103", "agent103", "angle103", "universe103", "memory103"],
    ),
    (
        ("kitten103 sitting103 agent103 angle103 universe103 memory103", 18),
        ["kitten103", "sitting103", "agent103 angle103", "universe103", "memory103"],
    ),
    (
        ("kitten103 sitting103 agent103 angle103 universe103 memory103", 28),
        ["kitten103 sitting103", "agent103 angle103", "universe103 memory103"],
    ),
    (
        ("sitting103 agent103 angle103 universe103 memory103 stream103", 6),
        ["sitting103", "agent103", "angle103", "universe103", "memory103", "stream103"],
    ),
    (
        ("sitting103 agent103 angle103 universe103 memory103 stream103", 10),
        ["sitting103", "agent103", "angle103", "universe103", "memory103", "stream103"],
    ),
    (
        ("sitting103 agent103 angle103 universe103 memory103 stream103", 18),
        ["sitting103", "agent103 angle103", "universe103", "memory103", "stream103"],
    ),
    (
        ("sitting103 agent103 angle103 universe103 memory103 stream103", 28),
        ["sitting103 agent103 angle103", "universe103 memory103", "stream103"],
    ),
    (
        ("agent103 angle103 universe103 memory103 stream103 context103", 6),
        ["agent103", "angle103", "universe103", "memory103", "stream103", "context103"],
    ),
    (
        ("agent103 angle103 universe103 memory103 stream103 context103", 10),
        ["agent103", "angle103", "universe103", "memory103", "stream103", "context103"],
    ),
    (
        ("agent103 angle103 universe103 memory103 stream103 context103", 18),
        ["agent103 angle103", "universe103", "memory103", "stream103", "context103"],
    ),
    (
        ("agent103 angle103 universe103 memory103 stream103 context103", 28),
        ["agent103 angle103", "universe103 memory103", "stream103 context103"],
    ),
    (
        ("angle103 universe103 memory103 stream103 context103 knowledge103", 6),
        ["angle103", "universe103", "memory103", "stream103", "context103", "knowledge103"],
    ),
    (
        ("angle103 universe103 memory103 stream103 context103 knowledge103", 10),
        ["angle103", "universe103", "memory103", "stream103", "context103", "knowledge103"],
    ),
    (
        ("angle103 universe103 memory103 stream103 context103 knowledge103", 18),
        ["angle103", "universe103", "memory103", "stream103", "context103", "knowledge103"],
    ),
    (
        ("angle103 universe103 memory103 stream103 context103 knowledge103", 28),
        ["angle103 universe103", "memory103 stream103", "context103 knowledge103"],
    ),
    (
        ("universe103 memory103 stream103 context103 knowledge103 vector103", 6),
        ["universe103", "memory103", "stream103", "context103", "knowledge103", "vector103"],
    ),
    (
        ("universe103 memory103 stream103 context103 knowledge103 vector103", 10),
        ["universe103", "memory103", "stream103", "context103", "knowledge103", "vector103"],
    ),
    (
        ("universe103 memory103 stream103 context103 knowledge103 vector103", 18),
        ["universe103", "memory103", "stream103", "context103", "knowledge103", "vector103"],
    ),
    (
        ("universe103 memory103 stream103 context103 knowledge103 vector103", 28),
        ["universe103 memory103", "stream103 context103", "knowledge103 vector103"],
    ),
    (
        ("memory103 stream103 context103 knowledge103 vector103 processor103", 6),
        ["memory103", "stream103", "context103", "knowledge103", "vector103", "processor103"],
    ),
    (
        ("memory103 stream103 context103 knowledge103 vector103 processor103", 10),
        ["memory103", "stream103", "context103", "knowledge103", "vector103", "processor103"],
    ),
    (
        ("memory103 stream103 context103 knowledge103 vector103 processor103", 18),
        ["memory103", "stream103", "context103", "knowledge103", "vector103", "processor103"],
    ),
    (
        ("memory103 stream103 context103 knowledge103 vector103 processor103", 28),
        ["memory103 stream103", "context103 knowledge103", "vector103 processor103"],
    ),
    (
        ("stream103 context103 knowledge103 vector103 processor103 reasoning103", 6),
        ["stream103", "context103", "knowledge103", "vector103", "processor103", "reasoning103"],
    ),
    (
        ("stream103 context103 knowledge103 vector103 processor103 reasoning103", 10),
        ["stream103", "context103", "knowledge103", "vector103", "processor103", "reasoning103"],
    ),
    (
        ("stream103 context103 knowledge103 vector103 processor103 reasoning103", 18),
        ["stream103", "context103", "knowledge103", "vector103", "processor103", "reasoning103"],
    ),
    (
        ("stream103 context103 knowledge103 vector103 processor103 reasoning103", 28),
        ["stream103 context103", "knowledge103 vector103", "processor103 reasoning103"],
    ),
    (
        ("context103 knowledge103 vector103 processor103 reasoning103 machine103", 6),
        ["context103", "knowledge103", "vector103", "processor103", "reasoning103", "machine103"],
    ),
    (
        ("context103 knowledge103 vector103 processor103 reasoning103 machine103", 10),
        ["context103", "knowledge103", "vector103", "processor103", "reasoning103", "machine103"],
    ),
    (
        ("context103 knowledge103 vector103 processor103 reasoning103 machine103", 18),
        ["context103", "knowledge103", "vector103", "processor103", "reasoning103", "machine103"],
    ),
    (
        ("context103 knowledge103 vector103 processor103 reasoning103 machine103", 28),
        ["context103 knowledge103", "vector103 processor103", "reasoning103 machine103"],
    ),
    (
        ("knowledge103 vector103 processor103 reasoning103 machine103 learning103", 6),
        ["knowledge103", "vector103", "processor103", "reasoning103", "machine103", "learning103"],
    ),
    (
        ("knowledge103 vector103 processor103 reasoning103 machine103 learning103", 10),
        ["knowledge103", "vector103", "processor103", "reasoning103", "machine103", "learning103"],
    ),
    (
        ("knowledge103 vector103 processor103 reasoning103 machine103 learning103", 18),
        ["knowledge103", "vector103", "processor103", "reasoning103", "machine103", "learning103"],
    ),
    (
        ("knowledge103 vector103 processor103 reasoning103 machine103 learning103", 28),
        ["knowledge103 vector103", "processor103 reasoning103", "machine103 learning103"],
    ),
    (
        ("vector103 processor103 reasoning103 machine103 learning103 model103", 6),
        ["vector103", "processor103", "reasoning103", "machine103", "learning103", "model103"],
    ),
    (
        ("vector103 processor103 reasoning103 machine103 learning103 model103", 10),
        ["vector103", "processor103", "reasoning103", "machine103", "learning103", "model103"],
    ),
    (
        ("vector103 processor103 reasoning103 machine103 learning103 model103", 18),
        ["vector103", "processor103", "reasoning103", "machine103", "learning103", "model103"],
    ),
    (
        ("vector103 processor103 reasoning103 machine103 learning103 model103", 28),
        ["vector103 processor103", "reasoning103 machine103", "learning103 model103"],
    ),
    (
        ("processor103 reasoning103 machine103 learning103 model103 token103", 6),
        ["processor103", "reasoning103", "machine103", "learning103", "model103", "token103"],
    ),
    (
        ("processor103 reasoning103 machine103 learning103 model103 token103", 10),
        ["processor103", "reasoning103", "machine103", "learning103", "model103", "token103"],
    ),
    (
        ("processor103 reasoning103 machine103 learning103 model103 token103", 18),
        ["processor103", "reasoning103", "machine103", "learning103", "model103 token103"],
    ),
    (
        ("processor103 reasoning103 machine103 learning103 model103 token103", 28),
        ["processor103 reasoning103", "machine103 learning103", "model103 token103"],
    ),
    (
        ("reasoning103 machine103 learning103 model103 token103 prompt103", 6),
        ["reasoning103", "machine103", "learning103", "model103", "token103", "prompt103"],
    ),
    (
        ("reasoning103 machine103 learning103 model103 token103 prompt103", 10),
        ["reasoning103", "machine103", "learning103", "model103", "token103", "prompt103"],
    ),
    (
        ("reasoning103 machine103 learning103 model103 token103 prompt103", 18),
        ["reasoning103", "machine103", "learning103", "model103 token103", "prompt103"],
    ),
    (
        ("reasoning103 machine103 learning103 model103 token103 prompt103", 28),
        ["reasoning103 machine103", "learning103 model103", "token103 prompt103"],
    ),
    (
        ("machine103 learning103 model103 token103 prompt103 session103", 6),
        ["machine103", "learning103", "model103", "token103", "prompt103", "session103"],
    ),
    (
        ("machine103 learning103 model103 token103 prompt103 session103", 10),
        ["machine103", "learning103", "model103", "token103", "prompt103", "session103"],
    ),
    (
        ("machine103 learning103 model103 token103 prompt103 session103", 18),
        ["machine103", "learning103", "model103 token103", "prompt103", "session103"],
    ),
    (
        ("machine103 learning103 model103 token103 prompt103 session103", 28),
        ["machine103 learning103", "model103 token103 prompt103", "session103"],
    ),
    (
        ("learning103 model103 token103 prompt103 session103 library103", 6),
        ["learning103", "model103", "token103", "prompt103", "session103", "library103"],
    ),
    (
        ("learning103 model103 token103 prompt103 session103 library103", 10),
        ["learning103", "model103", "token103", "prompt103", "session103", "library103"],
    ),
    (
        ("learning103 model103 token103 prompt103 session103 library103", 18),
        ["learning103", "model103 token103", "prompt103", "session103", "library103"],
    ),
    (
        ("learning103 model103 token103 prompt103 session103 library103", 28),
        ["learning103 model103", "token103 prompt103", "session103 library103"],
    ),
    (
        ("model103 token103 prompt103 session103 library103 service103", 6),
        ["model103", "token103", "prompt103", "session103", "library103", "service103"],
    ),
    (
        ("model103 token103 prompt103 session103 library103 service103", 10),
        ["model103", "token103", "prompt103", "session103", "library103", "service103"],
    ),
    (
        ("model103 token103 prompt103 session103 library103 service103", 18),
        ["model103 token103", "prompt103", "session103", "library103", "service103"],
    ),
    (
        ("model103 token103 prompt103 session103 library103 service103", 28),
        ["model103 token103 prompt103", "session103 library103", "service103"],
    ),
    (
        ("token103 prompt103 session103 library103 service103 gateway103", 6),
        ["token103", "prompt103", "session103", "library103", "service103", "gateway103"],
    ),
    (
        ("token103 prompt103 session103 library103 service103 gateway103", 10),
        ["token103", "prompt103", "session103", "library103", "service103", "gateway103"],
    ),
    (
        ("token103 prompt103 session103 library103 service103 gateway103", 18),
        ["token103 prompt103", "session103", "library103", "service103", "gateway103"],
    ),
    (
        ("token103 prompt103 session103 library103 service103 gateway103", 28),
        ["token103 prompt103", "session103 library103", "service103 gateway103"],
    ),
    (
        ("prompt103 session103 library103 service103 gateway103 storage103", 6),
        ["prompt103", "session103", "library103", "service103", "gateway103", "storage103"],
    ),
    (
        ("prompt103 session103 library103 service103 gateway103 storage103", 10),
        ["prompt103", "session103", "library103", "service103", "gateway103", "storage103"],
    ),
    (
        ("prompt103 session103 library103 service103 gateway103 storage103", 18),
        ["prompt103", "session103", "library103", "service103", "gateway103", "storage103"],
    ),
    (
        ("prompt103 session103 library103 service103 gateway103 storage103", 28),
        ["prompt103 session103", "library103 service103", "gateway103 storage103"],
    ),
    (
        ("session103 library103 service103 gateway103 storage103 network103", 6),
        ["session103", "library103", "service103", "gateway103", "storage103", "network103"],
    ),
    (
        ("session103 library103 service103 gateway103 storage103 network103", 10),
        ["session103", "library103", "service103", "gateway103", "storage103", "network103"],
    ),
    (
        ("session103 library103 service103 gateway103 storage103 network103", 18),
        ["session103", "library103", "service103", "gateway103", "storage103", "network103"],
    ),
    (
        ("session103 library103 service103 gateway103 storage103 network103", 28),
        ["session103 library103", "service103 gateway103", "storage103 network103"],
    ),
    (
        ("library103 service103 gateway103 storage103 network103 latency103", 6),
        ["library103", "service103", "gateway103", "storage103", "network103", "latency103"],
    ),
    (
        ("library103 service103 gateway103 storage103 network103 latency103", 10),
        ["library103", "service103", "gateway103", "storage103", "network103", "latency103"],
    ),
    (
        ("library103 service103 gateway103 storage103 network103 latency103", 18),
        ["library103", "service103", "gateway103", "storage103", "network103", "latency103"],
    ),
    (
        ("library103 service103 gateway103 storage103 network103 latency103", 28),
        ["library103 service103", "gateway103 storage103", "network103 latency103"],
    ),
    (
        ("service103 gateway103 storage103 network103 latency103 buffer103", 6),
        ["service103", "gateway103", "storage103", "network103", "latency103", "buffer103"],
    ),
    (
        ("service103 gateway103 storage103 network103 latency103 buffer103", 10),
        ["service103", "gateway103", "storage103", "network103", "latency103", "buffer103"],
    ),
    (
        ("service103 gateway103 storage103 network103 latency103 buffer103", 18),
        ["service103", "gateway103", "storage103", "network103", "latency103", "buffer103"],
    ),
    (
        ("service103 gateway103 storage103 network103 latency103 buffer103", 28),
        ["service103 gateway103", "storage103 network103", "latency103 buffer103"],
    ),
    (
        ("gateway103 storage103 network103 latency103 buffer103 queue103", 6),
        ["gateway103", "storage103", "network103", "latency103", "buffer103", "queue103"],
    ),
    (
        ("gateway103 storage103 network103 latency103 buffer103 queue103", 10),
        ["gateway103", "storage103", "network103", "latency103", "buffer103", "queue103"],
    ),
    (
        ("gateway103 storage103 network103 latency103 buffer103 queue103", 18),
        ["gateway103", "storage103", "network103", "latency103", "buffer103 queue103"],
    ),
    (
        ("gateway103 storage103 network103 latency103 buffer103 queue103", 28),
        ["gateway103 storage103", "network103 latency103", "buffer103 queue103"],
    ),
    (
        ("storage103 network103 latency103 buffer103 queue103 worker103", 6),
        ["storage103", "network103", "latency103", "buffer103", "queue103", "worker103"],
    ),
    (
        ("storage103 network103 latency103 buffer103 queue103 worker103", 10),
        ["storage103", "network103", "latency103", "buffer103", "queue103", "worker103"],
    ),
    (
        ("storage103 network103 latency103 buffer103 queue103 worker103", 18),
        ["storage103", "network103", "latency103", "buffer103 queue103", "worker103"],
    ),
    (
        ("storage103 network103 latency103 buffer103 queue103 worker103", 28),
        ["storage103 network103", "latency103 buffer103", "queue103 worker103"],
    ),
    (
        ("network103 latency103 buffer103 queue103 worker103 kernel103", 6),
        ["network103", "latency103", "buffer103", "queue103", "worker103", "kernel103"],
    ),
    (
        ("network103 latency103 buffer103 queue103 worker103 kernel103", 10),
        ["network103", "latency103", "buffer103", "queue103", "worker103", "kernel103"],
    ),
    (
        ("network103 latency103 buffer103 queue103 worker103 kernel103", 18),
        ["network103", "latency103", "buffer103 queue103", "worker103", "kernel103"],
    ),
    (
        ("network103 latency103 buffer103 queue103 worker103 kernel103", 28),
        ["network103 latency103", "buffer103 queue103 worker103", "kernel103"],
    ),
    (
        ("latency103 buffer103 queue103 worker103 kernel103 signal103", 6),
        ["latency103", "buffer103", "queue103", "worker103", "kernel103", "signal103"],
    ),
    (
        ("latency103 buffer103 queue103 worker103 kernel103 signal103", 10),
        ["latency103", "buffer103", "queue103", "worker103", "kernel103", "signal103"],
    ),
    (
        ("latency103 buffer103 queue103 worker103 kernel103 signal103", 18),
        ["latency103", "buffer103 queue103", "worker103", "kernel103", "signal103"],
    ),
    (
        ("latency103 buffer103 queue103 worker103 kernel103 signal103", 28),
        ["latency103 buffer103", "queue103 worker103 kernel103", "signal103"],
    ),
    (
        ("buffer103 queue103 worker103 kernel103 signal103 packet103", 6),
        ["buffer103", "queue103", "worker103", "kernel103", "signal103", "packet103"],
    ),
    (
        ("buffer103 queue103 worker103 kernel103 signal103 packet103", 10),
        ["buffer103", "queue103", "worker103", "kernel103", "signal103", "packet103"],
    ),
    (
        ("buffer103 queue103 worker103 kernel103 signal103 packet103", 18),
        ["buffer103 queue103", "worker103", "kernel103", "signal103", "packet103"],
    ),
    (
        ("buffer103 queue103 worker103 kernel103 signal103 packet103", 28),
        ["buffer103 queue103 worker103", "kernel103 signal103", "packet103"],
    ),
    (
        ("queue103 worker103 kernel103 signal103 packet103 router103", 6),
        ["queue103", "worker103", "kernel103", "signal103", "packet103", "router103"],
    ),
    (
        ("queue103 worker103 kernel103 signal103 packet103 router103", 10),
        ["queue103", "worker103", "kernel103", "signal103", "packet103", "router103"],
    ),
    (
        ("queue103 worker103 kernel103 signal103 packet103 router103", 18),
        ["queue103 worker103", "kernel103", "signal103", "packet103", "router103"],
    ),
    (
        ("queue103 worker103 kernel103 signal103 packet103 router103", 28),
        ["queue103 worker103 kernel103", "signal103 packet103", "router103"],
    ),
    (
        ("worker103 kernel103 signal103 packet103 router103 cluster103", 6),
        ["worker103", "kernel103", "signal103", "packet103", "router103", "cluster103"],
    ),
    (
        ("worker103 kernel103 signal103 packet103 router103 cluster103", 10),
        ["worker103", "kernel103", "signal103", "packet103", "router103", "cluster103"],
    ),
    (
        ("worker103 kernel103 signal103 packet103 router103 cluster103", 18),
        ["worker103", "kernel103", "signal103", "packet103", "router103", "cluster103"],
    ),
    (
        ("worker103 kernel103 signal103 packet103 router103 cluster103", 28),
        ["worker103 kernel103", "signal103 packet103", "router103 cluster103"],
    ),
    (
        ("kernel103 signal103 packet103 router103 cluster103 mirror103", 6),
        ["kernel103", "signal103", "packet103", "router103", "cluster103", "mirror103"],
    ),
    (
        ("kernel103 signal103 packet103 router103 cluster103 mirror103", 10),
        ["kernel103", "signal103", "packet103", "router103", "cluster103", "mirror103"],
    ),
    (
        ("kernel103 signal103 packet103 router103 cluster103 mirror103", 18),
        ["kernel103", "signal103", "packet103", "router103", "cluster103", "mirror103"],
    ),
    (
        ("kernel103 signal103 packet103 router103 cluster103 mirror103", 28),
        ["kernel103 signal103", "packet103 router103", "cluster103 mirror103"],
    ),
    (
        ("signal103 packet103 router103 cluster103 mirror103 filter103", 6),
        ["signal103", "packet103", "router103", "cluster103", "mirror103", "filter103"],
    ),
    (
        ("signal103 packet103 router103 cluster103 mirror103 filter103", 10),
        ["signal103", "packet103", "router103", "cluster103", "mirror103", "filter103"],
    ),
    (
        ("signal103 packet103 router103 cluster103 mirror103 filter103", 18),
        ["signal103", "packet103", "router103", "cluster103", "mirror103", "filter103"],
    ),
    (
        ("signal103 packet103 router103 cluster103 mirror103 filter103", 28),
        ["signal103 packet103", "router103 cluster103", "mirror103 filter103"],
    ),
    (
        ("packet103 router103 cluster103 mirror103 filter103 ranking103", 6),
        ["packet103", "router103", "cluster103", "mirror103", "filter103", "ranking103"],
    ),
    (
        ("packet103 router103 cluster103 mirror103 filter103 ranking103", 10),
        ["packet103", "router103", "cluster103", "mirror103", "filter103", "ranking103"],
    ),
    (
        ("packet103 router103 cluster103 mirror103 filter103 ranking103", 18),
        ["packet103", "router103", "cluster103", "mirror103", "filter103", "ranking103"],
    ),
    (
        ("packet103 router103 cluster103 mirror103 filter103 ranking103", 28),
        ["packet103 router103", "cluster103 mirror103", "filter103 ranking103"],
    ),
    (
        ("router103 cluster103 mirror103 filter103 ranking103 encoding103", 6),
        ["router103", "cluster103", "mirror103", "filter103", "ranking103", "encoding103"],
    ),
    (
        ("router103 cluster103 mirror103 filter103 ranking103 encoding103", 10),
        ["router103", "cluster103", "mirror103", "filter103", "ranking103", "encoding103"],
    ),
    (
        ("router103 cluster103 mirror103 filter103 ranking103 encoding103", 18),
        ["router103", "cluster103", "mirror103", "filter103", "ranking103", "encoding103"],
    ),
    (
        ("router103 cluster103 mirror103 filter103 ranking103 encoding103", 28),
        ["router103 cluster103", "mirror103 filter103", "ranking103 encoding103"],
    ),
    (
        ("cluster103 mirror103 filter103 ranking103 encoding103 mapping103", 6),
        ["cluster103", "mirror103", "filter103", "ranking103", "encoding103", "mapping103"],
    ),
    (
        ("cluster103 mirror103 filter103 ranking103 encoding103 mapping103", 10),
        ["cluster103", "mirror103", "filter103", "ranking103", "encoding103", "mapping103"],
    ),
    (
        ("cluster103 mirror103 filter103 ranking103 encoding103 mapping103", 18),
        ["cluster103", "mirror103", "filter103", "ranking103", "encoding103", "mapping103"],
    ),
    (
        ("cluster103 mirror103 filter103 ranking103 encoding103 mapping103", 28),
        ["cluster103 mirror103", "filter103 ranking103", "encoding103 mapping103"],
    ),
    (
        ("mirror103 filter103 ranking103 encoding103 mapping103 record103", 6),
        ["mirror103", "filter103", "ranking103", "encoding103", "mapping103", "record103"],
    ),
    (
        ("mirror103 filter103 ranking103 encoding103 mapping103 record103", 10),
        ["mirror103", "filter103", "ranking103", "encoding103", "mapping103", "record103"],
    ),
    (
        ("mirror103 filter103 ranking103 encoding103 mapping103 record103", 18),
        ["mirror103", "filter103", "ranking103", "encoding103", "mapping103", "record103"],
    ),
    (
        ("mirror103 filter103 ranking103 encoding103 mapping103 record103", 28),
        ["mirror103 filter103", "ranking103 encoding103", "mapping103 record103"],
    ),
    (
        ("filter103 ranking103 encoding103 mapping103 record103 candle103", 6),
        ["filter103", "ranking103", "encoding103", "mapping103", "record103", "candle103"],
    ),
    (
        ("filter103 ranking103 encoding103 mapping103 record103 candle103", 10),
        ["filter103", "ranking103", "encoding103", "mapping103", "record103", "candle103"],
    ),
    (
        ("filter103 ranking103 encoding103 mapping103 record103 candle103", 18),
        ["filter103", "ranking103", "encoding103", "mapping103", "record103", "candle103"],
    ),
    (
        ("filter103 ranking103 encoding103 mapping103 record103 candle103", 28),
        ["filter103 ranking103", "encoding103 mapping103", "record103 candle103"],
    ),
    (
        ("ranking103 encoding103 mapping103 record103 candle103 thread103", 6),
        ["ranking103", "encoding103", "mapping103", "record103", "candle103", "thread103"],
    ),
    (
        ("ranking103 encoding103 mapping103 record103 candle103 thread103", 10),
        ["ranking103", "encoding103", "mapping103", "record103", "candle103", "thread103"],
    ),
    (
        ("ranking103 encoding103 mapping103 record103 candle103 thread103", 18),
        ["ranking103", "encoding103", "mapping103", "record103", "candle103", "thread103"],
    ),
    (
        ("ranking103 encoding103 mapping103 record103 candle103 thread103", 28),
        ["ranking103 encoding103", "mapping103 record103", "candle103 thread103"],
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
