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
        ("round 51: the quick brown fox jumps over the lazy dog", 4),
        ["round", "51:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 51: the quick brown fox jumps over the lazy dog", 8),
        ["round", "51: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 51: the quick brown fox jumps over the lazy dog", 12),
        ["round 51:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 51: the quick brown fox jumps over the lazy dog", 16),
        ["round 51: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 51: the quick brown fox jumps over the lazy dog", 24),
        ["round 51: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 51: the quick brown fox jumps over the lazy dog", 32),
        ["round 51: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 51: agentuniverse is a framework for multi agents", 4),
        ["round", "51:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 51: agentuniverse is a framework for multi agents", 8),
        ["round", "51:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 51: agentuniverse is a framework for multi agents", 12),
        ["round 51:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 51: agentuniverse is a framework for multi agents", 16),
        ["round 51:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 51: agentuniverse is a framework for multi agents", 24),
        ["round 51: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 51: agentuniverse is a framework for multi agents", 32),
        ["round 51: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 51: knowledge stored as vectors enables retrieval", 4),
        ["round", "51:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 51: knowledge stored as vectors enables retrieval", 8),
        ["round", "51:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 51: knowledge stored as vectors enables retrieval", 12),
        ["round 51:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 51: knowledge stored as vectors enables retrieval", 16),
        ["round 51:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 51: knowledge stored as vectors enables retrieval", 24),
        ["round 51: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 51: knowledge stored as vectors enables retrieval", 32),
        ["round 51: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 51: the processor reads the record then stops", 4),
        ["round", "51:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 51: the processor reads the record then stops", 8),
        ["round", "51: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 51: the processor reads the record then stops", 12),
        ["round 51:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 51: the processor reads the record then stops", 16),
        ["round 51: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 51: the processor reads the record then stops", 24),
        ["round 51: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 51: the processor reads the record then stops", 32),
        ["round 51: the processor reads", "the record then stops"],
    ),
    (
        ("round 51: a worker pulls the next task from the queue", 4),
        ["round", "51:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 51: a worker pulls the next task from the queue", 8),
        ["round", "51: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 51: a worker pulls the next task from the queue", 12),
        ["round 51: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 51: a worker pulls the next task from the queue", 16),
        ["round 51: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 51: a worker pulls the next task from the queue", 24),
        ["round 51: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 51: a worker pulls the next task from the queue", 32),
        ["round 51: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 51: signals travel through the network layer", 4),
        ["round", "51:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 51: signals travel through the network layer", 8),
        ["round", "51:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 51: signals travel through the network layer", 12),
        ["round 51:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 51: signals travel through the network layer", 16),
        ["round 51:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 51: signals travel through the network layer", 24),
        ["round 51: signals travel", "through the network", "layer"],
    ),
    (
        ("round 51: signals travel through the network layer", 32),
        ["round 51: signals travel through", "the network layer"],
    ),
    (
        ("round 51: the gateway routes each request by policy", 4),
        ["round", "51:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 51: the gateway routes each request by policy", 8),
        ["round", "51: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 51: the gateway routes each request by policy", 12),
        ["round 51:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 51: the gateway routes each request by policy", 16),
        ["round 51: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 51: the gateway routes each request by policy", 24),
        ["round 51: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 51: the gateway routes each request by policy", 32),
        ["round 51: the gateway routes", "each request by policy"],
    ),
    (
        ("round 51: memory grows until the buffer is full", 4),
        ["round", "51:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 51: memory grows until the buffer is full", 8),
        ["round", "51:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 51: memory grows until the buffer is full", 12),
        ["round 51:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 51: memory grows until the buffer is full", 16),
        ["round 51: memory", "grows until the", "buffer is full"],
    ),
    (("round 51: memory grows until the buffer is full", 24), ["round 51: memory grows", "until the buffer is full"]),
    (("round 51: memory grows until the buffer is full", 32), ["round 51: memory grows until the", "buffer is full"]),
    (
        ("round 51: the cluster mirrors every packet twice", 4),
        ["round", "51:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 51: the cluster mirrors every packet twice", 8),
        ["round", "51: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 51: the cluster mirrors every packet twice", 12),
        ["round 51:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 51: the cluster mirrors every packet twice", 16),
        ["round 51: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 51: the cluster mirrors every packet twice", 24),
        ["round 51: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 51: the cluster mirrors every packet twice", 32), ["round 51: the cluster mirrors", "every packet twice"]),
    (
        ("round 51: ranking uses tokens learned from the corpus", 4),
        ["round", "51:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 51: ranking uses tokens learned from the corpus", 8),
        ["round", "51:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 51: ranking uses tokens learned from the corpus", 12),
        ["round 51:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 51: ranking uses tokens learned from the corpus", 16),
        ["round 51:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 51: ranking uses tokens learned from the corpus", 24),
        ["round 51: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 51: ranking uses tokens learned from the corpus", 32),
        ["round 51: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 51: a long session ends when the candle dies", 4),
        ["round", "51:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 51: a long session ends when the candle dies", 8),
        ["round", "51: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 51: a long session ends when the candle dies", 12),
        ["round 51: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 51: a long session ends when the candle dies", 16),
        ["round 51: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 51: a long session ends when the candle dies", 24),
        ["round 51: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 51: a long session ends when the candle dies", 32),
        ["round 51: a long session ends", "when the candle dies"],
    ),
    (
        ("round 51: encode the prompt then map the result", 4),
        ["round", "51:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 51: encode the prompt then map the result", 8),
        ["round", "51:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 51: encode the prompt then map the result", 12),
        ["round 51:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 51: encode the prompt then map the result", 16),
        ["round 51: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 51: encode the prompt then map the result", 24),
        ["round 51: encode the", "prompt then map the", "result"],
    ),
    (("round 51: encode the prompt then map the result", 32), ["round 51: encode the prompt then", "map the result"]),
    (
        ("round 51: the kernel wakes the worker at dawn", 4),
        ["round", "51:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 51: the kernel wakes the worker at dawn", 8),
        ["round", "51: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 51: the kernel wakes the worker at dawn", 12),
        ["round 51:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 51: the kernel wakes the worker at dawn", 16), ["round 51: the", "kernel wakes the", "worker at dawn"]),
    (("round 51: the kernel wakes the worker at dawn", 24), ["round 51: the kernel", "wakes the worker at dawn"]),
    (("round 51: the kernel wakes the worker at dawn", 32), ["round 51: the kernel wakes the", "worker at dawn"]),
    (
        ("round 51: service latency drops after the patch", 4),
        ["round", "51:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 51: service latency drops after the patch", 8),
        ["round", "51:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 51: service latency drops after the patch", 12),
        ["round 51:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 51: service latency drops after the patch", 16),
        ["round 51:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 51: service latency drops after the patch", 24),
        ["round 51: service", "latency drops after the", "patch"],
    ),
    (("round 51: service latency drops after the patch", 32), ["round 51: service latency drops", "after the patch"]),
    (
        ("round 51: the library caches every vector it sees", 4),
        ["round", "51:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 51: the library caches every vector it sees", 8),
        ["round", "51: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 51: the library caches every vector it sees", 12),
        ["round 51:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 51: the library caches every vector it sees", 16),
        ["round 51: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 51: the library caches every vector it sees", 24),
        ["round 51: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 51: the library caches every vector it sees", 32),
        ["round 51: the library caches", "every vector it sees"],
    ),
    (
        ("round 51: agents argue then the debate resolves", 4),
        ["round", "51:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 51: agents argue then the debate resolves", 8),
        ["round", "51:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 51: agents argue then the debate resolves", 12),
        ["round 51:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 51: agents argue then the debate resolves", 16),
        ["round 51: agents", "argue then the", "debate resolves"],
    ),
    (("round 51: agents argue then the debate resolves", 24), ["round 51: agents argue", "then the debate resolves"]),
    (("round 51: agents argue then the debate resolves", 32), ["round 51: agents argue then the", "debate resolves"]),
    (
        ("round 51: the filter keeps only strong matches", 4),
        ["round", "51:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 51: the filter keeps only strong matches", 8),
        ["round", "51: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 51: the filter keeps only strong matches", 12),
        ["round 51:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 51: the filter keeps only strong matches", 16),
        ["round 51: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 51: the filter keeps only strong matches", 24), ["round 51: the filter", "keeps only strong", "matches"]),
    (("round 51: the filter keeps only strong matches", 32), ["round 51: the filter keeps only", "strong matches"]),
    (
        ("round 51: the model answers with a short reply", 4),
        ["round", "51:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 51: the model answers with a short reply", 8),
        ["round", "51: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 51: the model answers with a short reply", 12),
        ["round 51:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 51: the model answers with a short reply", 16),
        ["round 51: the", "model answers", "with a short", "reply"],
    ),
    (("round 51: the model answers with a short reply", 24), ["round 51: the model", "answers with a short", "reply"]),
    (("round 51: the model answers with a short reply", 32), ["round 51: the model answers with", "a short reply"]),
    (
        ("round 51: the recorder stores the reasoning trace", 4),
        ["round", "51:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 51: the recorder stores the reasoning trace", 8),
        ["round", "51: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 51: the recorder stores the reasoning trace", 12),
        ["round 51:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 51: the recorder stores the reasoning trace", 16),
        ["round 51: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 51: the recorder stores the reasoning trace", 24),
        ["round 51: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 51: the recorder stores the reasoning trace", 32),
        ["round 51: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 51: the angel watches the processor run", 4),
        ["round", "51:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 51: the angel watches the processor run", 8),
        ["round", "51: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 51: the angel watches the processor run", 12),
        ["round 51:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 51: the angel watches the processor run", 16), ["round 51: the", "angel watches", "the processor", "run"]),
    (("round 51: the angel watches the processor run", 24), ["round 51: the angel", "watches the processor", "run"]),
    (("round 51: the angel watches the processor run", 32), ["round 51: the angel watches the", "processor run"]),
    (
        ("round 51: angle of the vector decides the match", 4),
        ["round", "51:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 51: angle of the vector decides the match", 8),
        ["round", "51:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 51: angle of the vector decides the match", 12),
        ["round 51:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 51: angle of the vector decides the match", 16),
        ["round 51: angle", "of the vector", "decides the", "match"],
    ),
    (("round 51: angle of the vector decides the match", 24), ["round 51: angle of the", "vector decides the match"]),
    (("round 51: angle of the vector decides the match", 32), ["round 51: angle of the vector", "decides the match"]),
    (
        ("round 51: the candle burns twice as long at night", 4),
        ["round", "51:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 51: the candle burns twice as long at night", 8),
        ["round", "51: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 51: the candle burns twice as long at night", 12),
        ["round 51:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 51: the candle burns twice as long at night", 16),
        ["round 51: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 51: the candle burns twice as long at night", 24),
        ["round 51: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 51: the candle burns twice as long at night", 32),
        ["round 51: the candle burns twice", "as long at night"],
    ),
    (
        ("round 51: a mirror of the universe in one line", 4),
        ["round", "51:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 51: a mirror of the universe in one line", 8),
        ["round", "51: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 51: a mirror of the universe in one line", 12),
        ["round 51: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 51: a mirror of the universe in one line", 16),
        ["round 51: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 51: a mirror of the universe in one line", 24), ["round 51: a mirror of", "the universe in one line"]),
    (("round 51: a mirror of the universe in one line", 32), ["round 51: a mirror of the", "universe in one line"]),
    (
        ("round 51: the queue drains before the storm", 4),
        ["round", "51:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 51: the queue drains before the storm", 8),
        ["round", "51: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 51: the queue drains before the storm", 12), ["round 51:", "the queue", "drains", "before the", "storm"]),
    (("round 51: the queue drains before the storm", 16), ["round 51: the", "queue drains", "before the storm"]),
    (("round 51: the queue drains before the storm", 24), ["round 51: the queue", "drains before the storm"]),
    (("round 51: the queue drains before the storm", 32), ["round 51: the queue drains", "before the storm"]),
    (
        ("kitten51 sitting51 agent51 angle51 universe51 memory51", 6),
        ["kitten51", "sitting51", "agent51", "angle51", "universe51", "memory51"],
    ),
    (
        ("kitten51 sitting51 agent51 angle51 universe51 memory51", 10),
        ["kitten51", "sitting51", "agent51", "angle51", "universe51", "memory51"],
    ),
    (
        ("kitten51 sitting51 agent51 angle51 universe51 memory51", 18),
        ["kitten51 sitting51", "agent51 angle51", "universe51", "memory51"],
    ),
    (
        ("kitten51 sitting51 agent51 angle51 universe51 memory51", 28),
        ["kitten51 sitting51 agent51", "angle51 universe51 memory51"],
    ),
    (
        ("sitting51 agent51 angle51 universe51 memory51 stream51", 6),
        ["sitting51", "agent51", "angle51", "universe51", "memory51", "stream51"],
    ),
    (
        ("sitting51 agent51 angle51 universe51 memory51 stream51", 10),
        ["sitting51", "agent51", "angle51", "universe51", "memory51", "stream51"],
    ),
    (
        ("sitting51 agent51 angle51 universe51 memory51 stream51", 18),
        ["sitting51 agent51", "angle51 universe51", "memory51 stream51"],
    ),
    (
        ("sitting51 agent51 angle51 universe51 memory51 stream51", 28),
        ["sitting51 agent51 angle51", "universe51 memory51 stream51"],
    ),
    (
        ("agent51 angle51 universe51 memory51 stream51 context51", 6),
        ["agent51", "angle51", "universe51", "memory51", "stream51", "context51"],
    ),
    (
        ("agent51 angle51 universe51 memory51 stream51 context51", 10),
        ["agent51", "angle51", "universe51", "memory51", "stream51", "context51"],
    ),
    (
        ("agent51 angle51 universe51 memory51 stream51 context51", 18),
        ["agent51 angle51", "universe51", "memory51 stream51", "context51"],
    ),
    (
        ("agent51 angle51 universe51 memory51 stream51 context51", 28),
        ["agent51 angle51 universe51", "memory51 stream51 context51"],
    ),
    (
        ("angle51 universe51 memory51 stream51 context51 knowledge51", 6),
        ["angle51", "universe51", "memory51", "stream51", "context51", "knowledge51"],
    ),
    (
        ("angle51 universe51 memory51 stream51 context51 knowledge51", 10),
        ["angle51", "universe51", "memory51", "stream51", "context51", "knowledge51"],
    ),
    (
        ("angle51 universe51 memory51 stream51 context51 knowledge51", 18),
        ["angle51 universe51", "memory51 stream51", "context51", "knowledge51"],
    ),
    (
        ("angle51 universe51 memory51 stream51 context51 knowledge51", 28),
        ["angle51 universe51 memory51", "stream51 context51", "knowledge51"],
    ),
    (
        ("universe51 memory51 stream51 context51 knowledge51 vector51", 6),
        ["universe51", "memory51", "stream51", "context51", "knowledge51", "vector51"],
    ),
    (
        ("universe51 memory51 stream51 context51 knowledge51 vector51", 10),
        ["universe51", "memory51", "stream51", "context51", "knowledge51", "vector51"],
    ),
    (
        ("universe51 memory51 stream51 context51 knowledge51 vector51", 18),
        ["universe51", "memory51 stream51", "context51", "knowledge51", "vector51"],
    ),
    (
        ("universe51 memory51 stream51 context51 knowledge51 vector51", 28),
        ["universe51 memory51 stream51", "context51 knowledge51", "vector51"],
    ),
    (
        ("memory51 stream51 context51 knowledge51 vector51 processor51", 6),
        ["memory51", "stream51", "context51", "knowledge51", "vector51", "processor51"],
    ),
    (
        ("memory51 stream51 context51 knowledge51 vector51 processor51", 10),
        ["memory51", "stream51", "context51", "knowledge51", "vector51", "processor51"],
    ),
    (
        ("memory51 stream51 context51 knowledge51 vector51 processor51", 18),
        ["memory51 stream51", "context51", "knowledge51", "vector51", "processor51"],
    ),
    (
        ("memory51 stream51 context51 knowledge51 vector51 processor51", 28),
        ["memory51 stream51 context51", "knowledge51 vector51", "processor51"],
    ),
    (
        ("stream51 context51 knowledge51 vector51 processor51 reasoning51", 6),
        ["stream51", "context51", "knowledge51", "vector51", "processor51", "reasoning51"],
    ),
    (
        ("stream51 context51 knowledge51 vector51 processor51 reasoning51", 10),
        ["stream51", "context51", "knowledge51", "vector51", "processor51", "reasoning51"],
    ),
    (
        ("stream51 context51 knowledge51 vector51 processor51 reasoning51", 18),
        ["stream51 context51", "knowledge51", "vector51", "processor51", "reasoning51"],
    ),
    (
        ("stream51 context51 knowledge51 vector51 processor51 reasoning51", 28),
        ["stream51 context51", "knowledge51 vector51", "processor51 reasoning51"],
    ),
    (
        ("context51 knowledge51 vector51 processor51 reasoning51 machine51", 6),
        ["context51", "knowledge51", "vector51", "processor51", "reasoning51", "machine51"],
    ),
    (
        ("context51 knowledge51 vector51 processor51 reasoning51 machine51", 10),
        ["context51", "knowledge51", "vector51", "processor51", "reasoning51", "machine51"],
    ),
    (
        ("context51 knowledge51 vector51 processor51 reasoning51 machine51", 18),
        ["context51", "knowledge51", "vector51", "processor51", "reasoning51", "machine51"],
    ),
    (
        ("context51 knowledge51 vector51 processor51 reasoning51 machine51", 28),
        ["context51 knowledge51", "vector51 processor51", "reasoning51 machine51"],
    ),
    (
        ("knowledge51 vector51 processor51 reasoning51 machine51 learning51", 6),
        ["knowledge51", "vector51", "processor51", "reasoning51", "machine51", "learning51"],
    ),
    (
        ("knowledge51 vector51 processor51 reasoning51 machine51 learning51", 10),
        ["knowledge51", "vector51", "processor51", "reasoning51", "machine51", "learning51"],
    ),
    (
        ("knowledge51 vector51 processor51 reasoning51 machine51 learning51", 18),
        ["knowledge51", "vector51", "processor51", "reasoning51", "machine51", "learning51"],
    ),
    (
        ("knowledge51 vector51 processor51 reasoning51 machine51 learning51", 28),
        ["knowledge51 vector51", "processor51 reasoning51", "machine51 learning51"],
    ),
    (
        ("vector51 processor51 reasoning51 machine51 learning51 model51", 6),
        ["vector51", "processor51", "reasoning51", "machine51", "learning51", "model51"],
    ),
    (
        ("vector51 processor51 reasoning51 machine51 learning51 model51", 10),
        ["vector51", "processor51", "reasoning51", "machine51", "learning51", "model51"],
    ),
    (
        ("vector51 processor51 reasoning51 machine51 learning51 model51", 18),
        ["vector51", "processor51", "reasoning51", "machine51", "learning51 model51"],
    ),
    (
        ("vector51 processor51 reasoning51 machine51 learning51 model51", 28),
        ["vector51 processor51", "reasoning51 machine51", "learning51 model51"],
    ),
    (
        ("processor51 reasoning51 machine51 learning51 model51 token51", 6),
        ["processor51", "reasoning51", "machine51", "learning51", "model51", "token51"],
    ),
    (
        ("processor51 reasoning51 machine51 learning51 model51 token51", 10),
        ["processor51", "reasoning51", "machine51", "learning51", "model51", "token51"],
    ),
    (
        ("processor51 reasoning51 machine51 learning51 model51 token51", 18),
        ["processor51", "reasoning51", "machine51", "learning51 model51", "token51"],
    ),
    (
        ("processor51 reasoning51 machine51 learning51 model51 token51", 28),
        ["processor51 reasoning51", "machine51 learning51 model51", "token51"],
    ),
    (
        ("reasoning51 machine51 learning51 model51 token51 prompt51", 6),
        ["reasoning51", "machine51", "learning51", "model51", "token51", "prompt51"],
    ),
    (
        ("reasoning51 machine51 learning51 model51 token51 prompt51", 10),
        ["reasoning51", "machine51", "learning51", "model51", "token51", "prompt51"],
    ),
    (
        ("reasoning51 machine51 learning51 model51 token51 prompt51", 18),
        ["reasoning51", "machine51", "learning51 model51", "token51 prompt51"],
    ),
    (
        ("reasoning51 machine51 learning51 model51 token51 prompt51", 28),
        ["reasoning51 machine51", "learning51 model51 token51", "prompt51"],
    ),
    (
        ("machine51 learning51 model51 token51 prompt51 session51", 6),
        ["machine51", "learning51", "model51", "token51", "prompt51", "session51"],
    ),
    (
        ("machine51 learning51 model51 token51 prompt51 session51", 10),
        ["machine51", "learning51", "model51", "token51", "prompt51", "session51"],
    ),
    (
        ("machine51 learning51 model51 token51 prompt51 session51", 18),
        ["machine51", "learning51 model51", "token51 prompt51", "session51"],
    ),
    (
        ("machine51 learning51 model51 token51 prompt51 session51", 28),
        ["machine51 learning51 model51", "token51 prompt51 session51"],
    ),
    (
        ("learning51 model51 token51 prompt51 session51 library51", 6),
        ["learning51", "model51", "token51", "prompt51", "session51", "library51"],
    ),
    (
        ("learning51 model51 token51 prompt51 session51 library51", 10),
        ["learning51", "model51", "token51", "prompt51", "session51", "library51"],
    ),
    (
        ("learning51 model51 token51 prompt51 session51 library51", 18),
        ["learning51 model51", "token51 prompt51", "session51", "library51"],
    ),
    (
        ("learning51 model51 token51 prompt51 session51 library51", 28),
        ["learning51 model51 token51", "prompt51 session51 library51"],
    ),
    (
        ("model51 token51 prompt51 session51 library51 service51", 6),
        ["model51", "token51", "prompt51", "session51", "library51", "service51"],
    ),
    (
        ("model51 token51 prompt51 session51 library51 service51", 10),
        ["model51", "token51", "prompt51", "session51", "library51", "service51"],
    ),
    (
        ("model51 token51 prompt51 session51 library51 service51", 18),
        ["model51 token51", "prompt51 session51", "library51", "service51"],
    ),
    (
        ("model51 token51 prompt51 session51 library51 service51", 28),
        ["model51 token51 prompt51", "session51 library51", "service51"],
    ),
    (
        ("token51 prompt51 session51 library51 service51 gateway51", 6),
        ["token51", "prompt51", "session51", "library51", "service51", "gateway51"],
    ),
    (
        ("token51 prompt51 session51 library51 service51 gateway51", 10),
        ["token51", "prompt51", "session51", "library51", "service51", "gateway51"],
    ),
    (
        ("token51 prompt51 session51 library51 service51 gateway51", 18),
        ["token51 prompt51", "session51", "library51", "service51", "gateway51"],
    ),
    (
        ("token51 prompt51 session51 library51 service51 gateway51", 28),
        ["token51 prompt51 session51", "library51 service51", "gateway51"],
    ),
    (
        ("prompt51 session51 library51 service51 gateway51 storage51", 6),
        ["prompt51", "session51", "library51", "service51", "gateway51", "storage51"],
    ),
    (
        ("prompt51 session51 library51 service51 gateway51 storage51", 10),
        ["prompt51", "session51", "library51", "service51", "gateway51", "storage51"],
    ),
    (
        ("prompt51 session51 library51 service51 gateway51 storage51", 18),
        ["prompt51 session51", "library51", "service51", "gateway51", "storage51"],
    ),
    (
        ("prompt51 session51 library51 service51 gateway51 storage51", 28),
        ["prompt51 session51 library51", "service51 gateway51", "storage51"],
    ),
    (
        ("session51 library51 service51 gateway51 storage51 network51", 6),
        ["session51", "library51", "service51", "gateway51", "storage51", "network51"],
    ),
    (
        ("session51 library51 service51 gateway51 storage51 network51", 10),
        ["session51", "library51", "service51", "gateway51", "storage51", "network51"],
    ),
    (
        ("session51 library51 service51 gateway51 storage51 network51", 18),
        ["session51", "library51", "service51", "gateway51", "storage51", "network51"],
    ),
    (
        ("session51 library51 service51 gateway51 storage51 network51", 28),
        ["session51 library51", "service51 gateway51", "storage51 network51"],
    ),
    (
        ("library51 service51 gateway51 storage51 network51 latency51", 6),
        ["library51", "service51", "gateway51", "storage51", "network51", "latency51"],
    ),
    (
        ("library51 service51 gateway51 storage51 network51 latency51", 10),
        ["library51", "service51", "gateway51", "storage51", "network51", "latency51"],
    ),
    (
        ("library51 service51 gateway51 storage51 network51 latency51", 18),
        ["library51", "service51", "gateway51", "storage51", "network51", "latency51"],
    ),
    (
        ("library51 service51 gateway51 storage51 network51 latency51", 28),
        ["library51 service51", "gateway51 storage51", "network51 latency51"],
    ),
    (
        ("service51 gateway51 storage51 network51 latency51 buffer51", 6),
        ["service51", "gateway51", "storage51", "network51", "latency51", "buffer51"],
    ),
    (
        ("service51 gateway51 storage51 network51 latency51 buffer51", 10),
        ["service51", "gateway51", "storage51", "network51", "latency51", "buffer51"],
    ),
    (
        ("service51 gateway51 storage51 network51 latency51 buffer51", 18),
        ["service51", "gateway51", "storage51", "network51", "latency51 buffer51"],
    ),
    (
        ("service51 gateway51 storage51 network51 latency51 buffer51", 28),
        ["service51 gateway51", "storage51 network51", "latency51 buffer51"],
    ),
    (
        ("gateway51 storage51 network51 latency51 buffer51 queue51", 6),
        ["gateway51", "storage51", "network51", "latency51", "buffer51", "queue51"],
    ),
    (
        ("gateway51 storage51 network51 latency51 buffer51 queue51", 10),
        ["gateway51", "storage51", "network51", "latency51", "buffer51", "queue51"],
    ),
    (
        ("gateway51 storage51 network51 latency51 buffer51 queue51", 18),
        ["gateway51", "storage51", "network51", "latency51 buffer51", "queue51"],
    ),
    (
        ("gateway51 storage51 network51 latency51 buffer51 queue51", 28),
        ["gateway51 storage51", "network51 latency51 buffer51", "queue51"],
    ),
    (
        ("storage51 network51 latency51 buffer51 queue51 worker51", 6),
        ["storage51", "network51", "latency51", "buffer51", "queue51", "worker51"],
    ),
    (
        ("storage51 network51 latency51 buffer51 queue51 worker51", 10),
        ["storage51", "network51", "latency51", "buffer51", "queue51", "worker51"],
    ),
    (
        ("storage51 network51 latency51 buffer51 queue51 worker51", 18),
        ["storage51", "network51", "latency51 buffer51", "queue51 worker51"],
    ),
    (
        ("storage51 network51 latency51 buffer51 queue51 worker51", 28),
        ["storage51 network51", "latency51 buffer51 queue51", "worker51"],
    ),
    (
        ("network51 latency51 buffer51 queue51 worker51 kernel51", 6),
        ["network51", "latency51", "buffer51", "queue51", "worker51", "kernel51"],
    ),
    (
        ("network51 latency51 buffer51 queue51 worker51 kernel51", 10),
        ["network51", "latency51", "buffer51", "queue51", "worker51", "kernel51"],
    ),
    (
        ("network51 latency51 buffer51 queue51 worker51 kernel51", 18),
        ["network51", "latency51 buffer51", "queue51 worker51", "kernel51"],
    ),
    (
        ("network51 latency51 buffer51 queue51 worker51 kernel51", 28),
        ["network51 latency51 buffer51", "queue51 worker51 kernel51"],
    ),
    (
        ("latency51 buffer51 queue51 worker51 kernel51 signal51", 6),
        ["latency51", "buffer51", "queue51", "worker51", "kernel51", "signal51"],
    ),
    (
        ("latency51 buffer51 queue51 worker51 kernel51 signal51", 10),
        ["latency51", "buffer51", "queue51", "worker51", "kernel51", "signal51"],
    ),
    (
        ("latency51 buffer51 queue51 worker51 kernel51 signal51", 18),
        ["latency51 buffer51", "queue51 worker51", "kernel51 signal51"],
    ),
    (
        ("latency51 buffer51 queue51 worker51 kernel51 signal51", 28),
        ["latency51 buffer51 queue51", "worker51 kernel51 signal51"],
    ),
    (
        ("buffer51 queue51 worker51 kernel51 signal51 packet51", 6),
        ["buffer51", "queue51", "worker51", "kernel51", "signal51", "packet51"],
    ),
    (
        ("buffer51 queue51 worker51 kernel51 signal51 packet51", 10),
        ["buffer51", "queue51", "worker51", "kernel51", "signal51", "packet51"],
    ),
    (
        ("buffer51 queue51 worker51 kernel51 signal51 packet51", 18),
        ["buffer51 queue51", "worker51 kernel51", "signal51 packet51"],
    ),
    (
        ("buffer51 queue51 worker51 kernel51 signal51 packet51", 28),
        ["buffer51 queue51 worker51", "kernel51 signal51 packet51"],
    ),
    (
        ("queue51 worker51 kernel51 signal51 packet51 router51", 6),
        ["queue51", "worker51", "kernel51", "signal51", "packet51", "router51"],
    ),
    (
        ("queue51 worker51 kernel51 signal51 packet51 router51", 10),
        ["queue51", "worker51", "kernel51", "signal51", "packet51", "router51"],
    ),
    (
        ("queue51 worker51 kernel51 signal51 packet51 router51", 18),
        ["queue51 worker51", "kernel51 signal51", "packet51 router51"],
    ),
    (
        ("queue51 worker51 kernel51 signal51 packet51 router51", 28),
        ["queue51 worker51 kernel51", "signal51 packet51 router51"],
    ),
    (
        ("worker51 kernel51 signal51 packet51 router51 cluster51", 6),
        ["worker51", "kernel51", "signal51", "packet51", "router51", "cluster51"],
    ),
    (
        ("worker51 kernel51 signal51 packet51 router51 cluster51", 10),
        ["worker51", "kernel51", "signal51", "packet51", "router51", "cluster51"],
    ),
    (
        ("worker51 kernel51 signal51 packet51 router51 cluster51", 18),
        ["worker51 kernel51", "signal51 packet51", "router51 cluster51"],
    ),
    (
        ("worker51 kernel51 signal51 packet51 router51 cluster51", 28),
        ["worker51 kernel51 signal51", "packet51 router51 cluster51"],
    ),
    (
        ("kernel51 signal51 packet51 router51 cluster51 mirror51", 6),
        ["kernel51", "signal51", "packet51", "router51", "cluster51", "mirror51"],
    ),
    (
        ("kernel51 signal51 packet51 router51 cluster51 mirror51", 10),
        ["kernel51", "signal51", "packet51", "router51", "cluster51", "mirror51"],
    ),
    (
        ("kernel51 signal51 packet51 router51 cluster51 mirror51", 18),
        ["kernel51 signal51", "packet51 router51", "cluster51 mirror51"],
    ),
    (
        ("kernel51 signal51 packet51 router51 cluster51 mirror51", 28),
        ["kernel51 signal51 packet51", "router51 cluster51 mirror51"],
    ),
    (
        ("signal51 packet51 router51 cluster51 mirror51 filter51", 6),
        ["signal51", "packet51", "router51", "cluster51", "mirror51", "filter51"],
    ),
    (
        ("signal51 packet51 router51 cluster51 mirror51 filter51", 10),
        ["signal51", "packet51", "router51", "cluster51", "mirror51", "filter51"],
    ),
    (
        ("signal51 packet51 router51 cluster51 mirror51 filter51", 18),
        ["signal51 packet51", "router51 cluster51", "mirror51 filter51"],
    ),
    (
        ("signal51 packet51 router51 cluster51 mirror51 filter51", 28),
        ["signal51 packet51 router51", "cluster51 mirror51 filter51"],
    ),
    (
        ("packet51 router51 cluster51 mirror51 filter51 ranking51", 6),
        ["packet51", "router51", "cluster51", "mirror51", "filter51", "ranking51"],
    ),
    (
        ("packet51 router51 cluster51 mirror51 filter51 ranking51", 10),
        ["packet51", "router51", "cluster51", "mirror51", "filter51", "ranking51"],
    ),
    (
        ("packet51 router51 cluster51 mirror51 filter51 ranking51", 18),
        ["packet51 router51", "cluster51 mirror51", "filter51 ranking51"],
    ),
    (
        ("packet51 router51 cluster51 mirror51 filter51 ranking51", 28),
        ["packet51 router51 cluster51", "mirror51 filter51 ranking51"],
    ),
    (
        ("router51 cluster51 mirror51 filter51 ranking51 encoding51", 6),
        ["router51", "cluster51", "mirror51", "filter51", "ranking51", "encoding51"],
    ),
    (
        ("router51 cluster51 mirror51 filter51 ranking51 encoding51", 10),
        ["router51", "cluster51", "mirror51", "filter51", "ranking51", "encoding51"],
    ),
    (
        ("router51 cluster51 mirror51 filter51 ranking51 encoding51", 18),
        ["router51 cluster51", "mirror51 filter51", "ranking51", "encoding51"],
    ),
    (
        ("router51 cluster51 mirror51 filter51 ranking51 encoding51", 28),
        ["router51 cluster51 mirror51", "filter51 ranking51", "encoding51"],
    ),
    (
        ("cluster51 mirror51 filter51 ranking51 encoding51 mapping51", 6),
        ["cluster51", "mirror51", "filter51", "ranking51", "encoding51", "mapping51"],
    ),
    (
        ("cluster51 mirror51 filter51 ranking51 encoding51 mapping51", 10),
        ["cluster51", "mirror51", "filter51", "ranking51", "encoding51", "mapping51"],
    ),
    (
        ("cluster51 mirror51 filter51 ranking51 encoding51 mapping51", 18),
        ["cluster51 mirror51", "filter51 ranking51", "encoding51", "mapping51"],
    ),
    (
        ("cluster51 mirror51 filter51 ranking51 encoding51 mapping51", 28),
        ["cluster51 mirror51 filter51", "ranking51 encoding51", "mapping51"],
    ),
    (
        ("mirror51 filter51 ranking51 encoding51 mapping51 record51", 6),
        ["mirror51", "filter51", "ranking51", "encoding51", "mapping51", "record51"],
    ),
    (
        ("mirror51 filter51 ranking51 encoding51 mapping51 record51", 10),
        ["mirror51", "filter51", "ranking51", "encoding51", "mapping51", "record51"],
    ),
    (
        ("mirror51 filter51 ranking51 encoding51 mapping51 record51", 18),
        ["mirror51 filter51", "ranking51", "encoding51", "mapping51 record51"],
    ),
    (
        ("mirror51 filter51 ranking51 encoding51 mapping51 record51", 28),
        ["mirror51 filter51 ranking51", "encoding51 mapping51", "record51"],
    ),
    (
        ("filter51 ranking51 encoding51 mapping51 record51 candle51", 6),
        ["filter51", "ranking51", "encoding51", "mapping51", "record51", "candle51"],
    ),
    (
        ("filter51 ranking51 encoding51 mapping51 record51 candle51", 10),
        ["filter51", "ranking51", "encoding51", "mapping51", "record51", "candle51"],
    ),
    (
        ("filter51 ranking51 encoding51 mapping51 record51 candle51", 18),
        ["filter51 ranking51", "encoding51", "mapping51 record51", "candle51"],
    ),
    (
        ("filter51 ranking51 encoding51 mapping51 record51 candle51", 28),
        ["filter51 ranking51", "encoding51 mapping51", "record51 candle51"],
    ),
    (
        ("ranking51 encoding51 mapping51 record51 candle51 thread51", 6),
        ["ranking51", "encoding51", "mapping51", "record51", "candle51", "thread51"],
    ),
    (
        ("ranking51 encoding51 mapping51 record51 candle51 thread51", 10),
        ["ranking51", "encoding51", "mapping51", "record51", "candle51", "thread51"],
    ),
    (
        ("ranking51 encoding51 mapping51 record51 candle51 thread51", 18),
        ["ranking51", "encoding51", "mapping51 record51", "candle51 thread51"],
    ),
    (
        ("ranking51 encoding51 mapping51 record51 candle51 thread51", 28),
        ["ranking51 encoding51", "mapping51 record51 candle51", "thread51"],
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
