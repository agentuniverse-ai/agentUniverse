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
        ("round 729: the quick brown fox jumps over the lazy dog", 4),
        ["round", "729:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", 8),
        ["round", "729: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", 12),
        ["round 729:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", 16),
        ["round 729: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", 24),
        ["round 729: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 729: the quick brown fox jumps over the lazy dog", 32),
        ["round 729: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", 4),
        ["round", "729:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", 8),
        ["round", "729:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", 12),
        ["round 729:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", 16),
        ["round 729:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", 24),
        ["round 729: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 729: agentuniverse is a framework for multi agents", 32),
        ["round 729: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", 4),
        ["round", "729:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", 8),
        ["round", "729:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", 12),
        ["round 729:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", 16),
        ["round 729:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", 24),
        ["round 729: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 729: knowledge stored as vectors enables retrieval", 32),
        ["round 729: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 729: the processor reads the record then stops", 4),
        ["round", "729:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 729: the processor reads the record then stops", 8),
        ["round", "729: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 729: the processor reads the record then stops", 12),
        ["round 729:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 729: the processor reads the record then stops", 16),
        ["round 729: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 729: the processor reads the record then stops", 24),
        ["round 729: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 729: the processor reads the record then stops", 32),
        ["round 729: the processor reads", "the record then stops"],
    ),
    (
        ("round 729: a worker pulls the next task from the queue", 4),
        ["round", "729:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 729: a worker pulls the next task from the queue", 8),
        ["round", "729: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 729: a worker pulls the next task from the queue", 12),
        ["round 729: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 729: a worker pulls the next task from the queue", 16),
        ["round 729: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 729: a worker pulls the next task from the queue", 24),
        ["round 729: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 729: a worker pulls the next task from the queue", 32),
        ["round 729: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 729: signals travel through the network layer", 4),
        ["round", "729:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 729: signals travel through the network layer", 8),
        ["round", "729:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 729: signals travel through the network layer", 12),
        ["round 729:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 729: signals travel through the network layer", 16),
        ["round 729:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 729: signals travel through the network layer", 24),
        ["round 729: signals", "travel through the", "network layer"],
    ),
    (
        ("round 729: signals travel through the network layer", 32),
        ["round 729: signals travel", "through the network layer"],
    ),
    (
        ("round 729: the gateway routes each request by policy", 4),
        ["round", "729:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 729: the gateway routes each request by policy", 8),
        ["round", "729: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 729: the gateway routes each request by policy", 12),
        ["round 729:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 729: the gateway routes each request by policy", 16),
        ["round 729: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 729: the gateway routes each request by policy", 24),
        ["round 729: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 729: the gateway routes each request by policy", 32),
        ["round 729: the gateway routes", "each request by policy"],
    ),
    (
        ("round 729: memory grows until the buffer is full", 4),
        ["round", "729:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 729: memory grows until the buffer is full", 8),
        ["round", "729:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 729: memory grows until the buffer is full", 12),
        ["round 729:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 729: memory grows until the buffer is full", 16),
        ["round 729:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 729: memory grows until the buffer is full", 24), ["round 729: memory grows", "until the buffer is full"]),
    (("round 729: memory grows until the buffer is full", 32), ["round 729: memory grows until", "the buffer is full"]),
    (
        ("round 729: the cluster mirrors every packet twice", 4),
        ["round", "729:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 729: the cluster mirrors every packet twice", 8),
        ["round", "729: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 729: the cluster mirrors every packet twice", 12),
        ["round 729:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 729: the cluster mirrors every packet twice", 16),
        ["round 729: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 729: the cluster mirrors every packet twice", 24),
        ["round 729: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 729: the cluster mirrors every packet twice", 32),
        ["round 729: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", 4),
        ["round", "729:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", 8),
        ["round", "729:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", 12),
        ["round 729:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", 16),
        ["round 729:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", 24),
        ["round 729: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 729: ranking uses tokens learned from the corpus", 32),
        ["round 729: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 729: a long session ends when the candle dies", 4),
        ["round", "729:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 729: a long session ends when the candle dies", 8),
        ["round", "729: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 729: a long session ends when the candle dies", 12),
        ["round 729: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 729: a long session ends when the candle dies", 16),
        ["round 729: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 729: a long session ends when the candle dies", 24),
        ["round 729: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 729: a long session ends when the candle dies", 32),
        ["round 729: a long session ends", "when the candle dies"],
    ),
    (
        ("round 729: encode the prompt then map the result", 4),
        ["round", "729:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 729: encode the prompt then map the result", 8),
        ["round", "729:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 729: encode the prompt then map the result", 12),
        ["round 729:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 729: encode the prompt then map the result", 16),
        ["round 729:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 729: encode the prompt then map the result", 24),
        ["round 729: encode the", "prompt then map the", "result"],
    ),
    (("round 729: encode the prompt then map the result", 32), ["round 729: encode the prompt", "then map the result"]),
    (
        ("round 729: the kernel wakes the worker at dawn", 4),
        ["round", "729:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 729: the kernel wakes the worker at dawn", 8),
        ["round", "729: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 729: the kernel wakes the worker at dawn", 12),
        ["round 729:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 729: the kernel wakes the worker at dawn", 16), ["round 729: the", "kernel wakes the", "worker at dawn"]),
    (("round 729: the kernel wakes the worker at dawn", 24), ["round 729: the kernel", "wakes the worker at dawn"]),
    (("round 729: the kernel wakes the worker at dawn", 32), ["round 729: the kernel wakes the", "worker at dawn"]),
    (
        ("round 729: service latency drops after the patch", 4),
        ["round", "729:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 729: service latency drops after the patch", 8),
        ["round", "729:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 729: service latency drops after the patch", 12),
        ["round 729:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 729: service latency drops after the patch", 16),
        ["round 729:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 729: service latency drops after the patch", 24),
        ["round 729: service", "latency drops after the", "patch"],
    ),
    (("round 729: service latency drops after the patch", 32), ["round 729: service latency drops", "after the patch"]),
    (
        ("round 729: the library caches every vector it sees", 4),
        ["round", "729:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 729: the library caches every vector it sees", 8),
        ["round", "729: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 729: the library caches every vector it sees", 12),
        ["round 729:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 729: the library caches every vector it sees", 16),
        ["round 729: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 729: the library caches every vector it sees", 24),
        ["round 729: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 729: the library caches every vector it sees", 32),
        ["round 729: the library caches", "every vector it sees"],
    ),
    (
        ("round 729: agents argue then the debate resolves", 4),
        ["round", "729:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 729: agents argue then the debate resolves", 8),
        ["round", "729:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 729: agents argue then the debate resolves", 12),
        ["round 729:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 729: agents argue then the debate resolves", 16),
        ["round 729:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 729: agents argue then the debate resolves", 24), ["round 729: agents argue", "then the debate resolves"]),
    (("round 729: agents argue then the debate resolves", 32), ["round 729: agents argue then the", "debate resolves"]),
    (
        ("round 729: the filter keeps only strong matches", 4),
        ["round", "729:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 729: the filter keeps only strong matches", 8),
        ["round", "729: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 729: the filter keeps only strong matches", 12),
        ["round 729:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 729: the filter keeps only strong matches", 16),
        ["round 729: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 729: the filter keeps only strong matches", 24),
        ["round 729: the filter", "keeps only strong", "matches"],
    ),
    (("round 729: the filter keeps only strong matches", 32), ["round 729: the filter keeps only", "strong matches"]),
    (
        ("round 729: the model answers with a short reply", 4),
        ["round", "729:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 729: the model answers with a short reply", 8),
        ["round", "729: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 729: the model answers with a short reply", 12),
        ["round 729:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 729: the model answers with a short reply", 16),
        ["round 729: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 729: the model answers with a short reply", 24),
        ["round 729: the model", "answers with a short", "reply"],
    ),
    (("round 729: the model answers with a short reply", 32), ["round 729: the model answers", "with a short reply"]),
    (
        ("round 729: the recorder stores the reasoning trace", 4),
        ["round", "729:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 729: the recorder stores the reasoning trace", 8),
        ["round", "729: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 729: the recorder stores the reasoning trace", 12),
        ["round 729:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 729: the recorder stores the reasoning trace", 16),
        ["round 729: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 729: the recorder stores the reasoning trace", 24),
        ["round 729: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 729: the recorder stores the reasoning trace", 32),
        ["round 729: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 729: the angel watches the processor run", 4),
        ["round", "729:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 729: the angel watches the processor run", 8),
        ["round", "729: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 729: the angel watches the processor run", 12),
        ["round 729:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 729: the angel watches the processor run", 16),
        ["round 729: the", "angel watches", "the processor", "run"],
    ),
    (("round 729: the angel watches the processor run", 24), ["round 729: the angel", "watches the processor", "run"]),
    (("round 729: the angel watches the processor run", 32), ["round 729: the angel watches the", "processor run"]),
    (
        ("round 729: angle of the vector decides the match", 4),
        ["round", "729:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 729: angle of the vector decides the match", 8),
        ["round", "729:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 729: angle of the vector decides the match", 12),
        ["round 729:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 729: angle of the vector decides the match", 16),
        ["round 729: angle", "of the vector", "decides the", "match"],
    ),
    (("round 729: angle of the vector decides the match", 24), ["round 729: angle of the", "vector decides the match"]),
    (("round 729: angle of the vector decides the match", 32), ["round 729: angle of the vector", "decides the match"]),
    (
        ("round 729: the candle burns twice as long at night", 4),
        ["round", "729:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 729: the candle burns twice as long at night", 8),
        ["round", "729: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 729: the candle burns twice as long at night", 12),
        ["round 729:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 729: the candle burns twice as long at night", 16),
        ["round 729: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 729: the candle burns twice as long at night", 24),
        ["round 729: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 729: the candle burns twice as long at night", 32),
        ["round 729: the candle burns", "twice as long at night"],
    ),
    (
        ("round 729: a mirror of the universe in one line", 4),
        ["round", "729:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 729: a mirror of the universe in one line", 8),
        ["round", "729: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 729: a mirror of the universe in one line", 12),
        ["round 729: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 729: a mirror of the universe in one line", 16),
        ["round 729: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 729: a mirror of the universe in one line", 24), ["round 729: a mirror of", "the universe in one line"]),
    (("round 729: a mirror of the universe in one line", 32), ["round 729: a mirror of the", "universe in one line"]),
    (
        ("round 729: the queue drains before the storm", 4),
        ["round", "729:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 729: the queue drains before the storm", 8),
        ["round", "729: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 729: the queue drains before the storm", 12),
        ["round 729:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 729: the queue drains before the storm", 16), ["round 729: the", "queue drains", "before the storm"]),
    (("round 729: the queue drains before the storm", 24), ["round 729: the queue", "drains before the storm"]),
    (("round 729: the queue drains before the storm", 32), ["round 729: the queue drains", "before the storm"]),
    (
        ("kitten729 sitting729 agent729 angle729 universe729 memory729", 6),
        ["kitten729", "sitting729", "agent729", "angle729", "universe729", "memory729"],
    ),
    (
        ("kitten729 sitting729 agent729 angle729 universe729 memory729", 10),
        ["kitten729", "sitting729", "agent729", "angle729", "universe729", "memory729"],
    ),
    (
        ("kitten729 sitting729 agent729 angle729 universe729 memory729", 18),
        ["kitten729", "sitting729", "agent729 angle729", "universe729", "memory729"],
    ),
    (
        ("kitten729 sitting729 agent729 angle729 universe729 memory729", 28),
        ["kitten729 sitting729", "agent729 angle729", "universe729 memory729"],
    ),
    (
        ("sitting729 agent729 angle729 universe729 memory729 stream729", 6),
        ["sitting729", "agent729", "angle729", "universe729", "memory729", "stream729"],
    ),
    (
        ("sitting729 agent729 angle729 universe729 memory729 stream729", 10),
        ["sitting729", "agent729", "angle729", "universe729", "memory729", "stream729"],
    ),
    (
        ("sitting729 agent729 angle729 universe729 memory729 stream729", 18),
        ["sitting729", "agent729 angle729", "universe729", "memory729", "stream729"],
    ),
    (
        ("sitting729 agent729 angle729 universe729 memory729 stream729", 28),
        ["sitting729 agent729 angle729", "universe729 memory729", "stream729"],
    ),
    (
        ("agent729 angle729 universe729 memory729 stream729 context729", 6),
        ["agent729", "angle729", "universe729", "memory729", "stream729", "context729"],
    ),
    (
        ("agent729 angle729 universe729 memory729 stream729 context729", 10),
        ["agent729", "angle729", "universe729", "memory729", "stream729", "context729"],
    ),
    (
        ("agent729 angle729 universe729 memory729 stream729 context729", 18),
        ["agent729 angle729", "universe729", "memory729", "stream729", "context729"],
    ),
    (
        ("agent729 angle729 universe729 memory729 stream729 context729", 28),
        ["agent729 angle729", "universe729 memory729", "stream729 context729"],
    ),
    (
        ("angle729 universe729 memory729 stream729 context729 knowledge729", 6),
        ["angle729", "universe729", "memory729", "stream729", "context729", "knowledge729"],
    ),
    (
        ("angle729 universe729 memory729 stream729 context729 knowledge729", 10),
        ["angle729", "universe729", "memory729", "stream729", "context729", "knowledge729"],
    ),
    (
        ("angle729 universe729 memory729 stream729 context729 knowledge729", 18),
        ["angle729", "universe729", "memory729", "stream729", "context729", "knowledge729"],
    ),
    (
        ("angle729 universe729 memory729 stream729 context729 knowledge729", 28),
        ["angle729 universe729", "memory729 stream729", "context729 knowledge729"],
    ),
    (
        ("universe729 memory729 stream729 context729 knowledge729 vector729", 6),
        ["universe729", "memory729", "stream729", "context729", "knowledge729", "vector729"],
    ),
    (
        ("universe729 memory729 stream729 context729 knowledge729 vector729", 10),
        ["universe729", "memory729", "stream729", "context729", "knowledge729", "vector729"],
    ),
    (
        ("universe729 memory729 stream729 context729 knowledge729 vector729", 18),
        ["universe729", "memory729", "stream729", "context729", "knowledge729", "vector729"],
    ),
    (
        ("universe729 memory729 stream729 context729 knowledge729 vector729", 28),
        ["universe729 memory729", "stream729 context729", "knowledge729 vector729"],
    ),
    (
        ("memory729 stream729 context729 knowledge729 vector729 processor729", 6),
        ["memory729", "stream729", "context729", "knowledge729", "vector729", "processor729"],
    ),
    (
        ("memory729 stream729 context729 knowledge729 vector729 processor729", 10),
        ["memory729", "stream729", "context729", "knowledge729", "vector729", "processor729"],
    ),
    (
        ("memory729 stream729 context729 knowledge729 vector729 processor729", 18),
        ["memory729", "stream729", "context729", "knowledge729", "vector729", "processor729"],
    ),
    (
        ("memory729 stream729 context729 knowledge729 vector729 processor729", 28),
        ["memory729 stream729", "context729 knowledge729", "vector729 processor729"],
    ),
    (
        ("stream729 context729 knowledge729 vector729 processor729 reasoning729", 6),
        ["stream729", "context729", "knowledge729", "vector729", "processor729", "reasoning729"],
    ),
    (
        ("stream729 context729 knowledge729 vector729 processor729 reasoning729", 10),
        ["stream729", "context729", "knowledge729", "vector729", "processor729", "reasoning729"],
    ),
    (
        ("stream729 context729 knowledge729 vector729 processor729 reasoning729", 18),
        ["stream729", "context729", "knowledge729", "vector729", "processor729", "reasoning729"],
    ),
    (
        ("stream729 context729 knowledge729 vector729 processor729 reasoning729", 28),
        ["stream729 context729", "knowledge729 vector729", "processor729 reasoning729"],
    ),
    (
        ("context729 knowledge729 vector729 processor729 reasoning729 machine729", 6),
        ["context729", "knowledge729", "vector729", "processor729", "reasoning729", "machine729"],
    ),
    (
        ("context729 knowledge729 vector729 processor729 reasoning729 machine729", 10),
        ["context729", "knowledge729", "vector729", "processor729", "reasoning729", "machine729"],
    ),
    (
        ("context729 knowledge729 vector729 processor729 reasoning729 machine729", 18),
        ["context729", "knowledge729", "vector729", "processor729", "reasoning729", "machine729"],
    ),
    (
        ("context729 knowledge729 vector729 processor729 reasoning729 machine729", 28),
        ["context729 knowledge729", "vector729 processor729", "reasoning729 machine729"],
    ),
    (
        ("knowledge729 vector729 processor729 reasoning729 machine729 learning729", 6),
        ["knowledge729", "vector729", "processor729", "reasoning729", "machine729", "learning729"],
    ),
    (
        ("knowledge729 vector729 processor729 reasoning729 machine729 learning729", 10),
        ["knowledge729", "vector729", "processor729", "reasoning729", "machine729", "learning729"],
    ),
    (
        ("knowledge729 vector729 processor729 reasoning729 machine729 learning729", 18),
        ["knowledge729", "vector729", "processor729", "reasoning729", "machine729", "learning729"],
    ),
    (
        ("knowledge729 vector729 processor729 reasoning729 machine729 learning729", 28),
        ["knowledge729 vector729", "processor729 reasoning729", "machine729 learning729"],
    ),
    (
        ("vector729 processor729 reasoning729 machine729 learning729 model729", 6),
        ["vector729", "processor729", "reasoning729", "machine729", "learning729", "model729"],
    ),
    (
        ("vector729 processor729 reasoning729 machine729 learning729 model729", 10),
        ["vector729", "processor729", "reasoning729", "machine729", "learning729", "model729"],
    ),
    (
        ("vector729 processor729 reasoning729 machine729 learning729 model729", 18),
        ["vector729", "processor729", "reasoning729", "machine729", "learning729", "model729"],
    ),
    (
        ("vector729 processor729 reasoning729 machine729 learning729 model729", 28),
        ["vector729 processor729", "reasoning729 machine729", "learning729 model729"],
    ),
    (
        ("processor729 reasoning729 machine729 learning729 model729 token729", 6),
        ["processor729", "reasoning729", "machine729", "learning729", "model729", "token729"],
    ),
    (
        ("processor729 reasoning729 machine729 learning729 model729 token729", 10),
        ["processor729", "reasoning729", "machine729", "learning729", "model729", "token729"],
    ),
    (
        ("processor729 reasoning729 machine729 learning729 model729 token729", 18),
        ["processor729", "reasoning729", "machine729", "learning729", "model729 token729"],
    ),
    (
        ("processor729 reasoning729 machine729 learning729 model729 token729", 28),
        ["processor729 reasoning729", "machine729 learning729", "model729 token729"],
    ),
    (
        ("reasoning729 machine729 learning729 model729 token729 prompt729", 6),
        ["reasoning729", "machine729", "learning729", "model729", "token729", "prompt729"],
    ),
    (
        ("reasoning729 machine729 learning729 model729 token729 prompt729", 10),
        ["reasoning729", "machine729", "learning729", "model729", "token729", "prompt729"],
    ),
    (
        ("reasoning729 machine729 learning729 model729 token729 prompt729", 18),
        ["reasoning729", "machine729", "learning729", "model729 token729", "prompt729"],
    ),
    (
        ("reasoning729 machine729 learning729 model729 token729 prompt729", 28),
        ["reasoning729 machine729", "learning729 model729", "token729 prompt729"],
    ),
    (
        ("machine729 learning729 model729 token729 prompt729 session729", 6),
        ["machine729", "learning729", "model729", "token729", "prompt729", "session729"],
    ),
    (
        ("machine729 learning729 model729 token729 prompt729 session729", 10),
        ["machine729", "learning729", "model729", "token729", "prompt729", "session729"],
    ),
    (
        ("machine729 learning729 model729 token729 prompt729 session729", 18),
        ["machine729", "learning729", "model729 token729", "prompt729", "session729"],
    ),
    (
        ("machine729 learning729 model729 token729 prompt729 session729", 28),
        ["machine729 learning729", "model729 token729 prompt729", "session729"],
    ),
    (
        ("learning729 model729 token729 prompt729 session729 library729", 6),
        ["learning729", "model729", "token729", "prompt729", "session729", "library729"],
    ),
    (
        ("learning729 model729 token729 prompt729 session729 library729", 10),
        ["learning729", "model729", "token729", "prompt729", "session729", "library729"],
    ),
    (
        ("learning729 model729 token729 prompt729 session729 library729", 18),
        ["learning729", "model729 token729", "prompt729", "session729", "library729"],
    ),
    (
        ("learning729 model729 token729 prompt729 session729 library729", 28),
        ["learning729 model729", "token729 prompt729", "session729 library729"],
    ),
    (
        ("model729 token729 prompt729 session729 library729 service729", 6),
        ["model729", "token729", "prompt729", "session729", "library729", "service729"],
    ),
    (
        ("model729 token729 prompt729 session729 library729 service729", 10),
        ["model729", "token729", "prompt729", "session729", "library729", "service729"],
    ),
    (
        ("model729 token729 prompt729 session729 library729 service729", 18),
        ["model729 token729", "prompt729", "session729", "library729", "service729"],
    ),
    (
        ("model729 token729 prompt729 session729 library729 service729", 28),
        ["model729 token729 prompt729", "session729 library729", "service729"],
    ),
    (
        ("token729 prompt729 session729 library729 service729 gateway729", 6),
        ["token729", "prompt729", "session729", "library729", "service729", "gateway729"],
    ),
    (
        ("token729 prompt729 session729 library729 service729 gateway729", 10),
        ["token729", "prompt729", "session729", "library729", "service729", "gateway729"],
    ),
    (
        ("token729 prompt729 session729 library729 service729 gateway729", 18),
        ["token729 prompt729", "session729", "library729", "service729", "gateway729"],
    ),
    (
        ("token729 prompt729 session729 library729 service729 gateway729", 28),
        ["token729 prompt729", "session729 library729", "service729 gateway729"],
    ),
    (
        ("prompt729 session729 library729 service729 gateway729 storage729", 6),
        ["prompt729", "session729", "library729", "service729", "gateway729", "storage729"],
    ),
    (
        ("prompt729 session729 library729 service729 gateway729 storage729", 10),
        ["prompt729", "session729", "library729", "service729", "gateway729", "storage729"],
    ),
    (
        ("prompt729 session729 library729 service729 gateway729 storage729", 18),
        ["prompt729", "session729", "library729", "service729", "gateway729", "storage729"],
    ),
    (
        ("prompt729 session729 library729 service729 gateway729 storage729", 28),
        ["prompt729 session729", "library729 service729", "gateway729 storage729"],
    ),
    (
        ("session729 library729 service729 gateway729 storage729 network729", 6),
        ["session729", "library729", "service729", "gateway729", "storage729", "network729"],
    ),
    (
        ("session729 library729 service729 gateway729 storage729 network729", 10),
        ["session729", "library729", "service729", "gateway729", "storage729", "network729"],
    ),
    (
        ("session729 library729 service729 gateway729 storage729 network729", 18),
        ["session729", "library729", "service729", "gateway729", "storage729", "network729"],
    ),
    (
        ("session729 library729 service729 gateway729 storage729 network729", 28),
        ["session729 library729", "service729 gateway729", "storage729 network729"],
    ),
    (
        ("library729 service729 gateway729 storage729 network729 latency729", 6),
        ["library729", "service729", "gateway729", "storage729", "network729", "latency729"],
    ),
    (
        ("library729 service729 gateway729 storage729 network729 latency729", 10),
        ["library729", "service729", "gateway729", "storage729", "network729", "latency729"],
    ),
    (
        ("library729 service729 gateway729 storage729 network729 latency729", 18),
        ["library729", "service729", "gateway729", "storage729", "network729", "latency729"],
    ),
    (
        ("library729 service729 gateway729 storage729 network729 latency729", 28),
        ["library729 service729", "gateway729 storage729", "network729 latency729"],
    ),
    (
        ("service729 gateway729 storage729 network729 latency729 buffer729", 6),
        ["service729", "gateway729", "storage729", "network729", "latency729", "buffer729"],
    ),
    (
        ("service729 gateway729 storage729 network729 latency729 buffer729", 10),
        ["service729", "gateway729", "storage729", "network729", "latency729", "buffer729"],
    ),
    (
        ("service729 gateway729 storage729 network729 latency729 buffer729", 18),
        ["service729", "gateway729", "storage729", "network729", "latency729", "buffer729"],
    ),
    (
        ("service729 gateway729 storage729 network729 latency729 buffer729", 28),
        ["service729 gateway729", "storage729 network729", "latency729 buffer729"],
    ),
    (
        ("gateway729 storage729 network729 latency729 buffer729 queue729", 6),
        ["gateway729", "storage729", "network729", "latency729", "buffer729", "queue729"],
    ),
    (
        ("gateway729 storage729 network729 latency729 buffer729 queue729", 10),
        ["gateway729", "storage729", "network729", "latency729", "buffer729", "queue729"],
    ),
    (
        ("gateway729 storage729 network729 latency729 buffer729 queue729", 18),
        ["gateway729", "storage729", "network729", "latency729", "buffer729 queue729"],
    ),
    (
        ("gateway729 storage729 network729 latency729 buffer729 queue729", 28),
        ["gateway729 storage729", "network729 latency729", "buffer729 queue729"],
    ),
    (
        ("storage729 network729 latency729 buffer729 queue729 worker729", 6),
        ["storage729", "network729", "latency729", "buffer729", "queue729", "worker729"],
    ),
    (
        ("storage729 network729 latency729 buffer729 queue729 worker729", 10),
        ["storage729", "network729", "latency729", "buffer729", "queue729", "worker729"],
    ),
    (
        ("storage729 network729 latency729 buffer729 queue729 worker729", 18),
        ["storage729", "network729", "latency729", "buffer729 queue729", "worker729"],
    ),
    (
        ("storage729 network729 latency729 buffer729 queue729 worker729", 28),
        ["storage729 network729", "latency729 buffer729", "queue729 worker729"],
    ),
    (
        ("network729 latency729 buffer729 queue729 worker729 kernel729", 6),
        ["network729", "latency729", "buffer729", "queue729", "worker729", "kernel729"],
    ),
    (
        ("network729 latency729 buffer729 queue729 worker729 kernel729", 10),
        ["network729", "latency729", "buffer729", "queue729", "worker729", "kernel729"],
    ),
    (
        ("network729 latency729 buffer729 queue729 worker729 kernel729", 18),
        ["network729", "latency729", "buffer729 queue729", "worker729", "kernel729"],
    ),
    (
        ("network729 latency729 buffer729 queue729 worker729 kernel729", 28),
        ["network729 latency729", "buffer729 queue729 worker729", "kernel729"],
    ),
    (
        ("latency729 buffer729 queue729 worker729 kernel729 signal729", 6),
        ["latency729", "buffer729", "queue729", "worker729", "kernel729", "signal729"],
    ),
    (
        ("latency729 buffer729 queue729 worker729 kernel729 signal729", 10),
        ["latency729", "buffer729", "queue729", "worker729", "kernel729", "signal729"],
    ),
    (
        ("latency729 buffer729 queue729 worker729 kernel729 signal729", 18),
        ["latency729", "buffer729 queue729", "worker729", "kernel729", "signal729"],
    ),
    (
        ("latency729 buffer729 queue729 worker729 kernel729 signal729", 28),
        ["latency729 buffer729", "queue729 worker729 kernel729", "signal729"],
    ),
    (
        ("buffer729 queue729 worker729 kernel729 signal729 packet729", 6),
        ["buffer729", "queue729", "worker729", "kernel729", "signal729", "packet729"],
    ),
    (
        ("buffer729 queue729 worker729 kernel729 signal729 packet729", 10),
        ["buffer729", "queue729", "worker729", "kernel729", "signal729", "packet729"],
    ),
    (
        ("buffer729 queue729 worker729 kernel729 signal729 packet729", 18),
        ["buffer729 queue729", "worker729", "kernel729", "signal729", "packet729"],
    ),
    (
        ("buffer729 queue729 worker729 kernel729 signal729 packet729", 28),
        ["buffer729 queue729 worker729", "kernel729 signal729", "packet729"],
    ),
    (
        ("queue729 worker729 kernel729 signal729 packet729 router729", 6),
        ["queue729", "worker729", "kernel729", "signal729", "packet729", "router729"],
    ),
    (
        ("queue729 worker729 kernel729 signal729 packet729 router729", 10),
        ["queue729", "worker729", "kernel729", "signal729", "packet729", "router729"],
    ),
    (
        ("queue729 worker729 kernel729 signal729 packet729 router729", 18),
        ["queue729 worker729", "kernel729", "signal729", "packet729", "router729"],
    ),
    (
        ("queue729 worker729 kernel729 signal729 packet729 router729", 28),
        ["queue729 worker729 kernel729", "signal729 packet729", "router729"],
    ),
    (
        ("worker729 kernel729 signal729 packet729 router729 cluster729", 6),
        ["worker729", "kernel729", "signal729", "packet729", "router729", "cluster729"],
    ),
    (
        ("worker729 kernel729 signal729 packet729 router729 cluster729", 10),
        ["worker729", "kernel729", "signal729", "packet729", "router729", "cluster729"],
    ),
    (
        ("worker729 kernel729 signal729 packet729 router729 cluster729", 18),
        ["worker729", "kernel729", "signal729", "packet729", "router729", "cluster729"],
    ),
    (
        ("worker729 kernel729 signal729 packet729 router729 cluster729", 28),
        ["worker729 kernel729", "signal729 packet729", "router729 cluster729"],
    ),
    (
        ("kernel729 signal729 packet729 router729 cluster729 mirror729", 6),
        ["kernel729", "signal729", "packet729", "router729", "cluster729", "mirror729"],
    ),
    (
        ("kernel729 signal729 packet729 router729 cluster729 mirror729", 10),
        ["kernel729", "signal729", "packet729", "router729", "cluster729", "mirror729"],
    ),
    (
        ("kernel729 signal729 packet729 router729 cluster729 mirror729", 18),
        ["kernel729", "signal729", "packet729", "router729", "cluster729", "mirror729"],
    ),
    (
        ("kernel729 signal729 packet729 router729 cluster729 mirror729", 28),
        ["kernel729 signal729", "packet729 router729", "cluster729 mirror729"],
    ),
    (
        ("signal729 packet729 router729 cluster729 mirror729 filter729", 6),
        ["signal729", "packet729", "router729", "cluster729", "mirror729", "filter729"],
    ),
    (
        ("signal729 packet729 router729 cluster729 mirror729 filter729", 10),
        ["signal729", "packet729", "router729", "cluster729", "mirror729", "filter729"],
    ),
    (
        ("signal729 packet729 router729 cluster729 mirror729 filter729", 18),
        ["signal729", "packet729", "router729", "cluster729", "mirror729", "filter729"],
    ),
    (
        ("signal729 packet729 router729 cluster729 mirror729 filter729", 28),
        ["signal729 packet729", "router729 cluster729", "mirror729 filter729"],
    ),
    (
        ("packet729 router729 cluster729 mirror729 filter729 ranking729", 6),
        ["packet729", "router729", "cluster729", "mirror729", "filter729", "ranking729"],
    ),
    (
        ("packet729 router729 cluster729 mirror729 filter729 ranking729", 10),
        ["packet729", "router729", "cluster729", "mirror729", "filter729", "ranking729"],
    ),
    (
        ("packet729 router729 cluster729 mirror729 filter729 ranking729", 18),
        ["packet729", "router729", "cluster729", "mirror729", "filter729", "ranking729"],
    ),
    (
        ("packet729 router729 cluster729 mirror729 filter729 ranking729", 28),
        ["packet729 router729", "cluster729 mirror729", "filter729 ranking729"],
    ),
    (
        ("router729 cluster729 mirror729 filter729 ranking729 encoding729", 6),
        ["router729", "cluster729", "mirror729", "filter729", "ranking729", "encoding729"],
    ),
    (
        ("router729 cluster729 mirror729 filter729 ranking729 encoding729", 10),
        ["router729", "cluster729", "mirror729", "filter729", "ranking729", "encoding729"],
    ),
    (
        ("router729 cluster729 mirror729 filter729 ranking729 encoding729", 18),
        ["router729", "cluster729", "mirror729", "filter729", "ranking729", "encoding729"],
    ),
    (
        ("router729 cluster729 mirror729 filter729 ranking729 encoding729", 28),
        ["router729 cluster729", "mirror729 filter729", "ranking729 encoding729"],
    ),
    (
        ("cluster729 mirror729 filter729 ranking729 encoding729 mapping729", 6),
        ["cluster729", "mirror729", "filter729", "ranking729", "encoding729", "mapping729"],
    ),
    (
        ("cluster729 mirror729 filter729 ranking729 encoding729 mapping729", 10),
        ["cluster729", "mirror729", "filter729", "ranking729", "encoding729", "mapping729"],
    ),
    (
        ("cluster729 mirror729 filter729 ranking729 encoding729 mapping729", 18),
        ["cluster729", "mirror729", "filter729", "ranking729", "encoding729", "mapping729"],
    ),
    (
        ("cluster729 mirror729 filter729 ranking729 encoding729 mapping729", 28),
        ["cluster729 mirror729", "filter729 ranking729", "encoding729 mapping729"],
    ),
    (
        ("mirror729 filter729 ranking729 encoding729 mapping729 record729", 6),
        ["mirror729", "filter729", "ranking729", "encoding729", "mapping729", "record729"],
    ),
    (
        ("mirror729 filter729 ranking729 encoding729 mapping729 record729", 10),
        ["mirror729", "filter729", "ranking729", "encoding729", "mapping729", "record729"],
    ),
    (
        ("mirror729 filter729 ranking729 encoding729 mapping729 record729", 18),
        ["mirror729", "filter729", "ranking729", "encoding729", "mapping729", "record729"],
    ),
    (
        ("mirror729 filter729 ranking729 encoding729 mapping729 record729", 28),
        ["mirror729 filter729", "ranking729 encoding729", "mapping729 record729"],
    ),
    (
        ("filter729 ranking729 encoding729 mapping729 record729 candle729", 6),
        ["filter729", "ranking729", "encoding729", "mapping729", "record729", "candle729"],
    ),
    (
        ("filter729 ranking729 encoding729 mapping729 record729 candle729", 10),
        ["filter729", "ranking729", "encoding729", "mapping729", "record729", "candle729"],
    ),
    (
        ("filter729 ranking729 encoding729 mapping729 record729 candle729", 18),
        ["filter729", "ranking729", "encoding729", "mapping729", "record729", "candle729"],
    ),
    (
        ("filter729 ranking729 encoding729 mapping729 record729 candle729", 28),
        ["filter729 ranking729", "encoding729 mapping729", "record729 candle729"],
    ),
    (
        ("ranking729 encoding729 mapping729 record729 candle729 thread729", 6),
        ["ranking729", "encoding729", "mapping729", "record729", "candle729", "thread729"],
    ),
    (
        ("ranking729 encoding729 mapping729 record729 candle729 thread729", 10),
        ["ranking729", "encoding729", "mapping729", "record729", "candle729", "thread729"],
    ),
    (
        ("ranking729 encoding729 mapping729 record729 candle729 thread729", 18),
        ["ranking729", "encoding729", "mapping729", "record729", "candle729", "thread729"],
    ),
    (
        ("ranking729 encoding729 mapping729 record729 candle729 thread729", 28),
        ["ranking729 encoding729", "mapping729 record729", "candle729 thread729"],
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
