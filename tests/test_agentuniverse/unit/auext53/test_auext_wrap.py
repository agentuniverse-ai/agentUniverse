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
        ("round 53: the quick brown fox jumps over the lazy dog", 4),
        ["round", "53:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 53: the quick brown fox jumps over the lazy dog", 8),
        ["round", "53: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 53: the quick brown fox jumps over the lazy dog", 12),
        ["round 53:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 53: the quick brown fox jumps over the lazy dog", 16),
        ["round 53: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 53: the quick brown fox jumps over the lazy dog", 24),
        ["round 53: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 53: the quick brown fox jumps over the lazy dog", 32),
        ["round 53: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 53: agentuniverse is a framework for multi agents", 4),
        ["round", "53:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 53: agentuniverse is a framework for multi agents", 8),
        ["round", "53:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 53: agentuniverse is a framework for multi agents", 12),
        ["round 53:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 53: agentuniverse is a framework for multi agents", 16),
        ["round 53:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 53: agentuniverse is a framework for multi agents", 24),
        ["round 53: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 53: agentuniverse is a framework for multi agents", 32),
        ["round 53: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 53: knowledge stored as vectors enables retrieval", 4),
        ["round", "53:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 53: knowledge stored as vectors enables retrieval", 8),
        ["round", "53:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 53: knowledge stored as vectors enables retrieval", 12),
        ["round 53:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 53: knowledge stored as vectors enables retrieval", 16),
        ["round 53:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 53: knowledge stored as vectors enables retrieval", 24),
        ["round 53: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 53: knowledge stored as vectors enables retrieval", 32),
        ["round 53: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 53: the processor reads the record then stops", 4),
        ["round", "53:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 53: the processor reads the record then stops", 8),
        ["round", "53: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 53: the processor reads the record then stops", 12),
        ["round 53:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 53: the processor reads the record then stops", 16),
        ["round 53: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 53: the processor reads the record then stops", 24),
        ["round 53: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 53: the processor reads the record then stops", 32),
        ["round 53: the processor reads", "the record then stops"],
    ),
    (
        ("round 53: a worker pulls the next task from the queue", 4),
        ["round", "53:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 53: a worker pulls the next task from the queue", 8),
        ["round", "53: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 53: a worker pulls the next task from the queue", 12),
        ["round 53: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 53: a worker pulls the next task from the queue", 16),
        ["round 53: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 53: a worker pulls the next task from the queue", 24),
        ["round 53: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 53: a worker pulls the next task from the queue", 32),
        ["round 53: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 53: signals travel through the network layer", 4),
        ["round", "53:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 53: signals travel through the network layer", 8),
        ["round", "53:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 53: signals travel through the network layer", 12),
        ["round 53:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 53: signals travel through the network layer", 16),
        ["round 53:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 53: signals travel through the network layer", 24),
        ["round 53: signals travel", "through the network", "layer"],
    ),
    (
        ("round 53: signals travel through the network layer", 32),
        ["round 53: signals travel through", "the network layer"],
    ),
    (
        ("round 53: the gateway routes each request by policy", 4),
        ["round", "53:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 53: the gateway routes each request by policy", 8),
        ["round", "53: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 53: the gateway routes each request by policy", 12),
        ["round 53:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 53: the gateway routes each request by policy", 16),
        ["round 53: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 53: the gateway routes each request by policy", 24),
        ["round 53: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 53: the gateway routes each request by policy", 32),
        ["round 53: the gateway routes", "each request by policy"],
    ),
    (
        ("round 53: memory grows until the buffer is full", 4),
        ["round", "53:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 53: memory grows until the buffer is full", 8),
        ["round", "53:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 53: memory grows until the buffer is full", 12),
        ["round 53:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 53: memory grows until the buffer is full", 16),
        ["round 53: memory", "grows until the", "buffer is full"],
    ),
    (("round 53: memory grows until the buffer is full", 24), ["round 53: memory grows", "until the buffer is full"]),
    (("round 53: memory grows until the buffer is full", 32), ["round 53: memory grows until the", "buffer is full"]),
    (
        ("round 53: the cluster mirrors every packet twice", 4),
        ["round", "53:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 53: the cluster mirrors every packet twice", 8),
        ["round", "53: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 53: the cluster mirrors every packet twice", 12),
        ["round 53:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 53: the cluster mirrors every packet twice", 16),
        ["round 53: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 53: the cluster mirrors every packet twice", 24),
        ["round 53: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 53: the cluster mirrors every packet twice", 32), ["round 53: the cluster mirrors", "every packet twice"]),
    (
        ("round 53: ranking uses tokens learned from the corpus", 4),
        ["round", "53:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 53: ranking uses tokens learned from the corpus", 8),
        ["round", "53:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 53: ranking uses tokens learned from the corpus", 12),
        ["round 53:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 53: ranking uses tokens learned from the corpus", 16),
        ["round 53:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 53: ranking uses tokens learned from the corpus", 24),
        ["round 53: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 53: ranking uses tokens learned from the corpus", 32),
        ["round 53: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 53: a long session ends when the candle dies", 4),
        ["round", "53:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 53: a long session ends when the candle dies", 8),
        ["round", "53: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 53: a long session ends when the candle dies", 12),
        ["round 53: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 53: a long session ends when the candle dies", 16),
        ["round 53: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 53: a long session ends when the candle dies", 24),
        ["round 53: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 53: a long session ends when the candle dies", 32),
        ["round 53: a long session ends", "when the candle dies"],
    ),
    (
        ("round 53: encode the prompt then map the result", 4),
        ["round", "53:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 53: encode the prompt then map the result", 8),
        ["round", "53:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 53: encode the prompt then map the result", 12),
        ["round 53:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 53: encode the prompt then map the result", 16),
        ["round 53: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 53: encode the prompt then map the result", 24),
        ["round 53: encode the", "prompt then map the", "result"],
    ),
    (("round 53: encode the prompt then map the result", 32), ["round 53: encode the prompt then", "map the result"]),
    (
        ("round 53: the kernel wakes the worker at dawn", 4),
        ["round", "53:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 53: the kernel wakes the worker at dawn", 8),
        ["round", "53: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 53: the kernel wakes the worker at dawn", 12),
        ["round 53:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 53: the kernel wakes the worker at dawn", 16), ["round 53: the", "kernel wakes the", "worker at dawn"]),
    (("round 53: the kernel wakes the worker at dawn", 24), ["round 53: the kernel", "wakes the worker at dawn"]),
    (("round 53: the kernel wakes the worker at dawn", 32), ["round 53: the kernel wakes the", "worker at dawn"]),
    (
        ("round 53: service latency drops after the patch", 4),
        ["round", "53:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 53: service latency drops after the patch", 8),
        ["round", "53:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 53: service latency drops after the patch", 12),
        ["round 53:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 53: service latency drops after the patch", 16),
        ["round 53:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 53: service latency drops after the patch", 24),
        ["round 53: service", "latency drops after the", "patch"],
    ),
    (("round 53: service latency drops after the patch", 32), ["round 53: service latency drops", "after the patch"]),
    (
        ("round 53: the library caches every vector it sees", 4),
        ["round", "53:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 53: the library caches every vector it sees", 8),
        ["round", "53: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 53: the library caches every vector it sees", 12),
        ["round 53:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 53: the library caches every vector it sees", 16),
        ["round 53: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 53: the library caches every vector it sees", 24),
        ["round 53: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 53: the library caches every vector it sees", 32),
        ["round 53: the library caches", "every vector it sees"],
    ),
    (
        ("round 53: agents argue then the debate resolves", 4),
        ["round", "53:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 53: agents argue then the debate resolves", 8),
        ["round", "53:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 53: agents argue then the debate resolves", 12),
        ["round 53:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 53: agents argue then the debate resolves", 16),
        ["round 53: agents", "argue then the", "debate resolves"],
    ),
    (("round 53: agents argue then the debate resolves", 24), ["round 53: agents argue", "then the debate resolves"]),
    (("round 53: agents argue then the debate resolves", 32), ["round 53: agents argue then the", "debate resolves"]),
    (
        ("round 53: the filter keeps only strong matches", 4),
        ["round", "53:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 53: the filter keeps only strong matches", 8),
        ["round", "53: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 53: the filter keeps only strong matches", 12),
        ["round 53:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 53: the filter keeps only strong matches", 16),
        ["round 53: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 53: the filter keeps only strong matches", 24), ["round 53: the filter", "keeps only strong", "matches"]),
    (("round 53: the filter keeps only strong matches", 32), ["round 53: the filter keeps only", "strong matches"]),
    (
        ("round 53: the model answers with a short reply", 4),
        ["round", "53:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 53: the model answers with a short reply", 8),
        ["round", "53: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 53: the model answers with a short reply", 12),
        ["round 53:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 53: the model answers with a short reply", 16),
        ["round 53: the", "model answers", "with a short", "reply"],
    ),
    (("round 53: the model answers with a short reply", 24), ["round 53: the model", "answers with a short", "reply"]),
    (("round 53: the model answers with a short reply", 32), ["round 53: the model answers with", "a short reply"]),
    (
        ("round 53: the recorder stores the reasoning trace", 4),
        ["round", "53:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 53: the recorder stores the reasoning trace", 8),
        ["round", "53: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 53: the recorder stores the reasoning trace", 12),
        ["round 53:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 53: the recorder stores the reasoning trace", 16),
        ["round 53: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 53: the recorder stores the reasoning trace", 24),
        ["round 53: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 53: the recorder stores the reasoning trace", 32),
        ["round 53: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 53: the angel watches the processor run", 4),
        ["round", "53:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 53: the angel watches the processor run", 8),
        ["round", "53: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 53: the angel watches the processor run", 12),
        ["round 53:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 53: the angel watches the processor run", 16), ["round 53: the", "angel watches", "the processor", "run"]),
    (("round 53: the angel watches the processor run", 24), ["round 53: the angel", "watches the processor", "run"]),
    (("round 53: the angel watches the processor run", 32), ["round 53: the angel watches the", "processor run"]),
    (
        ("round 53: angle of the vector decides the match", 4),
        ["round", "53:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 53: angle of the vector decides the match", 8),
        ["round", "53:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 53: angle of the vector decides the match", 12),
        ["round 53:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 53: angle of the vector decides the match", 16),
        ["round 53: angle", "of the vector", "decides the", "match"],
    ),
    (("round 53: angle of the vector decides the match", 24), ["round 53: angle of the", "vector decides the match"]),
    (("round 53: angle of the vector decides the match", 32), ["round 53: angle of the vector", "decides the match"]),
    (
        ("round 53: the candle burns twice as long at night", 4),
        ["round", "53:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 53: the candle burns twice as long at night", 8),
        ["round", "53: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 53: the candle burns twice as long at night", 12),
        ["round 53:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 53: the candle burns twice as long at night", 16),
        ["round 53: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 53: the candle burns twice as long at night", 24),
        ["round 53: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 53: the candle burns twice as long at night", 32),
        ["round 53: the candle burns twice", "as long at night"],
    ),
    (
        ("round 53: a mirror of the universe in one line", 4),
        ["round", "53:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 53: a mirror of the universe in one line", 8),
        ["round", "53: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 53: a mirror of the universe in one line", 12),
        ["round 53: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 53: a mirror of the universe in one line", 16),
        ["round 53: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 53: a mirror of the universe in one line", 24), ["round 53: a mirror of", "the universe in one line"]),
    (("round 53: a mirror of the universe in one line", 32), ["round 53: a mirror of the", "universe in one line"]),
    (
        ("round 53: the queue drains before the storm", 4),
        ["round", "53:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 53: the queue drains before the storm", 8),
        ["round", "53: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 53: the queue drains before the storm", 12), ["round 53:", "the queue", "drains", "before the", "storm"]),
    (("round 53: the queue drains before the storm", 16), ["round 53: the", "queue drains", "before the storm"]),
    (("round 53: the queue drains before the storm", 24), ["round 53: the queue", "drains before the storm"]),
    (("round 53: the queue drains before the storm", 32), ["round 53: the queue drains", "before the storm"]),
    (
        ("kitten53 sitting53 agent53 angle53 universe53 memory53", 6),
        ["kitten53", "sitting53", "agent53", "angle53", "universe53", "memory53"],
    ),
    (
        ("kitten53 sitting53 agent53 angle53 universe53 memory53", 10),
        ["kitten53", "sitting53", "agent53", "angle53", "universe53", "memory53"],
    ),
    (
        ("kitten53 sitting53 agent53 angle53 universe53 memory53", 18),
        ["kitten53 sitting53", "agent53 angle53", "universe53", "memory53"],
    ),
    (
        ("kitten53 sitting53 agent53 angle53 universe53 memory53", 28),
        ["kitten53 sitting53 agent53", "angle53 universe53 memory53"],
    ),
    (
        ("sitting53 agent53 angle53 universe53 memory53 stream53", 6),
        ["sitting53", "agent53", "angle53", "universe53", "memory53", "stream53"],
    ),
    (
        ("sitting53 agent53 angle53 universe53 memory53 stream53", 10),
        ["sitting53", "agent53", "angle53", "universe53", "memory53", "stream53"],
    ),
    (
        ("sitting53 agent53 angle53 universe53 memory53 stream53", 18),
        ["sitting53 agent53", "angle53 universe53", "memory53 stream53"],
    ),
    (
        ("sitting53 agent53 angle53 universe53 memory53 stream53", 28),
        ["sitting53 agent53 angle53", "universe53 memory53 stream53"],
    ),
    (
        ("agent53 angle53 universe53 memory53 stream53 context53", 6),
        ["agent53", "angle53", "universe53", "memory53", "stream53", "context53"],
    ),
    (
        ("agent53 angle53 universe53 memory53 stream53 context53", 10),
        ["agent53", "angle53", "universe53", "memory53", "stream53", "context53"],
    ),
    (
        ("agent53 angle53 universe53 memory53 stream53 context53", 18),
        ["agent53 angle53", "universe53", "memory53 stream53", "context53"],
    ),
    (
        ("agent53 angle53 universe53 memory53 stream53 context53", 28),
        ["agent53 angle53 universe53", "memory53 stream53 context53"],
    ),
    (
        ("angle53 universe53 memory53 stream53 context53 knowledge53", 6),
        ["angle53", "universe53", "memory53", "stream53", "context53", "knowledge53"],
    ),
    (
        ("angle53 universe53 memory53 stream53 context53 knowledge53", 10),
        ["angle53", "universe53", "memory53", "stream53", "context53", "knowledge53"],
    ),
    (
        ("angle53 universe53 memory53 stream53 context53 knowledge53", 18),
        ["angle53 universe53", "memory53 stream53", "context53", "knowledge53"],
    ),
    (
        ("angle53 universe53 memory53 stream53 context53 knowledge53", 28),
        ["angle53 universe53 memory53", "stream53 context53", "knowledge53"],
    ),
    (
        ("universe53 memory53 stream53 context53 knowledge53 vector53", 6),
        ["universe53", "memory53", "stream53", "context53", "knowledge53", "vector53"],
    ),
    (
        ("universe53 memory53 stream53 context53 knowledge53 vector53", 10),
        ["universe53", "memory53", "stream53", "context53", "knowledge53", "vector53"],
    ),
    (
        ("universe53 memory53 stream53 context53 knowledge53 vector53", 18),
        ["universe53", "memory53 stream53", "context53", "knowledge53", "vector53"],
    ),
    (
        ("universe53 memory53 stream53 context53 knowledge53 vector53", 28),
        ["universe53 memory53 stream53", "context53 knowledge53", "vector53"],
    ),
    (
        ("memory53 stream53 context53 knowledge53 vector53 processor53", 6),
        ["memory53", "stream53", "context53", "knowledge53", "vector53", "processor53"],
    ),
    (
        ("memory53 stream53 context53 knowledge53 vector53 processor53", 10),
        ["memory53", "stream53", "context53", "knowledge53", "vector53", "processor53"],
    ),
    (
        ("memory53 stream53 context53 knowledge53 vector53 processor53", 18),
        ["memory53 stream53", "context53", "knowledge53", "vector53", "processor53"],
    ),
    (
        ("memory53 stream53 context53 knowledge53 vector53 processor53", 28),
        ["memory53 stream53 context53", "knowledge53 vector53", "processor53"],
    ),
    (
        ("stream53 context53 knowledge53 vector53 processor53 reasoning53", 6),
        ["stream53", "context53", "knowledge53", "vector53", "processor53", "reasoning53"],
    ),
    (
        ("stream53 context53 knowledge53 vector53 processor53 reasoning53", 10),
        ["stream53", "context53", "knowledge53", "vector53", "processor53", "reasoning53"],
    ),
    (
        ("stream53 context53 knowledge53 vector53 processor53 reasoning53", 18),
        ["stream53 context53", "knowledge53", "vector53", "processor53", "reasoning53"],
    ),
    (
        ("stream53 context53 knowledge53 vector53 processor53 reasoning53", 28),
        ["stream53 context53", "knowledge53 vector53", "processor53 reasoning53"],
    ),
    (
        ("context53 knowledge53 vector53 processor53 reasoning53 machine53", 6),
        ["context53", "knowledge53", "vector53", "processor53", "reasoning53", "machine53"],
    ),
    (
        ("context53 knowledge53 vector53 processor53 reasoning53 machine53", 10),
        ["context53", "knowledge53", "vector53", "processor53", "reasoning53", "machine53"],
    ),
    (
        ("context53 knowledge53 vector53 processor53 reasoning53 machine53", 18),
        ["context53", "knowledge53", "vector53", "processor53", "reasoning53", "machine53"],
    ),
    (
        ("context53 knowledge53 vector53 processor53 reasoning53 machine53", 28),
        ["context53 knowledge53", "vector53 processor53", "reasoning53 machine53"],
    ),
    (
        ("knowledge53 vector53 processor53 reasoning53 machine53 learning53", 6),
        ["knowledge53", "vector53", "processor53", "reasoning53", "machine53", "learning53"],
    ),
    (
        ("knowledge53 vector53 processor53 reasoning53 machine53 learning53", 10),
        ["knowledge53", "vector53", "processor53", "reasoning53", "machine53", "learning53"],
    ),
    (
        ("knowledge53 vector53 processor53 reasoning53 machine53 learning53", 18),
        ["knowledge53", "vector53", "processor53", "reasoning53", "machine53", "learning53"],
    ),
    (
        ("knowledge53 vector53 processor53 reasoning53 machine53 learning53", 28),
        ["knowledge53 vector53", "processor53 reasoning53", "machine53 learning53"],
    ),
    (
        ("vector53 processor53 reasoning53 machine53 learning53 model53", 6),
        ["vector53", "processor53", "reasoning53", "machine53", "learning53", "model53"],
    ),
    (
        ("vector53 processor53 reasoning53 machine53 learning53 model53", 10),
        ["vector53", "processor53", "reasoning53", "machine53", "learning53", "model53"],
    ),
    (
        ("vector53 processor53 reasoning53 machine53 learning53 model53", 18),
        ["vector53", "processor53", "reasoning53", "machine53", "learning53 model53"],
    ),
    (
        ("vector53 processor53 reasoning53 machine53 learning53 model53", 28),
        ["vector53 processor53", "reasoning53 machine53", "learning53 model53"],
    ),
    (
        ("processor53 reasoning53 machine53 learning53 model53 token53", 6),
        ["processor53", "reasoning53", "machine53", "learning53", "model53", "token53"],
    ),
    (
        ("processor53 reasoning53 machine53 learning53 model53 token53", 10),
        ["processor53", "reasoning53", "machine53", "learning53", "model53", "token53"],
    ),
    (
        ("processor53 reasoning53 machine53 learning53 model53 token53", 18),
        ["processor53", "reasoning53", "machine53", "learning53 model53", "token53"],
    ),
    (
        ("processor53 reasoning53 machine53 learning53 model53 token53", 28),
        ["processor53 reasoning53", "machine53 learning53 model53", "token53"],
    ),
    (
        ("reasoning53 machine53 learning53 model53 token53 prompt53", 6),
        ["reasoning53", "machine53", "learning53", "model53", "token53", "prompt53"],
    ),
    (
        ("reasoning53 machine53 learning53 model53 token53 prompt53", 10),
        ["reasoning53", "machine53", "learning53", "model53", "token53", "prompt53"],
    ),
    (
        ("reasoning53 machine53 learning53 model53 token53 prompt53", 18),
        ["reasoning53", "machine53", "learning53 model53", "token53 prompt53"],
    ),
    (
        ("reasoning53 machine53 learning53 model53 token53 prompt53", 28),
        ["reasoning53 machine53", "learning53 model53 token53", "prompt53"],
    ),
    (
        ("machine53 learning53 model53 token53 prompt53 session53", 6),
        ["machine53", "learning53", "model53", "token53", "prompt53", "session53"],
    ),
    (
        ("machine53 learning53 model53 token53 prompt53 session53", 10),
        ["machine53", "learning53", "model53", "token53", "prompt53", "session53"],
    ),
    (
        ("machine53 learning53 model53 token53 prompt53 session53", 18),
        ["machine53", "learning53 model53", "token53 prompt53", "session53"],
    ),
    (
        ("machine53 learning53 model53 token53 prompt53 session53", 28),
        ["machine53 learning53 model53", "token53 prompt53 session53"],
    ),
    (
        ("learning53 model53 token53 prompt53 session53 library53", 6),
        ["learning53", "model53", "token53", "prompt53", "session53", "library53"],
    ),
    (
        ("learning53 model53 token53 prompt53 session53 library53", 10),
        ["learning53", "model53", "token53", "prompt53", "session53", "library53"],
    ),
    (
        ("learning53 model53 token53 prompt53 session53 library53", 18),
        ["learning53 model53", "token53 prompt53", "session53", "library53"],
    ),
    (
        ("learning53 model53 token53 prompt53 session53 library53", 28),
        ["learning53 model53 token53", "prompt53 session53 library53"],
    ),
    (
        ("model53 token53 prompt53 session53 library53 service53", 6),
        ["model53", "token53", "prompt53", "session53", "library53", "service53"],
    ),
    (
        ("model53 token53 prompt53 session53 library53 service53", 10),
        ["model53", "token53", "prompt53", "session53", "library53", "service53"],
    ),
    (
        ("model53 token53 prompt53 session53 library53 service53", 18),
        ["model53 token53", "prompt53 session53", "library53", "service53"],
    ),
    (
        ("model53 token53 prompt53 session53 library53 service53", 28),
        ["model53 token53 prompt53", "session53 library53", "service53"],
    ),
    (
        ("token53 prompt53 session53 library53 service53 gateway53", 6),
        ["token53", "prompt53", "session53", "library53", "service53", "gateway53"],
    ),
    (
        ("token53 prompt53 session53 library53 service53 gateway53", 10),
        ["token53", "prompt53", "session53", "library53", "service53", "gateway53"],
    ),
    (
        ("token53 prompt53 session53 library53 service53 gateway53", 18),
        ["token53 prompt53", "session53", "library53", "service53", "gateway53"],
    ),
    (
        ("token53 prompt53 session53 library53 service53 gateway53", 28),
        ["token53 prompt53 session53", "library53 service53", "gateway53"],
    ),
    (
        ("prompt53 session53 library53 service53 gateway53 storage53", 6),
        ["prompt53", "session53", "library53", "service53", "gateway53", "storage53"],
    ),
    (
        ("prompt53 session53 library53 service53 gateway53 storage53", 10),
        ["prompt53", "session53", "library53", "service53", "gateway53", "storage53"],
    ),
    (
        ("prompt53 session53 library53 service53 gateway53 storage53", 18),
        ["prompt53 session53", "library53", "service53", "gateway53", "storage53"],
    ),
    (
        ("prompt53 session53 library53 service53 gateway53 storage53", 28),
        ["prompt53 session53 library53", "service53 gateway53", "storage53"],
    ),
    (
        ("session53 library53 service53 gateway53 storage53 network53", 6),
        ["session53", "library53", "service53", "gateway53", "storage53", "network53"],
    ),
    (
        ("session53 library53 service53 gateway53 storage53 network53", 10),
        ["session53", "library53", "service53", "gateway53", "storage53", "network53"],
    ),
    (
        ("session53 library53 service53 gateway53 storage53 network53", 18),
        ["session53", "library53", "service53", "gateway53", "storage53", "network53"],
    ),
    (
        ("session53 library53 service53 gateway53 storage53 network53", 28),
        ["session53 library53", "service53 gateway53", "storage53 network53"],
    ),
    (
        ("library53 service53 gateway53 storage53 network53 latency53", 6),
        ["library53", "service53", "gateway53", "storage53", "network53", "latency53"],
    ),
    (
        ("library53 service53 gateway53 storage53 network53 latency53", 10),
        ["library53", "service53", "gateway53", "storage53", "network53", "latency53"],
    ),
    (
        ("library53 service53 gateway53 storage53 network53 latency53", 18),
        ["library53", "service53", "gateway53", "storage53", "network53", "latency53"],
    ),
    (
        ("library53 service53 gateway53 storage53 network53 latency53", 28),
        ["library53 service53", "gateway53 storage53", "network53 latency53"],
    ),
    (
        ("service53 gateway53 storage53 network53 latency53 buffer53", 6),
        ["service53", "gateway53", "storage53", "network53", "latency53", "buffer53"],
    ),
    (
        ("service53 gateway53 storage53 network53 latency53 buffer53", 10),
        ["service53", "gateway53", "storage53", "network53", "latency53", "buffer53"],
    ),
    (
        ("service53 gateway53 storage53 network53 latency53 buffer53", 18),
        ["service53", "gateway53", "storage53", "network53", "latency53 buffer53"],
    ),
    (
        ("service53 gateway53 storage53 network53 latency53 buffer53", 28),
        ["service53 gateway53", "storage53 network53", "latency53 buffer53"],
    ),
    (
        ("gateway53 storage53 network53 latency53 buffer53 queue53", 6),
        ["gateway53", "storage53", "network53", "latency53", "buffer53", "queue53"],
    ),
    (
        ("gateway53 storage53 network53 latency53 buffer53 queue53", 10),
        ["gateway53", "storage53", "network53", "latency53", "buffer53", "queue53"],
    ),
    (
        ("gateway53 storage53 network53 latency53 buffer53 queue53", 18),
        ["gateway53", "storage53", "network53", "latency53 buffer53", "queue53"],
    ),
    (
        ("gateway53 storage53 network53 latency53 buffer53 queue53", 28),
        ["gateway53 storage53", "network53 latency53 buffer53", "queue53"],
    ),
    (
        ("storage53 network53 latency53 buffer53 queue53 worker53", 6),
        ["storage53", "network53", "latency53", "buffer53", "queue53", "worker53"],
    ),
    (
        ("storage53 network53 latency53 buffer53 queue53 worker53", 10),
        ["storage53", "network53", "latency53", "buffer53", "queue53", "worker53"],
    ),
    (
        ("storage53 network53 latency53 buffer53 queue53 worker53", 18),
        ["storage53", "network53", "latency53 buffer53", "queue53 worker53"],
    ),
    (
        ("storage53 network53 latency53 buffer53 queue53 worker53", 28),
        ["storage53 network53", "latency53 buffer53 queue53", "worker53"],
    ),
    (
        ("network53 latency53 buffer53 queue53 worker53 kernel53", 6),
        ["network53", "latency53", "buffer53", "queue53", "worker53", "kernel53"],
    ),
    (
        ("network53 latency53 buffer53 queue53 worker53 kernel53", 10),
        ["network53", "latency53", "buffer53", "queue53", "worker53", "kernel53"],
    ),
    (
        ("network53 latency53 buffer53 queue53 worker53 kernel53", 18),
        ["network53", "latency53 buffer53", "queue53 worker53", "kernel53"],
    ),
    (
        ("network53 latency53 buffer53 queue53 worker53 kernel53", 28),
        ["network53 latency53 buffer53", "queue53 worker53 kernel53"],
    ),
    (
        ("latency53 buffer53 queue53 worker53 kernel53 signal53", 6),
        ["latency53", "buffer53", "queue53", "worker53", "kernel53", "signal53"],
    ),
    (
        ("latency53 buffer53 queue53 worker53 kernel53 signal53", 10),
        ["latency53", "buffer53", "queue53", "worker53", "kernel53", "signal53"],
    ),
    (
        ("latency53 buffer53 queue53 worker53 kernel53 signal53", 18),
        ["latency53 buffer53", "queue53 worker53", "kernel53 signal53"],
    ),
    (
        ("latency53 buffer53 queue53 worker53 kernel53 signal53", 28),
        ["latency53 buffer53 queue53", "worker53 kernel53 signal53"],
    ),
    (
        ("buffer53 queue53 worker53 kernel53 signal53 packet53", 6),
        ["buffer53", "queue53", "worker53", "kernel53", "signal53", "packet53"],
    ),
    (
        ("buffer53 queue53 worker53 kernel53 signal53 packet53", 10),
        ["buffer53", "queue53", "worker53", "kernel53", "signal53", "packet53"],
    ),
    (
        ("buffer53 queue53 worker53 kernel53 signal53 packet53", 18),
        ["buffer53 queue53", "worker53 kernel53", "signal53 packet53"],
    ),
    (
        ("buffer53 queue53 worker53 kernel53 signal53 packet53", 28),
        ["buffer53 queue53 worker53", "kernel53 signal53 packet53"],
    ),
    (
        ("queue53 worker53 kernel53 signal53 packet53 router53", 6),
        ["queue53", "worker53", "kernel53", "signal53", "packet53", "router53"],
    ),
    (
        ("queue53 worker53 kernel53 signal53 packet53 router53", 10),
        ["queue53", "worker53", "kernel53", "signal53", "packet53", "router53"],
    ),
    (
        ("queue53 worker53 kernel53 signal53 packet53 router53", 18),
        ["queue53 worker53", "kernel53 signal53", "packet53 router53"],
    ),
    (
        ("queue53 worker53 kernel53 signal53 packet53 router53", 28),
        ["queue53 worker53 kernel53", "signal53 packet53 router53"],
    ),
    (
        ("worker53 kernel53 signal53 packet53 router53 cluster53", 6),
        ["worker53", "kernel53", "signal53", "packet53", "router53", "cluster53"],
    ),
    (
        ("worker53 kernel53 signal53 packet53 router53 cluster53", 10),
        ["worker53", "kernel53", "signal53", "packet53", "router53", "cluster53"],
    ),
    (
        ("worker53 kernel53 signal53 packet53 router53 cluster53", 18),
        ["worker53 kernel53", "signal53 packet53", "router53 cluster53"],
    ),
    (
        ("worker53 kernel53 signal53 packet53 router53 cluster53", 28),
        ["worker53 kernel53 signal53", "packet53 router53 cluster53"],
    ),
    (
        ("kernel53 signal53 packet53 router53 cluster53 mirror53", 6),
        ["kernel53", "signal53", "packet53", "router53", "cluster53", "mirror53"],
    ),
    (
        ("kernel53 signal53 packet53 router53 cluster53 mirror53", 10),
        ["kernel53", "signal53", "packet53", "router53", "cluster53", "mirror53"],
    ),
    (
        ("kernel53 signal53 packet53 router53 cluster53 mirror53", 18),
        ["kernel53 signal53", "packet53 router53", "cluster53 mirror53"],
    ),
    (
        ("kernel53 signal53 packet53 router53 cluster53 mirror53", 28),
        ["kernel53 signal53 packet53", "router53 cluster53 mirror53"],
    ),
    (
        ("signal53 packet53 router53 cluster53 mirror53 filter53", 6),
        ["signal53", "packet53", "router53", "cluster53", "mirror53", "filter53"],
    ),
    (
        ("signal53 packet53 router53 cluster53 mirror53 filter53", 10),
        ["signal53", "packet53", "router53", "cluster53", "mirror53", "filter53"],
    ),
    (
        ("signal53 packet53 router53 cluster53 mirror53 filter53", 18),
        ["signal53 packet53", "router53 cluster53", "mirror53 filter53"],
    ),
    (
        ("signal53 packet53 router53 cluster53 mirror53 filter53", 28),
        ["signal53 packet53 router53", "cluster53 mirror53 filter53"],
    ),
    (
        ("packet53 router53 cluster53 mirror53 filter53 ranking53", 6),
        ["packet53", "router53", "cluster53", "mirror53", "filter53", "ranking53"],
    ),
    (
        ("packet53 router53 cluster53 mirror53 filter53 ranking53", 10),
        ["packet53", "router53", "cluster53", "mirror53", "filter53", "ranking53"],
    ),
    (
        ("packet53 router53 cluster53 mirror53 filter53 ranking53", 18),
        ["packet53 router53", "cluster53 mirror53", "filter53 ranking53"],
    ),
    (
        ("packet53 router53 cluster53 mirror53 filter53 ranking53", 28),
        ["packet53 router53 cluster53", "mirror53 filter53 ranking53"],
    ),
    (
        ("router53 cluster53 mirror53 filter53 ranking53 encoding53", 6),
        ["router53", "cluster53", "mirror53", "filter53", "ranking53", "encoding53"],
    ),
    (
        ("router53 cluster53 mirror53 filter53 ranking53 encoding53", 10),
        ["router53", "cluster53", "mirror53", "filter53", "ranking53", "encoding53"],
    ),
    (
        ("router53 cluster53 mirror53 filter53 ranking53 encoding53", 18),
        ["router53 cluster53", "mirror53 filter53", "ranking53", "encoding53"],
    ),
    (
        ("router53 cluster53 mirror53 filter53 ranking53 encoding53", 28),
        ["router53 cluster53 mirror53", "filter53 ranking53", "encoding53"],
    ),
    (
        ("cluster53 mirror53 filter53 ranking53 encoding53 mapping53", 6),
        ["cluster53", "mirror53", "filter53", "ranking53", "encoding53", "mapping53"],
    ),
    (
        ("cluster53 mirror53 filter53 ranking53 encoding53 mapping53", 10),
        ["cluster53", "mirror53", "filter53", "ranking53", "encoding53", "mapping53"],
    ),
    (
        ("cluster53 mirror53 filter53 ranking53 encoding53 mapping53", 18),
        ["cluster53 mirror53", "filter53 ranking53", "encoding53", "mapping53"],
    ),
    (
        ("cluster53 mirror53 filter53 ranking53 encoding53 mapping53", 28),
        ["cluster53 mirror53 filter53", "ranking53 encoding53", "mapping53"],
    ),
    (
        ("mirror53 filter53 ranking53 encoding53 mapping53 record53", 6),
        ["mirror53", "filter53", "ranking53", "encoding53", "mapping53", "record53"],
    ),
    (
        ("mirror53 filter53 ranking53 encoding53 mapping53 record53", 10),
        ["mirror53", "filter53", "ranking53", "encoding53", "mapping53", "record53"],
    ),
    (
        ("mirror53 filter53 ranking53 encoding53 mapping53 record53", 18),
        ["mirror53 filter53", "ranking53", "encoding53", "mapping53 record53"],
    ),
    (
        ("mirror53 filter53 ranking53 encoding53 mapping53 record53", 28),
        ["mirror53 filter53 ranking53", "encoding53 mapping53", "record53"],
    ),
    (
        ("filter53 ranking53 encoding53 mapping53 record53 candle53", 6),
        ["filter53", "ranking53", "encoding53", "mapping53", "record53", "candle53"],
    ),
    (
        ("filter53 ranking53 encoding53 mapping53 record53 candle53", 10),
        ["filter53", "ranking53", "encoding53", "mapping53", "record53", "candle53"],
    ),
    (
        ("filter53 ranking53 encoding53 mapping53 record53 candle53", 18),
        ["filter53 ranking53", "encoding53", "mapping53 record53", "candle53"],
    ),
    (
        ("filter53 ranking53 encoding53 mapping53 record53 candle53", 28),
        ["filter53 ranking53", "encoding53 mapping53", "record53 candle53"],
    ),
    (
        ("ranking53 encoding53 mapping53 record53 candle53 thread53", 6),
        ["ranking53", "encoding53", "mapping53", "record53", "candle53", "thread53"],
    ),
    (
        ("ranking53 encoding53 mapping53 record53 candle53 thread53", 10),
        ["ranking53", "encoding53", "mapping53", "record53", "candle53", "thread53"],
    ),
    (
        ("ranking53 encoding53 mapping53 record53 candle53 thread53", 18),
        ["ranking53", "encoding53", "mapping53 record53", "candle53 thread53"],
    ),
    (
        ("ranking53 encoding53 mapping53 record53 candle53 thread53", 28),
        ["ranking53 encoding53", "mapping53 record53 candle53", "thread53"],
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
