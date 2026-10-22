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
        ("round 88: the quick brown fox jumps over the lazy dog", 4),
        ["round", "88:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 88: the quick brown fox jumps over the lazy dog", 8),
        ["round", "88: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 88: the quick brown fox jumps over the lazy dog", 12),
        ["round 88:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 88: the quick brown fox jumps over the lazy dog", 16),
        ["round 88: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 88: the quick brown fox jumps over the lazy dog", 24),
        ["round 88: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 88: the quick brown fox jumps over the lazy dog", 32),
        ["round 88: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 88: agentuniverse is a framework for multi agents", 4),
        ["round", "88:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 88: agentuniverse is a framework for multi agents", 8),
        ["round", "88:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 88: agentuniverse is a framework for multi agents", 12),
        ["round 88:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 88: agentuniverse is a framework for multi agents", 16),
        ["round 88:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 88: agentuniverse is a framework for multi agents", 24),
        ["round 88: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 88: agentuniverse is a framework for multi agents", 32),
        ["round 88: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 88: knowledge stored as vectors enables retrieval", 4),
        ["round", "88:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 88: knowledge stored as vectors enables retrieval", 8),
        ["round", "88:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 88: knowledge stored as vectors enables retrieval", 12),
        ["round 88:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 88: knowledge stored as vectors enables retrieval", 16),
        ["round 88:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 88: knowledge stored as vectors enables retrieval", 24),
        ["round 88: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 88: knowledge stored as vectors enables retrieval", 32),
        ["round 88: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 88: the processor reads the record then stops", 4),
        ["round", "88:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 88: the processor reads the record then stops", 8),
        ["round", "88: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 88: the processor reads the record then stops", 12),
        ["round 88:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 88: the processor reads the record then stops", 16),
        ["round 88: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 88: the processor reads the record then stops", 24),
        ["round 88: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 88: the processor reads the record then stops", 32),
        ["round 88: the processor reads", "the record then stops"],
    ),
    (
        ("round 88: a worker pulls the next task from the queue", 4),
        ["round", "88:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 88: a worker pulls the next task from the queue", 8),
        ["round", "88: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 88: a worker pulls the next task from the queue", 12),
        ["round 88: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 88: a worker pulls the next task from the queue", 16),
        ["round 88: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 88: a worker pulls the next task from the queue", 24),
        ["round 88: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 88: a worker pulls the next task from the queue", 32),
        ["round 88: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 88: signals travel through the network layer", 4),
        ["round", "88:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 88: signals travel through the network layer", 8),
        ["round", "88:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 88: signals travel through the network layer", 12),
        ["round 88:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 88: signals travel through the network layer", 16),
        ["round 88:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 88: signals travel through the network layer", 24),
        ["round 88: signals travel", "through the network", "layer"],
    ),
    (
        ("round 88: signals travel through the network layer", 32),
        ["round 88: signals travel through", "the network layer"],
    ),
    (
        ("round 88: the gateway routes each request by policy", 4),
        ["round", "88:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 88: the gateway routes each request by policy", 8),
        ["round", "88: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 88: the gateway routes each request by policy", 12),
        ["round 88:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 88: the gateway routes each request by policy", 16),
        ["round 88: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 88: the gateway routes each request by policy", 24),
        ["round 88: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 88: the gateway routes each request by policy", 32),
        ["round 88: the gateway routes", "each request by policy"],
    ),
    (
        ("round 88: memory grows until the buffer is full", 4),
        ["round", "88:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 88: memory grows until the buffer is full", 8),
        ["round", "88:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 88: memory grows until the buffer is full", 12),
        ["round 88:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 88: memory grows until the buffer is full", 16),
        ["round 88: memory", "grows until the", "buffer is full"],
    ),
    (("round 88: memory grows until the buffer is full", 24), ["round 88: memory grows", "until the buffer is full"]),
    (("round 88: memory grows until the buffer is full", 32), ["round 88: memory grows until the", "buffer is full"]),
    (
        ("round 88: the cluster mirrors every packet twice", 4),
        ["round", "88:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 88: the cluster mirrors every packet twice", 8),
        ["round", "88: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 88: the cluster mirrors every packet twice", 12),
        ["round 88:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 88: the cluster mirrors every packet twice", 16),
        ["round 88: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 88: the cluster mirrors every packet twice", 24),
        ["round 88: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 88: the cluster mirrors every packet twice", 32), ["round 88: the cluster mirrors", "every packet twice"]),
    (
        ("round 88: ranking uses tokens learned from the corpus", 4),
        ["round", "88:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 88: ranking uses tokens learned from the corpus", 8),
        ["round", "88:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 88: ranking uses tokens learned from the corpus", 12),
        ["round 88:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 88: ranking uses tokens learned from the corpus", 16),
        ["round 88:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 88: ranking uses tokens learned from the corpus", 24),
        ["round 88: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 88: ranking uses tokens learned from the corpus", 32),
        ["round 88: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 88: a long session ends when the candle dies", 4),
        ["round", "88:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 88: a long session ends when the candle dies", 8),
        ["round", "88: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 88: a long session ends when the candle dies", 12),
        ["round 88: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 88: a long session ends when the candle dies", 16),
        ["round 88: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 88: a long session ends when the candle dies", 24),
        ["round 88: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 88: a long session ends when the candle dies", 32),
        ["round 88: a long session ends", "when the candle dies"],
    ),
    (
        ("round 88: encode the prompt then map the result", 4),
        ["round", "88:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 88: encode the prompt then map the result", 8),
        ["round", "88:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 88: encode the prompt then map the result", 12),
        ["round 88:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 88: encode the prompt then map the result", 16),
        ["round 88: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 88: encode the prompt then map the result", 24),
        ["round 88: encode the", "prompt then map the", "result"],
    ),
    (("round 88: encode the prompt then map the result", 32), ["round 88: encode the prompt then", "map the result"]),
    (
        ("round 88: the kernel wakes the worker at dawn", 4),
        ["round", "88:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 88: the kernel wakes the worker at dawn", 8),
        ["round", "88: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 88: the kernel wakes the worker at dawn", 12),
        ["round 88:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 88: the kernel wakes the worker at dawn", 16), ["round 88: the", "kernel wakes the", "worker at dawn"]),
    (("round 88: the kernel wakes the worker at dawn", 24), ["round 88: the kernel", "wakes the worker at dawn"]),
    (("round 88: the kernel wakes the worker at dawn", 32), ["round 88: the kernel wakes the", "worker at dawn"]),
    (
        ("round 88: service latency drops after the patch", 4),
        ["round", "88:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 88: service latency drops after the patch", 8),
        ["round", "88:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 88: service latency drops after the patch", 12),
        ["round 88:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 88: service latency drops after the patch", 16),
        ["round 88:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 88: service latency drops after the patch", 24),
        ["round 88: service", "latency drops after the", "patch"],
    ),
    (("round 88: service latency drops after the patch", 32), ["round 88: service latency drops", "after the patch"]),
    (
        ("round 88: the library caches every vector it sees", 4),
        ["round", "88:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 88: the library caches every vector it sees", 8),
        ["round", "88: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 88: the library caches every vector it sees", 12),
        ["round 88:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 88: the library caches every vector it sees", 16),
        ["round 88: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 88: the library caches every vector it sees", 24),
        ["round 88: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 88: the library caches every vector it sees", 32),
        ["round 88: the library caches", "every vector it sees"],
    ),
    (
        ("round 88: agents argue then the debate resolves", 4),
        ["round", "88:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 88: agents argue then the debate resolves", 8),
        ["round", "88:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 88: agents argue then the debate resolves", 12),
        ["round 88:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 88: agents argue then the debate resolves", 16),
        ["round 88: agents", "argue then the", "debate resolves"],
    ),
    (("round 88: agents argue then the debate resolves", 24), ["round 88: agents argue", "then the debate resolves"]),
    (("round 88: agents argue then the debate resolves", 32), ["round 88: agents argue then the", "debate resolves"]),
    (
        ("round 88: the filter keeps only strong matches", 4),
        ["round", "88:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 88: the filter keeps only strong matches", 8),
        ["round", "88: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 88: the filter keeps only strong matches", 12),
        ["round 88:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 88: the filter keeps only strong matches", 16),
        ["round 88: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 88: the filter keeps only strong matches", 24), ["round 88: the filter", "keeps only strong", "matches"]),
    (("round 88: the filter keeps only strong matches", 32), ["round 88: the filter keeps only", "strong matches"]),
    (
        ("round 88: the model answers with a short reply", 4),
        ["round", "88:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 88: the model answers with a short reply", 8),
        ["round", "88: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 88: the model answers with a short reply", 12),
        ["round 88:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 88: the model answers with a short reply", 16),
        ["round 88: the", "model answers", "with a short", "reply"],
    ),
    (("round 88: the model answers with a short reply", 24), ["round 88: the model", "answers with a short", "reply"]),
    (("round 88: the model answers with a short reply", 32), ["round 88: the model answers with", "a short reply"]),
    (
        ("round 88: the recorder stores the reasoning trace", 4),
        ["round", "88:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 88: the recorder stores the reasoning trace", 8),
        ["round", "88: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 88: the recorder stores the reasoning trace", 12),
        ["round 88:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 88: the recorder stores the reasoning trace", 16),
        ["round 88: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 88: the recorder stores the reasoning trace", 24),
        ["round 88: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 88: the recorder stores the reasoning trace", 32),
        ["round 88: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 88: the angel watches the processor run", 4),
        ["round", "88:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 88: the angel watches the processor run", 8),
        ["round", "88: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 88: the angel watches the processor run", 12),
        ["round 88:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 88: the angel watches the processor run", 16), ["round 88: the", "angel watches", "the processor", "run"]),
    (("round 88: the angel watches the processor run", 24), ["round 88: the angel", "watches the processor", "run"]),
    (("round 88: the angel watches the processor run", 32), ["round 88: the angel watches the", "processor run"]),
    (
        ("round 88: angle of the vector decides the match", 4),
        ["round", "88:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 88: angle of the vector decides the match", 8),
        ["round", "88:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 88: angle of the vector decides the match", 12),
        ["round 88:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 88: angle of the vector decides the match", 16),
        ["round 88: angle", "of the vector", "decides the", "match"],
    ),
    (("round 88: angle of the vector decides the match", 24), ["round 88: angle of the", "vector decides the match"]),
    (("round 88: angle of the vector decides the match", 32), ["round 88: angle of the vector", "decides the match"]),
    (
        ("round 88: the candle burns twice as long at night", 4),
        ["round", "88:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 88: the candle burns twice as long at night", 8),
        ["round", "88: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 88: the candle burns twice as long at night", 12),
        ["round 88:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 88: the candle burns twice as long at night", 16),
        ["round 88: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 88: the candle burns twice as long at night", 24),
        ["round 88: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 88: the candle burns twice as long at night", 32),
        ["round 88: the candle burns twice", "as long at night"],
    ),
    (
        ("round 88: a mirror of the universe in one line", 4),
        ["round", "88:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 88: a mirror of the universe in one line", 8),
        ["round", "88: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 88: a mirror of the universe in one line", 12),
        ["round 88: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 88: a mirror of the universe in one line", 16),
        ["round 88: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 88: a mirror of the universe in one line", 24), ["round 88: a mirror of", "the universe in one line"]),
    (("round 88: a mirror of the universe in one line", 32), ["round 88: a mirror of the", "universe in one line"]),
    (
        ("round 88: the queue drains before the storm", 4),
        ["round", "88:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 88: the queue drains before the storm", 8),
        ["round", "88: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 88: the queue drains before the storm", 12), ["round 88:", "the queue", "drains", "before the", "storm"]),
    (("round 88: the queue drains before the storm", 16), ["round 88: the", "queue drains", "before the storm"]),
    (("round 88: the queue drains before the storm", 24), ["round 88: the queue", "drains before the storm"]),
    (("round 88: the queue drains before the storm", 32), ["round 88: the queue drains", "before the storm"]),
    (
        ("kitten88 sitting88 agent88 angle88 universe88 memory88", 6),
        ["kitten88", "sitting88", "agent88", "angle88", "universe88", "memory88"],
    ),
    (
        ("kitten88 sitting88 agent88 angle88 universe88 memory88", 10),
        ["kitten88", "sitting88", "agent88", "angle88", "universe88", "memory88"],
    ),
    (
        ("kitten88 sitting88 agent88 angle88 universe88 memory88", 18),
        ["kitten88 sitting88", "agent88 angle88", "universe88", "memory88"],
    ),
    (
        ("kitten88 sitting88 agent88 angle88 universe88 memory88", 28),
        ["kitten88 sitting88 agent88", "angle88 universe88 memory88"],
    ),
    (
        ("sitting88 agent88 angle88 universe88 memory88 stream88", 6),
        ["sitting88", "agent88", "angle88", "universe88", "memory88", "stream88"],
    ),
    (
        ("sitting88 agent88 angle88 universe88 memory88 stream88", 10),
        ["sitting88", "agent88", "angle88", "universe88", "memory88", "stream88"],
    ),
    (
        ("sitting88 agent88 angle88 universe88 memory88 stream88", 18),
        ["sitting88 agent88", "angle88 universe88", "memory88 stream88"],
    ),
    (
        ("sitting88 agent88 angle88 universe88 memory88 stream88", 28),
        ["sitting88 agent88 angle88", "universe88 memory88 stream88"],
    ),
    (
        ("agent88 angle88 universe88 memory88 stream88 context88", 6),
        ["agent88", "angle88", "universe88", "memory88", "stream88", "context88"],
    ),
    (
        ("agent88 angle88 universe88 memory88 stream88 context88", 10),
        ["agent88", "angle88", "universe88", "memory88", "stream88", "context88"],
    ),
    (
        ("agent88 angle88 universe88 memory88 stream88 context88", 18),
        ["agent88 angle88", "universe88", "memory88 stream88", "context88"],
    ),
    (
        ("agent88 angle88 universe88 memory88 stream88 context88", 28),
        ["agent88 angle88 universe88", "memory88 stream88 context88"],
    ),
    (
        ("angle88 universe88 memory88 stream88 context88 knowledge88", 6),
        ["angle88", "universe88", "memory88", "stream88", "context88", "knowledge88"],
    ),
    (
        ("angle88 universe88 memory88 stream88 context88 knowledge88", 10),
        ["angle88", "universe88", "memory88", "stream88", "context88", "knowledge88"],
    ),
    (
        ("angle88 universe88 memory88 stream88 context88 knowledge88", 18),
        ["angle88 universe88", "memory88 stream88", "context88", "knowledge88"],
    ),
    (
        ("angle88 universe88 memory88 stream88 context88 knowledge88", 28),
        ["angle88 universe88 memory88", "stream88 context88", "knowledge88"],
    ),
    (
        ("universe88 memory88 stream88 context88 knowledge88 vector88", 6),
        ["universe88", "memory88", "stream88", "context88", "knowledge88", "vector88"],
    ),
    (
        ("universe88 memory88 stream88 context88 knowledge88 vector88", 10),
        ["universe88", "memory88", "stream88", "context88", "knowledge88", "vector88"],
    ),
    (
        ("universe88 memory88 stream88 context88 knowledge88 vector88", 18),
        ["universe88", "memory88 stream88", "context88", "knowledge88", "vector88"],
    ),
    (
        ("universe88 memory88 stream88 context88 knowledge88 vector88", 28),
        ["universe88 memory88 stream88", "context88 knowledge88", "vector88"],
    ),
    (
        ("memory88 stream88 context88 knowledge88 vector88 processor88", 6),
        ["memory88", "stream88", "context88", "knowledge88", "vector88", "processor88"],
    ),
    (
        ("memory88 stream88 context88 knowledge88 vector88 processor88", 10),
        ["memory88", "stream88", "context88", "knowledge88", "vector88", "processor88"],
    ),
    (
        ("memory88 stream88 context88 knowledge88 vector88 processor88", 18),
        ["memory88 stream88", "context88", "knowledge88", "vector88", "processor88"],
    ),
    (
        ("memory88 stream88 context88 knowledge88 vector88 processor88", 28),
        ["memory88 stream88 context88", "knowledge88 vector88", "processor88"],
    ),
    (
        ("stream88 context88 knowledge88 vector88 processor88 reasoning88", 6),
        ["stream88", "context88", "knowledge88", "vector88", "processor88", "reasoning88"],
    ),
    (
        ("stream88 context88 knowledge88 vector88 processor88 reasoning88", 10),
        ["stream88", "context88", "knowledge88", "vector88", "processor88", "reasoning88"],
    ),
    (
        ("stream88 context88 knowledge88 vector88 processor88 reasoning88", 18),
        ["stream88 context88", "knowledge88", "vector88", "processor88", "reasoning88"],
    ),
    (
        ("stream88 context88 knowledge88 vector88 processor88 reasoning88", 28),
        ["stream88 context88", "knowledge88 vector88", "processor88 reasoning88"],
    ),
    (
        ("context88 knowledge88 vector88 processor88 reasoning88 machine88", 6),
        ["context88", "knowledge88", "vector88", "processor88", "reasoning88", "machine88"],
    ),
    (
        ("context88 knowledge88 vector88 processor88 reasoning88 machine88", 10),
        ["context88", "knowledge88", "vector88", "processor88", "reasoning88", "machine88"],
    ),
    (
        ("context88 knowledge88 vector88 processor88 reasoning88 machine88", 18),
        ["context88", "knowledge88", "vector88", "processor88", "reasoning88", "machine88"],
    ),
    (
        ("context88 knowledge88 vector88 processor88 reasoning88 machine88", 28),
        ["context88 knowledge88", "vector88 processor88", "reasoning88 machine88"],
    ),
    (
        ("knowledge88 vector88 processor88 reasoning88 machine88 learning88", 6),
        ["knowledge88", "vector88", "processor88", "reasoning88", "machine88", "learning88"],
    ),
    (
        ("knowledge88 vector88 processor88 reasoning88 machine88 learning88", 10),
        ["knowledge88", "vector88", "processor88", "reasoning88", "machine88", "learning88"],
    ),
    (
        ("knowledge88 vector88 processor88 reasoning88 machine88 learning88", 18),
        ["knowledge88", "vector88", "processor88", "reasoning88", "machine88", "learning88"],
    ),
    (
        ("knowledge88 vector88 processor88 reasoning88 machine88 learning88", 28),
        ["knowledge88 vector88", "processor88 reasoning88", "machine88 learning88"],
    ),
    (
        ("vector88 processor88 reasoning88 machine88 learning88 model88", 6),
        ["vector88", "processor88", "reasoning88", "machine88", "learning88", "model88"],
    ),
    (
        ("vector88 processor88 reasoning88 machine88 learning88 model88", 10),
        ["vector88", "processor88", "reasoning88", "machine88", "learning88", "model88"],
    ),
    (
        ("vector88 processor88 reasoning88 machine88 learning88 model88", 18),
        ["vector88", "processor88", "reasoning88", "machine88", "learning88 model88"],
    ),
    (
        ("vector88 processor88 reasoning88 machine88 learning88 model88", 28),
        ["vector88 processor88", "reasoning88 machine88", "learning88 model88"],
    ),
    (
        ("processor88 reasoning88 machine88 learning88 model88 token88", 6),
        ["processor88", "reasoning88", "machine88", "learning88", "model88", "token88"],
    ),
    (
        ("processor88 reasoning88 machine88 learning88 model88 token88", 10),
        ["processor88", "reasoning88", "machine88", "learning88", "model88", "token88"],
    ),
    (
        ("processor88 reasoning88 machine88 learning88 model88 token88", 18),
        ["processor88", "reasoning88", "machine88", "learning88 model88", "token88"],
    ),
    (
        ("processor88 reasoning88 machine88 learning88 model88 token88", 28),
        ["processor88 reasoning88", "machine88 learning88 model88", "token88"],
    ),
    (
        ("reasoning88 machine88 learning88 model88 token88 prompt88", 6),
        ["reasoning88", "machine88", "learning88", "model88", "token88", "prompt88"],
    ),
    (
        ("reasoning88 machine88 learning88 model88 token88 prompt88", 10),
        ["reasoning88", "machine88", "learning88", "model88", "token88", "prompt88"],
    ),
    (
        ("reasoning88 machine88 learning88 model88 token88 prompt88", 18),
        ["reasoning88", "machine88", "learning88 model88", "token88 prompt88"],
    ),
    (
        ("reasoning88 machine88 learning88 model88 token88 prompt88", 28),
        ["reasoning88 machine88", "learning88 model88 token88", "prompt88"],
    ),
    (
        ("machine88 learning88 model88 token88 prompt88 session88", 6),
        ["machine88", "learning88", "model88", "token88", "prompt88", "session88"],
    ),
    (
        ("machine88 learning88 model88 token88 prompt88 session88", 10),
        ["machine88", "learning88", "model88", "token88", "prompt88", "session88"],
    ),
    (
        ("machine88 learning88 model88 token88 prompt88 session88", 18),
        ["machine88", "learning88 model88", "token88 prompt88", "session88"],
    ),
    (
        ("machine88 learning88 model88 token88 prompt88 session88", 28),
        ["machine88 learning88 model88", "token88 prompt88 session88"],
    ),
    (
        ("learning88 model88 token88 prompt88 session88 library88", 6),
        ["learning88", "model88", "token88", "prompt88", "session88", "library88"],
    ),
    (
        ("learning88 model88 token88 prompt88 session88 library88", 10),
        ["learning88", "model88", "token88", "prompt88", "session88", "library88"],
    ),
    (
        ("learning88 model88 token88 prompt88 session88 library88", 18),
        ["learning88 model88", "token88 prompt88", "session88", "library88"],
    ),
    (
        ("learning88 model88 token88 prompt88 session88 library88", 28),
        ["learning88 model88 token88", "prompt88 session88 library88"],
    ),
    (
        ("model88 token88 prompt88 session88 library88 service88", 6),
        ["model88", "token88", "prompt88", "session88", "library88", "service88"],
    ),
    (
        ("model88 token88 prompt88 session88 library88 service88", 10),
        ["model88", "token88", "prompt88", "session88", "library88", "service88"],
    ),
    (
        ("model88 token88 prompt88 session88 library88 service88", 18),
        ["model88 token88", "prompt88 session88", "library88", "service88"],
    ),
    (
        ("model88 token88 prompt88 session88 library88 service88", 28),
        ["model88 token88 prompt88", "session88 library88", "service88"],
    ),
    (
        ("token88 prompt88 session88 library88 service88 gateway88", 6),
        ["token88", "prompt88", "session88", "library88", "service88", "gateway88"],
    ),
    (
        ("token88 prompt88 session88 library88 service88 gateway88", 10),
        ["token88", "prompt88", "session88", "library88", "service88", "gateway88"],
    ),
    (
        ("token88 prompt88 session88 library88 service88 gateway88", 18),
        ["token88 prompt88", "session88", "library88", "service88", "gateway88"],
    ),
    (
        ("token88 prompt88 session88 library88 service88 gateway88", 28),
        ["token88 prompt88 session88", "library88 service88", "gateway88"],
    ),
    (
        ("prompt88 session88 library88 service88 gateway88 storage88", 6),
        ["prompt88", "session88", "library88", "service88", "gateway88", "storage88"],
    ),
    (
        ("prompt88 session88 library88 service88 gateway88 storage88", 10),
        ["prompt88", "session88", "library88", "service88", "gateway88", "storage88"],
    ),
    (
        ("prompt88 session88 library88 service88 gateway88 storage88", 18),
        ["prompt88 session88", "library88", "service88", "gateway88", "storage88"],
    ),
    (
        ("prompt88 session88 library88 service88 gateway88 storage88", 28),
        ["prompt88 session88 library88", "service88 gateway88", "storage88"],
    ),
    (
        ("session88 library88 service88 gateway88 storage88 network88", 6),
        ["session88", "library88", "service88", "gateway88", "storage88", "network88"],
    ),
    (
        ("session88 library88 service88 gateway88 storage88 network88", 10),
        ["session88", "library88", "service88", "gateway88", "storage88", "network88"],
    ),
    (
        ("session88 library88 service88 gateway88 storage88 network88", 18),
        ["session88", "library88", "service88", "gateway88", "storage88", "network88"],
    ),
    (
        ("session88 library88 service88 gateway88 storage88 network88", 28),
        ["session88 library88", "service88 gateway88", "storage88 network88"],
    ),
    (
        ("library88 service88 gateway88 storage88 network88 latency88", 6),
        ["library88", "service88", "gateway88", "storage88", "network88", "latency88"],
    ),
    (
        ("library88 service88 gateway88 storage88 network88 latency88", 10),
        ["library88", "service88", "gateway88", "storage88", "network88", "latency88"],
    ),
    (
        ("library88 service88 gateway88 storage88 network88 latency88", 18),
        ["library88", "service88", "gateway88", "storage88", "network88", "latency88"],
    ),
    (
        ("library88 service88 gateway88 storage88 network88 latency88", 28),
        ["library88 service88", "gateway88 storage88", "network88 latency88"],
    ),
    (
        ("service88 gateway88 storage88 network88 latency88 buffer88", 6),
        ["service88", "gateway88", "storage88", "network88", "latency88", "buffer88"],
    ),
    (
        ("service88 gateway88 storage88 network88 latency88 buffer88", 10),
        ["service88", "gateway88", "storage88", "network88", "latency88", "buffer88"],
    ),
    (
        ("service88 gateway88 storage88 network88 latency88 buffer88", 18),
        ["service88", "gateway88", "storage88", "network88", "latency88 buffer88"],
    ),
    (
        ("service88 gateway88 storage88 network88 latency88 buffer88", 28),
        ["service88 gateway88", "storage88 network88", "latency88 buffer88"],
    ),
    (
        ("gateway88 storage88 network88 latency88 buffer88 queue88", 6),
        ["gateway88", "storage88", "network88", "latency88", "buffer88", "queue88"],
    ),
    (
        ("gateway88 storage88 network88 latency88 buffer88 queue88", 10),
        ["gateway88", "storage88", "network88", "latency88", "buffer88", "queue88"],
    ),
    (
        ("gateway88 storage88 network88 latency88 buffer88 queue88", 18),
        ["gateway88", "storage88", "network88", "latency88 buffer88", "queue88"],
    ),
    (
        ("gateway88 storage88 network88 latency88 buffer88 queue88", 28),
        ["gateway88 storage88", "network88 latency88 buffer88", "queue88"],
    ),
    (
        ("storage88 network88 latency88 buffer88 queue88 worker88", 6),
        ["storage88", "network88", "latency88", "buffer88", "queue88", "worker88"],
    ),
    (
        ("storage88 network88 latency88 buffer88 queue88 worker88", 10),
        ["storage88", "network88", "latency88", "buffer88", "queue88", "worker88"],
    ),
    (
        ("storage88 network88 latency88 buffer88 queue88 worker88", 18),
        ["storage88", "network88", "latency88 buffer88", "queue88 worker88"],
    ),
    (
        ("storage88 network88 latency88 buffer88 queue88 worker88", 28),
        ["storage88 network88", "latency88 buffer88 queue88", "worker88"],
    ),
    (
        ("network88 latency88 buffer88 queue88 worker88 kernel88", 6),
        ["network88", "latency88", "buffer88", "queue88", "worker88", "kernel88"],
    ),
    (
        ("network88 latency88 buffer88 queue88 worker88 kernel88", 10),
        ["network88", "latency88", "buffer88", "queue88", "worker88", "kernel88"],
    ),
    (
        ("network88 latency88 buffer88 queue88 worker88 kernel88", 18),
        ["network88", "latency88 buffer88", "queue88 worker88", "kernel88"],
    ),
    (
        ("network88 latency88 buffer88 queue88 worker88 kernel88", 28),
        ["network88 latency88 buffer88", "queue88 worker88 kernel88"],
    ),
    (
        ("latency88 buffer88 queue88 worker88 kernel88 signal88", 6),
        ["latency88", "buffer88", "queue88", "worker88", "kernel88", "signal88"],
    ),
    (
        ("latency88 buffer88 queue88 worker88 kernel88 signal88", 10),
        ["latency88", "buffer88", "queue88", "worker88", "kernel88", "signal88"],
    ),
    (
        ("latency88 buffer88 queue88 worker88 kernel88 signal88", 18),
        ["latency88 buffer88", "queue88 worker88", "kernel88 signal88"],
    ),
    (
        ("latency88 buffer88 queue88 worker88 kernel88 signal88", 28),
        ["latency88 buffer88 queue88", "worker88 kernel88 signal88"],
    ),
    (
        ("buffer88 queue88 worker88 kernel88 signal88 packet88", 6),
        ["buffer88", "queue88", "worker88", "kernel88", "signal88", "packet88"],
    ),
    (
        ("buffer88 queue88 worker88 kernel88 signal88 packet88", 10),
        ["buffer88", "queue88", "worker88", "kernel88", "signal88", "packet88"],
    ),
    (
        ("buffer88 queue88 worker88 kernel88 signal88 packet88", 18),
        ["buffer88 queue88", "worker88 kernel88", "signal88 packet88"],
    ),
    (
        ("buffer88 queue88 worker88 kernel88 signal88 packet88", 28),
        ["buffer88 queue88 worker88", "kernel88 signal88 packet88"],
    ),
    (
        ("queue88 worker88 kernel88 signal88 packet88 router88", 6),
        ["queue88", "worker88", "kernel88", "signal88", "packet88", "router88"],
    ),
    (
        ("queue88 worker88 kernel88 signal88 packet88 router88", 10),
        ["queue88", "worker88", "kernel88", "signal88", "packet88", "router88"],
    ),
    (
        ("queue88 worker88 kernel88 signal88 packet88 router88", 18),
        ["queue88 worker88", "kernel88 signal88", "packet88 router88"],
    ),
    (
        ("queue88 worker88 kernel88 signal88 packet88 router88", 28),
        ["queue88 worker88 kernel88", "signal88 packet88 router88"],
    ),
    (
        ("worker88 kernel88 signal88 packet88 router88 cluster88", 6),
        ["worker88", "kernel88", "signal88", "packet88", "router88", "cluster88"],
    ),
    (
        ("worker88 kernel88 signal88 packet88 router88 cluster88", 10),
        ["worker88", "kernel88", "signal88", "packet88", "router88", "cluster88"],
    ),
    (
        ("worker88 kernel88 signal88 packet88 router88 cluster88", 18),
        ["worker88 kernel88", "signal88 packet88", "router88 cluster88"],
    ),
    (
        ("worker88 kernel88 signal88 packet88 router88 cluster88", 28),
        ["worker88 kernel88 signal88", "packet88 router88 cluster88"],
    ),
    (
        ("kernel88 signal88 packet88 router88 cluster88 mirror88", 6),
        ["kernel88", "signal88", "packet88", "router88", "cluster88", "mirror88"],
    ),
    (
        ("kernel88 signal88 packet88 router88 cluster88 mirror88", 10),
        ["kernel88", "signal88", "packet88", "router88", "cluster88", "mirror88"],
    ),
    (
        ("kernel88 signal88 packet88 router88 cluster88 mirror88", 18),
        ["kernel88 signal88", "packet88 router88", "cluster88 mirror88"],
    ),
    (
        ("kernel88 signal88 packet88 router88 cluster88 mirror88", 28),
        ["kernel88 signal88 packet88", "router88 cluster88 mirror88"],
    ),
    (
        ("signal88 packet88 router88 cluster88 mirror88 filter88", 6),
        ["signal88", "packet88", "router88", "cluster88", "mirror88", "filter88"],
    ),
    (
        ("signal88 packet88 router88 cluster88 mirror88 filter88", 10),
        ["signal88", "packet88", "router88", "cluster88", "mirror88", "filter88"],
    ),
    (
        ("signal88 packet88 router88 cluster88 mirror88 filter88", 18),
        ["signal88 packet88", "router88 cluster88", "mirror88 filter88"],
    ),
    (
        ("signal88 packet88 router88 cluster88 mirror88 filter88", 28),
        ["signal88 packet88 router88", "cluster88 mirror88 filter88"],
    ),
    (
        ("packet88 router88 cluster88 mirror88 filter88 ranking88", 6),
        ["packet88", "router88", "cluster88", "mirror88", "filter88", "ranking88"],
    ),
    (
        ("packet88 router88 cluster88 mirror88 filter88 ranking88", 10),
        ["packet88", "router88", "cluster88", "mirror88", "filter88", "ranking88"],
    ),
    (
        ("packet88 router88 cluster88 mirror88 filter88 ranking88", 18),
        ["packet88 router88", "cluster88 mirror88", "filter88 ranking88"],
    ),
    (
        ("packet88 router88 cluster88 mirror88 filter88 ranking88", 28),
        ["packet88 router88 cluster88", "mirror88 filter88 ranking88"],
    ),
    (
        ("router88 cluster88 mirror88 filter88 ranking88 encoding88", 6),
        ["router88", "cluster88", "mirror88", "filter88", "ranking88", "encoding88"],
    ),
    (
        ("router88 cluster88 mirror88 filter88 ranking88 encoding88", 10),
        ["router88", "cluster88", "mirror88", "filter88", "ranking88", "encoding88"],
    ),
    (
        ("router88 cluster88 mirror88 filter88 ranking88 encoding88", 18),
        ["router88 cluster88", "mirror88 filter88", "ranking88", "encoding88"],
    ),
    (
        ("router88 cluster88 mirror88 filter88 ranking88 encoding88", 28),
        ["router88 cluster88 mirror88", "filter88 ranking88", "encoding88"],
    ),
    (
        ("cluster88 mirror88 filter88 ranking88 encoding88 mapping88", 6),
        ["cluster88", "mirror88", "filter88", "ranking88", "encoding88", "mapping88"],
    ),
    (
        ("cluster88 mirror88 filter88 ranking88 encoding88 mapping88", 10),
        ["cluster88", "mirror88", "filter88", "ranking88", "encoding88", "mapping88"],
    ),
    (
        ("cluster88 mirror88 filter88 ranking88 encoding88 mapping88", 18),
        ["cluster88 mirror88", "filter88 ranking88", "encoding88", "mapping88"],
    ),
    (
        ("cluster88 mirror88 filter88 ranking88 encoding88 mapping88", 28),
        ["cluster88 mirror88 filter88", "ranking88 encoding88", "mapping88"],
    ),
    (
        ("mirror88 filter88 ranking88 encoding88 mapping88 record88", 6),
        ["mirror88", "filter88", "ranking88", "encoding88", "mapping88", "record88"],
    ),
    (
        ("mirror88 filter88 ranking88 encoding88 mapping88 record88", 10),
        ["mirror88", "filter88", "ranking88", "encoding88", "mapping88", "record88"],
    ),
    (
        ("mirror88 filter88 ranking88 encoding88 mapping88 record88", 18),
        ["mirror88 filter88", "ranking88", "encoding88", "mapping88 record88"],
    ),
    (
        ("mirror88 filter88 ranking88 encoding88 mapping88 record88", 28),
        ["mirror88 filter88 ranking88", "encoding88 mapping88", "record88"],
    ),
    (
        ("filter88 ranking88 encoding88 mapping88 record88 candle88", 6),
        ["filter88", "ranking88", "encoding88", "mapping88", "record88", "candle88"],
    ),
    (
        ("filter88 ranking88 encoding88 mapping88 record88 candle88", 10),
        ["filter88", "ranking88", "encoding88", "mapping88", "record88", "candle88"],
    ),
    (
        ("filter88 ranking88 encoding88 mapping88 record88 candle88", 18),
        ["filter88 ranking88", "encoding88", "mapping88 record88", "candle88"],
    ),
    (
        ("filter88 ranking88 encoding88 mapping88 record88 candle88", 28),
        ["filter88 ranking88", "encoding88 mapping88", "record88 candle88"],
    ),
    (
        ("ranking88 encoding88 mapping88 record88 candle88 thread88", 6),
        ["ranking88", "encoding88", "mapping88", "record88", "candle88", "thread88"],
    ),
    (
        ("ranking88 encoding88 mapping88 record88 candle88 thread88", 10),
        ["ranking88", "encoding88", "mapping88", "record88", "candle88", "thread88"],
    ),
    (
        ("ranking88 encoding88 mapping88 record88 candle88 thread88", 18),
        ["ranking88", "encoding88", "mapping88 record88", "candle88 thread88"],
    ),
    (
        ("ranking88 encoding88 mapping88 record88 candle88 thread88", 28),
        ["ranking88 encoding88", "mapping88 record88 candle88", "thread88"],
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
