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
        ("round 31: the quick brown fox jumps over the lazy dog", 4),
        ["round", "31:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 31: the quick brown fox jumps over the lazy dog", 8),
        ["round", "31: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 31: the quick brown fox jumps over the lazy dog", 12),
        ["round 31:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 31: the quick brown fox jumps over the lazy dog", 16),
        ["round 31: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 31: the quick brown fox jumps over the lazy dog", 24),
        ["round 31: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 31: the quick brown fox jumps over the lazy dog", 32),
        ["round 31: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 31: agentuniverse is a framework for multi agents", 4),
        ["round", "31:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 31: agentuniverse is a framework for multi agents", 8),
        ["round", "31:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 31: agentuniverse is a framework for multi agents", 12),
        ["round 31:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 31: agentuniverse is a framework for multi agents", 16),
        ["round 31:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 31: agentuniverse is a framework for multi agents", 24),
        ["round 31: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 31: agentuniverse is a framework for multi agents", 32),
        ["round 31: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 31: knowledge stored as vectors enables retrieval", 4),
        ["round", "31:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 31: knowledge stored as vectors enables retrieval", 8),
        ["round", "31:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 31: knowledge stored as vectors enables retrieval", 12),
        ["round 31:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 31: knowledge stored as vectors enables retrieval", 16),
        ["round 31:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 31: knowledge stored as vectors enables retrieval", 24),
        ["round 31: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 31: knowledge stored as vectors enables retrieval", 32),
        ["round 31: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 31: the processor reads the record then stops", 4),
        ["round", "31:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 31: the processor reads the record then stops", 8),
        ["round", "31: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 31: the processor reads the record then stops", 12),
        ["round 31:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 31: the processor reads the record then stops", 16),
        ["round 31: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 31: the processor reads the record then stops", 24),
        ["round 31: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 31: the processor reads the record then stops", 32),
        ["round 31: the processor reads", "the record then stops"],
    ),
    (
        ("round 31: a worker pulls the next task from the queue", 4),
        ["round", "31:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 31: a worker pulls the next task from the queue", 8),
        ["round", "31: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 31: a worker pulls the next task from the queue", 12),
        ["round 31: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 31: a worker pulls the next task from the queue", 16),
        ["round 31: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 31: a worker pulls the next task from the queue", 24),
        ["round 31: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 31: a worker pulls the next task from the queue", 32),
        ["round 31: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 31: signals travel through the network layer", 4),
        ["round", "31:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 31: signals travel through the network layer", 8),
        ["round", "31:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 31: signals travel through the network layer", 12),
        ["round 31:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 31: signals travel through the network layer", 16),
        ["round 31:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 31: signals travel through the network layer", 24),
        ["round 31: signals travel", "through the network", "layer"],
    ),
    (
        ("round 31: signals travel through the network layer", 32),
        ["round 31: signals travel through", "the network layer"],
    ),
    (
        ("round 31: the gateway routes each request by policy", 4),
        ["round", "31:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 31: the gateway routes each request by policy", 8),
        ["round", "31: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 31: the gateway routes each request by policy", 12),
        ["round 31:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 31: the gateway routes each request by policy", 16),
        ["round 31: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 31: the gateway routes each request by policy", 24),
        ["round 31: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 31: the gateway routes each request by policy", 32),
        ["round 31: the gateway routes", "each request by policy"],
    ),
    (
        ("round 31: memory grows until the buffer is full", 4),
        ["round", "31:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 31: memory grows until the buffer is full", 8),
        ["round", "31:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 31: memory grows until the buffer is full", 12),
        ["round 31:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 31: memory grows until the buffer is full", 16),
        ["round 31: memory", "grows until the", "buffer is full"],
    ),
    (("round 31: memory grows until the buffer is full", 24), ["round 31: memory grows", "until the buffer is full"]),
    (("round 31: memory grows until the buffer is full", 32), ["round 31: memory grows until the", "buffer is full"]),
    (
        ("round 31: the cluster mirrors every packet twice", 4),
        ["round", "31:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 31: the cluster mirrors every packet twice", 8),
        ["round", "31: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 31: the cluster mirrors every packet twice", 12),
        ["round 31:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 31: the cluster mirrors every packet twice", 16),
        ["round 31: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 31: the cluster mirrors every packet twice", 24),
        ["round 31: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 31: the cluster mirrors every packet twice", 32), ["round 31: the cluster mirrors", "every packet twice"]),
    (
        ("round 31: ranking uses tokens learned from the corpus", 4),
        ["round", "31:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 31: ranking uses tokens learned from the corpus", 8),
        ["round", "31:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 31: ranking uses tokens learned from the corpus", 12),
        ["round 31:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 31: ranking uses tokens learned from the corpus", 16),
        ["round 31:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 31: ranking uses tokens learned from the corpus", 24),
        ["round 31: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 31: ranking uses tokens learned from the corpus", 32),
        ["round 31: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 31: a long session ends when the candle dies", 4),
        ["round", "31:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 31: a long session ends when the candle dies", 8),
        ["round", "31: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 31: a long session ends when the candle dies", 12),
        ["round 31: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 31: a long session ends when the candle dies", 16),
        ["round 31: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 31: a long session ends when the candle dies", 24),
        ["round 31: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 31: a long session ends when the candle dies", 32),
        ["round 31: a long session ends", "when the candle dies"],
    ),
    (
        ("round 31: encode the prompt then map the result", 4),
        ["round", "31:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 31: encode the prompt then map the result", 8),
        ["round", "31:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 31: encode the prompt then map the result", 12),
        ["round 31:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 31: encode the prompt then map the result", 16),
        ["round 31: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 31: encode the prompt then map the result", 24),
        ["round 31: encode the", "prompt then map the", "result"],
    ),
    (("round 31: encode the prompt then map the result", 32), ["round 31: encode the prompt then", "map the result"]),
    (
        ("round 31: the kernel wakes the worker at dawn", 4),
        ["round", "31:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 31: the kernel wakes the worker at dawn", 8),
        ["round", "31: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 31: the kernel wakes the worker at dawn", 12),
        ["round 31:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 31: the kernel wakes the worker at dawn", 16), ["round 31: the", "kernel wakes the", "worker at dawn"]),
    (("round 31: the kernel wakes the worker at dawn", 24), ["round 31: the kernel", "wakes the worker at dawn"]),
    (("round 31: the kernel wakes the worker at dawn", 32), ["round 31: the kernel wakes the", "worker at dawn"]),
    (
        ("round 31: service latency drops after the patch", 4),
        ["round", "31:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 31: service latency drops after the patch", 8),
        ["round", "31:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 31: service latency drops after the patch", 12),
        ["round 31:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 31: service latency drops after the patch", 16),
        ["round 31:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 31: service latency drops after the patch", 24),
        ["round 31: service", "latency drops after the", "patch"],
    ),
    (("round 31: service latency drops after the patch", 32), ["round 31: service latency drops", "after the patch"]),
    (
        ("round 31: the library caches every vector it sees", 4),
        ["round", "31:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 31: the library caches every vector it sees", 8),
        ["round", "31: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 31: the library caches every vector it sees", 12),
        ["round 31:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 31: the library caches every vector it sees", 16),
        ["round 31: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 31: the library caches every vector it sees", 24),
        ["round 31: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 31: the library caches every vector it sees", 32),
        ["round 31: the library caches", "every vector it sees"],
    ),
    (
        ("round 31: agents argue then the debate resolves", 4),
        ["round", "31:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 31: agents argue then the debate resolves", 8),
        ["round", "31:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 31: agents argue then the debate resolves", 12),
        ["round 31:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 31: agents argue then the debate resolves", 16),
        ["round 31: agents", "argue then the", "debate resolves"],
    ),
    (("round 31: agents argue then the debate resolves", 24), ["round 31: agents argue", "then the debate resolves"]),
    (("round 31: agents argue then the debate resolves", 32), ["round 31: agents argue then the", "debate resolves"]),
    (
        ("round 31: the filter keeps only strong matches", 4),
        ["round", "31:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 31: the filter keeps only strong matches", 8),
        ["round", "31: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 31: the filter keeps only strong matches", 12),
        ["round 31:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 31: the filter keeps only strong matches", 16),
        ["round 31: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 31: the filter keeps only strong matches", 24), ["round 31: the filter", "keeps only strong", "matches"]),
    (("round 31: the filter keeps only strong matches", 32), ["round 31: the filter keeps only", "strong matches"]),
    (
        ("round 31: the model answers with a short reply", 4),
        ["round", "31:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 31: the model answers with a short reply", 8),
        ["round", "31: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 31: the model answers with a short reply", 12),
        ["round 31:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 31: the model answers with a short reply", 16),
        ["round 31: the", "model answers", "with a short", "reply"],
    ),
    (("round 31: the model answers with a short reply", 24), ["round 31: the model", "answers with a short", "reply"]),
    (("round 31: the model answers with a short reply", 32), ["round 31: the model answers with", "a short reply"]),
    (
        ("round 31: the recorder stores the reasoning trace", 4),
        ["round", "31:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 31: the recorder stores the reasoning trace", 8),
        ["round", "31: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 31: the recorder stores the reasoning trace", 12),
        ["round 31:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 31: the recorder stores the reasoning trace", 16),
        ["round 31: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 31: the recorder stores the reasoning trace", 24),
        ["round 31: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 31: the recorder stores the reasoning trace", 32),
        ["round 31: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 31: the angel watches the processor run", 4),
        ["round", "31:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 31: the angel watches the processor run", 8),
        ["round", "31: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 31: the angel watches the processor run", 12),
        ["round 31:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 31: the angel watches the processor run", 16), ["round 31: the", "angel watches", "the processor", "run"]),
    (("round 31: the angel watches the processor run", 24), ["round 31: the angel", "watches the processor", "run"]),
    (("round 31: the angel watches the processor run", 32), ["round 31: the angel watches the", "processor run"]),
    (
        ("round 31: angle of the vector decides the match", 4),
        ["round", "31:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 31: angle of the vector decides the match", 8),
        ["round", "31:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 31: angle of the vector decides the match", 12),
        ["round 31:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 31: angle of the vector decides the match", 16),
        ["round 31: angle", "of the vector", "decides the", "match"],
    ),
    (("round 31: angle of the vector decides the match", 24), ["round 31: angle of the", "vector decides the match"]),
    (("round 31: angle of the vector decides the match", 32), ["round 31: angle of the vector", "decides the match"]),
    (
        ("round 31: the candle burns twice as long at night", 4),
        ["round", "31:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 31: the candle burns twice as long at night", 8),
        ["round", "31: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 31: the candle burns twice as long at night", 12),
        ["round 31:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 31: the candle burns twice as long at night", 16),
        ["round 31: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 31: the candle burns twice as long at night", 24),
        ["round 31: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 31: the candle burns twice as long at night", 32),
        ["round 31: the candle burns twice", "as long at night"],
    ),
    (
        ("round 31: a mirror of the universe in one line", 4),
        ["round", "31:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 31: a mirror of the universe in one line", 8),
        ["round", "31: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 31: a mirror of the universe in one line", 12),
        ["round 31: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 31: a mirror of the universe in one line", 16),
        ["round 31: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 31: a mirror of the universe in one line", 24), ["round 31: a mirror of", "the universe in one line"]),
    (("round 31: a mirror of the universe in one line", 32), ["round 31: a mirror of the", "universe in one line"]),
    (
        ("round 31: the queue drains before the storm", 4),
        ["round", "31:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 31: the queue drains before the storm", 8),
        ["round", "31: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 31: the queue drains before the storm", 12), ["round 31:", "the queue", "drains", "before the", "storm"]),
    (("round 31: the queue drains before the storm", 16), ["round 31: the", "queue drains", "before the storm"]),
    (("round 31: the queue drains before the storm", 24), ["round 31: the queue", "drains before the storm"]),
    (("round 31: the queue drains before the storm", 32), ["round 31: the queue drains", "before the storm"]),
    (
        ("kitten31 sitting31 agent31 angle31 universe31 memory31", 6),
        ["kitten31", "sitting31", "agent31", "angle31", "universe31", "memory31"],
    ),
    (
        ("kitten31 sitting31 agent31 angle31 universe31 memory31", 10),
        ["kitten31", "sitting31", "agent31", "angle31", "universe31", "memory31"],
    ),
    (
        ("kitten31 sitting31 agent31 angle31 universe31 memory31", 18),
        ["kitten31 sitting31", "agent31 angle31", "universe31", "memory31"],
    ),
    (
        ("kitten31 sitting31 agent31 angle31 universe31 memory31", 28),
        ["kitten31 sitting31 agent31", "angle31 universe31 memory31"],
    ),
    (
        ("sitting31 agent31 angle31 universe31 memory31 stream31", 6),
        ["sitting31", "agent31", "angle31", "universe31", "memory31", "stream31"],
    ),
    (
        ("sitting31 agent31 angle31 universe31 memory31 stream31", 10),
        ["sitting31", "agent31", "angle31", "universe31", "memory31", "stream31"],
    ),
    (
        ("sitting31 agent31 angle31 universe31 memory31 stream31", 18),
        ["sitting31 agent31", "angle31 universe31", "memory31 stream31"],
    ),
    (
        ("sitting31 agent31 angle31 universe31 memory31 stream31", 28),
        ["sitting31 agent31 angle31", "universe31 memory31 stream31"],
    ),
    (
        ("agent31 angle31 universe31 memory31 stream31 context31", 6),
        ["agent31", "angle31", "universe31", "memory31", "stream31", "context31"],
    ),
    (
        ("agent31 angle31 universe31 memory31 stream31 context31", 10),
        ["agent31", "angle31", "universe31", "memory31", "stream31", "context31"],
    ),
    (
        ("agent31 angle31 universe31 memory31 stream31 context31", 18),
        ["agent31 angle31", "universe31", "memory31 stream31", "context31"],
    ),
    (
        ("agent31 angle31 universe31 memory31 stream31 context31", 28),
        ["agent31 angle31 universe31", "memory31 stream31 context31"],
    ),
    (
        ("angle31 universe31 memory31 stream31 context31 knowledge31", 6),
        ["angle31", "universe31", "memory31", "stream31", "context31", "knowledge31"],
    ),
    (
        ("angle31 universe31 memory31 stream31 context31 knowledge31", 10),
        ["angle31", "universe31", "memory31", "stream31", "context31", "knowledge31"],
    ),
    (
        ("angle31 universe31 memory31 stream31 context31 knowledge31", 18),
        ["angle31 universe31", "memory31 stream31", "context31", "knowledge31"],
    ),
    (
        ("angle31 universe31 memory31 stream31 context31 knowledge31", 28),
        ["angle31 universe31 memory31", "stream31 context31", "knowledge31"],
    ),
    (
        ("universe31 memory31 stream31 context31 knowledge31 vector31", 6),
        ["universe31", "memory31", "stream31", "context31", "knowledge31", "vector31"],
    ),
    (
        ("universe31 memory31 stream31 context31 knowledge31 vector31", 10),
        ["universe31", "memory31", "stream31", "context31", "knowledge31", "vector31"],
    ),
    (
        ("universe31 memory31 stream31 context31 knowledge31 vector31", 18),
        ["universe31", "memory31 stream31", "context31", "knowledge31", "vector31"],
    ),
    (
        ("universe31 memory31 stream31 context31 knowledge31 vector31", 28),
        ["universe31 memory31 stream31", "context31 knowledge31", "vector31"],
    ),
    (
        ("memory31 stream31 context31 knowledge31 vector31 processor31", 6),
        ["memory31", "stream31", "context31", "knowledge31", "vector31", "processor31"],
    ),
    (
        ("memory31 stream31 context31 knowledge31 vector31 processor31", 10),
        ["memory31", "stream31", "context31", "knowledge31", "vector31", "processor31"],
    ),
    (
        ("memory31 stream31 context31 knowledge31 vector31 processor31", 18),
        ["memory31 stream31", "context31", "knowledge31", "vector31", "processor31"],
    ),
    (
        ("memory31 stream31 context31 knowledge31 vector31 processor31", 28),
        ["memory31 stream31 context31", "knowledge31 vector31", "processor31"],
    ),
    (
        ("stream31 context31 knowledge31 vector31 processor31 reasoning31", 6),
        ["stream31", "context31", "knowledge31", "vector31", "processor31", "reasoning31"],
    ),
    (
        ("stream31 context31 knowledge31 vector31 processor31 reasoning31", 10),
        ["stream31", "context31", "knowledge31", "vector31", "processor31", "reasoning31"],
    ),
    (
        ("stream31 context31 knowledge31 vector31 processor31 reasoning31", 18),
        ["stream31 context31", "knowledge31", "vector31", "processor31", "reasoning31"],
    ),
    (
        ("stream31 context31 knowledge31 vector31 processor31 reasoning31", 28),
        ["stream31 context31", "knowledge31 vector31", "processor31 reasoning31"],
    ),
    (
        ("context31 knowledge31 vector31 processor31 reasoning31 machine31", 6),
        ["context31", "knowledge31", "vector31", "processor31", "reasoning31", "machine31"],
    ),
    (
        ("context31 knowledge31 vector31 processor31 reasoning31 machine31", 10),
        ["context31", "knowledge31", "vector31", "processor31", "reasoning31", "machine31"],
    ),
    (
        ("context31 knowledge31 vector31 processor31 reasoning31 machine31", 18),
        ["context31", "knowledge31", "vector31", "processor31", "reasoning31", "machine31"],
    ),
    (
        ("context31 knowledge31 vector31 processor31 reasoning31 machine31", 28),
        ["context31 knowledge31", "vector31 processor31", "reasoning31 machine31"],
    ),
    (
        ("knowledge31 vector31 processor31 reasoning31 machine31 learning31", 6),
        ["knowledge31", "vector31", "processor31", "reasoning31", "machine31", "learning31"],
    ),
    (
        ("knowledge31 vector31 processor31 reasoning31 machine31 learning31", 10),
        ["knowledge31", "vector31", "processor31", "reasoning31", "machine31", "learning31"],
    ),
    (
        ("knowledge31 vector31 processor31 reasoning31 machine31 learning31", 18),
        ["knowledge31", "vector31", "processor31", "reasoning31", "machine31", "learning31"],
    ),
    (
        ("knowledge31 vector31 processor31 reasoning31 machine31 learning31", 28),
        ["knowledge31 vector31", "processor31 reasoning31", "machine31 learning31"],
    ),
    (
        ("vector31 processor31 reasoning31 machine31 learning31 model31", 6),
        ["vector31", "processor31", "reasoning31", "machine31", "learning31", "model31"],
    ),
    (
        ("vector31 processor31 reasoning31 machine31 learning31 model31", 10),
        ["vector31", "processor31", "reasoning31", "machine31", "learning31", "model31"],
    ),
    (
        ("vector31 processor31 reasoning31 machine31 learning31 model31", 18),
        ["vector31", "processor31", "reasoning31", "machine31", "learning31 model31"],
    ),
    (
        ("vector31 processor31 reasoning31 machine31 learning31 model31", 28),
        ["vector31 processor31", "reasoning31 machine31", "learning31 model31"],
    ),
    (
        ("processor31 reasoning31 machine31 learning31 model31 token31", 6),
        ["processor31", "reasoning31", "machine31", "learning31", "model31", "token31"],
    ),
    (
        ("processor31 reasoning31 machine31 learning31 model31 token31", 10),
        ["processor31", "reasoning31", "machine31", "learning31", "model31", "token31"],
    ),
    (
        ("processor31 reasoning31 machine31 learning31 model31 token31", 18),
        ["processor31", "reasoning31", "machine31", "learning31 model31", "token31"],
    ),
    (
        ("processor31 reasoning31 machine31 learning31 model31 token31", 28),
        ["processor31 reasoning31", "machine31 learning31 model31", "token31"],
    ),
    (
        ("reasoning31 machine31 learning31 model31 token31 prompt31", 6),
        ["reasoning31", "machine31", "learning31", "model31", "token31", "prompt31"],
    ),
    (
        ("reasoning31 machine31 learning31 model31 token31 prompt31", 10),
        ["reasoning31", "machine31", "learning31", "model31", "token31", "prompt31"],
    ),
    (
        ("reasoning31 machine31 learning31 model31 token31 prompt31", 18),
        ["reasoning31", "machine31", "learning31 model31", "token31 prompt31"],
    ),
    (
        ("reasoning31 machine31 learning31 model31 token31 prompt31", 28),
        ["reasoning31 machine31", "learning31 model31 token31", "prompt31"],
    ),
    (
        ("machine31 learning31 model31 token31 prompt31 session31", 6),
        ["machine31", "learning31", "model31", "token31", "prompt31", "session31"],
    ),
    (
        ("machine31 learning31 model31 token31 prompt31 session31", 10),
        ["machine31", "learning31", "model31", "token31", "prompt31", "session31"],
    ),
    (
        ("machine31 learning31 model31 token31 prompt31 session31", 18),
        ["machine31", "learning31 model31", "token31 prompt31", "session31"],
    ),
    (
        ("machine31 learning31 model31 token31 prompt31 session31", 28),
        ["machine31 learning31 model31", "token31 prompt31 session31"],
    ),
    (
        ("learning31 model31 token31 prompt31 session31 library31", 6),
        ["learning31", "model31", "token31", "prompt31", "session31", "library31"],
    ),
    (
        ("learning31 model31 token31 prompt31 session31 library31", 10),
        ["learning31", "model31", "token31", "prompt31", "session31", "library31"],
    ),
    (
        ("learning31 model31 token31 prompt31 session31 library31", 18),
        ["learning31 model31", "token31 prompt31", "session31", "library31"],
    ),
    (
        ("learning31 model31 token31 prompt31 session31 library31", 28),
        ["learning31 model31 token31", "prompt31 session31 library31"],
    ),
    (
        ("model31 token31 prompt31 session31 library31 service31", 6),
        ["model31", "token31", "prompt31", "session31", "library31", "service31"],
    ),
    (
        ("model31 token31 prompt31 session31 library31 service31", 10),
        ["model31", "token31", "prompt31", "session31", "library31", "service31"],
    ),
    (
        ("model31 token31 prompt31 session31 library31 service31", 18),
        ["model31 token31", "prompt31 session31", "library31", "service31"],
    ),
    (
        ("model31 token31 prompt31 session31 library31 service31", 28),
        ["model31 token31 prompt31", "session31 library31", "service31"],
    ),
    (
        ("token31 prompt31 session31 library31 service31 gateway31", 6),
        ["token31", "prompt31", "session31", "library31", "service31", "gateway31"],
    ),
    (
        ("token31 prompt31 session31 library31 service31 gateway31", 10),
        ["token31", "prompt31", "session31", "library31", "service31", "gateway31"],
    ),
    (
        ("token31 prompt31 session31 library31 service31 gateway31", 18),
        ["token31 prompt31", "session31", "library31", "service31", "gateway31"],
    ),
    (
        ("token31 prompt31 session31 library31 service31 gateway31", 28),
        ["token31 prompt31 session31", "library31 service31", "gateway31"],
    ),
    (
        ("prompt31 session31 library31 service31 gateway31 storage31", 6),
        ["prompt31", "session31", "library31", "service31", "gateway31", "storage31"],
    ),
    (
        ("prompt31 session31 library31 service31 gateway31 storage31", 10),
        ["prompt31", "session31", "library31", "service31", "gateway31", "storage31"],
    ),
    (
        ("prompt31 session31 library31 service31 gateway31 storage31", 18),
        ["prompt31 session31", "library31", "service31", "gateway31", "storage31"],
    ),
    (
        ("prompt31 session31 library31 service31 gateway31 storage31", 28),
        ["prompt31 session31 library31", "service31 gateway31", "storage31"],
    ),
    (
        ("session31 library31 service31 gateway31 storage31 network31", 6),
        ["session31", "library31", "service31", "gateway31", "storage31", "network31"],
    ),
    (
        ("session31 library31 service31 gateway31 storage31 network31", 10),
        ["session31", "library31", "service31", "gateway31", "storage31", "network31"],
    ),
    (
        ("session31 library31 service31 gateway31 storage31 network31", 18),
        ["session31", "library31", "service31", "gateway31", "storage31", "network31"],
    ),
    (
        ("session31 library31 service31 gateway31 storage31 network31", 28),
        ["session31 library31", "service31 gateway31", "storage31 network31"],
    ),
    (
        ("library31 service31 gateway31 storage31 network31 latency31", 6),
        ["library31", "service31", "gateway31", "storage31", "network31", "latency31"],
    ),
    (
        ("library31 service31 gateway31 storage31 network31 latency31", 10),
        ["library31", "service31", "gateway31", "storage31", "network31", "latency31"],
    ),
    (
        ("library31 service31 gateway31 storage31 network31 latency31", 18),
        ["library31", "service31", "gateway31", "storage31", "network31", "latency31"],
    ),
    (
        ("library31 service31 gateway31 storage31 network31 latency31", 28),
        ["library31 service31", "gateway31 storage31", "network31 latency31"],
    ),
    (
        ("service31 gateway31 storage31 network31 latency31 buffer31", 6),
        ["service31", "gateway31", "storage31", "network31", "latency31", "buffer31"],
    ),
    (
        ("service31 gateway31 storage31 network31 latency31 buffer31", 10),
        ["service31", "gateway31", "storage31", "network31", "latency31", "buffer31"],
    ),
    (
        ("service31 gateway31 storage31 network31 latency31 buffer31", 18),
        ["service31", "gateway31", "storage31", "network31", "latency31 buffer31"],
    ),
    (
        ("service31 gateway31 storage31 network31 latency31 buffer31", 28),
        ["service31 gateway31", "storage31 network31", "latency31 buffer31"],
    ),
    (
        ("gateway31 storage31 network31 latency31 buffer31 queue31", 6),
        ["gateway31", "storage31", "network31", "latency31", "buffer31", "queue31"],
    ),
    (
        ("gateway31 storage31 network31 latency31 buffer31 queue31", 10),
        ["gateway31", "storage31", "network31", "latency31", "buffer31", "queue31"],
    ),
    (
        ("gateway31 storage31 network31 latency31 buffer31 queue31", 18),
        ["gateway31", "storage31", "network31", "latency31 buffer31", "queue31"],
    ),
    (
        ("gateway31 storage31 network31 latency31 buffer31 queue31", 28),
        ["gateway31 storage31", "network31 latency31 buffer31", "queue31"],
    ),
    (
        ("storage31 network31 latency31 buffer31 queue31 worker31", 6),
        ["storage31", "network31", "latency31", "buffer31", "queue31", "worker31"],
    ),
    (
        ("storage31 network31 latency31 buffer31 queue31 worker31", 10),
        ["storage31", "network31", "latency31", "buffer31", "queue31", "worker31"],
    ),
    (
        ("storage31 network31 latency31 buffer31 queue31 worker31", 18),
        ["storage31", "network31", "latency31 buffer31", "queue31 worker31"],
    ),
    (
        ("storage31 network31 latency31 buffer31 queue31 worker31", 28),
        ["storage31 network31", "latency31 buffer31 queue31", "worker31"],
    ),
    (
        ("network31 latency31 buffer31 queue31 worker31 kernel31", 6),
        ["network31", "latency31", "buffer31", "queue31", "worker31", "kernel31"],
    ),
    (
        ("network31 latency31 buffer31 queue31 worker31 kernel31", 10),
        ["network31", "latency31", "buffer31", "queue31", "worker31", "kernel31"],
    ),
    (
        ("network31 latency31 buffer31 queue31 worker31 kernel31", 18),
        ["network31", "latency31 buffer31", "queue31 worker31", "kernel31"],
    ),
    (
        ("network31 latency31 buffer31 queue31 worker31 kernel31", 28),
        ["network31 latency31 buffer31", "queue31 worker31 kernel31"],
    ),
    (
        ("latency31 buffer31 queue31 worker31 kernel31 signal31", 6),
        ["latency31", "buffer31", "queue31", "worker31", "kernel31", "signal31"],
    ),
    (
        ("latency31 buffer31 queue31 worker31 kernel31 signal31", 10),
        ["latency31", "buffer31", "queue31", "worker31", "kernel31", "signal31"],
    ),
    (
        ("latency31 buffer31 queue31 worker31 kernel31 signal31", 18),
        ["latency31 buffer31", "queue31 worker31", "kernel31 signal31"],
    ),
    (
        ("latency31 buffer31 queue31 worker31 kernel31 signal31", 28),
        ["latency31 buffer31 queue31", "worker31 kernel31 signal31"],
    ),
    (
        ("buffer31 queue31 worker31 kernel31 signal31 packet31", 6),
        ["buffer31", "queue31", "worker31", "kernel31", "signal31", "packet31"],
    ),
    (
        ("buffer31 queue31 worker31 kernel31 signal31 packet31", 10),
        ["buffer31", "queue31", "worker31", "kernel31", "signal31", "packet31"],
    ),
    (
        ("buffer31 queue31 worker31 kernel31 signal31 packet31", 18),
        ["buffer31 queue31", "worker31 kernel31", "signal31 packet31"],
    ),
    (
        ("buffer31 queue31 worker31 kernel31 signal31 packet31", 28),
        ["buffer31 queue31 worker31", "kernel31 signal31 packet31"],
    ),
    (
        ("queue31 worker31 kernel31 signal31 packet31 router31", 6),
        ["queue31", "worker31", "kernel31", "signal31", "packet31", "router31"],
    ),
    (
        ("queue31 worker31 kernel31 signal31 packet31 router31", 10),
        ["queue31", "worker31", "kernel31", "signal31", "packet31", "router31"],
    ),
    (
        ("queue31 worker31 kernel31 signal31 packet31 router31", 18),
        ["queue31 worker31", "kernel31 signal31", "packet31 router31"],
    ),
    (
        ("queue31 worker31 kernel31 signal31 packet31 router31", 28),
        ["queue31 worker31 kernel31", "signal31 packet31 router31"],
    ),
    (
        ("worker31 kernel31 signal31 packet31 router31 cluster31", 6),
        ["worker31", "kernel31", "signal31", "packet31", "router31", "cluster31"],
    ),
    (
        ("worker31 kernel31 signal31 packet31 router31 cluster31", 10),
        ["worker31", "kernel31", "signal31", "packet31", "router31", "cluster31"],
    ),
    (
        ("worker31 kernel31 signal31 packet31 router31 cluster31", 18),
        ["worker31 kernel31", "signal31 packet31", "router31 cluster31"],
    ),
    (
        ("worker31 kernel31 signal31 packet31 router31 cluster31", 28),
        ["worker31 kernel31 signal31", "packet31 router31 cluster31"],
    ),
    (
        ("kernel31 signal31 packet31 router31 cluster31 mirror31", 6),
        ["kernel31", "signal31", "packet31", "router31", "cluster31", "mirror31"],
    ),
    (
        ("kernel31 signal31 packet31 router31 cluster31 mirror31", 10),
        ["kernel31", "signal31", "packet31", "router31", "cluster31", "mirror31"],
    ),
    (
        ("kernel31 signal31 packet31 router31 cluster31 mirror31", 18),
        ["kernel31 signal31", "packet31 router31", "cluster31 mirror31"],
    ),
    (
        ("kernel31 signal31 packet31 router31 cluster31 mirror31", 28),
        ["kernel31 signal31 packet31", "router31 cluster31 mirror31"],
    ),
    (
        ("signal31 packet31 router31 cluster31 mirror31 filter31", 6),
        ["signal31", "packet31", "router31", "cluster31", "mirror31", "filter31"],
    ),
    (
        ("signal31 packet31 router31 cluster31 mirror31 filter31", 10),
        ["signal31", "packet31", "router31", "cluster31", "mirror31", "filter31"],
    ),
    (
        ("signal31 packet31 router31 cluster31 mirror31 filter31", 18),
        ["signal31 packet31", "router31 cluster31", "mirror31 filter31"],
    ),
    (
        ("signal31 packet31 router31 cluster31 mirror31 filter31", 28),
        ["signal31 packet31 router31", "cluster31 mirror31 filter31"],
    ),
    (
        ("packet31 router31 cluster31 mirror31 filter31 ranking31", 6),
        ["packet31", "router31", "cluster31", "mirror31", "filter31", "ranking31"],
    ),
    (
        ("packet31 router31 cluster31 mirror31 filter31 ranking31", 10),
        ["packet31", "router31", "cluster31", "mirror31", "filter31", "ranking31"],
    ),
    (
        ("packet31 router31 cluster31 mirror31 filter31 ranking31", 18),
        ["packet31 router31", "cluster31 mirror31", "filter31 ranking31"],
    ),
    (
        ("packet31 router31 cluster31 mirror31 filter31 ranking31", 28),
        ["packet31 router31 cluster31", "mirror31 filter31 ranking31"],
    ),
    (
        ("router31 cluster31 mirror31 filter31 ranking31 encoding31", 6),
        ["router31", "cluster31", "mirror31", "filter31", "ranking31", "encoding31"],
    ),
    (
        ("router31 cluster31 mirror31 filter31 ranking31 encoding31", 10),
        ["router31", "cluster31", "mirror31", "filter31", "ranking31", "encoding31"],
    ),
    (
        ("router31 cluster31 mirror31 filter31 ranking31 encoding31", 18),
        ["router31 cluster31", "mirror31 filter31", "ranking31", "encoding31"],
    ),
    (
        ("router31 cluster31 mirror31 filter31 ranking31 encoding31", 28),
        ["router31 cluster31 mirror31", "filter31 ranking31", "encoding31"],
    ),
    (
        ("cluster31 mirror31 filter31 ranking31 encoding31 mapping31", 6),
        ["cluster31", "mirror31", "filter31", "ranking31", "encoding31", "mapping31"],
    ),
    (
        ("cluster31 mirror31 filter31 ranking31 encoding31 mapping31", 10),
        ["cluster31", "mirror31", "filter31", "ranking31", "encoding31", "mapping31"],
    ),
    (
        ("cluster31 mirror31 filter31 ranking31 encoding31 mapping31", 18),
        ["cluster31 mirror31", "filter31 ranking31", "encoding31", "mapping31"],
    ),
    (
        ("cluster31 mirror31 filter31 ranking31 encoding31 mapping31", 28),
        ["cluster31 mirror31 filter31", "ranking31 encoding31", "mapping31"],
    ),
    (
        ("mirror31 filter31 ranking31 encoding31 mapping31 record31", 6),
        ["mirror31", "filter31", "ranking31", "encoding31", "mapping31", "record31"],
    ),
    (
        ("mirror31 filter31 ranking31 encoding31 mapping31 record31", 10),
        ["mirror31", "filter31", "ranking31", "encoding31", "mapping31", "record31"],
    ),
    (
        ("mirror31 filter31 ranking31 encoding31 mapping31 record31", 18),
        ["mirror31 filter31", "ranking31", "encoding31", "mapping31 record31"],
    ),
    (
        ("mirror31 filter31 ranking31 encoding31 mapping31 record31", 28),
        ["mirror31 filter31 ranking31", "encoding31 mapping31", "record31"],
    ),
    (
        ("filter31 ranking31 encoding31 mapping31 record31 candle31", 6),
        ["filter31", "ranking31", "encoding31", "mapping31", "record31", "candle31"],
    ),
    (
        ("filter31 ranking31 encoding31 mapping31 record31 candle31", 10),
        ["filter31", "ranking31", "encoding31", "mapping31", "record31", "candle31"],
    ),
    (
        ("filter31 ranking31 encoding31 mapping31 record31 candle31", 18),
        ["filter31 ranking31", "encoding31", "mapping31 record31", "candle31"],
    ),
    (
        ("filter31 ranking31 encoding31 mapping31 record31 candle31", 28),
        ["filter31 ranking31", "encoding31 mapping31", "record31 candle31"],
    ),
    (
        ("ranking31 encoding31 mapping31 record31 candle31 thread31", 6),
        ["ranking31", "encoding31", "mapping31", "record31", "candle31", "thread31"],
    ),
    (
        ("ranking31 encoding31 mapping31 record31 candle31 thread31", 10),
        ["ranking31", "encoding31", "mapping31", "record31", "candle31", "thread31"],
    ),
    (
        ("ranking31 encoding31 mapping31 record31 candle31 thread31", 18),
        ["ranking31", "encoding31", "mapping31 record31", "candle31 thread31"],
    ),
    (
        ("ranking31 encoding31 mapping31 record31 candle31 thread31", 28),
        ["ranking31 encoding31", "mapping31 record31 candle31", "thread31"],
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
