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
        ("round 152: the quick brown fox jumps over the lazy dog", 4),
        ["round", "152:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", 8),
        ["round", "152: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", 12),
        ["round 152:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", 16),
        ["round 152: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", 24),
        ["round 152: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 152: the quick brown fox jumps over the lazy dog", 32),
        ["round 152: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", 4),
        ["round", "152:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", 8),
        ["round", "152:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", 12),
        ["round 152:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", 16),
        ["round 152:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", 24),
        ["round 152: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 152: agentuniverse is a framework for multi agents", 32),
        ["round 152: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", 4),
        ["round", "152:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", 8),
        ["round", "152:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", 12),
        ["round 152:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", 16),
        ["round 152:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", 24),
        ["round 152: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 152: knowledge stored as vectors enables retrieval", 32),
        ["round 152: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 152: the processor reads the record then stops", 4),
        ["round", "152:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 152: the processor reads the record then stops", 8),
        ["round", "152: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 152: the processor reads the record then stops", 12),
        ["round 152:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 152: the processor reads the record then stops", 16),
        ["round 152: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 152: the processor reads the record then stops", 24),
        ["round 152: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 152: the processor reads the record then stops", 32),
        ["round 152: the processor reads", "the record then stops"],
    ),
    (
        ("round 152: a worker pulls the next task from the queue", 4),
        ["round", "152:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 152: a worker pulls the next task from the queue", 8),
        ["round", "152: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 152: a worker pulls the next task from the queue", 12),
        ["round 152: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 152: a worker pulls the next task from the queue", 16),
        ["round 152: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 152: a worker pulls the next task from the queue", 24),
        ["round 152: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 152: a worker pulls the next task from the queue", 32),
        ["round 152: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 152: signals travel through the network layer", 4),
        ["round", "152:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 152: signals travel through the network layer", 8),
        ["round", "152:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 152: signals travel through the network layer", 12),
        ["round 152:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 152: signals travel through the network layer", 16),
        ["round 152:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 152: signals travel through the network layer", 24),
        ["round 152: signals", "travel through the", "network layer"],
    ),
    (
        ("round 152: signals travel through the network layer", 32),
        ["round 152: signals travel", "through the network layer"],
    ),
    (
        ("round 152: the gateway routes each request by policy", 4),
        ["round", "152:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 152: the gateway routes each request by policy", 8),
        ["round", "152: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 152: the gateway routes each request by policy", 12),
        ["round 152:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 152: the gateway routes each request by policy", 16),
        ["round 152: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 152: the gateway routes each request by policy", 24),
        ["round 152: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 152: the gateway routes each request by policy", 32),
        ["round 152: the gateway routes", "each request by policy"],
    ),
    (
        ("round 152: memory grows until the buffer is full", 4),
        ["round", "152:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 152: memory grows until the buffer is full", 8),
        ["round", "152:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 152: memory grows until the buffer is full", 12),
        ["round 152:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 152: memory grows until the buffer is full", 16),
        ["round 152:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 152: memory grows until the buffer is full", 24), ["round 152: memory grows", "until the buffer is full"]),
    (("round 152: memory grows until the buffer is full", 32), ["round 152: memory grows until", "the buffer is full"]),
    (
        ("round 152: the cluster mirrors every packet twice", 4),
        ["round", "152:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 152: the cluster mirrors every packet twice", 8),
        ["round", "152: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 152: the cluster mirrors every packet twice", 12),
        ["round 152:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 152: the cluster mirrors every packet twice", 16),
        ["round 152: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 152: the cluster mirrors every packet twice", 24),
        ["round 152: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 152: the cluster mirrors every packet twice", 32),
        ["round 152: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", 4),
        ["round", "152:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", 8),
        ["round", "152:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", 12),
        ["round 152:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", 16),
        ["round 152:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", 24),
        ["round 152: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 152: ranking uses tokens learned from the corpus", 32),
        ["round 152: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 152: a long session ends when the candle dies", 4),
        ["round", "152:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 152: a long session ends when the candle dies", 8),
        ["round", "152: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 152: a long session ends when the candle dies", 12),
        ["round 152: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 152: a long session ends when the candle dies", 16),
        ["round 152: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 152: a long session ends when the candle dies", 24),
        ["round 152: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 152: a long session ends when the candle dies", 32),
        ["round 152: a long session ends", "when the candle dies"],
    ),
    (
        ("round 152: encode the prompt then map the result", 4),
        ["round", "152:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 152: encode the prompt then map the result", 8),
        ["round", "152:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 152: encode the prompt then map the result", 12),
        ["round 152:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 152: encode the prompt then map the result", 16),
        ["round 152:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 152: encode the prompt then map the result", 24),
        ["round 152: encode the", "prompt then map the", "result"],
    ),
    (("round 152: encode the prompt then map the result", 32), ["round 152: encode the prompt", "then map the result"]),
    (
        ("round 152: the kernel wakes the worker at dawn", 4),
        ["round", "152:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 152: the kernel wakes the worker at dawn", 8),
        ["round", "152: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 152: the kernel wakes the worker at dawn", 12),
        ["round 152:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 152: the kernel wakes the worker at dawn", 16), ["round 152: the", "kernel wakes the", "worker at dawn"]),
    (("round 152: the kernel wakes the worker at dawn", 24), ["round 152: the kernel", "wakes the worker at dawn"]),
    (("round 152: the kernel wakes the worker at dawn", 32), ["round 152: the kernel wakes the", "worker at dawn"]),
    (
        ("round 152: service latency drops after the patch", 4),
        ["round", "152:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 152: service latency drops after the patch", 8),
        ["round", "152:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 152: service latency drops after the patch", 12),
        ["round 152:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 152: service latency drops after the patch", 16),
        ["round 152:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 152: service latency drops after the patch", 24),
        ["round 152: service", "latency drops after the", "patch"],
    ),
    (("round 152: service latency drops after the patch", 32), ["round 152: service latency drops", "after the patch"]),
    (
        ("round 152: the library caches every vector it sees", 4),
        ["round", "152:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 152: the library caches every vector it sees", 8),
        ["round", "152: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 152: the library caches every vector it sees", 12),
        ["round 152:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 152: the library caches every vector it sees", 16),
        ["round 152: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 152: the library caches every vector it sees", 24),
        ["round 152: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 152: the library caches every vector it sees", 32),
        ["round 152: the library caches", "every vector it sees"],
    ),
    (
        ("round 152: agents argue then the debate resolves", 4),
        ["round", "152:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 152: agents argue then the debate resolves", 8),
        ["round", "152:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 152: agents argue then the debate resolves", 12),
        ["round 152:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 152: agents argue then the debate resolves", 16),
        ["round 152:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 152: agents argue then the debate resolves", 24), ["round 152: agents argue", "then the debate resolves"]),
    (("round 152: agents argue then the debate resolves", 32), ["round 152: agents argue then the", "debate resolves"]),
    (
        ("round 152: the filter keeps only strong matches", 4),
        ["round", "152:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 152: the filter keeps only strong matches", 8),
        ["round", "152: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 152: the filter keeps only strong matches", 12),
        ["round 152:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 152: the filter keeps only strong matches", 16),
        ["round 152: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 152: the filter keeps only strong matches", 24),
        ["round 152: the filter", "keeps only strong", "matches"],
    ),
    (("round 152: the filter keeps only strong matches", 32), ["round 152: the filter keeps only", "strong matches"]),
    (
        ("round 152: the model answers with a short reply", 4),
        ["round", "152:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 152: the model answers with a short reply", 8),
        ["round", "152: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 152: the model answers with a short reply", 12),
        ["round 152:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 152: the model answers with a short reply", 16),
        ["round 152: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 152: the model answers with a short reply", 24),
        ["round 152: the model", "answers with a short", "reply"],
    ),
    (("round 152: the model answers with a short reply", 32), ["round 152: the model answers", "with a short reply"]),
    (
        ("round 152: the recorder stores the reasoning trace", 4),
        ["round", "152:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 152: the recorder stores the reasoning trace", 8),
        ["round", "152: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 152: the recorder stores the reasoning trace", 12),
        ["round 152:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 152: the recorder stores the reasoning trace", 16),
        ["round 152: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 152: the recorder stores the reasoning trace", 24),
        ["round 152: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 152: the recorder stores the reasoning trace", 32),
        ["round 152: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 152: the angel watches the processor run", 4),
        ["round", "152:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 152: the angel watches the processor run", 8),
        ["round", "152: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 152: the angel watches the processor run", 12),
        ["round 152:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 152: the angel watches the processor run", 16),
        ["round 152: the", "angel watches", "the processor", "run"],
    ),
    (("round 152: the angel watches the processor run", 24), ["round 152: the angel", "watches the processor", "run"]),
    (("round 152: the angel watches the processor run", 32), ["round 152: the angel watches the", "processor run"]),
    (
        ("round 152: angle of the vector decides the match", 4),
        ["round", "152:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 152: angle of the vector decides the match", 8),
        ["round", "152:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 152: angle of the vector decides the match", 12),
        ["round 152:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 152: angle of the vector decides the match", 16),
        ["round 152: angle", "of the vector", "decides the", "match"],
    ),
    (("round 152: angle of the vector decides the match", 24), ["round 152: angle of the", "vector decides the match"]),
    (("round 152: angle of the vector decides the match", 32), ["round 152: angle of the vector", "decides the match"]),
    (
        ("round 152: the candle burns twice as long at night", 4),
        ["round", "152:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 152: the candle burns twice as long at night", 8),
        ["round", "152: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 152: the candle burns twice as long at night", 12),
        ["round 152:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 152: the candle burns twice as long at night", 16),
        ["round 152: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 152: the candle burns twice as long at night", 24),
        ["round 152: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 152: the candle burns twice as long at night", 32),
        ["round 152: the candle burns", "twice as long at night"],
    ),
    (
        ("round 152: a mirror of the universe in one line", 4),
        ["round", "152:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 152: a mirror of the universe in one line", 8),
        ["round", "152: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 152: a mirror of the universe in one line", 12),
        ["round 152: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 152: a mirror of the universe in one line", 16),
        ["round 152: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 152: a mirror of the universe in one line", 24), ["round 152: a mirror of", "the universe in one line"]),
    (("round 152: a mirror of the universe in one line", 32), ["round 152: a mirror of the", "universe in one line"]),
    (
        ("round 152: the queue drains before the storm", 4),
        ["round", "152:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 152: the queue drains before the storm", 8),
        ["round", "152: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 152: the queue drains before the storm", 12),
        ["round 152:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 152: the queue drains before the storm", 16), ["round 152: the", "queue drains", "before the storm"]),
    (("round 152: the queue drains before the storm", 24), ["round 152: the queue", "drains before the storm"]),
    (("round 152: the queue drains before the storm", 32), ["round 152: the queue drains", "before the storm"]),
    (
        ("kitten152 sitting152 agent152 angle152 universe152 memory152", 6),
        ["kitten152", "sitting152", "agent152", "angle152", "universe152", "memory152"],
    ),
    (
        ("kitten152 sitting152 agent152 angle152 universe152 memory152", 10),
        ["kitten152", "sitting152", "agent152", "angle152", "universe152", "memory152"],
    ),
    (
        ("kitten152 sitting152 agent152 angle152 universe152 memory152", 18),
        ["kitten152", "sitting152", "agent152 angle152", "universe152", "memory152"],
    ),
    (
        ("kitten152 sitting152 agent152 angle152 universe152 memory152", 28),
        ["kitten152 sitting152", "agent152 angle152", "universe152 memory152"],
    ),
    (
        ("sitting152 agent152 angle152 universe152 memory152 stream152", 6),
        ["sitting152", "agent152", "angle152", "universe152", "memory152", "stream152"],
    ),
    (
        ("sitting152 agent152 angle152 universe152 memory152 stream152", 10),
        ["sitting152", "agent152", "angle152", "universe152", "memory152", "stream152"],
    ),
    (
        ("sitting152 agent152 angle152 universe152 memory152 stream152", 18),
        ["sitting152", "agent152 angle152", "universe152", "memory152", "stream152"],
    ),
    (
        ("sitting152 agent152 angle152 universe152 memory152 stream152", 28),
        ["sitting152 agent152 angle152", "universe152 memory152", "stream152"],
    ),
    (
        ("agent152 angle152 universe152 memory152 stream152 context152", 6),
        ["agent152", "angle152", "universe152", "memory152", "stream152", "context152"],
    ),
    (
        ("agent152 angle152 universe152 memory152 stream152 context152", 10),
        ["agent152", "angle152", "universe152", "memory152", "stream152", "context152"],
    ),
    (
        ("agent152 angle152 universe152 memory152 stream152 context152", 18),
        ["agent152 angle152", "universe152", "memory152", "stream152", "context152"],
    ),
    (
        ("agent152 angle152 universe152 memory152 stream152 context152", 28),
        ["agent152 angle152", "universe152 memory152", "stream152 context152"],
    ),
    (
        ("angle152 universe152 memory152 stream152 context152 knowledge152", 6),
        ["angle152", "universe152", "memory152", "stream152", "context152", "knowledge152"],
    ),
    (
        ("angle152 universe152 memory152 stream152 context152 knowledge152", 10),
        ["angle152", "universe152", "memory152", "stream152", "context152", "knowledge152"],
    ),
    (
        ("angle152 universe152 memory152 stream152 context152 knowledge152", 18),
        ["angle152", "universe152", "memory152", "stream152", "context152", "knowledge152"],
    ),
    (
        ("angle152 universe152 memory152 stream152 context152 knowledge152", 28),
        ["angle152 universe152", "memory152 stream152", "context152 knowledge152"],
    ),
    (
        ("universe152 memory152 stream152 context152 knowledge152 vector152", 6),
        ["universe152", "memory152", "stream152", "context152", "knowledge152", "vector152"],
    ),
    (
        ("universe152 memory152 stream152 context152 knowledge152 vector152", 10),
        ["universe152", "memory152", "stream152", "context152", "knowledge152", "vector152"],
    ),
    (
        ("universe152 memory152 stream152 context152 knowledge152 vector152", 18),
        ["universe152", "memory152", "stream152", "context152", "knowledge152", "vector152"],
    ),
    (
        ("universe152 memory152 stream152 context152 knowledge152 vector152", 28),
        ["universe152 memory152", "stream152 context152", "knowledge152 vector152"],
    ),
    (
        ("memory152 stream152 context152 knowledge152 vector152 processor152", 6),
        ["memory152", "stream152", "context152", "knowledge152", "vector152", "processor152"],
    ),
    (
        ("memory152 stream152 context152 knowledge152 vector152 processor152", 10),
        ["memory152", "stream152", "context152", "knowledge152", "vector152", "processor152"],
    ),
    (
        ("memory152 stream152 context152 knowledge152 vector152 processor152", 18),
        ["memory152", "stream152", "context152", "knowledge152", "vector152", "processor152"],
    ),
    (
        ("memory152 stream152 context152 knowledge152 vector152 processor152", 28),
        ["memory152 stream152", "context152 knowledge152", "vector152 processor152"],
    ),
    (
        ("stream152 context152 knowledge152 vector152 processor152 reasoning152", 6),
        ["stream152", "context152", "knowledge152", "vector152", "processor152", "reasoning152"],
    ),
    (
        ("stream152 context152 knowledge152 vector152 processor152 reasoning152", 10),
        ["stream152", "context152", "knowledge152", "vector152", "processor152", "reasoning152"],
    ),
    (
        ("stream152 context152 knowledge152 vector152 processor152 reasoning152", 18),
        ["stream152", "context152", "knowledge152", "vector152", "processor152", "reasoning152"],
    ),
    (
        ("stream152 context152 knowledge152 vector152 processor152 reasoning152", 28),
        ["stream152 context152", "knowledge152 vector152", "processor152 reasoning152"],
    ),
    (
        ("context152 knowledge152 vector152 processor152 reasoning152 machine152", 6),
        ["context152", "knowledge152", "vector152", "processor152", "reasoning152", "machine152"],
    ),
    (
        ("context152 knowledge152 vector152 processor152 reasoning152 machine152", 10),
        ["context152", "knowledge152", "vector152", "processor152", "reasoning152", "machine152"],
    ),
    (
        ("context152 knowledge152 vector152 processor152 reasoning152 machine152", 18),
        ["context152", "knowledge152", "vector152", "processor152", "reasoning152", "machine152"],
    ),
    (
        ("context152 knowledge152 vector152 processor152 reasoning152 machine152", 28),
        ["context152 knowledge152", "vector152 processor152", "reasoning152 machine152"],
    ),
    (
        ("knowledge152 vector152 processor152 reasoning152 machine152 learning152", 6),
        ["knowledge152", "vector152", "processor152", "reasoning152", "machine152", "learning152"],
    ),
    (
        ("knowledge152 vector152 processor152 reasoning152 machine152 learning152", 10),
        ["knowledge152", "vector152", "processor152", "reasoning152", "machine152", "learning152"],
    ),
    (
        ("knowledge152 vector152 processor152 reasoning152 machine152 learning152", 18),
        ["knowledge152", "vector152", "processor152", "reasoning152", "machine152", "learning152"],
    ),
    (
        ("knowledge152 vector152 processor152 reasoning152 machine152 learning152", 28),
        ["knowledge152 vector152", "processor152 reasoning152", "machine152 learning152"],
    ),
    (
        ("vector152 processor152 reasoning152 machine152 learning152 model152", 6),
        ["vector152", "processor152", "reasoning152", "machine152", "learning152", "model152"],
    ),
    (
        ("vector152 processor152 reasoning152 machine152 learning152 model152", 10),
        ["vector152", "processor152", "reasoning152", "machine152", "learning152", "model152"],
    ),
    (
        ("vector152 processor152 reasoning152 machine152 learning152 model152", 18),
        ["vector152", "processor152", "reasoning152", "machine152", "learning152", "model152"],
    ),
    (
        ("vector152 processor152 reasoning152 machine152 learning152 model152", 28),
        ["vector152 processor152", "reasoning152 machine152", "learning152 model152"],
    ),
    (
        ("processor152 reasoning152 machine152 learning152 model152 token152", 6),
        ["processor152", "reasoning152", "machine152", "learning152", "model152", "token152"],
    ),
    (
        ("processor152 reasoning152 machine152 learning152 model152 token152", 10),
        ["processor152", "reasoning152", "machine152", "learning152", "model152", "token152"],
    ),
    (
        ("processor152 reasoning152 machine152 learning152 model152 token152", 18),
        ["processor152", "reasoning152", "machine152", "learning152", "model152 token152"],
    ),
    (
        ("processor152 reasoning152 machine152 learning152 model152 token152", 28),
        ["processor152 reasoning152", "machine152 learning152", "model152 token152"],
    ),
    (
        ("reasoning152 machine152 learning152 model152 token152 prompt152", 6),
        ["reasoning152", "machine152", "learning152", "model152", "token152", "prompt152"],
    ),
    (
        ("reasoning152 machine152 learning152 model152 token152 prompt152", 10),
        ["reasoning152", "machine152", "learning152", "model152", "token152", "prompt152"],
    ),
    (
        ("reasoning152 machine152 learning152 model152 token152 prompt152", 18),
        ["reasoning152", "machine152", "learning152", "model152 token152", "prompt152"],
    ),
    (
        ("reasoning152 machine152 learning152 model152 token152 prompt152", 28),
        ["reasoning152 machine152", "learning152 model152", "token152 prompt152"],
    ),
    (
        ("machine152 learning152 model152 token152 prompt152 session152", 6),
        ["machine152", "learning152", "model152", "token152", "prompt152", "session152"],
    ),
    (
        ("machine152 learning152 model152 token152 prompt152 session152", 10),
        ["machine152", "learning152", "model152", "token152", "prompt152", "session152"],
    ),
    (
        ("machine152 learning152 model152 token152 prompt152 session152", 18),
        ["machine152", "learning152", "model152 token152", "prompt152", "session152"],
    ),
    (
        ("machine152 learning152 model152 token152 prompt152 session152", 28),
        ["machine152 learning152", "model152 token152 prompt152", "session152"],
    ),
    (
        ("learning152 model152 token152 prompt152 session152 library152", 6),
        ["learning152", "model152", "token152", "prompt152", "session152", "library152"],
    ),
    (
        ("learning152 model152 token152 prompt152 session152 library152", 10),
        ["learning152", "model152", "token152", "prompt152", "session152", "library152"],
    ),
    (
        ("learning152 model152 token152 prompt152 session152 library152", 18),
        ["learning152", "model152 token152", "prompt152", "session152", "library152"],
    ),
    (
        ("learning152 model152 token152 prompt152 session152 library152", 28),
        ["learning152 model152", "token152 prompt152", "session152 library152"],
    ),
    (
        ("model152 token152 prompt152 session152 library152 service152", 6),
        ["model152", "token152", "prompt152", "session152", "library152", "service152"],
    ),
    (
        ("model152 token152 prompt152 session152 library152 service152", 10),
        ["model152", "token152", "prompt152", "session152", "library152", "service152"],
    ),
    (
        ("model152 token152 prompt152 session152 library152 service152", 18),
        ["model152 token152", "prompt152", "session152", "library152", "service152"],
    ),
    (
        ("model152 token152 prompt152 session152 library152 service152", 28),
        ["model152 token152 prompt152", "session152 library152", "service152"],
    ),
    (
        ("token152 prompt152 session152 library152 service152 gateway152", 6),
        ["token152", "prompt152", "session152", "library152", "service152", "gateway152"],
    ),
    (
        ("token152 prompt152 session152 library152 service152 gateway152", 10),
        ["token152", "prompt152", "session152", "library152", "service152", "gateway152"],
    ),
    (
        ("token152 prompt152 session152 library152 service152 gateway152", 18),
        ["token152 prompt152", "session152", "library152", "service152", "gateway152"],
    ),
    (
        ("token152 prompt152 session152 library152 service152 gateway152", 28),
        ["token152 prompt152", "session152 library152", "service152 gateway152"],
    ),
    (
        ("prompt152 session152 library152 service152 gateway152 storage152", 6),
        ["prompt152", "session152", "library152", "service152", "gateway152", "storage152"],
    ),
    (
        ("prompt152 session152 library152 service152 gateway152 storage152", 10),
        ["prompt152", "session152", "library152", "service152", "gateway152", "storage152"],
    ),
    (
        ("prompt152 session152 library152 service152 gateway152 storage152", 18),
        ["prompt152", "session152", "library152", "service152", "gateway152", "storage152"],
    ),
    (
        ("prompt152 session152 library152 service152 gateway152 storage152", 28),
        ["prompt152 session152", "library152 service152", "gateway152 storage152"],
    ),
    (
        ("session152 library152 service152 gateway152 storage152 network152", 6),
        ["session152", "library152", "service152", "gateway152", "storage152", "network152"],
    ),
    (
        ("session152 library152 service152 gateway152 storage152 network152", 10),
        ["session152", "library152", "service152", "gateway152", "storage152", "network152"],
    ),
    (
        ("session152 library152 service152 gateway152 storage152 network152", 18),
        ["session152", "library152", "service152", "gateway152", "storage152", "network152"],
    ),
    (
        ("session152 library152 service152 gateway152 storage152 network152", 28),
        ["session152 library152", "service152 gateway152", "storage152 network152"],
    ),
    (
        ("library152 service152 gateway152 storage152 network152 latency152", 6),
        ["library152", "service152", "gateway152", "storage152", "network152", "latency152"],
    ),
    (
        ("library152 service152 gateway152 storage152 network152 latency152", 10),
        ["library152", "service152", "gateway152", "storage152", "network152", "latency152"],
    ),
    (
        ("library152 service152 gateway152 storage152 network152 latency152", 18),
        ["library152", "service152", "gateway152", "storage152", "network152", "latency152"],
    ),
    (
        ("library152 service152 gateway152 storage152 network152 latency152", 28),
        ["library152 service152", "gateway152 storage152", "network152 latency152"],
    ),
    (
        ("service152 gateway152 storage152 network152 latency152 buffer152", 6),
        ["service152", "gateway152", "storage152", "network152", "latency152", "buffer152"],
    ),
    (
        ("service152 gateway152 storage152 network152 latency152 buffer152", 10),
        ["service152", "gateway152", "storage152", "network152", "latency152", "buffer152"],
    ),
    (
        ("service152 gateway152 storage152 network152 latency152 buffer152", 18),
        ["service152", "gateway152", "storage152", "network152", "latency152", "buffer152"],
    ),
    (
        ("service152 gateway152 storage152 network152 latency152 buffer152", 28),
        ["service152 gateway152", "storage152 network152", "latency152 buffer152"],
    ),
    (
        ("gateway152 storage152 network152 latency152 buffer152 queue152", 6),
        ["gateway152", "storage152", "network152", "latency152", "buffer152", "queue152"],
    ),
    (
        ("gateway152 storage152 network152 latency152 buffer152 queue152", 10),
        ["gateway152", "storage152", "network152", "latency152", "buffer152", "queue152"],
    ),
    (
        ("gateway152 storage152 network152 latency152 buffer152 queue152", 18),
        ["gateway152", "storage152", "network152", "latency152", "buffer152 queue152"],
    ),
    (
        ("gateway152 storage152 network152 latency152 buffer152 queue152", 28),
        ["gateway152 storage152", "network152 latency152", "buffer152 queue152"],
    ),
    (
        ("storage152 network152 latency152 buffer152 queue152 worker152", 6),
        ["storage152", "network152", "latency152", "buffer152", "queue152", "worker152"],
    ),
    (
        ("storage152 network152 latency152 buffer152 queue152 worker152", 10),
        ["storage152", "network152", "latency152", "buffer152", "queue152", "worker152"],
    ),
    (
        ("storage152 network152 latency152 buffer152 queue152 worker152", 18),
        ["storage152", "network152", "latency152", "buffer152 queue152", "worker152"],
    ),
    (
        ("storage152 network152 latency152 buffer152 queue152 worker152", 28),
        ["storage152 network152", "latency152 buffer152", "queue152 worker152"],
    ),
    (
        ("network152 latency152 buffer152 queue152 worker152 kernel152", 6),
        ["network152", "latency152", "buffer152", "queue152", "worker152", "kernel152"],
    ),
    (
        ("network152 latency152 buffer152 queue152 worker152 kernel152", 10),
        ["network152", "latency152", "buffer152", "queue152", "worker152", "kernel152"],
    ),
    (
        ("network152 latency152 buffer152 queue152 worker152 kernel152", 18),
        ["network152", "latency152", "buffer152 queue152", "worker152", "kernel152"],
    ),
    (
        ("network152 latency152 buffer152 queue152 worker152 kernel152", 28),
        ["network152 latency152", "buffer152 queue152 worker152", "kernel152"],
    ),
    (
        ("latency152 buffer152 queue152 worker152 kernel152 signal152", 6),
        ["latency152", "buffer152", "queue152", "worker152", "kernel152", "signal152"],
    ),
    (
        ("latency152 buffer152 queue152 worker152 kernel152 signal152", 10),
        ["latency152", "buffer152", "queue152", "worker152", "kernel152", "signal152"],
    ),
    (
        ("latency152 buffer152 queue152 worker152 kernel152 signal152", 18),
        ["latency152", "buffer152 queue152", "worker152", "kernel152", "signal152"],
    ),
    (
        ("latency152 buffer152 queue152 worker152 kernel152 signal152", 28),
        ["latency152 buffer152", "queue152 worker152 kernel152", "signal152"],
    ),
    (
        ("buffer152 queue152 worker152 kernel152 signal152 packet152", 6),
        ["buffer152", "queue152", "worker152", "kernel152", "signal152", "packet152"],
    ),
    (
        ("buffer152 queue152 worker152 kernel152 signal152 packet152", 10),
        ["buffer152", "queue152", "worker152", "kernel152", "signal152", "packet152"],
    ),
    (
        ("buffer152 queue152 worker152 kernel152 signal152 packet152", 18),
        ["buffer152 queue152", "worker152", "kernel152", "signal152", "packet152"],
    ),
    (
        ("buffer152 queue152 worker152 kernel152 signal152 packet152", 28),
        ["buffer152 queue152 worker152", "kernel152 signal152", "packet152"],
    ),
    (
        ("queue152 worker152 kernel152 signal152 packet152 router152", 6),
        ["queue152", "worker152", "kernel152", "signal152", "packet152", "router152"],
    ),
    (
        ("queue152 worker152 kernel152 signal152 packet152 router152", 10),
        ["queue152", "worker152", "kernel152", "signal152", "packet152", "router152"],
    ),
    (
        ("queue152 worker152 kernel152 signal152 packet152 router152", 18),
        ["queue152 worker152", "kernel152", "signal152", "packet152", "router152"],
    ),
    (
        ("queue152 worker152 kernel152 signal152 packet152 router152", 28),
        ["queue152 worker152 kernel152", "signal152 packet152", "router152"],
    ),
    (
        ("worker152 kernel152 signal152 packet152 router152 cluster152", 6),
        ["worker152", "kernel152", "signal152", "packet152", "router152", "cluster152"],
    ),
    (
        ("worker152 kernel152 signal152 packet152 router152 cluster152", 10),
        ["worker152", "kernel152", "signal152", "packet152", "router152", "cluster152"],
    ),
    (
        ("worker152 kernel152 signal152 packet152 router152 cluster152", 18),
        ["worker152", "kernel152", "signal152", "packet152", "router152", "cluster152"],
    ),
    (
        ("worker152 kernel152 signal152 packet152 router152 cluster152", 28),
        ["worker152 kernel152", "signal152 packet152", "router152 cluster152"],
    ),
    (
        ("kernel152 signal152 packet152 router152 cluster152 mirror152", 6),
        ["kernel152", "signal152", "packet152", "router152", "cluster152", "mirror152"],
    ),
    (
        ("kernel152 signal152 packet152 router152 cluster152 mirror152", 10),
        ["kernel152", "signal152", "packet152", "router152", "cluster152", "mirror152"],
    ),
    (
        ("kernel152 signal152 packet152 router152 cluster152 mirror152", 18),
        ["kernel152", "signal152", "packet152", "router152", "cluster152", "mirror152"],
    ),
    (
        ("kernel152 signal152 packet152 router152 cluster152 mirror152", 28),
        ["kernel152 signal152", "packet152 router152", "cluster152 mirror152"],
    ),
    (
        ("signal152 packet152 router152 cluster152 mirror152 filter152", 6),
        ["signal152", "packet152", "router152", "cluster152", "mirror152", "filter152"],
    ),
    (
        ("signal152 packet152 router152 cluster152 mirror152 filter152", 10),
        ["signal152", "packet152", "router152", "cluster152", "mirror152", "filter152"],
    ),
    (
        ("signal152 packet152 router152 cluster152 mirror152 filter152", 18),
        ["signal152", "packet152", "router152", "cluster152", "mirror152", "filter152"],
    ),
    (
        ("signal152 packet152 router152 cluster152 mirror152 filter152", 28),
        ["signal152 packet152", "router152 cluster152", "mirror152 filter152"],
    ),
    (
        ("packet152 router152 cluster152 mirror152 filter152 ranking152", 6),
        ["packet152", "router152", "cluster152", "mirror152", "filter152", "ranking152"],
    ),
    (
        ("packet152 router152 cluster152 mirror152 filter152 ranking152", 10),
        ["packet152", "router152", "cluster152", "mirror152", "filter152", "ranking152"],
    ),
    (
        ("packet152 router152 cluster152 mirror152 filter152 ranking152", 18),
        ["packet152", "router152", "cluster152", "mirror152", "filter152", "ranking152"],
    ),
    (
        ("packet152 router152 cluster152 mirror152 filter152 ranking152", 28),
        ["packet152 router152", "cluster152 mirror152", "filter152 ranking152"],
    ),
    (
        ("router152 cluster152 mirror152 filter152 ranking152 encoding152", 6),
        ["router152", "cluster152", "mirror152", "filter152", "ranking152", "encoding152"],
    ),
    (
        ("router152 cluster152 mirror152 filter152 ranking152 encoding152", 10),
        ["router152", "cluster152", "mirror152", "filter152", "ranking152", "encoding152"],
    ),
    (
        ("router152 cluster152 mirror152 filter152 ranking152 encoding152", 18),
        ["router152", "cluster152", "mirror152", "filter152", "ranking152", "encoding152"],
    ),
    (
        ("router152 cluster152 mirror152 filter152 ranking152 encoding152", 28),
        ["router152 cluster152", "mirror152 filter152", "ranking152 encoding152"],
    ),
    (
        ("cluster152 mirror152 filter152 ranking152 encoding152 mapping152", 6),
        ["cluster152", "mirror152", "filter152", "ranking152", "encoding152", "mapping152"],
    ),
    (
        ("cluster152 mirror152 filter152 ranking152 encoding152 mapping152", 10),
        ["cluster152", "mirror152", "filter152", "ranking152", "encoding152", "mapping152"],
    ),
    (
        ("cluster152 mirror152 filter152 ranking152 encoding152 mapping152", 18),
        ["cluster152", "mirror152", "filter152", "ranking152", "encoding152", "mapping152"],
    ),
    (
        ("cluster152 mirror152 filter152 ranking152 encoding152 mapping152", 28),
        ["cluster152 mirror152", "filter152 ranking152", "encoding152 mapping152"],
    ),
    (
        ("mirror152 filter152 ranking152 encoding152 mapping152 record152", 6),
        ["mirror152", "filter152", "ranking152", "encoding152", "mapping152", "record152"],
    ),
    (
        ("mirror152 filter152 ranking152 encoding152 mapping152 record152", 10),
        ["mirror152", "filter152", "ranking152", "encoding152", "mapping152", "record152"],
    ),
    (
        ("mirror152 filter152 ranking152 encoding152 mapping152 record152", 18),
        ["mirror152", "filter152", "ranking152", "encoding152", "mapping152", "record152"],
    ),
    (
        ("mirror152 filter152 ranking152 encoding152 mapping152 record152", 28),
        ["mirror152 filter152", "ranking152 encoding152", "mapping152 record152"],
    ),
    (
        ("filter152 ranking152 encoding152 mapping152 record152 candle152", 6),
        ["filter152", "ranking152", "encoding152", "mapping152", "record152", "candle152"],
    ),
    (
        ("filter152 ranking152 encoding152 mapping152 record152 candle152", 10),
        ["filter152", "ranking152", "encoding152", "mapping152", "record152", "candle152"],
    ),
    (
        ("filter152 ranking152 encoding152 mapping152 record152 candle152", 18),
        ["filter152", "ranking152", "encoding152", "mapping152", "record152", "candle152"],
    ),
    (
        ("filter152 ranking152 encoding152 mapping152 record152 candle152", 28),
        ["filter152 ranking152", "encoding152 mapping152", "record152 candle152"],
    ),
    (
        ("ranking152 encoding152 mapping152 record152 candle152 thread152", 6),
        ["ranking152", "encoding152", "mapping152", "record152", "candle152", "thread152"],
    ),
    (
        ("ranking152 encoding152 mapping152 record152 candle152 thread152", 10),
        ["ranking152", "encoding152", "mapping152", "record152", "candle152", "thread152"],
    ),
    (
        ("ranking152 encoding152 mapping152 record152 candle152 thread152", 18),
        ["ranking152", "encoding152", "mapping152", "record152", "candle152", "thread152"],
    ),
    (
        ("ranking152 encoding152 mapping152 record152 candle152 thread152", 28),
        ["ranking152 encoding152", "mapping152 record152", "candle152 thread152"],
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
