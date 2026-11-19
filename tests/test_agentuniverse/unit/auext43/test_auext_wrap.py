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
        ("round 43: the quick brown fox jumps over the lazy dog", 4),
        ["round", "43:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 43: the quick brown fox jumps over the lazy dog", 8),
        ["round", "43: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 43: the quick brown fox jumps over the lazy dog", 12),
        ["round 43:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 43: the quick brown fox jumps over the lazy dog", 16),
        ["round 43: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 43: the quick brown fox jumps over the lazy dog", 24),
        ["round 43: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 43: the quick brown fox jumps over the lazy dog", 32),
        ["round 43: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 43: agentuniverse is a framework for multi agents", 4),
        ["round", "43:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 43: agentuniverse is a framework for multi agents", 8),
        ["round", "43:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 43: agentuniverse is a framework for multi agents", 12),
        ["round 43:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 43: agentuniverse is a framework for multi agents", 16),
        ["round 43:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 43: agentuniverse is a framework for multi agents", 24),
        ["round 43: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 43: agentuniverse is a framework for multi agents", 32),
        ["round 43: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 43: knowledge stored as vectors enables retrieval", 4),
        ["round", "43:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 43: knowledge stored as vectors enables retrieval", 8),
        ["round", "43:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 43: knowledge stored as vectors enables retrieval", 12),
        ["round 43:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 43: knowledge stored as vectors enables retrieval", 16),
        ["round 43:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 43: knowledge stored as vectors enables retrieval", 24),
        ["round 43: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 43: knowledge stored as vectors enables retrieval", 32),
        ["round 43: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 43: the processor reads the record then stops", 4),
        ["round", "43:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 43: the processor reads the record then stops", 8),
        ["round", "43: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 43: the processor reads the record then stops", 12),
        ["round 43:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 43: the processor reads the record then stops", 16),
        ["round 43: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 43: the processor reads the record then stops", 24),
        ["round 43: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 43: the processor reads the record then stops", 32),
        ["round 43: the processor reads", "the record then stops"],
    ),
    (
        ("round 43: a worker pulls the next task from the queue", 4),
        ["round", "43:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 43: a worker pulls the next task from the queue", 8),
        ["round", "43: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 43: a worker pulls the next task from the queue", 12),
        ["round 43: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 43: a worker pulls the next task from the queue", 16),
        ["round 43: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 43: a worker pulls the next task from the queue", 24),
        ["round 43: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 43: a worker pulls the next task from the queue", 32),
        ["round 43: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 43: signals travel through the network layer", 4),
        ["round", "43:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 43: signals travel through the network layer", 8),
        ["round", "43:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 43: signals travel through the network layer", 12),
        ["round 43:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 43: signals travel through the network layer", 16),
        ["round 43:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 43: signals travel through the network layer", 24),
        ["round 43: signals travel", "through the network", "layer"],
    ),
    (
        ("round 43: signals travel through the network layer", 32),
        ["round 43: signals travel through", "the network layer"],
    ),
    (
        ("round 43: the gateway routes each request by policy", 4),
        ["round", "43:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 43: the gateway routes each request by policy", 8),
        ["round", "43: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 43: the gateway routes each request by policy", 12),
        ["round 43:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 43: the gateway routes each request by policy", 16),
        ["round 43: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 43: the gateway routes each request by policy", 24),
        ["round 43: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 43: the gateway routes each request by policy", 32),
        ["round 43: the gateway routes", "each request by policy"],
    ),
    (
        ("round 43: memory grows until the buffer is full", 4),
        ["round", "43:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 43: memory grows until the buffer is full", 8),
        ["round", "43:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 43: memory grows until the buffer is full", 12),
        ["round 43:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 43: memory grows until the buffer is full", 16),
        ["round 43: memory", "grows until the", "buffer is full"],
    ),
    (("round 43: memory grows until the buffer is full", 24), ["round 43: memory grows", "until the buffer is full"]),
    (("round 43: memory grows until the buffer is full", 32), ["round 43: memory grows until the", "buffer is full"]),
    (
        ("round 43: the cluster mirrors every packet twice", 4),
        ["round", "43:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 43: the cluster mirrors every packet twice", 8),
        ["round", "43: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 43: the cluster mirrors every packet twice", 12),
        ["round 43:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 43: the cluster mirrors every packet twice", 16),
        ["round 43: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 43: the cluster mirrors every packet twice", 24),
        ["round 43: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 43: the cluster mirrors every packet twice", 32), ["round 43: the cluster mirrors", "every packet twice"]),
    (
        ("round 43: ranking uses tokens learned from the corpus", 4),
        ["round", "43:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 43: ranking uses tokens learned from the corpus", 8),
        ["round", "43:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 43: ranking uses tokens learned from the corpus", 12),
        ["round 43:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 43: ranking uses tokens learned from the corpus", 16),
        ["round 43:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 43: ranking uses tokens learned from the corpus", 24),
        ["round 43: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 43: ranking uses tokens learned from the corpus", 32),
        ["round 43: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 43: a long session ends when the candle dies", 4),
        ["round", "43:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 43: a long session ends when the candle dies", 8),
        ["round", "43: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 43: a long session ends when the candle dies", 12),
        ["round 43: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 43: a long session ends when the candle dies", 16),
        ["round 43: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 43: a long session ends when the candle dies", 24),
        ["round 43: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 43: a long session ends when the candle dies", 32),
        ["round 43: a long session ends", "when the candle dies"],
    ),
    (
        ("round 43: encode the prompt then map the result", 4),
        ["round", "43:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 43: encode the prompt then map the result", 8),
        ["round", "43:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 43: encode the prompt then map the result", 12),
        ["round 43:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 43: encode the prompt then map the result", 16),
        ["round 43: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 43: encode the prompt then map the result", 24),
        ["round 43: encode the", "prompt then map the", "result"],
    ),
    (("round 43: encode the prompt then map the result", 32), ["round 43: encode the prompt then", "map the result"]),
    (
        ("round 43: the kernel wakes the worker at dawn", 4),
        ["round", "43:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 43: the kernel wakes the worker at dawn", 8),
        ["round", "43: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 43: the kernel wakes the worker at dawn", 12),
        ["round 43:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 43: the kernel wakes the worker at dawn", 16), ["round 43: the", "kernel wakes the", "worker at dawn"]),
    (("round 43: the kernel wakes the worker at dawn", 24), ["round 43: the kernel", "wakes the worker at dawn"]),
    (("round 43: the kernel wakes the worker at dawn", 32), ["round 43: the kernel wakes the", "worker at dawn"]),
    (
        ("round 43: service latency drops after the patch", 4),
        ["round", "43:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 43: service latency drops after the patch", 8),
        ["round", "43:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 43: service latency drops after the patch", 12),
        ["round 43:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 43: service latency drops after the patch", 16),
        ["round 43:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 43: service latency drops after the patch", 24),
        ["round 43: service", "latency drops after the", "patch"],
    ),
    (("round 43: service latency drops after the patch", 32), ["round 43: service latency drops", "after the patch"]),
    (
        ("round 43: the library caches every vector it sees", 4),
        ["round", "43:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 43: the library caches every vector it sees", 8),
        ["round", "43: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 43: the library caches every vector it sees", 12),
        ["round 43:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 43: the library caches every vector it sees", 16),
        ["round 43: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 43: the library caches every vector it sees", 24),
        ["round 43: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 43: the library caches every vector it sees", 32),
        ["round 43: the library caches", "every vector it sees"],
    ),
    (
        ("round 43: agents argue then the debate resolves", 4),
        ["round", "43:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 43: agents argue then the debate resolves", 8),
        ["round", "43:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 43: agents argue then the debate resolves", 12),
        ["round 43:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 43: agents argue then the debate resolves", 16),
        ["round 43: agents", "argue then the", "debate resolves"],
    ),
    (("round 43: agents argue then the debate resolves", 24), ["round 43: agents argue", "then the debate resolves"]),
    (("round 43: agents argue then the debate resolves", 32), ["round 43: agents argue then the", "debate resolves"]),
    (
        ("round 43: the filter keeps only strong matches", 4),
        ["round", "43:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 43: the filter keeps only strong matches", 8),
        ["round", "43: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 43: the filter keeps only strong matches", 12),
        ["round 43:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 43: the filter keeps only strong matches", 16),
        ["round 43: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 43: the filter keeps only strong matches", 24), ["round 43: the filter", "keeps only strong", "matches"]),
    (("round 43: the filter keeps only strong matches", 32), ["round 43: the filter keeps only", "strong matches"]),
    (
        ("round 43: the model answers with a short reply", 4),
        ["round", "43:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 43: the model answers with a short reply", 8),
        ["round", "43: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 43: the model answers with a short reply", 12),
        ["round 43:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 43: the model answers with a short reply", 16),
        ["round 43: the", "model answers", "with a short", "reply"],
    ),
    (("round 43: the model answers with a short reply", 24), ["round 43: the model", "answers with a short", "reply"]),
    (("round 43: the model answers with a short reply", 32), ["round 43: the model answers with", "a short reply"]),
    (
        ("round 43: the recorder stores the reasoning trace", 4),
        ["round", "43:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 43: the recorder stores the reasoning trace", 8),
        ["round", "43: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 43: the recorder stores the reasoning trace", 12),
        ["round 43:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 43: the recorder stores the reasoning trace", 16),
        ["round 43: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 43: the recorder stores the reasoning trace", 24),
        ["round 43: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 43: the recorder stores the reasoning trace", 32),
        ["round 43: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 43: the angel watches the processor run", 4),
        ["round", "43:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 43: the angel watches the processor run", 8),
        ["round", "43: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 43: the angel watches the processor run", 12),
        ["round 43:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 43: the angel watches the processor run", 16), ["round 43: the", "angel watches", "the processor", "run"]),
    (("round 43: the angel watches the processor run", 24), ["round 43: the angel", "watches the processor", "run"]),
    (("round 43: the angel watches the processor run", 32), ["round 43: the angel watches the", "processor run"]),
    (
        ("round 43: angle of the vector decides the match", 4),
        ["round", "43:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 43: angle of the vector decides the match", 8),
        ["round", "43:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 43: angle of the vector decides the match", 12),
        ["round 43:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 43: angle of the vector decides the match", 16),
        ["round 43: angle", "of the vector", "decides the", "match"],
    ),
    (("round 43: angle of the vector decides the match", 24), ["round 43: angle of the", "vector decides the match"]),
    (("round 43: angle of the vector decides the match", 32), ["round 43: angle of the vector", "decides the match"]),
    (
        ("round 43: the candle burns twice as long at night", 4),
        ["round", "43:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 43: the candle burns twice as long at night", 8),
        ["round", "43: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 43: the candle burns twice as long at night", 12),
        ["round 43:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 43: the candle burns twice as long at night", 16),
        ["round 43: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 43: the candle burns twice as long at night", 24),
        ["round 43: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 43: the candle burns twice as long at night", 32),
        ["round 43: the candle burns twice", "as long at night"],
    ),
    (
        ("round 43: a mirror of the universe in one line", 4),
        ["round", "43:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 43: a mirror of the universe in one line", 8),
        ["round", "43: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 43: a mirror of the universe in one line", 12),
        ["round 43: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 43: a mirror of the universe in one line", 16),
        ["round 43: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 43: a mirror of the universe in one line", 24), ["round 43: a mirror of", "the universe in one line"]),
    (("round 43: a mirror of the universe in one line", 32), ["round 43: a mirror of the", "universe in one line"]),
    (
        ("round 43: the queue drains before the storm", 4),
        ["round", "43:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 43: the queue drains before the storm", 8),
        ["round", "43: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 43: the queue drains before the storm", 12), ["round 43:", "the queue", "drains", "before the", "storm"]),
    (("round 43: the queue drains before the storm", 16), ["round 43: the", "queue drains", "before the storm"]),
    (("round 43: the queue drains before the storm", 24), ["round 43: the queue", "drains before the storm"]),
    (("round 43: the queue drains before the storm", 32), ["round 43: the queue drains", "before the storm"]),
    (
        ("kitten43 sitting43 agent43 angle43 universe43 memory43", 6),
        ["kitten43", "sitting43", "agent43", "angle43", "universe43", "memory43"],
    ),
    (
        ("kitten43 sitting43 agent43 angle43 universe43 memory43", 10),
        ["kitten43", "sitting43", "agent43", "angle43", "universe43", "memory43"],
    ),
    (
        ("kitten43 sitting43 agent43 angle43 universe43 memory43", 18),
        ["kitten43 sitting43", "agent43 angle43", "universe43", "memory43"],
    ),
    (
        ("kitten43 sitting43 agent43 angle43 universe43 memory43", 28),
        ["kitten43 sitting43 agent43", "angle43 universe43 memory43"],
    ),
    (
        ("sitting43 agent43 angle43 universe43 memory43 stream43", 6),
        ["sitting43", "agent43", "angle43", "universe43", "memory43", "stream43"],
    ),
    (
        ("sitting43 agent43 angle43 universe43 memory43 stream43", 10),
        ["sitting43", "agent43", "angle43", "universe43", "memory43", "stream43"],
    ),
    (
        ("sitting43 agent43 angle43 universe43 memory43 stream43", 18),
        ["sitting43 agent43", "angle43 universe43", "memory43 stream43"],
    ),
    (
        ("sitting43 agent43 angle43 universe43 memory43 stream43", 28),
        ["sitting43 agent43 angle43", "universe43 memory43 stream43"],
    ),
    (
        ("agent43 angle43 universe43 memory43 stream43 context43", 6),
        ["agent43", "angle43", "universe43", "memory43", "stream43", "context43"],
    ),
    (
        ("agent43 angle43 universe43 memory43 stream43 context43", 10),
        ["agent43", "angle43", "universe43", "memory43", "stream43", "context43"],
    ),
    (
        ("agent43 angle43 universe43 memory43 stream43 context43", 18),
        ["agent43 angle43", "universe43", "memory43 stream43", "context43"],
    ),
    (
        ("agent43 angle43 universe43 memory43 stream43 context43", 28),
        ["agent43 angle43 universe43", "memory43 stream43 context43"],
    ),
    (
        ("angle43 universe43 memory43 stream43 context43 knowledge43", 6),
        ["angle43", "universe43", "memory43", "stream43", "context43", "knowledge43"],
    ),
    (
        ("angle43 universe43 memory43 stream43 context43 knowledge43", 10),
        ["angle43", "universe43", "memory43", "stream43", "context43", "knowledge43"],
    ),
    (
        ("angle43 universe43 memory43 stream43 context43 knowledge43", 18),
        ["angle43 universe43", "memory43 stream43", "context43", "knowledge43"],
    ),
    (
        ("angle43 universe43 memory43 stream43 context43 knowledge43", 28),
        ["angle43 universe43 memory43", "stream43 context43", "knowledge43"],
    ),
    (
        ("universe43 memory43 stream43 context43 knowledge43 vector43", 6),
        ["universe43", "memory43", "stream43", "context43", "knowledge43", "vector43"],
    ),
    (
        ("universe43 memory43 stream43 context43 knowledge43 vector43", 10),
        ["universe43", "memory43", "stream43", "context43", "knowledge43", "vector43"],
    ),
    (
        ("universe43 memory43 stream43 context43 knowledge43 vector43", 18),
        ["universe43", "memory43 stream43", "context43", "knowledge43", "vector43"],
    ),
    (
        ("universe43 memory43 stream43 context43 knowledge43 vector43", 28),
        ["universe43 memory43 stream43", "context43 knowledge43", "vector43"],
    ),
    (
        ("memory43 stream43 context43 knowledge43 vector43 processor43", 6),
        ["memory43", "stream43", "context43", "knowledge43", "vector43", "processor43"],
    ),
    (
        ("memory43 stream43 context43 knowledge43 vector43 processor43", 10),
        ["memory43", "stream43", "context43", "knowledge43", "vector43", "processor43"],
    ),
    (
        ("memory43 stream43 context43 knowledge43 vector43 processor43", 18),
        ["memory43 stream43", "context43", "knowledge43", "vector43", "processor43"],
    ),
    (
        ("memory43 stream43 context43 knowledge43 vector43 processor43", 28),
        ["memory43 stream43 context43", "knowledge43 vector43", "processor43"],
    ),
    (
        ("stream43 context43 knowledge43 vector43 processor43 reasoning43", 6),
        ["stream43", "context43", "knowledge43", "vector43", "processor43", "reasoning43"],
    ),
    (
        ("stream43 context43 knowledge43 vector43 processor43 reasoning43", 10),
        ["stream43", "context43", "knowledge43", "vector43", "processor43", "reasoning43"],
    ),
    (
        ("stream43 context43 knowledge43 vector43 processor43 reasoning43", 18),
        ["stream43 context43", "knowledge43", "vector43", "processor43", "reasoning43"],
    ),
    (
        ("stream43 context43 knowledge43 vector43 processor43 reasoning43", 28),
        ["stream43 context43", "knowledge43 vector43", "processor43 reasoning43"],
    ),
    (
        ("context43 knowledge43 vector43 processor43 reasoning43 machine43", 6),
        ["context43", "knowledge43", "vector43", "processor43", "reasoning43", "machine43"],
    ),
    (
        ("context43 knowledge43 vector43 processor43 reasoning43 machine43", 10),
        ["context43", "knowledge43", "vector43", "processor43", "reasoning43", "machine43"],
    ),
    (
        ("context43 knowledge43 vector43 processor43 reasoning43 machine43", 18),
        ["context43", "knowledge43", "vector43", "processor43", "reasoning43", "machine43"],
    ),
    (
        ("context43 knowledge43 vector43 processor43 reasoning43 machine43", 28),
        ["context43 knowledge43", "vector43 processor43", "reasoning43 machine43"],
    ),
    (
        ("knowledge43 vector43 processor43 reasoning43 machine43 learning43", 6),
        ["knowledge43", "vector43", "processor43", "reasoning43", "machine43", "learning43"],
    ),
    (
        ("knowledge43 vector43 processor43 reasoning43 machine43 learning43", 10),
        ["knowledge43", "vector43", "processor43", "reasoning43", "machine43", "learning43"],
    ),
    (
        ("knowledge43 vector43 processor43 reasoning43 machine43 learning43", 18),
        ["knowledge43", "vector43", "processor43", "reasoning43", "machine43", "learning43"],
    ),
    (
        ("knowledge43 vector43 processor43 reasoning43 machine43 learning43", 28),
        ["knowledge43 vector43", "processor43 reasoning43", "machine43 learning43"],
    ),
    (
        ("vector43 processor43 reasoning43 machine43 learning43 model43", 6),
        ["vector43", "processor43", "reasoning43", "machine43", "learning43", "model43"],
    ),
    (
        ("vector43 processor43 reasoning43 machine43 learning43 model43", 10),
        ["vector43", "processor43", "reasoning43", "machine43", "learning43", "model43"],
    ),
    (
        ("vector43 processor43 reasoning43 machine43 learning43 model43", 18),
        ["vector43", "processor43", "reasoning43", "machine43", "learning43 model43"],
    ),
    (
        ("vector43 processor43 reasoning43 machine43 learning43 model43", 28),
        ["vector43 processor43", "reasoning43 machine43", "learning43 model43"],
    ),
    (
        ("processor43 reasoning43 machine43 learning43 model43 token43", 6),
        ["processor43", "reasoning43", "machine43", "learning43", "model43", "token43"],
    ),
    (
        ("processor43 reasoning43 machine43 learning43 model43 token43", 10),
        ["processor43", "reasoning43", "machine43", "learning43", "model43", "token43"],
    ),
    (
        ("processor43 reasoning43 machine43 learning43 model43 token43", 18),
        ["processor43", "reasoning43", "machine43", "learning43 model43", "token43"],
    ),
    (
        ("processor43 reasoning43 machine43 learning43 model43 token43", 28),
        ["processor43 reasoning43", "machine43 learning43 model43", "token43"],
    ),
    (
        ("reasoning43 machine43 learning43 model43 token43 prompt43", 6),
        ["reasoning43", "machine43", "learning43", "model43", "token43", "prompt43"],
    ),
    (
        ("reasoning43 machine43 learning43 model43 token43 prompt43", 10),
        ["reasoning43", "machine43", "learning43", "model43", "token43", "prompt43"],
    ),
    (
        ("reasoning43 machine43 learning43 model43 token43 prompt43", 18),
        ["reasoning43", "machine43", "learning43 model43", "token43 prompt43"],
    ),
    (
        ("reasoning43 machine43 learning43 model43 token43 prompt43", 28),
        ["reasoning43 machine43", "learning43 model43 token43", "prompt43"],
    ),
    (
        ("machine43 learning43 model43 token43 prompt43 session43", 6),
        ["machine43", "learning43", "model43", "token43", "prompt43", "session43"],
    ),
    (
        ("machine43 learning43 model43 token43 prompt43 session43", 10),
        ["machine43", "learning43", "model43", "token43", "prompt43", "session43"],
    ),
    (
        ("machine43 learning43 model43 token43 prompt43 session43", 18),
        ["machine43", "learning43 model43", "token43 prompt43", "session43"],
    ),
    (
        ("machine43 learning43 model43 token43 prompt43 session43", 28),
        ["machine43 learning43 model43", "token43 prompt43 session43"],
    ),
    (
        ("learning43 model43 token43 prompt43 session43 library43", 6),
        ["learning43", "model43", "token43", "prompt43", "session43", "library43"],
    ),
    (
        ("learning43 model43 token43 prompt43 session43 library43", 10),
        ["learning43", "model43", "token43", "prompt43", "session43", "library43"],
    ),
    (
        ("learning43 model43 token43 prompt43 session43 library43", 18),
        ["learning43 model43", "token43 prompt43", "session43", "library43"],
    ),
    (
        ("learning43 model43 token43 prompt43 session43 library43", 28),
        ["learning43 model43 token43", "prompt43 session43 library43"],
    ),
    (
        ("model43 token43 prompt43 session43 library43 service43", 6),
        ["model43", "token43", "prompt43", "session43", "library43", "service43"],
    ),
    (
        ("model43 token43 prompt43 session43 library43 service43", 10),
        ["model43", "token43", "prompt43", "session43", "library43", "service43"],
    ),
    (
        ("model43 token43 prompt43 session43 library43 service43", 18),
        ["model43 token43", "prompt43 session43", "library43", "service43"],
    ),
    (
        ("model43 token43 prompt43 session43 library43 service43", 28),
        ["model43 token43 prompt43", "session43 library43", "service43"],
    ),
    (
        ("token43 prompt43 session43 library43 service43 gateway43", 6),
        ["token43", "prompt43", "session43", "library43", "service43", "gateway43"],
    ),
    (
        ("token43 prompt43 session43 library43 service43 gateway43", 10),
        ["token43", "prompt43", "session43", "library43", "service43", "gateway43"],
    ),
    (
        ("token43 prompt43 session43 library43 service43 gateway43", 18),
        ["token43 prompt43", "session43", "library43", "service43", "gateway43"],
    ),
    (
        ("token43 prompt43 session43 library43 service43 gateway43", 28),
        ["token43 prompt43 session43", "library43 service43", "gateway43"],
    ),
    (
        ("prompt43 session43 library43 service43 gateway43 storage43", 6),
        ["prompt43", "session43", "library43", "service43", "gateway43", "storage43"],
    ),
    (
        ("prompt43 session43 library43 service43 gateway43 storage43", 10),
        ["prompt43", "session43", "library43", "service43", "gateway43", "storage43"],
    ),
    (
        ("prompt43 session43 library43 service43 gateway43 storage43", 18),
        ["prompt43 session43", "library43", "service43", "gateway43", "storage43"],
    ),
    (
        ("prompt43 session43 library43 service43 gateway43 storage43", 28),
        ["prompt43 session43 library43", "service43 gateway43", "storage43"],
    ),
    (
        ("session43 library43 service43 gateway43 storage43 network43", 6),
        ["session43", "library43", "service43", "gateway43", "storage43", "network43"],
    ),
    (
        ("session43 library43 service43 gateway43 storage43 network43", 10),
        ["session43", "library43", "service43", "gateway43", "storage43", "network43"],
    ),
    (
        ("session43 library43 service43 gateway43 storage43 network43", 18),
        ["session43", "library43", "service43", "gateway43", "storage43", "network43"],
    ),
    (
        ("session43 library43 service43 gateway43 storage43 network43", 28),
        ["session43 library43", "service43 gateway43", "storage43 network43"],
    ),
    (
        ("library43 service43 gateway43 storage43 network43 latency43", 6),
        ["library43", "service43", "gateway43", "storage43", "network43", "latency43"],
    ),
    (
        ("library43 service43 gateway43 storage43 network43 latency43", 10),
        ["library43", "service43", "gateway43", "storage43", "network43", "latency43"],
    ),
    (
        ("library43 service43 gateway43 storage43 network43 latency43", 18),
        ["library43", "service43", "gateway43", "storage43", "network43", "latency43"],
    ),
    (
        ("library43 service43 gateway43 storage43 network43 latency43", 28),
        ["library43 service43", "gateway43 storage43", "network43 latency43"],
    ),
    (
        ("service43 gateway43 storage43 network43 latency43 buffer43", 6),
        ["service43", "gateway43", "storage43", "network43", "latency43", "buffer43"],
    ),
    (
        ("service43 gateway43 storage43 network43 latency43 buffer43", 10),
        ["service43", "gateway43", "storage43", "network43", "latency43", "buffer43"],
    ),
    (
        ("service43 gateway43 storage43 network43 latency43 buffer43", 18),
        ["service43", "gateway43", "storage43", "network43", "latency43 buffer43"],
    ),
    (
        ("service43 gateway43 storage43 network43 latency43 buffer43", 28),
        ["service43 gateway43", "storage43 network43", "latency43 buffer43"],
    ),
    (
        ("gateway43 storage43 network43 latency43 buffer43 queue43", 6),
        ["gateway43", "storage43", "network43", "latency43", "buffer43", "queue43"],
    ),
    (
        ("gateway43 storage43 network43 latency43 buffer43 queue43", 10),
        ["gateway43", "storage43", "network43", "latency43", "buffer43", "queue43"],
    ),
    (
        ("gateway43 storage43 network43 latency43 buffer43 queue43", 18),
        ["gateway43", "storage43", "network43", "latency43 buffer43", "queue43"],
    ),
    (
        ("gateway43 storage43 network43 latency43 buffer43 queue43", 28),
        ["gateway43 storage43", "network43 latency43 buffer43", "queue43"],
    ),
    (
        ("storage43 network43 latency43 buffer43 queue43 worker43", 6),
        ["storage43", "network43", "latency43", "buffer43", "queue43", "worker43"],
    ),
    (
        ("storage43 network43 latency43 buffer43 queue43 worker43", 10),
        ["storage43", "network43", "latency43", "buffer43", "queue43", "worker43"],
    ),
    (
        ("storage43 network43 latency43 buffer43 queue43 worker43", 18),
        ["storage43", "network43", "latency43 buffer43", "queue43 worker43"],
    ),
    (
        ("storage43 network43 latency43 buffer43 queue43 worker43", 28),
        ["storage43 network43", "latency43 buffer43 queue43", "worker43"],
    ),
    (
        ("network43 latency43 buffer43 queue43 worker43 kernel43", 6),
        ["network43", "latency43", "buffer43", "queue43", "worker43", "kernel43"],
    ),
    (
        ("network43 latency43 buffer43 queue43 worker43 kernel43", 10),
        ["network43", "latency43", "buffer43", "queue43", "worker43", "kernel43"],
    ),
    (
        ("network43 latency43 buffer43 queue43 worker43 kernel43", 18),
        ["network43", "latency43 buffer43", "queue43 worker43", "kernel43"],
    ),
    (
        ("network43 latency43 buffer43 queue43 worker43 kernel43", 28),
        ["network43 latency43 buffer43", "queue43 worker43 kernel43"],
    ),
    (
        ("latency43 buffer43 queue43 worker43 kernel43 signal43", 6),
        ["latency43", "buffer43", "queue43", "worker43", "kernel43", "signal43"],
    ),
    (
        ("latency43 buffer43 queue43 worker43 kernel43 signal43", 10),
        ["latency43", "buffer43", "queue43", "worker43", "kernel43", "signal43"],
    ),
    (
        ("latency43 buffer43 queue43 worker43 kernel43 signal43", 18),
        ["latency43 buffer43", "queue43 worker43", "kernel43 signal43"],
    ),
    (
        ("latency43 buffer43 queue43 worker43 kernel43 signal43", 28),
        ["latency43 buffer43 queue43", "worker43 kernel43 signal43"],
    ),
    (
        ("buffer43 queue43 worker43 kernel43 signal43 packet43", 6),
        ["buffer43", "queue43", "worker43", "kernel43", "signal43", "packet43"],
    ),
    (
        ("buffer43 queue43 worker43 kernel43 signal43 packet43", 10),
        ["buffer43", "queue43", "worker43", "kernel43", "signal43", "packet43"],
    ),
    (
        ("buffer43 queue43 worker43 kernel43 signal43 packet43", 18),
        ["buffer43 queue43", "worker43 kernel43", "signal43 packet43"],
    ),
    (
        ("buffer43 queue43 worker43 kernel43 signal43 packet43", 28),
        ["buffer43 queue43 worker43", "kernel43 signal43 packet43"],
    ),
    (
        ("queue43 worker43 kernel43 signal43 packet43 router43", 6),
        ["queue43", "worker43", "kernel43", "signal43", "packet43", "router43"],
    ),
    (
        ("queue43 worker43 kernel43 signal43 packet43 router43", 10),
        ["queue43", "worker43", "kernel43", "signal43", "packet43", "router43"],
    ),
    (
        ("queue43 worker43 kernel43 signal43 packet43 router43", 18),
        ["queue43 worker43", "kernel43 signal43", "packet43 router43"],
    ),
    (
        ("queue43 worker43 kernel43 signal43 packet43 router43", 28),
        ["queue43 worker43 kernel43", "signal43 packet43 router43"],
    ),
    (
        ("worker43 kernel43 signal43 packet43 router43 cluster43", 6),
        ["worker43", "kernel43", "signal43", "packet43", "router43", "cluster43"],
    ),
    (
        ("worker43 kernel43 signal43 packet43 router43 cluster43", 10),
        ["worker43", "kernel43", "signal43", "packet43", "router43", "cluster43"],
    ),
    (
        ("worker43 kernel43 signal43 packet43 router43 cluster43", 18),
        ["worker43 kernel43", "signal43 packet43", "router43 cluster43"],
    ),
    (
        ("worker43 kernel43 signal43 packet43 router43 cluster43", 28),
        ["worker43 kernel43 signal43", "packet43 router43 cluster43"],
    ),
    (
        ("kernel43 signal43 packet43 router43 cluster43 mirror43", 6),
        ["kernel43", "signal43", "packet43", "router43", "cluster43", "mirror43"],
    ),
    (
        ("kernel43 signal43 packet43 router43 cluster43 mirror43", 10),
        ["kernel43", "signal43", "packet43", "router43", "cluster43", "mirror43"],
    ),
    (
        ("kernel43 signal43 packet43 router43 cluster43 mirror43", 18),
        ["kernel43 signal43", "packet43 router43", "cluster43 mirror43"],
    ),
    (
        ("kernel43 signal43 packet43 router43 cluster43 mirror43", 28),
        ["kernel43 signal43 packet43", "router43 cluster43 mirror43"],
    ),
    (
        ("signal43 packet43 router43 cluster43 mirror43 filter43", 6),
        ["signal43", "packet43", "router43", "cluster43", "mirror43", "filter43"],
    ),
    (
        ("signal43 packet43 router43 cluster43 mirror43 filter43", 10),
        ["signal43", "packet43", "router43", "cluster43", "mirror43", "filter43"],
    ),
    (
        ("signal43 packet43 router43 cluster43 mirror43 filter43", 18),
        ["signal43 packet43", "router43 cluster43", "mirror43 filter43"],
    ),
    (
        ("signal43 packet43 router43 cluster43 mirror43 filter43", 28),
        ["signal43 packet43 router43", "cluster43 mirror43 filter43"],
    ),
    (
        ("packet43 router43 cluster43 mirror43 filter43 ranking43", 6),
        ["packet43", "router43", "cluster43", "mirror43", "filter43", "ranking43"],
    ),
    (
        ("packet43 router43 cluster43 mirror43 filter43 ranking43", 10),
        ["packet43", "router43", "cluster43", "mirror43", "filter43", "ranking43"],
    ),
    (
        ("packet43 router43 cluster43 mirror43 filter43 ranking43", 18),
        ["packet43 router43", "cluster43 mirror43", "filter43 ranking43"],
    ),
    (
        ("packet43 router43 cluster43 mirror43 filter43 ranking43", 28),
        ["packet43 router43 cluster43", "mirror43 filter43 ranking43"],
    ),
    (
        ("router43 cluster43 mirror43 filter43 ranking43 encoding43", 6),
        ["router43", "cluster43", "mirror43", "filter43", "ranking43", "encoding43"],
    ),
    (
        ("router43 cluster43 mirror43 filter43 ranking43 encoding43", 10),
        ["router43", "cluster43", "mirror43", "filter43", "ranking43", "encoding43"],
    ),
    (
        ("router43 cluster43 mirror43 filter43 ranking43 encoding43", 18),
        ["router43 cluster43", "mirror43 filter43", "ranking43", "encoding43"],
    ),
    (
        ("router43 cluster43 mirror43 filter43 ranking43 encoding43", 28),
        ["router43 cluster43 mirror43", "filter43 ranking43", "encoding43"],
    ),
    (
        ("cluster43 mirror43 filter43 ranking43 encoding43 mapping43", 6),
        ["cluster43", "mirror43", "filter43", "ranking43", "encoding43", "mapping43"],
    ),
    (
        ("cluster43 mirror43 filter43 ranking43 encoding43 mapping43", 10),
        ["cluster43", "mirror43", "filter43", "ranking43", "encoding43", "mapping43"],
    ),
    (
        ("cluster43 mirror43 filter43 ranking43 encoding43 mapping43", 18),
        ["cluster43 mirror43", "filter43 ranking43", "encoding43", "mapping43"],
    ),
    (
        ("cluster43 mirror43 filter43 ranking43 encoding43 mapping43", 28),
        ["cluster43 mirror43 filter43", "ranking43 encoding43", "mapping43"],
    ),
    (
        ("mirror43 filter43 ranking43 encoding43 mapping43 record43", 6),
        ["mirror43", "filter43", "ranking43", "encoding43", "mapping43", "record43"],
    ),
    (
        ("mirror43 filter43 ranking43 encoding43 mapping43 record43", 10),
        ["mirror43", "filter43", "ranking43", "encoding43", "mapping43", "record43"],
    ),
    (
        ("mirror43 filter43 ranking43 encoding43 mapping43 record43", 18),
        ["mirror43 filter43", "ranking43", "encoding43", "mapping43 record43"],
    ),
    (
        ("mirror43 filter43 ranking43 encoding43 mapping43 record43", 28),
        ["mirror43 filter43 ranking43", "encoding43 mapping43", "record43"],
    ),
    (
        ("filter43 ranking43 encoding43 mapping43 record43 candle43", 6),
        ["filter43", "ranking43", "encoding43", "mapping43", "record43", "candle43"],
    ),
    (
        ("filter43 ranking43 encoding43 mapping43 record43 candle43", 10),
        ["filter43", "ranking43", "encoding43", "mapping43", "record43", "candle43"],
    ),
    (
        ("filter43 ranking43 encoding43 mapping43 record43 candle43", 18),
        ["filter43 ranking43", "encoding43", "mapping43 record43", "candle43"],
    ),
    (
        ("filter43 ranking43 encoding43 mapping43 record43 candle43", 28),
        ["filter43 ranking43", "encoding43 mapping43", "record43 candle43"],
    ),
    (
        ("ranking43 encoding43 mapping43 record43 candle43 thread43", 6),
        ["ranking43", "encoding43", "mapping43", "record43", "candle43", "thread43"],
    ),
    (
        ("ranking43 encoding43 mapping43 record43 candle43 thread43", 10),
        ["ranking43", "encoding43", "mapping43", "record43", "candle43", "thread43"],
    ),
    (
        ("ranking43 encoding43 mapping43 record43 candle43 thread43", 18),
        ["ranking43", "encoding43", "mapping43 record43", "candle43 thread43"],
    ),
    (
        ("ranking43 encoding43 mapping43 record43 candle43 thread43", 28),
        ["ranking43 encoding43", "mapping43 record43 candle43", "thread43"],
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
