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
        ("round 32: the quick brown fox jumps over the lazy dog", 4),
        ["round", "32:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 32: the quick brown fox jumps over the lazy dog", 8),
        ["round", "32: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 32: the quick brown fox jumps over the lazy dog", 12),
        ["round 32:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 32: the quick brown fox jumps over the lazy dog", 16),
        ["round 32: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 32: the quick brown fox jumps over the lazy dog", 24),
        ["round 32: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 32: the quick brown fox jumps over the lazy dog", 32),
        ["round 32: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 32: agentuniverse is a framework for multi agents", 4),
        ["round", "32:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 32: agentuniverse is a framework for multi agents", 8),
        ["round", "32:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 32: agentuniverse is a framework for multi agents", 12),
        ["round 32:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 32: agentuniverse is a framework for multi agents", 16),
        ["round 32:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 32: agentuniverse is a framework for multi agents", 24),
        ["round 32: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 32: agentuniverse is a framework for multi agents", 32),
        ["round 32: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 32: knowledge stored as vectors enables retrieval", 4),
        ["round", "32:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 32: knowledge stored as vectors enables retrieval", 8),
        ["round", "32:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 32: knowledge stored as vectors enables retrieval", 12),
        ["round 32:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 32: knowledge stored as vectors enables retrieval", 16),
        ["round 32:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 32: knowledge stored as vectors enables retrieval", 24),
        ["round 32: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 32: knowledge stored as vectors enables retrieval", 32),
        ["round 32: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 32: the processor reads the record then stops", 4),
        ["round", "32:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 32: the processor reads the record then stops", 8),
        ["round", "32: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 32: the processor reads the record then stops", 12),
        ["round 32:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 32: the processor reads the record then stops", 16),
        ["round 32: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 32: the processor reads the record then stops", 24),
        ["round 32: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 32: the processor reads the record then stops", 32),
        ["round 32: the processor reads", "the record then stops"],
    ),
    (
        ("round 32: a worker pulls the next task from the queue", 4),
        ["round", "32:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 32: a worker pulls the next task from the queue", 8),
        ["round", "32: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 32: a worker pulls the next task from the queue", 12),
        ["round 32: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 32: a worker pulls the next task from the queue", 16),
        ["round 32: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 32: a worker pulls the next task from the queue", 24),
        ["round 32: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 32: a worker pulls the next task from the queue", 32),
        ["round 32: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 32: signals travel through the network layer", 4),
        ["round", "32:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 32: signals travel through the network layer", 8),
        ["round", "32:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 32: signals travel through the network layer", 12),
        ["round 32:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 32: signals travel through the network layer", 16),
        ["round 32:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 32: signals travel through the network layer", 24),
        ["round 32: signals travel", "through the network", "layer"],
    ),
    (
        ("round 32: signals travel through the network layer", 32),
        ["round 32: signals travel through", "the network layer"],
    ),
    (
        ("round 32: the gateway routes each request by policy", 4),
        ["round", "32:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 32: the gateway routes each request by policy", 8),
        ["round", "32: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 32: the gateway routes each request by policy", 12),
        ["round 32:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 32: the gateway routes each request by policy", 16),
        ["round 32: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 32: the gateway routes each request by policy", 24),
        ["round 32: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 32: the gateway routes each request by policy", 32),
        ["round 32: the gateway routes", "each request by policy"],
    ),
    (
        ("round 32: memory grows until the buffer is full", 4),
        ["round", "32:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 32: memory grows until the buffer is full", 8),
        ["round", "32:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 32: memory grows until the buffer is full", 12),
        ["round 32:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 32: memory grows until the buffer is full", 16),
        ["round 32: memory", "grows until the", "buffer is full"],
    ),
    (("round 32: memory grows until the buffer is full", 24), ["round 32: memory grows", "until the buffer is full"]),
    (("round 32: memory grows until the buffer is full", 32), ["round 32: memory grows until the", "buffer is full"]),
    (
        ("round 32: the cluster mirrors every packet twice", 4),
        ["round", "32:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 32: the cluster mirrors every packet twice", 8),
        ["round", "32: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 32: the cluster mirrors every packet twice", 12),
        ["round 32:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 32: the cluster mirrors every packet twice", 16),
        ["round 32: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 32: the cluster mirrors every packet twice", 24),
        ["round 32: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 32: the cluster mirrors every packet twice", 32), ["round 32: the cluster mirrors", "every packet twice"]),
    (
        ("round 32: ranking uses tokens learned from the corpus", 4),
        ["round", "32:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 32: ranking uses tokens learned from the corpus", 8),
        ["round", "32:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 32: ranking uses tokens learned from the corpus", 12),
        ["round 32:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 32: ranking uses tokens learned from the corpus", 16),
        ["round 32:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 32: ranking uses tokens learned from the corpus", 24),
        ["round 32: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 32: ranking uses tokens learned from the corpus", 32),
        ["round 32: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 32: a long session ends when the candle dies", 4),
        ["round", "32:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 32: a long session ends when the candle dies", 8),
        ["round", "32: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 32: a long session ends when the candle dies", 12),
        ["round 32: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 32: a long session ends when the candle dies", 16),
        ["round 32: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 32: a long session ends when the candle dies", 24),
        ["round 32: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 32: a long session ends when the candle dies", 32),
        ["round 32: a long session ends", "when the candle dies"],
    ),
    (
        ("round 32: encode the prompt then map the result", 4),
        ["round", "32:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 32: encode the prompt then map the result", 8),
        ["round", "32:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 32: encode the prompt then map the result", 12),
        ["round 32:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 32: encode the prompt then map the result", 16),
        ["round 32: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 32: encode the prompt then map the result", 24),
        ["round 32: encode the", "prompt then map the", "result"],
    ),
    (("round 32: encode the prompt then map the result", 32), ["round 32: encode the prompt then", "map the result"]),
    (
        ("round 32: the kernel wakes the worker at dawn", 4),
        ["round", "32:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 32: the kernel wakes the worker at dawn", 8),
        ["round", "32: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 32: the kernel wakes the worker at dawn", 12),
        ["round 32:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 32: the kernel wakes the worker at dawn", 16), ["round 32: the", "kernel wakes the", "worker at dawn"]),
    (("round 32: the kernel wakes the worker at dawn", 24), ["round 32: the kernel", "wakes the worker at dawn"]),
    (("round 32: the kernel wakes the worker at dawn", 32), ["round 32: the kernel wakes the", "worker at dawn"]),
    (
        ("round 32: service latency drops after the patch", 4),
        ["round", "32:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 32: service latency drops after the patch", 8),
        ["round", "32:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 32: service latency drops after the patch", 12),
        ["round 32:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 32: service latency drops after the patch", 16),
        ["round 32:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 32: service latency drops after the patch", 24),
        ["round 32: service", "latency drops after the", "patch"],
    ),
    (("round 32: service latency drops after the patch", 32), ["round 32: service latency drops", "after the patch"]),
    (
        ("round 32: the library caches every vector it sees", 4),
        ["round", "32:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 32: the library caches every vector it sees", 8),
        ["round", "32: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 32: the library caches every vector it sees", 12),
        ["round 32:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 32: the library caches every vector it sees", 16),
        ["round 32: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 32: the library caches every vector it sees", 24),
        ["round 32: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 32: the library caches every vector it sees", 32),
        ["round 32: the library caches", "every vector it sees"],
    ),
    (
        ("round 32: agents argue then the debate resolves", 4),
        ["round", "32:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 32: agents argue then the debate resolves", 8),
        ["round", "32:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 32: agents argue then the debate resolves", 12),
        ["round 32:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 32: agents argue then the debate resolves", 16),
        ["round 32: agents", "argue then the", "debate resolves"],
    ),
    (("round 32: agents argue then the debate resolves", 24), ["round 32: agents argue", "then the debate resolves"]),
    (("round 32: agents argue then the debate resolves", 32), ["round 32: agents argue then the", "debate resolves"]),
    (
        ("round 32: the filter keeps only strong matches", 4),
        ["round", "32:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 32: the filter keeps only strong matches", 8),
        ["round", "32: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 32: the filter keeps only strong matches", 12),
        ["round 32:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 32: the filter keeps only strong matches", 16),
        ["round 32: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 32: the filter keeps only strong matches", 24), ["round 32: the filter", "keeps only strong", "matches"]),
    (("round 32: the filter keeps only strong matches", 32), ["round 32: the filter keeps only", "strong matches"]),
    (
        ("round 32: the model answers with a short reply", 4),
        ["round", "32:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 32: the model answers with a short reply", 8),
        ["round", "32: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 32: the model answers with a short reply", 12),
        ["round 32:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 32: the model answers with a short reply", 16),
        ["round 32: the", "model answers", "with a short", "reply"],
    ),
    (("round 32: the model answers with a short reply", 24), ["round 32: the model", "answers with a short", "reply"]),
    (("round 32: the model answers with a short reply", 32), ["round 32: the model answers with", "a short reply"]),
    (
        ("round 32: the recorder stores the reasoning trace", 4),
        ["round", "32:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 32: the recorder stores the reasoning trace", 8),
        ["round", "32: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 32: the recorder stores the reasoning trace", 12),
        ["round 32:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 32: the recorder stores the reasoning trace", 16),
        ["round 32: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 32: the recorder stores the reasoning trace", 24),
        ["round 32: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 32: the recorder stores the reasoning trace", 32),
        ["round 32: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 32: the angel watches the processor run", 4),
        ["round", "32:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 32: the angel watches the processor run", 8),
        ["round", "32: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 32: the angel watches the processor run", 12),
        ["round 32:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 32: the angel watches the processor run", 16), ["round 32: the", "angel watches", "the processor", "run"]),
    (("round 32: the angel watches the processor run", 24), ["round 32: the angel", "watches the processor", "run"]),
    (("round 32: the angel watches the processor run", 32), ["round 32: the angel watches the", "processor run"]),
    (
        ("round 32: angle of the vector decides the match", 4),
        ["round", "32:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 32: angle of the vector decides the match", 8),
        ["round", "32:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 32: angle of the vector decides the match", 12),
        ["round 32:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 32: angle of the vector decides the match", 16),
        ["round 32: angle", "of the vector", "decides the", "match"],
    ),
    (("round 32: angle of the vector decides the match", 24), ["round 32: angle of the", "vector decides the match"]),
    (("round 32: angle of the vector decides the match", 32), ["round 32: angle of the vector", "decides the match"]),
    (
        ("round 32: the candle burns twice as long at night", 4),
        ["round", "32:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 32: the candle burns twice as long at night", 8),
        ["round", "32: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 32: the candle burns twice as long at night", 12),
        ["round 32:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 32: the candle burns twice as long at night", 16),
        ["round 32: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 32: the candle burns twice as long at night", 24),
        ["round 32: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 32: the candle burns twice as long at night", 32),
        ["round 32: the candle burns twice", "as long at night"],
    ),
    (
        ("round 32: a mirror of the universe in one line", 4),
        ["round", "32:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 32: a mirror of the universe in one line", 8),
        ["round", "32: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 32: a mirror of the universe in one line", 12),
        ["round 32: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 32: a mirror of the universe in one line", 16),
        ["round 32: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 32: a mirror of the universe in one line", 24), ["round 32: a mirror of", "the universe in one line"]),
    (("round 32: a mirror of the universe in one line", 32), ["round 32: a mirror of the", "universe in one line"]),
    (
        ("round 32: the queue drains before the storm", 4),
        ["round", "32:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 32: the queue drains before the storm", 8),
        ["round", "32: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 32: the queue drains before the storm", 12), ["round 32:", "the queue", "drains", "before the", "storm"]),
    (("round 32: the queue drains before the storm", 16), ["round 32: the", "queue drains", "before the storm"]),
    (("round 32: the queue drains before the storm", 24), ["round 32: the queue", "drains before the storm"]),
    (("round 32: the queue drains before the storm", 32), ["round 32: the queue drains", "before the storm"]),
    (
        ("kitten32 sitting32 agent32 angle32 universe32 memory32", 6),
        ["kitten32", "sitting32", "agent32", "angle32", "universe32", "memory32"],
    ),
    (
        ("kitten32 sitting32 agent32 angle32 universe32 memory32", 10),
        ["kitten32", "sitting32", "agent32", "angle32", "universe32", "memory32"],
    ),
    (
        ("kitten32 sitting32 agent32 angle32 universe32 memory32", 18),
        ["kitten32 sitting32", "agent32 angle32", "universe32", "memory32"],
    ),
    (
        ("kitten32 sitting32 agent32 angle32 universe32 memory32", 28),
        ["kitten32 sitting32 agent32", "angle32 universe32 memory32"],
    ),
    (
        ("sitting32 agent32 angle32 universe32 memory32 stream32", 6),
        ["sitting32", "agent32", "angle32", "universe32", "memory32", "stream32"],
    ),
    (
        ("sitting32 agent32 angle32 universe32 memory32 stream32", 10),
        ["sitting32", "agent32", "angle32", "universe32", "memory32", "stream32"],
    ),
    (
        ("sitting32 agent32 angle32 universe32 memory32 stream32", 18),
        ["sitting32 agent32", "angle32 universe32", "memory32 stream32"],
    ),
    (
        ("sitting32 agent32 angle32 universe32 memory32 stream32", 28),
        ["sitting32 agent32 angle32", "universe32 memory32 stream32"],
    ),
    (
        ("agent32 angle32 universe32 memory32 stream32 context32", 6),
        ["agent32", "angle32", "universe32", "memory32", "stream32", "context32"],
    ),
    (
        ("agent32 angle32 universe32 memory32 stream32 context32", 10),
        ["agent32", "angle32", "universe32", "memory32", "stream32", "context32"],
    ),
    (
        ("agent32 angle32 universe32 memory32 stream32 context32", 18),
        ["agent32 angle32", "universe32", "memory32 stream32", "context32"],
    ),
    (
        ("agent32 angle32 universe32 memory32 stream32 context32", 28),
        ["agent32 angle32 universe32", "memory32 stream32 context32"],
    ),
    (
        ("angle32 universe32 memory32 stream32 context32 knowledge32", 6),
        ["angle32", "universe32", "memory32", "stream32", "context32", "knowledge32"],
    ),
    (
        ("angle32 universe32 memory32 stream32 context32 knowledge32", 10),
        ["angle32", "universe32", "memory32", "stream32", "context32", "knowledge32"],
    ),
    (
        ("angle32 universe32 memory32 stream32 context32 knowledge32", 18),
        ["angle32 universe32", "memory32 stream32", "context32", "knowledge32"],
    ),
    (
        ("angle32 universe32 memory32 stream32 context32 knowledge32", 28),
        ["angle32 universe32 memory32", "stream32 context32", "knowledge32"],
    ),
    (
        ("universe32 memory32 stream32 context32 knowledge32 vector32", 6),
        ["universe32", "memory32", "stream32", "context32", "knowledge32", "vector32"],
    ),
    (
        ("universe32 memory32 stream32 context32 knowledge32 vector32", 10),
        ["universe32", "memory32", "stream32", "context32", "knowledge32", "vector32"],
    ),
    (
        ("universe32 memory32 stream32 context32 knowledge32 vector32", 18),
        ["universe32", "memory32 stream32", "context32", "knowledge32", "vector32"],
    ),
    (
        ("universe32 memory32 stream32 context32 knowledge32 vector32", 28),
        ["universe32 memory32 stream32", "context32 knowledge32", "vector32"],
    ),
    (
        ("memory32 stream32 context32 knowledge32 vector32 processor32", 6),
        ["memory32", "stream32", "context32", "knowledge32", "vector32", "processor32"],
    ),
    (
        ("memory32 stream32 context32 knowledge32 vector32 processor32", 10),
        ["memory32", "stream32", "context32", "knowledge32", "vector32", "processor32"],
    ),
    (
        ("memory32 stream32 context32 knowledge32 vector32 processor32", 18),
        ["memory32 stream32", "context32", "knowledge32", "vector32", "processor32"],
    ),
    (
        ("memory32 stream32 context32 knowledge32 vector32 processor32", 28),
        ["memory32 stream32 context32", "knowledge32 vector32", "processor32"],
    ),
    (
        ("stream32 context32 knowledge32 vector32 processor32 reasoning32", 6),
        ["stream32", "context32", "knowledge32", "vector32", "processor32", "reasoning32"],
    ),
    (
        ("stream32 context32 knowledge32 vector32 processor32 reasoning32", 10),
        ["stream32", "context32", "knowledge32", "vector32", "processor32", "reasoning32"],
    ),
    (
        ("stream32 context32 knowledge32 vector32 processor32 reasoning32", 18),
        ["stream32 context32", "knowledge32", "vector32", "processor32", "reasoning32"],
    ),
    (
        ("stream32 context32 knowledge32 vector32 processor32 reasoning32", 28),
        ["stream32 context32", "knowledge32 vector32", "processor32 reasoning32"],
    ),
    (
        ("context32 knowledge32 vector32 processor32 reasoning32 machine32", 6),
        ["context32", "knowledge32", "vector32", "processor32", "reasoning32", "machine32"],
    ),
    (
        ("context32 knowledge32 vector32 processor32 reasoning32 machine32", 10),
        ["context32", "knowledge32", "vector32", "processor32", "reasoning32", "machine32"],
    ),
    (
        ("context32 knowledge32 vector32 processor32 reasoning32 machine32", 18),
        ["context32", "knowledge32", "vector32", "processor32", "reasoning32", "machine32"],
    ),
    (
        ("context32 knowledge32 vector32 processor32 reasoning32 machine32", 28),
        ["context32 knowledge32", "vector32 processor32", "reasoning32 machine32"],
    ),
    (
        ("knowledge32 vector32 processor32 reasoning32 machine32 learning32", 6),
        ["knowledge32", "vector32", "processor32", "reasoning32", "machine32", "learning32"],
    ),
    (
        ("knowledge32 vector32 processor32 reasoning32 machine32 learning32", 10),
        ["knowledge32", "vector32", "processor32", "reasoning32", "machine32", "learning32"],
    ),
    (
        ("knowledge32 vector32 processor32 reasoning32 machine32 learning32", 18),
        ["knowledge32", "vector32", "processor32", "reasoning32", "machine32", "learning32"],
    ),
    (
        ("knowledge32 vector32 processor32 reasoning32 machine32 learning32", 28),
        ["knowledge32 vector32", "processor32 reasoning32", "machine32 learning32"],
    ),
    (
        ("vector32 processor32 reasoning32 machine32 learning32 model32", 6),
        ["vector32", "processor32", "reasoning32", "machine32", "learning32", "model32"],
    ),
    (
        ("vector32 processor32 reasoning32 machine32 learning32 model32", 10),
        ["vector32", "processor32", "reasoning32", "machine32", "learning32", "model32"],
    ),
    (
        ("vector32 processor32 reasoning32 machine32 learning32 model32", 18),
        ["vector32", "processor32", "reasoning32", "machine32", "learning32 model32"],
    ),
    (
        ("vector32 processor32 reasoning32 machine32 learning32 model32", 28),
        ["vector32 processor32", "reasoning32 machine32", "learning32 model32"],
    ),
    (
        ("processor32 reasoning32 machine32 learning32 model32 token32", 6),
        ["processor32", "reasoning32", "machine32", "learning32", "model32", "token32"],
    ),
    (
        ("processor32 reasoning32 machine32 learning32 model32 token32", 10),
        ["processor32", "reasoning32", "machine32", "learning32", "model32", "token32"],
    ),
    (
        ("processor32 reasoning32 machine32 learning32 model32 token32", 18),
        ["processor32", "reasoning32", "machine32", "learning32 model32", "token32"],
    ),
    (
        ("processor32 reasoning32 machine32 learning32 model32 token32", 28),
        ["processor32 reasoning32", "machine32 learning32 model32", "token32"],
    ),
    (
        ("reasoning32 machine32 learning32 model32 token32 prompt32", 6),
        ["reasoning32", "machine32", "learning32", "model32", "token32", "prompt32"],
    ),
    (
        ("reasoning32 machine32 learning32 model32 token32 prompt32", 10),
        ["reasoning32", "machine32", "learning32", "model32", "token32", "prompt32"],
    ),
    (
        ("reasoning32 machine32 learning32 model32 token32 prompt32", 18),
        ["reasoning32", "machine32", "learning32 model32", "token32 prompt32"],
    ),
    (
        ("reasoning32 machine32 learning32 model32 token32 prompt32", 28),
        ["reasoning32 machine32", "learning32 model32 token32", "prompt32"],
    ),
    (
        ("machine32 learning32 model32 token32 prompt32 session32", 6),
        ["machine32", "learning32", "model32", "token32", "prompt32", "session32"],
    ),
    (
        ("machine32 learning32 model32 token32 prompt32 session32", 10),
        ["machine32", "learning32", "model32", "token32", "prompt32", "session32"],
    ),
    (
        ("machine32 learning32 model32 token32 prompt32 session32", 18),
        ["machine32", "learning32 model32", "token32 prompt32", "session32"],
    ),
    (
        ("machine32 learning32 model32 token32 prompt32 session32", 28),
        ["machine32 learning32 model32", "token32 prompt32 session32"],
    ),
    (
        ("learning32 model32 token32 prompt32 session32 library32", 6),
        ["learning32", "model32", "token32", "prompt32", "session32", "library32"],
    ),
    (
        ("learning32 model32 token32 prompt32 session32 library32", 10),
        ["learning32", "model32", "token32", "prompt32", "session32", "library32"],
    ),
    (
        ("learning32 model32 token32 prompt32 session32 library32", 18),
        ["learning32 model32", "token32 prompt32", "session32", "library32"],
    ),
    (
        ("learning32 model32 token32 prompt32 session32 library32", 28),
        ["learning32 model32 token32", "prompt32 session32 library32"],
    ),
    (
        ("model32 token32 prompt32 session32 library32 service32", 6),
        ["model32", "token32", "prompt32", "session32", "library32", "service32"],
    ),
    (
        ("model32 token32 prompt32 session32 library32 service32", 10),
        ["model32", "token32", "prompt32", "session32", "library32", "service32"],
    ),
    (
        ("model32 token32 prompt32 session32 library32 service32", 18),
        ["model32 token32", "prompt32 session32", "library32", "service32"],
    ),
    (
        ("model32 token32 prompt32 session32 library32 service32", 28),
        ["model32 token32 prompt32", "session32 library32", "service32"],
    ),
    (
        ("token32 prompt32 session32 library32 service32 gateway32", 6),
        ["token32", "prompt32", "session32", "library32", "service32", "gateway32"],
    ),
    (
        ("token32 prompt32 session32 library32 service32 gateway32", 10),
        ["token32", "prompt32", "session32", "library32", "service32", "gateway32"],
    ),
    (
        ("token32 prompt32 session32 library32 service32 gateway32", 18),
        ["token32 prompt32", "session32", "library32", "service32", "gateway32"],
    ),
    (
        ("token32 prompt32 session32 library32 service32 gateway32", 28),
        ["token32 prompt32 session32", "library32 service32", "gateway32"],
    ),
    (
        ("prompt32 session32 library32 service32 gateway32 storage32", 6),
        ["prompt32", "session32", "library32", "service32", "gateway32", "storage32"],
    ),
    (
        ("prompt32 session32 library32 service32 gateway32 storage32", 10),
        ["prompt32", "session32", "library32", "service32", "gateway32", "storage32"],
    ),
    (
        ("prompt32 session32 library32 service32 gateway32 storage32", 18),
        ["prompt32 session32", "library32", "service32", "gateway32", "storage32"],
    ),
    (
        ("prompt32 session32 library32 service32 gateway32 storage32", 28),
        ["prompt32 session32 library32", "service32 gateway32", "storage32"],
    ),
    (
        ("session32 library32 service32 gateway32 storage32 network32", 6),
        ["session32", "library32", "service32", "gateway32", "storage32", "network32"],
    ),
    (
        ("session32 library32 service32 gateway32 storage32 network32", 10),
        ["session32", "library32", "service32", "gateway32", "storage32", "network32"],
    ),
    (
        ("session32 library32 service32 gateway32 storage32 network32", 18),
        ["session32", "library32", "service32", "gateway32", "storage32", "network32"],
    ),
    (
        ("session32 library32 service32 gateway32 storage32 network32", 28),
        ["session32 library32", "service32 gateway32", "storage32 network32"],
    ),
    (
        ("library32 service32 gateway32 storage32 network32 latency32", 6),
        ["library32", "service32", "gateway32", "storage32", "network32", "latency32"],
    ),
    (
        ("library32 service32 gateway32 storage32 network32 latency32", 10),
        ["library32", "service32", "gateway32", "storage32", "network32", "latency32"],
    ),
    (
        ("library32 service32 gateway32 storage32 network32 latency32", 18),
        ["library32", "service32", "gateway32", "storage32", "network32", "latency32"],
    ),
    (
        ("library32 service32 gateway32 storage32 network32 latency32", 28),
        ["library32 service32", "gateway32 storage32", "network32 latency32"],
    ),
    (
        ("service32 gateway32 storage32 network32 latency32 buffer32", 6),
        ["service32", "gateway32", "storage32", "network32", "latency32", "buffer32"],
    ),
    (
        ("service32 gateway32 storage32 network32 latency32 buffer32", 10),
        ["service32", "gateway32", "storage32", "network32", "latency32", "buffer32"],
    ),
    (
        ("service32 gateway32 storage32 network32 latency32 buffer32", 18),
        ["service32", "gateway32", "storage32", "network32", "latency32 buffer32"],
    ),
    (
        ("service32 gateway32 storage32 network32 latency32 buffer32", 28),
        ["service32 gateway32", "storage32 network32", "latency32 buffer32"],
    ),
    (
        ("gateway32 storage32 network32 latency32 buffer32 queue32", 6),
        ["gateway32", "storage32", "network32", "latency32", "buffer32", "queue32"],
    ),
    (
        ("gateway32 storage32 network32 latency32 buffer32 queue32", 10),
        ["gateway32", "storage32", "network32", "latency32", "buffer32", "queue32"],
    ),
    (
        ("gateway32 storage32 network32 latency32 buffer32 queue32", 18),
        ["gateway32", "storage32", "network32", "latency32 buffer32", "queue32"],
    ),
    (
        ("gateway32 storage32 network32 latency32 buffer32 queue32", 28),
        ["gateway32 storage32", "network32 latency32 buffer32", "queue32"],
    ),
    (
        ("storage32 network32 latency32 buffer32 queue32 worker32", 6),
        ["storage32", "network32", "latency32", "buffer32", "queue32", "worker32"],
    ),
    (
        ("storage32 network32 latency32 buffer32 queue32 worker32", 10),
        ["storage32", "network32", "latency32", "buffer32", "queue32", "worker32"],
    ),
    (
        ("storage32 network32 latency32 buffer32 queue32 worker32", 18),
        ["storage32", "network32", "latency32 buffer32", "queue32 worker32"],
    ),
    (
        ("storage32 network32 latency32 buffer32 queue32 worker32", 28),
        ["storage32 network32", "latency32 buffer32 queue32", "worker32"],
    ),
    (
        ("network32 latency32 buffer32 queue32 worker32 kernel32", 6),
        ["network32", "latency32", "buffer32", "queue32", "worker32", "kernel32"],
    ),
    (
        ("network32 latency32 buffer32 queue32 worker32 kernel32", 10),
        ["network32", "latency32", "buffer32", "queue32", "worker32", "kernel32"],
    ),
    (
        ("network32 latency32 buffer32 queue32 worker32 kernel32", 18),
        ["network32", "latency32 buffer32", "queue32 worker32", "kernel32"],
    ),
    (
        ("network32 latency32 buffer32 queue32 worker32 kernel32", 28),
        ["network32 latency32 buffer32", "queue32 worker32 kernel32"],
    ),
    (
        ("latency32 buffer32 queue32 worker32 kernel32 signal32", 6),
        ["latency32", "buffer32", "queue32", "worker32", "kernel32", "signal32"],
    ),
    (
        ("latency32 buffer32 queue32 worker32 kernel32 signal32", 10),
        ["latency32", "buffer32", "queue32", "worker32", "kernel32", "signal32"],
    ),
    (
        ("latency32 buffer32 queue32 worker32 kernel32 signal32", 18),
        ["latency32 buffer32", "queue32 worker32", "kernel32 signal32"],
    ),
    (
        ("latency32 buffer32 queue32 worker32 kernel32 signal32", 28),
        ["latency32 buffer32 queue32", "worker32 kernel32 signal32"],
    ),
    (
        ("buffer32 queue32 worker32 kernel32 signal32 packet32", 6),
        ["buffer32", "queue32", "worker32", "kernel32", "signal32", "packet32"],
    ),
    (
        ("buffer32 queue32 worker32 kernel32 signal32 packet32", 10),
        ["buffer32", "queue32", "worker32", "kernel32", "signal32", "packet32"],
    ),
    (
        ("buffer32 queue32 worker32 kernel32 signal32 packet32", 18),
        ["buffer32 queue32", "worker32 kernel32", "signal32 packet32"],
    ),
    (
        ("buffer32 queue32 worker32 kernel32 signal32 packet32", 28),
        ["buffer32 queue32 worker32", "kernel32 signal32 packet32"],
    ),
    (
        ("queue32 worker32 kernel32 signal32 packet32 router32", 6),
        ["queue32", "worker32", "kernel32", "signal32", "packet32", "router32"],
    ),
    (
        ("queue32 worker32 kernel32 signal32 packet32 router32", 10),
        ["queue32", "worker32", "kernel32", "signal32", "packet32", "router32"],
    ),
    (
        ("queue32 worker32 kernel32 signal32 packet32 router32", 18),
        ["queue32 worker32", "kernel32 signal32", "packet32 router32"],
    ),
    (
        ("queue32 worker32 kernel32 signal32 packet32 router32", 28),
        ["queue32 worker32 kernel32", "signal32 packet32 router32"],
    ),
    (
        ("worker32 kernel32 signal32 packet32 router32 cluster32", 6),
        ["worker32", "kernel32", "signal32", "packet32", "router32", "cluster32"],
    ),
    (
        ("worker32 kernel32 signal32 packet32 router32 cluster32", 10),
        ["worker32", "kernel32", "signal32", "packet32", "router32", "cluster32"],
    ),
    (
        ("worker32 kernel32 signal32 packet32 router32 cluster32", 18),
        ["worker32 kernel32", "signal32 packet32", "router32 cluster32"],
    ),
    (
        ("worker32 kernel32 signal32 packet32 router32 cluster32", 28),
        ["worker32 kernel32 signal32", "packet32 router32 cluster32"],
    ),
    (
        ("kernel32 signal32 packet32 router32 cluster32 mirror32", 6),
        ["kernel32", "signal32", "packet32", "router32", "cluster32", "mirror32"],
    ),
    (
        ("kernel32 signal32 packet32 router32 cluster32 mirror32", 10),
        ["kernel32", "signal32", "packet32", "router32", "cluster32", "mirror32"],
    ),
    (
        ("kernel32 signal32 packet32 router32 cluster32 mirror32", 18),
        ["kernel32 signal32", "packet32 router32", "cluster32 mirror32"],
    ),
    (
        ("kernel32 signal32 packet32 router32 cluster32 mirror32", 28),
        ["kernel32 signal32 packet32", "router32 cluster32 mirror32"],
    ),
    (
        ("signal32 packet32 router32 cluster32 mirror32 filter32", 6),
        ["signal32", "packet32", "router32", "cluster32", "mirror32", "filter32"],
    ),
    (
        ("signal32 packet32 router32 cluster32 mirror32 filter32", 10),
        ["signal32", "packet32", "router32", "cluster32", "mirror32", "filter32"],
    ),
    (
        ("signal32 packet32 router32 cluster32 mirror32 filter32", 18),
        ["signal32 packet32", "router32 cluster32", "mirror32 filter32"],
    ),
    (
        ("signal32 packet32 router32 cluster32 mirror32 filter32", 28),
        ["signal32 packet32 router32", "cluster32 mirror32 filter32"],
    ),
    (
        ("packet32 router32 cluster32 mirror32 filter32 ranking32", 6),
        ["packet32", "router32", "cluster32", "mirror32", "filter32", "ranking32"],
    ),
    (
        ("packet32 router32 cluster32 mirror32 filter32 ranking32", 10),
        ["packet32", "router32", "cluster32", "mirror32", "filter32", "ranking32"],
    ),
    (
        ("packet32 router32 cluster32 mirror32 filter32 ranking32", 18),
        ["packet32 router32", "cluster32 mirror32", "filter32 ranking32"],
    ),
    (
        ("packet32 router32 cluster32 mirror32 filter32 ranking32", 28),
        ["packet32 router32 cluster32", "mirror32 filter32 ranking32"],
    ),
    (
        ("router32 cluster32 mirror32 filter32 ranking32 encoding32", 6),
        ["router32", "cluster32", "mirror32", "filter32", "ranking32", "encoding32"],
    ),
    (
        ("router32 cluster32 mirror32 filter32 ranking32 encoding32", 10),
        ["router32", "cluster32", "mirror32", "filter32", "ranking32", "encoding32"],
    ),
    (
        ("router32 cluster32 mirror32 filter32 ranking32 encoding32", 18),
        ["router32 cluster32", "mirror32 filter32", "ranking32", "encoding32"],
    ),
    (
        ("router32 cluster32 mirror32 filter32 ranking32 encoding32", 28),
        ["router32 cluster32 mirror32", "filter32 ranking32", "encoding32"],
    ),
    (
        ("cluster32 mirror32 filter32 ranking32 encoding32 mapping32", 6),
        ["cluster32", "mirror32", "filter32", "ranking32", "encoding32", "mapping32"],
    ),
    (
        ("cluster32 mirror32 filter32 ranking32 encoding32 mapping32", 10),
        ["cluster32", "mirror32", "filter32", "ranking32", "encoding32", "mapping32"],
    ),
    (
        ("cluster32 mirror32 filter32 ranking32 encoding32 mapping32", 18),
        ["cluster32 mirror32", "filter32 ranking32", "encoding32", "mapping32"],
    ),
    (
        ("cluster32 mirror32 filter32 ranking32 encoding32 mapping32", 28),
        ["cluster32 mirror32 filter32", "ranking32 encoding32", "mapping32"],
    ),
    (
        ("mirror32 filter32 ranking32 encoding32 mapping32 record32", 6),
        ["mirror32", "filter32", "ranking32", "encoding32", "mapping32", "record32"],
    ),
    (
        ("mirror32 filter32 ranking32 encoding32 mapping32 record32", 10),
        ["mirror32", "filter32", "ranking32", "encoding32", "mapping32", "record32"],
    ),
    (
        ("mirror32 filter32 ranking32 encoding32 mapping32 record32", 18),
        ["mirror32 filter32", "ranking32", "encoding32", "mapping32 record32"],
    ),
    (
        ("mirror32 filter32 ranking32 encoding32 mapping32 record32", 28),
        ["mirror32 filter32 ranking32", "encoding32 mapping32", "record32"],
    ),
    (
        ("filter32 ranking32 encoding32 mapping32 record32 candle32", 6),
        ["filter32", "ranking32", "encoding32", "mapping32", "record32", "candle32"],
    ),
    (
        ("filter32 ranking32 encoding32 mapping32 record32 candle32", 10),
        ["filter32", "ranking32", "encoding32", "mapping32", "record32", "candle32"],
    ),
    (
        ("filter32 ranking32 encoding32 mapping32 record32 candle32", 18),
        ["filter32 ranking32", "encoding32", "mapping32 record32", "candle32"],
    ),
    (
        ("filter32 ranking32 encoding32 mapping32 record32 candle32", 28),
        ["filter32 ranking32", "encoding32 mapping32", "record32 candle32"],
    ),
    (
        ("ranking32 encoding32 mapping32 record32 candle32 thread32", 6),
        ["ranking32", "encoding32", "mapping32", "record32", "candle32", "thread32"],
    ),
    (
        ("ranking32 encoding32 mapping32 record32 candle32 thread32", 10),
        ["ranking32", "encoding32", "mapping32", "record32", "candle32", "thread32"],
    ),
    (
        ("ranking32 encoding32 mapping32 record32 candle32 thread32", 18),
        ["ranking32", "encoding32", "mapping32 record32", "candle32 thread32"],
    ),
    (
        ("ranking32 encoding32 mapping32 record32 candle32 thread32", 28),
        ["ranking32 encoding32", "mapping32 record32 candle32", "thread32"],
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
