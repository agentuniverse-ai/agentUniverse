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
        ("round 70: the quick brown fox jumps over the lazy dog", 4),
        ["round", "70:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 70: the quick brown fox jumps over the lazy dog", 8),
        ["round", "70: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 70: the quick brown fox jumps over the lazy dog", 12),
        ["round 70:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 70: the quick brown fox jumps over the lazy dog", 16),
        ["round 70: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 70: the quick brown fox jumps over the lazy dog", 24),
        ["round 70: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 70: the quick brown fox jumps over the lazy dog", 32),
        ["round 70: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 70: agentuniverse is a framework for multi agents", 4),
        ["round", "70:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 70: agentuniverse is a framework for multi agents", 8),
        ["round", "70:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 70: agentuniverse is a framework for multi agents", 12),
        ["round 70:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 70: agentuniverse is a framework for multi agents", 16),
        ["round 70:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 70: agentuniverse is a framework for multi agents", 24),
        ["round 70: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 70: agentuniverse is a framework for multi agents", 32),
        ["round 70: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 70: knowledge stored as vectors enables retrieval", 4),
        ["round", "70:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 70: knowledge stored as vectors enables retrieval", 8),
        ["round", "70:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 70: knowledge stored as vectors enables retrieval", 12),
        ["round 70:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 70: knowledge stored as vectors enables retrieval", 16),
        ["round 70:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 70: knowledge stored as vectors enables retrieval", 24),
        ["round 70: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 70: knowledge stored as vectors enables retrieval", 32),
        ["round 70: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 70: the processor reads the record then stops", 4),
        ["round", "70:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 70: the processor reads the record then stops", 8),
        ["round", "70: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 70: the processor reads the record then stops", 12),
        ["round 70:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 70: the processor reads the record then stops", 16),
        ["round 70: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 70: the processor reads the record then stops", 24),
        ["round 70: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 70: the processor reads the record then stops", 32),
        ["round 70: the processor reads", "the record then stops"],
    ),
    (
        ("round 70: a worker pulls the next task from the queue", 4),
        ["round", "70:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 70: a worker pulls the next task from the queue", 8),
        ["round", "70: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 70: a worker pulls the next task from the queue", 12),
        ["round 70: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 70: a worker pulls the next task from the queue", 16),
        ["round 70: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 70: a worker pulls the next task from the queue", 24),
        ["round 70: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 70: a worker pulls the next task from the queue", 32),
        ["round 70: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 70: signals travel through the network layer", 4),
        ["round", "70:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 70: signals travel through the network layer", 8),
        ["round", "70:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 70: signals travel through the network layer", 12),
        ["round 70:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 70: signals travel through the network layer", 16),
        ["round 70:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 70: signals travel through the network layer", 24),
        ["round 70: signals travel", "through the network", "layer"],
    ),
    (
        ("round 70: signals travel through the network layer", 32),
        ["round 70: signals travel through", "the network layer"],
    ),
    (
        ("round 70: the gateway routes each request by policy", 4),
        ["round", "70:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 70: the gateway routes each request by policy", 8),
        ["round", "70: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 70: the gateway routes each request by policy", 12),
        ["round 70:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 70: the gateway routes each request by policy", 16),
        ["round 70: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 70: the gateway routes each request by policy", 24),
        ["round 70: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 70: the gateway routes each request by policy", 32),
        ["round 70: the gateway routes", "each request by policy"],
    ),
    (
        ("round 70: memory grows until the buffer is full", 4),
        ["round", "70:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 70: memory grows until the buffer is full", 8),
        ["round", "70:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 70: memory grows until the buffer is full", 12),
        ["round 70:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 70: memory grows until the buffer is full", 16),
        ["round 70: memory", "grows until the", "buffer is full"],
    ),
    (("round 70: memory grows until the buffer is full", 24), ["round 70: memory grows", "until the buffer is full"]),
    (("round 70: memory grows until the buffer is full", 32), ["round 70: memory grows until the", "buffer is full"]),
    (
        ("round 70: the cluster mirrors every packet twice", 4),
        ["round", "70:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 70: the cluster mirrors every packet twice", 8),
        ["round", "70: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 70: the cluster mirrors every packet twice", 12),
        ["round 70:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 70: the cluster mirrors every packet twice", 16),
        ["round 70: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 70: the cluster mirrors every packet twice", 24),
        ["round 70: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 70: the cluster mirrors every packet twice", 32), ["round 70: the cluster mirrors", "every packet twice"]),
    (
        ("round 70: ranking uses tokens learned from the corpus", 4),
        ["round", "70:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 70: ranking uses tokens learned from the corpus", 8),
        ["round", "70:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 70: ranking uses tokens learned from the corpus", 12),
        ["round 70:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 70: ranking uses tokens learned from the corpus", 16),
        ["round 70:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 70: ranking uses tokens learned from the corpus", 24),
        ["round 70: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 70: ranking uses tokens learned from the corpus", 32),
        ["round 70: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 70: a long session ends when the candle dies", 4),
        ["round", "70:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 70: a long session ends when the candle dies", 8),
        ["round", "70: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 70: a long session ends when the candle dies", 12),
        ["round 70: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 70: a long session ends when the candle dies", 16),
        ["round 70: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 70: a long session ends when the candle dies", 24),
        ["round 70: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 70: a long session ends when the candle dies", 32),
        ["round 70: a long session ends", "when the candle dies"],
    ),
    (
        ("round 70: encode the prompt then map the result", 4),
        ["round", "70:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 70: encode the prompt then map the result", 8),
        ["round", "70:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 70: encode the prompt then map the result", 12),
        ["round 70:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 70: encode the prompt then map the result", 16),
        ["round 70: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 70: encode the prompt then map the result", 24),
        ["round 70: encode the", "prompt then map the", "result"],
    ),
    (("round 70: encode the prompt then map the result", 32), ["round 70: encode the prompt then", "map the result"]),
    (
        ("round 70: the kernel wakes the worker at dawn", 4),
        ["round", "70:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 70: the kernel wakes the worker at dawn", 8),
        ["round", "70: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 70: the kernel wakes the worker at dawn", 12),
        ["round 70:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 70: the kernel wakes the worker at dawn", 16), ["round 70: the", "kernel wakes the", "worker at dawn"]),
    (("round 70: the kernel wakes the worker at dawn", 24), ["round 70: the kernel", "wakes the worker at dawn"]),
    (("round 70: the kernel wakes the worker at dawn", 32), ["round 70: the kernel wakes the", "worker at dawn"]),
    (
        ("round 70: service latency drops after the patch", 4),
        ["round", "70:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 70: service latency drops after the patch", 8),
        ["round", "70:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 70: service latency drops after the patch", 12),
        ["round 70:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 70: service latency drops after the patch", 16),
        ["round 70:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 70: service latency drops after the patch", 24),
        ["round 70: service", "latency drops after the", "patch"],
    ),
    (("round 70: service latency drops after the patch", 32), ["round 70: service latency drops", "after the patch"]),
    (
        ("round 70: the library caches every vector it sees", 4),
        ["round", "70:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 70: the library caches every vector it sees", 8),
        ["round", "70: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 70: the library caches every vector it sees", 12),
        ["round 70:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 70: the library caches every vector it sees", 16),
        ["round 70: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 70: the library caches every vector it sees", 24),
        ["round 70: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 70: the library caches every vector it sees", 32),
        ["round 70: the library caches", "every vector it sees"],
    ),
    (
        ("round 70: agents argue then the debate resolves", 4),
        ["round", "70:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 70: agents argue then the debate resolves", 8),
        ["round", "70:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 70: agents argue then the debate resolves", 12),
        ["round 70:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 70: agents argue then the debate resolves", 16),
        ["round 70: agents", "argue then the", "debate resolves"],
    ),
    (("round 70: agents argue then the debate resolves", 24), ["round 70: agents argue", "then the debate resolves"]),
    (("round 70: agents argue then the debate resolves", 32), ["round 70: agents argue then the", "debate resolves"]),
    (
        ("round 70: the filter keeps only strong matches", 4),
        ["round", "70:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 70: the filter keeps only strong matches", 8),
        ["round", "70: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 70: the filter keeps only strong matches", 12),
        ["round 70:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 70: the filter keeps only strong matches", 16),
        ["round 70: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 70: the filter keeps only strong matches", 24), ["round 70: the filter", "keeps only strong", "matches"]),
    (("round 70: the filter keeps only strong matches", 32), ["round 70: the filter keeps only", "strong matches"]),
    (
        ("round 70: the model answers with a short reply", 4),
        ["round", "70:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 70: the model answers with a short reply", 8),
        ["round", "70: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 70: the model answers with a short reply", 12),
        ["round 70:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 70: the model answers with a short reply", 16),
        ["round 70: the", "model answers", "with a short", "reply"],
    ),
    (("round 70: the model answers with a short reply", 24), ["round 70: the model", "answers with a short", "reply"]),
    (("round 70: the model answers with a short reply", 32), ["round 70: the model answers with", "a short reply"]),
    (
        ("round 70: the recorder stores the reasoning trace", 4),
        ["round", "70:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 70: the recorder stores the reasoning trace", 8),
        ["round", "70: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 70: the recorder stores the reasoning trace", 12),
        ["round 70:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 70: the recorder stores the reasoning trace", 16),
        ["round 70: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 70: the recorder stores the reasoning trace", 24),
        ["round 70: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 70: the recorder stores the reasoning trace", 32),
        ["round 70: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 70: the angel watches the processor run", 4),
        ["round", "70:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 70: the angel watches the processor run", 8),
        ["round", "70: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 70: the angel watches the processor run", 12),
        ["round 70:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 70: the angel watches the processor run", 16), ["round 70: the", "angel watches", "the processor", "run"]),
    (("round 70: the angel watches the processor run", 24), ["round 70: the angel", "watches the processor", "run"]),
    (("round 70: the angel watches the processor run", 32), ["round 70: the angel watches the", "processor run"]),
    (
        ("round 70: angle of the vector decides the match", 4),
        ["round", "70:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 70: angle of the vector decides the match", 8),
        ["round", "70:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 70: angle of the vector decides the match", 12),
        ["round 70:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 70: angle of the vector decides the match", 16),
        ["round 70: angle", "of the vector", "decides the", "match"],
    ),
    (("round 70: angle of the vector decides the match", 24), ["round 70: angle of the", "vector decides the match"]),
    (("round 70: angle of the vector decides the match", 32), ["round 70: angle of the vector", "decides the match"]),
    (
        ("round 70: the candle burns twice as long at night", 4),
        ["round", "70:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 70: the candle burns twice as long at night", 8),
        ["round", "70: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 70: the candle burns twice as long at night", 12),
        ["round 70:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 70: the candle burns twice as long at night", 16),
        ["round 70: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 70: the candle burns twice as long at night", 24),
        ["round 70: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 70: the candle burns twice as long at night", 32),
        ["round 70: the candle burns twice", "as long at night"],
    ),
    (
        ("round 70: a mirror of the universe in one line", 4),
        ["round", "70:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 70: a mirror of the universe in one line", 8),
        ["round", "70: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 70: a mirror of the universe in one line", 12),
        ["round 70: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 70: a mirror of the universe in one line", 16),
        ["round 70: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 70: a mirror of the universe in one line", 24), ["round 70: a mirror of", "the universe in one line"]),
    (("round 70: a mirror of the universe in one line", 32), ["round 70: a mirror of the", "universe in one line"]),
    (
        ("round 70: the queue drains before the storm", 4),
        ["round", "70:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 70: the queue drains before the storm", 8),
        ["round", "70: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 70: the queue drains before the storm", 12), ["round 70:", "the queue", "drains", "before the", "storm"]),
    (("round 70: the queue drains before the storm", 16), ["round 70: the", "queue drains", "before the storm"]),
    (("round 70: the queue drains before the storm", 24), ["round 70: the queue", "drains before the storm"]),
    (("round 70: the queue drains before the storm", 32), ["round 70: the queue drains", "before the storm"]),
    (
        ("kitten70 sitting70 agent70 angle70 universe70 memory70", 6),
        ["kitten70", "sitting70", "agent70", "angle70", "universe70", "memory70"],
    ),
    (
        ("kitten70 sitting70 agent70 angle70 universe70 memory70", 10),
        ["kitten70", "sitting70", "agent70", "angle70", "universe70", "memory70"],
    ),
    (
        ("kitten70 sitting70 agent70 angle70 universe70 memory70", 18),
        ["kitten70 sitting70", "agent70 angle70", "universe70", "memory70"],
    ),
    (
        ("kitten70 sitting70 agent70 angle70 universe70 memory70", 28),
        ["kitten70 sitting70 agent70", "angle70 universe70 memory70"],
    ),
    (
        ("sitting70 agent70 angle70 universe70 memory70 stream70", 6),
        ["sitting70", "agent70", "angle70", "universe70", "memory70", "stream70"],
    ),
    (
        ("sitting70 agent70 angle70 universe70 memory70 stream70", 10),
        ["sitting70", "agent70", "angle70", "universe70", "memory70", "stream70"],
    ),
    (
        ("sitting70 agent70 angle70 universe70 memory70 stream70", 18),
        ["sitting70 agent70", "angle70 universe70", "memory70 stream70"],
    ),
    (
        ("sitting70 agent70 angle70 universe70 memory70 stream70", 28),
        ["sitting70 agent70 angle70", "universe70 memory70 stream70"],
    ),
    (
        ("agent70 angle70 universe70 memory70 stream70 context70", 6),
        ["agent70", "angle70", "universe70", "memory70", "stream70", "context70"],
    ),
    (
        ("agent70 angle70 universe70 memory70 stream70 context70", 10),
        ["agent70", "angle70", "universe70", "memory70", "stream70", "context70"],
    ),
    (
        ("agent70 angle70 universe70 memory70 stream70 context70", 18),
        ["agent70 angle70", "universe70", "memory70 stream70", "context70"],
    ),
    (
        ("agent70 angle70 universe70 memory70 stream70 context70", 28),
        ["agent70 angle70 universe70", "memory70 stream70 context70"],
    ),
    (
        ("angle70 universe70 memory70 stream70 context70 knowledge70", 6),
        ["angle70", "universe70", "memory70", "stream70", "context70", "knowledge70"],
    ),
    (
        ("angle70 universe70 memory70 stream70 context70 knowledge70", 10),
        ["angle70", "universe70", "memory70", "stream70", "context70", "knowledge70"],
    ),
    (
        ("angle70 universe70 memory70 stream70 context70 knowledge70", 18),
        ["angle70 universe70", "memory70 stream70", "context70", "knowledge70"],
    ),
    (
        ("angle70 universe70 memory70 stream70 context70 knowledge70", 28),
        ["angle70 universe70 memory70", "stream70 context70", "knowledge70"],
    ),
    (
        ("universe70 memory70 stream70 context70 knowledge70 vector70", 6),
        ["universe70", "memory70", "stream70", "context70", "knowledge70", "vector70"],
    ),
    (
        ("universe70 memory70 stream70 context70 knowledge70 vector70", 10),
        ["universe70", "memory70", "stream70", "context70", "knowledge70", "vector70"],
    ),
    (
        ("universe70 memory70 stream70 context70 knowledge70 vector70", 18),
        ["universe70", "memory70 stream70", "context70", "knowledge70", "vector70"],
    ),
    (
        ("universe70 memory70 stream70 context70 knowledge70 vector70", 28),
        ["universe70 memory70 stream70", "context70 knowledge70", "vector70"],
    ),
    (
        ("memory70 stream70 context70 knowledge70 vector70 processor70", 6),
        ["memory70", "stream70", "context70", "knowledge70", "vector70", "processor70"],
    ),
    (
        ("memory70 stream70 context70 knowledge70 vector70 processor70", 10),
        ["memory70", "stream70", "context70", "knowledge70", "vector70", "processor70"],
    ),
    (
        ("memory70 stream70 context70 knowledge70 vector70 processor70", 18),
        ["memory70 stream70", "context70", "knowledge70", "vector70", "processor70"],
    ),
    (
        ("memory70 stream70 context70 knowledge70 vector70 processor70", 28),
        ["memory70 stream70 context70", "knowledge70 vector70", "processor70"],
    ),
    (
        ("stream70 context70 knowledge70 vector70 processor70 reasoning70", 6),
        ["stream70", "context70", "knowledge70", "vector70", "processor70", "reasoning70"],
    ),
    (
        ("stream70 context70 knowledge70 vector70 processor70 reasoning70", 10),
        ["stream70", "context70", "knowledge70", "vector70", "processor70", "reasoning70"],
    ),
    (
        ("stream70 context70 knowledge70 vector70 processor70 reasoning70", 18),
        ["stream70 context70", "knowledge70", "vector70", "processor70", "reasoning70"],
    ),
    (
        ("stream70 context70 knowledge70 vector70 processor70 reasoning70", 28),
        ["stream70 context70", "knowledge70 vector70", "processor70 reasoning70"],
    ),
    (
        ("context70 knowledge70 vector70 processor70 reasoning70 machine70", 6),
        ["context70", "knowledge70", "vector70", "processor70", "reasoning70", "machine70"],
    ),
    (
        ("context70 knowledge70 vector70 processor70 reasoning70 machine70", 10),
        ["context70", "knowledge70", "vector70", "processor70", "reasoning70", "machine70"],
    ),
    (
        ("context70 knowledge70 vector70 processor70 reasoning70 machine70", 18),
        ["context70", "knowledge70", "vector70", "processor70", "reasoning70", "machine70"],
    ),
    (
        ("context70 knowledge70 vector70 processor70 reasoning70 machine70", 28),
        ["context70 knowledge70", "vector70 processor70", "reasoning70 machine70"],
    ),
    (
        ("knowledge70 vector70 processor70 reasoning70 machine70 learning70", 6),
        ["knowledge70", "vector70", "processor70", "reasoning70", "machine70", "learning70"],
    ),
    (
        ("knowledge70 vector70 processor70 reasoning70 machine70 learning70", 10),
        ["knowledge70", "vector70", "processor70", "reasoning70", "machine70", "learning70"],
    ),
    (
        ("knowledge70 vector70 processor70 reasoning70 machine70 learning70", 18),
        ["knowledge70", "vector70", "processor70", "reasoning70", "machine70", "learning70"],
    ),
    (
        ("knowledge70 vector70 processor70 reasoning70 machine70 learning70", 28),
        ["knowledge70 vector70", "processor70 reasoning70", "machine70 learning70"],
    ),
    (
        ("vector70 processor70 reasoning70 machine70 learning70 model70", 6),
        ["vector70", "processor70", "reasoning70", "machine70", "learning70", "model70"],
    ),
    (
        ("vector70 processor70 reasoning70 machine70 learning70 model70", 10),
        ["vector70", "processor70", "reasoning70", "machine70", "learning70", "model70"],
    ),
    (
        ("vector70 processor70 reasoning70 machine70 learning70 model70", 18),
        ["vector70", "processor70", "reasoning70", "machine70", "learning70 model70"],
    ),
    (
        ("vector70 processor70 reasoning70 machine70 learning70 model70", 28),
        ["vector70 processor70", "reasoning70 machine70", "learning70 model70"],
    ),
    (
        ("processor70 reasoning70 machine70 learning70 model70 token70", 6),
        ["processor70", "reasoning70", "machine70", "learning70", "model70", "token70"],
    ),
    (
        ("processor70 reasoning70 machine70 learning70 model70 token70", 10),
        ["processor70", "reasoning70", "machine70", "learning70", "model70", "token70"],
    ),
    (
        ("processor70 reasoning70 machine70 learning70 model70 token70", 18),
        ["processor70", "reasoning70", "machine70", "learning70 model70", "token70"],
    ),
    (
        ("processor70 reasoning70 machine70 learning70 model70 token70", 28),
        ["processor70 reasoning70", "machine70 learning70 model70", "token70"],
    ),
    (
        ("reasoning70 machine70 learning70 model70 token70 prompt70", 6),
        ["reasoning70", "machine70", "learning70", "model70", "token70", "prompt70"],
    ),
    (
        ("reasoning70 machine70 learning70 model70 token70 prompt70", 10),
        ["reasoning70", "machine70", "learning70", "model70", "token70", "prompt70"],
    ),
    (
        ("reasoning70 machine70 learning70 model70 token70 prompt70", 18),
        ["reasoning70", "machine70", "learning70 model70", "token70 prompt70"],
    ),
    (
        ("reasoning70 machine70 learning70 model70 token70 prompt70", 28),
        ["reasoning70 machine70", "learning70 model70 token70", "prompt70"],
    ),
    (
        ("machine70 learning70 model70 token70 prompt70 session70", 6),
        ["machine70", "learning70", "model70", "token70", "prompt70", "session70"],
    ),
    (
        ("machine70 learning70 model70 token70 prompt70 session70", 10),
        ["machine70", "learning70", "model70", "token70", "prompt70", "session70"],
    ),
    (
        ("machine70 learning70 model70 token70 prompt70 session70", 18),
        ["machine70", "learning70 model70", "token70 prompt70", "session70"],
    ),
    (
        ("machine70 learning70 model70 token70 prompt70 session70", 28),
        ["machine70 learning70 model70", "token70 prompt70 session70"],
    ),
    (
        ("learning70 model70 token70 prompt70 session70 library70", 6),
        ["learning70", "model70", "token70", "prompt70", "session70", "library70"],
    ),
    (
        ("learning70 model70 token70 prompt70 session70 library70", 10),
        ["learning70", "model70", "token70", "prompt70", "session70", "library70"],
    ),
    (
        ("learning70 model70 token70 prompt70 session70 library70", 18),
        ["learning70 model70", "token70 prompt70", "session70", "library70"],
    ),
    (
        ("learning70 model70 token70 prompt70 session70 library70", 28),
        ["learning70 model70 token70", "prompt70 session70 library70"],
    ),
    (
        ("model70 token70 prompt70 session70 library70 service70", 6),
        ["model70", "token70", "prompt70", "session70", "library70", "service70"],
    ),
    (
        ("model70 token70 prompt70 session70 library70 service70", 10),
        ["model70", "token70", "prompt70", "session70", "library70", "service70"],
    ),
    (
        ("model70 token70 prompt70 session70 library70 service70", 18),
        ["model70 token70", "prompt70 session70", "library70", "service70"],
    ),
    (
        ("model70 token70 prompt70 session70 library70 service70", 28),
        ["model70 token70 prompt70", "session70 library70", "service70"],
    ),
    (
        ("token70 prompt70 session70 library70 service70 gateway70", 6),
        ["token70", "prompt70", "session70", "library70", "service70", "gateway70"],
    ),
    (
        ("token70 prompt70 session70 library70 service70 gateway70", 10),
        ["token70", "prompt70", "session70", "library70", "service70", "gateway70"],
    ),
    (
        ("token70 prompt70 session70 library70 service70 gateway70", 18),
        ["token70 prompt70", "session70", "library70", "service70", "gateway70"],
    ),
    (
        ("token70 prompt70 session70 library70 service70 gateway70", 28),
        ["token70 prompt70 session70", "library70 service70", "gateway70"],
    ),
    (
        ("prompt70 session70 library70 service70 gateway70 storage70", 6),
        ["prompt70", "session70", "library70", "service70", "gateway70", "storage70"],
    ),
    (
        ("prompt70 session70 library70 service70 gateway70 storage70", 10),
        ["prompt70", "session70", "library70", "service70", "gateway70", "storage70"],
    ),
    (
        ("prompt70 session70 library70 service70 gateway70 storage70", 18),
        ["prompt70 session70", "library70", "service70", "gateway70", "storage70"],
    ),
    (
        ("prompt70 session70 library70 service70 gateway70 storage70", 28),
        ["prompt70 session70 library70", "service70 gateway70", "storage70"],
    ),
    (
        ("session70 library70 service70 gateway70 storage70 network70", 6),
        ["session70", "library70", "service70", "gateway70", "storage70", "network70"],
    ),
    (
        ("session70 library70 service70 gateway70 storage70 network70", 10),
        ["session70", "library70", "service70", "gateway70", "storage70", "network70"],
    ),
    (
        ("session70 library70 service70 gateway70 storage70 network70", 18),
        ["session70", "library70", "service70", "gateway70", "storage70", "network70"],
    ),
    (
        ("session70 library70 service70 gateway70 storage70 network70", 28),
        ["session70 library70", "service70 gateway70", "storage70 network70"],
    ),
    (
        ("library70 service70 gateway70 storage70 network70 latency70", 6),
        ["library70", "service70", "gateway70", "storage70", "network70", "latency70"],
    ),
    (
        ("library70 service70 gateway70 storage70 network70 latency70", 10),
        ["library70", "service70", "gateway70", "storage70", "network70", "latency70"],
    ),
    (
        ("library70 service70 gateway70 storage70 network70 latency70", 18),
        ["library70", "service70", "gateway70", "storage70", "network70", "latency70"],
    ),
    (
        ("library70 service70 gateway70 storage70 network70 latency70", 28),
        ["library70 service70", "gateway70 storage70", "network70 latency70"],
    ),
    (
        ("service70 gateway70 storage70 network70 latency70 buffer70", 6),
        ["service70", "gateway70", "storage70", "network70", "latency70", "buffer70"],
    ),
    (
        ("service70 gateway70 storage70 network70 latency70 buffer70", 10),
        ["service70", "gateway70", "storage70", "network70", "latency70", "buffer70"],
    ),
    (
        ("service70 gateway70 storage70 network70 latency70 buffer70", 18),
        ["service70", "gateway70", "storage70", "network70", "latency70 buffer70"],
    ),
    (
        ("service70 gateway70 storage70 network70 latency70 buffer70", 28),
        ["service70 gateway70", "storage70 network70", "latency70 buffer70"],
    ),
    (
        ("gateway70 storage70 network70 latency70 buffer70 queue70", 6),
        ["gateway70", "storage70", "network70", "latency70", "buffer70", "queue70"],
    ),
    (
        ("gateway70 storage70 network70 latency70 buffer70 queue70", 10),
        ["gateway70", "storage70", "network70", "latency70", "buffer70", "queue70"],
    ),
    (
        ("gateway70 storage70 network70 latency70 buffer70 queue70", 18),
        ["gateway70", "storage70", "network70", "latency70 buffer70", "queue70"],
    ),
    (
        ("gateway70 storage70 network70 latency70 buffer70 queue70", 28),
        ["gateway70 storage70", "network70 latency70 buffer70", "queue70"],
    ),
    (
        ("storage70 network70 latency70 buffer70 queue70 worker70", 6),
        ["storage70", "network70", "latency70", "buffer70", "queue70", "worker70"],
    ),
    (
        ("storage70 network70 latency70 buffer70 queue70 worker70", 10),
        ["storage70", "network70", "latency70", "buffer70", "queue70", "worker70"],
    ),
    (
        ("storage70 network70 latency70 buffer70 queue70 worker70", 18),
        ["storage70", "network70", "latency70 buffer70", "queue70 worker70"],
    ),
    (
        ("storage70 network70 latency70 buffer70 queue70 worker70", 28),
        ["storage70 network70", "latency70 buffer70 queue70", "worker70"],
    ),
    (
        ("network70 latency70 buffer70 queue70 worker70 kernel70", 6),
        ["network70", "latency70", "buffer70", "queue70", "worker70", "kernel70"],
    ),
    (
        ("network70 latency70 buffer70 queue70 worker70 kernel70", 10),
        ["network70", "latency70", "buffer70", "queue70", "worker70", "kernel70"],
    ),
    (
        ("network70 latency70 buffer70 queue70 worker70 kernel70", 18),
        ["network70", "latency70 buffer70", "queue70 worker70", "kernel70"],
    ),
    (
        ("network70 latency70 buffer70 queue70 worker70 kernel70", 28),
        ["network70 latency70 buffer70", "queue70 worker70 kernel70"],
    ),
    (
        ("latency70 buffer70 queue70 worker70 kernel70 signal70", 6),
        ["latency70", "buffer70", "queue70", "worker70", "kernel70", "signal70"],
    ),
    (
        ("latency70 buffer70 queue70 worker70 kernel70 signal70", 10),
        ["latency70", "buffer70", "queue70", "worker70", "kernel70", "signal70"],
    ),
    (
        ("latency70 buffer70 queue70 worker70 kernel70 signal70", 18),
        ["latency70 buffer70", "queue70 worker70", "kernel70 signal70"],
    ),
    (
        ("latency70 buffer70 queue70 worker70 kernel70 signal70", 28),
        ["latency70 buffer70 queue70", "worker70 kernel70 signal70"],
    ),
    (
        ("buffer70 queue70 worker70 kernel70 signal70 packet70", 6),
        ["buffer70", "queue70", "worker70", "kernel70", "signal70", "packet70"],
    ),
    (
        ("buffer70 queue70 worker70 kernel70 signal70 packet70", 10),
        ["buffer70", "queue70", "worker70", "kernel70", "signal70", "packet70"],
    ),
    (
        ("buffer70 queue70 worker70 kernel70 signal70 packet70", 18),
        ["buffer70 queue70", "worker70 kernel70", "signal70 packet70"],
    ),
    (
        ("buffer70 queue70 worker70 kernel70 signal70 packet70", 28),
        ["buffer70 queue70 worker70", "kernel70 signal70 packet70"],
    ),
    (
        ("queue70 worker70 kernel70 signal70 packet70 router70", 6),
        ["queue70", "worker70", "kernel70", "signal70", "packet70", "router70"],
    ),
    (
        ("queue70 worker70 kernel70 signal70 packet70 router70", 10),
        ["queue70", "worker70", "kernel70", "signal70", "packet70", "router70"],
    ),
    (
        ("queue70 worker70 kernel70 signal70 packet70 router70", 18),
        ["queue70 worker70", "kernel70 signal70", "packet70 router70"],
    ),
    (
        ("queue70 worker70 kernel70 signal70 packet70 router70", 28),
        ["queue70 worker70 kernel70", "signal70 packet70 router70"],
    ),
    (
        ("worker70 kernel70 signal70 packet70 router70 cluster70", 6),
        ["worker70", "kernel70", "signal70", "packet70", "router70", "cluster70"],
    ),
    (
        ("worker70 kernel70 signal70 packet70 router70 cluster70", 10),
        ["worker70", "kernel70", "signal70", "packet70", "router70", "cluster70"],
    ),
    (
        ("worker70 kernel70 signal70 packet70 router70 cluster70", 18),
        ["worker70 kernel70", "signal70 packet70", "router70 cluster70"],
    ),
    (
        ("worker70 kernel70 signal70 packet70 router70 cluster70", 28),
        ["worker70 kernel70 signal70", "packet70 router70 cluster70"],
    ),
    (
        ("kernel70 signal70 packet70 router70 cluster70 mirror70", 6),
        ["kernel70", "signal70", "packet70", "router70", "cluster70", "mirror70"],
    ),
    (
        ("kernel70 signal70 packet70 router70 cluster70 mirror70", 10),
        ["kernel70", "signal70", "packet70", "router70", "cluster70", "mirror70"],
    ),
    (
        ("kernel70 signal70 packet70 router70 cluster70 mirror70", 18),
        ["kernel70 signal70", "packet70 router70", "cluster70 mirror70"],
    ),
    (
        ("kernel70 signal70 packet70 router70 cluster70 mirror70", 28),
        ["kernel70 signal70 packet70", "router70 cluster70 mirror70"],
    ),
    (
        ("signal70 packet70 router70 cluster70 mirror70 filter70", 6),
        ["signal70", "packet70", "router70", "cluster70", "mirror70", "filter70"],
    ),
    (
        ("signal70 packet70 router70 cluster70 mirror70 filter70", 10),
        ["signal70", "packet70", "router70", "cluster70", "mirror70", "filter70"],
    ),
    (
        ("signal70 packet70 router70 cluster70 mirror70 filter70", 18),
        ["signal70 packet70", "router70 cluster70", "mirror70 filter70"],
    ),
    (
        ("signal70 packet70 router70 cluster70 mirror70 filter70", 28),
        ["signal70 packet70 router70", "cluster70 mirror70 filter70"],
    ),
    (
        ("packet70 router70 cluster70 mirror70 filter70 ranking70", 6),
        ["packet70", "router70", "cluster70", "mirror70", "filter70", "ranking70"],
    ),
    (
        ("packet70 router70 cluster70 mirror70 filter70 ranking70", 10),
        ["packet70", "router70", "cluster70", "mirror70", "filter70", "ranking70"],
    ),
    (
        ("packet70 router70 cluster70 mirror70 filter70 ranking70", 18),
        ["packet70 router70", "cluster70 mirror70", "filter70 ranking70"],
    ),
    (
        ("packet70 router70 cluster70 mirror70 filter70 ranking70", 28),
        ["packet70 router70 cluster70", "mirror70 filter70 ranking70"],
    ),
    (
        ("router70 cluster70 mirror70 filter70 ranking70 encoding70", 6),
        ["router70", "cluster70", "mirror70", "filter70", "ranking70", "encoding70"],
    ),
    (
        ("router70 cluster70 mirror70 filter70 ranking70 encoding70", 10),
        ["router70", "cluster70", "mirror70", "filter70", "ranking70", "encoding70"],
    ),
    (
        ("router70 cluster70 mirror70 filter70 ranking70 encoding70", 18),
        ["router70 cluster70", "mirror70 filter70", "ranking70", "encoding70"],
    ),
    (
        ("router70 cluster70 mirror70 filter70 ranking70 encoding70", 28),
        ["router70 cluster70 mirror70", "filter70 ranking70", "encoding70"],
    ),
    (
        ("cluster70 mirror70 filter70 ranking70 encoding70 mapping70", 6),
        ["cluster70", "mirror70", "filter70", "ranking70", "encoding70", "mapping70"],
    ),
    (
        ("cluster70 mirror70 filter70 ranking70 encoding70 mapping70", 10),
        ["cluster70", "mirror70", "filter70", "ranking70", "encoding70", "mapping70"],
    ),
    (
        ("cluster70 mirror70 filter70 ranking70 encoding70 mapping70", 18),
        ["cluster70 mirror70", "filter70 ranking70", "encoding70", "mapping70"],
    ),
    (
        ("cluster70 mirror70 filter70 ranking70 encoding70 mapping70", 28),
        ["cluster70 mirror70 filter70", "ranking70 encoding70", "mapping70"],
    ),
    (
        ("mirror70 filter70 ranking70 encoding70 mapping70 record70", 6),
        ["mirror70", "filter70", "ranking70", "encoding70", "mapping70", "record70"],
    ),
    (
        ("mirror70 filter70 ranking70 encoding70 mapping70 record70", 10),
        ["mirror70", "filter70", "ranking70", "encoding70", "mapping70", "record70"],
    ),
    (
        ("mirror70 filter70 ranking70 encoding70 mapping70 record70", 18),
        ["mirror70 filter70", "ranking70", "encoding70", "mapping70 record70"],
    ),
    (
        ("mirror70 filter70 ranking70 encoding70 mapping70 record70", 28),
        ["mirror70 filter70 ranking70", "encoding70 mapping70", "record70"],
    ),
    (
        ("filter70 ranking70 encoding70 mapping70 record70 candle70", 6),
        ["filter70", "ranking70", "encoding70", "mapping70", "record70", "candle70"],
    ),
    (
        ("filter70 ranking70 encoding70 mapping70 record70 candle70", 10),
        ["filter70", "ranking70", "encoding70", "mapping70", "record70", "candle70"],
    ),
    (
        ("filter70 ranking70 encoding70 mapping70 record70 candle70", 18),
        ["filter70 ranking70", "encoding70", "mapping70 record70", "candle70"],
    ),
    (
        ("filter70 ranking70 encoding70 mapping70 record70 candle70", 28),
        ["filter70 ranking70", "encoding70 mapping70", "record70 candle70"],
    ),
    (
        ("ranking70 encoding70 mapping70 record70 candle70 thread70", 6),
        ["ranking70", "encoding70", "mapping70", "record70", "candle70", "thread70"],
    ),
    (
        ("ranking70 encoding70 mapping70 record70 candle70 thread70", 10),
        ["ranking70", "encoding70", "mapping70", "record70", "candle70", "thread70"],
    ),
    (
        ("ranking70 encoding70 mapping70 record70 candle70 thread70", 18),
        ["ranking70", "encoding70", "mapping70 record70", "candle70 thread70"],
    ),
    (
        ("ranking70 encoding70 mapping70 record70 candle70 thread70", 28),
        ["ranking70 encoding70", "mapping70 record70 candle70", "thread70"],
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
