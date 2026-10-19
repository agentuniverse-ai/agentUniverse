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
        ("round 743: the quick brown fox jumps over the lazy dog", 4),
        ["round", "743:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", 8),
        ["round", "743: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", 12),
        ["round 743:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", 16),
        ["round 743: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", 24),
        ["round 743: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 743: the quick brown fox jumps over the lazy dog", 32),
        ["round 743: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", 4),
        ["round", "743:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", 8),
        ["round", "743:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", 12),
        ["round 743:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", 16),
        ["round 743:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", 24),
        ["round 743: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 743: agentuniverse is a framework for multi agents", 32),
        ["round 743: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", 4),
        ["round", "743:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", 8),
        ["round", "743:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", 12),
        ["round 743:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", 16),
        ["round 743:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", 24),
        ["round 743: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 743: knowledge stored as vectors enables retrieval", 32),
        ["round 743: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 743: the processor reads the record then stops", 4),
        ["round", "743:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 743: the processor reads the record then stops", 8),
        ["round", "743: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 743: the processor reads the record then stops", 12),
        ["round 743:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 743: the processor reads the record then stops", 16),
        ["round 743: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 743: the processor reads the record then stops", 24),
        ["round 743: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 743: the processor reads the record then stops", 32),
        ["round 743: the processor reads", "the record then stops"],
    ),
    (
        ("round 743: a worker pulls the next task from the queue", 4),
        ["round", "743:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 743: a worker pulls the next task from the queue", 8),
        ["round", "743: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 743: a worker pulls the next task from the queue", 12),
        ["round 743: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 743: a worker pulls the next task from the queue", 16),
        ["round 743: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 743: a worker pulls the next task from the queue", 24),
        ["round 743: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 743: a worker pulls the next task from the queue", 32),
        ["round 743: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 743: signals travel through the network layer", 4),
        ["round", "743:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 743: signals travel through the network layer", 8),
        ["round", "743:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 743: signals travel through the network layer", 12),
        ["round 743:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 743: signals travel through the network layer", 16),
        ["round 743:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 743: signals travel through the network layer", 24),
        ["round 743: signals", "travel through the", "network layer"],
    ),
    (
        ("round 743: signals travel through the network layer", 32),
        ["round 743: signals travel", "through the network layer"],
    ),
    (
        ("round 743: the gateway routes each request by policy", 4),
        ["round", "743:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 743: the gateway routes each request by policy", 8),
        ["round", "743: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 743: the gateway routes each request by policy", 12),
        ["round 743:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 743: the gateway routes each request by policy", 16),
        ["round 743: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 743: the gateway routes each request by policy", 24),
        ["round 743: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 743: the gateway routes each request by policy", 32),
        ["round 743: the gateway routes", "each request by policy"],
    ),
    (
        ("round 743: memory grows until the buffer is full", 4),
        ["round", "743:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 743: memory grows until the buffer is full", 8),
        ["round", "743:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 743: memory grows until the buffer is full", 12),
        ["round 743:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 743: memory grows until the buffer is full", 16),
        ["round 743:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 743: memory grows until the buffer is full", 24), ["round 743: memory grows", "until the buffer is full"]),
    (("round 743: memory grows until the buffer is full", 32), ["round 743: memory grows until", "the buffer is full"]),
    (
        ("round 743: the cluster mirrors every packet twice", 4),
        ["round", "743:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 743: the cluster mirrors every packet twice", 8),
        ["round", "743: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 743: the cluster mirrors every packet twice", 12),
        ["round 743:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 743: the cluster mirrors every packet twice", 16),
        ["round 743: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 743: the cluster mirrors every packet twice", 24),
        ["round 743: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 743: the cluster mirrors every packet twice", 32),
        ["round 743: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", 4),
        ["round", "743:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", 8),
        ["round", "743:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", 12),
        ["round 743:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", 16),
        ["round 743:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", 24),
        ["round 743: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 743: ranking uses tokens learned from the corpus", 32),
        ["round 743: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 743: a long session ends when the candle dies", 4),
        ["round", "743:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 743: a long session ends when the candle dies", 8),
        ["round", "743: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 743: a long session ends when the candle dies", 12),
        ["round 743: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 743: a long session ends when the candle dies", 16),
        ["round 743: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 743: a long session ends when the candle dies", 24),
        ["round 743: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 743: a long session ends when the candle dies", 32),
        ["round 743: a long session ends", "when the candle dies"],
    ),
    (
        ("round 743: encode the prompt then map the result", 4),
        ["round", "743:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 743: encode the prompt then map the result", 8),
        ["round", "743:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 743: encode the prompt then map the result", 12),
        ["round 743:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 743: encode the prompt then map the result", 16),
        ["round 743:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 743: encode the prompt then map the result", 24),
        ["round 743: encode the", "prompt then map the", "result"],
    ),
    (("round 743: encode the prompt then map the result", 32), ["round 743: encode the prompt", "then map the result"]),
    (
        ("round 743: the kernel wakes the worker at dawn", 4),
        ["round", "743:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 743: the kernel wakes the worker at dawn", 8),
        ["round", "743: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 743: the kernel wakes the worker at dawn", 12),
        ["round 743:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 743: the kernel wakes the worker at dawn", 16), ["round 743: the", "kernel wakes the", "worker at dawn"]),
    (("round 743: the kernel wakes the worker at dawn", 24), ["round 743: the kernel", "wakes the worker at dawn"]),
    (("round 743: the kernel wakes the worker at dawn", 32), ["round 743: the kernel wakes the", "worker at dawn"]),
    (
        ("round 743: service latency drops after the patch", 4),
        ["round", "743:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 743: service latency drops after the patch", 8),
        ["round", "743:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 743: service latency drops after the patch", 12),
        ["round 743:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 743: service latency drops after the patch", 16),
        ["round 743:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 743: service latency drops after the patch", 24),
        ["round 743: service", "latency drops after the", "patch"],
    ),
    (("round 743: service latency drops after the patch", 32), ["round 743: service latency drops", "after the patch"]),
    (
        ("round 743: the library caches every vector it sees", 4),
        ["round", "743:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 743: the library caches every vector it sees", 8),
        ["round", "743: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 743: the library caches every vector it sees", 12),
        ["round 743:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 743: the library caches every vector it sees", 16),
        ["round 743: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 743: the library caches every vector it sees", 24),
        ["round 743: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 743: the library caches every vector it sees", 32),
        ["round 743: the library caches", "every vector it sees"],
    ),
    (
        ("round 743: agents argue then the debate resolves", 4),
        ["round", "743:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 743: agents argue then the debate resolves", 8),
        ["round", "743:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 743: agents argue then the debate resolves", 12),
        ["round 743:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 743: agents argue then the debate resolves", 16),
        ["round 743:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 743: agents argue then the debate resolves", 24), ["round 743: agents argue", "then the debate resolves"]),
    (("round 743: agents argue then the debate resolves", 32), ["round 743: agents argue then the", "debate resolves"]),
    (
        ("round 743: the filter keeps only strong matches", 4),
        ["round", "743:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 743: the filter keeps only strong matches", 8),
        ["round", "743: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 743: the filter keeps only strong matches", 12),
        ["round 743:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 743: the filter keeps only strong matches", 16),
        ["round 743: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 743: the filter keeps only strong matches", 24),
        ["round 743: the filter", "keeps only strong", "matches"],
    ),
    (("round 743: the filter keeps only strong matches", 32), ["round 743: the filter keeps only", "strong matches"]),
    (
        ("round 743: the model answers with a short reply", 4),
        ["round", "743:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 743: the model answers with a short reply", 8),
        ["round", "743: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 743: the model answers with a short reply", 12),
        ["round 743:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 743: the model answers with a short reply", 16),
        ["round 743: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 743: the model answers with a short reply", 24),
        ["round 743: the model", "answers with a short", "reply"],
    ),
    (("round 743: the model answers with a short reply", 32), ["round 743: the model answers", "with a short reply"]),
    (
        ("round 743: the recorder stores the reasoning trace", 4),
        ["round", "743:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 743: the recorder stores the reasoning trace", 8),
        ["round", "743: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 743: the recorder stores the reasoning trace", 12),
        ["round 743:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 743: the recorder stores the reasoning trace", 16),
        ["round 743: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 743: the recorder stores the reasoning trace", 24),
        ["round 743: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 743: the recorder stores the reasoning trace", 32),
        ["round 743: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 743: the angel watches the processor run", 4),
        ["round", "743:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 743: the angel watches the processor run", 8),
        ["round", "743: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 743: the angel watches the processor run", 12),
        ["round 743:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 743: the angel watches the processor run", 16),
        ["round 743: the", "angel watches", "the processor", "run"],
    ),
    (("round 743: the angel watches the processor run", 24), ["round 743: the angel", "watches the processor", "run"]),
    (("round 743: the angel watches the processor run", 32), ["round 743: the angel watches the", "processor run"]),
    (
        ("round 743: angle of the vector decides the match", 4),
        ["round", "743:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 743: angle of the vector decides the match", 8),
        ["round", "743:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 743: angle of the vector decides the match", 12),
        ["round 743:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 743: angle of the vector decides the match", 16),
        ["round 743: angle", "of the vector", "decides the", "match"],
    ),
    (("round 743: angle of the vector decides the match", 24), ["round 743: angle of the", "vector decides the match"]),
    (("round 743: angle of the vector decides the match", 32), ["round 743: angle of the vector", "decides the match"]),
    (
        ("round 743: the candle burns twice as long at night", 4),
        ["round", "743:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 743: the candle burns twice as long at night", 8),
        ["round", "743: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 743: the candle burns twice as long at night", 12),
        ["round 743:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 743: the candle burns twice as long at night", 16),
        ["round 743: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 743: the candle burns twice as long at night", 24),
        ["round 743: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 743: the candle burns twice as long at night", 32),
        ["round 743: the candle burns", "twice as long at night"],
    ),
    (
        ("round 743: a mirror of the universe in one line", 4),
        ["round", "743:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 743: a mirror of the universe in one line", 8),
        ["round", "743: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 743: a mirror of the universe in one line", 12),
        ["round 743: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 743: a mirror of the universe in one line", 16),
        ["round 743: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 743: a mirror of the universe in one line", 24), ["round 743: a mirror of", "the universe in one line"]),
    (("round 743: a mirror of the universe in one line", 32), ["round 743: a mirror of the", "universe in one line"]),
    (
        ("round 743: the queue drains before the storm", 4),
        ["round", "743:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 743: the queue drains before the storm", 8),
        ["round", "743: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 743: the queue drains before the storm", 12),
        ["round 743:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 743: the queue drains before the storm", 16), ["round 743: the", "queue drains", "before the storm"]),
    (("round 743: the queue drains before the storm", 24), ["round 743: the queue", "drains before the storm"]),
    (("round 743: the queue drains before the storm", 32), ["round 743: the queue drains", "before the storm"]),
    (
        ("kitten743 sitting743 agent743 angle743 universe743 memory743", 6),
        ["kitten743", "sitting743", "agent743", "angle743", "universe743", "memory743"],
    ),
    (
        ("kitten743 sitting743 agent743 angle743 universe743 memory743", 10),
        ["kitten743", "sitting743", "agent743", "angle743", "universe743", "memory743"],
    ),
    (
        ("kitten743 sitting743 agent743 angle743 universe743 memory743", 18),
        ["kitten743", "sitting743", "agent743 angle743", "universe743", "memory743"],
    ),
    (
        ("kitten743 sitting743 agent743 angle743 universe743 memory743", 28),
        ["kitten743 sitting743", "agent743 angle743", "universe743 memory743"],
    ),
    (
        ("sitting743 agent743 angle743 universe743 memory743 stream743", 6),
        ["sitting743", "agent743", "angle743", "universe743", "memory743", "stream743"],
    ),
    (
        ("sitting743 agent743 angle743 universe743 memory743 stream743", 10),
        ["sitting743", "agent743", "angle743", "universe743", "memory743", "stream743"],
    ),
    (
        ("sitting743 agent743 angle743 universe743 memory743 stream743", 18),
        ["sitting743", "agent743 angle743", "universe743", "memory743", "stream743"],
    ),
    (
        ("sitting743 agent743 angle743 universe743 memory743 stream743", 28),
        ["sitting743 agent743 angle743", "universe743 memory743", "stream743"],
    ),
    (
        ("agent743 angle743 universe743 memory743 stream743 context743", 6),
        ["agent743", "angle743", "universe743", "memory743", "stream743", "context743"],
    ),
    (
        ("agent743 angle743 universe743 memory743 stream743 context743", 10),
        ["agent743", "angle743", "universe743", "memory743", "stream743", "context743"],
    ),
    (
        ("agent743 angle743 universe743 memory743 stream743 context743", 18),
        ["agent743 angle743", "universe743", "memory743", "stream743", "context743"],
    ),
    (
        ("agent743 angle743 universe743 memory743 stream743 context743", 28),
        ["agent743 angle743", "universe743 memory743", "stream743 context743"],
    ),
    (
        ("angle743 universe743 memory743 stream743 context743 knowledge743", 6),
        ["angle743", "universe743", "memory743", "stream743", "context743", "knowledge743"],
    ),
    (
        ("angle743 universe743 memory743 stream743 context743 knowledge743", 10),
        ["angle743", "universe743", "memory743", "stream743", "context743", "knowledge743"],
    ),
    (
        ("angle743 universe743 memory743 stream743 context743 knowledge743", 18),
        ["angle743", "universe743", "memory743", "stream743", "context743", "knowledge743"],
    ),
    (
        ("angle743 universe743 memory743 stream743 context743 knowledge743", 28),
        ["angle743 universe743", "memory743 stream743", "context743 knowledge743"],
    ),
    (
        ("universe743 memory743 stream743 context743 knowledge743 vector743", 6),
        ["universe743", "memory743", "stream743", "context743", "knowledge743", "vector743"],
    ),
    (
        ("universe743 memory743 stream743 context743 knowledge743 vector743", 10),
        ["universe743", "memory743", "stream743", "context743", "knowledge743", "vector743"],
    ),
    (
        ("universe743 memory743 stream743 context743 knowledge743 vector743", 18),
        ["universe743", "memory743", "stream743", "context743", "knowledge743", "vector743"],
    ),
    (
        ("universe743 memory743 stream743 context743 knowledge743 vector743", 28),
        ["universe743 memory743", "stream743 context743", "knowledge743 vector743"],
    ),
    (
        ("memory743 stream743 context743 knowledge743 vector743 processor743", 6),
        ["memory743", "stream743", "context743", "knowledge743", "vector743", "processor743"],
    ),
    (
        ("memory743 stream743 context743 knowledge743 vector743 processor743", 10),
        ["memory743", "stream743", "context743", "knowledge743", "vector743", "processor743"],
    ),
    (
        ("memory743 stream743 context743 knowledge743 vector743 processor743", 18),
        ["memory743", "stream743", "context743", "knowledge743", "vector743", "processor743"],
    ),
    (
        ("memory743 stream743 context743 knowledge743 vector743 processor743", 28),
        ["memory743 stream743", "context743 knowledge743", "vector743 processor743"],
    ),
    (
        ("stream743 context743 knowledge743 vector743 processor743 reasoning743", 6),
        ["stream743", "context743", "knowledge743", "vector743", "processor743", "reasoning743"],
    ),
    (
        ("stream743 context743 knowledge743 vector743 processor743 reasoning743", 10),
        ["stream743", "context743", "knowledge743", "vector743", "processor743", "reasoning743"],
    ),
    (
        ("stream743 context743 knowledge743 vector743 processor743 reasoning743", 18),
        ["stream743", "context743", "knowledge743", "vector743", "processor743", "reasoning743"],
    ),
    (
        ("stream743 context743 knowledge743 vector743 processor743 reasoning743", 28),
        ["stream743 context743", "knowledge743 vector743", "processor743 reasoning743"],
    ),
    (
        ("context743 knowledge743 vector743 processor743 reasoning743 machine743", 6),
        ["context743", "knowledge743", "vector743", "processor743", "reasoning743", "machine743"],
    ),
    (
        ("context743 knowledge743 vector743 processor743 reasoning743 machine743", 10),
        ["context743", "knowledge743", "vector743", "processor743", "reasoning743", "machine743"],
    ),
    (
        ("context743 knowledge743 vector743 processor743 reasoning743 machine743", 18),
        ["context743", "knowledge743", "vector743", "processor743", "reasoning743", "machine743"],
    ),
    (
        ("context743 knowledge743 vector743 processor743 reasoning743 machine743", 28),
        ["context743 knowledge743", "vector743 processor743", "reasoning743 machine743"],
    ),
    (
        ("knowledge743 vector743 processor743 reasoning743 machine743 learning743", 6),
        ["knowledge743", "vector743", "processor743", "reasoning743", "machine743", "learning743"],
    ),
    (
        ("knowledge743 vector743 processor743 reasoning743 machine743 learning743", 10),
        ["knowledge743", "vector743", "processor743", "reasoning743", "machine743", "learning743"],
    ),
    (
        ("knowledge743 vector743 processor743 reasoning743 machine743 learning743", 18),
        ["knowledge743", "vector743", "processor743", "reasoning743", "machine743", "learning743"],
    ),
    (
        ("knowledge743 vector743 processor743 reasoning743 machine743 learning743", 28),
        ["knowledge743 vector743", "processor743 reasoning743", "machine743 learning743"],
    ),
    (
        ("vector743 processor743 reasoning743 machine743 learning743 model743", 6),
        ["vector743", "processor743", "reasoning743", "machine743", "learning743", "model743"],
    ),
    (
        ("vector743 processor743 reasoning743 machine743 learning743 model743", 10),
        ["vector743", "processor743", "reasoning743", "machine743", "learning743", "model743"],
    ),
    (
        ("vector743 processor743 reasoning743 machine743 learning743 model743", 18),
        ["vector743", "processor743", "reasoning743", "machine743", "learning743", "model743"],
    ),
    (
        ("vector743 processor743 reasoning743 machine743 learning743 model743", 28),
        ["vector743 processor743", "reasoning743 machine743", "learning743 model743"],
    ),
    (
        ("processor743 reasoning743 machine743 learning743 model743 token743", 6),
        ["processor743", "reasoning743", "machine743", "learning743", "model743", "token743"],
    ),
    (
        ("processor743 reasoning743 machine743 learning743 model743 token743", 10),
        ["processor743", "reasoning743", "machine743", "learning743", "model743", "token743"],
    ),
    (
        ("processor743 reasoning743 machine743 learning743 model743 token743", 18),
        ["processor743", "reasoning743", "machine743", "learning743", "model743 token743"],
    ),
    (
        ("processor743 reasoning743 machine743 learning743 model743 token743", 28),
        ["processor743 reasoning743", "machine743 learning743", "model743 token743"],
    ),
    (
        ("reasoning743 machine743 learning743 model743 token743 prompt743", 6),
        ["reasoning743", "machine743", "learning743", "model743", "token743", "prompt743"],
    ),
    (
        ("reasoning743 machine743 learning743 model743 token743 prompt743", 10),
        ["reasoning743", "machine743", "learning743", "model743", "token743", "prompt743"],
    ),
    (
        ("reasoning743 machine743 learning743 model743 token743 prompt743", 18),
        ["reasoning743", "machine743", "learning743", "model743 token743", "prompt743"],
    ),
    (
        ("reasoning743 machine743 learning743 model743 token743 prompt743", 28),
        ["reasoning743 machine743", "learning743 model743", "token743 prompt743"],
    ),
    (
        ("machine743 learning743 model743 token743 prompt743 session743", 6),
        ["machine743", "learning743", "model743", "token743", "prompt743", "session743"],
    ),
    (
        ("machine743 learning743 model743 token743 prompt743 session743", 10),
        ["machine743", "learning743", "model743", "token743", "prompt743", "session743"],
    ),
    (
        ("machine743 learning743 model743 token743 prompt743 session743", 18),
        ["machine743", "learning743", "model743 token743", "prompt743", "session743"],
    ),
    (
        ("machine743 learning743 model743 token743 prompt743 session743", 28),
        ["machine743 learning743", "model743 token743 prompt743", "session743"],
    ),
    (
        ("learning743 model743 token743 prompt743 session743 library743", 6),
        ["learning743", "model743", "token743", "prompt743", "session743", "library743"],
    ),
    (
        ("learning743 model743 token743 prompt743 session743 library743", 10),
        ["learning743", "model743", "token743", "prompt743", "session743", "library743"],
    ),
    (
        ("learning743 model743 token743 prompt743 session743 library743", 18),
        ["learning743", "model743 token743", "prompt743", "session743", "library743"],
    ),
    (
        ("learning743 model743 token743 prompt743 session743 library743", 28),
        ["learning743 model743", "token743 prompt743", "session743 library743"],
    ),
    (
        ("model743 token743 prompt743 session743 library743 service743", 6),
        ["model743", "token743", "prompt743", "session743", "library743", "service743"],
    ),
    (
        ("model743 token743 prompt743 session743 library743 service743", 10),
        ["model743", "token743", "prompt743", "session743", "library743", "service743"],
    ),
    (
        ("model743 token743 prompt743 session743 library743 service743", 18),
        ["model743 token743", "prompt743", "session743", "library743", "service743"],
    ),
    (
        ("model743 token743 prompt743 session743 library743 service743", 28),
        ["model743 token743 prompt743", "session743 library743", "service743"],
    ),
    (
        ("token743 prompt743 session743 library743 service743 gateway743", 6),
        ["token743", "prompt743", "session743", "library743", "service743", "gateway743"],
    ),
    (
        ("token743 prompt743 session743 library743 service743 gateway743", 10),
        ["token743", "prompt743", "session743", "library743", "service743", "gateway743"],
    ),
    (
        ("token743 prompt743 session743 library743 service743 gateway743", 18),
        ["token743 prompt743", "session743", "library743", "service743", "gateway743"],
    ),
    (
        ("token743 prompt743 session743 library743 service743 gateway743", 28),
        ["token743 prompt743", "session743 library743", "service743 gateway743"],
    ),
    (
        ("prompt743 session743 library743 service743 gateway743 storage743", 6),
        ["prompt743", "session743", "library743", "service743", "gateway743", "storage743"],
    ),
    (
        ("prompt743 session743 library743 service743 gateway743 storage743", 10),
        ["prompt743", "session743", "library743", "service743", "gateway743", "storage743"],
    ),
    (
        ("prompt743 session743 library743 service743 gateway743 storage743", 18),
        ["prompt743", "session743", "library743", "service743", "gateway743", "storage743"],
    ),
    (
        ("prompt743 session743 library743 service743 gateway743 storage743", 28),
        ["prompt743 session743", "library743 service743", "gateway743 storage743"],
    ),
    (
        ("session743 library743 service743 gateway743 storage743 network743", 6),
        ["session743", "library743", "service743", "gateway743", "storage743", "network743"],
    ),
    (
        ("session743 library743 service743 gateway743 storage743 network743", 10),
        ["session743", "library743", "service743", "gateway743", "storage743", "network743"],
    ),
    (
        ("session743 library743 service743 gateway743 storage743 network743", 18),
        ["session743", "library743", "service743", "gateway743", "storage743", "network743"],
    ),
    (
        ("session743 library743 service743 gateway743 storage743 network743", 28),
        ["session743 library743", "service743 gateway743", "storage743 network743"],
    ),
    (
        ("library743 service743 gateway743 storage743 network743 latency743", 6),
        ["library743", "service743", "gateway743", "storage743", "network743", "latency743"],
    ),
    (
        ("library743 service743 gateway743 storage743 network743 latency743", 10),
        ["library743", "service743", "gateway743", "storage743", "network743", "latency743"],
    ),
    (
        ("library743 service743 gateway743 storage743 network743 latency743", 18),
        ["library743", "service743", "gateway743", "storage743", "network743", "latency743"],
    ),
    (
        ("library743 service743 gateway743 storage743 network743 latency743", 28),
        ["library743 service743", "gateway743 storage743", "network743 latency743"],
    ),
    (
        ("service743 gateway743 storage743 network743 latency743 buffer743", 6),
        ["service743", "gateway743", "storage743", "network743", "latency743", "buffer743"],
    ),
    (
        ("service743 gateway743 storage743 network743 latency743 buffer743", 10),
        ["service743", "gateway743", "storage743", "network743", "latency743", "buffer743"],
    ),
    (
        ("service743 gateway743 storage743 network743 latency743 buffer743", 18),
        ["service743", "gateway743", "storage743", "network743", "latency743", "buffer743"],
    ),
    (
        ("service743 gateway743 storage743 network743 latency743 buffer743", 28),
        ["service743 gateway743", "storage743 network743", "latency743 buffer743"],
    ),
    (
        ("gateway743 storage743 network743 latency743 buffer743 queue743", 6),
        ["gateway743", "storage743", "network743", "latency743", "buffer743", "queue743"],
    ),
    (
        ("gateway743 storage743 network743 latency743 buffer743 queue743", 10),
        ["gateway743", "storage743", "network743", "latency743", "buffer743", "queue743"],
    ),
    (
        ("gateway743 storage743 network743 latency743 buffer743 queue743", 18),
        ["gateway743", "storage743", "network743", "latency743", "buffer743 queue743"],
    ),
    (
        ("gateway743 storage743 network743 latency743 buffer743 queue743", 28),
        ["gateway743 storage743", "network743 latency743", "buffer743 queue743"],
    ),
    (
        ("storage743 network743 latency743 buffer743 queue743 worker743", 6),
        ["storage743", "network743", "latency743", "buffer743", "queue743", "worker743"],
    ),
    (
        ("storage743 network743 latency743 buffer743 queue743 worker743", 10),
        ["storage743", "network743", "latency743", "buffer743", "queue743", "worker743"],
    ),
    (
        ("storage743 network743 latency743 buffer743 queue743 worker743", 18),
        ["storage743", "network743", "latency743", "buffer743 queue743", "worker743"],
    ),
    (
        ("storage743 network743 latency743 buffer743 queue743 worker743", 28),
        ["storage743 network743", "latency743 buffer743", "queue743 worker743"],
    ),
    (
        ("network743 latency743 buffer743 queue743 worker743 kernel743", 6),
        ["network743", "latency743", "buffer743", "queue743", "worker743", "kernel743"],
    ),
    (
        ("network743 latency743 buffer743 queue743 worker743 kernel743", 10),
        ["network743", "latency743", "buffer743", "queue743", "worker743", "kernel743"],
    ),
    (
        ("network743 latency743 buffer743 queue743 worker743 kernel743", 18),
        ["network743", "latency743", "buffer743 queue743", "worker743", "kernel743"],
    ),
    (
        ("network743 latency743 buffer743 queue743 worker743 kernel743", 28),
        ["network743 latency743", "buffer743 queue743 worker743", "kernel743"],
    ),
    (
        ("latency743 buffer743 queue743 worker743 kernel743 signal743", 6),
        ["latency743", "buffer743", "queue743", "worker743", "kernel743", "signal743"],
    ),
    (
        ("latency743 buffer743 queue743 worker743 kernel743 signal743", 10),
        ["latency743", "buffer743", "queue743", "worker743", "kernel743", "signal743"],
    ),
    (
        ("latency743 buffer743 queue743 worker743 kernel743 signal743", 18),
        ["latency743", "buffer743 queue743", "worker743", "kernel743", "signal743"],
    ),
    (
        ("latency743 buffer743 queue743 worker743 kernel743 signal743", 28),
        ["latency743 buffer743", "queue743 worker743 kernel743", "signal743"],
    ),
    (
        ("buffer743 queue743 worker743 kernel743 signal743 packet743", 6),
        ["buffer743", "queue743", "worker743", "kernel743", "signal743", "packet743"],
    ),
    (
        ("buffer743 queue743 worker743 kernel743 signal743 packet743", 10),
        ["buffer743", "queue743", "worker743", "kernel743", "signal743", "packet743"],
    ),
    (
        ("buffer743 queue743 worker743 kernel743 signal743 packet743", 18),
        ["buffer743 queue743", "worker743", "kernel743", "signal743", "packet743"],
    ),
    (
        ("buffer743 queue743 worker743 kernel743 signal743 packet743", 28),
        ["buffer743 queue743 worker743", "kernel743 signal743", "packet743"],
    ),
    (
        ("queue743 worker743 kernel743 signal743 packet743 router743", 6),
        ["queue743", "worker743", "kernel743", "signal743", "packet743", "router743"],
    ),
    (
        ("queue743 worker743 kernel743 signal743 packet743 router743", 10),
        ["queue743", "worker743", "kernel743", "signal743", "packet743", "router743"],
    ),
    (
        ("queue743 worker743 kernel743 signal743 packet743 router743", 18),
        ["queue743 worker743", "kernel743", "signal743", "packet743", "router743"],
    ),
    (
        ("queue743 worker743 kernel743 signal743 packet743 router743", 28),
        ["queue743 worker743 kernel743", "signal743 packet743", "router743"],
    ),
    (
        ("worker743 kernel743 signal743 packet743 router743 cluster743", 6),
        ["worker743", "kernel743", "signal743", "packet743", "router743", "cluster743"],
    ),
    (
        ("worker743 kernel743 signal743 packet743 router743 cluster743", 10),
        ["worker743", "kernel743", "signal743", "packet743", "router743", "cluster743"],
    ),
    (
        ("worker743 kernel743 signal743 packet743 router743 cluster743", 18),
        ["worker743", "kernel743", "signal743", "packet743", "router743", "cluster743"],
    ),
    (
        ("worker743 kernel743 signal743 packet743 router743 cluster743", 28),
        ["worker743 kernel743", "signal743 packet743", "router743 cluster743"],
    ),
    (
        ("kernel743 signal743 packet743 router743 cluster743 mirror743", 6),
        ["kernel743", "signal743", "packet743", "router743", "cluster743", "mirror743"],
    ),
    (
        ("kernel743 signal743 packet743 router743 cluster743 mirror743", 10),
        ["kernel743", "signal743", "packet743", "router743", "cluster743", "mirror743"],
    ),
    (
        ("kernel743 signal743 packet743 router743 cluster743 mirror743", 18),
        ["kernel743", "signal743", "packet743", "router743", "cluster743", "mirror743"],
    ),
    (
        ("kernel743 signal743 packet743 router743 cluster743 mirror743", 28),
        ["kernel743 signal743", "packet743 router743", "cluster743 mirror743"],
    ),
    (
        ("signal743 packet743 router743 cluster743 mirror743 filter743", 6),
        ["signal743", "packet743", "router743", "cluster743", "mirror743", "filter743"],
    ),
    (
        ("signal743 packet743 router743 cluster743 mirror743 filter743", 10),
        ["signal743", "packet743", "router743", "cluster743", "mirror743", "filter743"],
    ),
    (
        ("signal743 packet743 router743 cluster743 mirror743 filter743", 18),
        ["signal743", "packet743", "router743", "cluster743", "mirror743", "filter743"],
    ),
    (
        ("signal743 packet743 router743 cluster743 mirror743 filter743", 28),
        ["signal743 packet743", "router743 cluster743", "mirror743 filter743"],
    ),
    (
        ("packet743 router743 cluster743 mirror743 filter743 ranking743", 6),
        ["packet743", "router743", "cluster743", "mirror743", "filter743", "ranking743"],
    ),
    (
        ("packet743 router743 cluster743 mirror743 filter743 ranking743", 10),
        ["packet743", "router743", "cluster743", "mirror743", "filter743", "ranking743"],
    ),
    (
        ("packet743 router743 cluster743 mirror743 filter743 ranking743", 18),
        ["packet743", "router743", "cluster743", "mirror743", "filter743", "ranking743"],
    ),
    (
        ("packet743 router743 cluster743 mirror743 filter743 ranking743", 28),
        ["packet743 router743", "cluster743 mirror743", "filter743 ranking743"],
    ),
    (
        ("router743 cluster743 mirror743 filter743 ranking743 encoding743", 6),
        ["router743", "cluster743", "mirror743", "filter743", "ranking743", "encoding743"],
    ),
    (
        ("router743 cluster743 mirror743 filter743 ranking743 encoding743", 10),
        ["router743", "cluster743", "mirror743", "filter743", "ranking743", "encoding743"],
    ),
    (
        ("router743 cluster743 mirror743 filter743 ranking743 encoding743", 18),
        ["router743", "cluster743", "mirror743", "filter743", "ranking743", "encoding743"],
    ),
    (
        ("router743 cluster743 mirror743 filter743 ranking743 encoding743", 28),
        ["router743 cluster743", "mirror743 filter743", "ranking743 encoding743"],
    ),
    (
        ("cluster743 mirror743 filter743 ranking743 encoding743 mapping743", 6),
        ["cluster743", "mirror743", "filter743", "ranking743", "encoding743", "mapping743"],
    ),
    (
        ("cluster743 mirror743 filter743 ranking743 encoding743 mapping743", 10),
        ["cluster743", "mirror743", "filter743", "ranking743", "encoding743", "mapping743"],
    ),
    (
        ("cluster743 mirror743 filter743 ranking743 encoding743 mapping743", 18),
        ["cluster743", "mirror743", "filter743", "ranking743", "encoding743", "mapping743"],
    ),
    (
        ("cluster743 mirror743 filter743 ranking743 encoding743 mapping743", 28),
        ["cluster743 mirror743", "filter743 ranking743", "encoding743 mapping743"],
    ),
    (
        ("mirror743 filter743 ranking743 encoding743 mapping743 record743", 6),
        ["mirror743", "filter743", "ranking743", "encoding743", "mapping743", "record743"],
    ),
    (
        ("mirror743 filter743 ranking743 encoding743 mapping743 record743", 10),
        ["mirror743", "filter743", "ranking743", "encoding743", "mapping743", "record743"],
    ),
    (
        ("mirror743 filter743 ranking743 encoding743 mapping743 record743", 18),
        ["mirror743", "filter743", "ranking743", "encoding743", "mapping743", "record743"],
    ),
    (
        ("mirror743 filter743 ranking743 encoding743 mapping743 record743", 28),
        ["mirror743 filter743", "ranking743 encoding743", "mapping743 record743"],
    ),
    (
        ("filter743 ranking743 encoding743 mapping743 record743 candle743", 6),
        ["filter743", "ranking743", "encoding743", "mapping743", "record743", "candle743"],
    ),
    (
        ("filter743 ranking743 encoding743 mapping743 record743 candle743", 10),
        ["filter743", "ranking743", "encoding743", "mapping743", "record743", "candle743"],
    ),
    (
        ("filter743 ranking743 encoding743 mapping743 record743 candle743", 18),
        ["filter743", "ranking743", "encoding743", "mapping743", "record743", "candle743"],
    ),
    (
        ("filter743 ranking743 encoding743 mapping743 record743 candle743", 28),
        ["filter743 ranking743", "encoding743 mapping743", "record743 candle743"],
    ),
    (
        ("ranking743 encoding743 mapping743 record743 candle743 thread743", 6),
        ["ranking743", "encoding743", "mapping743", "record743", "candle743", "thread743"],
    ),
    (
        ("ranking743 encoding743 mapping743 record743 candle743 thread743", 10),
        ["ranking743", "encoding743", "mapping743", "record743", "candle743", "thread743"],
    ),
    (
        ("ranking743 encoding743 mapping743 record743 candle743 thread743", 18),
        ["ranking743", "encoding743", "mapping743", "record743", "candle743", "thread743"],
    ),
    (
        ("ranking743 encoding743 mapping743 record743 candle743 thread743", 28),
        ["ranking743 encoding743", "mapping743 record743", "candle743 thread743"],
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
