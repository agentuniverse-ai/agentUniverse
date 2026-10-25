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
        ("round 37: the quick brown fox jumps over the lazy dog", 4),
        ["round", "37:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 37: the quick brown fox jumps over the lazy dog", 8),
        ["round", "37: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 37: the quick brown fox jumps over the lazy dog", 12),
        ["round 37:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 37: the quick brown fox jumps over the lazy dog", 16),
        ["round 37: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 37: the quick brown fox jumps over the lazy dog", 24),
        ["round 37: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 37: the quick brown fox jumps over the lazy dog", 32),
        ["round 37: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 37: agentuniverse is a framework for multi agents", 4),
        ["round", "37:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 37: agentuniverse is a framework for multi agents", 8),
        ["round", "37:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 37: agentuniverse is a framework for multi agents", 12),
        ["round 37:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 37: agentuniverse is a framework for multi agents", 16),
        ["round 37:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 37: agentuniverse is a framework for multi agents", 24),
        ["round 37: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 37: agentuniverse is a framework for multi agents", 32),
        ["round 37: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 37: knowledge stored as vectors enables retrieval", 4),
        ["round", "37:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 37: knowledge stored as vectors enables retrieval", 8),
        ["round", "37:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 37: knowledge stored as vectors enables retrieval", 12),
        ["round 37:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 37: knowledge stored as vectors enables retrieval", 16),
        ["round 37:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 37: knowledge stored as vectors enables retrieval", 24),
        ["round 37: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 37: knowledge stored as vectors enables retrieval", 32),
        ["round 37: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 37: the processor reads the record then stops", 4),
        ["round", "37:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 37: the processor reads the record then stops", 8),
        ["round", "37: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 37: the processor reads the record then stops", 12),
        ["round 37:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 37: the processor reads the record then stops", 16),
        ["round 37: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 37: the processor reads the record then stops", 24),
        ["round 37: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 37: the processor reads the record then stops", 32),
        ["round 37: the processor reads", "the record then stops"],
    ),
    (
        ("round 37: a worker pulls the next task from the queue", 4),
        ["round", "37:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 37: a worker pulls the next task from the queue", 8),
        ["round", "37: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 37: a worker pulls the next task from the queue", 12),
        ["round 37: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 37: a worker pulls the next task from the queue", 16),
        ["round 37: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 37: a worker pulls the next task from the queue", 24),
        ["round 37: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 37: a worker pulls the next task from the queue", 32),
        ["round 37: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 37: signals travel through the network layer", 4),
        ["round", "37:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 37: signals travel through the network layer", 8),
        ["round", "37:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 37: signals travel through the network layer", 12),
        ["round 37:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 37: signals travel through the network layer", 16),
        ["round 37:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 37: signals travel through the network layer", 24),
        ["round 37: signals travel", "through the network", "layer"],
    ),
    (
        ("round 37: signals travel through the network layer", 32),
        ["round 37: signals travel through", "the network layer"],
    ),
    (
        ("round 37: the gateway routes each request by policy", 4),
        ["round", "37:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 37: the gateway routes each request by policy", 8),
        ["round", "37: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 37: the gateway routes each request by policy", 12),
        ["round 37:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 37: the gateway routes each request by policy", 16),
        ["round 37: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 37: the gateway routes each request by policy", 24),
        ["round 37: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 37: the gateway routes each request by policy", 32),
        ["round 37: the gateway routes", "each request by policy"],
    ),
    (
        ("round 37: memory grows until the buffer is full", 4),
        ["round", "37:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 37: memory grows until the buffer is full", 8),
        ["round", "37:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 37: memory grows until the buffer is full", 12),
        ["round 37:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 37: memory grows until the buffer is full", 16),
        ["round 37: memory", "grows until the", "buffer is full"],
    ),
    (("round 37: memory grows until the buffer is full", 24), ["round 37: memory grows", "until the buffer is full"]),
    (("round 37: memory grows until the buffer is full", 32), ["round 37: memory grows until the", "buffer is full"]),
    (
        ("round 37: the cluster mirrors every packet twice", 4),
        ["round", "37:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 37: the cluster mirrors every packet twice", 8),
        ["round", "37: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 37: the cluster mirrors every packet twice", 12),
        ["round 37:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 37: the cluster mirrors every packet twice", 16),
        ["round 37: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 37: the cluster mirrors every packet twice", 24),
        ["round 37: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 37: the cluster mirrors every packet twice", 32), ["round 37: the cluster mirrors", "every packet twice"]),
    (
        ("round 37: ranking uses tokens learned from the corpus", 4),
        ["round", "37:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 37: ranking uses tokens learned from the corpus", 8),
        ["round", "37:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 37: ranking uses tokens learned from the corpus", 12),
        ["round 37:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 37: ranking uses tokens learned from the corpus", 16),
        ["round 37:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 37: ranking uses tokens learned from the corpus", 24),
        ["round 37: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 37: ranking uses tokens learned from the corpus", 32),
        ["round 37: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 37: a long session ends when the candle dies", 4),
        ["round", "37:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 37: a long session ends when the candle dies", 8),
        ["round", "37: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 37: a long session ends when the candle dies", 12),
        ["round 37: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 37: a long session ends when the candle dies", 16),
        ["round 37: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 37: a long session ends when the candle dies", 24),
        ["round 37: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 37: a long session ends when the candle dies", 32),
        ["round 37: a long session ends", "when the candle dies"],
    ),
    (
        ("round 37: encode the prompt then map the result", 4),
        ["round", "37:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 37: encode the prompt then map the result", 8),
        ["round", "37:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 37: encode the prompt then map the result", 12),
        ["round 37:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 37: encode the prompt then map the result", 16),
        ["round 37: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 37: encode the prompt then map the result", 24),
        ["round 37: encode the", "prompt then map the", "result"],
    ),
    (("round 37: encode the prompt then map the result", 32), ["round 37: encode the prompt then", "map the result"]),
    (
        ("round 37: the kernel wakes the worker at dawn", 4),
        ["round", "37:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 37: the kernel wakes the worker at dawn", 8),
        ["round", "37: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 37: the kernel wakes the worker at dawn", 12),
        ["round 37:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 37: the kernel wakes the worker at dawn", 16), ["round 37: the", "kernel wakes the", "worker at dawn"]),
    (("round 37: the kernel wakes the worker at dawn", 24), ["round 37: the kernel", "wakes the worker at dawn"]),
    (("round 37: the kernel wakes the worker at dawn", 32), ["round 37: the kernel wakes the", "worker at dawn"]),
    (
        ("round 37: service latency drops after the patch", 4),
        ["round", "37:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 37: service latency drops after the patch", 8),
        ["round", "37:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 37: service latency drops after the patch", 12),
        ["round 37:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 37: service latency drops after the patch", 16),
        ["round 37:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 37: service latency drops after the patch", 24),
        ["round 37: service", "latency drops after the", "patch"],
    ),
    (("round 37: service latency drops after the patch", 32), ["round 37: service latency drops", "after the patch"]),
    (
        ("round 37: the library caches every vector it sees", 4),
        ["round", "37:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 37: the library caches every vector it sees", 8),
        ["round", "37: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 37: the library caches every vector it sees", 12),
        ["round 37:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 37: the library caches every vector it sees", 16),
        ["round 37: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 37: the library caches every vector it sees", 24),
        ["round 37: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 37: the library caches every vector it sees", 32),
        ["round 37: the library caches", "every vector it sees"],
    ),
    (
        ("round 37: agents argue then the debate resolves", 4),
        ["round", "37:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 37: agents argue then the debate resolves", 8),
        ["round", "37:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 37: agents argue then the debate resolves", 12),
        ["round 37:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 37: agents argue then the debate resolves", 16),
        ["round 37: agents", "argue then the", "debate resolves"],
    ),
    (("round 37: agents argue then the debate resolves", 24), ["round 37: agents argue", "then the debate resolves"]),
    (("round 37: agents argue then the debate resolves", 32), ["round 37: agents argue then the", "debate resolves"]),
    (
        ("round 37: the filter keeps only strong matches", 4),
        ["round", "37:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 37: the filter keeps only strong matches", 8),
        ["round", "37: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 37: the filter keeps only strong matches", 12),
        ["round 37:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 37: the filter keeps only strong matches", 16),
        ["round 37: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 37: the filter keeps only strong matches", 24), ["round 37: the filter", "keeps only strong", "matches"]),
    (("round 37: the filter keeps only strong matches", 32), ["round 37: the filter keeps only", "strong matches"]),
    (
        ("round 37: the model answers with a short reply", 4),
        ["round", "37:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 37: the model answers with a short reply", 8),
        ["round", "37: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 37: the model answers with a short reply", 12),
        ["round 37:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 37: the model answers with a short reply", 16),
        ["round 37: the", "model answers", "with a short", "reply"],
    ),
    (("round 37: the model answers with a short reply", 24), ["round 37: the model", "answers with a short", "reply"]),
    (("round 37: the model answers with a short reply", 32), ["round 37: the model answers with", "a short reply"]),
    (
        ("round 37: the recorder stores the reasoning trace", 4),
        ["round", "37:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 37: the recorder stores the reasoning trace", 8),
        ["round", "37: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 37: the recorder stores the reasoning trace", 12),
        ["round 37:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 37: the recorder stores the reasoning trace", 16),
        ["round 37: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 37: the recorder stores the reasoning trace", 24),
        ["round 37: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 37: the recorder stores the reasoning trace", 32),
        ["round 37: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 37: the angel watches the processor run", 4),
        ["round", "37:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 37: the angel watches the processor run", 8),
        ["round", "37: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 37: the angel watches the processor run", 12),
        ["round 37:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 37: the angel watches the processor run", 16), ["round 37: the", "angel watches", "the processor", "run"]),
    (("round 37: the angel watches the processor run", 24), ["round 37: the angel", "watches the processor", "run"]),
    (("round 37: the angel watches the processor run", 32), ["round 37: the angel watches the", "processor run"]),
    (
        ("round 37: angle of the vector decides the match", 4),
        ["round", "37:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 37: angle of the vector decides the match", 8),
        ["round", "37:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 37: angle of the vector decides the match", 12),
        ["round 37:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 37: angle of the vector decides the match", 16),
        ["round 37: angle", "of the vector", "decides the", "match"],
    ),
    (("round 37: angle of the vector decides the match", 24), ["round 37: angle of the", "vector decides the match"]),
    (("round 37: angle of the vector decides the match", 32), ["round 37: angle of the vector", "decides the match"]),
    (
        ("round 37: the candle burns twice as long at night", 4),
        ["round", "37:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 37: the candle burns twice as long at night", 8),
        ["round", "37: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 37: the candle burns twice as long at night", 12),
        ["round 37:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 37: the candle burns twice as long at night", 16),
        ["round 37: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 37: the candle burns twice as long at night", 24),
        ["round 37: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 37: the candle burns twice as long at night", 32),
        ["round 37: the candle burns twice", "as long at night"],
    ),
    (
        ("round 37: a mirror of the universe in one line", 4),
        ["round", "37:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 37: a mirror of the universe in one line", 8),
        ["round", "37: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 37: a mirror of the universe in one line", 12),
        ["round 37: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 37: a mirror of the universe in one line", 16),
        ["round 37: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 37: a mirror of the universe in one line", 24), ["round 37: a mirror of", "the universe in one line"]),
    (("round 37: a mirror of the universe in one line", 32), ["round 37: a mirror of the", "universe in one line"]),
    (
        ("round 37: the queue drains before the storm", 4),
        ["round", "37:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 37: the queue drains before the storm", 8),
        ["round", "37: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 37: the queue drains before the storm", 12), ["round 37:", "the queue", "drains", "before the", "storm"]),
    (("round 37: the queue drains before the storm", 16), ["round 37: the", "queue drains", "before the storm"]),
    (("round 37: the queue drains before the storm", 24), ["round 37: the queue", "drains before the storm"]),
    (("round 37: the queue drains before the storm", 32), ["round 37: the queue drains", "before the storm"]),
    (
        ("kitten37 sitting37 agent37 angle37 universe37 memory37", 6),
        ["kitten37", "sitting37", "agent37", "angle37", "universe37", "memory37"],
    ),
    (
        ("kitten37 sitting37 agent37 angle37 universe37 memory37", 10),
        ["kitten37", "sitting37", "agent37", "angle37", "universe37", "memory37"],
    ),
    (
        ("kitten37 sitting37 agent37 angle37 universe37 memory37", 18),
        ["kitten37 sitting37", "agent37 angle37", "universe37", "memory37"],
    ),
    (
        ("kitten37 sitting37 agent37 angle37 universe37 memory37", 28),
        ["kitten37 sitting37 agent37", "angle37 universe37 memory37"],
    ),
    (
        ("sitting37 agent37 angle37 universe37 memory37 stream37", 6),
        ["sitting37", "agent37", "angle37", "universe37", "memory37", "stream37"],
    ),
    (
        ("sitting37 agent37 angle37 universe37 memory37 stream37", 10),
        ["sitting37", "agent37", "angle37", "universe37", "memory37", "stream37"],
    ),
    (
        ("sitting37 agent37 angle37 universe37 memory37 stream37", 18),
        ["sitting37 agent37", "angle37 universe37", "memory37 stream37"],
    ),
    (
        ("sitting37 agent37 angle37 universe37 memory37 stream37", 28),
        ["sitting37 agent37 angle37", "universe37 memory37 stream37"],
    ),
    (
        ("agent37 angle37 universe37 memory37 stream37 context37", 6),
        ["agent37", "angle37", "universe37", "memory37", "stream37", "context37"],
    ),
    (
        ("agent37 angle37 universe37 memory37 stream37 context37", 10),
        ["agent37", "angle37", "universe37", "memory37", "stream37", "context37"],
    ),
    (
        ("agent37 angle37 universe37 memory37 stream37 context37", 18),
        ["agent37 angle37", "universe37", "memory37 stream37", "context37"],
    ),
    (
        ("agent37 angle37 universe37 memory37 stream37 context37", 28),
        ["agent37 angle37 universe37", "memory37 stream37 context37"],
    ),
    (
        ("angle37 universe37 memory37 stream37 context37 knowledge37", 6),
        ["angle37", "universe37", "memory37", "stream37", "context37", "knowledge37"],
    ),
    (
        ("angle37 universe37 memory37 stream37 context37 knowledge37", 10),
        ["angle37", "universe37", "memory37", "stream37", "context37", "knowledge37"],
    ),
    (
        ("angle37 universe37 memory37 stream37 context37 knowledge37", 18),
        ["angle37 universe37", "memory37 stream37", "context37", "knowledge37"],
    ),
    (
        ("angle37 universe37 memory37 stream37 context37 knowledge37", 28),
        ["angle37 universe37 memory37", "stream37 context37", "knowledge37"],
    ),
    (
        ("universe37 memory37 stream37 context37 knowledge37 vector37", 6),
        ["universe37", "memory37", "stream37", "context37", "knowledge37", "vector37"],
    ),
    (
        ("universe37 memory37 stream37 context37 knowledge37 vector37", 10),
        ["universe37", "memory37", "stream37", "context37", "knowledge37", "vector37"],
    ),
    (
        ("universe37 memory37 stream37 context37 knowledge37 vector37", 18),
        ["universe37", "memory37 stream37", "context37", "knowledge37", "vector37"],
    ),
    (
        ("universe37 memory37 stream37 context37 knowledge37 vector37", 28),
        ["universe37 memory37 stream37", "context37 knowledge37", "vector37"],
    ),
    (
        ("memory37 stream37 context37 knowledge37 vector37 processor37", 6),
        ["memory37", "stream37", "context37", "knowledge37", "vector37", "processor37"],
    ),
    (
        ("memory37 stream37 context37 knowledge37 vector37 processor37", 10),
        ["memory37", "stream37", "context37", "knowledge37", "vector37", "processor37"],
    ),
    (
        ("memory37 stream37 context37 knowledge37 vector37 processor37", 18),
        ["memory37 stream37", "context37", "knowledge37", "vector37", "processor37"],
    ),
    (
        ("memory37 stream37 context37 knowledge37 vector37 processor37", 28),
        ["memory37 stream37 context37", "knowledge37 vector37", "processor37"],
    ),
    (
        ("stream37 context37 knowledge37 vector37 processor37 reasoning37", 6),
        ["stream37", "context37", "knowledge37", "vector37", "processor37", "reasoning37"],
    ),
    (
        ("stream37 context37 knowledge37 vector37 processor37 reasoning37", 10),
        ["stream37", "context37", "knowledge37", "vector37", "processor37", "reasoning37"],
    ),
    (
        ("stream37 context37 knowledge37 vector37 processor37 reasoning37", 18),
        ["stream37 context37", "knowledge37", "vector37", "processor37", "reasoning37"],
    ),
    (
        ("stream37 context37 knowledge37 vector37 processor37 reasoning37", 28),
        ["stream37 context37", "knowledge37 vector37", "processor37 reasoning37"],
    ),
    (
        ("context37 knowledge37 vector37 processor37 reasoning37 machine37", 6),
        ["context37", "knowledge37", "vector37", "processor37", "reasoning37", "machine37"],
    ),
    (
        ("context37 knowledge37 vector37 processor37 reasoning37 machine37", 10),
        ["context37", "knowledge37", "vector37", "processor37", "reasoning37", "machine37"],
    ),
    (
        ("context37 knowledge37 vector37 processor37 reasoning37 machine37", 18),
        ["context37", "knowledge37", "vector37", "processor37", "reasoning37", "machine37"],
    ),
    (
        ("context37 knowledge37 vector37 processor37 reasoning37 machine37", 28),
        ["context37 knowledge37", "vector37 processor37", "reasoning37 machine37"],
    ),
    (
        ("knowledge37 vector37 processor37 reasoning37 machine37 learning37", 6),
        ["knowledge37", "vector37", "processor37", "reasoning37", "machine37", "learning37"],
    ),
    (
        ("knowledge37 vector37 processor37 reasoning37 machine37 learning37", 10),
        ["knowledge37", "vector37", "processor37", "reasoning37", "machine37", "learning37"],
    ),
    (
        ("knowledge37 vector37 processor37 reasoning37 machine37 learning37", 18),
        ["knowledge37", "vector37", "processor37", "reasoning37", "machine37", "learning37"],
    ),
    (
        ("knowledge37 vector37 processor37 reasoning37 machine37 learning37", 28),
        ["knowledge37 vector37", "processor37 reasoning37", "machine37 learning37"],
    ),
    (
        ("vector37 processor37 reasoning37 machine37 learning37 model37", 6),
        ["vector37", "processor37", "reasoning37", "machine37", "learning37", "model37"],
    ),
    (
        ("vector37 processor37 reasoning37 machine37 learning37 model37", 10),
        ["vector37", "processor37", "reasoning37", "machine37", "learning37", "model37"],
    ),
    (
        ("vector37 processor37 reasoning37 machine37 learning37 model37", 18),
        ["vector37", "processor37", "reasoning37", "machine37", "learning37 model37"],
    ),
    (
        ("vector37 processor37 reasoning37 machine37 learning37 model37", 28),
        ["vector37 processor37", "reasoning37 machine37", "learning37 model37"],
    ),
    (
        ("processor37 reasoning37 machine37 learning37 model37 token37", 6),
        ["processor37", "reasoning37", "machine37", "learning37", "model37", "token37"],
    ),
    (
        ("processor37 reasoning37 machine37 learning37 model37 token37", 10),
        ["processor37", "reasoning37", "machine37", "learning37", "model37", "token37"],
    ),
    (
        ("processor37 reasoning37 machine37 learning37 model37 token37", 18),
        ["processor37", "reasoning37", "machine37", "learning37 model37", "token37"],
    ),
    (
        ("processor37 reasoning37 machine37 learning37 model37 token37", 28),
        ["processor37 reasoning37", "machine37 learning37 model37", "token37"],
    ),
    (
        ("reasoning37 machine37 learning37 model37 token37 prompt37", 6),
        ["reasoning37", "machine37", "learning37", "model37", "token37", "prompt37"],
    ),
    (
        ("reasoning37 machine37 learning37 model37 token37 prompt37", 10),
        ["reasoning37", "machine37", "learning37", "model37", "token37", "prompt37"],
    ),
    (
        ("reasoning37 machine37 learning37 model37 token37 prompt37", 18),
        ["reasoning37", "machine37", "learning37 model37", "token37 prompt37"],
    ),
    (
        ("reasoning37 machine37 learning37 model37 token37 prompt37", 28),
        ["reasoning37 machine37", "learning37 model37 token37", "prompt37"],
    ),
    (
        ("machine37 learning37 model37 token37 prompt37 session37", 6),
        ["machine37", "learning37", "model37", "token37", "prompt37", "session37"],
    ),
    (
        ("machine37 learning37 model37 token37 prompt37 session37", 10),
        ["machine37", "learning37", "model37", "token37", "prompt37", "session37"],
    ),
    (
        ("machine37 learning37 model37 token37 prompt37 session37", 18),
        ["machine37", "learning37 model37", "token37 prompt37", "session37"],
    ),
    (
        ("machine37 learning37 model37 token37 prompt37 session37", 28),
        ["machine37 learning37 model37", "token37 prompt37 session37"],
    ),
    (
        ("learning37 model37 token37 prompt37 session37 library37", 6),
        ["learning37", "model37", "token37", "prompt37", "session37", "library37"],
    ),
    (
        ("learning37 model37 token37 prompt37 session37 library37", 10),
        ["learning37", "model37", "token37", "prompt37", "session37", "library37"],
    ),
    (
        ("learning37 model37 token37 prompt37 session37 library37", 18),
        ["learning37 model37", "token37 prompt37", "session37", "library37"],
    ),
    (
        ("learning37 model37 token37 prompt37 session37 library37", 28),
        ["learning37 model37 token37", "prompt37 session37 library37"],
    ),
    (
        ("model37 token37 prompt37 session37 library37 service37", 6),
        ["model37", "token37", "prompt37", "session37", "library37", "service37"],
    ),
    (
        ("model37 token37 prompt37 session37 library37 service37", 10),
        ["model37", "token37", "prompt37", "session37", "library37", "service37"],
    ),
    (
        ("model37 token37 prompt37 session37 library37 service37", 18),
        ["model37 token37", "prompt37 session37", "library37", "service37"],
    ),
    (
        ("model37 token37 prompt37 session37 library37 service37", 28),
        ["model37 token37 prompt37", "session37 library37", "service37"],
    ),
    (
        ("token37 prompt37 session37 library37 service37 gateway37", 6),
        ["token37", "prompt37", "session37", "library37", "service37", "gateway37"],
    ),
    (
        ("token37 prompt37 session37 library37 service37 gateway37", 10),
        ["token37", "prompt37", "session37", "library37", "service37", "gateway37"],
    ),
    (
        ("token37 prompt37 session37 library37 service37 gateway37", 18),
        ["token37 prompt37", "session37", "library37", "service37", "gateway37"],
    ),
    (
        ("token37 prompt37 session37 library37 service37 gateway37", 28),
        ["token37 prompt37 session37", "library37 service37", "gateway37"],
    ),
    (
        ("prompt37 session37 library37 service37 gateway37 storage37", 6),
        ["prompt37", "session37", "library37", "service37", "gateway37", "storage37"],
    ),
    (
        ("prompt37 session37 library37 service37 gateway37 storage37", 10),
        ["prompt37", "session37", "library37", "service37", "gateway37", "storage37"],
    ),
    (
        ("prompt37 session37 library37 service37 gateway37 storage37", 18),
        ["prompt37 session37", "library37", "service37", "gateway37", "storage37"],
    ),
    (
        ("prompt37 session37 library37 service37 gateway37 storage37", 28),
        ["prompt37 session37 library37", "service37 gateway37", "storage37"],
    ),
    (
        ("session37 library37 service37 gateway37 storage37 network37", 6),
        ["session37", "library37", "service37", "gateway37", "storage37", "network37"],
    ),
    (
        ("session37 library37 service37 gateway37 storage37 network37", 10),
        ["session37", "library37", "service37", "gateway37", "storage37", "network37"],
    ),
    (
        ("session37 library37 service37 gateway37 storage37 network37", 18),
        ["session37", "library37", "service37", "gateway37", "storage37", "network37"],
    ),
    (
        ("session37 library37 service37 gateway37 storage37 network37", 28),
        ["session37 library37", "service37 gateway37", "storage37 network37"],
    ),
    (
        ("library37 service37 gateway37 storage37 network37 latency37", 6),
        ["library37", "service37", "gateway37", "storage37", "network37", "latency37"],
    ),
    (
        ("library37 service37 gateway37 storage37 network37 latency37", 10),
        ["library37", "service37", "gateway37", "storage37", "network37", "latency37"],
    ),
    (
        ("library37 service37 gateway37 storage37 network37 latency37", 18),
        ["library37", "service37", "gateway37", "storage37", "network37", "latency37"],
    ),
    (
        ("library37 service37 gateway37 storage37 network37 latency37", 28),
        ["library37 service37", "gateway37 storage37", "network37 latency37"],
    ),
    (
        ("service37 gateway37 storage37 network37 latency37 buffer37", 6),
        ["service37", "gateway37", "storage37", "network37", "latency37", "buffer37"],
    ),
    (
        ("service37 gateway37 storage37 network37 latency37 buffer37", 10),
        ["service37", "gateway37", "storage37", "network37", "latency37", "buffer37"],
    ),
    (
        ("service37 gateway37 storage37 network37 latency37 buffer37", 18),
        ["service37", "gateway37", "storage37", "network37", "latency37 buffer37"],
    ),
    (
        ("service37 gateway37 storage37 network37 latency37 buffer37", 28),
        ["service37 gateway37", "storage37 network37", "latency37 buffer37"],
    ),
    (
        ("gateway37 storage37 network37 latency37 buffer37 queue37", 6),
        ["gateway37", "storage37", "network37", "latency37", "buffer37", "queue37"],
    ),
    (
        ("gateway37 storage37 network37 latency37 buffer37 queue37", 10),
        ["gateway37", "storage37", "network37", "latency37", "buffer37", "queue37"],
    ),
    (
        ("gateway37 storage37 network37 latency37 buffer37 queue37", 18),
        ["gateway37", "storage37", "network37", "latency37 buffer37", "queue37"],
    ),
    (
        ("gateway37 storage37 network37 latency37 buffer37 queue37", 28),
        ["gateway37 storage37", "network37 latency37 buffer37", "queue37"],
    ),
    (
        ("storage37 network37 latency37 buffer37 queue37 worker37", 6),
        ["storage37", "network37", "latency37", "buffer37", "queue37", "worker37"],
    ),
    (
        ("storage37 network37 latency37 buffer37 queue37 worker37", 10),
        ["storage37", "network37", "latency37", "buffer37", "queue37", "worker37"],
    ),
    (
        ("storage37 network37 latency37 buffer37 queue37 worker37", 18),
        ["storage37", "network37", "latency37 buffer37", "queue37 worker37"],
    ),
    (
        ("storage37 network37 latency37 buffer37 queue37 worker37", 28),
        ["storage37 network37", "latency37 buffer37 queue37", "worker37"],
    ),
    (
        ("network37 latency37 buffer37 queue37 worker37 kernel37", 6),
        ["network37", "latency37", "buffer37", "queue37", "worker37", "kernel37"],
    ),
    (
        ("network37 latency37 buffer37 queue37 worker37 kernel37", 10),
        ["network37", "latency37", "buffer37", "queue37", "worker37", "kernel37"],
    ),
    (
        ("network37 latency37 buffer37 queue37 worker37 kernel37", 18),
        ["network37", "latency37 buffer37", "queue37 worker37", "kernel37"],
    ),
    (
        ("network37 latency37 buffer37 queue37 worker37 kernel37", 28),
        ["network37 latency37 buffer37", "queue37 worker37 kernel37"],
    ),
    (
        ("latency37 buffer37 queue37 worker37 kernel37 signal37", 6),
        ["latency37", "buffer37", "queue37", "worker37", "kernel37", "signal37"],
    ),
    (
        ("latency37 buffer37 queue37 worker37 kernel37 signal37", 10),
        ["latency37", "buffer37", "queue37", "worker37", "kernel37", "signal37"],
    ),
    (
        ("latency37 buffer37 queue37 worker37 kernel37 signal37", 18),
        ["latency37 buffer37", "queue37 worker37", "kernel37 signal37"],
    ),
    (
        ("latency37 buffer37 queue37 worker37 kernel37 signal37", 28),
        ["latency37 buffer37 queue37", "worker37 kernel37 signal37"],
    ),
    (
        ("buffer37 queue37 worker37 kernel37 signal37 packet37", 6),
        ["buffer37", "queue37", "worker37", "kernel37", "signal37", "packet37"],
    ),
    (
        ("buffer37 queue37 worker37 kernel37 signal37 packet37", 10),
        ["buffer37", "queue37", "worker37", "kernel37", "signal37", "packet37"],
    ),
    (
        ("buffer37 queue37 worker37 kernel37 signal37 packet37", 18),
        ["buffer37 queue37", "worker37 kernel37", "signal37 packet37"],
    ),
    (
        ("buffer37 queue37 worker37 kernel37 signal37 packet37", 28),
        ["buffer37 queue37 worker37", "kernel37 signal37 packet37"],
    ),
    (
        ("queue37 worker37 kernel37 signal37 packet37 router37", 6),
        ["queue37", "worker37", "kernel37", "signal37", "packet37", "router37"],
    ),
    (
        ("queue37 worker37 kernel37 signal37 packet37 router37", 10),
        ["queue37", "worker37", "kernel37", "signal37", "packet37", "router37"],
    ),
    (
        ("queue37 worker37 kernel37 signal37 packet37 router37", 18),
        ["queue37 worker37", "kernel37 signal37", "packet37 router37"],
    ),
    (
        ("queue37 worker37 kernel37 signal37 packet37 router37", 28),
        ["queue37 worker37 kernel37", "signal37 packet37 router37"],
    ),
    (
        ("worker37 kernel37 signal37 packet37 router37 cluster37", 6),
        ["worker37", "kernel37", "signal37", "packet37", "router37", "cluster37"],
    ),
    (
        ("worker37 kernel37 signal37 packet37 router37 cluster37", 10),
        ["worker37", "kernel37", "signal37", "packet37", "router37", "cluster37"],
    ),
    (
        ("worker37 kernel37 signal37 packet37 router37 cluster37", 18),
        ["worker37 kernel37", "signal37 packet37", "router37 cluster37"],
    ),
    (
        ("worker37 kernel37 signal37 packet37 router37 cluster37", 28),
        ["worker37 kernel37 signal37", "packet37 router37 cluster37"],
    ),
    (
        ("kernel37 signal37 packet37 router37 cluster37 mirror37", 6),
        ["kernel37", "signal37", "packet37", "router37", "cluster37", "mirror37"],
    ),
    (
        ("kernel37 signal37 packet37 router37 cluster37 mirror37", 10),
        ["kernel37", "signal37", "packet37", "router37", "cluster37", "mirror37"],
    ),
    (
        ("kernel37 signal37 packet37 router37 cluster37 mirror37", 18),
        ["kernel37 signal37", "packet37 router37", "cluster37 mirror37"],
    ),
    (
        ("kernel37 signal37 packet37 router37 cluster37 mirror37", 28),
        ["kernel37 signal37 packet37", "router37 cluster37 mirror37"],
    ),
    (
        ("signal37 packet37 router37 cluster37 mirror37 filter37", 6),
        ["signal37", "packet37", "router37", "cluster37", "mirror37", "filter37"],
    ),
    (
        ("signal37 packet37 router37 cluster37 mirror37 filter37", 10),
        ["signal37", "packet37", "router37", "cluster37", "mirror37", "filter37"],
    ),
    (
        ("signal37 packet37 router37 cluster37 mirror37 filter37", 18),
        ["signal37 packet37", "router37 cluster37", "mirror37 filter37"],
    ),
    (
        ("signal37 packet37 router37 cluster37 mirror37 filter37", 28),
        ["signal37 packet37 router37", "cluster37 mirror37 filter37"],
    ),
    (
        ("packet37 router37 cluster37 mirror37 filter37 ranking37", 6),
        ["packet37", "router37", "cluster37", "mirror37", "filter37", "ranking37"],
    ),
    (
        ("packet37 router37 cluster37 mirror37 filter37 ranking37", 10),
        ["packet37", "router37", "cluster37", "mirror37", "filter37", "ranking37"],
    ),
    (
        ("packet37 router37 cluster37 mirror37 filter37 ranking37", 18),
        ["packet37 router37", "cluster37 mirror37", "filter37 ranking37"],
    ),
    (
        ("packet37 router37 cluster37 mirror37 filter37 ranking37", 28),
        ["packet37 router37 cluster37", "mirror37 filter37 ranking37"],
    ),
    (
        ("router37 cluster37 mirror37 filter37 ranking37 encoding37", 6),
        ["router37", "cluster37", "mirror37", "filter37", "ranking37", "encoding37"],
    ),
    (
        ("router37 cluster37 mirror37 filter37 ranking37 encoding37", 10),
        ["router37", "cluster37", "mirror37", "filter37", "ranking37", "encoding37"],
    ),
    (
        ("router37 cluster37 mirror37 filter37 ranking37 encoding37", 18),
        ["router37 cluster37", "mirror37 filter37", "ranking37", "encoding37"],
    ),
    (
        ("router37 cluster37 mirror37 filter37 ranking37 encoding37", 28),
        ["router37 cluster37 mirror37", "filter37 ranking37", "encoding37"],
    ),
    (
        ("cluster37 mirror37 filter37 ranking37 encoding37 mapping37", 6),
        ["cluster37", "mirror37", "filter37", "ranking37", "encoding37", "mapping37"],
    ),
    (
        ("cluster37 mirror37 filter37 ranking37 encoding37 mapping37", 10),
        ["cluster37", "mirror37", "filter37", "ranking37", "encoding37", "mapping37"],
    ),
    (
        ("cluster37 mirror37 filter37 ranking37 encoding37 mapping37", 18),
        ["cluster37 mirror37", "filter37 ranking37", "encoding37", "mapping37"],
    ),
    (
        ("cluster37 mirror37 filter37 ranking37 encoding37 mapping37", 28),
        ["cluster37 mirror37 filter37", "ranking37 encoding37", "mapping37"],
    ),
    (
        ("mirror37 filter37 ranking37 encoding37 mapping37 record37", 6),
        ["mirror37", "filter37", "ranking37", "encoding37", "mapping37", "record37"],
    ),
    (
        ("mirror37 filter37 ranking37 encoding37 mapping37 record37", 10),
        ["mirror37", "filter37", "ranking37", "encoding37", "mapping37", "record37"],
    ),
    (
        ("mirror37 filter37 ranking37 encoding37 mapping37 record37", 18),
        ["mirror37 filter37", "ranking37", "encoding37", "mapping37 record37"],
    ),
    (
        ("mirror37 filter37 ranking37 encoding37 mapping37 record37", 28),
        ["mirror37 filter37 ranking37", "encoding37 mapping37", "record37"],
    ),
    (
        ("filter37 ranking37 encoding37 mapping37 record37 candle37", 6),
        ["filter37", "ranking37", "encoding37", "mapping37", "record37", "candle37"],
    ),
    (
        ("filter37 ranking37 encoding37 mapping37 record37 candle37", 10),
        ["filter37", "ranking37", "encoding37", "mapping37", "record37", "candle37"],
    ),
    (
        ("filter37 ranking37 encoding37 mapping37 record37 candle37", 18),
        ["filter37 ranking37", "encoding37", "mapping37 record37", "candle37"],
    ),
    (
        ("filter37 ranking37 encoding37 mapping37 record37 candle37", 28),
        ["filter37 ranking37", "encoding37 mapping37", "record37 candle37"],
    ),
    (
        ("ranking37 encoding37 mapping37 record37 candle37 thread37", 6),
        ["ranking37", "encoding37", "mapping37", "record37", "candle37", "thread37"],
    ),
    (
        ("ranking37 encoding37 mapping37 record37 candle37 thread37", 10),
        ["ranking37", "encoding37", "mapping37", "record37", "candle37", "thread37"],
    ),
    (
        ("ranking37 encoding37 mapping37 record37 candle37 thread37", 18),
        ["ranking37", "encoding37", "mapping37 record37", "candle37 thread37"],
    ),
    (
        ("ranking37 encoding37 mapping37 record37 candle37 thread37", 28),
        ["ranking37 encoding37", "mapping37 record37 candle37", "thread37"],
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
