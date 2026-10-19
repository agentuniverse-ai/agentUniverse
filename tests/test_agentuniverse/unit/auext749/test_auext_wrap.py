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
        ("round 749: the quick brown fox jumps over the lazy dog", 4),
        ["round", "749:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", 8),
        ["round", "749: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", 12),
        ["round 749:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", 16),
        ["round 749: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", 24),
        ["round 749: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 749: the quick brown fox jumps over the lazy dog", 32),
        ["round 749: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", 4),
        ["round", "749:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", 8),
        ["round", "749:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", 12),
        ["round 749:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", 16),
        ["round 749:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", 24),
        ["round 749: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 749: agentuniverse is a framework for multi agents", 32),
        ["round 749: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", 4),
        ["round", "749:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", 8),
        ["round", "749:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", 12),
        ["round 749:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", 16),
        ["round 749:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", 24),
        ["round 749: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 749: knowledge stored as vectors enables retrieval", 32),
        ["round 749: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 749: the processor reads the record then stops", 4),
        ["round", "749:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 749: the processor reads the record then stops", 8),
        ["round", "749: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 749: the processor reads the record then stops", 12),
        ["round 749:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 749: the processor reads the record then stops", 16),
        ["round 749: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 749: the processor reads the record then stops", 24),
        ["round 749: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 749: the processor reads the record then stops", 32),
        ["round 749: the processor reads", "the record then stops"],
    ),
    (
        ("round 749: a worker pulls the next task from the queue", 4),
        ["round", "749:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 749: a worker pulls the next task from the queue", 8),
        ["round", "749: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 749: a worker pulls the next task from the queue", 12),
        ["round 749: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 749: a worker pulls the next task from the queue", 16),
        ["round 749: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 749: a worker pulls the next task from the queue", 24),
        ["round 749: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 749: a worker pulls the next task from the queue", 32),
        ["round 749: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 749: signals travel through the network layer", 4),
        ["round", "749:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 749: signals travel through the network layer", 8),
        ["round", "749:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 749: signals travel through the network layer", 12),
        ["round 749:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 749: signals travel through the network layer", 16),
        ["round 749:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 749: signals travel through the network layer", 24),
        ["round 749: signals", "travel through the", "network layer"],
    ),
    (
        ("round 749: signals travel through the network layer", 32),
        ["round 749: signals travel", "through the network layer"],
    ),
    (
        ("round 749: the gateway routes each request by policy", 4),
        ["round", "749:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 749: the gateway routes each request by policy", 8),
        ["round", "749: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 749: the gateway routes each request by policy", 12),
        ["round 749:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 749: the gateway routes each request by policy", 16),
        ["round 749: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 749: the gateway routes each request by policy", 24),
        ["round 749: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 749: the gateway routes each request by policy", 32),
        ["round 749: the gateway routes", "each request by policy"],
    ),
    (
        ("round 749: memory grows until the buffer is full", 4),
        ["round", "749:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 749: memory grows until the buffer is full", 8),
        ["round", "749:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 749: memory grows until the buffer is full", 12),
        ["round 749:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 749: memory grows until the buffer is full", 16),
        ["round 749:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 749: memory grows until the buffer is full", 24), ["round 749: memory grows", "until the buffer is full"]),
    (("round 749: memory grows until the buffer is full", 32), ["round 749: memory grows until", "the buffer is full"]),
    (
        ("round 749: the cluster mirrors every packet twice", 4),
        ["round", "749:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 749: the cluster mirrors every packet twice", 8),
        ["round", "749: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 749: the cluster mirrors every packet twice", 12),
        ["round 749:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 749: the cluster mirrors every packet twice", 16),
        ["round 749: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 749: the cluster mirrors every packet twice", 24),
        ["round 749: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 749: the cluster mirrors every packet twice", 32),
        ["round 749: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", 4),
        ["round", "749:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", 8),
        ["round", "749:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", 12),
        ["round 749:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", 16),
        ["round 749:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", 24),
        ["round 749: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 749: ranking uses tokens learned from the corpus", 32),
        ["round 749: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 749: a long session ends when the candle dies", 4),
        ["round", "749:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 749: a long session ends when the candle dies", 8),
        ["round", "749: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 749: a long session ends when the candle dies", 12),
        ["round 749: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 749: a long session ends when the candle dies", 16),
        ["round 749: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 749: a long session ends when the candle dies", 24),
        ["round 749: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 749: a long session ends when the candle dies", 32),
        ["round 749: a long session ends", "when the candle dies"],
    ),
    (
        ("round 749: encode the prompt then map the result", 4),
        ["round", "749:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 749: encode the prompt then map the result", 8),
        ["round", "749:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 749: encode the prompt then map the result", 12),
        ["round 749:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 749: encode the prompt then map the result", 16),
        ["round 749:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 749: encode the prompt then map the result", 24),
        ["round 749: encode the", "prompt then map the", "result"],
    ),
    (("round 749: encode the prompt then map the result", 32), ["round 749: encode the prompt", "then map the result"]),
    (
        ("round 749: the kernel wakes the worker at dawn", 4),
        ["round", "749:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 749: the kernel wakes the worker at dawn", 8),
        ["round", "749: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 749: the kernel wakes the worker at dawn", 12),
        ["round 749:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 749: the kernel wakes the worker at dawn", 16), ["round 749: the", "kernel wakes the", "worker at dawn"]),
    (("round 749: the kernel wakes the worker at dawn", 24), ["round 749: the kernel", "wakes the worker at dawn"]),
    (("round 749: the kernel wakes the worker at dawn", 32), ["round 749: the kernel wakes the", "worker at dawn"]),
    (
        ("round 749: service latency drops after the patch", 4),
        ["round", "749:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 749: service latency drops after the patch", 8),
        ["round", "749:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 749: service latency drops after the patch", 12),
        ["round 749:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 749: service latency drops after the patch", 16),
        ["round 749:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 749: service latency drops after the patch", 24),
        ["round 749: service", "latency drops after the", "patch"],
    ),
    (("round 749: service latency drops after the patch", 32), ["round 749: service latency drops", "after the patch"]),
    (
        ("round 749: the library caches every vector it sees", 4),
        ["round", "749:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 749: the library caches every vector it sees", 8),
        ["round", "749: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 749: the library caches every vector it sees", 12),
        ["round 749:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 749: the library caches every vector it sees", 16),
        ["round 749: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 749: the library caches every vector it sees", 24),
        ["round 749: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 749: the library caches every vector it sees", 32),
        ["round 749: the library caches", "every vector it sees"],
    ),
    (
        ("round 749: agents argue then the debate resolves", 4),
        ["round", "749:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 749: agents argue then the debate resolves", 8),
        ["round", "749:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 749: agents argue then the debate resolves", 12),
        ["round 749:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 749: agents argue then the debate resolves", 16),
        ["round 749:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 749: agents argue then the debate resolves", 24), ["round 749: agents argue", "then the debate resolves"]),
    (("round 749: agents argue then the debate resolves", 32), ["round 749: agents argue then the", "debate resolves"]),
    (
        ("round 749: the filter keeps only strong matches", 4),
        ["round", "749:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 749: the filter keeps only strong matches", 8),
        ["round", "749: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 749: the filter keeps only strong matches", 12),
        ["round 749:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 749: the filter keeps only strong matches", 16),
        ["round 749: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 749: the filter keeps only strong matches", 24),
        ["round 749: the filter", "keeps only strong", "matches"],
    ),
    (("round 749: the filter keeps only strong matches", 32), ["round 749: the filter keeps only", "strong matches"]),
    (
        ("round 749: the model answers with a short reply", 4),
        ["round", "749:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 749: the model answers with a short reply", 8),
        ["round", "749: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 749: the model answers with a short reply", 12),
        ["round 749:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 749: the model answers with a short reply", 16),
        ["round 749: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 749: the model answers with a short reply", 24),
        ["round 749: the model", "answers with a short", "reply"],
    ),
    (("round 749: the model answers with a short reply", 32), ["round 749: the model answers", "with a short reply"]),
    (
        ("round 749: the recorder stores the reasoning trace", 4),
        ["round", "749:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 749: the recorder stores the reasoning trace", 8),
        ["round", "749: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 749: the recorder stores the reasoning trace", 12),
        ["round 749:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 749: the recorder stores the reasoning trace", 16),
        ["round 749: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 749: the recorder stores the reasoning trace", 24),
        ["round 749: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 749: the recorder stores the reasoning trace", 32),
        ["round 749: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 749: the angel watches the processor run", 4),
        ["round", "749:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 749: the angel watches the processor run", 8),
        ["round", "749: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 749: the angel watches the processor run", 12),
        ["round 749:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 749: the angel watches the processor run", 16),
        ["round 749: the", "angel watches", "the processor", "run"],
    ),
    (("round 749: the angel watches the processor run", 24), ["round 749: the angel", "watches the processor", "run"]),
    (("round 749: the angel watches the processor run", 32), ["round 749: the angel watches the", "processor run"]),
    (
        ("round 749: angle of the vector decides the match", 4),
        ["round", "749:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 749: angle of the vector decides the match", 8),
        ["round", "749:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 749: angle of the vector decides the match", 12),
        ["round 749:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 749: angle of the vector decides the match", 16),
        ["round 749: angle", "of the vector", "decides the", "match"],
    ),
    (("round 749: angle of the vector decides the match", 24), ["round 749: angle of the", "vector decides the match"]),
    (("round 749: angle of the vector decides the match", 32), ["round 749: angle of the vector", "decides the match"]),
    (
        ("round 749: the candle burns twice as long at night", 4),
        ["round", "749:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 749: the candle burns twice as long at night", 8),
        ["round", "749: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 749: the candle burns twice as long at night", 12),
        ["round 749:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 749: the candle burns twice as long at night", 16),
        ["round 749: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 749: the candle burns twice as long at night", 24),
        ["round 749: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 749: the candle burns twice as long at night", 32),
        ["round 749: the candle burns", "twice as long at night"],
    ),
    (
        ("round 749: a mirror of the universe in one line", 4),
        ["round", "749:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 749: a mirror of the universe in one line", 8),
        ["round", "749: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 749: a mirror of the universe in one line", 12),
        ["round 749: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 749: a mirror of the universe in one line", 16),
        ["round 749: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 749: a mirror of the universe in one line", 24), ["round 749: a mirror of", "the universe in one line"]),
    (("round 749: a mirror of the universe in one line", 32), ["round 749: a mirror of the", "universe in one line"]),
    (
        ("round 749: the queue drains before the storm", 4),
        ["round", "749:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 749: the queue drains before the storm", 8),
        ["round", "749: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 749: the queue drains before the storm", 12),
        ["round 749:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 749: the queue drains before the storm", 16), ["round 749: the", "queue drains", "before the storm"]),
    (("round 749: the queue drains before the storm", 24), ["round 749: the queue", "drains before the storm"]),
    (("round 749: the queue drains before the storm", 32), ["round 749: the queue drains", "before the storm"]),
    (
        ("kitten749 sitting749 agent749 angle749 universe749 memory749", 6),
        ["kitten749", "sitting749", "agent749", "angle749", "universe749", "memory749"],
    ),
    (
        ("kitten749 sitting749 agent749 angle749 universe749 memory749", 10),
        ["kitten749", "sitting749", "agent749", "angle749", "universe749", "memory749"],
    ),
    (
        ("kitten749 sitting749 agent749 angle749 universe749 memory749", 18),
        ["kitten749", "sitting749", "agent749 angle749", "universe749", "memory749"],
    ),
    (
        ("kitten749 sitting749 agent749 angle749 universe749 memory749", 28),
        ["kitten749 sitting749", "agent749 angle749", "universe749 memory749"],
    ),
    (
        ("sitting749 agent749 angle749 universe749 memory749 stream749", 6),
        ["sitting749", "agent749", "angle749", "universe749", "memory749", "stream749"],
    ),
    (
        ("sitting749 agent749 angle749 universe749 memory749 stream749", 10),
        ["sitting749", "agent749", "angle749", "universe749", "memory749", "stream749"],
    ),
    (
        ("sitting749 agent749 angle749 universe749 memory749 stream749", 18),
        ["sitting749", "agent749 angle749", "universe749", "memory749", "stream749"],
    ),
    (
        ("sitting749 agent749 angle749 universe749 memory749 stream749", 28),
        ["sitting749 agent749 angle749", "universe749 memory749", "stream749"],
    ),
    (
        ("agent749 angle749 universe749 memory749 stream749 context749", 6),
        ["agent749", "angle749", "universe749", "memory749", "stream749", "context749"],
    ),
    (
        ("agent749 angle749 universe749 memory749 stream749 context749", 10),
        ["agent749", "angle749", "universe749", "memory749", "stream749", "context749"],
    ),
    (
        ("agent749 angle749 universe749 memory749 stream749 context749", 18),
        ["agent749 angle749", "universe749", "memory749", "stream749", "context749"],
    ),
    (
        ("agent749 angle749 universe749 memory749 stream749 context749", 28),
        ["agent749 angle749", "universe749 memory749", "stream749 context749"],
    ),
    (
        ("angle749 universe749 memory749 stream749 context749 knowledge749", 6),
        ["angle749", "universe749", "memory749", "stream749", "context749", "knowledge749"],
    ),
    (
        ("angle749 universe749 memory749 stream749 context749 knowledge749", 10),
        ["angle749", "universe749", "memory749", "stream749", "context749", "knowledge749"],
    ),
    (
        ("angle749 universe749 memory749 stream749 context749 knowledge749", 18),
        ["angle749", "universe749", "memory749", "stream749", "context749", "knowledge749"],
    ),
    (
        ("angle749 universe749 memory749 stream749 context749 knowledge749", 28),
        ["angle749 universe749", "memory749 stream749", "context749 knowledge749"],
    ),
    (
        ("universe749 memory749 stream749 context749 knowledge749 vector749", 6),
        ["universe749", "memory749", "stream749", "context749", "knowledge749", "vector749"],
    ),
    (
        ("universe749 memory749 stream749 context749 knowledge749 vector749", 10),
        ["universe749", "memory749", "stream749", "context749", "knowledge749", "vector749"],
    ),
    (
        ("universe749 memory749 stream749 context749 knowledge749 vector749", 18),
        ["universe749", "memory749", "stream749", "context749", "knowledge749", "vector749"],
    ),
    (
        ("universe749 memory749 stream749 context749 knowledge749 vector749", 28),
        ["universe749 memory749", "stream749 context749", "knowledge749 vector749"],
    ),
    (
        ("memory749 stream749 context749 knowledge749 vector749 processor749", 6),
        ["memory749", "stream749", "context749", "knowledge749", "vector749", "processor749"],
    ),
    (
        ("memory749 stream749 context749 knowledge749 vector749 processor749", 10),
        ["memory749", "stream749", "context749", "knowledge749", "vector749", "processor749"],
    ),
    (
        ("memory749 stream749 context749 knowledge749 vector749 processor749", 18),
        ["memory749", "stream749", "context749", "knowledge749", "vector749", "processor749"],
    ),
    (
        ("memory749 stream749 context749 knowledge749 vector749 processor749", 28),
        ["memory749 stream749", "context749 knowledge749", "vector749 processor749"],
    ),
    (
        ("stream749 context749 knowledge749 vector749 processor749 reasoning749", 6),
        ["stream749", "context749", "knowledge749", "vector749", "processor749", "reasoning749"],
    ),
    (
        ("stream749 context749 knowledge749 vector749 processor749 reasoning749", 10),
        ["stream749", "context749", "knowledge749", "vector749", "processor749", "reasoning749"],
    ),
    (
        ("stream749 context749 knowledge749 vector749 processor749 reasoning749", 18),
        ["stream749", "context749", "knowledge749", "vector749", "processor749", "reasoning749"],
    ),
    (
        ("stream749 context749 knowledge749 vector749 processor749 reasoning749", 28),
        ["stream749 context749", "knowledge749 vector749", "processor749 reasoning749"],
    ),
    (
        ("context749 knowledge749 vector749 processor749 reasoning749 machine749", 6),
        ["context749", "knowledge749", "vector749", "processor749", "reasoning749", "machine749"],
    ),
    (
        ("context749 knowledge749 vector749 processor749 reasoning749 machine749", 10),
        ["context749", "knowledge749", "vector749", "processor749", "reasoning749", "machine749"],
    ),
    (
        ("context749 knowledge749 vector749 processor749 reasoning749 machine749", 18),
        ["context749", "knowledge749", "vector749", "processor749", "reasoning749", "machine749"],
    ),
    (
        ("context749 knowledge749 vector749 processor749 reasoning749 machine749", 28),
        ["context749 knowledge749", "vector749 processor749", "reasoning749 machine749"],
    ),
    (
        ("knowledge749 vector749 processor749 reasoning749 machine749 learning749", 6),
        ["knowledge749", "vector749", "processor749", "reasoning749", "machine749", "learning749"],
    ),
    (
        ("knowledge749 vector749 processor749 reasoning749 machine749 learning749", 10),
        ["knowledge749", "vector749", "processor749", "reasoning749", "machine749", "learning749"],
    ),
    (
        ("knowledge749 vector749 processor749 reasoning749 machine749 learning749", 18),
        ["knowledge749", "vector749", "processor749", "reasoning749", "machine749", "learning749"],
    ),
    (
        ("knowledge749 vector749 processor749 reasoning749 machine749 learning749", 28),
        ["knowledge749 vector749", "processor749 reasoning749", "machine749 learning749"],
    ),
    (
        ("vector749 processor749 reasoning749 machine749 learning749 model749", 6),
        ["vector749", "processor749", "reasoning749", "machine749", "learning749", "model749"],
    ),
    (
        ("vector749 processor749 reasoning749 machine749 learning749 model749", 10),
        ["vector749", "processor749", "reasoning749", "machine749", "learning749", "model749"],
    ),
    (
        ("vector749 processor749 reasoning749 machine749 learning749 model749", 18),
        ["vector749", "processor749", "reasoning749", "machine749", "learning749", "model749"],
    ),
    (
        ("vector749 processor749 reasoning749 machine749 learning749 model749", 28),
        ["vector749 processor749", "reasoning749 machine749", "learning749 model749"],
    ),
    (
        ("processor749 reasoning749 machine749 learning749 model749 token749", 6),
        ["processor749", "reasoning749", "machine749", "learning749", "model749", "token749"],
    ),
    (
        ("processor749 reasoning749 machine749 learning749 model749 token749", 10),
        ["processor749", "reasoning749", "machine749", "learning749", "model749", "token749"],
    ),
    (
        ("processor749 reasoning749 machine749 learning749 model749 token749", 18),
        ["processor749", "reasoning749", "machine749", "learning749", "model749 token749"],
    ),
    (
        ("processor749 reasoning749 machine749 learning749 model749 token749", 28),
        ["processor749 reasoning749", "machine749 learning749", "model749 token749"],
    ),
    (
        ("reasoning749 machine749 learning749 model749 token749 prompt749", 6),
        ["reasoning749", "machine749", "learning749", "model749", "token749", "prompt749"],
    ),
    (
        ("reasoning749 machine749 learning749 model749 token749 prompt749", 10),
        ["reasoning749", "machine749", "learning749", "model749", "token749", "prompt749"],
    ),
    (
        ("reasoning749 machine749 learning749 model749 token749 prompt749", 18),
        ["reasoning749", "machine749", "learning749", "model749 token749", "prompt749"],
    ),
    (
        ("reasoning749 machine749 learning749 model749 token749 prompt749", 28),
        ["reasoning749 machine749", "learning749 model749", "token749 prompt749"],
    ),
    (
        ("machine749 learning749 model749 token749 prompt749 session749", 6),
        ["machine749", "learning749", "model749", "token749", "prompt749", "session749"],
    ),
    (
        ("machine749 learning749 model749 token749 prompt749 session749", 10),
        ["machine749", "learning749", "model749", "token749", "prompt749", "session749"],
    ),
    (
        ("machine749 learning749 model749 token749 prompt749 session749", 18),
        ["machine749", "learning749", "model749 token749", "prompt749", "session749"],
    ),
    (
        ("machine749 learning749 model749 token749 prompt749 session749", 28),
        ["machine749 learning749", "model749 token749 prompt749", "session749"],
    ),
    (
        ("learning749 model749 token749 prompt749 session749 library749", 6),
        ["learning749", "model749", "token749", "prompt749", "session749", "library749"],
    ),
    (
        ("learning749 model749 token749 prompt749 session749 library749", 10),
        ["learning749", "model749", "token749", "prompt749", "session749", "library749"],
    ),
    (
        ("learning749 model749 token749 prompt749 session749 library749", 18),
        ["learning749", "model749 token749", "prompt749", "session749", "library749"],
    ),
    (
        ("learning749 model749 token749 prompt749 session749 library749", 28),
        ["learning749 model749", "token749 prompt749", "session749 library749"],
    ),
    (
        ("model749 token749 prompt749 session749 library749 service749", 6),
        ["model749", "token749", "prompt749", "session749", "library749", "service749"],
    ),
    (
        ("model749 token749 prompt749 session749 library749 service749", 10),
        ["model749", "token749", "prompt749", "session749", "library749", "service749"],
    ),
    (
        ("model749 token749 prompt749 session749 library749 service749", 18),
        ["model749 token749", "prompt749", "session749", "library749", "service749"],
    ),
    (
        ("model749 token749 prompt749 session749 library749 service749", 28),
        ["model749 token749 prompt749", "session749 library749", "service749"],
    ),
    (
        ("token749 prompt749 session749 library749 service749 gateway749", 6),
        ["token749", "prompt749", "session749", "library749", "service749", "gateway749"],
    ),
    (
        ("token749 prompt749 session749 library749 service749 gateway749", 10),
        ["token749", "prompt749", "session749", "library749", "service749", "gateway749"],
    ),
    (
        ("token749 prompt749 session749 library749 service749 gateway749", 18),
        ["token749 prompt749", "session749", "library749", "service749", "gateway749"],
    ),
    (
        ("token749 prompt749 session749 library749 service749 gateway749", 28),
        ["token749 prompt749", "session749 library749", "service749 gateway749"],
    ),
    (
        ("prompt749 session749 library749 service749 gateway749 storage749", 6),
        ["prompt749", "session749", "library749", "service749", "gateway749", "storage749"],
    ),
    (
        ("prompt749 session749 library749 service749 gateway749 storage749", 10),
        ["prompt749", "session749", "library749", "service749", "gateway749", "storage749"],
    ),
    (
        ("prompt749 session749 library749 service749 gateway749 storage749", 18),
        ["prompt749", "session749", "library749", "service749", "gateway749", "storage749"],
    ),
    (
        ("prompt749 session749 library749 service749 gateway749 storage749", 28),
        ["prompt749 session749", "library749 service749", "gateway749 storage749"],
    ),
    (
        ("session749 library749 service749 gateway749 storage749 network749", 6),
        ["session749", "library749", "service749", "gateway749", "storage749", "network749"],
    ),
    (
        ("session749 library749 service749 gateway749 storage749 network749", 10),
        ["session749", "library749", "service749", "gateway749", "storage749", "network749"],
    ),
    (
        ("session749 library749 service749 gateway749 storage749 network749", 18),
        ["session749", "library749", "service749", "gateway749", "storage749", "network749"],
    ),
    (
        ("session749 library749 service749 gateway749 storage749 network749", 28),
        ["session749 library749", "service749 gateway749", "storage749 network749"],
    ),
    (
        ("library749 service749 gateway749 storage749 network749 latency749", 6),
        ["library749", "service749", "gateway749", "storage749", "network749", "latency749"],
    ),
    (
        ("library749 service749 gateway749 storage749 network749 latency749", 10),
        ["library749", "service749", "gateway749", "storage749", "network749", "latency749"],
    ),
    (
        ("library749 service749 gateway749 storage749 network749 latency749", 18),
        ["library749", "service749", "gateway749", "storage749", "network749", "latency749"],
    ),
    (
        ("library749 service749 gateway749 storage749 network749 latency749", 28),
        ["library749 service749", "gateway749 storage749", "network749 latency749"],
    ),
    (
        ("service749 gateway749 storage749 network749 latency749 buffer749", 6),
        ["service749", "gateway749", "storage749", "network749", "latency749", "buffer749"],
    ),
    (
        ("service749 gateway749 storage749 network749 latency749 buffer749", 10),
        ["service749", "gateway749", "storage749", "network749", "latency749", "buffer749"],
    ),
    (
        ("service749 gateway749 storage749 network749 latency749 buffer749", 18),
        ["service749", "gateway749", "storage749", "network749", "latency749", "buffer749"],
    ),
    (
        ("service749 gateway749 storage749 network749 latency749 buffer749", 28),
        ["service749 gateway749", "storage749 network749", "latency749 buffer749"],
    ),
    (
        ("gateway749 storage749 network749 latency749 buffer749 queue749", 6),
        ["gateway749", "storage749", "network749", "latency749", "buffer749", "queue749"],
    ),
    (
        ("gateway749 storage749 network749 latency749 buffer749 queue749", 10),
        ["gateway749", "storage749", "network749", "latency749", "buffer749", "queue749"],
    ),
    (
        ("gateway749 storage749 network749 latency749 buffer749 queue749", 18),
        ["gateway749", "storage749", "network749", "latency749", "buffer749 queue749"],
    ),
    (
        ("gateway749 storage749 network749 latency749 buffer749 queue749", 28),
        ["gateway749 storage749", "network749 latency749", "buffer749 queue749"],
    ),
    (
        ("storage749 network749 latency749 buffer749 queue749 worker749", 6),
        ["storage749", "network749", "latency749", "buffer749", "queue749", "worker749"],
    ),
    (
        ("storage749 network749 latency749 buffer749 queue749 worker749", 10),
        ["storage749", "network749", "latency749", "buffer749", "queue749", "worker749"],
    ),
    (
        ("storage749 network749 latency749 buffer749 queue749 worker749", 18),
        ["storage749", "network749", "latency749", "buffer749 queue749", "worker749"],
    ),
    (
        ("storage749 network749 latency749 buffer749 queue749 worker749", 28),
        ["storage749 network749", "latency749 buffer749", "queue749 worker749"],
    ),
    (
        ("network749 latency749 buffer749 queue749 worker749 kernel749", 6),
        ["network749", "latency749", "buffer749", "queue749", "worker749", "kernel749"],
    ),
    (
        ("network749 latency749 buffer749 queue749 worker749 kernel749", 10),
        ["network749", "latency749", "buffer749", "queue749", "worker749", "kernel749"],
    ),
    (
        ("network749 latency749 buffer749 queue749 worker749 kernel749", 18),
        ["network749", "latency749", "buffer749 queue749", "worker749", "kernel749"],
    ),
    (
        ("network749 latency749 buffer749 queue749 worker749 kernel749", 28),
        ["network749 latency749", "buffer749 queue749 worker749", "kernel749"],
    ),
    (
        ("latency749 buffer749 queue749 worker749 kernel749 signal749", 6),
        ["latency749", "buffer749", "queue749", "worker749", "kernel749", "signal749"],
    ),
    (
        ("latency749 buffer749 queue749 worker749 kernel749 signal749", 10),
        ["latency749", "buffer749", "queue749", "worker749", "kernel749", "signal749"],
    ),
    (
        ("latency749 buffer749 queue749 worker749 kernel749 signal749", 18),
        ["latency749", "buffer749 queue749", "worker749", "kernel749", "signal749"],
    ),
    (
        ("latency749 buffer749 queue749 worker749 kernel749 signal749", 28),
        ["latency749 buffer749", "queue749 worker749 kernel749", "signal749"],
    ),
    (
        ("buffer749 queue749 worker749 kernel749 signal749 packet749", 6),
        ["buffer749", "queue749", "worker749", "kernel749", "signal749", "packet749"],
    ),
    (
        ("buffer749 queue749 worker749 kernel749 signal749 packet749", 10),
        ["buffer749", "queue749", "worker749", "kernel749", "signal749", "packet749"],
    ),
    (
        ("buffer749 queue749 worker749 kernel749 signal749 packet749", 18),
        ["buffer749 queue749", "worker749", "kernel749", "signal749", "packet749"],
    ),
    (
        ("buffer749 queue749 worker749 kernel749 signal749 packet749", 28),
        ["buffer749 queue749 worker749", "kernel749 signal749", "packet749"],
    ),
    (
        ("queue749 worker749 kernel749 signal749 packet749 router749", 6),
        ["queue749", "worker749", "kernel749", "signal749", "packet749", "router749"],
    ),
    (
        ("queue749 worker749 kernel749 signal749 packet749 router749", 10),
        ["queue749", "worker749", "kernel749", "signal749", "packet749", "router749"],
    ),
    (
        ("queue749 worker749 kernel749 signal749 packet749 router749", 18),
        ["queue749 worker749", "kernel749", "signal749", "packet749", "router749"],
    ),
    (
        ("queue749 worker749 kernel749 signal749 packet749 router749", 28),
        ["queue749 worker749 kernel749", "signal749 packet749", "router749"],
    ),
    (
        ("worker749 kernel749 signal749 packet749 router749 cluster749", 6),
        ["worker749", "kernel749", "signal749", "packet749", "router749", "cluster749"],
    ),
    (
        ("worker749 kernel749 signal749 packet749 router749 cluster749", 10),
        ["worker749", "kernel749", "signal749", "packet749", "router749", "cluster749"],
    ),
    (
        ("worker749 kernel749 signal749 packet749 router749 cluster749", 18),
        ["worker749", "kernel749", "signal749", "packet749", "router749", "cluster749"],
    ),
    (
        ("worker749 kernel749 signal749 packet749 router749 cluster749", 28),
        ["worker749 kernel749", "signal749 packet749", "router749 cluster749"],
    ),
    (
        ("kernel749 signal749 packet749 router749 cluster749 mirror749", 6),
        ["kernel749", "signal749", "packet749", "router749", "cluster749", "mirror749"],
    ),
    (
        ("kernel749 signal749 packet749 router749 cluster749 mirror749", 10),
        ["kernel749", "signal749", "packet749", "router749", "cluster749", "mirror749"],
    ),
    (
        ("kernel749 signal749 packet749 router749 cluster749 mirror749", 18),
        ["kernel749", "signal749", "packet749", "router749", "cluster749", "mirror749"],
    ),
    (
        ("kernel749 signal749 packet749 router749 cluster749 mirror749", 28),
        ["kernel749 signal749", "packet749 router749", "cluster749 mirror749"],
    ),
    (
        ("signal749 packet749 router749 cluster749 mirror749 filter749", 6),
        ["signal749", "packet749", "router749", "cluster749", "mirror749", "filter749"],
    ),
    (
        ("signal749 packet749 router749 cluster749 mirror749 filter749", 10),
        ["signal749", "packet749", "router749", "cluster749", "mirror749", "filter749"],
    ),
    (
        ("signal749 packet749 router749 cluster749 mirror749 filter749", 18),
        ["signal749", "packet749", "router749", "cluster749", "mirror749", "filter749"],
    ),
    (
        ("signal749 packet749 router749 cluster749 mirror749 filter749", 28),
        ["signal749 packet749", "router749 cluster749", "mirror749 filter749"],
    ),
    (
        ("packet749 router749 cluster749 mirror749 filter749 ranking749", 6),
        ["packet749", "router749", "cluster749", "mirror749", "filter749", "ranking749"],
    ),
    (
        ("packet749 router749 cluster749 mirror749 filter749 ranking749", 10),
        ["packet749", "router749", "cluster749", "mirror749", "filter749", "ranking749"],
    ),
    (
        ("packet749 router749 cluster749 mirror749 filter749 ranking749", 18),
        ["packet749", "router749", "cluster749", "mirror749", "filter749", "ranking749"],
    ),
    (
        ("packet749 router749 cluster749 mirror749 filter749 ranking749", 28),
        ["packet749 router749", "cluster749 mirror749", "filter749 ranking749"],
    ),
    (
        ("router749 cluster749 mirror749 filter749 ranking749 encoding749", 6),
        ["router749", "cluster749", "mirror749", "filter749", "ranking749", "encoding749"],
    ),
    (
        ("router749 cluster749 mirror749 filter749 ranking749 encoding749", 10),
        ["router749", "cluster749", "mirror749", "filter749", "ranking749", "encoding749"],
    ),
    (
        ("router749 cluster749 mirror749 filter749 ranking749 encoding749", 18),
        ["router749", "cluster749", "mirror749", "filter749", "ranking749", "encoding749"],
    ),
    (
        ("router749 cluster749 mirror749 filter749 ranking749 encoding749", 28),
        ["router749 cluster749", "mirror749 filter749", "ranking749 encoding749"],
    ),
    (
        ("cluster749 mirror749 filter749 ranking749 encoding749 mapping749", 6),
        ["cluster749", "mirror749", "filter749", "ranking749", "encoding749", "mapping749"],
    ),
    (
        ("cluster749 mirror749 filter749 ranking749 encoding749 mapping749", 10),
        ["cluster749", "mirror749", "filter749", "ranking749", "encoding749", "mapping749"],
    ),
    (
        ("cluster749 mirror749 filter749 ranking749 encoding749 mapping749", 18),
        ["cluster749", "mirror749", "filter749", "ranking749", "encoding749", "mapping749"],
    ),
    (
        ("cluster749 mirror749 filter749 ranking749 encoding749 mapping749", 28),
        ["cluster749 mirror749", "filter749 ranking749", "encoding749 mapping749"],
    ),
    (
        ("mirror749 filter749 ranking749 encoding749 mapping749 record749", 6),
        ["mirror749", "filter749", "ranking749", "encoding749", "mapping749", "record749"],
    ),
    (
        ("mirror749 filter749 ranking749 encoding749 mapping749 record749", 10),
        ["mirror749", "filter749", "ranking749", "encoding749", "mapping749", "record749"],
    ),
    (
        ("mirror749 filter749 ranking749 encoding749 mapping749 record749", 18),
        ["mirror749", "filter749", "ranking749", "encoding749", "mapping749", "record749"],
    ),
    (
        ("mirror749 filter749 ranking749 encoding749 mapping749 record749", 28),
        ["mirror749 filter749", "ranking749 encoding749", "mapping749 record749"],
    ),
    (
        ("filter749 ranking749 encoding749 mapping749 record749 candle749", 6),
        ["filter749", "ranking749", "encoding749", "mapping749", "record749", "candle749"],
    ),
    (
        ("filter749 ranking749 encoding749 mapping749 record749 candle749", 10),
        ["filter749", "ranking749", "encoding749", "mapping749", "record749", "candle749"],
    ),
    (
        ("filter749 ranking749 encoding749 mapping749 record749 candle749", 18),
        ["filter749", "ranking749", "encoding749", "mapping749", "record749", "candle749"],
    ),
    (
        ("filter749 ranking749 encoding749 mapping749 record749 candle749", 28),
        ["filter749 ranking749", "encoding749 mapping749", "record749 candle749"],
    ),
    (
        ("ranking749 encoding749 mapping749 record749 candle749 thread749", 6),
        ["ranking749", "encoding749", "mapping749", "record749", "candle749", "thread749"],
    ),
    (
        ("ranking749 encoding749 mapping749 record749 candle749 thread749", 10),
        ["ranking749", "encoding749", "mapping749", "record749", "candle749", "thread749"],
    ),
    (
        ("ranking749 encoding749 mapping749 record749 candle749 thread749", 18),
        ["ranking749", "encoding749", "mapping749", "record749", "candle749", "thread749"],
    ),
    (
        ("ranking749 encoding749 mapping749 record749 candle749 thread749", 28),
        ["ranking749 encoding749", "mapping749 record749", "candle749 thread749"],
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
