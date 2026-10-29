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
        ("round 145: the quick brown fox jumps over the lazy dog", 4),
        ["round", "145:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", 8),
        ["round", "145: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", 12),
        ["round 145:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", 16),
        ["round 145: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", 24),
        ["round 145: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 145: the quick brown fox jumps over the lazy dog", 32),
        ["round 145: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", 4),
        ["round", "145:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", 8),
        ["round", "145:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", 12),
        ["round 145:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", 16),
        ["round 145:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", 24),
        ["round 145: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 145: agentuniverse is a framework for multi agents", 32),
        ["round 145: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", 4),
        ["round", "145:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", 8),
        ["round", "145:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", 12),
        ["round 145:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", 16),
        ["round 145:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", 24),
        ["round 145: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 145: knowledge stored as vectors enables retrieval", 32),
        ["round 145: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 145: the processor reads the record then stops", 4),
        ["round", "145:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 145: the processor reads the record then stops", 8),
        ["round", "145: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 145: the processor reads the record then stops", 12),
        ["round 145:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 145: the processor reads the record then stops", 16),
        ["round 145: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 145: the processor reads the record then stops", 24),
        ["round 145: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 145: the processor reads the record then stops", 32),
        ["round 145: the processor reads", "the record then stops"],
    ),
    (
        ("round 145: a worker pulls the next task from the queue", 4),
        ["round", "145:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 145: a worker pulls the next task from the queue", 8),
        ["round", "145: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 145: a worker pulls the next task from the queue", 12),
        ["round 145: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 145: a worker pulls the next task from the queue", 16),
        ["round 145: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 145: a worker pulls the next task from the queue", 24),
        ["round 145: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 145: a worker pulls the next task from the queue", 32),
        ["round 145: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 145: signals travel through the network layer", 4),
        ["round", "145:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 145: signals travel through the network layer", 8),
        ["round", "145:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 145: signals travel through the network layer", 12),
        ["round 145:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 145: signals travel through the network layer", 16),
        ["round 145:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 145: signals travel through the network layer", 24),
        ["round 145: signals", "travel through the", "network layer"],
    ),
    (
        ("round 145: signals travel through the network layer", 32),
        ["round 145: signals travel", "through the network layer"],
    ),
    (
        ("round 145: the gateway routes each request by policy", 4),
        ["round", "145:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 145: the gateway routes each request by policy", 8),
        ["round", "145: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 145: the gateway routes each request by policy", 12),
        ["round 145:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 145: the gateway routes each request by policy", 16),
        ["round 145: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 145: the gateway routes each request by policy", 24),
        ["round 145: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 145: the gateway routes each request by policy", 32),
        ["round 145: the gateway routes", "each request by policy"],
    ),
    (
        ("round 145: memory grows until the buffer is full", 4),
        ["round", "145:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 145: memory grows until the buffer is full", 8),
        ["round", "145:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 145: memory grows until the buffer is full", 12),
        ["round 145:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 145: memory grows until the buffer is full", 16),
        ["round 145:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 145: memory grows until the buffer is full", 24), ["round 145: memory grows", "until the buffer is full"]),
    (("round 145: memory grows until the buffer is full", 32), ["round 145: memory grows until", "the buffer is full"]),
    (
        ("round 145: the cluster mirrors every packet twice", 4),
        ["round", "145:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 145: the cluster mirrors every packet twice", 8),
        ["round", "145: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 145: the cluster mirrors every packet twice", 12),
        ["round 145:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 145: the cluster mirrors every packet twice", 16),
        ["round 145: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 145: the cluster mirrors every packet twice", 24),
        ["round 145: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 145: the cluster mirrors every packet twice", 32),
        ["round 145: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", 4),
        ["round", "145:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", 8),
        ["round", "145:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", 12),
        ["round 145:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", 16),
        ["round 145:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", 24),
        ["round 145: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 145: ranking uses tokens learned from the corpus", 32),
        ["round 145: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 145: a long session ends when the candle dies", 4),
        ["round", "145:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 145: a long session ends when the candle dies", 8),
        ["round", "145: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 145: a long session ends when the candle dies", 12),
        ["round 145: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 145: a long session ends when the candle dies", 16),
        ["round 145: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 145: a long session ends when the candle dies", 24),
        ["round 145: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 145: a long session ends when the candle dies", 32),
        ["round 145: a long session ends", "when the candle dies"],
    ),
    (
        ("round 145: encode the prompt then map the result", 4),
        ["round", "145:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 145: encode the prompt then map the result", 8),
        ["round", "145:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 145: encode the prompt then map the result", 12),
        ["round 145:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 145: encode the prompt then map the result", 16),
        ["round 145:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 145: encode the prompt then map the result", 24),
        ["round 145: encode the", "prompt then map the", "result"],
    ),
    (("round 145: encode the prompt then map the result", 32), ["round 145: encode the prompt", "then map the result"]),
    (
        ("round 145: the kernel wakes the worker at dawn", 4),
        ["round", "145:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 145: the kernel wakes the worker at dawn", 8),
        ["round", "145: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 145: the kernel wakes the worker at dawn", 12),
        ["round 145:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 145: the kernel wakes the worker at dawn", 16), ["round 145: the", "kernel wakes the", "worker at dawn"]),
    (("round 145: the kernel wakes the worker at dawn", 24), ["round 145: the kernel", "wakes the worker at dawn"]),
    (("round 145: the kernel wakes the worker at dawn", 32), ["round 145: the kernel wakes the", "worker at dawn"]),
    (
        ("round 145: service latency drops after the patch", 4),
        ["round", "145:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 145: service latency drops after the patch", 8),
        ["round", "145:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 145: service latency drops after the patch", 12),
        ["round 145:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 145: service latency drops after the patch", 16),
        ["round 145:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 145: service latency drops after the patch", 24),
        ["round 145: service", "latency drops after the", "patch"],
    ),
    (("round 145: service latency drops after the patch", 32), ["round 145: service latency drops", "after the patch"]),
    (
        ("round 145: the library caches every vector it sees", 4),
        ["round", "145:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 145: the library caches every vector it sees", 8),
        ["round", "145: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 145: the library caches every vector it sees", 12),
        ["round 145:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 145: the library caches every vector it sees", 16),
        ["round 145: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 145: the library caches every vector it sees", 24),
        ["round 145: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 145: the library caches every vector it sees", 32),
        ["round 145: the library caches", "every vector it sees"],
    ),
    (
        ("round 145: agents argue then the debate resolves", 4),
        ["round", "145:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 145: agents argue then the debate resolves", 8),
        ["round", "145:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 145: agents argue then the debate resolves", 12),
        ["round 145:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 145: agents argue then the debate resolves", 16),
        ["round 145:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 145: agents argue then the debate resolves", 24), ["round 145: agents argue", "then the debate resolves"]),
    (("round 145: agents argue then the debate resolves", 32), ["round 145: agents argue then the", "debate resolves"]),
    (
        ("round 145: the filter keeps only strong matches", 4),
        ["round", "145:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 145: the filter keeps only strong matches", 8),
        ["round", "145: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 145: the filter keeps only strong matches", 12),
        ["round 145:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 145: the filter keeps only strong matches", 16),
        ["round 145: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 145: the filter keeps only strong matches", 24),
        ["round 145: the filter", "keeps only strong", "matches"],
    ),
    (("round 145: the filter keeps only strong matches", 32), ["round 145: the filter keeps only", "strong matches"]),
    (
        ("round 145: the model answers with a short reply", 4),
        ["round", "145:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 145: the model answers with a short reply", 8),
        ["round", "145: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 145: the model answers with a short reply", 12),
        ["round 145:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 145: the model answers with a short reply", 16),
        ["round 145: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 145: the model answers with a short reply", 24),
        ["round 145: the model", "answers with a short", "reply"],
    ),
    (("round 145: the model answers with a short reply", 32), ["round 145: the model answers", "with a short reply"]),
    (
        ("round 145: the recorder stores the reasoning trace", 4),
        ["round", "145:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 145: the recorder stores the reasoning trace", 8),
        ["round", "145: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 145: the recorder stores the reasoning trace", 12),
        ["round 145:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 145: the recorder stores the reasoning trace", 16),
        ["round 145: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 145: the recorder stores the reasoning trace", 24),
        ["round 145: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 145: the recorder stores the reasoning trace", 32),
        ["round 145: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 145: the angel watches the processor run", 4),
        ["round", "145:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 145: the angel watches the processor run", 8),
        ["round", "145: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 145: the angel watches the processor run", 12),
        ["round 145:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 145: the angel watches the processor run", 16),
        ["round 145: the", "angel watches", "the processor", "run"],
    ),
    (("round 145: the angel watches the processor run", 24), ["round 145: the angel", "watches the processor", "run"]),
    (("round 145: the angel watches the processor run", 32), ["round 145: the angel watches the", "processor run"]),
    (
        ("round 145: angle of the vector decides the match", 4),
        ["round", "145:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 145: angle of the vector decides the match", 8),
        ["round", "145:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 145: angle of the vector decides the match", 12),
        ["round 145:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 145: angle of the vector decides the match", 16),
        ["round 145: angle", "of the vector", "decides the", "match"],
    ),
    (("round 145: angle of the vector decides the match", 24), ["round 145: angle of the", "vector decides the match"]),
    (("round 145: angle of the vector decides the match", 32), ["round 145: angle of the vector", "decides the match"]),
    (
        ("round 145: the candle burns twice as long at night", 4),
        ["round", "145:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 145: the candle burns twice as long at night", 8),
        ["round", "145: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 145: the candle burns twice as long at night", 12),
        ["round 145:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 145: the candle burns twice as long at night", 16),
        ["round 145: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 145: the candle burns twice as long at night", 24),
        ["round 145: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 145: the candle burns twice as long at night", 32),
        ["round 145: the candle burns", "twice as long at night"],
    ),
    (
        ("round 145: a mirror of the universe in one line", 4),
        ["round", "145:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 145: a mirror of the universe in one line", 8),
        ["round", "145: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 145: a mirror of the universe in one line", 12),
        ["round 145: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 145: a mirror of the universe in one line", 16),
        ["round 145: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 145: a mirror of the universe in one line", 24), ["round 145: a mirror of", "the universe in one line"]),
    (("round 145: a mirror of the universe in one line", 32), ["round 145: a mirror of the", "universe in one line"]),
    (
        ("round 145: the queue drains before the storm", 4),
        ["round", "145:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 145: the queue drains before the storm", 8),
        ["round", "145: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 145: the queue drains before the storm", 12),
        ["round 145:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 145: the queue drains before the storm", 16), ["round 145: the", "queue drains", "before the storm"]),
    (("round 145: the queue drains before the storm", 24), ["round 145: the queue", "drains before the storm"]),
    (("round 145: the queue drains before the storm", 32), ["round 145: the queue drains", "before the storm"]),
    (
        ("kitten145 sitting145 agent145 angle145 universe145 memory145", 6),
        ["kitten145", "sitting145", "agent145", "angle145", "universe145", "memory145"],
    ),
    (
        ("kitten145 sitting145 agent145 angle145 universe145 memory145", 10),
        ["kitten145", "sitting145", "agent145", "angle145", "universe145", "memory145"],
    ),
    (
        ("kitten145 sitting145 agent145 angle145 universe145 memory145", 18),
        ["kitten145", "sitting145", "agent145 angle145", "universe145", "memory145"],
    ),
    (
        ("kitten145 sitting145 agent145 angle145 universe145 memory145", 28),
        ["kitten145 sitting145", "agent145 angle145", "universe145 memory145"],
    ),
    (
        ("sitting145 agent145 angle145 universe145 memory145 stream145", 6),
        ["sitting145", "agent145", "angle145", "universe145", "memory145", "stream145"],
    ),
    (
        ("sitting145 agent145 angle145 universe145 memory145 stream145", 10),
        ["sitting145", "agent145", "angle145", "universe145", "memory145", "stream145"],
    ),
    (
        ("sitting145 agent145 angle145 universe145 memory145 stream145", 18),
        ["sitting145", "agent145 angle145", "universe145", "memory145", "stream145"],
    ),
    (
        ("sitting145 agent145 angle145 universe145 memory145 stream145", 28),
        ["sitting145 agent145 angle145", "universe145 memory145", "stream145"],
    ),
    (
        ("agent145 angle145 universe145 memory145 stream145 context145", 6),
        ["agent145", "angle145", "universe145", "memory145", "stream145", "context145"],
    ),
    (
        ("agent145 angle145 universe145 memory145 stream145 context145", 10),
        ["agent145", "angle145", "universe145", "memory145", "stream145", "context145"],
    ),
    (
        ("agent145 angle145 universe145 memory145 stream145 context145", 18),
        ["agent145 angle145", "universe145", "memory145", "stream145", "context145"],
    ),
    (
        ("agent145 angle145 universe145 memory145 stream145 context145", 28),
        ["agent145 angle145", "universe145 memory145", "stream145 context145"],
    ),
    (
        ("angle145 universe145 memory145 stream145 context145 knowledge145", 6),
        ["angle145", "universe145", "memory145", "stream145", "context145", "knowledge145"],
    ),
    (
        ("angle145 universe145 memory145 stream145 context145 knowledge145", 10),
        ["angle145", "universe145", "memory145", "stream145", "context145", "knowledge145"],
    ),
    (
        ("angle145 universe145 memory145 stream145 context145 knowledge145", 18),
        ["angle145", "universe145", "memory145", "stream145", "context145", "knowledge145"],
    ),
    (
        ("angle145 universe145 memory145 stream145 context145 knowledge145", 28),
        ["angle145 universe145", "memory145 stream145", "context145 knowledge145"],
    ),
    (
        ("universe145 memory145 stream145 context145 knowledge145 vector145", 6),
        ["universe145", "memory145", "stream145", "context145", "knowledge145", "vector145"],
    ),
    (
        ("universe145 memory145 stream145 context145 knowledge145 vector145", 10),
        ["universe145", "memory145", "stream145", "context145", "knowledge145", "vector145"],
    ),
    (
        ("universe145 memory145 stream145 context145 knowledge145 vector145", 18),
        ["universe145", "memory145", "stream145", "context145", "knowledge145", "vector145"],
    ),
    (
        ("universe145 memory145 stream145 context145 knowledge145 vector145", 28),
        ["universe145 memory145", "stream145 context145", "knowledge145 vector145"],
    ),
    (
        ("memory145 stream145 context145 knowledge145 vector145 processor145", 6),
        ["memory145", "stream145", "context145", "knowledge145", "vector145", "processor145"],
    ),
    (
        ("memory145 stream145 context145 knowledge145 vector145 processor145", 10),
        ["memory145", "stream145", "context145", "knowledge145", "vector145", "processor145"],
    ),
    (
        ("memory145 stream145 context145 knowledge145 vector145 processor145", 18),
        ["memory145", "stream145", "context145", "knowledge145", "vector145", "processor145"],
    ),
    (
        ("memory145 stream145 context145 knowledge145 vector145 processor145", 28),
        ["memory145 stream145", "context145 knowledge145", "vector145 processor145"],
    ),
    (
        ("stream145 context145 knowledge145 vector145 processor145 reasoning145", 6),
        ["stream145", "context145", "knowledge145", "vector145", "processor145", "reasoning145"],
    ),
    (
        ("stream145 context145 knowledge145 vector145 processor145 reasoning145", 10),
        ["stream145", "context145", "knowledge145", "vector145", "processor145", "reasoning145"],
    ),
    (
        ("stream145 context145 knowledge145 vector145 processor145 reasoning145", 18),
        ["stream145", "context145", "knowledge145", "vector145", "processor145", "reasoning145"],
    ),
    (
        ("stream145 context145 knowledge145 vector145 processor145 reasoning145", 28),
        ["stream145 context145", "knowledge145 vector145", "processor145 reasoning145"],
    ),
    (
        ("context145 knowledge145 vector145 processor145 reasoning145 machine145", 6),
        ["context145", "knowledge145", "vector145", "processor145", "reasoning145", "machine145"],
    ),
    (
        ("context145 knowledge145 vector145 processor145 reasoning145 machine145", 10),
        ["context145", "knowledge145", "vector145", "processor145", "reasoning145", "machine145"],
    ),
    (
        ("context145 knowledge145 vector145 processor145 reasoning145 machine145", 18),
        ["context145", "knowledge145", "vector145", "processor145", "reasoning145", "machine145"],
    ),
    (
        ("context145 knowledge145 vector145 processor145 reasoning145 machine145", 28),
        ["context145 knowledge145", "vector145 processor145", "reasoning145 machine145"],
    ),
    (
        ("knowledge145 vector145 processor145 reasoning145 machine145 learning145", 6),
        ["knowledge145", "vector145", "processor145", "reasoning145", "machine145", "learning145"],
    ),
    (
        ("knowledge145 vector145 processor145 reasoning145 machine145 learning145", 10),
        ["knowledge145", "vector145", "processor145", "reasoning145", "machine145", "learning145"],
    ),
    (
        ("knowledge145 vector145 processor145 reasoning145 machine145 learning145", 18),
        ["knowledge145", "vector145", "processor145", "reasoning145", "machine145", "learning145"],
    ),
    (
        ("knowledge145 vector145 processor145 reasoning145 machine145 learning145", 28),
        ["knowledge145 vector145", "processor145 reasoning145", "machine145 learning145"],
    ),
    (
        ("vector145 processor145 reasoning145 machine145 learning145 model145", 6),
        ["vector145", "processor145", "reasoning145", "machine145", "learning145", "model145"],
    ),
    (
        ("vector145 processor145 reasoning145 machine145 learning145 model145", 10),
        ["vector145", "processor145", "reasoning145", "machine145", "learning145", "model145"],
    ),
    (
        ("vector145 processor145 reasoning145 machine145 learning145 model145", 18),
        ["vector145", "processor145", "reasoning145", "machine145", "learning145", "model145"],
    ),
    (
        ("vector145 processor145 reasoning145 machine145 learning145 model145", 28),
        ["vector145 processor145", "reasoning145 machine145", "learning145 model145"],
    ),
    (
        ("processor145 reasoning145 machine145 learning145 model145 token145", 6),
        ["processor145", "reasoning145", "machine145", "learning145", "model145", "token145"],
    ),
    (
        ("processor145 reasoning145 machine145 learning145 model145 token145", 10),
        ["processor145", "reasoning145", "machine145", "learning145", "model145", "token145"],
    ),
    (
        ("processor145 reasoning145 machine145 learning145 model145 token145", 18),
        ["processor145", "reasoning145", "machine145", "learning145", "model145 token145"],
    ),
    (
        ("processor145 reasoning145 machine145 learning145 model145 token145", 28),
        ["processor145 reasoning145", "machine145 learning145", "model145 token145"],
    ),
    (
        ("reasoning145 machine145 learning145 model145 token145 prompt145", 6),
        ["reasoning145", "machine145", "learning145", "model145", "token145", "prompt145"],
    ),
    (
        ("reasoning145 machine145 learning145 model145 token145 prompt145", 10),
        ["reasoning145", "machine145", "learning145", "model145", "token145", "prompt145"],
    ),
    (
        ("reasoning145 machine145 learning145 model145 token145 prompt145", 18),
        ["reasoning145", "machine145", "learning145", "model145 token145", "prompt145"],
    ),
    (
        ("reasoning145 machine145 learning145 model145 token145 prompt145", 28),
        ["reasoning145 machine145", "learning145 model145", "token145 prompt145"],
    ),
    (
        ("machine145 learning145 model145 token145 prompt145 session145", 6),
        ["machine145", "learning145", "model145", "token145", "prompt145", "session145"],
    ),
    (
        ("machine145 learning145 model145 token145 prompt145 session145", 10),
        ["machine145", "learning145", "model145", "token145", "prompt145", "session145"],
    ),
    (
        ("machine145 learning145 model145 token145 prompt145 session145", 18),
        ["machine145", "learning145", "model145 token145", "prompt145", "session145"],
    ),
    (
        ("machine145 learning145 model145 token145 prompt145 session145", 28),
        ["machine145 learning145", "model145 token145 prompt145", "session145"],
    ),
    (
        ("learning145 model145 token145 prompt145 session145 library145", 6),
        ["learning145", "model145", "token145", "prompt145", "session145", "library145"],
    ),
    (
        ("learning145 model145 token145 prompt145 session145 library145", 10),
        ["learning145", "model145", "token145", "prompt145", "session145", "library145"],
    ),
    (
        ("learning145 model145 token145 prompt145 session145 library145", 18),
        ["learning145", "model145 token145", "prompt145", "session145", "library145"],
    ),
    (
        ("learning145 model145 token145 prompt145 session145 library145", 28),
        ["learning145 model145", "token145 prompt145", "session145 library145"],
    ),
    (
        ("model145 token145 prompt145 session145 library145 service145", 6),
        ["model145", "token145", "prompt145", "session145", "library145", "service145"],
    ),
    (
        ("model145 token145 prompt145 session145 library145 service145", 10),
        ["model145", "token145", "prompt145", "session145", "library145", "service145"],
    ),
    (
        ("model145 token145 prompt145 session145 library145 service145", 18),
        ["model145 token145", "prompt145", "session145", "library145", "service145"],
    ),
    (
        ("model145 token145 prompt145 session145 library145 service145", 28),
        ["model145 token145 prompt145", "session145 library145", "service145"],
    ),
    (
        ("token145 prompt145 session145 library145 service145 gateway145", 6),
        ["token145", "prompt145", "session145", "library145", "service145", "gateway145"],
    ),
    (
        ("token145 prompt145 session145 library145 service145 gateway145", 10),
        ["token145", "prompt145", "session145", "library145", "service145", "gateway145"],
    ),
    (
        ("token145 prompt145 session145 library145 service145 gateway145", 18),
        ["token145 prompt145", "session145", "library145", "service145", "gateway145"],
    ),
    (
        ("token145 prompt145 session145 library145 service145 gateway145", 28),
        ["token145 prompt145", "session145 library145", "service145 gateway145"],
    ),
    (
        ("prompt145 session145 library145 service145 gateway145 storage145", 6),
        ["prompt145", "session145", "library145", "service145", "gateway145", "storage145"],
    ),
    (
        ("prompt145 session145 library145 service145 gateway145 storage145", 10),
        ["prompt145", "session145", "library145", "service145", "gateway145", "storage145"],
    ),
    (
        ("prompt145 session145 library145 service145 gateway145 storage145", 18),
        ["prompt145", "session145", "library145", "service145", "gateway145", "storage145"],
    ),
    (
        ("prompt145 session145 library145 service145 gateway145 storage145", 28),
        ["prompt145 session145", "library145 service145", "gateway145 storage145"],
    ),
    (
        ("session145 library145 service145 gateway145 storage145 network145", 6),
        ["session145", "library145", "service145", "gateway145", "storage145", "network145"],
    ),
    (
        ("session145 library145 service145 gateway145 storage145 network145", 10),
        ["session145", "library145", "service145", "gateway145", "storage145", "network145"],
    ),
    (
        ("session145 library145 service145 gateway145 storage145 network145", 18),
        ["session145", "library145", "service145", "gateway145", "storage145", "network145"],
    ),
    (
        ("session145 library145 service145 gateway145 storage145 network145", 28),
        ["session145 library145", "service145 gateway145", "storage145 network145"],
    ),
    (
        ("library145 service145 gateway145 storage145 network145 latency145", 6),
        ["library145", "service145", "gateway145", "storage145", "network145", "latency145"],
    ),
    (
        ("library145 service145 gateway145 storage145 network145 latency145", 10),
        ["library145", "service145", "gateway145", "storage145", "network145", "latency145"],
    ),
    (
        ("library145 service145 gateway145 storage145 network145 latency145", 18),
        ["library145", "service145", "gateway145", "storage145", "network145", "latency145"],
    ),
    (
        ("library145 service145 gateway145 storage145 network145 latency145", 28),
        ["library145 service145", "gateway145 storage145", "network145 latency145"],
    ),
    (
        ("service145 gateway145 storage145 network145 latency145 buffer145", 6),
        ["service145", "gateway145", "storage145", "network145", "latency145", "buffer145"],
    ),
    (
        ("service145 gateway145 storage145 network145 latency145 buffer145", 10),
        ["service145", "gateway145", "storage145", "network145", "latency145", "buffer145"],
    ),
    (
        ("service145 gateway145 storage145 network145 latency145 buffer145", 18),
        ["service145", "gateway145", "storage145", "network145", "latency145", "buffer145"],
    ),
    (
        ("service145 gateway145 storage145 network145 latency145 buffer145", 28),
        ["service145 gateway145", "storage145 network145", "latency145 buffer145"],
    ),
    (
        ("gateway145 storage145 network145 latency145 buffer145 queue145", 6),
        ["gateway145", "storage145", "network145", "latency145", "buffer145", "queue145"],
    ),
    (
        ("gateway145 storage145 network145 latency145 buffer145 queue145", 10),
        ["gateway145", "storage145", "network145", "latency145", "buffer145", "queue145"],
    ),
    (
        ("gateway145 storage145 network145 latency145 buffer145 queue145", 18),
        ["gateway145", "storage145", "network145", "latency145", "buffer145 queue145"],
    ),
    (
        ("gateway145 storage145 network145 latency145 buffer145 queue145", 28),
        ["gateway145 storage145", "network145 latency145", "buffer145 queue145"],
    ),
    (
        ("storage145 network145 latency145 buffer145 queue145 worker145", 6),
        ["storage145", "network145", "latency145", "buffer145", "queue145", "worker145"],
    ),
    (
        ("storage145 network145 latency145 buffer145 queue145 worker145", 10),
        ["storage145", "network145", "latency145", "buffer145", "queue145", "worker145"],
    ),
    (
        ("storage145 network145 latency145 buffer145 queue145 worker145", 18),
        ["storage145", "network145", "latency145", "buffer145 queue145", "worker145"],
    ),
    (
        ("storage145 network145 latency145 buffer145 queue145 worker145", 28),
        ["storage145 network145", "latency145 buffer145", "queue145 worker145"],
    ),
    (
        ("network145 latency145 buffer145 queue145 worker145 kernel145", 6),
        ["network145", "latency145", "buffer145", "queue145", "worker145", "kernel145"],
    ),
    (
        ("network145 latency145 buffer145 queue145 worker145 kernel145", 10),
        ["network145", "latency145", "buffer145", "queue145", "worker145", "kernel145"],
    ),
    (
        ("network145 latency145 buffer145 queue145 worker145 kernel145", 18),
        ["network145", "latency145", "buffer145 queue145", "worker145", "kernel145"],
    ),
    (
        ("network145 latency145 buffer145 queue145 worker145 kernel145", 28),
        ["network145 latency145", "buffer145 queue145 worker145", "kernel145"],
    ),
    (
        ("latency145 buffer145 queue145 worker145 kernel145 signal145", 6),
        ["latency145", "buffer145", "queue145", "worker145", "kernel145", "signal145"],
    ),
    (
        ("latency145 buffer145 queue145 worker145 kernel145 signal145", 10),
        ["latency145", "buffer145", "queue145", "worker145", "kernel145", "signal145"],
    ),
    (
        ("latency145 buffer145 queue145 worker145 kernel145 signal145", 18),
        ["latency145", "buffer145 queue145", "worker145", "kernel145", "signal145"],
    ),
    (
        ("latency145 buffer145 queue145 worker145 kernel145 signal145", 28),
        ["latency145 buffer145", "queue145 worker145 kernel145", "signal145"],
    ),
    (
        ("buffer145 queue145 worker145 kernel145 signal145 packet145", 6),
        ["buffer145", "queue145", "worker145", "kernel145", "signal145", "packet145"],
    ),
    (
        ("buffer145 queue145 worker145 kernel145 signal145 packet145", 10),
        ["buffer145", "queue145", "worker145", "kernel145", "signal145", "packet145"],
    ),
    (
        ("buffer145 queue145 worker145 kernel145 signal145 packet145", 18),
        ["buffer145 queue145", "worker145", "kernel145", "signal145", "packet145"],
    ),
    (
        ("buffer145 queue145 worker145 kernel145 signal145 packet145", 28),
        ["buffer145 queue145 worker145", "kernel145 signal145", "packet145"],
    ),
    (
        ("queue145 worker145 kernel145 signal145 packet145 router145", 6),
        ["queue145", "worker145", "kernel145", "signal145", "packet145", "router145"],
    ),
    (
        ("queue145 worker145 kernel145 signal145 packet145 router145", 10),
        ["queue145", "worker145", "kernel145", "signal145", "packet145", "router145"],
    ),
    (
        ("queue145 worker145 kernel145 signal145 packet145 router145", 18),
        ["queue145 worker145", "kernel145", "signal145", "packet145", "router145"],
    ),
    (
        ("queue145 worker145 kernel145 signal145 packet145 router145", 28),
        ["queue145 worker145 kernel145", "signal145 packet145", "router145"],
    ),
    (
        ("worker145 kernel145 signal145 packet145 router145 cluster145", 6),
        ["worker145", "kernel145", "signal145", "packet145", "router145", "cluster145"],
    ),
    (
        ("worker145 kernel145 signal145 packet145 router145 cluster145", 10),
        ["worker145", "kernel145", "signal145", "packet145", "router145", "cluster145"],
    ),
    (
        ("worker145 kernel145 signal145 packet145 router145 cluster145", 18),
        ["worker145", "kernel145", "signal145", "packet145", "router145", "cluster145"],
    ),
    (
        ("worker145 kernel145 signal145 packet145 router145 cluster145", 28),
        ["worker145 kernel145", "signal145 packet145", "router145 cluster145"],
    ),
    (
        ("kernel145 signal145 packet145 router145 cluster145 mirror145", 6),
        ["kernel145", "signal145", "packet145", "router145", "cluster145", "mirror145"],
    ),
    (
        ("kernel145 signal145 packet145 router145 cluster145 mirror145", 10),
        ["kernel145", "signal145", "packet145", "router145", "cluster145", "mirror145"],
    ),
    (
        ("kernel145 signal145 packet145 router145 cluster145 mirror145", 18),
        ["kernel145", "signal145", "packet145", "router145", "cluster145", "mirror145"],
    ),
    (
        ("kernel145 signal145 packet145 router145 cluster145 mirror145", 28),
        ["kernel145 signal145", "packet145 router145", "cluster145 mirror145"],
    ),
    (
        ("signal145 packet145 router145 cluster145 mirror145 filter145", 6),
        ["signal145", "packet145", "router145", "cluster145", "mirror145", "filter145"],
    ),
    (
        ("signal145 packet145 router145 cluster145 mirror145 filter145", 10),
        ["signal145", "packet145", "router145", "cluster145", "mirror145", "filter145"],
    ),
    (
        ("signal145 packet145 router145 cluster145 mirror145 filter145", 18),
        ["signal145", "packet145", "router145", "cluster145", "mirror145", "filter145"],
    ),
    (
        ("signal145 packet145 router145 cluster145 mirror145 filter145", 28),
        ["signal145 packet145", "router145 cluster145", "mirror145 filter145"],
    ),
    (
        ("packet145 router145 cluster145 mirror145 filter145 ranking145", 6),
        ["packet145", "router145", "cluster145", "mirror145", "filter145", "ranking145"],
    ),
    (
        ("packet145 router145 cluster145 mirror145 filter145 ranking145", 10),
        ["packet145", "router145", "cluster145", "mirror145", "filter145", "ranking145"],
    ),
    (
        ("packet145 router145 cluster145 mirror145 filter145 ranking145", 18),
        ["packet145", "router145", "cluster145", "mirror145", "filter145", "ranking145"],
    ),
    (
        ("packet145 router145 cluster145 mirror145 filter145 ranking145", 28),
        ["packet145 router145", "cluster145 mirror145", "filter145 ranking145"],
    ),
    (
        ("router145 cluster145 mirror145 filter145 ranking145 encoding145", 6),
        ["router145", "cluster145", "mirror145", "filter145", "ranking145", "encoding145"],
    ),
    (
        ("router145 cluster145 mirror145 filter145 ranking145 encoding145", 10),
        ["router145", "cluster145", "mirror145", "filter145", "ranking145", "encoding145"],
    ),
    (
        ("router145 cluster145 mirror145 filter145 ranking145 encoding145", 18),
        ["router145", "cluster145", "mirror145", "filter145", "ranking145", "encoding145"],
    ),
    (
        ("router145 cluster145 mirror145 filter145 ranking145 encoding145", 28),
        ["router145 cluster145", "mirror145 filter145", "ranking145 encoding145"],
    ),
    (
        ("cluster145 mirror145 filter145 ranking145 encoding145 mapping145", 6),
        ["cluster145", "mirror145", "filter145", "ranking145", "encoding145", "mapping145"],
    ),
    (
        ("cluster145 mirror145 filter145 ranking145 encoding145 mapping145", 10),
        ["cluster145", "mirror145", "filter145", "ranking145", "encoding145", "mapping145"],
    ),
    (
        ("cluster145 mirror145 filter145 ranking145 encoding145 mapping145", 18),
        ["cluster145", "mirror145", "filter145", "ranking145", "encoding145", "mapping145"],
    ),
    (
        ("cluster145 mirror145 filter145 ranking145 encoding145 mapping145", 28),
        ["cluster145 mirror145", "filter145 ranking145", "encoding145 mapping145"],
    ),
    (
        ("mirror145 filter145 ranking145 encoding145 mapping145 record145", 6),
        ["mirror145", "filter145", "ranking145", "encoding145", "mapping145", "record145"],
    ),
    (
        ("mirror145 filter145 ranking145 encoding145 mapping145 record145", 10),
        ["mirror145", "filter145", "ranking145", "encoding145", "mapping145", "record145"],
    ),
    (
        ("mirror145 filter145 ranking145 encoding145 mapping145 record145", 18),
        ["mirror145", "filter145", "ranking145", "encoding145", "mapping145", "record145"],
    ),
    (
        ("mirror145 filter145 ranking145 encoding145 mapping145 record145", 28),
        ["mirror145 filter145", "ranking145 encoding145", "mapping145 record145"],
    ),
    (
        ("filter145 ranking145 encoding145 mapping145 record145 candle145", 6),
        ["filter145", "ranking145", "encoding145", "mapping145", "record145", "candle145"],
    ),
    (
        ("filter145 ranking145 encoding145 mapping145 record145 candle145", 10),
        ["filter145", "ranking145", "encoding145", "mapping145", "record145", "candle145"],
    ),
    (
        ("filter145 ranking145 encoding145 mapping145 record145 candle145", 18),
        ["filter145", "ranking145", "encoding145", "mapping145", "record145", "candle145"],
    ),
    (
        ("filter145 ranking145 encoding145 mapping145 record145 candle145", 28),
        ["filter145 ranking145", "encoding145 mapping145", "record145 candle145"],
    ),
    (
        ("ranking145 encoding145 mapping145 record145 candle145 thread145", 6),
        ["ranking145", "encoding145", "mapping145", "record145", "candle145", "thread145"],
    ),
    (
        ("ranking145 encoding145 mapping145 record145 candle145 thread145", 10),
        ["ranking145", "encoding145", "mapping145", "record145", "candle145", "thread145"],
    ),
    (
        ("ranking145 encoding145 mapping145 record145 candle145 thread145", 18),
        ["ranking145", "encoding145", "mapping145", "record145", "candle145", "thread145"],
    ),
    (
        ("ranking145 encoding145 mapping145 record145 candle145 thread145", 28),
        ["ranking145 encoding145", "mapping145 record145", "candle145 thread145"],
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
