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
        ("round 142: the quick brown fox jumps over the lazy dog", 4),
        ["round", "142:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", 8),
        ["round", "142: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", 12),
        ["round 142:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", 16),
        ["round 142: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", 24),
        ["round 142: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 142: the quick brown fox jumps over the lazy dog", 32),
        ["round 142: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", 4),
        ["round", "142:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", 8),
        ["round", "142:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", 12),
        ["round 142:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", 16),
        ["round 142:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", 24),
        ["round 142: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 142: agentuniverse is a framework for multi agents", 32),
        ["round 142: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", 4),
        ["round", "142:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", 8),
        ["round", "142:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", 12),
        ["round 142:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", 16),
        ["round 142:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", 24),
        ["round 142: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 142: knowledge stored as vectors enables retrieval", 32),
        ["round 142: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 142: the processor reads the record then stops", 4),
        ["round", "142:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 142: the processor reads the record then stops", 8),
        ["round", "142: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 142: the processor reads the record then stops", 12),
        ["round 142:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 142: the processor reads the record then stops", 16),
        ["round 142: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 142: the processor reads the record then stops", 24),
        ["round 142: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 142: the processor reads the record then stops", 32),
        ["round 142: the processor reads", "the record then stops"],
    ),
    (
        ("round 142: a worker pulls the next task from the queue", 4),
        ["round", "142:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 142: a worker pulls the next task from the queue", 8),
        ["round", "142: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 142: a worker pulls the next task from the queue", 12),
        ["round 142: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 142: a worker pulls the next task from the queue", 16),
        ["round 142: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 142: a worker pulls the next task from the queue", 24),
        ["round 142: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 142: a worker pulls the next task from the queue", 32),
        ["round 142: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 142: signals travel through the network layer", 4),
        ["round", "142:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 142: signals travel through the network layer", 8),
        ["round", "142:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 142: signals travel through the network layer", 12),
        ["round 142:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 142: signals travel through the network layer", 16),
        ["round 142:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 142: signals travel through the network layer", 24),
        ["round 142: signals", "travel through the", "network layer"],
    ),
    (
        ("round 142: signals travel through the network layer", 32),
        ["round 142: signals travel", "through the network layer"],
    ),
    (
        ("round 142: the gateway routes each request by policy", 4),
        ["round", "142:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 142: the gateway routes each request by policy", 8),
        ["round", "142: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 142: the gateway routes each request by policy", 12),
        ["round 142:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 142: the gateway routes each request by policy", 16),
        ["round 142: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 142: the gateway routes each request by policy", 24),
        ["round 142: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 142: the gateway routes each request by policy", 32),
        ["round 142: the gateway routes", "each request by policy"],
    ),
    (
        ("round 142: memory grows until the buffer is full", 4),
        ["round", "142:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 142: memory grows until the buffer is full", 8),
        ["round", "142:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 142: memory grows until the buffer is full", 12),
        ["round 142:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 142: memory grows until the buffer is full", 16),
        ["round 142:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 142: memory grows until the buffer is full", 24), ["round 142: memory grows", "until the buffer is full"]),
    (("round 142: memory grows until the buffer is full", 32), ["round 142: memory grows until", "the buffer is full"]),
    (
        ("round 142: the cluster mirrors every packet twice", 4),
        ["round", "142:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 142: the cluster mirrors every packet twice", 8),
        ["round", "142: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 142: the cluster mirrors every packet twice", 12),
        ["round 142:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 142: the cluster mirrors every packet twice", 16),
        ["round 142: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 142: the cluster mirrors every packet twice", 24),
        ["round 142: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 142: the cluster mirrors every packet twice", 32),
        ["round 142: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", 4),
        ["round", "142:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", 8),
        ["round", "142:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", 12),
        ["round 142:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", 16),
        ["round 142:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", 24),
        ["round 142: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 142: ranking uses tokens learned from the corpus", 32),
        ["round 142: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 142: a long session ends when the candle dies", 4),
        ["round", "142:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 142: a long session ends when the candle dies", 8),
        ["round", "142: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 142: a long session ends when the candle dies", 12),
        ["round 142: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 142: a long session ends when the candle dies", 16),
        ["round 142: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 142: a long session ends when the candle dies", 24),
        ["round 142: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 142: a long session ends when the candle dies", 32),
        ["round 142: a long session ends", "when the candle dies"],
    ),
    (
        ("round 142: encode the prompt then map the result", 4),
        ["round", "142:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 142: encode the prompt then map the result", 8),
        ["round", "142:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 142: encode the prompt then map the result", 12),
        ["round 142:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 142: encode the prompt then map the result", 16),
        ["round 142:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 142: encode the prompt then map the result", 24),
        ["round 142: encode the", "prompt then map the", "result"],
    ),
    (("round 142: encode the prompt then map the result", 32), ["round 142: encode the prompt", "then map the result"]),
    (
        ("round 142: the kernel wakes the worker at dawn", 4),
        ["round", "142:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 142: the kernel wakes the worker at dawn", 8),
        ["round", "142: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 142: the kernel wakes the worker at dawn", 12),
        ["round 142:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 142: the kernel wakes the worker at dawn", 16), ["round 142: the", "kernel wakes the", "worker at dawn"]),
    (("round 142: the kernel wakes the worker at dawn", 24), ["round 142: the kernel", "wakes the worker at dawn"]),
    (("round 142: the kernel wakes the worker at dawn", 32), ["round 142: the kernel wakes the", "worker at dawn"]),
    (
        ("round 142: service latency drops after the patch", 4),
        ["round", "142:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 142: service latency drops after the patch", 8),
        ["round", "142:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 142: service latency drops after the patch", 12),
        ["round 142:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 142: service latency drops after the patch", 16),
        ["round 142:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 142: service latency drops after the patch", 24),
        ["round 142: service", "latency drops after the", "patch"],
    ),
    (("round 142: service latency drops after the patch", 32), ["round 142: service latency drops", "after the patch"]),
    (
        ("round 142: the library caches every vector it sees", 4),
        ["round", "142:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 142: the library caches every vector it sees", 8),
        ["round", "142: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 142: the library caches every vector it sees", 12),
        ["round 142:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 142: the library caches every vector it sees", 16),
        ["round 142: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 142: the library caches every vector it sees", 24),
        ["round 142: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 142: the library caches every vector it sees", 32),
        ["round 142: the library caches", "every vector it sees"],
    ),
    (
        ("round 142: agents argue then the debate resolves", 4),
        ["round", "142:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 142: agents argue then the debate resolves", 8),
        ["round", "142:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 142: agents argue then the debate resolves", 12),
        ["round 142:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 142: agents argue then the debate resolves", 16),
        ["round 142:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 142: agents argue then the debate resolves", 24), ["round 142: agents argue", "then the debate resolves"]),
    (("round 142: agents argue then the debate resolves", 32), ["round 142: agents argue then the", "debate resolves"]),
    (
        ("round 142: the filter keeps only strong matches", 4),
        ["round", "142:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 142: the filter keeps only strong matches", 8),
        ["round", "142: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 142: the filter keeps only strong matches", 12),
        ["round 142:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 142: the filter keeps only strong matches", 16),
        ["round 142: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 142: the filter keeps only strong matches", 24),
        ["round 142: the filter", "keeps only strong", "matches"],
    ),
    (("round 142: the filter keeps only strong matches", 32), ["round 142: the filter keeps only", "strong matches"]),
    (
        ("round 142: the model answers with a short reply", 4),
        ["round", "142:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 142: the model answers with a short reply", 8),
        ["round", "142: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 142: the model answers with a short reply", 12),
        ["round 142:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 142: the model answers with a short reply", 16),
        ["round 142: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 142: the model answers with a short reply", 24),
        ["round 142: the model", "answers with a short", "reply"],
    ),
    (("round 142: the model answers with a short reply", 32), ["round 142: the model answers", "with a short reply"]),
    (
        ("round 142: the recorder stores the reasoning trace", 4),
        ["round", "142:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 142: the recorder stores the reasoning trace", 8),
        ["round", "142: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 142: the recorder stores the reasoning trace", 12),
        ["round 142:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 142: the recorder stores the reasoning trace", 16),
        ["round 142: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 142: the recorder stores the reasoning trace", 24),
        ["round 142: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 142: the recorder stores the reasoning trace", 32),
        ["round 142: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 142: the angel watches the processor run", 4),
        ["round", "142:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 142: the angel watches the processor run", 8),
        ["round", "142: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 142: the angel watches the processor run", 12),
        ["round 142:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 142: the angel watches the processor run", 16),
        ["round 142: the", "angel watches", "the processor", "run"],
    ),
    (("round 142: the angel watches the processor run", 24), ["round 142: the angel", "watches the processor", "run"]),
    (("round 142: the angel watches the processor run", 32), ["round 142: the angel watches the", "processor run"]),
    (
        ("round 142: angle of the vector decides the match", 4),
        ["round", "142:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 142: angle of the vector decides the match", 8),
        ["round", "142:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 142: angle of the vector decides the match", 12),
        ["round 142:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 142: angle of the vector decides the match", 16),
        ["round 142: angle", "of the vector", "decides the", "match"],
    ),
    (("round 142: angle of the vector decides the match", 24), ["round 142: angle of the", "vector decides the match"]),
    (("round 142: angle of the vector decides the match", 32), ["round 142: angle of the vector", "decides the match"]),
    (
        ("round 142: the candle burns twice as long at night", 4),
        ["round", "142:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 142: the candle burns twice as long at night", 8),
        ["round", "142: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 142: the candle burns twice as long at night", 12),
        ["round 142:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 142: the candle burns twice as long at night", 16),
        ["round 142: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 142: the candle burns twice as long at night", 24),
        ["round 142: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 142: the candle burns twice as long at night", 32),
        ["round 142: the candle burns", "twice as long at night"],
    ),
    (
        ("round 142: a mirror of the universe in one line", 4),
        ["round", "142:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 142: a mirror of the universe in one line", 8),
        ["round", "142: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 142: a mirror of the universe in one line", 12),
        ["round 142: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 142: a mirror of the universe in one line", 16),
        ["round 142: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 142: a mirror of the universe in one line", 24), ["round 142: a mirror of", "the universe in one line"]),
    (("round 142: a mirror of the universe in one line", 32), ["round 142: a mirror of the", "universe in one line"]),
    (
        ("round 142: the queue drains before the storm", 4),
        ["round", "142:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 142: the queue drains before the storm", 8),
        ["round", "142: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 142: the queue drains before the storm", 12),
        ["round 142:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 142: the queue drains before the storm", 16), ["round 142: the", "queue drains", "before the storm"]),
    (("round 142: the queue drains before the storm", 24), ["round 142: the queue", "drains before the storm"]),
    (("round 142: the queue drains before the storm", 32), ["round 142: the queue drains", "before the storm"]),
    (
        ("kitten142 sitting142 agent142 angle142 universe142 memory142", 6),
        ["kitten142", "sitting142", "agent142", "angle142", "universe142", "memory142"],
    ),
    (
        ("kitten142 sitting142 agent142 angle142 universe142 memory142", 10),
        ["kitten142", "sitting142", "agent142", "angle142", "universe142", "memory142"],
    ),
    (
        ("kitten142 sitting142 agent142 angle142 universe142 memory142", 18),
        ["kitten142", "sitting142", "agent142 angle142", "universe142", "memory142"],
    ),
    (
        ("kitten142 sitting142 agent142 angle142 universe142 memory142", 28),
        ["kitten142 sitting142", "agent142 angle142", "universe142 memory142"],
    ),
    (
        ("sitting142 agent142 angle142 universe142 memory142 stream142", 6),
        ["sitting142", "agent142", "angle142", "universe142", "memory142", "stream142"],
    ),
    (
        ("sitting142 agent142 angle142 universe142 memory142 stream142", 10),
        ["sitting142", "agent142", "angle142", "universe142", "memory142", "stream142"],
    ),
    (
        ("sitting142 agent142 angle142 universe142 memory142 stream142", 18),
        ["sitting142", "agent142 angle142", "universe142", "memory142", "stream142"],
    ),
    (
        ("sitting142 agent142 angle142 universe142 memory142 stream142", 28),
        ["sitting142 agent142 angle142", "universe142 memory142", "stream142"],
    ),
    (
        ("agent142 angle142 universe142 memory142 stream142 context142", 6),
        ["agent142", "angle142", "universe142", "memory142", "stream142", "context142"],
    ),
    (
        ("agent142 angle142 universe142 memory142 stream142 context142", 10),
        ["agent142", "angle142", "universe142", "memory142", "stream142", "context142"],
    ),
    (
        ("agent142 angle142 universe142 memory142 stream142 context142", 18),
        ["agent142 angle142", "universe142", "memory142", "stream142", "context142"],
    ),
    (
        ("agent142 angle142 universe142 memory142 stream142 context142", 28),
        ["agent142 angle142", "universe142 memory142", "stream142 context142"],
    ),
    (
        ("angle142 universe142 memory142 stream142 context142 knowledge142", 6),
        ["angle142", "universe142", "memory142", "stream142", "context142", "knowledge142"],
    ),
    (
        ("angle142 universe142 memory142 stream142 context142 knowledge142", 10),
        ["angle142", "universe142", "memory142", "stream142", "context142", "knowledge142"],
    ),
    (
        ("angle142 universe142 memory142 stream142 context142 knowledge142", 18),
        ["angle142", "universe142", "memory142", "stream142", "context142", "knowledge142"],
    ),
    (
        ("angle142 universe142 memory142 stream142 context142 knowledge142", 28),
        ["angle142 universe142", "memory142 stream142", "context142 knowledge142"],
    ),
    (
        ("universe142 memory142 stream142 context142 knowledge142 vector142", 6),
        ["universe142", "memory142", "stream142", "context142", "knowledge142", "vector142"],
    ),
    (
        ("universe142 memory142 stream142 context142 knowledge142 vector142", 10),
        ["universe142", "memory142", "stream142", "context142", "knowledge142", "vector142"],
    ),
    (
        ("universe142 memory142 stream142 context142 knowledge142 vector142", 18),
        ["universe142", "memory142", "stream142", "context142", "knowledge142", "vector142"],
    ),
    (
        ("universe142 memory142 stream142 context142 knowledge142 vector142", 28),
        ["universe142 memory142", "stream142 context142", "knowledge142 vector142"],
    ),
    (
        ("memory142 stream142 context142 knowledge142 vector142 processor142", 6),
        ["memory142", "stream142", "context142", "knowledge142", "vector142", "processor142"],
    ),
    (
        ("memory142 stream142 context142 knowledge142 vector142 processor142", 10),
        ["memory142", "stream142", "context142", "knowledge142", "vector142", "processor142"],
    ),
    (
        ("memory142 stream142 context142 knowledge142 vector142 processor142", 18),
        ["memory142", "stream142", "context142", "knowledge142", "vector142", "processor142"],
    ),
    (
        ("memory142 stream142 context142 knowledge142 vector142 processor142", 28),
        ["memory142 stream142", "context142 knowledge142", "vector142 processor142"],
    ),
    (
        ("stream142 context142 knowledge142 vector142 processor142 reasoning142", 6),
        ["stream142", "context142", "knowledge142", "vector142", "processor142", "reasoning142"],
    ),
    (
        ("stream142 context142 knowledge142 vector142 processor142 reasoning142", 10),
        ["stream142", "context142", "knowledge142", "vector142", "processor142", "reasoning142"],
    ),
    (
        ("stream142 context142 knowledge142 vector142 processor142 reasoning142", 18),
        ["stream142", "context142", "knowledge142", "vector142", "processor142", "reasoning142"],
    ),
    (
        ("stream142 context142 knowledge142 vector142 processor142 reasoning142", 28),
        ["stream142 context142", "knowledge142 vector142", "processor142 reasoning142"],
    ),
    (
        ("context142 knowledge142 vector142 processor142 reasoning142 machine142", 6),
        ["context142", "knowledge142", "vector142", "processor142", "reasoning142", "machine142"],
    ),
    (
        ("context142 knowledge142 vector142 processor142 reasoning142 machine142", 10),
        ["context142", "knowledge142", "vector142", "processor142", "reasoning142", "machine142"],
    ),
    (
        ("context142 knowledge142 vector142 processor142 reasoning142 machine142", 18),
        ["context142", "knowledge142", "vector142", "processor142", "reasoning142", "machine142"],
    ),
    (
        ("context142 knowledge142 vector142 processor142 reasoning142 machine142", 28),
        ["context142 knowledge142", "vector142 processor142", "reasoning142 machine142"],
    ),
    (
        ("knowledge142 vector142 processor142 reasoning142 machine142 learning142", 6),
        ["knowledge142", "vector142", "processor142", "reasoning142", "machine142", "learning142"],
    ),
    (
        ("knowledge142 vector142 processor142 reasoning142 machine142 learning142", 10),
        ["knowledge142", "vector142", "processor142", "reasoning142", "machine142", "learning142"],
    ),
    (
        ("knowledge142 vector142 processor142 reasoning142 machine142 learning142", 18),
        ["knowledge142", "vector142", "processor142", "reasoning142", "machine142", "learning142"],
    ),
    (
        ("knowledge142 vector142 processor142 reasoning142 machine142 learning142", 28),
        ["knowledge142 vector142", "processor142 reasoning142", "machine142 learning142"],
    ),
    (
        ("vector142 processor142 reasoning142 machine142 learning142 model142", 6),
        ["vector142", "processor142", "reasoning142", "machine142", "learning142", "model142"],
    ),
    (
        ("vector142 processor142 reasoning142 machine142 learning142 model142", 10),
        ["vector142", "processor142", "reasoning142", "machine142", "learning142", "model142"],
    ),
    (
        ("vector142 processor142 reasoning142 machine142 learning142 model142", 18),
        ["vector142", "processor142", "reasoning142", "machine142", "learning142", "model142"],
    ),
    (
        ("vector142 processor142 reasoning142 machine142 learning142 model142", 28),
        ["vector142 processor142", "reasoning142 machine142", "learning142 model142"],
    ),
    (
        ("processor142 reasoning142 machine142 learning142 model142 token142", 6),
        ["processor142", "reasoning142", "machine142", "learning142", "model142", "token142"],
    ),
    (
        ("processor142 reasoning142 machine142 learning142 model142 token142", 10),
        ["processor142", "reasoning142", "machine142", "learning142", "model142", "token142"],
    ),
    (
        ("processor142 reasoning142 machine142 learning142 model142 token142", 18),
        ["processor142", "reasoning142", "machine142", "learning142", "model142 token142"],
    ),
    (
        ("processor142 reasoning142 machine142 learning142 model142 token142", 28),
        ["processor142 reasoning142", "machine142 learning142", "model142 token142"],
    ),
    (
        ("reasoning142 machine142 learning142 model142 token142 prompt142", 6),
        ["reasoning142", "machine142", "learning142", "model142", "token142", "prompt142"],
    ),
    (
        ("reasoning142 machine142 learning142 model142 token142 prompt142", 10),
        ["reasoning142", "machine142", "learning142", "model142", "token142", "prompt142"],
    ),
    (
        ("reasoning142 machine142 learning142 model142 token142 prompt142", 18),
        ["reasoning142", "machine142", "learning142", "model142 token142", "prompt142"],
    ),
    (
        ("reasoning142 machine142 learning142 model142 token142 prompt142", 28),
        ["reasoning142 machine142", "learning142 model142", "token142 prompt142"],
    ),
    (
        ("machine142 learning142 model142 token142 prompt142 session142", 6),
        ["machine142", "learning142", "model142", "token142", "prompt142", "session142"],
    ),
    (
        ("machine142 learning142 model142 token142 prompt142 session142", 10),
        ["machine142", "learning142", "model142", "token142", "prompt142", "session142"],
    ),
    (
        ("machine142 learning142 model142 token142 prompt142 session142", 18),
        ["machine142", "learning142", "model142 token142", "prompt142", "session142"],
    ),
    (
        ("machine142 learning142 model142 token142 prompt142 session142", 28),
        ["machine142 learning142", "model142 token142 prompt142", "session142"],
    ),
    (
        ("learning142 model142 token142 prompt142 session142 library142", 6),
        ["learning142", "model142", "token142", "prompt142", "session142", "library142"],
    ),
    (
        ("learning142 model142 token142 prompt142 session142 library142", 10),
        ["learning142", "model142", "token142", "prompt142", "session142", "library142"],
    ),
    (
        ("learning142 model142 token142 prompt142 session142 library142", 18),
        ["learning142", "model142 token142", "prompt142", "session142", "library142"],
    ),
    (
        ("learning142 model142 token142 prompt142 session142 library142", 28),
        ["learning142 model142", "token142 prompt142", "session142 library142"],
    ),
    (
        ("model142 token142 prompt142 session142 library142 service142", 6),
        ["model142", "token142", "prompt142", "session142", "library142", "service142"],
    ),
    (
        ("model142 token142 prompt142 session142 library142 service142", 10),
        ["model142", "token142", "prompt142", "session142", "library142", "service142"],
    ),
    (
        ("model142 token142 prompt142 session142 library142 service142", 18),
        ["model142 token142", "prompt142", "session142", "library142", "service142"],
    ),
    (
        ("model142 token142 prompt142 session142 library142 service142", 28),
        ["model142 token142 prompt142", "session142 library142", "service142"],
    ),
    (
        ("token142 prompt142 session142 library142 service142 gateway142", 6),
        ["token142", "prompt142", "session142", "library142", "service142", "gateway142"],
    ),
    (
        ("token142 prompt142 session142 library142 service142 gateway142", 10),
        ["token142", "prompt142", "session142", "library142", "service142", "gateway142"],
    ),
    (
        ("token142 prompt142 session142 library142 service142 gateway142", 18),
        ["token142 prompt142", "session142", "library142", "service142", "gateway142"],
    ),
    (
        ("token142 prompt142 session142 library142 service142 gateway142", 28),
        ["token142 prompt142", "session142 library142", "service142 gateway142"],
    ),
    (
        ("prompt142 session142 library142 service142 gateway142 storage142", 6),
        ["prompt142", "session142", "library142", "service142", "gateway142", "storage142"],
    ),
    (
        ("prompt142 session142 library142 service142 gateway142 storage142", 10),
        ["prompt142", "session142", "library142", "service142", "gateway142", "storage142"],
    ),
    (
        ("prompt142 session142 library142 service142 gateway142 storage142", 18),
        ["prompt142", "session142", "library142", "service142", "gateway142", "storage142"],
    ),
    (
        ("prompt142 session142 library142 service142 gateway142 storage142", 28),
        ["prompt142 session142", "library142 service142", "gateway142 storage142"],
    ),
    (
        ("session142 library142 service142 gateway142 storage142 network142", 6),
        ["session142", "library142", "service142", "gateway142", "storage142", "network142"],
    ),
    (
        ("session142 library142 service142 gateway142 storage142 network142", 10),
        ["session142", "library142", "service142", "gateway142", "storage142", "network142"],
    ),
    (
        ("session142 library142 service142 gateway142 storage142 network142", 18),
        ["session142", "library142", "service142", "gateway142", "storage142", "network142"],
    ),
    (
        ("session142 library142 service142 gateway142 storage142 network142", 28),
        ["session142 library142", "service142 gateway142", "storage142 network142"],
    ),
    (
        ("library142 service142 gateway142 storage142 network142 latency142", 6),
        ["library142", "service142", "gateway142", "storage142", "network142", "latency142"],
    ),
    (
        ("library142 service142 gateway142 storage142 network142 latency142", 10),
        ["library142", "service142", "gateway142", "storage142", "network142", "latency142"],
    ),
    (
        ("library142 service142 gateway142 storage142 network142 latency142", 18),
        ["library142", "service142", "gateway142", "storage142", "network142", "latency142"],
    ),
    (
        ("library142 service142 gateway142 storage142 network142 latency142", 28),
        ["library142 service142", "gateway142 storage142", "network142 latency142"],
    ),
    (
        ("service142 gateway142 storage142 network142 latency142 buffer142", 6),
        ["service142", "gateway142", "storage142", "network142", "latency142", "buffer142"],
    ),
    (
        ("service142 gateway142 storage142 network142 latency142 buffer142", 10),
        ["service142", "gateway142", "storage142", "network142", "latency142", "buffer142"],
    ),
    (
        ("service142 gateway142 storage142 network142 latency142 buffer142", 18),
        ["service142", "gateway142", "storage142", "network142", "latency142", "buffer142"],
    ),
    (
        ("service142 gateway142 storage142 network142 latency142 buffer142", 28),
        ["service142 gateway142", "storage142 network142", "latency142 buffer142"],
    ),
    (
        ("gateway142 storage142 network142 latency142 buffer142 queue142", 6),
        ["gateway142", "storage142", "network142", "latency142", "buffer142", "queue142"],
    ),
    (
        ("gateway142 storage142 network142 latency142 buffer142 queue142", 10),
        ["gateway142", "storage142", "network142", "latency142", "buffer142", "queue142"],
    ),
    (
        ("gateway142 storage142 network142 latency142 buffer142 queue142", 18),
        ["gateway142", "storage142", "network142", "latency142", "buffer142 queue142"],
    ),
    (
        ("gateway142 storage142 network142 latency142 buffer142 queue142", 28),
        ["gateway142 storage142", "network142 latency142", "buffer142 queue142"],
    ),
    (
        ("storage142 network142 latency142 buffer142 queue142 worker142", 6),
        ["storage142", "network142", "latency142", "buffer142", "queue142", "worker142"],
    ),
    (
        ("storage142 network142 latency142 buffer142 queue142 worker142", 10),
        ["storage142", "network142", "latency142", "buffer142", "queue142", "worker142"],
    ),
    (
        ("storage142 network142 latency142 buffer142 queue142 worker142", 18),
        ["storage142", "network142", "latency142", "buffer142 queue142", "worker142"],
    ),
    (
        ("storage142 network142 latency142 buffer142 queue142 worker142", 28),
        ["storage142 network142", "latency142 buffer142", "queue142 worker142"],
    ),
    (
        ("network142 latency142 buffer142 queue142 worker142 kernel142", 6),
        ["network142", "latency142", "buffer142", "queue142", "worker142", "kernel142"],
    ),
    (
        ("network142 latency142 buffer142 queue142 worker142 kernel142", 10),
        ["network142", "latency142", "buffer142", "queue142", "worker142", "kernel142"],
    ),
    (
        ("network142 latency142 buffer142 queue142 worker142 kernel142", 18),
        ["network142", "latency142", "buffer142 queue142", "worker142", "kernel142"],
    ),
    (
        ("network142 latency142 buffer142 queue142 worker142 kernel142", 28),
        ["network142 latency142", "buffer142 queue142 worker142", "kernel142"],
    ),
    (
        ("latency142 buffer142 queue142 worker142 kernel142 signal142", 6),
        ["latency142", "buffer142", "queue142", "worker142", "kernel142", "signal142"],
    ),
    (
        ("latency142 buffer142 queue142 worker142 kernel142 signal142", 10),
        ["latency142", "buffer142", "queue142", "worker142", "kernel142", "signal142"],
    ),
    (
        ("latency142 buffer142 queue142 worker142 kernel142 signal142", 18),
        ["latency142", "buffer142 queue142", "worker142", "kernel142", "signal142"],
    ),
    (
        ("latency142 buffer142 queue142 worker142 kernel142 signal142", 28),
        ["latency142 buffer142", "queue142 worker142 kernel142", "signal142"],
    ),
    (
        ("buffer142 queue142 worker142 kernel142 signal142 packet142", 6),
        ["buffer142", "queue142", "worker142", "kernel142", "signal142", "packet142"],
    ),
    (
        ("buffer142 queue142 worker142 kernel142 signal142 packet142", 10),
        ["buffer142", "queue142", "worker142", "kernel142", "signal142", "packet142"],
    ),
    (
        ("buffer142 queue142 worker142 kernel142 signal142 packet142", 18),
        ["buffer142 queue142", "worker142", "kernel142", "signal142", "packet142"],
    ),
    (
        ("buffer142 queue142 worker142 kernel142 signal142 packet142", 28),
        ["buffer142 queue142 worker142", "kernel142 signal142", "packet142"],
    ),
    (
        ("queue142 worker142 kernel142 signal142 packet142 router142", 6),
        ["queue142", "worker142", "kernel142", "signal142", "packet142", "router142"],
    ),
    (
        ("queue142 worker142 kernel142 signal142 packet142 router142", 10),
        ["queue142", "worker142", "kernel142", "signal142", "packet142", "router142"],
    ),
    (
        ("queue142 worker142 kernel142 signal142 packet142 router142", 18),
        ["queue142 worker142", "kernel142", "signal142", "packet142", "router142"],
    ),
    (
        ("queue142 worker142 kernel142 signal142 packet142 router142", 28),
        ["queue142 worker142 kernel142", "signal142 packet142", "router142"],
    ),
    (
        ("worker142 kernel142 signal142 packet142 router142 cluster142", 6),
        ["worker142", "kernel142", "signal142", "packet142", "router142", "cluster142"],
    ),
    (
        ("worker142 kernel142 signal142 packet142 router142 cluster142", 10),
        ["worker142", "kernel142", "signal142", "packet142", "router142", "cluster142"],
    ),
    (
        ("worker142 kernel142 signal142 packet142 router142 cluster142", 18),
        ["worker142", "kernel142", "signal142", "packet142", "router142", "cluster142"],
    ),
    (
        ("worker142 kernel142 signal142 packet142 router142 cluster142", 28),
        ["worker142 kernel142", "signal142 packet142", "router142 cluster142"],
    ),
    (
        ("kernel142 signal142 packet142 router142 cluster142 mirror142", 6),
        ["kernel142", "signal142", "packet142", "router142", "cluster142", "mirror142"],
    ),
    (
        ("kernel142 signal142 packet142 router142 cluster142 mirror142", 10),
        ["kernel142", "signal142", "packet142", "router142", "cluster142", "mirror142"],
    ),
    (
        ("kernel142 signal142 packet142 router142 cluster142 mirror142", 18),
        ["kernel142", "signal142", "packet142", "router142", "cluster142", "mirror142"],
    ),
    (
        ("kernel142 signal142 packet142 router142 cluster142 mirror142", 28),
        ["kernel142 signal142", "packet142 router142", "cluster142 mirror142"],
    ),
    (
        ("signal142 packet142 router142 cluster142 mirror142 filter142", 6),
        ["signal142", "packet142", "router142", "cluster142", "mirror142", "filter142"],
    ),
    (
        ("signal142 packet142 router142 cluster142 mirror142 filter142", 10),
        ["signal142", "packet142", "router142", "cluster142", "mirror142", "filter142"],
    ),
    (
        ("signal142 packet142 router142 cluster142 mirror142 filter142", 18),
        ["signal142", "packet142", "router142", "cluster142", "mirror142", "filter142"],
    ),
    (
        ("signal142 packet142 router142 cluster142 mirror142 filter142", 28),
        ["signal142 packet142", "router142 cluster142", "mirror142 filter142"],
    ),
    (
        ("packet142 router142 cluster142 mirror142 filter142 ranking142", 6),
        ["packet142", "router142", "cluster142", "mirror142", "filter142", "ranking142"],
    ),
    (
        ("packet142 router142 cluster142 mirror142 filter142 ranking142", 10),
        ["packet142", "router142", "cluster142", "mirror142", "filter142", "ranking142"],
    ),
    (
        ("packet142 router142 cluster142 mirror142 filter142 ranking142", 18),
        ["packet142", "router142", "cluster142", "mirror142", "filter142", "ranking142"],
    ),
    (
        ("packet142 router142 cluster142 mirror142 filter142 ranking142", 28),
        ["packet142 router142", "cluster142 mirror142", "filter142 ranking142"],
    ),
    (
        ("router142 cluster142 mirror142 filter142 ranking142 encoding142", 6),
        ["router142", "cluster142", "mirror142", "filter142", "ranking142", "encoding142"],
    ),
    (
        ("router142 cluster142 mirror142 filter142 ranking142 encoding142", 10),
        ["router142", "cluster142", "mirror142", "filter142", "ranking142", "encoding142"],
    ),
    (
        ("router142 cluster142 mirror142 filter142 ranking142 encoding142", 18),
        ["router142", "cluster142", "mirror142", "filter142", "ranking142", "encoding142"],
    ),
    (
        ("router142 cluster142 mirror142 filter142 ranking142 encoding142", 28),
        ["router142 cluster142", "mirror142 filter142", "ranking142 encoding142"],
    ),
    (
        ("cluster142 mirror142 filter142 ranking142 encoding142 mapping142", 6),
        ["cluster142", "mirror142", "filter142", "ranking142", "encoding142", "mapping142"],
    ),
    (
        ("cluster142 mirror142 filter142 ranking142 encoding142 mapping142", 10),
        ["cluster142", "mirror142", "filter142", "ranking142", "encoding142", "mapping142"],
    ),
    (
        ("cluster142 mirror142 filter142 ranking142 encoding142 mapping142", 18),
        ["cluster142", "mirror142", "filter142", "ranking142", "encoding142", "mapping142"],
    ),
    (
        ("cluster142 mirror142 filter142 ranking142 encoding142 mapping142", 28),
        ["cluster142 mirror142", "filter142 ranking142", "encoding142 mapping142"],
    ),
    (
        ("mirror142 filter142 ranking142 encoding142 mapping142 record142", 6),
        ["mirror142", "filter142", "ranking142", "encoding142", "mapping142", "record142"],
    ),
    (
        ("mirror142 filter142 ranking142 encoding142 mapping142 record142", 10),
        ["mirror142", "filter142", "ranking142", "encoding142", "mapping142", "record142"],
    ),
    (
        ("mirror142 filter142 ranking142 encoding142 mapping142 record142", 18),
        ["mirror142", "filter142", "ranking142", "encoding142", "mapping142", "record142"],
    ),
    (
        ("mirror142 filter142 ranking142 encoding142 mapping142 record142", 28),
        ["mirror142 filter142", "ranking142 encoding142", "mapping142 record142"],
    ),
    (
        ("filter142 ranking142 encoding142 mapping142 record142 candle142", 6),
        ["filter142", "ranking142", "encoding142", "mapping142", "record142", "candle142"],
    ),
    (
        ("filter142 ranking142 encoding142 mapping142 record142 candle142", 10),
        ["filter142", "ranking142", "encoding142", "mapping142", "record142", "candle142"],
    ),
    (
        ("filter142 ranking142 encoding142 mapping142 record142 candle142", 18),
        ["filter142", "ranking142", "encoding142", "mapping142", "record142", "candle142"],
    ),
    (
        ("filter142 ranking142 encoding142 mapping142 record142 candle142", 28),
        ["filter142 ranking142", "encoding142 mapping142", "record142 candle142"],
    ),
    (
        ("ranking142 encoding142 mapping142 record142 candle142 thread142", 6),
        ["ranking142", "encoding142", "mapping142", "record142", "candle142", "thread142"],
    ),
    (
        ("ranking142 encoding142 mapping142 record142 candle142 thread142", 10),
        ["ranking142", "encoding142", "mapping142", "record142", "candle142", "thread142"],
    ),
    (
        ("ranking142 encoding142 mapping142 record142 candle142 thread142", 18),
        ["ranking142", "encoding142", "mapping142", "record142", "candle142", "thread142"],
    ),
    (
        ("ranking142 encoding142 mapping142 record142 candle142 thread142", 28),
        ["ranking142 encoding142", "mapping142 record142", "candle142 thread142"],
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
