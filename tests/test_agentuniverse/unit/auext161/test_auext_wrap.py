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
        ("round 161: the quick brown fox jumps over the lazy dog", 4),
        ["round", "161:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", 8),
        ["round", "161: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", 12),
        ["round 161:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", 16),
        ["round 161: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", 24),
        ["round 161: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 161: the quick brown fox jumps over the lazy dog", 32),
        ["round 161: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", 4),
        ["round", "161:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", 8),
        ["round", "161:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", 12),
        ["round 161:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", 16),
        ["round 161:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", 24),
        ["round 161: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 161: agentuniverse is a framework for multi agents", 32),
        ["round 161: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", 4),
        ["round", "161:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", 8),
        ["round", "161:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", 12),
        ["round 161:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", 16),
        ["round 161:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", 24),
        ["round 161: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 161: knowledge stored as vectors enables retrieval", 32),
        ["round 161: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 161: the processor reads the record then stops", 4),
        ["round", "161:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 161: the processor reads the record then stops", 8),
        ["round", "161: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 161: the processor reads the record then stops", 12),
        ["round 161:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 161: the processor reads the record then stops", 16),
        ["round 161: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 161: the processor reads the record then stops", 24),
        ["round 161: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 161: the processor reads the record then stops", 32),
        ["round 161: the processor reads", "the record then stops"],
    ),
    (
        ("round 161: a worker pulls the next task from the queue", 4),
        ["round", "161:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 161: a worker pulls the next task from the queue", 8),
        ["round", "161: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 161: a worker pulls the next task from the queue", 12),
        ["round 161: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 161: a worker pulls the next task from the queue", 16),
        ["round 161: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 161: a worker pulls the next task from the queue", 24),
        ["round 161: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 161: a worker pulls the next task from the queue", 32),
        ["round 161: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 161: signals travel through the network layer", 4),
        ["round", "161:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 161: signals travel through the network layer", 8),
        ["round", "161:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 161: signals travel through the network layer", 12),
        ["round 161:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 161: signals travel through the network layer", 16),
        ["round 161:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 161: signals travel through the network layer", 24),
        ["round 161: signals", "travel through the", "network layer"],
    ),
    (
        ("round 161: signals travel through the network layer", 32),
        ["round 161: signals travel", "through the network layer"],
    ),
    (
        ("round 161: the gateway routes each request by policy", 4),
        ["round", "161:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 161: the gateway routes each request by policy", 8),
        ["round", "161: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 161: the gateway routes each request by policy", 12),
        ["round 161:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 161: the gateway routes each request by policy", 16),
        ["round 161: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 161: the gateway routes each request by policy", 24),
        ["round 161: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 161: the gateway routes each request by policy", 32),
        ["round 161: the gateway routes", "each request by policy"],
    ),
    (
        ("round 161: memory grows until the buffer is full", 4),
        ["round", "161:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 161: memory grows until the buffer is full", 8),
        ["round", "161:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 161: memory grows until the buffer is full", 12),
        ["round 161:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 161: memory grows until the buffer is full", 16),
        ["round 161:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 161: memory grows until the buffer is full", 24), ["round 161: memory grows", "until the buffer is full"]),
    (("round 161: memory grows until the buffer is full", 32), ["round 161: memory grows until", "the buffer is full"]),
    (
        ("round 161: the cluster mirrors every packet twice", 4),
        ["round", "161:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 161: the cluster mirrors every packet twice", 8),
        ["round", "161: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 161: the cluster mirrors every packet twice", 12),
        ["round 161:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 161: the cluster mirrors every packet twice", 16),
        ["round 161: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 161: the cluster mirrors every packet twice", 24),
        ["round 161: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 161: the cluster mirrors every packet twice", 32),
        ["round 161: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", 4),
        ["round", "161:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", 8),
        ["round", "161:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", 12),
        ["round 161:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", 16),
        ["round 161:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", 24),
        ["round 161: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 161: ranking uses tokens learned from the corpus", 32),
        ["round 161: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 161: a long session ends when the candle dies", 4),
        ["round", "161:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 161: a long session ends when the candle dies", 8),
        ["round", "161: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 161: a long session ends when the candle dies", 12),
        ["round 161: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 161: a long session ends when the candle dies", 16),
        ["round 161: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 161: a long session ends when the candle dies", 24),
        ["round 161: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 161: a long session ends when the candle dies", 32),
        ["round 161: a long session ends", "when the candle dies"],
    ),
    (
        ("round 161: encode the prompt then map the result", 4),
        ["round", "161:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 161: encode the prompt then map the result", 8),
        ["round", "161:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 161: encode the prompt then map the result", 12),
        ["round 161:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 161: encode the prompt then map the result", 16),
        ["round 161:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 161: encode the prompt then map the result", 24),
        ["round 161: encode the", "prompt then map the", "result"],
    ),
    (("round 161: encode the prompt then map the result", 32), ["round 161: encode the prompt", "then map the result"]),
    (
        ("round 161: the kernel wakes the worker at dawn", 4),
        ["round", "161:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 161: the kernel wakes the worker at dawn", 8),
        ["round", "161: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 161: the kernel wakes the worker at dawn", 12),
        ["round 161:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 161: the kernel wakes the worker at dawn", 16), ["round 161: the", "kernel wakes the", "worker at dawn"]),
    (("round 161: the kernel wakes the worker at dawn", 24), ["round 161: the kernel", "wakes the worker at dawn"]),
    (("round 161: the kernel wakes the worker at dawn", 32), ["round 161: the kernel wakes the", "worker at dawn"]),
    (
        ("round 161: service latency drops after the patch", 4),
        ["round", "161:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 161: service latency drops after the patch", 8),
        ["round", "161:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 161: service latency drops after the patch", 12),
        ["round 161:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 161: service latency drops after the patch", 16),
        ["round 161:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 161: service latency drops after the patch", 24),
        ["round 161: service", "latency drops after the", "patch"],
    ),
    (("round 161: service latency drops after the patch", 32), ["round 161: service latency drops", "after the patch"]),
    (
        ("round 161: the library caches every vector it sees", 4),
        ["round", "161:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 161: the library caches every vector it sees", 8),
        ["round", "161: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 161: the library caches every vector it sees", 12),
        ["round 161:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 161: the library caches every vector it sees", 16),
        ["round 161: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 161: the library caches every vector it sees", 24),
        ["round 161: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 161: the library caches every vector it sees", 32),
        ["round 161: the library caches", "every vector it sees"],
    ),
    (
        ("round 161: agents argue then the debate resolves", 4),
        ["round", "161:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 161: agents argue then the debate resolves", 8),
        ["round", "161:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 161: agents argue then the debate resolves", 12),
        ["round 161:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 161: agents argue then the debate resolves", 16),
        ["round 161:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 161: agents argue then the debate resolves", 24), ["round 161: agents argue", "then the debate resolves"]),
    (("round 161: agents argue then the debate resolves", 32), ["round 161: agents argue then the", "debate resolves"]),
    (
        ("round 161: the filter keeps only strong matches", 4),
        ["round", "161:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 161: the filter keeps only strong matches", 8),
        ["round", "161: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 161: the filter keeps only strong matches", 12),
        ["round 161:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 161: the filter keeps only strong matches", 16),
        ["round 161: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 161: the filter keeps only strong matches", 24),
        ["round 161: the filter", "keeps only strong", "matches"],
    ),
    (("round 161: the filter keeps only strong matches", 32), ["round 161: the filter keeps only", "strong matches"]),
    (
        ("round 161: the model answers with a short reply", 4),
        ["round", "161:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 161: the model answers with a short reply", 8),
        ["round", "161: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 161: the model answers with a short reply", 12),
        ["round 161:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 161: the model answers with a short reply", 16),
        ["round 161: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 161: the model answers with a short reply", 24),
        ["round 161: the model", "answers with a short", "reply"],
    ),
    (("round 161: the model answers with a short reply", 32), ["round 161: the model answers", "with a short reply"]),
    (
        ("round 161: the recorder stores the reasoning trace", 4),
        ["round", "161:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 161: the recorder stores the reasoning trace", 8),
        ["round", "161: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 161: the recorder stores the reasoning trace", 12),
        ["round 161:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 161: the recorder stores the reasoning trace", 16),
        ["round 161: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 161: the recorder stores the reasoning trace", 24),
        ["round 161: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 161: the recorder stores the reasoning trace", 32),
        ["round 161: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 161: the angel watches the processor run", 4),
        ["round", "161:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 161: the angel watches the processor run", 8),
        ["round", "161: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 161: the angel watches the processor run", 12),
        ["round 161:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 161: the angel watches the processor run", 16),
        ["round 161: the", "angel watches", "the processor", "run"],
    ),
    (("round 161: the angel watches the processor run", 24), ["round 161: the angel", "watches the processor", "run"]),
    (("round 161: the angel watches the processor run", 32), ["round 161: the angel watches the", "processor run"]),
    (
        ("round 161: angle of the vector decides the match", 4),
        ["round", "161:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 161: angle of the vector decides the match", 8),
        ["round", "161:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 161: angle of the vector decides the match", 12),
        ["round 161:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 161: angle of the vector decides the match", 16),
        ["round 161: angle", "of the vector", "decides the", "match"],
    ),
    (("round 161: angle of the vector decides the match", 24), ["round 161: angle of the", "vector decides the match"]),
    (("round 161: angle of the vector decides the match", 32), ["round 161: angle of the vector", "decides the match"]),
    (
        ("round 161: the candle burns twice as long at night", 4),
        ["round", "161:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 161: the candle burns twice as long at night", 8),
        ["round", "161: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 161: the candle burns twice as long at night", 12),
        ["round 161:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 161: the candle burns twice as long at night", 16),
        ["round 161: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 161: the candle burns twice as long at night", 24),
        ["round 161: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 161: the candle burns twice as long at night", 32),
        ["round 161: the candle burns", "twice as long at night"],
    ),
    (
        ("round 161: a mirror of the universe in one line", 4),
        ["round", "161:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 161: a mirror of the universe in one line", 8),
        ["round", "161: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 161: a mirror of the universe in one line", 12),
        ["round 161: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 161: a mirror of the universe in one line", 16),
        ["round 161: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 161: a mirror of the universe in one line", 24), ["round 161: a mirror of", "the universe in one line"]),
    (("round 161: a mirror of the universe in one line", 32), ["round 161: a mirror of the", "universe in one line"]),
    (
        ("round 161: the queue drains before the storm", 4),
        ["round", "161:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 161: the queue drains before the storm", 8),
        ["round", "161: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 161: the queue drains before the storm", 12),
        ["round 161:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 161: the queue drains before the storm", 16), ["round 161: the", "queue drains", "before the storm"]),
    (("round 161: the queue drains before the storm", 24), ["round 161: the queue", "drains before the storm"]),
    (("round 161: the queue drains before the storm", 32), ["round 161: the queue drains", "before the storm"]),
    (
        ("kitten161 sitting161 agent161 angle161 universe161 memory161", 6),
        ["kitten161", "sitting161", "agent161", "angle161", "universe161", "memory161"],
    ),
    (
        ("kitten161 sitting161 agent161 angle161 universe161 memory161", 10),
        ["kitten161", "sitting161", "agent161", "angle161", "universe161", "memory161"],
    ),
    (
        ("kitten161 sitting161 agent161 angle161 universe161 memory161", 18),
        ["kitten161", "sitting161", "agent161 angle161", "universe161", "memory161"],
    ),
    (
        ("kitten161 sitting161 agent161 angle161 universe161 memory161", 28),
        ["kitten161 sitting161", "agent161 angle161", "universe161 memory161"],
    ),
    (
        ("sitting161 agent161 angle161 universe161 memory161 stream161", 6),
        ["sitting161", "agent161", "angle161", "universe161", "memory161", "stream161"],
    ),
    (
        ("sitting161 agent161 angle161 universe161 memory161 stream161", 10),
        ["sitting161", "agent161", "angle161", "universe161", "memory161", "stream161"],
    ),
    (
        ("sitting161 agent161 angle161 universe161 memory161 stream161", 18),
        ["sitting161", "agent161 angle161", "universe161", "memory161", "stream161"],
    ),
    (
        ("sitting161 agent161 angle161 universe161 memory161 stream161", 28),
        ["sitting161 agent161 angle161", "universe161 memory161", "stream161"],
    ),
    (
        ("agent161 angle161 universe161 memory161 stream161 context161", 6),
        ["agent161", "angle161", "universe161", "memory161", "stream161", "context161"],
    ),
    (
        ("agent161 angle161 universe161 memory161 stream161 context161", 10),
        ["agent161", "angle161", "universe161", "memory161", "stream161", "context161"],
    ),
    (
        ("agent161 angle161 universe161 memory161 stream161 context161", 18),
        ["agent161 angle161", "universe161", "memory161", "stream161", "context161"],
    ),
    (
        ("agent161 angle161 universe161 memory161 stream161 context161", 28),
        ["agent161 angle161", "universe161 memory161", "stream161 context161"],
    ),
    (
        ("angle161 universe161 memory161 stream161 context161 knowledge161", 6),
        ["angle161", "universe161", "memory161", "stream161", "context161", "knowledge161"],
    ),
    (
        ("angle161 universe161 memory161 stream161 context161 knowledge161", 10),
        ["angle161", "universe161", "memory161", "stream161", "context161", "knowledge161"],
    ),
    (
        ("angle161 universe161 memory161 stream161 context161 knowledge161", 18),
        ["angle161", "universe161", "memory161", "stream161", "context161", "knowledge161"],
    ),
    (
        ("angle161 universe161 memory161 stream161 context161 knowledge161", 28),
        ["angle161 universe161", "memory161 stream161", "context161 knowledge161"],
    ),
    (
        ("universe161 memory161 stream161 context161 knowledge161 vector161", 6),
        ["universe161", "memory161", "stream161", "context161", "knowledge161", "vector161"],
    ),
    (
        ("universe161 memory161 stream161 context161 knowledge161 vector161", 10),
        ["universe161", "memory161", "stream161", "context161", "knowledge161", "vector161"],
    ),
    (
        ("universe161 memory161 stream161 context161 knowledge161 vector161", 18),
        ["universe161", "memory161", "stream161", "context161", "knowledge161", "vector161"],
    ),
    (
        ("universe161 memory161 stream161 context161 knowledge161 vector161", 28),
        ["universe161 memory161", "stream161 context161", "knowledge161 vector161"],
    ),
    (
        ("memory161 stream161 context161 knowledge161 vector161 processor161", 6),
        ["memory161", "stream161", "context161", "knowledge161", "vector161", "processor161"],
    ),
    (
        ("memory161 stream161 context161 knowledge161 vector161 processor161", 10),
        ["memory161", "stream161", "context161", "knowledge161", "vector161", "processor161"],
    ),
    (
        ("memory161 stream161 context161 knowledge161 vector161 processor161", 18),
        ["memory161", "stream161", "context161", "knowledge161", "vector161", "processor161"],
    ),
    (
        ("memory161 stream161 context161 knowledge161 vector161 processor161", 28),
        ["memory161 stream161", "context161 knowledge161", "vector161 processor161"],
    ),
    (
        ("stream161 context161 knowledge161 vector161 processor161 reasoning161", 6),
        ["stream161", "context161", "knowledge161", "vector161", "processor161", "reasoning161"],
    ),
    (
        ("stream161 context161 knowledge161 vector161 processor161 reasoning161", 10),
        ["stream161", "context161", "knowledge161", "vector161", "processor161", "reasoning161"],
    ),
    (
        ("stream161 context161 knowledge161 vector161 processor161 reasoning161", 18),
        ["stream161", "context161", "knowledge161", "vector161", "processor161", "reasoning161"],
    ),
    (
        ("stream161 context161 knowledge161 vector161 processor161 reasoning161", 28),
        ["stream161 context161", "knowledge161 vector161", "processor161 reasoning161"],
    ),
    (
        ("context161 knowledge161 vector161 processor161 reasoning161 machine161", 6),
        ["context161", "knowledge161", "vector161", "processor161", "reasoning161", "machine161"],
    ),
    (
        ("context161 knowledge161 vector161 processor161 reasoning161 machine161", 10),
        ["context161", "knowledge161", "vector161", "processor161", "reasoning161", "machine161"],
    ),
    (
        ("context161 knowledge161 vector161 processor161 reasoning161 machine161", 18),
        ["context161", "knowledge161", "vector161", "processor161", "reasoning161", "machine161"],
    ),
    (
        ("context161 knowledge161 vector161 processor161 reasoning161 machine161", 28),
        ["context161 knowledge161", "vector161 processor161", "reasoning161 machine161"],
    ),
    (
        ("knowledge161 vector161 processor161 reasoning161 machine161 learning161", 6),
        ["knowledge161", "vector161", "processor161", "reasoning161", "machine161", "learning161"],
    ),
    (
        ("knowledge161 vector161 processor161 reasoning161 machine161 learning161", 10),
        ["knowledge161", "vector161", "processor161", "reasoning161", "machine161", "learning161"],
    ),
    (
        ("knowledge161 vector161 processor161 reasoning161 machine161 learning161", 18),
        ["knowledge161", "vector161", "processor161", "reasoning161", "machine161", "learning161"],
    ),
    (
        ("knowledge161 vector161 processor161 reasoning161 machine161 learning161", 28),
        ["knowledge161 vector161", "processor161 reasoning161", "machine161 learning161"],
    ),
    (
        ("vector161 processor161 reasoning161 machine161 learning161 model161", 6),
        ["vector161", "processor161", "reasoning161", "machine161", "learning161", "model161"],
    ),
    (
        ("vector161 processor161 reasoning161 machine161 learning161 model161", 10),
        ["vector161", "processor161", "reasoning161", "machine161", "learning161", "model161"],
    ),
    (
        ("vector161 processor161 reasoning161 machine161 learning161 model161", 18),
        ["vector161", "processor161", "reasoning161", "machine161", "learning161", "model161"],
    ),
    (
        ("vector161 processor161 reasoning161 machine161 learning161 model161", 28),
        ["vector161 processor161", "reasoning161 machine161", "learning161 model161"],
    ),
    (
        ("processor161 reasoning161 machine161 learning161 model161 token161", 6),
        ["processor161", "reasoning161", "machine161", "learning161", "model161", "token161"],
    ),
    (
        ("processor161 reasoning161 machine161 learning161 model161 token161", 10),
        ["processor161", "reasoning161", "machine161", "learning161", "model161", "token161"],
    ),
    (
        ("processor161 reasoning161 machine161 learning161 model161 token161", 18),
        ["processor161", "reasoning161", "machine161", "learning161", "model161 token161"],
    ),
    (
        ("processor161 reasoning161 machine161 learning161 model161 token161", 28),
        ["processor161 reasoning161", "machine161 learning161", "model161 token161"],
    ),
    (
        ("reasoning161 machine161 learning161 model161 token161 prompt161", 6),
        ["reasoning161", "machine161", "learning161", "model161", "token161", "prompt161"],
    ),
    (
        ("reasoning161 machine161 learning161 model161 token161 prompt161", 10),
        ["reasoning161", "machine161", "learning161", "model161", "token161", "prompt161"],
    ),
    (
        ("reasoning161 machine161 learning161 model161 token161 prompt161", 18),
        ["reasoning161", "machine161", "learning161", "model161 token161", "prompt161"],
    ),
    (
        ("reasoning161 machine161 learning161 model161 token161 prompt161", 28),
        ["reasoning161 machine161", "learning161 model161", "token161 prompt161"],
    ),
    (
        ("machine161 learning161 model161 token161 prompt161 session161", 6),
        ["machine161", "learning161", "model161", "token161", "prompt161", "session161"],
    ),
    (
        ("machine161 learning161 model161 token161 prompt161 session161", 10),
        ["machine161", "learning161", "model161", "token161", "prompt161", "session161"],
    ),
    (
        ("machine161 learning161 model161 token161 prompt161 session161", 18),
        ["machine161", "learning161", "model161 token161", "prompt161", "session161"],
    ),
    (
        ("machine161 learning161 model161 token161 prompt161 session161", 28),
        ["machine161 learning161", "model161 token161 prompt161", "session161"],
    ),
    (
        ("learning161 model161 token161 prompt161 session161 library161", 6),
        ["learning161", "model161", "token161", "prompt161", "session161", "library161"],
    ),
    (
        ("learning161 model161 token161 prompt161 session161 library161", 10),
        ["learning161", "model161", "token161", "prompt161", "session161", "library161"],
    ),
    (
        ("learning161 model161 token161 prompt161 session161 library161", 18),
        ["learning161", "model161 token161", "prompt161", "session161", "library161"],
    ),
    (
        ("learning161 model161 token161 prompt161 session161 library161", 28),
        ["learning161 model161", "token161 prompt161", "session161 library161"],
    ),
    (
        ("model161 token161 prompt161 session161 library161 service161", 6),
        ["model161", "token161", "prompt161", "session161", "library161", "service161"],
    ),
    (
        ("model161 token161 prompt161 session161 library161 service161", 10),
        ["model161", "token161", "prompt161", "session161", "library161", "service161"],
    ),
    (
        ("model161 token161 prompt161 session161 library161 service161", 18),
        ["model161 token161", "prompt161", "session161", "library161", "service161"],
    ),
    (
        ("model161 token161 prompt161 session161 library161 service161", 28),
        ["model161 token161 prompt161", "session161 library161", "service161"],
    ),
    (
        ("token161 prompt161 session161 library161 service161 gateway161", 6),
        ["token161", "prompt161", "session161", "library161", "service161", "gateway161"],
    ),
    (
        ("token161 prompt161 session161 library161 service161 gateway161", 10),
        ["token161", "prompt161", "session161", "library161", "service161", "gateway161"],
    ),
    (
        ("token161 prompt161 session161 library161 service161 gateway161", 18),
        ["token161 prompt161", "session161", "library161", "service161", "gateway161"],
    ),
    (
        ("token161 prompt161 session161 library161 service161 gateway161", 28),
        ["token161 prompt161", "session161 library161", "service161 gateway161"],
    ),
    (
        ("prompt161 session161 library161 service161 gateway161 storage161", 6),
        ["prompt161", "session161", "library161", "service161", "gateway161", "storage161"],
    ),
    (
        ("prompt161 session161 library161 service161 gateway161 storage161", 10),
        ["prompt161", "session161", "library161", "service161", "gateway161", "storage161"],
    ),
    (
        ("prompt161 session161 library161 service161 gateway161 storage161", 18),
        ["prompt161", "session161", "library161", "service161", "gateway161", "storage161"],
    ),
    (
        ("prompt161 session161 library161 service161 gateway161 storage161", 28),
        ["prompt161 session161", "library161 service161", "gateway161 storage161"],
    ),
    (
        ("session161 library161 service161 gateway161 storage161 network161", 6),
        ["session161", "library161", "service161", "gateway161", "storage161", "network161"],
    ),
    (
        ("session161 library161 service161 gateway161 storage161 network161", 10),
        ["session161", "library161", "service161", "gateway161", "storage161", "network161"],
    ),
    (
        ("session161 library161 service161 gateway161 storage161 network161", 18),
        ["session161", "library161", "service161", "gateway161", "storage161", "network161"],
    ),
    (
        ("session161 library161 service161 gateway161 storage161 network161", 28),
        ["session161 library161", "service161 gateway161", "storage161 network161"],
    ),
    (
        ("library161 service161 gateway161 storage161 network161 latency161", 6),
        ["library161", "service161", "gateway161", "storage161", "network161", "latency161"],
    ),
    (
        ("library161 service161 gateway161 storage161 network161 latency161", 10),
        ["library161", "service161", "gateway161", "storage161", "network161", "latency161"],
    ),
    (
        ("library161 service161 gateway161 storage161 network161 latency161", 18),
        ["library161", "service161", "gateway161", "storage161", "network161", "latency161"],
    ),
    (
        ("library161 service161 gateway161 storage161 network161 latency161", 28),
        ["library161 service161", "gateway161 storage161", "network161 latency161"],
    ),
    (
        ("service161 gateway161 storage161 network161 latency161 buffer161", 6),
        ["service161", "gateway161", "storage161", "network161", "latency161", "buffer161"],
    ),
    (
        ("service161 gateway161 storage161 network161 latency161 buffer161", 10),
        ["service161", "gateway161", "storage161", "network161", "latency161", "buffer161"],
    ),
    (
        ("service161 gateway161 storage161 network161 latency161 buffer161", 18),
        ["service161", "gateway161", "storage161", "network161", "latency161", "buffer161"],
    ),
    (
        ("service161 gateway161 storage161 network161 latency161 buffer161", 28),
        ["service161 gateway161", "storage161 network161", "latency161 buffer161"],
    ),
    (
        ("gateway161 storage161 network161 latency161 buffer161 queue161", 6),
        ["gateway161", "storage161", "network161", "latency161", "buffer161", "queue161"],
    ),
    (
        ("gateway161 storage161 network161 latency161 buffer161 queue161", 10),
        ["gateway161", "storage161", "network161", "latency161", "buffer161", "queue161"],
    ),
    (
        ("gateway161 storage161 network161 latency161 buffer161 queue161", 18),
        ["gateway161", "storage161", "network161", "latency161", "buffer161 queue161"],
    ),
    (
        ("gateway161 storage161 network161 latency161 buffer161 queue161", 28),
        ["gateway161 storage161", "network161 latency161", "buffer161 queue161"],
    ),
    (
        ("storage161 network161 latency161 buffer161 queue161 worker161", 6),
        ["storage161", "network161", "latency161", "buffer161", "queue161", "worker161"],
    ),
    (
        ("storage161 network161 latency161 buffer161 queue161 worker161", 10),
        ["storage161", "network161", "latency161", "buffer161", "queue161", "worker161"],
    ),
    (
        ("storage161 network161 latency161 buffer161 queue161 worker161", 18),
        ["storage161", "network161", "latency161", "buffer161 queue161", "worker161"],
    ),
    (
        ("storage161 network161 latency161 buffer161 queue161 worker161", 28),
        ["storage161 network161", "latency161 buffer161", "queue161 worker161"],
    ),
    (
        ("network161 latency161 buffer161 queue161 worker161 kernel161", 6),
        ["network161", "latency161", "buffer161", "queue161", "worker161", "kernel161"],
    ),
    (
        ("network161 latency161 buffer161 queue161 worker161 kernel161", 10),
        ["network161", "latency161", "buffer161", "queue161", "worker161", "kernel161"],
    ),
    (
        ("network161 latency161 buffer161 queue161 worker161 kernel161", 18),
        ["network161", "latency161", "buffer161 queue161", "worker161", "kernel161"],
    ),
    (
        ("network161 latency161 buffer161 queue161 worker161 kernel161", 28),
        ["network161 latency161", "buffer161 queue161 worker161", "kernel161"],
    ),
    (
        ("latency161 buffer161 queue161 worker161 kernel161 signal161", 6),
        ["latency161", "buffer161", "queue161", "worker161", "kernel161", "signal161"],
    ),
    (
        ("latency161 buffer161 queue161 worker161 kernel161 signal161", 10),
        ["latency161", "buffer161", "queue161", "worker161", "kernel161", "signal161"],
    ),
    (
        ("latency161 buffer161 queue161 worker161 kernel161 signal161", 18),
        ["latency161", "buffer161 queue161", "worker161", "kernel161", "signal161"],
    ),
    (
        ("latency161 buffer161 queue161 worker161 kernel161 signal161", 28),
        ["latency161 buffer161", "queue161 worker161 kernel161", "signal161"],
    ),
    (
        ("buffer161 queue161 worker161 kernel161 signal161 packet161", 6),
        ["buffer161", "queue161", "worker161", "kernel161", "signal161", "packet161"],
    ),
    (
        ("buffer161 queue161 worker161 kernel161 signal161 packet161", 10),
        ["buffer161", "queue161", "worker161", "kernel161", "signal161", "packet161"],
    ),
    (
        ("buffer161 queue161 worker161 kernel161 signal161 packet161", 18),
        ["buffer161 queue161", "worker161", "kernel161", "signal161", "packet161"],
    ),
    (
        ("buffer161 queue161 worker161 kernel161 signal161 packet161", 28),
        ["buffer161 queue161 worker161", "kernel161 signal161", "packet161"],
    ),
    (
        ("queue161 worker161 kernel161 signal161 packet161 router161", 6),
        ["queue161", "worker161", "kernel161", "signal161", "packet161", "router161"],
    ),
    (
        ("queue161 worker161 kernel161 signal161 packet161 router161", 10),
        ["queue161", "worker161", "kernel161", "signal161", "packet161", "router161"],
    ),
    (
        ("queue161 worker161 kernel161 signal161 packet161 router161", 18),
        ["queue161 worker161", "kernel161", "signal161", "packet161", "router161"],
    ),
    (
        ("queue161 worker161 kernel161 signal161 packet161 router161", 28),
        ["queue161 worker161 kernel161", "signal161 packet161", "router161"],
    ),
    (
        ("worker161 kernel161 signal161 packet161 router161 cluster161", 6),
        ["worker161", "kernel161", "signal161", "packet161", "router161", "cluster161"],
    ),
    (
        ("worker161 kernel161 signal161 packet161 router161 cluster161", 10),
        ["worker161", "kernel161", "signal161", "packet161", "router161", "cluster161"],
    ),
    (
        ("worker161 kernel161 signal161 packet161 router161 cluster161", 18),
        ["worker161", "kernel161", "signal161", "packet161", "router161", "cluster161"],
    ),
    (
        ("worker161 kernel161 signal161 packet161 router161 cluster161", 28),
        ["worker161 kernel161", "signal161 packet161", "router161 cluster161"],
    ),
    (
        ("kernel161 signal161 packet161 router161 cluster161 mirror161", 6),
        ["kernel161", "signal161", "packet161", "router161", "cluster161", "mirror161"],
    ),
    (
        ("kernel161 signal161 packet161 router161 cluster161 mirror161", 10),
        ["kernel161", "signal161", "packet161", "router161", "cluster161", "mirror161"],
    ),
    (
        ("kernel161 signal161 packet161 router161 cluster161 mirror161", 18),
        ["kernel161", "signal161", "packet161", "router161", "cluster161", "mirror161"],
    ),
    (
        ("kernel161 signal161 packet161 router161 cluster161 mirror161", 28),
        ["kernel161 signal161", "packet161 router161", "cluster161 mirror161"],
    ),
    (
        ("signal161 packet161 router161 cluster161 mirror161 filter161", 6),
        ["signal161", "packet161", "router161", "cluster161", "mirror161", "filter161"],
    ),
    (
        ("signal161 packet161 router161 cluster161 mirror161 filter161", 10),
        ["signal161", "packet161", "router161", "cluster161", "mirror161", "filter161"],
    ),
    (
        ("signal161 packet161 router161 cluster161 mirror161 filter161", 18),
        ["signal161", "packet161", "router161", "cluster161", "mirror161", "filter161"],
    ),
    (
        ("signal161 packet161 router161 cluster161 mirror161 filter161", 28),
        ["signal161 packet161", "router161 cluster161", "mirror161 filter161"],
    ),
    (
        ("packet161 router161 cluster161 mirror161 filter161 ranking161", 6),
        ["packet161", "router161", "cluster161", "mirror161", "filter161", "ranking161"],
    ),
    (
        ("packet161 router161 cluster161 mirror161 filter161 ranking161", 10),
        ["packet161", "router161", "cluster161", "mirror161", "filter161", "ranking161"],
    ),
    (
        ("packet161 router161 cluster161 mirror161 filter161 ranking161", 18),
        ["packet161", "router161", "cluster161", "mirror161", "filter161", "ranking161"],
    ),
    (
        ("packet161 router161 cluster161 mirror161 filter161 ranking161", 28),
        ["packet161 router161", "cluster161 mirror161", "filter161 ranking161"],
    ),
    (
        ("router161 cluster161 mirror161 filter161 ranking161 encoding161", 6),
        ["router161", "cluster161", "mirror161", "filter161", "ranking161", "encoding161"],
    ),
    (
        ("router161 cluster161 mirror161 filter161 ranking161 encoding161", 10),
        ["router161", "cluster161", "mirror161", "filter161", "ranking161", "encoding161"],
    ),
    (
        ("router161 cluster161 mirror161 filter161 ranking161 encoding161", 18),
        ["router161", "cluster161", "mirror161", "filter161", "ranking161", "encoding161"],
    ),
    (
        ("router161 cluster161 mirror161 filter161 ranking161 encoding161", 28),
        ["router161 cluster161", "mirror161 filter161", "ranking161 encoding161"],
    ),
    (
        ("cluster161 mirror161 filter161 ranking161 encoding161 mapping161", 6),
        ["cluster161", "mirror161", "filter161", "ranking161", "encoding161", "mapping161"],
    ),
    (
        ("cluster161 mirror161 filter161 ranking161 encoding161 mapping161", 10),
        ["cluster161", "mirror161", "filter161", "ranking161", "encoding161", "mapping161"],
    ),
    (
        ("cluster161 mirror161 filter161 ranking161 encoding161 mapping161", 18),
        ["cluster161", "mirror161", "filter161", "ranking161", "encoding161", "mapping161"],
    ),
    (
        ("cluster161 mirror161 filter161 ranking161 encoding161 mapping161", 28),
        ["cluster161 mirror161", "filter161 ranking161", "encoding161 mapping161"],
    ),
    (
        ("mirror161 filter161 ranking161 encoding161 mapping161 record161", 6),
        ["mirror161", "filter161", "ranking161", "encoding161", "mapping161", "record161"],
    ),
    (
        ("mirror161 filter161 ranking161 encoding161 mapping161 record161", 10),
        ["mirror161", "filter161", "ranking161", "encoding161", "mapping161", "record161"],
    ),
    (
        ("mirror161 filter161 ranking161 encoding161 mapping161 record161", 18),
        ["mirror161", "filter161", "ranking161", "encoding161", "mapping161", "record161"],
    ),
    (
        ("mirror161 filter161 ranking161 encoding161 mapping161 record161", 28),
        ["mirror161 filter161", "ranking161 encoding161", "mapping161 record161"],
    ),
    (
        ("filter161 ranking161 encoding161 mapping161 record161 candle161", 6),
        ["filter161", "ranking161", "encoding161", "mapping161", "record161", "candle161"],
    ),
    (
        ("filter161 ranking161 encoding161 mapping161 record161 candle161", 10),
        ["filter161", "ranking161", "encoding161", "mapping161", "record161", "candle161"],
    ),
    (
        ("filter161 ranking161 encoding161 mapping161 record161 candle161", 18),
        ["filter161", "ranking161", "encoding161", "mapping161", "record161", "candle161"],
    ),
    (
        ("filter161 ranking161 encoding161 mapping161 record161 candle161", 28),
        ["filter161 ranking161", "encoding161 mapping161", "record161 candle161"],
    ),
    (
        ("ranking161 encoding161 mapping161 record161 candle161 thread161", 6),
        ["ranking161", "encoding161", "mapping161", "record161", "candle161", "thread161"],
    ),
    (
        ("ranking161 encoding161 mapping161 record161 candle161 thread161", 10),
        ["ranking161", "encoding161", "mapping161", "record161", "candle161", "thread161"],
    ),
    (
        ("ranking161 encoding161 mapping161 record161 candle161 thread161", 18),
        ["ranking161", "encoding161", "mapping161", "record161", "candle161", "thread161"],
    ),
    (
        ("ranking161 encoding161 mapping161 record161 candle161 thread161", 28),
        ["ranking161 encoding161", "mapping161 record161", "candle161 thread161"],
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
