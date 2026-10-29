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
        ("round 199: the quick brown fox jumps over the lazy dog", 4),
        ["round", "199:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", 8),
        ["round", "199: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", 12),
        ["round 199:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", 16),
        ["round 199: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", 24),
        ["round 199: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 199: the quick brown fox jumps over the lazy dog", 32),
        ["round 199: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", 4),
        ["round", "199:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", 8),
        ["round", "199:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", 12),
        ["round 199:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", 16),
        ["round 199:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", 24),
        ["round 199: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 199: agentuniverse is a framework for multi agents", 32),
        ["round 199: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", 4),
        ["round", "199:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", 8),
        ["round", "199:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", 12),
        ["round 199:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", 16),
        ["round 199:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", 24),
        ["round 199: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 199: knowledge stored as vectors enables retrieval", 32),
        ["round 199: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 199: the processor reads the record then stops", 4),
        ["round", "199:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 199: the processor reads the record then stops", 8),
        ["round", "199: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 199: the processor reads the record then stops", 12),
        ["round 199:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 199: the processor reads the record then stops", 16),
        ["round 199: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 199: the processor reads the record then stops", 24),
        ["round 199: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 199: the processor reads the record then stops", 32),
        ["round 199: the processor reads", "the record then stops"],
    ),
    (
        ("round 199: a worker pulls the next task from the queue", 4),
        ["round", "199:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 199: a worker pulls the next task from the queue", 8),
        ["round", "199: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 199: a worker pulls the next task from the queue", 12),
        ["round 199: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 199: a worker pulls the next task from the queue", 16),
        ["round 199: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 199: a worker pulls the next task from the queue", 24),
        ["round 199: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 199: a worker pulls the next task from the queue", 32),
        ["round 199: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 199: signals travel through the network layer", 4),
        ["round", "199:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 199: signals travel through the network layer", 8),
        ["round", "199:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 199: signals travel through the network layer", 12),
        ["round 199:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 199: signals travel through the network layer", 16),
        ["round 199:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 199: signals travel through the network layer", 24),
        ["round 199: signals", "travel through the", "network layer"],
    ),
    (
        ("round 199: signals travel through the network layer", 32),
        ["round 199: signals travel", "through the network layer"],
    ),
    (
        ("round 199: the gateway routes each request by policy", 4),
        ["round", "199:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 199: the gateway routes each request by policy", 8),
        ["round", "199: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 199: the gateway routes each request by policy", 12),
        ["round 199:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 199: the gateway routes each request by policy", 16),
        ["round 199: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 199: the gateway routes each request by policy", 24),
        ["round 199: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 199: the gateway routes each request by policy", 32),
        ["round 199: the gateway routes", "each request by policy"],
    ),
    (
        ("round 199: memory grows until the buffer is full", 4),
        ["round", "199:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 199: memory grows until the buffer is full", 8),
        ["round", "199:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 199: memory grows until the buffer is full", 12),
        ["round 199:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 199: memory grows until the buffer is full", 16),
        ["round 199:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 199: memory grows until the buffer is full", 24), ["round 199: memory grows", "until the buffer is full"]),
    (("round 199: memory grows until the buffer is full", 32), ["round 199: memory grows until", "the buffer is full"]),
    (
        ("round 199: the cluster mirrors every packet twice", 4),
        ["round", "199:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 199: the cluster mirrors every packet twice", 8),
        ["round", "199: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 199: the cluster mirrors every packet twice", 12),
        ["round 199:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 199: the cluster mirrors every packet twice", 16),
        ["round 199: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 199: the cluster mirrors every packet twice", 24),
        ["round 199: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 199: the cluster mirrors every packet twice", 32),
        ["round 199: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", 4),
        ["round", "199:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", 8),
        ["round", "199:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", 12),
        ["round 199:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", 16),
        ["round 199:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", 24),
        ["round 199: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 199: ranking uses tokens learned from the corpus", 32),
        ["round 199: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 199: a long session ends when the candle dies", 4),
        ["round", "199:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 199: a long session ends when the candle dies", 8),
        ["round", "199: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 199: a long session ends when the candle dies", 12),
        ["round 199: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 199: a long session ends when the candle dies", 16),
        ["round 199: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 199: a long session ends when the candle dies", 24),
        ["round 199: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 199: a long session ends when the candle dies", 32),
        ["round 199: a long session ends", "when the candle dies"],
    ),
    (
        ("round 199: encode the prompt then map the result", 4),
        ["round", "199:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 199: encode the prompt then map the result", 8),
        ["round", "199:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 199: encode the prompt then map the result", 12),
        ["round 199:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 199: encode the prompt then map the result", 16),
        ["round 199:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 199: encode the prompt then map the result", 24),
        ["round 199: encode the", "prompt then map the", "result"],
    ),
    (("round 199: encode the prompt then map the result", 32), ["round 199: encode the prompt", "then map the result"]),
    (
        ("round 199: the kernel wakes the worker at dawn", 4),
        ["round", "199:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 199: the kernel wakes the worker at dawn", 8),
        ["round", "199: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 199: the kernel wakes the worker at dawn", 12),
        ["round 199:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 199: the kernel wakes the worker at dawn", 16), ["round 199: the", "kernel wakes the", "worker at dawn"]),
    (("round 199: the kernel wakes the worker at dawn", 24), ["round 199: the kernel", "wakes the worker at dawn"]),
    (("round 199: the kernel wakes the worker at dawn", 32), ["round 199: the kernel wakes the", "worker at dawn"]),
    (
        ("round 199: service latency drops after the patch", 4),
        ["round", "199:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 199: service latency drops after the patch", 8),
        ["round", "199:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 199: service latency drops after the patch", 12),
        ["round 199:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 199: service latency drops after the patch", 16),
        ["round 199:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 199: service latency drops after the patch", 24),
        ["round 199: service", "latency drops after the", "patch"],
    ),
    (("round 199: service latency drops after the patch", 32), ["round 199: service latency drops", "after the patch"]),
    (
        ("round 199: the library caches every vector it sees", 4),
        ["round", "199:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 199: the library caches every vector it sees", 8),
        ["round", "199: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 199: the library caches every vector it sees", 12),
        ["round 199:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 199: the library caches every vector it sees", 16),
        ["round 199: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 199: the library caches every vector it sees", 24),
        ["round 199: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 199: the library caches every vector it sees", 32),
        ["round 199: the library caches", "every vector it sees"],
    ),
    (
        ("round 199: agents argue then the debate resolves", 4),
        ["round", "199:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 199: agents argue then the debate resolves", 8),
        ["round", "199:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 199: agents argue then the debate resolves", 12),
        ["round 199:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 199: agents argue then the debate resolves", 16),
        ["round 199:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 199: agents argue then the debate resolves", 24), ["round 199: agents argue", "then the debate resolves"]),
    (("round 199: agents argue then the debate resolves", 32), ["round 199: agents argue then the", "debate resolves"]),
    (
        ("round 199: the filter keeps only strong matches", 4),
        ["round", "199:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 199: the filter keeps only strong matches", 8),
        ["round", "199: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 199: the filter keeps only strong matches", 12),
        ["round 199:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 199: the filter keeps only strong matches", 16),
        ["round 199: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 199: the filter keeps only strong matches", 24),
        ["round 199: the filter", "keeps only strong", "matches"],
    ),
    (("round 199: the filter keeps only strong matches", 32), ["round 199: the filter keeps only", "strong matches"]),
    (
        ("round 199: the model answers with a short reply", 4),
        ["round", "199:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 199: the model answers with a short reply", 8),
        ["round", "199: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 199: the model answers with a short reply", 12),
        ["round 199:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 199: the model answers with a short reply", 16),
        ["round 199: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 199: the model answers with a short reply", 24),
        ["round 199: the model", "answers with a short", "reply"],
    ),
    (("round 199: the model answers with a short reply", 32), ["round 199: the model answers", "with a short reply"]),
    (
        ("round 199: the recorder stores the reasoning trace", 4),
        ["round", "199:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 199: the recorder stores the reasoning trace", 8),
        ["round", "199: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 199: the recorder stores the reasoning trace", 12),
        ["round 199:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 199: the recorder stores the reasoning trace", 16),
        ["round 199: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 199: the recorder stores the reasoning trace", 24),
        ["round 199: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 199: the recorder stores the reasoning trace", 32),
        ["round 199: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 199: the angel watches the processor run", 4),
        ["round", "199:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 199: the angel watches the processor run", 8),
        ["round", "199: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 199: the angel watches the processor run", 12),
        ["round 199:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 199: the angel watches the processor run", 16),
        ["round 199: the", "angel watches", "the processor", "run"],
    ),
    (("round 199: the angel watches the processor run", 24), ["round 199: the angel", "watches the processor", "run"]),
    (("round 199: the angel watches the processor run", 32), ["round 199: the angel watches the", "processor run"]),
    (
        ("round 199: angle of the vector decides the match", 4),
        ["round", "199:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 199: angle of the vector decides the match", 8),
        ["round", "199:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 199: angle of the vector decides the match", 12),
        ["round 199:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 199: angle of the vector decides the match", 16),
        ["round 199: angle", "of the vector", "decides the", "match"],
    ),
    (("round 199: angle of the vector decides the match", 24), ["round 199: angle of the", "vector decides the match"]),
    (("round 199: angle of the vector decides the match", 32), ["round 199: angle of the vector", "decides the match"]),
    (
        ("round 199: the candle burns twice as long at night", 4),
        ["round", "199:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 199: the candle burns twice as long at night", 8),
        ["round", "199: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 199: the candle burns twice as long at night", 12),
        ["round 199:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 199: the candle burns twice as long at night", 16),
        ["round 199: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 199: the candle burns twice as long at night", 24),
        ["round 199: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 199: the candle burns twice as long at night", 32),
        ["round 199: the candle burns", "twice as long at night"],
    ),
    (
        ("round 199: a mirror of the universe in one line", 4),
        ["round", "199:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 199: a mirror of the universe in one line", 8),
        ["round", "199: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 199: a mirror of the universe in one line", 12),
        ["round 199: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 199: a mirror of the universe in one line", 16),
        ["round 199: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 199: a mirror of the universe in one line", 24), ["round 199: a mirror of", "the universe in one line"]),
    (("round 199: a mirror of the universe in one line", 32), ["round 199: a mirror of the", "universe in one line"]),
    (
        ("round 199: the queue drains before the storm", 4),
        ["round", "199:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 199: the queue drains before the storm", 8),
        ["round", "199: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 199: the queue drains before the storm", 12),
        ["round 199:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 199: the queue drains before the storm", 16), ["round 199: the", "queue drains", "before the storm"]),
    (("round 199: the queue drains before the storm", 24), ["round 199: the queue", "drains before the storm"]),
    (("round 199: the queue drains before the storm", 32), ["round 199: the queue drains", "before the storm"]),
    (
        ("kitten199 sitting199 agent199 angle199 universe199 memory199", 6),
        ["kitten199", "sitting199", "agent199", "angle199", "universe199", "memory199"],
    ),
    (
        ("kitten199 sitting199 agent199 angle199 universe199 memory199", 10),
        ["kitten199", "sitting199", "agent199", "angle199", "universe199", "memory199"],
    ),
    (
        ("kitten199 sitting199 agent199 angle199 universe199 memory199", 18),
        ["kitten199", "sitting199", "agent199 angle199", "universe199", "memory199"],
    ),
    (
        ("kitten199 sitting199 agent199 angle199 universe199 memory199", 28),
        ["kitten199 sitting199", "agent199 angle199", "universe199 memory199"],
    ),
    (
        ("sitting199 agent199 angle199 universe199 memory199 stream199", 6),
        ["sitting199", "agent199", "angle199", "universe199", "memory199", "stream199"],
    ),
    (
        ("sitting199 agent199 angle199 universe199 memory199 stream199", 10),
        ["sitting199", "agent199", "angle199", "universe199", "memory199", "stream199"],
    ),
    (
        ("sitting199 agent199 angle199 universe199 memory199 stream199", 18),
        ["sitting199", "agent199 angle199", "universe199", "memory199", "stream199"],
    ),
    (
        ("sitting199 agent199 angle199 universe199 memory199 stream199", 28),
        ["sitting199 agent199 angle199", "universe199 memory199", "stream199"],
    ),
    (
        ("agent199 angle199 universe199 memory199 stream199 context199", 6),
        ["agent199", "angle199", "universe199", "memory199", "stream199", "context199"],
    ),
    (
        ("agent199 angle199 universe199 memory199 stream199 context199", 10),
        ["agent199", "angle199", "universe199", "memory199", "stream199", "context199"],
    ),
    (
        ("agent199 angle199 universe199 memory199 stream199 context199", 18),
        ["agent199 angle199", "universe199", "memory199", "stream199", "context199"],
    ),
    (
        ("agent199 angle199 universe199 memory199 stream199 context199", 28),
        ["agent199 angle199", "universe199 memory199", "stream199 context199"],
    ),
    (
        ("angle199 universe199 memory199 stream199 context199 knowledge199", 6),
        ["angle199", "universe199", "memory199", "stream199", "context199", "knowledge199"],
    ),
    (
        ("angle199 universe199 memory199 stream199 context199 knowledge199", 10),
        ["angle199", "universe199", "memory199", "stream199", "context199", "knowledge199"],
    ),
    (
        ("angle199 universe199 memory199 stream199 context199 knowledge199", 18),
        ["angle199", "universe199", "memory199", "stream199", "context199", "knowledge199"],
    ),
    (
        ("angle199 universe199 memory199 stream199 context199 knowledge199", 28),
        ["angle199 universe199", "memory199 stream199", "context199 knowledge199"],
    ),
    (
        ("universe199 memory199 stream199 context199 knowledge199 vector199", 6),
        ["universe199", "memory199", "stream199", "context199", "knowledge199", "vector199"],
    ),
    (
        ("universe199 memory199 stream199 context199 knowledge199 vector199", 10),
        ["universe199", "memory199", "stream199", "context199", "knowledge199", "vector199"],
    ),
    (
        ("universe199 memory199 stream199 context199 knowledge199 vector199", 18),
        ["universe199", "memory199", "stream199", "context199", "knowledge199", "vector199"],
    ),
    (
        ("universe199 memory199 stream199 context199 knowledge199 vector199", 28),
        ["universe199 memory199", "stream199 context199", "knowledge199 vector199"],
    ),
    (
        ("memory199 stream199 context199 knowledge199 vector199 processor199", 6),
        ["memory199", "stream199", "context199", "knowledge199", "vector199", "processor199"],
    ),
    (
        ("memory199 stream199 context199 knowledge199 vector199 processor199", 10),
        ["memory199", "stream199", "context199", "knowledge199", "vector199", "processor199"],
    ),
    (
        ("memory199 stream199 context199 knowledge199 vector199 processor199", 18),
        ["memory199", "stream199", "context199", "knowledge199", "vector199", "processor199"],
    ),
    (
        ("memory199 stream199 context199 knowledge199 vector199 processor199", 28),
        ["memory199 stream199", "context199 knowledge199", "vector199 processor199"],
    ),
    (
        ("stream199 context199 knowledge199 vector199 processor199 reasoning199", 6),
        ["stream199", "context199", "knowledge199", "vector199", "processor199", "reasoning199"],
    ),
    (
        ("stream199 context199 knowledge199 vector199 processor199 reasoning199", 10),
        ["stream199", "context199", "knowledge199", "vector199", "processor199", "reasoning199"],
    ),
    (
        ("stream199 context199 knowledge199 vector199 processor199 reasoning199", 18),
        ["stream199", "context199", "knowledge199", "vector199", "processor199", "reasoning199"],
    ),
    (
        ("stream199 context199 knowledge199 vector199 processor199 reasoning199", 28),
        ["stream199 context199", "knowledge199 vector199", "processor199 reasoning199"],
    ),
    (
        ("context199 knowledge199 vector199 processor199 reasoning199 machine199", 6),
        ["context199", "knowledge199", "vector199", "processor199", "reasoning199", "machine199"],
    ),
    (
        ("context199 knowledge199 vector199 processor199 reasoning199 machine199", 10),
        ["context199", "knowledge199", "vector199", "processor199", "reasoning199", "machine199"],
    ),
    (
        ("context199 knowledge199 vector199 processor199 reasoning199 machine199", 18),
        ["context199", "knowledge199", "vector199", "processor199", "reasoning199", "machine199"],
    ),
    (
        ("context199 knowledge199 vector199 processor199 reasoning199 machine199", 28),
        ["context199 knowledge199", "vector199 processor199", "reasoning199 machine199"],
    ),
    (
        ("knowledge199 vector199 processor199 reasoning199 machine199 learning199", 6),
        ["knowledge199", "vector199", "processor199", "reasoning199", "machine199", "learning199"],
    ),
    (
        ("knowledge199 vector199 processor199 reasoning199 machine199 learning199", 10),
        ["knowledge199", "vector199", "processor199", "reasoning199", "machine199", "learning199"],
    ),
    (
        ("knowledge199 vector199 processor199 reasoning199 machine199 learning199", 18),
        ["knowledge199", "vector199", "processor199", "reasoning199", "machine199", "learning199"],
    ),
    (
        ("knowledge199 vector199 processor199 reasoning199 machine199 learning199", 28),
        ["knowledge199 vector199", "processor199 reasoning199", "machine199 learning199"],
    ),
    (
        ("vector199 processor199 reasoning199 machine199 learning199 model199", 6),
        ["vector199", "processor199", "reasoning199", "machine199", "learning199", "model199"],
    ),
    (
        ("vector199 processor199 reasoning199 machine199 learning199 model199", 10),
        ["vector199", "processor199", "reasoning199", "machine199", "learning199", "model199"],
    ),
    (
        ("vector199 processor199 reasoning199 machine199 learning199 model199", 18),
        ["vector199", "processor199", "reasoning199", "machine199", "learning199", "model199"],
    ),
    (
        ("vector199 processor199 reasoning199 machine199 learning199 model199", 28),
        ["vector199 processor199", "reasoning199 machine199", "learning199 model199"],
    ),
    (
        ("processor199 reasoning199 machine199 learning199 model199 token199", 6),
        ["processor199", "reasoning199", "machine199", "learning199", "model199", "token199"],
    ),
    (
        ("processor199 reasoning199 machine199 learning199 model199 token199", 10),
        ["processor199", "reasoning199", "machine199", "learning199", "model199", "token199"],
    ),
    (
        ("processor199 reasoning199 machine199 learning199 model199 token199", 18),
        ["processor199", "reasoning199", "machine199", "learning199", "model199 token199"],
    ),
    (
        ("processor199 reasoning199 machine199 learning199 model199 token199", 28),
        ["processor199 reasoning199", "machine199 learning199", "model199 token199"],
    ),
    (
        ("reasoning199 machine199 learning199 model199 token199 prompt199", 6),
        ["reasoning199", "machine199", "learning199", "model199", "token199", "prompt199"],
    ),
    (
        ("reasoning199 machine199 learning199 model199 token199 prompt199", 10),
        ["reasoning199", "machine199", "learning199", "model199", "token199", "prompt199"],
    ),
    (
        ("reasoning199 machine199 learning199 model199 token199 prompt199", 18),
        ["reasoning199", "machine199", "learning199", "model199 token199", "prompt199"],
    ),
    (
        ("reasoning199 machine199 learning199 model199 token199 prompt199", 28),
        ["reasoning199 machine199", "learning199 model199", "token199 prompt199"],
    ),
    (
        ("machine199 learning199 model199 token199 prompt199 session199", 6),
        ["machine199", "learning199", "model199", "token199", "prompt199", "session199"],
    ),
    (
        ("machine199 learning199 model199 token199 prompt199 session199", 10),
        ["machine199", "learning199", "model199", "token199", "prompt199", "session199"],
    ),
    (
        ("machine199 learning199 model199 token199 prompt199 session199", 18),
        ["machine199", "learning199", "model199 token199", "prompt199", "session199"],
    ),
    (
        ("machine199 learning199 model199 token199 prompt199 session199", 28),
        ["machine199 learning199", "model199 token199 prompt199", "session199"],
    ),
    (
        ("learning199 model199 token199 prompt199 session199 library199", 6),
        ["learning199", "model199", "token199", "prompt199", "session199", "library199"],
    ),
    (
        ("learning199 model199 token199 prompt199 session199 library199", 10),
        ["learning199", "model199", "token199", "prompt199", "session199", "library199"],
    ),
    (
        ("learning199 model199 token199 prompt199 session199 library199", 18),
        ["learning199", "model199 token199", "prompt199", "session199", "library199"],
    ),
    (
        ("learning199 model199 token199 prompt199 session199 library199", 28),
        ["learning199 model199", "token199 prompt199", "session199 library199"],
    ),
    (
        ("model199 token199 prompt199 session199 library199 service199", 6),
        ["model199", "token199", "prompt199", "session199", "library199", "service199"],
    ),
    (
        ("model199 token199 prompt199 session199 library199 service199", 10),
        ["model199", "token199", "prompt199", "session199", "library199", "service199"],
    ),
    (
        ("model199 token199 prompt199 session199 library199 service199", 18),
        ["model199 token199", "prompt199", "session199", "library199", "service199"],
    ),
    (
        ("model199 token199 prompt199 session199 library199 service199", 28),
        ["model199 token199 prompt199", "session199 library199", "service199"],
    ),
    (
        ("token199 prompt199 session199 library199 service199 gateway199", 6),
        ["token199", "prompt199", "session199", "library199", "service199", "gateway199"],
    ),
    (
        ("token199 prompt199 session199 library199 service199 gateway199", 10),
        ["token199", "prompt199", "session199", "library199", "service199", "gateway199"],
    ),
    (
        ("token199 prompt199 session199 library199 service199 gateway199", 18),
        ["token199 prompt199", "session199", "library199", "service199", "gateway199"],
    ),
    (
        ("token199 prompt199 session199 library199 service199 gateway199", 28),
        ["token199 prompt199", "session199 library199", "service199 gateway199"],
    ),
    (
        ("prompt199 session199 library199 service199 gateway199 storage199", 6),
        ["prompt199", "session199", "library199", "service199", "gateway199", "storage199"],
    ),
    (
        ("prompt199 session199 library199 service199 gateway199 storage199", 10),
        ["prompt199", "session199", "library199", "service199", "gateway199", "storage199"],
    ),
    (
        ("prompt199 session199 library199 service199 gateway199 storage199", 18),
        ["prompt199", "session199", "library199", "service199", "gateway199", "storage199"],
    ),
    (
        ("prompt199 session199 library199 service199 gateway199 storage199", 28),
        ["prompt199 session199", "library199 service199", "gateway199 storage199"],
    ),
    (
        ("session199 library199 service199 gateway199 storage199 network199", 6),
        ["session199", "library199", "service199", "gateway199", "storage199", "network199"],
    ),
    (
        ("session199 library199 service199 gateway199 storage199 network199", 10),
        ["session199", "library199", "service199", "gateway199", "storage199", "network199"],
    ),
    (
        ("session199 library199 service199 gateway199 storage199 network199", 18),
        ["session199", "library199", "service199", "gateway199", "storage199", "network199"],
    ),
    (
        ("session199 library199 service199 gateway199 storage199 network199", 28),
        ["session199 library199", "service199 gateway199", "storage199 network199"],
    ),
    (
        ("library199 service199 gateway199 storage199 network199 latency199", 6),
        ["library199", "service199", "gateway199", "storage199", "network199", "latency199"],
    ),
    (
        ("library199 service199 gateway199 storage199 network199 latency199", 10),
        ["library199", "service199", "gateway199", "storage199", "network199", "latency199"],
    ),
    (
        ("library199 service199 gateway199 storage199 network199 latency199", 18),
        ["library199", "service199", "gateway199", "storage199", "network199", "latency199"],
    ),
    (
        ("library199 service199 gateway199 storage199 network199 latency199", 28),
        ["library199 service199", "gateway199 storage199", "network199 latency199"],
    ),
    (
        ("service199 gateway199 storage199 network199 latency199 buffer199", 6),
        ["service199", "gateway199", "storage199", "network199", "latency199", "buffer199"],
    ),
    (
        ("service199 gateway199 storage199 network199 latency199 buffer199", 10),
        ["service199", "gateway199", "storage199", "network199", "latency199", "buffer199"],
    ),
    (
        ("service199 gateway199 storage199 network199 latency199 buffer199", 18),
        ["service199", "gateway199", "storage199", "network199", "latency199", "buffer199"],
    ),
    (
        ("service199 gateway199 storage199 network199 latency199 buffer199", 28),
        ["service199 gateway199", "storage199 network199", "latency199 buffer199"],
    ),
    (
        ("gateway199 storage199 network199 latency199 buffer199 queue199", 6),
        ["gateway199", "storage199", "network199", "latency199", "buffer199", "queue199"],
    ),
    (
        ("gateway199 storage199 network199 latency199 buffer199 queue199", 10),
        ["gateway199", "storage199", "network199", "latency199", "buffer199", "queue199"],
    ),
    (
        ("gateway199 storage199 network199 latency199 buffer199 queue199", 18),
        ["gateway199", "storage199", "network199", "latency199", "buffer199 queue199"],
    ),
    (
        ("gateway199 storage199 network199 latency199 buffer199 queue199", 28),
        ["gateway199 storage199", "network199 latency199", "buffer199 queue199"],
    ),
    (
        ("storage199 network199 latency199 buffer199 queue199 worker199", 6),
        ["storage199", "network199", "latency199", "buffer199", "queue199", "worker199"],
    ),
    (
        ("storage199 network199 latency199 buffer199 queue199 worker199", 10),
        ["storage199", "network199", "latency199", "buffer199", "queue199", "worker199"],
    ),
    (
        ("storage199 network199 latency199 buffer199 queue199 worker199", 18),
        ["storage199", "network199", "latency199", "buffer199 queue199", "worker199"],
    ),
    (
        ("storage199 network199 latency199 buffer199 queue199 worker199", 28),
        ["storage199 network199", "latency199 buffer199", "queue199 worker199"],
    ),
    (
        ("network199 latency199 buffer199 queue199 worker199 kernel199", 6),
        ["network199", "latency199", "buffer199", "queue199", "worker199", "kernel199"],
    ),
    (
        ("network199 latency199 buffer199 queue199 worker199 kernel199", 10),
        ["network199", "latency199", "buffer199", "queue199", "worker199", "kernel199"],
    ),
    (
        ("network199 latency199 buffer199 queue199 worker199 kernel199", 18),
        ["network199", "latency199", "buffer199 queue199", "worker199", "kernel199"],
    ),
    (
        ("network199 latency199 buffer199 queue199 worker199 kernel199", 28),
        ["network199 latency199", "buffer199 queue199 worker199", "kernel199"],
    ),
    (
        ("latency199 buffer199 queue199 worker199 kernel199 signal199", 6),
        ["latency199", "buffer199", "queue199", "worker199", "kernel199", "signal199"],
    ),
    (
        ("latency199 buffer199 queue199 worker199 kernel199 signal199", 10),
        ["latency199", "buffer199", "queue199", "worker199", "kernel199", "signal199"],
    ),
    (
        ("latency199 buffer199 queue199 worker199 kernel199 signal199", 18),
        ["latency199", "buffer199 queue199", "worker199", "kernel199", "signal199"],
    ),
    (
        ("latency199 buffer199 queue199 worker199 kernel199 signal199", 28),
        ["latency199 buffer199", "queue199 worker199 kernel199", "signal199"],
    ),
    (
        ("buffer199 queue199 worker199 kernel199 signal199 packet199", 6),
        ["buffer199", "queue199", "worker199", "kernel199", "signal199", "packet199"],
    ),
    (
        ("buffer199 queue199 worker199 kernel199 signal199 packet199", 10),
        ["buffer199", "queue199", "worker199", "kernel199", "signal199", "packet199"],
    ),
    (
        ("buffer199 queue199 worker199 kernel199 signal199 packet199", 18),
        ["buffer199 queue199", "worker199", "kernel199", "signal199", "packet199"],
    ),
    (
        ("buffer199 queue199 worker199 kernel199 signal199 packet199", 28),
        ["buffer199 queue199 worker199", "kernel199 signal199", "packet199"],
    ),
    (
        ("queue199 worker199 kernel199 signal199 packet199 router199", 6),
        ["queue199", "worker199", "kernel199", "signal199", "packet199", "router199"],
    ),
    (
        ("queue199 worker199 kernel199 signal199 packet199 router199", 10),
        ["queue199", "worker199", "kernel199", "signal199", "packet199", "router199"],
    ),
    (
        ("queue199 worker199 kernel199 signal199 packet199 router199", 18),
        ["queue199 worker199", "kernel199", "signal199", "packet199", "router199"],
    ),
    (
        ("queue199 worker199 kernel199 signal199 packet199 router199", 28),
        ["queue199 worker199 kernel199", "signal199 packet199", "router199"],
    ),
    (
        ("worker199 kernel199 signal199 packet199 router199 cluster199", 6),
        ["worker199", "kernel199", "signal199", "packet199", "router199", "cluster199"],
    ),
    (
        ("worker199 kernel199 signal199 packet199 router199 cluster199", 10),
        ["worker199", "kernel199", "signal199", "packet199", "router199", "cluster199"],
    ),
    (
        ("worker199 kernel199 signal199 packet199 router199 cluster199", 18),
        ["worker199", "kernel199", "signal199", "packet199", "router199", "cluster199"],
    ),
    (
        ("worker199 kernel199 signal199 packet199 router199 cluster199", 28),
        ["worker199 kernel199", "signal199 packet199", "router199 cluster199"],
    ),
    (
        ("kernel199 signal199 packet199 router199 cluster199 mirror199", 6),
        ["kernel199", "signal199", "packet199", "router199", "cluster199", "mirror199"],
    ),
    (
        ("kernel199 signal199 packet199 router199 cluster199 mirror199", 10),
        ["kernel199", "signal199", "packet199", "router199", "cluster199", "mirror199"],
    ),
    (
        ("kernel199 signal199 packet199 router199 cluster199 mirror199", 18),
        ["kernel199", "signal199", "packet199", "router199", "cluster199", "mirror199"],
    ),
    (
        ("kernel199 signal199 packet199 router199 cluster199 mirror199", 28),
        ["kernel199 signal199", "packet199 router199", "cluster199 mirror199"],
    ),
    (
        ("signal199 packet199 router199 cluster199 mirror199 filter199", 6),
        ["signal199", "packet199", "router199", "cluster199", "mirror199", "filter199"],
    ),
    (
        ("signal199 packet199 router199 cluster199 mirror199 filter199", 10),
        ["signal199", "packet199", "router199", "cluster199", "mirror199", "filter199"],
    ),
    (
        ("signal199 packet199 router199 cluster199 mirror199 filter199", 18),
        ["signal199", "packet199", "router199", "cluster199", "mirror199", "filter199"],
    ),
    (
        ("signal199 packet199 router199 cluster199 mirror199 filter199", 28),
        ["signal199 packet199", "router199 cluster199", "mirror199 filter199"],
    ),
    (
        ("packet199 router199 cluster199 mirror199 filter199 ranking199", 6),
        ["packet199", "router199", "cluster199", "mirror199", "filter199", "ranking199"],
    ),
    (
        ("packet199 router199 cluster199 mirror199 filter199 ranking199", 10),
        ["packet199", "router199", "cluster199", "mirror199", "filter199", "ranking199"],
    ),
    (
        ("packet199 router199 cluster199 mirror199 filter199 ranking199", 18),
        ["packet199", "router199", "cluster199", "mirror199", "filter199", "ranking199"],
    ),
    (
        ("packet199 router199 cluster199 mirror199 filter199 ranking199", 28),
        ["packet199 router199", "cluster199 mirror199", "filter199 ranking199"],
    ),
    (
        ("router199 cluster199 mirror199 filter199 ranking199 encoding199", 6),
        ["router199", "cluster199", "mirror199", "filter199", "ranking199", "encoding199"],
    ),
    (
        ("router199 cluster199 mirror199 filter199 ranking199 encoding199", 10),
        ["router199", "cluster199", "mirror199", "filter199", "ranking199", "encoding199"],
    ),
    (
        ("router199 cluster199 mirror199 filter199 ranking199 encoding199", 18),
        ["router199", "cluster199", "mirror199", "filter199", "ranking199", "encoding199"],
    ),
    (
        ("router199 cluster199 mirror199 filter199 ranking199 encoding199", 28),
        ["router199 cluster199", "mirror199 filter199", "ranking199 encoding199"],
    ),
    (
        ("cluster199 mirror199 filter199 ranking199 encoding199 mapping199", 6),
        ["cluster199", "mirror199", "filter199", "ranking199", "encoding199", "mapping199"],
    ),
    (
        ("cluster199 mirror199 filter199 ranking199 encoding199 mapping199", 10),
        ["cluster199", "mirror199", "filter199", "ranking199", "encoding199", "mapping199"],
    ),
    (
        ("cluster199 mirror199 filter199 ranking199 encoding199 mapping199", 18),
        ["cluster199", "mirror199", "filter199", "ranking199", "encoding199", "mapping199"],
    ),
    (
        ("cluster199 mirror199 filter199 ranking199 encoding199 mapping199", 28),
        ["cluster199 mirror199", "filter199 ranking199", "encoding199 mapping199"],
    ),
    (
        ("mirror199 filter199 ranking199 encoding199 mapping199 record199", 6),
        ["mirror199", "filter199", "ranking199", "encoding199", "mapping199", "record199"],
    ),
    (
        ("mirror199 filter199 ranking199 encoding199 mapping199 record199", 10),
        ["mirror199", "filter199", "ranking199", "encoding199", "mapping199", "record199"],
    ),
    (
        ("mirror199 filter199 ranking199 encoding199 mapping199 record199", 18),
        ["mirror199", "filter199", "ranking199", "encoding199", "mapping199", "record199"],
    ),
    (
        ("mirror199 filter199 ranking199 encoding199 mapping199 record199", 28),
        ["mirror199 filter199", "ranking199 encoding199", "mapping199 record199"],
    ),
    (
        ("filter199 ranking199 encoding199 mapping199 record199 candle199", 6),
        ["filter199", "ranking199", "encoding199", "mapping199", "record199", "candle199"],
    ),
    (
        ("filter199 ranking199 encoding199 mapping199 record199 candle199", 10),
        ["filter199", "ranking199", "encoding199", "mapping199", "record199", "candle199"],
    ),
    (
        ("filter199 ranking199 encoding199 mapping199 record199 candle199", 18),
        ["filter199", "ranking199", "encoding199", "mapping199", "record199", "candle199"],
    ),
    (
        ("filter199 ranking199 encoding199 mapping199 record199 candle199", 28),
        ["filter199 ranking199", "encoding199 mapping199", "record199 candle199"],
    ),
    (
        ("ranking199 encoding199 mapping199 record199 candle199 thread199", 6),
        ["ranking199", "encoding199", "mapping199", "record199", "candle199", "thread199"],
    ),
    (
        ("ranking199 encoding199 mapping199 record199 candle199 thread199", 10),
        ["ranking199", "encoding199", "mapping199", "record199", "candle199", "thread199"],
    ),
    (
        ("ranking199 encoding199 mapping199 record199 candle199 thread199", 18),
        ["ranking199", "encoding199", "mapping199", "record199", "candle199", "thread199"],
    ),
    (
        ("ranking199 encoding199 mapping199 record199 candle199 thread199", 28),
        ["ranking199 encoding199", "mapping199 record199", "candle199 thread199"],
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
